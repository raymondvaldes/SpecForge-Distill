# Engineering Standards: SpecForge Distill

This document defines the mandatory architectural patterns for SpecForge Distill. All new features must adhere to these four pillars to ensure the tool remains "AI-First" and "Trust-Grounded."

## 1. Schema Enforcement (Strict Boundaries)
- **Rule:** Every data structure exiting a module must be a **Pydantic Model**.
- **Rationale:** Downstream AIs and automation tools require 100% predictable schemas.
- **Enforcement:** Never return raw dicts across package boundaries.

## 2. Validation as Data (Warn, Don't Crash)
- **Rule:** Domain-level issues (missing IDs, ambiguous text) must be captured as `ValidationIssue` objects, not raised as exceptions or assertions.
- **Rationale:** Users (human and AI) need partial results from "noisy" PDFs rather than total process failure.
- **Enforcement:** All extraction logic must have a corresponding entry in `specforge_distill/validation.py`.

## 3. Explicit Failure Classification
- **Rule:** Hard runtime failures (e.g., FileNotFoundError, PermissionError) must be mapped to a member of `FAILURE_CLASSES` in `automation.py`.
- **Rationale:** Automation agents need stable error codes to attempt autonomous recovery.
- **Enforcement:** The CLI must return a specific non-zero exit code (2-5) mapped to the failure class.

## 4. The Evidence Mandate (Provenance)
- **Rule:** No entity exists without a `Citation`.
- **Rationale:** Trust is built on evidence. Neither humans nor AIs should be asked to "blindly trust" an extraction.
- **Enforcement:** `assert_citations_present` must remain a blocking call in the main pipeline.

---
*Last Updated: 2026-03-01*
