"""Requirement and Candidate models."""

from __future__ import annotations

from typing import Any

__all__ = ["Candidate", "CandidateLink", "Requirement", "VCRMAttributes"]


def __getattr__(name: str) -> Any:
    if name in {"Candidate", "CandidateLink"}:
        from specforge_distill.models.candidates import Candidate, CandidateLink

        exports = {
            "Candidate": Candidate,
            "CandidateLink": CandidateLink,
        }
        return exports[name]

    if name in {"Requirement", "VCRMAttributes"}:
        from specforge_distill.models.requirement import Requirement, VCRMAttributes

        exports = {
            "Requirement": Requirement,
            "VCRMAttributes": VCRMAttributes,
        }
        return exports[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
