# Phase 1: Extraction and Provenance Foundation - Context

**Gathered:** 2026-02-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 delivers single-PDF ingestion for digital-text files, broad candidate extraction from narrative/table/caption sources, low text-layer quality warnings, architecture-section extraction, and page-level provenance on extracted artifacts. This phase establishes extraction breadth and traceability; downstream obligation policy tuning and richer normalization continue in later phases.

</domain>

<decisions>
## Implementation Decisions

### Candidate Capture Scope
- Use broad candidate capture in Phase 1 rather than strict SHALL-only filtering.
- Include requirement-adjacent non-obligation statements as neutral candidates for later classification.
- Preserve bounded nearby context for each candidate to support review/debug.
- For long paragraphs, split candidates when modal/obligation verbs are present.

### Source Typing and Duplication Strategy
- Keep source-typed candidate buckets: `narrative`, `table_cell`, `caption_context`.
- If equivalent statements appear across sources, keep both candidates and link them rather than deduping immediately.
- Preserve source-type visibility to make coverage gaps and parser failures diagnosable.

### Obligation Verb Baseline Governance
- Maintain a configurable obligation-verb baseline list (starting with `shall`, `must`, `required`) and allow extension.
- Store taxonomy in an external project config file (not hardcoded in code constants).
- If unknown domain verbs appear, keep the candidate and flag `unknown_obligation_verb` for review.
- Record taxonomy version in output metadata for run reproducibility.
- (Autonomous default while user away) Do not auto-add unknown verbs to taxonomy; log suggestions for explicit human approval.

### Claude's Discretion
- Exact context window sizing and token/character bounds around extracted candidates.
- Internal linkage format for duplicate-equivalent candidates across source types.
- Flag naming convention details as long as semantics remain stable and documented.

</decisions>

<specifics>
## Specific Ideas

- User wants a path that avoids future regret on obligation semantics, including room for ARINC-style/domain verb sets.
- North star: establish Distill as best-in-class utility for this problem through strong recall plus auditable provenance.

</specifics>

<deferred>
## Deferred Ideas

- Full obligation-quality linting/scoring remains a separate tool concern (outside Distill v1 scope).
- Finalized domain-specific verb taxonomy curation workflow can expand in a later phase.

</deferred>

---

*Phase: 01-extraction-and-provenance-foundation*
*Context gathered: 2026-02-26*
