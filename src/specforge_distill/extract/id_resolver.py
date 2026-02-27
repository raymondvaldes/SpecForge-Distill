"""Logic for preserving source IDs and generating stable deterministic IDs."""

import re
import hashlib
from typing import Optional

from specforge_distill.models.candidates import normalize_text


def detect_source_id(text: str) -> Optional[str]:
    """
    Detect requirement IDs from source text using common patterns.
    
    Supports:
    - REQ-001, REQ_001
    - [R-123], [REQ-123]
    - 3.2.1-1 (Section-based IDs)
    """
    patterns = [
        r"^\[(R(?:EQ)?-\d+)\]",        # [R-123] or [REQ-123] at start
        r"^(REQ[-_]\d+)",              # REQ-001 or REQ_001 at start
        r"^(\d+\.(?:\d+\.)*\d+-\d+)",  # 3.2.1-1 at start
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
            
    return None


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
