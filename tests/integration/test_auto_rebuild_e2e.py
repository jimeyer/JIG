"""End-to-end integration tests for auto-rebuild with staleness detection.

Verifies that the SCOPE problem is solved:
- Commands operate on current data without manual rebuild
- When nothing changed, staleness check is fast
- When graphs stale, only affected graphs rebuild
- --no-rebuild flag provides escape hatch
"""

import json
import subprocess
import tempfile
import time
from pathlib import Path

import pytest

import jig
from jig.config import JigConfig, PathsConfig
from jig.staleness import collect_git_metadata, get_staleness_status, is_stale


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
        charter=tmp_path / "jig" / "Charter.md",
        architecture=tmp_path / "jig" / "architecture",
    )
    return JigConfig(
        paths=paths,
        project_root=tmp_path,
        config_file_path=None,
        has_config_file=False,
    )


def setup_git_project(tmp_path: Path) -> JigConfig:
    """Create a minimal git project with JIG structure."""
    # Initialize git
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=tmp_path,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=tmp_path,
        capture_output=True,
    )

    # Create config
    config = make_config(tmp_path)

    # Create source structure
    config.paths.source.mkdir(parents=True)
    (config.paths.source / "module.py").write_text("def foo(): pass\n")

    # Create test structure
    config.paths.tests.mkdir(parents=True)
    (config.paths.tests / "test_module.py").write_text("def test_foo(): pass\n")

    # Create intent structure
    config.paths.specifications.mkdir(parents=True)
    config.paths.outcomes.mkdir(parents=True)
    config.paths.generated.mkdir(parents=True)
    (config.paths.specifications / "S-001.md").write_text(
        "---\nid: S-001\ntype: specification\n---\n\n# Test Spec\n"
    )
    config.paths.bricks.write_text("bricks: []\n")

    # Initial commit
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )

    return config


def build_all_graphs(config: JigConfig) -> None:
    """Build all three graphs for the test project."""
    from jig.impl_graph.builder import build_graph
    from jig.intent_graph.generator import generate_intent_graph
    from jig.staleness import collect_git_metadata
    from jig.verification_graph.builder import build_verification_graph

    # Build impl
    impl_git = collect_git_metadata(config, [config.paths.source])
    build_graph(
        project_root=config.project_root,
        source_dir=config.paths.source,
        output_path=config.paths.generated / "implementation-graph.ndjson",
        git_metadata=impl_git,
    )

    # Build verify
    verify_git = collect_git_metadata(config, [config.paths.tests])
    build_verification_graph(
        project_root=config.project_root,
        test_dir=config.paths.tests,
        output_path=config.paths.generated / "verification-graph.ndjson",
        git_metadata=verify_git,
    )

    # Build intent
    intent_git = collect_git_metadata(config, [
        config.paths.specifications,
        config.paths.outcomes,
        config.paths.bricks.parent,
    ])
    generate_intent_graph(
        project_root=config.project_root,
        output_path=config.paths.generated / "intent-graph.ndjson",
        git_metadata=intent_git,
    )


class TestFreshProject:
    """Tests for fresh projects with no graphs."""

    @jig.verifies("S-069", "S-070")
    def test_all_graphs_stale_when_missing(self, tmp_path: Path):
        """Fresh project (no graphs) - all graphs stale."""
        config = setup_git_project(tmp_path)

        status = get_staleness_status(config)

        assert status["impl"] is True
        assert status["verify"] is True
        assert status["intent"] is True


class TestNothingChanged:
    """Tests for when nothing has changed."""

    @jig.verifies("S-069", "S-070")
    def test_all_graphs_current_after_rebuild(self, tmp_path: Path):
        """Nothing changed - all graphs current after rebuild."""
        config = setup_git_project(tmp_path)
        build_all_graphs(config)

        status = get_staleness_status(config)

        assert status["impl"] is False
        assert status["verify"] is False
        assert status["intent"] is False

    @jig.verifies("S-069")
    def test_staleness_check_is_fast(self, tmp_path: Path):
        """Staleness check for all graphs completes in <200ms."""
        config = setup_git_project(tmp_path)
        build_all_graphs(config)

        # Warm up (first call may be slower due to imports)
        get_staleness_status(config)

        # Measure 10 iterations
        start = time.time()
        for _ in range(10):
            get_staleness_status(config)
        elapsed = time.time() - start

        # 10 iterations should complete in <2 seconds
        # (well under the 200ms per check target)
        assert elapsed < 2.0, f"10 staleness checks took {elapsed:.2f}s"


class TestSourceChanged:
    """Tests for when source files change."""

    @jig.verifies("S-069", "S-070")
    def test_impl_stale_after_source_modified(self, tmp_path: Path):
        """Source changed - impl graph stale, others current."""
        config = setup_git_project(tmp_path)
        build_all_graphs(config)

        # Modify source file (creates dirty state)
        (config.paths.source / "module.py").write_text("def foo(): return 1\n")

        status = get_staleness_status(config)

        assert status["impl"] is True  # Source changed
        assert status["verify"] is False  # Tests unchanged
        assert status["intent"] is False  # Intent unchanged


class TestTestChanged:
    """Tests for when test files change."""

    @jig.verifies("S-069", "S-070")
    def test_verify_stale_after_test_modified(self, tmp_path: Path):
        """Test changed - verify graph stale, others current."""
        config = setup_git_project(tmp_path)
        build_all_graphs(config)

        # Modify test file
        (config.paths.tests / "test_module.py").write_text("def test_bar(): pass\n")

        status = get_staleness_status(config)

        assert status["impl"] is False  # Source unchanged
        assert status["verify"] is True  # Tests changed
        assert status["intent"] is False  # Intent unchanged


class TestSpecChanged:
    """Tests for when spec files change."""

    @jig.verifies("S-069", "S-070")
    def test_intent_stale_after_spec_modified(self, tmp_path: Path):
        """Spec changed - intent graph stale, others current."""
        config = setup_git_project(tmp_path)
        build_all_graphs(config)

        # Modify spec file
        (config.paths.specifications / "S-001.md").write_text(
            "---\nid: S-001\ntype: specification\n---\n\n# Updated Spec\n"
        )

        status = get_staleness_status(config)

        assert status["impl"] is False  # Source unchanged
        assert status["verify"] is False  # Tests unchanged
        assert status["intent"] is True  # Specs changed


class TestNewUncommittedFile:
    """Tests for new uncommitted files."""

    @jig.verifies("S-069")
    def test_detects_new_source_file(self, tmp_path: Path):
        """New uncommitted source file - impl stale."""
        config = setup_git_project(tmp_path)
        build_all_graphs(config)

        # Add new source file
        (config.paths.source / "new_module.py").write_text("def bar(): pass\n")

        status = get_staleness_status(config)

        assert status["impl"] is True  # New file in source


class TestNoRebuildFlag:
    """Tests for --no-rebuild flag behavior."""

    @jig.verifies("S-071")
    def test_skip_rebuild_prevents_staleness_check(self, tmp_path: Path):
        """--no-rebuild skips staleness check entirely."""
        config = setup_git_project(tmp_path)
        # Don't build graphs - they would be stale

        from jig.cli.auto_rebuild import ensure_graphs_current

        # With skip_rebuild=True, should not attempt to rebuild
        # even though graphs don't exist
        ensure_graphs_current(
            ["impl", "verify", "intent"],
            config,
            skip_rebuild=True,
        )

        # Graphs still don't exist - that's expected
        assert not (config.paths.generated / "implementation-graph.ndjson").exists()


class TestNonGitProject:
    """Tests for non-git projects."""

    @jig.verifies("S-069")
    def test_always_stale_in_non_git(self):
        """Non-git project - always returns stale (graceful degradation)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            config = make_config(tmp_path)

            # Create minimal structure but no git
            config.paths.source.mkdir(parents=True)
            config.paths.generated.mkdir(parents=True)
            (config.paths.source / "module.py").write_text("def foo(): pass\n")

            # Should always be stale (cannot detect changes)
            assert is_stale("impl", config) is True


class TestGraphMetadataPresence:
    """Tests that graphs contain required metadata."""

    @jig.verifies("S-068")
    def test_impl_graph_has_git_metadata(self, tmp_path: Path):
        """Implementation graph contains git metadata in _meta."""
        config = setup_git_project(tmp_path)
        build_all_graphs(config)

        graph_path = config.paths.generated / "implementation-graph.ndjson"
        with graph_path.open() as f:
            first_line = f.readline()
            data = json.loads(first_line)

        meta = data.get("_meta", {})
        assert "git_head" in meta
        assert meta["git_head"] is not None
        assert len(meta["git_head"]) == 40
        assert "git_tree_hashes" in meta
        assert "git_dirty_files" in meta

    @jig.verifies("S-068")
    def test_verify_graph_has_git_metadata(self, tmp_path: Path):
        """Verification graph contains git metadata in _meta."""
        config = setup_git_project(tmp_path)
        build_all_graphs(config)

        graph_path = config.paths.generated / "verification-graph.ndjson"
        with graph_path.open() as f:
            first_line = f.readline()
            data = json.loads(first_line)

        meta = data.get("_meta", {})
        assert "git_head" in meta
        assert "git_tree_hashes" in meta
        assert "git_dirty_files" in meta

    @jig.verifies("S-068")
    def test_intent_graph_has_git_metadata(self, tmp_path: Path):
        """Intent graph contains git metadata in _meta."""
        config = setup_git_project(tmp_path)
        build_all_graphs(config)

        graph_path = config.paths.generated / "intent-graph.ndjson"
        with graph_path.open() as f:
            first_line = f.readline()
            data = json.loads(first_line)

        meta = data.get("_meta", {})
        assert "git_head" in meta
        assert "git_tree_hashes" in meta
        assert "git_dirty_files" in meta
