---
source_file: "2nd brain/career artifacts/raw drive/Pacifica weekly ingestion pattern 2.docx"
source_sha256: 844f981207975e93dd0e42ff95c0b905650df5e95857870d890a7ff718f82b78
converter: mammoth 1.12.0
---

1. Download POS and SPS files from S3 bucket 
2. Merge them with the parse\_852\_edi\_py file
3. Open the merged file
4. Upload it to S3
5. Go to snowflake and trigger the DAG with USE ROLE DATA\_SCIENTIST\_ROLE; USE DATABASE COOPERAI\_PROD; USE SCHEMA PACIFICA; EXECUTE TASK TASK\_DAG;
6. Go to snowflake and click tasks, then see when the last run was \(should say just now or 1 min ago\)
