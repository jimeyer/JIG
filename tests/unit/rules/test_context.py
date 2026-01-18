# ABOUTME: Tests for ValidationContext and MendContext classes.
# ABOUTME: Verifies artifact loading, querying, and modification capabilities.
"""
Tests for rules/context.py context classes.

ValidationContext loads and queries artifacts.
MendContext batches and commits modifications.
"""

import tempfile
from pathlib import Path

import jig
from jig.rules.context import MendContext, ValidationContext


class TestValidationContext:
    """Tests for ValidationContext artifact loading and querying."""

    def test_loads_specifications(self):
        """ValidationContext loads specs from jig/specifications/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jig_dir = Path(tmpdir) / "jig"
            spec_dir = jig_dir / "specifications"
            spec_dir.mkdir(parents=True)

            (spec_dir / "S-001_Test.md").write_text(
                "---\nid: S-001\ntitle: Test\ntype: specification\n---\n# Test\n"
            )
            (spec_dir / "S-002_Another.md").write_text(
                "---\nid: S-002\ntitle: Another\ntype: specification\n---\n# Another\n"
            )

            ctx = ValidationContext(project_root=Path(tmpdir))
            assert len(ctx.specifications) == 2
            assert "S-001" in ctx.specifications
            assert "S-002" in ctx.specifications

    def test_loads_outcomes(self):
        """ValidationContext loads outcomes from jig/outcomes/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jig_dir = Path(tmpdir) / "jig"
            outcome_dir = jig_dir / "outcomes"
            outcome_dir.mkdir(parents=True)

            (outcome_dir / "O-001_Test.md").write_text(
                "---\nid: O-001\ntitle: Test\ntype: outcome\n---\n# Test\n"
            )

            ctx = ValidationContext(project_root=Path(tmpdir))
            assert len(ctx.outcomes) == 1
            assert "O-001" in ctx.outcomes

    def test_loads_architecture(self):
        """ValidationContext loads architecture docs from jig/architecture/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jig_dir = Path(tmpdir) / "jig"
            arch_dir = jig_dir / "architecture"
            arch_dir.mkdir(parents=True)

            (arch_dir / "A-001_Design.md").write_text(
                "---\nid: A-001\ntitle: Design\ntype: architecture\n---\n# Design\n"
            )

            ctx = ValidationContext(project_root=Path(tmpdir))
            assert len(ctx.architectures) == 1
            assert "A-001" in ctx.architectures

    def test_loads_charter(self):
        """ValidationContext loads Charter.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jig_dir = Path(tmpdir) / "jig"
            jig_dir.mkdir(parents=True)

            (jig_dir / "Charter.md").write_text(
                "---\nname: TestProject\nversion: 1.0\n---\n# Charter\n"
            )

            ctx = ValidationContext(project_root=Path(tmpdir))
            assert ctx.charter is not None
            assert ctx.charter.frontmatter["name"] == "TestProject"

    def test_loads_bricks(self):
        """ValidationContext loads bricks from jig/bricks.yaml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jig_dir = Path(tmpdir) / "jig"
            jig_dir.mkdir(parents=True)

            (jig_dir / "bricks.yaml").write_text(
                "bricks:\n  - id: B-test\n    name: Test\n    layer: 0\n    units:\n      - M-test\n"
            )

            ctx = ValidationContext(project_root=Path(tmpdir))
            assert len(ctx.bricks) == 1
            assert ctx.bricks[0]["id"] == "B-test"

    def test_get_artifact_by_id(self):
        """ValidationContext.get(id) returns artifact or None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jig_dir = Path(tmpdir) / "jig"
            spec_dir = jig_dir / "specifications"
            spec_dir.mkdir(parents=True)

            (spec_dir / "S-001_Test.md").write_text(
                "---\nid: S-001\ntitle: Test\ntype: specification\n---\n# Test\n"
            )

            ctx = ValidationContext(project_root=Path(tmpdir))
            artifact = ctx.get("S-001")
            assert artifact is not None
            assert artifact.id == "S-001"

            missing = ctx.get("S-999")
            assert missing is None

    def test_all_artifacts_property(self):
        """ValidationContext.all_artifacts returns all loaded artifacts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jig_dir = Path(tmpdir) / "jig"
            spec_dir = jig_dir / "specifications"
            outcome_dir = jig_dir / "outcomes"
            spec_dir.mkdir(parents=True)
            outcome_dir.mkdir(parents=True)

            (spec_dir / "S-001_Test.md").write_text(
                "---\nid: S-001\ntitle: Test\ntype: specification\n---\n# Test\n"
            )
            (outcome_dir / "O-001_Out.md").write_text(
                "---\nid: O-001\ntitle: Out\ntype: outcome\n---\n# Out\n"
            )

            ctx = ValidationContext(project_root=Path(tmpdir))
            all_arts = ctx.all_artifacts
            assert len(all_arts) == 2

    def test_handles_missing_directories(self):
        """ValidationContext handles missing jig directories gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # No jig/ directory at all
            ctx = ValidationContext(project_root=Path(tmpdir))
            assert len(ctx.specifications) == 0
            assert len(ctx.outcomes) == 0
            assert ctx.charter is None
            assert len(ctx.bricks) == 0

    def test_loads_goals(self):
        """ValidationContext loads goals from jig/goals/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jig_dir = Path(tmpdir) / "jig"
            goals_dir = jig_dir / "goals"
            goals_dir.mkdir(parents=True)

            (goals_dir / "G-001_Quality.md").write_text(
                "---\nid: G-001\ntitle: Quality\ntype: goal\n---\n# Quality\n"
            )

            ctx = ValidationContext(project_root=Path(tmpdir))
            assert len(ctx.goals) == 1
            assert "G-001" in ctx.goals


class TestMendContext:
    """Tests for MendContext batched modifications."""

    def test_set_field_batches_change(self):
        """MendContext.set_field batches a field change."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jig_dir = Path(tmpdir) / "jig"
            spec_dir = jig_dir / "specifications"
            spec_dir.mkdir(parents=True)

            spec_file = spec_dir / "S-001_Test.md"
            spec_file.write_text(
                "---\nid: S-001\ntitle: Test\ntype: specification\n---\n# Test\n"
            )

            ctx = MendContext(project_root=Path(tmpdir))
            ctx.set_field(str(spec_file), "outcomes", ["O-001"])

            # Change not applied yet (batched)
            content = spec_file.read_text()
            assert "outcomes" not in content

            # Pending changes should be tracked
            assert len(ctx.pending_changes) > 0

    def test_commit_applies_changes(self):
        """MendContext.commit() applies all batched changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jig_dir = Path(tmpdir) / "jig"
            spec_dir = jig_dir / "specifications"
            spec_dir.mkdir(parents=True)

            spec_file = spec_dir / "S-001_Test.md"
            spec_file.write_text(
                "---\nid: S-001\ntitle: Test\ntype: specification\n---\n# Test\n"
            )

            ctx = MendContext(project_root=Path(tmpdir))
            ctx.set_field(str(spec_file), "outcomes", ["O-001"])
            ctx.commit()

            # Now change should be applied
            content = spec_file.read_text()
            assert "outcomes" in content

    def test_add_field_value_appends_to_array(self):
        """MendContext.add_field_value appends to array field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jig_dir = Path(tmpdir) / "jig"
            spec_dir = jig_dir / "specifications"
            spec_dir.mkdir(parents=True)

            spec_file = spec_dir / "S-001_Test.md"
            spec_file.write_text(
                "---\nid: S-001\noutcomes:\n  - O-001\n---\n# Test\n"
            )

            ctx = MendContext(project_root=Path(tmpdir))
            ctx.add_field_value(str(spec_file), "outcomes", "O-002")
            ctx.commit()

            content = spec_file.read_text()
            assert "O-001" in content
            assert "O-002" in content

    def test_remove_field_value_removes_from_array(self):
        """MendContext.remove_field_value removes from array field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jig_dir = Path(tmpdir) / "jig"
            spec_dir = jig_dir / "specifications"
            spec_dir.mkdir(parents=True)

            spec_file = spec_dir / "S-001_Test.md"
            spec_file.write_text(
                "---\nid: S-001\noutcomes:\n  - O-001\n  - O-002\n---\n# Test\n"
            )

            ctx = MendContext(project_root=Path(tmpdir))
            ctx.remove_field_value(str(spec_file), "outcomes", "O-001")
            ctx.commit()

            content = spec_file.read_text()
            assert "O-001" not in content
            assert "O-002" in content

    def test_delete_field_removes_field(self):
        """MendContext.delete_field removes field entirely."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jig_dir = Path(tmpdir) / "jig"
            spec_dir = jig_dir / "specifications"
            spec_dir.mkdir(parents=True)

            spec_file = spec_dir / "S-001_Test.md"
            spec_file.write_text(
                "---\nid: S-001\nobsolete: true\n---\n# Test\n"
            )

            ctx = MendContext(project_root=Path(tmpdir))
            ctx.delete_field(str(spec_file), "obsolete")
            ctx.commit()

            content = spec_file.read_text()
            assert "obsolete" not in content
            assert "id: S-001" in content

    def test_rollback_discards_pending_changes(self):
        """MendContext.rollback() discards pending changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jig_dir = Path(tmpdir) / "jig"
            spec_dir = jig_dir / "specifications"
            spec_dir.mkdir(parents=True)

            spec_file = spec_dir / "S-001_Test.md"
            spec_file.write_text(
                "---\nid: S-001\n---\n# Test\n"
            )

            ctx = MendContext(project_root=Path(tmpdir))
            ctx.set_field(str(spec_file), "outcomes", ["O-001"])
            ctx.rollback()

            assert len(ctx.pending_changes) == 0

            # File should be unchanged
            content = spec_file.read_text()
            assert "outcomes" not in content

    def test_multiple_changes_to_same_file(self):
        """MendContext batches multiple changes to same file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jig_dir = Path(tmpdir) / "jig"
            spec_dir = jig_dir / "specifications"
            spec_dir.mkdir(parents=True)

            spec_file = spec_dir / "S-001_Test.md"
            spec_file.write_text(
                "---\nid: S-001\ntitle: Old\n---\n# Old\n"
            )

            ctx = MendContext(project_root=Path(tmpdir))
            ctx.set_field(str(spec_file), "title", "New Title")
            ctx.set_field(str(spec_file), "outcomes", ["O-001"])
            ctx.commit()

            content = spec_file.read_text()
            assert "New Title" in content
            assert "outcomes" in content
