"""Candidate models used across extraction channels."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha1
from typing import Any


@dataclass(frozen=True)
class CandidateLink:
    """Represents a semantic link between two extracted candidates."""

    relation: str
    target_id: str
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "relation": self.relation,
            "target_id": self.target_id,
            "confidence": self.confidence,
        }


@dataclass
class Candidate:
    """Typed extracted statement candidate."""

    id: str
    text: str
    source_type: str
    page: int
    classification: str = "neutral"
    source_location: dict[str, Any] = field(default_factory=dict)
    flags: list[str] = field(default_factory=list)
    context_window: str | None = None
    links: list[CandidateLink] = field(default_factory=list)
    provenance: Any | None = None

    def to_dict(self) -> dict[str, Any]:
        provenance_value: Any
        if self.provenance is None:
            provenance_value = None
        elif hasattr(self.provenance, "to_dict"):
            provenance_value = self.provenance.to_dict()
        else:
            provenance_value = self.provenance

        return {
            "id": self.id,
            "text": self.text,
            "source_type": self.source_type,
            "page": self.page,
            "classification": self.classification,
            "source_location": dict(self.source_location),
            "flags": list(self.flags),
            "context_window": self.context_window,
            "links": [link.to_dict() for link in self.links],
            "provenance": provenance_value,
        }


def normalize_text(value: str) -> str:
    """Canonical text form for stable IDs and duplicate linking."""

    cleaned = " ".join(value.lower().split())
    return "".join(ch for ch in cleaned if ch.isalnum() or ch.isspace()).strip()


def stable_candidate_id(source_type: str, page: int, index: int, text: str) -> str:
    """Generate deterministic candidate IDs."""

    digest = sha1(normalize_text(text).encode("utf-8")).hexdigest()[:10]
    return f"cand-{source_type}-{page:03d}-{index:03d}-{digest}"
