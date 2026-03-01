"""PDF loading helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PageTextRecord:
    """Extracted text payload for a single page."""

    page_number: int
    text: str


def _has_pdf_signature(path: Path) -> bool:
    """Check for a PDF header near the start of the file before invoking pypdf."""

    with path.open("rb") as handle:
        header = handle.read(1024)
    return b"%PDF-" in header


def load_pdf_pages(pdf_path: str | Path) -> list[PageTextRecord]:
    """Load per-page text from a digital-text PDF using pypdf."""

    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")
    if not _has_pdf_signature(path):
        raise ValueError(f"Input does not appear to be a PDF file: {path}")

    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - import failure path
        raise RuntimeError("pypdf is required for PDF ingestion") from exc

    reader = PdfReader(str(path))
    records: list[PageTextRecord] = []
    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        records.append(PageTextRecord(page_number=idx, text=normalized))

    return records
