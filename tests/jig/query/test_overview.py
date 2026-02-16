# ABOUTME: Tests for jig.query.overview module — project overview building and formatting.
# ABOUTME: Verifies build_overview returns structured data and formatters produce valid output.

"""Tests for query.overview module.

Tests build_overview() data structure and format_overview_* output functions.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

import jig
from jig.query.overview import (
    build_overview,
    format_overview_human,
    format_overview_json,
    format_overview_markdown,
)


@dataclass
class _FakePaths:
    """Minimal PathsConfig stand-in for tests."""

    specifications: Path
    outcomes: Path
    architecture: Path
    charter: Path
    bricks: Path
    generated: Path


@dataclass
class _FakeConfig:
    """Minimal JigConfig stand-in for tests."""

    paths: _FakePaths
    project_root: Path
    config_file_path: Path | None = None
    has_config_file: bool = False


def _make_config(tmp_path: Path) -> _FakeConfig:
    """Create a config with all dirs created and a basic charter."""
    specs_dir = tmp_path / "jig" / "specifications"
    outcomes_dir = tmp_path / "jig" / "outcomes"
    arch_dir = tmp_path / "jig" / "architecture"
    charter_path = tmp_path / "jig" / "Charter.md"
    bricks_path = tmp_path / "jig" / "bricks.yaml"
    generated_dir = tmp_path / "jig" / "generated"

    specs_dir.mkdir(parents=True)
    outcomes_dir.mkdir(parents=True)
    arch_dir.mkdir(parents=True)
    generated_dir.mkdir(parents=True)

    # Write a basic charter
    charter_path.write_text(
        "---\ngoals:\n  - G-001\n---\n# Test Project\n\n## G-001: Be Great\n"
    )

    # Write a spec
    (specs_dir / "S-001_Test_Spec.md").write_text(
        "---\nid: S-001\ntitle: Test Spec\n---\n# Test Spec\n"
    )

    # Write bricks.yaml
    bricks_path.write_text(
        "bricks:\n  - id: B-core\n    layer: 0\n  - id: B-cli\n    layer: 1\n"
    )

    return _FakeConfig(
        paths=_FakePaths(
            specifications=specs_dir,
            outcomes=outcomes_dir,
            architecture=arch_dir,
            charter=charter_path,
            bricks=bricks_path,
            generated=generated_dir,
        ),
        project_root=tmp_path,
    )


@jig.verifies("S-114")
class TestBuildOverview:
    """build_overview returns a dict with expected top-level keys."""

    def test_returns_expected_keys(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        overview = build_overview(config)

        assert "charter" in overview
        assert "goals" in overview
        assert "specs" in overview
        assert "bricks_by_layer" in overview
        assert "traversal_keys" in overview

    def test_charter_extracted(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        overview = build_overview(config)

        assert overview["charter"] is not None
        assert overview["charter"]["name"] == "Test Project"

    def test_goals_extracted(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        overview = build_overview(config)

        assert len(overview["goals"]) == 1
        assert overview["goals"][0]["id"] == "G-001"

    def test_specs_counted(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        overview = build_overview(config)

        assert overview["specs"]["total"] == 1

    def test_bricks_by_layer(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        overview = build_overview(config)

        assert "0" in overview["bricks_by_layer"]
        assert "B-core" in overview["bricks_by_layer"]["0"]


@jig.verifies("S-114")
class TestFormatOverviewJson:
    """format_overview_json returns valid JSON."""

    def test_returns_valid_json(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        overview = build_overview(config)

        json_str = format_overview_json(overview)
        parsed = json.loads(json_str)

        assert "charter" in parsed
        assert "specs" in parsed

    def test_roundtrip_preserves_data(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        overview = build_overview(config)

        json_str = format_overview_json(overview)
        parsed = json.loads(json_str)

        assert parsed["specs"]["total"] == overview["specs"]["total"]


@jig.verifies("S-114")
class TestFormatOverviewHuman:
    """format_overview_human returns non-empty string."""

    def test_includes_project_name(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        overview = build_overview(config)

        text = format_overview_human(overview)
        assert "Test Project" in text

    def test_includes_specs_count(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        overview = build_overview(config)

        text = format_overview_human(overview)
        assert "1 total" in text


@jig.verifies("S-114")
class TestFormatOverviewMarkdown:
    """format_overview_markdown returns markdown with headers."""

    def test_includes_markdown_headers(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        overview = build_overview(config)

        md = format_overview_markdown(overview)
        assert "# Test Project" in md
        assert "## Specifications" in md
