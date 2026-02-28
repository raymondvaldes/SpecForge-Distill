# Test Specification: SpecForge Distill v1.1.0

Latest shipped release: `v1.1.0`

This document maps technical test cases to systems engineering functional statements. Every test in the suite must be traceable to a specific capability.

For the higher-level purpose of the suite, see [docs/TEST_IVV_VISION.md](TEST_IVV_VISION.md). That document explains how the tests execute the repository's integration Verification and Validation process, while this file maps individual tests to specific requirement statements.

## 1. Ingestion & Quality Layer (`tests/phase1/`)

| Test ID | Ensures Statement | Requirement |
|---------|-------------------|-------------|
| `test_loads_external_taxonomy` | Ensures the engine can load custom obligation verbs from a YAML config. | REQ-03 |
| `test_quality_assessment_edge` | Ensures boundary conditions (empty text, long text) don't crash diagnostics. | ING-02 |
| `test_cli_invocation_path` | Ensures the `--dry-run` flag bypasses heavy PDF processing safely. | ING-01 |
| `test_cli_write_output_failure_returns_error_and_nonzero` | Ensures output-path and permission failures are surfaced as a distinct runtime boundary, not a generic crash. | CLI-04 |
| `test_cli_dry_run_reports_likely_text_layer_issue` | Ensures successful low-text runs are distinguishable from malformed-PDF failures. | CLI-04 |

## 2. Requirement Modeling (`tests/phase2/`)

| Test ID | Ensures Statement | Requirement |
|---------|-------------------|-------------|
| `test_id_preservation` | Ensures IDs present in source (e.g. [REQ-001]) are never overwritten. | REQ-04 |
| `test_deterministic_ids` | Ensures anonymous requirements receive stable hashes based on text and page. | REQ-05 |

## 3. Rendering & Output (`tests/phase3/`)

| Test ID | Ensures Statement | Requirement |
|---------|-------------------|-------------|
| `test_manifest_schema` | Ensures generated JSON validates against the Pydantic v2 model. | OUT-05 |
| `test_markdown_robustness` | Ensures special characters (*, #) in text don't break markdown layout. | OUT-03 |
| `test_interop_serialization` | Ensures SysML v2 hooks are present in both artifacts and requirements. | INT-01 |

## 4. Regression & Determinism (`tests/regression/`, `tests/test_determinism.py`)

| Test ID | Ensures Statement | Requirement |
|---------|-------------------|-------------|
| `test_pipeline_idempotency` | Ensures byte-for-byte identical output across multiple runs. | CLI-03 |
| `test_vcrm_merging` | Ensures VCRM table rows are captured as single merged entities. | REQ-02 |
| `test_varied_id_formats` | Ensures ID detection works anywhere in a sentence (flexible regex). | REQ-04 |
| `test_pipeline_determinism` | Ensures manifest and markdown output remain hermetic and repeatable without mutating repository fixtures. | CLI-03 |
| `test_manifest_paths_are_relative` | Ensures manifest path normalization remains deterministic across output directories. | CLI-03 |

## 5. Reliability, Wrappers, And Release Contracts (`tests/reliability/`)

| Test ID | Ensures Statement | Requirement |
|---------|-------------------|-------------|
| `test_distill_wrapper_prefers_repo_venv` | Ensures the local development runner prefers the repository virtualenv instead of ambient Python resolution. | PLAT-02 |
| `test_powershell_wrapper_tracks_same_shared_runner_contract` | Ensures the PowerShell development entrypoint stays aligned with the same runner contract as the POSIX entrypoint. | PLAT-02 |
| `test_release_workflow_uses_contract_and_self_test_smoke_checks` | Ensures the release workflow keeps `--describe-output json` and `--self-test` as first-run validation gates. | REL-01 |
| `test_troubleshooting_routes_by_failure_class` | Ensures troubleshooting guidance covers the documented runtime failure and low-text result classes. | PLAT-03 |
| `test_pipeline_scaling_is_approximately_linear` | Ensures synthetic pipeline scaling catches non-linear regressions without relying on brittle machine-specific timing budgets. | CLI-04 |
| `test_detect_source_id_scales_without_regex_backtracking` | Ensures pathological input does not trigger catastrophic regex behavior in requirement ID detection. | CLI-04 |

## 6. Final Acceptance (`tests/test_v1_acceptance_final.py`)

| Test ID | Ensures Statement | Requirement |
|---------|-------------------|-------------|
| `test_v1_full_acceptance` | Ensures the full end-to-end flow meets all 20 v1 requirements. | ALL-v1 |
| `test_v1_empty_acceptance` | Ensures graceful handling and correct messaging for empty PDFs. | RUN-01 |
