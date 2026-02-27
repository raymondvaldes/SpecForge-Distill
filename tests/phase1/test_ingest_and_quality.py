from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from specforge_distill.cli import main as cli_main
from specforge_distill.ingest.pdf_loader import PageTextRecord, load_pdf_pages
from specforge_distill.ingest.text_quality import QualityWarning, assess_text_quality
from specforge_distill.models.artifacts import ArtifactBlock
from specforge_distill.models.candidates import Candidate
from specforge_distill.models.requirement import Requirement
from specforge_distill.pipeline import load_obligation_taxonomy, run_distill_pipeline


class _FakePipelineResult:
    def __init__(self) -> None:
        self.warnings = [
            QualityWarning(
                code="low_text_quality",
                page=2,
                chars=3,
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "warnings": [warning.to_dict() for warning in self.warnings],
            "candidates": [c.to_dict() for c in self.candidates],
            "requirements": [r.to_dict() for r in self.requirements],
            "artifacts": [a.to_dict() for a in self.artifacts],
            "metadata": dict(self.metadata),
        }


def test_loads_external_taxonomy_version() -> None:
    taxonomy = load_obligation_taxonomy()
    assert taxonomy.version == "2026.02"
    assert taxonomy.verbs == ("must", "required", "shall")


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


def test_warns_on_low_text_pages() -> None:
    pages = [
        PageTextRecord(page_number=1, text="The system shall provide telemetry support."),
        PageTextRecord(page_number=2, text=""),
    ]

    warnings = assess_text_quality(pages, min_chars_per_page=20)
    assert [warning.page for warning in warnings] == [2]
    assert warnings[0].code == "low_text_quality"


def test_quality_threshold_boundary_is_non_warning_at_exact_limit() -> None:
    pages = [
        PageTextRecord(page_number=1, text="x" * 20),
        PageTextRecord(page_number=2, text="x" * 19),
    ]

    warnings = assess_text_quality(pages, min_chars_per_page=20)
    assert [warning.page for warning in warnings] == [2]


def test_cli_invocation_path(tmp_path: Path) -> None:
    fake_pdf = tmp_path / "sample-digital.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n%placeholder\n")

    exit_code = cli_main(["distill", str(fake_pdf), "--dry-run"])
    assert exit_code == 0

    dry_result = run_distill_pipeline(fake_pdf, dry_run=True)
    assert dry_result.metadata["taxonomy_version"] == "2026.02"


def test_cli_missing_file_returns_error_and_nonzero(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli_main(["distill", "does-not-exist.pdf"])
    io = capsys.readouterr()

    assert exit_code == 2
    assert "error: file not found" in io.err


def test_cli_writes_output_json_and_passes_runtime_args(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_pdf = tmp_path / "sample.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n%placeholder\n")
    output_dir = tmp_path / "out"
    observed: dict[str, object] = {}

    def _fake_run(pdf_path: Path, *, dry_run: bool, min_chars_per_page: int) -> _FakePipelineResult:
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

    assert "Distillation complete for sample.pdf" in io.out
    assert "Extracted 1 requirements and 1 architecture blocks." in io.out
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


def test_load_pdf_pages_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_pdf_pages("missing-source.pdf")
