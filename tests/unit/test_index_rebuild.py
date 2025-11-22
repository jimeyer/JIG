# @jig T-JIGY-024 verifies:S-JIGY-009 subsystem:jigy-tool
"""Unit tests for graph-index.yaml rebuild functionality."""

from datetime import datetime
from pathlib import Path
from textwrap import dedent

import pytest

from jig.core.index_builder import (
    IndexBuilder,
    RebuildResult,
    build_graph_index,
    detect_conflicts,
    merge_nodes,
)
from jig.utils.yaml_utils import load_yaml


class TestIndexBuilder:
    """Test IndexBuilder class."""

    def test_initialize_builder(self, tmp_path: Path) -> None:
        """Initialize index builder with project directory."""
        builder = IndexBuilder(tmp_path)
        
        assert builder.project_root == tmp_path
        assert builder.intent_dir == tmp_path / "jig"

    def test_discover_markdown_nodes(self, tmp_path: Path) -> None:
        """Discover O/S nodes from markdown files."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        specs_dir = jig_dir / "specifications"
        outcomes_dir.mkdir(parents=True)
        specs_dir.mkdir(parents=True)

        # Create outcome
        (outcomes_dir / "O-TEST-001.md").write_text(dedent("""
            ---
            id: O-TEST-001
            type: outcome
            title: Test outcome
            subsystem: test
            status: active
            ---
            
            # Test
        """))

        # Create specification
        (specs_dir / "S-TEST-001.md").write_text(dedent("""
            ---
            id: S-TEST-001
            type: specification
            title: Test spec
            subsystem: test
            status: active
            implements:
              - O-TEST-001
            ---
            
            # Spec
        """))

        builder = IndexBuilder(tmp_path)
        nodes = builder.discover_markdown_nodes()

        assert len(nodes) == 2
        ids = {n.id for n in nodes}
        assert ids == {"O-TEST-001", "S-TEST-001"}

    def test_discover_annotation_nodes(self, tmp_path: Path) -> None:
        """Discover C/T nodes from code annotations."""
        src_dir = tmp_path / "src"
        test_dir = tmp_path / "test"
        src_dir.mkdir()
        test_dir.mkdir()

        # Create code file with annotation
        (src_dir / "code.py").write_text(dedent("""
            # @jig C-TEST-001 implements:S-TEST-001 subsystem:test
            class TestClass:
                pass
        """))

        # Create test file with annotation
        (test_dir / "test_code.py").write_text(dedent("""
            # @jig T-TEST-001 verifies:S-TEST-001 subsystem:test
            def test_something():
                pass
        """))

        builder = IndexBuilder(tmp_path)
        nodes = builder.discover_annotation_nodes()

        assert len(nodes) == 2
        ids = {n.id for n in nodes}
        assert ids == {"C-TEST-001", "T-TEST-001"}

    def test_build_complete_registry(self, tmp_path: Path) -> None:
        """Build complete node registry from all sources."""
        # Setup markdown files
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)
        
        (outcomes_dir / "O-TEST-001.md").write_text(dedent("""
            ---
            id: O-TEST-001
            type: outcome
            title: Test outcome
            subsystem: test
            ---
            Content
        """))

        # Setup annotation files
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        
        (src_dir / "code.py").write_text("# @jig C-TEST-001 implements:O-TEST-001 subsystem:test")

        builder = IndexBuilder(tmp_path)
        result = builder.build()

        assert result.success
        assert len(result.nodes) == 2
        assert "O-TEST-001" in result.nodes
        assert "C-TEST-001" in result.nodes


class TestConflictDetection:
    """Test duplicate node ID detection."""

    def test_detect_no_conflicts(self, tmp_path: Path) -> None:
        """No conflicts when all IDs are unique."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)

        (outcomes_dir / "O-TEST-001.md").write_text(dedent("""
            ---
            id: O-TEST-001
            type: outcome
            title: First
            ---
        """))

        (outcomes_dir / "O-TEST-002.md").write_text(dedent("""
            ---
            id: O-TEST-002
            type: outcome
            title: Second
            ---
        """))

        builder = IndexBuilder(tmp_path)
        result = builder.build()

        assert result.success
        assert len(result.conflicts) == 0

    def test_detect_duplicate_in_markdown(self, tmp_path: Path) -> None:
        """Detect duplicate ID in multiple markdown files."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)

        (outcomes_dir / "O-TEST-001.md").write_text(dedent("""
            ---
            id: O-TEST-001
            type: outcome
            title: First
            ---
        """))

        (outcomes_dir / "O-TEST-001-copy.md").write_text(dedent("""
            ---
            id: O-TEST-001
            type: outcome
            title: Duplicate
            ---
        """))

        builder = IndexBuilder(tmp_path)
        result = builder.build()

        assert not result.success
        assert len(result.conflicts) > 0
        assert "O-TEST-001" in str(result.conflicts[0])

    def test_detect_duplicate_in_annotations(self, tmp_path: Path) -> None:
        """Detect duplicate ID in code annotations."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        (src_dir / "file1.py").write_text("# @jig C-TEST-001 implements:S-001 subsystem:test")
        (src_dir / "file2.py").write_text("# @jig C-TEST-001 implements:S-002 subsystem:test")

        builder = IndexBuilder(tmp_path)
        result = builder.build()

        assert not result.success
        assert len(result.conflicts) > 0

    def test_detect_cross_source_conflict(self, tmp_path: Path) -> None:
        """Detect conflict between markdown and annotation (type mismatch)."""
        # O-TEST-001 in markdown (outcome)
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)
        
        (outcomes_dir / "O-TEST-001.md").write_text(dedent("""
            ---
            id: O-TEST-001
            type: outcome
            title: Test
            ---
        """))

        # O-TEST-001 in annotation (code) - WRONG! O prefix should be outcome
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "code.py").write_text("# @jig O-TEST-001 implements:S-001 subsystem:test")

        builder = IndexBuilder(tmp_path)
        result = builder.build()

        # Should detect conflict or type mismatch
        assert not result.success or len(result.warnings) > 0


class TestYAMLGeneration:
    """Test graph-index.yaml generation."""

    def test_generate_yaml_format(self, tmp_path: Path) -> None:
        """Generate node-centric YAML format."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        specs_dir = jig_dir / "specifications"
        outcomes_dir.mkdir(parents=True)
        specs_dir.mkdir(parents=True)

        (outcomes_dir / "O-TEST-001.md").write_text(dedent("""
            ---
            id: O-TEST-001
            type: outcome
            title: Test outcome
            subsystem: test
            status: active
            ---
        """))

        (specs_dir / "S-TEST-001.md").write_text(dedent("""
            ---
            id: S-TEST-001
            type: specification
            title: Test spec
            subsystem: test
            status: active
            implements:
              - O-TEST-001
            ---
        """))

        builder = IndexBuilder(tmp_path)
        result = builder.build()
        
        assert result.success
        
        # Write to file
        output_file = tmp_path / "graph-index.yaml"
        builder.write_yaml(result, output_file)

        assert output_file.exists()
        
        # Load and verify structure
        data = load_yaml(output_file)
        assert "nodes" in data
        assert len(data["nodes"]) == 2
        
        # Find S node and verify relationships
        s_node = next(n for n in data["nodes"] if n["id"] == "S-TEST-001")
        assert "implements" in s_node
        assert s_node["implements"] == ["O-TEST-001"]

    def test_yaml_includes_metadata(self, tmp_path: Path) -> None:
        """Generated YAML includes version and timestamp."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)

        (outcomes_dir / "O-TEST-001.md").write_text(dedent("""
            ---
            id: O-TEST-001
            type: outcome
            title: Test
            ---
        """))

        builder = IndexBuilder(tmp_path)
        result = builder.build()
        
        output_file = tmp_path / "graph-index.yaml"
        builder.write_yaml(result, output_file)

        data = load_yaml(output_file)
        assert "version" in data
        assert "generated" in data

    def test_yaml_includes_code_node_line_numbers(self, tmp_path: Path) -> None:
        """C/T nodes include file path and line number."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        (src_dir / "code.py").write_text(dedent("""
            # Some comment
            # @jig C-TEST-001 implements:S-001 subsystem:test
            class TestClass:
                pass
        """))

        builder = IndexBuilder(tmp_path)
        result = builder.build()
        
        output_file = tmp_path / "graph-index.yaml"
        builder.write_yaml(result, output_file)

        data = load_yaml(output_file)
        c_node = next(n for n in data["nodes"] if n["id"] == "C-TEST-001")
        
        assert "file" in c_node
        assert "line" in c_node
        assert c_node["line"] == 3  # Second line (annotation line)


class TestBackupStrategy:
    """Test backup of existing graph-index.yaml."""

    def test_backup_existing_file(self, tmp_path: Path) -> None:
        """Backup existing graph-index.yaml before overwriting."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)

        # Create existing graph-index.yaml
        existing_file = jig_dir / "graph-index.yaml"
        existing_file.write_text("nodes: []\n")

        # Create outcome for rebuild
        (outcomes_dir / "O-TEST-001.md").write_text(dedent("""
            ---
            id: O-TEST-001
            type: outcome
            title: Test
            ---
        """))

        builder = IndexBuilder(tmp_path)
        result = builder.build()
        builder.write_yaml(result, existing_file, backup=True)

        # Verify backup exists
        backup_file = jig_dir / "graph-index.yaml.bak"
        assert backup_file.exists()
        assert backup_file.read_text() == "nodes: []\n"

    def test_no_backup_when_disabled(self, tmp_path: Path) -> None:
        """Don't create backup when backup=False."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)

        existing_file = jig_dir / "graph-index.yaml"
        existing_file.write_text("nodes: []\n")

        (outcomes_dir / "O-TEST-001.md").write_text(dedent("""
            ---
            id: O-TEST-001
            type: outcome
            title: Test
            ---
        """))

        builder = IndexBuilder(tmp_path)
        result = builder.build()
        builder.write_yaml(result, existing_file, backup=False)

        backup_file = jig_dir / "graph-index.yaml.bak"
        assert not backup_file.exists()


class TestIdempotence:
    """Test rebuild idempotence."""

    def test_rebuild_twice_produces_same_output(self, tmp_path: Path) -> None:
        """Rebuilding twice with no changes produces identical output."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)

        (outcomes_dir / "O-TEST-001.md").write_text(dedent("""
            ---
            id: O-TEST-001
            type: outcome
            title: Test outcome
            subsystem: test
            status: active
            ---
        """))

        # First rebuild
        builder1 = IndexBuilder(tmp_path)
        result1 = builder1.build()
        output_file = jig_dir / "graph-index.yaml"
        builder1.write_yaml(result1, output_file)
        content1 = output_file.read_text()

        # Second rebuild
        builder2 = IndexBuilder(tmp_path)
        result2 = builder2.build()
        builder2.write_yaml(result2, output_file)
        content2 = output_file.read_text()

        # Compare (excluding timestamp which may differ)
        lines1 = [line for line in content1.split('\n') if not line.startswith('generated:')]
        lines2 = [line for line in content2.split('\n') if not line.startswith('generated:')]
        
        assert lines1 == lines2


class TestValidationBeforeWrite:
    """Test validation before writing YAML."""

    def test_validate_node_ids(self, tmp_path: Path) -> None:
        """Validate all node IDs match expected format."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)

        # Valid ID
        (outcomes_dir / "O-TEST-001.md").write_text(dedent("""
            ---
            id: O-TEST-001
            type: outcome
            title: Valid
            ---
        """))

        builder = IndexBuilder(tmp_path)
        result = builder.build()

        assert result.success
        assert len(result.validation_errors) == 0

    def test_validate_edge_targets_exist(self, tmp_path: Path) -> None:
        """Validate all relationship targets exist."""
        jig_dir = tmp_path / "jig"
        specs_dir = jig_dir / "specifications"
        specs_dir.mkdir(parents=True)

        # Spec references non-existent outcome
        (specs_dir / "S-TEST-001.md").write_text(dedent("""
            ---
            id: S-TEST-001
            type: specification
            title: Spec
            implements:
              - O-MISSING-001
            ---
        """))

        builder = IndexBuilder(tmp_path)
        result = builder.build()

        # Should detect broken reference
        assert not result.success or len(result.warnings) > 0


class TestRebuildResult:
    """Test RebuildResult dataclass."""

    def test_rebuild_result_success(self) -> None:
        """Create successful rebuild result."""
        result = RebuildResult(
            success=True,
            nodes={"O-001": None, "S-001": None},  # type: ignore
            conflicts=[],
            warnings=[],
            validation_errors=[],
        )

        assert result.success
        assert len(result.nodes) == 2
        assert len(result.conflicts) == 0

    def test_rebuild_result_with_conflicts(self) -> None:
        """Create rebuild result with conflicts."""
        result = RebuildResult(
            success=False,
            nodes={},
            conflicts=["Duplicate ID: C-TEST-001"],
            warnings=[],
            validation_errors=[],
        )

        assert not result.success
        assert len(result.conflicts) == 1


class TestHelperFunctions:
    """Test module-level helper functions."""

    def test_build_graph_index_function(self, tmp_path: Path) -> None:
        """Test build_graph_index convenience function."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)

        (outcomes_dir / "O-TEST-001.md").write_text(dedent("""
            ---
            id: O-TEST-001
            type: outcome
            title: Test
            ---
        """))

        result = build_graph_index(tmp_path)

        assert result.success
        assert len(result.nodes) == 1

    def test_detect_conflicts_function(self) -> None:
        """Test detect_conflicts helper function."""
        from jig.core.parser import OSTCNode
        
        nodes = [
            OSTCNode(id="O-001", type="outcome", title="First"),
            OSTCNode(id="O-001", type="outcome", title="Duplicate"),
            OSTCNode(id="O-002", type="outcome", title="Unique"),
        ]

        conflicts = detect_conflicts(nodes)

        assert len(conflicts) > 0
        assert any("O-001" in str(c) for c in conflicts)

    def test_merge_nodes_deduplicates(self) -> None:
        """Test merge_nodes handles duplicates."""
        from jig.core.parser import OSTCNode
        
        nodes = [
            OSTCNode(id="O-001", type="outcome", title="First"),
            OSTCNode(id="O-001", type="outcome", title="Duplicate"),
        ]

        merged, conflicts = merge_nodes(nodes)

        # Should keep one and report conflict
        assert len(merged) == 1
        assert len(conflicts) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_rebuild_empty_project(self, tmp_path: Path) -> None:
        """Rebuild with no markdown or annotations."""
        jig_dir = tmp_path / "jig"
        jig_dir.mkdir()

        builder = IndexBuilder(tmp_path)
        result = builder.build()

        assert result.success  # Empty is valid
        assert len(result.nodes) == 0

    def test_rebuild_missing_jig_directory(self, tmp_path: Path) -> None:
        """Handle missing jig/ directory gracefully."""
        builder = IndexBuilder(tmp_path)
        result = builder.build()

        # Should not crash, just return empty result
        assert len(result.nodes) == 0

    def test_rebuild_with_malformed_markdown(self, tmp_path: Path) -> None:
        """Handle malformed markdown files."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)

        # Missing required fields
        (outcomes_dir / "O-BAD-001.md").write_text(dedent("""
            ---
            title: Missing ID field
            ---
        """))

        builder = IndexBuilder(tmp_path)
        result = builder.build()

        # Should continue despite error, report in warnings/errors
        assert len(result.warnings) > 0 or len(result.validation_errors) > 0

    def test_rebuild_with_missing_source_files(self, tmp_path: Path) -> None:
        """Handle missing src/ or test/ directories."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)

        (outcomes_dir / "O-TEST-001.md").write_text(dedent("""
            ---
            id: O-TEST-001
            type: outcome
            title: Test
            ---
        """))

        # No src/ or test/ directories exist
        builder = IndexBuilder(tmp_path)
        result = builder.build()

        # Should succeed with just markdown nodes
        assert result.success
        assert len(result.nodes) == 1


# @jig T-JIGY-032 verifies:S-JIGY-011 subsystem:jigy-tool
class TestStatusBasedFiltering:
    """Test Tier 2: Status-based filtering to exclude template/deprecated nodes."""

    def test_excludes_template_status(self, tmp_path: Path) -> None:
        """Test that nodes with status: template are excluded."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)

        # Create template outcome
        (outcomes_dir / "O-TEMPLATE-001.md").write_text(dedent("""
            ---
            id: O-TEMPLATE-001
            type: outcome
            title: Template Outcome
            subsystem: test
            status: template
            ---

            # Template
        """))

        # Create active outcome
        (outcomes_dir / "O-REAL-001.md").write_text(dedent("""
            ---
            id: O-REAL-001
            type: outcome
            title: Real Outcome
            subsystem: test
            status: active
            ---

            # Real
        """))

        builder = IndexBuilder(tmp_path)
        nodes = builder.discover_markdown_nodes()

        # Should only discover the active node
        assert len(nodes) == 1
        assert nodes[0].id == "O-REAL-001"

    def test_excludes_deprecated_status(self, tmp_path: Path) -> None:
        """Test that nodes with status: deprecated are excluded."""
        jig_dir = tmp_path / "jig"
        specs_dir = jig_dir / "specifications"
        specs_dir.mkdir(parents=True)

        # Create deprecated spec
        (specs_dir / "S-OLD-001.md").write_text(dedent("""
            ---
            id: S-OLD-001
            type: specification
            title: Old Spec
            subsystem: test
            status: deprecated
            ---

            # Deprecated
        """))

        # Create active spec
        (specs_dir / "S-NEW-001.md").write_text(dedent("""
            ---
            id: S-NEW-001
            type: specification
            title: New Spec
            subsystem: test
            status: active
            ---

            # Active
        """))

        builder = IndexBuilder(tmp_path)
        nodes = builder.discover_markdown_nodes()

        # Should only discover the active node
        assert len(nodes) == 1
        assert nodes[0].id == "S-NEW-001"

    def test_excludes_draft_status(self, tmp_path: Path) -> None:
        """Test that nodes with status: draft are excluded."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)

        # Create draft outcome
        (outcomes_dir / "O-DRAFT-001.md").write_text(dedent("""
            ---
            id: O-DRAFT-001
            type: outcome
            title: Draft Outcome
            subsystem: test
            status: draft
            ---

            # Draft
        """))

        # Create active outcome
        (outcomes_dir / "O-ACTIVE-001.md").write_text(dedent("""
            ---
            id: O-ACTIVE-001
            type: outcome
            title: Active Outcome
            subsystem: test
            status: active
            ---

            # Active
        """))

        builder = IndexBuilder(tmp_path)
        nodes = builder.discover_markdown_nodes()

        # Should only discover the active node
        assert len(nodes) == 1
        assert nodes[0].id == "O-ACTIVE-001"

    def test_includes_planned_status(self, tmp_path: Path) -> None:
        """Test that nodes with status: planned are included."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)

        # Create planned outcome
        (outcomes_dir / "O-PLANNED-001.md").write_text(dedent("""
            ---
            id: O-PLANNED-001
            type: outcome
            title: Planned Outcome
            subsystem: test
            status: planned
            ---

            # Planned
        """))

        builder = IndexBuilder(tmp_path)
        nodes = builder.discover_markdown_nodes()

        # Should discover the planned node
        assert len(nodes) == 1
        assert nodes[0].id == "O-PLANNED-001"

    def test_includes_missing_status_defaults_to_active(self, tmp_path: Path) -> None:
        """Test that nodes with missing status field are included (default: active)."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)

        # Create outcome without status field
        (outcomes_dir / "O-NO-STATUS-001.md").write_text(dedent("""
            ---
            id: O-NO-STATUS-001
            type: outcome
            title: No Status Outcome
            subsystem: test
            ---

            # No status field
        """))

        builder = IndexBuilder(tmp_path)
        nodes = builder.discover_markdown_nodes()

        # Should discover the node (defaults to active)
        assert len(nodes) == 1
        assert nodes[0].id == "O-NO-STATUS-001"

    def test_mixed_statuses(self, tmp_path: Path) -> None:
        """Test filtering with mixed statuses."""
        jig_dir = tmp_path / "jig"
        outcomes_dir = jig_dir / "outcomes"
        outcomes_dir.mkdir(parents=True)

        # Create nodes with various statuses
        (outcomes_dir / "O-TEMPLATE-001.md").write_text(dedent("""
            ---
            id: O-TEMPLATE-001
            type: outcome
            title: Template
            status: template
            ---
        """))

        (outcomes_dir / "O-DEPRECATED-001.md").write_text(dedent("""
            ---
            id: O-DEPRECATED-001
            type: outcome
            title: Deprecated
            status: deprecated
            ---
        """))

        (outcomes_dir / "O-DRAFT-001.md").write_text(dedent("""
            ---
            id: O-DRAFT-001
            type: outcome
            title: Draft
            status: draft
            ---
        """))

        (outcomes_dir / "O-ACTIVE-001.md").write_text(dedent("""
            ---
            id: O-ACTIVE-001
            type: outcome
            title: Active
            status: active
            ---
        """))

        (outcomes_dir / "O-PLANNED-001.md").write_text(dedent("""
            ---
            id: O-PLANNED-001
            type: outcome
            title: Planned
            status: planned
            ---
        """))

        builder = IndexBuilder(tmp_path)
        nodes = builder.discover_markdown_nodes()

        # Should only discover active and planned nodes
        assert len(nodes) == 2
        node_ids = {node.id for node in nodes}
        assert node_ids == {"O-ACTIVE-001", "O-PLANNED-001"}

