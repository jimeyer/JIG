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

    # Create a minimal spec
    (root / "jig" / "specifications" / "S-001.md").write_text(
        """---
id: S-001
type: specification
---

# Test Specification
"""
    )

    # Create a minimal outcome
    (root / "jig" / "outcomes" / "O-001.md").write_text(
        """---
id: O-001
type: outcome
specifies: [S-001]
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
    paths:
      - src/
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
