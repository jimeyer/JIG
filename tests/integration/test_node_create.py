# @jig T-CLI-004 verifies:S-JIG-002 subsystem:core
"""Integration tests for jigy node create command."""

import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import yaml
from click.testing import CliRunner

from jig.cli.main import cli
from jig.core.parser import parse_ostc_node


@contextmanager
def chdir(path: Path) -> Iterator[None]:
    """Context manager to temporarily change directory."""
    original_dir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_dir)


def test_jigy_node_create_outcome(tmp_path: Path) -> None:
    """Verify jigy node create generates valid Outcome node."""
    runner = CliRunner()

    # Initialize JIG first
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    # Create outcome node (need to run from tmp_path directory)
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
                "Test Outcome",
                "--subsystem",
                "core",
            ],
        )

    # Should succeed
    assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}. Output: {result.output}"
    assert "✓ Created outcome node: O-TEST-001" in result.output

    # Verify file created
    node_file = tmp_path / "jig" / "outcomes" / "O-TEST-001.md"
    assert node_file.exists()

    # Verify valid YAML frontmatter
    node = parse_ostc_node(node_file)
    assert node.id == "O-TEST-001"
    assert node.type == "outcome"
    assert node.title == "Test Outcome"
    assert node.subsystem == "core"

    # Verify graph-index updated
    graph_file = tmp_path / "jig" / "graph-index.yaml"
    graph_data = yaml.safe_load(graph_file.read_text())
    assert any(n["id"] == "O-TEST-001" for n in graph_data["nodes"])


def test_jigy_node_create_specification(tmp_path: Path) -> None:
    """Verify jigy node create works for specification nodes."""
    runner = CliRunner()

    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    with chdir(tmp_path):
        result = runner.invoke(
            cli,
            [
                "node",
                "create",
                "--type",
                "specification",
                "--id",
                "S-API-001",
                "--title",
                "API Specification",
            ],
        )

    assert result.exit_code == 0
    assert "✓ Created specification node: S-API-001" in result.output

    node_file = tmp_path / "jig" / "specifications" / "S-API-001.md"
    assert node_file.exists()

    node = parse_ostc_node(node_file)
    assert node.id == "S-API-001"
    assert node.type == "specification"


def test_jigy_node_create_constraint(tmp_path: Path) -> None:
    """Verify jigy node create works for constraint nodes."""
    runner = CliRunner()

    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    with chdir(tmp_path):
        result = runner.invoke(
            cli,
            [
                "node",
                "create",
                "--type",
                "constraint",
                "--id",
                "C-PERF-001",
                "--title",
                "Performance Constraint",
            ],
        )

    assert result.exit_code == 0
    node_file = tmp_path / "jig" / "constraints" / "C-PERF-001.md"
    assert node_file.exists()


# @jig T-CLI-005 verifies:S-JIG-002 subsystem:core
def test_jigy_node_create_invalid_id_format(tmp_path: Path) -> None:
    """Verify jigy node create rejects invalid ID format."""
    runner = CliRunner()

    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    # Try with invalid ID (underscore instead of hyphen)
    with chdir(tmp_path):
        result = runner.invoke(
            cli,
            [
                "node",
                "create",
                "--type",
                "outcome",
                "--id",
                "O_TEST_001",
                "--title",
                "Test",
            ],
        )

    assert result.exit_code == 1
    assert "Error: Invalid ID format" in result.output


def test_jigy_node_create_invalid_id_lowercase(tmp_path: Path) -> None:
    """Verify jigy node create rejects lowercase IDs."""
    runner = CliRunner()

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
                "o-test-001",
                "--title",
                "Test",
            ],
        )

    assert result.exit_code == 1
    assert "Error: Invalid ID format" in result.output


def test_jigy_node_create_prefix_mismatch(tmp_path: Path) -> None:
    """Verify jigy node create rejects ID prefix that doesn't match type."""
    runner = CliRunner()

    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    # Try to create outcome with specification prefix
    with chdir(tmp_path):
        result = runner.invoke(
            cli,
            [
                "node",
                "create",
                "--type",
                "outcome",
                "--id",
                "S-TEST-001",
                "--title",
                "Test",
            ],
        )

    assert result.exit_code == 1
    assert "Error: ID prefix 'S' doesn't match type 'outcome'" in result.output
    assert "Expected ID to start with 'O-'" in result.output


def test_jigy_node_create_not_initialized(tmp_path: Path) -> None:
    """Verify jigy node create fails if JIG not initialized."""
    runner = CliRunner()

    # Don't run init
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

    assert result.exit_code == 3
    assert "JIG not initialized" in result.output or "Run 'jigy init' first" in result.output


def test_jigy_node_create_already_exists(tmp_path: Path) -> None:
    """Verify jigy node create fails if node already exists."""
    runner = CliRunner()

    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    # Create node first time
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

        # Try to create same node again
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
                "Test 2",
            ],
        )

    assert result.exit_code == 2
    assert "already exists" in result.output


# @jig T-CLI-006 verifies:S-JIG-001 subsystem:core
def test_jigy_node_create_performance(tmp_path: Path) -> None:
    """Verify jigy node create completes in <200ms."""
    runner = CliRunner()

    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    # Measure execution time
    with chdir(tmp_path):
        start_time = time.time()
        result = runner.invoke(
            cli,
            [
                "node",
                "create",
                "--type",
                "outcome",
                "--id",
                "O-PERF-001",
                "--title",
                "Performance Test",
            ],
        )
        elapsed_time = time.time() - start_time

    assert result.exit_code == 0
    assert elapsed_time < 0.2, f"jigy node create took {elapsed_time:.3f}s, expected <0.2s"


def test_jigy_node_create_help() -> None:
    """Verify jigy node create --help displays usage."""
    runner = CliRunner()

    result = runner.invoke(cli, ["node", "create", "--help"])

    assert result.exit_code == 0
    assert "Create a new OSTC node from template" in result.output
    assert "--type" in result.output
    assert "--id" in result.output
    assert "--title" in result.output
    assert "--subsystem" in result.output


def test_jigy_node_help() -> None:
    """Verify jigy node --help displays subcommands."""
    runner = CliRunner()

    result = runner.invoke(cli, ["node", "--help"])

    assert result.exit_code == 0
    assert "Manage OSTC nodes" in result.output
    assert "create" in result.output


def test_jigy_node_create_updates_graph_index(tmp_path: Path) -> None:
    """Verify multiple nodes are all added to graph index."""
    runner = CliRunner()

    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    # Create multiple nodes (O/S/C only - T nodes use annotations)
    nodes = [
        ("outcome", "O-TEST-001", "Outcome 1"),
        ("specification", "S-TEST-001", "Spec 1"),
        ("constraint", "C-TEST-001", "Constraint 1"),
    ]

    with chdir(tmp_path):
        for node_type, node_id, title in nodes:
            result = runner.invoke(
                cli,
                [
                    "node",
                    "create",
                    "--type",
                    node_type,
                    "--id",
                    node_id,
                    "--title",
                    title,
                ],
            )
            assert result.exit_code == 0

    # Verify all nodes in graph index
    graph_file = tmp_path / "jig" / "graph-index.yaml"
    graph_data = yaml.safe_load(graph_file.read_text())

    assert len(graph_data["nodes"]) == 3
    node_ids = [n["id"] for n in graph_data["nodes"]]
    assert "O-TEST-001" in node_ids
    assert "S-TEST-001" in node_ids
    assert "C-TEST-001" in node_ids


def test_jigy_node_create_without_subsystem(tmp_path: Path) -> None:
    """Verify nodes can be created without specifying subsystem."""
    runner = CliRunner()

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
            ],
        )

    assert result.exit_code == 0

    node_file = tmp_path / "jig" / "outcomes" / "O-TEST-001.md"
    node = parse_ostc_node(node_file)
    assert node.id == "O-TEST-001"
    # Subsystem should be null/None when not specified
    content = node_file.read_text()
    assert "subsystem: null" in content
