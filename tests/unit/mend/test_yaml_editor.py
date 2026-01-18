# ABOUTME: Tests for YAML frontmatter editor.
# ABOUTME: Verifies frontmatter manipulation preserves structure and body content.
"""
Tests for mend/yaml_editor.py frontmatter editing.

The YAML editor parses markdown files with YAML frontmatter and allows
modifying frontmatter fields while preserving the body content.
"""

import tempfile
from pathlib import Path

import jig
from jig.mend.yaml_editor import (
    parse_frontmatter_file,
    write_frontmatter_file,
    FrontmatterFile,
)


@jig.verifies("S-105", "S-106")
class TestParseFrontmatterFile:
    """Tests for parsing frontmatter from markdown files."""

    def test_parses_valid_frontmatter(self):
        """parse_frontmatter_file extracts frontmatter and body."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text(
                "---\nid: S-001\ntitle: Test\ntype: specification\n---\n# Test\n\nBody content.\n"
            )

            result = parse_frontmatter_file(file_path)

            assert result is not None
            assert result.frontmatter["id"] == "S-001"
            assert result.frontmatter["title"] == "Test"
            assert result.body == "\n# Test\n\nBody content.\n"

    def test_returns_none_for_no_frontmatter(self):
        """parse_frontmatter_file returns None for files without frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text("# Just a heading\n\nNo frontmatter here.\n")

            result = parse_frontmatter_file(file_path)
            assert result is None

    def test_returns_none_for_malformed_frontmatter(self):
        """parse_frontmatter_file returns None for malformed YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text("---\ninvalid: yaml: content:\n---\n# Test\n")

            result = parse_frontmatter_file(file_path)
            assert result is None

    def test_handles_empty_frontmatter(self):
        """parse_frontmatter_file handles empty frontmatter block."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text("---\n---\n# Empty frontmatter\n")

            result = parse_frontmatter_file(file_path)
            assert result is not None
            assert result.frontmatter == {}
            assert "# Empty frontmatter" in result.body


@jig.verifies("S-105", "S-106")
class TestWriteFrontmatterFile:
    """Tests for writing frontmatter back to files."""

    def test_writes_modified_frontmatter(self):
        """write_frontmatter_file writes updated frontmatter and body."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text(
                "---\nid: S-001\ntitle: Old\n---\n# Old\n\nBody.\n"
            )

            parsed = parse_frontmatter_file(file_path)
            parsed.frontmatter["title"] = "New"
            write_frontmatter_file(file_path, parsed)

            content = file_path.read_text()
            assert "title: New" in content
            assert "id: S-001" in content
            assert "# Old" in content  # Body preserved

    def test_preserves_body_content(self):
        """write_frontmatter_file preserves exact body content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            original_body = "\n# Test\n\nSome **markdown** content.\n\n- List item\n"
            file_path.write_text(f"---\nid: S-001\n---{original_body}")

            parsed = parse_frontmatter_file(file_path)
            parsed.frontmatter["new_field"] = "value"
            write_frontmatter_file(file_path, parsed)

            content = file_path.read_text()
            # Body should be preserved exactly
            assert original_body in content

    def test_adds_new_field(self):
        """write_frontmatter_file can add new fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"
            file_path.write_text("---\nid: S-001\n---\n# Test\n")

            parsed = parse_frontmatter_file(file_path)
            parsed.frontmatter["outcomes"] = ["O-001"]
            write_frontmatter_file(file_path, parsed)

            content = file_path.read_text()
            assert "outcomes:" in content
            assert "O-001" in content


@jig.verifies("S-105", "S-106")
class TestFrontmatterFile:
    """Tests for FrontmatterFile dataclass operations."""

    def test_set_field(self):
        """FrontmatterFile.set_field sets a field value."""
        fm = FrontmatterFile(
            frontmatter={"id": "S-001", "title": "Test"},
            body="\n# Test\n",
        )
        fm.set_field("title", "New Title")
        assert fm.frontmatter["title"] == "New Title"

    def test_add_field_value_creates_list(self):
        """FrontmatterFile.add_field_value creates list if field missing."""
        fm = FrontmatterFile(
            frontmatter={"id": "S-001"},
            body="\n# Test\n",
        )
        fm.add_field_value("outcomes", "O-001")
        assert fm.frontmatter["outcomes"] == ["O-001"]

    def test_add_field_value_appends(self):
        """FrontmatterFile.add_field_value appends to existing list."""
        fm = FrontmatterFile(
            frontmatter={"id": "S-001", "outcomes": ["O-001"]},
            body="\n# Test\n",
        )
        fm.add_field_value("outcomes", "O-002")
        assert fm.frontmatter["outcomes"] == ["O-001", "O-002"]

    def test_remove_field_value(self):
        """FrontmatterFile.remove_field_value removes from list."""
        fm = FrontmatterFile(
            frontmatter={"id": "S-001", "outcomes": ["O-001", "O-002"]},
            body="\n# Test\n",
        )
        fm.remove_field_value("outcomes", "O-001")
        assert fm.frontmatter["outcomes"] == ["O-002"]

    def test_remove_field_value_noop_if_missing(self):
        """FrontmatterFile.remove_field_value is no-op if value not in list."""
        fm = FrontmatterFile(
            frontmatter={"id": "S-001", "outcomes": ["O-001"]},
            body="\n# Test\n",
        )
        fm.remove_field_value("outcomes", "O-999")
        assert fm.frontmatter["outcomes"] == ["O-001"]

    def test_delete_field(self):
        """FrontmatterFile.delete_field removes field entirely."""
        fm = FrontmatterFile(
            frontmatter={"id": "S-001", "obsolete": True},
            body="\n# Test\n",
        )
        fm.delete_field("obsolete")
        assert "obsolete" not in fm.frontmatter

    def test_delete_field_noop_if_missing(self):
        """FrontmatterFile.delete_field is no-op if field not present."""
        fm = FrontmatterFile(
            frontmatter={"id": "S-001"},
            body="\n# Test\n",
        )
        fm.delete_field("nonexistent")  # Should not raise
        assert "nonexistent" not in fm.frontmatter
