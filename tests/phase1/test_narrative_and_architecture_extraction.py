from __future__ import annotations

from specforge_distill.extract.architecture import extract_architecture_blocks
from specforge_distill.extract.narrative import extract_narrative_candidates
from specforge_distill.ingest.pdf_loader import PageTextRecord


OBLIGATION_VERBS = {"shall", "must", "required"}


def test_modal_trigger_split_and_neutral_capture() -> None:
    page = PageTextRecord(
        page_number=1,
        text=(
            "The system shall log events. The interface shall display alerts.\n\n"
            "The module provides analytics dashboards for operators."
        ),
    )

    candidates = extract_narrative_candidates([page], OBLIGATION_VERBS)

    obligation_candidates = [c for c in candidates if c.classification == "obligation"]
    neutral_candidates = [c for c in candidates if c.classification == "neutral"]

    assert len(obligation_candidates) == 2
    assert len(neutral_candidates) >= 1
    assert all(candidate.source_type == "narrative" for candidate in candidates)

    split_segments = [
        c
        for c in candidates
        if c.source_location.get("paragraph_index") == 1 and c.source_location.get("segment_index") in (1, 2)
    ]
    assert len(split_segments) == 2


def test_architecture_blocks_are_structured() -> None:
    page = PageTextRecord(
        page_number=2,
        text=(
            "3 System Architecture\n"
            "The architecture uses redundant controllers and a safety bus.\n"
            "Interfaces are separated by trust boundary.\n"
            "\n"
            "4 Operational Concept\n"
            "Operators monitor all nodes."
        ),
    )

    blocks = extract_architecture_blocks([page])

    assert len(blocks) == 1
    block = blocks[0]
    assert block.section.startswith("3 System Architecture")
    assert "redundant controllers" in block.content
    assert block.page == 2
