---
phase: 05-trusted-distribution-and-install-verification
plan: 01
subsystem: infra
tags: [github-actions, release, checksums, signing, notarization]
requires: []
provides:
  - versioned release asset contract
  - aggregate checksums publication flow
  - per-platform trust holdback workflow
affects: [install-docs, release-notes, reliability]
tech-stack:
  added: []
  patterns:
    - "Release contract as code via checked-in manifest and aggregate publication jobs"
key-files:
  created: [scripts/release_manifest.py]
  modified:
    - .github/workflows/release.yml
    - tests/reliability/test_release_and_wrapper_contracts.py
    - tests/reliability/test_wrapper_and_fixture_contracts.py
key-decisions:
  - "Generate release asset names from one checked-in Python manifest to eliminate drift between workflow, docs, and tests."
  - "Publish release assets from one aggregate job so trust validation can hold back only the affected platform."
patterns-established:
  - "Versioned asset naming: distill-vX.Y.Z-platform-arch"
  - "Trust-gated publication: matrix builds feed one aggregate release job"
requirements-completed: [REL-01, REL-03]
duration: 1 min
completed: 2026-02-28
---

# Phase 05 Plan 01: Release Trust Contract Summary

**Versioned release assets, aggregate checksums, and per-platform trust holdbacks wired into the GitHub release workflow**

## Performance

- **Duration:** 1 min
- **Started:** 2026-02-28T07:34:42-08:00
- **Completed:** 2026-02-28T07:35:03-08:00
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- Added a checked-in release manifest helper that defines the official versioned asset names and packaging rules.
- Reworked the release workflow so matrix builds produce trust-gated bundles that are aggregated into one release upload step.
- Locked the new asset and workflow contract with reliability tests while moving non-release checks out of the release verifier slice.

## Task Commits

Each task was committed atomically:

1. **Task 1: Introduce a deterministic versioned release manifest** - `b77fb4b` (feat)
2. **Task 2: Tighten trust-gated workflow publication** - `c6ce6a1` (feat)
3. **Task 3: Lock the release contract with reliability tests** - `27aafe8` (test)

Planning metadata is recorded in the follow-up docs commit for this plan.

## Files Created/Modified

- `scripts/release_manifest.py` - Defines the official release asset names, upload paths, and aggregate checksum generation.
- `.github/workflows/release.yml` - Generates the build matrix from the manifest, aggregates successful artifacts, and publishes only trust-valid assets.
- `tests/reliability/test_release_and_wrapper_contracts.py` - Verifies the release workflow uses the manifest-driven aggregate publication contract.
- `tests/reliability/test_wrapper_and_fixture_contracts.py` - Holds wrapper and fixture checks outside the release-only verifier slice.

## Decisions Made

- Centralized release asset naming in `scripts/release_manifest.py` so the workflow, docs, and tests all share one contract.
- Switched from per-matrix direct GitHub Release uploads to one aggregate publish job so trust failures stay platform-local instead of release-wide.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

Configure GitHub repository secrets for Windows signing and Apple Developer ID / notary flows only if you want live trust validation on those official release assets.

## Next Phase Readiness

The repo now has one stable versioned asset contract that install docs and release-note automation can reuse directly. Phase 05-02 can point users at the official filenames and checksum artifacts without duplicating workflow logic.
