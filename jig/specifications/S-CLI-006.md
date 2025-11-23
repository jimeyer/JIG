---
id: S-CLI-006
type: specification
title: "Standard Formatting Library for CLI Output"
subsystem: cli
implements:
  - O-CLI-003
created: 2025-11-21
---

# Specification: Standard Formatting Library for CLI Output

Create a shared formatting module (`src/jig/cli/formatting.py`) that all CLI commands use for consistent output formatting.

## Requirements

### Core Functions

**`format_node_list(nodes: list[str], max_width: int = 80) -> str`**
- Takes a list of node IDs
- Returns comma-separated string with wrapping
- Small lists (≤5 items): single line if fits within max_width
- Large lists (>5 items): wrap at ~max_width chars with 2-space indent continuation
- Never split node IDs across lines (e.g., "C-PERF-001" stays together)
- Empty list returns empty string

**`format_section_header(title: str, count: int | None = None) -> str`**
- Returns formatted section header
- With count: "Dependencies (3):"
- Without count: "Node summary:"
- Consistent colon placement

**`format_node_summary(nodes_by_type: dict[str, int]) -> str`**
- Takes dict of {type: count}
- Returns formatted node type breakdown:
  ```
  Node summary:
    • Outcomes: 9
    • Specifications: 10
    • Constraints: 1
  ```
- Pluralizes type names
- Uses • bullet with 2-space indent

**`format_warning(message: str, nodes: list[str] | None = None) -> str`**
- Returns warning with ⚠ prefix
- With nodes: "⚠ Orphaned nodes (12): C-PERF-001, O-CLI-001, ..."
- Without nodes: "⚠ General warning message"
- Uses format_node_list() for node formatting

**`format_suggestion(message: str) -> str`**
- Returns suggestion with • prefix
- "• Add relationships to orphaned nodes"
- Used in Suggestions sections

### Implementation Approach

- Use Python's `textwrap` module for line wrapping
- All functions pure (no side effects, no state)
- All functions handle None and empty inputs gracefully
- Type hints for all parameters and return values
- Comprehensive docstrings with examples

### Line Wrapping Algorithm

For comma-separated lists:
1. Start with first item
2. Add items while line length < max_width
3. When next item would exceed max_width:
   - Start new line with 2-space indent
   - Continue adding items
4. Never break mid-item (node IDs are atomic)

Example:
```
⚠ Orphaned nodes (12): C-PERF-001, O-CLI-001, O-CLI-002, O-JIG-004,
  O-PERF-001, O-TEST-001, S-API-001, S-CLI-003, S-CLI-004, S-CLI-005,
  S-JIG-005, S-JIG-006
```

## Rationale

Shared formatting library ensures consistency across all commands. When `status`, `validate`, and `graph` commands use the same functions, terminology and formatting are automatically consistent. This also makes it easier to change formatting rules later (change in one place, applies everywhere).

DRY principle: Don't repeat formatting logic across multiple command files.

## Acceptance Criteria

- File created: `src/jig/cli/formatting.py`
- All 5 core functions implemented with type hints
- All functions handle edge cases:
  - Empty lists
  - None values
  - Single-item lists
  - Very long node IDs (>20 chars)
- Unit test coverage >95% in `tests/unit/cli/test_formatting.py`
- Tests verify wrapping behavior (no mid-ID splits)
- Tests verify empty input handling
- All functions have docstrings with examples

## Related

- implements: O-CLI-003 (Consistent CLI Output Formatting)
- used_by: S-CLI-007 (Status Command)
- used_by: S-CLI-008 (Validate Command)
- used_by: S-CLI-009 (Graph Commands)
- subsystem: cli

## History

- 2025-11-21: Created during WU0 (known constraint from S011_SUMMARY_cli_output_alignment.md)
