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


def test_no_modal_keeps_requirement_adjacent_paragraph_unsplit() -> None:
    page = PageTextRecord(
        page_number=1,
        text="The system provides telemetry updates. It supports diagnostics and audit review.",
    )

    candidates = extract_narrative_candidates([page], OBLIGATION_VERBS)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.classification == "neutral"
    assert candidate.source_location["segment_index"] == 1
    assert "telemetry updates" in candidate.text
    assert "diagnostics" in candidate.text


def test_unknown_obligation_flag_is_preserved_for_narrative_candidates() -> None:
    page = PageTextRecord(
        page_number=1,
        text="The system should retain execution logs for 30 days.",
    )

    candidates = extract_narrative_candidates([page], OBLIGATION_VERBS)

    assert len(candidates) == 1
    assert candidates[0].classification == "neutral"
    assert "unknown_obligation_verb" in candidates[0].flags


def test_context_window_respects_maximum_character_bound() -> None:
    long_paragraph = (
        "The system should collect and preserve detailed telemetry data for delayed analysis "
        "during post-event reconstruction and operator review cycles."
    )
    page = PageTextRecord(page_number=1, text=long_paragraph)

    candidates = extract_narrative_candidates([page], OBLIGATION_VERBS, context_chars=25)

    assert len(candidates) == 1
    assert candidates[0].context_window == long_paragraph[:25]


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


def test_architecture_extractor_flushes_multiple_sections() -> None:
    page = PageTextRecord(
        page_number=3,
        text=(
            "1 System Architecture\n"
            "Logical decomposition defines module boundaries.\n"
            "\n"
            "2 Physical Architecture\n"
            "Redundant compute units run in active-passive mode."
        ),
    )

    blocks = extract_architecture_blocks([page])

    assert len(blocks) == 2
    assert blocks[0].section.startswith("1 System Architecture")
    assert blocks[1].section.startswith("2 Physical Architecture")
