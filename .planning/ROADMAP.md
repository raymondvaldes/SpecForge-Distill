# Roadmap: SpecForge Distill

## Overview

`v1.1.0` builds on the shipped binary-first `v1.0.1` release. The next milestone focuses on trusted distribution, smoother cross-platform operation, broader day-to-day CLI usefulness, and follow-on validation/interop hooks without sacrificing deterministic outputs.

## Milestones

- [x] **v1.0.1 Stable Binary Release** - Shipped 2026-02-28. Archive: `.planning/milestones/v1.0.1-ROADMAP.md`
- [ ] **v1.1.0** - In progress

## Phases

- [x] **Phase 5: Trusted Distribution and Install Verification** - Turn the published binary story into a verifiable, lower-friction install experience. (completed 2026-02-28)
- [ ] **Phase 6: Cross-Platform Runtime Ergonomics** - Improve wrapper/runtime UX across WSL, Ubuntu, macOS, and Windows PowerShell 7.
- [ ] **Phase 7: Batch Processing and Aggregate Reporting** - Add multi-file CLI workflows with deterministic output naming and machine-readable summaries.
- [ ] **Phase 8: Extended Ingestion and Validation Hooks** - Improve scanned/OCR diagnostics and add downstream validation/export-oriented hooks.

## Phase Details

### Phase 5: Trusted Distribution and Install Verification
**Goal**: Make official release assets easier to trust, verify, and adopt without manual Python setup.

Plans:
- [x] 05-01: Finalize signing/notarization validation and release trust checks
- [x] 05-02: Add install/self-test guidance and checksum-first verification flows
- [x] 05-03: Tighten release notes and artifact publishing automation

### Phase 6: Cross-Platform Runtime Ergonomics
**Goal**: Remove platform-specific friction in local usage, especially for PowerShell 7 and WSL users.

Plans:
- [ ] 06-01: Improve PowerShell-friendly and WSL-friendly wrapper and invocation paths
- [ ] 06-02: Harden path, permissions, and malformed-input error messaging
- [ ] 06-03: Expand platform verification coverage for first-run workflows

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
Phases execute in numeric order: 5 → 6 → 7 → 8

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 5. Trusted Distribution and Install Verification | 3/3 | Complete | 2026-02-28 |
| 6. Cross-Platform Runtime Ergonomics | 0/3 | Not Started | — |
| 7. Batch Processing and Aggregate Reporting | 0/3 | Not Started | — |
| 8. Extended Ingestion and Validation Hooks | 0/3 | Not Started | — |

**Latest shipped milestone: `v1.0.1` on 2026-02-28**
