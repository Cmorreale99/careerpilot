"""Chunk every ingested 2nd brain document into sentences in Postgres.

Implementation step 5 of claude.md: deterministic, auditable, no LLM.
Reads the `documents` table populated by ingest_corpus.py and writes a
`chunks` table. Traceability chain for every chunk:

  chunks.document_id           -> documents row (which traces to the file
                                  and, for converted docs, the original
                                  .pdf/.docx bytes)
  chunks.char_start/char_end   -> exact span inside documents.body
  chunks.heading_path          -> markdown heading trail above the chunk

Markdown is split structurally first — headings, list items, and table
rows become one chunk each, fenced code blocks stay whole — and paragraph
text is then split into sentences by a rule-based splitter (regex plus an
abbreviation list; no model involved). HTML comments such as the
converter's `<!-- source page N -->` markers are skipped: the page number
is instead recorded on each chunk while it is in effect.

`text_norm_sha256` is the SHA-256 of the whitespace-collapsed,
markdown-unescaped chunk text; step 6 uses it for exact deduplication.

Chunking is idempotent: a document is re-chunked only when its
content_sha256 differs from the hash recorded at its last chunking
(documents.chunked_sha256); its old chunks are then replaced atomically.

Usage:
    python scripts/chunk_documents.py            # chunk new/changed docs
    python scripts/chunk_documents.py --rechunk  # force re-chunk of all
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

import psycopg

REPO_ROOT = Path(__file__).resolve().parent.parent

SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id      BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index      INTEGER NOT NULL,
    chunk_type       TEXT NOT NULL CHECK (chunk_type IN
                         ('sentence', 'heading', 'list_item', 'table_row', 'code')),
    text             TEXT NOT NULL,
    text_norm        TEXT NOT NULL,
    text_norm_sha256 TEXT NOT NULL,
    char_start       INTEGER NOT NULL,
    char_end         INTEGER NOT NULL,
    heading_path     TEXT[] NOT NULL DEFAULT '{}',
    source_page      INTEGER,
    UNIQUE (document_id, chunk_index)
);
CREATE INDEX IF NOT EXISTS chunks_norm_sha_idx ON chunks (text_norm_sha256);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS chunked_sha256 TEXT;
"""

PAGE_MARKER_RE = re.compile(r"<!--\s*source page (\d+)\s*-->")
HTML_COMMENT_RE = re.compile(r"^\s*<!--.*-->\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\S")
TABLE_ROW_RE = re.compile(r"^\s*\|")
FENCE_RE = re.compile(r"^\s*(```|~~~)")

# A period after one of these tokens does not end a sentence.
ABBREVIATIONS = {
    "e.g", "i.e", "etc", "vs", "cf", "approx", "no", "dept", "inc", "corp",
    "dr", "mr", "mrs", "ms", "jr", "sr", "st", "jan", "feb", "mar", "apr",
    "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec", "fig", "vol",
}

BOUNDARY_RE = re.compile(r"[.!?]+[\"')\]]*\s+(?=[\"'(\[]?[A-Z0-9])")
UNESCAPE_RE = re.compile(r"\\([\\`*_{}\[\]()#+.!><~|-])")

# Sentence spans longer than this are split at line breaks (layout text).
MAX_SENTENCE_CHARS = 400


def normalize(text: str) -> str:
    return " ".join(UNESCAPE_RE.sub(r"\1", text).split())


def split_sentences(text: str) -> list[tuple[int, int]]:
    """Return (start, end) spans of sentences within *text*."""
    boundaries = []
    for match in BOUNDARY_RE.finditer(text):
        before = text[: match.start() + 1]
        last_word = re.search(r"([\w.\\]+)$", before)
        token = (last_word.group(1) if last_word else "").rstrip(".").replace("\\", "").lower()
        if token in ABBREVIATIONS or re.fullmatch(r"[a-z]", token):
            continue  # abbreviation or single initial, not a boundary
        boundaries.append(match.end())
    spans, start = [], 0
    for boundary in boundaries:
        spans.append((start, boundary))
        start = boundary
    spans.append((start, len(text)))

    # Layout-style text (e.g. PDF resumes) can have no sentence punctuation
    # at all; fall back to line breaks so one page never becomes one chunk.
    line_split: list[tuple[int, int]] = []
    for s, e in spans:
        if e - s <= MAX_SENTENCE_CHARS:
            line_split.append((s, e))
            continue
        line_start = s
        for match in re.finditer(r"\n", text[s:e]):
            line_split.append((line_start, s + match.end()))
            line_start = s + match.end()
        line_split.append((line_start, e))
    return [(s, e) for s, e in line_split if text[s:e].strip()]


def chunk_body(body: str) -> list[dict]:
    """Split a markdown body into ordered, offset-tracked chunks."""
    chunks: list[dict] = []
    heading_stack: list[tuple[int, str]] = []
    source_page: int | None = None
    in_fence = False
    fence_start = 0

    def add(kind: str, start: int, end: int, text: str | None = None) -> None:
        raw = body[start:end] if text is None else text
        norm = normalize(raw)
        if not norm:
            return
        chunks.append({
            "chunk_type": kind,
            "text": raw.strip(),
            "text_norm": norm,
            "char_start": start,
            "char_end": end,
            "heading_path": [title for _, title in heading_stack],
            "source_page": source_page,
        })

    paragraph_start: int | None = None

    def flush_paragraph(end: int) -> None:
        nonlocal paragraph_start
        if paragraph_start is None:
            return
        para = body[paragraph_start:end]
        for s, e in split_sentences(para):
            add("sentence", paragraph_start + s, paragraph_start + e)
        paragraph_start = None

    pos = 0
    for line in body.splitlines(keepends=True):
        start, end = pos, pos + len(line)
        pos = end
        stripped = line.strip()

        if in_fence:
            if FENCE_RE.match(line):
                in_fence = False
                add("code", fence_start, end)
            continue

        page = PAGE_MARKER_RE.search(line)
        if page:
            flush_paragraph(start)
            source_page = int(page.group(1))
            continue
        if HTML_COMMENT_RE.match(line):
            flush_paragraph(start)
            continue
        if FENCE_RE.match(line):
            flush_paragraph(start)
            in_fence = True
            fence_start = start
            continue
        if not stripped:
            flush_paragraph(start)
            continue

        heading = HEADING_RE.match(stripped)
        if heading:
            flush_paragraph(start)
            level, title = len(heading.group(1)), normalize(heading.group(2))
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            add("heading", start, end, heading.group(2))
            heading_stack.append((level, title))
            continue
        if LIST_ITEM_RE.match(line):
            flush_paragraph(start)
            add("list_item", start, end)
            continue
        if TABLE_ROW_RE.match(line):
            flush_paragraph(start)
            add("table_row", start, end)
            continue

        if paragraph_start is None:
            paragraph_start = start

    if in_fence:  # unterminated fence: keep what we have
        add("code", fence_start, len(body))
    flush_paragraph(len(body))
    return chunks


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


def run(rechunk: bool) -> int:
    processed = skipped = total_chunks = 0
    with psycopg.connect(database_url()) as conn:
        for statement in SCHEMA.strip().split(";"):
            if statement.strip():
                conn.execute(statement)

        docs = conn.execute(
            "SELECT id, relative_path, content_sha256, chunked_sha256, body "
            "FROM documents ORDER BY relative_path"
        ).fetchall()

        for doc_id, relative_path, content_sha, chunked_sha, body in docs:
            if not rechunk and chunked_sha == content_sha:
                skipped += 1
                continue

            chunks = chunk_body(body)
            conn.execute("DELETE FROM chunks WHERE document_id = %s", (doc_id,))
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO chunks
                        (document_id, chunk_index, chunk_type, text, text_norm,
                         text_norm_sha256, char_start, char_end, heading_path,
                         source_page)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        (doc_id, index, c["chunk_type"], c["text"], c["text_norm"],
                         hashlib.sha256(c["text_norm"].encode("utf-8")).hexdigest(),
                         c["char_start"], c["char_end"], c["heading_path"],
                         c["source_page"])
                        for index, c in enumerate(chunks)
                    ],
                )
            conn.execute(
                "UPDATE documents SET chunked_sha256 = %s WHERE id = %s",
                (content_sha, doc_id),
            )
            processed += 1
            total_chunks += len(chunks)
            print(f"chunked   {relative_path} ({len(chunks)} chunks)")

        conn.commit()
        grand_total, by_type = (
            conn.execute("SELECT count(*) FROM chunks").fetchone()[0],
            conn.execute(
                "SELECT chunk_type, count(*) FROM chunks GROUP BY 1 ORDER BY 2 DESC"
            ).fetchall(),
        )

    print(
        f"\n{processed} documents chunked ({total_chunks} chunks written), "
        f"{skipped} unchanged; {grand_total} chunks in database"
    )
    print("by type: " + ", ".join(f"{kind}={count}" for kind, count in by_type))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rechunk", action="store_true",
                        help="re-chunk every document even if unchanged")
    args = parser.parse_args()
    return run(rechunk=args.rechunk)


if __name__ == "__main__":
    raise SystemExit(main())
