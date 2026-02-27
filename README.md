# SpecForge Distill (v1.0.0)

Transform legacy specification PDFs into structured, provenance-linked, AI-ready Markdown.

SpecForge Distill is a deterministic extraction engine designed for systems engineering workflows. It specializes in converting complex engineering documents into a machine-readable "Distilled Specification Package" that preserves high-fidelity citations and requirement obligations.

## Key Capabilities

- **High-Fidelity Extraction**: Captures narrative text, tables, and captions with 100% page-level provenance.
- **Requirement Modeling**: Automatically identifies obligations (Shall, Must, Should), preserves existing IDs, and detects ambiguity patterns.
- **RAG-Ready Outputs**: Produces semantic Markdown and a canonical JSON manifest optimized for LLM ingestion and MBSE toolchains.
- **SysML v2 Hooks**: Includes lightweight interop metadata for future integration with model-based engineering environments.
- **Deterministic & Local**: Guarantees identical output for identical input; runs 100% locally by default to protect sensitive engineering data.

## Installation

```bash
# Requires Python 3.10+
pip install -e .
```

## Quick Start

```bash
# Distill a specification PDF
distill path/to/spec.pdf

# Specify a custom output directory
distill path/to/spec.pdf -o results/
```

## Output Structure

The tool generates a directory containing:
- `manifest.json`: Machine-readable index of all entities and files.
- `full.md`: Consolidated Markdown view of the entire document.
- `requirements.md`: Focused view containing only extracted and normalized requirements.
- `architecture.md`: Focused view of narrative architecture and artifact blocks.

## Status: v1.0.0 Stable

SpecForge Distill has completed its initial development roadmap and is verified for digital-text PDF distillation.

### Constraints & Out-of-Scope (v1)
- **Scanned PDFs**: Not supported in v1.0.0 (deferred to v2).
- **Complex Graphics**: Diagram-to-Mermaid conversion is currently out of scope.
- **Multi-file Batching**: v1 focuses on reliable single-document processing.

---
*Developed for systems engineering rigor and AI-augmented reliability.*
