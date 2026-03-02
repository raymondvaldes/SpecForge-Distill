"""Command-line interface for SpecForge Distill."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from specforge_distill import __version__


HELP_DESCRIPTION = f"""
SpecForge Distill (v{__version__})
----------------------------------
Transform legacy specification PDFs into structured, provenance-linked, AI-ready Markdown.

SpecForge Distill is a deterministic extraction engine designed for systems engineering workflows. 
It extracts requirements, architecture blocks, and VCRM (Verification Cross Reference Matrix) 
tables from digital-text PDFs, outputting them into structured Markdown and a JSON manifest.
"""

HELP_EPILOG = """
HOW IT WORKS:
  1. Ingestion: Reads text, tables, and captions from digital-text PDFs.
  2. Extraction: Identifies narrative requirements based on obligation verbs (shall, must, should, may)
                 and specific architectural/system contexts.
  3. Modeling: Normalizes requirements, generates stable/deterministic IDs (if none are found), 
               and merges VCRM table rows into single entities.
  4. Packaging: Outputs a canonical JSON manifest and separated Markdown files optimized for LLMs
                and MBSE (Model-Based Systems Engineering) tools.

LIMITATIONS & PITFALLS:
  - Scanned PDFs / OCR: NOT supported. The tool relies on the embedded text layer of a digital PDF.
    If your PDF is an image scan, extraction will fail or produce empty/garbage results.
  - Complex Graphics: Diagrams and flowcharts are not interpreted (e.g., no automatic Mermaid conversion).
  - VCRM Extraction: Table extraction attempts to detect "Req ID", "Verification Method", etc. 
    If your table uses highly non-standard headers, they may not be parsed as VCRM blocks.
  - Custom Taxonomy: By default, looks for "shall", "must", "required", "should", "recommended",
    "may", "optional".
  - Missing Context: Cross-page tables or extremely complex nested tables might break cell alignment.

OUTPUT STRUCTURE:
  Creates `<filename>_distilled/` (or path specified by -o) containing:
  - manifest.json: Complete JSON representation of all entities and metadata (SysML v2 ready).
  - full.md: Consolidated document view.
  - requirements.md: List of extracted requirements with obligations and source citations.
  - architecture.md: Extracted architecture narrative blocks.
  Batch mode creates one batch root containing one child output package per PDF plus `batch-summary.json`.
  - `--describe-output json`: Machine-readable output contract for automation clients.
  - `--emit-example-output [DIR]`: Canonical example output package using the real writer path.
  - `--self-test [DIR]`: Built-in output-package verification for install and automation checks.

EXAMPLES:
  Standard distillation:
      distill specs/system_requirements.pdf
  
  Output to a specific folder and show a detailed report:
      distill specs/system_requirements.pdf -o ./output/sys_reqs --report

  Dry run (validate file without writing output):
      distill specs/system_requirements.pdf --dry-run

  Process an explicit batch of PDFs:
      distill specs/a.pdf specs/b.pdf -o ./batch-output --report

  Process every direct child PDF in a directory:
      distill --input-dir ./specs -o ./batch-output --report

  Describe output contract for tools:
      distill --describe-output json

  Emit canonical example output:
      distill --emit-example-output ./example-output

  Run built-in self-test:
      distill --self-test
"""


_EXTRACTION_NOTES = {
    "content_extracted": None,
    "content_extracted_with_low_text_warnings": "note: extraction completed, but low text-layer warnings may indicate partial coverage on some pages.",
    "likely_scanned_pdf": (
        "note: the PDF appears to be a scan or image-only file. SpecForge Distill requires "
        "a text layer. Please run OCR on the PDF before processing."
    ),
    "likely_text_layer_issue": (
        "note: no structured content was extracted. The PDF may be image-only, OCR-only, "
        "or too low-text for the current extractor."
    ),
    "no_structured_content": (
        "note: distillation completed, but no structured requirements or architecture blocks were extracted."
    ),
}


def build_failure_payload(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from specforge_distill.automation import build_failure_payload as _impl

    return _impl(*args, **kwargs)


def build_dry_run_payload(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from specforge_distill.automation import build_dry_run_payload as _impl

    return _impl(*args, **kwargs)


def classify_extraction_assessment(*args: Any, **kwargs: Any) -> str:
    from specforge_distill.automation import classify_extraction_assessment as _impl

    return _impl(*args, **kwargs)


def describe_output_contract(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from specforge_distill.automation import describe_output_contract as _impl

    return _impl(*args, **kwargs)


def emit_example_output(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from specforge_distill.automation import emit_example_output as _impl

    return _impl(*args, **kwargs)


def run_self_test(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from specforge_distill.automation import run_self_test as _impl

    return _impl(*args, **kwargs)


def write_output_package(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from specforge_distill.automation import write_output_package as _impl

    return _impl(*args, **kwargs)


def execute_batch(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from specforge_distill.batch import execute_batch as _impl

    return _impl(*args, **kwargs)


def resolve_batch_inputs(*args: Any, **kwargs: Any) -> list[Path]:
    from specforge_distill.batch import resolve_batch_inputs as _impl

    return _impl(*args, **kwargs)


def resolve_batch_output_root(*args: Any, **kwargs: Any) -> Path:
    from specforge_distill.batch import resolve_batch_output_root as _impl

    return _impl(*args, **kwargs)


def run_distill_pipeline(*args: Any, **kwargs: Any) -> Any:
    from specforge_distill.pipeline import run_distill_pipeline as _impl

    return _impl(*args, **kwargs)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="distill",
        description=HELP_DESCRIPTION,
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--describe-output",
        choices=["json"],
        help="Print the CLI output contract in a machine-readable format.",
    )
    mode_group.add_argument(
        "--emit-example-output",
        nargs="?",
        const="",
        metavar="DIR",
        help="Write a canonical example output package to DIR or to ./specforge_distill_example_output.",
    )
    mode_group.add_argument(
        "--self-test",
        nargs="?",
        const="",
        metavar="DIR",
        help="Run a built-in deterministic self-test and optionally preserve output in DIR.",
    )
    parser.add_argument("pdf_paths", nargs="*", help="Path to one or more source PDFs")
    parser.add_argument(
        "--input-dir",
        help="Process every direct child PDF in DIR as a deterministic batch",
        default=None,
    )
    parser.add_argument("-o", "--output-dir", help="Optional output directory", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Validate startup without extraction")
    parser.add_argument(
        "--min-chars-per-page",
        type=int,
        default=40,
        help="Low-text warning threshold per page",
    )
    parser.add_argument(
        "--allow-external-ai",
        action="store_true",
        help="Placeholder for future LLM-based enrichment (currently no-op)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print detailed file list and summary report at the end",
    )
    return parser


def _normalize_argv(argv: list[str]) -> list[str]:
    if argv and argv[0] == "distill":
        return argv[1:]
    return argv


def _resolve_special_output_dir(primary_value: str | None, fallback_output_dir: str | None, default_name: str) -> Path | None:
    value = primary_value if primary_value not in (None, "") else fallback_output_dir
    if value:
        return Path(value)
    if primary_value is None:
        return None
    return Path(default_name)


def _resolve_self_test_output_dir(primary_value: str | None, fallback_output_dir: str | None) -> Path | None:
    value = primary_value if primary_value not in (None, "") else fallback_output_dir
    if value:
        return Path(value)
    return None


def _build_dry_run_payload(result: object, source_pdf: Path) -> dict[str, object]:
    return build_dry_run_payload(result, source_pdf)


def _clear_progress_line() -> None:
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()


def _emit_runtime_notes(result: Any) -> None:
    warning_pages = [warning.page for warning in result.warnings]
    if warning_pages:
        print(f"warning: low text-layer quality on pages {warning_pages}", file=sys.stderr)

    if result.validation:
        totals = result.validation.to_dict()["totals"]
        if totals["errors"] > 0 or totals["warnings"] > 0:
            print(
                f"note: validation found {totals['errors']} errors and {totals['warnings']} warnings in the extracted requirements.",
                file=sys.stderr,
            )

    extraction_note = _EXTRACTION_NOTES[classify_extraction_assessment(result)]

    if extraction_note:
        print(
            f"{extraction_note} See docs/TROUBLESHOOTING.md for recovery guidance.",
            file=sys.stderr,
        )


def _emit_batch_console_summary(summary: dict[str, object], *, report: bool) -> None:
    totals = summary["totals"]
    batch_root = summary["batch_root"]
    summary_path = summary["summary_path"]
    if summary["status"] == "ok":
        print("Batch distillation complete")
    else:
        print("Batch distillation finished with failures")
    print(f"  Batch root: {batch_root}")
    if summary_path:
        print(f"  Summary:    {summary_path}")
    print(
        "  Totals:     "
        f"{totals['succeeded']} succeeded, {totals['failed']} failed, "
        f"{totals['requirements']} requirements, {totals['artifacts']} architecture blocks."
    )

    if report:
        print("\nBatch items:")
        for item in summary["items"]:
            source_name = Path(item["source"]).name
            if item["status"] == "ok":
                print(f"  - ok     {source_name} -> {item['output_dir']}")
            else:
                print(f"  - failed {source_name} ({item['failure_class']})")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(_normalize_argv(list(argv or sys.argv[1:])))
    explicit_paths = list(args.pdf_paths)

    if args.describe_output:
        if explicit_paths or args.input_dir or args.output_dir or args.report or args.dry_run:
            print("error: --describe-output cannot be combined with PDF processing flags.", file=sys.stderr)
            return 2
        print(json.dumps(describe_output_contract(), indent=2))
        return 0

    if args.emit_example_output is not None:
        if explicit_paths or args.input_dir or args.dry_run:
            print("error: --emit-example-output cannot be combined with a PDF path or --dry-run.", file=sys.stderr)
            return 2
        output_dir = _resolve_special_output_dir(
            args.emit_example_output,
            args.output_dir,
            "specforge_distill_example_output",
        )
        assert output_dir is not None
        print(json.dumps(emit_example_output(output_dir), indent=2))
        return 0

    if args.self_test is not None:
        if explicit_paths or args.input_dir or args.dry_run:
            print("error: --self-test cannot be combined with a PDF path or --dry-run.", file=sys.stderr)
            return 2
        preserved_output_dir = _resolve_self_test_output_dir(args.self_test, args.output_dir)
        try:
            print(json.dumps(run_self_test(preserved_output_dir), indent=2))
            return 0
        except Exception as e:
            print(
                json.dumps(
                    build_failure_payload(
                        "self_test_validation_failure",
                        mode="self-test",
                        detail=str(e),
                    ),
                    indent=2,
                ),
                file=sys.stderr,
            )
            return 4

    if args.input_dir and explicit_paths:
        print("error: --input-dir cannot be combined with explicit PDF paths.", file=sys.stderr)
        return 2

    if args.input_dir is None and not explicit_paths:
        print("error: missing PDF path. Provide a PDF or use --describe-output, --emit-example-output, or --self-test.", file=sys.stderr)
        return 2

    is_batch_mode = args.input_dir is not None or len(explicit_paths) > 1
    if is_batch_mode:
        try:
            source_pdfs = resolve_batch_inputs(explicit_paths, args.input_dir)
        except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        batch_root = resolve_batch_output_root(args.output_dir)
        try:
            summary = execute_batch(
                source_pdfs,
                batch_root=batch_root,
                dry_run=args.dry_run,
                min_chars_per_page=args.min_chars_per_page,
                run_pipeline=run_distill_pipeline,
                package_writer=write_output_package,
            )
        except OSError as exc:
            print(
                (
                    f"error: failed to write batch output package to {batch_root}. "
                    "Check path and permissions for the current shell or platform.\n"
                    f"Details: {exc}"
                ),
                file=sys.stderr,
            )
            return 3

        if args.dry_run:
            print(json.dumps(summary, indent=2))
        else:
            _emit_batch_console_summary(summary, report=args.report)
        return 0 if summary["status"] == "ok" else 5

    source_pdf = Path(explicit_paths[0])

    if not source_pdf.exists():
        print(f"error: file not found: {source_pdf}", file=sys.stderr)
        return 2

    # Calculate default output directory if not provided
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = source_pdf.parent / f"{source_pdf.stem}_distilled"

    start_time = time.time()
    progress_started = False
    
    def _progress(msg: str) -> None:
        nonlocal progress_started
        progress_started = True
        # Clear line and print new progress
        sys.stdout.write(f"\r\033[K[~] {msg}")
        sys.stdout.flush()

    try:
        result = run_distill_pipeline(
            source_pdf,
            dry_run=args.dry_run,
            min_chars_per_page=args.min_chars_per_page,
            progress_callback=None if args.dry_run else _progress,
        )
        if progress_started:
            _clear_progress_line()
    except Exception as e:
        if progress_started:
            _clear_progress_line()
        print(f"error: Failed to process PDF. The file may be corrupted, encrypted, or malformed.\nDetails: {e}", file=sys.stderr)
        return 3

    duration = time.time() - start_time
    _emit_runtime_notes(result)

    if args.dry_run:
        print(json.dumps(_build_dry_run_payload(result, source_pdf), indent=2))
        return 0

    try:
        package_summary = write_output_package(result, output_dir)
    except OSError as e:
        print(
            (
                f"error: failed to write output package to {output_dir}. "
                "Check path and permissions for the current shell or platform.\n"
                f"Details: {e}"
            ),
            file=sys.stderr,
        )
        return 3

    # Console Summary
    print(f"Distillation complete in {duration:.2f}s")
    print(f"  Output: {package_summary['output_dir']}")
    print(f"  Stats:  {len(result.requirements)} requirements, {len(result.artifacts)} architecture blocks.")

    if args.report:
        print("\nGenerated files:")
        for key, filename in package_summary["file_names"].items():
            print(f"  - {key:12}: {filename}")

        if result.validation:
            v_summary = result.validation.to_dict()
            if v_summary["issues"]:
                print("\nValidation Findings:")
                for issue in v_summary["issues"]:
                    sev = issue["severity"].upper()
                    print(f"  - [{sev:7}] p.{issue['page']:<3} {issue['entity_id']:15} {issue['message']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
