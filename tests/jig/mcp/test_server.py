# ABOUTME: Tests for MCP server tool functions.
# ABOUTME: Verifies tools delegate correctly to query layer.

"""Tests for jig.mcp.server module.

Tests tool functions directly (not MCP protocol), verifying they
delegate to the query layer and return correct types.
"""

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

import pytest

import jig
from jig.mcp.server import (
    get_overview,
    lookup_node,
    mcp,
    run_server,
    search_docs,
    validate_project,
)


@dataclass
class _FakePaths:
    """Minimal PathsConfig stand-in for tests."""

    source: Path
    tests: Path
    jig_root: Path
    specifications: Path
    outcomes: Path
    bricks: Path
    generated: Path
    charter: Path
    architecture: Path


@dataclass
class _FakeConfig:
    """Minimal JigConfig stand-in for tests."""

    paths: _FakePaths
    project_root: Path
    config_file_path: Path | None = None
    has_config_file: bool = False


def _make_config(tmp_path: Path) -> _FakeConfig:
    """Create a fake config rooted in tmp_path with standard subdirs."""
    jig_root = tmp_path / "jig"
    specs_dir = jig_root / "specifications"
    outcomes_dir = jig_root / "outcomes"
    arch_dir = jig_root / "architecture"
    charter_path = jig_root / "Charter.md"
    generated_dir = jig_root / "generated"
    bricks_path = jig_root / "bricks.yaml"
    src_dir = tmp_path / "src"
    tests_dir = tmp_path / "tests"

    specs_dir.mkdir(parents=True)
    outcomes_dir.mkdir(parents=True)
    arch_dir.mkdir(parents=True)
    generated_dir.mkdir(parents=True)
    src_dir.mkdir(parents=True)
    tests_dir.mkdir(parents=True)

    return _FakeConfig(
        paths=_FakePaths(
            source=src_dir,
            tests=tests_dir,
            jig_root=jig_root,
            specifications=specs_dir,
            outcomes=outcomes_dir,
            bricks=bricks_path,
            generated=generated_dir,
            charter=charter_path,
            architecture=arch_dir,
        ),
        project_root=tmp_path,
    )


@jig.verifies("S-117")
def test_lookup_node_valid_returns_dict(tmp_path: Path) -> None:
    """lookup_node returns a dict (possibly empty) for valid identifiers."""
    config = _make_config(tmp_path)

    with patch("jig.mcp.server._get_config", return_value=config):
        result = lookup_node("S-001")
    assert isinstance(result, dict)


@jig.verifies("S-117")
def test_lookup_node_invalid_returns_empty_dict(tmp_path: Path) -> None:
    """lookup_node returns {} for identifiers that don't resolve."""
    config = _make_config(tmp_path)

    with patch("jig.mcp.server._get_config", return_value=config):
        result = lookup_node("ZZZZZ-999")
    assert result == {}


@jig.verifies("S-117")
def test_search_docs_returns_list(tmp_path: Path) -> None:
    """search_docs returns a list of matching documents."""
    config = _make_config(tmp_path)
    # Write a spec file with searchable content
    spec_file = config.paths.specifications / "S-001_Test_Spec.md"
    spec_file.write_text("---\nid: S-001\ntitle: Test Spec\n---\n# Test Spec\n\nSome searchable content here.\n")

    with patch("jig.mcp.server._get_config", return_value=config):
        result = search_docs("searchable")
    assert isinstance(result, list)
    assert len(result) >= 1
    assert result[0]["id"] == "S-001"


@jig.verifies("S-117")
def test_search_docs_empty_query_returns_empty(tmp_path: Path) -> None:
    """search_docs returns [] for empty query."""
    config = _make_config(tmp_path)

    with patch("jig.mcp.server._get_config", return_value=config):
        result = search_docs("")
    assert result == []


@jig.verifies("S-117")
def test_get_overview_returns_dict(tmp_path: Path) -> None:
    """get_overview returns a dict with overview data."""
    config = _make_config(tmp_path)

    with patch("jig.mcp.server._get_config", return_value=config):
        result = get_overview()
    assert isinstance(result, dict)


@jig.verifies("S-117")
def test_validate_project_returns_dict(tmp_path: Path) -> None:
    """validate_project returns a dict with errors key."""
    config = _make_config(tmp_path)

    with patch("jig.mcp.server._get_config", return_value=config):
        result = validate_project()
    assert isinstance(result, dict)
    assert "errors" in result


@jig.verifies("S-117")
def test_run_server_function_exists() -> None:
    """run_server is importable and callable."""
    assert callable(run_server)


@jig.verifies("S-117")
def test_mcp_instance_has_tools() -> None:
    """The FastMCP instance has all 4 tools registered."""
    tool_names = {t.name for t in mcp._tool_manager._tools.values()}
    expected = {"lookup_node", "search_docs", "get_overview", "validate_project"}
    assert expected.issubset(tool_names), f"Missing tools: {expected - tool_names}"
