"""
Tests for layers CLI commands (S-040).
"""

import json
import tempfile
from pathlib import Path

from click.testing import CliRunner

import jig
from jig.cli.main import cli


@jig.verifies("S-040")
def test_layers_basic_output():
    """jigy layers shows bricks grouped by layer."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.func1", "type": "function"}) + "\n"
            + json.dumps({"id": "F-core.func2", "type": "function"}) + "\n"
            + json.dumps({"id": "F-api.handler", "type": "function"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-api.handler", "target": "F-core.func1"}) + "\n"
        )

        # Create bricks
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-core
  name: Core
  layer: 0
  units:
    - F-core.func1
    - F-core.func2

- id: B-api
  name: API
  layer: 1
  units:
    - F-api.handler
"""
        )

        result = runner.invoke(cli, ["layers", "--project-root", "."])
        assert result.exit_code == 0

        # Check for layer headers
        assert "Layer 0" in result.output or "layer 0" in result.output.lower()
        assert "Layer 1" in result.output or "layer 1" in result.output.lower()

        # Check for brick names
        assert "B-core" in result.output
        assert "B-api" in result.output
        assert "Core" in result.output
        assert "API" in result.output


@jig.verifies("S-040")
def test_layers_shows_function_counts():
    """jigy layers shows function counts for each brick."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph with multiple functions
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.func1", "type": "function"}) + "\n"
            + json.dumps({"id": "F-core.func2", "type": "function"}) + "\n"
            + json.dumps({"id": "F-core.func3", "type": "function"}) + "\n"
        )

        # Create bricks
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-core
  name: Core
  layer: 0
  units:
    - F-core.func1
    - F-core.func2
    - F-core.func3
"""
        )

        result = runner.invoke(cli, ["layers", "--project-root", "."])
        assert result.exit_code == 0

        # Should show function count (3 functions)
        assert "3" in result.output or "3 functions" in result.output.lower()


@jig.verifies("S-040")
def test_layers_shows_dependencies():
    """jigy layers shows brick dependencies."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph with dependencies
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.utils", "type": "function"}) + "\n"
            + json.dumps({"id": "F-api.handler", "type": "function"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-api.handler", "target": "F-core.utils"}) + "\n"
        )

        # Create bricks
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-core
  name: Core
  layer: 0
  units:
    - F-core.utils

- id: B-api
  name: API
  layer: 1
  units:
    - F-api.handler
"""
        )

        result = runner.invoke(cli, ["layers", "--project-root", "."])
        assert result.exit_code == 0

        # Should show dependency from B-api to B-core
        # Look for patterns like "depends on: B-core" or "→ B-core"
        assert "B-core" in result.output
        assert ("depends" in result.output.lower() or "→" in result.output or "↓" in result.output)


@jig.verifies("S-040")
def test_layers_summary_option():
    """jigy layers --summary shows counts only."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.func1", "type": "function"}) + "\n"
            + json.dumps({"id": "F-core.func2", "type": "function"}) + "\n"
            + json.dumps({"id": "F-api.handler", "type": "function"}) + "\n"
        )

        # Create bricks
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-core
  name: Core
  layer: 0
  units:
    - F-core.func1
    - F-core.func2

- id: B-api
  name: API
  layer: 1
  units:
    - F-api.handler
"""
        )

        result = runner.invoke(cli, ["layers", "--summary", "--project-root", "."])
        assert result.exit_code == 0

        # Summary should show layer counts
        assert "Layer 0" in result.output or "layer 0" in result.output.lower()
        assert "Layer 1" in result.output or "layer 1" in result.output.lower()

        # Should show counts
        assert "2" in result.output  # 2 bricks total or 2 functions in layer 0


@jig.verifies("S-040")
def test_layers_total_summary():
    """jigy layers shows total summary at bottom."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.func1", "type": "function"}) + "\n"
            + json.dumps({"id": "F-api.handler", "type": "function"}) + "\n"
        )

        # Create bricks
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-core
  name: Core
  layer: 0
  units:
    - F-core.func1

- id: B-api
  name: API
  layer: 1
  units:
    - F-api.handler
"""
        )

        result = runner.invoke(cli, ["layers", "--project-root", "."])
        assert result.exit_code == 0

        # Should show total summary
        assert "Total" in result.output or "total" in result.output.lower()
        assert "2" in result.output  # 2 bricks or 2 functions


@jig.verifies("S-040")
def test_layers_dag_status():
    """jigy layers indicates DAG status."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph with no cycles (DAG)
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.func1", "type": "function"}) + "\n"
            + json.dumps({"id": "F-api.handler", "type": "function"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-api.handler", "target": "F-core.func1"}) + "\n"
        )

        # Create bricks
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-core
  name: Core
  layer: 0
  units:
    - F-core.func1

- id: B-api
  name: API
  layer: 1
  units:
    - F-api.handler
"""
        )

        result = runner.invoke(cli, ["layers", "--project-root", "."])
        assert result.exit_code == 0

        # Should indicate DAG status
        # Looking for "DAG" or "no cycles" or similar
        output_lower = result.output.lower()
        assert "dag" in output_lower or "cycle" in output_lower


@jig.verifies("S-040")
def test_layers_missing_graph():
    """jigy layers errors gracefully if implementation graph missing."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create bricks but no graph
        Path("jig").mkdir()
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-core
  name: Core
  layer: 0
  units:
    - F-core.func1
"""
        )

        result = runner.invoke(cli, ["layers", "--project-root", "."])
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "missing" in result.output.lower()


@jig.verifies("S-040")
def test_layers_empty_layers():
    """jigy layers handles bricks at single layer."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.func1", "type": "function"}) + "\n"
            + json.dumps({"id": "F-core.func2", "type": "function"}) + "\n"
        )

        # Create bricks all at layer 0
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-core-a
  name: Core A
  layer: 0
  units:
    - F-core.func1

- id: B-core-b
  name: Core B
  layer: 0
  units:
    - F-core.func2
"""
        )

        result = runner.invoke(cli, ["layers", "--project-root", "."])
        assert result.exit_code == 0

        # Should show Layer 0 with both bricks
        assert "Layer 0" in result.output or "layer 0" in result.output.lower()
        assert "B-core-a" in result.output
        assert "B-core-b" in result.output


@jig.verifies("S-040")
def test_layers_multiple_layers():
    """jigy layers handles multiple layers correctly."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-l0.func", "type": "function"}) + "\n"
            + json.dumps({"id": "F-l1.func", "type": "function"}) + "\n"
            + json.dumps({"id": "F-l2.func", "type": "function"}) + "\n"
        )

        # Create bricks at layers 0, 1, 2
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-layer0
  name: Layer 0
  layer: 0
  units:
    - F-l0.func

- id: B-layer1
  name: Layer 1
  layer: 1
  units:
    - F-l1.func

- id: B-layer2
  name: Layer 2
  layer: 2
  units:
    - F-l2.func
"""
        )

        result = runner.invoke(cli, ["layers", "--project-root", "."])
        assert result.exit_code == 0

        # Should show all three layers
        assert "Layer 0" in result.output or "layer 0" in result.output.lower()
        assert "Layer 1" in result.output or "layer 1" in result.output.lower()
        assert "Layer 2" in result.output or "layer 2" in result.output.lower()

        # Should show 3 layers in total
        assert "3 layers" in result.output.lower() or "3 layer" in result.output.lower()
