# @jig T-CLI-007 verifies:S-JIG-002 subsystem:core
"""Integration tests for jigy validate command."""

import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import yaml
from click.testing import CliRunner

from jig.cli.main import cli


@contextmanager
def chdir(path: Path) -> Iterator[None]:
    """Context manager to temporarily change directory."""
    original_dir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_dir)


def test_jigy_validate_all_valid(tmp_path: Path) -> None:
    """Verify jigy validate passes for valid graph."""
    runner = CliRunner()

    # Initialize and create valid nodes
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    with chdir(tmp_path):
        # Create a valid outcome node
        result = runner.invoke(
            cli,
            [
                "node",
                "create",
                "--type",
                "outcome",
                "--id",
                "O-TEST-001",
                "--title",
                "Test Outcome",
                "--subsystem",
                "core",
            ],
        )
        assert result.exit_code == 0

        # Create a valid specification node
        result = runner.invoke(
            cli,
            [
                "node",
                "create",
                "--type",
                "specification",
                "--id",
                "S-TEST-001",
                "--title",
                "Test Specification",
                "--subsystem",
                "core",
            ],
        )
        assert result.exit_code == 0

        # Run validate
        result = runner.invoke(cli, ["validate"])

    # Should succeed
    assert result.exit_code == 0
    assert "✓" in result.output
    assert "nodes valid" in result.output.lower()


# @jig T-CLI-008 verifies:S-JIG-002 subsystem:core
def test_jigy_validate_detects_errors(tmp_path: Path) -> None:
    """Verify jigy validate detects invalid nodes."""
    runner = CliRunner()

    # Initialize JIG
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    # Create node with invalid ID format
    outcomes_dir = tmp_path / "jig" / "outcomes"
    invalid_node = """---
id: O_INVALID_001
type: outcome
title: "Invalid ID"
---
Content
"""
    (outcomes_dir / "invalid.md").write_text(invalid_node)

    with chdir(tmp_path):
        # Run validate
        result = runner.invoke(cli, ["validate"])

    # Should fail
    assert result.exit_code == 1
    assert "✗" in result.output
    assert "error" in result.output.lower()
    assert "invalid id format" in result.output.lower()


def test_jigy_validate_not_initialized(tmp_path: Path) -> None:
    """Verify jigy validate fails gracefully if JIG not initialized."""
    runner = CliRunner()

    with chdir(tmp_path):
        result = runner.invoke(cli, ["validate"])

    assert result.exit_code == 3
    assert "not initialized" in result.output.lower()


def test_jigy_validate_help() -> None:
    """Verify jigy validate --help displays usage."""
    runner = CliRunner()

    result = runner.invoke(cli, ["validate", "--help"])

    assert result.exit_code == 0
    assert "Validate OSTC nodes" in result.output
    assert "--verbose" in result.output


def test_jigy_validate_verbose(tmp_path: Path) -> None:
    """Verify jigy validate --verbose shows detailed output."""
    runner = CliRunner()

    # Initialize and create node
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    with chdir(tmp_path):
        result = runner.invoke(
            cli,
            [
                "node",
                "create",
                "--type",
                "outcome",
                "--id",
                "O-TEST-001",
                "--title",
                "Test",
            ],
        )
        assert result.exit_code == 0

        # Run validate with verbose
        result = runner.invoke(cli, ["validate", "--verbose"])

    assert result.exit_code == 0
    assert "Node files:" in result.output
    assert "O-TEST-001.md" in result.output


def test_jigy_validate_shows_warnings(tmp_path: Path) -> None:
    """Verify jigy validate shows warnings by default."""
    runner = CliRunner()

    # Initialize and create node without subsystem
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    with chdir(tmp_path):
        result = runner.invoke(
            cli,
            [
                "node",
                "create",
                "--type",
                "outcome",
                "--id",
                "O-TEST-001",
                "--title",
                "Test Without Subsystem",
                # No subsystem - will generate warning
            ],
        )
        assert result.exit_code == 0

        # Run validate - warnings should be shown by default
        result = runner.invoke(cli, ["validate"])

    assert result.exit_code == 0
    # Should show warnings
    assert "warning" in result.output.lower() or "⚠" in result.output


def test_jigy_validate_duplicate_ids(tmp_path: Path) -> None:
    """Verify jigy validate detects duplicate node IDs."""
    runner = CliRunner()

    # Initialize
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    # Create two nodes with same ID
    outcomes_dir = tmp_path / "jig" / "outcomes"
    node1 = """---
id: O-TEST-001
type: outcome
title: "First node"
---
Content
"""
    node2 = """---
id: O-TEST-001
type: outcome
title: "Second node"
---
Content
"""
    (outcomes_dir / "first.md").write_text(node1)
    (outcomes_dir / "second.md").write_text(node2)

    with chdir(tmp_path):
        result = runner.invoke(cli, ["validate"])

    assert result.exit_code == 1
    assert "duplicate" in result.output.lower()
    assert "O-TEST-001" in result.output


def test_jigy_validate_graph_index_nonexistent_node(tmp_path: Path) -> None:
    """Verify jigy validate detects graph index referencing non-existent nodes."""
    runner = CliRunner()

    # Initialize
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    # Create one real node
    with chdir(tmp_path):
        result = runner.invoke(
            cli,
            [
                "node",
                "create",
                "--type",
                "outcome",
                "--id",
                "O-TEST-001",
                "--title",
                "Real Node",
            ],
        )
        assert result.exit_code == 0

    # Manually add non-existent node to graph index
    graph_index_file = tmp_path / "jig" / "graph-index.yaml"
    graph_data = yaml.safe_load(graph_index_file.read_text())
    graph_data["nodes"].append({"id": "O-MISSING-001", "type": "outcome"})
    graph_index_file.write_text(yaml.dump(graph_data))

    with chdir(tmp_path):
        result = runner.invoke(cli, ["validate"])

    assert result.exit_code == 1
    assert "non-existent" in result.output.lower() or "missing" in result.output.lower()


# @jig T-CLI-009 verifies:S-JIG-001 subsystem:core
def test_jigy_validate_performance(tmp_path: Path) -> None:
    """Verify jigy validate completes in <1s for 100 nodes."""
    runner = CliRunner()

    # Initialize
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    # Create 100 valid nodes
    with chdir(tmp_path):
        for i in range(100):
            result = runner.invoke(
                cli,
                [
                    "node",
                    "create",
                    "--type",
                    "outcome",
                    "--id",
                    f"O-PERF-{i:03d}",
                    "--title",
                    f"Performance Test Node {i}",
                    "--subsystem",
                    "core",
                ],
            )
            assert result.exit_code == 0

        # Measure validation time
        start_time = time.time()
        result = runner.invoke(cli, ["validate"])
        elapsed_time = time.time() - start_time

    assert result.exit_code == 0
    assert elapsed_time < 1.0, f"jigy validate took {elapsed_time:.3f}s, expected <1.0s"
    assert "100 nodes valid" in result.output


def test_jigy_validate_empty_graph(tmp_path: Path) -> None:
    """Verify jigy validate handles empty graph (no nodes)."""
    runner = CliRunner()

    # Initialize but don't create any nodes
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    with chdir(tmp_path):
        result = runner.invoke(cli, ["validate"])

    # Should succeed (no nodes is not an error)
    assert result.exit_code == 0
    assert "0 nodes valid" in result.output


def test_jigy_validate_mixed_valid_invalid(tmp_path: Path) -> None:
    """Verify jigy validate shows both valid and invalid nodes."""
    runner = CliRunner()

    # Initialize
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    # Create valid node
    with chdir(tmp_path):
        result = runner.invoke(
            cli,
            [
                "node",
                "create",
                "--type",
                "outcome",
                "--id",
                "O-VALID-001",
                "--title",
                "Valid Node",
            ],
        )
        assert result.exit_code == 0

    # Create invalid node
    outcomes_dir = tmp_path / "jig" / "outcomes"
    invalid_node = """---
id: O-INVALID
type: outcome
title: "Invalid ID - no number"
---
Content
"""
    (outcomes_dir / "invalid.md").write_text(invalid_node)

    with chdir(tmp_path):
        result = runner.invoke(cli, ["validate", "--verbose"])

    # Should fail but show both nodes
    assert result.exit_code == 1
    assert "O-VALID-001.md" in result.output
    assert "invalid.md" in result.output or "O-INVALID" in result.output


def test_jigy_validate_exit_codes(tmp_path: Path) -> None:
    """Verify jigy validate uses correct exit codes."""
    runner = CliRunner()

    # Test exit code 3 (not initialized)
    with chdir(tmp_path):
        result = runner.invoke(cli, ["validate"])
    assert result.exit_code == 3

    # Test exit code 0 (valid)
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    with chdir(tmp_path):
        result = runner.invoke(
            cli,
            ["node", "create", "--type", "outcome", "--id", "O-TEST-001", "--title", "Test"],
        )
        assert result.exit_code == 0

        result = runner.invoke(cli, ["validate"])
    assert result.exit_code == 0

    # Test exit code 1 (errors)
    outcomes_dir = tmp_path / "jig" / "outcomes"
    invalid = "---\nid: BAD\ntype: outcome\ntitle: Test\n---\nContent"
    (outcomes_dir / "bad.md").write_text(invalid)

    with chdir(tmp_path):
        result = runner.invoke(cli, ["validate"])
    assert result.exit_code == 1


def test_jigy_validate_colorized_output(tmp_path: Path) -> None:
    """Verify jigy validate uses colorized output."""
    runner = CliRunner()

    # Initialize and create node
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    with chdir(tmp_path):
        result = runner.invoke(
            cli,
            ["node", "create", "--type", "outcome", "--id", "O-TEST-001", "--title", "Test"],
        )
        assert result.exit_code == 0

        result = runner.invoke(cli, ["validate"])

    # Check for checkmark (✓) or cross (✗) symbols
    assert "✓" in result.output or "✗" in result.output
