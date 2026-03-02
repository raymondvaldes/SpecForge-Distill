from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class InteropMetadata(BaseModel):
    """Hooks for SysML v2 and MBSE toolchain integration."""

    target: str = "sysmlv2-future"
    candidate_concept: Optional[str] = None
    mapping_status: str = "unmapped"
    logical_layer: Optional[str] = None  # functional, logical, physical
    external_ref: Optional[str] = None    # Link to external system or document
    verification_status: str = "unverified"
