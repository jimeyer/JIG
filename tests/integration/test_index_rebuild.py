# @jig T-JIGY-043 verifies:S-JIGY-013 subsystem:jigy-tool
"""Integration tests for jigy index rebuild command."""

import json
import os
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


def test_index_rebuild_exports_subsystems(tmp_path: Path) -> None:
    """Verify index rebuild writes subsystems section to graph-index.json."""
    runner = CliRunner()

    # Initialize JIG
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    jig_dir = tmp_path / "jig"

    # Create nodes with subsystem metadata
    outcomes_dir = jig_dir / "outcomes"
    (outcomes_dir / "O-AUTH-001.md").write_text(dedent("""
        ---
        id: O-AUTH-001
        type: outcome
        title: "Auth Outcome"
        subsystem: auth
        status: active
        ---
        Content
    """).lstrip())

    (outcomes_dir / "O-AUTH-002.md").write_text(dedent("""
        ---
        id: O-AUTH-002
        type: outcome
        title: "Core Outcome"
        subsystem: core
        status: active
        ---
        Content
    """).lstrip())

    specs_dir = jig_dir / "specifications"
    (specs_dir / "S-AUTH-001.md").write_text(dedent("""
        ---
        id: S-AUTH-001
        type: specification
        title: "Auth Spec"
        subsystem: auth
        status: active
        implements:
          - O-AUTH-001
        ---
        Content
    """).lstrip())

    #  Create a nested subsystem using a constraint node
    constraints_dir = jig_dir / "constraints"
    constraints_dir.mkdir(parents=True, exist_ok=True)
    (constraints_dir / "C-AUTH-001.md").write_text(dedent("""
        ---
        id: C-AUTH-001
        type: constraint
        title: "CRDT Serialization Constraint"
        subsystem: crdt.ser
        status: active
        ---
        Content
    """).lstrip())

    # Run index rebuild
    result = runner.invoke(cli, ["index", "rebuild", "--project-dir", str(tmp_path)])

    assert result.exit_code == 0, f"rebuild failed: {result.output}"

    # Check graph-index.json
    index_file = jig_dir / "graph-index.json"
    assert index_file.exists()

    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)

    # Verify subsystems section exists
    assert "subsystems" in index_data, "subsystems section missing from graph-index.json"
    assert len(index_data["subsystems"]) > 0, "subsystems section is empty"

    # Verify flat subsystems
    assert "auth" in index_data["subsystems"]
    assert "core" in index_data["subsystems"]

    # Verify nodes assigned to subsystems
    auth_nodes = set(index_data["subsystems"]["auth"]["nodes"])
    assert "O-AUTH-001" in auth_nodes
    assert "S-AUTH-001" in auth_nodes

    core_nodes = index_data["subsystems"]["core"]["nodes"]
    assert "O-AUTH-002" in core_nodes

    # Verify nested subsystem
    assert "crdt" in index_data["subsystems"]
    assert "subsystems" in index_data["subsystems"]["crdt"]
    assert "ser" in index_data["subsystems"]["crdt"]["subsystems"]
    assert "C-AUTH-001" in index_data["subsystems"]["crdt"]["subsystems"]["ser"]["nodes"]


def test_status_shows_correct_subsystem_count(tmp_path: Path) -> None:
    """Verify jigy status shows correct subsystem count after rebuild."""
    runner = CliRunner()

    # Initialize JIG
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    jig_dir = tmp_path / "jig"

    # Create nodes with subsystems
    outcomes_dir = jig_dir / "outcomes"
    (outcomes_dir / "O-AUTH-001.md").write_text(dedent("""
        ---
        id: O-AUTH-001
        type: outcome
        title: "Test Outcome"
        subsystem: auth
        status: active
        ---
        Content
    """).lstrip())

    (outcomes_dir / "O-AUTH-002.md").write_text(dedent("""
        ---
        id: O-AUTH-002
        type: outcome
        title: "Test Outcome 2"
        subsystem: core
        status: active
        ---
        Content
    """).lstrip())

    # Run index rebuild
    result = runner.invoke(cli, ["index", "rebuild", "--project-dir", str(tmp_path)])
    assert result.exit_code == 0

    # Run status
    with chdir(tmp_path):
        result = runner.invoke(cli, ["status"])

    assert result.exit_code == 0

    # Should show subsystems (not 0)
    assert "subsystems" in result.output.lower() or "subsystem" in result.output.lower()
    # Should not say "0 subsystems"
    assert "0 subsystem" not in result.output.lower()
