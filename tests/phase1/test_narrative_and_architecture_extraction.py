
import pytest
from specforge_distill.extract.narrative import extract_narrative_candidates
from specforge_distill.ingest.pdf_loader import PageTextRecord

def test_modal_trigger_split_and_neutral_capture():
    # Now we require a modal for EVERY candidate
    pages = [
        PageTextRecord(
            page_number=1,
            text="The system shall log events. The interface shall display alerts.",
            image_count=0
        )
    ]
    # 'shall' is in the taxonomy
    candidates = extract_narrative_candidates(pages, {"shall"})
    assert len(candidates) == 2
    assert candidates[0].text == "The system shall log events."
    assert candidates[1].text == "The interface shall display alerts."

def test_no_modal_ignores_neutral_paragraph():
    pages = [
        PageTextRecord(
            page_number=1,
            text="The system provides a log file.",
            image_count=0
        )
    ]
    # No modal verb -> should be ignored now
    candidates = extract_narrative_candidates(pages, {"shall"})
    assert len(candidates) == 0

def test_unknown_obligation_flag_is_preserved_for_narrative_candidates():
    pages = [
        PageTextRecord(
            page_number=1,
            text="The system shall ought to log events.",
            image_count=0
        )
    ]
    # 'shall' is the modal that triggers capture
    # 'ought' is in _UNKNOWN_OBLIGATION_VERBS
    candidates = extract_narrative_candidates(pages, {"shall"})
    assert len(candidates) == 1
    assert "unknown_obligation_verb" in candidates[0].flags

def test_context_window_respects_maximum_character_bound():
    pages = [
        PageTextRecord(
            page_number=1,
            text="The system shall log events and this is a very long sentence that should be truncated in the context window if we set a small limit.",
            image_count=0
        )
    ]
    candidates = extract_narrative_candidates(pages, {"shall"}, context_chars=20)
    assert len(candidates) == 1
    assert len(candidates[0].context_window) <= 20
