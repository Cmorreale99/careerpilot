# Personal Knowledge OS (KOS)

A local-first personal knowledge operating system designed to turn unstructured notes and documents into structured, queryable, learning-oriented infrastructure — with no cloud dependencies or API costs.

---

## Current Status

This repository currently implements a **working V1 RAG prototype**: local ingestion, embedding, chunk storage, cosine retrieval, and LLM-grounded Q&A. All inference runs locally via Ollama.

**V2** will build the full relational knowledge architecture on top of V1 — CognitiveProfile, Learning_Outputs, Knowledge_Gaps, and multi-document synthesis. That schema is designed and documented below; implementation begins once V1 is stable.

---

## Implemented in V1

- Paragraph-aware, token-bounded document chunking (tiktoken, `cl100k_base` encoding)
- Local embedding generation via Ollama (`nomic-embed-text`, 768 dimensions)
- Chunk storage in PostgreSQL with float array embeddings
- Cosine similarity retrieval over stored chunks (NumPy)
- Grounded Q&A using a local LLM (`llama3.2` via Ollama)
- CLI tools for ingestion (`ingest.py`) and querying (`ask.py`, `query.py`)

---

## How the Current Pipeline Works

```
Source documents → chunking → embedding → Postgres storage
                                                  ↑
User query → embedding → cosine similarity search ┘ → local LLM → answer
```

```mermaid
flowchart TD
    A[Source Documents] --> B[chunker.py\nparagraph packing, 512-token budget]
    B --> C[embedder.py\nnomic-embed-text via Ollama]
    C --> D[(PostgreSQL\nchunks table)]

    E[User Query] --> F[embedder.py\nEmbed query]
    F --> G[retriever.py\nNumPy cosine similarity]
    G --> D
    G --> H[qa.py\nllama3.2 via Ollama]
    H --> I[Answer + cited sources]
```

---

## Quickstart

**Prerequisites:** Python 3.10+, PostgreSQL, [Ollama](https://ollama.com)

```bash
# 1. Clone and set up environment
git clone https://github.com/Cmorreale99/personal-knowledge-os.git
cd personal-knowledge-os
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env          # then edit DATABASE_URL for your local Postgres

# 4. Pull local models
ollama pull nomic-embed-text
ollama pull llama3.2

# 5. Initialize the database
python -c "from db import init_db; init_db()"

# 6. Ingest a document
python ingest.py your_notes.txt

# 7. Ask a question
python ask.py "what did I learn about transformers?"

# Raw retrieval (no LLM, just ranked chunks)
python query.py "attention mechanism"

# Useful flags
python ingest.py your_notes.txt --force            # replace an already-indexed source
python ask.py "..." --top-k 8 --model llama3.2 -v  # tune retrieval / model, trace chunks
python query.py "..." --top-k 10 -v                # more results + retrieval tracing
```

### Running the tests

```bash
pytest
```

Unit tests cover chunking, cosine ranking, and the ingest/Q&A flow; external services
(Postgres, Ollama) are mocked, so no database or model server is required to run them.

---

## Current Database Layer

The implemented schema stores one row per document chunk:

```sql
CREATE TABLE chunks (
    id           SERIAL PRIMARY KEY,
    source       TEXT NOT NULL,        -- source filename
    chunk_index  INTEGER NOT NULL,     -- position within source document
    content      TEXT NOT NULL,        -- raw chunk text
    embedding    FLOAT[],              -- 768-dim nomic-embed-text vector
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

This is the V1 retrieval layer. The V2 relational schema (KnowledgeBase, CognitiveProfile, etc.) documented below will be built on top of this foundation.

> **Note on pgvector:** The Python `pgvector` package is installed but not in use. PostgreSQL 18 does not yet have a pre-built pgvector binary. Cosine similarity is computed in Python with NumPy, which is sufficient at personal scale.

---

## V2 Architecture

V2 expands the flat chunk store into a full relational knowledge layer. The schema is designed; implementation follows V1 stabilization.

Five relational layers:

```mermaid
erDiagram

    CognitiveProfile {
        int cognitive_profile_id PK
        text linguistic_analysis
        text source_documents
        text neuropsych
        text prior_knowledge_integration
        text cross_domain_synthesis
        text retrieval_behavior
        json metadata
    }

    KnowledgeBase {
        int document_id PK
        text knowledge_level
        text domain
        text topic
        date date
        text entry_type
        text title
        int version
        json metadata
    }

    Learning_Outputs {
        int output_id PK
        text entry_type
        text title
        text source_scope
        text lesson_or_topic
        text summary
        text why_it_matters
        text system_relevance
        text implementation_implications
        text connections_to_prior_knowledge
        float confidence_score
        json metadata
        int learning_goals_id FK
        int cognitive_profile_id FK
        text implementation
    }

    Knowledge_Gaps {
        int learning_goals_id PK
        int document_id FK
        int output_id FK
        text conceptual_gap
        text technology_gap
        text implementation_gap
    }

    LearningOutputDocuments {
        int learning_output_document_id PK
        int output_id FK
        int document_id FK
        text relationship_type
        json metadata
    }

    CognitiveProfile ||--o{ Learning_Outputs : drives
    KnowledgeBase ||--o{ Knowledge_Gaps : exposes
    Learning_Outputs ||--o{ Knowledge_Gaps : surfaces
    Knowledge_Gaps ||--o{ Learning_Outputs : guides
    KnowledgeBase ||--o{ LearningOutputDocuments : contributes
    Learning_Outputs ||--o{ LearningOutputDocuments : uses
```

**Layer summary:**

- **KnowledgeBase** — canonical source-of-truth: transcripts, papers, architecture notes, documentation
- **CognitiveProfile** — governs how knowledge is transformed into understanding; controls retrieval behavior, explanation structure, and synthesis strategy
- **Learning_Outputs** — synthesized understanding, implementation implications, and contextual reasoning artifacts
- **Knowledge_Gaps** — detected conceptual weaknesses, implementation gaps, and technical deficiencies that drive future retrieval
- **LearningOutputDocuments** — junction table enabling many-to-many synthesis across multiple source documents

The goal: the same source material produces different outputs depending on cognitive profile, implementation context, and prior knowledge state.

---

## Roadmap

### V1 — Hardening (current)
- [x] Add `requirements.txt`
- [x] Add `.env.example`
- [x] Handle duplicate ingestion (skip already-indexed sources; `--force` to replace)
- [x] Add basic CLI flags (`--top-k`, `--model`)
- [x] Semantic chunking (pack whole paragraphs, fall back to token windows for oversized ones)
- [x] Retrieval tracing (`-v/--verbose` logs which chunks were surfaced per query)
- [x] Unit test suite (`pytest`)
- [ ] Migrate to pgvector once PG18 support ships (drop NumPy fallback) — *blocked: no PG18 binary yet*

### V2 — Relational Knowledge Layer
- [ ] Implement `KnowledgeBase` table and ingestion mapping
- [ ] Implement `Learning_Outputs` storage for synthesized Q&A responses
- [ ] Implement `Knowledge_Gaps` detection pass
- [ ] Implement `LearningOutputDocuments` provenance tracking
- [ ] Implement `CognitiveProfile` configuration
- [ ] Hybrid retrieval (BM25 + vector) and reranking

### V2 — Evaluation and Diagnostics
- [ ] Confidence scoring on retrieved chunks
- [ ] Prompt/response history logging
- [ ] Gap detection and recursive learning loop

### V2 — Interface and Orchestration
- [ ] Structured ingestion pipeline (watch folder, auto-ingest)
- [ ] Interactive CLI or lightweight web interface

---

## What V2 Adds

Not yet implemented — targeted for V2:

- Full relational schema: KnowledgeBase, CognitiveProfile, Learning_Outputs, Knowledge_Gaps, LearningOutputDocuments
- Multi-document provenance tracking
- pgvector / production vector indexing (pending PG18 binary)
- Hybrid retrieval, reranking, and retrieval tracing
- Gap detection and recursive learning loops
- Prompt/response history logging
- Lightweight web interface or interactive CLI
- Orchestration pipelines

---

## Why This Project Matters

Most personal knowledge tools optimize for capture. KOS is designed to optimize for **retrieval and reuse** — turning accumulated notes into infrastructure you can query, reason over, and build on.

The V1 prototype establishes the retrieval foundation. The planned architecture addresses the harder problem: encoding not just what you know, but how your understanding connects across domains, what gaps remain, and what you should learn next.

This is learning infrastructure, not note-taking software.
