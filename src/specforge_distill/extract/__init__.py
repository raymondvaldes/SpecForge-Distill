"""Extraction logic for requirement entities."""

from __future__ import annotations

from typing import Any

__all__ = [
    "detect_source_id",
    "generate_stable_id",
    "resolve_requirement_id",
    "classify_obligation",
    "detect_ambiguity",
    "enrich_requirement",
]


def __getattr__(name: str) -> Any:
    if name in {"detect_source_id", "generate_stable_id", "resolve_requirement_id"}:
        from specforge_distill.extract.id_resolver import (
            detect_source_id,
            generate_stable_id,
            resolve_requirement_id,
        )

        exports = {
            "detect_source_id": detect_source_id,
            "generate_stable_id": generate_stable_id,
            "resolve_requirement_id": resolve_requirement_id,
        }
        return exports[name]

    if name in {"classify_obligation", "detect_ambiguity", "enrich_requirement"}:
        from specforge_distill.extract.classifier import (
            classify_obligation,
            detect_ambiguity,
            enrich_requirement,
        )

        exports = {
            "classify_obligation": classify_obligation,
            "detect_ambiguity": detect_ambiguity,
            "enrich_requirement": enrich_requirement,
        }
        return exports[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
