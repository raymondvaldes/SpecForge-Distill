from __future__ import annotations

import concurrent.futures
import json
from copy import deepcopy
from pathlib import Path
from time import perf_counter
from unittest.mock import patch

from specforge_distill.cli import main as cli_main
from specforge_distill.extract.id_resolver import detect_source_id
from specforge_distill.ingest.pdf_loader import PageTextRecord
from specforge_distill.pipeline import run_distill_pipeline


def _build_page_records(
    page_count: int,
    *,
    requirements_per_page: int = 3,
) -> list[PageTextRecord]:
    page_records: list[PageTextRecord] = []
    for page_number in range(1, page_count + 1):
        requirement_lines = "\n".join(
            f"The system shall perform task {page_number}-{requirement_number}."
            for requirement_number in range(1, requirements_per_page + 1)
        )
        page_records.append(
            PageTextRecord(
                page_number=page_number,
                text=f"Section {page_number}\n\n{requirement_lines}",
            )
        )
    return page_records


def _run_synthetic_pipeline(
    tmp_path: Path,
    *,
    page_count: int,
    requirements_per_page: int = 3,
):
    dummy_pdf = tmp_path / f"synthetic-{page_count}.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4\n")

    start = perf_counter()
    with patch("specforge_distill.pipeline.extract_table_candidates", return_value=[]), patch(
        "specforge_distill.pipeline.extract_caption_candidates",
        return_value=[],
    ):
        result = run_distill_pipeline(
            dummy_pdf,
            page_records=_build_page_records(
                page_count,
                requirements_per_page=requirements_per_page,
            ),
        )
    duration = perf_counter() - start
    return result, duration


def _measure_detect_source_id(text: str, *, iterations: int = 50) -> float:
    start = perf_counter()
    for _ in range(iterations):
        detect_source_id(text)
    return perf_counter() - start


def test_cli_handles_corrupt_pdf(tmp_path: Path) -> None:
    """
    Ensures that providing a fundamentally broken/corrupt PDF does not result in
    an uncaught exception, but rather exits gracefully with an error code.
    """
    corrupt_pdf = tmp_path / "corrupt_file.pdf"
    corrupt_pdf.write_bytes(
        b"This is not a PDF file. It's just random text that will break pypdf."
    )

    exit_code = cli_main(["distill", str(corrupt_pdf)])
    assert exit_code != 0
    assert exit_code != 1


def test_cli_handles_malformed_filenames(tmp_path: Path) -> None:
    """
    Ensures that files with strange characters, no extension, or unusual paths
    are handled correctly by the output directory generation logic.
    """
    weird_file = tmp_path / "My Weird File Name  "
    weird_file.write_bytes(b"%PDF-1.4\n%mock\n")

    exit_code = cli_main(["distill", str(weird_file), "--dry-run"])
    assert exit_code == 0

    unicode_file = tmp_path / "spec_rock_ñ.pdf"
    unicode_file.write_bytes(b"%PDF-1.4\n%mock\n")

    exit_code = cli_main(["distill", str(unicode_file), "--dry-run"])
    assert exit_code == 0


def test_pipeline_scaling_is_approximately_linear(tmp_path: Path) -> None:
    """
    Synthetic pipeline work should scale roughly linearly with page count.

    This compares two controlled runs instead of relying on a single wall-clock
    threshold that is overly sensitive to machine variance.
    """
    small_result, small_duration = _run_synthetic_pipeline(tmp_path, page_count=80)
    large_result, large_duration = _run_synthetic_pipeline(tmp_path, page_count=160)

    assert len(small_result.requirements) == 240
    assert len(large_result.requirements) == 480
    assert large_duration < 8.0
    assert large_duration <= max(small_duration * 3.0, small_duration + 1.0)


def test_detect_source_id_scales_without_regex_backtracking() -> None:
    """
    The ID resolver should scale with input length and avoid catastrophic regex behavior.
    """
    shorter = "[" + ("REQ-" * 2_000) + "x"
    longer = "[" + ("REQ-" * 10_000) + "x"

    assert detect_source_id(shorter) is None
    assert detect_source_id(longer) is None

    short_duration = _measure_detect_source_id(shorter)
    long_duration = _measure_detect_source_id(longer)

    assert long_duration <= max(short_duration * 8.0, short_duration + 0.25)


def test_concurrency_race_conditions(tmp_path: Path) -> None:
    """
    Ensures that multiple instances of the CLI writing to the same directory
    don't crash due to file locking or shared state issues.
    """
    from specforge_distill.pipeline import PipelineResult

    pdf = tmp_path / "source.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")

    out_dir = tmp_path / "concurrent_out"
    mock_result = PipelineResult(
        warnings=[],
        candidates=[],
        requirements=[],
        artifacts=[],
        metadata={"source_pdf": "source.pdf", "taxonomy_version": "1.0"},
    )

    def run_cli_instance() -> int:
        return cli_main(["distill", str(pdf), "-o", str(out_dir)])

    with patch(
        "specforge_distill.cli.run_distill_pipeline",
        side_effect=lambda *args, **kwargs: deepcopy(mock_result),
    ):
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(run_cli_instance) for _ in range(4)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

    assert all(code == 0 for code in results)
    for file_name in ["full.md", "requirements.md", "architecture.md", "manifest.json"]:
        assert (out_dir / file_name).exists()

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source_pdf"] == "source.pdf"
    assert manifest["metadata"]["source_pdf"] == "source.pdf"
    assert manifest["entities"] == []
