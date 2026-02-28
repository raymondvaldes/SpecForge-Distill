# Research: Phase 3 - Output Packaging and Interop Hooks

## Overview
Phase 3 focuses on transforming the internal `PipelineResult` into user-facing deliverables (Markdown) and machine-readable manifests (JSON). It also introduces lightweight hooks for future SysML v2 integration.

## Requirement Analysis

### OUT-03: Consolidated Markdown File
- **Goal**: One file containing everything from the PDF.
- **Structure**:
  - Title (from PDF name/metadata)
  - Extraction Warnings (if any)
  - Architecture Artifacts (Section headers + content)
  - Requirements (Grouped by section or page, with IDs and obligation labels)
  - Provenance (Citations inline or as footnotes)

### OUT-04: Split Markdown Package
- **Goal**: Separate files for different artifact types.
- **Files**:
  - `requirements.md`: All extracted and normalized requirements.
  - `architecture.md`: Narrative architecture blocks.
  - `tables_and_figures.md` (Optional/Bonus?): Or just include in architecture.
- **Benefits**: Easier to review specific content types in isolation.

### OUT-05: Manifest JSON
- **Goal**: Index all generated files and entities for downstream tools.
- **Schema Idea**:
  ```json
  {
    "manifest_version": "1.0",
    "source_pdf": "...",
    "generated_files": {
      "consolidated": "output.md",
      "requirements": "requirements.md",
      "architecture": "architecture.md"
    },
    "entities": {
      "requirements": [ { "id": "...", "path": "requirements.md#...", "page": 1 } ],
      "artifacts": [ { "id": "...", "path": "architecture.md#...", "page": 1 } ]
    }
  }
  ```

### CLI-01/CLI-02: Output Paths
- **Behavior**:
  - `distill spec.pdf` -> Creates `spec_distilled/` adjacent to `spec.pdf`.
  - `distill spec.pdf -o results/` -> Creates `results/`.
- **Implementation**: Use `pathlib` for robust path manipulation.

### RUN-01: Local-only Default
- **Status**: Currently local-only (using `pypdf`, `re`, `yaml`).
- **Action**: Ensure no accidental dependencies on external services. Add `--allow-external-ai` (or similar) placeholder flag if needed for future proofing.

### INT-01: SysML v2 Interop Hooks
- **Goal**: Add fields to `Requirement` and `ArtifactBlock` models.
- **Fields**:
  - `interop`: A new optional sub-model.
  - `target`: String (the system element).
  - `candidate_concept`: String (SysML concept).
  - `mapping_status`: Enum (e.g., `draft`, `mapped`, `reviewed`).

## Implementation Strategy

### 1. Rendering Engine
- **Module**: `src/specforge_distill/render/`
- **Classes**:
  - `MarkdownRenderer`: Template-based (or simple f-string) markdown generation.
  - `ManifestWriter`: JSON serialization with schema validation.

### 2. Model Updates
- Update `Requirement` in `src/specforge_distill/models/requirement.py` to include `interop` metadata.
- Update `ArtifactBlock` in `src/specforge_distill/models/artifacts.py` similarly.

### 3. CLI Updates
- Update `src/specforge_distill/cli.py` to handle default output paths and call the rendering engine.

### 4. Pipeline Updates
- `run_distill_pipeline` should return the `PipelineResult`, and the CLI (or a new `OutputOrchestrator`) should handle the file writing.

## Verification Plan
- **Unit Tests**:
  - Test individual renderers with mocked data.
  - Verify manifest JSON matches schema.
- **Acceptance Tests**:
  - Run full pipeline and check file existence/content.
  - Verify `-o` flag behavior.
  - Verify SysML v2 fields are present in JSON output.

## RAG-Readiness and Structural Chunking

To support downstream RAG (Retrieval-Augmented Generation) workflows, the output must be "chunk-friendly":

1. **Header-to-Header Slicing**: Markdown must use semantic headers (`#`, `##`) that clearly define context boundaries.
2. **Asset Isolation**: Tables and architecture blocks should be rendered as atomic units in the markdown to prevent them from being split across chunks by naive chunkers.
3. **Metadata Enrichment**: The `manifest.json` should provide enough context for a chunker to enrich individual chunks with:
   - Source document title and version.
   - Full hierarchical path (e.g., `Section 3 > Subsection 3.2 > ...`).
   - Explicit links between requirements and their referenced tables/figures.

## Output Structure

The tool will generate a directory containing the following:

```text
<output_dir>/
├── manifest.json          # Index of all entities and files
├── [source_name]_full.md  # Consolidated view
├── requirements.md        # Specialized view: Requirements only
└── architecture.md        # Specialized view: Architecture artifacts only
```

## Metadata Alignment

### INCOSE Quality Attributes
To align with INCOSE Guide for Writing Requirements (v4), the `Requirement` model should include slots for:
- **Priority**: High, Medium, Low (placeholder).
- **Risk**: Assessment of implementation risk (placeholder).
- **Rationale**: Why the requirement exists.
- **Verification Method**: (Already in Phase 2 VCRM).

### SysML v2 Interop Detail
The `interop` metadata block for entities will follow this structure:

```json
"interop": {
  "sysml_v2": {
    "target": null,
    "candidate_concept": null,
    "mapping_status": "unmapped"
  }
}
```
The `manifest.json` will include a `model_interop_target` field (defaulting to `sysmlv2-future`) to signal readiness for downstream model generators.
