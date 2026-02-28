# Phase 5: Trusted Distribution and Install Verification - Context

**Gathered:** 2026-02-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 5 covers the trust and verification experience around official release assets. The scope is making binaries easy to trust, easy to choose, easy to verify, and easy to recover when install or first-run goes wrong. This phase does not add new core distillation capabilities.

</domain>

<decisions>
## Implementation Decisions

### Trust Signals and Verification Path
- SHA256 checksums are mandatory for every official release asset.
- Platform signing and notarization should be used wherever the platform supports them and the release pipeline can produce them.
- A signing or notarization failure on one platform should not block the entire release. Unaffected platforms may ship; the failed platform should be held back.
- The canonical verification flow before first real use is: verify checksum, run `--version`, then run `--self-test`.
- Official downloads are GitHub Releases only.

### Release Asset Selection and Naming
- Official asset filenames should be explicit and versioned, for example `distill-v1.1.0-windows-x64.exe` and `distill-v1.1.0-macos-arm64.zip`.
- Packaging should remain platform-native: macOS assets zipped, Linux as a raw executable, Windows as `.exe`.
- Publish both per-asset `.sha256` files and one aggregate `checksums.txt`.
- Put a platform and CPU selection matrix at the top of the release notes so users can pick the correct asset quickly.

### First-Run Verification UX
- Every install guide should require users to run `--version` and then `--self-test` after download.
- A healthy first-run means `--version` prints the expected release version and `--self-test` exits successfully.
- `--self-test` should be a first-class install verification step, not a troubleshooting-only command.
- If `--self-test` fails, the tool and docs should present structured failure details and route users to troubleshooting guidance by failure class.

### Failure and Recovery Guidance
- Troubleshooting should be organized by failure class first, then by platform-specific recovery steps.
- On checksum mismatch, users should be told to discard the file, redownload only from the official GitHub Release, and never run the mismatched binary.
- Gatekeeper and SmartScreen guidance should provide exact platform-specific recovery steps, but only after the asset source and checksum have been verified.
- CLI failures in this phase should prioritize a machine-readable failure class plus a concise human recovery hint.

### Claude's Discretion
- Exact release-note layout and wording, as long as the platform-selection matrix is prominent and unambiguous.
- Exact checksum command examples per platform, as long as they remain copy-pasteable and platform-correct.
- Exact naming of failure classes, as long as they remain stable and machine-readable.

</decisions>

<specifics>
## Specific Ideas

- The trust and verification story should be strong enough for production aerospace and defense engineering environments.
- The official binary channel should be singular and unambiguous: GitHub Releases.
- Release guidance should optimize for first-run confidence, not just successful download.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 05-trusted-distribution-and-install-verification*
*Context gathered: 2026-02-28*
