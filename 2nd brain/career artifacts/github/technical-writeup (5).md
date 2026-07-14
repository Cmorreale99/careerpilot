# MassDEP — Document Intelligence & Power BI Analytics System

## Overview

For MassDEP, I worked on a team building an NLP-based document intelligence and analytics system designed to convert unstructured environmental construction reports into structured, validated, Power BI-ready datasets.

MassDEP receives construction report forms from third-party companies managing soil reclamation sites. These reports contain critical information such as PFAS metrics, shipment quantities, soil quality indicators, inspection data, site conditions, and project-level details, but the formats are inconsistent, often lengthy, and difficult to analyze manually.

The system combined PDF preprocessing, semantic retrieval, retrieval-augmented generation, hybrid named entity recognition, entity validation, hallucination detection, backend orchestration, and Microsoft Power BI dashboard integration. The final workflow connected an NLP backend to a Power BI analytics frontend, giving stakeholders interactive dashboards and visual reports derived from processed environmental document data.

The result was an end-to-end workflow:

**Unstructured environmental reports → semantic chunks → grounded extraction → validated structured outputs → Power BI dashboards → stakeholder reporting**

---

## System Overview

<img width="750" height="500" alt="architecture" src="../assets/images/massdep_architecture.png" />

*Built a document intelligence and analytics pipeline that converts unstructured environmental reports into validated structured outputs, exports them into Power BI-ready datasets, and enables stakeholder-facing dashboards for environmental reporting workflows.*

---

## Technical Problem

MassDEP’s reporting workflow depended on unstandardized construction report forms submitted by third-party companies. These documents varied widely in structure, formatting, terminology, and quality.

Some reports contained chemical concentrations as explicit key-value pairs. Others buried important values in long paragraphs. Some documents included scanned or OCR-affected content, inconsistent formatting, and domain-specific environmental terminology.

The core problem was not simply extracting text from PDFs. The challenge was transforming inconsistent, unstructured environmental reports into structured, validated datasets that could support repeatable Power BI reporting.

MassDEP needed a system that could:

* Parse and standardize inconsistent PDF report formats
* Extract critical environmental fields such as PFAS metrics, shipment quantities, site conditions, inspection details, and project identifiers
* Preserve traceability back to the original source material
* Reduce hallucination risk in LLM-generated outputs
* Surface unreadable pages, missing values, and validation failures
* Convert extracted fields into analytics-ready tabular outputs
* Load structured outputs into Power BI for dashboarding, inspection, and stakeholder reporting

Without this pipeline, MassDEP staff were left with manual document review rather than a scalable reporting layer.

---

## Environment & Constraints

* **Source Documents:** Unstructured environmental construction reports submitted to MassDEP
* **Document Formats:** PDFs, scanned reports, inconsistent forms, long-form text, OCR-affected content
* **Domain:** Soil reclamation, environmental compliance, PFAS monitoring, shipment reporting
* **Preprocessing:** Extended `PDFStandardizer` workflow for PDF text cleanup and normalization
* **Retrieval:** SentenceTransformer embeddings using `all-MiniLM-L6-v2`
* **Similarity Search:** Cosine similarity over paragraph-level document chunks
* **Generation:** T5 sequence-to-sequence model with retrieval-augmented prompts
* **Entity Extraction:** Hugging Face transformer NER pipeline with spaCy fallback extraction
* **Validation:** Entity disambiguation, regex validation, post-generation fact verification, hallucination detection
* **Analytics Layer:** CSV outputs loaded into Microsoft Power BI
* **Primary Constraints:** Inconsistent input formats, long documents, hallucination risk, proof-of-concept timeline, and need for non-technical stakeholder usability

---

## My Role

* Designed and implemented retrieval grounding, entity extraction, validation, hallucination detection, and evaluation layers
* Built semantic retrieval using SentenceTransformer embeddings and cosine similarity over paragraph-level document chunks
* Integrated retrieval with constrained generation so model outputs were grounded in source-document context
* Implemented hybrid named entity extraction using a Hugging Face transformer pipeline with spaCy fallback
* Designed entity disambiguation logic for ambiguous location, date, quantity, and miscellaneous entities
* Implemented post-generation verification by comparing generated entities against source-document entities
* Built evaluation routines for precision, recall, F1, hallucination categories, and validation failures
* Structured NLP outputs into tabular CSV datasets suitable for Power BI ingestion
* Integrated and optimized outputs for a Power BI analytics layer with page-level inspection, readability tracking, and system performance visualization
* Helped turn the backend NLP pipeline into a stakeholder-facing analytics workflow rather than a standalone model experiment

---

## Document-to-Data Layer Mapping

A central part of the work was translating unstructured environmental reports into structured data fields that could support analysis.

MassDEP’s source documents did not follow a consistent schema. Critical information appeared in different locations, formats, and writing styles depending on the report. This required mapping document-level business meaning to structured output fields.

The document-to-data mapping process involved:

* Identifying recurring environmental reporting concepts across inconsistent documents
* Mapping free-text report content to structured fields such as PFAS values, shipment quantities, site identifiers, dates, locations, and inspection attributes
* Distinguishing relevant environmental entities from surrounding narrative text
* Preserving page-level context so extracted outputs could be traced back to the original document
* Structuring report content into CSV-style outputs suitable for Power BI analytics
* Designing validation logic to flag missing, ambiguous, or unsupported extracted values

This transformed the problem from “summarize a PDF” into a structured data architecture problem: converting inconsistent environmental documentation into reliable, queryable, Power BI-ready datasets.

---

## Document Preprocessing & Standardization Pipeline

The pipeline began with a document preprocessing stage built around an extended `PDFStandardizer` class. This component converted raw, unstructured PDF text into cleaned and normalized text suitable for downstream NLP tasks.

After standardization, document content was divided into paragraph-level semantic chunks. This chunking strategy preserved relationships within the source material while enabling efficient indexing and retrieval across large document collections.

The preprocessing pipeline focused on:

* Extracting raw text from PDF reports
* Cleaning and normalizing document text
* Splitting reports into paragraph-level semantic chunks
* Preserving source-document references for validation and review
* Preparing extracted content for retrieval, generation, entity extraction, and Power BI output

The resulting chunks were stored in a knowledge base that served as the foundation for the retrieval and generation pipeline.

---

## Semantic Retrieval Layer

To enable context-aware retrieval, each paragraph-level document chunk was encoded into a dense vector representation using the SentenceTransformer model `all-MiniLM-L6-v2`.

When a user submitted a query, the system encoded the query into the same vector space and calculated cosine similarity against stored chunk embeddings. The top-k most semantically similar chunks were retrieved and assembled into a context window for downstream generation.

The semantic retrieval workflow worked as follows:

1. Cleaned document text was split into paragraph-level chunks
2. Each chunk was embedded using `all-MiniLM-L6-v2`
3. User queries were embedded into the same vector space
4. Cosine similarity identified the most relevant chunks
5. Retrieved chunks were assembled into a structured context window
6. The generation layer answered using only the retrieved context

This retrieval mechanism ensured that the generation model operated on targeted, relevant source content rather than relying on generalized parametric knowledge.

---

## Retrieval-Augmented Generation Layer

The system used a T5 sequence-to-sequence transformer model as its generation backbone.

Retrieved document chunks were injected into a structured prompt that instructed the model to answer using only the provided context. If the retrieved context did not contain enough information to answer the query, the model was directed to state that explicitly rather than generate unsupported content.

The generation process used beam search with repetition penalties, including `no_repeat_ngram_size=3`, to reduce redundant or repetitive outputs.

This retrieval-augmented generation architecture reduced hallucination risk by grounding model outputs in source-document context. The goal was not just to produce fluent answers, but to produce answers tied to evidence from the original reports.

---

## Hybrid Named Entity Extraction

Beyond response generation, the system incorporated a hybrid named entity recognition framework to extract structured entities from document text.

The primary extraction method used a Hugging Face transformer-based NER pipeline. To improve recall and robustness across varied report formats, spaCy was integrated as a fallback extractor.

Entities were categorized into four classes:

* Locations
* Dates
* Quantities
* Other

Each extracted entity carried metadata, including:

* Text span
* Entity category
* Confidence score
* Source model: transformer or spaCy
* Source document context

This metadata enabled traceability from structured outputs back to the underlying extraction method and source material.

---

## Entity Disambiguation & Validation

A dedicated disambiguation layer resolved classification ambiguities in extracted entities.

The logic evaluated medium- and low-confidence entities using contextual evidence from spaCy dependency parsing and entity recognition. For example, a low-confidence location entity could be checked against surrounding context to determine whether it might actually represent a person, organization, or unrelated label.

Date entities below a confidence threshold were validated against regular expression patterns covering common formats such as:

* MM/DD/YYYY
* ISO 8601
* Written-out month formats

Entities failing validation were reassigned to the `Other` category or flagged as uncertain. This improved precision by preventing ambiguous or low-confidence outputs from flowing directly into structured datasets.

The validation layer helped ensure that extracted entities were not only detected, but also plausible, categorized correctly, and suitable for downstream analytics.

---

## Hallucination Detection & Post-Generation Verification

A major focus of the system was reducing hallucinated or unsupported model outputs.

After each response was generated, a post-generation verification module compared entities extracted from the generated text against entities present in the original source document. Any entity appearing in generated output that could not be matched exactly or partially to a source entity was flagged as a potential hallucination.

The verification module also included a natural language inference placeholder designed to be extended with a full NLI model for contradiction detection.

The hallucination detection workflow focused on:

* Comparing generated entities against source-document entities
* Identifying unsupported values or statements
* Detecting source conflicts and input conflicts
* Categorizing hallucination types
* Returning structured verification results
* Storing flagged outputs for analysis and iteration

This created an auditable quality-control layer for generated responses. Instead of silently accepting fluent model output, the system explicitly checked whether generated information was grounded in the source documents.

---

## Power BI Analytics Integration

Power BI integration was a central part of the system because the goal was not only to extract data from documents. The goal was to make environmental report data usable for analysis, monitoring, and stakeholder-facing reporting.

The structured outputs produced by the NLP pipeline, including extracted entities, corrected document text, readability statuses, and document metadata, were exported into tabular CSV datasets and loaded into Microsoft Power BI.

Within Power BI, the data was modeled and transformed to support interactive analysis across processed documents. This converted raw machine learning outputs into a user-facing analytics layer.

The Power BI layer supported:

* Interactive dashboards built from processed environmental report data
* Page-level inspection of corrected text extracted from individual report pages
* A custom Python visual allowing users to select a page number and view extracted text
* Readability status tracking at the page level
* Green `SUCCESS` indicators for successfully processed pages
* Red `FAILED` indicators for pages where no readable text was recovered
* A readability-status pie chart showing overall processing coverage
* Visual monitoring of successful versus failed page extraction
* A stakeholder-facing interface for reviewing output quality and extracted report content

The Power BI report showed approximately **97.4% page processing coverage**, with **75 pages successfully processed** and **2 pages failed**. This made system performance visible to stakeholders rather than hidden inside backend logs.

This layer closed the loop between NLP extraction and actual business use. A structured CSV output alone would not solve the reporting problem if stakeholders still had to manually inspect files or trust model outputs blindly. Power BI gave MassDEP users an interface to inspect, filter, visualize, and validate processed document data.

The end-to-end workflow became:

**Raw environmental reports → PDF preprocessing → semantic retrieval → entity extraction → validation → CSV outputs → Power BI dashboards**

This positioned the project as a document intelligence and analytics system, not merely an NLP prototype.

---

## Evaluation Framework

The project implemented formal evaluation routines to measure and validate system performance.

The NER component was evaluated using standard information retrieval metrics:

* Precision
* Recall
* F1 score

These metrics were computed overall and by entity category, including Locations, Dates, Quantities, and Other. True positives, false positives, and false negatives were tracked at the category level, enabling fine-grained analysis of where extraction performed well and where errors occurred.

A separate hallucination evaluation routine measured how often the generation model produced unsupported or contradictory content across a test dataset. Hallucinations were categorized into fact conflicts and input conflicts, providing structured insight into the nature and frequency of model errors.

These evaluation pipelines enabled iterative improvement and provided quantitative reliability metrics for communicating system performance to stakeholders.

---

## Challenges & Limitations

The project involved several real-world constraints.

### Document Complexity

MassDEP reports varied widely in structure, formatting, and quality. Some reports contained clean key-value pairs, while others embedded critical values in long paragraphs or scanned content.

### Hallucination Risk

LLMs can generate unsupported outputs when context is incomplete, ambiguous, or too long. This required retrieval grounding, entity validation, and post-generation verification.

### Long-Document Limitations

Large reports introduced context-window and performance issues. Longer documents increased the risk of hallucination, context loss, and incomplete extraction.

### Entity Ambiguity

Environmental reports contain overlapping entity types, including locations, organizations, people, dates, measurements, and domain-specific values. This required fallback extraction, confidence thresholds, disambiguation, and validation.

### Proof-of-Concept Scope

The system demonstrated a viable architecture, but it was not a full production deployment. A production version would require stronger models, more robust OCR handling, domain-specific fine-tuning, broader report coverage, and hardened infrastructure.

### Stakeholder Usability

The system needed to expose outputs in a way non-technical users could inspect. This made the Power BI layer essential, because it translated backend processing results into readable dashboards and visual feedback.

---

## System Architecture & Documentation

A major deliverable was the architecture and workflow documentation explaining how the system transformed unstructured environmental documents into structured analytics-ready outputs.

The documentation described:

* PDF ingestion and preprocessing
* Paragraph-level semantic chunking
* SentenceTransformer embedding generation
* Cosine-similarity retrieval
* Retrieval-augmented T5 generation
* Hybrid NER using transformer extraction and spaCy fallback
* Entity disambiguation and validation
* Hallucination detection and post-generation verification
* CSV output generation
* Power BI dashboard integration
* Page-level readability tracking
* Evaluation routines for extraction quality and hallucination behavior
* Future improvements such as stronger NER, RAG expansion, domain-specific fine-tuning, and production infrastructure

This documentation converted a complex NLP and analytics system into an interpretable architecture that could be reviewed by MassDEP stakeholders, advisors, and future technical teams.

---

## Business Impact

* Built a proof-of-concept document intelligence and analytics system for MassDEP environmental construction reports
* Converted inconsistent unstructured reports into structured outputs suitable for Power BI reporting
* Reduced manual document review burden by automating repetitive extraction and standardization workflows
* Created a pipeline from raw PDF reports to validated tabular datasets and stakeholder-facing dashboards
* Integrated structured outputs with Power BI to enable inspection, filtering, visualization, and reporting
* Achieved approximately **97.4% page processing coverage**, with processed pages surfaced through dashboard visuals
* Built page-level inspection and readability tracking so users could identify successful versus failed extractions
* Designed validation layers to reduce hallucination risk and improve trust in AI-generated outputs
* Established a practical architecture MassDEP could extend with stronger models, domain-specific fine-tuning, RAG, and production analytics infrastructure

---

## Technical Skills Demonstrated

* NLP system architecture
* Document intelligence pipeline design
* PDF preprocessing and document standardization
* Semantic search using SentenceTransformer embeddings
* Cosine-similarity-based retrieval
* Retrieval-augmented generation
* T5 sequence-to-sequence generation
* Prompt grounding and constrained generation
* Hugging Face transformer NER
* spaCy fallback entity extraction
* Entity disambiguation and validation
* Regex-based date validation
* Hallucination detection
* Post-generation fact verification
* Precision, recall, and F1 evaluation
* CSV dataset generation
* Microsoft Power BI analytics integration
* Custom Python visual in Power BI
* Dashboard design for processed document inspection
* Page-level readability tracking
* AI output validation for regulated workflows
* Technical documentation under proof-of-concept constraints

---

## Key Takeaway

This work followed a consistent architecture pattern:

* **Identified** unstructured environmental reports as a bottleneck in MassDEP reporting workflows
* **Preprocessed** inconsistent PDF content into standardized text representations
* **Chunked** reports into semantic units for retrieval and traceability
* **Grounded** generation in retrieved source-document context
* **Extracted** structured entities using a hybrid transformer/spaCy NER pipeline
* **Validated** entities and generated outputs against source material to reduce hallucination risk
* **Evaluated** extraction and generation reliability through precision, recall, F1, and hallucination tracking
* **Exported** structured outputs into CSV datasets
* **Integrated** validated outputs with Power BI for page-level inspection, readability tracking, and stakeholder reporting
* **Documented** the system architecture so future teams could extend the proof of concept

The result was an end-to-end proof of concept for turning unstructured environmental construction reports into structured, validated, Power BI-ready data infrastructure for MassDEP decision workflows.
