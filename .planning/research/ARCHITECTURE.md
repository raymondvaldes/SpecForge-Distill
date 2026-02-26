# Architecture Research

**Domain:** AI-ready markdown distillation from legacy systems-engineering PDFs
**Researched:** 2026-02-26
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Layer                             │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ distill cmd  │  │ config/env   │  │ run telemetry    │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘   │
│         │                 │                   │             │
├─────────┴─────────────────┴───────────────────┴─────────────┤
│                     Pipeline Orchestrator                     │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────┐ → ┌──────────────┐ → ┌──────────────────┐   │
│  │ Ingestion  │   │ Extraction   │   │ Normalization    │   │
│  └────────────┘   └──────────────┘   └──────────────────┘   │
│          │                 │                    │            │
│          └──────────────────────────────────────┼──────────┐ │
│                                                 ↓          │ │
│                                        ┌────────────────┐  │ │
│                                        │ Provenance DB  │  │ │
│                                        └────────────────┘  │ │
├─────────────────────────────────────────────────────────────┤
│                        Output Layer                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐  │
│  │ consolidated.md  │  │ split md files   │  │ manifest   │  │
│  └──────────────────┘  └──────────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Ingestion | Load PDF, detect text-layer quality, page map | pypdf + pdfplumber wrappers |
| Extractor | Pull raw sections, requirements, tables, figure context | rule-based parser + layout helpers |
| Normalizer | Convert extracted candidates into canonical schema | Pydantic models + deterministic transforms |
| Obligation Analyzer | Classify SHALL/must/required and confidence | lexical/rule engine + optional AI enrichment |
| Provenance Store | Record source page/span anchors for each entity | JSONL/manifest records keyed by entity IDs |
| Renderer | Emit consolidated and split markdown outputs | template renderer from canonical schema |

## Recommended Project Structure

```
src/specforge_distill/
├── cli/                    # Typer commands and argument handling
│   └── main.py
├── ingest/                 # PDF loaders and page utilities
│   ├── pypdf_loader.py
│   └── pdfplumber_tables.py
├── extract/                # Section, requirement, and artifact extraction
│   ├── sections.py
│   ├── requirements.py
│   ├── tables.py
│   └── figures.py
├── normalize/              # Canonical schema mapping and ID logic
│   ├── models.py
│   └── transform.py
├── provenance/             # Citation and anchor generation
│   └── citations.py
├── render/                 # Markdown and manifest emitters
│   ├── consolidated.py
│   ├── split_files.py
│   └── manifest.py
├── confidence/             # Ambiguity/low-confidence scoring and flags
│   └── scoring.py
└── tests/                  # Fixture-driven extraction tests
```

### Structure Rationale

- **extract/** is isolated from **normalize/** to avoid semantic drift from tightly coupled parsing/rendering logic.
- **provenance/** is its own boundary so every downstream output uses the same citation model.
- **confidence/** remains explicit so “review required” behavior is consistent across artifacts.

## Architectural Patterns

### Pattern 1: Deterministic-First, AI-Second

**What:** Always run deterministic extraction path first; optionally enrich/classify with local or external AI.
**When to use:** Enterprise/offline-first workflows that still need quality fallback paths.
**Trade-offs:** More engineering upfront, but stronger auditability and predictable behavior.

**Example:**
```python
candidates = deterministic_extract(page_blocks)
enriched = ai_enrich(candidates) if ai_enabled else candidates
```

### Pattern 2: Immutable Intermediate Representation

**What:** Persist normalized JSON artifacts before markdown rendering.
**When to use:** Any workflow with multiple output views (consolidated + split files).
**Trade-offs:** Extra storage I/O, but easier debugging and reproducibility.

**Example:**
```python
normalized = NormalizedDocument.model_validate(raw)
write_json(run_dir / "normalized.json", normalized.model_dump())
```

### Pattern 3: Provenance-First Entity Modeling

**What:** Every extracted entity carries page/source anchors at creation time.
**When to use:** Regulated or safety-critical document processing.
**Trade-offs:** Slightly heavier data structures, significantly better review and traceability.

## Data Flow

### Request Flow

```
[distill file.pdf]
    ↓
[Ingestion] → [Section/Table/Figure Extraction] → [Normalization]
    ↓                    ↓                            ↓
[Page map]         [Entity candidates]          [Canonical entities]
    └──────────────────────────────→ [Provenance linking]
                                      ↓
                               [Markdown rendering]
                                      ↓
                         [consolidated.md + split package + manifest]
```

### State Management

```
[run manifest]
    ↓
[entity store] ←→ [confidence flags] → [review-required list]
    ↓
[renderer outputs + trace index]
```

### Key Data Flows

1. **Requirement path:** raw paragraph/table cell -> candidate requirement -> obligation classification -> normalized requirement with citation.
2. **Diagram path:** figure object -> extracted image asset + surrounding text window -> split artifact references.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 1 PDF/run (v1 target) | Single-process pipeline with deterministic ordering |
| 5-20 PDFs | Add job queue + per-document worker concurrency |
| 100+ PDFs | Add distributed workers, artifact registry, and stronger observability |

### Scaling Priorities

1. **First bottleneck:** table/caption extraction latency — optimize by page-level selective parsing.
2. **Second bottleneck:** normalization/render throughput — cache intermediate representations and parallelize per-section rendering.

## Anti-Patterns

### Anti-Pattern 1: Parser-Renderer Coupling

**What people do:** Directly write markdown during extraction.
**Why it's wrong:** Hard to verify correctness or produce alternative outputs.
**Do this instead:** Normalize into schema first, render second.

### Anti-Pattern 2: Citation as Afterthought

**What people do:** Add provenance only in final output formatting.
**Why it's wrong:** Loses precise anchors and introduces mismatch bugs.
**Do this instead:** Attach provenance at candidate extraction time.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Optional external LLM API | Adapter with strict input/output schema | Disabled by default; only for low-confidence enrichment |
| Optional local model runtime | Same adapter contract as external | Supports offline enterprise execution |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| extract ↔ normalize | Typed entity DTOs | No renderer logic should leak into extraction |
| normalize ↔ render | Canonical model + manifest | Ensures consolidated/split consistency |
| normalize ↔ provenance | Entity ID + page anchor contract | Required for traceability correctness |

## Sources

- https://pypi.org/project/pypdf/ — parsing capabilities and compatibility
- https://pypi.org/project/pdfplumber/ — layout/table extraction context
- https://pypi.org/project/pydantic/ — schema validation model
- https://pypi.org/project/typer/ — CLI framework context
- https://pypi.org/project/docling/ — alternative architecture reference point
- https://pypi.org/project/unstructured/ — alternative architecture reference point

---
*Architecture research for: spec PDF distillation CLI*
*Researched: 2026-02-26*
