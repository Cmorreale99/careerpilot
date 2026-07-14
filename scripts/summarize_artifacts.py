"""Generate one-page artifact summaries with Ollama (claude.md v2 step 2).

Loops through canonical artifacts one at a time and builds each a
one-page summary containing a high-level overview, the user's
contributions, the technical and professional capabilities
demonstrated, and why the work mattered — as structured JSON from the
local Ollama model pinned in v2 step 1.

Guarantees, per the claude.md v2 constraints:
  - runs strictly downstream: reads canonical evidence via the read-only
    corpus access from app/ollama_client.py; never creates artifacts,
    assigns chunks, or modifies evidence
  - every summary preserves supporting chunk IDs; every contribution and
    capability bullet cites the chunk IDs it rests on
  - citations are validated against the artifact's actual evidence set;
    an unsupported citation or invalid output FAILS that artifact —
    there is no silent acceptance and no paid-provider fallback
  - artifacts whose evidence exceeds the context budget are summarized
    via deterministic batches (batch -> cited notes -> final reduce)
  - each artifact's summary is committed independently the moment it
    succeeds, so one failed request never forces a full re-run; re-runs
    skip artifacts whose evidence and model are unchanged

Usage:
    python scripts/summarize_artifacts.py                 # all artifacts
    python scripts/summarize_artifacts.py --artifact SLUG # just one
    python scripts/summarize_artifacts.py --force         # regenerate all
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ollama_client import (  # noqa: E402
    OllamaClient,
    OllamaError,
    batch_chunks,
    database_url,
    estimate_tokens,
    fetch_artifact_evidence,
)

# Context is 8,192 tokens; reserve room for instructions and the JSON reply.
EVIDENCE_BUDGET_TOKENS = 6000

SCHEMA = """
CREATE TABLE IF NOT EXISTS artifact_summaries (
    artifact_id          BIGINT PRIMARY KEY REFERENCES artifacts(id) ON DELETE CASCADE,
    model                TEXT NOT NULL,
    overview             TEXT NOT NULL,
    contributions        JSONB NOT NULL,
    capabilities         JSONB NOT NULL,
    why_it_mattered      TEXT NOT NULL,
    supporting_chunk_ids BIGINT[] NOT NULL,
    evidence_sha256      TEXT NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

SYSTEM_PROMPT = (
    "You summarize career evidence. You may only state facts supported by the "
    "provided evidence lines, each of which starts with its line number in "
    "brackets. Never invent projects, numbers, employers, dates, or outcomes. "
    "Cite the line numbers that support each point. Reply with a single JSON "
    "object and nothing else."
)

SUMMARY_PROMPT = """Artifact: {name}
Type: {type}

Evidence lines (format: [line number] text):
{evidence}

Write a one-page summary of this artifact as JSON with exactly these keys:
- "overview": 2-4 sentences describing at a high level what the artifact was
- "contributions": list of 1-8 objects {{"text": one contribution of the person, "chunk_ids": [line numbers of evidence lines supporting it]}} — as many as the evidence actually supports
- "capabilities": list of 1-8 objects {{"text": one technical or professional capability demonstrated, "chunk_ids": [supporting line numbers]}} — as many as the evidence actually supports
- "why_it_mattered": 2-4 sentences on why the work mattered
- "supporting_chunk_ids": list of every line number you relied on

Only use facts from the evidence lines. Cite only line numbers that appear above.
If the evidence does not support a section, return it empty ([] or "") rather
than inventing content — but extract everything the evidence does support."""

NOTES_PROMPT = """Artifact: {name}
Type: {type}

Evidence lines (format: [line number] text):
{evidence}

This is one batch of a larger evidence set. Condense it into factual notes as
JSON with exactly one key:
- "notes": list of 5-15 objects {{"text": one factual note about the person's work on this artifact, "chunk_ids": [line numbers of evidence lines supporting it]}}

Only use facts from the evidence lines. Cite only line numbers that appear above."""


def build_prompt_lines(entries: list[tuple[str, set[int]]]) -> tuple[str, dict[int, set[int]]]:
    """Number prompt lines 1..N and return the local->chunk-IDs mapping.

    Long database IDs with gaps invite the model to interpolate missing
    numbers (observed with duplicate-chunk gaps); short gapless local
    numbers avoid that, and every citation is translated back to real
    chunk IDs deterministically. An unknown local number still fails.
    """
    lines = []
    mapping: dict[int, set[int]] = {}
    for local, (text, chunk_ids) in enumerate(entries, start=1):
        lines.append(f"[{local}] {text}")
        mapping[local] = set(chunk_ids)
    return "\n".join(lines), mapping


def translate_citations(bullets, mapping: dict[int, set[int]], field: str) -> None:
    """Rewrite each bullet's local line numbers into real chunk IDs, in place."""
    if not isinstance(bullets, list):
        raise OllamaError(f"{field} must be a list")
    for bullet in bullets:
        if not isinstance(bullet, dict):
            raise OllamaError(f"{field} bullet malformed: {bullet!r}")
        locals_cited = collect_ids(bullet.get("chunk_ids", []))
        unknown = locals_cited - set(mapping)
        if unknown:
            raise OllamaError(
                f"{field} bullet cites line numbers not in the prompt: "
                f"{sorted(unknown)}")
        bullet["chunk_ids"] = sorted(
            set().union(set(), *(mapping[n] for n in locals_cited)))


def evidence_hash(chunks: list[dict]) -> str:
    payload = json.dumps([[c["chunk_id"], c["text"]] for c in chunks],
                         ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def collect_ids(value) -> set[int]:
    """All integer chunk IDs cited anywhere in a parsed model output."""
    if isinstance(value, bool):
        return set()
    if isinstance(value, int):
        return {value}
    if isinstance(value, list):
        return set().union(set(), *(collect_ids(v) for v in value))
    if isinstance(value, dict):
        return collect_ids(value.get("chunk_ids", []))
    return set()


def validate_bullets(bullets, valid_ids: set[int], field: str,
                     allow_empty: bool = False) -> None:
    if not isinstance(bullets, list) or (not bullets and not allow_empty):
        raise OllamaError(f"{field} must be a non-empty list")
    for bullet in bullets:
        if (not isinstance(bullet, dict) or not str(bullet.get("text", "")).strip()
                or not isinstance(bullet.get("chunk_ids"), list) or not bullet["chunk_ids"]):
            raise OllamaError(f"{field} bullet malformed: {bullet!r}")
        unsupported = collect_ids(bullet["chunk_ids"]) - valid_ids
        if unsupported:
            raise OllamaError(
                f"{field} bullet cites chunk IDs not in the evidence set: "
                f"{sorted(unsupported)}")


def validate_summary(summary: dict, valid_ids: set[int]) -> None:
    """Enforce citations and substance without forcing invention.

    Sections may be empty when the evidence genuinely does not support
    them (claude.md: the LLM must not invent claims), but the overview
    must exist, every present bullet must cite in-set chunk IDs, and the
    summary as a whole must contain at least one cited bullet.
    """
    if not str(summary.get("overview", "")).strip():
        raise OllamaError("summary field overview is empty")
    if not isinstance(summary.get("why_it_mattered", ""), str):
        raise OllamaError("why_it_mattered must be a string")
    validate_bullets(summary["contributions"], valid_ids, "contributions",
                     allow_empty=True)
    validate_bullets(summary["capabilities"], valid_ids, "capabilities",
                     allow_empty=True)
    if not summary["contributions"] and not summary["capabilities"]:
        raise OllamaError(
            "summary has no cited contributions or capabilities at all")
    supporting = collect_ids(summary.get("supporting_chunk_ids", []))
    if not supporting:
        raise OllamaError("supporting_chunk_ids is empty")
    unsupported = supporting - valid_ids
    if unsupported:
        raise OllamaError(
            f"supporting_chunk_ids cites IDs not in the evidence set: "
            f"{sorted(unsupported)}")


def summarize_artifact(client: OllamaClient, evidence: dict) -> dict:
    chunks = evidence["chunks"]
    if not chunks:
        raise OllamaError("artifact has no evidence chunks")
    valid_ids = {c["chunk_id"] for c in chunks}
    batches = batch_chunks(chunks, EVIDENCE_BUDGET_TOKENS)

    if len(batches) > 1:
        # Deterministic reduce: each batch becomes cited notes (translated
        # to real chunk IDs immediately); the final summary is generated
        # from the notes, whose citations expand back to the original IDs.
        notes: list[dict] = []
        for index, batch in enumerate(batches, start=1):
            print(f"    batch {index}/{len(batches)} ({len(batch)} chunks)")
            prompt, mapping = build_prompt_lines(
                [(c["text"], {c["chunk_id"]}) for c in batch])
            result = client.generate_json(
                NOTES_PROMPT.format(name=evidence["name"], type=evidence["type"],
                                    evidence=prompt),
                required_keys=("notes",), system=SYSTEM_PROMPT)
            translate_citations(result["notes"], mapping, "notes")
            validate_bullets(result["notes"], valid_ids, "notes")
            notes.extend(result["notes"])
        entries = [(n["text"], set(n["chunk_ids"])) for n in notes]
        prompt_evidence, mapping = build_prompt_lines(entries)
        if estimate_tokens(prompt_evidence) > EVIDENCE_BUDGET_TOKENS:
            raise OllamaError(
                "condensed notes still exceed the context budget; "
                "cannot summarize within the pinned context window")
    else:
        prompt_evidence, mapping = build_prompt_lines(
            [(c["text"], {c["chunk_id"]}) for c in chunks])

    summary = client.generate_json(
        SUMMARY_PROMPT.format(name=evidence["name"], type=evidence["type"],
                              evidence=prompt_evidence),
        required_keys=("overview", "contributions", "capabilities",
                       "why_it_mattered"),
        system=SYSTEM_PROMPT)
    translate_citations(summary["contributions"], mapping, "contributions")
    translate_citations(summary["capabilities"], mapping, "capabilities")
    # supporting_chunk_ids: translate the model's line numbers, or derive
    # mechanically as the union of every bullet's citations.
    cited_locals = collect_ids(summary.get("supporting_chunk_ids", []))
    if cited_locals and cited_locals <= set(mapping):
        summary["supporting_chunk_ids"] = sorted(
            set().union(set(), *(mapping[n] for n in cited_locals)))
    else:
        summary["supporting_chunk_ids"] = sorted(
            collect_ids(summary["contributions"]) | collect_ids(summary["capabilities"]))
    validate_summary(summary, valid_ids)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--artifact", help="summarize a single artifact slug")
    parser.add_argument("--force", action="store_true",
                        help="regenerate even if evidence and model are unchanged")
    args = parser.parse_args()

    client = OllamaClient()
    model = client.select_model()
    print(f"model: {model}")

    done = skipped = failed = 0
    with psycopg.connect(database_url()) as conn:
        conn.execute(SCHEMA)
        conn.commit()

        slugs = [s for (s,) in conn.execute(
            "SELECT slug FROM artifacts WHERE same_as IS NULL ORDER BY slug")]
        if args.artifact:
            if args.artifact not in slugs:
                print(f"error: unknown canonical artifact {args.artifact!r}",
                      file=sys.stderr)
                return 1
            slugs = [args.artifact]

        for slug in slugs:
            evidence = fetch_artifact_evidence(conn, slug)
            digest = evidence_hash(evidence["chunks"])
            existing = conn.execute(
                """SELECT 1 FROM artifact_summaries s JOIN artifacts a
                   ON a.id = s.artifact_id
                   WHERE a.slug = %s AND s.evidence_sha256 = %s AND s.model = %s""",
                (slug, digest, model)).fetchone()
            if existing and not args.force:
                skipped += 1
                print(f"skip      {slug} (summary current)")
                continue

            print(f"summarize {slug} ({len(evidence['chunks'])} chunks)")
            summary = None
            for attempt in (1, 2):
                try:
                    summary = summarize_artifact(client, evidence)
                    break
                except OllamaError as exc:
                    print(f"attempt {attempt} failed for {slug}: {exc}",
                          file=sys.stderr)
            if summary is None:
                failed += 1
                print(f"FAIL      {slug}: giving up after 2 attempts "
                      "(no fallback provider; re-run to retry)", file=sys.stderr)
                continue

            # Save immediately and independently: one artifact per commit.
            conn.execute(
                """
                INSERT INTO artifact_summaries
                    (artifact_id, model, overview, contributions, capabilities,
                     why_it_mattered, supporting_chunk_ids, evidence_sha256)
                SELECT a.id, %s, %s, %s, %s, %s, %s, %s FROM artifacts a
                WHERE a.slug = %s
                ON CONFLICT (artifact_id) DO UPDATE SET
                    model = EXCLUDED.model,
                    overview = EXCLUDED.overview,
                    contributions = EXCLUDED.contributions,
                    capabilities = EXCLUDED.capabilities,
                    why_it_mattered = EXCLUDED.why_it_mattered,
                    supporting_chunk_ids = EXCLUDED.supporting_chunk_ids,
                    evidence_sha256 = EXCLUDED.evidence_sha256,
                    created_at = now()
                """,
                (model, summary["overview"],
                 json.dumps(summary["contributions"], ensure_ascii=False),
                 json.dumps(summary["capabilities"], ensure_ascii=False),
                 summary["why_it_mattered"],
                 sorted(collect_ids(summary["supporting_chunk_ids"])),
                 digest, slug),
            )
            conn.commit()
            done += 1
            print(f"saved     {slug}")

    print(f"\n{done} summarized, {skipped} skipped (current), {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
