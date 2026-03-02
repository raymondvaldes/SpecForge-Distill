"""Phase 1 pipeline orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Sequence

if TYPE_CHECKING:
    from specforge_distill.ingest.pdf_loader import PageTextRecord


def extract_architecture_blocks(*args: Any, **kwargs: Any) -> list[Any]:
    from specforge_distill.extract.architecture import extract_architecture_blocks as _impl

    return _impl(*args, **kwargs)


def extract_caption_candidates(*args: Any, **kwargs: Any) -> list[Any]:
    from specforge_distill.extract.captions import extract_caption_candidates as _impl

    return _impl(*args, **kwargs)


def link_equivalent_candidates(*args: Any, **kwargs: Any) -> None:
    from specforge_distill.extract.merge import link_equivalent_candidates as _impl

    return _impl(*args, **kwargs)


def extract_narrative_candidates(*args: Any, **kwargs: Any) -> list[Any]:
    from specforge_distill.extract.narrative import extract_narrative_candidates as _impl

    return _impl(*args, **kwargs)


def extract_table_candidates(*args: Any, **kwargs: Any) -> list[Any]:
    from specforge_distill.extract.tables import extract_table_candidates as _impl

    return _impl(*args, **kwargs)


def load_pdf_pages(*args: Any, **kwargs: Any) -> list["PageTextRecord"]:
    from specforge_distill.ingest.pdf_loader import load_pdf_pages as _impl

    return _impl(*args, **kwargs)


def assess_text_quality(*args: Any, **kwargs: Any) -> list[Any]:
    from specforge_distill.ingest.text_quality import assess_text_quality as _impl

    return _impl(*args, **kwargs)


def load_obligation_taxonomy(*args: Any, **kwargs: Any) -> Any:
    from specforge_distill.normalize import load_obligation_taxonomy as _impl

    return _impl(*args, **kwargs)


def normalize_requirements(*args: Any, **kwargs: Any) -> list[Any]:
    from specforge_distill.normalize import normalize_requirements as _impl

    return _impl(*args, **kwargs)


def assert_citations_present(*args: Any, **kwargs: Any) -> None:
    from specforge_distill.provenance.linker import assert_citations_present as _impl

    return _impl(*args, **kwargs)


def link_artifact_provenance(*args: Any, **kwargs: Any) -> None:
    from specforge_distill.provenance.linker import link_artifact_provenance as _impl

    return _impl(*args, **kwargs)


def link_candidate_provenance(*args: Any, **kwargs: Any) -> None:
    from specforge_distill.provenance.linker import link_candidate_provenance as _impl

    return _impl(*args, **kwargs)


@dataclass
class PipelineResult:
    """Output envelope for the specification distillation flow."""

    warnings: list[Any]
    candidates: list[Any]
    requirements: list[Any]
    artifacts: list[Any]
    metadata: dict[str, Any]
    validation: Any = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "warnings": [warning.to_dict() for warning in self.warnings],
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "requirements": [req.to_dict() for req in self.requirements],
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "metadata": dict(self.metadata),
        }
        if self.validation:
            result["validation"] = self.validation.to_dict()
        return result


def run_distill_pipeline(
    pdf_path: str | Path,
    *,
    taxonomy_path: str | Path | None = None,
    min_chars_per_page: int = 40,
    dry_run: bool = False,
    page_records: Sequence["PageTextRecord"] | None = None,
    table_rows_by_page: dict[int, list[list[str]]] | None = None,
    progress_callback: Callable[[str], None] | None = None,
) -> PipelineResult:
    """Execute full distillation flow: ingest -> extract -> normalize."""
    from specforge_distill.validation import validate_requirements

    def _notify(msg: str) -> None:
        if progress_callback:
            progress_callback(msg)

    source_path = Path(pdf_path)
    _notify("Loading obligation taxonomy...")
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
        _notify("Loading PDF pages...")
        page_records = load_pdf_pages(source_path)

    _notify(f"Assessing text quality for {len(page_records)} pages...")
    warnings = assess_text_quality(page_records, min_chars_per_page=min_chars_per_page)
    obligation_verbs = set(taxonomy.verbs)

    _notify("Extracting narrative candidates...")
    narrative_candidates = extract_narrative_candidates(page_records, obligation_verbs)
    
    _notify("Extracting architecture blocks...")
    architecture_blocks = extract_architecture_blocks(page_records)
    
    _notify("Extracting table candidates...")
    table_candidates = extract_table_candidates(
        str(source_path),
        obligation_verbs,
        table_rows_by_page=table_rows_by_page,
    )
    
    _notify("Extracting caption candidates...")
    caption_candidates = extract_caption_candidates(page_records, obligation_verbs)

    all_candidates = narrative_candidates + table_candidates + caption_candidates
    _notify(f"Linking {len(all_candidates)} candidates...")
    link_equivalent_candidates(all_candidates)

    _notify("Resolving provenance...")
    link_candidate_provenance(all_candidates, str(source_path))
    link_artifact_provenance(architecture_blocks, str(source_path))
    assert_citations_present(all_candidates, architecture_blocks)

    _notify("Normalizing requirements...")
    # Phase 2: Normalization
    requirements = normalize_requirements(all_candidates, taxonomy.taxonomy_dict)
    
    result = PipelineResult(
        warnings=warnings,
        candidates=all_candidates,
        requirements=requirements,
        artifacts=architecture_blocks,
        metadata=metadata,
    )

    _notify("Running quality validation...")
    result.validation = validate_requirements(result)
    
    _notify("Extraction complete.")

    return result


# Alias for backward compatibility with Phase 1 tests
run_phase1_pipeline = run_distill_pipeline
