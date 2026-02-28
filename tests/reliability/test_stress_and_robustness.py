import pytest
from pathlib import Path
import json
import time
import concurrent.futures

from specforge_distill.cli import main as cli_main
from specforge_distill.pipeline import run_distill_pipeline
from specforge_distill.ingest.pdf_loader import PageTextRecord
from specforge_distill.extract.id_resolver import detect_source_id

def test_cli_handles_corrupt_pdf(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """
    Ensures that providing a fundamentally broken/corrupt PDF does not result in 
    an uncaught exception, but rather exits gracefully with an error code.
    """
    corrupt_pdf = tmp_path / "corrupt_file.pdf"
    corrupt_pdf.write_bytes(b"This is not a PDF file. It's just random text that will break pypdf.")
    
    # The CLI should catch PDF errors and exit gracefully (e.g., exit code 3)
    # instead of crashing with a raw stack trace.
    exit_code = cli_main(["distill", str(corrupt_pdf)])
    assert exit_code != 0
    assert exit_code != 1 # It shouldn't be a generic crash


def test_cli_handles_malformed_filenames(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """
    Ensures that files with strange characters, no extension, or unusual paths
    are handled correctly by the output directory generation logic.
    """
    # File with no extension and spaces
    weird_file = tmp_path / "My Weird File Name  "
    weird_file.write_bytes(b"%PDF-1.4\n%mock\n")
    
    exit_code = cli_main(["distill", str(weird_file), "--dry-run"])
    assert exit_code == 0
    
    # File with unicode characters
    unicode_file = tmp_path / "spec_rock_ñ.pdf"
    unicode_file.write_bytes(b"%PDF-1.4\n%mock\n")
    
    exit_code = cli_main(["distill", str(unicode_file), "--dry-run"])
    assert exit_code == 0


def test_performance_megabook_simulation(tmp_path: Path) -> None:
    """
    Stress test: Simulates processing a 1,000-page document with 5,000 requirements.
    Ensures the pipeline can scale without OOM or quadratic time complexity hangs.
    """
    page_records = []
    # 1000 pages, 5 requirements per page
    for i in range(1, 1001):
        text = f"Page {i} content. \n" + "\n".join([f"The system shall do thing {j}." for j in range(5)])
        page_records.append(PageTextRecord(page_number=i, text=text))
        
    dummy_pdf = tmp_path / "megabook.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4\n")
        
    from unittest.mock import patch
    
    start_time = time.time()
    
    with patch("specforge_distill.pipeline.extract_table_candidates", return_value=[]):
        result = run_distill_pipeline(
            dummy_pdf,
            page_records=page_records
        )
    
    duration = time.time() - start_time
    
    assert len(result.requirements) >= 5000
    # The pipeline should process 1000 pages of mock text very quickly.
    # If it takes more than 10 seconds for just the NLP logic (no actual PDF parsing), 
    # we have a catastrophic performance bug ($O(N^2)$).
    assert duration < 10.0, f"Megabook processing took too long: {duration}s"


def test_regex_catastrophic_backtracking_protection() -> None:
    """
    Ensures the ID resolver regexes do not hang on pathological strings.
    """
    # A string designed to punish naive regexes
    pathological_string = "REQ-" + ("9" * 100000) + "a" 
    
    start_time = time.time()
    # If the regex is vulnerable, this will hang indefinitely.
    detect_source_id(pathological_string)
    duration = time.time() - start_time
    
    assert duration < 1.0, "Regex evaluation took too long, possible catastrophic backtracking."


def test_concurrency_race_conditions(tmp_path: Path) -> None:
    """
    Ensures that multiple instances of the CLI writing to the same directory 
    don't crash due to file locking or shared state issues.
    """
    pdf = tmp_path / "source.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    
    out_dir = tmp_path / "concurrent_out"

    from unittest.mock import patch
    from specforge_distill.pipeline import PipelineResult

    mock_result = PipelineResult(
        warnings=[], candidates=[], requirements=[], artifacts=[],
        metadata={"source_pdf": "source.pdf", "taxonomy_version": "1.0"}
    )
    
    def run_cli_instance(instance_id: int):
        return cli_main(["distill", str(pdf), "-o", str(out_dir)])

    # Run 10 CLI invocations concurrently targeting the exact same output folder
    with patch("specforge_distill.cli.run_distill_pipeline", return_value=mock_result):
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(run_cli_instance, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
    assert all(code == 0 for code in results)
    assert (out_dir / "manifest.json").exists()
