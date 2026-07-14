"""Detect candidate duplicate artifact references in the corpus.

Implementation step 8 of claude.md (detection half): deterministic,
auditable, no LLM. This script only REPORTS — merging is a human
decision recorded in artifacts/registry.yaml via `same_as` (see
scripts/assign_artifacts.py), because claude.md requires artifacts that
merely *might* be the same to stay separate.

Three deterministic signals, each printed with its concrete evidence:

  co-assignment   chunks assigned to both artifacts of a pair
  cross-document  an artifact's alias matched inside a document that is
                  wholly mapped to a different artifact
  name overlap    shared non-generic name/alias tokens between artifacts

Resolving a pair does not delete evidence: a `same_as` merge folds the
duplicate's aliases and documents into the canonical artifact and keeps
the duplicate's registry entry and grounding on record.

Usage:
    python scripts/dedupe_artifacts.py
"""

from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import psycopg

REPO_ROOT = Path(__file__).resolve().parent.parent

# Tokens too generic to signal that two artifact names refer to one thing.
GENERIC_TOKENS = {
    "ai", "data", "system", "platform", "pipeline", "engine", "os", "the",
    "and", "of", "a", "management", "analytics", "learning", "market",
    "workflow", "wpi", "boston", "hackathon", "decentralized", "tokenized",
    "automation", "ingestion", "architecture", "science", "bs", "ms",
}


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


def tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower())
            if len(t) > 1 and t not in GENERIC_TOKENS}


def main() -> int:
    with psycopg.connect(database_url()) as conn:
        artifacts = conn.execute(
            "SELECT id, slug, name, aliases, "
            "       coalesce(same_as, '') FROM artifacts ORDER BY slug"
        ).fetchall()
        resolved = {slug: same for _, slug, _, _, same in artifacts if same}
        if resolved:
            print("already resolved via same_as:")
            for slug, same in sorted(resolved.items()):
                print(f"  {slug} -> {same}")
            print()

        candidates: dict[tuple[str, str], list[str]] = defaultdict(list)

        # Signal 1: chunks assigned to both artifacts of a pair.
        for a, b, n, sample in conn.execute("""
            SELECT x.slug, y.slug, count(*),
                   left(min(c.text_norm), 90)
            FROM chunk_artifacts ca
            JOIN chunk_artifacts cb ON cb.chunk_id = ca.chunk_id
                                   AND cb.artifact_id > ca.artifact_id
            JOIN artifacts x ON x.id = ca.artifact_id
            JOIN artifacts y ON y.id = cb.artifact_id
            JOIN chunks c ON c.id = ca.chunk_id
            GROUP BY x.slug, y.slug ORDER BY x.slug, y.slug
        """):
            candidates[(a, b)].append(
                f"co-assignment: {n} shared chunks (e.g. \"{sample}\")")

        # Signal 2: alias of A matched by mention/heading inside a document
        # wholly mapped (document method) to B.
        for a, b, n, docs in conn.execute("""
            SELECT x.slug, y.slug, count(*),
                   array_agg(DISTINCT split_part(d.relative_path, '/', 4))
            FROM chunk_artifacts ca
            JOIN chunks c ON c.id = ca.chunk_id
            JOIN documents d ON d.id = c.document_id
            JOIN artifacts x ON x.id = ca.artifact_id
            JOIN chunk_artifacts cb ON cb.chunk_id = ca.chunk_id
                                   AND cb.method = 'document'
                                   AND cb.artifact_id != ca.artifact_id
            JOIN artifacts y ON y.id = cb.artifact_id
            WHERE ca.method IN ('mention', 'heading')
            GROUP BY x.slug, y.slug ORDER BY x.slug, y.slug
        """):
            pair = tuple(sorted((a, b)))
            candidates[pair].append(
                f"cross-document: {a} referenced {n}x inside document(s) "
                f"mapped to {b}: {', '.join(sorted(docs))}")

        # Signal 3: shared non-generic tokens across name + aliases.
        namesets = {slug: tokens(name) | set().union(*(tokens(al) for al in aliases))
                    for _, slug, name, aliases, _ in artifacts}
        for a, b in combinations(sorted(namesets), 2):
            shared = namesets[a] & namesets[b]
            if shared:
                candidates[(a, b)].append(
                    f"name overlap: shared tokens {sorted(shared)}")

        if not candidates:
            print("no duplicate-artifact candidates found")
            return 0

        print(f"{len(candidates)} candidate pairs (strongest first); "
              "resolve real duplicates by adding `same_as` in "
              "artifacts/registry.yaml and re-running assign_artifacts.py:\n")
        ranked = sorted(candidates.items(),
                        key=lambda kv: (-len(kv[1]), kv[0]))
        for (a, b), signals in ranked:
            print(f"{a}  <->  {b}")
            for signal in signals:
                print(f"    {signal}")
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
