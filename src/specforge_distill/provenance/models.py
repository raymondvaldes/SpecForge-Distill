"""Provenance models for page-level citation anchoring."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Citation:
    """Citation anchor tied to a source page."""

    page: int
    source_path: str
    anchor: str
    excerpt: str | None = None

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("Citation page anchor must be >= 1")
        if not self.source_path:
            raise ValueError("Citation source_path is required")
        if not self.anchor:
            raise ValueError("Citation anchor is required")

    def to_dict(self) -> dict[str, str | int | None]:
        return {
            "page": self.page,
            "source_path": self.source_path,
            "anchor": self.anchor,
            "excerpt": self.excerpt,
        }
