# CareerPilot

## New Product Idea

CareerPilot combines an Obsidian-based second brain with AI to create a structured career profile from a user's career evidence.

The Obsidian vault serves as the data layer and contains evidence for the user's career artifacts. CareerPilot ingests this data (manually selected GitHub `README.md` files and a user-curated Google Drive converted to Markdown), organizes it, and renders a comprehensive career profile.

The goal is to help career coaches understand the full extent of their clients' capabilities, identify strengths, determine which roles are the best fit, decide which career artifacts should be emphasized, and help clients market themselves more effectively.

---

## Lessons Learned from JobPilot V1

CareerPilot is a significant architectural pivot based on what I learned from JobPilot V1.

The biggest lessons were:

- Start with the data source and ingestion pipeline before building downstream functionality.
- Define the architecture before implementation.
- Constrain the MVP aggressively.
- Keep a single source of truth.
- Avoid searching the user's entire digital life.
- Build the minimum useful workflow before adding automation.

These lessons directly influenced the design decisions below.

---

## Scope Reduction

The scope has been narrowed significantly.

CareerPilot will **not** search through a user's entire Google Drive. Doing so introduces unnecessary complexity, privacy concerns, security concerns, and architectural challenges.

Instead:

- The user manually curates the files they want CareerPilot to ingest.
- Claude converts supported files (`.pdf` and `.docx`) into Markdown using a conversion script.
- GitHub repositories are added manually by copying selected `README.md` files into the Obsidian vault.

The following features are intentionally deferred until later versions:

- GitHub MCP integration
- Google Drive MCP integration
- Claude Code artifact extraction
- Automatic repository discovery

The goal is to validate the product and data model before increasing automation.

---

# Second Brain Workflow

1. User forks the CareerPilot repository (formerly JobPilot V2).

2. Create `CLAUDE.md`.

`CLAUDE.md` defines:

- project goals
- career artifact definitions
- privacy rules
- folders Claude is allowed to access
- folders Claude cannot modify

Career artifacts are **defined by the user**. Claude does **not** infer them.

The Obsidian vault is the source of truth.

3. Create hooks.

Hooks define rules that Claude is never allowed to violate.

4. Build this folder structure

```
CareerPilot
│
├── README.md
├── CLAUDE.md
│
└── Career Artifacts
    ├── raw drive (not .md, will be a mix of pdfs and word docs)
    ├── raw education (docs or pdf, transcript)
    ├── github (a manually curated collection of readmes and technical writeups from your repos)
    ├── converted drive 
    └── converted education
```

5. The user:

- manually selects career-related Google Drive files
- manually selects GitHub markdown files

6. Configure Obsidian plugins for document conversion.

The conversion script converts supported Drive documents into Markdown and places them into the appropriate `Converted` folders.

7. The second brain is now ready for ingestion.

Run CareerPilot ingestion.

---

# Career Evidence Invariants

These invariants must always hold.

### No duplication

The second brain will naturally contain duplicate evidence.

CareerPilot must deduplicate evidence before assigning it to career artifacts.

### Career artifacts

Every experience, personal project, class project, or hackathon is its own career artifact.

Each artifact owns its own collection of career evidence.

### Output

Instead of generating a Master CV, CareerPilot generates a comprehensive Career Profile.

The Career Profile represents the complete universe of the user's career artifacts together with all evidence relevant to each artifact.

Artifacts are organized into:

- Experience
- Projects
- Hackathons

Each artifact receives its own structured career narrative.

---

# Implementation Order

Once the second brain is complete:

1. Build rendering logic (reuse JobPilot code where appropriate).
2. Deduplicate evidence.
3. Correctly identify career artifacts.
4. **Do not continue until artifact assignment is correct.**
5. Assign evidence to artifacts.
6. Generate artifact narratives.
7. Construct the Career Profile.

Done.
