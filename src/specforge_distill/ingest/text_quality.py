"""Low text-layer quality diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from specforge_distill.ingest.pdf_loader import PageTextRecord


@dataclass(frozen=True)
class QualityWarning:
    """Warning emitted when page text quality is likely degraded."""

    code: str
    page: int
    chars: int
    message: str
    image_count: int = 0

    def to_dict(self) -> dict[str, str | int]:
        return {
            "code": self.code,
            "page": self.page,
            "chars": self.chars,
            "message": self.message,
            "image_count": self.image_count,
        }


def assess_text_quality(
    page_records: Iterable[PageTextRecord],
    *,
    min_chars_per_page: int = 40,
) -> list[QualityWarning]:
    """Detect low-text or scanned pages while allowing pipeline execution to continue."""

    warnings: list[QualityWarning] = []
    for page in page_records:
        char_count = len(page.text.strip())
        if char_count < min_chars_per_page:
            # If there is low text and at least one image, it's a scanned-PDF candidate
            if page.image_count > 0:
                code = "likely_scanned_page"
                message = (
                    "Page appears to be a scan or image-only; "
                    "extraction continues but text quality is likely insufficient."
                )
            else:
                code = "low_text_quality"
                message = (
                    "Low text-layer quality detected; extraction continues but output may be incomplete."
                )

            warnings.append(
                QualityWarning(
                    code=code,
                    page=page.page_number,
                    chars=char_count,
                    image_count=page.image_count,
                    message=message,
                )
            )
    return warnings
