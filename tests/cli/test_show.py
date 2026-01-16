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


# ============================================================================
# Output Format Flag Tests (S-060, S-093)
# ============================================================================

def create_jig_project_with_charter(root: Path) -> None:
    """Create JIG project with charter and architecture for show tests."""
    create_minimal_jig_project(root)

    # Add Charter.md with goals
    (root / "jig" / "Charter.md").write_text(
        """---
id: Charter
type: charter
goals:
  - G-001
  - G-002
---

# Project Charter

## G-001: Test Goal One

First goal description.

## G-002: Test Goal Two

Second goal description.
"""
    )

    # Add architecture directory with a doc
    (root / "jig" / "architecture").mkdir(parents=True)
    (root / "jig" / "architecture" / "A-001_Test_Architecture.md").write_text(
        """---
id: A-001
title: Test Architecture
type: architecture
goals:
  - G-001
specifications:
  - S-001
---

# Test Architecture

Architecture description.
"""
    )


@jig.verifies("S-060", "S-093")
def test_show_overview_json_flag():
    """jigy show -j produces valid JSON output."""
    import json

    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        # Use --no-rebuild to avoid rebuild output mixing with JSON
        result = runner.invoke(cli, ["--no-rebuild", "show", "-j"])

        assert result.exit_code == 0
        # Output should be valid JSON
        data = json.loads(result.output)
        assert "bricks" in data
        assert "layers" in data


@jig.verifies("S-060", "S-093")
def test_show_overview_markdown_flag():
    """jigy show -m produces markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["show", "-m"])

        assert result.exit_code == 0
        # Markdown should have headers
        assert "#" in result.output


@jig.verifies("S-060", "S-093")
def test_show_overview_verbose_flag():
    """jigy show -v produces verbose output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["show", "-v"])

        assert result.exit_code == 0
        # Verbose output should have more detail (units listed)
        assert "M-foundation" in result.output or "M-core" in result.output


@jig.verifies("S-060", "S-093")
def test_show_layers_json_flag():
    """jigy show layers -j produces valid JSON output."""
    import json

    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        # Use --no-rebuild to avoid rebuild output mixing with JSON
        result = runner.invoke(cli, ["--no-rebuild", "show", "layers", "-j"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "layers" in data
        # Should have layer 0 and layer 1
        layer_numbers = [l["layer"] for l in data["layers"]]
        assert 0 in layer_numbers
        assert 1 in layer_numbers


@jig.verifies("S-060", "S-093")
def test_show_bricks_json_flag():
    """jigy show bricks -j produces valid JSON output."""
    import json

    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        # Use --no-rebuild to avoid rebuild output mixing with JSON
        result = runner.invoke(cli, ["--no-rebuild", "show", "bricks", "-j"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "bricks" in data
        brick_ids = [b["id"] for b in data["bricks"]]
        assert "B-foundation" in brick_ids
        assert "B-core" in brick_ids


@jig.verifies("S-060", "S-093")
def test_show_charter_markdown_flag():
    """jigy show charter -m produces markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_jig_project_with_charter(root)

        result = runner.invoke(cli, ["show", "charter", "-m"])

        assert result.exit_code == 0
        # Should have markdown headers
        assert "# " in result.output or "## " in result.output


@jig.verifies("S-060", "S-093")
def test_show_charter_json_flag():
    """jigy show charter -j produces valid JSON output."""
    import json

    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_jig_project_with_charter(root)

        result = runner.invoke(cli, ["show", "charter", "-j"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "goals" in data


@jig.verifies("S-060", "S-093")
def test_show_goals_markdown_flag():
    """jigy show goals -m produces markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_jig_project_with_charter(root)

        result = runner.invoke(cli, ["show", "goals", "-m"])

        assert result.exit_code == 0
        assert "#" in result.output


@jig.verifies("S-060", "S-093")
def test_show_goals_json_flag():
    """jigy show goals -j produces valid JSON output."""
    import json

    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_jig_project_with_charter(root)

        # Use --no-rebuild to avoid rebuild output mixing with JSON
        result = runner.invoke(cli, ["--no-rebuild", "show", "goals", "-j"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "goals" in data


@jig.verifies("S-060", "S-093")
def test_show_architecture_json_flag():
    """jigy show architecture -j produces valid JSON output."""
    import json

    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_jig_project_with_charter(root)

        result = runner.invoke(cli, ["show", "architecture", "-j"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "documents" in data


@jig.verifies("S-093")
def test_show_mutually_exclusive_flags():
    """jigy show -j -m errors with mutually exclusive message."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["show", "-j", "-m"])

        assert result.exit_code != 0
        assert "mutually exclusive" in result.output.lower()


@jig.verifies("S-093")
def test_show_json_verbose_combination():
    """jigy show -j -v produces verbose JSON output."""
    import json

    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        # Use --no-rebuild to avoid rebuild output mixing with JSON
        result = runner.invoke(cli, ["--no-rebuild", "show", "-j", "-v"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        # Verbose JSON should have additional fields
        assert "bricks" in data


@jig.verifies("S-093")
def test_show_markdown_verbose_combination():
    """jigy show -m -v produces verbose markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)

        result = runner.invoke(cli, ["show", "-m", "-v"])

        assert result.exit_code == 0
        assert "#" in result.output


@jig.verifies("S-060", "S-093")
def test_show_all_subcommands_accept_json_flag():
    """All show subcommands accept -j flag."""
    runner = CliRunner()

    subcommands = ["layers", "bricks", "charter", "goals", "architecture"]

    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_jig_project_with_charter(root)

        for subcmd in subcommands:
            result = runner.invoke(cli, ["show", subcmd, "-j"])
            # Should not error with "no such option"
            assert "no such option" not in result.output.lower(), f"show {subcmd} should accept -j"


@jig.verifies("S-060", "S-093")
def test_show_all_subcommands_accept_markdown_flag():
    """All show subcommands accept -m flag."""
    runner = CliRunner()

    subcommands = ["layers", "bricks", "charter", "goals", "architecture"]

    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_jig_project_with_charter(root)

        for subcmd in subcommands:
            result = runner.invoke(cli, ["show", subcmd, "-m"])
            # Should not error with "no such option"
            assert "no such option" not in result.output.lower(), f"show {subcmd} should accept -m"


@jig.verifies("S-060", "S-093")
def test_show_all_subcommands_accept_verbose_flag():
    """All show subcommands accept -v flag."""
    runner = CliRunner()

    subcommands = ["layers", "bricks", "charter", "goals", "architecture"]

    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_jig_project_with_charter(root)

        for subcmd in subcommands:
            result = runner.invoke(cli, ["show", subcmd, "-v"])
            # Should not error with "no such option"
            assert "no such option" not in result.output.lower(), f"show {subcmd} should accept -v"


# ============================================================================
# Towers Command Tests (S-060, S-090, S-093)
# ============================================================================


def create_multi_tower_project(root: Path) -> None:
    """Create JIG project with multiple towers for testing."""
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

    # Create bricks.yaml with multiple towers
    (root / "jig" / "bricks.yaml").write_text(
        """bricks:
  - id: B-backend-data
    name: Backend Data Layer
    layer: 0
    tower: backend
    units:
      - M-backend-data

  - id: B-backend-api
    name: Backend API Layer
    layer: 1
    tower: backend
    units:
      - M-backend-api

  - id: B-frontend-state
    name: Frontend State
    layer: 0
    tower: frontend
    units:
      - M-frontend-state

  - id: B-frontend-ui
    name: Frontend UI
    layer: 1
    tower: frontend
    units:
      - M-frontend-ui
      - M-frontend-components
"""
    )

    # Create src directory
    (root / "src").mkdir()
    (root / "src" / "backend.py").write_text('"""Backend module."""\n')
    (root / "src" / "frontend.py").write_text('"""Frontend module."""\n')


@jig.verifies("S-060", "S-090")
def test_show_towers_basic():
    """jigy show towers lists all towers with brick counts."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_multi_tower_project(root)

        result = runner.invoke(cli, ["show", "towers"])

        assert result.exit_code == 0
        assert "backend" in result.output.lower()
        assert "frontend" in result.output.lower()


@jig.verifies("S-060", "S-090")
def test_show_towers_specific_tower():
    """jigy show towers <id> shows specific tower details."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_multi_tower_project(root)

        result = runner.invoke(cli, ["show", "towers", "backend"])

        assert result.exit_code == 0
        assert "backend" in result.output.lower()
        assert "B-backend-data" in result.output or "backend-data" in result.output.lower()


@jig.verifies("S-060", "S-090")
def test_show_towers_nonexistent_tower():
    """jigy show towers <id> for nonexistent tower gives error."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_multi_tower_project(root)

        result = runner.invoke(cli, ["show", "towers", "nonexistent"])

        assert result.exit_code != 0 or "not found" in result.output.lower()


@jig.verifies("S-060", "S-090")
def test_show_towers_single_tower_project():
    """jigy show towers shows single-tower message when no towers declared."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)  # No towers declared

        result = runner.invoke(cli, ["show", "towers"])

        assert result.exit_code == 0
        assert "single" in result.output.lower() or "no towers" in result.output.lower()


@jig.verifies("S-060", "S-090", "S-093")
def test_show_towers_json_flag():
    """jigy show towers -j produces valid JSON output."""
    import json

    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_multi_tower_project(root)

        result = runner.invoke(cli, ["--no-rebuild", "show", "towers", "-j"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "towers" in data
        tower_names = [t.get("name") or t.get("id") for t in data["towers"]]
        assert "backend" in tower_names
        assert "frontend" in tower_names


@jig.verifies("S-060", "S-090", "S-093")
def test_show_towers_markdown_flag():
    """jigy show towers -m produces markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_multi_tower_project(root)

        result = runner.invoke(cli, ["show", "towers", "-m"])

        assert result.exit_code == 0
        assert "#" in result.output  # Markdown headers


@jig.verifies("S-060", "S-090", "S-093")
def test_show_towers_verbose_flag():
    """jigy show towers -v produces verbose output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_multi_tower_project(root)

        result = runner.invoke(cli, ["show", "towers", "-v"])

        assert result.exit_code == 0
        # Verbose should show more detail about bricks
        assert "backend" in result.output.lower()


# ============================================================================
# Matrix Command Tests (S-060, S-091, S-093)
# ============================================================================


@jig.verifies("S-060", "S-091")
def test_show_matrix_basic():
    """jigy show matrix displays layer x tower grid."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_multi_tower_project(root)

        result = runner.invoke(cli, ["show", "matrix"])

        assert result.exit_code == 0
        # Should show matrix with tower headers
        assert "backend" in result.output.lower() or "frontend" in result.output.lower()
        # Should reference layers
        assert "layer" in result.output.lower() or "L0" in result.output or "L1" in result.output


@jig.verifies("S-060", "S-091")
def test_show_matrix_single_tower_project():
    """jigy show matrix shows appropriate message for single-tower projects."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_minimal_jig_project(root)  # No towers declared

        result = runner.invoke(cli, ["show", "matrix"])

        assert result.exit_code == 0
        assert "single" in result.output.lower() or "not applicable" in result.output.lower()


@jig.verifies("S-060", "S-091", "S-093")
def test_show_matrix_json_flag():
    """jigy show matrix -j produces valid JSON with 2D grid data."""
    import json

    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_multi_tower_project(root)

        result = runner.invoke(cli, ["--no-rebuild", "show", "matrix", "-j"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        # Should have matrix or grid data structure
        assert "matrix" in data or "grid" in data or "layers" in data


@jig.verifies("S-060", "S-091", "S-093")
def test_show_matrix_markdown_flag():
    """jigy show matrix -m produces markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_multi_tower_project(root)

        result = runner.invoke(cli, ["show", "matrix", "-m"])

        assert result.exit_code == 0
        assert "#" in result.output  # Markdown headers


@jig.verifies("S-060", "S-091", "S-093")
def test_show_matrix_verbose_flag():
    """jigy show matrix -v produces verbose output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_multi_tower_project(root)

        result = runner.invoke(cli, ["show", "matrix", "-v"])

        assert result.exit_code == 0


# ============================================================================
# Old Command Removal Tests (S-060, S-090, S-091)
# ============================================================================


@jig.verifies("S-060", "S-090")
def test_old_towers_command_not_available():
    """jigy towers (root level) should not be available."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_multi_tower_project(root)

        result = runner.invoke(cli, ["towers"])

        # Should fail - command not found at root level
        assert result.exit_code != 0
        assert "no such command" in result.output.lower() or "error" in result.output.lower()


@jig.verifies("S-060", "S-091")
def test_old_matrix_command_not_available():
    """jigy matrix (root level) should not be available."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_multi_tower_project(root)

        result = runner.invoke(cli, ["matrix"])

        # Should fail - command not found at root level
        assert result.exit_code != 0
        assert "no such command" in result.output.lower() or "error" in result.output.lower()
