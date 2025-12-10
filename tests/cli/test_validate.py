"""
Tests for validate CLI commands.
"""

import json
from pathlib import Path

from click.testing import CliRunner

import jig
from jig.cli.main import cli


@jig.verifies("S-023")
@jig.verifies("S-061")
def test_validate_intent_success():
    """jigy validate intent passes with valid artifacts."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create valid spec
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
type: specification
---

# Test
"""
        )

        result = runner.invoke(cli, ["validate", "intent"])
        assert result.exit_code == 0
        assert "specifications" in result.output.lower()


@jig.verifies("S-023")
@jig.verifies("S-061")
def test_validate_intent_failure():
    """jigy validate intent fails with invalid artifacts."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create invalid spec (missing id)
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)
        (spec_dir / "S-001.md").write_text(
            """---
type: specification
---

# Test
"""
        )

        result = runner.invoke(cli, ["validate", "intent"])
        assert result.exit_code == 1  # Validation failure
        assert "error" in result.output.lower() or "✗" in result.output


@jig.verifies("S-023")
@jig.verifies("S-061")
def test_validate_intent_exit_codes():
    """jigy validate intent uses correct exit codes."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)

        # Success: exit code 0
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
type: specification
---

# Test
"""
        )

        result = runner.invoke(cli, ["validate", "intent"])
        assert result.exit_code == 0


@jig.verifies("S-024")
@jig.verifies("S-061")
def test_validate_bricks_success():
    """jigy validate bricks passes with valid bricks."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "M-test", "type": "module"}) + "\n"
            + json.dumps({"id": "F-test.func", "type": "function"}) + "\n"
        )

        # Create valid bricks
        (Path("jig") / "bricks.yaml").write_text(
            """
- id: B-test
  name: Test
  layer: 0
  units:
    - M-test
"""
        )

        result = runner.invoke(cli, ["validate", "bricks"])
        assert result.exit_code == 0
        assert "brick" in result.output.lower()


@jig.verifies("S-024")
@jig.verifies("S-061")
def test_validate_bricks_missing_graph():
    """jigy validate bricks errors if implementation graph missing."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create bricks but no graph
        Path("jig").mkdir()
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-test
  name: Test
  layer: 0
  units:
    - M-test
"""
        )

        result = runner.invoke(cli, ["validate", "bricks"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "missing" in result.output.lower()


@jig.verifies("S-024")
@jig.verifies("S-061")
def test_validate_bricks_partition_gap():
    """jigy validate bricks detects partition gaps."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph with function
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-test.func", "type": "function"}) + "\n"
        )

        # Create bricks that don't include the function (gap)
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-empty
  name: Empty
  layer: 0
  units: []
"""
        )

        result = runner.invoke(cli, ["validate", "bricks"])
        assert result.exit_code == 1
        assert "gap" in result.output.lower() or "0 bricks" in result.output.lower()


@jig.verifies("S-025")
@jig.verifies("S-061")
def test_validate_full_success():
    """jigy validate runs both intent and brick validation."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create valid spec
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
type: specification
---

# Test
"""
        )

        # Create implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-test.func", "type": "function"}) + "\n"
        )

        # Create valid bricks
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-test
  name: Test
  layer: 0
  units:
    - F-test.func
"""
        )

        result = runner.invoke(cli, ["validate"])
        assert result.exit_code == 0
        # Should run both validations
        assert "intent" in result.output.lower() or "specification" in result.output.lower()
        assert "brick" in result.output.lower()


@jig.verifies("S-025")
@jig.verifies("S-061")
def test_validate_full_skips_bricks_if_no_graph():
    """jigy validate gracefully skips brick validation if no graph."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create valid spec only (no graph)
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
type: specification
---

# Test
"""
        )

        result = runner.invoke(cli, ["validate"])
        # Should succeed (intent validation passes, brick validation skipped)
        assert result.exit_code == 0


@jig.verifies("S-025")
@jig.verifies("S-061")
def test_validate_full_fails_on_intent_error():
    """jigy validate fails if intent validation fails."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create invalid spec
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)
        (spec_dir / "S-001.md").write_text(
            """---
type: specification
---

# Test (missing id)
"""
        )

        result = runner.invoke(cli, ["validate"])
        assert result.exit_code == 1


@jig.verifies("S-061")
def test_validate_no_project_root_option():
    """jigy validate commands reject --project-root option."""
    runner = CliRunner()

    result = runner.invoke(cli, ["validate", "--project-root", "."])
    assert result.exit_code != 0
    assert "no such option" in result.output.lower()

    result = runner.invoke(cli, ["validate", "intent", "--project-root", "."])
    assert result.exit_code != 0
    assert "no such option" in result.output.lower()

    result = runner.invoke(cli, ["validate", "bricks", "--project-root", "."])
    assert result.exit_code != 0
    assert "no such option" in result.output.lower()


@jig.verifies("S-061")
def test_validate_no_format_option():
    """jigy validate commands reject --format option."""
    runner = CliRunner()

    result = runner.invoke(cli, ["validate", "--format", "json"])
    assert result.exit_code != 0
    assert "no such option" in result.output.lower()

    result = runner.invoke(cli, ["validate", "intent", "--format", "json"])
    assert result.exit_code != 0
    assert "no such option" in result.output.lower()


@jig.verifies("S-061")
def test_validate_not_in_project():
    """jigy validate fails with clear error when not in JIG project."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # No jig/ directory

        result = runner.invoke(cli, ["validate"])
        assert result.exit_code != 0
        assert "Not in a JIG project" in result.output or "jig/ directory" in result.output


@jig.verifies("S-061")
def test_validate_human_output_only():
    """jigy validate produces human-readable output."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create valid spec
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
type: specification
---

# Test
"""
        )

        result = runner.invoke(cli, ["validate", "intent"])
        assert result.exit_code == 0

        # Should be human-readable (contains checkmarks and text), not JSON
        assert "✓" in result.output or "Validating" in result.output
        # Should NOT be parseable as JSON
        try:
            json.loads(result.output)
            assert False, "Output should not be JSON"
        except json.JSONDecodeError:
            pass  # Expected
