# Test Specification: SpecForge Distill v1.0.0

This document maps technical test cases to systems engineering functional statements. Every test in the suite must be traceable to a specific capability.

## 1. Ingestion & Quality Layer (`tests/phase1/`)

| Test ID | Ensures Statement | Requirement |
|---------|-------------------|-------------|
| `test_loads_external_taxonomy` | Ensures the engine can load custom obligation verbs from a YAML config. | REQ-03 |
| `test_quality_assessment_edge` | Ensures boundary conditions (empty text, long text) don't crash diagnostics. | ING-02 |
| `test_cli_invocation_path` | Ensures the `--dry-run` flag bypasses heavy PDF processing safely. | ING-01 |

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

## 5. Final Acceptance (`tests/test_v1_acceptance_final.py`)

| Test ID | Ensures Statement | Requirement |
|---------|-------------------|-------------|
| `test_v1_full_acceptance` | Ensures the full end-to-end flow meets all 20 v1 requirements. | ALL-v1 |
| `test_v1_empty_acceptance` | Ensures graceful handling and correct messaging for empty PDFs. | RUN-01 |
