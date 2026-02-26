from __future__ import annotations

from specforge_distill.extract.captions import extract_caption_candidates
from specforge_distill.extract.merge import link_equivalent_candidates
from specforge_distill.extract.tables import extract_table_candidates_from_rows
from specforge_distill.ingest.pdf_loader import PageTextRecord
from specforge_distill.models.candidates import Candidate


OBLIGATION_VERBS = {"shall", "must", "required"}


def test_table_requirements_are_extracted_with_cell_origin() -> None:
    rows = [
        ["ID", "Requirement"],
        ["REQ-1", "The controller shall encrypt telemetry."],
        ["NOTE", "The control room display layout."],
    ]

    candidates = extract_table_candidates_from_rows(
        page_number=3,
        table_id="p3_t1",
        rows=rows,
        obligation_verbs=OBLIGATION_VERBS,
    )

    assert candidates
    assert all(candidate.source_type == "table_cell" for candidate in candidates)
    assert all("cell_ref" in candidate.source_location for candidate in candidates)
    assert any(candidate.classification == "obligation" for candidate in candidates)


def test_caption_context_candidates_include_flags() -> None:
    page = PageTextRecord(
        page_number=4,
        text=(
            "Figure 5: Backup behavior\n"
            "The backup path should remain available during maintenance."
        ),
    )

    candidates = extract_caption_candidates([page], OBLIGATION_VERBS)

    assert len(candidates) == 1
    assert candidates[0].source_type == "caption_context"
    assert "unknown_obligation_verb" in candidates[0].flags


def test_merge_links_equivalent_statements_without_deduping() -> None:
    text = "The gateway shall authenticate all sessions."
    candidates = [
        Candidate(
            id="cand-narrative-001",
            text=text,
            source_type="narrative",
            page=1,
            classification="obligation",
        ),
        Candidate(
            id="cand-table-001",
            text=text,
            source_type="table_cell",
            page=1,
            classification="obligation",
        ),
    ]

    link_equivalent_candidates(candidates)

    assert len(candidates) == 2
    assert candidates[0].links and candidates[1].links
    assert candidates[0].links[0].target_id == "cand-table-001"
    assert candidates[1].links[0].target_id == "cand-narrative-001"
