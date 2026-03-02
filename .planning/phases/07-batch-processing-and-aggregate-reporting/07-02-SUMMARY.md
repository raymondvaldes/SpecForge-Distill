---
phase: 07-batch-processing-and-aggregate-reporting
plan: 02
subsystem: reporting
tags: [batch, summary, automation, exit-codes, docs]
requires:
  - phase: 07-01
    provides: deterministic batch CLI entry path and shared planning helpers
provides:
  - batch summary schema
  - batch-summary.json artifact
  - explicit partial-failure exit behavior
affects: [automation, user-workflows, acceptance]
tech-stack:
  added: []
  patterns:
    - "Batch result items and totals are built from shared automation contract helpers"
key-files:
  created: []
  modified:
    - src/specforge_distill/automation.py
    - src/specforge_distill/batch.py
    - src/specforge_distill/cli.py
    - README.md
    - tests/phase1/test_ingest_and_quality.py
    - tests/phase3/test_cli_outputs.py
key-decisions:
  - "Use one stable batch item vocabulary with ok/failed item states and a top-level ok/partial_failure batch status."
  - "Preserve successful per-file outputs even when the overall batch exits non-zero."
patterns-established:
  - "Dry-run and normal batch modes share the same summary vocabulary"
  - "Aggregate summary writing happens in one linear pass without rescanning outputs"
requirements-completed: [OUT-06, RUN-02]
duration: 1 min
completed: 2026-03-01
---

# Phase 07 Plan 02: Aggregate Reporting Summary

**Batch mode now emits one machine-readable aggregate summary with deterministic ordering, preserved successful outputs, and an explicit partial-failure exit contract**

## Performance

- **Duration:** 1 min
- **Started:** 2026-03-01T04:21:00Z
- **Completed:** 2026-03-01T04:32:00Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- Added a documented batch summary schema and dedicated exit code `5` for mixed-success or failed batch runs.
- Implemented `batch-summary.json` emission for normal batch runs and aligned dry-run aggregation with the same status vocabulary.
- Updated README and contract tests so the supported batch workflow is explicit for both humans and automation clients.

## Task Commits

This plan was executed as part of the consolidated Phase 7 implementation commit:

1. **Plan 07-02 implementation and follow-on hardening** - `bd3f533` (fix)

## Files Created/Modified

- `src/specforge_distill/automation.py` - Defines the batch item schema, batch summary schema, and exit code metadata.
- `src/specforge_distill/batch.py` - Assembles aggregate batch items and writes `batch-summary.json`.
- `src/specforge_distill/cli.py` - Emits batch console summaries and returns non-zero when any batch item fails.
- `README.md` - Documents explicit multi-file mode, directory mode, and `batch-summary.json`.
- `tests/phase1/test_ingest_and_quality.py` - Verifies batch summary discoverability in `--describe-output json`.
- `tests/phase3/test_cli_outputs.py` - Verifies summary emission, deterministic ordering, and partial-failure exit behavior.

## Decisions Made

- Kept one aggregate summary file in the batch root rather than scattering top-level status into per-item outputs.
- Reused existing counts, warning totals, extraction assessment, and output path fields so automation clients do not need a parallel naming system for batch runs.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - aggregate reporting is part of the standard batch CLI path.

## Next Phase Readiness

The batch workflow now has a documented and machine-readable aggregate contract. Phase 07-03 can harden it with acceptance, determinism, and robustness coverage.
