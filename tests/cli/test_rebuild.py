"""Tests for rebuild CLI commands."""

import tempfile
from pathlib import Path

from click.testing import CliRunner

import jig
from jig.cli.main import cli


def create_minimal_jig_project(root: Path) -> None:
    """Create minimal JIG project structure for testing."""
    # Create jig directory structure
    (root / "jig" / "specifications").mkdir(parents=True)
    (root / "jig" / "outcomes").mkdir(parents=True)
    (root / "jig" / "bricks").mkdir(parents=True)
    (root / "jig" / "generated").mkdir(parents=True)

    # Create a minimal spec with proper filename format
    (root / "jig" / "specifications" / "S-001_Test_Specification.md").write_text(
        """---
id: S-001
title: Test Specification
type: specification
outcomes: [O-001]
architecture: []
---

# Test Specification
"""
    )

    # Create a minimal outcome with proper filename format
    (root / "jig" / "outcomes" / "O-001_Test_Outcome.md").write_text(
        """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001]
---

# Test Outcome
"""
    )

    # Create bricks.yaml
    (root / "jig" / "bricks.yaml").write_text(
        """bricks:
  - id: B-test
    name: Test Brick
    layer: 1
    units:
      - M-example
"""
    )

    # Create src directory with a simple Python file
    (root / "src").mkdir()
    (root / "src" / "example.py").write_text(
        '''"""Example module."""

import jig


@jig.implements("S-001")
def example_function():
    """Example function."""
    pass
'''
    )

    # Create tests directory with a simple test
    (root / "tests").mkdir()
    (root / "tests" / "test_example.py").write_text(
        '''"""Example tests."""

import jig


@jig.verifies("S-001")
def test_example():
    """Example test."""
    pass
'''
    )


@jig.verifies("S-058")
def test_rebuild_impl():
    """jigy rebuild impl rebuilds implementation graph."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["rebuild", "impl"])

        assert result.exit_code == 0
        assert "impl:" in result.output
        assert (root / "jig" / "generated" / "implementation-graph.ndjson").exists()


@jig.verifies("S-058")
def test_rebuild_intent():
    """jigy rebuild intent rebuilds intent graph."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["rebuild", "intent"])

        assert result.exit_code == 0
        assert "intent:" in result.output
        assert (root / "jig" / "generated" / "intent-graph.ndjson").exists()


@jig.verifies("S-058")
def test_rebuild_verify():
    """jigy rebuild verify rebuilds verification graph."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["rebuild", "verify"])

        assert result.exit_code == 0
        assert "verify:" in result.output
        assert (root / "jig" / "generated" / "verification-graph.ndjson").exists()


@jig.verifies("S-058")
def test_rebuild_all():
    """jigy rebuild (no args) rebuilds all three graphs."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["rebuild"])

        assert result.exit_code == 0
        assert "impl:" in result.output
        assert "verify:" in result.output
        assert "intent:" in result.output
        assert (root / "jig" / "generated" / "implementation-graph.ndjson").exists()
        assert (root / "jig" / "generated" / "verification-graph.ndjson").exists()
        assert (root / "jig" / "generated" / "intent-graph.ndjson").exists()


@jig.verifies("S-058")
def test_rebuild_no_options():
    """Rebuild commands have no options (uses discovery)."""
    runner = CliRunner()

    # Check that --project-root is not accepted
    result = runner.invoke(cli, ["rebuild", "impl", "--project-root", "."])
    assert result.exit_code != 0
    assert "no such option" in result.output.lower() or "error" in result.output.lower()


@jig.verifies("S-058")
def test_rebuild_not_in_project():
    """Rebuild commands fail with clear error when not in JIG project."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # No jig/ directory created

        result = runner.invoke(cli, ["rebuild", "impl"])

        assert result.exit_code != 0
        assert "Not in a JIG project" in result.output or "jig/ directory" in result.output


# ========================================================================
# Output Format Flag Tests for S-093
# ========================================================================


@jig.verifies("S-093")
def test_rebuild_impl_json_flag():
    """jigy rebuild impl -j produces valid JSON output."""
    import json

    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["rebuild", "impl", "-j"])

        assert result.exit_code == 0
        # Output should be valid JSON
        output = json.loads(result.output)
        assert output["status"] == "success"
        assert "graphs" in output
        assert "duration_ms" in output
        # Should have impl graph info
        impl_graph = next((g for g in output["graphs"] if g["name"] == "impl"), None)
        assert impl_graph is not None
        assert "nodes" in impl_graph
        assert "edges" in impl_graph


@jig.verifies("S-093")
def test_rebuild_impl_markdown_flag():
    """jigy rebuild impl -m produces markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["rebuild", "impl", "-m"])

        assert result.exit_code == 0
        # Output should be markdown
        assert "# Rebuild Result" in result.output or "**Status:**" in result.output
        assert "impl" in result.output.lower()


@jig.verifies("S-093")
def test_rebuild_all_json_flag():
    """jigy rebuild -j produces valid JSON with all three graphs."""
    import json

    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["rebuild", "-j"])

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["status"] == "success"
        assert "graphs" in output
        # Should have all three graphs
        graph_names = [g["name"] for g in output["graphs"]]
        assert "impl" in graph_names
        assert "intent" in graph_names
        assert "verify" in graph_names


@jig.verifies("S-093")
def test_rebuild_all_markdown_flag():
    """jigy rebuild -m produces markdown with all three graphs."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["rebuild", "-m"])

        assert result.exit_code == 0
        # Output should be markdown with all graphs
        assert "# Rebuild Result" in result.output or "**Status:**" in result.output
        # Should mention all graphs
        output_lower = result.output.lower()
        assert "impl" in output_lower
        assert "intent" in output_lower
        assert "verify" in output_lower


@jig.verifies("S-093")
def test_rebuild_json_markdown_mutually_exclusive():
    """jigy rebuild -j -m should error (mutually exclusive)."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["rebuild", "-j", "-m"])

        assert result.exit_code != 0
        assert "mutually exclusive" in result.output.lower()


@jig.verifies("S-093")
def test_rebuild_intent_json_flag():
    """jigy rebuild intent -j produces valid JSON output."""
    import json

    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["rebuild", "intent", "-j"])

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["status"] == "success"
        intent_graph = next((g for g in output["graphs"] if g["name"] == "intent"), None)
        assert intent_graph is not None


@jig.verifies("S-093")
def test_rebuild_verify_json_flag():
    """jigy rebuild verify -j produces valid JSON output."""
    import json

    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["rebuild", "verify", "-j"])

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["status"] == "success"
        verify_graph = next((g for g in output["graphs"] if g["name"] == "verify"), None)
        assert verify_graph is not None


@jig.verifies("S-093")
def test_rebuild_verbose_flag():
    """jigy rebuild -v produces verbose output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["rebuild", "-v"])

        assert result.exit_code == 0
        # Verbose should still work (additional detail)
        assert "impl:" in result.output or "impl" in result.output.lower()


@jig.verifies("S-093")
def test_rebuild_json_verbose_flag():
    """jigy rebuild -j -v produces verbose JSON output."""
    import json

    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["rebuild", "-j", "-v"])

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["status"] == "success"
        # Verbose JSON might have additional fields
        assert "graphs" in output
