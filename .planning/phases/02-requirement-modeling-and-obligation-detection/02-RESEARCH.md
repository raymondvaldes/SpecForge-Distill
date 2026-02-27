# Phase 2: Requirement Modeling and Obligation Detection - Research

**Researched:** 2026-02-26
**Domain:** Requirement Engineering, NLP, Pydantic Modeling
**Confidence:** HIGH

## Summary

This phase focuses on transforming raw extraction "candidates" into formal "Requirement" records. The research confirms that a Pydantic-based schema is the standard for modern Python data validation, providing the necessary structure for VCRM (Verification Cross Reference Matrix) attributes and provenance links. 

The primary recommendation is to transition from simple dataclasses to Pydantic models to enable robust validation and serialization. ID generation will utilize a hybrid approach: preserving source IDs when detected and falling back to stable SHA1-based hashes for anonymous requirements. Obligation detection will remain rule-based for v1, leveraging the existing `obligation_verbs.yml` but adding checks for "weak" verbs and ambiguity patterns.

**Primary recommendation:** Use Pydantic `BaseModel` for the canonical requirement schema and implement a multi-stage ID resolver that prioritizes source-provided IDs.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| REQ-03 | Obligation classification (`shall`, `must`, `required`) | Rule-based classification against `obligation_verbs.yml` is confirmed as a robust v1 approach. |
| REQ-04 | Preserve existing IDs | Research indicates regex-based ID detection (e.g., `REQ-001`) during extraction is needed to populate the `id` field before hashing. |
| REQ-05 | Deterministic canonical IDs | SHA1 hashing of normalized text + page number provides stability across runs as seen in Phase 1 prototypes. |
| REQ-06 | Ambiguity/low-confidence flags | Linguistic patterns (passive voice, vague quantifiers) identified as standard criteria for flagging. |
| ART-02 | VCRM-rebuild attributes | Standard VCRM attributes (Verification Method, Rationale, Allocation) mapped to Pydantic optional fields. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pydantic | ^2.0 | Data validation/Schema | Industry standard for type-safe Python data models. |
| PyYAML | ^6.0 | Configuration | Already used for `obligation_verbs.yml`. |
| hashlib | (stdlib) | ID Generation | Built-in support for stable SHA1/SHA256 hashing. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|--------------|
| Spacy | ^3.0 | NLP/POS Tagging | Use if regex-based ambiguity detection proves insufficient for passive voice. |

## Architecture Patterns

### Recommended Project Structure
Existing structure is sound. Phase 2 will enhance `models/` and add logic to `extract/`.
```
src/specforge_distill/
├── models/
│   ├── requirement.py    # NEW: Pydantic-based canonical Requirement model
│   └── candidates.py     # Keep: For raw extraction stage
├── extract/
│   ├── classifier.py     # NEW: Obligation and Ambiguity logic
│   └── id_resolver.py    # NEW: Logic for REQ-04 and REQ-05
└── config/
    └── obligation_verbs.yml
```

### Pattern 1: Multi-Stage ID Resolution
**What:** A strategy to assign IDs based on priority: (1) Source ID, (2) User-provided mapping, (3) Deterministic hash.
**When to use:** To satisfy REQ-04 and REQ-05.

### Pattern 2: VCRM Attribute Mapping
**What:** Define a nested `VCRMAttributes` model within the `Requirement` schema to hold verification data.
**When to use:** To satisfy ART-02.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Data Validation | Manual `__post_init__` checks | Pydantic | Handles coercion, validation, and JSON schema export automatically. |
| Hashing | Custom string summing | `hashlib.sha1` | Prevents collisions and ensures platform independence. |
| YAML Parsing | Manual string splitting | `yaml.safe_load` | Security and correctness. |

## Common Pitfalls

### Pitfall 1: ID Collisions on Duplicate Text
**What goes wrong:** Two different requirements with identical text (e.g., "The system shall be grounded.") on different pages get the same hash.
**How to avoid:** Include `page_number` and `source_type` in the hash seed.

### Pitfall 2: Brittle Regex for IDs
**What goes wrong:** Missing source IDs like `[R-123]` or `3.2.1-1` because regex is too narrow.
**How to avoid:** Use a configurable set of regex patterns for ID detection.

## Code Examples

### Canonical Pydantic Requirement (Draft)
```python
from pydantic import BaseModel, Field
from typing import Optional, List

class VCRMAttributes(BaseModel):
    method: Optional[str] = None  # Test, Demo, Inspection, Analysis
    rationale: Optional[str] = None
    allocation: Optional[str] = None
    success_criteria: Optional[str] = None

class Requirement(BaseModel):
    id: str
    text: str
    obligation: str  # shall, must, should, etc.
    page: int
    is_ambiguous: bool = False
    ambiguity_reasons: List[str] = []
    vcrm: VCRMAttributes = Field(default_factory=VCRMAttributes)
    provenance_link: str
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Dataclasses | Pydantic v2 | 2023 | 10x performance boost and better TypeAdapter support. |
| Simple Regex | NLP-informed rules | - | Better detection of "passive voice" ambiguity. |

## Sources

### Primary (HIGH confidence)
- `src/specforge_distill/models/candidates.py` - Existing candidate model.
- `src/specforge_distill/config/obligation_verbs.yml` - Existing config.

### Secondary (MEDIUM confidence)
- INCOSE Guide to Writing Requirements - For ambiguity criteria (passive voice, vague words).
- Pydantic Official Documentation - For schema best practices.

## Metadata
**Research date:** 2026-02-26
**Valid until:** 2026-03-26
