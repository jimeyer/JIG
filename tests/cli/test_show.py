"""Tests for show CLI commands."""

from pathlib import Path

from click.testing import CliRunner

import jig
from jig.cli.main import cli


def create_minimal_jig_project(root: Path) -> None:
    """Create minimal JIG project structure for testing."""
    # Create jig directory structure
    (root / "jig" / "specifications").mkdir(parents=True)
    (root / "jig" / "outcomes").mkdir(parents=True)
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

    # Create bricks.yaml with two layers
    (root / "jig" / "bricks.yaml").write_text(
        """bricks:
  - id: B-foundation
    name: Foundation Brick
    layer: 0
    units:
      - M-foundation

  - id: B-core
    name: Core Brick
    layer: 1
    units:
      - M-core
"""
    )

    # Create src directory with modules
    (root / "src").mkdir()
    (root / "src" / "foundation.py").write_text(
        '''"""Foundation module."""

def foundation_func():
    pass
'''
    )
    (root / "src" / "core.py").write_text(
        '''"""Core module."""

from foundation import foundation_func

def core_func():
    foundation_func()
'''
    )


@jig.verifies("S-060")
def test_show_overview():
    """jigy show displays bricks + layers overview."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["show"])

        assert result.exit_code == 0
        assert "Bricks:" in result.output
        assert "Layers:" in result.output
        assert "B-foundation" in result.output
        assert "B-core" in result.output


@jig.verifies("S-060")
def test_show_layers():
    """jigy show layers displays layer hierarchy."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["show", "layers"])

        assert result.exit_code == 0
        assert "Layer Hierarchy" in result.output
        assert "Layer 0" in result.output
        assert "Layer 1" in result.output
        assert "Foundation" in result.output or "B-foundation" in result.output


@jig.verifies("S-060")
def test_show_bricks():
    """jigy show bricks displays brick details."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["show", "bricks"])

        assert result.exit_code == 0
        assert "Brick Details" in result.output
        assert "B-foundation" in result.output
        assert "B-core" in result.output
        assert "Name:" in result.output
        assert "Layer:" in result.output
        assert "Units:" in result.output


@jig.verifies("S-060")
def test_show_no_options():
    """Show commands have no options (uses discovery)."""
    runner = CliRunner()

    # Check that --project-root is not accepted
    result = runner.invoke(cli, ["show", "--project-root", "."])
    assert result.exit_code != 0


@jig.verifies("S-060")
def test_show_not_in_project():
    """Show commands fail with clear error when not in JIG project."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # No jig/ directory created

        result = runner.invoke(cli, ["show"])

        assert result.exit_code != 0
        assert "Not in a JIG project" in result.output or "jig/ directory" in result.output


@jig.verifies("S-060")
def test_show_no_bricks_file():
    """Show commands handle missing bricks.yaml gracefully."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        # Create jig dir but no bricks.yaml
        (root / "jig").mkdir()

        result = runner.invoke(cli, ["show"])

        assert result.exit_code == 0
        assert "No bricks.yaml found" in result.output
