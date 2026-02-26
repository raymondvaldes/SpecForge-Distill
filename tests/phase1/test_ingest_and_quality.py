from __future__ import annotations

from pathlib import Path

from specforge_distill.cli import main as cli_main
from specforge_distill.ingest.pdf_loader import PageTextRecord
from specforge_distill.ingest.text_quality import assess_text_quality
from specforge_distill.pipeline import load_obligation_taxonomy, run_phase1_pipeline


def test_loads_external_taxonomy_version() -> None:
    taxonomy = load_obligation_taxonomy()
    assert taxonomy.version == "2026.02"
    assert taxonomy.verbs == ("must", "required", "shall")


def test_warns_on_low_text_pages() -> None:
    pages = [
        PageTextRecord(page_number=1, text="The system shall provide telemetry support."),
        PageTextRecord(page_number=2, text=""),
    ]

    warnings = assess_text_quality(pages, min_chars_per_page=20)
    assert [warning.page for warning in warnings] == [2]
    assert warnings[0].code == "low_text_quality"


def test_cli_invocation_path(tmp_path: Path) -> None:
    fake_pdf = tmp_path / "sample-digital.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n%placeholder\n")

    exit_code = cli_main(["distill", str(fake_pdf), "--dry-run"])
    assert exit_code == 0

    dry_result = run_phase1_pipeline(fake_pdf, dry_run=True)
    assert dry_result.metadata["taxonomy_version"] == "2026.02"
