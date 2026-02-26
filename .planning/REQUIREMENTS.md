# Requirements: SpecForge Distill

**Defined:** 2026-02-26
**Core Value:** Transform legacy spec PDFs into structured, provenance-linked markdown without missing critical requirement obligations.

## v1 Requirements

### Ingestion

- [ ] **ING-01**: User can run `distill <file.pdf>` on a single digital-text PDF and start extraction.
- [ ] **ING-02**: User receives a warning when low text-layer quality is detected, including impacted pages.

### Requirements Extraction

- [ ] **REQ-01**: User gets requirement statements extracted from narrative text.
- [ ] **REQ-02**: User gets requirement statements extracted from tables and figure/caption contexts.
- [ ] **REQ-03**: Each extracted requirement is classified for obligation language (`shall`, `must`, `required`).
- [ ] **REQ-04**: Existing requirement IDs are preserved exactly when present in source.
- [ ] **REQ-05**: Deterministic canonical requirement IDs are generated when source IDs are absent.
- [ ] **REQ-06**: Ambiguous/low-confidence requirement candidates are included and flagged for review.

### Structured Artifacts

- [ ] **ART-01**: User gets architecture sections extracted into structured markdown blocks.
- [ ] **ART-02**: Requirement records capture VCRM-rebuild attributes when present (for example: verification method, success criteria, evidence reference, performing organization, phase).

### Provenance and Output

- [ ] **OUT-01**: All extracted requirements include page-level citations.
- [ ] **OUT-02**: All structured artifacts include page-level citations.
- [ ] **OUT-03**: Tool emits one consolidated markdown file per source PDF.
- [ ] **OUT-04**: Tool emits split markdown package files (for example: `requirements.md`, `architecture.md`).
- [ ] **OUT-05**: Tool emits `manifest.json` indexing generated files, entities, and citation references.

### CLI and Runtime

- [ ] **CLI-01**: Default output location is adjacent to source PDF when `-o` is not provided.
- [ ] **CLI-02**: User can override output location with `-o <dir>`.
- [ ] **CLI-03**: Re-running on unchanged input produces stable IDs and deterministic output ordering.
- [ ] **RUN-01**: Local-only processing is default; optional external AI usage is explicit opt-in.

### Interop Hooks

- [ ] **INT-01**: Canonical entities include lightweight SysML-v2-ready interop metadata hooks (`target`, `candidate concept`, `mapping status`) without generating SysML artifacts.

## v2 Requirements

### Extended Ingestion and Scale

- **ING-03**: User can process scanned/OCR PDFs with acceptable extraction quality.
- **CLI-04**: User can run folder/batch processing workflows.
- **PLAT-01**: User can run the CLI in Windows/PowerShell 7 environments.

### Additional Artifact Coverage

- **ART-03**: User gets CONOPS content extracted into structured sections.
- **ART-04**: User gets SysML-adjacent artifacts classified into richer typed outputs.
- **SEQ-01**: Sequence diagrams are converted into Mermaid when semantics are clear.

### Validation and Model Interop

- **VAL-01**: User can run requirement-quality checks/linting in a separate validation tool.
- **INT-02**: User can export or transform distilled outputs into SysML v2 textual/model artifacts.
- **INT-03**: User can integrate with Systems Modeling API services for repository workflows.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Scanned/OCR-heavy PDF support in v1 | Explicitly deferred to reduce complexity and protect extraction quality bar |
| Full requirement-quality scoring/lint engine in Distill v1 | Better architectural fit as a separate validation-focused tool |
| SysML v2 model generation/API integration in v1 | Deferred to v2; v1 includes only lightweight interop hooks |
| Large-scale batch orchestration in v1 | v1 focuses on reliable single-document processing |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ING-01 | TBD | Pending |
| ING-02 | TBD | Pending |
| REQ-01 | TBD | Pending |
| REQ-02 | TBD | Pending |
| REQ-03 | TBD | Pending |
| REQ-04 | TBD | Pending |
| REQ-05 | TBD | Pending |
| REQ-06 | TBD | Pending |
| ART-01 | TBD | Pending |
| ART-02 | TBD | Pending |
| OUT-01 | TBD | Pending |
| OUT-02 | TBD | Pending |
| OUT-03 | TBD | Pending |
| OUT-04 | TBD | Pending |
| OUT-05 | TBD | Pending |
| CLI-01 | TBD | Pending |
| CLI-02 | TBD | Pending |
| CLI-03 | TBD | Pending |
| RUN-01 | TBD | Pending |
| INT-01 | TBD | Pending |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 0
- Unmapped: 20 ⚠️

---
*Requirements defined: 2026-02-26*
*Last updated: 2026-02-26 after initial definition*
