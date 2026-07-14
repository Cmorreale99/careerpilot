---
source_file: "2nd brain/career artifacts/raw drive/Second brain.docx"
source_sha256: 6e84d7afa5b7850731e776e78f0a865c2a071142be855657aaded448cae08528
converter: mammoth 1.12.0
---

Goal: build a “second brain” with Claude \+ obsidian \.md files that will serve as the raw corpus of career artifacts to be queried and cleaned by jobpilot, cleaned version will be stored in Postgres for masterCV integration\. 

1. Write a [claude\.m](http://claude.me)d file \(define the goals eg this is a database of career artifacts, remove personal info etc, define artifacts etc \(this will be a useful reference point later on when its time to define the artifacts\), Obsidian connector and instruct Claude how to read this vault and what files it can and cannot touch\. This is where career artifacts are defined \(the user gets to define them, claude does not infer it\) All other files are off limits besides when converting to \.md files with connector\)\. This folder is the source of truth\.
2. Write hooks \(rules that cannot be broken\)
3. Build the Folder structure MANUALLY \(do NOT shortcut this with AI\): root\- [Claude\.md](http://claude.md), readme, career artifacts folder\. Inside career artifacts folder: [drive](http://drive.md) folder \(contains a curated set of google drive artifacts, I’m going to abandon the drive MCP and choose manually to give me more control\), and GitHub folder \(a set of github readmes I select manually, again to give me more control\)

What this accomplishes: having a database of all my career artifacts is incredibly useful for generating new connections between things I’ve previously done to accelerate learning \(eg I can take engineering lessons I learned from jobpilot v1 and apply them to building my personal knowledge OS project\), outsourcing working memory \(I don’t have to remember and dig through my entire drive and github every time I want to add something to my resume\. \(This is especially helpful given my cognitive profile\), and for careerpilot integration\.
