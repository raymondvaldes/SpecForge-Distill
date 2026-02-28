"""Structured artifact models for extracted non-requirement content."""

from __future__ import annotations

from hashlib import sha1
from typing import Any, Optional
from pydantic import BaseModel, Field

from specforge_distill.models.common import InteropMetadata


class ArtifactBlock(BaseModel):
    """Structured architecture block with deterministic identity."""

    id: str
    section: str
    content: str
    page: int
    source_type: str = "architecture_block"
    source_location: dict[str, Any] = Field(default_factory=dict)
    interop: InteropMetadata = Field(default_factory=InteropMetadata)
    provenance: Optional[Any] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for legacy compatibility."""
        return self.model_dump()


def stable_artifact_id(section: str, page: int, content: str) -> str:
    """Generate deterministic artifact IDs."""

    digest = sha1(f"{section}|{content}".encode("utf-8")).hexdigest()[:10]
    return f"art-{page:03d}-{digest}"
