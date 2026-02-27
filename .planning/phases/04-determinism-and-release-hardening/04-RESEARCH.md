# Research: Phase 4 - Determinism and Release Hardening

## Overview
Phase 4 focuses on ensuring that SpecForge Distill produces identical outputs for identical inputs across different environments and runs. The current implementation already uses SHA1-based hashing for ID generation, but there are opportunities to harden the ordering and establish a robust regression suite before the v1.0.0 release.

## Requirement Analysis

### CLI-03: Deterministic Outputs
- **Goal**: Re-running on unchanged input produces stable IDs and deterministic output ordering.
- **Current State**: 
  - `stable_candidate_id` uses `page`, `index`, and `text` hash. This is deterministic if the extraction order is stable.
  - `stable_artifact_id` uses `section`, `page`, and `content` hash.
- **Risks**:
  - Unsorted dictionary iteration (e.g., `table_rows_by_page` keys).
  - Unsorted set iteration.
  - Environment-dependent absolute paths in `manifest.json`.
  - Non-deterministic semantic linking order.

## Implementation Strategy

### 1. Determinism Hardening
- **Audit**: Review all loops over dictionaries and sets in `src/specforge_distill/extract/` and `src/specforge_distill/pipeline.py`.
- **Action**: Wrap iterations in `sorted()` where keys or values affect the final list of candidates or artifacts.
- **Relative Paths**: Ensure all paths in `manifest.json` (e.g., `source_pdf`, `target_file`) are relative to the output directory or documented as relative to the execution root.

### 2. Regression Fixture Suite
- **Goal**: Validate no loss in requirement/provenance coverage for core document patterns.
- **Structure**:
  - `tests/regression/fixtures/`: Directory for complex PDFs and their expected outputs.
  - `tests/regression/test_determinism.py`: A test that runs the tool multiple times and compares the output byte-for-byte (or semantically for JSON).

### 3. Release Guardrails
- **Goal**: Finalize v1 readiness and enforce out-of-scope boundaries.
- **Checklist**:
  - [ ] **Determinism**: Identical `manifest.json` across 3 runs.
  - [ ] **Schema**: `manifest.json` validates against Pydantic models.
  - [ ] **Coverage**: Extraction and rendering modules have high unit test coverage.
  - [ ] **Provenance**: 100% of requirements have valid citations.

## Technical Risks
- **Dictionary Iteration in Python 3.7+**: While dicts are insertion-ordered in modern Python, they are not *sorted*. If the insertion order depends on non-deterministic events, the iteration order will also be non-deterministic.
- **Floating Point Precision**: If any confidence scores or coordinates are compared, small precision differences could lead to different branching.

## Proposed Plans

- **04-01**: Build deterministic ordering/idempotency test harness and audit extraction loops.
- **04-02**: Create regression fixture suite for complex tables, captions, and obligation edge cases.
- **04-03**: Finalize release guardrails and v1 acceptance checklist.
