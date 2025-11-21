---
id: S-CLI-009
type: specification
title: "Graph Command Output Format"
subsystem: cli
created: 2025-11-21
---

# Specification: Graph Command Output Format

Define the standard output format for `jigy graph show` and `jigy graph list` commands using shared formatting library.

## Requirements

### Graph Show Output

**Current Structure (to be updated):**
```
O-JIG-001
Type: outcome
Title: JIG tools run in <1 second for most operations
Subsystem: core
Status: active

Body:
[First 10 lines of content...]
... (use 'cat jig/outcomes/O-JIG-001.md' for full content)

Dependencies (3):
  → S-JIG-001, S-JIG-002, S-GRAPH-001

Dependents (2):
  ← S-CLI-001, T-JIG-001
```

**Changes:**
1. Dependencies/Dependents use comma-separated format (not newline-separated)
2. Section headers include counts: "Dependencies (3):"
3. Full file path in hint: "use 'cat jig/outcomes/O-JIG-001.md'"
4. Use `format_node_list()` for comma-separated node lists
5. Use `format_section_header()` for consistent section headers

### Graph List Output

**Add new --format compact option:**

```bash
jigy graph list --subsystem core --format compact
```

**Output:**
```
Core subsystem (9 nodes):
  • Outcomes (5): O-JIG-001, O-JIG-002, O-JIG-003, O-JIG-004, O-JIG-005
  • Specifications (4): S-JIG-001, S-JIG-002, S-JIG-003, S-JIG-004
```

**Default table format remains unchanged (backward compatibility):**
```bash
jigy graph list --subsystem core
```

**Output:**
```
ID                   Type            Subsystem            Title
------------------------------------------------------------------------------------------
O-JIG-001            outcome         core                 JIG tools run in <1 second...
O-JIG-002            outcome         core                 JIG uses simple text formats...
[... table continues ...]
```

## Detailed Specifications

### Graph Show Command

**Dependencies Section:**
- Use `format_section_header("Dependencies", count)` for header
- Use `format_node_list()` for node IDs
- Single line if ≤5 dependencies
- Wrapped if >5 dependencies (comma-separated)
- Arrow indicator: "→" prefix for visual consistency
- Format: "→ {comma-separated node list}"

**Dependents Section:**
- Use `format_section_header("Dependents", count)` for header
- Use `format_node_list()` for node IDs
- Single line if ≤5 dependents
- Wrapped if >5 dependents (comma-separated)
- Arrow indicator: "←" prefix for visual consistency
- Format: "← {comma-separated node list}"

**File Path Hint:**
- Include full path: "use 'cat jig/outcomes/O-JIG-001.md'"
- Not just: "use 'cat' to see full content"
- More actionable and copy-paste ready

### Graph List Compact Format (New Feature)

**Option Specification:**
- Add `--format` option with choices: ["table", "compact"]
- Default: "table" (backward compatibility)
- Short form: `-f compact` or `-f table`

**Compact Format Output:**
- Groups nodes by type within subsystem
- Uses `format_node_list()` for comma-separated IDs
- Uses `format_section_header()` for section headers
- Shows total count in main header: "Core subsystem (9 nodes):"
- Shows count per type: "• Outcomes (5):"
- Compact and scannable for quick overview

**Table Format Output:**
- Remains unchanged (existing behavior)
- Default format for backward compatibility

## Breaking Changes

**Graph Show:**
- Dependencies/Dependents change from newline-separated to comma-separated
- May break scripts parsing line-by-line

**Graph List:**
- No breaking changes (new --format option, default unchanged)

## Rationale

**Graph Show:**
Current format uses newline-separated lists for dependencies, which wastes vertical space:
```
Dependencies:
  → S-JIG-001
  → S-JIG-002
  → S-GRAPH-001
```

New format is more compact and scannable:
```
Dependencies (3):
  → S-JIG-001, S-JIG-002, S-GRAPH-001
```

Saves 2 lines per dependency, more scannable, easier to copy-paste.

**Graph List Compact:**
Table format is verbose for quick overview. Compact format groups by type and shows only IDs, making it easier to:
- Quickly see distribution of node types
- Copy-paste node IDs for batch operations
- Scan large subsystems without scrolling

Both formats serve different purposes:
- Table: Detailed view with titles (default)
- Compact: Quick overview with just IDs (opt-in)

## Acceptance Criteria

- File modified: `src/jig/cli/graph.py`
- Graph show command:
  - Uses `format_section_header()` for Dependencies/Dependents headers
  - Uses `format_node_list()` for comma-separated node lists
  - Shows counts in section headers: "Dependencies (3):"
  - Includes full file path in hint
- Graph list command:
  - Adds `--format` option with choices ["table", "compact"]
  - Default format is "table" (unchanged behavior)
  - Compact format uses `format_node_list()` and groups by type
  - Help text documents both formats
- Integration tests pass in `tests/integration/test_graph_*.py`
- Output matches examples in S011_EXAMPLES_cli_output_before_after.md

## Related

- implements: O-CLI-003 (Consistent CLI Output Formatting)
- implements: O-CLI-005 (Progressive Disclosure - compact format)
- uses: S-CLI-006 (Standard Formatting Library)
- subsystem: cli

## History

- 2025-11-21: Created during WU0 (known constraint from S011_SUMMARY_cli_output_alignment.md)
