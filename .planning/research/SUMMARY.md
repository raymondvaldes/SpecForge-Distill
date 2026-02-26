# Project Research Summary

**Project:** SpecForge Distill
**Domain:** AI-ready markdown distillation for systems-engineering specification PDFs
**Researched:** 2026-02-26
**Confidence:** MEDIUM-HIGH

## Executive Summary

SpecForge Distill should be built as a deterministic-first PDF distillation pipeline with provenance-first entity modeling. The highest-risk outcome for this domain is missing mandatory requirements; therefore, the architecture must prioritize recall of SHALL-class obligations (including mandatory equivalents) across paragraphs, tables, and figure/caption contexts.

The strongest v1 approach is a Python CLI stack that keeps extraction auditable and local-first: `pypdf + pdfplumber` for parsing/layout, Pydantic for canonical schema normalization, and template-based markdown rendering for consistent consolidated and split outputs. Optional AI enrichment can exist behind explicit flags for low-confidence cases only, preserving enterprise/offline defaults.

The main project risks are coverage blind spots (especially table/caption requirements), provenance drift, and unstable requirement IDs. Each has direct mitigations that should be built into phase success criteria rather than deferred.

## Key Findings

### Recommended Stack

Python-based CLI architecture aligns with your platform and local-first constraints while still allowing optional quality fallback. The stack should use deterministic extraction as the primary source of truth and treat AI as a controlled assistive layer.

**Core technologies:**
- Python 3.12.x: implementation baseline for macOS/Linux and enterprise packaging
- Typer 0.19.2: clear command UX (`distill <file.pdf> [-o ...]`)
- pypdf 6.1.0: core PDF parsing and object extraction
- pdfplumber 0.11.8: layout/table extraction to reduce missed requirements
- Pydantic 2.11.9: schema enforcement for artifact consistency

### Expected Features

The feature landscape is clear: table-stakes are all directly tied to trust and traceability.

**Must have (table stakes):**
- Digital-text PDF ingestion and parsing
- Structured extraction for requirements/architecture/CONOPS
- SHALL + mandatory-form detection with confidence flags
- Page-level provenance for every extracted entity
- Requirement extraction from tables and caption contexts
- Consolidated and split markdown output package + manifest

**Should have (competitive):**
- VCRM-rebuild-ready requirement attributes
- Deterministic + optional AI hybrid mode
- Explicit trace-link model (`req -> arch -> verification`)

**Defer (v2+):**
- OCR/scanned PDFs
- Mermaid generation from sequence diagrams
- Large-scale batch workflows

### Architecture Approach

Use a staged pipeline (`ingest -> extract -> normalize -> render`) with immutable intermediate representations and provenance attached at extraction time. This design supports both output forms from one canonical source, prevents drift, and makes validation/testing straightforward.

**Major components:**
1. Ingestion: PDF load, text-layer checks, page map
2. Extraction: sections, requirements, tables, figures/captions
3. Normalization: canonical entities + deterministic IDs
4. Provenance/Confidence: citation anchors + review-required flags
5. Renderer: consolidated markdown + split package + manifest

### Critical Pitfalls

1. **Missing table/caption obligations** — build dedicated extractors and fixture tests early.
2. **Obligation classifier drift** — use tiered lexical rules with confidence flags and regression tests.
3. **Provenance drift** — make citation metadata mandatory in every transformation.
4. **ID instability/collisions** — preserve source IDs and use deterministic generated IDs.
5. **Hidden online dependencies** — keep local/offline mode as default and explicit for cloud fallback.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Extraction & Provenance Foundation
**Rationale:** Trust depends first on accurate capture and traceability.  
**Delivers:** PDF ingest, section/table/caption extraction, base provenance model.  
**Addresses:** table-stakes around extraction coverage and citations.  
**Avoids:** missed table/caption requirements and provenance drift.

### Phase 2: Requirement Modeling & Obligation Detection
**Rationale:** Core value centers on not missing critical obligations.  
**Delivers:** requirement schema, ID strategy, SHALL/must/required classification, confidence flags.  
**Uses:** canonical models from Phase 1.  
**Implements:** deterministic requirement identity and review-required paths.

### Phase 3: Artifact Packaging & Output UX
**Rationale:** Product is only useful when outputs are consumable by humans and AI pipelines.  
**Delivers:** consolidated markdown, split artifact files, manifest index, sequence image/context capture.

### Phase 4: Verification Harness & v1 Readiness
**Rationale:** Adoption bar requires demonstrated recall and deterministic behavior.  
**Delivers:** fixture corpus tests, repeat-run stability checks, offline-mode verification, release hardening.

### Phase Ordering Rationale

- Extraction/provenance must precede requirement confidence work because all downstream trust depends on anchored source data.
- Requirement modeling must precede output packaging to avoid format churn and ID drift.
- Verification last ensures the full end-to-end pipeline meets recall and determinism standards before release.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** obligation detection tuning and false-positive controls for mandatory-language patterns.
- **Phase 4:** objective recall metrics and corpus design for requirement extraction quality.

Phases with standard patterns (skip research-phase):
- **Phase 1:** PDF ingest/extract/provenance layering is established.
- **Phase 3:** multi-file packaging/manifest patterns are straightforward once schema is stable.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Versions and ecosystem choices are clear and stable for v1 scope |
| Features | HIGH | User priorities align with domain table-stakes |
| Architecture | MEDIUM | Precise extractor boundaries may shift after real fixture analysis |
| Pitfalls | MEDIUM-HIGH | Known risk patterns are established for PDF extraction pipelines |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- Objective recall benchmark for SHALL-class detection needs a labeled fixture set.
- Exact VCRM attribute schema should be finalized during requirement definition.
- Sequence diagram capture heuristics (image+context window size) need empirical tuning.

## Sources

### Primary (HIGH confidence)
- https://pypi.org/project/pypdf/ — parser versions and compatibility
- https://pypi.org/project/pdfplumber/ — table/layout extraction context
- https://pypi.org/project/pydantic/ — schema modeling baseline
- https://pypi.org/project/typer/ — CLI baseline

### Secondary (MEDIUM confidence)
- https://pypi.org/project/docling/ — alternative conversion architecture
- https://pypi.org/project/unstructured/ — alternative ingestion architecture

### Tertiary (LOW confidence)
- https://www.incose.org/ — general requirements engineering context (specific extraction tactics still require empirical validation)

---
*Research completed: 2026-02-26*
*Ready for roadmap: yes*
