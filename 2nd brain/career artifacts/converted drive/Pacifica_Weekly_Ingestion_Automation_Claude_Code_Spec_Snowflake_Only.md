---
source_file: "2nd brain/career artifacts/raw drive/Pacifica_Weekly_Ingestion_Automation_Claude_Code_Spec_Snowflake_Only.docx"
source_sha256: c48a65b03658f62e897dadc6b3d63fc17dd762b579ba169f7054f58ccb083d53
converter: mammoth 1.12.0
conversion_warnings:
  - "Unrecognised paragraph style: Code (Style ID: Code)"
---

__Pacifica Weekly Ingestion Automation__

__Architecture V1 \- Snowflake\-Controlled Implementation Spec for Claude Code__

*Corrected scope: Snowflake is the system of record for ingestion state\.*

This document synthesizes the Pacifica manual ingestion notes and the architecture discussion into an implementation\-ready specification\. It is written to minimize Claude Code hallucination by explicitly defining the required components, state model, Snowflake control tables, Lambda orchestration behavior, completeness gating, merge refactor, error handling, and implementation tasks\.

# 1\. Executive Summary

The current Pacifica weekly ingestion workflow is manual: download POS and SPS files from the Pacifica S3 landing zone, edit the existing parse\_852\_edi\_py script, merge the files, upload the merged output back to S3, manually execute the Snowflake TASK\_DAG, and verify the task ran successfully\.

The primary issue is not simply file movement\. The primary issue is weekly data completeness\. POS files arrive in pieces, while SPS typically arrives separately and may be missing in some weeks\. Processing on first file arrival is unsafe because it can generate an incomplete weekly dataset\.

V1 should implement a stateful, Snowflake\-controlled, event\-triggered architecture: S3 file arrival triggers Lambda; Lambda classifies the file, records metadata in Snowflake, updates the weekly ingestion state, evaluates whether the week is ready, and only then runs the merge and triggers the Snowflake DAG\.

__Design Decision__

__V1 Choice__

State store

Snowflake control tables only

Trigger model

S3 event triggers Lambda

Processing model

Gated processing, not immediate processing

POS handling

Accumulate POS files until final POS/completeness condition

SPS handling

Case\-insensitive detection; missing\-SPS routes to configurable rule or review

Idempotency

Snowflake checks prevent duplicate processing

# 2\. Current Manual Workflow

- Open the Pacifica S3 landing zone and identify the latest POS CSV file\(s\) and SPS TXT file\.
- Download the relevant files locally\.
- Open VS Code and edit hardcoded date/file references in parse\_852\_edi\_py, currently around lines 13\-17\.
- Run the merge script to generate the merged Pacifica output file\.
- Open/review the merged output\.
- Upload the merged file back to S3\.
- Manually trigger the Snowflake task with USE ROLE DATA\_SCIENTIST\_ROLE; USE DATABASE COOPERAI\_PROD; USE SCHEMA PACIFICA; EXECUTE TASK TASK\_DAG;
- Check Snowflake Tasks to confirm the last run is recent and successful\.

# 3\. Observed File Arrival Pattern

POS observed dates: 4/6, 4/13, 4/20, 4/22, 4/25, 4/28, 5/4, 5/8, 5/10, 5/16, 5/23, 5/30, 6/6\. SPS observed dates: 4/18, 4/27, 5/2, 5/16, 5/23, 5/30, 6/6\.

- POS can arrive in multiple pieces during the same business week\.
- The final POS file is believed to indicate that the week is complete\.
- SPS appears to arrive once per week when it is sent\.
- SPS filenames may use inconsistent casing, so matching must be case\-insensitive\.
- Some weeks may have no SPS file, or the client may forget to send it\. V1 must not silently assume missing SPS is safe\.

# 4\. Target Architecture

S3 Pacifica Landing Zone  
  \-> S3 ObjectCreated event  
  \-> Lambda orchestration function  
  \-> Snowflake control tables: PACIFICA\_INGESTION\_FILES and PACIFICA\_INGESTION\_STATE  
  \-> Completeness evaluation in Lambda using Snowflake state  
  \-> Merge engine using refactored parse\_852\_edi\_py logic  
  \-> Output S3 location  
  \-> Snowflake TASK\_DAG execution  
  \-> Snowflake audit logging and alerts/review states

The Lambda function should behave as an event\-triggered gatekeeper\. Every file arrival is registered, but not every file arrival triggers a merge\. Merge execution occurs only when the corresponding week is marked ready\_to\_process in Snowflake\.

# 5\. Snowflake\-Only Control Plane

Snowflake is the system of record for ingestion state, file registry, processing status, and execution audit\. Do not add any secondary state database in V1\. This keeps operational visibility inside the data platform that already owns the downstream DAG\.

Recommended schema placement:  
COOPERAI\_PROD\.PACIFICA\.PACIFICA\_INGESTION\_FILES  
COOPERAI\_PROD\.PACIFICA\.PACIFICA\_INGESTION\_STATE  
COOPERAI\_PROD\.PACIFICA\.PACIFICA\_INGESTION\_RUN\_LOG

## 6\. Snowflake Table DDL \- File Registry

CREATE TABLE IF NOT EXISTS PACIFICA\_INGESTION\_FILES \(  
    FILE\_ID STRING DEFAULT UUID\_STRING\(\),  
    FILE\_NAME STRING NOT NULL,  
    S3\_BUCKET STRING NOT NULL,  
    S3\_KEY STRING NOT NULL,  
    FILE\_TYPE STRING NOT NULL, \-\- POS or SPS  
    FILE\_DATE DATE,  
    WEEK\_END\_DATE DATE,  
    ARRIVAL\_TS TIMESTAMP\_NTZ DEFAULT CURRENT\_TIMESTAMP\(\),  
    ROW\_COUNT NUMBER,  
    FILE\_SIZE\_BYTES NUMBER,  
    CHECKSUM STRING,  
    STATUS STRING DEFAULT 'REGISTERED',  
    ERROR\_MESSAGE STRING,  
    CREATED\_AT TIMESTAMP\_NTZ DEFAULT CURRENT\_TIMESTAMP\(\),  
    UPDATED\_AT TIMESTAMP\_NTZ DEFAULT CURRENT\_TIMESTAMP\(\)  
\);

## 7\. Snowflake Table DDL \- Weekly State

CREATE TABLE IF NOT EXISTS PACIFICA\_INGESTION\_STATE \(  
    WEEK\_END\_DATE DATE PRIMARY KEY,  
    POS\_FILE\_COUNT NUMBER DEFAULT 0,  
    SPS\_FILE\_COUNT NUMBER DEFAULT 0,  
    SPS\_RECEIVED BOOLEAN DEFAULT FALSE,  
    FINAL\_POS\_RECEIVED BOOLEAN DEFAULT FALSE,  
    POS\_COMPLETE BOOLEAN DEFAULT FALSE,  
    READY\_TO\_PROCESS BOOLEAN DEFAULT FALSE,  
    PROCESSING\_STARTED BOOLEAN DEFAULT FALSE,  
    PROCESSED BOOLEAN DEFAULT FALSE,  
    PROCESSED\_AT TIMESTAMP\_NTZ,  
    STATUS STRING DEFAULT 'WAITING\_FOR\_FILES',  
    OUTPUT\_S3\_KEY STRING,  
    ERROR\_MESSAGE STRING,  
    CREATED\_AT TIMESTAMP\_NTZ DEFAULT CURRENT\_TIMESTAMP\(\),  
    UPDATED\_AT TIMESTAMP\_NTZ DEFAULT CURRENT\_TIMESTAMP\(\)  
\);

## 8\. Snowflake Table DDL \- Run Log

CREATE TABLE IF NOT EXISTS PACIFICA\_INGESTION\_RUN\_LOG \(  
    RUN\_ID STRING DEFAULT UUID\_STRING\(\),  
    WEEK\_END\_DATE DATE,  
    STARTED\_AT TIMESTAMP\_NTZ DEFAULT CURRENT\_TIMESTAMP\(\),  
    ENDED\_AT TIMESTAMP\_NTZ,  
    STATUS STRING,  
    POS\_FILES\_USED ARRAY,  
    SPS\_FILE\_USED STRING,  
    OUTPUT\_S3\_KEY STRING,  
    OUTPUT\_ROW\_COUNT NUMBER,  
    SNOWFLAKE\_TASK\_TRIGGERED BOOLEAN DEFAULT FALSE,  
    TASK\_TRIGGERED\_AT TIMESTAMP\_NTZ,  
    ERROR\_MESSAGE STRING  
\);

# 9\. State Machine

__State__

__Meaning__

__Next Valid Transitions__

WAITING\_FOR\_FILES

No relevant files registered for the week\.

PARTIAL\_POS\_RECEIVED, WAITING\_FOR\_SPS

PARTIAL\_POS\_RECEIVED

One or more POS files received, but final POS not detected\.

POS\_COMPLETE, ERROR

POS\_COMPLETE

Final POS detected and POS set considered complete\.

READY\_TO\_PROCESS, WAITING\_FOR\_SPS, NEEDS\_REVIEW

WAITING\_FOR\_SPS

POS complete but SPS missing\.

READY\_TO\_PROCESS, NEEDS\_REVIEW

READY\_TO\_PROCESS

POS complete and SPS rule satisfied\.

MERGING

MERGING

Merge engine running\.

MERGED\_OUTPUT\_UPLOADED, ERROR

MERGED\_OUTPUT\_UPLOADED

Output generated and uploaded to S3\.

SNOWFLAKE\_TASK\_TRIGGERED, ERROR

SNOWFLAKE\_TASK\_TRIGGERED

TASK\_DAG executed\.

PROCESSED, ERROR

PROCESSED

Week completed successfully\.

Manual reprocess only

NEEDS\_REVIEW

Ambiguous or missing business rule\.

Manual resolution

ERROR

Technical failure occurred\.

Retry or manual resolution

# 10\. Completeness Logic

The highest\-risk decision is determining whether a week is complete\. V1 should encode the current best understanding while making the final POS rule explicitly configurable and observable\.

def evaluate\_week\_state\(week\_end\_date\):  
    files = fetch\_files\_from\_snowflake\(week\_end\_date\)  
    pos\_files = \[f for f in files if f\.file\_type == 'POS'\]  
    sps\_files = \[f for f in files if f\.file\_type == 'SPS'\]  
  
    pos\_complete = any\(is\_final\_pos\_file\(f\) for f in pos\_files\)  
    sps\_received = len\(sps\_files\) > 0  
  
    if not pos\_files:  
        return 'WAITING\_FOR\_FILES'  
    if not pos\_complete:  
        return 'PARTIAL\_POS\_RECEIVED'  
    if pos\_complete and sps\_received:  
        return 'READY\_TO\_PROCESS'  
    if pos\_complete and not sps\_received:  
        return 'WAITING\_FOR\_SPS'  \# or NEEDS\_REVIEW depending on cutoff/business rule  


## 11\. Final POS Detection

Claude Code should not invent the final POS detection rule\. Implement it as a function with clearly isolated logic and TODOs where business confirmation is required\.

def is\_final\_pos\_file\(file\_metadata\) \-> bool:  
    """  
    Return True only when the POS file indicates weekly completeness\.  
    Implementation options to confirm:  
    1\. Filename date equals expected week\-ending date\.  
    2\. File contents contain final\-period marker\.  
    3\. Known cutoff convention, likely Saturday\.  
    4\. Existing manual convention from current Pacifica process\.  
    """  
    \# V1 placeholder: implement confirmed rule only\. Do not guess silently\.  
    return file\_metadata\.file\_date == file\_metadata\.week\_end\_date

# 12\. Lambda Orchestrator Requirements

The Lambda should be small, idempotent, and explicit\. It should not own durable state locally\. It should read and write state through Snowflake\.

- Input: S3 ObjectCreated event for Pacifica landing\-zone files\.
- Parse bucket and key from event\.
- Classify file type as POS or SPS using case\-insensitive filename detection\.
- Extract file date and infer week\_end\_date\.
- Compute checksum or use S3 ETag if appropriate\.
- Register file in PACIFICA\_INGESTION\_FILES using idempotent MERGE semantics\.
- Update PACIFICA\_INGESTION\_STATE for the week\.
- Evaluate completeness using Snowflake state\.
- If READY\_TO\_PROCESS and not already processed, run merge engine\.
- Upload merged output to S3\.
- Trigger Snowflake TASK\_DAG\.
- Write run log and update final state\.

def lambda\_handler\(event, context\):  
    for record in event\['Records'\]:  
        bucket, key = parse\_s3\_record\(record\)  
        metadata = build\_file\_metadata\(bucket, key\)  
  
        upsert\_file\_registry\(metadata\)      \# Snowflake MERGE  
        update\_weekly\_state\(metadata\)       \# Snowflake MERGE/UPDATE  
  
        week\_state = evaluate\_week\_state\(metadata\.week\_end\_date\)  
        persist\_week\_state\(metadata\.week\_end\_date, week\_state\)  
  
        if week\_state == 'READY\_TO\_PROCESS':  
            if not already\_processed\(metadata\.week\_end\_date\):  
                process\_week\(metadata\.week\_end\_date\)  
            else:  
                log\_skip\(metadata\.week\_end\_date, reason='Already processed'\)  


# 13\. Merge Engine Refactor

The existing parse\_852\_edi\_py script should be refactored so Claude Code does not preserve manual hardcoded date editing\. The merge logic should become callable from Lambda or a local runner\.

def merge\_pacifica\_week\(  
    pos\_file\_paths: list\[str\],  
    sps\_file\_path: str | None,  
    output\_path: str,  
    week\_end\_date: str,  
\) \-> str:  
    """  
    Merge all POS files for the week and the corresponding SPS file\.  
    Return the output path\. Raise explicit exceptions on validation failure\.  
    """  
    validate\_pos\_files\(pos\_file\_paths\)  
    pos\_df = merge\_pos\_files\(pos\_file\_paths\)  
  
    if sps\_file\_path is None:  
        raise MissingSPSFileError\('SPS missing and POS\-only mode not approved for V1'\)  
  
    sps\_df = parse\_sps\_file\(sps\_file\_path\)  
    merged\_df = apply\_existing\_parse\_852\_merge\_logic\(pos\_df, sps\_df\)  
    validate\_merged\_output\(merged\_df\)  
    write\_output\(merged\_df, output\_path\)  
    return output\_path

# 14\. Snowflake Task Trigger

After the merged output is successfully uploaded, execute the existing Snowflake task\. The exact connector mechanism can use the current project conventions, but the SQL must remain explicit\.

USE ROLE DATA\_SCIENTIST\_ROLE;  
USE DATABASE COOPERAI\_PROD;  
USE SCHEMA PACIFICA;  
EXECUTE TASK TASK\_DAG;

# 15\. Idempotency and Reprocessing

V1 must prevent accidental duplicate processing\. Before running a merge, query PACIFICA\_INGESTION\_STATE for the week\_end\_date\. If PROCESSED is true and no explicit force\_reprocess flag exists, skip processing and log the skip\.

def already\_processed\(week\_end\_date\):  
    row = query\_snowflake\("""  
        SELECT PROCESSED, STATUS  
        FROM PACIFICA\_INGESTION\_STATE  
        WHERE WEEK\_END\_DATE = %s  
    """, \[week\_end\_date\]\)  
    return row and row\['PROCESSED'\] is True

For reprocessing, implement a controlled reset function or script that sets PROCESSED = FALSE, READY\_TO\_PROCESS = TRUE, STATUS = READY\_TO\_PROCESS, and records the reason in the run log\. Do not overwrite previous run logs\.

# 16\. Error Handling and Review Rules

__Condition__

__Action__

__State__

POS incomplete

Register file and wait

PARTIAL\_POS\_RECEIVED

POS complete but SPS missing

Wait or route to review depending on cutoff rule

WAITING\_FOR\_SPS or NEEDS\_REVIEW

Duplicate file arrival

Ignore duplicate after Snowflake MERGE detects existing checksum/key

No state change

Merge exception

Capture stack/error message in Snowflake

ERROR

Output upload failure

Do not trigger TASK\_DAG; log failure

ERROR

Snowflake task failure

Log failure and leave week recoverable

ERROR

Attempted duplicate processing

Skip unless force\_reprocess approved

PROCESSED

# 17\. Monitoring and Audit Requirements

- Every file arrival is visible in PACIFICA\_INGESTION\_FILES\.
- Every week has one row in PACIFICA\_INGESTION\_STATE\.
- Every processing attempt writes to PACIFICA\_INGESTION\_RUN\_LOG\.
- Missing SPS after POS completion should be visible as WAITING\_FOR\_SPS or NEEDS\_REVIEW\.
- A failed merge must preserve enough error context to debug without rerunning blindly\.
- A successful run must record output\_s3\_key, processed\_at, and Snowflake task trigger timestamp\.

# 18\. Claude Code Implementation Instructions

- Do not introduce new external state stores unless explicitly requested later\.
- Use Snowflake as the control plane for state, registry, and run logs\.
- Refactor existing parse\_852\_edi\_py logic rather than rewriting the business logic from scratch\.
- Make filename matching case\-insensitive for SPS\.
- Keep final POS detection isolated in one function so the business rule can be corrected easily\.
- Use idempotent Snowflake MERGE statements for file registry updates\.
- Never trigger TASK\_DAG before output upload succeeds\.
- Never process a week already marked PROCESSED unless an explicit reprocess path is invoked\.
- Surface missing or ambiguous SPS behavior instead of silently proceeding\.

# 19\. Implementation Roadmap

__Phase__

__Deliverable__

__Acceptance Criteria__

__Notes__

1

Refactor parse\_852\_edi\_py

No hardcoded dates/paths; callable merge\_pacifica\_week function

Preserve existing merge semantics

2

Create Snowflake control tables

DDL created for files, state, run log

Snowflake only

3

Build file classifier

POS/SPS detection works; SPS case\-insensitive

Unit\-test filename patterns

4

Build Lambda state updater

S3 event upserts file metadata and weekly state

Use idempotent MERGE

5

Implement completeness gate

Processing waits until POS complete and SPS rule satisfied

Final POS logic isolated

6

Implement merge execution

All POS files for week merged with SPS and output uploaded

No TASK\_DAG on failure

7

Trigger Snowflake TASK\_DAG

Task executes after successful upload and logs status

Use existing role/db/schema

8

Monitoring and recovery

ERROR/NEEDS\_REVIEW visible; reprocess path documented

Do not overwrite run history

# 20\. V1 Success Criteria

- Pacifica file arrivals are automatically detected from S3\.
- All file arrivals are registered in Snowflake\.
- Weekly ingestion state is visible and queryable in Snowflake\.
- POS files are accumulated until completeness is detected\.
- SPS detection is case\-insensitive\.
- Missing SPS does not silently produce an invalid output\.
- Merged output is generated and uploaded automatically only when the week is ready\.
- TASK\_DAG is triggered only after successful output upload\.
- Duplicate processing is prevented through Snowflake state checks\.
- Failures are logged with enough context for debugging and recovery\.

# 21\. Open Business Questions

- What is the authoritative rule for identifying the final POS file?
- Is SPS required every week, or can POS\-only processing ever be valid?
- What is the official weekly cutoff day/time?
- Can POS files arrive after the final POS file? If yes, should the week be reprocessed?
- What is the exact output S3 path convention for merged files?
- Should alerts be sent to Slack, email, Snowflake\-only status tables, or existing Cooper monitoring?
- What validation metrics define a successful Pacifica load beyond task completion?

Bottom line: V1 should automate the repeatable Pacifica ingestion backbone while keeping Snowflake as the single source of truth for operational state\. The architecture should gate on weekly data readiness instead of assuming that file arrival equals process readiness\.
