
import pytest
from pathlib import Path
from specforge_distill.pipeline import run_distill_pipeline
from specforge_distill.ingest.pdf_loader import PageTextRecord

def test_note_merging_and_strict_extraction():
    # 1. Mock PDF pages with notes and low-obligation verbs
    pages = [
        PageTextRecord(
            page_number=1,
            text="""
            REQ-001: The system shall provide a user interface. 
            Note: This includes mobile and web views.
            
            This is a neutral sentence that ought to be ignored.
            
            REQ-002: Users may configure their profiles.
            
            REQ-003: The database must backup daily. 
            Notes: Backups should be stored off-site.
            """,
            image_count=0
        )
    ]

    # 2. Run the pipeline
    result = run_distill_pipeline("dummy.pdf", page_records=pages, table_rows_by_page={})

    # 3. Assertions
    reqs = result.requirements
    print(f"Captured {len(reqs)} requirements:")
    for r in reqs:
        print(f"  - '{r.text}'")
    
    # Check that REQ-001 includes its Note
    req_001 = next(r for r in reqs if "REQ-001" in r.text)
    assert "Note: This includes mobile and web views." in req_001.text
    assert "shall provide a user interface." in req_001.text
    
    # Check that REQ-002 (may) is ignored because it's no longer in taxonomy
    assert not any("REQ-002" in r.text or "may configure" in r.text for r in reqs)
    
    # Check that REQ-003 includes its Notes
    req_003 = next(r for r in reqs if "REQ-003" in r.text)
    assert "Notes: Backups should be stored off-site." in req_003.text
    
    # Check that neutral sentences are ignored
    assert not any("neutral sentence" in r.text for r in reqs)
    
    print("Success: Notes merged and strict extraction verified.")

if __name__ == "__main__":
    test_note_merging_and_strict_extraction()
