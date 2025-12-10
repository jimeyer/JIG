"""Tests for project root auto-discovery."""

import tempfile
from pathlib import Path

import pytest

import jig
from jig.cli.discovery import ProjectNotFoundError, find_project_root


@jig.verifies("S-057")
def test_find_project_root_in_current_dir():
    """Finds project root when jig/ is in current directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir).resolve()
        (root / "jig").mkdir()

        result = find_project_root(root)
        assert result == root


@jig.verifies("S-057")
def test_find_project_root_in_parent():
    """Finds project root when jig/ is in parent directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir).resolve()
        (root / "jig").mkdir()
        subdir = root / "src" / "deep"
        subdir.mkdir(parents=True)

        result = find_project_root(subdir)
        assert result == root


@jig.verifies("S-057")
def test_find_project_root_in_grandparent():
    """Finds project root when jig/ is in grandparent directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir).resolve()
        (root / "jig").mkdir()
        deep_subdir = root / "src" / "pkg" / "subpkg" / "module"
        deep_subdir.mkdir(parents=True)

        result = find_project_root(deep_subdir)
        assert result == root


@jig.verifies("S-057")
def test_find_project_root_not_found():
    """Raises ProjectNotFoundError when no jig/ directory exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        # No jig/ directory created

        with pytest.raises(ProjectNotFoundError) as exc_info:
            find_project_root(root)

        assert "Not in a JIG project" in str(exc_info.value)
        assert "No jig/ directory found" in str(exc_info.value)


@jig.verifies("S-057")
def test_find_project_root_file_not_dir():
    """Does not match if jig is a file instead of directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "jig").write_text("not a directory")

        with pytest.raises(ProjectNotFoundError):
            find_project_root(root)


@jig.verifies("S-057")
def test_find_project_root_defaults_to_cwd(monkeypatch):
    """Uses current working directory when start_dir is None."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir).resolve()
        (root / "jig").mkdir()

        monkeypatch.chdir(root)
        result = find_project_root()
        assert result == root
