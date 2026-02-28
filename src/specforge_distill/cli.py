"""Command-line interface for SpecForge Distill."""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Callable
from pathlib import Path

from specforge_distill.pipeline import run_distill_pipeline
from specforge_distill.render.markdown import MarkdownRenderer
from specforge_distill.render.manifest import ManifestWriter


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="distill")
    parser.add_argument("pdf_path", help="Path to source PDF")
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


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(_normalize_argv(list(argv or sys.argv[1:])))
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
        output_payload = {
            "source": str(source_pdf),
            "warnings": [warning.to_dict() for warning in result.warnings],
            "candidate_count": len(result.candidates),
            "artifact_count": len(result.artifacts),
            "taxonomy_version": result.metadata["taxonomy_version"],
        }
        print(json.dumps(output_payload, indent=2))
        return 0

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Orchestrate output generation
    renderer = MarkdownRenderer(result)
    
    file_mapping = {
        "full": "full.md",
        "requirements": "requirements.md",
        "architecture": "architecture.md",
        "manifest": "manifest.json",
    }

    # Write Markdown files
    (output_dir / file_mapping["full"]).write_text(renderer.render_full(), encoding="utf-8")
    (output_dir / file_mapping["requirements"]).write_text(renderer.render_requirements(), encoding="utf-8")
    (output_dir / file_mapping["architecture"]).write_text(renderer.render_architecture(), encoding="utf-8")

    # Write Manifest
    manifest_writer = ManifestWriter(result, file_mapping)
    manifest_writer.write(output_dir / file_mapping["manifest"])

    # Console Summary
    print(f"✓ Distillation complete in {duration:.2f}s")
    print(f"  Output: {output_dir.absolute()}")
    print(f"  Stats:  {len(result.requirements)} requirements, {len(result.artifacts)} architecture blocks.")

    if args.report:
        print("\nGenerated files:")
        for key, filename in file_mapping.items():
            print(f"  - {key:12}: {filename}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
