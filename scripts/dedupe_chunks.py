"""Deduplicate identical chunks across the corpus in Postgres.

Implementation step 6 of claude.md: exact, deterministic, no LLM.

Duplicate chunks (same chunk_type and same normalized-text SHA-256, per
the hashes precomputed in step 5) are resolved to one canonical chunk.
Nothing is deleted: duplicate rows keep their document_id and character
offsets — the provenance chain required by claude.md — and simply point
at their canonical row via chunks.duplicate_of. Downstream steps read
the deduplicated corpus through the chunks_deduped view.

Canonical selection is deterministic: within a duplicate group, the chunk
whose document has the lexicographically smallest relative_path (then the
smallest chunk_index) wins. Re-running recomputes the mapping from
scratch, so the result is idempotent and reflects the current chunk set.

Usage:
    python scripts/dedupe_chunks.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg

REPO_ROOT = Path(__file__).resolve().parent.parent

SCHEMA = """
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS duplicate_of BIGINT
    REFERENCES chunks(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS chunks_duplicate_of_idx ON chunks (duplicate_of);
CREATE OR REPLACE VIEW chunks_deduped AS
    SELECT * FROM chunks WHERE duplicate_of IS NULL;
"""

DEDUPE = """
WITH ranked AS (
    SELECT c.id,
           first_value(c.id) OVER (
               PARTITION BY c.chunk_type, c.text_norm_sha256
               ORDER BY d.relative_path, c.chunk_index
           ) AS canonical_id
    FROM chunks c
    JOIN documents d ON d.id = c.document_id
)
UPDATE chunks
SET duplicate_of = CASE WHEN ranked.id = ranked.canonical_id
                        THEN NULL ELSE ranked.canonical_id END
FROM ranked
WHERE chunks.id = ranked.id
  AND chunks.duplicate_of IS DISTINCT FROM
      CASE WHEN ranked.id = ranked.canonical_id
           THEN NULL ELSE ranked.canonical_id END
"""


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    env_file = REPO_ROOT / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            key, _, value = line.strip().partition("=")
            if key == "DATABASE_URL" and value:
                return value
    print("error: DATABASE_URL not set and not found in .env", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    with psycopg.connect(database_url()) as conn:
        for statement in SCHEMA.strip().split(";"):
            if statement.strip():
                conn.execute(statement)

        changed = conn.execute(DEDUPE).rowcount
        conn.commit()

        total, canonical, duplicates = conn.execute(
            "SELECT count(*), count(*) FILTER (WHERE duplicate_of IS NULL), "
            "count(*) FILTER (WHERE duplicate_of IS NOT NULL) FROM chunks"
        ).fetchone()
        top = conn.execute(
            """
            SELECT left(min(text_norm), 70), count(*)
            FROM chunks
            GROUP BY chunk_type, text_norm_sha256
            HAVING count(*) > 1
            ORDER BY count(*) DESC, min(text_norm)
            LIMIT 5
            """
        ).fetchall()

    print(f"{changed} rows updated")
    print(f"{total} chunks total: {canonical} canonical, {duplicates} duplicates")
    if top:
        print("\nmost duplicated:")
        for text, count in top:
            print(f"  {count:>4}x  {text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
