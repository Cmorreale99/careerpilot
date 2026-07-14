"""Assign evidence chunks to grounded artifacts in Postgres.

Implementation step 7 of claude.md: deterministic, auditable, no LLM.

Artifacts are defined in artifacts/registry.yaml — a human-reviewable
file where every artifact cites the corpus evidence that grounds it.
This script loads the registry into an `artifacts` table and assigns
chunks to artifacts in a `chunk_artifacts` table using three matching
methods, strongest kept when several apply to the same pair:

  document  the chunk's document is registry-mapped to the artifact
  heading   an alias appears in the chunk's markdown heading trail
  mention   an alias appears in the chunk's normalized text

Alias matching is exact and rule-based: word-boundary, case-insensitive
(curly apostrophes folded to straight ones), except ALL-CAPS aliases of
four characters or fewer (acronyms like KOS/BGG) which match
case-sensitively to avoid false positives. Every assignment records its
method and the matched alias or path, so each one is auditable back to
the rule and text that produced it. A chunk may belong to several
artifacts; chunks matching nothing stay unassigned rather than being
guessed at.

Duplicate artifact references (claude.md step 8) are resolved in the
registry with `same_as: <canonical-slug>`: the duplicate entry stays in
the registry and the artifacts table — its name, grounding, and the
evidence for the resolution remain on record — while its aliases and
document mappings fold into the canonical artifact, so all evidence
assigns to one canonical artifact and nothing is deleted. Candidates
are surfaced by scripts/dedupe_artifacts.py; adding `same_as` is a
human decision, per the claude.md rule against merging without
sufficient evidence.

Re-running rebuilds all assignments from the current registry and chunk
set, so the result is idempotent.

Usage:
    python scripts/assign_artifacts.py
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import psycopg
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "artifacts" / "registry.yaml"

ARTIFACT_TYPES = ("project", "hackathon", "professional_experience", "education")

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS artifacts (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    slug          TEXT NOT NULL UNIQUE,
    name          TEXT NOT NULL,
    artifact_type TEXT NOT NULL CHECK (artifact_type IN {ARTIFACT_TYPES!r}),
    aliases       TEXT[] NOT NULL,
    grounded_in   TEXT NOT NULL,
    same_as       TEXT
);
ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS same_as TEXT;
CREATE TABLE IF NOT EXISTS chunk_artifacts (
    chunk_id      BIGINT NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    artifact_id   BIGINT NOT NULL REFERENCES artifacts(id) ON DELETE CASCADE,
    method        TEXT NOT NULL CHECK (method IN ('document', 'heading', 'mention')),
    matched_value TEXT NOT NULL,
    PRIMARY KEY (chunk_id, artifact_id)
);
CREATE INDEX IF NOT EXISTS chunk_artifacts_artifact_idx ON chunk_artifacts (artifact_id);
"""

METHOD_RANK = {"document": 0, "heading": 1, "mention": 2}


def strip_emphasis(text: str) -> str:
    # Mammoth renders bold as __text__/**text** and underscores count as \w,
    # which would defeat the word-boundary lookarounds around an alias.
    return text.replace("__", " ").replace("**", " ")


def fold(text: str) -> str:
    return strip_emphasis(text).replace("’", "'").replace("‘", "'").lower()


def alias_pattern(alias: str) -> tuple[re.Pattern, bool]:
    """Compile an alias to a word-boundary regex; returns (pattern, case_sensitive)."""
    case_sensitive = alias.isupper() and len(alias) <= 4
    body = re.escape(alias if case_sensitive else fold(alias))
    left = r"(?<![\w])" if alias[0].isalnum() else ""
    right = r"(?![\w])" if alias[-1].isalnum() else ""
    return re.compile(left + body + right), case_sensitive


def load_registry() -> list[dict]:
    with REGISTRY_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    entries = data.get("artifacts") if isinstance(data, dict) else None
    if not entries:
        print(f"error: no artifacts found in {REGISTRY_PATH}", file=sys.stderr)
        raise SystemExit(1)
    seen_slugs: set[str] = set()
    seen_aliases: dict[str, str] = {}
    for entry in entries:
        for field in ("slug", "name", "type", "aliases", "grounded_in"):
            if field not in entry:
                print(f"error: artifact {entry.get('slug', '?')} missing '{field}'",
                      file=sys.stderr)
                raise SystemExit(1)
        if entry["type"] not in ARTIFACT_TYPES:
            print(f"error: artifact {entry['slug']} has unknown type {entry['type']}",
                  file=sys.stderr)
            raise SystemExit(1)
        if entry["slug"] in seen_slugs:
            print(f"error: duplicate slug {entry['slug']}", file=sys.stderr)
            raise SystemExit(1)
        seen_slugs.add(entry["slug"])
        entry.setdefault("documents", [])
        entry.setdefault("same_as", None)
        entry["aliases"] = [str(a) for a in entry["aliases"]]
        for alias in entry["aliases"]:
            if not alias.strip():
                print(f"error: artifact {entry['slug']} has an empty alias",
                      file=sys.stderr)
                raise SystemExit(1)

    # Resolve same_as references (step 8): validate targets, then fold each
    # duplicate's aliases and documents into its canonical entry. The
    # duplicate entry itself is kept (returned) so it stays on record.
    by_slug = {e["slug"]: e for e in entries}
    for entry in entries:
        target = entry["same_as"]
        if target is None:
            continue
        if target not in by_slug:
            print(f"error: {entry['slug']} has same_as unknown slug {target!r}",
                  file=sys.stderr)
            raise SystemExit(1)
        if target == entry["slug"] or by_slug[target]["same_as"] is not None:
            print(f"error: {entry['slug']} same_as {target!r} is self-referential "
                  "or chained (same_as targets must be canonical)", file=sys.stderr)
            raise SystemExit(1)
        canonical = by_slug[target]
        canonical["aliases"] += [a for a in entry["aliases"]
                                 if fold(a) not in {fold(x) for x in canonical["aliases"]}]
        canonical["documents"] += [d for d in entry["documents"]
                                   if d not in canonical["documents"]]

    # Alias uniqueness is enforced across *canonical* artifacts only.
    for entry in entries:
        if entry["same_as"] is not None:
            continue
        for alias in entry["aliases"]:
            key = fold(alias)
            if key in seen_aliases and seen_aliases[key] != entry["slug"]:
                print(f"error: alias {alias!r} appears in both "
                      f"{seen_aliases[key]} and {entry['slug']}", file=sys.stderr)
                raise SystemExit(1)
            seen_aliases[key] = entry["slug"]
    return entries


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
    registry = load_registry()

    with psycopg.connect(database_url()) as conn:
        for statement in SCHEMA.strip().split(";"):
            if statement.strip():
                conn.execute(statement)

        # Sync the artifacts table to the registry (registry is source of truth).
        slugs = [e["slug"] for e in registry]
        for entry in registry:
            conn.execute(
                """
                INSERT INTO artifacts (slug, name, artifact_type, aliases, grounded_in, same_as)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (slug) DO UPDATE SET
                    name = EXCLUDED.name, artifact_type = EXCLUDED.artifact_type,
                    aliases = EXCLUDED.aliases, grounded_in = EXCLUDED.grounded_in,
                    same_as = EXCLUDED.same_as
                """,
                (entry["slug"], entry["name"], entry["type"],
                 entry["aliases"], entry["grounded_in"], entry["same_as"]),
            )
        removed = conn.execute(
            "DELETE FROM artifacts WHERE slug != ALL(%s)", (slugs,)
        ).rowcount
        if removed:
            print(f"removed {removed} artifacts no longer in the registry")
        artifact_ids = dict(conn.execute("SELECT slug, id FROM artifacts").fetchall())

        # Only canonical artifacts match and receive assignments; same_as
        # entries have already folded their aliases/documents into them.
        canonical = [e for e in registry if e["same_as"] is None]

        # Validate document mappings against the ingested corpus.
        known_paths = {p for (p,) in conn.execute("SELECT relative_path FROM documents")}
        doc_map: dict[str, list[str]] = {}
        for entry in canonical:
            for doc in entry["documents"]:
                if doc not in known_paths:
                    print(f"warning: {entry['slug']} maps unknown document: {doc}",
                          file=sys.stderr)
                    continue
                doc_map.setdefault(doc, []).append(entry["slug"])

        matchers = [
            (entry["slug"], alias, *alias_pattern(alias))
            for entry in canonical for alias in entry["aliases"]
        ]

        # Rebuild all assignments from scratch (deterministic, idempotent).
        conn.execute("DELETE FROM chunk_artifacts")
        assignments: dict[tuple[int, str], tuple[str, str]] = {}

        def propose(chunk_id: int, slug: str, method: str, matched: str) -> None:
            key = (chunk_id, slug)
            if key not in assignments or METHOD_RANK[method] < METHOD_RANK[assignments[key][0]]:
                assignments[key] = (method, matched)

        rows = conn.execute(
            """
            SELECT c.id, d.relative_path, c.text, c.text_norm, c.heading_path
            FROM chunks c JOIN documents d ON d.id = c.document_id
            """
        )
        for chunk_id, relative_path, text, text_norm, heading_path in rows:
            for slug in doc_map.get(relative_path, []):
                propose(chunk_id, slug, "document", relative_path)
            heading_blob = " > ".join(heading_path)
            heading_folded, text_folded = fold(heading_blob), fold(text_norm)
            for slug, alias, pattern, case_sensitive in matchers:
                heading_hay = strip_emphasis(heading_blob) if case_sensitive else heading_folded
                text_hay = strip_emphasis(text) if case_sensitive else text_folded
                if pattern.search(heading_hay):
                    propose(chunk_id, slug, "heading", alias)
                elif pattern.search(text_hay):
                    propose(chunk_id, slug, "mention", alias)

        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO chunk_artifacts (chunk_id, artifact_id, method, matched_value) "
                "VALUES (%s, %s, %s, %s)",
                [(chunk_id, artifact_ids[slug], method, matched)
                 for (chunk_id, slug), (method, matched) in assignments.items()],
            )
        conn.commit()

        resolved = [(e["slug"], e["same_as"]) for e in registry if e["same_as"]]
        print(f"{len(assignments)} assignments written for {len(canonical)} canonical "
              f"artifacts ({len(resolved)} resolved via same_as)")
        for slug, target in resolved:
            print(f"  {slug} -> {target}")
        print()
        stats = conn.execute(
            """
            SELECT a.slug, a.artifact_type, count(*) AS chunks,
                   count(*) FILTER (WHERE ca.method = 'document') AS by_doc,
                   count(*) FILTER (WHERE ca.method = 'heading')  AS by_heading,
                   count(*) FILTER (WHERE ca.method = 'mention')  AS by_mention
            FROM artifacts a JOIN chunk_artifacts ca ON ca.artifact_id = a.id
            GROUP BY a.slug, a.artifact_type ORDER BY chunks DESC
            """
        ).fetchall()
        print(f"{'artifact':<34} {'type':<24} {'chunks':>6} {'doc':>6} {'head':>5} {'ment':>5}")
        for slug, kind, chunks, by_doc, by_heading, by_mention in stats:
            print(f"{slug:<34} {kind:<24} {chunks:>6} {by_doc:>6} {by_heading:>5} {by_mention:>5}")
        assigned_slugs = {s for s, *_ in stats}
        canonical_slugs = {e["slug"] for e in canonical}
        for slug in sorted(canonical_slugs - assigned_slugs):
            print(f"{slug:<34} (no chunks assigned)")

        unassigned = conn.execute(
            """
            SELECT count(*) FROM chunks c
            WHERE c.duplicate_of IS NULL
              AND NOT EXISTS (SELECT 1 FROM chunk_artifacts ca WHERE ca.chunk_id = c.id)
            """
        ).fetchone()[0]
        print(f"\ncanonical chunks with no artifact: {unassigned}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
