"""Phase 1 pipeline orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from specforge_distill.extract.architecture import extract_architecture_blocks
from specforge_distill.extract.captions import extract_caption_candidates
from specforge_distill.extract.merge import link_equivalent_candidates
from specforge_distill.extract.narrative import extract_narrative_candidates
from specforge_distill.extract.tables import extract_table_candidates
from specforge_distill.ingest.pdf_loader import PageTextRecord, load_pdf_pages
from specforge_distill.ingest.text_quality import QualityWarning, assess_text_quality
from specforge_distill.models.artifacts import ArtifactBlock
from specforge_distill.models.candidates import Candidate
from specforge_distill.models.requirement import Requirement
from specforge_distill.normalize import (
    ObligationTaxonomy,
    load_obligation_taxonomy,
    normalize_requirements,
)
from specforge_distill.provenance.linker import (
    assert_citations_present,
    link_artifact_provenance,
    link_candidate_provenance,
)


@dataclass
class PipelineResult:
    """Output envelope for the specification distillation flow."""

    warnings: list[QualityWarning]
    candidates: list[Candidate]
    requirements: list[Requirement]
    artifacts: list[ArtifactBlock]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "warnings": [warning.to_dict() for warning in self.warnings],
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "requirements": [req.to_dict() for req in self.requirements],
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "metadata": dict(self.metadata),
        }


def run_distill_pipeline(
    pdf_path: str | Path,
    *,
    taxonomy_path: str | Path | None = None,
    min_chars_per_page: int = 40,
    dry_run: bool = False,
    page_records: Sequence[PageTextRecord] | None = None,
    table_rows_by_page: dict[int, list[list[str]]] | None = None,
) -> PipelineResult:
    """Execute full distillation flow: ingest -> extract -> normalize."""

    source_path = Path(pdf_path)
    taxonomy = load_obligation_taxonomy(taxonomy_path)

    metadata = {
        "source_pdf": str(source_path),
        "taxonomy_version": taxonomy.version,
        "obligation_verbs": list(taxonomy.verbs),
    }

    if dry_run:
        return PipelineResult(
            warnings=[], candidates=[], requirements=[], artifacts=[], metadata=metadata
        )

    if page_records is None:
        page_records = load_pdf_pages(source_path)

    warnings = assess_text_quality(page_records, min_chars_per_page=min_chars_per_page)
    obligation_verbs = set(taxonomy.verbs)

    narrative_candidates = extract_narrative_candidates(page_records, obligation_verbs)
    architecture_blocks = extract_architecture_blocks(page_records)
    table_candidates = extract_table_candidates(
        str(source_path),
        obligation_verbs,
        table_rows_by_page=table_rows_by_page,
    )
    caption_candidates = extract_caption_candidates(page_records, obligation_verbs)

    all_candidates = narrative_candidates + table_candidates + caption_candidates
    link_equivalent_candidates(all_candidates)

    link_candidate_provenance(all_candidates, str(source_path))
    link_artifact_provenance(architecture_blocks, str(source_path))
    assert_citations_present(all_candidates, architecture_blocks)

    # Phase 2: Normalization
    requirements = normalize_requirements(all_candidates, taxonomy.taxonomy_dict)

    return PipelineResult(
        warnings=warnings,
        candidates=all_candidates,
        requirements=requirements,
        artifacts=architecture_blocks,
        metadata=metadata,
    )


# Alias for backward compatibility with Phase 1 tests
run_phase1_pipeline = run_distill_pipeline
