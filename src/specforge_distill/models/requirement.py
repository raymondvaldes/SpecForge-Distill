"""Canonical requirement models for normalized specification entities."""

from __future__ import annotations

from typing import List, Optional, Any
from pydantic import BaseModel, Field

from specforge_distill.provenance.models import Citation
from specforge_distill.models.candidates import Candidate
from specforge_distill.models.common import InteropMetadata


class VCRMAttributes(BaseModel):
    """Attributes for Verification Cross Reference Matrix (VCRM) reconstruction."""

    method: Optional[str] = None  # Test, Demo, Inspection, Analysis
    rationale: Optional[str] = None
    allocation: Optional[str] = None
    success_criteria: Optional[str] = None


class Requirement(BaseModel):
    """Formal validated requirement record with provenance and obligation classification."""

    id: str
    text: str
    obligation: str = "unknown"  # shall, must, should, etc.
    page: int
    source_type: str
    is_ambiguous: bool = False
    ambiguity_reasons: List[str] = Field(default_factory=list)
    vcrm: VCRMAttributes = Field(default_factory=VCRMAttributes)
    interop: InteropMetadata = Field(default_factory=InteropMetadata)
    provenance: Optional[Citation] = None

    @staticmethod
    def from_candidate(candidate: Candidate) -> Requirement:
        """Transform an extraction candidate into a formal requirement record."""
        
        # Ensure provenance is correctly typed as Citation if it exists
        provenance: Optional[Citation] = None
        if isinstance(candidate.provenance, Citation):
            provenance = candidate.provenance
        
        return Requirement(
            id=candidate.id,
            text=candidate.text,
            obligation="unknown",  # To be filled by classifier
            page=candidate.page,
            source_type=candidate.source_type,
            is_ambiguous=False,    # To be filled by classifier
            ambiguity_reasons=[],  # To be filled by classifier
            vcrm=VCRMAttributes(),
            interop=InteropMetadata(),
            provenance=provenance,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for legacy compatibility/serialization."""
        return self.model_dump()
