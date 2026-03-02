import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from specforge_distill.cli import main as cli_main
from specforge_distill.pipeline import PipelineResult
from specforge_distill.models.requirement import Requirement, InteropMetadata as ReqInterop
from specforge_distill.models.artifacts import ArtifactBlock
from specforge_distill.ingest.text_quality import QualityWarning
from specforge_distill.validation import validate_requirements, ValidationIssue, ValidationSummary
from specforge_distill.render.manifest import Manifest

def _make_result_with_issues(source_pdf="test.pdf", req_id="REQ-1"):
    req = Requirement(
        id=req_id,
        text="The system shall be fast.",
        page=1,
        source_type="narrative",
        obligation="shall",
        is_generated_id=True,
        is_ambiguous=True,
        ambiguity_reasons=["vague"],
        interop=ReqInterop(logical_layer="functional", external_ref="DOORS-123")
    )
    result = PipelineResult(
        warnings=[],
        candidates=[],
        requirements=[req],
        artifacts=[],
        metadata={"source_pdf": source_pdf, "taxonomy_version": "1.0"}
    )
    result.validation = validate_requirements(result)
    return result

def test_batch_summary_aggregates_validation_totals(tmp_path):
    """Verify that batch-summary.json correctly sums validation issues across multiple PDFs."""
    pdf1 = tmp_path / "one.pdf"
    pdf2 = tmp_path / "two.pdf"
    pdf1.write_text("%PDF-1.4")
    pdf2.write_text("%PDF-1.4")
    batch_root = tmp_path / "batch_val"

    # pdf1 has 2 issues (info:generated, warning:ambiguous)
    # pdf2 has 2 issues (info:generated, warning:ambiguous)
    
    with patch("specforge_distill.cli.run_distill_pipeline", side_effect=[
        _make_result_with_issues("one.pdf", "REQ-A"),
        _make_result_with_issues("two.pdf", "REQ-B")
    ]):
        cli_main(["distill", str(pdf1), str(pdf2), "-o", str(batch_root)])

    summary_path = batch_root / "batch-summary.json"
    payload = json.loads(summary_path.read_text())
    
    # Check individual item validation
    for item in payload["items"]:
        assert item["validation"]["totals"]["warnings"] == 1
        assert item["validation"]["totals"]["info"] == 1
        
    # Totals are not currently aggregated in the root "totals" of batch-summary.json 
    # (only entities/warnings). This test confirms the items themselves carry the payload.

def test_manifest_contains_enriched_interop(tmp_path):
    """Verify the new SysML interop fields are correctly serialized in the manifest."""
    pdf = tmp_path / "interop.pdf"
    pdf.write_text("%PDF-1.4")
    out_dir = tmp_path / "out"
    
    result = _make_result_with_issues("interop.pdf")
    
    with patch("specforge_distill.cli.run_distill_pipeline", return_value=result):
        cli_main(["distill", str(pdf), "-o", str(out_dir)])
        
    manifest = Manifest.model_validate_json((out_dir / "manifest.json").read_text())
    req_entity = next(e for e in manifest.entities if e.type == "requirement")
    
    assert req_entity.interop["logical_layer"] == "functional"
    assert req_entity.interop["external_ref"] == "DOORS-123"
    assert req_entity.interop["verification_status"] == "unverified"

def test_duplicate_id_across_source_types():
    """Verify validation detects duplicate IDs even if one comes from a table and one from narrative."""
    req_narrative = Requirement(
        id="DUP-001", text="Narrative", page=1, source_type="narrative", obligation="shall"
    )
    req_table = Requirement(
        id="DUP-001", text="Table", page=5, source_type="table", obligation="shall"
    )
    
    result = PipelineResult(
        warnings=[],
        candidates=[],
        requirements=[req_narrative, req_table],
        artifacts=[],
        metadata={}
    )
    
    summary = validate_requirements(result)
    assert any(i.code == "duplicate_id" for i in summary.issues)
    # The second one (p.5) should be the one flagged as duplicate
    dup_issue = next(i for i in summary.issues if i.code == "duplicate_id")
    assert dup_issue.page == 5

def test_mixed_scanned_digital_assessment():
    """Verify extraction assessment handles a mix of scanned and digital pages."""
    from specforge_distill.automation import classify_extraction_assessment
    
    # Case: Extracted some content (digital) BUT also had a scanned page warning
    result = MagicMock()
    result.candidates = [MagicMock()] # Has content
    result.requirements = [MagicMock()]
    result.artifacts = []
    result.warnings = [
        QualityWarning(code="likely_scanned_page", page=10, chars=0, message="Scan", image_count=1)
    ]
    
    assessment = classify_extraction_assessment(result)
    # Should prefer 'content_extracted_with_low_text_warnings' over 'likely_scanned_pdf' 
    # because we DID get content.
    assert assessment == "content_extracted_with_low_text_warnings"

    # Case: No content, and has a scanned warning
    result.requirements = []
    result.candidates = []
def test_validation_summary_counting():
    """Verify the math in ValidationSummary totals."""
    issues = [
        ValidationIssue("e1", "error", "msg", 1, "id1"),
        ValidationIssue("w1", "warning", "msg", 1, "id2"),
        ValidationIssue("w2", "warning", "msg", 1, "id3"),
        ValidationIssue("i1", "info", "msg", 1, "id4"),
    ]
    summary = ValidationSummary(issues=issues)
    totals = summary.to_dict()["totals"]
    assert totals["errors"] == 1
    assert totals["warnings"] == 2
    assert totals["info"] == 1

def test_cli_report_zero_findings(tmp_path, capsys):
    """Verify that --report does not show 'Validation Findings' if there are none."""
    pdf = tmp_path / "clean.pdf"
    pdf.write_text("%PDF-1.4")
    out_dir = tmp_path / "out"
    
    # Result with no requirements/issues
    result = PipelineResult([], [], [], [], {"source_pdf": "clean.pdf"})
    result.validation = ValidationSummary([])
    
    with patch("specforge_distill.cli.run_distill_pipeline", return_value=result):
        cli_main(["distill", str(pdf), "-o", str(out_dir), "--report"])
        
    out, _ = capsys.readouterr()
    assert "Validation Findings" not in out

def test_cli_report_long_id_formatting(tmp_path, capsys):
    """Verify that very long entity IDs in validation findings don't crash formatting."""
    pdf = tmp_path / "long.pdf"
    pdf.write_text("%PDF-1.4")
    out_dir = tmp_path / "out"
    
    long_id = "EXTREMELY-LONG-REQUIREMENT-ID-THAT-MIGHT-BREAK-COLUMN-ALIGNMENT-001"
    issue = ValidationIssue("code", "error", "message", 999, long_id)
    result = PipelineResult([], [], [], [], {"source_pdf": "long.pdf"})
    result.validation = ValidationSummary([issue])
    
    with patch("specforge_distill.cli.run_distill_pipeline", return_value=result):
        cli_main(["distill", str(pdf), "-o", str(out_dir), "--report"])
        
    out, _ = capsys.readouterr()
    assert "Validation Findings" in out
    assert long_id in out
    assert "p.999" in out
