"""Acceptance tests for Requirement Modeling and Normalization (Phase 2)."""

import pytest
import yaml
from pathlib import Path
from specforge_distill.models.candidates import Candidate
from specforge_distill.pipeline import normalize_requirements

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "requirements.yaml"

def load_fixtures():
    with open(FIXTURE_PATH, "r") as f:
        return yaml.safe_load(f)["requirements"]

@pytest.mark.parametrize("fixture", load_fixtures())
def test_requirement_normalization(fixture):
    """Verify that various text patterns are correctly normalized into Requirements."""
    # Setup candidate
    cand = Candidate(
        id=fixture.get("id", "test-id"),
        text=fixture["text"],
        source_type="narrative",
        page=fixture.get("page", 1)
    )
    
    # Run normalization
    reqs = normalize_requirements([cand])
    assert len(reqs) == 1
    req = reqs[0]
    
    # Verify ID resolution
    if "expected_id" in fixture:
        assert req.id == fixture["expected_id"]
        
    # Verify obligation classification
    if "expected_obligation" in fixture:
        assert req.obligation == fixture["expected_obligation"]
        
    # Verify ambiguity flagging
    if "is_ambiguous" in fixture:
        assert req.is_ambiguous == fixture["is_ambiguous"]
        
    # Verify ambiguity reasons if applicable
    if fixture.get("is_ambiguous") and "ambiguity_reasons" in fixture:
        for expected_reason in fixture["ambiguity_reasons"]:
            assert expected_reason in req.ambiguity_reasons

def test_id_stability():
    """Verify that anonymous requirements get stable IDs across runs."""
    text = "The system shall be stable."
    page = 10
    source = "narrative"
    
    cand1 = Candidate(id="tmp1", text=text, page=page, source_type=source)
    cand2 = Candidate(id="tmp2", text=text, page=page, source_type=source)
    
    req1 = normalize_requirements([cand1])[0]
    req2 = normalize_requirements([cand2])[0]
    
    assert req1.id == req2.id
    assert req1.id.startswith("req-narrative-010-")

def test_vcrm_attribute_existence():
    """Verify that VCRM attributes are present in the Requirement model."""
    cand = Candidate(id="1", text="Shall", page=1, source_type="narrative")
    req = normalize_requirements([cand])[0]
    
    assert hasattr(req, "vcrm")
    assert req.vcrm.method is None
    assert req.vcrm.rationale is None
