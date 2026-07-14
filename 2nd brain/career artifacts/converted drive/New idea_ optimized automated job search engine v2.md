---
source_file: "2nd brain/career artifacts/raw drive/New idea_ optimized automated job search engine v2.docx"
source_sha256: 302fde8336834846e48ef22ec5a7873176df4baa3b778c663296459ac77402d8
converter: mammoth 1.12.0
---

Pain point\- AI has raised the bar for technical ability and hiring for entry level tech roles is declining, HR is increasingly using AI to filter applicants \(eg ATS, AI interviews, AI written job posts etc\)\. The gap: my theory is a big part of why it’s an “employers market” is the job seekers aren’t leveraging AI to the extent the employers are in regards to the job search process specifically \(the gap is not in ability to leverage AI, many of these job seekers struggling do leverage AI in their everyday lives with success\. It’s about willingness and belief that it’s possible\. The gap is many job seekers are discouraged and lose hope, get burned out etc\. 

My hypothesis is this is a solvable game theory problem\. We need a fully end to end job hunting application optimized for the individual job seeker that will directly address the real bottlenecks: burnout, underleveraging AI, and hopelessness\. The job market is literally a market, the optimal strategy in markets is to identify every possible edge you have and relentlessly push your advantage\. The efficient market hypothesis states that when everyone has perfect information and participants act rationally, you cannot get an edge\. We have seen that human psychology isn’t necessarily that simple, and often people make irrational decisions \(see the 2020 pandemic, 2008 financial crisis, GME short squeeze, those who made big money in crypto vs those who panic sell when it tanks etc\)\.

When it comes to job searching this means tailoring applications by optimizing the resume to the specific job posting, networking \(this can be systemized, this is one area I plan to differentiate with my app\), building a master CV for the user by combing through the users curated google drive, github readmes, claude\.mds, markdown files, conversations with chatbots etc\. I’m thinking of connecting multiple Claude MCPS such as Claude in chrome, github MCP, connecting it to your Google drive etc to help Claude identify the job seekers technical skills \(github, drive, conversations with chatbots etc\), Claude would use all this information to build a master CV that is the source of truth, it would contain every technical skill the user has demonstrated, how they demonstrated it, what problem they solved, the business value they added\. All this info will be used to cross validate against each job posting selected by the user\. Then, the master CV/source of truth document will be used to construct an optimized CV/resume based on similarity scores\. For the data source, im going to be creating an obsidian based “second brain” by wiring up the claude MCP, drive MCP, and github MCP so claude can search through my google drive, github, chatgpt conversations, claude conversations, and claude code conversations and construct a raw database of all my career signals that is the source of truth that will be queried by jobpilot\. 

What we need:

Career evidence: defined as any chunk of information \(eg a sentence or paragraph\) containing evidence of problem solving, automating something, generating business value, improving efficiency, leveraging technical skills, class projects, personal projects, github repositories \(search through all markdown files, readmes, and [claude\.md](http://claude.md) files for career evidence, do not use commits, comments, and PRs as that will bloat the database with implementation details recruiters do not care about, one of the key design errors of the V1 architecture\)\.

How we will quantify how good or bad of a match a given project/experience in the master CV is for a job posting:

Binary inclusion \- if the score is over 80, you add the experience/project from the masterCV to the optimized CV for that job posting, if its below 80 you skip that and move to the next iteration of the loop and increment by 1\. I want the process to be start from experience 1 and do a loop over the entire list of experiences in the master CV\. If there are less than 3 experiences and or projects in the optimized CV, jobpilot will tell you “This role is not the best fit for your experience”, but will still construct the optimized CV\. If there are 3 or more experiences, jobpilot will say “Good fit, apply now with this resume”\.

Where do these numbers come from? 

ATS matching, years of experience, education, PAR framing, etc \(honestly, before implementing I need to talk to several big tech recruiters and understand the system better, otherwise it will be AI slop\. Garbage in = garbage out as i learned from Jobpilot V1\)

Tech stack:

Backend:

Local LLM \(ollama\) for roster proposal, section assignment, chunking, I learned from V1 that API costs are a real bottleneck, and extreme token optimization is a core part of the project design, not a side note

Anthropic API for claim extraction and story synthesis \(this part is filtering the data and ensuring the information is presented in resume ready format, will require more horsepower and higher reasoning\)

Obsidian/second brain integration for raw corpus/querying

Cleaned and filtered data queried from obsidian stored in postgres

Python, fastAPI, SQL =Alchemy, Alembic, APSchuedler, MCP client SDK, Frontend: [Next\.js](http://next.js) \(app router, typescript\), react, tailwind CSS, QA: pytest, ruff, mypy

Backend: Python 3\.12, uv, FastAPI, SQLAlchemy 2\.x, Alembic, Postgres, APScheduler, Anthropic Messages API, MCP client SDK\. Frontend: Next\.js \(app router, TypeScript\), React, Tailwind CSS\.

Need some kind of PDF to markdown and Docx to markdown converter, JSON to markdown converter

This needs to be built systematically\. Do not try to build everything at once, otherwise claude will lose context, hallucinate, ignore architectural constraints, invent new architecture etc

Start with the data source, the source of truth\. Bad data = corrupted masterCV = corrupted optimized CVs = unhappy user/useless product

What I learned from the Jobpilot V1 failure:

1. You must start with the data source and pipeline before touching anything else, this means Build the second brain integration first before touching jobpilot\. I was doing it backwards in V1
2. Product discovery before implementation, need to have architecture locked in and on point before implementation, constantly redesigning architecture mid implementation = spaghetti code and rapid accumulation of technical debt\.
3. Code reviews are mandatory\. This does not mean understand every line of code claude implements, but you must review lines created, lines deleted, files changed, spend 20 or so minutes skimming through the files, checking which types of files got changed \(tests vs new implementation vs edits vs deletions\), take notes of the shape of the changes, and most importantly run the program and ask “how much did the product improve relative to code complexity added?” Big product improvement \+ lots of code added \(complexity added\) = good\. Lots of code added \+minimal or marginal product improvement = RED FLAG, this is how technical debt accumulates over time\. If this happens, do NOT approve merge, go to claude and ask claude to explain each change, why it was made, what problem it solved\. Then prompt it with each grievance written down during the product analysis and code review\. Skill needed: Learning how to prompt claude effectively to identify architectural bottlenecks, and dealing with technical debt right away\.
4. Technical debt does not increase linearly, it explodes exponentially\. It cannot be put off, it needs to be dealt with immediately
5. Need to get mentorship from a senior or even principal engineer to learn how to leverage claude more effectively\. LLMs do work, they are effective and amplify strong engineers\. However, as I learned poor engineering practices such as blindly merging claudes output to main, outsourcing architecture to claude, and not understanding how to prompt claude effectively when debugging are major bottlenecks\. LLMs are multipliers which means marginal gains in engineering skill = significant gains\. Its worth investing in this\.
6. As good as vibe coding as, don’t let coding skills atrophy\. Keep reading SQL books, learning etc every day\. An hour a day of reading will pay off tremendously
7. A more complex pipeline isnt always better\. I want something simple so its easier to debug when things break\. The first major inflection point is cleaning and filtering data from what will be a large obsidian corpus before storing into postgres, Instead of trying to build the entire pipeline at once i should build:
	1. Obsidian/second brain layer 
	2. LLM cost control layer
	3. Obsidian to postgres layer
	4. Postgres to jobpilot layer 
	5. Then optimize master CV
	6. Then build the layer that allows users to add job postings and have a coherent integration
	7. Then build the scoring layer
	8. Then build the opitmized CV from that
8. Product scale was too large for Jobpilot V1\. Defer the drafting emails, detecting interviews etc for a later version\. None of that is needed to actually have a product I can sell, so don’t bother adding unnecessary complexity
9. Do NOT under any circumstances outsource architectural reasoning to any LLM\. This layer must all be done by me, otherwise I no longer have control of the product vision
10. Keep what i did well\. Readme, [claude\.md](http://claude.md) file, [plan\.md](http://plan.md) files\. But write them manually instead of having an LLM write them\.
11. The \#1 cause of failure: I did not constrain the product scope\. Properly defining and constraining the product scope is crucial, my initial idea was dependent on an LLM being capable of doing things it isn’t yet capable of doing \(inferring ambiguous requirements, etc\)\. It is important to understand when things are fundamentally flawed to the point it cannot be solved through brute force and willpower, no amount of prompting will force AI to be able to infer ambiguous requirements without hallucinating\. One of the most important skills an aspiring founder can have is knowing when it’s time to pivot\. The aspiring founder who is technically adept enough to understand the limitations of AI, the limitations of vibe coding without constraints, pivots quickly, learns from mistakes quickly instead of banging his head against a wall for 6 months and launching a product doomed to fail on week 2, moves to agentic engineering rather than undisciplined vibe coding is the one who will be successful\. When you get knocked down, you need to be able to adapt\.

New product idea:careerpilot\. What careerpilot does is it combines a 2nd brain obsidian integration that serves as the data layer containing evidence of the users career artifacts, and careerpilot ingests the obsidian data \(manually selected github [readme\.md](http://readme.md) files \+ a user curated drive converted to markdown with claude connectors that convert docx and pdf to \.md files\), renders and organizes the data into a career narrative document so career coaches can understand the full extent of their clients capabilities, help them market themselves, identify which roles to target, which artifacts to emphasize etc\. 

Update: I have narrowed the scope significantly, I will no longer be searching through the users entire drive, that creates massive complexity, privacy and security concerns\. Instead the idea will be to have Claude search through a user curated folder, and convert files to \.md \(for the obsidian second brain\)\. The user will upload [readme\.md](http://readme.md) files from their github to obsidian for the second brain manually \(I’ll do the github MCP integration later, for now the idea is to get all the info in there for a product MVP\. Claude code artifacts \+ extraction will also be deferred to later\)\.  The current 2nd brain workflow \(will be outlined in the second brain readme\) is:

1. User forks Careerpilot \(jobpilotV2 will be called careerpilot\) repo
2. User adds GitHub [readme\.md](http://readme.md) files to the GitHub folder
3. Directly inside obsidian set up a claude docdrop and pdf to md plugin to convert drive artifacts to \.md
4. Second brain integration is set up and ready for ingestion
5. Run the careerpilot ingestion

For ingestion: career evidence invariants:

No duplication: there will be duplicates in the 2nd brain, so careerpilot must have some deduping logic

Each experience, personal project, class project, or hackathon is an individual artifact\. Each individual artifact has its own set of career evidence\. 

Instead of a masterCV, it will be a constructed career profile doc that contains the entire universe of the users artifacts and all career evidence relevant to that artifact\. 

Once 2nd brain is built

1. Set up rendering logic \(can possibly reuse jobpilot code for this\) 
2. Dedup \(before assigning everything to artifacts\)
3. Define career artifacts correctly \(do not move to the next step until this is done correctly\. I will know exactly how to do this better once the second brain integration is complete\) 
4. Assign each artifact a narrative of career evidence
5. Break down artifacts into 3 sections: experience, projects, hackathons
