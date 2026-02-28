# SpecForge Distill (v1.0.1)

Transform legacy specification PDFs into structured, provenance-linked, AI-ready Markdown.

SpecForge Distill is a deterministic extraction engine designed for systems engineering workflows. It specializes in converting complex engineering documents into a machine-readable "Distilled Specification Package" that preserves high-fidelity citations and requirement obligations.

## 🚀 Quick Start (No Python Required)

The simplest way to use SpecForge Distill is to download the standalone executable for your platform from the [GitHub Releases](https://github.com/raymondvaldes/SpecForge-Distill/releases) page. These binaries are self-contained and do not require Python or any dependencies to be installed.

### macOS / Linux
```bash
# 1. Download the binary (e.g., distill-macos)
# 2. Make it executable
chmod +x distill-macos

# 3. Run it
./distill-macos path/to/spec.pdf
```

### Windows
```powershell
# 1. Download distill-windows.exe
# 2. Run it in Terminal
.\distill-windows.exe path/to/spec.pdf
```

---

## 🛠 Other Ways to Run

### 1. No-Install Script (Recommended for development)
If you have the source code but don’t want to "install" the package, use the provided `distill` wrapper script in the project root. It handles all pathing and dependency checks automatically.

```bash
./distill path/to/spec.pdf
```

### 2. Docker
Run SpecForge Distill in a completely isolated environment without touching your host system.

```bash
docker build -t distill .
docker run --rm -v "$(pwd):/data" distill /data/your-spec.pdf
```

### 3. Standard Python Install
Best for developers who want to integrate SpecForge Distill into other Python projects.

```bash
# Requires Python 3.10+
pip install .
distill path/to/spec.pdf
```

---

## Key Capabilities

- **High-Fidelity Extraction**: Captures narrative text, tables, and captions with 100% page-level provenance.
- **Requirement Modeling**: Automatically identifies obligations (Shall, Must, Should, May), preserves existing IDs, and detects ambiguity patterns.
- **RAG-Ready Outputs**: Produces semantic Markdown and a canonical JSON manifest optimized for LLM ingestion and MBSE toolchains.
- **SysML v2 Hooks**: Includes lightweight interop metadata for future integration with model-based engineering environments.
- **Deterministic & Local**: Guarantees identical output for identical input; runs 100% locally by default to protect sensitive engineering data.

## Output Structure

The tool generates a directory containing:
- `manifest.json`: Machine-readable index of all entities and files (SysML v2 ready).
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
