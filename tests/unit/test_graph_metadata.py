"""Tests for graph metadata with git staleness fields.

Verifies that generated graphs include git state metadata in _meta blocks.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest

import jig
from jig.config import JigConfig, PathsConfig
from jig.impl_graph.builder import build_graph
from jig.impl_graph.graph import Graph
from jig.impl_graph.ndjson_writer import NDJSONWriter, write_ndjson
from jig.intent_graph.generator import generate_intent_graph
from jig.staleness import collect_git_metadata
from jig.verification_graph.builder import build_verification_graph


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


def read_graph_metadata(graph_path: Path) -> Dict[str, Any]:
    """Read metadata from a graph file."""
    with graph_path.open() as f:
        first_line = f.readline()
        data = json.loads(first_line)
        return data.get("_meta", {})


class TestNDJSONWriterMetadata:
    """Tests for NDJSONWriter git metadata."""

    @jig.verifies("S-068")
    def test_includes_git_metadata_when_provided(self, tmp_path: Path):
        """Git metadata included in _meta when provided."""
        graph = Graph()
        git_metadata = {
            "git_head": "abc123def456789",
            "git_tree_hashes": {"src": "tree123"},
            "git_dirty_files": [],
        }

        writer = NDJSONWriter(graph, git_metadata=git_metadata)
        output_path = tmp_path / "graph.ndjson"
        writer.write(output_path)

        metadata = read_graph_metadata(output_path)

        assert metadata.get("git_head") == "abc123def456789"
        assert metadata.get("git_tree_hashes") == {"src": "tree123"}
        assert metadata.get("git_dirty_files") == []

    @jig.verifies("S-068")
    def test_no_git_metadata_when_not_provided(self, tmp_path: Path):
        """No git metadata fields when not provided."""
        graph = Graph()

        writer = NDJSONWriter(graph)
        output_path = tmp_path / "graph.ndjson"
        writer.write(output_path)

        metadata = read_graph_metadata(output_path)

        assert "git_head" not in metadata
        assert "git_tree_hashes" not in metadata
        assert "git_dirty_files" not in metadata


class TestWriteNdjsonMetadata:
    """Tests for write_ndjson git metadata."""

    @jig.verifies("S-068")
    def test_passes_git_metadata_through(self, tmp_path: Path):
        """Git metadata passed through to writer."""
        graph = Graph()
        git_metadata = {
            "git_head": "def456abc123",
            "git_tree_hashes": {"tests": "tree456"},
            "git_dirty_files": ["tests/test_foo.py"],
        }

        output_path = tmp_path / "graph.ndjson"
        write_ndjson(graph, output_path, git_metadata=git_metadata)

        metadata = read_graph_metadata(output_path)

        assert metadata.get("git_head") == "def456abc123"
        assert metadata.get("git_dirty_files") == ["tests/test_foo.py"]


class TestBuildGraphMetadata:
    """Tests for build_graph git metadata."""

    @jig.verifies("S-068")
    def test_includes_git_metadata_in_impl_graph(self, tmp_path: Path):
        """Implementation graph includes git metadata when provided."""
        # Create minimal source structure
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "module.py").write_text("def foo(): pass")

        output_path = tmp_path / "impl-graph.ndjson"
        git_metadata = {
            "git_head": "impl123",
            "git_tree_hashes": {"src": "impltree"},
            "git_dirty_files": [],
        }

        build_graph(
            project_root=tmp_path,
            source_dir=src_dir,
            output_path=output_path,
            git_metadata=git_metadata,
        )

        metadata = read_graph_metadata(output_path)

        assert metadata.get("git_head") == "impl123"
        assert metadata.get("git_tree_hashes") == {"src": "impltree"}


class TestVerificationGraphMetadata:
    """Tests for verification graph git metadata."""

    @jig.verifies("S-068")
    def test_includes_git_metadata_in_verify_graph(self, tmp_path: Path):
        """Verification graph includes git metadata when provided."""
        # Create minimal test structure
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_module.py").write_text("def test_foo(): pass")

        output_path = tmp_path / "verify-graph.ndjson"
        git_metadata = {
            "git_head": "verify456",
            "git_tree_hashes": {"tests": "verifytree"},
            "git_dirty_files": ["tests/test_new.py"],
        }

        build_verification_graph(
            project_root=tmp_path,
            test_dir=tests_dir,
            output_path=output_path,
            git_metadata=git_metadata,
        )

        metadata = read_graph_metadata(output_path)

        assert metadata.get("git_head") == "verify456"
        assert metadata.get("git_dirty_files") == ["tests/test_new.py"]


class TestIntentGraphMetadata:
    """Tests for intent graph git metadata."""

    @jig.verifies("S-068")
    def test_includes_git_metadata_in_intent_graph(self, tmp_path: Path):
        """Intent graph includes git metadata when provided."""
        # Create minimal intent structure
        jig_dir = tmp_path / "jig"
        jig_dir.mkdir()
        (jig_dir / "specifications").mkdir()
        (jig_dir / "outcomes").mkdir()
        (jig_dir / "bricks.yaml").write_text("bricks: []")
        (jig_dir / "specifications" / "S-001.md").write_text(
            "---\nid: S-001\ntype: specification\n---\n\n# Test Spec"
        )

        output_path = tmp_path / "intent-graph.ndjson"
        git_metadata = {
            "git_head": "intent789",
            "git_tree_hashes": {"jig/specifications": "intenttree"},
            "git_dirty_files": [],
        }

        generate_intent_graph(
            project_root=tmp_path,
            output_path=output_path,
            git_metadata=git_metadata,
        )

        metadata = read_graph_metadata(output_path)

        assert metadata.get("git_head") == "intent789"
        assert "git_tree_hashes" in metadata


class TestNonGitProjectMetadata:
    """Tests for non-git project metadata."""

    @jig.verifies("S-068")
    def test_null_metadata_for_non_git_project(self):
        """Non-git projects have null/empty git metadata."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            config = make_config(tmp_path)
            config.paths.source.mkdir(parents=True)

            git_metadata = collect_git_metadata(config, [config.paths.source])

            assert git_metadata["git_head"] is None
            assert git_metadata["git_tree_hashes"] == {}
            assert git_metadata["git_dirty_files"] == []


class TestRealGitRepoMetadata:
    """Tests with real git repositories."""

    @jig.verifies("S-068")
    def test_real_git_metadata_in_graph(self, tmp_path: Path):
        """Git metadata from real repo included in graph."""
        # Create a git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
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

        # Create source structure
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "module.py").write_text("def foo(): pass")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=tmp_path,
            capture_output=True,
        )

        config = make_config(tmp_path)
        git_metadata = collect_git_metadata(config, [src_dir])

        output_path = tmp_path / "impl-graph.ndjson"
        build_graph(
            project_root=tmp_path,
            source_dir=src_dir,
            output_path=output_path,
            git_metadata=git_metadata,
        )

        metadata = read_graph_metadata(output_path)

        # Should have a real 40-char SHA
        assert metadata.get("git_head") is not None
        assert len(metadata["git_head"]) == 40
        assert "git_tree_hashes" in metadata
        assert "git_dirty_files" in metadata
        assert metadata["git_dirty_files"] == []
