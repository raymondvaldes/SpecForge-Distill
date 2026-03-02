# SpecForge Distill

## What This Is

SpecForge Distill is a local-first command line utility for systems engineering and MBSE teams to convert legacy specification PDFs into deterministic, provenance-linked Markdown and JSON artifacts. The shipped `v1.1.0` release supports a binary-first installation path on Ubuntu/WSL, macOS Intel, macOS Apple Silicon, and Windows PowerShell 7, while preserving source grounding through page-level citations and trust-first install verification.

## Core Value

Transform legacy spec PDFs into structured, provenance-linked markdown without missing critical requirement obligations.

## Current State

- Latest shipped release: `v1.1.0` on 2026-02-28
- Current branch target: `v1.2.0`
- Stable capabilities: deterministic single-document distillation, split/consolidated Markdown outputs, manifest generation, downloadable cross-platform binaries, checksum-first install verification, `--describe-output json`, `--emit-example-output`, `--self-test`, explicit multi-file and directory-driven batch mode, `batch-summary.json`, and clearer runtime failure/result classification
- Known limits: digital-text PDFs only, no full validation/export workflow yet, and no explicit scanned/OCR command path beyond low-text signaling

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
- ✓ Support deterministic local batch workflows with aggregate reporting and partial-failure preservation — `v1.2.0`
- ✓ Improve scanned/OCR-only PDF diagnostics and provide clear user guidance — `v1.2.0`
- ✓ Add validation/lint-oriented output hooks and enriched SysML interop metadata — `v1.2.0`

### Active

- [ ] (Milestone v1.2.0 complete)

### Out of Scope

- Cloud-hosted or multi-user orchestration in `v1.2.0`
- Automatic OCR correction of arbitrary scans in `v1.2.0`
- Automatic diagram-to-Mermaid conversion
- Repository-scale workflow orchestration beyond local batch CLI usage

## Context

This project is a bridge utility that brings legacy systems documentation into modern AI and MBSE workflows. The main risk has shifted again: Phase 7 established deterministic batch execution and aggregate reporting on top of the `v1.1.0` trust/runtime baseline, so the remaining `v1.2.0` work can focus on scanned/OCR boundaries and downstream validation/export affordances without reopening batch contract questions. The broader SpecForge product family still positions Distill as the distillation stage that prepares canonical markdown inputs for downstream tooling.

## Constraints

- **Input Scope**: PDF only (digital text first) — Reduce ingestion variability for v1 quality.
- **Primary Users**: Systems engineering / MBSE teams — Optimize for technical workflows over general-public UX.
- **Runtime Preference**: Local-first processing, enterprise/offline friendly — Minimize data exposure and fit restricted environments.
- **Quality Flexibility**: External AI APIs remain explicit opt-in; local deterministic behavior is still the baseline.
- **Platform**: Ubuntu, WSL, macOS, and Windows PowerShell 7 must remain first-class user paths.
- **Execution Scale**: `v1.2.0` now supports deterministic local batch workflows, but output contracts must remain stable as validation/export scope expands.

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
| Add batch/validation/export after trust and runtime ergonomics are stable | Avoids bloating the release that hardened distribution and runtime contracts | ✓ Batch/reporting shipped in Phase 7; validation/export remains active for `v1.2.0` |

<details>
<summary>Archived pre-v1.0.1 framing</summary>

Initial project framing emphasized internal MBSE adoption, digital-text PDF scope, and single-document reliability as the first release bar. Historical phase details now live under `.planning/milestones/`.

</details>

---
*Last updated: 2026-03-01 after completing Phase 7 batch processing and aggregate reporting*
