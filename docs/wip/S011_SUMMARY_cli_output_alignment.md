# CLI Output Alignment - Executive Summary

**Status**: Proposed  
**Created**: 2025-11-21  
**Related Documents**:
- `S011_PLAN_cli_output_alignment.md` (Detailed planning)
- `S011_EXAMPLES_cli_output_before_after.md` (Visual examples)

---

## Problem

The JIG CLI commands use inconsistent formatting and terminology:

- ❌ **`status`** lists orphaned nodes with newlines, **`validate`** uses commas
- ❌ **`status`** says "Orphaned nodes", **`validate`** says "Nodes not referenced in graph index"  
- ❌ **`validate`** repeats "subsystem not specified" per node instead of aggregating
- ❌ No standard for when to use comma-separated vs newline-separated lists
- ❌ Mixed use of "Warnings", "Suggestions", and unlabeled output

**Impact**: Confusing UX, harder to learn, difficult to script against

---

## Solution

### Core Principles

1. **Consistent terminology** across all commands
2. **Comma-separated lists** for >5 items (more scannable)
3. **Count in parentheses** for quick overview
4. **Separate Warnings from Suggestions** (problems vs actions)
5. **Node summary** shown in all commands

### Key Changes

| Before | After | Rationale |
|--------|-------|-----------|
| "Nodes not referenced in graph index" | **"Orphaned nodes"** | Shorter, clearer |
| "subsystem not specified" (per node) | **"Unassigned nodes"** (aggregate) | Less noise |
| Newline-separated lists | **Comma-separated** (wrapped) | More scannable |
| Mixed warnings/suggestions | **Separate sections** | Clearer structure |
| Type counts only in status | **Node summary** in all | Consistency |

---

## Before & After Comparison

### `jigy status`

**BEFORE**:
```
⚠ Orphaned nodes:
  12 node(s) have no relationships:
    - C-PERF-001
    - O-CLI-001
    - O-CLI-002
    [... 9 more lines ...]
```

**AFTER**:
```
Warnings:
  ⚠ Orphaned nodes (12): C-PERF-001, O-CLI-001, O-CLI-002, O-JIG-004,
    O-PERF-001, O-TEST-001, S-API-001, S-CLI-003, S-CLI-004, S-CLI-005,
    S-JIG-005, S-JIG-006
  ⚠ Unassigned nodes (3): O-PERF-001, S-API-001, C-PERF-001
```

**Savings**: 12 lines → 3 lines, easier to scan

### `jigy validate`

**BEFORE**:
```
Warnings:
  ⚠ Node O-PERF-001: subsystem not specified
  ⚠ Node S-API-001: subsystem not specified
  ⚠ Node C-PERF-001: subsystem not specified
  ⚠ Nodes not referenced in graph index: C-PERF-001, O-CLI-001, ... [20 nodes]
```

**AFTER**:
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

**Improvements**: 
- Added node summary (context)
- Consolidated warnings (4 lines → 2 lines)
- Consistent terminology with status

---

## Standard Terminology

| Concept | Standard Term | Used In |
|---------|--------------|---------|
| Nodes without edges | **Orphaned nodes** | status, validate |
| Nodes missing subsystem | **Unassigned nodes** | status, validate |
| Node type counts | **Node summary** | status, validate, graph |
| Edge types | **implements**, **verifies**, **depends_on** | All commands |
| Problems | **Warnings** | status, validate |
| Actions | **Suggestions** | status, validate |

---

## Formatting Standards

### Node Lists

```
Small (≤5 items): C-PERF-001, O-CLI-001, O-CLI-002, O-JIG-004, O-PERF-001

Large (>5 items): C-PERF-001, O-CLI-001, O-CLI-002, O-JIG-004, O-PERF-001,
  O-TEST-001, S-API-001, S-CLI-003, S-CLI-004, S-CLI-005, S-JIG-005,
  S-JIG-006
```

### Section Structure

```
[COMMAND NAME]

[STATUS] Summary line with counts

Section Header:
  • Item with 2-space indent
  • Another item

Warnings: (if any)
  ⚠ Warning message

Suggestions: (if any)
  • Actionable suggestion
```

### Status Indicators

```
✓  Success (green)
✗  Error (red)
⚠  Warning (yellow)
•  List item (cyan)
→  Forward relationship
←  Reverse relationship
```

---

## Implementation Plan

### Phase 1: Core Library (Week 1)
- Create `src/jig/cli/formatting.py`
- Implement shared formatting functions
- Add comprehensive unit tests

### Phase 2: Status & Validate (Week 2)
- Update status command with new format
- Update validate command with new format
- Update integration tests

### Phase 3: Graph Commands (Week 3)
- Update graph show command
- Add --format compact to graph list
- Update tests

### Phase 4: Documentation (Week 4)
- Update all help text
- Update user guide
- Add migration guide for scripts

---

## Proposed Outcomes & Specs

### Outcomes (in `jig/outcomes/`)

#### O-CLI-003: Consistent CLI Output Formatting
- All commands use same terminology
- Node lists use comma-separated format
- Status indicators used consistently

#### O-CLI-004: Actionable Error Messages
- Every error includes suggested action
- Suggestions are copy-paste ready
- Users can resolve >90% issues without docs

#### O-CLI-005: Progressive Disclosure
- Default output fits on screen
- --verbose provides detailed info
- Summary always shown first

### Specifications (in `jig/specifications/`)

#### S-CLI-006: Standard Formatting Library
- Shared formatting module
- Node list formatting with wrapping
- Section header formatting

#### S-CLI-007: Status Command Output Format
- Comma-separated node lists
- Separate Warnings/Suggestions sections
- Show edge count in summary

#### S-CLI-008: Validate Command Output Format
- Add node summary
- Use "Orphaned nodes" terminology
- Consolidate warnings

#### S-CLI-009: Graph Command Output Format
- Comma-separated dependencies/dependents
- Add --format compact option
- Show counts in headers

---

## Testing Strategy

### Unit Tests
```python
# Test formatting functions
test_format_node_list_small()
test_format_node_list_wrapping()
test_format_orphaned_nodes_terminology()
```

### Integration Tests
```python
# Test command output
test_status_uses_comma_separated_lists()
test_validate_uses_orphaned_terminology()
test_commands_use_consistent_node_summary()
```

### Acceptance Criteria
- [ ] All commands use shared formatting library
- [ ] Terminology consistent across commands
- [ ] Node lists comma-separated for >5 items
- [ ] Warnings separate from Suggestions
- [ ] All tests passing
- [ ] Documentation updated

---

## Breaking Changes & Migration

### Breaking Changes

1. **Status orphaned nodes format**
   - Old: Newline-separated list
   - New: Comma-separated list
   - Impact: Scripts parsing line-by-line

2. **Validate warning consolidation**
   - Old: One warning per node
   - New: Aggregated warnings
   - Impact: Scripts counting warnings

### Mitigation

1. Add `--format json` for machine-readable output
2. Add `--legacy` flag during transition (v0.2.0-v0.3.0)
3. Document changes in CHANGELOG
4. Provide migration guide for scripts

### Timeline

- **v0.2.0**: New format available, old format deprecated with warnings
- **v0.3.0**: New format default, old format via --legacy
- **v0.4.0**: Remove legacy format

---

## Success Metrics

### Qualitative
- ✓ Users find output "clear and consistent"
- ✓ New contributors understand without asking
- ✓ Examples are copy-paste ready

### Quantitative
- ✓ 100% commands use shared formatting
- ✓ <5% output lines exceed 80 chars (excluding tables)
- ✓ 0 terminology inconsistencies
- ✓ >95% test coverage for formatting

---

## Quick Reference Card

### Orphaned Nodes Everywhere

```bash
# Both commands now use same format:
jigy status   → "Orphaned nodes (12): C-PERF-001, O-CLI-001, ..."
jigy validate → "Orphaned nodes (12): C-PERF-001, O-CLI-001, ..."
```

### Comma-Separated Lists

```bash
# Old (hard to scan):
- C-PERF-001
- O-CLI-001
- O-CLI-002
...

# New (easier to scan):
C-PERF-001, O-CLI-001, O-CLI-002, O-JIG-004, O-PERF-001, O-TEST-001,
S-API-001, S-CLI-003, ...
```

### Count in Parentheses

```bash
# Quick overview without reading full list:
Orphaned nodes (12): ...
Unassigned nodes (3): ...
Dependencies (5): ...
```

### Warnings vs Suggestions

```bash
Warnings:       # Problems that exist
  ⚠ Orphaned nodes (12): ...

Suggestions:    # Actions to take
  • Add relationships to orphaned nodes
  • Run 'jigy validate'
```

---

## Next Actions

1. **Review**: Get maintainer feedback on this proposal
2. **Refine**: Adjust based on feedback
3. **Create**: Break down into implementation tasks
4. **Implement**: Execute Phase 1 (formatting library)
5. **Iterate**: Gather user feedback, adjust
6. **Document**: Update guides with new conventions

---

## Files to Review

- **Current implementations**:
  - `/src/jig/cli/status.py` (lines 129-245: format_status_output)
  - `/src/jig/cli/validate.py` (lines 100-106: warning display)
  - `/src/jig/cli/graph.py` (lines 132-148: dependencies display)

- **Test files**:
  - `/tests/integration/test_status_command.py`
  - `/tests/integration/test_validate_command.py`
  - `/tests/integration/test_graph_*.py`

- **Related documents**:
  - This directory: `docs/wip/S011_*.md`
  - Existing outcomes: `jig/outcomes/O-CLI-001.md`, `O-CLI-002.md`
  - Existing specs: `jig/specifications/S-CLI-003.md`, `S-CLI-004.md`, `S-CLI-005.md`

---

**Questions?** See `S011_PLAN_cli_output_alignment.md` for detailed planning and rationale.

**Examples?** See `S011_EXAMPLES_cli_output_before_after.md` for visual before/after comparisons.

