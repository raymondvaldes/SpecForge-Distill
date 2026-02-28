---
phase: 06-cross-platform-runtime-ergonomics
plan: 01
subsystem: infra
tags: [powershell, wsl, wrapper, runner, contributor-workflow]
requires: []
provides:
  - shared local development runner
  - PowerShell 7 development entrypoint
  - cross-platform entrypoint guidance
affects: [runtime-failures, contributor-setup, reliability]
tech-stack:
  added: []
  patterns:
    - "Thin shell wrappers delegating to one shared Python development runner"
key-files:
  created:
    - distill.ps1
    - scripts/run_local_dev.py
  modified:
    - distill
    - README.md
    - docs/BUILD.md
    - docs/TROUBLESHOOTING.md
    - tests/reliability/test_wrapper_and_fixture_contracts.py
key-decisions:
  - "Keep POSIX and PowerShell entrypoints thin by moving dependency checks and CLI invocation into one shared Python runner."
  - "Document repository-local development entrypoints separately from verified release-binary usage."
patterns-established:
  - "Shared launcher contract for POSIX and PowerShell local development"
  - "Wrapper tests validate contract markers even when pwsh is unavailable in CI"
requirements-completed: [PLAT-02, PLAT-03]
duration: 1 min
completed: 2026-02-28
---

# Phase 06 Plan 01: Cross-Platform Entry Points Summary

**Shared local development runners for POSIX shells and PowerShell 7, with docs and tests aligned around the same launcher contract**

## Performance

- **Duration:** 1 min
- **Started:** 2026-02-28T17:40:00Z
- **Completed:** 2026-02-28T17:45:00Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- Refactored the POSIX launcher into a thin wrapper over a shared Python development runner.
- Added a PowerShell 7 development entrypoint that follows the same environment-selection and dependency-checking contract.
- Documented the local development runner story across README, build docs, and troubleshooting, then locked it with wrapper tests.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add a PowerShell-friendly local development entrypoint** - `7e8e98f` (feat)
2. **Task 2: Rewrite local runtime docs around entrypoint selection** - `5261375` (docs)
3. **Task 3: Extend wrapper contract coverage for cross-platform entrypoints** - `760e6ba` (test)

Planning metadata is recorded in the follow-up docs commit for this plan.

## Files Created/Modified

- `distill` - POSIX development runner now delegates to the shared Python launcher.
- `distill.ps1` - PowerShell 7 development runner for editable source workflows.
- `scripts/run_local_dev.py` - Shared dependency-check and CLI-invocation path used by both wrappers.
- `README.md` - Documents repository-local development entrypoints separately from release binaries.
- `docs/BUILD.md` - Adds contributor-facing examples for `./distill` and `.\distill.ps1`.
- `docs/TROUBLESHOOTING.md` - Explains local runner recovery in the source-environment drift path.
- `tests/reliability/test_wrapper_and_fixture_contracts.py` - Verifies shared-runner and PowerShell wrapper contract markers.

## Decisions Made

- Centralized the launcher logic in `scripts/run_local_dev.py` so PowerShell and POSIX wrappers do not drift.
- Kept PowerShell verification hermetic by checking for `pwsh` opportunistically while still asserting the wrapper contract when it is unavailable.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

The initial wrapper contract tests assumed a module-level CLI entrypoint that no longer existed in the fake test repo. The fixture was updated to expose `main()` so the shared runner could be tested through the same import path as the real package.

## User Setup Required

Have PowerShell 7 installed only if you want to use `.\distill.ps1` locally on Windows. POSIX shells and WSL continue to use `./distill`.

## Next Phase Readiness

The local entrypoint story is now explicit and maintainable. Phase 06-02 can build richer runtime classification and recovery behavior on top of a stable contributor-facing launcher contract.
