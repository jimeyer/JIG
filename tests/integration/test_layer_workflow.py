"""
Integration tests for layer validation workflow.

Tests the full workflow: validation → layers → suggest → apply
"""

import json
import shutil
import tempfile
from pathlib import Path

from click.testing import CliRunner

import jig
from jig.cli.main import cli


def test_full_layer_workflow_from_invalid_to_valid():
    """
    Integration test: Start with invalid bricks, fix them, validate, visualize, suggest.

    Workflow:
    1. Create bricks with old format (B-001) and no layer field
    2. Run validation → should fail
    3. Fix brick IDs to kebab-case and add layers
    4. Run validation → should pass
    5. Run `jigy layers` → should visualize
    6. Run `jigy layers suggest` → should suggest (and match)
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Setup: Create implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.utils.helper", "type": "function"}) + "\n"
            + json.dumps({"id": "F-api.handler.process", "type": "function"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-api.handler.process", "target": "F-core.utils.helper"}) + "\n"
        )

        # Step 1: Create bricks with OLD format (should fail validation)
        bricks_file = Path("jig") / "bricks.yaml"
        bricks_file.write_text(
            """- id: B-001
  name: Core Utils
  units:
    - F-core.utils.helper

- id: B-002
  name: API Handler
  units:
    - F-api.handler.process
"""
        )

        # Step 2: Run validation (should fail due to old format + missing layers)
        result = runner.invoke(cli, ["validate", "bricks", "--project-root", "."])
        assert result.exit_code != 0
        assert "B-001" in result.output or "invalid" in result.output.lower()

        # Step 3: Fix brick IDs to kebab-case and add layers
        bricks_file.write_text(
            """- id: B-core-utils
  name: Core Utils
  layer: 0
  units:
    - F-core.utils.helper

- id: B-api-handler
  name: API Handler
  layer: 1
  units:
    - F-api.handler.process
"""
        )

        # Step 4: Run validation again (should pass now)
        result = runner.invoke(cli, ["validate", "bricks", "--project-root", "."])
        assert result.exit_code == 0
        assert "passed" in result.output.lower() or "✓" in result.output

        # Step 5: Run `jigy layers` to visualize
        result = runner.invoke(cli, ["layers", "--project-root", "."])
        assert result.exit_code == 0
        assert "Layer 0" in result.output or "layer 0" in result.output.lower()
        assert "Layer 1" in result.output or "layer 1" in result.output.lower()
        assert "B-core-utils" in result.output
        assert "B-api-handler" in result.output

        # Step 6: Run `jigy layers suggest` (should show everything matches)
        result = runner.invoke(cli, ["layers", "suggest", "--project-root", "."])
        assert result.exit_code == 0
        assert "MATCHES" in result.output or "match" in result.output.lower()


def test_layer_violation_detection_and_suggestion():
    """
    Integration test: Create a layer violation and use suggest to fix it.

    Workflow:
    1. Create bricks with wrong layer assignments
    2. Run validation → should detect layer violation
    3. Run `jigy layers suggest` → should suggest corrections
    4. Apply suggestions
    5. Run validation → should pass
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Setup: Create implementation graph with B-api depending on B-core
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.utils", "type": "function"}) + "\n"
            + json.dumps({"id": "F-api.handler", "type": "function"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-api.handler", "target": "F-core.utils"}) + "\n"
        )

        # Step 1: Create bricks with WRONG layer assignments (violation)
        bricks_file = Path("jig") / "bricks.yaml"
        bricks_file.write_text(
            """- id: B-core
  name: Core
  layer: 2
  units:
    - F-core.utils

- id: B-api
  name: API
  layer: 1
  units:
    - F-api.handler
"""
        )

        # Step 2: Run validation (should detect upward dependency violation)
        result = runner.invoke(cli, ["validate", "bricks", "--project-root", "."])
        assert result.exit_code != 0
        # Should show layer constraint violation (B-api at layer 1 depends on B-core at layer 2)

        # Step 3: Run suggest (should show mismatches)
        result = runner.invoke(cli, ["layers", "suggest", "--project-root", "."])
        assert result.exit_code == 0
        assert "MISMATCH" in result.output or "mismatch" in result.output.lower()

        # Step 4: Apply suggestions (auto-confirm with 'y')
        result = runner.invoke(cli, ["layers", "suggest", "--apply", "--project-root", "."], input="y\n")
        assert result.exit_code == 0
        assert "Updated" in result.output or "updated" in result.output.lower()

        # Step 5: Run validation again (should pass now)
        result = runner.invoke(cli, ["validate", "bricks", "--project-root", "."])
        assert result.exit_code == 0
        assert "passed" in result.output.lower() or "✓" in result.output


def test_cycle_detection_across_workflow():
    """
    Integration test: Verify cycle detection works in both validation and suggestion.

    Workflow:
    1. Create bricks with circular dependencies
    2. Run validation → should detect cycles
    3. Run `jigy layers suggest` → should report error (can't suggest with cycles)
    4. Run `jigy layers` → should show cycle warning
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Setup: Create implementation graph with cycle
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-a.func", "type": "function"}) + "\n"
            + json.dumps({"id": "F-b.func", "type": "function"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-a.func", "target": "F-b.func"}) + "\n"
            + json.dumps({"type": "calls", "source": "F-b.func", "target": "F-a.func"}) + "\n"
        )

        # Create bricks with proper format
        bricks_file = Path("jig") / "bricks.yaml"
        bricks_file.write_text(
            """- id: B-a
  name: Brick A
  layer: 0
  units:
    - F-a.func

- id: B-b
  name: Brick B
  layer: 0
  units:
    - F-b.func
"""
        )

        # Run validation (should detect cycle)
        result = runner.invoke(cli, ["validate", "bricks", "--project-root", "."])
        assert result.exit_code != 0
        assert "cycle" in result.output.lower() or "circular" in result.output.lower()

        # Run suggest (should report error due to cycles)
        result = runner.invoke(cli, ["layers", "suggest", "--project-root", "."])
        assert result.exit_code != 0
        assert "cycle" in result.output.lower() or "circular" in result.output.lower()

        # Run layers visualization (should show cycle warning)
        result = runner.invoke(cli, ["layers", "--project-root", "."])
        assert result.exit_code == 0
        assert "cycle" in result.output.lower() or "⚠" in result.output


def test_summary_mode_integration():
    """
    Integration test: Verify --summary flag works end-to-end.
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Setup
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.func1", "type": "function"}) + "\n"
            + json.dumps({"id": "F-core.func2", "type": "function"}) + "\n"
            + json.dumps({"id": "F-api.func", "type": "function"}) + "\n"
        )

        bricks_file = Path("jig") / "bricks.yaml"
        bricks_file.write_text(
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
    - F-api.func
"""
        )

        # Run with --summary
        result = runner.invoke(cli, ["layers", "--summary", "--project-root", "."])
        assert result.exit_code == 0
        assert "Layer 0" in result.output or "layer 0" in result.output.lower()
        assert "Layer 1" in result.output or "layer 1" in result.output.lower()
        # Summary should show counts
        assert "2" in result.output  # 2 bricks or 2 functions


def test_json_validation_output_integration():
    """
    Integration test: Verify JSON output works across validation commands.
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create valid setup
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-core.func", "type": "function"}) + "\n"
        )

        bricks_file = Path("jig") / "bricks.yaml"
        bricks_file.write_text(
            """- id: B-core
  name: Core
  layer: 0
  units:
    - F-core.func
"""
        )

        # Run validation with --format json
        result = runner.invoke(cli, ["validate", "bricks", "--project-root", ".", "--format", "json"])
        assert result.exit_code == 0

        # Should be valid JSON
        output_json = json.loads(result.output)
        assert "status" in output_json
        assert output_json["status"] == "passed"
