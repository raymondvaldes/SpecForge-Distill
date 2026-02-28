# SpecForge Distill

## What This Is

SpecForge Distill is a local-first command line utility for systems engineering and MBSE teams to convert legacy specification PDFs into deterministic, provenance-linked Markdown and JSON artifacts. The shipped `v1.1.0` release supports a binary-first installation path on Ubuntu/WSL, macOS Intel, macOS Apple Silicon, and Windows PowerShell 7, while preserving source grounding through page-level citations and trust-first install verification.

## Core Value

Transform legacy spec PDFs into structured, provenance-linked markdown without missing critical requirement obligations.

## Current State

- Latest shipped release: `v1.1.0` on 2026-02-28
- Current branch target: `v1.2.0`
- Stable capabilities: deterministic single-document distillation, split/consolidated Markdown outputs, manifest generation, downloadable cross-platform binaries, checksum-first install verification, `--describe-output json`, `--emit-example-output`, `--self-test`, and clearer runtime failure/result classification
- Known limits: digital-text PDFs only, no first-class batch mode yet, no full validation/export workflow yet, and no explicit scanned/OCR command path beyond low-text signaling

## Requirements

### Validated

- ✓ Distill a digital-text PDF into consolidated and split Markdown plus `manifest.json` with page-level provenance — `v1.0.1`
- ✓ Preserve source requirement IDs when present and generate deterministic IDs when absent — `v1.0.1`
- ✓ Classify obligation language and flag ambiguous requirements for review — `v1.0.1`
- ✓ Publish downloadable binaries for Ubuntu/WSL, macOS Intel, macOS Apple Silicon, and Windows PowerShell 7 — `v1.0.1`
- ✓ Build and smoke-test release assets in GitHub Actions before publication — `v1.0.1`
- ✓ Verify downloaded binaries with checksums, `--version`, and `--self-test` before first real use — `v1.1.0`
- ✓ Expose machine-readable install and automation hooks through `--describe-output json`, `--emit-example-output`, and `--self-test` — `v1.1.0`
- ✓ Support PowerShell-friendly local development entrypoints without Bash-only assumptions — `v1.1.0`
- ✓ Distinguish malformed PDFs, low-text/image-only outcomes, and output-write failures in the runtime boundary — `v1.1.0`

### Active

- [ ] Add batch processing and aggregate reporting for multi-PDF workflows.
- [ ] Improve unsupported/scanned PDF diagnostics and define the OCR boundary more clearly for users.
- [ ] Add validation/export hooks for downstream requirement review and SysML-oriented follow-on tooling.

### Out of Scope

- Cloud-hosted or multi-user orchestration in `v1.2.0`
- Automatic OCR correction of arbitrary scans in `v1.2.0`
- Automatic diagram-to-Mermaid conversion
- Repository-scale workflow orchestration beyond local batch CLI usage

## Context

This project is a bridge utility that brings legacy systems documentation into modern AI and MBSE workflows. The main risk has shifted again: `v1.1.0` established a trustworthy release/install path and cleaner runtime behavior, so `v1.2.0` can focus on scaling from one PDF to many and adding clearer downstream validation/export affordances without eroding determinism. The broader SpecForge product family still positions Distill as the distillation stage that prepares canonical markdown inputs for downstream tooling.

## Constraints

- **Input Scope**: PDF only (digital text first) — Reduce ingestion variability for v1 quality.
- **Primary Users**: Systems engineering / MBSE teams — Optimize for technical workflows over general-public UX.
- **Runtime Preference**: Local-first processing, enterprise/offline friendly — Minimize data exposure and fit restricted environments.
- **Quality Flexibility**: External AI APIs remain explicit opt-in; local deterministic behavior is still the baseline.
- **Platform**: Ubuntu, WSL, macOS, and Windows PowerShell 7 must remain first-class user paths.
- **Execution Scale**: `v1.1.0` is still single-PDF focused; `v1.2.0` may broaden that through deterministic batch workflows only if output contracts stay stable.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Prioritize deterministic extraction and provenance before broader feature scope | Trust depends on reproducible, citation-grounded outputs | ✓ Shipped in `v1.0.1` |
| Use page-level citations as provenance granularity | Gives practical traceability without excessive overhead | ✓ Shipped in `v1.0.1` |
| Output both consolidated and split Markdown artifacts | Supports both human review and machine-ingestion workflows | ✓ Shipped in `v1.0.1` |
| Publish single-file binaries as the primary install path | Reduces Python friction for end users | ✓ Shipped in `v1.0.1` |
| Keep manifest paths relative and schema-stable | Protects deterministic downstream consumption | ✓ Shipped in `v1.0.1` |
| Treat release trust as part of runtime behavior | Installation confidence is part of the product contract | ✓ Shipped in `v1.1.0` |
| Use shared local development runners for POSIX and PowerShell | Prevents wrapper drift across supported contributor environments | ✓ Shipped in `v1.1.0` |
| Distinguish malformed PDFs, low-text outcomes, and output-write failures explicitly | Gives users and automation clearer recovery paths | ✓ Shipped in `v1.1.0` |
| Keep scanned/OCR support as explicit boundary-setting work before OCR correction | Prevents lowering extraction quality standards while broadening scope | ⚠ Revisit in `v1.2.0` |
| Add batch/validation/export after trust and runtime ergonomics are stable | Avoids bloating the release that hardened distribution and runtime contracts | — Active for `v1.2.0` |

<details>
<summary>Archived pre-v1.0.1 framing</summary>

Initial project framing emphasized internal MBSE adoption, digital-text PDF scope, and single-document reliability as the first release bar. Historical phase details now live under `.planning/milestones/`.

</details>

---
*Last updated: 2026-02-28 after v1.1.0 release archival and v1.2.0 preparation*
