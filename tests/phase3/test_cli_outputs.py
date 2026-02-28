"""Integration tests for CLI output behavior."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from specforge_distill.cli import main
from specforge_distill.pipeline import PipelineResult


@pytest.fixture
def mock_pipeline_result():
    mock_result = MagicMock(spec=PipelineResult)
    mock_result.warnings = []
    mock_result.candidates = []
    mock_result.requirements = []
    mock_result.artifacts = []
    mock_result.metadata = {"taxonomy_version": "1.0", "source_pdf": "test_spec.pdf"}
    return mock_result


@pytest.fixture
def dummy_pdf(tmp_path):
    pdf_file = tmp_path / "test_spec.pdf"
    pdf_file.write_text("%PDF-1.4")
    return pdf_file


def test_cli_default_output_directory(dummy_pdf, mock_pipeline_result):
    """Verify default directory creation next to a mock PDF."""
    with patch("specforge_distill.cli.run_distill_pipeline", return_value=mock_pipeline_result):
        exit_code = main(["distill", str(dummy_pdf)])
        assert exit_code == 0

    expected_dir = dummy_pdf.parent / "test_spec_distilled"
    assert expected_dir.exists()
    assert expected_dir.is_dir()
    assert (expected_dir / "full.md").exists()
    assert (expected_dir / "requirements.md").exists()
    assert (expected_dir / "architecture.md").exists()
    assert (expected_dir / "manifest.json").exists()
    assert "## Requirements" in (expected_dir / "full.md").read_text(encoding="utf-8")
    assert (expected_dir / "requirements.md").read_text(encoding="utf-8") == "_No requirements found._"


def test_cli_output_directory_override(dummy_pdf, mock_pipeline_result, tmp_path):
    """Verify -o override behavior."""
    custom_output = tmp_path / "custom_results"

    with patch("specforge_distill.cli.run_distill_pipeline", return_value=mock_pipeline_result):
        exit_code = main(["distill", str(dummy_pdf), "-o", str(custom_output)])
        assert exit_code == 0

    assert custom_output.exists()
    assert custom_output.is_dir()
    assert (custom_output / "full.md").exists()
    assert (custom_output / "requirements.md").exists()
    assert (custom_output / "architecture.md").exists()
    assert (custom_output / "manifest.json").exists()


def test_cli_allow_external_ai_flag(dummy_pdf, mock_pipeline_result):
    """Verify --allow-external-ai flag is accepted (even if no-op)."""
    with patch("specforge_distill.cli.run_distill_pipeline", return_value=mock_pipeline_result):
        exit_code = main(["distill", str(dummy_pdf), "--allow-external-ai"])
        assert exit_code == 0
