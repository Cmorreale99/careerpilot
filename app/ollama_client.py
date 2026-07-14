"""Ollama integration for CareerPilot v2 — setup and corpus access (v2 step 1).

Wraps the local Ollama server with the exact parameters pinned in
claude.md and gives it read access to the corpus:

  model      qwen3.5:9b-q4_K_M primary, qwen3.5:4b-q8_0 fallback
  endpoint   http://localhost:11434
  context    8,192 tokens
  sampling   temperature 0.1
  output     structured JSON, validated against a required-keys schema

Boundaries, enforced here and by the callers in later v2 steps:
  - the LLM reads evidence only through fetch_artifact_evidence(), which
    serves canonical chunks (post-ingestion, post-dedup, post-assignment)
    with their chunk IDs so summaries can cite them
  - it cannot create artifacts, assign chunks, or modify evidence — this
    module has no write path to the pipeline tables
  - invalid output raises OllamaError; there is no remote/paid fallback
    of any kind (the only fallback is the pinned local fallback model)

Batching is deterministic: chunks are packed in corpus order (document
path, chunk index) into batches that fit the context budget, so the same
corpus state always produces the same batches.

Smoke test (requires the Ollama server and a pinned model):
    python -m app.ollama_client
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

OLLAMA_URL = "http://localhost:11434"
PRIMARY_MODEL = "qwen3.5:9b-q4_K_M"
FALLBACK_MODEL = "qwen3.5:4b-q8_0"
NUM_CTX = 8192
TEMPERATURE = 0.1

# Deterministic char-based token estimate (~4 chars/token, rounded up).
CHARS_PER_TOKEN = 4


class OllamaError(RuntimeError):
    """Raised for any Ollama failure. Never falls back to a paid provider."""


def estimate_tokens(text: str) -> int:
    return max(1, -(-len(text) // CHARS_PER_TOKEN))


@dataclass
class OllamaClient:
    base_url: str = OLLAMA_URL
    primary_model: str = PRIMARY_MODEL
    fallback_model: str = FALLBACK_MODEL
    num_ctx: int = NUM_CTX
    temperature: float = TEMPERATURE
    timeout: int = 600
    model: str = field(default="", init=False)

    def _request(self, path: str, payload: dict | None = None) -> dict:
        url = self.base_url.rstrip("/") + path
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"},
            method="POST" if data else "GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise OllamaError(f"Ollama request to {path} failed: {exc}") from exc

    def available_models(self) -> list[str]:
        return [m["name"] for m in self._request("/api/tags").get("models", [])]

    def select_model(self) -> str:
        """Pick the primary model, or the pinned local fallback; else fail."""
        models = self.available_models()
        for candidate in (self.primary_model, self.fallback_model):
            if candidate in models:
                if candidate != self.primary_model:
                    print(f"note: primary model {self.primary_model} unavailable, "
                          f"using fallback {candidate}", file=sys.stderr)
                self.model = candidate
                return candidate
        raise OllamaError(
            f"neither {self.primary_model} nor {self.fallback_model} is available; "
            f"run: ollama pull {self.primary_model}"
        )

    def generate_json(self, prompt: str, required_keys: tuple[str, ...],
                      system: str | None = None) -> dict:
        """One structured-JSON completion; raises OllamaError on any invalid output."""
        if not self.model:
            self.select_model()
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            # Qwen3.5 is a thinking model; without this it routes the whole
            # completion into the `thinking` field and `response` comes back
            # empty. Structured output requires plain completion.
            "think": False,
            "options": {"temperature": self.temperature, "num_ctx": self.num_ctx},
        }
        if system:
            payload["system"] = system
        response = self._request("/api/generate", payload)
        raw = response.get("response", "")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise OllamaError(f"model returned invalid JSON: {raw[:200]!r}") from exc
        if not isinstance(parsed, dict):
            raise OllamaError(f"model returned non-object JSON: {raw[:200]!r}")
        missing = [k for k in required_keys if k not in parsed]
        if missing:
            raise OllamaError(f"model output missing required keys {missing}")
        return parsed


# ---------------------------------------------------------------- corpus access

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
    raise OllamaError("DATABASE_URL not set and not found in .env")


def fetch_artifact_evidence(conn, slug: str) -> dict:
    """Read one artifact and its canonical evidence chunks (with IDs).

    Read-only corpus access for the summarizer: canonical artifacts,
    canonical chunks only, ordered deterministically. Each line carries
    its chunk ID so generated summaries can cite (and be validated
    against) the exact evidence they used.
    """
    row = conn.execute(
        "SELECT id, slug, name, artifact_type, grounded_in FROM artifacts "
        "WHERE slug = %s AND same_as IS NULL", (slug,)
    ).fetchone()
    if row is None:
        raise OllamaError(f"unknown or non-canonical artifact: {slug}")
    artifact_id, slug, name, artifact_type, grounded_in = row

    chunks = conn.execute(
        """
        SELECT c.id, c.text_norm, d.relative_path, c.source_page
        FROM chunk_artifacts ca
        JOIN chunks c ON c.id = ca.chunk_id
        JOIN documents d ON d.id = c.document_id
        WHERE ca.artifact_id = %s AND c.duplicate_of IS NULL
          AND c.chunk_type IN ('sentence', 'list_item', 'table_row')
        ORDER BY d.relative_path, c.chunk_index
        """,
        (artifact_id,),
    ).fetchall()

    return {
        "slug": slug,
        "name": name,
        "type": artifact_type,
        "grounded_in": grounded_in,
        "chunks": [
            {"chunk_id": chunk_id, "text": text, "document": path, "page": page}
            for chunk_id, text, path, page in chunks
        ],
    }


def batch_chunks(chunks: list[dict], budget_tokens: int) -> list[list[dict]]:
    """Pack chunks into deterministic, order-preserving batches.

    Each batch's estimated tokens (text + citation overhead) stay within
    budget_tokens. A single oversized chunk still gets its own batch
    rather than being dropped — evidence is never silently discarded.
    """
    if budget_tokens < 1:
        raise ValueError("budget_tokens must be positive")
    batches: list[list[dict]] = []
    current: list[dict] = []
    current_tokens = 0
    for chunk in chunks:
        tokens = estimate_tokens(chunk["text"]) + 8  # id + separators
        if current and current_tokens + tokens > budget_tokens:
            batches.append(current)
            current, current_tokens = [], 0
        current.append(chunk)
        current_tokens += tokens
    if current:
        batches.append(current)
    return batches


# ------------------------------------------------------------------ smoke test

def main() -> int:
    import psycopg

    client = OllamaClient()
    version = client._request("/api/version")
    print(f"ollama {version.get('version')} at {client.base_url}")
    model = client.select_model()
    print(f"model: {model} (ctx {client.num_ctx}, temperature {client.temperature})")

    with psycopg.connect(database_url()) as conn:
        slugs = [s for (s,) in conn.execute(
            "SELECT slug FROM artifacts WHERE same_as IS NULL ORDER BY slug")]
        print(f"corpus access: {len(slugs)} canonical artifacts visible")
        evidence = fetch_artifact_evidence(conn, "cooper-ai")
    print(f"sample artifact {evidence['slug']}: {len(evidence['chunks'])} chunks")
    batches = batch_chunks(evidence["chunks"], budget_tokens=6000)
    print(f"batching: {len(batches)} batch(es)")

    lines = "\n".join(f"[{c['chunk_id']}] {c['text']}" for c in evidence["chunks"])
    result = client.generate_json(
        "Echo test. Reply with JSON containing exactly two keys: "
        '"artifact" (the artifact name below) and "chunk_ids" (the integer IDs '
        "in brackets below, as a list).\n\n"
        f"Artifact: {evidence['name']}\n{lines}",
        required_keys=("artifact", "chunk_ids"),
    )
    print(f"structured JSON round-trip ok: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
