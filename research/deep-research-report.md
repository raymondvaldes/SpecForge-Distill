# SpecForge-Distill Deep Research Report

SpecForge-Distill’s core challenge is to turn heterogeneous, human-authored specifications (PDF/Word/Markdown) into a **canonical, deterministic intermediate representation** that preserves structure, identifiers, and traceability well enough for downstream AI retrieval and reasoning—*without* embedding probabilistic “AI inference” in the compilation path. This puts it closer to a **standards-informed document compiler** than a typical “LLM document understanding” pipeline. citeturn0search3turn0search11turn12view0turn7view1

A practical way to research and design SpecForge-Distill is to borrow proven concepts from: (a) requirements interchange standards (ReqIF / OSLC), (b) deterministic build and canonicalization work (reproducible builds, canonical JSON/XML), and (c) modern RAG chunking and retrieval ergonomics—while treating PDF/Word parsing limitations as first-class constraints. citeturn13view1turn0search1turn2search0turn2search1turn0search3turn8search0turn8search16

## Problem framing and product boundaries

SpecForge-Distill is positioned as an “open core compiler” that outputs a **stable SpecIR** plus **RAG-optimized chunks**. The most consequential boundary in the spec is that the *core layer* is deterministic and does **not** rely on embedded AI inference, meaning any heuristic must be rule-based and reproducible (e.g., explicit parsing, configurable regex/pattern rules, schema validation), and the output must be stable under identical inputs and toolchain versions. citeturn0search3turn2search0turn1search3

This boundary matters because many “document-to-structured” tools explicitly emphasize higher-level layout detection, reading-order reconstruction, OCR, and other capabilities that are often ML-driven (and therefore probabilistic unless very tightly controlled). For example, **GROBID** is explicitly a machine-learning library that restructures PDFs into TEI XML, and **Docling** markets table/formula/reading-order detection and OCR; these are useful references for the *problem space*, but they illustrate the kind of inference SpecForge-Distill’s core aims to avoid. citeturn2search3turn2search7turn9search1turn9search9turn9search5

A complementary reference point is the ecosystem around “RAG-ready ingestion,” where open-source tooling like Unstructured emphasizes pre-processing diverse formats into structured “elements” specifically to optimize LLM workflows. This validates market pull for “canonical document structuring,” but also highlights that many pipelines bias toward *best-effort* extraction rather than strict determinism. citeturn9search0turn9search4turn9search8

## Standards and ecosystem patterns worth borrowing

Two mature interoperability anchors in requirements engineering are **ReqIF** and **OSLC Requirements Management**.

ReqIF is maintained by entity["organization","Object Management Group","standards consortium"] as a formal specification intended for standards-based exchange of requirements between tools. citeturn0search0turn0search12  
The ReqIF 1.0.1 spec is particularly relevant because it encodes several data-model ideas that map cleanly onto a “SpecIR” concept:

- The “core content” model separates **SpecObject** (requirement), **Specification** (container), **SpecRelation** (trace link), plus types and data types. citeturn13view1turn12view0  
- Information elements are identified through **global unique identifiers**, and the spec explicitly discusses use of **AlternativeID** when tools cannot preserve original identifiers—this is directly analogous to SpecForge-Distill’s requirement to preserve originals while producing canonical identifiers. citeturn13view1turn12view0  
- ReqIF models hierarchical structure using **SpecHierarchy** and expresses requirement relations via **SpecRelation** between two SpecObjects (source/target), optionally grouped by the related specifications. citeturn13view4turn12view0  
- ReqIF includes a formatted-content datatype (XHTML-based) that can reference external objects such as pictures, which is a useful precedent for “figure extraction + reference linking.” citeturn12view0

OSLC RM, published under the entity["organization","OASIS Open","standards consortium"] OSLC Open Project, is equally important as an integration target: it defines HTTP RESTful interfaces for managing Requirements and related resources and is explicitly about tool interoperability rather than imposing a single native data model. citeturn0search1turn10search7  
OSLC also standardizes a vocabulary and resource shapes: the RM vocabulary is intended to support common integration scenarios and the resource shapes describe expected RDF triples and constraints. citeturn10search7turn10search27turn10search3

A third “semantic anchor” is how traceability is described in systems engineering guidance. The entity["organization","NASA","us space agency"] Systems Engineering Handbook defines “traceability” and “bidirectional traceability,” and describes requirements management activities that include conducting expectations/requirements traceability and recording traceability (often via a matrix or a requirements tool). citeturn7view1turn7view3turn6view0  
This is valuable because it frames traceability not just as a link graph, but as part of a lifecycle discipline where each requirement should trace to a parent/source requirement (or be explicitly “self-derived”), and “gold plating” is treated as a traceability smell. citeturn7view3turn6view0

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["ReqIF SpecObject SpecRelation SpecHierarchy diagram","OSLC Requirements Management specification diagram","requirements traceability matrix example"],"num_per_query":1}

## Input formats: what extraction can and cannot promise

A deterministic SpecIR must begin with an honest “capability envelope” for each input type.

PDF is standardized as ISO 32000 and is fundamentally a fixed-layout, device-independent representation; entity["company","Adobe","software company"] describes PDF as relying on the same imaging model as the PostScript page description language. citeturn11search1turn11search9turn11search6  
In practice, many PDFs do not carry reliable semantic structure: a common extraction reality is that PDF stores glyphs positioned by coordinates rather than a “logical reading order,” forcing parsers to infer ordering from layout. citeturn1search22turn1search30turn9search29  
This is why layout-aware extraction remains an active research area for text mining and NLP from PDFs. citeturn1search30

Security and adversarial robustness also matter for enterprise-safe ingestion. Recent research shows that “standard-compliant” PDF features can be abused so that **parsed content differs from what is visually rendered**, including via font-level glyph remapping; this is directly relevant to any pipeline trusting text extraction for compliance or safety-critical requirements. citeturn1search2  
PDF also supports embedded file streams and attachments (and related structures), which implies that a secure ingestion pipeline should treat PDFs as potentially containing additional payloads, not merely “flat text + images.” citeturn11search16turn0search31

Word “.docx” files (and related formats) are typically entity["company","Microsoft","software company"] Office Open XML packages: the OOXML standards family (ECMA-376) defines vocabularies and packaging for these formats, and public format descriptions emphasize that OOXML documents are ZIP-packaged collections of XML parts and resources. citeturn1search1turn1search17turn1search21  
From a SpecForge-Distill standpoint, this is good news: Word docs often preserve explicit structure (headings, lists, tables) more reliably than PDFs because the underlying representation is semantic XML rather than a page-description stream. citeturn1search1turn1search17

Markdown has historically been ambiguous across implementations, but CommonMark provides an unambiguous specification and accompanying test suite intended to standardize parsing behavior across engines—exactly the kind of determinism SpecForge-Distill wants at the “front end.” citeturn1search3turn1search15turn1search11

## Deterministic ingestion toolchain options

A deterministic compiler needs **version-pinned, well-scoped parsers** with predictable outputs under configuration. Several widely used building blocks are relevant (even if SpecForge-Distill later replaces components for tighter control).

entity["organization","Apache Tika","content analysis toolkit"] is a content analysis toolkit that detects and extracts metadata and text from a very large number of file types via a single interface, and is widely positioned for search indexing and content analysis use cases. citeturn0search2turn0search10  
For PDFs specifically, Tika’s PDFParser documentation indicates it can process encrypted PDFs (including attempting an empty password) and can extract embedded documents via an EmbeddedDocumentExtractor—useful capabilities for a robust ingestion stage. citeturn0search31

Pandoc is positioned as a “universal document converter” and explicitly supports conversion between word-processing formats (including docx) and multiple Markdown variants. This is relevant both for normalization (docx→markdown-like AST) and for reproducible transformations if versions and flags are pinned. citeturn3search0turn3search3

The existence of more ML-forward document processors is still strategically relevant even if the core avoids them, because they define user expectations and competitive benchmarks. Unstructured explicitly frames itself around ingesting/pre-processing PDFs and Word documents into structured elements optimized for LLM workflows, and IBM Research describes Docling as an open-source toolkit to convert PDFs/manuals/slide decks into specialized data for enterprise generative AI grounding. citeturn9search4turn9search0turn9search9turn9search5  
These systems indicate that the “canonical IR + chunking” concept is broadly validated, but SpecForge-Distill’s differentiation hinges on determinism, auditability, and enterprise-safe reproducibility rather than “best-effort ML understanding.” citeturn9search4turn9search9turn0search3

## Figures and tables: extraction and reference linking

SpecForge-Distill’s requirement to “extract figures and tables with reference linking” is a major complexity jump because figures/tables are where PDF and Word diverge most sharply.

For PDFs, one reliable strategy is to extract images from the PDF object model rather than rendering pages. Tools like **pdfimages** (part of poppler-utils) are explicitly intended as “PDF image extractor” utilities. citeturn3search30turn3search10  
Similarly, PyMuPDF documents basic APIs to iterate through pages, enumerate images, and extract image binaries (e.g., Page.get_images() and doc.extract_image(xref)), which is compatible with a deterministic extraction approach as long as tool versions are frozen. citeturn3search15turn3search11

Tables in PDFs are the archetypal “hard case” because many PDFs do not encode table semantics; table extractors must infer structure from ruling lines (“lattice”) or whitespace/alignment (“stream”). Camelot’s documentation makes this explicit by exposing multiple parsing flavors (lattice/stream and others in newer docs), which is a useful conceptual model for how a deterministic pipeline can offer multiple extraction passes while keeping outputs reproducible. citeturn3search5turn3search20turn3search8

Reference linking (e.g., “see Figure 6.2‑1”) typically requires: (a) capturing figure/table identifiers and captions, (b) binding them to extracted assets, and (c) detecting in-text references. ReqIF provides a precedent that formatted content can reference external objects like pictures and that relations/structure are first-class. citeturn12view0turn13view4  
A pragmatic deterministic approach is to implement reference linking as a strict rule system over extracted text (caption patterns, label normalization, and explicit anchors), rather than an inference model that “guesses” semantic references. citeturn12view0turn7view3

## SpecIR and traceability semantics

A high-value research conclusion is that SpecIR will be strongest if it is designed less like “a cleaned-up text dump” and more like an explicit **graph + hierarchy model** with strong provenance—similar in spirit to ReqIF’s separation of objects, hierarchy, and relations.

ReqIF’s model provides several directly portable design patterns:

- **Requirement objects are individually identifiable** (SpecObject) and appear within a **container** (Specification). citeturn12view0turn13view4  
- **Hierarchy is explicit** (SpecHierarchy), not an emergent property of indentation, which is essential for reproducible structure. citeturn13view4  
- **Traceability is explicit** as relations between requirements (SpecRelation source/target), and relations can be grouped by source/target specifications. citeturn13view4turn12view0  
- The spec explicitly anticipates identifier incompatibilities and allows **AlternativeID** as a complementary identifier—highly relevant to “normalize and canonicalize requirement identifiers” while preserving originals. citeturn13view1turn12view0

OSLC RM provides parallel patterns that matter for enterprise integrations:

- Requirements and collections are managed via standardized RESTful interfaces. citeturn0search1  
- The RM vocabulary is designed for interoperability scenarios and may not match native tool schemas exactly, which suggests SpecIR should include enough metadata to map to multiple downstream representations (ALM tools, knowledge graphs, etc.). citeturn10search7  
- Resource Shapes and the OSLC Core resource shape vocabulary provide a precedent for schema/shape-driven validation of linked data resources. citeturn10search27turn10search3

Traceability semantics should also incorporate the “lifecycle” notion from NASA guidance: traceability is an association among entities (requirements, system elements, verification, tasks), and bidirectional traceability means being able to trace to parents and allocated children. NASA also explicitly describes recording bidirectional traceability and tracing each requirement back to a parent/source or identifying it as self-derived (and treating untraceable requirements as potential “gold plating”). citeturn7view1turn7view3turn6view0

A SpecIR that is optimized for AI ingestion and retrieval should therefore likely encode at least:

- A **deterministic document tree** (sections, subsections, paragraphs, lists), where each node has stable provenance (file hash + page + offsets) and stable ordering.
- A **requirements layer** (explicit “requirement” nodes) that can either be detected from explicit numbering/formatting rules (deterministic) or imported from existing IDs (ReqIF/OSLC exports).
- A **relationship graph** (trace, reference, contains, defines, etc.) grounded in explicit evidence such as hyperlinks, cross-references, or requirement link tables. citeturn13view4turn7view3turn0search1

## RAG-optimized outputs and chunking

The research literature around Retrieval-Augmented Generation (RAG) establishes why retrieval-friendly chunking matters: RAG explicitly combines parametric generation with access to an external indexed corpus, and the quality of retrieval units influences factuality, provenance, and answer precision. citeturn8search0turn8search3  
Dense retrieval approaches like DPR show that a learned retriever over passages can significantly outperform sparse baselines for top-k retrieval accuracy in open-domain QA settings, reinforcing that “what counts as a passage” (chunk granularity and coherence) is an important design parameter. citeturn8search1turn8search4  
At the infrastructure layer, approximate nearest neighbor methods like HNSW are a widely cited approach for efficient similarity search in high-dimensional vector spaces, which is consistent with how many vector indexes are implemented. citeturn8search2turn8search8

For a deterministic compiler, the actionable research is less “which embedding model” and more “how to produce stable, queryable chunks with strong anchors.” Vendor and practice guidance emphasizes chunking as the process of breaking large documents into manageable segments for retrieval, and warns that poor chunking harms retrieval relevance and downstream response quality. citeturn8search16turn8search37

Implications for SpecForge-Distill’s chunk output design:

- Chunk boundaries should be **structure-aware** (section headings, requirement blocks, table/figure captions) rather than purely token-count-based, because structure-aware boundaries are more stable under small edits and preserve semantic neighborhoods. citeturn1search3turn7view3turn8search16  
- Each chunk should preserve **bidirectional anchors**: (a) a pointer back to the canonical SpecIR node(s), and (b) forward pointers to related nodes (e.g., trace links, referenced figures/tables). This directly aligns with the bidirectional traceability concept and with ReqIF’s explicit relations/hierarchy. citeturn7view1turn13view4turn12view0  
- Chunk metadata should include stable provenance fields (source id, page references for PDFs, section path for Word/Markdown), enabling downstream systems to cite and render context—an important motivation in RAG research for provenance and updateability. citeturn8search0turn7view3

Finally, it is strategically important that many public “parse PDF for RAG” examples explicitly use multimodal LLMs to interpret layout (which can work well but is non-deterministic). SpecForge-Distill can treat these as inspiration for optional non-core layers, while keeping the core compilation path deterministic. citeturn9search26turn1search2turn0search3

## Licensing and open-core strategy

SpecForge-Distill’s target license for the open core is Apache 2.0, which is a permissive license with explicit terms and conditions for redistribution; the canonical text is published by the entity["organization","Apache Software Foundation","open source foundation"]. citeturn1search0turn10search17  
The Apache License also specifies how NOTICE attributions must be handled when redistributing derivative works that include a NOTICE file, and ASF guidance provides concrete distribution practices for assembling LICENSE and NOTICE files. citeturn10search17turn10search1turn1search28  
Apache 2.0’s patent provisions and defensive termination are widely cited as key “enterprise-safe” characteristics of the license compared to simpler permissive licenses. citeturn1search0turn1search24turn1search4

On “open core” as a go-to-market model, multiple definitions converge on the idea of an open-source core paired with proprietary add-ons/premium features; this is commonly treated as a hybrid commercialization model and is sometimes controversial in open-source communities. citeturn10search0turn10search12turn10search4turn10search8  
For SpecForge-Distill, the research implication is architectural: keep the deterministic compiler and SpecIR schema open under Apache 2.0, while monetizable enterprise features naturally cluster around deployment, compliance, integrations (e.g., packaged connectors to ALM tools), governance, and operational controls—capabilities that OSLC/ReqIF ecosystems show are valuable in practice. citeturn0search1turn9search2turn10search22turn10search3