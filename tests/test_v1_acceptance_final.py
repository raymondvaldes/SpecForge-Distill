from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from specforge_distill.cli import main as cli_main
from specforge_distill.pipeline import PipelineResult
from specforge_distill.models.requirement import Requirement, InteropMetadata
from specforge_distill.models.artifacts import ArtifactBlock

def create_v1_mock_result() -> PipelineResult:
    """Create a mock PipelineResult that satisfies all v1 requirements."""
    req = Requirement(
        id="REQ-001",
        text="The system shall provide telemetry.",
        page=1,
        source_type="narrative",
        obligation="shall",
        interop=InteropMetadata(mapping_status="unmapped")
    )
    art = ArtifactBlock(
        id="art-1",
        section="Overview",
        content="Architecture description.",
        page=1,
        interop=InteropMetadata(mapping_status="unmapped")
    )
    return PipelineResult(
        warnings=[],
        candidates=[],
        requirements=[req],
        artifacts=[art],
        metadata={
            "source_pdf": "sample-digital.pdf",
            "taxonomy_version": "2026.02"
        }
    )

def test_v1_full_acceptance(tmp_path: Path) -> None:
    """
    Comprehensive end-to-end acceptance test for v1.0.0 using mocks.
    """
    source_pdf = tmp_path / "sample-digital.pdf"
    source_pdf.write_bytes(b"%PDF-1.4\n")
        
    out_dir = tmp_path / "v1_acceptance_distilled"
    
    mock_result = create_v1_mock_result()
    
    with patch("specforge_distill.cli.run_distill_pipeline", return_value=mock_result):
        exit_code = cli_main(["distill", str(source_pdf), "-o", str(out_dir)])
    
    assert exit_code == 0
    assert out_dir.exists()
    
    # Verify Output Files
    for f in ["full.md", "requirements.md", "architecture.md", "manifest.json"]:
        assert (out_dir / f).exists()
        
    # Verify Manifest
    manifest = json.loads((out_dir / "manifest.json").read_text())
    assert manifest["manifest_version"] == "1.0.0"
    assert len(manifest["entities"]) == 2
    
    # Verify Interop Hooks
    for entity in manifest["entities"]:
        assert entity["interop"]["mapping_status"] == "unmapped"
        
    # Verify Requirements Markdown
    reqs_md = (out_dir / "requirements.md").read_text()
    assert "REQ-001" in reqs_md
    assert "**Obligation:** `SHALL`" in reqs_md
    assert "(p. 1)" in reqs_md
    
    print(f"\nv1.0.0 Acceptance Mocked Passed")
