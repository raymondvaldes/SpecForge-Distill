import pytest
from specforge_distill.validation import validate_requirements, ValidationIssue
from specforge_distill.pipeline import PipelineResult
from specforge_distill.models.requirement import Requirement

def test_validate_duplicate_ids():
    req1 = Requirement(id="REQ-001", text="Req 1", page=1, source_type="text", obligation="shall")
    req2 = Requirement(id="REQ-001", text="Req 2", page=2, source_type="text", obligation="shall")
    
    result = PipelineResult(
        warnings=[],
        candidates=[],
        requirements=[req1, req2],
        artifacts=[],
        metadata={}
    )
    
    summary = validate_requirements(result)
    assert len(summary.issues) == 1
    assert summary.issues[0].code == "duplicate_id"
    assert summary.issues[0].severity == "error"
    assert summary.issues[0].entity_id == "REQ-001"

def test_validate_generated_id():
    req = Requirement(id="gen-123", text="Req 1", page=1, source_type="text", obligation="shall", is_generated_id=True)
    
    result = PipelineResult(
        warnings=[],
        candidates=[],
        requirements=[req],
        artifacts=[],
        metadata={}
    )
    
    summary = validate_requirements(result)
    assert any(i.code == "generated_id" for i in summary.issues)

def test_validate_ambiguous():
    req = Requirement(
        id="REQ-001", 
        text="The system shall be fast.", 
        page=1, 
        source_type="text", 
        obligation="shall",
        is_ambiguous=True,
        ambiguity_reasons=["vague term: fast"]
    )
    
    result = PipelineResult(
        warnings=[],
        candidates=[],
        requirements=[req],
        artifacts=[],
        metadata={}
    )
    
    summary = validate_requirements(result)
    assert any(i.code == "ambiguous_requirement" for i in summary.issues)
    assert "vague term: fast" in summary.issues[0].message

def test_validate_unknown_obligation():
    req = Requirement(id="REQ-001", text="The system exists.", page=1, source_type="text", obligation="unknown")
    
    result = PipelineResult(
        warnings=[],
        candidates=[],
        requirements=[req],
        artifacts=[],
        metadata={}
    )
    
    summary = validate_requirements(result)
    assert any(i.code == "unknown_obligation" for i in summary.issues)
