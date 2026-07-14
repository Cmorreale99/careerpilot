---
source_file: "2nd brain/career artifacts/raw drive/Laufer logistics data pipeline.docx"
source_sha256: 38d45b25d35e2f0f7bf0fdacf4575a828a574d828c2d8ecb718a1cff3ad72c0f
converter: mammoth 1.12.0
---

Laufer Logistics Data Pipeline — Technical Summary

Overview

Built an automated ETL pipeline that ingests Laufer \(freight forwarder\) logistics reports into Snowflake and exposes them to the analytics/LLM layer for the Excelligence client\. Replaced a manual, human\-in\-the\-loop process with an event\-driven AWS Lambda \+ Snowflake ingestion, and resolved several real\-world data\-quality and infrastructure issues discovered during validation\.

Background / business context

Laufer provides two Excel reports covering ~12 months of historical shipments plus ~6 months forward:

\- Milestones report \(tabs: Milestones, Purchase Orders, LCL Milestones\)

\- Landed Cost report \(tabs: Commercial Invoices, Landed Costs \[summary\], Billing Details\)

Each daily drop contains the full data window, so the model is a full overwrite, no history\. The data feeds the Excelligence client's analytics in Snowflake \(COOPERAI\_PROD\.EXCELLIGENCE\) and is surfaced to the LLM/front\-end via admin\-UI Data Roles\.

Problem

The reports were being prepared manually by Noah: download each Excel file, delete junk rows, save each relevant tab as a <tab>\_cleaned\.csv, and drop the CSVs in S3 \(prod\-cooper\-client\-data/adhoc/excelligence/laufer/\)\. Nothing then loaded them into Snowflake — the pipeline effectively stopped at hand\-made CSVs in S3, with no automation and no warehouse tables\.

Goal: automate cleaning, land the data in Snowflake as queryable staging tables on a daily schedule, and expose it — with no manual steps\.

Solution architecture \(end\-to\-end\)

Raw \.xlsx dropped in s3://cooper\-prod\-excelligence\-data\-landing\-zone/Laufer\_files/

   │  \(S3 ObjectCreated, suffix \.xlsx\)

   ▼

AWS Lambda  \(laufer\-excel\-to\-csv, container image: pandas \+ openpyxl\)

   • route by filename stem \(ignore the YYYYMMDD\-YYYYMMDD date window\)

   • read each whitelisted tab, clean it, write one CSV per tab

   ▼

s3://prod\-cooper\-client\-data/adhoc/excelligence/laufer/<tab>\_cleaned\.csv

   │  \(read by the Snowflake S3\_ADHOC\_DATA stage\)

   ▼

Snowflake stored proc  INGEST\_LAUFER\_CSV  \(called by 5 daily DAG tasks\)

   • positional load → STG\_\* tables, full overwrite, failure\-safe

   ▼

EXCELLIGENCE schema:  STG\_MILESTONES\_MILESTONES, STG\_MILESTONES\_PURCHASE\_ORDERS,

   STG\_MILESTONES\_LCL, STG\_LANDEDCOST\_COMMERCIAL\_INVOICES, STG\_LANDEDCOST\_BILLING

   ▼

Exposed to LLM/front\-end via admin UI → Clients → Excelligence → Data Roles

Lambda \(cleaning\) — etl/src/shared/lambda/laufer\-excel\-to\-csv/

\- Container\-image Lambda \(pandas \+ openpyxl exceed the zip size limit\), CDK\-deployed, mirroring the existing unzip\-s3\-files project\.

\- Cleaning logic isolated in a pure, AWS\-free module \(cleaning\.py\) so it's fully unit\-testable \(16 tests over synthetic workbooks\)\.

\- Cleaning rules: detect the real header row on Milestones p1 \(it has ~4 header rows\), drop fully\-empty/Unnamed phantom columns, drop a broken Link formula column, de\-duplicate repeated header names, keep legitimate nulls, exclude the Landed Costs summary tab \(whitelist kept tabs\), LayoutValidationError on a collapsed/shifted layout\.

\- Output: flat <tab>\_cleaned\.csv filenames matching what the ingest reads — a drop\-in replacement for the manual step\.

Snowflake ingestion — etl/src/clients/excelligence/pipelines/

\- INGEST\_LAUFER\_CSV\(input\_file, to\_table\[, has\_header\]\) Snowpark proc, registered in snowflake\.yml, called by 5 standalone daily tasks in the task DAG \(infra\.py\), with paths/table names in config\.py\. Mirrors the existing carrier\-ingest pattern\.

\- Failure\-safe full overwrite: load into a \*\_TEMP table with ON\_ERROR=ABORT\_STATEMENT, then CREATE OR REPLACE TABLE … CLONE to swap — so a malformed daily file never wipes the prior good load\.

\- All columns staged as VARCHAR\.

Key technical challenges solved

1\. Duplicate effort discovered mid\-build\. Cleaned CSVs already existed in S3 with timestamps predating the work and no matching code in the repo\. Investigated and determined they came from Noah's manual process, not an automated job — avoided shipping a competing pipeline, and correctly scoped the Lambda as the automation of that manual step \(single writer, no dual\-writer collision\)\.

2\. Duplicate column headers\. The reports contain repeated header names \(e\.g\. multiple UOM columns after Gross Weight / Volume / Pieces\)\. Snowflake's INFER\_SCHEMA and MATCH\_BY\_COLUMN\_NAME both reject duplicate headers \(duplicated column names "UOM" is not allowed\)\. Re\-architected the ingest to read the header row, de\-duplicate names \(UOM, UOM\_2, UOM\_3\), and load positionally with SKIP\_HEADER=1 — no reliance on header\-name matching\.

3\. SELECT \* not supported on CSV stages\. Probing column count/header via SELECT \* failed with SELECT with no columns\. Switched to enumerating positional columns \($1\.\.$N\) and trimming trailing NULLs to recover the true width\.

4\. Silent data loss trap\. An early hand\-tested load used ON\_ERROR=CONTINUE, which silently skipped every row on a column\-count mismatch \(0 rows, no error\)\. Standardized on ON\_ERROR=ABORT\_STATEMENT so failures are loud, and on positional/de\-duped loading so counts always match\.

5\. Squash\-merge rebase conflicts\. A follow\-up branch showed "5 conflicts" against main because the first PR was squash\-merged \(original commits absent from main's history\)\. Resolved by rebasing only the post\-merge commits onto main \(git rebase \-\-onto\), producing a clean, conflict\-free diff\.

6\. Deploy\-flow clarity\. Documented the repo's deploy gating: merge to main → test → deploy\_dev \(automatic\) → deploy\_prod \(GitHub Environment approval gate\); Snowpark procs deploy per\-client \(schema = client slug\) to the environment's default database\.

Validation

\- Lambda: 16 unit tests pass \(synthetic workbooks reproducing every quirk — multi\-row header, empty/Unnamed cols, the Link column, the summary tab, duplicate headers\)\.

\- Snowflake: smoke\-tested the positional load against all 5 real files in COOPERAI\_PROD\.EXCELLIGENCE — all loaded cleanly with expected row counts \(~244 / 1,798 / 79 / ~3–4k / ~3–4k\), no header/column errors\.

\- ruff \+ py\_compile clean throughout\.

Results / business value

\- Eliminated a recurring manual task\. Noah no longer has to download, hand\-clean, and upload these reports each day — it's an automated, event\-driven pipeline\.

\- Data is now queryable in Snowflake \(5 staging tables\) and exposable to the LLM/front\-end, where before it sat as loose CSVs in S3 with no warehouse presence\.

\- Reliable and safe by design — failure\-safe full overwrite \(no risk of wiping good data\), loud failures instead of silent partial loads, and validation that fails on layout drift instead of ingesting garbage\.

\- Lower maintenance / fits existing patterns — built on the repo's established CDK\-Lambda and Snowpark\-proc \+ task\-DAG conventions, so it's consistent for the next engineer\.

Artifacts

\- Lambda \+ cleaning \+ tests: etl/src/shared/lambda/laufer\-excel\-to\-csv/

\- Ingestion proc / config / DAG: etl/src/clients/excelligence/pipelines/\{app/procedures\.py, config\.py, snowflake\.yml, infra\.py\}

\- PRs: initial pipeline \(\#667, merged\); retarget to existing filenames \+ remove redundant Lambda \(merged\); duplicate\-header \+ $1\.\.$N proc fix \(fix/laufer\-duplicate\-headers\); restore Lambda as the producer \(feature/restore\-laufer\-lambda\)\.

Outstanding / next steps

\- Approve the pending prod deploy of the ingest proc; run the 5 CALL INGEST\_LAUFER\_CSV\(\.\.\.\); expose the STG\_\* tables in admin UI Data Roles\.

\- Confirm the raw \.xlsx reliably lands in Laufer\_files/ \(the Lambda trigger\) — i\.e\., who/what delivers the upstream file\.

\- Parity\-check the Lambda's auto\-cleaned output against Noah's hand\-cleaned files \(row counts\) before fully cutting over the manual process\.

\- Optionally harden cleaning\.py expected\_columns once a canonical workbook is available\.

\-\-\-
