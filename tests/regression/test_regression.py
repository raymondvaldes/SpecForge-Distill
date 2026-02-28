import pytest
import yaml
from pathlib import Path
from specforge_distill.pipeline import run_distill_pipeline
from specforge_distill.ingest.pdf_loader import PageTextRecord

FIXTURE_DIR = Path(__file__).parent / "fixtures"

def load_fixture(fixture_name):
    with open(FIXTURE_DIR / fixture_name, "r") as f:
        return yaml.safe_load(f)

def verify_result(result, expected, case_name):
    # Verify requirements
    expected_reqs = expected.get("requirements", [])
    assert len(result.requirements) == len(expected_reqs), \
        f"Case '{case_name}': Requirement count mismatch. Expected {len(expected_reqs)}, got {len(result.requirements)}"
    
    for i, exp_req in enumerate(expected_reqs):
        actual_req = result.requirements[i]
        if "text" in exp_req:
            assert exp_req["text"] in actual_req.text, \
                f"Case '{case_name}': Req {i} text mismatch. Expected substring '{exp_req['text']}', got '{actual_req.text}'"
        if "obligation" in exp_req:
            assert actual_req.obligation == exp_req["obligation"], \
                f"Case '{case_name}': Req {i} obligation mismatch. Expected '{exp_req['obligation']}', got '{actual_req.obligation}'"
        if "is_ambiguous" in exp_req:
            assert actual_req.is_ambiguous == exp_req["is_ambiguous"], \
                f"Case '{case_name}': Req {i} ambiguity mismatch. Expected {exp_req['is_ambiguous']}, got {actual_req.is_ambiguous}"
        if "vcrm" in exp_req:
            actual_vcrm = actual_req.vcrm.model_dump() if hasattr(actual_req.vcrm, "model_dump") else actual_req.vcrm.dict()
            for k, v in exp_req["vcrm"].items():
                assert actual_vcrm.get(k) == v, \
                    f"Case '{case_name}': Req {i} VCRM {k} mismatch. Expected '{v}', got '{actual_vcrm.get(k)}'"

    # Verify artifacts
    expected_arts = expected.get("artifacts", [])
    assert len(result.artifacts) == len(expected_arts), \
        f"Case '{case_name}': Artifact count mismatch. Expected {len(expected_arts)}, got {len(result.artifacts)}"

@pytest.mark.parametrize("fixture_file", [
    "complex_requirements.yaml",
    "complex_tables.yaml",
    "varied_docs.yaml",
])
def test_regression_cases(fixture_file):
    """
    Requirements: REQ-02, REQ-04, CLI-03
    Ensures that the pipeline correctly handles complex document variations including
    VCRM tables, non-standard ID formats, and spread requirements by comparing
    actual output against 'golden' reference fixtures.
    """
    fixture_path = FIXTURE_DIR / fixture_file
    if not fixture_path.exists():
        pytest.skip(f"Fixture file not found: {fixture_file}")
        
    fixture_data = load_fixture(fixture_file)
    
    for case in fixture_data["cases"]:
        name = case["name"]
        pages_data = case.get("pages", [])
        tables_data = case.get("tables", {})
        expected = case["expected"]
        
        page_records = [
            PageTextRecord(page_number=p["number"], text=p["text"])
            for p in pages_data
        ]
        
        # Table data in fixture is dict[page_int, list[list[str]]]
        # But YAML keys might be strings, so convert to int
        table_rows_by_page = {int(k): v for k, v in tables_data.items()}
        
        result = run_distill_pipeline(
            "mock.pdf",
            page_records=page_records,
            table_rows_by_page=table_rows_by_page
        )
        
        verify_result(result, expected, name)
