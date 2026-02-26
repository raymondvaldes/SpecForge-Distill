from __future__ import annotations

from pathlib import Path

import pytest

from specforge_distill.ingest.pdf_loader import PageTextRecord
from specforge_distill.models.candidates import Candidate
from specforge_distill.pipeline import run_phase1_pipeline
from specforge_distill.provenance.linker import link_candidate_provenance
from specforge_distill.provenance.models import Citation


def _sample_pages() -> list[PageTextRecord]:
    return [
        PageTextRecord(
            page_number=1,
            text=(
                "2 System Architecture\n"
                "The system shall sustain primary mission during disruption.\n"
                "Figure 2: Fallback behavior\n"
                "The fallback path should remain operational."
            ),
        ),
        PageTextRecord(page_number=2, text=""),
    ]


def test_provenance_model_requires_page_anchor() -> None:
    with pytest.raises(ValueError):
        Citation(page=0, source_path="input.pdf", anchor="invalid")


def test_all_channels_emit_cited_entities(tmp_path: Path) -> None:
    fake_pdf = tmp_path / "phase1.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n%placeholder\n")

    result = run_phase1_pipeline(
        fake_pdf,
        page_records=_sample_pages(),
        table_rows_by_page={1: [["Requirement", "Subsystem shall validate signatures."]]},
        min_chars_per_page=20,
    )

    source_types = {candidate.source_type for candidate in result.candidates}
    assert {"narrative", "table_cell", "caption_context"}.issubset(source_types)

    assert result.artifacts
    assert all(candidate.provenance is not None for candidate in result.candidates)
    assert all(artifact.provenance is not None for artifact in result.artifacts)


def test_missing_page_anchor_fails_candidate_linking() -> None:
    candidate = Candidate(
        id="bad-candidate",
        text="The system shall log faults.",
        source_type="narrative",
        page=0,
    )

    with pytest.raises(ValueError):
        link_candidate_provenance([candidate], "source.pdf")
