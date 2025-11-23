---
id: S-CLI-008
type: specification
title: "Validate Command Output Format"
subsystem: cli
implements:
  - O-CLI-003
  - O-CLI-004
created: 2025-11-21
---

# Specification: Validate Command Output Format

Define the standard output format for `jigy validate` command using shared formatting library and consistent terminology.

## Requirements

### Output Structure

```
Validating JIG graph...
✓ All 20 nodes valid

Node summary:
  • Outcomes: 9
  • Specifications: 10
  • Constraints: 1

Warnings:
  ⚠ Unassigned nodes (3): O-PERF-001, S-API-001, C-PERF-001
  ⚠ Orphaned nodes (12): C-PERF-001, O-CLI-001, O-CLI-002, O-JIG-004,
    O-PERF-001, O-TEST-001, S-API-001, S-CLI-003, S-CLI-004, S-CLI-005,
    S-JIG-005, S-JIG-006

Suggestions:
  • Run 'jigy status' for detailed graph health metrics
```

### Section Specifications

**Validation Status Line (Required)**
- First line: "Validating JIG graph..."
- Second line: Result status
  - Success: "✓ All {N} nodes valid"
  - Failure: "✗ {N} nodes invalid (see errors below)"
- Uses ✓ for success, ✗ for error

**Node Summary (New Addition - Required)**
- Use `format_node_summary()` from formatting library
- Shows breakdown by type (Outcomes, Specifications, Constraints, etc.)
- Provides context about graph composition
- Same format as status command (consistency)

**Warnings (If Present)**
- Section header: "Warnings:"
- Unassigned nodes: Nodes missing subsystem field
  - Format: "⚠ Unassigned nodes (3): {comma-separated list}"
  - Consolidates per-node warnings into single line
- Orphaned nodes: Nodes not referenced in graph index
  - Format: "⚠ Orphaned nodes (12): {comma-separated list}"
  - Uses "Orphaned nodes" terminology (consistent with status command)
- Uses `format_warning()` from formatting library
- No warnings: Omit section entirely

**Suggestions (If Present)**
- Section header: "Suggestions:"
- Use `format_suggestion()` from formatting library
- Actionable next steps:
  - "Run 'jigy status' for detailed graph health metrics"
  - "Add 'subsystem: <name>' to frontmatter for unassigned nodes"
- No suggestions: Omit section entirely

### Breaking Changes from Previous Format

**BEFORE (per-node warnings, inconsistent terminology):**
```
Warnings:
  ⚠ Node O-PERF-001: subsystem not specified
  ⚠ Node S-API-001: subsystem not specified
  ⚠ Node C-PERF-001: subsystem not specified
  ⚠ Nodes not referenced in graph index: C-PERF-001, O-CLI-001, ... [20 nodes]
```

**AFTER (aggregated warnings, consistent terminology):**
```
Node summary:
  • Outcomes: 9
  • Specifications: 10
  • Constraints: 1

Warnings:
  ⚠ Unassigned nodes (3): O-PERF-001, S-API-001, C-PERF-001
  ⚠ Orphaned nodes (12): C-PERF-001, O-CLI-001, O-CLI-002, O-JIG-004,
    O-PERF-001, O-TEST-001, S-API-001, S-CLI-003, S-CLI-004, S-CLI-005,
    S-JIG-005, S-JIG-006
```

**Impact:**
- Reduces noise (4 warnings → 2 warnings for same issues)
- Adds node summary for context
- Uses consistent terminology with status command
- May break scripts counting warning lines

## Rationale

Current validate output is verbose and uses different terminology than status command:
- "subsystem not specified" vs "Unassigned nodes" (inconsistent)
- "Nodes not referenced in graph index" vs "Orphaned nodes" (inconsistent)
- Per-node warnings create noise (3 separate lines for same issue)
- Missing node summary (status has it, validate should too)

New format provides:
- Consistent terminology across commands
- Less noise (aggregated warnings)
- More context (node summary)
- Clear separation of problems (Warnings) from actions (Suggestions)

## Acceptance Criteria

- File modified: `src/jig/cli/validate.py` (warning display section)
- Uses formatting library functions:
  - `format_node_summary()` for node type breakdown
  - `format_warning()` for unassigned/orphaned nodes
  - `format_suggestion()` for suggestion bullets
- Node summary section added (new feature)
- Terminology changed: "subsystem not specified" → "Unassigned nodes"
- Terminology changed: "Nodes not referenced in graph index" → "Orphaned nodes"
- Warnings consolidated: one line per issue type, not per node
- Suggestions section added (new feature)
- Integration tests pass in `tests/integration/test_validate_command.py`
- Output matches example in S011_EXAMPLES_cli_output_before_after.md

## Related

- implements: O-CLI-003 (Consistent CLI Output Formatting)
- implements: O-CLI-004 (Actionable Error Messages)
- uses: S-CLI-006 (Standard Formatting Library)
- consistent_with: S-CLI-007 (Status Command - same terminology)
- subsystem: cli

## History

- 2025-11-21: Created during WU0 (known constraint from S011_SUMMARY_cli_output_alignment.md)
