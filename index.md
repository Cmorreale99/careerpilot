---
title: CareerPilot
description: CareerPilot turns scattered career evidence into structured, evidence-backed career profiles for career advisors and their clients.
---

# CareerPilot

## Turn scattered career evidence into a complete, evidence-backed career profile.

CareerPilot helps career advisors understand the full scope of a client’s capabilities by organizing scattered professional experience, projects, hackathons, technical work, and other career evidence into a structured Career portfolio.

**Functional local MVP · Preparing for pilot validation**

[View the product demo](#product-demo) · [Join the pilot](#pilot-interest) · [View the technical documentation](README.md)

---

## The Problem

### Traditional résumés show only a fraction of what someone can do.

Career evidence is often scattered across:

- Résumés and cover letters
- Project documentation
- GitHub repositories
- Presentations and reports
- Internship deliverables
- Hackathon submissions
- Academic work
- Personal notes and career documents

Most of this information never reaches a career advisor.

A one- or two-page résumé compresses years of work into a small number of bullets. Important context is lost, including:

- The problems a candidate solved
- The decisions they made
- The technologies they used
- The complexity of their work
- The measurable or potential business value
- The patterns connecting experiences across different roles and projects

As a result, career advisors may be forced to make recommendations using incomplete information.

They may overlook strong accomplishments, misunderstand a client’s technical depth, recommend poorly matched roles, or fail to identify the most compelling professional narrative.

---

## The Solution

### CareerPilot creates a structured career intelligence layer.

CareerPilot transforms user-selected career materials into a comprehensive Career Profile.

Instead of immediately generating another résumé, CareerPilot first builds an organized representation of the user’s complete body of work.

The Career Profile gives career advisors a clearer view of:

- What the client has worked on
- Which problems they have solved
- What actions they personally took
- Which technologies and methods they used
- What results or business value they produced
- Which capabilities appear repeatedly across their experience
- Which roles may best match their demonstrated strengths
- Which career artifacts should be emphasized in applications and interviews

CareerPilot is designed to support career professionals, not replace them.

The product gives advisors better evidence so they can provide more informed, personalized guidance.

---

## Who CareerPilot Is For

CareerPilot is being designed for organizations and professionals that help people navigate their careers, including:

- College and university career centers
- Independent career coaches
- Workforce-development organizations
- Technical bootcamps and training programs
- Neurodiversity employment programs
- Early-career development programs
- Outplacement and career-transition services

The initial focus is on career advisors working with students, early-career professionals, technical candidates, and people with broad or nonlinear experience.

---

## How It Works

### 1. Curate career evidence

The user selects the documents and project materials they want CareerPilot to analyze.

CareerPilot does not require unrestricted access to the user’s entire Google Drive or personal file system.

The user remains in control of what enters the system.

### 2. Build the career evidence repository

Supported files are converted into structured source material and organized inside an Obsidian-based second brain.

This repository becomes the source of truth for the user’s career evidence.

### 3. Identify career artifacts

CareerPilot organizes the evidence into distinct career artifacts, such as:

- Professional experiences
- Personal projects
- Academic projects
- Hackathons
- Research
- Volunteer work
- Other relevant accomplishments

Each artifact remains separate so that evidence from unrelated projects or experiences is not incorrectly combined.

### 4. Deduplicate and assign evidence

CareerPilot identifies repeated evidence and associates each piece of information with the appropriate career artifact.

This creates a cleaner, more reliable representation of the user’s body of work.

### 5. Generate structured career narratives

Each career artifact receives its own structured narrative describing:

- The problem or opportunity
- The user’s actions
- The technical approach
- Important architectural or strategic decisions
- The results
- The measurable or potential business value

### 6. Construct the Career Profile

CareerPilot combines the artifact-level narratives into a comprehensive Career Profile.

The final output gives career advisors a detailed but organized view of the client’s professional capabilities.

### 7. Support career strategy

The advisor can use the Career Profile to:

- Identify target roles
- Surface overlooked strengths
- Improve positioning
- Select the strongest career stories
- Develop application materials
- Prepare the client for interviews
- Recommend areas for further development

---

## Example Output

A Career Profile may include sections such as:

### Professional Experience

A structured overview of each job, internship, contract, or volunteer experience, including the problems addressed, actions taken, technologies used, and resulting value.

### Projects

A detailed record of personal, academic, technical, and entrepreneurial projects.

### Hackathons

Evidence of rapid product development, teamwork, ideation, technical execution, and presentation ability.

### Technical Capabilities

Capabilities demonstrated across multiple artifacts, supported by concrete evidence rather than self-reported skill ratings.

### Career Themes

Patterns connecting the user’s experiences, such as:

- Applied AI product development
- Data engineering
- Workflow automation
- Technical problem solving
- Customer discovery
- Product strategy
- Cross-functional communication

### Role Alignment

Potential role categories based on demonstrated experience, recurring capabilities, and the types of problems the user has solved.

---

## Why CareerPilot Is Different

### Evidence-backed

CareerPilot works from concrete career artifacts rather than relying only on questionnaires, memory, or self-reported skill lists.

### Advisor-centered

The product is designed to improve the quality of human career guidance.

CareerPilot helps advisors understand their clients more deeply instead of attempting to replace the advisor-client relationship.

### Career profile before résumé generation

Most career tools start by trying to produce a résumé.

CareerPilot starts earlier in the process by organizing the underlying evidence first.

Once the evidence layer is reliable, it can support résumés, interviews, portfolios, career coaching, role targeting, and other downstream use cases.

### User-controlled data access

Users manually select the files CareerPilot may process.

The MVP intentionally avoids searching through an entire personal drive, reducing privacy risk, implementation complexity, and irrelevant data ingestion.

### Artifact-level separation

CareerPilot treats every experience, project, and hackathon as its own career artifact.

This reduces the risk of combining evidence from unrelated work.

### Local AI inference

The MVP uses Ollama for local model inference.

This approach reduces recurring API costs and allows sensitive career materials to remain under greater local control during early product validation.

### Designed for complex career histories

CareerPilot is particularly relevant for people whose capabilities are difficult to represent through a conventional résumé, including:

- Technical generalists
- Career changers
- Students with substantial project experience
- Candidates with nonlinear work histories
- Neurodivergent professionals
- Founders and independent builders
- People whose strongest work exists outside formal employment

---

## Product Principles

CareerPilot is being developed around several core principles.

### The evidence layer comes first

Downstream career recommendations are only as reliable as the information used to generate them.

CareerPilot prioritizes the quality, organization, and traceability of career evidence before adding more automation.

### Users define their career artifacts

The user determines which experiences and projects should be treated as distinct artifacts.

The system should not invent experiences or merge unrelated work.

### Every important claim should be traceable

Generated narratives should remain connected to the source evidence that supports them.

### Privacy should be designed into the workflow

Users should control which materials enter the system, and unnecessary personal or sensitive information should not be included.

### Product improvement must justify added complexity

New implementation should create clear user value.

CareerPilot will not add automation merely because it is technically possible.

---

## Product Demo

<!-- Replace the placeholder below with a Loom, YouTube, Vimeo, or other public demo link. -->

A short demonstration of the functional local MVP will be added here.

[Watch the CareerPilot demo](#)

The demonstration will show:

- The user-curated evidence repository
- Career artifact organization
- Evidence ingestion
- Deduplication
- Artifact narrative generation
- Career Profile generation
- The final advisor-facing output

---

## Current MVP

CareerPilot currently exists as a functional local MVP.

The current version can:

- Ingest a user-curated collection of career documents
- Convert supported files into structured source material
- Organize evidence inside an Obsidian-based second brain
- Identify distinct career artifacts
- Associate evidence with the appropriate artifact
- Deduplicate repeated evidence
- Generate artifact-level career narratives
- Produce a consolidated Career Profile
- Run local model inference through Ollama
- Render the final output as a downloadable document

The current MVP is intentionally narrow.

Its purpose is to validate the core data model, workflow, and usefulness of the Career Profile before increasing automation or building a production-scale platform.

---

## Current Stage

CareerPilot is currently:

- Refining the functional MVP
- Conducting customer discovery
- Preparing a structured product demonstration
- Seeking feedback from career advisors
- Identifying potential pilot partners
- Evaluating the highest-value initial customer segment
- Preparing for accelerator and pitch competition applications

CareerPilot does not yet have a publicly hosted SaaS application.

The product currently runs locally while the core workflow, data model, privacy controls, and advisor use case are validated.

---

## Pilot Goals

The first pilot will evaluate whether CareerPilot helps career advisors:

- Understand clients more quickly
- Discover accomplishments that would otherwise be missed
- Identify stronger career narratives
- Recommend more appropriate target roles
- Improve résumé and interview preparation
- Deliver more personalized guidance
- Reduce the time required to review large amounts of client material

The pilot will also evaluate:

- Which source materials are most valuable
- How much evidence advisors want to review
- Which parts of the Career Profile are most useful
- Which workflows should remain human-controlled
- Which steps should be automated in future versions
- What privacy and security requirements institutions expect

---

## Roadmap

### Phase 1: Validate the Career Profile

- Complete the local MVP
- Conduct advisor interviews
- Run initial product demonstrations
- Collect feedback on the Career Profile
- Validate the core problem and target customer
- Confirm which outputs create the most value

### Phase 2: Private pilot

- Support a small number of career advisors and clients
- Improve onboarding
- Add structured advisor feedback
- Strengthen data-quality checks
- Improve source traceability
- Refine privacy controls
- Measure advisor time saved and decision quality

### Phase 3: Increase automation

Potential future capabilities include:

- GitHub repository integration
- Google Drive integration for user-approved folders
- Automated repository discovery
- Sensitive-data detection during ingestion
- Improved artifact extraction
- Advisor dashboards
- Role-targeting support
- Application-material generation
- Interview-story generation
- Multi-client career-center workflows

These features will be added only after the core workflow has been validated.

---

## Origin of the Product

CareerPilot emerged from lessons learned while building an earlier product called JobPilot.

JobPilot attempted to generate optimized career materials before the underlying career evidence had been organized reliably.

That approach exposed a more fundamental problem:

> Career tools cannot produce consistently strong outputs when the user’s underlying evidence is fragmented, incomplete, or incorrectly structured.

CareerPilot represents a deliberate pivot.

Instead of beginning with résumé optimization, CareerPilot begins with the data source, evidence structure, and career artifact model.

The goal is to create a reliable career intelligence layer that can support multiple downstream career services.

---

## About the Founder

CareerPilot was created by **Cameron Morreale**, an applied AI product builder and data professional with a BS and MS in Data Science from Worcester Polytechnic Institute.

Cameron’s background includes work across:

- Applied AI
- Data engineering
- Analytics
- ETL and workflow automation
- Cloud infrastructure
- Technical product development
- Career technology
- Hackathon product development

His experience includes building data pipelines, automating operational workflows, developing AI-assisted products, and translating complex technical work into business-facing outcomes.

CareerPilot was also motivated by a personal problem: accurately representing a broad body of technical, professional, academic, and entrepreneurial work through conventional career materials.

<!-- Add links after reviewing the page. -->

[GitHub](#) · [LinkedIn](#) · [Email](#)

---

## Pilot Interest

CareerPilot is seeking conversations with:

- Career advisors
- College career centers
- Workforce-development professionals
- Career coaches
- Employment programs
- Technical training organizations
- Potential pilot partners

Relevant feedback includes:

- How advisors currently collect client career evidence
- What information is usually missing
- How much time advisors spend reviewing client materials
- Which Career Profile sections would be most useful
- What privacy or security requirements would need to be met
- Whether the product could improve advisor effectiveness

<!-- Replace the links below with your actual form and email address. -->

[Join the CareerPilot pilot](#) · [Schedule a conversation](#) · [Contact the founder](mailto:YOUR_EMAIL_HERE)

---

## Technical Documentation

This page provides a product-level overview of CareerPilot.

The repository README contains the technical architecture, implementation workflow, system invariants, scope decisions, and development documentation.

[Read the technical documentation](README.md)

---

## Project Status

**Stage:** Functional local MVP  
**Primary customer:** Career advisors and career-service organizations  
**Current objective:** Customer discovery and pilot validation  
**Business model:** Under evaluation  
**Public application:** Not yet deployed  
**Pilot availability:** In preparation  

---

© 2026 CareerPilot
