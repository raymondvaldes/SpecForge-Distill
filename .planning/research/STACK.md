# Stack Research

**Domain:** AI-ready markdown distillation from legacy systems-engineering PDFs
**Researched:** 2026-02-26
**Confidence:** MEDIUM-HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.12.x | Primary implementation language for CLI and extraction pipeline | Strong PDF/NLP ecosystem, excellent CLI tooling, and straightforward local/offline deployment for enterprise environments |
| Typer | 0.19.2 | CLI interface (`distill <file.pdf>`) | Modern typed CLI ergonomics on top of Click, fast to ship and maintain |
| pypdf | 6.1.0 | PDF parsing, text/object/image access, metadata access | Pure-Python, permissive-license baseline for deterministic extraction and provenance capture |
| pdfplumber | 0.11.8 | Table-aware and layout-aware text extraction | Strong tabular extraction support, critical for requirements embedded in tables |
| Pydantic | 2.11.9 | Canonical schema for requirements/artifacts/trace metadata | Reliable validation for normalized outputs and manifest consistency |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| PyYAML | 6.0.x | YAML frontmatter generation/reading | Required for metadata-rich markdown artifacts |
| Jinja2 | 3.1.x | Deterministic markdown rendering templates | Useful for stable output formatting across consolidated and split files |
| RapidFuzz | 3.x | ID normalization and fuzzy matching for near-duplicate labels | Helpful when source PDFs have inconsistent identifier formatting |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| pytest (8.4.2) | Unit/integration tests for parser pipeline | Build fixture corpus with known SHALL/table/caption cases |
| Ruff (0.13.2) | Linting/formatting | Fast checks suitable for CI and local dev loops |
| pre-commit | Enforce checks pre-commit | Keep deterministic output rules and schema checks from drifting |

## Installation

```bash
# Core
pip install "typer==0.19.2" "pypdf==6.1.0" "pdfplumber==0.11.8" "pydantic==2.11.9"

# Supporting
pip install "PyYAML>=6.0,<7" "Jinja2>=3.1,<4" "RapidFuzz>=3,<4"

# Dev dependencies
pip install "pytest==8.4.2" "ruff==0.13.2" pre-commit
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| pypdf + pdfplumber | Docling (2.54.0) | Use when layout reconstruction quality is more important than minimal dependency footprint |
| pypdf + pdfplumber | Unstructured (0.18.15) | Use when you need broad document-type parity later (DOCX/HTML/etc.), not just PDF-first v1 |
| Typer | Click directly | Use if you need very custom low-level CLI behavior and want to avoid Typer abstractions |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| OCR-first pipeline for digital-text PDFs | Increases error surface and can degrade exact requirement wording | Text-layer-first extraction, add OCR only as explicit v2 fallback |
| “LLM-only” extraction without deterministic pass | Hard to guarantee recall on SHALL-class obligations and table requirements | Deterministic extraction first, AI-assisted enrichment/normalization second |
| AGPL/commercially constrained PDF libs as hard dependency | Can complicate enterprise/compliance rollout | Keep permissive-license core stack; isolate optional constrained dependencies behind adapters |

## Stack Patterns by Variant

**If strict local-only enterprise deployment:**
- Use deterministic extraction + rules + confidence scoring
- Keep AI assist optional via local models (adapter boundary), never mandatory for v1

**If quality threshold cannot be met locally for edge cases:**
- Enable optional external AI enrichment behind a feature flag
- Preserve deterministic provenance and confidence flags so outputs remain auditable

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| typer@0.19.2 | click@8.x | Typer is built on Click; pin both in lockfile for reproducible CLI behavior |
| pydantic@2.11.x | Python 3.9+ | Works with chosen Python 3.12 baseline |
| pypdf@6.1.0 | Python 3.9+ | Aligns with local-first baseline and pure-Python packaging |

## Sources

- https://pypi.org/project/pypdf/ — latest release and Python compatibility
- https://pypi.org/project/pdfplumber/ — release history and table extraction project details
- https://pypi.org/project/pydantic/ — latest release and validation framework details
- https://pypi.org/project/typer/ — CLI framework release/version details
- https://pypi.org/project/docling/ — alternative document-conversion stack
- https://pypi.org/project/unstructured/ — alternative unstructured ingestion stack
- https://pypi.org/project/pytest/ — test framework version details
- https://pypi.org/project/ruff/ — linter/formatter version details
- https://pymupdf.readthedocs.io/en/latest/ — licensing model notes for optional dependency decisions

---
*Stack research for: spec PDF distillation CLI*
*Researched: 2026-02-26*
