"""Ingest all raw Markdown from the 2nd brain corpus into Postgres.

Implementation step 4 of claude.md: deterministic, auditable, no LLM.
Every `.md` file under `2nd brain/` (excluding the `.obsidian/` vault
config) is stored as one row in the `documents` table. Traceability chain:

  documents.relative_path  -> the markdown file in the repo
  documents.content_sha256 -> hash of that file's exact bytes
  documents.frontmatter    -> parsed YAML frontmatter; for converted files
                              this carries source_file / source_sha256
                              pointing at the original .pdf/.docx

Ingestion is idempotent: rows are upserted by relative_path and untouched
when the content hash is unchanged, so re-runs are safe. Rows whose files
have disappeared from disk are reported (and only deleted with --prune).

Usage:
    python scripts/ingest_corpus.py            # ingest/refresh the corpus
    python scripts/ingest_corpus.py --prune    # also delete orphaned rows

Connection comes from DATABASE_URL (environment, falling back to the
repo-root .env file).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import psycopg
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS_ROOT = REPO_ROOT / "2nd brain"
EXCLUDED_DIRS = {".obsidian"}

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    relative_path   TEXT NOT NULL UNIQUE,
    content_sha256  TEXT NOT NULL,
    frontmatter     JSONB,
    source_file     TEXT,
    source_sha256   TEXT,
    body            TEXT NOT NULL,
    byte_size       BIGINT NOT NULL,
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
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


def corpus_files() -> list[Path]:
    files = [
        p for p in CORPUS_ROOT.rglob("*.md")
        if not EXCLUDED_DIRS.intersection(part for part in p.relative_to(CORPUS_ROOT).parts)
    ]
    return sorted(files, key=lambda p: p.relative_to(REPO_ROOT).as_posix())


def split_frontmatter(text: str) -> tuple[dict | None, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text
    try:
        parsed = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None, text
    if not isinstance(parsed, dict):
        return None, text
    return parsed, text[match.end():]


def ingest(prune: bool) -> int:
    files = corpus_files()
    if not files:
        print(f"error: no markdown files found under {CORPUS_ROOT}", file=sys.stderr)
        return 1

    inserted = updated = unchanged = 0
    with psycopg.connect(database_url()) as conn:
        conn.execute(SCHEMA)

        existing = dict(conn.execute(
            "SELECT relative_path, content_sha256 FROM documents"
        ).fetchall())

        seen: set[str] = set()
        for path in files:
            relative = path.relative_to(REPO_ROOT).as_posix()
            seen.add(relative)
            raw = path.read_bytes()
            content_hash = hashlib.sha256(raw).hexdigest()

            if existing.get(relative) == content_hash:
                unchanged += 1
                continue

            frontmatter, body = split_frontmatter(raw.decode("utf-8"))
            source_file = frontmatter.get("source_file") if frontmatter else None
            source_sha256 = frontmatter.get("source_sha256") if frontmatter else None

            conn.execute(
                """
                INSERT INTO documents
                    (relative_path, content_sha256, frontmatter, source_file,
                     source_sha256, body, byte_size)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (relative_path) DO UPDATE SET
                    content_sha256 = EXCLUDED.content_sha256,
                    frontmatter    = EXCLUDED.frontmatter,
                    source_file    = EXCLUDED.source_file,
                    source_sha256  = EXCLUDED.source_sha256,
                    body           = EXCLUDED.body,
                    byte_size      = EXCLUDED.byte_size,
                    updated_at     = now()
                """,
                (relative, content_hash,
                 json.dumps(frontmatter, ensure_ascii=False, default=str) if frontmatter else None,
                 source_file, source_sha256, body, len(raw)),
            )
            if relative in existing:
                updated += 1
                print(f"updated   {relative}")
            else:
                inserted += 1
                print(f"inserted  {relative}")
            if not body.strip():
                print(f"          note: {relative} has an empty body")

        orphans = sorted(set(existing) - seen)
        if orphans:
            if prune:
                conn.execute(
                    "DELETE FROM documents WHERE relative_path = ANY(%s)", (orphans,)
                )
            for relative in orphans:
                print(f"{'pruned' if prune else 'orphaned'}    {relative}")

        conn.commit()
        total = conn.execute("SELECT count(*) FROM documents").fetchone()[0]

    print(
        f"\n{inserted} inserted, {updated} updated, {unchanged} unchanged, "
        f"{len(orphans)} orphaned{' (pruned)' if prune and orphans else ''}; "
        f"{total} documents in database"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--prune", action="store_true",
                        help="delete rows whose source files no longer exist")
    args = parser.parse_args()
    return ingest(prune=args.prune)


if __name__ == "__main__":
    raise SystemExit(main())
