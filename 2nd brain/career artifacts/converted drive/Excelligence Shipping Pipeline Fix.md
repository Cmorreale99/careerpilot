---
source_file: "2nd brain/career artifacts/raw drive/Excelligence Shipping Pipeline Fix.docx"
source_sha256: c8ce1dc4a6c46ef6b97fcdddef910a5d6807b3a3d91e7d910f5a74b2d22bc33e
converter: mammoth 1.12.0
---

Excelligence Shipping Pipeline Fix — Summary

The Problem

The Excelligence shipping ingestion loads four carriers \(Kenco, FedEx, UPS, Pitney Bowes\) into Snowflake daily\. Each carrier sends a rolling ~90\-day file, and the pipeline keeps recent data fresh while letting history accumulate via a date\-range refresh: for each file it finds the min/max date, deletes that date range from staging, then re\-inserts the file\. Two defects were corrupting this:

\- Problem A — Wrong dedup date column \(all carriers\)\. The refresh deduped on "the earliest date column it could find" rather than the specific field each carrier windows its 90 days on\. When the delete range didn't match the file's true window, the pipeline deleted more than it added back, leaving gaps — most visibly missing February data\.

\- Problem B — FedEx schema mismatch \+ runaway duplication\. FedEx moved to a modern 22\-column billing export\. The dedup was keyed on INVOICEDATE\_MM\_DD\_YYYY, which is only ~10% populated in that export, so the ~90% of rows with a NULL invoice date were never deleted but re\-inserted every run — silent, compounding duplication\. The downstream FACT\_FEDEX\_SHIPPING also referenced a renamed column and was broken\.

Making it harder: the "correct" dedup columns had been relayed verbally and weren't exact \(one was a typo\), so every value had to be verified against the real files\.

What I Solved

\- Closed the data gaps by deduping each carrier on the correct, fully\-populated date field\.

\- Found and fixed the silent failure mode that had been hiding the bug\.

\- Identified and corrected FedEx's 195,528 duplicate rows \(37% of the table\) and rebuilt its fact layer\.

\- Hardened the pipeline so this class of bug fails loudly going forward\.

How I Solved It

Investigation: Traced the ingest, found the per\-carrier dedup column was driven by a lookup whose values were wrong, with a silent fallback masking the mismatch\. Verified real column names against the staging tables, fact definitions, and actual CSV headers — not the verbally\-relayed values\.

Phase 1 \(Kenco / UPS / PB\):

\- Corrected dedup keys: Kenco → ACTUAL\_DROP \(was ship date\), Pitney Bowes → STATUSDATE \(was ship date\), UPS already correct \(INVOICEDATE\)\.

\- Replaced the silent fallback with a hard\-fail so a missing/wrong dedup column raises instead of silently corrupting the window\.

Phase 2 \(FedEx\):

\- Verified the 22\-column export; found delivery/invoice dates ~10% populated but SHIPMENTDATE 100% populated — the true window key\. Switched FedEx to SHIPMENTDATE and removed the temporary carve\-out\.

\- Wrote migration V1\.1\.276 rebuilding FACT\_FEDEX\_SHIPPING \(ship\_date from SHIPMENTDATE; added SHIPMENTDATE as the fallback for primary\_activity\_date, which was otherwise ~90% NULL\)\.

\- Specified a drop\+reload to purge the existing 195K duplicates\.

Validation \(Dev, before any prod change\):

\- Phase 1: symmetric refresh confirmed; UPS February gap filled \(17,772 rows\); Kenco/PB's missing February confirmed as an upstream source reality, not a pipeline loss\.

\- Phase 2 \(SQL simulation, no deploy\): old key would strand 470,508 rows/run \(the bug\) vs 0 for SHIPMENTDATE \(the fix\); deduped count 326,426; symmetric refresh covers 100% of rows; Feb–May continuous; FACT date coverage 100% \(was ~10%\)\.

Delivery: Shipped as two clean PRs — Phase 1 merged \(\#658\); Phase 2 rebased to a FedEx\-only diff\. ruff\-clean; validated via Dev row counts and SQL simulation\.

Value Added

\- Restored data completeness — closed the February gap and stopped the pipeline from deleting more than it reloaded; shipping facts are trustworthy again\.

\- Removed 37% duplication on FedEx \(~195K rows\), collapsing to the true ~326K and preventing recurrence\.

\- Made the FedEx fact usable — primary\_activity\_date from ~90% NULL to 100% populated\.

\- Turned a silent failure into a loud one — future schema drift now fails the run immediately, a durable safeguard beyond this bug\.

\- De\-risked the rollout — verified every column against real data, validated entirely in Dev, and surfaced a latent NULL\-date duplication risk for other carriers as a follow\-up\.
