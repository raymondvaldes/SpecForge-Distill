---
phase: 07-batch-processing-and-aggregate-reporting
plan: 01
subsystem: cli
tags: [batch, cli, deterministic-ordering, wrapper, maintainability]
requires: []
provides:
  - deterministic batch CLI entrypoints
  - shared batch input and output planning helpers
  - wrapper coverage for multi-file and directory invocation
affects: [automation, runtime-contracts, phase-7-reporting]
tech-stack:
  added: []
  patterns:
    - "CLI delegates batch input resolution and child output planning into shared helper functions"
key-files:
  created:
    - src/specforge_distill/batch.py
  modified:
    - src/specforge_distill/cli.py
    - src/specforge_distill/automation.py
    - tests/phase3/test_cli_outputs.py
    - tests/reliability/test_wrapper_and_fixture_contracts.py
key-decisions:
  - "Allow batch entry through either multiple explicit PDF paths or one --input-dir path while keeping special modes mutually exclusive."
  - "Keep batch directory scanning intentionally narrow in v1.2.0: direct child PDFs only, no recursive traversal."
patterns-established:
  - "Deterministic batch input normalization before any processing starts"
  - "Collision-safe child output directory planning shared across CLI and later batch reporting"
requirements-completed: [CLI-05, RUN-02]
duration: 1 min
completed: 2026-03-01
---

# Phase 07 Plan 01: Batch Entry Path Summary

**The CLI now supports deterministic multi-file and directory-driven batch execution through one shared helper layer instead of ad hoc path logic in `cli.py`**

## Performance

- **Duration:** 1 min
- **Started:** 2026-03-01T04:10:00Z
- **Completed:** 2026-03-01T04:20:00Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Extended normal distill mode so one command can process either multiple explicit PDFs or one `--input-dir`.
- Added shared batch helper functions for deterministic input resolution, deduplication, and child output directory planning.
- Locked the new invocation surface with focused CLI and wrapper contract tests instead of help-text snapshots.

## Task Commits

This plan was executed as part of the consolidated Phase 7 implementation commit:

1. **Plan 07-01 implementation and follow-on hardening** - `bd3f533` (fix)

## Files Created/Modified

- `src/specforge_distill/batch.py` - Adds deterministic batch input resolution and child output directory planning.
- `src/specforge_distill/cli.py` - Separates single-file, batch, and special-mode dispatch paths.
- `src/specforge_distill/automation.py` - Documents the expanded CLI contract for batch entry paths.
- `tests/phase3/test_cli_outputs.py` - Verifies directory mode, explicit multi-file mode, and invalid mixed invocation.
- `tests/reliability/test_wrapper_and_fixture_contracts.py` - Verifies the launcher forwards the batch invocation surface cleanly.

## Decisions Made

- Kept batch mode within the existing `distill` command so users do not need a second command surface for the same core workflow.
- Resolved inputs and planned child output directories before processing so ordering and naming remain deterministic and testable.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

The initial wrapper contract tests could hang in this environment when executing the shell wrapper directly. The tests were refactored to invoke the wrapper through `/bin/sh` with clean subprocess environments and explicit timeouts.

## User Setup Required

None - batch mode is available through the existing local and release-facing CLI entrypoints.

## Next Phase Readiness

The batch entry boundary is now stable and maintainable. Phase 07-02 can build aggregate reporting on top of a deterministic input and output planning layer.
