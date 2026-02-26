"""Utilities for attaching mandatory provenance metadata."""

from __future__ import annotations

from typing import Iterable

from specforge_distill.models.artifacts import ArtifactBlock
from specforge_distill.models.candidates import Candidate
from specforge_distill.provenance.models import Citation


def _build_anchor(source_type: str, page: int, source_location: dict[str, object]) -> str:
    suffix = ";".join(f"{key}={source_location[key]}" for key in sorted(source_location))
    if suffix:
        return f"p{page}:{source_type}:{suffix}"
    return f"p{page}:{source_type}"


def link_candidate_provenance(candidates: Iterable[Candidate], source_path: str) -> None:
    """Attach page-level citations to every candidate in place."""

    for candidate in candidates:
        if candidate.page < 1:
            raise ValueError(f"Candidate {candidate.id} has invalid page anchor: {candidate.page}")
        candidate.provenance = Citation(
            page=candidate.page,
            source_path=source_path,
            anchor=_build_anchor(candidate.source_type, candidate.page, candidate.source_location),
            excerpt=candidate.text[:180] or None,
        )


def link_artifact_provenance(artifacts: Iterable[ArtifactBlock], source_path: str) -> None:
    """Attach page-level citations to every structured artifact in place."""

    for artifact in artifacts:
        if artifact.page < 1:
            raise ValueError(f"Artifact {artifact.id} has invalid page anchor: {artifact.page}")
        artifact.provenance = Citation(
            page=artifact.page,
            source_path=source_path,
            anchor=_build_anchor(artifact.source_type, artifact.page, artifact.source_location),
            excerpt=artifact.content[:180] or None,
        )


def assert_citations_present(candidates: Iterable[Candidate], artifacts: Iterable[ArtifactBlock]) -> None:
    """Raise if any extracted entity lacks provenance."""

    for candidate in candidates:
        if candidate.provenance is None:
            raise ValueError(f"Candidate {candidate.id} is missing provenance")
    for artifact in artifacts:
        if artifact.provenance is None:
            raise ValueError(f"Artifact {artifact.id} is missing provenance")
