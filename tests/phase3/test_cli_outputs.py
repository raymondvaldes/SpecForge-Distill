"""Integration tests for CLI output behavior."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from specforge_distill.cli import main
from specforge_distill.pipeline import PipelineResult


pytestmark = pytest.mark.fast_ivv


def _make_mock_pipeline_result(*, source_pdf: str = "test_spec.pdf") -> PipelineResult:
    mock_result = MagicMock(spec=PipelineResult)
    mock_result.warnings = []
    mock_result.candidates = []
    mock_result.requirements = []
    mock_result.artifacts = []
    mock_result.metadata = {"taxonomy_version": "1.0", "source_pdf": source_pdf}
    
    # Validation mock
    mock_validation = MagicMock()
    mock_validation.to_dict.return_value = {"issues": [], "totals": {"errors": 0, "warnings": 0, "info": 0}}
    mock_result.validation = mock_validation
    
    return mock_result


@pytest.fixture
def mock_pipeline_result():
    return _make_mock_pipeline_result()


@pytest.fixture
def dummy_pdf(tmp_path):
    pdf_file = tmp_path / "test_spec.pdf"
    pdf_file.write_text("%PDF-1.4")
    return pdf_file


@pytest.fixture
def dummy_pdf_pair(tmp_path):
    first = tmp_path / "b_spec.pdf"
    second = tmp_path / "a_spec.pdf"
    first.write_text("%PDF-1.4")
    second.write_text("%PDF-1.4")
    return first, second


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


def test_cli_batch_default_output_directory(
    dummy_pdf_pair,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Verify multi-file input uses the deterministic default batch root."""
    first, second = dummy_pdf_pair
    monkeypatch.chdir(tmp_path)

    with patch(
        "specforge_distill.cli.run_distill_pipeline",
        side_effect=[
            _make_mock_pipeline_result(source_pdf=first.name),
            _make_mock_pipeline_result(source_pdf=second.name),
        ],
    ):
        exit_code = main(["distill", str(first), str(second)])

    batch_root = tmp_path / "specforge_distill_batch_output"
    summary_path = batch_root / "batch-summary.json"

    assert exit_code == 0
    assert summary_path.exists()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["status"] == "ok"
    assert payload["totals"]["succeeded"] == 2
    assert payload["totals"]["failed"] == 0


def test_cli_batch_input_dir_is_sorted_and_writes_summary(tmp_path: Path):
    """Verify directory-driven batch mode sorts inputs deterministically."""
    input_dir = tmp_path / "inputs"
    input_dir.mkdir()
    beta_pdf = input_dir / "b.pdf"
    alpha_pdf = input_dir / "a.pdf"
    beta_pdf.write_text("%PDF-1.4")
    alpha_pdf.write_text("%PDF-1.4")
    batch_root = tmp_path / "batch-out"
    observed_names: list[str] = []

    def _fake_run(pdf_path: Path, *, dry_run: bool, min_chars_per_page: int, progress_callback=None):
        observed_names.append(pdf_path.name)
        return _make_mock_pipeline_result(source_pdf=pdf_path.name)

    with patch("specforge_distill.cli.run_distill_pipeline", side_effect=_fake_run):
        exit_code = main(["distill", "--input-dir", str(input_dir), "-o", str(batch_root)])

    assert exit_code == 0
    assert observed_names == ["a.pdf", "b.pdf"]

    payload = json.loads((batch_root / "batch-summary.json").read_text(encoding="utf-8"))
    assert [Path(item["source"]).name for item in payload["items"]] == ["a.pdf", "b.pdf"]
    assert all(Path(item["output_dir"]).exists() for item in payload["items"])


def test_cli_batch_invalid_mixed_invocation_returns_error(
    dummy_pdf: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Verify directory mode and explicit PDF paths remain mutually exclusive."""
    input_dir = tmp_path / "inputs"
    input_dir.mkdir()

    exit_code = main(["distill", str(dummy_pdf), "--input-dir", str(input_dir)])
    io = capsys.readouterr()

    assert exit_code == 2
    assert "--input-dir cannot be combined with explicit PDF paths" in io.err


def test_cli_batch_partial_failure_returns_nonzero_and_preserves_successful_output(
    dummy_pdf_pair,
    tmp_path: Path,
):
    """Verify mixed batch outcomes preserve successes and write an aggregate summary."""
    first, second = dummy_pdf_pair
    batch_root = tmp_path / "batch"

    def _fake_run(pdf_path: Path, *, dry_run: bool, min_chars_per_page: int, progress_callback=None):
        if pdf_path == first:
            return _make_mock_pipeline_result(source_pdf=pdf_path.name)
        raise RuntimeError("corrupt pdf")

    with patch("specforge_distill.cli.run_distill_pipeline", side_effect=_fake_run):
        exit_code = main(["distill", str(first), str(second), "-o", str(batch_root)])

    assert exit_code == 5

    payload = json.loads((batch_root / "batch-summary.json").read_text(encoding="utf-8"))
    assert payload["status"] == "partial_failure"
    assert payload["totals"]["succeeded"] == 1
    assert payload["totals"]["failed"] == 1

    successful_item = next(item for item in payload["items"] if item["status"] == "ok")
    failed_item = next(item for item in payload["items"] if item["status"] == "failed")

    assert Path(successful_item["manifest_path"]).exists()
    assert failed_item["failure_class"] == "pdf_processing_failure"
    assert failed_item["detail"] == "corrupt pdf"


def test_cli_batch_dry_run_emits_aggregate_json(
    dummy_pdf_pair,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Verify batch dry-run emits the aggregate JSON contract without writing files."""
    first, second = dummy_pdf_pair
    batch_root = tmp_path / "batch"

    with patch(
        "specforge_distill.cli.run_distill_pipeline",
        side_effect=[
            _make_mock_pipeline_result(source_pdf=first.name),
            _make_mock_pipeline_result(source_pdf=second.name),
        ],
    ):
        exit_code = main(["distill", str(first), str(second), "--dry-run", "-o", str(batch_root)])

    io = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(io.out)
    assert payload["mode"] == "batch-dry-run"
    assert payload["dry_run"] is True
    assert payload["summary_path"] is None
    assert payload["totals"]["sources"] == 2
    assert not (batch_root / "batch-summary.json").exists()
