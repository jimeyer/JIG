"""Tests for align CLI command."""

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
title: Test Specification
---

# Test Specification
"""
    )

    # Create a minimal outcome
    (root / "jig" / "outcomes" / "O-001.md").write_text(
        """---
id: O-001
type: outcome
title: Test Outcome
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


@jig.verifies("S-059")
def test_align_success():
    """jigy align runs full workflow and returns success."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["align"])

        assert result.exit_code == 0
        assert "Rebuilding graphs..." in result.output
        assert "impl:" in result.output
        assert "verify:" in result.output
        assert "intent:" in result.output
        assert "Validating..." in result.output
        assert "Summary:" in result.output
        assert "ALIGNED" in result.output


@jig.verifies("S-059")
def test_align_creates_all_graphs():
    """jigy align creates all three graph files."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["align"])

        assert result.exit_code == 0
        assert (root / "jig" / "generated" / "implementation-graph.ndjson").exists()
        assert (root / "jig" / "generated" / "verification-graph.ndjson").exists()
        assert (root / "jig" / "generated" / "intent-graph.ndjson").exists()


@jig.verifies("S-059")
def test_align_output_format():
    """jigy align output matches expected format per A002."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["align"])

        assert result.exit_code == 0
        # Check for expected output format
        lines = result.output.strip().split("\n")
        assert any("Rebuilding graphs..." in line for line in lines)
        assert any("impl:" in line for line in lines)
        assert any("verify:" in line for line in lines)
        assert any("intent:" in line for line in lines)
        assert any("Validating..." in line for line in lines)
        assert any("intent: OK" in line for line in lines)
        assert any("bricks: OK" in line for line in lines)
        assert any("Summary:" in line for line in lines)
        assert any("Specs:" in line for line in lines)
        assert any("Status: ALIGNED" in line for line in lines)


@jig.verifies("S-059")
def test_align_validation_failure_stops():
    """jigy align returns non-zero on validation failure."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        # Create invalid spec (missing id)
        (root / "jig" / "specifications" / "S-002.md").write_text(
            """---
type: specification
---

# Invalid Spec (no id)
"""
        )

        result = runner.invoke(cli, ["align"])

        # Should fail during validation
        assert result.exit_code != 0


@jig.verifies("S-059")
def test_align_not_in_project():
    """jigy align fails with clear error when not in JIG project."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # No jig/ directory created

        result = runner.invoke(cli, ["align"])

        assert result.exit_code != 0
        assert "Not in a JIG project" in result.output or "jig/ directory" in result.output
