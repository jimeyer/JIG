# ABOUTME: Tests for mend action functions.
# ABOUTME: Verifies each fix action primitive works correctly.
"""
Tests for mend/actions.py fix action implementations.

Each action function takes a file path and parameters, and modifies
the file to apply the fix.
"""

import shutil
import tempfile
from pathlib import Path

import jig
from jig.mend.actions import (
    apply_set_field,
    apply_add_field_value,
    apply_remove_field_value,
    apply_delete_field,
    apply_rename_file,
    apply_sync_title,
    apply_set_h1,
)


@jig.verifies("S-105", "S-106")
class TestApplySetField:
    """Tests for apply_set_field action."""

    def test_sets_field_value(self):
        """apply_set_field sets a frontmatter field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text(
                "---\nid: S-001\ntitle: Old\n---\n# Test\n"
            )

            apply_set_field(file_path, "title", "New")

            content = file_path.read_text()
            assert "title: New" in content

    def test_adds_new_field(self):
        """apply_set_field adds field if not present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text("---\nid: S-001\n---\n# Test\n")

            apply_set_field(file_path, "outcomes", ["O-001"])

            content = file_path.read_text()
            assert "outcomes:" in content
            assert "O-001" in content

    def test_preserves_body(self):
        """apply_set_field preserves body content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            body = "\n# Test\n\nBody content with **markdown**.\n"
            file_path.write_text(f"---\nid: S-001\n---{body}")

            apply_set_field(file_path, "title", "New Title")

            content = file_path.read_text()
            assert body in content


@jig.verifies("S-105", "S-106")
class TestApplyAddFieldValue:
    """Tests for apply_add_field_value action."""

    def test_appends_to_existing_array(self):
        """apply_add_field_value appends to existing array."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text(
                "---\nid: S-001\noutcomes:\n  - O-001\n---\n# Test\n"
            )

            apply_add_field_value(file_path, "outcomes", "O-002")

            content = file_path.read_text()
            assert "O-001" in content
            assert "O-002" in content

    def test_creates_array_if_missing(self):
        """apply_add_field_value creates array if field missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text("---\nid: S-001\n---\n# Test\n")

            apply_add_field_value(file_path, "outcomes", "O-001")

            content = file_path.read_text()
            assert "outcomes:" in content
            assert "O-001" in content


@jig.verifies("S-105", "S-106")
class TestApplyRemoveFieldValue:
    """Tests for apply_remove_field_value action."""

    def test_removes_value_from_array(self):
        """apply_remove_field_value removes value from array."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text(
                "---\nid: S-001\noutcomes:\n  - O-001\n  - O-002\n---\n# Test\n"
            )

            apply_remove_field_value(file_path, "outcomes", "O-001")

            content = file_path.read_text()
            assert "O-001" not in content
            assert "O-002" in content

    def test_noop_if_value_not_present(self):
        """apply_remove_field_value is no-op if value not in array."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text(
                "---\nid: S-001\noutcomes:\n  - O-001\n---\n# Test\n"
            )

            apply_remove_field_value(file_path, "outcomes", "O-999")

            content = file_path.read_text()
            assert "O-001" in content


@jig.verifies("S-105", "S-106")
class TestApplyDeleteField:
    """Tests for apply_delete_field action."""

    def test_removes_field(self):
        """apply_delete_field removes field from frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text(
                "---\nid: S-001\nobsolete: true\n---\n# Test\n"
            )

            apply_delete_field(file_path, "obsolete")

            content = file_path.read_text()
            assert "obsolete" not in content
            assert "id: S-001" in content

    def test_noop_if_field_not_present(self):
        """apply_delete_field is no-op if field not present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            original = "---\nid: S-001\n---\n# Test\n"
            file_path.write_text(original)

            apply_delete_field(file_path, "nonexistent")

            content = file_path.read_text()
            # Should still have valid frontmatter structure
            assert "---\n" in content
            assert "id: S-001" in content


@jig.verifies("S-105", "S-106")
class TestApplyRenameFile:
    """Tests for apply_rename_file action."""

    def test_renames_file(self):
        """apply_rename_file renames file to new path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_path = Path(tmpdir) / "S-001_Old_Name.md"
            new_path = Path(tmpdir) / "S-001_New_Name.md"
            old_path.write_text("---\nid: S-001\n---\n# Test\n")

            apply_rename_file(old_path, new_path)

            assert not old_path.exists()
            assert new_path.exists()
            assert "id: S-001" in new_path.read_text()

    def test_creates_parent_directories(self):
        """apply_rename_file creates parent directories if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_path = Path(tmpdir) / "test.md"
            new_path = Path(tmpdir) / "subdir" / "nested" / "test.md"
            old_path.write_text("---\nid: S-001\n---\n# Test\n")

            apply_rename_file(old_path, new_path)

            assert not old_path.exists()
            assert new_path.exists()

    def test_handles_same_directory_rename(self):
        """apply_rename_file handles renaming within same directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_path = Path(tmpdir) / "old.md"
            new_path = Path(tmpdir) / "new.md"
            old_path.write_text("content")

            apply_rename_file(old_path, new_path)

            assert not old_path.exists()
            assert new_path.exists()
            assert new_path.read_text() == "content"


@jig.verifies("S-105", "S-106")
class TestApplySyncTitle:
    """Tests for apply_sync_title action."""

    def test_syncs_h1_to_frontmatter_title(self):
        """apply_sync_title updates H1 to match frontmatter title."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text(
                "---\nid: S-001\ntitle: Correct Title\n---\n# Wrong Title\n\nBody.\n"
            )

            apply_sync_title(file_path, direction="to_h1")

            content = file_path.read_text()
            assert "# Correct Title" in content
            assert "# Wrong Title" not in content

    def test_syncs_frontmatter_to_h1(self):
        """apply_sync_title updates frontmatter title to match H1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text(
                "---\nid: S-001\ntitle: Wrong Title\n---\n# Correct Title\n\nBody.\n"
            )

            apply_sync_title(file_path, direction="to_frontmatter")

            content = file_path.read_text()
            assert "title: Correct Title" in content
            assert "Wrong Title" not in content

    def test_preserves_body_content(self):
        """apply_sync_title preserves body content after H1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            body_after_h1 = "\n\nSome **markdown** content.\n\n- Item 1\n- Item 2\n"
            file_path.write_text(
                f"---\nid: S-001\ntitle: New\n---\n# Old{body_after_h1}"
            )

            apply_sync_title(file_path, direction="to_h1")

            content = file_path.read_text()
            assert body_after_h1 in content


@jig.verifies("S-105", "S-106")
class TestApplySetH1:
    """Tests for apply_set_h1 action."""

    def test_sets_h1_heading(self):
        """apply_set_h1 sets the H1 heading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text(
                "---\nid: S-001\n---\n# Old Heading\n\nBody.\n"
            )

            apply_set_h1(file_path, "New Heading")

            content = file_path.read_text()
            assert "# New Heading" in content
            assert "# Old Heading" not in content

    def test_adds_h1_if_missing(self):
        """apply_set_h1 adds H1 if not present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text("---\nid: S-001\n---\n\nBody without heading.\n")

            apply_set_h1(file_path, "New Heading")

            content = file_path.read_text()
            assert "# New Heading" in content
            # Body should still be present
            assert "Body without heading" in content

    def test_preserves_body_after_h1(self):
        """apply_set_h1 preserves content after H1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text(
                "---\nid: S-001\n---\n# Old\n\n## Section\n\nContent.\n"
            )

            apply_set_h1(file_path, "New")

            content = file_path.read_text()
            assert "# New" in content
            assert "## Section" in content
            assert "Content." in content
