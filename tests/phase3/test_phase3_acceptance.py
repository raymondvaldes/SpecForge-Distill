"""Phase 3 Acceptance Suite: End-to-end verification of output packaging and interop hooks."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from specforge_distill.cli import main
from specforge_distill.pipeline import PipelineResult
from specforge_distill.models.requirement import Requirement, InteropMetadata as ReqInterop
from specforge_distill.models.artifacts import ArtifactBlock, InteropMetadata as ArtInterop

@pytest.fixture
def complex_pipeline_result():
    """Create a mock PipelineResult with requirements and artifacts."""
    mock_result = MagicMock(spec=PipelineResult)
    mock_result.warnings = []
    
    # Create a few requirements
    req1 = Requirement(
        id="REQ-001",
        text="The system shall process data.",
        obligation="shall",
        page=1,
        source_type="narrative_text",
        interop=ReqInterop(candidate_concept="ProcessData")
    )
    req2 = Requirement(
        id="REQ-002",
        text="The system must be secure.",
        obligation="must",
        page=2,
        source_type="narrative_text",
        interop=ReqInterop(mapping_status="mapped")
    )
    mock_result.requirements = [req1, req2]
    
    # Create an architecture block
    art1 = ArtifactBlock(
        id="art-001-abc",
        section="System Architecture",
        content="Overview of the system structure.",
        page=1,
        interop=ArtInterop(target="sysmlv2-custom")
    )
    mock_result.artifacts = [art1]
    
    mock_result.metadata = {
        "source_pdf": "test_spec.pdf",
        "taxonomy_version": "1.0.0"
    }
    
    return mock_result

@pytest.fixture
def dummy_pdf(tmp_path):
    pdf_file = tmp_path / "test_spec.pdf"
    pdf_file.write_text("%PDF-1.4")
    return pdf_file

def test_phase3_output_package_acceptance(dummy_pdf, complex_pipeline_result, tmp_path):
    """
    End-to-end test of the Phase 3 output generation.
    - Verifies all 4 files are created.
    - Verifies manifest content and links.
    - Verifies interop metadata presence.
    """
    output_dir = tmp_path / "distilled_output"
    
    with patch("specforge_distill.cli.run_distill_pipeline", return_value=complex_pipeline_result):
        # Run the CLI
        exit_code = main(["distill", str(dummy_pdf), "-o", str(output_dir)])
        assert exit_code == 0
        
        # 1. Verify existence of all 4 output files
        expected_files = ["full.md", "requirements.md", "architecture.md", "manifest.json"]
        for filename in expected_files:
            assert (output_dir / filename).exists(), f"Missing expected file: {filename}"
            
        # 2. Verify manifest correctly links all requirements
        manifest_path = output_dir / "manifest.json"
        with open(manifest_path, "r") as f:
            manifest_data = json.load(f)
            
        assert manifest_data["manifest_version"] == "1.0.0"
        assert manifest_data["model_interop_target"] == "sysmlv2-future"
        
        entities = manifest_data["entities"]
        assert len(entities) == 3  # 2 requirements + 1 artifact
        
        req_ids = [e["id"] for e in entities if e["type"] == "requirement"]
        assert "REQ-001" in req_ids
        assert "REQ-002" in req_ids
        
        art_ids = [e["id"] for e in entities if e["type"] == "artifact"]
        assert "art-001-abc" in art_ids
        
        # 3. Verify IDs in markdown files match manifest
        req_md_content = (output_dir / "requirements.md").read_text()
        assert "REQ-001" in req_md_content
        assert "REQ-002" in req_md_content
        
        art_md_content = (output_dir / "architecture.md").read_text()
        assert "art-001-abc" in art_md_content
        
        # 4. Verify all requirement entities have the expected attributes
        # Specifically check interop metadata in manifest
        req1_entry = next(e for e in entities if e["id"] == "REQ-001")
        assert req1_entry["interop"]["candidate_concept"] == "ProcessData"
        assert req1_entry["interop"]["target"] == "sysmlv2-future"
        
        art1_entry = next(e for e in entities if e["id"] == "art-001-abc")
        assert art1_entry["interop"]["target"] == "sysmlv2-custom"

def test_manifest_consistency_with_markdown(dummy_pdf, complex_pipeline_result, tmp_path):
    """
    Verification check: Ensure every requirement in the markdown files 
    has a corresponding entry in the manifest.json with matching IDs.
    """
    output_dir = tmp_path / "consistency_test"
    
    with patch("specforge_distill.cli.run_distill_pipeline", return_value=complex_pipeline_result):
        main(["distill", str(dummy_pdf), "-o", str(output_dir)])
        
        manifest_path = output_dir / "manifest.json"
        with open(manifest_path, "r") as f:
            manifest_data = json.load(f)
            
        manifest_req_ids = {e["id"] for e in manifest_data["entities"] if e["type"] == "requirement"}
        
        # Crude check for IDs in markdown (assuming they appear as plain text/headers)
        req_md_content = (output_dir / "requirements.md").read_text()
        for rid in manifest_req_ids:
            assert rid in req_md_content, f"Requirement {rid} in manifest but not in markdown"
