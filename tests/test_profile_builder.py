"""Tests for the deterministic profile markdown renderer (no DB needed)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.profile_builder import profile_markdown  # noqa: E402

PROFILE = {
    "subject": "Cam Morreale",
    "pipeline": {"documents": 2, "chunks": 10, "canonical_chunks": 9, "artifacts": 1},
    "resolved_references": [
        {"slug": "greenie", "canonical": "oneworld", "name": "Greenie"},
    ],
    "sections": [
        {"type": "professional_experience", "title": "Professional Experience",
         "artifacts": []},
        {"type": "project", "title": "Projects", "artifacts": [{
            "slug": "demo",
            "name": "Demo Project",
            "grounded_in": "Demo doc title.",
            "evidence_count": 2,
            "source_count": 1,
            "sources": [{
                "document": "2nd brain/demo.md",
                "source_file": "2nd brain/demo.pdf",
                "source_sha256": "abcdef0123456789",
                "lines": [
                    {"text": "Built the demo.", "page": 1, "method": "document", "matched": "x"},
                    {"text": "Shipped the demo.", "page": None, "method": "mention", "matched": "Demo"},
                ],
            }],
        }]},
    ],
}


class TestProfileMarkdown:
    def test_structure_and_content(self):
        md = profile_markdown(PROFILE)
        assert md.startswith("# Cam Morreale — Career Profile")
        assert "## Projects" in md
        assert "### Demo Project" in md
        assert "#### Source: `2nd brain/demo.pdf` (sha256 abcdef012345…)" in md
        assert "- Built the demo. (p. 1)" in md
        assert "- Shipped the demo.\n" in md  # no page tag when page is None

    def test_empty_sections_omitted(self):
        md = profile_markdown(PROFILE)
        assert "## Professional Experience" not in md

    def test_resolved_reference_note(self):
        md = profile_markdown(PROFILE)
        assert "“Greenie” (greenie) resolves to the oneworld artifact" in md

    def test_deterministic(self):
        assert profile_markdown(PROFILE) == profile_markdown(PROFILE)
