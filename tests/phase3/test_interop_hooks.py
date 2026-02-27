import pytest
from specforge_distill.models.requirement import Requirement, InteropMetadata as ReqInterop
from specforge_distill.models.artifacts import ArtifactBlock, InteropMetadata as ArtInterop
from specforge_distill.models.candidates import Candidate
from specforge_distill.render.manifest import ManifestWriter
from specforge_distill.pipeline import PipelineResult

def test_requirement_interop_serialization():
    candidate = Candidate(id="REQ-001", text="Test req", page=1, source_type="text")
    req = Requirement.from_candidate(candidate)
    
    assert req.interop.target == "sysmlv2-future"
    assert req.interop.mapping_status == "unmapped"
    
    data = req.to_dict()
    assert "interop" in data
    assert data["interop"]["target"] == "sysmlv2-future"

def test_artifact_interop_serialization():
    art = ArtifactBlock(id="ART-001", section="Intro", content="Some text", page=1)
    
    assert art.interop.target == "sysmlv2-future"
    
    data = art.to_dict()
    assert "interop" in data
    assert data["interop"]["target"] == "sysmlv2-future"

def test_manifest_interop_serialization():
    candidate = Candidate(id="REQ-001", text="Test req", page=1, source_type="text")
    req = Requirement.from_candidate(candidate)
    art = ArtifactBlock(id="ART-001", section="Intro", content="Some text", page=1)
    
    result = PipelineResult(
        warnings=[],
        candidates=[candidate],
        requirements=[req],
        artifacts=[art],
        metadata={"source_pdf": "test.pdf"}
    )
    
    writer = ManifestWriter(result, {"requirements": "reqs.md", "architecture": "arch.md"})
    manifest = writer.generate()
    
    assert manifest.model_interop_target == "sysmlv2-future"
    assert len(manifest.entities) == 2
    
    for entity in manifest.entities:
        assert "target" in entity.interop
        assert entity.interop["target"] == "sysmlv2-future"
