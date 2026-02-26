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

    def to_dict(self) -> dict[str, str | int]:
        return {
            "code": self.code,
            "page": self.page,
            "chars": self.chars,
            "message": self.message,
        }


def assess_text_quality(
    page_records: Iterable[PageTextRecord],
    *,
    min_chars_per_page: int = 40,
) -> list[QualityWarning]:
    """Detect low-text pages while allowing pipeline execution to continue."""

    warnings: list[QualityWarning] = []
    for page in page_records:
        char_count = len(page.text.strip())
        if char_count < min_chars_per_page:
            warnings.append(
                QualityWarning(
                    code="low_text_quality",
                    page=page.page_number,
                    chars=char_count,
                    message=(
                        "Low text-layer quality detected; extraction continues but output may be incomplete."
                    ),
                )
            )
    return warnings
