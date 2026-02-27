"""Structured artifact models for extracted non-requirement content."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha1
from typing import Any


@dataclass
class InteropMetadata:
    """Hooks for SysML v2 and MBSE toolchain integration."""

    target: str = "sysmlv2-future"
    candidate_concept: str | None = None
    mapping_status: str = "unmapped"

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "candidate_concept": self.candidate_concept,
            "mapping_status": self.mapping_status,
        }


@dataclass
class ArtifactBlock:
    """Structured architecture block with deterministic identity."""

    id: str
    section: str
    content: str
    page: int
    source_type: str = "architecture_block"
    source_location: dict[str, Any] = field(default_factory=dict)
    interop: InteropMetadata = field(default_factory=InteropMetadata)
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
            "section": self.section,
            "content": self.content,
            "page": self.page,
            "source_type": self.source_type,
            "source_location": dict(self.source_location),
            "interop": self.interop.to_dict(),
            "provenance": provenance_value,
        }


def stable_artifact_id(section: str, page: int, content: str) -> str:
    """Generate deterministic artifact IDs."""

    digest = sha1(f"{section}|{content}".encode("utf-8")).hexdigest()[:10]
    return f"art-{page:03d}-{digest}"
