---
phase: 06-cross-platform-runtime-ergonomics
plan: 02
subsystem: cli
tags: [cli, diagnostics, permissions, low-text, troubleshooting]
requires:
  - phase: 06-01
    provides: shared local development runners and cross-platform entrypoint guidance
provides:
  - runtime extraction assessment
  - output-write failure classification
  - clearer low-text versus malformed-PDF recovery paths
affects: [testing, troubleshooting, validation]
tech-stack:
  added: []
  patterns:
    - "CLI runtime notes emitted from explicit extraction-assessment helpers"
key-files:
  created: []
  modified:
    - src/specforge_distill/automation.py
    - src/specforge_distill/cli.py
    - README.md
    - docs/TROUBLESHOOTING.md
    - tests/phase1/test_ingest_and_quality.py
key-decisions:
  - "Treat successful low-text or image-only extraction as an explicit result class instead of conflating it with malformed-PDF failure."
  - "Add an output-write failure class to the automation contract while keeping the existing exit-code envelope unchanged."
patterns-established:
  - "Dry-run JSON remains machine-readable by suppressing progress output in JSON-emitting mode"
  - "Runtime failure text stays short while detailed recovery guidance lives in troubleshooting"
requirements-completed: [PLAT-03, CLI-04]
duration: 1 min
completed: 2026-02-28
---

# Phase 06 Plan 02: Runtime Failure Boundary Summary

**Runtime classification now separates malformed PDFs, write-path failures, and successful low-text extraction outcomes without sacrificing the deterministic CLI contract**

## Performance

- **Duration:** 1 min
- **Started:** 2026-02-28T17:46:00Z
- **Completed:** 2026-02-28T17:52:00Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Refactored CLI runtime handling into explicit extraction-assessment and progress-cleanup helpers.
- Extended the machine-readable automation contract with an `output_write_failure` class.
- Documented and tested the distinction between malformed input, unwritable output paths, and successful but low-text extraction outcomes.

## Task Commits

Each task was committed atomically:

1. **Task 1: Refine runtime failure taxonomy without breaking determinism** - `aa36981` (fix)
2. **Task 2: Improve path and permission recovery guidance for cross-platform users** - `a202986` (docs)
3. **Task 3: Lock the runtime boundary with focused tests** - `2f16d62` (test)

Planning metadata is recorded in the follow-up docs commit for this plan.

## Files Created/Modified

- `src/specforge_distill/automation.py` - Adds `output_write_failure` and extends the dry-run schema with extraction assessment.
- `src/specforge_distill/cli.py` - Centralizes progress cleanup, extraction assessment, runtime notes, and output-write failure handling.
- `README.md` - Clarifies that successful low-text empty extraction is an input-quality problem rather than a parser crash.
- `docs/TROUBLESHOOTING.md` - Separates output-write recovery from malformed-PDF recovery and documents low-text/image-only result handling.
- `tests/phase1/test_ingest_and_quality.py` - Verifies dry-run assessment output and output-write failure behavior.

## Decisions Made

- Preserved exit code `3` for runtime failures while distinguishing specific failure classes through the automation contract and troubleshooting anchors.
- Disabled progress rendering for dry-run mode so JSON output remains clean for automation and wrappers.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Suppressed progress escape sequences in dry-run JSON**
- **Found during:** Task 1 (Refine runtime failure taxonomy without breaking determinism)
- **Issue:** Real dry-run commands were still writing progress-control sequences into stdout before the JSON payload.
- **Fix:** Disabled progress callbacks for `--dry-run` and only clear the progress line when progress output was actually emitted.
- **Files modified:** `src/specforge_distill/cli.py`
- **Verification:** `./distill fixtures/specs/sample-digital.pdf --dry-run` now emits clean JSON on stdout.
- **Committed in:** `aa36981` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** The fix was required to keep the dry-run machine-readable contract intact. No scope creep.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Runtime behavior now exposes clearer boundaries for wrappers, users, and automation clients. Phase 06-03 can harden the supporting determinism, performance, and IV&V documentation around those boundaries.
