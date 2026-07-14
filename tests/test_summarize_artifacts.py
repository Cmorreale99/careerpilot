"""Tests for summary validation — unsupported citations must fail."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ollama_client import OllamaError  # noqa: E402
from scripts.summarize_artifacts import (  # noqa: E402
    build_prompt_lines,
    collect_ids,
    evidence_hash,
    translate_citations,
    validate_bullets,
    validate_summary,
)

VALID_IDS = {1, 2, 3}


def summary(**overrides) -> dict:
    base = {
        "overview": "Built a thing.",
        "contributions": [{"text": "Did work.", "chunk_ids": [1, 2]}],
        "capabilities": [{"text": "Python.", "chunk_ids": [3]}],
        "why_it_mattered": "It mattered.",
        "supporting_chunk_ids": [1, 2, 3],
    }
    base.update(overrides)
    return base


class TestCollectIds:
    def test_nested_and_flat(self):
        assert collect_ids([1, [2, 3]]) == {1, 2, 3}
        assert collect_ids({"chunk_ids": [4]}) == {4}
        assert collect_ids("7") == set()      # strings are not IDs
        assert collect_ids(True) == set()     # bools are not IDs


class TestValidateSummary:
    def test_valid_summary_passes(self):
        validate_summary(summary(), VALID_IDS)

    def test_unsupported_citation_fails(self):
        bad = summary(contributions=[{"text": "x", "chunk_ids": [99]}])
        with pytest.raises(OllamaError, match="not in the evidence set"):
            validate_summary(bad, VALID_IDS)

    def test_unsupported_supporting_ids_fail(self):
        with pytest.raises(OllamaError, match="not in the evidence set"):
            validate_summary(summary(supporting_chunk_ids=[1, 99]), VALID_IDS)

    def test_empty_overview_fails(self):
        with pytest.raises(OllamaError, match="overview"):
            validate_summary(summary(overview="  "), VALID_IDS)

    def test_bullet_without_citation_fails(self):
        bad = summary(capabilities=[{"text": "x", "chunk_ids": []}])
        with pytest.raises(OllamaError, match="malformed"):
            validate_summary(bad, VALID_IDS)

    def test_one_empty_section_allowed(self):
        # Thin evidence: the model may honestly return an empty section
        # rather than inventing content.
        validate_summary(summary(contributions=[]), VALID_IDS)
        validate_summary(summary(capabilities=[], why_it_mattered=""), VALID_IDS)

    def test_all_sections_empty_fails(self):
        with pytest.raises(OllamaError, match="no cited contributions"):
            validate_summary(summary(contributions=[], capabilities=[]), VALID_IDS)

    def test_non_string_why_it_mattered_fails(self):
        with pytest.raises(OllamaError, match="must be a string"):
            validate_summary(summary(why_it_mattered=[1]), VALID_IDS)


class TestValidateBullets:
    def test_non_list_fails(self):
        with pytest.raises(OllamaError):
            validate_bullets("nope", VALID_IDS, "notes")


class TestPromptLineTranslation:
    def test_lines_numbered_gaplessly(self):
        prompt, mapping = build_prompt_lines([("a", {21197}), ("b", {21203})])
        assert prompt == "[1] a\n[2] b"
        assert mapping == {1: {21197}, 2: {21203}}

    def test_translate_expands_to_chunk_ids(self):
        _, mapping = build_prompt_lines([("a", {10}), ("b", {20, 21})])
        bullets = [{"text": "x", "chunk_ids": [1, 2]}]
        translate_citations(bullets, mapping, "notes")
        assert bullets[0]["chunk_ids"] == [10, 20, 21]

    def test_unknown_line_number_fails(self):
        # Regression: the model interpolated gap IDs (e.g. dedup-excluded
        # chunks); with local numbering any out-of-range citation fails.
        _, mapping = build_prompt_lines([("a", {10})])
        with pytest.raises(OllamaError, match="not in the prompt"):
            translate_citations([{"text": "x", "chunk_ids": [7]}], mapping, "notes")

    def test_non_dict_bullet_fails(self):
        _, mapping = build_prompt_lines([("a", {10})])
        with pytest.raises(OllamaError, match="malformed"):
            translate_citations(["nope"], mapping, "notes")


class TestEvidenceHash:
    def test_deterministic_and_content_sensitive(self):
        chunks = [{"chunk_id": 1, "text": "a"}, {"chunk_id": 2, "text": "b"}]
        assert evidence_hash(chunks) == evidence_hash(chunks)
        changed = [{"chunk_id": 1, "text": "a"}, {"chunk_id": 2, "text": "c"}]
        assert evidence_hash(chunks) != evidence_hash(changed)
