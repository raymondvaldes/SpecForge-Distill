# Test Integration Verification And Validation Vision

Latest shipped release: `v1.1.0`

## Purpose

This document defines the vision for the Test Integration Verification and Validation process for SpecForge Distill. In this repository, test cases are not treated as generic code-coverage assets. They are the executable mechanism used to verify system behavior, validate user-facing outcomes, and produce release confidence for a deterministic document-compilation product.

The test suite therefore exists to answer a narrow question with defensible evidence:

Does the system produce the right outputs, with the right contracts, on the right platforms, with deterministic behavior and acceptable performance for supported usage?

## Vision Statement

The SpecForge Distill IV&V process should make every important product claim executable, repeatable, and auditable. A change is not considered integrated simply because it compiles or passes isolated unit logic. It is integrated only when the relevant tests prove that the end-to-end behavior, output contract, release path, and trust path still satisfy the intended operating model.

## What The Test Cases Are Responsible For

The test cases execute the project IV&V process across five layers:

1. Requirement and extraction verification.
   Tests prove that ingestion, narrative extraction, caption handling, table handling, normalization, citation linkage, and requirement identity behave as specified.
2. Integration verification.
   Tests prove that pipeline outputs, manifest generation, markdown generation, CLI behavior, wrappers, and machine-readable contracts continue to work together as one system.
3. Validation of user-facing workflows.
   Tests prove that the product still supports the workflows the user actually depends on: trusted install, self-test, dry-run, release binary use, and end-to-end PDF processing.
4. Regression containment.
   Tests prove that previously supported behaviors remain stable across refactors, release work, packaging work, and extraction changes.
5. Reliability and performance guardrails.
   Tests prove that determinism, concurrency tolerance, pathological-input handling, and scaling characteristics remain within acceptable operational bounds.

## IV&V Principles

### Deterministic Evidence First

SpecForge Distill is intended to be deterministic. The IV&V process must prefer byte-stable and schema-stable evidence over subjective inspection. Tests should assert contracts, ordering, identifiers, manifest structure, and rendered outputs directly.

### Requirement Traceability

Every meaningful test should map to a product capability, workflow promise, release guarantee, or failure-class expectation. The suite should remain traceable back to technical requirements and forward to observable outputs.

### Integration Over Isolated Correctness

A function that passes in isolation is not enough. The process must prioritize system boundaries where integration failures occur:

- ingest to pipeline
- pipeline to normalization
- normalization to renderers
- renderers to package writer
- CLI to automation modes
- release workflow to downloadable assets
- wrapper/runtime environment to user execution path

### Trust Path Verification

For this product, install trust is part of system behavior. The IV&V process must verify the sequence users are instructed to follow:

1. obtain the correct asset
2. verify checksum
3. run `--version`
4. run `--self-test`
5. process a real PDF

If this path is broken, the product is not operationally validated even if internal extraction logic still works.

### Performance As A Contract, Not A Benchmark Contest

Performance tests should guard against pathological regressions, non-linear scaling, unnecessary repeated work, and robustness failures. They should avoid fragile machine-specific timing targets when a relative or scaling-based assertion provides stronger long-term signal.

### Deterministic Pytest Orchestration

IV&V evidence is only trustworthy if the test runner behavior is also controlled. Pytest execution in this repository must follow a deterministic orchestration policy:

- run one controlling pytest process at a time for a given verification pass
- prefer bounded subprocess execution with explicit return codes, captured stdout/stderr, and hard timeouts
- use the fast IV&V tier first for small changes, then expand to broader file or suite coverage
- when isolating a suspected regression, bisect by file before bisecting by individual test node
- treat overlapping pytest runs, mixed ad hoc probes, and stale long-lived subprocesses as invalid evidence
- write transient diagnostics to `/tmp` or another scratch path, not into the repository tree

If a verification pass becomes noisy or ambiguous, the run should be discarded and repeated under one clean controller process instead of trying to infer correctness from partial output.

## Scope Of Verification

The current test architecture maps to the IV&V process as follows.

### Phase Verification

`tests/phase1/`, `tests/phase2/`, and `tests/phase3/` verify the technical contracts of the major system layers:

- ingestion and text-quality assessment
- candidate extraction and provenance
- requirement modeling and identity
- manifest and markdown rendering
- CLI output package behavior
- interop and automation hooks

### Integration Verification

Cross-cutting integration checks live in tests such as:

- [`tests/test_determinism.py`](../tests/test_determinism.py)
- [`tests/test_v1_acceptance_final.py`](../tests/test_v1_acceptance_final.py)
- [`tests/reliability/test_wrapper_and_fixture_contracts.py`](../tests/reliability/test_wrapper_and_fixture_contracts.py)
- [`tests/reliability/test_release_and_wrapper_contracts.py`](../tests/reliability/test_release_and_wrapper_contracts.py)

These tests verify that separate subsystems still compose into a coherent product.

### Validation

Validation means the product proves the behavior users and downstream tools care about, not just internal correctness. In this repository, validation includes:

- acceptance flows using representative fixture inputs
- built-in `--self-test` behavior
- stable `--describe-output json` automation contracts
- local development runner behavior for POSIX shells and PowerShell 7
- release workflow trust checks
- real fixture parsing for supported digital-text PDFs

### Reliability And Performance

Reliability tests must focus on:

- deterministic output across runs
- fixture stability
- wrapper/runtime behavior
- malformed or unsupported input handling
- output-path and permission failure handling
- successful low-text or image-only extraction signaling
- concurrency safety at shared output boundaries
- performance scaling that detects quadratic or catastrophic behavior

## Expected Test Evidence

A healthy IV&V process produces evidence in forms that are reviewable and repeatable:

- passing pytest suites
- bounded pytest subprocess results with explicit exit codes when isolation is needed
- validated `manifest.json` output
- stable markdown output
- release-workflow contract checks
- self-test pass/fail payload validation
- deterministic acceptance outputs

When possible, evidence should be machine-readable and tied to concrete failure classes rather than free-form console interpretation.

## Entry And Exit Expectations For Changes

### A change is ready to integrate when:

- the impacted requirement or workflow has explicit test coverage
- the relevant integration boundary is exercised
- deterministic outputs remain stable unless the contract intentionally changed
- release, wrapper, and automation expectations are updated if behavior changed
- performance-sensitive paths are protected from obvious regression
- the verification path itself was run through one clean deterministic pytest controller process

### A change is not complete when:

- it passes only unit-level assertions but not end-to-end flows
- it changes output shape without updating contract tests
- it mutates user-trust workflows without release-path validation
- it relies on manual interpretation where a deterministic assertion should exist
- it is declared green from overlapping, partially buffered, or otherwise ambiguous pytest runs

## Non-Goals

This IV&V vision does not attempt to:

- maximize raw test count
- optimize for coverage percentages alone
- turn every helper into an isolated micro-test if the system-level contract matters more
- freeze implementation details that are irrelevant to user-visible or automation-visible behavior

## Relationship To Other Documents

- [`docs/vision.md`](vision.md) defines the product-level vision.
- [`docs/TEST_SPEC.md`](TEST_SPEC.md) maps concrete tests to requirement statements.
- [`docs/BUILD.md`](BUILD.md) defines contributor and release verification workflows.
- [`docs/TROUBLESHOOTING.md`](TROUBLESHOOTING.md) defines failure-class recovery for runtime validation issues.

Together, these documents define why the IV&V process exists, what it must prove, and how the repository executes it.
