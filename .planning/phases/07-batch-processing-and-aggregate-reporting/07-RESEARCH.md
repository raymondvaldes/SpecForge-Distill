# Phase 07 Research

**Phase:** 07
**Name:** Batch Processing and Aggregate Reporting
**Date:** 2026-03-01
**Relevant requirements:** `CLI-05`, `OUT-06`, `RUN-02`

## Goal

Let users process multiple PDFs in one run without losing deterministic output naming, actionable partial-failure behavior, or the existing machine-readable CLI contract.

## Current Baseline

The current CLI only supports one positional `pdf_path` at a time. Special modes (`--describe-output`, `--emit-example-output`, `--self-test`) are already mutually exclusive and stable. Normal runs either:

- write one output package through `write_output_package()`, or
- emit one dry-run JSON payload through `_build_dry_run_payload()`.

Important boundaries already in place:

- `src/specforge_distill/cli.py` owns argparse, special-mode gating, and the normal single-run flow.
- `src/specforge_distill/automation.py` owns machine-readable schemas, exit-code documentation, and output-package summaries.
- Determinism tests already protect stable markdown and manifest generation for one source at a time.

Phase 7 should extend those boundaries rather than replace them.

## Planning Constraints

### Keep single-file behavior stable

Single-PDF invocation should continue to behave exactly as it does now unless the user explicitly enters batch mode. Existing output directory naming, human-readable console output, and dry-run behavior should remain intact for the one-file path.

### Batch mode must be explicit but not awkward

The lowest-friction contract is:

- multiple positional PDF paths for explicit multi-file runs
- one `--input-dir DIR` option for directory-based runs

That keeps the current CLI mental model intact while satisfying both halves of `CLI-05`.

### Determinism must cover discovery, ordering, and naming

The current project already treats deterministic output as a product claim. For batch mode, determinism has to apply to:

- which files are selected from a directory
- the order they are processed
- the output directory assigned to each input
- the order of entries in any aggregate summary

Processing order should therefore be derived from a normalized, sorted list of resolved PDF paths before any execution begins.

### Partial failure is a first-class result

`RUN-02` requires a non-zero exit when any input fails, but Phase 7 should not fail fast. Users need successful outputs preserved for the files that did work, plus a summary that clearly identifies which inputs failed and why.

## Recommended Product Decisions

### Batch input contract

Recommended Phase 7 contract:

- Keep special modes unchanged.
- Change the normal positional argument to accept multiple PDF paths.
- Add `--input-dir DIR` for directory mode.
- Treat `--input-dir` and explicit positional PDF lists as mutually exclusive in normal distill mode.
- For directory mode, scan direct child PDFs only in Phase 7. Recursive traversal can be deferred until there is a clear requirement for it.
- Reject an empty resolved input set as invalid invocation rather than silently succeeding.

This gives the user one obvious directory path and one obvious explicit-list path without introducing glob semantics or recursive traversal edge cases in the same phase.

### Output directory strategy

Recommended output strategy:

- Single-file run: preserve the existing `<stem>_distilled` default behavior.
- Batch run with `-o/--output-dir`: treat the provided directory as the batch root.
- Batch run without `-o`: create a deterministic batch root such as `./specforge_distill_batch_output`.
- Inside the batch root, create one child output directory per source PDF.

Collision handling matters when two inputs share the same stem. Phase 7 should therefore introduce one shared helper that:

- sanitizes the visible child directory name, and
- adds a deterministic suffix only when needed to prevent collisions.

That logic should not live inline in `cli.py`.

### Aggregate summary contract

Recommended machine-readable contract:

- Normal batch runs write one `batch-summary.json` file in the batch root.
- Batch `--dry-run` prints one aggregate JSON payload to stdout and writes no files.
- Each item in the batch summary should include:
  - source path
  - status (`ok` or `failed`)
  - output directory or `null`
  - generated file paths when successful
  - warning count
  - entity counts
  - extraction assessment
  - failure class and detail when failed
- The top-level summary should include:
  - mode
  - version
  - overall status (`ok` or `partial_failure`)
  - totals for resolved, succeeded, failed, warnings, requirements, and artifacts
  - item list in deterministic input order

This is enough for automation consumers without turning the summary into a second manifest format.

### Exit-code strategy

Phase 7 should use a distinct batch failure exit code instead of overloading the single-file processing code path. Reusing exit code `3` would hide whether the problem was:

- one failed file in a larger batch, or
- a single-file processing failure before any aggregate result existed.

Recommended approach:

- `0`: all batch items succeeded
- new explicit batch non-zero code when any batch item fails after resolution begins

That keeps automation clients from having to infer batch partial failure purely from stdout or stderr text.

## Maintainability Split

Phase 7 should avoid pushing all of the new behavior into `cli.py`.

Recommended code organization:

- `src/specforge_distill/cli.py`
  - parser updates
  - mode validation
  - dispatch to single-file vs batch orchestration
- `src/specforge_distill/batch.py`
  - input resolution
  - deterministic ordering
  - batch output-directory planning
  - per-item execution orchestration
  - aggregate result assembly
- `src/specforge_distill/automation.py`
  - schema definitions
  - output/failure contract metadata
  - batch summary builders used by `--describe-output`

This keeps parser concerns, orchestration logic, and machine-readable contract metadata from drifting into one file.

## Test And IV&V Implications

Phase 7 should extend the existing IV&V strategy instead of adding slow or brittle batch tests.

Key test responsibilities:

- parser and invocation contract tests for explicit list vs directory mode
- aggregate summary schema tests through `--describe-output`
- acceptance tests for mixed-success batch runs that preserve successful outputs
- determinism tests for path ordering, summary ordering, and collision-safe naming
- robustness/performance checks that use scaling-oriented assertions instead of machine-sensitive timing targets

The performance signal should focus on:

- avoiding repeated directory scans
- avoiding non-deterministic filesystem iteration
- keeping batch summary assembly linear in input count

## Recommended Plan Split

### 07-01

Add the batch CLI entry path, deterministic input resolution, and shared output-planning helpers without yet finalizing the aggregate reporting artifact.

### 07-02

Add the aggregate batch summary contract, machine-readable describe-output updates, dry-run aggregation, and user-facing docs for the new batch workflow.

### 07-03

Add acceptance, determinism, and robustness coverage for mixed-success batches, deterministic naming collisions, and aggregate exit semantics. Update IV&V mapping docs so the new batch contract is traceable.

## Risks To Watch

- letting special-mode validation drift while changing positional parsing
- silently changing single-file default output behavior
- creating unstable child output names when stems collide
- writing aggregate summaries in a different order than actual processing order
- coupling batch error handling too tightly to current single-file stderr strings

## Research Outcome

Phase 7 is ready for executable planning. The main architectural decision is to keep single-file flows intact while introducing a small shared batch orchestration layer and one explicit aggregate summary artifact.
