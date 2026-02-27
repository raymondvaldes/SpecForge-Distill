"""Extraction logic for requirement entities."""

from specforge_distill.extract.id_resolver import (
    detect_source_id,
    generate_stable_id,
    resolve_requirement_id,
)
from specforge_distill.extract.classifier import (
    classify_obligation,
    detect_ambiguity,
    enrich_requirement,
)

__all__ = [
    "detect_source_id",
    "generate_stable_id",
    "resolve_requirement_id",
    "classify_obligation",
    "detect_ambiguity",
    "enrich_requirement",
]
