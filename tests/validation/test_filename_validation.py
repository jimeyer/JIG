"""
Tests for filename format and H1 validation functions.

Tests S-018 (specification validation), S-019 (outcome validation),
and S-076 (architecture validation) filename and H1 requirements.
"""

import pytest

import jig
from jig.validation.intent import (
    to_snake_case,
    validate_filename_format,
    validate_h1_matches_title,
)


# ============================================================================
# Tests for to_snake_case()
# ============================================================================


class TestToSnakeCase:
    """Tests for the to_snake_case() helper function."""

    @jig.verifies("S-018", "S-019", "S-076")
    def test_simple_title(self):
        """Simple multi-word title converts correctly."""
        assert to_snake_case("Simple Title") == "Simple_Title"

    @jig.verifies("S-018", "S-019", "S-076")
    def test_three_word_title(self):
        """Three word title converts correctly."""
        assert to_snake_case("Python Code Structure") == "Python_Code_Structure"

    @jig.verifies("S-018", "S-019", "S-076")
    def test_acronym_preserved(self):
        """Acronyms are preserved in original case."""
        assert to_snake_case("CLI Commands") == "CLI_Commands"
        assert to_snake_case("YAML Frontmatter Parsing") == "YAML_Frontmatter_Parsing"
        assert to_snake_case("CLI Show Commands") == "CLI_Show_Commands"

    @jig.verifies("S-018", "S-019", "S-076")
    def test_punctuation_removed(self):
        """Apostrophes and question marks are removed."""
        assert to_snake_case("What's New?") == "Whats_New"
        assert to_snake_case("Don't Stop") == "Dont_Stop"

    @jig.verifies("S-018", "S-019", "S-076")
    def test_hyphens_preserved(self):
        """Hyphens in compound words are preserved."""
        assert to_snake_case("Cross-Tower Isolation") == "Cross-Tower_Isolation"
        assert to_snake_case("Self-Healing Systems") == "Self-Healing_Systems"

    @jig.verifies("S-018", "S-019", "S-076")
    def test_single_word(self):
        """Single word title stays unchanged."""
        assert to_snake_case("Validation") == "Validation"

    @jig.verifies("S-018", "S-019", "S-076")
    def test_mixed_case_preserved(self):
        """Mixed case is preserved."""
        assert to_snake_case("JIG Core Architecture") == "JIG_Core_Architecture"


# ============================================================================
# Tests for validate_filename_format()
# ============================================================================


class TestValidateFilenameFormat:
    """Tests for filename format validation."""

    @jig.verifies("S-018")
    def test_valid_spec_filename(self, tmp_path):
        """Valid specification filename passes validation."""
        spec_file = tmp_path / "S-001_Valid_Title.md"
        spec_file.write_text("---\nid: S-001\ntitle: Valid Title\ntype: specification\n---\n# Valid Title\n")

        frontmatter = {"id": "S-001", "title": "Valid Title", "type": "specification"}
        errors = validate_filename_format(spec_file, frontmatter, "S")

        assert errors == []

    @jig.verifies("S-019")
    def test_valid_outcome_filename(self, tmp_path):
        """Valid outcome filename passes validation."""
        outcome_file = tmp_path / "O-015_Valid_Title.md"
        outcome_file.write_text("---\nid: O-015\ntitle: Valid Title\ntype: outcome\n---\n# Valid Title\n")

        frontmatter = {"id": "O-015", "title": "Valid Title", "type": "outcome"}
        errors = validate_filename_format(outcome_file, frontmatter, "O")

        assert errors == []

    @jig.verifies("S-076")
    def test_valid_architecture_filename(self, tmp_path):
        """Valid architecture filename passes validation."""
        arch_file = tmp_path / "A-001_Valid_Title.md"
        arch_file.write_text("---\nid: A-001\ntitle: Valid Title\ntype: architecture\n---\n# Valid Title\n")

        frontmatter = {"id": "A-001", "title": "Valid Title", "type": "architecture"}
        errors = validate_filename_format(arch_file, frontmatter, "A")

        assert errors == []

    @jig.verifies("S-018")
    def test_invalid_filename_without_title(self, tmp_path):
        """Filename without title fails validation."""
        spec_file = tmp_path / "S-001.md"
        spec_file.write_text("---\nid: S-001\ntitle: Valid Title\ntype: specification\n---\n# Valid Title\n")

        frontmatter = {"id": "S-001", "title": "Valid Title", "type": "specification"}
        errors = validate_filename_format(spec_file, frontmatter, "S")

        assert len(errors) == 1
        assert "Invalid filename format" in errors[0]
        assert "Expected: S-001_Valid_Title.md" in errors[0]

    @jig.verifies("S-018")
    def test_filename_title_mismatch(self, tmp_path):
        """Filename title differs from frontmatter title."""
        spec_file = tmp_path / "S-001_Wrong_Title.md"
        spec_file.write_text("---\nid: S-001\ntitle: Correct Title\ntype: specification\n---\n# Correct Title\n")

        frontmatter = {"id": "S-001", "title": "Correct Title", "type": "specification"}
        errors = validate_filename_format(spec_file, frontmatter, "S")

        assert len(errors) == 1
        assert "Expected: S-001_Correct_Title.md" in errors[0]

    @jig.verifies("S-018")
    def test_missing_title_skips_validation(self, tmp_path):
        """Missing title in frontmatter skips filename validation."""
        spec_file = tmp_path / "S-001.md"
        spec_file.write_text("---\nid: S-001\ntype: specification\n---\n# Some Title\n")

        frontmatter = {"id": "S-001", "type": "specification"}  # No title
        errors = validate_filename_format(spec_file, frontmatter, "S")

        # Should skip validation when title is missing (caught by required field check)
        assert errors == []


# ============================================================================
# Tests for validate_h1_matches_title()
# ============================================================================


class TestValidateH1MatchesTitle:
    """Tests for H1 header validation."""

    @jig.verifies("S-018", "S-019", "S-076")
    def test_h1_matches_title(self, tmp_path):
        """First H1 matches frontmatter title."""
        doc_file = tmp_path / "S-001_Test.md"
        doc_file.write_text("---\nid: S-001\ntitle: Test Title\n---\n# Test Title\n\nContent here.\n")

        frontmatter = {"id": "S-001", "title": "Test Title"}
        errors = validate_h1_matches_title(doc_file, frontmatter)

        assert errors == []

    @jig.verifies("S-018", "S-019", "S-076")
    def test_h1_mismatch(self, tmp_path):
        """First H1 differs from frontmatter title."""
        doc_file = tmp_path / "S-001_Test.md"
        doc_file.write_text("---\nid: S-001\ntitle: Correct Title\n---\n# Wrong Title\n\nContent here.\n")

        frontmatter = {"id": "S-001", "title": "Correct Title"}
        errors = validate_h1_matches_title(doc_file, frontmatter)

        assert len(errors) == 1
        assert "H1 does not match title" in errors[0]
        assert 'Frontmatter title: "Correct Title"' in errors[0]
        assert 'First H1: "# Wrong Title"' in errors[0]

    @jig.verifies("S-076")
    def test_h1_with_id_prefix_fails(self, tmp_path):
        """H1 like '# A-001: Title' fails validation."""
        doc_file = tmp_path / "A-001_Test.md"
        doc_file.write_text("---\nid: A-001\ntitle: Test Title\n---\n# A-001: Test Title\n\nContent here.\n")

        frontmatter = {"id": "A-001", "title": "Test Title"}
        errors = validate_h1_matches_title(doc_file, frontmatter)

        # Should have TWO errors: mismatch AND id prefix
        assert len(errors) == 2
        assert any("H1 does not match title" in e for e in errors)
        assert any("H1 contains ID prefix" in e for e in errors)

    @jig.verifies("S-018", "S-019", "S-076")
    def test_missing_h1(self, tmp_path):
        """Document without H1 fails validation."""
        doc_file = tmp_path / "S-001_Test.md"
        doc_file.write_text("---\nid: S-001\ntitle: Test Title\n---\n\nNo heading here, just content.\n")

        frontmatter = {"id": "S-001", "title": "Test Title"}
        errors = validate_h1_matches_title(doc_file, frontmatter)

        assert len(errors) == 1
        assert "Missing H1 header" in errors[0]

    @jig.verifies("S-018", "S-019", "S-076")
    def test_multiple_h1_uses_first(self, tmp_path):
        """Only first H1 is checked for title match."""
        doc_file = tmp_path / "S-001_Test.md"
        doc_file.write_text("---\nid: S-001\ntitle: First Title\n---\n# First Title\n\n## Section\n\n# Second Title\n")

        frontmatter = {"id": "S-001", "title": "First Title"}
        errors = validate_h1_matches_title(doc_file, frontmatter)

        assert errors == []  # Only first H1 matters

    @jig.verifies("S-018", "S-019", "S-076")
    def test_h2_not_confused_with_h1(self, tmp_path):
        """H2 headers are not mistaken for H1."""
        doc_file = tmp_path / "S-001_Test.md"
        doc_file.write_text("---\nid: S-001\ntitle: Title\n---\n## Not H1\n\n# Title\n")

        frontmatter = {"id": "S-001", "title": "Title"}
        errors = validate_h1_matches_title(doc_file, frontmatter)

        assert errors == []

    @jig.verifies("S-018", "S-019", "S-076")
    def test_missing_title_skips_validation(self, tmp_path):
        """Missing title in frontmatter skips H1 validation."""
        doc_file = tmp_path / "S-001.md"
        doc_file.write_text("---\nid: S-001\n---\n# Some Title\n")

        frontmatter = {"id": "S-001"}  # No title
        errors = validate_h1_matches_title(doc_file, frontmatter)

        # Should skip validation when title is missing
        assert errors == []

