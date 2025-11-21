"""
Shared formatting library for consistent CLI output across all JIG commands.

This module provides formatting functions for node lists, section headers,
node summaries, warnings, and suggestions. All CLI commands should use these
functions to ensure consistent terminology and visual presentation.

Functions:
    format_node_list: Format node IDs as comma-separated list with wrapping
    format_section_header: Format section headers with optional counts
    format_node_summary: Format node type breakdown
    format_warning: Format warning messages with optional node list
    format_suggestion: Format actionable suggestion messages

# @jig C-CLI-014 implements:S-CLI-006 subsystem:cli interface:public
"""

from typing import Optional


def format_node_list(nodes: list[str], max_width: int = 80) -> str:
    """
    Format a list of node IDs as a comma-separated string with intelligent wrapping.

    Small lists (≤5 items) are displayed on a single line if they fit within max_width.
    Large lists (>5 items) are wrapped at ~max_width with 2-space indent continuation.
    Node IDs are never split across lines.

    Args:
        nodes: List of node IDs (e.g., ["O-CLI-001", "S-JIG-002"])
        max_width: Maximum line width before wrapping (default: 80)

    Returns:
        Formatted string with comma-separated node IDs, possibly multi-line

    Examples:
        >>> format_node_list(["O-CLI-001", "S-JIG-002"])
        'O-CLI-001, S-JIG-002'

        >>> format_node_list(["A"] * 15, max_width=40)
        'A, A, A, A, A, A, A, A, A, A, A, A, A,\\n  A, A'
    """
    if not nodes:
        return ""

    # Small lists: try single line first
    if len(nodes) <= 5:
        single_line = ", ".join(nodes)
        if len(single_line) <= max_width:
            return single_line

    # Large lists or lists that don't fit: wrap with indentation
    lines = []
    current_line = ""
    indent = "  "  # 2-space indent for continuation lines

    for i, node in enumerate(nodes):
        if i == 0:
            # First item starts with no indent
            current_line = node
        else:
            # Check if adding next item would exceed max_width
            test_line = current_line + ", " + node

            if len(test_line) <= max_width:
                # Fits on current line
                current_line = test_line
            else:
                # Need to wrap - save current line and start new one
                lines.append(current_line + ",")
                current_line = indent + node

    # Add the last line (no trailing comma on final line)
    if current_line:
        # Remove trailing comma from last line if present
        if lines:
            lines.append(current_line)
        else:
            lines.append(current_line)

    return "\n".join(lines)


def format_section_header(title: str, count: Optional[int] = None) -> str:
    """
    Format a section header with optional count.

    Args:
        title: Section title (e.g., "Dependencies", "Node summary")
        count: Optional count to display in parentheses

    Returns:
        Formatted section header with colon

    Examples:
        >>> format_section_header("Dependencies", 3)
        'Dependencies (3):'

        >>> format_section_header("Node summary")
        'Node summary:'
    """
    if count is not None:
        return f"{title} ({count}):"
    return f"{title}:"


def format_node_summary(nodes_by_type: dict[str, int]) -> str:
    """
    Format a node type breakdown summary.

    Args:
        nodes_by_type: Dictionary mapping node type to count
                      (e.g., {"outcome": 9, "specification": 10})

    Returns:
        Multi-line formatted summary with bullet points

    Examples:
        >>> summary = format_node_summary({"outcome": 9, "specification": 10, "constraint": 1})
        >>> print(summary)
        Node summary:
          • Outcomes: 9
          • Specifications: 10
          • Constraints: 1
    """
    if not nodes_by_type:
        return "Node summary:\n  (none)"

    # Type name pluralization mapping
    plurals = {
        "outcome": "Outcomes",
        "specification": "Specifications",
        "constraint": "Constraints",
        "test": "Tests",
        "code": "Code",
    }

    lines = ["Node summary:"]

    # Sort by type name for consistent ordering
    for node_type in sorted(nodes_by_type.keys()):
        count = nodes_by_type[node_type]
        # Get plural form, or capitalize and add 's' as fallback
        type_label = plurals.get(node_type, node_type.capitalize() + "s")
        lines.append(f"  • {type_label}: {count}")

    return "\n".join(lines)


def format_warning(message: str, nodes: Optional[list[str]] = None) -> str:
    """
    Format a warning message with optional node list.

    Args:
        message: Warning message (e.g., "Orphaned nodes")
        nodes: Optional list of node IDs to display (empty list treated as None)

    Returns:
        Formatted warning with ⚠ prefix and optional comma-separated node list

    Examples:
        >>> format_warning("General warning")
        '⚠ General warning'

        >>> format_warning("Orphaned nodes", ["O-CLI-001", "S-JIG-002"])
        '⚠ Orphaned nodes (2): O-CLI-001, S-JIG-002'
    """
    if nodes and len(nodes) > 0:
        count = len(nodes)
        node_list = format_node_list(nodes, max_width=78)  # Account for "⚠ " prefix
        # If node list is multi-line, indent continuation lines by 2 more spaces
        if "\n" in node_list:
            lines = node_list.split("\n")
            # First line gets the prefix, subsequent lines get extra indent
            formatted_nodes = lines[0] + "\n" + "\n".join("  " + line for line in lines[1:])
            return f"⚠ {message} ({count}): {formatted_nodes}"
        else:
            return f"⚠ {message} ({count}): {node_list}"
    else:
        return f"⚠ {message}"


def format_suggestion(message: str) -> str:
    """
    Format an actionable suggestion message.

    Args:
        message: Suggestion text (e.g., "Run 'jigy validate' to check graph")

    Returns:
        Formatted suggestion with • bullet prefix

    Examples:
        >>> format_suggestion("Add relationships to orphaned nodes")
        '• Add relationships to orphaned nodes'
    """
    return f"• {message}"
