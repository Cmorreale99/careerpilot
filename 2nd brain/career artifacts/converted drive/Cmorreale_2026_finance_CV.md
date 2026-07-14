---
source_file: "2nd brain/career artifacts/raw drive/Cmorreale_2026_finance_CV.pdf"
source_sha256: 2e356f0fc76e8b2915c18c513c8b1f07f4752cd744d1990d37de305f7711f9d1
converter: pdfplumber 0.11.10
---

<!-- source page 1 -->

Cam Morreale
Reverse-engineers broken data systems into scalable decision infrastructure
Worcester, MA • cmorreale@wpi.edu • 774-277-1205 • linkedin.com/in/cam-morreale • github.com/Cmorreale99
EDUCATION
Worcester Polytechnic Institute — MS Data Science (May 2026), BS Data Science (May 2025)
SKILLS
Languages & Development — Python, Pandas, NumPy, SQL, R, Power BI, React, TypeScript, Git
Data Engineering & Systems — ETL/ELT Pipelines, Data Modeling, Schema Design, Data Ingestion &
Normalization, Async I/O (aiohttp)
Machine Learning & LLM Systems — Transformer Models (BERT, RoBERTa), Named Entity Recognition
(NER), Retrieval-Augmented Generation (RAG), Embeddings (SentenceTransformers), Semantic Search, Prompt
Engineering, Model Evaluation (Precision/Recall/F1), Hallucination Detection, Hugging Face, spaCy
Cloud & Infrastructure — AWS (Lambda, API Gateway, RDS, S3, IAM), Oracle Database, Serverless
Architectures, Docker, REST APIs, IPFS, Filecoin, Web3.Storage
PROFESSIONAL EXPERIENCE
Wellington Management — Data Architecture & Engineering Intern | Boston, MA Jun–Aug 2025
• Reconstructed the data architecture powering a Python-based investment decision platform supporting
$153B in insurance assets across 23 countries, replacing a fragmented Excel workflow used by ~160
investment professionals and enabling ~$8M in annual operational efficiency gains.
• Reverse-engineered an undocumented Oracle environment (~250 tables), mapping business logic to the
data layer by prioritizing key tables to reconstruct schema and data lineage under incomplete visibility.
• Diagnosed and resolved a missing upstream dataset as the root cause of system-wide pipeline failures,
restoring execution by re-establishing critical data dependencies with minimal downstream changes.
• Co-designed an analytics-override framework balancing model integrity with user flexibility, enabling
controlled input adjustments with validation and auditability for real-world investment decision workflows.
• Developed a system-level architecture mapping data pipelines, transformation logic, and user interaction
layers, enabling reliable integration and clarifying dependencies across the platform.
MassDEP — Technical Business Analyst (Data & AI Systems) | Worcester, MA Jan–May 2025
• Owned retrieval, extraction, and validation layers of an LLM pipeline, converting unstructured reports into
Power BI–ready datasets and reducing manual reporting effort by ~40% across 50+ projects.
• Reduced hallucinated outputs in LLM-generated data by implementing a retrieval-based grounding system
using embeddings and semantic search, improving reliability of extracted information for analytics.
• Optimized entity extraction accuracy across inconsistent report formats by building a hybrid NER pipeline
with validation logic, reducing missing and incorrect data in structured outputs.
• Standardized model outputs into structured CSV datasets and integrated them into Power BI, enabling
analysis of extracted data across documents.
• Architected page-level inspection and validation logic to detect unreadable outputs, surface failure states,
and quantify system reliability (97% successful extraction rate).
Embue — Data Systems Architecture Lead | Worcester, MA Aug–Dec 2022
• Addressed lack of tamper-resistant storage in IoT systems by architecting a distributed data infrastructure,
enabling verifiable data integrity and reliable ingestion across decentralized environments.
• Designed a layered system separating encryption, storage, verification, and access control, improving
scalability and security across the data pipeline.
• Identified scalability limitations of on-chain storage and implemented a hybrid architecture using IPFS for
off-chain storage and Filecoin for verification, balancing performance with integrity guarantees.
• Enabled secure ingestion and retrieval of IoT data across decentralized systems by building an encrypted
pipeline, ensuring confidentiality while maintaining verifiable data integrity.
• Deployed and validated decentralized infrastructure (IPFS nodes, Filecoin client), confirming end-to-end
integrity through content-addressed retrieval and controlled decryption.

<!-- source page 2 -->

PROJECTS & HACKATHONS
BoardGameGeek Platform — Data Engineering & System Development (WPI) Aug–Dec 2025
• Improved reliability and throughput of API-constrained data ingestion by engineering a 3-stage
asynchronous ELT pipeline, ensuring consistent collection of external data across ~150 entities.
• Standardized and integrated heterogeneous datasets by architecting data transformation workflows,
reducing inconsistencies and improving downstream data usability.
• Modeled recursive relationships between entities to improve data integrity and support more complex
queries beyond flat relational structures.
• Integrated backend data pipelines with AWS Lambda services and a React-based frontend, enabling full-
stack functionality from ingestion to user interaction.
Oasis — EasyA x Polkadot Hackathon (1st place) | System Design & Business Logic Lead Jun 2023
• Led system design for a decentralized platform in a 48-hour hackathon (1st out of 100+ teams), translating
governance and incentive requirements into a clear, executable architecture under tight constraints.
• Optimized token-based incentive mechanisms and governance structures, aligning system behavior with
user participation and platform sustainability.
• Translated abstract economic and system requirements into a functional architecture, prioritizing clarity,
feasibility, and rapid execution.
OneWorld — EasyA x HackBoston (3rd place) | System Architecture & Incentive Design Lead Oct 2022
• Designed and delivered a blockchain-based carbon market in a competitive hackathon (Top 3 out of 100+
teams), prioritizing business viability and incentive-aligned system design under time constraints.
• Modeled emissions permits as tokenized financial assets with lifecycle constraints, aligning system
behavior with real-world regulatory and market dynamics.
• Engineered supply and pricing mechanisms (deterministic issuance decay, tiered marginal pricing) to
control emissions supply and align long-term incentives.
• Architected on-chain infrastructure enabling real-time auditability of emissions issuance, trading, and
retirement, reducing information asymmetry in carbon markets.
SafePool — DeFi Infrastructure (Avalanche L1 Hackathon) | System Design Lead Mar 2025
• Co-designed a decentralized financial system to formalize informal credit markets (ROSCAs), addressing
counterparty risk, lack of transparency, and enforcement limitations in ~$1.5T+ global capital flows.
• Reduced counterparty risk in pooled savings systems by architecting smart contract–based financial
primitives, enabling transparent and enforceable contribution and payout mechanisms.
• Enabled scalable deployment of a decentralized credit system by building infrastructure on Avalanche L1,
optimizing for transaction throughput, settlement finality, and interoperability in underbanked markets.
FINANCIAL SYSTEMS & MARKETS
Quantitative Market Modeling — Multi-Strategy Trading Simulation (WPI) Jan–May 2022
• Pioneered trading simulations beating S&P 500 (+24.73%, +9.20% vs. +1.36%) over a 7-week period.
• Built a position-trading portfolio using DCF valuation, price-to-book analysis, and macroeconomic sector
screening to identify undervalued equities in energy and emerging sectors.
• Analyzed options pricing dynamics and volatility-driven distortions in risk-reward.
Quantitative Market Research — Cryptocurrency ML Models (WPI) Mar–May 2024
• Conducted a meta-analysis of machine learning approaches for cryptocurrency trading, evaluating models
including reinforcement learning (AdaBoost-LSTM), XGBoost, and SVM across profitability and risk-
adjusted return metrics.
• Designed feature engineering and evaluation frameworks using technical indicators (RSI, MACD, ROC)
and performance metrics (Sharpe ratio, drawdown, predictive accuracy).
