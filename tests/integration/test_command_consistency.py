# @jig T-JIGY-046 verifies:S-JIGY-014 subsystem:jigy-tool
"""Integration tests for command consistency across validate, status, and index rebuild."""

import os
import re
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from textwrap import dedent

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


def parse_node_count(output: str) -> int:
    """Parse total node count from command output.

    Handles formats like:
    - "Total nodes: 88 (14 O, 41 S, 0 X, 33 C, 0 T)"
    - "✓ 92 nodes, 57 edges, 5 subsystems"
    """
    # Try status format first: "✓ 92 nodes, 57 edges"
    match = re.search(r'✓\s+(\d+)\s+nodes?', output)
    if match:
        return int(match.group(1))

    # Try rebuild/validate format: "Total nodes: 88"
    match = re.search(r'Total nodes:\s+(\d+)', output)
    if match:
        return int(match.group(1))

    return 0


def parse_edge_count(output: str) -> int:
    """Parse total edge count from command output.

    Handles formats like:
    - "Total edges: 57 (after deduplication)"
    - "✓ 92 nodes, 57 edges, 5 subsystems"
    """
    # Try rebuild format first: "Total edges: 57"
    match = re.search(r'Total edges:\s+(\d+)', output)
    if match:
        return int(match.group(1))

    # Try status format: "57 edges,"
    match = re.search(r'(\d+)\s+edges?', output)
    if match:
        return int(match.group(1))

    return 0


def parse_subsystem_count(output: str) -> int:
    """Parse subsystem count from command output.

    Handles formats like:
    - "✓ 92 nodes, 57 edges, 5 subsystems"
    """
    match = re.search(r'(\d+)\s+subsystems?', output)
    if match:
        return int(match.group(1))

    return 0


def test_validate_status_index_consistency(tmp_path: Path) -> None:
    """Verify all commands report consistent counts."""
    runner = CliRunner()

    # Initialize JIG
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    jig_dir = tmp_path / "jig"

    # Create test nodes with various types and subsystems
    outcomes_dir = jig_dir / "outcomes"
    (outcomes_dir / "O-TEST-001.md").write_text(dedent("""
        ---
        id: O-TEST-001
        type: outcome
        title: "Test Outcome 1"
        subsystem: core
        status: active
        ---
        Content
    """).lstrip())

    (outcomes_dir / "O-TEST-002.md").write_text(dedent("""
        ---
        id: O-TEST-002
        type: outcome
        title: "Test Outcome 2"
        subsystem: auth
        status: active
        ---
        Content
    """).lstrip())

    specs_dir = jig_dir / "specifications"
    (specs_dir / "S-TEST-001.md").write_text(dedent("""
        ---
        id: S-TEST-001
        type: specification
        title: "Test Spec 1"
        subsystem: core
        status: active
        implements:
          - O-TEST-001
        ---
        Content
    """).lstrip())

    (specs_dir / "S-TEST-002.md").write_text(dedent("""
        ---
        id: S-TEST-002
        type: specification
        title: "Test Spec 2"
        subsystem: auth
        status: active
        implements:
          - O-TEST-002
        ---
        Content
    """).lstrip())

    (specs_dir / "S-TEST-003.md").write_text(dedent("""
        ---
        id: S-TEST-003
        type: specification
        title: "Test Spec 3"
        subsystem: core.security
        status: active
        implements:
          - O-TEST-001
        ---
        Content
    """).lstrip())

    # Run index rebuild
    rebuild_result = runner.invoke(cli, ["index", "rebuild", "--project-dir", str(tmp_path)])
    assert rebuild_result.exit_code == 0, f"rebuild failed: {rebuild_result.output}"

    # Run status
    with chdir(tmp_path):
        status_result = runner.invoke(cli, ["status"])
    assert status_result.exit_code == 0, f"status failed: {status_result.output}"

    # Run validate
    with chdir(tmp_path):
        validate_result = runner.invoke(cli, ["validate"])
    assert validate_result.exit_code == 0, f"validate failed: {validate_result.output}"

    # Parse counts from each command
    rebuild_nodes = parse_node_count(rebuild_result.output)
    rebuild_edges = parse_edge_count(rebuild_result.output)

    status_nodes = parse_node_count(status_result.output)
    status_edges = parse_edge_count(status_result.output)
    status_subsystems = parse_subsystem_count(status_result.output)

    # Verify consistency
    assert rebuild_nodes == status_nodes, \
        f"Node count mismatch: rebuild={rebuild_nodes}, status={status_nodes}\n" \
        f"Rebuild output:\n{rebuild_result.output}\n" \
        f"Status output:\n{status_result.output}"

    assert rebuild_edges == status_edges, \
        f"Edge count mismatch: rebuild={rebuild_edges}, status={status_edges}\n" \
        f"Rebuild output:\n{rebuild_result.output}\n" \
        f"Status output:\n{status_result.output}"

    # Verify subsystems are reported (should be > 0)
    assert status_subsystems > 0, \
        f"Status should show subsystems (got {status_subsystems})\n" \
        f"Status output:\n{status_result.output}"

    # Verify validate passes without errors
    assert "✓" in validate_result.output or "valid" in validate_result.output.lower(), \
        f"Validate should pass\n" \
        f"Validate output:\n{validate_result.output}"

    # Verify expected counts based on what we created
    # 2 outcomes + 3 specs = 5 nodes
    assert rebuild_nodes == 5, f"Expected 5 nodes, got {rebuild_nodes}"

    # 3 implements edges (S-TEST-001 → O-TEST-001, S-TEST-002 → O-TEST-002, S-TEST-003 → O-TEST-001)
    assert rebuild_edges == 3, f"Expected 3 edges, got {rebuild_edges}"

    # 2 top-level subsystems (core, auth) + 1 nested (core.security)
    # Depending on how nesting is counted, could be 2 or 3
    assert status_subsystems >= 2, f"Expected at least 2 subsystems, got {status_subsystems}"


def test_consistency_with_code_annotations(tmp_path: Path) -> None:
    """Verify consistency when code annotations are present."""
    runner = CliRunner()

    # Initialize JIG
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    jig_dir = tmp_path / "jig"

    # Create an outcome
    outcomes_dir = jig_dir / "outcomes"
    (outcomes_dir / "O-CODE-001.md").write_text(dedent("""
        ---
        id: O-CODE-001
        type: outcome
        title: "Code Outcome"
        subsystem: impl
        status: active
        ---
        Content
    """).lstrip())

    # Create a specification
    specs_dir = jig_dir / "specifications"
    (specs_dir / "S-CODE-001.md").write_text(dedent("""
        ---
        id: S-CODE-001
        type: specification
        title: "Code Spec"
        subsystem: impl
        status: active
        implements:
          - O-CODE-001
        ---
        Content
    """).lstrip())

    # Create a code file with annotation
    src_dir = tmp_path / "src"
    src_dir.mkdir(parents=True)
    (src_dir / "module.py").write_text(dedent("""
        # @jig C-CODE-001 implements:S-CODE-001 subsystem:impl
        class MyClass:
            pass
    """).lstrip())

    # Run index rebuild
    rebuild_result = runner.invoke(cli, ["index", "rebuild", "--project-dir", str(tmp_path)])
    assert rebuild_result.exit_code == 0

    # Run status
    with chdir(tmp_path):
        status_result = runner.invoke(cli, ["status"])
    assert status_result.exit_code == 0

    # Parse counts
    rebuild_nodes = parse_node_count(rebuild_result.output)
    status_nodes = parse_node_count(status_result.output)

    rebuild_edges = parse_edge_count(rebuild_result.output)
    status_edges = parse_edge_count(status_result.output)

    # Verify consistency
    assert rebuild_nodes == status_nodes, \
        f"Node count mismatch with code annotations: rebuild={rebuild_nodes}, status={status_nodes}"

    assert rebuild_edges == status_edges, \
        f"Edge count mismatch with code annotations: rebuild={rebuild_edges}, status={status_edges}"

    # Should have 3 nodes (1 outcome + 1 spec + 1 code)
    assert rebuild_nodes == 3, f"Expected 3 nodes, got {rebuild_nodes}"

    # Should have 2 edges (S → O, C → S)
    assert rebuild_edges == 2, f"Expected 2 edges, got {rebuild_edges}"


def test_consistency_handles_template_filtering(tmp_path: Path) -> None:
    """Verify consistency when template nodes are filtered out."""
    runner = CliRunner()

    # Initialize JIG
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    jig_dir = tmp_path / "jig"

    # Create an active outcome
    outcomes_dir = jig_dir / "outcomes"
    (outcomes_dir / "O-ACTIVE-001.md").write_text(dedent("""
        ---
        id: O-ACTIVE-001
        type: outcome
        title: "Active Outcome"
        subsystem: test
        status: active
        ---
        Content
    """).lstrip())

    # Create a template outcome (should be filtered)
    (outcomes_dir / "O-TEMPLATE-001.md").write_text(dedent("""
        ---
        id: O-TEMPLATE-001
        type: outcome
        title: "Template Outcome"
        subsystem: test
        status: template
        ---
        Content
    """).lstrip())

    # Run index rebuild
    rebuild_result = runner.invoke(cli, ["index", "rebuild", "--project-dir", str(tmp_path)])
    assert rebuild_result.exit_code == 0

    # Parse rebuild count
    rebuild_nodes = parse_node_count(rebuild_result.output)

    # Should only count the active node (template filtered out)
    assert rebuild_nodes == 1, \
        f"Expected 1 node (template filtered), got {rebuild_nodes}\n" \
        f"Rebuild output:\n{rebuild_result.output}"

    # Verify template node is NOT in the output
    assert "O-TEMPLATE-001" not in rebuild_result.output, \
        "Template node should not appear in rebuild output"
