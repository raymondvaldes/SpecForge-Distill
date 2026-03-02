---
phase: 07-batch-processing-and-aggregate-reporting
plan: 03
subsystem: testing
tags: [acceptance, determinism, reliability, fast-ivv, docker, malformed-input]
requires:
  - phase: 07-01
    provides: deterministic batch entry path and helper boundaries
  - phase: 07-02
    provides: aggregate batch summary and partial-failure contract
provides:
  - acceptance coverage for mixed-success batch runs
  - fast IV&V boundary checks
  - reliability fixes for malformed-input and Docker availability paths
affects: [full-suite-runtime, contributor-feedback, ivv-docs]
tech-stack:
  added: []
  patterns:
    - "Fast IV&V marker for small high-signal changes"
    - "Explicit runtime precondition assertions instead of environment-driven skips where practical"
key-files:
  created: []
  modified:
    - tests/phase3/test_phase3_acceptance.py
    - tests/test_v1_acceptance_final.py
    - tests/test_determinism.py
    - tests/reliability/test_stress_and_robustness.py
    - tests/reliability/test_docker.py
    - tests/reliability/test_wrapper_and_fixture_contracts.py
    - tests/phase1/test_ingest_and_quality.py
    - src/specforge_distill/ingest/pdf_loader.py
    - src/specforge_distill/normalize.py
    - src/specforge_distill/pipeline.py
    - scripts/run_local_dev.py
    - docs/TEST_SPEC.md
    - docs/BUILD.md
    - README.md
    - pyproject.toml
key-decisions:
  - "Fix malformed-input hangs in production code instead of masking them with weaker tests."
  - "Add a narrow fast_ivv tier so boundary regressions are cheap to rerun during refactors."
patterns-established:
  - "Boundary validation lives at the loader/helper layer and is also covered end to end"
  - "Docker reliability tests assert runtime availability explicitly and use stable binary resolution"
requirements-completed: [CLI-05, OUT-06, RUN-02]
duration: 1 min
completed: 2026-03-01
---

# Phase 07 Plan 03: Batch IV&V Hardening Summary

**Batch acceptance, determinism, and reliability coverage now treats mixed-success execution, malformed-input fast-fail, and runner preconditions as first-class product behavior**

## Performance

- **Duration:** 1 min
- **Started:** 2026-03-01T04:33:00Z
- **Completed:** 2026-03-01T05:05:00Z
- **Tasks:** 3
- **Files modified:** 15

## Accomplishments

- Added acceptance coverage for mixed-success batch runs that preserve successful outputs while reporting failed items explicitly.
- Extended determinism and robustness tests for batch ordering, collision-safe naming, missing input handling, and scaling-oriented helper behavior.
- Added a fast IV&V tier plus direct malformed-input and taxonomy boundary tests, then fixed the real production hang that those tests exposed.

## Task Commits

This plan was executed as part of the consolidated Phase 7 implementation commit:

1. **Plan 07-03 implementation and follow-on hardening** - `bd3f533` (fix)

## Files Created/Modified

- `tests/phase3/test_phase3_acceptance.py` - Covers mixed-success batch acceptance and preserved outputs.
- `tests/test_v1_acceptance_final.py` - Adds milestone-level batch acceptance coverage.
- `tests/test_determinism.py` - Verifies deterministic batch input resolution and collision-safe output naming.
- `tests/reliability/test_stress_and_robustness.py` - Adds helper-level batch robustness and scaling checks.
- `tests/reliability/test_docker.py` - Replaces skip-only behavior with explicit Docker runtime assertions and stable binary lookup.
- `tests/reliability/test_wrapper_and_fixture_contracts.py` - Hardens wrapper subprocess execution with clean environments and timeouts.
- `tests/phase1/test_ingest_and_quality.py` - Adds fast malformed-input and taxonomy boundary coverage.
- `src/specforge_distill/ingest/pdf_loader.py` - Fails non-PDF bytes before third-party parser invocation.
- `src/specforge_distill/normalize.py` - Caches taxonomy loads and supports both nested and flat parser shapes cheaply.
- `src/specforge_distill/pipeline.py` - Defers heavy imports behind runtime wrappers to reduce test collection and startup overhead.
- `scripts/run_local_dev.py` - Uses lightweight dependency discovery for faster, safer wrapper startup.
- `docs/TEST_SPEC.md`, `docs/BUILD.md`, `README.md`, `pyproject.toml` - Document the fast IV&V tier and updated batch traceability.

## Decisions Made

- Kept the suite fast by using scaling-oriented assertions and helper-level synthetic coverage instead of machine-sensitive timing ceilings.
- Treated Docker and malformed-input behavior as explicit environment and boundary contracts that should fail clearly rather than disappearing behind skips or hangs.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrupt non-PDF bytes could reach `pypdf` and stall the test loop**
- **Found during:** Task 2 (Add determinism and performance guardrails for batch scaling)
- **Issue:** A reliability case exposed that arbitrary non-PDF bytes were reaching `pypdf.PdfReader`, which could hang instead of failing fast.
- **Fix:** Added a PDF signature check in `src/specforge_distill/ingest/pdf_loader.py` so malformed bytes fail immediately at the loader boundary.
- **Files modified:** `src/specforge_distill/ingest/pdf_loader.py`, `tests/phase1/test_ingest_and_quality.py`
- **Verification:** Full suite now completes cleanly with `122 passed`.
- **Committed in:** `bd3f533`

**2. [Rule 1 - Bug] Docker reliability tests depended on ambient PATH and sometimes skipped even when Docker was installed**
- **Found during:** Task 3 (Update IV&V traceability for the Phase 7 batch workflow)
- **Issue:** Clean subprocess environments omitted the Docker binary path, causing false skips or misleading availability results.
- **Fix:** Resolved Docker from explicit fallback paths and asserted `docker info` availability directly in the test fixture.
- **Files modified:** `tests/reliability/test_docker.py`
- **Verification:** Docker module now passes explicitly with `2 passed`.
- **Committed in:** `bd3f533`

---

**Total deviations:** 2 auto-fixed (2 bugs)
**Impact on plan:** Both fixes strengthened the intended IV&V and reliability outcome rather than expanding scope.

## Issues Encountered

The test harness accumulated many open exec sessions during diagnosis, which made some subprocess behavior look less deterministic than it was. The actual root causes were malformed-input handling, import-time overhead, and Docker path resolution.

## User Setup Required

Docker must be installed and the daemon running if you want the Docker reliability module to pass locally. The suite now asserts that precondition explicitly instead of silently skipping it.

## Next Phase Readiness

Phase 7 leaves behind a fast rerun tier, a full green suite, and a release-grade batch contract. Phase 8 can focus on scanned/OCR diagnostics and validation/export hooks without inheriting batch ambiguity or test harness stalls.
