"""Tests for the deterministic alias-matching logic in assign_artifacts.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import pytest  # noqa: E402

from assign_artifacts import alias_pattern, fold, strip_emphasis  # noqa: E402
import assign_artifacts  # noqa: E402


def matches(alias: str, text: str) -> bool:
    """Replicate the script's mention-matching for one alias against one text."""
    pattern, case_sensitive = alias_pattern(alias)
    hay = strip_emphasis(text) if case_sensitive else fold(text)
    return pattern.search(hay) is not None


class TestFold:
    def test_lowercases_and_folds_curly_quotes(self):
        assert fold("Master’s of Science") == "master's of science"

    def test_strips_bold_markers(self):
        assert fold("__Wellington Management__") == " wellington management "
        assert fold("**KOS** design") == " kos  design"


class TestAliasMatching:
    def test_plain_word_boundary_match(self):
        assert matches("Wellington", "joined Wellington Management in Boston")

    def test_case_insensitive_by_default(self):
        assert matches("JobPilot", "the jobpilot pipeline")

    def test_bold_wrapped_alias_matches(self):
        # Regression: mammoth bold markers must not defeat word boundaries.
        assert matches("Wellington", "__Wellington Management Company, LLP, Boston, MA__")
        assert matches("OneWorld", "__OneWorld (EasyA HackBoston) __Sep 2022")
        assert matches("Stock Market Simulation", "__Stock Market Simulation (WPI) __Jan 2022")

    def test_snake_case_identifiers_do_not_match(self):
        assert not matches("Wellington", '"wellington_oracle_python_platform",')

    def test_compound_tokens_do_not_match(self):
        assert not matches("OneWorld", "each token (OneWorldToken, OWT)")
        assert not matches("JobPilot", "jobpilotV2 will be called careerpilot")

    def test_short_acronyms_are_case_sensitive(self):
        assert matches("KOS", "the KOS ingestion layer")
        assert not matches("KOS", "kos ingestion")
        assert not matches("KOS", "kiosks")

    def test_long_aliases_ignore_case(self):
        assert matches("MassDEP", "massdep staff upload documents")

    def test_dotted_alias(self):
        assert matches("Cooper.ai", "Cooper.ai — Data Engineer (Contract)")
        assert not matches("Cooper.ai", "cooperative aid")

    def test_alias_with_trailing_paren(self):
        assert matches("Data Science (BS)", "Programs of Study: Data Science (BS)")


def make_registry(tmp_path, monkeypatch, yaml_text: str):
    registry = tmp_path / "registry.yaml"
    registry.write_text(yaml_text, encoding="utf-8")
    monkeypatch.setattr(assign_artifacts, "REGISTRY_PATH", registry)
    return assign_artifacts.load_registry()


BASE = """
artifacts:
  - {{slug: canonical, name: Canonical, type: project, aliases: [Canon],
     documents: ["doc-a.md"], grounded_in: x{extra_canonical}}}
  - {{slug: dupe, name: Dupe, type: project, aliases: [Dupe],
     documents: ["doc-b.md"], grounded_in: x{extra_dupe}}}
"""


class TestSameAsResolution:
    def test_same_as_folds_aliases_and_documents(self, tmp_path, monkeypatch):
        entries = make_registry(tmp_path, monkeypatch,
                                BASE.format(extra_canonical="", extra_dupe=", same_as: canonical"))
        canonical = next(e for e in entries if e["slug"] == "canonical")
        assert canonical["aliases"] == ["Canon", "Dupe"]
        assert canonical["documents"] == ["doc-a.md", "doc-b.md"]
        dupe = next(e for e in entries if e["slug"] == "dupe")
        assert dupe["same_as"] == "canonical"  # entry kept on record

    def test_same_as_unknown_target_rejected(self, tmp_path, monkeypatch):
        with pytest.raises(SystemExit):
            make_registry(tmp_path, monkeypatch,
                          BASE.format(extra_canonical="", extra_dupe=", same_as: nope"))

    def test_same_as_chain_rejected(self, tmp_path, monkeypatch):
        with pytest.raises(SystemExit):
            make_registry(tmp_path, monkeypatch,
                          BASE.format(extra_canonical=", same_as: dupe",
                                      extra_dupe=", same_as: canonical"))

    def test_duplicate_alias_across_canonicals_rejected(self, tmp_path, monkeypatch):
        with pytest.raises(SystemExit):
            make_registry(tmp_path, monkeypatch, """
artifacts:
  - {slug: one, name: One, type: project, aliases: [Shared], grounded_in: x}
  - {slug: two, name: Two, type: project, aliases: [Shared], grounded_in: x}
""")

    def test_shared_alias_with_same_as_target_allowed(self, tmp_path, monkeypatch):
        entries = make_registry(tmp_path, monkeypatch, """
artifacts:
  - {slug: one, name: One, type: project, aliases: [Shared], grounded_in: x}
  - {slug: two, name: Two, type: project, aliases: [Shared], grounded_in: x,
     same_as: one}
""")
        canonical = next(e for e in entries if e["slug"] == "one")
        assert canonical["aliases"] == ["Shared"]  # no duplicate added
