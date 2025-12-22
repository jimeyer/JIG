"""Tests for staleness detection module.

Verifies git-based staleness detection for graph rebuild decisions.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import jig
from jig.config import JigConfig, PathsConfig
from jig.staleness import (
    collect_git_metadata,
    get_staleness_status,
    git_rev_parse,
    git_status_porcelain,
    git_tree_hash,
    is_stale,
)


def make_config(tmp_path: Path) -> JigConfig:
    """Create a test JigConfig with paths in tmp_path."""
    paths = PathsConfig(
        source=tmp_path / "src",
        tests=tmp_path / "tests",
        jig_root=tmp_path / "jig",
        specifications=tmp_path / "jig" / "specifications",
        outcomes=tmp_path / "jig" / "outcomes",
        bricks=tmp_path / "jig" / "bricks.yaml",
        generated=tmp_path / "jig" / "generated",
    )
    return JigConfig(
        paths=paths,
        project_root=tmp_path,
        config_file_path=None,
        has_config_file=False,
    )


class TestGitRevParse:
    """Tests for git_rev_parse helper."""

    @jig.verifies("S-069")
    def test_returns_sha_in_git_repo(self, tmp_path: Path):
        """Returns HEAD SHA when in a git repository."""
        # Create a git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        (tmp_path / "file.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        result = git_rev_parse(tmp_path)

        assert result is not None
        assert len(result) == 40
        assert all(c in "0123456789abcdef" for c in result)

    @jig.verifies("S-069")
    def test_returns_none_outside_git_repo(self):
        """Returns None when not in a git repository."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = git_rev_parse(Path(tmp_dir))
            assert result is None


class TestGitTreeHash:
    """Tests for git_tree_hash helper."""

    @jig.verifies("S-069")
    def test_returns_hash_for_tracked_directory(self, tmp_path: Path):
        """Returns tree hash for a tracked directory."""
        # Create a git repo with a subdirectory
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "module.py").write_text("x = 1")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        result = git_tree_hash(tmp_path, src_dir)

        assert result is not None
        assert len(result) == 40

    @jig.verifies("S-069")
    def test_returns_none_for_untracked_directory(self, tmp_path: Path):
        """Returns None for an untracked directory."""
        # Create a git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        (tmp_path / "file.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        # Create untracked directory
        untracked = tmp_path / "untracked"
        untracked.mkdir()
        (untracked / "file.py").write_text("y = 2")

        result = git_tree_hash(tmp_path, untracked)

        assert result is None


class TestGitStatusPorcelain:
    """Tests for git_status_porcelain helper."""

    @jig.verifies("S-069")
    def test_returns_empty_when_clean(self, tmp_path: Path):
        """Returns empty list when working directory is clean."""
        # Create a git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "module.py").write_text("x = 1")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        result = git_status_porcelain(tmp_path, [src_dir])

        assert result == []

    @jig.verifies("S-069")
    def test_returns_dirty_files(self, tmp_path: Path):
        """Returns list of modified/untracked files."""
        # Create a git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "module.py").write_text("x = 1")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        # Modify a file
        (src_dir / "module.py").write_text("x = 2")

        result = git_status_porcelain(tmp_path, [src_dir])

        assert "src/module.py" in result


class TestIsStale:
    """Tests for is_stale function."""

    @jig.verifies("S-069")
    def test_stale_when_graph_missing(self, tmp_path: Path):
        """Returns True when graph file does not exist."""
        config = make_config(tmp_path)
        # No graph file created

        result = is_stale("impl", config)

        assert result is True

    @jig.verifies("S-069")
    def test_stale_when_metadata_corrupt(self, tmp_path: Path):
        """Returns True when metadata cannot be parsed."""
        config = make_config(tmp_path)
        config.paths.generated.mkdir(parents=True)
        graph_path = config.paths.generated / "implementation-graph.ndjson"
        graph_path.write_text("not valid json")

        result = is_stale("impl", config)

        assert result is True

    @jig.verifies("S-069")
    def test_stale_when_no_git_metadata(self, tmp_path: Path):
        """Returns True when graph has no git metadata (old format)."""
        config = make_config(tmp_path)
        config.paths.generated.mkdir(parents=True)
        graph_path = config.paths.generated / "implementation-graph.ndjson"
        metadata = {"_meta": {"version": "1.0"}}
        graph_path.write_text(json.dumps(metadata))

        result = is_stale("impl", config)

        assert result is True

    @jig.verifies("S-069")
    def test_current_when_git_state_matches(self, tmp_path: Path):
        """Returns False when git state matches recorded metadata."""
        # Create git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)

        # Create source directory
        config = make_config(tmp_path)
        config.paths.source.mkdir(parents=True)
        (config.paths.source / "module.py").write_text("x = 1")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        # Get current git state
        head = git_rev_parse(tmp_path)
        tree_hash = git_tree_hash(tmp_path, config.paths.source)

        # Create graph with matching metadata
        config.paths.generated.mkdir(parents=True)
        graph_path = config.paths.generated / "implementation-graph.ndjson"
        metadata = {
            "_meta": {
                "version": "1.0",
                "git_head": head,
                "git_tree_hashes": {"src": tree_hash},
                "git_dirty_files": [],
            }
        }
        graph_path.write_text(json.dumps(metadata))

        result = is_stale("impl", config)

        assert result is False

    @jig.verifies("S-069")
    def test_stale_when_dirty_files_differ(self, tmp_path: Path):
        """Returns True when uncommitted files differ from recorded."""
        # Create git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)

        # Create source directory
        config = make_config(tmp_path)
        config.paths.source.mkdir(parents=True)
        (config.paths.source / "module.py").write_text("x = 1")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        head = git_rev_parse(tmp_path)
        tree_hash = git_tree_hash(tmp_path, config.paths.source)

        # Create graph with no dirty files recorded
        config.paths.generated.mkdir(parents=True)
        graph_path = config.paths.generated / "implementation-graph.ndjson"
        metadata = {
            "_meta": {
                "version": "1.0",
                "git_head": head,
                "git_tree_hashes": {"src": tree_hash},
                "git_dirty_files": [],
            }
        }
        graph_path.write_text(json.dumps(metadata))

        # Modify a file (create dirty state)
        (config.paths.source / "module.py").write_text("x = 2")

        result = is_stale("impl", config)

        assert result is True

    @jig.verifies("S-069")
    def test_stale_in_non_git_project(self):
        """Returns True for non-git projects (graceful degradation)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            config = make_config(tmp_path)
            config.paths.generated.mkdir(parents=True)
            graph_path = config.paths.generated / "implementation-graph.ndjson"
            metadata = {"_meta": {"git_head": "abc123"}}
            graph_path.write_text(json.dumps(metadata))

            result = is_stale("impl", config)

            assert result is True


class TestGetStalenessStatus:
    """Tests for get_staleness_status function."""

    @jig.verifies("S-069")
    def test_returns_status_for_all_graphs(self, tmp_path: Path):
        """Returns status dict for impl, verify, intent."""
        config = make_config(tmp_path)

        result = get_staleness_status(config)

        assert "impl" in result
        assert "verify" in result
        assert "intent" in result
        assert all(isinstance(v, bool) for v in result.values())

    @jig.verifies("S-069")
    def test_all_stale_when_no_graphs(self, tmp_path: Path):
        """All graphs stale when none exist."""
        config = make_config(tmp_path)

        result = get_staleness_status(config)

        assert result == {"impl": True, "verify": True, "intent": True}


class TestCollectGitMetadata:
    """Tests for collect_git_metadata function."""

    @jig.verifies("S-068")
    def test_collects_head_and_tree_hashes(self, tmp_path: Path):
        """Collects git_head, git_tree_hashes, git_dirty_files."""
        # Create git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)

        # Create source directory
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "module.py").write_text("x = 1")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        config = make_config(tmp_path)
        config.paths.source.mkdir(parents=True, exist_ok=True)

        result = collect_git_metadata(config, [src_dir])

        assert "git_head" in result
        assert result["git_head"] is not None
        assert len(result["git_head"]) == 40
        assert "git_tree_hashes" in result
        assert "git_dirty_files" in result
        assert isinstance(result["git_dirty_files"], list)

    @jig.verifies("S-068")
    def test_returns_null_for_non_git(self):
        """Returns null/empty values for non-git projects."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            src_dir = tmp_path / "src"
            src_dir.mkdir()
            config = make_config(tmp_path)

            result = collect_git_metadata(config, [src_dir])

            assert result["git_head"] is None
            assert result["git_tree_hashes"] == {}
            assert result["git_dirty_files"] == []


class TestStalenessPerformance:
    """Tests for staleness check performance."""

    @jig.verifies("S-069")
    @pytest.mark.timeout(1)  # Should complete in under 1 second
    def test_staleness_check_is_fast(self, tmp_path: Path):
        """Staleness check for all graphs completes quickly."""
        config = make_config(tmp_path)

        # Even with no graphs, should complete fast
        import time
        start = time.time()

        for _ in range(10):
            get_staleness_status(config)

        elapsed = time.time() - start

        # 10 iterations should complete in under 1 second
        # (well under the 100ms target per full check)
        assert elapsed < 1.0
