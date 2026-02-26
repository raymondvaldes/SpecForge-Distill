# SpecForge Distill

## What This Is

SpecForge Distill is a command line utility for internal systems engineering and MBSE teams to convert legacy specification PDFs into AI-ready markdown artifacts. It preserves source grounding through page-level citations while producing structured outputs that can be consumed by humans and downstream AI workflows. The v1 focus is single-document distillation with high recall on requirement obligations, especially SHALL-class statements.

## Core Value

Transform legacy spec PDFs into structured, provenance-linked markdown without missing critical requirement obligations.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Convert a digital-text PDF into both a consolidated markdown file and a split markdown package (requirements, architecture, CONOPS, and related artifacts when present).
- [ ] Extract and normalize requirement data with original IDs preserved when present and generated canonical IDs when absent.
- [ ] Preserve page-level provenance for extracted content so each structured output can be traced back to source PDF locations.
- [ ] Capture SHALL and equivalent mandatory statements (`must`, `required`) with review flags for low-confidence/ambiguous extractions.
- [ ] Extract requirements found in tables and figure/caption contexts, and capture sequence diagram images with surrounding explanatory text.

### Out of Scope

- Scanned/OCR-heavy PDFs — deferred to later milestone to avoid v1 OCR complexity.
- Mermaid sequence diagram generation — deferred to v2 (v1 captures images/text context only).
- Folder-scale batch processing (5+ docs) — deferred; v1 targets single-PDF runs.
- Full quality/completeness reporting dashboards — planned for phase 2 after core extraction quality is proven.

## Context

This project is a bridge utility to bring legacy systems documentation into modern AI workflows. Source documents include requirements, architecture, CONOPS, sequence diagrams, VCRM-relevant requirement attributes, and SysML-adjacent artifacts embedded in PDFs. The primary adoption risk is missing requirement obligations; trust depends on high extraction recall, especially for SHALL-class language. The broader SpecForge product family vision positions Distill as the distillation stage that prepares canonical markdown inputs for downstream tooling.

## Constraints

- **Input Scope**: PDF only (digital text first) — Reduce ingestion variability for v1 quality.
- **Primary Users**: Internal systems engineering / MBSE team — Optimize for technical workflows over general-public UX.
- **Runtime Preference**: Local-first processing, enterprise/offline friendly — Minimize data exposure and fit restricted environments.
- **Quality Flexibility**: External AI APIs allowed if required to meet extraction quality — Quality bar takes precedence when local-only methods are insufficient.
- **Platform**: macOS + Linux for v1 — Align with current team environments, defer PowerShell/Windows support.
- **Execution Scale**: Single PDF per run — Keep first release focused and reliable.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Prioritize structured extraction and provenance for v1 | These are the critical bridge capabilities for AI-ready outputs | — Pending |
| Use page-level citations as provenance granularity | Gives practical traceability without excessive overhead | — Pending |
| Output both consolidated and split markdown artifacts | Supports both human review and machine-ingestion workflows | — Pending |
| Preserve original requirement IDs, generate IDs when missing | Maintains legacy traceability while ensuring complete structure | — Pending |
| Include low-confidence flags instead of silent drops | Avoids hidden misses and supports human-in-the-loop quality control | — Pending |
| Defer Mermaid conversion to v2, capture sequence diagram images/text in v1 | Keeps v1 scope manageable while preserving diagram context | — Pending |

---
*Last updated: 2026-02-26 after initialization*
