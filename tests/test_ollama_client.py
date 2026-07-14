"""Tests for the Ollama integration layer (no server or DB needed)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ollama_client import (  # noqa: E402
    FALLBACK_MODEL,
    NUM_CTX,
    PRIMARY_MODEL,
    TEMPERATURE,
    OllamaClient,
    OllamaError,
    batch_chunks,
    estimate_tokens,
)


def chunk(text: str, chunk_id: int = 1) -> dict:
    return {"chunk_id": chunk_id, "text": text, "document": "d.md", "page": None}


class TestSpecPins:
    def test_parameters_match_claude_md(self):
        assert PRIMARY_MODEL == "qwen3.5:9b-q4_K_M"
        assert FALLBACK_MODEL == "qwen3.5:4b-q8_0"
        assert NUM_CTX == 8192
        assert TEMPERATURE == 0.1
        assert OllamaClient().base_url == "http://localhost:11434"


class TestEstimateTokens:
    def test_rounds_up(self):
        assert estimate_tokens("abcd") == 1
        assert estimate_tokens("abcde") == 2

    def test_empty_is_nonzero(self):
        assert estimate_tokens("") == 1


class TestBatchChunks:
    def test_single_batch_when_under_budget(self):
        chunks = [chunk("x" * 40, i) for i in range(3)]
        assert batch_chunks(chunks, budget_tokens=1000) == [chunks]

    def test_splits_at_budget_preserving_order(self):
        chunks = [chunk("x" * 400, i) for i in range(4)]  # ~108 tokens each
        batches = batch_chunks(chunks, budget_tokens=220)
        assert [len(b) for b in batches] == [2, 2]
        assert [c["chunk_id"] for b in batches for c in b] == [0, 1, 2, 3]

    def test_oversized_chunk_gets_own_batch(self):
        chunks = [chunk("a" * 40, 0), chunk("b" * 9000, 1), chunk("c" * 40, 2)]
        batches = batch_chunks(chunks, budget_tokens=100)
        assert [len(b) for b in batches] == [1, 1, 1]  # nothing dropped

    def test_deterministic(self):
        chunks = [chunk("x" * 100, i) for i in range(10)]
        assert batch_chunks(chunks, 200) == batch_chunks(chunks, 200)

    def test_rejects_nonpositive_budget(self):
        with pytest.raises(ValueError):
            batch_chunks([chunk("x")], 0)


class TestGenerateJsonValidation:
    """generate_json must hard-fail on invalid output (no silent fallback)."""

    def make_client(self, response_text: str) -> OllamaClient:
        client = OllamaClient()
        client.model = PRIMARY_MODEL
        client._request = lambda path, payload=None: {"response": response_text}
        return client

    def test_valid_json_passes(self):
        client = self.make_client('{"summary": "ok", "chunk_ids": [1]}')
        assert client.generate_json("p", ("summary", "chunk_ids")) == {
            "summary": "ok", "chunk_ids": [1]}

    def test_invalid_json_raises(self):
        client = self.make_client("not json at all")
        with pytest.raises(OllamaError, match="invalid JSON"):
            client.generate_json("p", ("summary",))

    def test_non_object_raises(self):
        client = self.make_client('["a", "b"]')
        with pytest.raises(OllamaError, match="non-object"):
            client.generate_json("p", ("summary",))

    def test_missing_keys_raise(self):
        client = self.make_client('{"summary": "ok"}')
        with pytest.raises(OllamaError, match="missing required keys"):
            client.generate_json("p", ("summary", "chunk_ids"))
