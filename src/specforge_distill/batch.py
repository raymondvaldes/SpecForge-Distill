"""Batch input resolution and aggregate execution helpers."""

from __future__ import annotations

from collections import Counter
from hashlib import sha1
from pathlib import Path
import re
from typing import Any, Callable, Sequence


DEFAULT_BATCH_OUTPUT_ROOT = "specforge_distill_batch_output"
_PDF_SUFFIX = ".pdf"
_SAFE_OUTPUT_NAME = re.compile(r"[^A-Za-z0-9._-]+")


def build_batch_failure_item(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from specforge_distill.automation import build_batch_failure_item as _impl

    return _impl(*args, **kwargs)


def build_batch_success_item(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from specforge_distill.automation import build_batch_success_item as _impl

    return _impl(*args, **kwargs)


def summarize_batch_items(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from specforge_distill.automation import summarize_batch_items as _impl

    return _impl(*args, **kwargs)


def write_batch_summary(*args: Any, **kwargs: Any) -> Path:
    from specforge_distill.automation import write_batch_summary as _impl

    return _impl(*args, **kwargs)


def _normalize_source_key(path: str | Path) -> str:
    return Path(path).resolve(strict=False).as_posix().casefold()


def _deduplicate_sorted_paths(paths: Sequence[str | Path]) -> list[Path]:
    deduped: dict[str, Path] = {}
    for path in paths:
        path_obj = Path(path)
        deduped[_normalize_source_key(path_obj)] = path_obj
    return [deduped[key] for key in sorted(deduped)]


def sanitize_output_stem(stem: str) -> str:
    """Return a filesystem-safe stem for batch child output directories."""

    sanitized = _SAFE_OUTPUT_NAME.sub("-", stem).strip("._-")
    return sanitized or "source"


def resolve_batch_inputs(
    pdf_paths: Sequence[str | Path],
    input_dir: str | Path | None,
) -> list[Path]:
    """Resolve explicit or directory-driven batch inputs into deterministic order."""

    if input_dir is not None and pdf_paths:
        raise ValueError("--input-dir cannot be combined with explicit PDF paths.")

    if input_dir is not None:
        input_dir_path = Path(input_dir)
        if not input_dir_path.exists():
            raise FileNotFoundError(f"input directory not found: {input_dir_path}")
        if not input_dir_path.is_dir():
            raise NotADirectoryError(f"input path is not a directory: {input_dir_path}")

        pdf_sources = [
            child
            for child in input_dir_path.iterdir()
            if child.is_file() and child.suffix.lower() == _PDF_SUFFIX
        ]
        if not pdf_sources:
            raise ValueError(f"no PDF files found in input directory: {input_dir_path}")
        return _deduplicate_sorted_paths(pdf_sources)

    if not pdf_paths:
        raise ValueError("missing PDF path. Provide a PDF or use --input-dir.")

    return _deduplicate_sorted_paths(pdf_paths)


def resolve_batch_output_root(output_dir: str | Path | None) -> Path:
    """Return the deterministic batch output root."""

    if output_dir is not None:
        return Path(output_dir)
    return Path(DEFAULT_BATCH_OUTPUT_ROOT)


def plan_batch_output_directories(
    source_pdfs: Sequence[str | Path],
    batch_root: str | Path,
) -> dict[Path, Path]:
    """Plan stable child output directories for each batch source."""

    batch_root_path = Path(batch_root)
    sources = [Path(source_pdf) for source_pdf in source_pdfs]
    stem_counts = Counter(sanitize_output_stem(source_pdf.stem) for source_pdf in sources)

    planned: dict[Path, Path] = {}
    used_names: set[str] = set()
    for source_pdf in sources:
        stem = sanitize_output_stem(source_pdf.stem)
        if stem_counts[stem] == 1:
            child_name = f"{stem}_distilled"
        else:
            digest = sha1(_normalize_source_key(source_pdf).encode("utf-8")).hexdigest()[:8]
            child_name = f"{stem}-{digest}_distilled"

        if child_name in used_names:
            index = 2
            candidate_name = f"{child_name}-{index:02d}"
            while candidate_name in used_names:
                index += 1
                candidate_name = f"{child_name}-{index:02d}"
            child_name = candidate_name

        used_names.add(child_name)
        planned[source_pdf] = batch_root_path / child_name

    return planned


def execute_batch(
    source_pdfs: Sequence[str | Path],
    *,
    batch_root: str | Path,
    dry_run: bool,
    min_chars_per_page: int,
    run_pipeline: Callable[..., Any],
    package_writer: Callable[[Any, str | Path], dict[str, Any]],
) -> dict[str, Any]:
    """Execute deterministic batch processing and return the aggregate summary."""

    resolved_sources = [Path(source_pdf) for source_pdf in source_pdfs]
    planned_outputs = plan_batch_output_directories(resolved_sources, batch_root)
    items: list[dict[str, Any]] = []

    for source_pdf in resolved_sources:
        planned_output_dir = planned_outputs[source_pdf]
        if not source_pdf.exists():
            items.append(
                build_batch_failure_item(
                    source_pdf,
                    planned_output_dir,
                    failure_class="missing_input_file",
                    detail=f"file not found: {source_pdf}",
                )
            )
            continue

        try:
            result = run_pipeline(
                source_pdf,
                dry_run=dry_run,
                min_chars_per_page=min_chars_per_page,
                progress_callback=None,
            )
        except Exception as exc:  # pragma: no cover - exercised through CLI integration tests
            items.append(
                build_batch_failure_item(
                    source_pdf,
                    planned_output_dir,
                    failure_class="pdf_processing_failure",
                    detail=str(exc),
                )
            )
            continue

        if dry_run:
            items.append(build_batch_success_item(source_pdf, result, planned_output_dir=planned_output_dir))
            continue

        try:
            package_summary = package_writer(result, planned_output_dir)
        except OSError as exc:
            items.append(
                build_batch_failure_item(
                    source_pdf,
                    planned_output_dir,
                    failure_class="output_write_failure",
                    detail=str(exc),
                )
            )
            continue

        items.append(
            build_batch_success_item(
                source_pdf,
                result,
                planned_output_dir=planned_output_dir,
                package_summary=package_summary,
            )
        )

    summary = summarize_batch_items(items, batch_root=batch_root, dry_run=dry_run)
    if not dry_run:
        summary_path = write_batch_summary(summary, batch_root)
        summary["summary_path"] = str(summary_path.absolute())
    return summary
