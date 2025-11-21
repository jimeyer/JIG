# CLI Output Alignment: Before & After Examples

**Related**: S011_PLAN_cli_output_alignment.md  
**Purpose**: Visual comparison of proposed output changes

## Key Changes Summary

1. ✅ Use **"Orphaned nodes"** terminology consistently
2. ✅ Use **comma-separated lists** instead of newline-separated (for >5 items)
3. ✅ Add **node summary** to all commands showing type breakdown
4. ✅ Distinguish **"Warnings"** (problems) from **"Suggestions"** (actions)
5. ✅ Use **"Unassigned nodes"** for nodes missing subsystems
6. ✅ Show **counts in parentheses** for quick scanning

---

## Command: `jigy status`

### BEFORE (Current)

```
JIG Graph Status

✓ Total nodes: 20

Node counts by type:
  constraint: 1
  outcome: 9
  specification: 10

Subsystems:
  core (9 nodes)

⚠ Orphaned nodes:
  12 node(s) have no relationships:
    - C-PERF-001
    - O-CLI-001
    - O-CLI-002
    - O-JIG-004
    - O-PERF-001
    - O-TEST-001
    - S-API-001
    - S-CLI-003
    - S-CLI-004
    - S-CLI-005
    - S-JIG-005
    - S-JIG-006

Suggestions:
  • 12 node(s) need relationships (add 'implements', 'verifies', or 'depends_on' edges)
  • 3 node(s) need subsystem assignment (add 'subsystem: <name>' to frontmatter)
  • Run 'jigy validate' to check graph consistency
```

### AFTER (Proposed)

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

### Changes Made

| Change | Rationale |
|--------|-----------|
| Summary shows edges count | More complete health metric |
| "Node counts" → "Node summary" | Clearer section purpose |
| Pluralized node types | More natural English |
| Orphaned nodes: newline → comma list | More scannable for large lists |
| Added "Warnings" section | Separates problems from actions |
| Added "Unassigned nodes" warning | Explicit identification of missing subsystems |
| Count in parentheses: (12) | Quick scanning without reading full list |

---

## Command: `jigy validate`

### BEFORE (Current)

```
Validating JIG graph...
✓ All 20 nodes valid

Warnings:
  ⚠ Node O-PERF-001: subsystem not specified
  ⚠ Node S-API-001: subsystem not specified
  ⚠ Node C-PERF-001: subsystem not specified
  ⚠ Nodes not referenced in graph index: C-PERF-001, O-CLI-001, O-CLI-002, O-JIG-001, O-JIG-002, O-JIG-003, O-JIG-004, O-JIG-005, O-PERF-001, O-TEST-001, S-API-001, S-CLI-003, S-CLI-004, S-CLI-005, S-JIG-001, S-JIG-002, S-JIG-003, S-JIG-004, S-JIG-005, S-JIG-006
```

### AFTER (Proposed)

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

### Changes Made

| Change | Rationale |
|--------|-----------|
| Added "Node summary" section | Consistency with status command |
| "subsystem not specified" → "Unassigned nodes" | Clearer, matches status terminology |
| Consolidated per-node warnings | Reduces noise, improves scanning |
| "Nodes not referenced" → "Orphaned nodes" | Consistent terminology across commands |
| Added "Suggestions" section | Clearer separation of issues vs actions |
| Line wrapping for long lists | Improves readability |

---

## Command: `jigy graph show O-JIG-001`

### BEFORE (Current)

```
O-JIG-001
Type: outcome
Title: JIG tools run in <1 second for most operations
Subsystem: core
Status: active

[Body content - first 10 lines...]
... (use 'cat' to see full content)

Dependencies:
  → S-JIG-001
  → S-JIG-002
  → S-GRAPH-001

Dependents:
  ← S-CLI-001
  ← T-JIG-001
```

### AFTER (Proposed)

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

### Changes Made

| Change | Rationale |
|--------|-----------|
| Dependencies on one line | More compact, easier to copy-paste |
| Added count in section header | Quick overview without reading list |
| Full file path in hint | More actionable |
| "Body:" label | Clearer section start |

---

## Command: `jigy graph list --subsystem core --format compact` (NEW)

### BEFORE (Not Available)

Only table format existed:

```
ID                   Type            Subsystem            Title
------------------------------------------------------------------------------------------
O-JIG-001            outcome         core                 JIG tools run in <1 second...
O-JIG-002            outcome         core                 JIG uses simple text formats...
O-JIG-003            outcome         core                 JIG is composable (pipes work)
O-JIG-004            outcome         core                 JIG requires no external services
O-JIG-005            outcome         core                 JIG demonstrates modularity >0.7
S-JIG-001            specification   core                 Marker extraction processes 1000...
S-JIG-002            specification   core                 OSTC nodes use YAML frontmatter...
S-JIG-003            specification   core                 Commands output valid YAML
S-JIG-004            specification   core                 Subsystems export <5 interfaces
```

### AFTER (Proposed)

New compact format option:

```
Core subsystem (9 nodes):
  • Outcomes (5): O-JIG-001, O-JIG-002, O-JIG-003, O-JIG-004, O-JIG-005
  • Specifications (4): S-JIG-001, S-JIG-002, S-JIG-003, S-JIG-004
```

### Changes Made

| Change | Rationale |
|--------|-----------|
| Added `--format compact` option | Provides alternative to table for quick overview |
| Groups by node type | Easier to see distribution |
| Comma-separated IDs | Compact, copy-paste friendly |
| Table format remains default | Backward compatibility |

---

## Side-by-Side: Terminology Consistency

### Before (Inconsistent)

| Command | Term for "No Edges" | Term for "No Subsystem" |
|---------|---------------------|-------------------------|
| `status` | "Orphaned nodes: 12 node(s) have no relationships" | (shown in suggestions) |
| `validate` | "Nodes not referenced in graph index" | "subsystem not specified" |

### After (Consistent)

| Command | Term for "No Edges" | Term for "No Subsystem" |
|---------|---------------------|-------------------------|
| `status` | "Orphaned nodes (12)" | "Unassigned nodes (3)" |
| `validate` | "Orphaned nodes (12)" | "Unassigned nodes (3)" |
| `graph show` | (shown in Dependencies count) | (shown in metadata) |

**Result**: Users learn terminology once, applies everywhere.

---

## Formatting Patterns Reference

### Node Lists

**Small (≤5 items)**: Single line, comma-separated
```
⚠ Unassigned nodes (3): O-PERF-001, S-API-001, C-PERF-001
```

**Large (>5 items)**: Wrapped at ~80 chars, comma-separated
```
⚠ Orphaned nodes (12): C-PERF-001, O-CLI-001, O-CLI-002, O-JIG-004,
  O-PERF-001, O-TEST-001, S-API-001, S-CLI-003, S-CLI-004, S-CLI-005,
  S-JIG-005, S-JIG-006
```

### Section Headers

**With count**:
```
Dependencies (3):
Warnings (2):
Orphaned nodes (12):
```

**Without count**:
```
Node summary:
Subsystems:
Suggestions:
```

### Status Indicators

```
✓  Success state (green)
✗  Error state (red)
⚠  Warning state (yellow)
•  List item / Suggestion (cyan)
→  Dependency / Forward (default)
←  Dependent / Reverse (default)
```

### Indentation

```
Section Header:
  • Item with 2-space indent
    Additional line with 4-space indent (continuation)

Tree structure:
  node
  ├── child1
  │   └── grandchild
  └── child2
```

---

## Impact on Scripts and Parsing

### Breaking Changes

**Status command orphaned nodes** (if scripts parse line-by-line):

```bash
# OLD (breaks with new format):
jigy status | grep -A 100 "Orphaned nodes" | grep "^    -" | cut -d' ' -f6

# NEW (works with comma-separated format):
jigy status | grep "Orphaned nodes" | sed 's/.*: //' | tr ',' '\n' | tr -d ' '
```

### Mitigation Strategies

1. **Add `--format json` option** for machine-readable output:
```bash
jigy status --format json | jq '.orphaned_nodes[]'
```

2. **Add `--legacy` flag** during transition period:
```bash
jigy status --legacy  # Uses old newline format
```

3. **Document migration** in CHANGELOG and upgrade guide

---

## Verbose Mode Examples

### `jigy status --verbose` (Enhanced)

```
JIG Graph Status

✓ 20 nodes, 8 edges, 1 subsystem

Node summary:
  • Outcomes: 9
  • Specifications: 10
  • Constraints: 1

Subsystems:
  • core (9 nodes)
    - O-JIG-001: JIG tools run in <1 second for most operations
    - O-JIG-002: JIG uses simple text formats (YAML + Markdown)
    - O-JIG-003: JIG is composable (pipes work)
    [... 6 more nodes ...]

Edges:
  • S-JIG-001 implements→ O-JIG-001
  • S-JIG-002 implements→ O-JIG-001
  • S-JIG-003 implements→ O-JIG-002
  [... 5 more edges ...]

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

**Added in verbose mode:**
- Individual node titles under subsystems
- Complete edge list with relationship types
- File paths (optional)

### `jigy validate --verbose` (Enhanced)

```
Validating JIG graph...
✓ All 20 nodes valid

Node summary:
  • Outcomes: 9
  • Specifications: 10
  • Constraints: 1

Node files:

  outcomes:
    ✓ jig/outcomes/O-JIG-001.md
    ✓ jig/outcomes/O-JIG-002.md
    ✓ jig/outcomes/O-JIG-003.md
    [... 6 more files ...]

  specifications:
    ✓ jig/specifications/S-JIG-001.md
    ✓ jig/specifications/S-JIG-002.md
    [... 8 more files ...]

  constraints:
    ✓ jig/constraints/C-PERF-001.md

Warnings:
  ⚠ Unassigned nodes (3): O-PERF-001, S-API-001, C-PERF-001
  ⚠ Orphaned nodes (12): C-PERF-001, O-CLI-001, O-CLI-002, O-JIG-004,
    O-PERF-001, O-TEST-001, S-API-001, S-CLI-003, S-CLI-004, S-CLI-005,
    S-JIG-005, S-JIG-006

Suggestions:
  • Run 'jigy status' for detailed graph health metrics
```

**Added in verbose mode:**
- Per-file validation results with paths
- Checkmark for each valid file

---

## Color Usage (Accessibility Note)

All status indicators work with or without color:

**With color** (terminal default):
```
✓ All 20 nodes valid (green checkmark)
⚠ Orphaned nodes (12) (yellow warning)
```

**Without color** (NO_COLOR=1 or --no-color):
```
✓ All 20 nodes valid (still clear)
⚠ Orphaned nodes (12) (still clear)
```

**Rationale**: 
- Icons (✓, ✗, ⚠) convey meaning without color
- Color enhances but is not required
- Follows accessibility best practices

---

## Implementation Checklist

### Phase 1: Core Library
- [ ] Create `src/jig/cli/formatting.py`
- [ ] Implement `format_node_list()` with wrapping
- [ ] Implement `format_section()` helper
- [ ] Implement `format_node_summary()`
- [ ] Add unit tests for all formatting functions

### Phase 2: Status Command
- [ ] Update `format_status_output()` to use shared formatting
- [ ] Change orphaned nodes to comma-separated
- [ ] Add "Unassigned nodes" section
- [ ] Add "Warnings" section (separate from Suggestions)
- [ ] Update tests

### Phase 3: Validate Command
- [ ] Add node summary section
- [ ] Change terminology to "Orphaned nodes"
- [ ] Change terminology to "Unassigned nodes"
- [ ] Consolidate warnings into lists
- [ ] Add suggestions section
- [ ] Update tests

### Phase 4: Graph Commands
- [ ] Update `graph show` to comma-separated lists
- [ ] Add count to Dependencies/Dependents headers
- [ ] Add `--format compact` to `graph list`
- [ ] Update tests

### Phase 5: Documentation
- [ ] Update CLI help text for all commands
- [ ] Update user guide with new examples
- [ ] Document migration for scripts
- [ ] Add formatting conventions to CONTRIBUTING.md

---

## Success Criteria

✅ All commands use "Orphaned nodes" terminology  
✅ All commands use comma-separated lists for >5 items  
✅ All commands show node summary consistently  
✅ Warnings and Suggestions clearly separated  
✅ Count shown in parentheses for quick scanning  
✅ Output still parseable by standard tools (grep, awk, sed)  
✅ Tests validate output format consistency  
✅ Documentation includes before/after examples  

---

## Related Documents

- **Planning**: `S011_PLAN_cli_output_alignment.md`
- **Outcomes**: O-CLI-003, O-CLI-004, O-CLI-005 (proposed)
- **Specs**: S-CLI-006, S-CLI-007, S-CLI-008, S-CLI-009 (proposed)
- **Implementation**: `/src/jig/cli/status.py`, `/src/jig/cli/validate.py`, `/src/jig/cli/graph.py`

