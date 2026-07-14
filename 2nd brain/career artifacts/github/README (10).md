# AI-Recovery-navigation
AI relapse prevention and care navigation planner for intake and initial treatment for substance use rehab facilities

---

## Project status

Local-first MVP, built in phases (see "Implementation phases" below).

- **Phase 1 complete:** monorepo scaffold, FastAPI backend with `/health`, Next.js landing page, Docker Compose (Postgres/pgvector + Redis), and mock-mode LLM config.
- **Phase 2 complete:** SQLAlchemy models + Alembic migration for the 11 core tables (`users`, `consents`, `intake_sessions`, `intake_answers`, `journal_entries`, `documents`, `document_chunks`, `extracted_entities`, `generated_artifacts`, `safety_events`, `audit_logs`).
- **Phase 3 complete:** consent + structured intake flow. Backend endpoints `GET /me`, `POST /consent`, `GET /intake/questions`, `POST /intake/start`, `POST /intake/answers`, `GET /intake/latest`, with audit logging. Frontend consent page and a structured-intake form driven by the server-side question catalog. (v1 has no auth — a seeded demo user stands in for the current user.)

Phases 4–7 (journal/documents, safety classifier, mock artifact generation, dashboard/exports) are not yet implemented.

This is a demo/MVP. It is **not** production healthcare infrastructure, makes no HIPAA claims, and must not be used with real patient data until legal/security review.

## Local development setup

Requirements: Docker + Docker Compose. (Optional: Python 3.12 and Node 20 to run services outside containers.)

```bash
# 1. Configure environment (defaults run fully offline in mock LLM mode)
cp .env.example .env

# 2. Start the stack: Postgres/pgvector, Redis, API, and web
make up            # or: docker compose up

# 3. Verify
#    API health:    http://localhost:8000/health
#    API docs:      http://localhost:8000/docs
#    Web landing:   http://localhost:3000

# 4. Apply database migrations
make migrate       # or: docker compose run --rm api alembic upgrade head

# 5. Run backend tests (inside the api container)
make test          # or: docker compose run --rm api pytest
```

Monorepo layout: `apps/api` (FastAPI backend), `apps/web` (Next.js + TypeScript + Tailwind frontend). No LLM API key is required — `LLM_PROVIDER=mock` produces deterministic outputs; the provider is configurable via env (no provider is hardcoded).

---

Build v1 of an AI relapse-prevention and care-navigation planner.

Product definition:
A web application for people trying to quit or reduce substances that collects structured intake information, optional journals/documents, symptoms, withdrawal symptoms, diagnoses, neuropsych/ADHD/autism/trauma notes, insurance/budget/location constraints, and treatment preferences, then generates:

1. Personal relapse-risk map
2. Urge pattern decoder
3. Resource plan
4. Clinician handoff summary for intake/treatment planning
5. Relapse-prevention protocol
6. Safety escalation routing for high-risk situations

Critical boundary:
This app does NOT diagnose, prescribe, replace therapy, replace medical care, recommend medication changes, or determine level of care autonomously.

It produces clinician-reviewable decision-support artifacts. Use language like:

* “Based on user-provided information…”
* “This may suggest…”
* “Consider discussing this with a clinician…”
* “This is not medical advice.”
* “If there is immediate danger, contact emergency services or crisis support.”

Do not build an unconstrained chatbot as the main product. Build structured workflows and report generation.

Tech stack:

* Monorepo
* Frontend: Next.js + TypeScript + Tailwind
* Backend: FastAPI + Python
* Database: Postgres + pgvector
* ORM/migrations: SQLAlchemy + Alembic
* Jobs: Celery or RQ + Redis
* Object storage: local filesystem abstraction for dev, S3-compatible interface later
* LLM layer: provider-agnostic wrapper with mock mode by default
* Embeddings: provider-agnostic wrapper with mock/local fallback
* Deployment: local Docker Compose

Use local-first development. Do not overbuild cloud infrastructure.

Core product flow:

1. User completes intake.
2. User optionally uploads documents or enters journal entries.
3. App extracts structured recovery-relevant entities.
4. App runs safety classifier.
5. App generates relapse-risk map.
6. App generates urge decoder.
7. App generates resource plan based on insurance, budget, location, and preferred modality.
8. App generates clinician handoff summary.
9. App generates relapse-prevention protocol.
10. User can export/copy outputs.

Frontend pages:

1. Landing page

   * Explain product as “AI relapse-prevention and care-navigation planner.”
   * State clearly: not medical advice, not emergency support, not a replacement for treatment.
   * Main CTA: “Start intake.”

2. Consent/privacy page

   * Explain that user-provided data may include sensitive substance-use and mental-health information.
   * Consent checkbox for processing data.
   * Disclaimer: local MVP/demo is not production healthcare infrastructure.

3. Intake page
   Collect:

   * current goal: quit, reduce, maintain sobriety, prevent relapse, unsure
   * primary substance(s)
   * last use date or current use pattern
   * previous longest sober period
   * prior treatment history
   * current supports
   * current medications mentioned by user, with warning that app does not advise changes
   * diagnoses/conditions user wants to disclose
   * neuropsych/ADHD/autism/trauma notes if available
   * withdrawal symptoms
   * current symptoms
   * sleep problems
   * insurance
   * budget constraints
   * location
   * preferred support modalities: SMART, AA/NA, therapy, IOP/PHP, psychiatry, medication-assisted treatment discussion, coaching, peer support, sober living, other
   * urgency level

Important: Do not call these “diagnostic questions” in the UI. Call them “structured intake questions” or “symptom and support questions.” The app can ask about symptoms, but must not diagnose.

4. Journal page

   * User enters journal text.
   * Optional tags: craving, withdrawal, sleep issue, anxiety, shame, boredom, anger, grief, trauma trigger, progress/win, relapse risk, other.
   * Submission triggers extraction and safety classifier.

5. Document upload page

   * Accept .txt, .md, .pdf.
   * Store raw upload metadata.
   * Parse text where possible.
   * Chunk text.
   * Preserve source provenance.

6. Dashboard
   Show:

   * intake completion status
   * latest relapse-risk map status
   * latest high-risk states
   * latest urge patterns
   * latest resource plan
   * safety flags
   * recent journal entries/logs

7. Relapse-risk map page
   Output:

   * highest-risk states
   * trigger chains
   * vulnerable time windows
   * co-occurring factors mentioned by user
   * protective factors
   * constraints
   * confidence level for each claim
   * source labels: intake, journal, document, tracker, cautious inference

Example output:
“Your highest-risk states appear to be sleep deprivation, boredom, grief, shame, and evening dysregulation.”

8. Urge decoder page
   Output:

   * user-specific urge phrases
   * emotional state connected to each phrase
   * likely function of the urge
   * recommended pause/check action
   * evidence/source snippets

Example output:
“When you say ‘using happens’ or ‘just a little,’ this tends to appear during acute distress and may represent bargaining with use rather than a stable treatment decision.”

9. Resource plan page
   Output:

   * feasible resources based on insurance, budget, location, urgency, and preferred modality
   * categories:

     * outpatient therapy
     * psychiatry
     * IOP/PHP
     * peer support: SMART, AA/NA, other
     * recovery coaching
     * crisis resources
     * primary care / addiction medicine discussion
   * For v1, use placeholder/local mock resource data unless an external resource API is explicitly added later.
   * Do not fabricate real providers.
   * If exact resources are unavailable, generate a “search/action plan” rather than fake listings.

Example:
“Given your insurance, budget, and location, feasible next steps may include calling your insurance behavioral-health line, searching for in-network outpatient therapists with SUD experience, attending SMART Recovery meetings, and discussing medication/sleep concerns with a psychiatrist.”

10. Clinician handoff summary page
    Generate a clean one-page summary for an intake coordinator to hand off to clinicians.
    Sections:

* user goal
* substance-use history
* current use/recovery status
* withdrawal symptoms
* mental-health/neurodevelopmental/trauma factors mentioned by user
* sleep and energy concerns
* primary relapse-risk states
* known urge phrases/patterns
* previous supports/treatment
* insurance/budget/location constraints
* preferred modality
* safety concerns
* questions for clinician
* source data used

Use neutral clinical language.
Do not diagnose.
Do not recommend medications.
Do not determine level of care.
Phrase as “clinician-reviewable initial treatment outline,” not “treatment prescription.”

11. Relapse-prevention protocol page
    Generate personalized if-then plans:

* If high-risk state X appears, then action Y.
* Include delay tactics, contact actions, environment changes, coping actions, sleep-protection actions, and escalation conditions.
* Include specific “do not negotiate” boundaries the user has entered.
* Make protocol printable/exportable as Markdown.

Example:
“If sleep deprivation + evening distress + ‘just a little’ thoughts appear, delay all substance-related decisions for 30 minutes, contact a support person, move away from procurement contexts, and use the preselected coping routine.”

12. Safety escalation page
    Triggered by classifier.
    Routes user away from normal AI planning when high-risk content appears.

Safety categories:

* suicidality/self-harm
* overdose risk
* dangerous intoxication
* dangerous withdrawal
* psychosis/mania risk
* medication misuse
* imminent relapse/use
* driving while impaired or driving to obtain substances
* medical danger

For high-risk situations, display:

* “This may require immediate human support.”
* “If you may harm yourself or someone else, call emergency services now.”
* “If overdose or dangerous withdrawal may be happening, seek urgent medical care.”
* “Contact a trusted person, clinician, sponsor, recovery coach, or crisis line now.”
* Do not continue normal planning flow until acknowledged.

Backend architecture:
Use lightweight medallion architecture.

Bronze/raw layer:

* raw_intake_responses
* raw_journal_entries
* raw_documents
* upload_events

Silver/structured layer:

* extracted_substances
* extracted_withdrawal_symptoms
* extracted_symptoms
* extracted_conditions_mentioned
* extracted_medications_mentioned
* extracted_triggers
* extracted_high_risk_states
* extracted_urge_phrases
* extracted_constraints
* extracted_protective_factors
* extracted_treatment_preferences
* extracted_supports
* document_chunks
* document_embeddings

Gold/output layer:

* relapse_risk_maps
* urge_pattern_decoders
* resource_plans
* clinician_handoff_summaries
* relapse_prevention_protocols
* safety_plans

Operational tables:

* users
* user_profiles
* consents
* intake_sessions
* intake_answers
* documents
* document_chunks
* journal_entries
* tracker_logs
* generated_artifacts
* artifact_versions
* safety_events
* audit_logs

Minimum analytics tables:

* fact_urge_event
* fact_sleep_log
* fact_journal_entry
* fact_safety_event
* dim_substance
* dim_trigger
* dim_symptom
* dim_condition_mentioned
* dim_treatment_modality
* dim_date

API endpoints:

System:

* GET /health

User/intake:

* GET /me
* POST /consent
* POST /intake/start
* POST /intake/answers
* GET /intake/latest

Journal:

* POST /journal
* GET /journal
* GET /journal/{id}

Documents:

* POST /documents/upload
* GET /documents
* GET /documents/{id}
* GET /documents/{id}/chunks

Extraction:

* POST /extract/intake/{id}
* POST /extract/journal/{id}
* POST /extract/document/{id}
* GET /extractions/latest

Safety:

* POST /safety/classify
* GET /safety/events

Artifacts:

* POST /artifacts/relapse-risk-map/generate
* GET /artifacts/relapse-risk-map/latest
* POST /artifacts/urge-decoder/generate
* GET /artifacts/urge-decoder/latest
* POST /artifacts/resource-plan/generate
* GET /artifacts/resource-plan/latest
* POST /artifacts/clinician-handoff/generate
* GET /artifacts/clinician-handoff/latest
* POST /artifacts/relapse-protocol/generate
* GET /artifacts/relapse-protocol/latest

Tracker:

* POST /tracker/log
* GET /tracker/recent

Export:

* GET /export/clinician-handoff/markdown
* GET /export/relapse-protocol/markdown

Audit:

* Internal audit logging on intake submission, journal creation, document upload, extraction, artifact generation, safety classification, and export.

LLM/RAG layer:
Create a provider-agnostic service:

* generate_structured_output(prompt, schema, context)
* extract_recovery_entities(text)
* generate_relapse_risk_map(user_id)
* generate_urge_decoder(user_id)
* generate_resource_plan(user_id)
* generate_clinician_handoff(user_id)
* generate_relapse_protocol(user_id)
* embed_text(text)
* classify_safety_risk(text)

Mock mode:
If no LLM API key is present, produce deterministic mock outputs using heuristic extraction.

RAG separation:
Personal RAG:

* intake answers
* journal entries
* uploaded documents
* tracker logs
* extracted personal patterns

Curated resource RAG:

* seed a local docs/curated_resources.md file with general non-medical recovery concepts:

  * urge surfing
  * delay tactics
  * support contact planning
  * environment modification
  * sleep as relapse-risk factor
  * clinician discussion prompts
  * crisis escalation language

Do not use web scraping in v1.
Do not fabricate clinical evidence.
Do not claim treatment efficacy.

Structured extraction rules:
Extract entities with:

* label
* category
* source_text
* source_type
* source_id
* confidence
* extraction_method
* created_at

Entity categories:

* substance
* use pattern
* withdrawal symptom
* symptom
* condition mentioned
* medication mentioned
* trigger
* high-risk state
* urge phrase
* protective factor
* coping action
* constraint
* support
* treatment preference
* safety flag

Safety classifier:
Implement deterministic rule-based classifier before any artifact generation.

Trigger examples:
Self-harm:

* “I want to die”
* “I don’t want to be alive”
* “I might hurt myself”
* “kill myself”

Overdose/dangerous intoxication:

* “overdose”
* “can’t breathe”
* “passed out”
* “mixing benzos and alcohol”
* “opioids and alcohol”

Dangerous withdrawal:

* “quitting alcohol and shaking”
* “benzo withdrawal”
* “seizure”
* “hallucinating after stopping”

Imminent relapse/use:

* “I’m going to use”
* “using happens”
* “just a little”
* “I’m driving to buy”
* “dispensary run”
* “dealer”
* “I already ordered”

Medication misuse:

* “took extra”
* “double dose”
* “mixing meds”
* “not prescribed”

Psychosis/mania:

* “voices are telling me”
* “haven’t slept in days”
* “I am invincible”
* severe paranoia language

System behavior:

* Create safety_event.
* Return risk category and severity.
* Frontend displays safety escalation screen.
* Pause normal generation if severe.
* Never provide procurement advice, dosing advice, detox instructions, or encouragement to use.

Prompt templates:

Relapse-risk map prompt:
Given the user’s structured intake, journal/document snippets, tracker logs, and extracted entities, generate a clinician-reviewable relapse-risk map.
Include:

1. Highest-risk states
2. Trigger chains
3. Vulnerable times/settings
4. Co-occurring symptoms or conditions mentioned by user
5. Protective factors
6. Constraints
7. Confidence level for each conclusion
8. Source labels
9. Questions for clinician
   Do not diagnose.
   Do not recommend medications.
   Do not determine level of care.
   Use cautious language.

Urge decoder prompt:
Given user-provided phrases and context, identify repeated urge patterns.
For each pattern:

* phrase
* likely emotional/physiological context
* possible function of the urge
* recommended pause/check action
* source snippets
* confidence
  Do not shame the user.
  Do not imply certainty.
  Do not encourage use.

Resource plan prompt:
Given insurance, budget, location, urgency, preferred modality, and user constraints, generate a realistic resource-navigation plan.
Include:

* categories of support to consider
* exact next search/call actions
* questions to ask providers
* what information to have ready
* crisis/urgent-care routing when needed
  Do not fabricate specific providers.
  Do not guarantee coverage.
  Do not claim a treatment is medically required.

Clinician handoff prompt:
Generate a one-page intake coordinator handoff summary.
Sections:

* current goal
* substance-use history
* current status
* withdrawal symptoms
* symptoms/conditions mentioned
* relapse-risk states
* urge patterns
* current supports
* constraints
* modality preferences
* safety concerns
* suggested clinician questions
  Use neutral clinical language.
  Avoid unsupported conclusions.
  Do not diagnose or prescribe.

Relapse-prevention protocol prompt:
Generate a clinician-reviewable if-then relapse-prevention protocol.
Include:

* high-risk state
* early warning signs
* immediate action
* delay tactic
* support contact
* environment change
* coping action
* escalation condition
* source basis
  Do not include substance procurement advice.
  Do not include dosing advice.
  Do not include medication changes.

Security/privacy baseline:

* No raw sensitive text in logs.
* Use environment variables for secrets.
* Include .env.example.
* Consent table required before processing.
* Audit logs required.
* Export/delete TODO endpoints.
* Clear README warning: not production-compliant, do not use real patient data until legal/security review.
* Separate demo/seed data from real data.

Local dev deliverables:

1. Working monorepo
2. Docker Compose for Postgres/pgvector, Redis, API
3. FastAPI backend
4. Next.js frontend
5. Alembic migrations
6. Seed demo user
7. Seed curated resources
8. Intake workflow
9. Journal workflow
10. Document upload/chunking workflow
11. Extraction service
12. Safety classifier
13. Artifact generation in mock LLM mode
14. Dashboard and output pages
15. Markdown export for clinician handoff and relapse protocol
16. README
17. docs/ARCHITECTURE.md
18. docs/SAFETY.md
19. docs/DEMO_SCRIPT.md
20. docs/MVP_LIMITATIONS.md

Implementation phases:
Phase 1:

* Scaffold monorepo
* Docker Compose
* Backend skeleton
* Frontend skeleton
* README

Phase 2:

* Database schema
* Alembic migrations
* Demo user
* Consent and intake flow

Phase 3:

* Journal and document upload
* Chunking and source provenance

Phase 4:

* Extraction service
* Safety classifier
* Safety event logging

Phase 5:

* Artifact generation with mock LLM
* Relapse-risk map
* Urge decoder
* Resource plan
* Clinician handoff
* Relapse protocol

Phase 6:

* Frontend output pages
* Dashboard
* Markdown exports

Phase 7:

* Tests
* Docs
* Demo script
* Polish

Tests:
Add basic tests for:

* safety classifier
* intake creation
* journal creation
* document chunking
* extraction service
* mock artifact generation
* health endpoint

Definition of done:
A local user can:

1. Start the app with Docker Compose.
2. Complete consent and intake.
3. Enter substance-use history, symptoms, withdrawal symptoms, diagnoses/conditions, insurance, budget, location, and modality preferences.
4. Add a journal entry.
5. Upload a simple document.
6. See extracted triggers, symptoms, withdrawal symptoms, constraints, supports, and high-risk phrases.
7. Generate a relapse-risk map.
8. Generate an urge decoder.
9. Generate a resource plan.
10. Generate a clinician handoff summary.
11. Generate a relapse-prevention protocol.
12. Trigger safety escalation using high-risk phrases.
13. Export clinician handoff and relapse protocol as Markdown.

Start by inspecting the repo. If empty, create the project from scratch. First produce a concise implementation plan, then execute phase by phase.
