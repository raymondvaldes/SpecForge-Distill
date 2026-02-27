"""Phase 1 pipeline orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from specforge_distill.extract.architecture import extract_architecture_blocks
from specforge_distill.extract.captions import extract_caption_candidates
from specforge_distill.extract.classifier import enrich_requirement
from specforge_distill.extract.id_resolver import resolve_requirement_id
from specforge_distill.extract.merge import link_equivalent_candidates
from specforge_distill.extract.narrative import extract_narrative_candidates
from specforge_distill.extract.tables import extract_table_candidates
from specforge_distill.ingest.pdf_loader import PageTextRecord, load_pdf_pages
from specforge_distill.ingest.text_quality import QualityWarning, assess_text_quality
from specforge_distill.models.artifacts import ArtifactBlock
from specforge_distill.models.candidates import Candidate
from specforge_distill.models.requirement import Requirement
from specforge_distill.provenance.linker import (
    assert_citations_present,
    link_artifact_provenance,
    link_candidate_provenance,
)


@dataclass(frozen=True)
class ObligationTaxonomy:
    """Runtime obligation taxonomy loaded from external config."""

    version: str
    verbs: tuple[str, ...]


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


DEFAULT_TAXONOMY_PATH = Path(__file__).resolve().parent / "config" / "obligation_verbs.yml"


def _parse_basic_yaml(text: str) -> dict[str, Any]:
    """Simple parser for the small taxonomy format used by this project."""

    data: dict[str, Any] = {}
    current_list_key: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("-"):
            if current_list_key is None:
                continue
            item = line[1:].strip().strip('"').strip("'")
            data.setdefault(current_list_key, []).append(item)
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", maxsplit=1)
        key = key.strip()
        value = value.strip()

        if value:
            data[key] = value.strip('"').strip("'")
            current_list_key = None
        else:
            data[key] = []
            current_list_key = key

    return data


def load_obligation_taxonomy(taxonomy_path: str | Path | None = None) -> ObligationTaxonomy:
    """Load obligation verbs from external config with version metadata."""

    path = Path(taxonomy_path or DEFAULT_TAXONOMY_PATH)
    payload = path.read_text(encoding="utf-8")

    parsed: dict[str, Any]
    try:
        import yaml  # type: ignore

        maybe = yaml.safe_load(payload)
        parsed = maybe if isinstance(maybe, dict) else {}
    except Exception:
        parsed = _parse_basic_yaml(payload)

    version = str(parsed.get("version", "unknown"))
    
    # Try getting verbs from nested taxonomy first, then fallback to top-level list
    verbs_list = []
    if "taxonomy" in parsed and isinstance(parsed["taxonomy"], dict):
        for level_verbs in parsed["taxonomy"].values():
            if isinstance(level_verbs, list):
                verbs_list.extend(level_verbs)
    elif "obligation_verbs" in parsed and isinstance(parsed["obligation_verbs"], list):
        verbs_list = parsed["obligation_verbs"]

    canonical_verbs = tuple(sorted({str(verb).strip().lower() for verb in verbs_list if str(verb).strip()}))
    return ObligationTaxonomy(version=version, verbs=canonical_verbs)


def normalize_requirements(candidates: list[Candidate]) -> list[Requirement]:
    """Transform extraction candidates into formal normalized Requirement records."""
    requirements = []
    for cand in candidates:
        # 1. Create Requirement model
        req = Requirement.from_candidate(cand)
        
        # 2. Resolve ID (preserving source or generating stable hash)
        req.id = resolve_requirement_id(cand.text, cand.page, cand.source_type)
        
        # 3. Classify obligation and detect ambiguity
        enrich_requirement(req)
        
        requirements.append(req)
        
    return requirements


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
    requirements = normalize_requirements(all_candidates)

    return PipelineResult(
        warnings=warnings,
        candidates=all_candidates,
        requirements=requirements,
        artifacts=architecture_blocks,
        metadata=metadata,
    )


# Alias for backward compatibility with Phase 1 tests
run_phase1_pipeline = run_distill_pipeline
