from __future__ import annotations

import json
from pathlib import Path

import pytest

from specforge_distill.ingest.pdf_loader import PageTextRecord
from specforge_distill.pipeline import PipelineResult, run_phase1_pipeline


FIXTURE_DIR = Path(__file__).parent / "fixtures"
EXPECTED_CONTRACT_PATH = FIXTURE_DIR / "expected_outputs.yaml"


def load_expected_contract() -> dict[str, object]:
    return json.loads(EXPECTED_CONTRACT_PATH.read_text(encoding="utf-8"))


def _run_acceptance_pipeline(tmp_path: Path) -> PipelineResult:
    fake_pdf = tmp_path / "acceptance.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n%placeholder\n")

    page_records = [
        PageTextRecord(
            page_number=1,
            text=(
                "1 Overview\n"
                "The platform shall provide secure telemetry.\n\n"
                "2 System Architecture\n"
                "The architecture separates control and data planes.\n"
                "Figure 7: Maintenance path\n"
                "The maintenance route should remain available during updates."
            ),
        ),
        PageTextRecord(page_number=2, text=""),
    ]

    return run_phase1_pipeline(
        fake_pdf,
        page_records=page_records,
        table_rows_by_page={2: [["Req", "Gateway must isolate untrusted inputs"]]},
        min_chars_per_page=20,
    )


def _assert_phase1_contract(result: PipelineResult, contract: dict[str, object]) -> None:
    expected_warning = str(contract["required_warning_code"])
    warning_codes = {warning.code for warning in result.warnings}
    assert expected_warning in warning_codes

    required_sources = set(contract["required_source_types"])
    observed_sources = {candidate.source_type for candidate in result.candidates}
    assert required_sources.issubset(observed_sources)

    min_architecture_blocks = int(contract["min_architecture_blocks"])
    assert len(result.artifacts) >= min_architecture_blocks

    if bool(contract["require_citations"]):
        assert all(candidate.provenance is not None for candidate in result.candidates)
        assert all(artifact.provenance is not None for artifact in result.artifacts)


def test_expected_contract_schema() -> None:
    contract = load_expected_contract()

    assert contract["schema_version"] == 1
    assert set(contract["required_source_types"]) == {"narrative", "table_cell", "caption_context"}
    assert contract["required_warning_code"] == "low_text_quality"
    assert contract["require_citations"] is True


def test_phase1_end_to_end_acceptance(tmp_path: Path) -> None:
    contract = load_expected_contract()
    result = _run_acceptance_pipeline(tmp_path)

    _assert_phase1_contract(result, contract)


def test_warn_and_continue_low_text_pages(tmp_path: Path) -> None:
    result = _run_acceptance_pipeline(tmp_path)

    warning_pages = {warning.page for warning in result.warnings}
    assert 2 in warning_pages
    assert result.candidates


def test_missing_citation_fails_acceptance(tmp_path: Path) -> None:
    contract = load_expected_contract()
    result = _run_acceptance_pipeline(tmp_path)
    result.candidates[0].provenance = None

    with pytest.raises(AssertionError):
        _assert_phase1_contract(result, contract)


def test_missing_required_channel_fails_acceptance(tmp_path: Path) -> None:
    contract = load_expected_contract()
    result = _run_acceptance_pipeline(tmp_path)
    result.candidates = [candidate for candidate in result.candidates if candidate.source_type != "caption_context"]

    with pytest.raises(AssertionError):
        _assert_phase1_contract(result, contract)


def test_acceptance_metadata_includes_taxonomy_details(tmp_path: Path) -> None:
    result = _run_acceptance_pipeline(tmp_path)

    assert result.metadata["taxonomy_version"] == "2026.02"
    assert result.metadata["obligation_verbs"] == ["must", "required", "shall"]


def test_equivalent_statements_are_linked_but_not_deduped(tmp_path: Path) -> None:
    fake_pdf = tmp_path / "duplicates.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n%placeholder\n")

    statement = "Gateway must isolate untrusted inputs."
    page_records = [
        PageTextRecord(
            page_number=1,
                text=(
                    "1 Overview\n"
                    "\n"
                    f"{statement}\n"
                    "\n"
                    "2 System Architecture\n"
                    "Control and data planes are segmented."
                ),
            )
        ]

    result = run_phase1_pipeline(
        fake_pdf,
        page_records=page_records,
        table_rows_by_page={1: [["Req", statement]]},
    )

    normalized = " ".join(statement.lower().split()).strip(".")
    matching = [candidate for candidate in result.candidates if normalized in candidate.text.lower().strip(".")]
    assert len(matching) >= 2
    assert any(candidate.links for candidate in matching)
