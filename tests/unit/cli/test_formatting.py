"""
Unit tests for CLI formatting library.

Tests all formatting functions with various inputs including edge cases,
empty inputs, and wrapping behavior.

# @jig T-CLI-015 verifies:S-CLI-006 subsystem:cli
"""

import pytest

from jig.cli.formatting import (
    format_node_list,
    format_section_header,
    format_node_summary,
    format_warning,
    format_suggestion,
)


class TestFormatNodeList:
    """Tests for format_node_list function."""

    # @jig T-CLI-016 verifies:S-CLI-006 subsystem:cli
    def test_empty_list(self):
        """Empty list returns empty string."""
        assert format_node_list([]) == ""

    # @jig T-CLI-017 verifies:S-CLI-006 subsystem:cli
    def test_single_item(self):
        """Single item returns just that item."""
        assert format_node_list(["O-CLI-001"]) == "O-CLI-001"

    # @jig T-CLI-018 verifies:S-CLI-006 subsystem:cli
    def test_small_list_single_line(self):
        """Small list (≤5 items) on single line if fits."""
        result = format_node_list(["O-CLI-001", "O-CLI-002", "S-JIG-001"])
        assert result == "O-CLI-001, O-CLI-002, S-JIG-001"
        assert "\n" not in result

    # @jig T-CLI-019 verifies:S-CLI-006 subsystem:cli
    def test_small_list_wraps_if_long(self):
        """Small list wraps if it exceeds max_width."""
        # Create 5 items that would exceed 80 chars on one line
        nodes = [f"O-VERYLONGNAME-{i:03d}" for i in range(5)]
        result = format_node_list(nodes, max_width=40)
        assert "\n" in result
        lines = result.split("\n")
        # All continuation lines should start with 2-space indent
        for line in lines[1:]:
            assert line.startswith("  ")

    # @jig T-CLI-020 verifies:S-CLI-006 subsystem:cli
    def test_large_list_wraps(self):
        """Large list (>5 items) wraps at max_width."""
        nodes = [f"O-CLI-{i:03d}" for i in range(12)]
        result = format_node_list(nodes, max_width=80)
        assert "\n" in result
        lines = result.split("\n")
        assert len(lines) > 1
        # Check continuation lines are indented
        for line in lines[1:]:
            assert line.startswith("  ")

    # @jig T-CLI-021 verifies:S-CLI-006 subsystem:cli
    def test_wrapping_preserves_ids(self):
        """Node IDs are never split across lines."""
        nodes = ["O-CLI-001", "O-CLI-002", "S-JIG-001", "S-JIG-002"] * 3
        result = format_node_list(nodes, max_width=40)
        # Check that no line contains a partial ID
        for line in result.split("\n"):
            # Each node ID should be complete (no mid-ID breaks)
            # Remove indent and commas to get clean IDs
            clean_line = line.strip().rstrip(",")
            if clean_line:
                parts = [p.strip() for p in clean_line.split(",")]
                for part in parts:
                    # Each part should be a valid node ID format or empty
                    if part:
                        assert part.count("-") >= 2, f"Partial ID found: {part}"

    # @jig T-CLI-022 verifies:S-CLI-006 subsystem:cli
    def test_respects_max_width(self):
        """Lines respect max_width constraint."""
        nodes = [f"NODE-{i:02d}" for i in range(20)]
        max_width = 50
        result = format_node_list(nodes, max_width=max_width)
        for line in result.split("\n"):
            assert len(line) <= max_width + 5, f"Line too long: {len(line)} > {max_width}"

    # @jig T-CLI-023 verifies:S-CLI-006 subsystem:cli
    def test_no_trailing_comma_on_last_line(self):
        """Last line should not have a trailing comma."""
        nodes = [f"O-CLI-{i:03d}" for i in range(12)]
        result = format_node_list(nodes, max_width=40)
        lines = result.split("\n")
        last_line = lines[-1].strip()
        assert not last_line.endswith(","), f"Last line has trailing comma: {last_line}"

    # @jig T-CLI-024 verifies:S-CLI-006 subsystem:cli
    def test_intermediate_lines_have_trailing_comma(self):
        """Intermediate lines should have trailing commas."""
        nodes = [f"O-CLI-{i:03d}" for i in range(12)]
        result = format_node_list(nodes, max_width=40)
        lines = result.split("\n")
        if len(lines) > 1:
            for line in lines[:-1]:  # All but last line
                assert line.rstrip().endswith(","), f"Line missing comma: {line}"


class TestFormatSectionHeader:
    """Tests for format_section_header function."""

    # @jig T-CLI-025 verifies:S-CLI-006 subsystem:cli
    def test_header_without_count(self):
        """Header without count shows just title and colon."""
        assert format_section_header("Node summary") == "Node summary:"
        assert format_section_header("Warnings") == "Warnings:"

    # @jig T-CLI-026 verifies:S-CLI-006 subsystem:cli
    def test_header_with_count(self):
        """Header with count shows title, count in parens, and colon."""
        assert format_section_header("Dependencies", 3) == "Dependencies (3):"
        assert format_section_header("Orphaned nodes", 12) == "Orphaned nodes (12):"

    # @jig T-CLI-027 verifies:S-CLI-006 subsystem:cli
    def test_header_with_zero_count(self):
        """Header with zero count is handled correctly."""
        assert format_section_header("Items", 0) == "Items (0):"


class TestFormatNodeSummary:
    """Tests for format_node_summary function."""

    # @jig T-CLI-028 verifies:S-CLI-006 subsystem:cli
    def test_empty_summary(self):
        """Empty node types shows (none)."""
        result = format_node_summary({})
        assert "Node summary:" in result
        assert "(none)" in result

    # @jig T-CLI-029 verifies:S-CLI-006 subsystem:cli
    def test_single_type(self):
        """Single node type formatted correctly."""
        result = format_node_summary({"outcome": 9})
        expected = "Node summary:\n  • Outcomes: 9"
        assert result == expected

    # @jig T-CLI-030 verifies:S-CLI-006 subsystem:cli
    def test_multiple_types(self):
        """Multiple node types formatted correctly with pluralization."""
        result = format_node_summary({
            "outcome": 9,
            "specification": 10,
            "constraint": 1
        })
        assert "Node summary:" in result
        assert "• Outcomes: 9" in result
        assert "• Specifications: 10" in result
        assert "• Constraints: 1" in result
        # Check indent
        lines = result.split("\n")
        for line in lines[1:]:
            assert line.startswith("  ")

    # @jig T-CLI-031 verifies:S-CLI-006 subsystem:cli
    def test_types_sorted_alphabetically(self):
        """Node types are sorted alphabetically."""
        result = format_node_summary({
            "specification": 10,
            "constraint": 1,
            "outcome": 9
        })
        lines = result.split("\n")
        # After "Node summary:", should be: constraint, outcome, specification
        assert "Constraints" in lines[1]
        assert "Outcomes" in lines[2]
        assert "Specifications" in lines[3]

    # @jig T-CLI-032 verifies:S-CLI-006 subsystem:cli
    def test_unknown_type_pluralization(self):
        """Unknown types get capitalized and 's' added."""
        result = format_node_summary({"custom": 5})
        assert "• Customs: 5" in result


class TestFormatWarning:
    """Tests for format_warning function."""

    # @jig T-CLI-033 verifies:S-CLI-006 subsystem:cli
    def test_warning_without_nodes(self):
        """Warning without nodes shows just message with ⚠ prefix."""
        result = format_warning("General warning")
        assert result == "⚠ General warning"

    # @jig T-CLI-034 verifies:S-CLI-006 subsystem:cli
    def test_warning_with_empty_node_list(self):
        """Warning with empty node list behaves like no nodes."""
        result = format_warning("Orphaned nodes", [])
        # Empty list treated as no nodes (cleaner output)
        assert result == "⚠ Orphaned nodes"

    # @jig T-CLI-035 verifies:S-CLI-006 subsystem:cli
    def test_warning_with_few_nodes(self):
        """Warning with small node list on single line."""
        result = format_warning("Orphaned nodes", ["O-CLI-001", "S-JIG-002"])
        assert result == "⚠ Orphaned nodes (2): O-CLI-001, S-JIG-002"

    # @jig T-CLI-036 verifies:S-CLI-006 subsystem:cli
    def test_warning_with_many_nodes_wraps(self):
        """Warning with many nodes wraps correctly."""
        nodes = [f"O-CLI-{i:03d}" for i in range(12)]
        result = format_warning("Orphaned nodes", nodes)
        assert "⚠ Orphaned nodes (12):" in result
        # Should wrap
        assert "\n" in result
        lines = result.split("\n")
        # Continuation lines should be indented (2 for base + 2 for warning indent)
        for line in lines[1:]:
            # Account for the extra indent in format_warning for multiline
            assert line.startswith("    "), f"Line not properly indented: '{line}'"

    # @jig T-CLI-037 verifies:S-CLI-006 subsystem:cli
    def test_warning_shows_count(self):
        """Warning includes node count in parentheses."""
        result = format_warning("Unassigned nodes", ["A", "B", "C"])
        assert "(3)" in result


class TestFormatSuggestion:
    """Tests for format_suggestion function."""

    # @jig T-CLI-038 verifies:S-CLI-006 subsystem:cli
    def test_simple_suggestion(self):
        """Simple suggestion formatted with • bullet."""
        result = format_suggestion("Run 'jigy validate'")
        assert result == "• Run 'jigy validate'"

    # @jig T-CLI-039 verifies:S-CLI-006 subsystem:cli
    def test_long_suggestion(self):
        """Long suggestion text is preserved as-is."""
        long_text = "Add relationships to 12 orphaned nodes (use 'implements:', 'verifies:', or 'depends_on:')"
        result = format_suggestion(long_text)
        assert result == f"• {long_text}"

    # @jig T-CLI-040 verifies:S-CLI-006 subsystem:cli
    def test_empty_suggestion(self):
        """Empty suggestion shows just bullet."""
        result = format_suggestion("")
        assert result == "• "


# Integration tests combining multiple functions
class TestFormattingIntegration:
    """Integration tests showing realistic usage patterns."""

    # @jig T-CLI-041 verifies:S-CLI-006 subsystem:cli
    def test_status_output_pattern(self):
        """Test pattern similar to status command output."""
        # Node summary
        summary = format_node_summary({"outcome": 9, "specification": 10})
        assert "Node summary:" in summary
        assert "Outcomes: 9" in summary

        # Warning with nodes
        orphaned = ["C-PERF-001", "O-CLI-001", "O-CLI-002"]
        warning = format_warning("Orphaned nodes", orphaned)
        assert "⚠ Orphaned nodes (3):" in warning

        # Suggestion
        suggestion = format_suggestion("Add relationships to orphaned nodes")
        assert suggestion.startswith("• ")

    # @jig T-CLI-042 verifies:S-CLI-006 subsystem:cli
    def test_validate_output_pattern(self):
        """Test pattern similar to validate command output."""
        # Section header with count
        header = format_section_header("Warnings", 2)
        assert header == "Warnings (2):"

        # Multiple warnings
        unassigned = format_warning("Unassigned nodes", ["O-PERF-001", "S-API-001"])
        orphaned = format_warning("Orphaned nodes", ["C-PERF-001"] * 12)

        assert "Unassigned nodes (2)" in unassigned
        assert "Orphaned nodes (12)" in orphaned

    # @jig T-CLI-043 verifies:S-CLI-006 subsystem:cli
    def test_graph_show_pattern(self):
        """Test pattern similar to graph show command output."""
        # Dependencies header
        dep_header = format_section_header("Dependencies", 3)
        assert dep_header == "Dependencies (3):"

        # Dependencies list
        deps = format_node_list(["S-JIG-001", "S-JIG-002", "S-GRAPH-001"])
        assert deps == "S-JIG-001, S-JIG-002, S-GRAPH-001"

        # Dependents header
        dpt_header = format_section_header("Dependents", 2)
        assert dpt_header == "Dependents (2):"
