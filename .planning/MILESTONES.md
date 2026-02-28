# Project Milestones: SpecForge Distill

Entries are listed newest first.

## v1.1.0 Trusted Distribution And Runtime Release (Shipped: 2026-02-28)

**Delivered:** A hardened `v1.1.0` release that made the binary install path checksum-first and self-test-first, added generated trust-first GitHub release notes, and improved local/runtime ergonomics across POSIX shells, WSL, and PowerShell 7.

**Phases completed:** 5-6 (6 plans total)

**Key accomplishments:**
- Versioned official release assets, per-asset checksums, and aggregate `checksums.txt` publication are now enforced by checked-in release contracts.
- The CLI now supports `--describe-output json`, `--emit-example-output`, and `--self-test` as stable automation and install-verification paths.
- Local development entrypoints for POSIX shells and PowerShell 7 now share one runner contract.
- Runtime behavior now distinguishes malformed PDFs, low-text/image-only outcomes, and output-write failures while the IV&V suite remains fast and deterministic.

**Known gaps carried forward:**
- Batch processing and aggregate reporting
- Richer scanned/OCR diagnostics
- Validation/export hooks for downstream review and interop

**Stats:**
- 2 phases completed
- 6 plans completed
- Latest stable tag: `v1.1.0`

**What's next:** `v1.2.0` focuses on batch processing, aggregate reporting, scanned/OCR diagnostics, and validation/export hooks.

---

## v1.0.1 Stable Binary Release (Shipped: 2026-02-28)

**Delivered:** A stable binary-first release of SpecForge Distill for Ubuntu/WSL, macOS Intel, macOS Apple Silicon, and Windows PowerShell 7.

**Phases completed:** 1-4 (17 plans total)

**Key accomplishments:**
- Built deterministic digital-text PDF distillation with page-level provenance.
- Added requirement modeling, obligation detection, and stable ID generation.
- Shipped consolidated/split Markdown outputs plus `manifest.json`.
- Published cross-platform single-file binaries with CI-backed release validation.

**Stats:**
- 4 phases completed
- 17 plans completed
- Latest stable tag: `v1.0.1`

**What's next:** `v1.1.0` focuses on trusted distribution, cross-platform runtime ergonomics, batch workflows, and validation/interop hooks.

---
