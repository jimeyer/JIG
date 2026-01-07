"""Integration tests for validation commands.

These tests verify that validation actually runs by catching deliberate errors.
Each test creates invalid artifacts and verifies the correct error is caught.
"""

import json
from pathlib import Path

import jig
from click.testing import CliRunner
from jig.cli.main import cli


@jig.verifies("S-072", "S-073", "S-074")
def test_validate_catches_invalid_charter():
    """Verify jigy validate actually runs charter validation."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create jig directory structure
        Path("jig").mkdir()

        # Create Charter.md missing defines_goals field
        (Path("jig") / "Charter.md").write_text(
            """---
id: Charter
type: charter
---

# Project Charter

## Overview

This is a test charter without defines_goals.
"""
        )

        result = runner.invoke(cli, ["validate"])

        # Assert validation fails
        assert result.exit_code != 0, f"Expected validation to fail, got exit_code={result.exit_code}"

        # Assert error mentions defines_goals or charter-related issue
        output_lower = result.output.lower()
        assert (
            "defines_goals" in output_lower
            or "charter" in output_lower
        ), f"Expected error about defines_goals or charter, got:\n{result.output}"


@jig.verifies("S-076", "S-077", "S-078", "S-079")
def test_validate_catches_invalid_architecture():
    """Verify jigy validate actually runs architecture validation."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create valid Charter with G-001
        Path("jig").mkdir()
        (Path("jig") / "Charter.md").write_text(
            """---
id: Charter
type: charter
defines_goals: [G-001]
---

# Project Charter

### G-001: Test Goal

This is a test goal.
"""
        )

        # Create architecture directory
        arch_dir = Path("jig/architecture")
        arch_dir.mkdir(parents=True)

        # Create architecture file with bad filename (not A-NNN_Title.md pattern)
        # Using A-1_Test.md instead of A-001_Test.md (not zero-padded)
        (arch_dir / "A-1_Test.md").write_text(
            """---
id: A-1
type: architecture
title: Test
status: active
supports_goals: [G-001]
---

# Test

Test architecture.
"""
        )

        result = runner.invoke(cli, ["validate"])

        # Assert validation fails
        assert result.exit_code != 0, f"Expected validation to fail, got exit_code={result.exit_code}"

        # Assert error mentions filename pattern or ID format
        output_lower = result.output.lower()
        assert (
            "a-nnn" in output_lower
            or "a-001" in output_lower
            or "pattern" in output_lower
            or "invalid" in output_lower
            or "format" in output_lower
        ), f"Expected error about filename pattern or ID format, got:\n{result.output}"


@jig.verifies("S-075")
def test_validate_catches_invalid_goal_reference():
    """Verify jigy validate catches invalid goal references."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create Charter defining G-001
        Path("jig").mkdir()
        (Path("jig") / "Charter.md").write_text(
            """---
id: Charter
type: charter
defines_goals: [G-001]
---

# Project Charter

### G-001: Test Goal

This is the only valid goal.
"""
        )

        # Create Outcome with supports_goals: [G-999] (doesn't exist)
        outcome_dir = Path("jig/outcomes")
        outcome_dir.mkdir(parents=True)
        (outcome_dir / "O-001_Test_Outcome.md").write_text(
            """---
id: O-001
type: outcome
title: Test Outcome
specifies: []
supports_goals: [G-999]
---

# Test Outcome

This outcome references a non-existent goal G-999.
"""
        )

        result = runner.invoke(cli, ["validate"])

        # Assert validation fails
        assert result.exit_code != 0, f"Expected validation to fail, got exit_code={result.exit_code}"

        # Assert G-999 is mentioned in output
        assert "G-999" in result.output, f"Expected error to mention G-999, got:\n{result.output}"


@jig.verifies("S-087", "S-088", "S-089")
def test_validate_catches_invalid_tower_format():
    """Verify jigy validate bricks catches invalid tower format."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create mock implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "M-test", "type": "module"}) + "\n"
            + json.dumps({"id": "F-test.func", "type": "function"}) + "\n"
        )

        # Create bricks.yaml with invalid tower format (CamelCase instead of kebab-case)
        Path("jig").mkdir(exist_ok=True)
        (Path("jig") / "bricks.yaml").write_text(
            """
bricks:
  - id: B-test
    name: Test
    layer: 0
    tower: InvalidCamelCase
    units:
      - M-test
"""
        )

        # Use --no-rebuild to skip auto-rebuild (we have mock graphs)
        result = runner.invoke(cli, ["--no-rebuild", "validate", "bricks"])

        # Assert validation fails
        assert result.exit_code != 0, f"Expected validation to fail, got exit_code={result.exit_code}"

        # Assert error mentions tower or kebab-case
        output_lower = result.output.lower()
        assert (
            "tower" in output_lower
            or "kebab" in output_lower
            or "invalidcamelcase" in output_lower
        ), f"Expected error about tower format, got:\n{result.output}"
