# Roadmap: SpecForge Distill

## Overview

This roadmap delivers SpecForge Distill from PDF ingestion to auditable AI-ready markdown outputs in four phases. The sequencing prioritizes trust-critical capabilities first: extraction coverage and provenance, then requirement identity/obligation handling, then packaging and interop hooks, and finally hardening through deterministic verification.

## Phases

- [x] **Phase 1: Extraction and Provenance Foundation** - Build core PDF ingestion and citation-grounded extraction pipeline. (Completed 2026-02-26)
- [x] **Phase 2: Requirement Modeling and Obligation Detection** - Implement requirement normalization, IDs, obligation classification, and review flags. (Completed 2026-02-27)
- [x] **Phase 3: Output Packaging and Interop Hooks** - Deliver consolidated/split outputs, manifest, runtime controls, and SysML-v2-ready metadata hooks. (Completed 2026-02-27)
- [x] **Phase 4: Determinism and Release Hardening** - Enforce repeatable outputs and validate v1 reliability for internal MBSE usage. (Completed 2026-02-27)

## Phase Details

### Phase 1: Extraction and Provenance Foundation
**Goal**: Establish reliable single-PDF ingestion and page-cited extraction of core artifact content.
**Completed**: 2026-02-26

### Phase 2: Requirement Modeling and Obligation Detection
**Goal**: Normalize extracted requirements with stable identities, obligation classes, and review-ready ambiguity flags.
**Completed**: 2026-02-27

### Phase 3: Output Packaging and Interop Hooks
**Goal**: Produce complete v1 deliverables for human and machine consumers with local-first runtime behavior.
**Completed**: 2026-02-27

### Phase 4: Determinism and Release Hardening
**Goal**: Verify stable repeatable behavior and readiness for internal MBSE team adoption.
**Completed**: 2026-02-27

Plans:
- [x] 04-01: Build deterministic ordering/idempotency test harness and audit extraction loops
- [x] 04-02: Create regression fixture suite for complex tables, captions, and obligation edge cases
- [x] 04-03: Finalize release guardrails and v1 acceptance checklist

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Extraction and Provenance Foundation | 5/5 | Complete | 2026-02-26 |
| 2. Requirement Modeling and Obligation Detection | 4/4 | Complete | 2026-02-27 |
| 3. Output Packaging and Interop Hooks | 4/4 | Complete | 2026-02-27 |
| 4. Determinism and Release Hardening | 3/3 | Complete | 2026-02-27 |

**Milestone v1.0.0 achieved: 2026-02-27**
