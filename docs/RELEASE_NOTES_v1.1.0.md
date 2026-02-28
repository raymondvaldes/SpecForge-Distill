# Draft Release Notes: v1.1.0

This file is the working draft for the next release. Update it as changes land so the eventual GitHub release notes do not depend on reconstructing history from commits.

## How To Maintain This File

- Add an entry for every user-visible feature, fix, docs change, packaging/release change, or important known issue.
- Prefer user-facing language over internal implementation details.
- Keep entries short while the release is in progress; tighten wording at release cut time.
- Move an item between sections if its impact becomes clearer later.
- Keep empty sections in place so future updates have an obvious home.

## Release Snapshot

- Target release: `v1.1.0`
- Current branch version: `1.1.0.dev0`
- Latest stable release: `v1.0.1`
- Status: In progress

## Highlights

- Expanded troubleshooting coverage into a dedicated platform-aware guide for binary users and contributors.
- Added machine-readable CLI modes so agents and automation can inspect the output contract, emit canonical sample output, and run a built-in self-test.
- Official release assets now use explicit versioned filenames, per-asset `.sha256` files, and one aggregate `checksums.txt` manifest.
- The GitHub release page now leads with a platform matrix and the trust-first install sequence instead of leaving verification details buried in troubleshooting.

## Added

- Added a dedicated troubleshooting guide covering binary verification, platform-specific startup failures, PDF failure diagnosis, Docker issues, and source-build recovery.
- Added `--describe-output json` for a machine-readable output contract.
- Added `--emit-example-output` to generate a canonical output package without a source PDF.
- Added `--self-test` to verify the output-generation path and installation state from the CLI itself.
- Expanded the `--describe-output json` contract with machine-readable CLI flag metadata, invocation modes, response schemas, and failure classes for automation clients.
- Added a generated GitHub release body that combines the curated change log with a deterministic platform-selection and verification section.

## Changed

- Shortened the root README by moving troubleshooting into a dedicated document and keeping the main install/run path focused on getting started quickly.
- Added explicit automation-facing CLI guidance to the README and build docs.
- Reworked the binary install flow so every platform verifies checksums, runs `--version`, and runs `--self-test` before a real PDF command.
- Structured self-test failures now return a stable `failure_class`, a short recovery hint, and a deterministic troubleshooting pointer.

## Fixed

- None yet.

## Documentation

- Added detailed troubleshooting instructions for Ubuntu, WSL, macOS, and Windows PowerShell 7.
- Added checksum verification examples for Linux, macOS, and PowerShell 7 users.
- Added recovery guidance for malformed PDFs, image-only scans, output-path issues, Docker bind mounts, and local development environments.

## Packaging And Release

- Versioned the official GitHub release asset names to the `distill-vX.Y.Z-platform-arch` pattern.
- Publish `checksums.txt` in addition to per-asset `.sha256` files.
- Hold back only the platform whose signing or notarization validation fails while still publishing unaffected assets.
- Generate the GitHub release body from checked-in release notes plus the current asset contract.

## Developer Experience

- Added a standing maintainer rule to keep this release-note draft updated as `v1.1.0` work lands.
- Reduced duplication by routing normal CLI output generation and example/self-test output generation through the same package writer path.

## Known Issues And Follow-Up Candidates

- Stable releases still depend on optional signing and notarization secrets to minimize Gatekeeper and SmartScreen friction completely.
- The stable release remains focused on digital-text PDFs and does not yet provide first-class scanned/OCR workflows.
- Batch processing and aggregate reporting remain planned follow-on work for the `v1.1.0` cycle.

## Upgrade Path

- Binary users should normally upgrade by downloading the new platform asset, verifying its checksum, replacing the previous binary, and rerunning `--version` plus a known-good `--dry-run`.
- Tools integrating with the CLI should start using `--describe-output json` and `--self-test` as stable preflight checks before processing real inputs.
- macOS users should treat each new zipped release asset as a fresh binary and reverify the correct Intel vs Apple Silicon download before replacing the old executable.
- Users with scripts or automation should compare CLI flags, output file names, and `manifest.json` behavior before rolling a new release into production workflows.
- Source-install users should expect to refresh `.venv` and rerun `python -m pip install -e ".[dev]"` when a future release changes packaging or dependencies.
