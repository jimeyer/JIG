# ABOUTME: Tests for overview module - Project Overview Output (S-114).
# ABOUTME: TDD tests verifying build_overview and format functions.

"""Tests for overview module (S-114).

S-114: Project Overview Output - unified context for agent orientation
"""

import json
from pathlib import Path

import pytest

import jig


@pytest.fixture
def overview_project(tmp_path):
    """Create a sample project for overview testing."""
    # Create directory structure
    jig_dir = tmp_path / "jig"
    jig_dir.mkdir()
    (jig_dir / "specifications").mkdir()
    (jig_dir / "outcomes").mkdir()
    (jig_dir / "architecture").mkdir()
    (jig_dir / "generated").mkdir()

    # Charter
    charter = jig_dir / "Charter_Test.md"
    charter.write_text("""---
id: Charter
type: charter
goals: [G-001, G-002]
---

# Test Project Charter

## G-001: First Goal

Description of first goal.

## G-002: Second Goal

Description of second goal.
""")

    # Specifications
    (jig_dir / "specifications" / "S-001_First_Spec.md").write_text("""---
id: S-001
title: First Spec
type: specification
outcomes: [O-001]
---

# First Spec

Acceptance criteria...
""")
    (jig_dir / "specifications" / "S-002_Second_Spec.md").write_text("""---
id: S-002
title: Second Spec
type: specification
outcomes: [O-001]
---

# Second Spec
""")

    # Outcomes
    (jig_dir / "outcomes" / "O-001_Test_Outcome.md").write_text("""---
id: O-001
title: Test Outcome
type: outcome
goals: [G-001]
specifications: [S-001, S-002]
---

# Test Outcome
""")

    # Architecture
    (jig_dir / "architecture" / "A-001_Test_Arch.md").write_text("""---
id: A-001
title: Test Architecture
type: architecture
goals: [G-001]
specifications: [S-001]
---

# Test Architecture
""")

    # Bricks
    bricks = jig_dir / "bricks.yaml"
    bricks.write_text("""bricks:
  - id: B-core
    name: Core
    layer: 0
    units:
      - M-core.utils

  - id: B-cli
    name: CLI
    layer: 1
    units:
      - M-cli.main
""")

    # Generated graphs
    # Intent graph
    intent_graph = jig_dir / "generated" / "intent-graph.ndjson"
    intent_nodes = [
        {"_meta": {"version": "2.0"}},
        {"id": "Charter", "type": "charter"},
        {"id": "G-001", "type": "goal"},
        {"id": "G-002", "type": "goal"},
        {"id": "O-001", "type": "outcome"},
        {"id": "A-001", "type": "architecture"},
        {"id": "S-001", "type": "specification"},
        {"id": "S-002", "type": "specification"},
    ]
    with intent_graph.open("w") as f:
        for node in intent_nodes:
            f.write(json.dumps(node) + "\n")

    # Impl graph with implements edges
    impl_graph = jig_dir / "generated" / "implementation-graph.ndjson"
    impl_items = [
        {"_meta": {"version": "1.0"}},
        {"id": "F-core.utils.helper", "type": "function"},
        {"source": "F-core.utils.helper", "target": "S-001", "type": "implements"},
    ]
    with impl_graph.open("w") as f:
        for item in impl_items:
            f.write(json.dumps(item) + "\n")

    # Verify graph with verifies edges
    verify_graph = jig_dir / "generated" / "verification-graph.ndjson"
    verify_items = [
        {"_meta": {"version": "1.0"}},
        {"id": "T-test_core.test_helper", "type": "test"},
        {"source": "T-test_core.test_helper", "target": "S-001", "type": "verifies"},
    ]
    with verify_graph.open("w") as f:
        for item in verify_items:
            f.write(json.dumps(item) + "\n")

    # Create jig.toml for config
    jig_toml = tmp_path / "jig.toml"
    jig_toml.write_text("""[jig]
version = "0.1.0"
""")

    return tmp_path


@pytest.fixture
def mock_config(overview_project):
    """Create a mock JigConfig for the overview project."""
    from jig.config.schema import load_config

    return load_config(overview_project)


class TestBuildOverview:
    """Tests for build_overview function (S-114)."""

    @jig.verifies("S-114")
    def test_overview_has_charter_section(self, mock_config):
        """Overview includes charter name and file."""
        from jig.cli.overview import build_overview

        result = build_overview(mock_config)

        assert "charter" in result
        assert result["charter"] is not None
        assert result["charter"]["name"] == "Test Project Charter"

    @jig.verifies("S-114")
    def test_overview_has_goals_section(self, mock_config):
        """Overview includes goals with IDs and titles."""
        from jig.cli.overview import build_overview

        result = build_overview(mock_config)

        assert "goals" in result
        assert len(result["goals"]) == 2
        goal_ids = [g["id"] for g in result["goals"]]
        assert "G-001" in goal_ids
        assert "G-002" in goal_ids

    @jig.verifies("S-114")
    def test_overview_has_architecture_section(self, mock_config):
        """Overview includes architecture documents."""
        from jig.cli.overview import build_overview

        result = build_overview(mock_config)

        assert "architecture" in result
        assert len(result["architecture"]) == 1
        assert result["architecture"][0]["id"] == "A-001"

    @jig.verifies("S-114")
    def test_overview_has_outcomes_section(self, mock_config):
        """Overview includes outcomes with goal references."""
        from jig.cli.overview import build_overview

        result = build_overview(mock_config)

        assert "outcomes" in result
        assert len(result["outcomes"]) == 1
        assert result["outcomes"][0]["id"] == "O-001"
        assert "G-001" in result["outcomes"][0]["goals"]

    @jig.verifies("S-114")
    def test_overview_has_specs_counts(self, mock_config):
        """Overview includes spec total/implemented/verified counts."""
        from jig.cli.overview import build_overview

        result = build_overview(mock_config)

        assert "specs" in result
        assert result["specs"]["total"] == 2
        assert result["specs"]["implemented"] >= 0
        assert result["specs"]["verified"] >= 0

    @jig.verifies("S-114")
    def test_overview_has_bricks_by_layer(self, mock_config):
        """Overview groups bricks by layer number."""
        from jig.cli.overview import build_overview

        result = build_overview(mock_config)

        assert "bricks_by_layer" in result
        assert "0" in result["bricks_by_layer"]
        assert "1" in result["bricks_by_layer"]
        assert "B-core" in result["bricks_by_layer"]["0"]
        assert "B-cli" in result["bricks_by_layer"]["1"]

    @jig.verifies("S-114")
    def test_overview_has_traversal_keys(self, mock_config):
        """Overview includes list of valid traversal identifiers."""
        from jig.cli.overview import build_overview

        result = build_overview(mock_config)

        assert "traversal_keys" in result
        keys = result["traversal_keys"]
        # Should include specs, outcomes, goals, architecture, bricks
        assert "S-001" in keys
        assert "O-001" in keys
        assert "G-001" in keys
        assert "A-001" in keys
        assert "B-core" in keys
        assert "Charter" in keys

    @jig.verifies("S-114")
    def test_overview_towers_none_for_single_tower(self, mock_config):
        """Overview towers is None for single-tower projects."""
        from jig.cli.overview import build_overview

        result = build_overview(mock_config)

        assert "towers" in result
        assert result["towers"] is None


class TestFormatOverview:
    """Tests for overview formatting functions (S-114)."""

    @jig.verifies("S-114")
    def test_format_json_is_valid_json(self, mock_config):
        """JSON format produces valid JSON output."""
        from jig.cli.overview import build_overview, format_overview_json

        overview = build_overview(mock_config)
        output = format_overview_json(overview)

        # Should parse without error
        parsed = json.loads(output)
        assert "charter" in parsed
        assert "goals" in parsed

    @jig.verifies("S-114")
    def test_format_human_includes_key_sections(self, mock_config):
        """Human format includes readable sections."""
        from jig.cli.overview import build_overview, format_overview_human

        overview = build_overview(mock_config)
        output = format_overview_human(overview)

        assert "JIG:" in output
        assert "Goals:" in output
        assert "Bricks by Layer:" in output
        assert "Specs:" in output

    @jig.verifies("S-114")
    def test_format_markdown_has_headers(self, mock_config):
        """Markdown format has proper headers."""
        from jig.cli.overview import build_overview, format_overview_markdown

        overview = build_overview(mock_config)
        output = format_overview_markdown(overview)

        assert "# " in output  # H1 header
        assert "## Goals" in output
        assert "## Specifications" in output


class TestShowOverview:
    """Tests for show_overview entry point (S-114)."""

    @jig.verifies("S-114")
    def test_show_overview_returns_zero(self, mock_config, capsys):
        """show_overview returns 0 on success."""
        from jig.cli.overview import show_overview
        from jig.cli.output import OutputFormat

        result = show_overview(mock_config, OutputFormat.HUMAN, skip_rebuild=True)

        assert result == 0

    @jig.verifies("S-114")
    def test_show_overview_with_note(self, mock_config, capsys):
        """show_overview prepends note when provided."""
        from jig.cli.overview import show_overview
        from jig.cli.output import OutputFormat

        show_overview(
            mock_config,
            OutputFormat.HUMAN,
            skip_rebuild=True,
            note='"S-999" not found in project.',
        )

        captured = capsys.readouterr()
        assert "S-999" in captured.out
        assert "not found" in captured.out
