---
source_file: "2nd brain/career artifacts/raw drive/cmorreale_resume.docx (1).pdf"
source_sha256: a9ce205da4f5ffc3457935f68565c593605a18550aa410de91a14489d376d07b
converter: pdfplumber 0.11.10
---

<!-- source page 1 -->

Cam Morreale
Reverse-engineers broken data systems into scalable decision infrastructure
Worcester, MA • cmorreale@wpi.edu • 774-277-1205 • linkedin.com/in/cam-morreale • github.com/Cmorreale99
EDUCATION
Worcester Polytechnic Institute — MS Data Science (May 2026), BS Data Science (May 2025)
SKILLS
Programming & Systems — Python, SQL, R, Bash, React, TypeScript, Git
Data Engineering & Architecture — ETL/ELT pipelines, data modeling, data validation, data quality &
deduplication, schema design, data ingestion & normalization
Data & Analytics Tooling — Pandas, NumPy, Scikit-learn, PyTorch, TensorFlow, Jupyter/ipywidgets
Cloud & Data Infrastructure — Snowflake, Snowpark, AWS Lambda, S3, IAM, Airbyte, Docker, Oracle SQL
PROFESSIONAL EXPERIENCE
Wellington Management — Data Architecture & Engineering Intern | Boston, MA June–Aug 2025
• Reconstructed the data architecture powering a $153B investment platform used by ~160 investment
professionals, replacing a fragmented legacy Excel workflow and driving ~$8M in annual efficiency gains.
• Reverse-engineered an unmapped 250-table Oracle database, inferring schema, primary/foreign key
relationships, and data dependencies to reconstruct the system architecture.
• Diagnosed and resolved a missing upstream dependency causing system-wide pipeline failure.
• Co-designed and implemented an analytics-override framework (Python, Pandas, ipywidgets, Oracle SQL),
enabling validated, auditable model adjustments for investment workflows.
Cooper.ai — Data Engineer (Contract) | Remote June 2026–Present
• Automated recurring client data-ingestion workflows by replacing manual file preparation and merge steps
with scheduled AWS Lambda/S3/Snowflake pipelines.
• Built a production retail-data ingestion automation that merges multiple upstream feeds, handles
late-arriving files, writes auditable outputs, and triggers downstream Snowflake processing.
• Automated a logistics-reporting pipeline that converts multi-tab Excel reports into Snowflake-ready
datasets, loads five production staging tables, and enables daily analytics/AI refreshes.
• Remediated production shipping-ingestion defects across four carriers, removing 195K+ duplicate FedEx
rows, restoring full date coverage, and preventing recurring data corruption.
MassDEP — Technical Business Analyst (Data & AI Systems) | Worcester, MA Jan-May 2025
• Owned retrieval, extraction, and validation layers of an LLM pipeline, converting unstructured reports into
Power BI–ready datasets and reducing manual reporting effort by ~40% across 50+ projects.
• Designed and implemented a RAG system to ground outputs in source documents and reduce hallucination.
• Standardized model outputs into structured CSV datasets and integrated them into power BI, enabling
downstream analysis of extracted environmental data across documents.
• Built page-level inspection and validation logic to detect unreadable outputs, surface failure states, and
quantify system reliability (97% successful extraction rate).
Embue — Data Systems Architecture Lead | Worcester, MA Aug–Dec 2022
• Solved lack of tamper-evident storage in IoT systems by architecting a distributed data infrastructure to
enable verifiable data integrity across decentralized environments.
• Designed a layered architecture separating encryption, storage, verification, and access control, improving
scalability, security, and system modularity.
• Identified scalability limitations of on-chain storage and implemented a hybrid architecture using IPFS for
off-chain storage and Filecoin for verification, balancing performance with integrity guarantees.
• Built and shipped an end-to-end encrypted pipeline (GnuPG → IPFS → Filecoin), enabling secure
ingestion, storage, and retrieval of IoT data.
