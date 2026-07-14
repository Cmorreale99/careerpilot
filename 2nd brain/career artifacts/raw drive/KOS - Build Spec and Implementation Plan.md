---
title: KOS - Build Spec and Implementation Plan
aliases:
  - Personalized Learning OS Summary
  - KOS Build Plan
  - KOS Implementation Plan
status: active
project: KOS
type: build-spec
source_doc: Personalized learning OS summary(2).docx
created: 2026-05-07
tags:
  - kos
  - build-plan
  - postgres
  - pgvector
  - rag
  - agents
  - claude-code
---

# KOS - Build Spec and Implementation Plan

## Build objective

Build a personal knowledge operating system that ingests learning material, retrieves context from persistent personal documents, generates structured outputs optimized for the user's learning style and build goals, and stores everything in a retrievable long-term knowledge base.

## Core design principle

This should not be an AI note-taker.

It should be retrieval-backed knowledge infrastructure that converts raw inputs into structured, reusable, system-linked knowledge.

## V1 repo structure

```text
personal-knowledge-os/
├── README.md
├── .env
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── docker-compose.yml
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── services/
│   ├── pipelines/
│   ├── prompts/
│   ├── loaders/
│   ├── preprocess/
│   ├── retrieval/
│   ├── llm/
│   └── agents/
├── scripts/
├── data/
│   ├── raw/
│   ├── processed/
│   └── exports/
├── tests/
└── docs/
    ├── architecture.md
    ├── schema.md
    ├── prompts.md
    └── decisions/
```

## Database design

Use PostgreSQL with pgvector.

### Required extensions

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
```

### Core tables

#### `documents`

Stores raw document metadata.

Key fields:

- `id`
- `title`
- `source_type`
- `source_subtype`
- `file_name`
- `file_path`
- `mime_type`
- `content_hash`
- `version`
- `is_profile_doc`
- `is_active`
- `metadata`

#### `document_sections`

Optional section-aware retrieval layer.

Key fields:

- `document_id`
- `section_title`
- `section_index`
- `section_text`
- `metadata`

#### `document_chunks`

Core retrieval table.

Key fields:

- `document_id`
- `section_id`
- `chunk_index`
- `chunk_text`
- `token_count`
- `embedding`
- `chunk_type`
- `summary_text`
- `metadata`

#### `knowledge_entries`

The most important table. It stores structured LLM outputs.

Key fields:

- `document_id`
- `entry_type`
- `title`
- `source_scope`
- `lesson_or_topic`
- `summary`
- `why_it_matters`
- `system_relevance`
- `implementation_implications`
- `connections_to_prior_knowledge`
- `confidence_score`
- `status`
- `metadata`

#### `knowledge_entry_embeddings`

Embeds structured knowledge entries separately from raw chunks.

#### `concepts`

Canonical concept layer.

Example categories:

- `ai`
- `rag`
- `retrieval`
- `database`
- `orchestration`
- `finance`
- `learning_system`

#### `knowledge_entry_concepts`

Many-to-many mapping between structured outputs and concepts.

#### `concept_relationships`

Models concept hierarchy and relationships.

Example relationship types:

- `prerequisite_for`
- `related_to`
- `used_by`
- `implemented_with`
- `contrasts_with`
- `part_of`

#### `open_questions`

Tracks unresolved knowledge gaps.

Question types:

- `conceptual_gap`
- `implementation_gap`
- `architecture_decision`
- `terminology_gap`

#### `implementation_tasks`

Converts learning into build tasks.

Task types:

- `research`
- `implement`
- `refactor`
- `evaluate`
- `read`
- `design`

#### `retrieval_logs`

Stores query and retrieval observability.

#### `prompt_runs`

Stores prompt versioning, model name, input context, raw response, and parse status.

## Pipeline design

### Pipeline 1 - Profile document ingestion

Inputs:

- Neuropsych document
- Linguistic analysis document
- Architecture documents
- Summary documents

Steps:

1. Load raw file.
2. Normalize text.
3. Classify source type.
4. Write to `documents`.
5. Chunk text.
6. Embed chunks.
7. Write to `document_chunks`.

Purpose: create the persistent personalization and system-context layer.

### Pipeline 2 - Learning material ingestion

Inputs:

- Transcript `.txt`
- Paper `.pdf`
- Technical document
- Markdown note

Steps:

1. Load file.
2. Extract plain text.
3. Clean text.
4. Detect title and metadata.
5. Write to `documents`.
6. Chunk content.
7. Embed chunks.
8. Write to `document_chunks`.

### Pipeline 3 - Retrieval-augmented synthesis

Steps:

1. Select source chunks.
2. Retrieve personalization context.
3. Retrieve related prior knowledge.
4. Compose RAG context.
5. Generate structured knowledge entry.
6. Parse and validate JSON.
7. Write to storage.

Storage writes:

- `knowledge_entries`
- `knowledge_entry_embeddings`
- `concepts`
- `knowledge_entry_concepts`
- `open_questions`
- `implementation_tasks`

### Pipeline 4 - Concept consolidation

Steps:

1. Find newly extracted concepts.
2. Match to existing concepts by normalized name.
3. Create missing concepts.
4. Update `last_seen_at`.
5. Detect concept relationships.
6. Write concept links.

### Pipeline 5 - Query pipeline

Example queries:

- What do I know about vector databases?
- What open questions still exist around retrievers?
- How does LangGraph connect to my investing AI workflow?
- Show me all lessons tied to orchestration.

Steps:

1. Classify query type.
2. Retrieve relevant `knowledge_entries`.
3. Retrieve supporting chunks.
4. Retrieve concepts.
5. Retrieve open questions and tasks if relevant.
6. Generate grounded response.
7. Log run to `retrieval_logs`.

## Retrieval strategy

Use hybrid retrieval.

### Retrieval blend for synthesis

- 35 percent source chunks
- 25 percent profile documents
- 20 percent architecture documents
- 20 percent prior knowledge entries

### Retrieval blend for direct query

- 40 percent knowledge entries
- 30 percent relevant source chunks
- 15 percent profile documents
- 15 percent open questions and tasks, if relevant

## RAG synthesis prompt template

```text
SOURCE MATERIAL
{source_text}

USER PROFILE CONTEXT
{profile_context}

USER ARCHITECTURE CONTEXT
{architecture_context}

PRIOR KNOWLEDGE CONTEXT
{prior_knowledge_context}

OPEN QUESTIONS CONTEXT
{open_questions_context}

TASK
Generate a structured technical synthesis of the source material optimized for this user's learning style and system-building goals.

Focus on:
- the most important concepts
- what is new or important relative to prior knowledge
- how the material connects to the user's AI and investing workflow architecture
- what implementation implications follow from this lesson
- what remains unclear or unresolved

OUTPUT REQUIREMENTS
Return valid JSON with:
- title
- lesson_or_topic
- summary
- key_concepts
- why_it_matters
- system_relevance
- implementation_implications
- connections_to_prior_knowledge
- open_questions
- follow_up_tasks
- confidence_score
```

## Typed output model

```python
from pydantic import BaseModel, Field
from typing import List, Literal

class KeyConcept(BaseModel):
    name: str
    category: str
    description: str
    relevance_score: float
    is_primary: bool = False

class OpenQuestionOut(BaseModel):
    question_text: str
    question_type: Literal[
        "conceptual_gap",
        "implementation_gap",
        "architecture_decision",
        "terminology_gap",
    ]
    priority: Literal["low", "medium", "high"]

class FollowUpTaskOut(BaseModel):
    title: str
    description: str
    task_type: Literal["research", "implement", "refactor", "evaluate", "read", "design"]
    priority: Literal["low", "medium", "high"]

class KnowledgeEntryOut(BaseModel):
    title: str
    lesson_or_topic: str
    summary: str
    key_concepts: List[KeyConcept]
    why_it_matters: str
    system_relevance: str
    implementation_implications: str
    connections_to_prior_knowledge: str
    open_questions: List[OpenQuestionOut] = Field(default_factory=list)
    follow_up_tasks: List[FollowUpTaskOut] = Field(default_factory=list)
    confidence_score: float
```

## Implementation order

### Phase 1 - Foundation

Build:

- PostgreSQL
- pgvector
- `documents` table
- `document_chunks` table
- basic ingestion
- embedding pipeline

### Phase 2 - Profile-aware retrieval

Build:

- profile document ingestion
- hybrid retrieval
- weighting for profile documents

### Phase 3 - Structured synthesis

Build:

- synthesis prompt
- JSON validation
- `knowledge_entries` write path
- concept extraction

### Phase 4 - Query layer

Build:

- query pipeline over entries and chunks
- open question retrieval
- task retrieval

### Phase 5 - Refinement

Add:

- concept relationships
- retrieval logs
- prompt version tracking
- reranking
- lightweight UI

## MVP definition

The MVP should only do this:

1. Ingest transcript text.
2. Retrieve relevant profile and architecture context.
3. Generate a structured knowledge entry.
4. Store it in PostgreSQL.
5. Embed and retrieve prior knowledge entries later.
6. Answer questions across stored entries.

## Highest-leverage design decision

Store structured knowledge entries, not just summaries.

Without structured entries, the system is transcript summarization. With structured entries, it becomes knowledge infrastructure.

## Claude Code implementation prompt

```text
You are working inside the personal-knowledge-os repo.

Use the KOS build spec as the source of truth.

Goal: implement the smallest local MVP that can ingest a text or Markdown file, chunk it, store metadata in PostgreSQL, embed chunks with a swappable embedding client, and prepare the system for structured knowledge entry generation.

Constraints:
- Do not build UI yet.
- Keep modules small.
- Use typed Python models.
- Put database logic in app/db.
- Put ingestion logic in app/pipelines and app/services.
- Add tests for chunking and ingestion.
- Do not hardcode secrets.
- Use .env for configuration.

Before editing, inspect the repo structure and propose the minimal file changes.
```

## Related notes

- [[KOS - High Level Architecture]]
- [[KOS - Technical Design Document]]
- [[KOS Project Index]]
- [[Structured Knowledge Entries]]
- [[Hybrid Retrieval]]
- [[Prompt Runs]]
- [[pgvector]]
