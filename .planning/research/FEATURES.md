# Feature Research

**Domain:** AI-ready markdown distillation from legacy systems-engineering PDFs
**Researched:** 2026-02-26
**Confidence:** MEDIUM-HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| PDF ingest + parse (digital text) | Core entry point for legacy spec conversion | LOW | v1 scope explicitly PDF-only |
| Structured requirement extraction | MBSE workflows need requirements as first-class objects | MEDIUM | Include statement, IDs, obligation type, provenance |
| Original ID preservation + generated IDs when missing | Traceability depends on continuity with legacy identifiers | MEDIUM | Canonical IDs should be deterministic |
| Page-level citations | Teams must audit outputs back to source PDFs | MEDIUM | Required for trust and review workflows |
| SHALL + mandatory-form detection | Obligation statements are critical and cannot be missed | HIGH | Cover `shall`, `must`, `required` patterns with confidence flags |
| Table/caption requirement extraction | Specs often hide key requirements in tables/figure contexts | HIGH | Must be included in v1 according to project priorities |
| Dual markdown outputs (consolidated + split package) | Different consumers need different artifact granularity | MEDIUM | Single review file + machine-ingestion package |
| Low-confidence review flags | Human review must focus on ambiguous extraction cases | MEDIUM | No silent drops |
| Sequence diagram image/context capture | Preserve diagram intent until Mermaid conversion (v2) | MEDIUM | Capture image + nearby explanatory text |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| VCRM-rebuild-ready requirement attributes | Enables downstream compliance and verification workflows | HIGH | Attribute completeness drives utility in MBSE contexts |
| Deterministic + AI hybrid extraction modes | Balances enterprise auditability with higher recall when needed | HIGH | External API only as optional quality fallback |
| Explicit trace graph links (`req -> arch -> verification`) | Creates direct bridge into future SpecForge products | HIGH | Better than plain markdown dumps |
| Domain-aware artifact typing (CONOPS/architecture/SysML-adjacent) | Reduces manual sorting effort after conversion | HIGH | Requires robust section classification heuristics |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Full OCR/scan support in v1 | “Handle every PDF immediately” | Adds major quality and tuning complexity, dilutes core quality bar | Keep v1 digital-text only; design OCR adapter for v2 |
| Large-scale batch orchestration first | “Save time on many docs” | Hides extraction quality defects until late; harder debugging | Nail single-document fidelity first, then scale |
| Auto-rewriting requirements into new wording | “Make requirements cleaner” | Risks semantic drift and loss of contractual language | Preserve original wording + add normalized metadata |
| Early Mermaid auto-generation from ambiguous diagrams | “Need immediately reusable diagrams” | High hallucination/incorrect flow risk from partial context | Capture images/context in v1, generate Mermaid in v2 |

## Feature Dependencies

```
PDF ingest + parse
    └──requires──> provenance capture
                      └──enables──> auditable markdown output

requirement extraction
    └──requires──> section + table/caption extraction
                      └──enables──> SHALL recall quality

dual output rendering
    └──requires──> canonical schema + manifest
```

### Dependency Notes

- **Requirement extraction requires table/caption extraction:** missing these creates unacceptable recall gaps for critical obligations.
- **Provenance capture enables trust:** without page citations, MBSE reviewers cannot validate extracted claims.
- **Dual output requires canonical schema:** consolidated and split files must come from the same normalized source to prevent drift.

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [ ] PDF (digital-text) ingest and parsing
- [ ] Requirement + architecture + CONOPS structured extraction
- [ ] Original/generate ID strategy for requirements
- [ ] SHALL/must/required detection with confidence flags
- [ ] Table/caption extraction for requirement coverage
- [ ] Page-level citations across outputs
- [ ] Consolidated markdown + split markdown package + manifest index
- [ ] Sequence diagram image/context capture

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] Extraction quality checks/reporting command (coverage and uncertainty summaries)
- [ ] Small-batch folder processing

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] OCR/scanned PDF support
- [ ] Mermaid generation for sequence diagrams
- [ ] Deeper automated traceability graph reconstruction
- [ ] Windows/PowerShell support

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| SHALL + mandatory extraction recall | HIGH | HIGH | P1 |
| Page-level provenance | HIGH | MEDIUM | P1 |
| Table/caption requirement extraction | HIGH | HIGH | P1 |
| Dual output packaging | HIGH | MEDIUM | P1 |
| Sequence image/context capture | MEDIUM | MEDIUM | P2 |
| Batch mode | MEDIUM | MEDIUM | P2 |
| Mermaid generation | MEDIUM | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Docling | Unstructured | Our Approach |
|---------|---------|--------------|--------------|
| Generic document conversion | Strong | Strong | Narrower, domain-specific for specs/MBSE |
| Requirement-obligation extraction | Generic | Generic | Explicit SHALL-class and mandatory-form focus |
| Provenance for MBSE audit | Partial/general | Partial/general | Page-level citations as first-class artifact |
| VCRM-rebuild orientation | Not primary focus | Not primary focus | Explicitly designed for requirement attribute recovery |

## Sources

- https://pypi.org/project/docling/ — feature scope of Docling ecosystem
- https://pypi.org/project/unstructured/ — feature scope of Unstructured ecosystem
- https://www.incose.org/ — systems engineering and requirements quality context

---
*Feature research for: spec PDF distillation CLI*
*Researched: 2026-02-26*
