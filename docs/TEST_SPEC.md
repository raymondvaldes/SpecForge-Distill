# Test Specification: SpecForge Distill v1.2.0-dev

Latest shipped release: `v1.1.0`

This document maps technical test cases to systems engineering functional statements. Every test in the suite must be traceable to a specific capability.

For the higher-level purpose of the suite, see [docs/TEST_IVV_VISION.md](TEST_IVV_VISION.md). That document explains how the tests execute the repository's integration Verification and Validation process, while this file maps individual tests to specific requirement statements.

## Fast IV&V Tier

Small changes should first run the `fast_ivv` marker:

```bash
pytest -m fast_ivv
```

This tier is intentionally narrow. It exists to fail fast on boundary handling, malformed-input rejection, CLI contract drift, and determinism-sensitive helper regressions before the broader reliability and acceptance suites run.

## 1. Ingestion & Quality Layer (`tests/phase1/`)

| Test ID | Ensures Statement | Requirement |
|---------|-------------------|-------------|
| `test_loads_external_taxonomy` | Ensures the engine can load custom obligation verbs from a YAML config. | REQ-03 |
| `test_load_obligation_taxonomy_falls_back_to_basic_parser` | Ensures fallback parsing still handles the flat `obligation_verbs` contract without depending on PyYAML. | REQ-03 |
| `test_load_obligation_taxonomy_parses_nested_taxonomy_shape` | Ensures the lightweight parser handles the shipped nested `taxonomy` structure correctly. | REQ-03 |
| `test_quality_assessment_edge` | Ensures boundary conditions (empty text, long text) don't crash diagnostics. | ING-02 |
| `test_cli_invocation_path` | Ensures the `--dry-run` flag bypasses heavy PDF processing safely. | ING-01 |
| `test_load_pdf_pages_rejects_non_pdf_bytes_immediately` | Ensures malformed non-PDF bytes fail at the loader boundary before third-party parsing can stall. | CLI-04 |
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
| `test_cli_batch_input_dir_is_sorted_and_writes_summary` | Ensures directory-driven batch mode resolves inputs deterministically and writes one aggregate summary artifact. | CLI-05 |
| `test_cli_batch_partial_failure_returns_nonzero_and_preserves_successful_output` | Ensures mixed batch outcomes preserve successful packages while surfacing failures through a non-zero exit and `batch-summary.json`. | OUT-06 / RUN-02 |

## 4. Regression & Determinism (`tests/regression/`, `tests/test_determinism.py`)

| Test ID | Ensures Statement | Requirement |
|---------|-------------------|-------------|
| `test_pipeline_idempotency` | Ensures byte-for-byte identical output across multiple runs. | CLI-03 |
| `test_vcrm_merging` | Ensures VCRM table rows are captured as single merged entities. | REQ-02 |
| `test_varied_id_formats` | Ensures ID detection works anywhere in a sentence (flexible regex). | REQ-04 |
| `test_pipeline_determinism` | Ensures manifest and markdown output remain hermetic and repeatable without mutating repository fixtures. | CLI-03 |
| `test_manifest_paths_are_relative` | Ensures manifest path normalization remains deterministic across output directories. | CLI-03 |
| `test_batch_input_resolution_is_sorted_and_deduplicated` | Ensures explicit batch inputs resolve in deterministic order before execution begins. | CLI-05 |
| `test_batch_output_planning_is_deterministic_for_name_collisions` | Ensures same-stem batch inputs receive stable, collision-safe child output directories. | RUN-02 |

## 5. Reliability, Wrappers, And Release Contracts (`tests/reliability/`)

| Test ID | Ensures Statement | Requirement |
|---------|-------------------|-------------|
| `test_distill_wrapper_prefers_repo_venv` | Ensures the local development runner prefers the repository virtualenv instead of ambient Python resolution. | PLAT-02 |
| `test_powershell_wrapper_tracks_same_shared_runner_contract` | Ensures the PowerShell development entrypoint stays aligned with the same runner contract as the POSIX entrypoint. | PLAT-02 |
| `test_release_workflow_uses_contract_and_self_test_smoke_checks` | Ensures the release workflow keeps `--describe-output json` and `--self-test` as first-run validation gates. | REL-01 |
| `test_troubleshooting_routes_by_failure_class` | Ensures troubleshooting guidance covers the documented runtime failure and low-text result classes. | PLAT-03 |
| `test_pipeline_scaling_is_approximately_linear` | Ensures synthetic pipeline scaling catches non-linear regressions without relying on brittle machine-specific timing budgets. | CLI-04 |
| `test_detect_source_id_scales_without_regex_backtracking` | Ensures pathological input does not trigger catastrophic regex behavior in requirement ID detection. | CLI-04 |
| `test_batch_output_planning_scales_approximately_linearly` | Ensures batch naming and output planning remain scaling-oriented even with many colliding stems. | RUN-02 |
| `test_batch_execution_records_missing_files_without_aborting_successful_items` | Ensures helper-level batch execution keeps successful outputs even when one input is missing. | OUT-06 / RUN-02 |

## 6. Final Acceptance (`tests/test_v1_acceptance_final.py`)

| Test ID | Ensures Statement | Requirement |
|---------|-------------------|-------------|
| `test_v1_full_acceptance` | Ensures the full end-to-end flow meets all 20 v1 requirements. | ALL-v1 |
| `test_v1_empty_acceptance` | Ensures graceful handling and correct messaging for empty PDFs. | RUN-01 |
| `test_phase3_batch_partial_failure_acceptance` | Ensures a mixed-success batch still produces a valid successful package and records the failed item explicitly. | OUT-06 / RUN-02 |
| `test_v1_batch_acceptance` | Ensures the supported explicit batch workflow behaves as a user-facing acceptance flow rather than just a helper contract. | CLI-05 / OUT-06 / RUN-02 |
