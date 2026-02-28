---
phase: 05-trusted-distribution-and-install-verification
plan: 02
subsystem: cli
tags: [docs, self-test, troubleshooting, json, install]
requires:
  - phase: 05-trusted-distribution-and-install-verification
    provides: versioned release asset contract and trust-gated publication behavior
provides:
  - checksum-first install guides
  - structured self-test failure payloads
  - troubleshooting organized by failure class
affects: [release-notes, support, automation]
tech-stack:
  added: []
  patterns:
    - "Install verification uses checksum, version, and self-test before real input"
key-files:
  created: []
  modified:
    - README.md
    - docs/BUILD.md
    - docs/TROUBLESHOOTING.md
    - verify_markdown.py
    - src/specforge_distill/automation.py
    - src/specforge_distill/cli.py
    - tests/phase1/test_ingest_and_quality.py
    - tests/reliability/test_release_and_wrapper_contracts.py
key-decisions:
  - "Expose self-test failures through the same failure-class vocabulary advertised by --describe-output json."
  - "Require every documented binary path to complete checksum, version, and self-test before real processing."
patterns-established:
  - "Failure payloads include failure_class, recovery_hint, and troubleshooting pointer"
  - "Troubleshooting starts from failure class, then drops into platform-specific recovery"
requirements-completed: [REL-01, REL-02]
duration: 1 min
completed: 2026-02-28
---

# Phase 05 Plan 02: Secure Install Flow Summary

**Checksum-first install docs and structured self-test recovery payloads now define the supported binary onboarding path**

## Performance

- **Duration:** 1 min
- **Started:** 2026-02-28T07:42:30-08:00
- **Completed:** 2026-02-28T07:42:44-08:00
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Rewrote the README, build guide, and troubleshooting guide so every binary install path uses official GitHub Releases, checksum verification, `--version`, and `--self-test` before a real PDF.
- Extended the CLI failure contract so self-test errors return a stable `failure_class`, a short recovery hint, and a deterministic troubleshooting pointer.
- Added tests that pin the new install story in both the CLI JSON contract and the docs.

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite install guides around the trust sequence** - `341a17e` (docs)
2. **Task 2: Expose structured install-verification failures in the CLI** - `d42a0fc` (feat)
3. **Task 3: Add contract tests for the secure install story** - `d9461e9` (test)

Planning metadata is recorded in the follow-up docs commit for this plan.

## Files Created/Modified

- `README.md` - Requires GitHub Releases, checksum verification, `--version`, and `--self-test` in the primary install flow.
- `docs/BUILD.md` - Mirrors the trust-first verification sequence for maintainers and release operators.
- `docs/TROUBLESHOOTING.md` - Reorganized around failure classes before platform-specific recovery steps.
- `verify_markdown.py` - Provides the repo-local markdown validation command referenced by the plan.
- `src/specforge_distill/automation.py` - Defines failure-class metadata, recovery hints, and troubleshooting pointers.
- `src/specforge_distill/cli.py` - Emits structured self-test failure JSON on stderr.
- `tests/phase1/test_ingest_and_quality.py` - Verifies the failure contract surfaces in CLI JSON.
- `tests/reliability/test_release_and_wrapper_contracts.py` - Guards the docs-level install contract.

## Decisions Made

- Kept install-verification failure vocabulary aligned with the existing `--describe-output json` failure class keys instead of inventing a second install-only taxonomy.
- Treated checksum verification and `--self-test` as part of the happy path, not as troubleshooting-only steps.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Replace the dormant markdown verification stub**
- **Found during:** Task 1 (Rewrite install guides around the trust sequence)
- **Issue:** `python3 verify_markdown.py README.md docs/TROUBLESHOOTING.md docs/BUILD.md` failed because the script was a rendering stub that depended on package imports and ignored the requested files.
- **Fix:** Replaced the stub with a repo-local markdown verifier that checks file existence, top-level headings, and balanced fenced code blocks.
- **Files modified:** `verify_markdown.py`
- **Verification:** `python3 verify_markdown.py README.md docs/TROUBLESHOOTING.md docs/BUILD.md`
- **Committed in:** `341a17e` (part of Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 Rule 3 - Blocking)
**Impact on plan:** The fix was required to make the planned documentation verification command real and repeatable. No scope creep beyond the intended verification path.

## Issues Encountered

The original `verify_markdown.py` implementation could not validate the docs touched by the plan. Replacing it was necessary before the required markdown verification step could pass.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

The install and recovery language is now stable enough to embed directly into the GitHub release page. Phase 05-03 can render release notes from the same trust sequence without copying prose by hand.
