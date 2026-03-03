
import pytest
from specforge_distill.extract.tables import extract_table_candidates
from specforge_distill.extract.captions import extract_caption_candidates
from specforge_distill.ingest.pdf_loader import PageTextRecord

def test_table_candidates_flag_unknown_obligation_verbs():
    # Adding a modal verb 'shall' so it's captured under new strict rules
    rows = [
        ["ID", "Requirement"],
        ["1", "The system shall ought to log events."]
    ]
    # 'shall' triggers capture, 'ought' triggers the flag
    candidates = extract_table_candidates(
        "dummy.pdf", 
        {"shall"}, 
        table_rows_by_page={1: rows}
    )
    assert len(candidates) == 1
    assert "unknown_obligation_verb" in candidates[0].flags

def test_caption_context_candidates_include_flags():
    # Adding 'shall' to trigger capture
    pages = [
        PageTextRecord(
            page_number=1,
            text="Figure 1-1: The interface shall expected to display status.",
            image_count=0
        )
    ]
    # 'shall' triggers capture, 'expected' triggers flag
    candidates = extract_caption_candidates(pages, {"shall"})
    assert len(candidates) == 1
    assert "unknown_obligation_verb" in candidates[0].flags

def test_vcrm_header_switching_logic():
    rows = [
        ["Req ID", "Requirement Text", "Verification Method"],
        ["REQ-01", "The system shall provide power.", "Test"]
    ]
    candidates = extract_table_candidates(
        "dummy.pdf",
        {"shall"},
        table_rows_by_page={1: rows}
    )
    # VCRM processor merges columns
    assert len(candidates) == 1
    assert "REQ-01 | The system shall provide power. | Test" in candidates[0].text
    assert "vcrm_context" in candidates[0].flags
