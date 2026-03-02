# Research: Phase 09 - External AI Enrichment

Milestone: `v1.3.0`

## Objective
Enable optional, external LLM enrichment of extracted requirements while adhering to the core SpecForge pillars: **Provenance, Strict Schemas, and Validation as Data.**

## Key Questions
1. **Provenance Preservation:** How do we ensure an LLM-rewritten requirement doesn't lose its link to the original PDF page?
   - *Proposed Solution:* Use a `RefinedRequirement` model that points to the `OriginalRequirement` ID.
2. **Deterministic AI Boundaries:** How do we handle AI timeouts or hallucinations?
   - *Proposed Solution:* Treat AI failure as a `ValidationIssue` (e.g., `code: enrichment_failed`) rather than a pipeline crash.
3. **Data Privacy:** What metadata is safe to send to external APIs?
   - *Proposed Solution:* Send only the requirement text and ID; never send full PDF blocks or system-level metadata unless explicitly configured.

## Tooling Targets
- Gemini 1.5 Pro (Native multimodal support for diagram review later)
- OpenAI GPT-4o (Standard for logic refinement)
- Local LLMs (Ollama/LlamaCpp) for air-gapped environments.

## Proposed Contract
```python
class EnrichmentIssue(ValidationIssue):
    original_text: str
    refined_text: str
    rationale: str
```

---
*Research started: 2026-03-01*
