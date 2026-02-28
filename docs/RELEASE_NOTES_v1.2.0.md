# Draft Release Notes: v1.2.0

This file is the working draft for the next release. Update it as changes land so the eventual GitHub release notes do not depend on reconstructing history from commits.

## How To Maintain This File

- Add an entry for every user-visible feature, fix, docs change, packaging/release change, or important known issue.
- Prefer user-facing language over internal implementation details.
- Keep entries short while the release is in progress; tighten wording at release cut time.
- Move an item between sections if its impact becomes clearer later.
- Keep empty sections in place so future updates have an obvious home.

## Release Snapshot

- Target release: `v1.2.0`
- Current branch version: `1.2.0.dev0`
- Latest stable release: `v1.1.0`
- Status: In progress

## Highlights

- None yet.

## Added

- None yet.

## Changed

- None yet.

## Fixed

- None yet.

## Documentation

- None yet.

## Packaging And Release

- None yet.

## Developer Experience

- None yet.

## Known Issues And Follow-Up Candidates

- Stable releases still depend on optional signing and notarization secrets to minimize Gatekeeper and SmartScreen friction completely.
- The stable release remains focused on digital-text PDFs and does not yet provide first-class scanned/OCR workflows.
- Batch processing, aggregate reporting, and validation/export hooks remain the primary `v1.2.0` follow-on work.

## Upgrade Path

- Users upgrading from `v1.1.0` should continue to verify checksums, run `--version`, and run `--self-test` before real PDF processing.
- Automation clients should continue to rely on `--describe-output json` and `--self-test` as stable preflight checks while the next release expands the processing surface.
