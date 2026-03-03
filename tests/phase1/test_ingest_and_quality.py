from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path
from typing import Any
from types import SimpleNamespace

import pytest

from specforge_distill import __version__
from specforge_distill.cli import main as cli_main
from specforge_distill.ingest.pdf_loader import PageTextRecord, load_pdf_pages
from specforge_distill.ingest.text_quality import QualityWarning, assess_text_quality
from specforge_distill.models.artifacts import ArtifactBlock
from specforge_distill.models.candidates import Candidate
from specforge_distill.models.requirement import Requirement
from specforge_distill.pipeline import load_obligation_taxonomy, run_distill_pipeline
from specforge_distill.render.manifest import Manifest


pytestmark = pytest.mark.fast_ivv


class _FakePipelineResult:
    def __init__(self) -> None:
        self.warnings = [
            QualityWarning(
                code="low_text_quality",
                page=2,
                chars=3,
                image_count=0,
                message="Low text quality",
            )
        ]
        self.candidates = [
            Candidate(id="c-1", text="Text 1", source_type="narrative", page=1),
            Candidate(id="c-2", text="Text 2", source_type="narrative", page=1),
        ]
        self.requirements = [
            Requirement(id="r-1", text="Req 1", page=1, source_type="narrative", obligation="shall")
        ]
        self.artifacts = [
            ArtifactBlock(id="a-1", section="Sec 1", content="Content 1", page=1)
        ]
        self.metadata = {"taxonomy_version": "test-v1"}
        self.validation = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "warnings": [warning.to_dict() for warning in self.warnings],
            "candidates": [c.to_dict() for c in self.candidates],
            "requirements": [r.to_dict() for r in self.requirements],
            "artifacts": [a.to_dict() for a in self.artifacts],
            "metadata": dict(self.metadata),
            "validation": {"issues": [], "totals": {"errors": 0, "warnings": 0, "info": 0}},
        }


def test_loads_external_taxonomy_version() -> None:
    """
    Requirement: REQ-03 (Obligation Taxonomy)
    Ensures that the engine can load and parse an external YAML taxonomy,
    allowing for domain-specific obligation verbs (e.g. 'SHALL', 'MUST').
    """
    taxonomy = load_obligation_taxonomy()
    assert taxonomy.version == "2026.03"
    assert taxonomy.verbs == ("must", "recommended", "required", "shall", "should")


def test_load_obligation_taxonomy_falls_back_to_basic_parser(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    taxonomy_path = tmp_path / "taxonomy.yml"
    taxonomy_path.write_text(
        "\n".join(
            [
                'version: "fallback-v1"',
                "obligation_verbs:",
                "  - SHALL",
                "  - must",
                "  - must",
                '  - " required "',
            ]
        ),
        encoding="utf-8",
    )

    def _boom(_payload: str) -> dict[str, object]:
        raise RuntimeError("force fallback parser")

    monkeypatch.setitem(sys.modules, "yaml", SimpleNamespace(safe_load=_boom))

    taxonomy = load_obligation_taxonomy(taxonomy_path)
    assert taxonomy.version == "fallback-v1"
    assert taxonomy.verbs == ("must", "required", "shall")


def test_load_obligation_taxonomy_parses_nested_taxonomy_shape(tmp_path: Path) -> None:
    taxonomy_path = tmp_path / "taxonomy.yml"
    taxonomy_path.write_text(
        "\n".join(
            [
                'version: "nested-v1"',
                "taxonomy:",
                "  shall:",
                "    - SHALL",
                "    - required",
                "  should:",
                "    - recommended",
                "  may:",
                "    - optional",
            ]
        ),
        encoding="utf-8",
    )

    taxonomy = load_obligation_taxonomy(taxonomy_path)
    assert taxonomy.version == "nested-v1"
    assert taxonomy.verbs == ("optional", "recommended", "required", "shall")


@pytest.mark.parametrize("text, min_chars, expected_warning", [
    ("Short", 20, True),
    ("Exactly twenty chars", 20, False),
    ("More than twenty characters here", 20, False),
    ("", 1, True),
    ("   ", 1, True),
    ("\n\n\n", 1, True),
    ("A" * 1000, 40, False), # Long text
    ("!@#$%^&*()", 5, False), # Special characters
])
def test_quality_assessment_edge_cases(text: str, min_chars: int, expected_warning: bool) -> None:
    """
    Requirement: ING-02 (Quality Diagnostics)
    Ensures that boundary conditions (empty text, very long text, special characters) 
    are handled correctly by the text quality assessment engine without crashing.
    """
    pages = [PageTextRecord(page_number=1, text=text, image_count=0)]
    warnings = assess_text_quality(pages, min_chars_per_page=min_chars)
    
    if expected_warning:
        assert len(warnings) == 1
        assert warnings[0].page == 1
        assert warnings[0].code == "low_text_quality"
    else:
        assert len(warnings) == 0


@pytest.mark.parametrize("text, image_count, min_chars, expected_code", [
    ("Short", 0, 20, "low_text_quality"),
    ("Short", 1, 20, "likely_scanned_page"),
    ("Exactly twenty chars", 0, 20, None),
    ("Exactly twenty chars", 5, 20, None), # High text overrides image scan suspicion
    ("", 1, 1, "likely_scanned_page"),
    ("   ", 0, 1, "low_text_quality"),
])
def test_quality_assessment_scanned_vs_low_text(text: str, image_count: int, min_chars: int, expected_code: str | None) -> None:
    """
    Requirement: ING-03 (Scanned Diagnostics)
    Ensures that low-text pages are differentiated between generic low-quality 
    and likely-scanned/image-only based on presence of images.
    """
    pages = [PageTextRecord(page_number=1, text=text, image_count=image_count)]
    warnings = assess_text_quality(pages, min_chars_per_page=min_chars)
    
    if expected_code:
        assert len(warnings) == 1
        assert warnings[0].code == expected_code
        assert warnings[0].image_count == image_count
    else:
        assert len(warnings) == 0


def test_warns_on_low_text_pages() -> None:
    pages = [
        PageTextRecord(page_number=1, text="The system shall provide telemetry support.", image_count=0),
        PageTextRecord(page_number=2, text="", image_count=0),
    ]

    warnings = assess_text_quality(pages, min_chars_per_page=20)
    assert [warning.page for warning in warnings] == [2]
    assert warnings[0].code == "low_text_quality"


def test_quality_threshold_boundary_is_non_warning_at_exact_limit() -> None:
    pages = [
        PageTextRecord(page_number=1, text="x" * 20, image_count=0),
        PageTextRecord(page_number=2, text="x" * 19, image_count=0),
    ]

    warnings = assess_text_quality(pages, min_chars_per_page=20)
    assert [warning.page for warning in warnings] == [2]


def test_cli_invocation_path(tmp_path: Path) -> None:
    fake_pdf = tmp_path / "sample-digital.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n%placeholder\n")

    exit_code = cli_main(["distill", str(fake_pdf), "--dry-run"])
    assert exit_code == 0

    dry_result = run_distill_pipeline(fake_pdf, dry_run=True)
    assert dry_result.metadata["taxonomy_version"] == "2026.03"


def test_load_pdf_pages_rejects_non_pdf_bytes_immediately(tmp_path: Path) -> None:
    invalid_pdf = tmp_path / "not-really-a-pdf.pdf"
    invalid_pdf.write_bytes(b"This is not a PDF header.")

    with pytest.raises(ValueError, match="does not appear to be a PDF file"):
        load_pdf_pages(invalid_pdf)


def test_cli_missing_file_returns_error_and_nonzero(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli_main(["distill", "does-not-exist.pdf"])
    io = capsys.readouterr()

    assert exit_code == 2
    assert "error: file not found" in io.err


def test_cli_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli_main(["distill", "--version"])

    io = capsys.readouterr()

    assert excinfo.value.code == 0
    assert io.out.strip() == f"distill {__version__}"


def test_package_version_matches_pyproject() -> None:
    pyproject_data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject_data["project"]["version"] == __version__


def test_cli_requires_pdf_or_special_mode(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli_main(["distill"])
    io = capsys.readouterr()

    assert exit_code == 2
    assert "missing PDF path" in io.err


def test_cli_describe_output_json(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli_main(["distill", "--describe-output", "json"])
    io = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(io.out)
    assert payload["tool"] == "specforge-distill"
    assert payload["output_contract"]["manifest_version"] == "1.1.0"
    assert payload["output_contract"]["batch_summary_file"] == "batch-summary.json"
    assert payload["exit_codes"]["4"] == "self-test validation failure"
    assert payload["exit_codes"]["5"] == "batch completed with one or more item failures"
    assert payload["cli_contract"]["flags"]["pdf_path"]["required_in_modes"] == ["distill"]
    assert payload["cli_contract"]["flags"]["--input-dir"]["supported_in_modes"] == ["distill"]
    assert payload["cli_contract"]["flags"]["--emit-example-output"]["stdout_schema"] == "example-output"
    assert payload["cli_contract"]["response_schemas"]["batch-summary"]["type"] == "object"
    assert payload["cli_contract"]["response_schemas"]["self-test"]["type"] == "object"
    assert payload["failure_classes"]["self_test_validation_failure"]["recovery_hint"].startswith("Do not process a real PDF")
    assert payload["failure_classes"]["pdf_processing_failure"]["exit_code"] == 3
    assert payload["failure_classes"]["output_write_failure"]["exit_code"] == 3
    assert payload["failure_classes"]["batch_partial_failure"]["exit_code"] == 5
    assert payload["failure_classes"]["self_test_validation_failure"]["stderr_format"] == "json"
    assert payload["failure_classes"]["self_test_validation_failure"]["troubleshooting"]["anchor"] == "#failure-class-self-test-validation-failure"


def test_cli_emit_example_output_creates_contract_package(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = tmp_path / "example-output"

    exit_code = cli_main(["distill", "--emit-example-output", str(output_dir)])
    io = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(io.out)
    assert payload["status"] == "ok"
    assert payload["mode"] == "example-output"
    assert payload["entity_counts"]["requirements"] == 1
    assert (output_dir / "full.md").exists()
    assert (output_dir / "requirements.md").exists()
    assert (output_dir / "architecture.md").exists()
    manifest = Manifest.model_validate_json((output_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest.manifest_version == "1.1.0"
    assert manifest.entities[0].id == "EX-REQ-001"


def test_cli_self_test_reports_success(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli_main(["distill", "--self-test"])
    io = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(io.out)
    assert payload["status"] == "ok"
    assert payload["mode"] == "self-test"
    assert payload["preserved_output"] is False
    assert all(check["status"] == "ok" for check in payload["checks"])


def test_cli_self_test_reports_structured_failure(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def _boom(_output_dir=None):
        raise RuntimeError("forced self-test failure")

    monkeypatch.setattr("specforge_distill.cli.run_self_test", _boom)

    exit_code = cli_main(["distill", "--self-test"])
    io = capsys.readouterr()

    assert exit_code == 4
    payload = json.loads(io.err)
    assert payload["status"] == "failed"
    assert payload["mode"] == "self-test"
    assert payload["failure_class"] == "self_test_validation_failure"
    assert payload["recovery_hint"].startswith("Do not process a real PDF")
    assert payload["troubleshooting"]["guide"] == "docs/TROUBLESHOOTING.md"
    assert payload["troubleshooting"]["anchor"] == "#failure-class-self-test-validation-failure"
    assert payload["detail"] == "forced self-test failure"


def test_cli_writes_output_json_and_passes_runtime_args(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_pdf = tmp_path / "sample.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n%placeholder\n")
    output_dir = tmp_path / "out"
    observed: dict[str, object] = {}

    def _fake_run(pdf_path: Path, *, dry_run: bool, min_chars_per_page: int, progress_callback=None) -> _FakePipelineResult:
        observed["pdf_path"] = pdf_path
        observed["dry_run"] = dry_run
        observed["min_chars_per_page"] = min_chars_per_page
        return _FakePipelineResult()

    monkeypatch.setattr("specforge_distill.cli.run_distill_pipeline", _fake_run)

    exit_code = cli_main(
        [
            "distill",
            str(fake_pdf),
            "-o",
            str(output_dir),
            "--min-chars-per-page",
            "11",
        ]
    )
    io = capsys.readouterr()

    assert exit_code == 0
    assert observed["pdf_path"] == fake_pdf
    assert observed["dry_run"] is False
    assert observed["min_chars_per_page"] == 11

    assert "Distillation complete in" in io.out
    assert "Stats:  1 requirements, 1 architecture blocks." in io.out
    assert "warning: low text-layer quality on pages [2]" in io.err

    output_path = output_dir / "manifest.json"
    assert output_path.exists()
    saved_payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved_payload["metadata"]["taxonomy_version"] == "test-v1"


def test_cli_dry_run_does_not_write_output_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_pdf = tmp_path / "sample.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n%placeholder\n")
    output_dir = tmp_path / "out"

    monkeypatch.setattr(
        "specforge_distill.cli.run_distill_pipeline",
        lambda *_args, **_kwargs: _FakePipelineResult(),
    )

    exit_code = cli_main(["distill", str(fake_pdf), "--dry-run", "-o", str(output_dir)])

    assert exit_code == 0
    assert not (output_dir / "manifest.json").exists()


def test_cli_dry_run_reports_likely_text_layer_issue(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_pdf = tmp_path / "scan-like.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n%placeholder\n")

    class _NoOutputResult:
        def __init__(self) -> None:
            self.warnings = [
                QualityWarning(
                    code="low_text_quality",
                    page=1,
                    chars=0,
                    image_count=0,
                    message="Low text quality",
                )
            ]
            self.candidates = []
            self.requirements = []
            self.artifacts = []
            self.metadata = {"taxonomy_version": "test-v1"}
            self.validation = None

        def to_dict(self) -> dict[str, Any]:
             return {
                "warnings": [warning.to_dict() for warning in self.warnings],
                "candidates": [],
                "requirements": [],
                "artifacts": [],
                "metadata": dict(self.metadata),
                "validation": {"issues": [], "totals": {"errors": 0, "warnings": 0, "info": 0}},
            }

    monkeypatch.setattr(
        "specforge_distill.cli.run_distill_pipeline",
        lambda *_args, **_kwargs: _NoOutputResult(),
    )

    exit_code = cli_main(["distill", str(fake_pdf), "--dry-run"])
    io = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(io.out)
    assert payload["extraction_assessment"] == "likely_text_layer_issue"
    assert "image-only" in io.err


def test_cli_dry_run_reports_likely_scanned_pdf(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_pdf = tmp_path / "scanned.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n%placeholder\n")

    class _ScannedNoOutputResult:
        def __init__(self) -> None:
            self.warnings = [
                QualityWarning(
                    code="likely_scanned_page",
                    page=1,
                    chars=0,
                    image_count=1,
                    message="Likely scanned",
                )
            ]
            self.candidates = []
            self.requirements = []
            self.artifacts = []
            self.metadata = {"taxonomy_version": "test-v1"}
            self.validation = None

        def to_dict(self) -> dict[str, Any]:
             return {
                "warnings": [warning.to_dict() for warning in self.warnings],
                "candidates": [],
                "requirements": [],
                "artifacts": [],
                "metadata": dict(self.metadata),
                "validation": {"issues": [], "totals": {"errors": 0, "warnings": 0, "info": 0}},
            }

    monkeypatch.setattr(
        "specforge_distill.cli.run_distill_pipeline",
        lambda *_args, **_kwargs: _ScannedNoOutputResult(),
    )

    exit_code = cli_main(["distill", str(fake_pdf), "--dry-run"])
    io = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(io.out)
    assert payload["extraction_assessment"] == "likely_scanned_pdf"
    assert "appears to be a scan or image-only" in io.err


def test_cli_write_output_failure_returns_error_and_nonzero(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_pdf = tmp_path / "sample.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n%placeholder\n")

    monkeypatch.setattr(
        "specforge_distill.cli.run_distill_pipeline",
        lambda *_args, **_kwargs: _FakePipelineResult(),
    )

    def _boom(*_args, **_kwargs):
        raise PermissionError("permission denied")

    monkeypatch.setattr("specforge_distill.cli.write_output_package", _boom)

    exit_code = cli_main(["distill", str(fake_pdf)])
    io = capsys.readouterr()

    assert exit_code == 3
    assert "failed to write output package" in io.err
    assert "Check path and permissions" in io.err


def test_load_pdf_pages_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_pdf_pages("missing-source.pdf")
