# ABOUTME: Tests for jig.query.search module — text search across JIG documents.
# ABOUTME: Verifies search_docs returns matching docs with id, title, path, match fields.

"""Tests for query.search module.

Tests search_docs() for case-insensitive substring search across
specifications, outcomes, architecture, and charter documents.
"""

from dataclasses import dataclass
from pathlib import Path

import pytest

import jig
from jig.query.search import search_docs


@dataclass
class _FakePaths:
    """Minimal PathsConfig stand-in for tests."""

    specifications: Path
    outcomes: Path
    architecture: Path
    charter: Path


@dataclass
class _FakeConfig:
    """Minimal JigConfig stand-in for tests."""

    paths: _FakePaths
    project_root: Path
    config_file_path: Path | None = None
    has_config_file: bool = False


def _make_config(tmp_path: Path) -> _FakeConfig:
    """Create a fake config rooted in tmp_path with standard subdirs."""
    specs_dir = tmp_path / "jig" / "specifications"
    outcomes_dir = tmp_path / "jig" / "outcomes"
    arch_dir = tmp_path / "jig" / "architecture"
    charter_path = tmp_path / "jig" / "Charter.md"

    specs_dir.mkdir(parents=True)
    outcomes_dir.mkdir(parents=True)
    arch_dir.mkdir(parents=True)

    return _FakeConfig(
        paths=_FakePaths(
            specifications=specs_dir,
            outcomes=outcomes_dir,
            architecture=arch_dir,
            charter=charter_path,
        ),
        project_root=tmp_path,
    )


def _write_spec(specs_dir: Path, spec_id: str, title: str, body: str = "") -> None:
    """Write a spec markdown file with frontmatter."""
    content = f"---\nid: {spec_id}\ntitle: {title}\n---\n# {title}\n\n{body}\n"
    filename = f"{spec_id}_{title.replace(' ', '_')}.md"
    (specs_dir / filename).write_text(content)


@jig.verifies("S-116")
class TestSearchDocsEmpty:
    """Empty/no-match searches return empty list."""

    def test_empty_query_returns_empty(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        assert search_docs("", config) == []

    def test_nonexistent_query_returns_empty(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        _write_spec(config.paths.specifications, "S-001", "Some Spec", "body content")
        assert search_docs("nonexistent_xyzzy", config) == []


@jig.verifies("S-116")
class TestSearchDocsMatching:
    """Matching queries return results with expected fields."""

    def test_match_returns_id_title_path_match(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        _write_spec(config.paths.specifications, "S-042", "Widget Validation", "Validates widgets correctly")

        results = search_docs("widget", config)

        assert len(results) == 1
        r = results[0]
        assert r["id"] == "S-042"
        assert r["title"] == "Widget Validation"
        assert "path" in r
        assert "match" in r

    def test_match_in_body_content(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        _write_spec(config.paths.specifications, "S-010", "Alpha", "The frobnicator is essential")

        results = search_docs("frobnicator", config)
        assert len(results) == 1
        assert results[0]["id"] == "S-010"

    def test_searches_outcomes(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        content = "---\nid: O-001\ntitle: Business Value\n---\n# Business Value\n\nDeliver value\n"
        (config.paths.outcomes / "O-001_Business_Value.md").write_text(content)

        results = search_docs("value", config)
        assert len(results) >= 1
        assert any(r["id"] == "O-001" for r in results)

    def test_searches_architecture(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        content = "---\nid: A-001\ntitle: System Arch\n---\n# System Arch\n\nMicroservices pattern\n"
        (config.paths.architecture / "A-001_System_Arch.md").write_text(content)

        results = search_docs("microservices", config)
        assert len(results) == 1
        assert results[0]["id"] == "A-001"

    def test_searches_charter(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        charter_content = "---\nid: Charter\ntitle: Project Charter\n---\n# My Project\n\nAlignment tracking\n"
        config.paths.charter.write_text(charter_content)

        results = search_docs("alignment", config)
        assert len(results) == 1


@jig.verifies("S-116")
class TestSearchDocsLimit:
    """Limit parameter caps result count."""

    def test_respects_limit(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        # Create 5 specs all containing "common"
        for i in range(5):
            _write_spec(config.paths.specifications, f"S-{i:03d}", f"Spec {i}", "common keyword here")

        results = search_docs("common", config, limit=2)
        assert len(results) == 2


@jig.verifies("S-116")
class TestSearchDocsCaseInsensitive:
    """Search is case-insensitive."""

    def test_case_insensitive_match(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        _write_spec(config.paths.specifications, "S-050", "Uppercase Test", "IMPORTANT feature")

        results = search_docs("important", config)
        assert len(results) == 1

    def test_case_insensitive_query(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        _write_spec(config.paths.specifications, "S-051", "Lower Test", "small detail")

        results = search_docs("SMALL", config)
        assert len(results) == 1
