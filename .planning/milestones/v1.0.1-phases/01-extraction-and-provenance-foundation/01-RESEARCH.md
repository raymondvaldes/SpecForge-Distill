# Phase 1: Extraction and Provenance Foundation - Research

**Researched:** 2026-02-26
**Domain:** Digital-text PDF extraction pipeline foundations for systems-engineering artifacts
**Confidence:** HIGH

## User Constraints

### Locked Decisions (from 01-CONTEXT.md)
- Use broad candidate capture in Phase 1 rather than strict SHALL-only filtering.
- Include requirement-adjacent non-obligation statements as neutral candidates for later classification.
- Preserve bounded nearby context for each candidate to support review/debug.
- For long paragraphs, split candidates when modal/obligation verbs are present.
- Keep source-typed candidate buckets: `narrative`, `table_cell`, `caption_context`.
- If equivalent statements appear across sources, keep both candidates and link them rather than deduping immediately.
- Maintain a configurable obligation-verb baseline list in external project config.
- If unknown domain verbs appear, keep the candidate and flag `unknown_obligation_verb`.
- Record taxonomy version in output metadata.

### Claude's Discretion
- Exact context window sizing and token/character bounds around extracted candidates.
- Internal linkage format for duplicate-equivalent candidates across source types.
- Flag naming conventions if semantics stay stable/documented.

### Deferred Ideas (out of scope for this phase)
- Full requirement-quality linting/scoring engine.
- Finalized enterprise taxonomy governance workflow.

## Summary

Phase 1 should implement a deterministic, source-typed extraction baseline with provenance attached at candidate creation time. The extraction pipeline should prioritize coverage and traceability over early filtering so downstream phases can classify and refine candidates without losing potential obligations.

A Python package layout with a thin CLI, explicit ingest/extract/provenance modules, and test fixtures is the fastest path with lowest rework risk. The most important technical choice is to preserve typed candidate origin (`narrative`, `table_cell`, `caption_context`) and defer aggressive dedupe/filtering until after citation-grounded extraction is complete.

**Primary recommendation:** Build Phase 1 as four plans: ingest foundation, narrative/architecture extraction, table/caption extraction, then provenance propagation and acceptance verification.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12.x | Runtime and packaging baseline | Strong PDF/text ecosystem and simple local-first deployment |
| Typer | 0.24.x | CLI command surface (`distill`) | Typed CLI patterns with fast implementation |
| pypdf | 6.7.x | PDF page/text/object access | Mature parsing base for digital-text PDFs |
| pdfplumber | 0.11.9 | Table/layout-aware extraction | Better table/cell handling than plain text extraction alone |
| Pydantic | 2.12.x | Candidate/provenance schema contracts | Keeps extraction outputs deterministic and validated |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| PyYAML | 6.x | External taxonomy config loading | Required for obligation verb list + version metadata |
| pytest | 9.x | Deterministic regression checks | Validate coverage and warnings in fixtures |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pypdf + pdfplumber | Docling | Strong conversion tooling but heavier integration and broader scope than needed for Phase 1 |
| Typer | Click | Equivalent capability but Typer accelerates typed CLI development |

**Installation:**
```bash
pip install "typer>=0.24,<0.25" "pypdf>=6.7,<7" "pdfplumber>=0.11.9,<0.12" "pydantic>=2.12,<3" "PyYAML>=6,<7"
pip install -D "pytest>=9,<10"
```

## Architecture Patterns

### Recommended Project Structure
```text
src/specforge_distill/
├── cli.py                     # CLI entrypoint and command wiring
├── config/
│   └── obligation_verbs.yml   # External verb taxonomy and version
├── ingest/
│   ├── pdf_loader.py          # PDF read helpers
│   └── text_quality.py        # low-text-quality diagnostics
├── extract/
│   ├── narrative.py           # paragraph extraction + modal split logic
│   ├── architecture.py        # architecture section extraction
│   ├── tables.py              # table cell extraction
│   ├── captions.py            # caption/nearby context extraction
│   └── merge.py               # typed candidate merge/linking
├── provenance/
│   ├── models.py              # citation data models
│   └── linker.py              # attach page anchors to all candidates
└── pipeline.py                # orchestration for Phase 1 outputs
```

### Pattern 1: Typed Candidate Ledger
**What:** Preserve each candidate with explicit source type and origin anchors.
**When to use:** Anytime multiple extraction channels feed later normalization.
**Example:**
```python
candidate.source_type = "table_cell"
candidate.origin = {"page": 14, "table_id": "p14_t2", "cell": "R3C2"}
```

### Pattern 2: Late Dedupe via Link Edges
**What:** Keep potentially duplicate candidates but add equivalence links.
**When to use:** When recall matters more than early noise reduction.
**Example:**
```python
link = {"relation": "semantic_duplicate", "target_id": "cand-0018", "confidence": 0.82}
```

### Anti-Patterns to Avoid
- **Early hard filtering:** drops candidates that may become requirements after phase-2 classification.
- **Citation-at-render-time:** provenance drift occurs when anchors are attached too late.
- **Unified anonymous candidate list:** hides extraction channel failures and complicates tuning.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PDF parsing primitives | Custom binary parser | `pypdf` | Avoids brittle low-level parsing complexity |
| Complex table geometry engine | Bespoke table detector | `pdfplumber` | Handles common table extraction cases with less risk |
| Ad-hoc dict schemas | Loose nested dict conventions | `Pydantic` models | Prevents silent schema drift across plans |

**Key insight:** Hand-rolling foundational PDF and schema infrastructure increases risk of missed requirements and non-deterministic outputs.

## Common Pitfalls

### Pitfall 1: Missing Requirement Candidates in Tables
**What goes wrong:** narrative extraction succeeds while table obligations are absent.
**Why it happens:** pipeline treats table parsing as optional.
**How to avoid:** make table extraction a first-class plan with dedicated fixture checks.
**Warning signs:** candidate count drops sharply on table-heavy documents.

### Pitfall 2: Overzealous Dedupe Removes Valid Signals
**What goes wrong:** repeated requirement statements across sections collapse too early.
**Why it happens:** text-similarity dedupe before provenance + typing.
**How to avoid:** link duplicates instead of dropping in Phase 1.
**Warning signs:** fewer candidates than obvious source statements.

### Pitfall 3: Weak Text-Layer Quality Not Surfaced
**What goes wrong:** tool appears successful but output is sparse/incorrect.
**Why it happens:** no diagnostics for missing/fragmented text layers.
**How to avoid:** implement page-level text-quality scoring and warnings.
**Warning signs:** pages with almost zero extracted text in otherwise dense PDFs.

## Code Examples

### Minimal Low-Text Quality Warning Pattern
```python
if page_text_char_count < config.min_chars_per_page:
    warnings.append({
        "code": "low_text_quality",
        "page": page_number,
        "chars": page_text_char_count,
    })
```

### Modal-Triggered Split Heuristic
```python
MODAL_SET = load_modal_verb_set(config_path)
for sentence in split_sentences(paragraph):
    if contains_modal_verb(sentence, MODAL_SET):
        emit_candidate(sentence)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Text-only paragraph scraping | Multi-channel extraction with table/caption handling | 2023-2026 tool ecosystem maturity | Higher requirement recall and traceability |
| Monolithic extraction output | Typed candidates + canonical schemas | Modern AI/data pipelines | Better debuggability and downstream transformation fidelity |

**Deprecated/outdated:**
- OCR-first for digital-text PDFs as default path.

## Open Questions

1. **Exact sentence splitter for engineering PDFs**
   - What we know: modal-triggered splitting is required.
   - What's unclear: best splitter for numbered clauses and semicolon-heavy specs.
   - Recommendation: start with deterministic regex/heuristics and add fixture-driven refinements.

2. **Default context window size around candidates**
   - What we know: bounded context is required.
   - What's unclear: ideal length balancing review utility vs payload size.
   - Recommendation: implement configurable bounds with conservative default.

## Validation Architecture

- **Fixture set A:** narrative-heavy PDF with known expected candidate counts.
- **Fixture set B:** table-heavy PDF where key requirements appear only in table cells.
- **Fixture set C:** mixed PDF with captions carrying obligation-adjacent text.
- **Acceptance checks:**
  - Every candidate has page-level origin metadata.
  - Warnings emitted for low-text pages in degraded fixtures.
  - Source-type distribution present (`narrative`, `table_cell`, `caption_context`).
  - No early candidate loss from dedupe in Phase 1.

## Sources

- https://pypi.org/project/pypdf/
- https://pypi.org/project/pdfplumber/
- https://pypi.org/project/pydantic/
- https://pypi.org/project/typer/

---
*Phase: 01-extraction-and-provenance-foundation*
*Research completed: 2026-02-26*
