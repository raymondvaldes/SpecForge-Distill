---
phase: 8
title: "Extended Ingestion and Validation Hooks"
status: "active"
---

# Phase 8 Context: Extended Ingestion and Validation Hooks

This document captures the user's design decisions for Phase 8. Downstream agents (researcher, planner, executor) must treat these as absolute constraints.

## 1. Scanned/OCR PDF Handling

- **Behavior & Timing:** The pipeline must perform a hard block (error out) very early in the **ingestion phase** if a low-text PDF is detected.
- **Classification & Heuristic:** Group "image-only" (no text layer) and "messy OCR" together under a single **"low-text quality"** classification. The heuristic should be based on a **Text vs Image ratio**, and completely **blank pages must be ignored** in this calculation.
- **User Guidance:** The error message must explicitly advise the user to **"Run through an external OCR tool first"**.
- **Overrides:** The system must provide a CLI flag (e.g., `--force` or `--ignore-low-text`) to allow users to override the block and force processing anyway.
- **Error Formatting:** Output the error as human-readable standard error (stderr) by default, but allow structured JSON output if a `--json` flag is active (or similar pipeline mode).

## 2. Validation/Linting Output

- **Trigger & Behavior:** Linting must be **always on** (runs automatically on every execution). It must **never fail the process** (always Exit 0, warn only) to avoid breaking automated CI/CD pipelines.
- **Output Destination:** Results must be embedded as a **top-level key** (e.g., `validation` or `lint_results`) within the existing `manifest.json`, AND a human-readable summary should be printed to the console.
- **Scope & Severity:** The linter will check for both **structural** and **semantic** gaps. Issues should be categorized by standard severities (`info`, `warning`, `error`).
- **Most Critical Check:** The #1 most important semantic check for v1 is detecting a **"High SHALL word count but Low/Zero extracted requirements"** scenario.
- **Configuration:** Thresholds for linting (like the SHALL-to-Requirement ratio) should use **hardcoded sensible defaults** for now. No user-configurable thresholds are needed in this version.

## 3. SysML Interop Contracts

- **Output Strategy:** Use a **JSON Schema tailored for bridges**. Do not attempt to export native XMI files. Instead, add richer, SysML-ready metadata directly to the requirements in `manifest.json` so downstream tools can easily map it.
- **Content Scope:** This enrichment applies to **Requirements only** (not Architecture or Tables).
- **Trigger:** Adding this SysML interop metadata should be the **default behavior** (always on), no special flags required.
- **Data Structure:** The new SysML-specific fields must be added as **flat properties** directly on the requirement JSON objects (not nested in a sub-object). If a field doesn't apply to a specific requirement, **omit the key entirely** (do not include it as null).
- **SysML Specifics:** 
  - Remain **agnostic** regarding SysML version (v1.4 vs v2).
  - Use **standard types only** (do not try to automatically assign specific SysML stereotypes).
  - **Do not attempt to automatically detect trace links** (e.g., `satisfies`); leave linking to the user in their respective SysML tools.
  - Rely on the **main manifest version**; no dedicated schema version for the SysML fields is required.
