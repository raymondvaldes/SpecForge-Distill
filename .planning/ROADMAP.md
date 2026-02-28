# Roadmap: SpecForge Distill

## Overview

`v1.2.0` builds on the shipped `v1.1.0` trust-and-runtime release. The next milestone focuses on broader day-to-day CLI usefulness through deterministic batch workflows, clearer scanned/OCR boundaries, and stronger validation/export hooks without weakening the citation-grounded core.

## Milestones

- [x] **v1.0.1 Stable Binary Release** - Shipped 2026-02-28. Archive: `.planning/milestones/v1.0.1-ROADMAP.md`
- [x] **v1.1.0 Trusted Distribution And Runtime Release** - Shipped 2026-02-28. Archive: `.planning/milestones/v1.1.0-ROADMAP.md`
- [ ] **v1.2.0** - In progress

## Phases

- [ ] **Phase 7: Batch Processing and Aggregate Reporting** - Add multi-file CLI workflows with deterministic output naming and machine-readable summaries.
- [ ] **Phase 8: Extended Ingestion and Validation Hooks** - Improve scanned/OCR diagnostics and add downstream validation/export-oriented hooks.

## Phase Details

### Phase 7: Batch Processing and Aggregate Reporting

**Goal**: Let users process multiple PDFs in one run without losing determinism or actionable failure reporting.

Plans:

- [ ] 07-01: Add batch CLI mode for directory and explicit multi-file inputs
- [ ] 07-02: Emit aggregate batch summaries and machine-readable status output
- [ ] 07-03: Add regression and failure-handling coverage for partial batch failures

### Phase 8: Extended Ingestion and Validation Hooks

**Goal**: Broaden supported workflows without weakening the deterministic, citation-grounded core.

Plans:

- [ ] 08-01: Detect scanned/OCR-only PDFs explicitly and improve user guidance
- [ ] 08-02: Add validation/lint-oriented output hooks for downstream review
- [ ] 08-03: Define richer interop/export contracts for later SysML-oriented tooling

## Progress

**Execution Order:**
Phases execute in numeric order: 7 → 8

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 7. Batch Processing and Aggregate Reporting | 0/3 | Not Started | — |
| 8. Extended Ingestion and Validation Hooks | 0/3 | Not Started | — |

**Latest shipped milestone: `v1.1.0` on 2026-02-28**
