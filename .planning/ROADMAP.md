# Roadmap: SpecForge Distill

## Overview

This roadmap delivers SpecForge Distill from PDF ingestion to auditable AI-ready markdown outputs in four phases. The sequencing prioritizes trust-critical capabilities first: extraction coverage and provenance, then requirement identity/obligation handling, then packaging and interop hooks, and finally hardening through deterministic verification.

## Phases

- [x] **Phase 1: Extraction and Provenance Foundation** - Build core PDF ingestion and citation-grounded extraction pipeline. (Completed 2026-02-26)
- [x] **Phase 2: Requirement Modeling and Obligation Detection** - Implement requirement normalization, IDs, obligation classification, and review flags. (Completed 2026-02-27)
- [x] **Phase 3: Output Packaging and Interop Hooks** - Deliver consolidated/split outputs, manifest, runtime controls, and SysML-v2-ready metadata hooks. (Completed 2026-02-27)
- [ ] **Phase 4: Determinism and Release Hardening** - Enforce repeatable outputs and validate v1 reliability for internal MBSE usage.

## Phase Details

### Phase 1: Extraction and Provenance Foundation
**Goal**: Establish reliable single-PDF ingestion and page-cited extraction of core artifact content.
**Depends on**: Nothing (first phase)
**Requirements**: ING-01, ING-02, REQ-01, REQ-02, ART-01, OUT-01, OUT-02
**Success Criteria** (what must be TRUE):
  1. User can run `distill <file.pdf>` on a digital-text PDF and receive extracted narrative/table/caption content.
  2. All extracted requirements and architecture artifact blocks include valid page-level citations.
  3. Low text-layer quality pages are detected and surfaced to the user as warnings.
  4. Architecture sections are captured as structured markdown blocks with preserved source references.
**Plans**: 5 plans

Plans:
- [x] 01-01: Implement CLI entrypoint, PDF loader, and text-layer quality diagnostics
- [x] 01-02: Build section extraction for narrative architecture and requirement text
- [x] 01-03: Add table/caption extraction pass and merge strategy
- [x] 01-04: Implement provenance model and citation propagation checks
- [x] 01-05: Add phase acceptance harness for extraction channels, warnings, and citation completeness

### Phase 2: Requirement Modeling and Obligation Detection
**Goal**: Normalize extracted requirements with stable identities, obligation classes, and review-ready ambiguity flags.
**Depends on**: Phase 1
**Requirements**: REQ-03, REQ-04, REQ-05, REQ-06, ART-02
**Success Criteria** (what must be TRUE):
  1. Existing requirement IDs are preserved exactly, and deterministic IDs are generated when IDs are absent.
  2. Requirements are classified for obligation language (`shall`, `must`, `required`) with transparent rule behavior.
  3. Ambiguous or low-confidence requirement candidates are retained and flagged for review rather than dropped.
  4. VCRM-rebuild attributes are captured when present and persisted in canonical requirement records.
**Plans**: 4 plans

Plans:
- [x] 02-01: Define canonical requirement schema (including VCRM-rebuild attributes)
- [x] 02-02: Implement ID preservation/generation and determinism safeguards
- [x] 02-03: Implement obligation classifier and ambiguity/confidence flagging
- [x] 02-04: Build requirement normalization tests with edge-case fixtures

### Phase 3: Output Packaging and Interop Hooks
**Goal**: Produce complete v1 deliverables for human and machine consumers with local-first runtime behavior.
**Depends on**: Phase 2
**Requirements**: OUT-03, OUT-04, OUT-05, CLI-01, CLI-02, RUN-01, INT-01
**Success Criteria** (what must be TRUE):
  1. A run emits both consolidated markdown and split artifact markdown package from one canonical source.
  2. A `manifest.json` is generated and indexes entities, files, and citation links.
  3. Output location defaults next to source PDF, with `-o <dir>` override working consistently.
  4. Local-only runtime is default, with optional external AI usage requiring explicit opt-in.
  5. Canonical entities include lightweight SysML-v2 interop metadata hooks without model generation.
**Plans**: 4 plans

Plans:
- [x] 03-01: Implement markdown renderers for consolidated and split outputs
- [x] 03-02: Implement manifest writer and schema validation
- [x] 03-03: Implement output-path behavior (default and -o) and runtime mode controls
- [x] 03-04: Add interop metadata hooks and output compatibility checks

### Phase 4: Determinism and Release Hardening
**Goal**: Verify stable repeatable behavior and readiness for internal MBSE team adoption.
**Depends on**: Phase 3
**Requirements**: CLI-03
**Success Criteria** (what must be TRUE):
  1. Re-running the tool on unchanged input produces stable IDs and deterministic output ordering.
  2. Regression fixture suite validates no loss in requirement/provenance coverage for core document patterns.
  3. Release checklist confirms v1 constraints and out-of-scope boundaries are enforced.
**Plans**: 3 plans

Plans:
- [ ] 04-01-PLAN.md — Build deterministic ordering/idempotency test harness and audit extraction loops.
- [ ] 04-02-PLAN.md — Create regression fixture suite for complex tables, captions, and obligation edge cases.
- [ ] 04-03-PLAN.md — Finalize release guardrails and v1 acceptance checklist.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Extraction and Provenance Foundation | 5/5 | Complete | 2026-02-26 |
| 2. Requirement Modeling and Obligation Detection | 4/4 | Complete | 2026-02-27 |
| 3. Output Packaging and Interop Hooks | 4/4 | Complete | 2026-02-27 |
| 4. Determinism and Release Hardening | 0/3 | Not started | - |
