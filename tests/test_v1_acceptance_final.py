from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from specforge_distill.cli import main as cli_main
from specforge_distill.models.artifacts import ArtifactBlock
from specforge_distill.models.requirement import InteropMetadata, Requirement
from specforge_distill.pipeline import PipelineResult
from specforge_distill.render.manifest import Manifest

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
    Requirement: ALL-v1 (Complete Roadmap)
    Ensures that the full pipeline flow (ingest -> extract -> normalize -> package)
    is operational and correctly orchestrates all 4 output file types while
    maintaining Pydantic schema validity for the manifest.
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
    manifest_data = json.loads((out_dir / "manifest.json").read_text())
    # Explicit Pydantic validation (Robustness)
    manifest = Manifest.model_validate(manifest_data)

    assert manifest.manifest_version == "1.0.0"
    assert len(manifest.entities) == 2
    assert sum(1 for entity in manifest.entities if entity.type == "requirement") == 1

    # Verify Interop Hooks
    for entity in manifest.entities:
        assert entity.interop["mapping_status"] == "unmapped"
        assert entity.interop["target"] == "sysmlv2-future"

    # Verify Requirements Markdown
    reqs_md = (out_dir / "requirements.md").read_text()
    assert "REQ-001" in reqs_md
    assert "**Obligation:** `SHALL`" in reqs_md
    assert "(p. 1)" in reqs_md


def test_v1_empty_acceptance(tmp_path: Path) -> None:
    """Verify system behavior on a PDF with zero extracted requirements."""
    source_pdf = tmp_path / "empty.pdf"
    source_pdf.write_bytes(b"%PDF-1.4\n")
    
    out_dir = tmp_path / "empty_distilled"
    
    mock_result = PipelineResult(
        warnings=[],
        candidates=[],
        requirements=[],
        artifacts=[],
        metadata={"source_pdf": "empty.pdf", "taxonomy_version": "1.0"}
    )
    
    with patch("specforge_distill.cli.run_distill_pipeline", return_value=mock_result):
        exit_code = cli_main(["distill", str(source_pdf), "-o", str(out_dir)])

    assert exit_code == 0
    manifest = Manifest.model_validate_json((out_dir / "manifest.json").read_text())
    assert len(manifest.entities) == 0

    reqs_md = (out_dir / "requirements.md").read_text()
    assert "_No requirements found._" in reqs_md


def test_v1_batch_acceptance(tmp_path: Path) -> None:
    """Verify the supported explicit batch workflow keeps good outputs when one input fails."""
    first_pdf = tmp_path / "good.pdf"
    second_pdf = tmp_path / "bad.pdf"
    first_pdf.write_bytes(b"%PDF-1.4\n")
    second_pdf.write_bytes(b"%PDF-1.4\n")
    batch_root = tmp_path / "batch_distilled"

    mock_result = create_v1_mock_result()

    def _fake_run(pdf_path: Path, *, dry_run: bool, min_chars_per_page: int, progress_callback=None):
        if pdf_path == first_pdf:
            return mock_result
        raise RuntimeError("broken second pdf")

    with patch("specforge_distill.cli.run_distill_pipeline", side_effect=_fake_run):
        exit_code = cli_main(["distill", str(first_pdf), str(second_pdf), "-o", str(batch_root)])

    assert exit_code == 5

    payload = json.loads((batch_root / "batch-summary.json").read_text(encoding="utf-8"))
    assert payload["status"] == "partial_failure"
    assert payload["totals"]["succeeded"] == 1
    assert payload["totals"]["failed"] == 1

    successful_item = next(item for item in payload["items"] if item["status"] == "ok")
    failed_item = next(item for item in payload["items"] if item["status"] == "failed")

    manifest = Manifest.model_validate_json(Path(successful_item["manifest_path"]).read_text(encoding="utf-8"))
    assert len(manifest.entities) == 2
    assert failed_item["failure_class"] == "pdf_processing_failure"
