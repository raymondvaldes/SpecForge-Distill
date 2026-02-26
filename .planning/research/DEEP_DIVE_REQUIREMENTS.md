# Deep-Dive Research: SHALL Semantics and VCRM-Rebuild Fields

**Project:** SpecForge Distill
**Researched:** 2026-02-26
**Focus:** Obligation extraction quality and verification/compliance trace attributes
**Confidence:** HIGH (for source-backed fields), MEDIUM (for implementation heuristics)

## Why This Deep Dive

You asked for stronger research to reduce risk of missing critical requirements. This addendum narrows scope to:

1. What counts as a requirement statement vs non-requirement language
2. Minimum fields needed to rebuild verification/compliance-style matrices from extracted content
3. Stack/version updates that affect extraction reliability

## Findings

### 1) Requirement Language Semantics (Primary Source: NASA SE Handbook Rev 2)

NASA’s published guidance provides directly useful normalization rules for v1 extraction logic:

- `Shall = requirement`
- `Will = facts or declaration of purpose`
- `Should = goal`
- Good requirement statements should use complete `shall` statements, ideally with a single `shall` per statement.

Practical implication for SpecForge Distill v1:

- Treat `shall` as highest-confidence obligation indicator.
- Treat `must` and `required` as mandatory equivalents with lower initial confidence unless project rules promote them.
- Flag multi-obligation sentences for review when one sentence appears to bundle multiple obligations.

### 2) Minimum Verification Matrix Fields (Primary Source: NASA Table D-1)

NASA’s example Requirements Verification Matrix includes the exact fields most relevant to your VCRM-rebuild goal:

- Requirement No. (unique identifier)
- Document
- Paragraph
- Shall Statement
- Verification Success Criteria
- Verification Method (analysis, inspection, demonstration, test)
- Facility or Lab
- Phase
- Acceptance Requirement?
- Preflight Acceptance?
- Performing Organization
- Results (objective evidence reference)

Practical implication for SpecForge Distill v1:

- Even if not all fields are always present in source PDFs, canonical schema should include optional slots for these attributes.
- Requirement outputs should preserve enough context (document/page/paragraph anchor + statement text) to reconstruct verification rows.

### 3) Validation Matrix Companion Fields (Primary Source: NASA Table E-1)

NASA’s example Validation Requirements Matrix includes:

- Validation Product #
- Activity
- Objective
- Validation Method
- Facility/Lab
- Phase
- Performing Organization
- Results (objective evidence)

Practical implication for SpecForge Distill v1:

- Add validation-oriented attribute hooks in requirement metadata now, even if full validation matrix generation is deferred.

### 4) Tooling and Version Updates (Primary Sources: PyPI)

Latest observed stable versions (as of 2026-02-26 research pass):

- pypdf: `6.7.0` (uploaded 2026-02-08)
- pdfplumber: `0.11.9` (uploaded 2026-01-05)
- Typer: `0.24.1` (uploaded 2026-02-21)
- Pydantic: `2.12.5` (2025-11-26 release)
- Ruff: `0.15.1` (2026-02-12)
- pytest: `9.0.2` (2025-12-06)

Practical implication for SpecForge Distill v1:

- Pin to these versions (or tested ranges around them) for initial reproducibility baseline.
- Re-run compatibility check before implementation start if planning window extends.

## Proposed Requirement Impacts

Based on this deeper research, consider adding these to v1 requirements scope:

1. **REQ-XX:** Classify modal verbs (`shall`/`must`/`required`/`will`/`should`) and store obligation class in metadata.
2. **REQ-XX:** Capture paragraph-level anchors in addition to page-level citations when paragraph IDs are inferable.
3. **REQ-XX:** Include optional verification attributes in canonical requirement schema (method, success criteria, phase, performing organization, evidence reference).
4. **REQ-XX:** Flag potential multi-obligation requirement statements for human review.

## Sources

### Primary

- NASA Systems Engineering Handbook Rev 2 (PDF): https://essp.larc.nasa.gov/EVI-6/pdf_files/NASA_SystemsEngineeringHandbookRev2.pdf
  - Appendix C: `Shall = requirement`, `Will = facts`, `Should = goal`
  - Section 4.2.1.2.3: acceptable requirement statements with a single `shall`
  - Appendix D Table D-1: verification matrix fields
  - Appendix E Table E-1: validation matrix fields

- PyPI project pages:
  - pypdf: https://pypi.org/project/pypdf/
  - pdfplumber: https://pypi.org/project/pdfplumber/
  - typer: https://pypi.org/pypi/typer/
  - pydantic: https://pypi.org/project/pydantic/
  - ruff: https://pypi.org/project/ruff/
  - pytest: https://pypi.org/project/pytest/

## Confidence Notes

- The matrix field recommendations are directly sourced from a primary systems-engineering reference and are strong anchors for your VCRM-rebuild direction.
- Mapping `must`/`required` into the same confidence class as `shall` is a policy decision and should remain configurable.

---
*Deep-dive completed: 2026-02-26*
