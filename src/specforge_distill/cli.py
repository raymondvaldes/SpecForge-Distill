"""Command-line interface for SpecForge Distill."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from specforge_distill import __version__
from specforge_distill.automation import (
    describe_output_contract,
    emit_example_output,
    run_self_test,
    write_output_package,
)
from specforge_distill.pipeline import run_distill_pipeline


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

  Describe output contract for tools:
      distill --describe-output json

  Emit canonical example output:
      distill --emit-example-output ./example-output

  Run built-in self-test:
      distill --self-test
"""


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
    parser.add_argument("pdf_path", nargs="?", help="Path to source PDF")
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
    return {
        "source": str(source_pdf),
        "warnings": [warning.to_dict() for warning in result.warnings],
        "candidate_count": len(result.candidates),
        "artifact_count": len(result.artifacts),
        "taxonomy_version": result.metadata["taxonomy_version"],
    }


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(_normalize_argv(list(argv or sys.argv[1:])))

    if args.describe_output:
        if args.pdf_path or args.output_dir or args.report or args.dry_run:
            print("error: --describe-output cannot be combined with PDF processing flags.", file=sys.stderr)
            return 2
        print(json.dumps(describe_output_contract(), indent=2))
        return 0

    if args.emit_example_output is not None:
        if args.pdf_path or args.dry_run:
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
        if args.pdf_path or args.dry_run:
            print("error: --self-test cannot be combined with a PDF path or --dry-run.", file=sys.stderr)
            return 2
        preserved_output_dir = _resolve_self_test_output_dir(args.self_test, args.output_dir)
        try:
            print(json.dumps(run_self_test(preserved_output_dir), indent=2))
            return 0
        except Exception as e:
            print(
                json.dumps(
                    {
                        "status": "failed",
                        "mode": "self-test",
                        "version": __version__,
                        "detail": str(e),
                    },
                    indent=2,
                ),
                file=sys.stderr,
            )
            return 4

    if args.pdf_path is None:
        print("error: missing PDF path. Provide a PDF or use --describe-output, --emit-example-output, or --self-test.", file=sys.stderr)
        return 2

    source_pdf = Path(args.pdf_path)

    if not source_pdf.exists():
        print(f"error: file not found: {source_pdf}", file=sys.stderr)
        return 2

    # Calculate default output directory if not provided
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = source_pdf.parent / f"{source_pdf.stem}_distilled"

    start_time = time.time()
    
    def _progress(msg: str) -> None:
        # Clear line and print new progress
        sys.stdout.write(f"\r\033[K[~] {msg}")
        sys.stdout.flush()

    try:
        result = run_distill_pipeline(
            source_pdf,
            dry_run=args.dry_run,
            min_chars_per_page=args.min_chars_per_page,
            progress_callback=_progress,
        )
        sys.stdout.write("\r\033[K") # Clear the final progress line
        sys.stdout.flush()
    except Exception as e:
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()
        print(f"error: Failed to process PDF. The file may be corrupted, encrypted, or malformed.\nDetails: {e}", file=sys.stderr)
        return 3

    duration = time.time() - start_time

    warning_pages = [warning.page for warning in result.warnings]
    if warning_pages:
        print(f"warning: low text-layer quality on pages {warning_pages}", file=sys.stderr)

    if args.dry_run:
        print(json.dumps(_build_dry_run_payload(result, source_pdf), indent=2))
        return 0

    package_summary = write_output_package(result, output_dir)

    # Console Summary
    print(f"Distillation complete in {duration:.2f}s")
    print(f"  Output: {package_summary['output_dir']}")
    print(f"  Stats:  {len(result.requirements)} requirements, {len(result.artifacts)} architecture blocks.")

    if args.report:
        print("\nGenerated files:")
        for key, filename in package_summary["file_names"].items():
            print(f"  - {key:12}: {filename}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
