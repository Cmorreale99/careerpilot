---
source_file: "2nd brain/career artifacts/raw drive/jobpilot_second_brain_architecture_reconstructed_obsidian_mvp_update.docx"
source_sha256: add1f53a32266ac9524946a134ba0215072bf7f20d4fbe436e4ae5babcdebd5a
converter: mammoth 1.12.0
conversion_warnings:
  - "Unrecognised paragraph style: Code Block (Style ID: CodeBlock)"
---

__Jobpilot \+ Second Brain  
Architecture Synthesis__

*From evidence\-to\-career\-story compiler to unified personal context substrate*

__Document thesis__  
Second Brain is the unified personal context substrate\.  
  
Jobpilot is a downstream career\-story compiler that consumes only approved, app\-scoped career context\.  
  
The system must never treat raw text as truth and must never let unapproved generated prose become canonical evidence\.

__Prepared for Cam Morreale__

Working draft \- reconstructed from Jobpilot V2 audit, Architecture V3 draft, V3 audit, second\-brain design discussion, architecture notes, sensitive\-career\-project update, universal ingestion/cost guardrails, and Obsidian\-first MVP ingestion correction

# Table of Contents

1\. Executive Summary

2\. The Actual Problem Space

3\. What the V2 Audit Proved

4\. What Architecture V3 Got Right and Wrong

5\. Corrected Jobpilot Target Architecture

6\. Project Story Model and Resume\-Ready Gate

7\. Review UX: From 148 Claims to Project Cards

8\. Second Brain as Personal Context Substrate

9\. Data Layer / Second Brain Build

10\. Source Adapters and Context Ingestion

10\.2 Universal Source Ingestion and Cost Guardrails

10\.3 Source\-Specific Guardrail Matrix

10\.4 Source Budget Policy

10\.5 Cost\-Controlled Runtime Retrieval Contract

10\.6 Dry\-Run Audit Output

11\. Trust, Provenance, and App\-Scoped Memory

11\.1 Sensitive Career Evidence Exception

12\. Jobpilot Integration: CareerContextView

13\. Jobpilot V4 UI and Application Architecture

14\. Repo/Fork Recommendation

15\. Data Model Blueprint

16\. Implementation Roadmap

17\. Acceptance Criteria and Test Harness

18\. Risk Register and Guardrails

19\. Decision Register

20\. Obsidian\-First Raw Markdown Archive and MVP Ingestion Contract

Appendix A\. Prompting Strategy

Appendix B\. Minimal Next Build Spec

# 1\. Executive Summary

The architecture has converged on one clear direction: Jobpilot should not be a generic resume generator, generic RAG app, or claim\-review workflow\. Jobpilot should be an evidence\-to\-career\-story compiler\. Its job is to convert messy personal evidence into a small number of accurate, high\-leverage, project\-level stories that can safely feed resumes, outreach, and interview prep\.

Obsidian\-first correction: importing everything raw into Obsidian is allowed and cheap; Opus extraction over the whole vault is prohibited by default\. The MVP should parse local Markdown, YAML frontmatter, wikilinks, and explicit jobpilot\_ingest flags, then run selective extraction only on career\-scoped notes\.

Cost and ingestion control are first\-class architecture constraints\. Every source adapter must run metadata\-first, estimate cost before extraction, deduplicate before embedding, deny sensitive classes by default, and produce candidate memories only\. Jobpilot runtime must never search raw ChatGPT, Claude, Perplexity, Google Drive, or GitHub history directly; it may use only a local Career Index and one locked RetrievalSnapshot per job posting\.

The larger second\-brain idea is not separate\. The latest correction is that Obsidian is the near\-term staging substrate: raw ChatGPT, Claude, Claude Code, Perplexity, GitHub, and Google Drive context should be imported into Obsidian as Markdown first\. Jobpilot MVP should consume career\-scoped Obsidian notes and canonical Project Stories, not direct raw\-source connectors\.

The handwritten architecture notes sharpen the near\-term implementation: the data layer is a Claude \+ Obsidian\-oriented second\-brain build; Jobpilot v4 should have a dashboard, master CV storage, manual job\-posting input, and a “Create Optimized Resume” action\. Scraping is deliberately deferred to v5\. The application layer should cross\-reference the job posting against the master CV and approved career context, then construct a targeted resume from the strongest grounded projects for that role\.

New correction: sensitive personal material is denied by default but can be explicitly promoted into a redacted, app\-scoped SensitiveCareerProject\. This prevents recovery, medical, therapy, dating, or other private contexts from leaking into Jobpilot while still allowing legitimate technical and mission\-driven projects, such as AI Recovery Navigation, to become career evidence when the user deliberately approves the disclosure boundary\.

__High\-level architecture__  
Second Brain builds structured memory\.  
  
Jobpilot compiles approved career memory into career capital\.  
  
Downstream outputs \- Master CV, tailored resumes, outreach, and interview prep \- may use only approved Project Stories\.

__Question__

__Answer__

What is Jobpilot?

An evidence\-to\-career\-story compiler, not a resume generator\.

What is the core object?

Approved Project Story / Project Capsule\.

What is the Second Brain?

A typed, temporal, provenance\-backed personal context substrate\.

What should the user review?

One project card per real project, not raw claims\.

What should never happen?

Raw text, unapproved claims, or LLM\-composed prose becoming canonical career truth\.

Best repo to fork?

Graphiti, extended with approval states, app scopes, source adapters, and Jobpilot\-specific Project Stories\.

What is v4?

Dashboard \+ master CV \+ pasted job posting \+ project ranking \+ optimized resume generation using approved context\.

What is v5?

Scraping, automated job\-board ingestion, company research, and broader workflow automation\.

How does Jobpilot handle sensitive career evidence?

Denied by default; usable only through explicit promotion into a redacted, scoped SensitiveCareerProject with artifact\-specific disclosure approval\.

How are ingestion costs controlled?

Every source adapter requires a dry\-run audit, budget cap, dedupe pass, sensitivity filter, and cheap\-model extraction plan before processing\.

Can Jobpilot search raw chats or Drive at runtime?

No\. Runtime generation uses only a locked RetrievalSnapshot from the local Career Index unless the user explicitly refreshes evidence search\.

The immediate build direction should be deliberately boring: gates, schemas, state transitions, review objects, provenance, and tests\. More LLM synthesis should come after those mechanics are correct\.

# 2\. The Actual Problem Space

__Precise problem definition: __Jobpilot must transform a noisy, redundant, heterogeneous personal corpus into a small number of verifiably true, high\-leverage, project\-level career stories within a tolerable review budget\. The hard problem is not generating prose\. The hard problem is deciding what work exists, what problem each project solved, what actions remedied that problem, what results are credible, and what is worth showing to the user\.

## 2\.1 The product is not the extraction pipeline

- Not a resume generator: Resume bullets are downstream renderings, not canonical truth\.
- Not generic RAG: The system cannot simply retrieve snippets and ask an LLM to write a resume\.
- Not claim review: Claims are internal inventory\. They are not the user\-facing object\.
- Not Drive cleanup: Messy input should reduce recall or create targeted questions, not corrupt the Master CV\.
- Not an LLM creativity task: The system must compile, verify, and elicit\. It must not invent\.

## 2\.2 Correct north star

Raw personal corpus  
 \-> Source and entity discovery  
 \-> Project clustering  
 \-> Evidence assignment  
 \-> Candidate Problem / Action / Result extraction  
 \-> Project Story construction  
 \-> Human approval / targeted elicitation  
 \-> Approved Master CV entries  
 \-> Tailored downstream artifacts

__Core invariant__  
No complete Project Story, no Master CV entry\.  
No approved Project Story, no tailoring/outreach\.  
No evidence or user attestation, no factual sentence\.

# 3\. What the V2 Audit Proved

The V2 audit established that the original failure was architectural, not cosmetic\. The system was organizing evidence around files and claims rather than real projects\. That caused filename\-shaped experiences, duplicated resume versions, cross\-project contamination, one\-word Problems, missing Results, and polished unsupported prose\.

__Failure__

__Meaning__

__Architectural lesson__

Files treated as experiences

A resume PDF, degree form, or multi\-project case study became a career entity\.

Source files are not projects\. Add project/entity boundaries before extraction\.

One\-word Problems

Fragments like “manual” or metric\-only snippets passed validators\.

Problem must be a complete problem\-space statement, not an extracted token\.

Cross\-project Results

Metrics could support unrelated claims because evidence scope was too broad\.

Every Problem, Action, Result, and evidence span must share project\_id\.

V1 bypass

Legacy master\_cv output could feed user\-facing prose without reviewed claims\.

All user\-facing generation must route through approved ledger/story objects\.

Review flood

The user became deduper, validator, and chunker\.

The review unit must be Project Story, not raw claim\.

The V2 remediation improved obvious symptoms: better project separation, fewer broken PAR fragments, and fewer one\-word Problems\. But it exposed the next problem: even a cleaner claim ledger can still produce an intolerable review workflow if the user must click through dozens or hundreds of components\.

# 4\. What Architecture V3 Got Right and Wrong

## 4\.1 What V3 got right

- Project Story is the correct central object\.
- Claims should be demoted to internal inventory\.
- One project should appear once\.
- Problem Space should be defined before Actions and Results are selected\.
- Incomplete projects should become needs\_problem, needs\_result, evidence\_only, portfolio\_inventory, or exclude\_low\_value rather than resume material\.
- Review should happen at the project\-card level, not as a 148\-item claim queue\.

## 4\.2 What V3 got wrong

__Issue__

__Why it matters__

__Correction__

Statements without mechanisms

The architecture says resume\_ready is enforced, but code did not enforce it everywhere\.

Build pure domain gate \+ server\-side approval check \+ render\-time refusal\.

Machine readiness conflated with human approval

A model or heuristic can mark something resume\_ready, but only user approval should make it canonical\.

Separate readiness from review\_status\.

LLM composition too early

Compose\-and\-elevate can create plausible unsupported Problem prose\.

Start with deterministic selection/gating; add LLM prose after evidence mechanics are enforced\.

Claim\-level edit fallback

The 148\-claim nightmare returns one click deep\.

Create story\-component edit/attestation paths that do not expose raw claim queues\.

Weak dedupe plan

Per\-entity synthesis cannot detect duplicates across entities\.

Add deterministic cross\-entity evidence/result overlap checks before review/render\.

Downstream safety underspecified

Tailoring/outreach can silently no\-op or bypass story gates\.

Add story\-to\-output adapters and number/evidence guards for all outbound prose\.

__Implementation verdict__  
Use Architecture V3 as the conceptual direction\. Use the V3 audit as the implementation plan\. Do not implement V3 exactly as written\.

# 5\. Corrected Jobpilot Target Architecture

The corrected architecture keeps the Project Story abstraction but moves enforcement away from prompts and into domain code, database state, review APIs, and render\-time gates\.

Confirmed roster entity  
 \-> Internal claims and evidence inventory  
 \-> Deterministic readiness computation  
 \-> Project Story card  
 \-> Targeted missing\-info questions  
 \-> Human approval  
 \-> ApprovedProjectStory  
 \-> MasterCvEntry  
 \-> Tailoring / outreach / interview prep

__Layer__

__Purpose__

__Hard rule__

Source layer

Register files, conversations, repos, chats, docs\.

Raw source text is never truth by itself\.

Evidence layer

Chunks/spans tied to sources and entities\.

Evidence must carry source\_id, project\_id, and location\.

Claim inventory

Internal candidate facts extracted from evidence\.

Claims are not user\-facing review objects\.

Project Story

One coherent career story per real project\.

One project appears once\.

Readiness gate

Determines whether story is complete enough\.

Needs approved/attested Problem, Action\(s\), Result\.

Human approval

Turns a ready story into canonical career context\.

No human approval, no Master CV\.

Output adapters

Generate CV/resume/outreach/prep from stories\.

Every factual sentence traces back to approved story components\.

# 6\. Project Story Model and Resume\-Ready Gate

## 6\.1 Project Story structure

- Problem Space: The real user, business, technical, operational, or process problem the project existed to solve\.
- Actions: The technical and strategic interventions taken to remedy that Problem Space\.
- Results: The measurable, observable, or user\-attested outcomes caused by those Actions\.
- Evidence: Source\-backed support or explicit user attestation for every included component\.
- Inclusion decision: Whether the story belongs in the Master CV, portfolio inventory, or exclusion set\.

__Resume\-ready hard gate__  
A project is resume\_ready only if it has all of the following under the same Project Story: one approved or user\-attested Problem Space, one or more approved Actions, and one approved or user\-attested Result\. If any piece is missing, the project must not render into the Master CV\.

__Readiness state__

__Meaning__

__Allowed to render?__

resume\_ready

Complete PAR and passed integrity checks\.

Only after human approval\.

needs\_problem

Actions/results may exist, but the real problem space is absent or unsupported\.

No\. Ask targeted question\.

needs\_result

Problem/actions exist, but no credible outcome exists\.

No\. Ask targeted question\.

needs\_action

Problem/result exist, but action evidence is missing\.

No\. Rare, but possible\.

evidence\_only

Useful context, not resume material yet\.

No, unless explicitly promoted later\.

portfolio\_inventory

Useful for portfolio/search, not Master CV\.

No\.

duplicate\_needs\_merge

Likely duplicate of another project\.

No until merged or split\.

exclude\_low\_value

Not worth including\.

No\.

# 7\. Review UX: From 148 Claims to Project Cards

The user should never be asked to approve raw claims as the primary workflow\. A 148\-item review queue means the system is exposing implementation artifacts\. The correct UX is one card per Project Story with ranked candidates and targeted questions\.

Project: Cooper\.ai \- Pacifica Automation  
Status: needs\_result / resume\_ready  
  
Problem: Manual weekly/monthly POS/SPS ingestion created operational friction and delayed forecast updates\.  
  
Actions:  
 1\. Built EventBridge/Lambda/S3/Snowflake automation for weekly and monthly ingest\.  
 2\. Added idempotent late\-file handling\.  
 3\. Normalized SPS/POS file formats\.  
  
Result:  
 Candidate: Late\-arriving client data still processed successfully\.  
  
Question if missing:  
 What measurable or observable outcome came from this automation?  
  
Actions: Approve | Edit component | Answer question | Portfolio inventory | Exclude

__Should appear in normal review__

__Should not appear in normal review__

Project card

Raw claim queue

Recommended Problem / Actions / Result

Validator flag wall

Targeted missing\-info question

Fragment evidence snippets with no context

Merge suggestion

Duplicate cards for the same project

Include/exclude decision

Low\-level source/debug details

# 8\. Second Brain as Personal Context Substrate

The second\-brain idea is not a separate product tangent\. It is the context substrate Jobpilot needs\. The Second Brain ingests and structures personal context; Jobpilot consumes a career\-scoped view of that context\.

__Unifying model__  
Second Brain = memory infrastructure\.  
  
Jobpilot = career compiler\.  
  
Other future apps = scoped consumers of the same approved context graph\.

Second Brain  
 captures projects, notes, conversations, decisions, goals, timelines, people,  
 deliverables, outcomes, preferences, and personal operating context\.  
  
Jobpilot  
 queries approved career context to construct Project Stories, Master CV entries,  
 targeted resumes, outreach, and interview prep\.

## 8\.1 Why this solves Jobpilot gaps

- Missing Problems: GitHub READMEs often explain implementation but not why the project mattered\. Second\-brain notes/conversations can supply candidate context\.
- Missing Results: Conversation history, work logs, invoices, and reflections may contain outcomes not present in source docs\.
- Deduplication: The same project appears across a repo, resume, case study, invoice, and chat\. A context graph can cluster these\.
- Timeline reconstruction: Events, decisions, and deliverables can be ordered across sources\.
- Interview prep: Approved project memories can support STAR/PAR answers without re\-mining raw chats\.
- Target\-role ranking: Preferences and target roles can influence which Project Stories are most valuable\.

# 9\. Data Layer / Second Brain Build

The data layer is the explicit second\-brain build\. In the handwritten notes, this is described as a Claude \+ Obsidian\-oriented system: a massive queryable database of professional context, technical work, AI conversations, GitHub work, and personal Drive documents\. This layer should not directly generate resumes\. It should create and maintain structured, source\-backed memory candidates that can be approved, scoped, and consumed by Jobpilot\.

__Data layer principle__  
The Second Brain is a massive queryable context database, but queryable does not mean automatically trusted\. All raw context becomes candidate memory first; career use requires approval, app\-scope permission, and provenance\.

__Second Brain input__

__Role in the system__

Claude conversations

Architecture brainstorming, project reasoning, prompt iterations, and unresolved design questions\.

ChatGPT conversations

Project discussions, decisions, work reflections, target\-role preferences, and missing problem/result context\.

Perplexity / chatbot conversations

Research conversations, market/tool/company findings, and citation\-backed context\.

Claude Code conversations

Implementation work, PLAN\.md/CLAUDE\.md context, codebase decisions, bugs fixed, tests, and deliverables\.

GitHub

Repos, README files, commits, PRs, issues, implementation artifacts, and technical evidence\.

Google Drive

Resumes, case studies, notes, PDFs, invoices, meeting notes, work logs, and deliverable summaries\.

Google Docs / documents

Long\-form project docs, career material, architecture notes, and human\-authored evidence\.

Obsidian vault

Human\-facing knowledge layer and navigation surface over approved or reviewable memory\.

Data Layer / Second Brain Build  
 \- Claude \+ Obsidian personal knowledge system  
 \- Queryable database of career/project context  
 \- Ingests AI conversations, Claude Code, GitHub, Drive, Docs, notes, and project logs  
 \- Produces candidate memories, project clusters, source\-backed evidence, and targeted questions  
 \- Exposes only app\-scoped approved context to Jobpilot

# 10\. Source Adapters and Context Ingestion

__Adapter__

__Input examples__

__High\-value extractions__

ChatGPT conversations

Exports, project discussions, reasoning logs, therapy/recovery conversations if explicitly allowed\.

Decisions, project context, goals, preferences, self\-observations, missing Problems/Results\.

Claude Code projects

PLAN\.md, CLAUDE\.md, README, diffs, audits, implementation notes\.

Technical actions, architectural decisions, tests, deliverables\.

Claude Chat conversations

Architecture brainstorming, coding plans, prompt iterations\.

Design decisions, rationale, unresolved questions\.

Perplexity conversations

Research chats with citations\.

Market/tool/company research, factual findings, source\-backed context\.

Google Drive

Resumes, PDFs, notes, invoices, meeting notes, case studies\.

Career evidence, dates, project descriptions, outcomes\.

Google Docs

Drafts, documents, architecture memos, project notes\.

Human\-authored context, structured thinking, career claims, problem statements\.

GitHub

Repos, commits, PRs, issues, READMEs, architecture docs\.

Implementation actions, technical depth, timelines, artifacts\.

Universal adapter gate

Every source adapter before full ingestion\.

Metadata inventory, token estimate, dedupe, sensitivity class, budget check, and scoped candidate extraction\.

## 10\.1 Ingestion pipeline

Source adapters  
 \-> Raw source registry  
 \-> Normalization  
 \-> Chunking / span extraction  
 \-> Entity resolution  
 \-> Memory candidate extraction  
 \-> Provenance graph  
 \-> Review / attestation  
 \-> Durable personal context graph  
 \-> App\-scoped context views

## 10\.2 Universal Source Ingestion and Cost Guardrails

The ingestion contract must apply to every source adapter: ChatGPT, Claude Chat, Claude Code, Perplexity, Google Drive, GitHub, and future sources\. No source gets special trust\. Each source is raw material until it passes inventory, cost estimation, deduplication, sensitivity classification, scoped extraction, and approval\.

Universal ingestion invariant  
Inventory first\. Estimate cost first\. Classify before extraction\. Dedupe before embedding\. Deny sensitive categories by default\. Use cheap models for bulk extraction\. Use local indexes for retrieval\. Freeze one RetrievalSnapshot per job\. Never let Jobpilot search raw source history at runtime\.

### Required ingestion sequence

Raw source  
 \-> metadata inventory  
 \-> local token estimate  
 \-> hash and duplicate grouping  
 \-> source/category classification  
 \-> privacy/sensitivity filter  
 \-> cost budget check  
 \-> embedding/indexing  
 \-> cheap candidate extraction  
 \-> human approval/attestation  
 \-> app\-scoped context view

__Gate__

__Purpose__

__Hard rule__

Metadata inventory

List files/conversations/repos before reading full text\.

No full fetch until the source is counted and classified\.

Token estimate

Estimate cost before any paid model call\.

No extraction run without an estimated max spend\.

Hash \+ dedupe

Collapse duplicates, exports, copies, and repeated docs\.

Duplicates are grouped before embedding or extraction\.

Sensitivity classification

Separate career/project material from recovery, medical, dating/private, finance, legal, and other sensitive classes\.

Sensitive classes are denied by default\.

Budget check

Compare proposed embed/extract tokens against source budget\.

Runs fail closed when the cap is exceeded\.

Scoped extraction

Create candidate memories, not canonical truth\.

Raw source text and generated summaries do not become approved memories\.

Human approval

Promote only reviewed/attested memories\.

No approval means no CareerContextView output\.

## 10\.3 Source\-Specific Guardrail Matrix

__Source__

__Default treatment__

__CareerContextView access__

__Special guardrail__

ChatGPT history

High\-volume raw conversation export\.

Only career/project/technical candidates after classification\.

Classify conversations first; exclude sensitive or repetitive loops by default\.

Claude chats

Architecture, reasoning, coding, and design conversations\.

Allowed if career/project scoped\.

Treat as reasoning logs, not truth; extract decisions and candidates only\.

Claude Code projects

Implementation\-adjacent evidence: PLAN\.md, CLAUDE\.md, README, diffs, audits, tests\.

High priority if project\-relevant\.

Prefer repo files, diffs, test output, and committed artifacts over chat prose\.

Perplexity chats

Research/reference material with citations\.

Limited; only when attached to a project decision\.

Research context is not career evidence by itself\. Preserve source URLs/date accessed\.

Google Drive

Mixed\-quality document lake with duplicates and private files\.

Only allowlisted or classified career/project docs\.

Metadata scan first; dedupe \.docx/Google Doc/PDF copies; deny medical/recovery/dating/private by default\.

GitHub

Technical artifact layer\.

Allowed if project\-relevant\.

Exclude forks, vendor repos, huge irrelevant repos, and generated artifacts unless manually promoted\.

Google Drive rule  
Drive should not execute: search all Drive \-> fetch everything \-> send to model\. Drive should execute: inventory Drive \-> classify locally \-> allowlist \-> estimate cost \-> confirm \-> process\.

## 10\.4 Source Budget Policy

Each adapter must declare a source budget before ingestion\. Exact dollar values can be tuned, but the architecture must enforce a hard cap and require user confirmation above a configured threshold\.

__Source__

__First\-pass budget__

__Hard stop__

__Runtime raw search allowed?__

ChatGPT

$25\-$75

$150

No

Claude Chat

$10\-$50

$100

No

Claude Code

$5\-$25

$50

No

Perplexity

$5\-$25

$50

No

Google Drive

$10\-$75

$150

No

GitHub

$5\-$25

$50

No

### Canonical policy object

\{  
  "source": "google\_drive",  
  "mode": "metadata\_first",  
  "dry\_run\_required": true,  
  "max\_tokens\_to\_embed": 50000000,  
  "max\_tokens\_to\_extract": 10000000,  
  "max\_cost\_usd": 25,  
  "requires\_user\_confirmation\_above\_usd": 10,  
  "sensitive\_default": "deny",  
  "runtime\_retrieval\_allowed": false  
\}

## 10\.5 Cost\-Controlled Runtime Retrieval Contract

Jobpilot must not search ChatGPT, Claude, Perplexity, Google Drive, or GitHub directly during resume generation\. Runtime generation may use only a precomputed, local, app\-scoped Career Index and one frozen RetrievalSnapshot per job posting\.

Runtime prohibition  
No model\-controlled search tools at resume\-generation time\. No agentic re\-search\. No repeated raw\-source scans\. Regeneration, edits, interview prep, and outreach reuse the same locked RetrievalSnapshot unless the user explicitly clicks Refresh evidence search\.

__Runtime action__

__Allowed source__

__Rule__

Generate tailored resume

Locked RetrievalSnapshot

No new raw source search\.

Regenerate bullet

Same RetrievalSnapshot

No new raw source search\.

Explain project selection

Snapshot metadata and selected evidence refs

No new raw source search\.

Generate outreach/interview prep

Approved Project Stories and snapshot evidence

No new raw source search\.

Refresh evidence search

Local Career Index only

Allowed only after explicit user action and budget preview\.

### RetrievalSnapshot example

\{  
  "retrieval\_snapshot\_id": "snapshot\_job\_2026\_07\_06",  
  "job\_posting\_hash": "abc123",  
  "career\_index\_version": "v42",  
  "permission\_scope\_version": "v9",  
  "retrieval\_call\_count": 1,  
  "selected\_projects": \[  
    "cooper\_pacifica\_automation",  
    "cooper\_shipping\_pipeline\_fixes",  
    "wellington\_oracle\_python\_platform",  
    "massdep\_llm\_pipeline"  
  \],  
  "evidence\_span\_budget": 20,  
  "max\_context\_tokens": 12000,  
  "locked": true  
\}

## 10\.6 Dry\-Run Audit Output

Every ingestion run must begin with a dry\-run audit\. The audit must be visible to the user before execution if the estimated cost exceeds the confirmation threshold\.

__Audit field__

__Meaning__

source\_type

ChatGPT, Claude Chat, Claude Code, Perplexity, Google Drive, GitHub, or future source\.

item\_count

Files, conversations, repos, commits, or other units discovered\.

estimated\_tokens

Total token estimate before embedding/extraction\.

duplicate\_count

Items grouped or skipped by hash/title/content similarity\.

sensitive\_category\_count

Items denied by default pending explicit promotion\.

tokens\_excluded

Estimated tokens removed by filters\.

tokens\_to\_embed

Estimated tokens sent to embedding\.

tokens\_to\_extract

Estimated tokens sent to candidate\-memory extraction\.

estimated\_embedding\_cost

Embedding\-only estimate\.

estimated\_extraction\_cost

Cheap\-model extraction estimate\.

max\_approved\_spend

Hard cap for the run\.

# 11\. Trust, Provenance, and App\-Scoped Memory

The central trust boundary is simple: raw sources are not truth\. Extracted memories are candidates\. Approved memories become durable personal context\. Downstream apps consume only context scoped for their purpose\.

__State__

__Meaning__

__Usable by Jobpilot?__

raw\_source

Unprocessed source text or file\.

No\.

extracted\_candidate

Model/heuristic extracted memory candidate\.

No, except as review input\.

needs\_review

Possibly useful but not approved\.

No, unless shown as question/candidate\.

approved

Reviewed durable memory\.

Yes, if app scope permits\.

user\_attested

Typed/confirmed by user\.

Yes, if app scope permits\.

rejected

False/irrelevant\.

No\.

superseded

Historically useful but not current\.

No by default; may be used for history\.

private\_do\_not\_use

Sensitive or out\-of\-scope\.

No\.

redacted\_promoted

Sensitive source transformed into a career\-safe summary with user approval\.

Yes, only within the approved app scope and disclosure mode\.

disclosure\_approved

User approved a specific sensitive disclosure for a specific output type\.

Yes, for that artifact only; never as global permission\.

inventory\_only

Metadata discovered, content not fetched or extracted yet\.

No\.

cost\_estimated

Token/cost estimate completed before paid processing\.

No\.

duplicate\_grouped

Item grouped with duplicate or near\-duplicate source\.

No, except the canonical item may continue\.

budget\_blocked

Estimated run exceeds configured budget or confirmation threshold\.

No until explicitly approved\.

__Privacy invariant__  
Every downstream app receives a scoped context view, not full\-brain access\. Jobpilot should see career/project context only\. Recovery, dating, medical, and unrelated private context should not flow into Jobpilot by default\.

__Memory class__

__Default Jobpilot access__

Career/project memories

Allowed after approval\.

Technical project notes

Allowed after approval\.

Interview feedback and professional preferences

Allowed after approval\.

Mental health/recovery content

Denied by default; may enter only through explicit SensitiveCareerProject promotion, redaction, and artifact\-specific approval\.

Dating/sexual/private personal content

Denied by default\.

Medical/medication context

Denied by default unless explicitly scoped\.

Public technical artifact in sensitive domain

Allowed as technical\_only after approval; personal origin excluded by default\.

User\-approved personal origin story

Allowed only for the specific output mode approved by the user; revocable and not global\.

## 11\.1 Sensitive Career Evidence Exception

Some high\-value career evidence originates in sensitive personal domains such as recovery, health, disability, trauma, family history, or other private lived experience\. The architecture should not make sensitive context globally available, but it also should not force the user to discard legitimate career evidence\. The correct rule is deny by default, then allow explicit promotion into a redacted, app\-scoped, career\-safe form\.

Sensitive evidence invariant  
Raw sensitive sources are not usable by Jobpilot\. A sensitive project can enter CareerContextView only through explicit user promotion, redaction, source/provenance binding, and artifact\-specific disclosure approval\.

### SensitiveCareerProject policy

__Mode__

__Meaning__

__Example use__

technical\_only

Use the project as a software/product artifact\. Exclude personal motivation, diagnosis, recovery history, medication, therapy, and relapse details\.

Built an AI relapse\-prevention and care\-navigation MVP\.

domain\_context\_allowed

Mention the recovery/SUD domain and product problem, but do not disclose the user's personal history\.

Designed decision\-support workflows for substance\-use recovery navigation\.

personal\_origin\_allowed

Use a specific user\-approved origin sentence\. Requires artifact\-specific approval and can be revoked\.

Built the system from lived experience recovering from severe cannabis addiction\.

private\_do\_not\_use

Exclude the project and associated sensitive context from Jobpilot outputs\.

Do not include in resumes, outreach, or interview prep\.

### Promotion workflow

Sensitive source material must pass through a separate promotion gate before it becomes available to career outputs\. The gate should create a sanitized Project Story variant rather than granting Jobpilot broad access to recovery, medical, therapy, or private notes\.

Sensitive raw source  
 \-> Sensitivity classification  
 \-> Candidate public technical artifact  
 \-> Redaction / promotion review  
 \-> SensitiveCareerProject profile  
 \-> Disclosure mode selection  
 \-> CareerContextView projection  
 \-> Jobpilot Project Story compiler

### AI Recovery Navigation example

The AI\-Recovery\-navigation repo is a valid portfolio artifact and should not be automatically excluded because its domain is sensitive\. It should default to technical\_only\. The public project evidence can support technical/product claims\. The personal sobriety origin story is a separate disclosure object that requires explicit approval for each output type\.

__Field__

__Architecture value__

project\_id

ai\_recovery\_navigation

project\_type

SensitiveCareerProject

default\_visibility

technical\_only

allowed\_context\_view

CareerContextView

sensitive\_origin\_default

private\_do\_not\_use

requires\_explicit\_approval

true for personal origin disclosure

public evidence scope

GitHub repo/README, architecture, code, technical stack, product boundaries, implementation phases

blocked by default

Recovery logs, therapy notes, relapse\-risk details, medication context, private personal history, raw self\-disclosure

### Public technical story candidate

Problem: People seeking substance\-use recovery support often need structured intake, relapse\-risk mapping, care navigation, and clinician\-reviewable handoff artifacts without relying on an unconstrained chatbot\.  
  
Actions: Built a local\-first MVP with FastAPI, Next\.js, Docker Compose, Postgres/pgvector, Redis, SQLAlchemy, and Alembic; implemented consent, structured intake, audit logging, and an 11\-table data model; defined safety/product boundaries preventing diagnosis, medication advice, autonomous level\-of\-care decisions, or emergency\-care replacement\.  
  
Result: Created a working Phase 1\-3 MVP foundation for a safety\-aware AI recovery navigation planner, with later journal/document, safety\-classifier, artifact\-generation, dashboard/export phases still pending\.

### Output rules

__Output type__

__Allowed content__

__Blocked content unless separately approved__

Generic data engineering resume

Technical stack, data model, backend/frontend architecture, Docker/local\-first implementation, audit logging\.

Personal addiction/recovery disclosure\.

AI/product/healthtech resume

Recovery\-navigation product domain, structured intake, clinician\-reviewable artifact generation, safety\-aware boundaries\.

Claiming clinical efficacy or personal sobriety causation\.

Mission\-driven outreach

Optional domain motivation if user approves the specific disclosure\.

Raw recovery details, therapy notes, medication history, relapse specifics\.

Interview prep

Private coaching notes may include fuller context, but the system must label what is safe to say externally\.

Any statement that implies the app treated or cured the user\.

Career claim boundary  
Safe: "I leveraged AI as part of my own recovery process and later built a recovery\-navigation MVP inspired by that experience," if explicitly approved\.  
Unsafe unless clinically validated: "The app helps people get sober\."  
Architecture rule: personal outcome evidence is not product efficacy evidence\.

### Candidate technical bullet

Built a local\-first AI relapse\-prevention and care\-navigation MVP using FastAPI, Next\.js, Postgres/pgvector, Redis, Docker, SQLAlchemy, and Alembic, implementing consent, structured intake, audit logging, and safety\-aware decision\-support boundaries for substance\-use recovery workflows\.

# 12\. Jobpilot Integration: CareerContextView

Jobpilot should not directly search the entire second brain\. It should query a CareerContextView: a filtered, permission\-scoped, provenance\-backed projection over approved or reviewable career memories\.

SecondBrainContextGraph  
 \-> CareerContextView  
    \- approved project memories  
    \- candidate problem spaces  
    \- candidate results  
    \- timelines  
    \- target\-role preferences  
    \- interview feedback  
    \- excluded sensitive context removed  
 \-> Jobpilot Project Story compiler

__Jobpilot query__

__Purpose__

get\_project\_context\(project\_id\)

Retrieve approved/candidate context for one project\.

get\_possible\_problem\_spaces\(project\_id\)

Find or elicit why the project mattered\.

get\_possible\_results\(project\_id\)

Find outcomes across notes, logs, docs, chats\.

get\_related\_sources\(project\_id\)

List evidence sources across Drive/GitHub/chats\.

get\_timeline\(project\_id\)

Reconstruct project sequence and deliverables\.

get\_best\_projects\_for\_role\(role\)

Rank stories for a target job\.

get\_sensitive\_project\_view\(project\_id, disclosure\_mode\)

Return the redacted, approved project view for a sensitive\-domain project without exposing raw sensitive sources\.

get\_retrieval\_snapshot\(snapshot\_id\)

Retrieve the locked job\-specific evidence package used for generation\.

create\_retrieval\_snapshot\(job\_posting\_hash\)

Perform one bounded local retrieval against Career Index and freeze the result\.

refresh\_retrieval\_snapshot\(snapshot\_id\)

User\-initiated refresh only; shows budget preview and creates a new snapshot version\.

__Anti\-slop rule__  
Do not let Jobpilot ask: “search everything and write my resume\.”  
  
Let the Second Brain extract candidate memories\. Let Jobpilot compile approved career context into Project Stories\.

# 13\. Jobpilot V4 UI and Application Architecture

The v4 product should be intentionally narrow\. It should not try to become a full job\-search automation platform yet\. It should provide a dashboard where the user stores the Master CV, enters or pastes a job posting, and clicks one clear action: Create Optimized Resume\. Scraping should be deferred to v5\.

Jobpilot V4  
 UI Layer  
  \-> Dashboard  
  \-> Master CV storage/import  
  \-> Job posting input field or link field  
  \-> Extracted requirements view  
  \-> Matched Project Story cards  
  \-> Create Optimized Resume button  
  \-> Resume preview \+ human review \+ export  
  
 Application Layer  
  \-> Python services for parsing, scoring, matching, and document generation  
  \-> JavaScript/TypeScript frontend for dashboard and review UX  
  \-> CareerContextView client  
  \-> Master CV snapshot reader  
  \-> Project ranker  
  \-> Resume compiler

__Layer__

__Responsibilities__

__Non\-negotiable constraints__

UI layer

Dashboard, master CV import/storage, job\-posting input, matched projects, review panel, export\.

Expose project cards and traceability; never expose raw claim queues as the main workflow\.

Job parser

Extract title, seniority, company, required skills, preferred skills, responsibilities, ATS terms, and domain signals\.

Manual job text input is sufficient for v4; scraping waits for v5\.

Matching layer

Cross\-reference job posting against Master CV and CareerContextView\.

Rank approved or reviewable project stories; do not search full\-brain context\.

Resume optimizer

Build an optimized resume using seniority match, ATS match, skill overlap, domain relevance, project leverage, and evidence strength\.

Every selected factual sentence must trace to an approved story component or explicit attestation\.

Project selector

Search the resume/project inventory and select the strongest grounded projects for the job\.

Target the top four grounded projects unless the role or resume format requires otherwise\.

Export layer

Generate DOCX/PDF resume snapshot after user review\.

No incomplete or unapproved story renders\.

Sensitive disclosure gate

Classify sensitive\-domain projects, select technical\_only/domain\_context\_allowed/personal\_origin\_allowed/private\_do\_not\_use, and bind approvals to specific output types\.

Deny by default; never let raw recovery/medical/private context flow into Jobpilot outputs\.

Cost and retrieval controller

Dry\-run audits, token budgets, source caps, local Career Index, and locked RetrievalSnapshots\.

No runtime raw\-source search; no model\-controlled repeated retrieval\.

## 13\.1 V4 workflow

User saves or uploads Master CV  
 \-> User enters/pastes job posting or optional job link  
 \-> System extracts job requirements  
 \-> System cross\-references requirements against Master CV \+ CareerContextView  
 \-> System scores projects by seniority match, ATS match, skill match, evidence strength, and narrative fit  
 \-> System selects the strongest grounded projects, typically top 4  
 \-> System creates optimized resume draft  
 \-> User reviews evidence, edits, approves, and exports

__V4 scoping decision__  
Jobpilot v4 should optimize the resume from approved career context\. It should not scrape job boards, auto\-apply, or perform broad company research\. Those functions belong in v5 or later\.

# 14\. Repo/Fork Recommendation

If forking one repository, the best starting point is Graphiti\. The reason is architectural: the hard problem is not generic document search; it is entity\-centered, temporal, provenance\-backed memory\. Graphiti is closer to a temporal knowledge graph substrate than Onyx, Mem0, Khoj, or generic RAG tools\.

__Repo__

__Best for__

__Why not the full solution__

Graphiti

Temporal entity graph / context substrate\.

Needs custom approval states, app scopes, source adapters, and Jobpilot Project Stories\.

Onyx

Connectors and enterprise search patterns\.

Document search center of gravity; less suited as canonical typed memory graph\.

Mem0 / OpenMemory

Cross\-agent persistent memory\.

Too generic for project/evidence/attestation semantics\.

Khoj / Reor / AnythingLLM

Personal knowledge UI and semantic note search\.

Closer to AI knowledge base than typed context substrate\.

Rowboat

Work graph inspiration\.

Reference architecture, not proven fit for the complete system\.

__Fork decision__  
Fork Graphiti\. Add source adapters, typed memory extraction, approval/attestation states, app\-scoped permissions, CareerContextView, and Jobpilot Project Story integration\.

# 15\. Data Model Blueprint

## 15\.1 Second Brain core entities

__Entity/table__

__Purpose__

sources

Registry of raw files, conversations, repos, chats, docs, and exports\.

source\_chunks

Normalized text spans with offsets, hashes, and source references\.

entities

People, organizations, projects, tools, topics, companies\.

entity\_aliases

Alternate names, abbreviations, repo names, informal references\.

memories

Typed candidate/approved facts, decisions, preferences, events, outcomes\.

memory\_evidence

Links memories to source chunks, conversations, commits, or attestations\.

attestations

User\-provided confirmations, corrections, and outcomes\.

app\_context\_views

Scoped projections for Jobpilot, planning, learning, recovery, etc\.

permissions

Which apps may use which memory classes\.

sensitivity\_labels

Classification metadata for memory classes such as career, recovery, medical, dating/private, and technical artifact in sensitive domain\.

redacted\_memory\_variants

Career\-safe summaries derived from sensitive sources, with source links preserved but raw sensitive text excluded from app views\.

source\_inventory

Metadata\-first source registry: title, URI, type, dates, MIME type, size, estimated tokens, hashes, sensitivity class, app scope, ingestion status\.

ingestion\_runs

Tracks estimated/actual tokens, estimated/actual cost, max budget, status, source type, start/end times, and failure reason\.

source\_budget\_policies

Per\-source caps for embed tokens, extract tokens, max spend, confirmation threshold, runtime retrieval permission, and sensitive default\.

duplicate\_groups

Groups equivalent or near\-equivalent exports, copied docs, generated PDFs, and repeated resumes before embedding/extraction\.

retrieval\_snapshots

Locked job\-specific evidence package: job hash, Career Index version, permission scope version, selected projects, evidence IDs, token budget, and lock state\.

## 15\.2 Jobpilot\-specific entities

__Entity/table__

__Purpose__

project\_capsules

One canonical project container per real\-world project/workstream\.

problem\_candidates

Candidate Problem Spaces with evidence/attestation status\.

action\_candidates

Strategic actions and technical implementation details\.

result\_candidates

Evidence\-backed or attestation\-needed outcomes\.

project\_story\_readiness

Derived readiness struct, not human approval\.

project\_story\_reviews

Human approval/rejection/exclusion decisions\.

approved\_project\_stories

Canonical durable career stories\.

master\_cv\_entries

Structured downstream entries derived from approved stories\.

resume\_bullet\_candidates

Generated renderings, never canonical truth\.

quarantined\_artifacts

Invalid or low\-confidence extractions retained for debugging\.

job\_postings

Raw pasted job descriptions, optional links, extracted requirements, and target\-role metadata\.

job\_requirement\_features

Parsed skills, seniority, domain, responsibilities, ATS terms, and scoring inputs\.

project\_role\_scores

Match scores between job posting requirements and approved Project Stories\.

optimized\_resume\_snapshots

Generated job\-specific resume drafts that point back to approved stories and score rationale\.

sensitive\_project\_profiles

SensitiveCareerProject metadata: default visibility, disclosure modes, redaction requirements, and app scopes\.

disclosure\_approvals

Artifact\-specific approvals for sensitive disclosures; distinguishes technical\_only, domain\_context\_allowed, and personal\_origin\_allowed\.

career\_project\_index

Materialized local index of approved/candidate career memories, project capsules, skills, tools, domains, seniority signals, and evidence refs\.

retrieval\_snapshot\_events

Audit trail for creation, reuse, regeneration, and user\-initiated refresh of snapshots\.

generation\_budget\_events

Per\-output accounting: input tokens, output tokens, model tier, snapshot ID, and estimated cost\.

__Critical modeling correction__  
Separate readiness from approval\. Readiness is machine\-derived\. Approval is a human decision\. A story can be resume\_ready but not approved; it still must not render\.

# 16\. Implementation Roadmap

__Phase__

__Scope__

__Exit criteria__

0A \- Cost envelope and retrieval budget

Add local Career Index, source budget policies, dry\-run audits, source hashing, dedupe, token caps, and RetrievalSnapshot lock\.

A job posting can be processed with one deterministic retrieval snapshot; regeneration reuses it; no generation path can trigger raw\-source search\.

0B \- Universal source adapter contract

Apply the same metadata\-first, cost\-first, sensitivity\-first contract to ChatGPT, Claude, Perplexity, Drive, and GitHub\.

No source bypasses inventory, token estimate, dedupe, budget, and privacy gates\.

0 \- Stop user\-facing slop

Close legacy/V1/fallback paths; keep integrity flags blocking; prevent incomplete stories from rendering\.

No unapproved/incomplete content can reach Master CV or outbound prose\.

1 \- Project Capsule foundation

One confirmed entity/project appears once; deterministic cross\-entity duplicate checks; unassigned evidence surfaced\.

One project card per project; no file\-shaped experiences\.

2 \- Story domain layer

Pure readiness struct, targeted questions, leverage ranking, validation gates\.

Offline tests prove missing Problem/Result cannot become resume\-ready\.

3 \- Project\-level review UX

Story cards; answer/edit/approve/exclude/portfolio decisions; no raw claim queue as primary UI\.

Review surface is small and tolerable\.

4 \- Master CV generation

Build snapshot only from approved complete Project Stories\.

No duplicate sections; no incomplete projects; all numbers trace\.

5 \- V4 resume optimization

Dashboard, master CV storage, pasted job posting, requirement extraction, project scoring, top\-project selection, optimized resume preview\.

A job\-specific resume can be generated from approved context with no scraping dependency\.

6 \- Tailoring/outreach

Adapters from approved stories to tailored outputs; metric/evidence gates for all outbound prose\.

No factual sentence without approved story component\.

6a \- Sensitive career evidence policy

Add SensitiveCareerProject profile, disclosure modes, redacted public story variants, and artifact\-specific approval checks\.

AI Recovery Navigation can render as technical\_only; personal sobriety origin cannot render unless explicitly approved for that output\.

7 \- Second Brain substrate

Graphiti fork; source registry; memory candidates; approval/app\-scope; CareerContextView\.

Jobpilot can query approved career context without full\-brain access\.

8 \- Broader ingestion

Add ChatGPT/Claude/Perplexity/Drive/GitHub/Docs adapters progressively\.

Messy sources produce candidates/questions, not corrupted truth\.

9 \- V5 automation

Job posting scraping, job\-board ingestion, company research, application tracking, and workflow automation\.

Automation improves throughput without bypassing project\-story gates\.

# 17\. Acceptance Criteria and Test Harness

The most important lesson from the V2/V3 audits is that tests must resemble the real corpus\. Do not rely on clean fixture triplets\. The test corpus should include duplicate resumes, multi\-project documents, GitHub repos without Problems, projects with Actions but no Results, stale inflated sources, and cross\-source duplicates\.

__Test__

__Expected behavior__

148 raw claims collapse

A small number of Project Story cards, bounded by confirmed project count\.

Same project from resume \+ repo \+ notes

One Project Story, not multiple cards or CV sections\.

No Problem

needs\_problem, targeted question, no render\.

No Result

needs\_result, targeted question, no render\.

Technical GitHub demo

portfolio\_inventory or needs\_problem unless context is approved\.

Cross\-project metric

Quarantined or blocked; cannot render\.

Duplicate Result span

Detected before final CV; cannot render twice\.

Unapproved story

Cannot feed Master CV, tailoring, outreach, or interview prep\.

Outbound outreach metric

Every number must trace to approved evidence/attestation\.

Sensitive memory leakage

Jobpilot cannot access private/recovery/dating/medical context by default\.

V4 job posting input

Pasted job text extracts requirements without requiring scraping\.

Top\-project resume build

Optimized resume uses strongest grounded Project Stories for the job, not arbitrary master\-CV bullets\.

Sensitive technical project

Renders as technical\_only by default; no personal recovery disclosure appears\.

Personal origin not approved

The project can be used technically, but sobriety/addiction origin text is blocked\.

Personal origin approved for one artifact

Disclosure appears only in that artifact; it does not become global career truth\.

Product efficacy overclaim

Claims like app got people sober or app treated addiction are blocked unless supported by approved outcome evidence\.

Dry\-run required

Ingestion run cannot start paid extraction until item count, token estimate, duplicate count, sensitive count, and max spend are calculated\.

Budget exceeded

Run fails closed or asks for explicit confirmation; it does not silently continue\.

Duplicate Drive docs

\.docx, Google Doc, and PDF copies are grouped before embedding/extraction\.

Runtime raw\-source search

Resume generation cannot search ChatGPT, Claude, Perplexity, Drive, or GitHub directly\.

Regenerate resume

Uses the same locked RetrievalSnapshot; no additional search occurs\.

Perplexity research as career evidence

Blocked unless attached to a project decision; research notes cannot become accomplishments\.

Claude chat vs Claude Code evidence

Committed code/docs/tests outrank chat reasoning as evidence\.

__Evaluation principle__  
The test harness should prove that bad inputs become questions, quarantine entries, or exclusions \- never polished career prose\.

# 18\. Risk Register and Guardrails

__Risk__

__Failure mode__

__Guardrail__

Context sludge

Second Brain becomes RAG over everything\.

Typed memories, entity graph, approval states, app scopes\.

LLM\-composed truth

Model writes plausible Problem Space unsupported by evidence\.

Show evidence quotes; require approval/attestation; no automatic canon\.

Review explosion

User sees raw claims/debug flags\.

One Project Story card per project; debug mode separate\.

Duplicate projects

Same project appears multiple times\.

Cross\-source/project dedupe before review and before render\.

V1/fallback leakage

Legacy or fallback path generates output\.

Fail\-closed guards and tests for all outbound paths\.

Privacy breach

Sensitive conversations leak into career materials\.

App\-scoped context views and deny\-by\-default sensitive categories\.

Overengineering

Build graph/LLM/UX before gates\.

Phase 0 mechanical enforcement first\.

Overtrusting source resumes

Stale or inflated resume wording passes verbatim gates\.

Conflict/staleness detection and targeted user confirmation\.

Premature scraping

Scraping work distracts from career\-story correctness\.

Defer scraping to v5; v4 uses manual job posting input\.

Resume optimizer slop

System picks projects based on keyword overlap but weak evidence\.

Score by ATS match, seniority match, evidence strength, result quality, and narrative fit\.

Sensitive context leakage

Recovery, medical, therapy, or private history appears in career output by accident\.

Deny\-by\-default memory classes, SensitiveCareerProject gate, redacted variants, and artifact\-specific approval\.

Mission\-story overdisclosure

A powerful personal origin story is used too broadly or in the wrong professional context\.

Per\-output disclosure modes and preview warnings before export\.

Efficacy overclaim

Personal sobriety or product domain gets converted into unsupported clinical/product effectiveness claims\.

Separate personal outcome evidence from product efficacy evidence; block unsupported clinical claims\.

API cost overrun

Bulk ingestion or generation runs consume unexpectedly high token/tool budgets\.

Dry\-run audit, source budget policies, hard caps, confirmation thresholds, and cost logging\.

Hosted search loop

Model repeatedly searches raw sources or hosted file search during generation\.

No model\-controlled search tools; local Career Index; locked RetrievalSnapshot; explicit refresh only\.

Drive sludge

Random PDFs, duplicates, private files, and old coursework pollute the career index\.

Metadata\-first Drive inventory, dedupe, allowlists, sensitivity filters, and exclusion defaults\.

Perplexity truth laundering

External research summary becomes a career accomplishment\.

Research memories require source citation and project linkage; cannot become personal evidence by itself\.

Claude reasoning treated as implementation fact

Planning chat gets mistaken for work actually done\.

Prefer commits, files, tests, and accepted artifacts; Claude chat creates candidate decisions only\.

Hidden repeated extraction

Regeneration triggers extraction or retrieval again without user awareness\.

Snapshot reuse tests, generation budget events, and no implicit refresh path\.

# 19\. Decision Register

__Decision__

__Status__

__Rationale__

Jobpilot core object = Project Story

Adopt

Solves the wrong\-review\-object failure\.

Claims are internal inventory

Adopt

Claims support stories but should not be primary UX\.

No complete PAR, no Master CV inclusion

Adopt

Prevents incomplete projects from becoming polished slop\.

Separate readiness and approval

Adopt

Machine readiness is not human authorization\.

Direct RAG over all data

Reject

Creates context sludge and trust boundary violations\.

Manual Drive cleanup as product solution

Reject

System should handle messy bounded corpus through triage and quarantine\.

Graphiti as fork base

Adopt

Best fit for temporal/entity\-centered context graph\.

Onyx as primary fork

Reject/defer

Useful connector reference, wrong central abstraction\.

LLM synthesis first

Reject

Gates and story mechanics must be correct before prose quality layer\.

Second Brain connected to Jobpilot

Adopt

Second Brain supplies candidate context; Jobpilot compiles approved career context\.

Claude \+ Obsidian as human\-facing second\-brain layer

Adopt

Matches the intended personal knowledge workflow while preserving structured backend controls\.

Jobpilot v4 scraping

Defer

Manual/pasted job posting input is enough to validate matching and resume optimization\.

Top grounded projects for each role

Adopt

Optimized resume should select the best\-fit Project Stories, typically top four, rather than remixing the entire CV\.

Sensitive career evidence explicit promotion

Adopt

Allows high\-value technical/mission projects from sensitive domains while preventing raw private context leakage\.

Universal source ingestion guardrails

Adopt

Keeps ChatGPT, Claude, Perplexity, Drive, and GitHub economically bounded and privacy\-safe\.

One locked RetrievalSnapshot per job posting

Adopt

Prevents agentic re\-search loops and makes per\-job generation predictable\.

Local Career Index over hosted runtime search

Adopt

Moves cost to controlled indexing and avoids repeated raw\-source search at generation time\.

# 20\. Obsidian\-First Raw Markdown Archive and MVP Ingestion Contract

Correction: Obsidian is not merely an optional note\-taking UI\. For the MVP, Obsidian is the raw Markdown archive, curated evidence workspace, and staging layer between raw source systems and Jobpilot\. The prior source\-adapter plan remains valid for later phases, but it should not be the first implementation path\.

Raw sources  
ChatGPT / Claude Chat / Claude Code / Perplexity / Google Drive / GitHub  
        \->  
Obsidian raw Markdown archive  
        \->  
Local index, tags, frontmatter, wikilinks, dedupe  
        \->  
Career\-scoped Obsidian evidence notes  
        \->  
Selective Opus extraction / Project Story construction  
        \->  
Jobpilot approved CareerContextView

Hard invariant: importing everything into Obsidian is permitted; extracting everything from Obsidian with Opus is prohibited by default\. Raw Obsidian notes are searchable and auditable, but they are not canonical career truth\.

## 20\.1 Obsidian Vault Zones

__Vault zone__

__Purpose__

__Jobpilot rule__

00\_Raw\_Archive

Raw converted exports from ChatGPT, Claude, Claude Code, Perplexity, Google Drive, and GitHub\.

Searchable only\. Not ingested by Jobpilot by default\. No Opus full\-vault extraction\.

10\_Career\_Evidence

Curated career/project notes, work logs, selected source excerpts, interviews, portfolio materials, and evidence notes\.

Default Jobpilot ingestion zone when frontmatter permits it\.

20\_JobPilot\_Canonical

Reviewed Project Stories, approved career context, sensitive disclosure decisions, and Master CV source entries\.

Canonical input to resume generation\. Only approved complete stories can render\.

30\_Runtime\_Artifacts

Job descriptions, RetrievalSnapshots, generated resume runs, exports, and review artifacts\.

Runtime outputs\. Never becomes canonical evidence automatically\.

Recommended folder shape:

ObsidianVault/  
  00\_Raw\_Archive/  
    ChatGPT/  
    Claude/  
    Claude\_Code/  
    Perplexity/  
    Google\_Drive/  
    GitHub/  
  10\_Career\_Evidence/  
    Projects/  
    Evidence/  
    Work\_Logs/  
    Interviews/  
    Resume\_Source/  
  20\_JobPilot\_Canonical/  
    Project\_Stories/  
    Approved\_CareerContext/  
    SensitiveCareerProjects/  
  30\_Runtime\_Artifacts/  
    Job\_Postings/  
    RetrievalSnapshots/  
    Resume\_Runs/

## 20\.2 Markdown Frontmatter Contract

Jobpilot should treat Obsidian as a structured Markdown database\. Every note can be parsed locally, but only notes with explicit career metadata should be eligible for Project Story extraction or resume use\.

\-\-\-  
source\_type: chatgpt | claude | claude\_code | perplexity | google\_drive | github | manual  
source\_uri: optional\_original\_reference  
created: 2026\-07\-06  
updated: 2026\-07\-06  
project\_id: cooper\_pacifica\_automation  
career\_relevance: high | medium | low | unknown  
sensitivity: career\_public | sensitive\_career | private\_do\_not\_use | unknown  
sensitivity\_mode: career\_public | technical\_only | domain\_context\_allowed | personal\_origin\_allowed | private\_do\_not\_use  
jobpilot\_ingest: true | false  
ingestion\_status: raw\_archive | candidate\_evidence | extracted\_signal | approved\_story | rejected | superseded  
evidence\_type: work\_log | architecture\_note | repo\_doc | interview\_feedback | source\_excerpt | user\_attestation  
\-\-\-

__Field__

__Meaning__

__Hard rule__

jobpilot\_ingest

Explicit allow flag for MVP ingestion\.

Default false for raw archive notes\.

project\_id

Binds evidence to one canonical project\.

Required for direct Project Story extraction\.

career\_relevance

High\-recall triage field\.

High/medium eligible; low ignored unless manually promoted\.

sensitivity

Privacy class of the note\.

private\_do\_not\_use is always blocked\. unknown requires review\.

sensitivity\_mode

Disclosure mode for sensitive\-career projects\.

technical\_only is the default safe mode\.

ingestion\_status

Lifecycle state inside Obsidian/Jobpilot\.

Only approved\_story can feed Master CV/resume outputs\.

## 20\.3 Default Ingestion Filter

Jobpilot MVP should not crawl the whole vault\. It should read a configured allowlist of folders and notes\. Raw archive search is an explicit user action, not default runtime behavior\.

__Filter rule__

__Scope__

__Behavior__

Default include

10\_Career\_Evidence/\*\* and 20\_JobPilot\_Canonical/\*\*

Only when jobpilot\_ingest: true or ingestion\_status is candidate\_evidence/approved\_story\.

Default exclude

00\_Raw\_Archive/\*\*

Searchable locally but not sent to Opus or used in resume generation by default\.

Sensitive block

sensitivity: private\_do\_not\_use or sensitivity: unknown

Blocked until manually reviewed and promoted\.

Project binding requirement

project\_id must be present for direct extraction\.

Unbound notes become review tasks, not resume evidence\.

Full\-vault Opus extraction

Prohibited by default\.

Requires explicit cost estimate, explicit approval, and a hard budget cap\.

## 20\.4 MVP Pipeline

__Step__

__Operation__

__Guardrail__

1 \- Raw import

Convert source exports into Markdown files in 00\_Raw\_Archive\.

No LLM required\. Preserve source metadata and original references\.

2 \- Local inventory

Parse Markdown/frontmatter, compute hashes, estimate tokens, group duplicates\.

No Opus call\. Output an audit report\.

3 \- Career triage

Promote selected notes or excerpts into 10\_Career\_Evidence\.

Manual or cheap local/keyword classification\.

4 \- Selective extraction

Run Opus only on eligible career notes or known project folders\.

Cost\-visible, batched, capped, and never full\-vault by default\.

5 \- Project Story compile

Merge extracted signals into PAR Project Story cards\.

No complete PAR, no resume inclusion\.

6 \- Human approval

Approve, edit, exclude, or mark portfolio\-only\.

No human approval, no CareerContextView\.

7 \- Resume runtime

Paste job posting, rank approved stories, generate resume from locked snapshot\.

No raw archive search at generation time\.

## 20\.5 Cost Policy for Obsidian\-Based Ingestion

Moving raw context into Obsidian should be treated as a local archival operation, not an extraction operation\. Costs only become meaningful when selected notes are sent to Opus for structured career\-signal extraction\.

__Operation__

__Expected cost band__

__Architecture decision__

Import everything raw into Obsidian

$0\-$50

Parser/converter work; no model extraction required\.

Local index, hash, dedupe, frontmatter audit

$0\-$50

Can be implemented in Python locally\. Embeddings are optional\.

Top 10\-15 curated project/evidence notes

$25\-$100

Best MVP path\. High signal, low cost\.

Career\-relevant Obsidian subset

$100\-$300

Reasonable expanded pass after MVP proves value\.

Broad career\-signal sweep across Obsidian

$300\-$750

Only after token audit and budget approval\.

Whole raw vault Opus extraction

$1,000\-$2,000\+

Prohibited by default; not needed for MVP\.

## 20\.6 Data Model Additions

__Entity/table__

__Purpose__

obsidian\_notes

One row per Markdown file: path, title, frontmatter, source\_type, hash, estimated\_tokens, modified\_at\.

obsidian\_links

Wikilinks and backlinks between projects, evidence notes, source notes, and runtime artifacts\.

obsidian\_ingestion\_policies

Folder allowlists, exclusion patterns, frontmatter requirements, budget caps, and sensitivity defaults\.

obsidian\_note\_states

raw\_archive, candidate\_evidence, extracted\_signal, approved\_story, rejected, superseded\.

career\_signal\_candidates

Structured extracted signals from eligible Obsidian notes, linked to project\_id and source note path\.

project\_story\_cards

Compiled PAR cards generated from approved or reviewable career signals\.

## 20\.7 Acceptance Tests

__Test__

__Expected behavior__

Raw archive ignored by default

A note under 00\_Raw\_Archive with no jobpilot\_ingest flag is not sent to Opus and cannot feed a resume\.

Career note eligible

A note under 10\_Career\_Evidence with project\_id and jobpilot\_ingest: true becomes extraction\-eligible\.

Sensitive unknown blocks

A note with sensitivity: unknown cannot render into Project Story output until reviewed\.

Technical\-only sensitive project

AI Recovery Navigation can render as technical\_only while personal origin language remains blocked\.

Full\-vault extraction blocked

Attempting to run Opus over the whole vault fails closed unless explicit approval and budget cap are present\.

Runtime raw search blocked

Resume generation cannot search 00\_Raw\_Archive unless the user starts an explicit evidence\-expansion workflow\.

## 20\.8 Decision Update

__Decision__

__Status__

__Rationale__

Obsidian as MVP staging substrate

Adopt

Raw source systems already consolidate into Obsidian; direct source adapters are not required for the first Jobpilot MVP\.

Direct raw\-source ingestion for MVP

Reject/defer

It creates unnecessary connector, cost, and privacy complexity\.

Whole\-vault Opus extraction

Reject by default

Importing raw Markdown is cheap; full Opus extraction remains expensive and unnecessary\.

Jobpilot default source = career\-scoped Obsidian folders

Adopt

The MVP should parse curated Markdown and canonical Project Story notes first\.

Raw archive as evidence reserve

Adopt

Raw notes remain locally searchable for evidence expansion but do not become canonical automatically\.

Updated final architecture sentence: Build an Obsidian\-first career compiler\. Import all raw context into Obsidian as local Markdown, promote only career\-relevant notes into career evidence folders, run selective Opus extraction under explicit cost gates, and let Jobpilot compile only approved Project Stories into resumes\.

# Appendix A\. Prompting Strategy

Prompts should force Claude to define the problem space before architecture\. The most useful prompt pattern is not “extract claims” but “construct one coherent Project Story per project\.”

For each project:  
 1\. Define the actual Problem Space\.  
 2\. Select Actions as the highest\-leverage steps taken to remedy that Problem Space\.  
 3\. Select Results as evidence that the remedy worked\.  
 4\. If Problem or Result is missing, ask a targeted question\.  
 5\. If complete and approved, generate candidate resume bullets from the selected components only\.

__Prompt anti\-pattern__

__Better instruction__

Extract Problems, Actions, Results from docs\.

Define each project’s Problem Space, then select Actions/Results that belong to that story\.

Review all extracted claims\.

Review one Project Story card per confirmed project\.

Use all context to write a resume\.

Use only approved CareerContextView memories and approved Project Stories\.

Fix validator warnings\.

Classify fatal vs repairable failures; convert repairable missing fields into targeted questions\.

Scrape this job and optimize everything\.

For v4, use the pasted job posting, extract requirements, rank approved Project Stories, and generate a traceable resume draft\.

Use my recovery context to strengthen the resume\.

Classify the project disclosure mode first; use technical\_only by default, and ask for explicit approval before any personal\-origin wording\.

Search my whole second brain and write the resume\.

Use only the approved CareerContextView and the locked RetrievalSnapshot for this job\.

Ingest everything from Drive/Claude/Perplexity\.

Run a dry\-run audit, classify, dedupe, estimate cost, and ask for confirmation before extraction\.

# Appendix B\. Minimal Next Build Spec

__Build this next__  
A mechanical Project Story gate and review layer that works without new LLM synthesis\. If this cannot prevent slop offline, more model calls will only hide the problem\.

1. Remove or fail\-close any legacy/fallback path that can create user\-facing content without approved stories\.
2. Implement ProjectStoryReadiness as a pure domain function over existing entity/claim/evidence data\.
3. Separate readiness from review\_status in the schema/API\.
4. Create one Project Story card per confirmed project/entity\.
5. Derive targeted questions for missing Problem, Action, or Result\.
6. Add server\-side approval checks: incomplete stories cannot be approved as Master CV material\.
7. Rewrite Master CV snapshot generation to consume only approved complete Project Stories\.
8. Add tests for no Problem, no Result, duplicate project, cross\-project metric, unapproved story, and outbound prose traceability\.
9. Implement the v4 dashboard path: master CV input, pasted job posting input, extracted requirements, project ranking, optimized resume preview, and export\.
10. Defer scraping to v5\. Do not block v4 on job\-board ingestion\.
11. Only after those pass, add LLM synthesis as a quality layer behind the same gates\.
12. For the MVP, defer the Second Brain fork and broad source adapters\. Build the Obsidian vault parser first: read local Markdown, YAML/frontmatter, wikilinks, project\_id, sensitivity\_mode, and jobpilot\_ingest flags\.
13. Add source adapters progressively later as raw Markdown importers into Obsidian\. Jobpilot should not depend on direct ChatGPT, Claude, Perplexity, Drive, or GitHub connectors for the MVP\.
14. Add SensitiveCareerProject modes and deny\-by\-default disclosure gates before using recovery/medical/private projects in Jobpilot\.
15. Add tests proving AI Recovery Navigation can render as a technical project while personal sobriety\-origin wording is blocked unless explicitly approved\.
16. Add universal source ingestion guardrails: metadata inventory, token estimate, hash/dedupe, sensitivity classification, budget check, scoped extraction, and approval\.
17. Add source\_budget\_policies, ingestion\_runs, source\_inventory, duplicate\_groups, career\_project\_index, and retrieval\_snapshots tables before broad ingestion\.
18. Enforce one locked RetrievalSnapshot per job posting and prohibit model\-controlled raw\-source search at generation time\.

__Closing Principle__  
Build one personal context substrate\. Expose scoped, approved context views to specialized apps\. Let Jobpilot compile career\-safe Project Stories from CareerContextView\. Never let raw source text, unapproved claims, or LLM\-generated summaries become truth\.
