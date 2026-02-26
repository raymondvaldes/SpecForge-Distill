# Deep-Dive Research: SysML v2 + INCOSE Quality Guidance

**Project:** SpecForge Distill
**Researched:** 2026-02-26
**Focus:** SysML v2 ecosystem readiness and INCOSE requirement quality/attribute alignment
**Confidence:** HIGH (status/version facts), MEDIUM-HIGH (product implications)

## SysML v2 Research Findings

### 1) SysML v2 Is Now Formal (Not Just Beta)

OMG currently marks these as **formal/final** with publication date January 2026:

- SysML v2 Language, formal/final (`ptc/25-04-31`)
- SysML v2 Transformation, formal/final (`ptc/25-04-32`)
- KerML 1.0, formal/final (`ptc/25-04-18`)
- Systems Modeling API and Services 1.0, formal/final (`ptc/25-04-24`)

Practical implication:

- Distill should treat SysML v2 compatibility as a near-term product direction, not speculative R&D.

### 2) SysML v2 Release Cadence Is Active

The SysML-v2 Release repository notes:

- `2025-09`: includes final/final updates and synchronization with formal versions.
- `2025-11`: bugfix release.
- `2026-01`: bugfix release.

Practical implication:

- Keep a versioned adapter boundary for SysML-specific mappings because post-formal bugfix cadence continues.

### 3) Pilot Implementation + Textual/Model Formats Are Public

SysML-v2 Release content includes:

- Pilot implementation and API/services usage guidance
- Textual notation samples
- Multiple forms: `.sysml`, `.kerml`, packaged forms (`.kpar`), and XMI forms (`.sysmlx`, `.kermlx`)

Practical implication:

- Distill should preserve enough normalized structure to enable future exports/transforms into SysML v2 textual/model artifacts.

## INCOSE Research Findings

### 1) INCOSE GtWR v4 Characteristics of Good Requirements

The public INCOSE Guide for Writing Requirements v4 summary states requirement quality characteristics such as:

- Necessary
- Implementation-free
- Unambiguous
- Singular
- Feasible
- Verifiable
- Correct
- Conforming

Practical implication:

- Distill review flags can be expanded beyond extraction confidence to quality checks aligned with these characteristics.

### 2) INCOSE Requirement Attribute Set (VCRM-Relevant)

The same summary identifies a 15-attribute framework including:

- Identifier
- Title
- Statement(s)
- Rationale
- Parent/child relationship
- Verification method
- Unit
- Quantitative values
- Tolerance
- Assumptions
- Source
- Priority
- Risk
- Verification evidence

Practical implication:

- Your VCRM rebuild goal is well-supported by aligning canonical schema to these attribute buckets now, even if some remain optional in v1.

## Direct Impact on SpecForge Distill Scope

### Recommended Additions to Requirements

1. Add explicit requirement metadata slots for INCOSE-aligned attributes (at least identifier, statement, source, verification method, rationale/evidence placeholders).
2. Add a future-facing compatibility requirement: preserve normalized artifact typing that can map to SysML v2 constructs in v2.
3. Add output manifest metadata for `model_interop_target` (e.g., `none`, `sysmlv2-future`) to avoid schema migration pain later.

### Proposed v1/v2 Boundary Clarification

- **v1:** Extract from PDFs into markdown + canonical metadata with SysML-v2-ready typing hooks.
- **v2:** Generate/transform into SysML v2 textual or model artifacts and/or integrate with Systems Modeling API services.

## Sources

### SysML v2 (Primary)

- OMG SysML 2.0 formal page: https://www.omg.org/spec/SysML/2.0/About-SysML
- OMG Systems Modeling API 1.0 formal page: https://www.omg.org/spec/SystemsModelingAPI/1.0/About-SystemsModelingAPI
- OMG KerML 1.0 formal page: https://www.omg.org/spec/KerML/1.0/About-KerML
- SysML-v2 Release (official project repo): https://github.com/Systems-Modeling/SysML-v2-Release

### INCOSE (Primary)

- INCOSE Guide for Writing Requirements v4 Summary Sheet (public): https://www.incose.org/docs/default-source/working-groups/requirements-wg/gtwr-summary-sheet-v4.pdf

## Confidence Notes

- SysML v2 status is explicit and high confidence from OMG formal pages.
- INCOSE quality/attribute framework is high confidence from published INCOSE summary material.
- Exact one-to-one mapping from PDF narrative to SysML v2 model constructs remains medium confidence until tested on real source docs.

---
*Deep-dive completed: 2026-02-26*
