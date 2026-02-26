# Pitfalls Research

**Domain:** AI-ready markdown distillation from legacy systems-engineering PDFs
**Researched:** 2026-02-26
**Confidence:** MEDIUM-HIGH

## Critical Pitfalls

### Pitfall 1: Missing Obligations Embedded in Tables/Captions

**What goes wrong:**
Parser catches narrative SHALL statements but misses mandatory statements in table rows, footnotes, or figure captions.

**Why it happens:**
Teams optimize for plain paragraph extraction and under-handle layout-specific structures.

**How to avoid:**
Implement dedicated table/caption extraction passes and include them in the same requirement candidate pipeline as paragraphs.

**Warning signs:**
Traceability review finds requirements with IDs in tables not present in output.

**Phase to address:**
Phase 1 (extraction foundation)

---

### Pitfall 2: Obligation Classifier Too Narrow or Too Broad

**What goes wrong:**
Strict `SHALL`-only rules miss valid mandatory forms; broad semantic rules over-classify non-requirements.

**Why it happens:**
No explicit obligation taxonomy and no confidence thresholding.

**How to avoid:**
Use tiered detection: lexical mandatory forms (`shall`, `must`, `required`) + confidence scoring + review flags.

**Warning signs:**
Large swings in requirement count after small rule changes.

**Phase to address:**
Phase 2 (requirement modeling and confidence)

---

### Pitfall 3: Provenance Drift During Normalization

**What goes wrong:**
Rendered markdown text cannot be traced back to exact PDF pages/anchors.

**Why it happens:**
Citation IDs are attached late or dropped during transformation.

**How to avoid:**
Provenance-first entity model; every transformation function must preserve/merge citation references.

**Warning signs:**
Entities appear in output with null/empty source metadata.

**Phase to address:**
Phase 1 and Phase 3 (schema + rendering contracts)

---

### Pitfall 4: Requirement ID Collisions and Instability

**What goes wrong:**
Generated IDs change between runs or collide with existing source IDs, breaking downstream trace links.

**Why it happens:**
Non-deterministic ID generation and weak namespace strategy.

**How to avoid:**
Preserve source IDs exactly when present; generate deterministic canonical IDs with stable hash/ordinal scheme when absent.

**Warning signs:**
Running distillation twice on unchanged input produces different IDs.

**Phase to address:**
Phase 2 (normalization and identity)

---

### Pitfall 5: “Local-Only” Promise Broken by Hidden Online Dependencies

**What goes wrong:**
Tool fails in restricted/offline environments due implicit cloud calls or runtime downloads.

**Why it happens:**
Dependencies pull assets/models lazily at runtime without explicit control.

**How to avoid:**
Make offline mode default, declare all external calls behind explicit flags, and test in no-network CI profile.

**Warning signs:**
First-run behavior differs dramatically between connected and disconnected hosts.

**Phase to address:**
Phase 0/1 (CLI and runtime configuration)

---

### Pitfall 6: Sequence Diagram Context Loss

**What goes wrong:**
Only image binaries are saved; explanatory text around diagrams is dropped, making artifacts hard to interpret.

**Why it happens:**
Figure extraction ignores neighboring text windows and caption anchors.

**How to avoid:**
Capture figure asset + caption + configurable nearby text window in the same artifact record.

**Warning signs:**
Reviewers cannot determine actor/flow meaning from extracted diagram artifacts.

**Phase to address:**
Phase 3 (artifact packaging)

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcoded regexes without fixtures | Fast start | Brittle detection across document styles | Only for throwaway spike, never for v1 release |
| Rendering directly from parser output | Fewer layers | Output drift and hard debugging | Never for production path |
| Skipping confidence metadata | Cleaner output | Review burden hidden, trust collapses | Never where recall is critical |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| External LLM fallback | Sending full doc without schema controls | Use chunked structured prompts and strict JSON schema validation |
| Local model runtime | Assuming same output quality across hosts | Calibrate confidence thresholds by model profile and keep deterministic baseline |
| CI in enterprise env | Tests depend on internet/model downloads | Build offline fixture tests and explicit network-required test markers |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Full-document repeated parsing per extractor | Slow runtimes per PDF | Parse once, share page objects across extraction passes | Usually noticeable by 200+ page specs |
| Large in-memory image payloads | High memory spikes/crashes | Stream image extraction to disk and reference by manifest path | Documents with many embedded diagrams |
| Overly expensive AI enrichment on all candidates | High latency/cost | Run enrichment only on low-confidence subsets | Any nontrivial document set |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Logging full requirement text with sensitive data | Data leakage in logs/CI artifacts | Redact content in logs; keep full text only in controlled outputs |
| Unsandboxed PDF processing on untrusted files | Potential parser exploit surface | Isolate parsing process and keep dependencies patched |
| Silent cloud fallback in restricted domains | Compliance breach | Require explicit opt-in for external API usage |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Ambiguous “success” output with no coverage hints | False confidence in extraction quality | Emit summary counts + low-confidence flags |
| Non-deterministic file naming | Hard to diff/review in engineering workflows | Use stable naming conventions and deterministic ordering |
| Hidden assumptions about requirement wording | Missed obligations in edge formats | Document detection rules and expose config |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Requirement extraction:** Often missing table/caption requirements — verify sampled source pages and IDs.
- [ ] **Provenance:** Often missing anchors for transformed text — verify every entity has page citation metadata.
- [ ] **ID strategy:** Often unstable generated IDs — verify repeat run produces identical canonical IDs.
- [ ] **Confidence flags:** Often omitted for ambiguous statements — verify low-confidence cases are surfaced for review.
- [ ] **Sequence artifacts:** Often image-only dumps — verify surrounding explanatory text is preserved.

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Missing table/caption requirements | MEDIUM | Add targeted extractors, reprocess affected PDFs, compare diff against prior outputs |
| Provenance drift | HIGH | Rebuild normalized entity store from raw extraction with strict provenance checks |
| ID instability | MEDIUM | Freeze ID algorithm, migrate with mapping table, regenerate manifests |
| Over/under-classification of obligations | MEDIUM | Tune lexical rules + thresholds using fixture regression suite |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Missing table/caption obligations | Phase 1 | Fixture PDFs with known table/caption SHALLs all extracted |
| Obligation classifier drift | Phase 2 | Precision/recall checks on curated requirement corpus |
| Provenance drift | Phase 1 + 3 | Every emitted entity links to page citations |
| ID instability | Phase 2 | Repeat-run determinism test passes |
| Sequence context loss | Phase 3 | Diagram artifacts include image + explanatory text window |

## Sources

- https://pypi.org/project/pdfplumber/ — table/layout extraction limitations and expectations
- https://pypi.org/project/pypdf/ — parser behavior context
- https://pypi.org/project/unstructured/ — ingestion tradeoffs in broader pipelines
- https://pypi.org/project/docling/ — conversion pipeline tradeoffs in alternative stack

---
*Pitfalls research for: spec PDF distillation CLI*
*Researched: 2026-02-26*
