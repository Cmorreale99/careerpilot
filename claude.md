Goal: the second brain is a database of artifacts. This file is the source of truth. The goal of careerpilot is to combine an Obsidian-based second brain with AI to create a structured career profile from a user's career evidence.
The Obsidian vault serves as the data layer and contains evidence for the user's career artifacts. CareerPilot ingests this data (manually selected GitHub markdown files and a user-curated Google Drive converted to Markdown), organizes it, and renders a comprehensive career profile.

## Technology and AI Constraints

CareerPilot may reuse the general application stack, database infrastructure, frontend patterns, and rendering components from JobPilot where appropriate. However, CareerPilot has a separate ingestion and evidence-processing pipeline defined in this file. Do not copy JobPilot's pipeline behavior into CareerPilot unless it directly satisfies the CareerPilot invariants.
The core ingestion pipeline must be deterministic and auditable. File conversion, ingestion, chunking, source tracking, exact deduplication, artifact identification, artifact assignment, and profile assembly must not depend on a generative LLM unless an LLM is demonstrably necessary.
Every stored evidence chunk and every artifact assignment must remain traceable to the original source document.
An LLM may be added later as an optional presentation layer for narrative synthesis, rewriting, summarization, or ambiguity review. An LLM must not silently invent evidence, create unsupported artifacts, merge ambiguous artifacts, or replace the underlying source evidence.

Implementation

1. the second brain layer has its own folder labeled 2nd brain, any integration and reference to the second brain will reference this folder.
2. write a script to convert .pdf and .docx files in the raw drive folder (located C:\Users\cmorr\careerpilot\2nd brain\career artifacts\raw drive)to markdown format and move the extracted markdown to C:\Users\cmorr\careerpilot\2nd brain\career artifacts\converted drive.
3. Next, write a script to convert .pdf and .docx files in the raw education folder C:\Users\cmorr\careerpilot\2nd brain\career artifacts\raw education) and move the extracted markdown to C:\Users\cmorr\careerpilot\2nd brain\career artifacts\raw education
4. ingest all raw markdown data from the 2nd brain corpus and store it in postgres.
5. search though the entire postgres database and organize the data into chunks (sentences)
6. dedup: There will be duplicate chunks, so i want you to search though the postgres database and dedupe duplicate chunks
7.Identify artifacts explicitly referenced throughout the corpus. An artifact is an individual project, hackathon, professional experience, or education entry. Artifact names and boundaries must be grounded in project titles, experience names, education records, document headings, and repeated references found in the source material. Do not invent artifacts that are not supported by the corpus.
For each artifact, collect the chunks that describe the user's role, responsibilities, actions, contributions, technologies, decisions, and results. Use document headings, artifact names, aliases, organization names, source-file context, and surrounding sentences to determine which artifact each chunk belongs to.
8. Deduplicate artifact references. Different names or aliases that clearly refer to the same project, hackathon, experience, or education entry should resolve to one canonical artifact. Deduplicating an artifact must not delete its evidence or source references. If two artifact references might represent separate artifacts, keep them separate rather than merging them without sufficient evidence.
9. create the website using plugins/frontend-design/. I want the comprehensive career profile at the top with a button to render it and another to download it.

v2: V1 already has artifacts broken correctly defined and the pipeline is working. The corpus is present. However, the document is around 250 pages which is far too long and nobody will read that. The goal of v2 is to summarize each artifact into a one page summary that contains a high level overview of what the artifact was, my contributions, the technical and professional capabilities demonstrated, and why the work mattered. 

v2 implementation
1. Set up Ollama and allow it to access the corpus
2. Have it do one pass, it will loop through the document one artifact at a time and build the one page summary one by one containing a high level overview of the artifact, my contributions, technical and professional capabilities demonstrated, and why the work mattered. (Note: save each artifact summary independently so one failed API request does not force the entire corpus to be processed again)
3. Update the renderable document so it’s the new LLM organized one while preserving the original complete corpus separately.




