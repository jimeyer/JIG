---
id: S-CLI-007
type: specification
title: "Status Command Output Format"
subsystem: cli
created: 2025-11-21
---

# Specification: Status Command Output Format

Define the standard output format for `jigy status` command using shared formatting library.

## Requirements

### Output Structure

```
JIG Graph Status

✓ 20 nodes, 8 edges, 1 subsystem

Node summary:
  • Outcomes: 9
  • Specifications: 10
  • Constraints: 1

Subsystems:
  • core (9 nodes)

Warnings:
  ⚠ Orphaned nodes (12): C-PERF-001, O-CLI-001, O-CLI-002, O-JIG-004,
    O-PERF-001, O-TEST-001, S-API-001, S-CLI-003, S-CLI-004, S-CLI-005,
    S-JIG-005, S-JIG-006
  ⚠ Unassigned nodes (3): O-PERF-001, S-API-001, C-PERF-001

Suggestions:
  • Add relationships to 12 orphaned nodes (use 'implements:', 'verifies:',
    or 'depends_on:')
  • Assign 3 nodes to subsystems (add 'subsystem: <name>' to frontmatter)
  • Run 'jigy validate' to check graph consistency
```

### Section Specifications

**Summary Line (Required)**
- Format: "✓ {N} nodes, {M} edges, {K} subsystem(s)"
- Shows all three counts for complete health metric
- Uses ✓ (success) or ✗ (error) indicator based on validation status

**Node Summary (Required)**
- Use `format_node_summary()` from formatting library
- Shows breakdown by type (Outcomes, Specifications, Constraints, etc.)
- Pluralized type names
- 2-space indent with • bullet

**Subsystems (Required)**
- Lists each subsystem with node count
- Format: "• {subsystem_name} ({count} nodes)"
- If no subsystems: Show message "No subsystems defined"
- 2-space indent with • bullet

**Warnings (If Present)**
- Section header: "Warnings:"
- Orphaned nodes: Use `format_warning()` with "Orphaned nodes" terminology
  - Nodes with no incoming or outgoing edges
  - Format: "⚠ Orphaned nodes (12): {comma-separated list}"
- Unassigned nodes: Use `format_warning()` with "Unassigned nodes" terminology
  - Nodes missing subsystem field in frontmatter
  - Format: "⚠ Unassigned nodes (3): {comma-separated list}"
- No warnings: Omit section entirely (don't show "Warnings: None")

**Suggestions (If Present)**
- Section header: "Suggestions:"
- Use `format_suggestion()` for each suggestion
- Each suggestion starts with • bullet
- Suggestions are actionable and specific:
  - "Add relationships to N orphaned nodes (use 'implements:', 'verifies:', or 'depends_on:')"
  - "Assign N nodes to subsystems (add 'subsystem: <name>' to frontmatter)"
  - "Run 'jigy validate' to check graph consistency"
- No suggestions: Omit section entirely

### Breaking Changes from Previous Format

**BEFORE (newline-separated):**
```
⚠ Orphaned nodes:
  12 node(s) have no relationships:
    - C-PERF-001
    - O-CLI-001
    [... 10 more lines ...]
```

**AFTER (comma-separated):**
```
Warnings:
  ⚠ Orphaned nodes (12): C-PERF-001, O-CLI-001, O-CLI-002, O-JIG-004,
    O-PERF-001, O-TEST-001, S-API-001, S-CLI-003, S-CLI-004, S-CLI-005,
    S-JIG-005, S-JIG-006
```

**Impact:** Saves 10-12 lines, more scannable. May break scripts parsing line-by-line.

## Rationale

Current format is verbose (12 lines for orphaned nodes list) and inconsistent with validate command. New format:
- More scannable: count in parentheses for quick overview
- More compact: comma-separated saves vertical space
- More consistent: matches validate command terminology
- More actionable: separates Warnings (problems) from Suggestions (actions)

## Acceptance Criteria

- File modified: `src/jig/cli/status.py` (format_status_output function)
- Uses formatting library functions:
  - `format_node_summary()` for node type breakdown
  - `format_warning()` for orphaned/unassigned nodes
  - `format_suggestion()` for suggestion bullets
  - `format_node_list()` internally via format_warning()
- Summary line shows edge count (new addition)
- Orphaned nodes use comma-separated format (breaking change)
- Unassigned nodes explicitly listed as warning (new addition)
- Warnings and Suggestions are separate sections (new structure)
- Integration tests pass in `tests/integration/test_status_command.py`
- Output matches example in S011_EXAMPLES_cli_output_before_after.md

## Related

- implements: O-CLI-003 (Consistent CLI Output Formatting)
- implements: O-CLI-005 (Progressive Disclosure)
- uses: S-CLI-006 (Standard Formatting Library)
- consistent_with: S-CLI-008 (Validate Command - same terminology)
- subsystem: cli

## History

- 2025-11-21: Created during WU0 (known constraint from S011_SUMMARY_cli_output_alignment.md)
