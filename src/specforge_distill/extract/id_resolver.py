"""Logic for preserving source IDs and generating stable deterministic IDs."""

from __future__ import annotations

import hashlib
import re
from typing import List, Optional

from specforge_distill.models.candidates import normalize_text


class PatternRegistry:
    """Registry for requirement ID detection patterns."""

    def __init__(self) -> None:
        self._patterns: List[re.Pattern] = [
            re.compile(r"\[(R(?:EQ)?-\d+)\]", re.IGNORECASE),  # [R-123] or [REQ-123]
            re.compile(r"(REQ[-_]\d+)", re.IGNORECASE),        # REQ-001 or REQ_001
            re.compile(r"(\d+\.(?:\d+\.)*\d+-\d+)"),           # 3.2.1-1
        ]

    def add_pattern(self, regex: str, flags: int = re.IGNORECASE) -> None:
        """Register a new ID pattern."""
        self._patterns.append(re.compile(regex, flags))

    def detect(self, text: str) -> Optional[str]:
        """Attempt to detect an ID using registered patterns."""
        for pattern in self._patterns:
            match = pattern.search(text)
            if match:
                return match.group(1)
        return None


# Global registry for v1
_REGISTRY = PatternRegistry()


def detect_source_id(text: str) -> Optional[str]:
    """Detect requirement IDs from source text using registered patterns."""
    return _REGISTRY.detect(text)


def generate_stable_id(text: str, page: int, source_type: str) -> str:
    """
    Generate a deterministic SHA1-based ID for anonymous requirements.
    
    Includes page and source_type in seed to prevent collisions for identical text.
    """
    normalized = normalize_text(text)
    seed = f"{source_type}:{page}:{normalized}"
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:10]
    
    return f"req-{source_type}-{page:03d}-{digest}"


def resolve_requirement_id(text: str, page: int, source_type: str) -> str:
    """
    Resolve the final ID for a requirement, prioritizing source-provided IDs.
    """
    source_id = detect_source_id(text)
    if source_id:
        return source_id
        
    return generate_stable_id(text, page, source_type)
