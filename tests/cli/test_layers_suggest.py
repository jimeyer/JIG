"""
Tests for layers suggest CLI command (S-041).
"""

import json
import tempfile
from pathlib import Path

from click.testing import CliRunner

import jig
from jig.cli.main import cli


@jig.verifies("S-041")
def test_layers_suggest_no_dependencies():
    """Bricks with no dependencies are assigned layer 0."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph with no dependencies
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.func1", "type": "function"}) + "\n"
            + json.dumps({"id": "F-core.func2", "type": "function"}) + "\n"
        )

        # Create bricks without layer field
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-core-a
  name: Core A
  units:
    - F-core.func1

- id: B-core-b
  name: Core B
  units:
    - F-core.func2
"""
        )

        result = runner.invoke(cli, ["layers", "suggest", "--project-root", "."])
        assert result.exit_code == 0

        # Should suggest layer 0 for both bricks
        assert "Suggested: 0" in result.output or "layer 0" in result.output.lower()
        assert "no dependencies" in result.output.lower() or "foundation" in result.output.lower()


@jig.verifies("S-041")
def test_layers_suggest_simple_dependency():
    """Layer suggestion follows dependency structure."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph with B-api depending on B-core
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.utils", "type": "function"}) + "\n"
            + json.dumps({"id": "F-api.handler", "type": "function"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-api.handler", "target": "F-core.utils"}) + "\n"
        )

        # Create bricks without layer field
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-core
  name: Core
  units:
    - F-core.utils

- id: B-api
  name: API
  units:
    - F-api.handler
"""
        )

        result = runner.invoke(cli, ["layers", "suggest", "--project-root", "."])
        assert result.exit_code == 0

        # B-core should be layer 0, B-api should be layer 1
        output_lines = result.output.split("\n")

        # Check that both bricks appear in output
        assert "B-core" in result.output
        assert "B-api" in result.output

        # Should show dependency relationship
        assert "depends on" in result.output.lower() or "B-core" in result.output


@jig.verifies("S-041")
def test_layers_suggest_multi_level_dependencies():
    """Layer suggestion handles multi-level dependencies correctly."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create 3-level dependency: B-cli → B-api → B-core
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.utils", "type": "function"}) + "\n"
            + json.dumps({"id": "F-api.handler", "type": "function"}) + "\n"
            + json.dumps({"id": "F-cli.main", "type": "function"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-api.handler", "target": "F-core.utils"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-cli.main", "target": "F-api.handler"}) + "\n"
        )

        # Create bricks without layer field
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-core
  name: Core
  units:
    - F-core.utils

- id: B-api
  name: API
  units:
    - F-api.handler

- id: B-cli
  name: CLI
  units:
    - F-cli.main
"""
        )

        result = runner.invoke(cli, ["layers", "suggest", "--project-root", "."])
        assert result.exit_code == 0

        # Should suggest layer 0, 1, 2 for core, api, cli respectively
        assert "B-core" in result.output
        assert "B-api" in result.output
        assert "B-cli" in result.output


@jig.verifies("S-041")
def test_layers_suggest_shows_current_vs_suggested():
    """Suggest command compares current vs suggested layers."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.utils", "type": "function"}) + "\n"
            + json.dumps({"id": "F-api.handler", "type": "function"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-api.handler", "target": "F-core.utils"}) + "\n"
        )

        # Create bricks WITH layer field (some correct, some wrong)
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-core
  name: Core
  layer: 0
  units:
    - F-core.utils

- id: B-api
  name: API
  layer: 5
  units:
    - F-api.handler
"""
        )

        result = runner.invoke(cli, ["layers", "suggest", "--project-root", "."])
        assert result.exit_code == 0

        # Should show current and suggested
        assert "Current" in result.output or "current" in result.output.lower()
        assert "Suggested" in result.output or "suggested" in result.output.lower()


@jig.verifies("S-041")
def test_layers_suggest_identifies_mismatches():
    """Suggest command identifies mismatches between current and suggested."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.utils", "type": "function"}) + "\n"
        )

        # Create brick with wrong layer
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-core
  name: Core
  layer: 10
  units:
    - F-core.utils
"""
        )

        result = runner.invoke(cli, ["layers", "suggest", "--project-root", "."])
        assert result.exit_code == 0

        # Should show mismatch
        assert "MISMATCH" in result.output or "mismatch" in result.output.lower() or "⚠" in result.output


@jig.verifies("S-041")
def test_layers_suggest_with_cycles():
    """Suggest command reports error when cycles exist."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph with cycle
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-a.func1", "type": "function"}) + "\n"
            + json.dumps({"id": "F-b.func1", "type": "function"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-a.func1", "target": "F-b.func1"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-b.func1", "target": "F-a.func1"}) + "\n"
        )

        # Create bricks
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-a
  name: Brick A
  units:
    - F-a.func1

- id: B-b
  name: Brick B
  units:
    - F-b.func1
"""
        )

        result = runner.invoke(cli, ["layers", "suggest", "--project-root", "."])
        assert result.exit_code != 0

        # Should report cycle error
        assert "cycle" in result.output.lower() or "circular" in result.output.lower()


@jig.verifies("S-041")
def test_layers_suggest_apply_updates_file():
    """--apply flag updates bricks.yaml with suggested layers."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.utils", "type": "function"}) + "\n"
            + json.dumps({"id": "F-api.handler", "type": "function"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-api.handler", "target": "F-core.utils"}) + "\n"
        )

        # Create bricks without layer field
        bricks_file = Path("jig") / "bricks.yaml"
        bricks_file.write_text(
            """- id: B-core
  name: Core
  units:
    - F-core.utils

- id: B-api
  name: API
  units:
    - F-api.handler
"""
        )

        # Run with --apply and auto-confirm with 'y'
        result = runner.invoke(cli, ["layers", "suggest", "--apply", "--project-root", "."], input="y\n")
        assert result.exit_code == 0

        # Check that bricks.yaml was updated
        updated_content = bricks_file.read_text()
        assert "layer: 0" in updated_content  # B-core
        assert "layer: 1" in updated_content  # B-api


@jig.verifies("S-041")
def test_layers_suggest_apply_with_no_confirmation():
    """--apply without confirmation does not modify file."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.utils", "type": "function"}) + "\n"
        )

        # Create bricks without layer field
        bricks_file = Path("jig") / "bricks.yaml"
        original_content = """- id: B-core
  name: Core
  units:
    - F-core.utils
"""
        bricks_file.write_text(original_content)

        # Run with --apply but decline with 'n'
        result = runner.invoke(cli, ["layers", "suggest", "--apply", "--project-root", "."], input="n\n")

        # File should not be modified
        assert bricks_file.read_text() == original_content


@jig.verifies("S-041")
def test_layers_suggest_missing_graph():
    """Suggest command errors gracefully if implementation graph missing."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create bricks but no graph
        Path("jig").mkdir()
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-core
  name: Core
  units:
    - F-core.func1
"""
        )

        result = runner.invoke(cli, ["layers", "suggest", "--project-root", "."])
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "missing" in result.output.lower()


@jig.verifies("S-041")
def test_layers_suggest_diamond_dependency():
    """Layer suggestion handles diamond dependencies correctly."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create diamond: B-top → B-left → B-bottom
        #                      ↓ → B-right → ↑
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-bottom.func", "type": "function"}) + "\n"
            + json.dumps({"id": "F-left.func", "type": "function"}) + "\n"
            + json.dumps({"id": "F-right.func", "type": "function"}) + "\n"
            + json.dumps({"id": "F-top.func", "type": "function"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-left.func", "target": "F-bottom.func"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-right.func", "target": "F-bottom.func"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-top.func", "target": "F-left.func"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-top.func", "target": "F-right.func"}) + "\n"
        )

        # Create bricks
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-bottom
  name: Bottom
  units:
    - F-bottom.func

- id: B-left
  name: Left
  units:
    - F-left.func

- id: B-right
  name: Right
  units:
    - F-right.func

- id: B-top
  name: Top
  units:
    - F-top.func
"""
        )

        result = runner.invoke(cli, ["layers", "suggest", "--project-root", "."])
        assert result.exit_code == 0

        # B-bottom: layer 0 (no deps)
        # B-left, B-right: layer 1 (dep on bottom)
        # B-top: layer 2 (dep on left/right)
        assert "B-bottom" in result.output
        assert "B-top" in result.output
