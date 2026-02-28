# Phase 5: Trusted Distribution and Install Verification - Research

**Researched:** 2026-02-28
**Domain:** Cross-platform CLI release trust, artifact verification, and first-run install validation
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- SHA256 checksums are mandatory for every official release asset.
- Platform signing and notarization should be used wherever the platform supports them and the release pipeline can produce them.
- A signing or notarization failure on one platform should not block the entire release. Unaffected platforms may ship; the failed platform should be held back.
- The canonical verification flow before first real use is: verify checksum, run `--version`, then run `--self-test`.
- Official downloads are GitHub Releases only.
- Official asset filenames should be explicit and versioned, for example `distill-v1.1.0-windows-x64.exe` and `distill-v1.1.0-macos-arm64.zip`.
- Packaging should remain platform-native: macOS assets zipped, Linux as a raw executable, Windows as `.exe`.
- Publish both per-asset `.sha256` files and one aggregate `checksums.txt`.
- Put a platform and CPU selection matrix at the top of the release notes so users can pick the correct asset quickly.
- Every install guide should require users to run `--version` and then `--self-test` after download.
- A healthy first-run means `--version` prints the expected release version and `--self-test` exits successfully.
- `--self-test` should be a first-class install verification step, not a troubleshooting-only command.
- If `--self-test` fails, the tool and docs should present structured failure details and route users to troubleshooting guidance by failure class.
- Troubleshooting should be organized by failure class first, then by platform-specific recovery steps.
- On checksum mismatch, users should be told to discard the file, redownload only from the official GitHub Release, and never run the mismatched binary.
- Gatekeeper and SmartScreen guidance should provide exact platform-specific recovery steps, but only after the asset source and checksum have been verified.
- CLI failures in this phase should prioritize a machine-readable failure class plus a concise human recovery hint.

### Claude's Discretion
- Exact release-note layout and wording, as long as the platform-selection matrix is prominent and unambiguous.
- Exact checksum command examples per platform, as long as they remain copy-pasteable and platform-correct.
- Exact naming of failure classes, as long as they remain stable and machine-readable.

### Deferred Ideas (OUT OF SCOPE)
- None.

</user_constraints>

<research_summary>
## Summary

The repo already has a strong base for this phase: the release workflow builds Linux, macOS, and Windows binaries; optional signing and notarization are already wired in; the workflow smoke-tests real built executables; and the CLI now exposes `--self-test` and a machine-readable output contract. The phase should build on that foundation rather than replacing it.

The main gaps are consistency and trust presentation. Release asset names are still platform-specific but not versioned, the workflow publishes per-asset `.sha256` files but no aggregate `checksums.txt`, the main download path in the README does not yet require checksum verification plus `--self-test`, and release publication does not yet generate a first-class trust-oriented release body with a platform matrix, official-download-only guidance, and explicit verification steps.

**Primary recommendation:** Treat Phase 5 as three linked layers: harden the release artifact contract first, make install verification checksum-first and self-test-first second, and then automate release-note/publication output from the same artifact metadata so the trust story stays synchronized.
</research_summary>

<standard_stack>
## Standard Stack

The established tools already present in this repo are the right base for Phase 5.

### Core
| Tool | Purpose | Why Standard Here |
|------|---------|-------------------|
| GitHub Actions | Build and publish release artifacts | Already the project's release path |
| PyInstaller | Produce single-file binaries | Already used successfully across platforms |
| GitHub Releases | Official distribution channel | Matches the locked "official downloads only" decision |
| SHA256 checksums | Integrity verification | Simple, portable, and already partially implemented |
| macOS `codesign` + `notarytool` | macOS trust validation | Native Apple trust path |
| Windows `signtool` + `Get-AuthenticodeSignature` | Windows trust validation | Native Microsoft trust path |

### Supporting
| Tool | Purpose | When To Use |
|------|---------|-------------|
| `--version` | Quick binary identity check | Every first-run flow |
| `--self-test` | Deterministic install verification | Every first-run flow and support triage |
| Reliability tests | Keep workflow/docs/asset contracts aligned | Every release-contract change |
| GitHub artifact attestations | Build provenance hardening | Optional future enhancement if Phase 5 scope allows |

### Alternatives Considered
| Instead Of | Could Use | Tradeoff |
|------------|-----------|----------|
| GitHub Releases only | Mirrors or package registries | Adds more distribution surfaces to secure and document |
| Per-asset hashes only | Aggregate manifest only | Harder for users to verify single downloaded files in isolation |
| Unsuffixed asset names | Versioned release names | Versioned names are clearer for audit and rollback workflows |

</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Pattern 1: Release Contract As Code
**What:** Keep asset naming, checksum generation, and release publication behavior in executable workflow/script logic, then assert that contract in tests.
**When to use:** Whenever README/release notes need to stay aligned with workflow outputs.
**Repo fit:** The repo already has reliability tests that compare documented assets with workflow expectations. Phase 5 should extend that pattern instead of relying on prose alone.

### Pattern 2: Verify Before First Real Input
**What:** The official install path should be download -> checksum -> `--version` -> `--self-test` -> real PDF.
**When to use:** Every platform-specific install guide and release note.
**Repo fit:** `--self-test` already exists and uses the same output writer path as real execution, which makes it the right canonical readiness check.

### Pattern 3: Hold Back Only The Failed Platform
**What:** A platform-specific trust failure should prevent only that platform from publishing, while unaffected matrix jobs still complete.
**When to use:** Optional signing/notarization workflows where one runner or secret path may fail independently.
**Repo fit:** The matrix build already has `fail-fast: false`, so Phase 5 should preserve and clarify per-platform hold-back behavior rather than switching to all-or-nothing publishing.

### Anti-Patterns to Avoid
- **Trust guidance only in troubleshooting:** makes the secure path feel optional.
- **Ambiguous asset naming:** increases wrong-download risk and weakens auditability.
- **Unsigned platform published with soft warning when trust checks were expected to pass:** too easy for users to miss.
- **Docs ahead of workflow reality:** release instructions and actual attached assets must come from the same contract.

</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| macOS trust validation | Custom notarization status parser | `codesign`, `spctl`, `notarytool` | Native trust tools define the acceptance path |
| Windows signature validation | Custom PE signature parsing | `signtool` and `Get-AuthenticodeSignature` | Native tooling is the authoritative source |
| First-run readiness | Ad hoc smoke-test script outside the CLI | `distill --self-test` | Keeps verification on the same execution path users run |
| Release publishing guidance | Manual copy-paste release notes | Generated release body from checked-in data/template | Reduces drift between assets and docs |

**Key insight:** The trust path should use platform-native validation and the CLI's own self-test surface, not custom side channels that can drift from the shipped binary behavior.
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Asset Name Drift
**What goes wrong:** README, workflow matrix, tests, and release notes disagree about asset names.
**Why it happens:** Asset names are duplicated in multiple places with no single source of truth.
**How to avoid:** Centralize asset naming and test the contract.
**Warning signs:** Release pages look right but docs or checksum filenames still reference old names.

### Pitfall 2: Verification Feels Optional
**What goes wrong:** Users run binaries before checking source, checksum, or self-test.
**Why it happens:** Secure guidance is buried under troubleshooting instead of install steps.
**How to avoid:** Make checksum + `--version` + `--self-test` mandatory in the happy path.
**Warning signs:** Main install sections stop after download plus execute.

### Pitfall 3: Trust Failures Leak Through Publication
**What goes wrong:** A platform with signing/notary problems still ends up looking "official enough" to users.
**Why it happens:** Workflow upload steps are not tightly coupled to trust validation steps or the release body does not disclose the state.
**How to avoid:** Fail the affected matrix job before upload and publish trust status explicitly.
**Warning signs:** Release assets exist but there is no clear indication whether they are signed/notarized/verified.

### Pitfall 4: Recovery Guidance Starts Before Verification
**What goes wrong:** Docs tell users to bypass Gatekeeper or SmartScreen before they confirm the file is official and intact.
**Why it happens:** Platform friction gets documented without a checksum-first trust model.
**How to avoid:** Always sequence recovery after source and hash verification.
**Warning signs:** `xattr -d` or `Run anyway` appears before checksum comparison steps.

</common_pitfalls>

<current_repo_assessment>
## Current Repo Assessment

### What Already Exists
- `.github/workflows/release.yml` already builds all supported binaries, smoke-tests them, signs/notarizes conditionally, and validates signatures when those paths are enabled.
- `README.md` already positions GitHub Releases as the primary install path.
- `docs/TROUBLESHOOTING.md` already includes checksum examples, Gatekeeper/SmartScreen guidance, and `--self-test`.
- `src/specforge_distill/cli.py` and `src/specforge_distill/automation.py` already expose structured CLI contract data and a deterministic self-test.

### Gaps Phase 5 Should Close
- Release asset names are not yet explicit and versioned.
- The workflow does not yet publish one aggregate `checksums.txt`.
- The main install guides do not yet require checksum verification plus `--self-test` before real use.
- Runtime failure output for install verification can be more explicit about failure class and recovery hints.
- Release publication does not yet generate a trust-first release body with a platform matrix and official verification steps.

</current_repo_assessment>

<open_questions>
## Open Questions

1. **Should GitHub artifact attestations be in Phase 5 or deferred?**
   - What we know: GitHub officially supports artifact attestations for build provenance, and this repo is public.
   - What's unclear: Whether adding provenance verification now would keep Phase 5 focused or over-expand it.
   - Recommendation: Treat attestations as optional if they fit naturally into the release workflow changes; otherwise note them as a follow-on hardening step.

2. **How much of the release body should be generated versus curated?**
   - What we know: Asset matrix, checksum instructions, and verification steps are deterministic and should be generated or templated.
   - What's unclear: How much human-authored release narrative should stay in `docs/RELEASE_NOTES_v1.1.0.md`.
   - Recommendation: Generate the trust/installation matrix and keep feature/change prose curated.

</open_questions>

<sources>
## Sources

### Primary (HIGH confidence)
- Local repo: `.github/workflows/release.yml`
- Local repo: `README.md`
- Local repo: `docs/TROUBLESHOOTING.md`
- Local repo: `src/specforge_distill/cli.py`
- Local repo: `src/specforge_distill/automation.py`

### Secondary (MEDIUM confidence)
- GitHub Docs: Artifact attestations and build provenance
  - https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds
- Apple Developer Documentation: Customizing the notarization workflow
  - https://developer.apple.com/documentation/security/customizing-the-notarization-workflow
- Microsoft Learn: SignTool
  - https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool
- NIST SSDF publications
  - https://csrc.nist.gov/Projects/ssdf/publications

</sources>

<metadata>
## Metadata

**Research scope:**
- Core technology: GitHub Actions release automation for cross-platform CLI binaries
- Ecosystem: GitHub Releases, PyInstaller, platform signing/notarization tools
- Patterns: checksum-first verification, self-test-first install validation, trust-gated publication
- Pitfalls: asset drift, unsigned publication leakage, recovery guidance sequencing

**Confidence breakdown:**
- Repo state: HIGH - based on current local files
- Release trust patterns: HIGH - based on native platform tooling and existing workflow structure
- Provenance/attestation extension: MEDIUM - useful but optional within this phase

**Research date:** 2026-02-28
**Valid until:** 2026-03-30
</metadata>

---

*Phase: 05-trusted-distribution-and-install-verification*
*Research completed: 2026-02-28*
*Ready for planning: yes*
