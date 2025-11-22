---
id: S-NESTED-003
type: specification
title: Display nested subsystems in status and graph commands
subsystem: core
status: active
created: 2025-11-21
---

# Specification: Nested Subsystem Display

## Purpose

Render nested subsystem hierarchies in CLI output with tree-style formatting, supporting both hierarchical and flat views.

## Requirements

### 1. Hierarchical View (Default)

Display subsystems as indented tree:

```
Subsystems (3):
  crdt (8 nodes)
  ├── crdt.ser (3 nodes)
  ├── crdt.merge (2 nodes)
  └── crdt.conflict (3 nodes)
  auth (5 nodes)
```

**Rules:**
- Parent subsystems show aggregate node count
- Child subsystems indented with tree characters (`├──`, `└──`)
- Leaf subsystems show direct node count
- Use standard box-drawing characters for clarity

### 2. Flat View (--flat option)

Display subsystems as flat list with full paths:

```
Subsystems (4):
  crdt (8 nodes)
  crdt.ser (3 nodes)
  crdt.merge (2 nodes)
  crdt.conflict (3 nodes)
  auth (5 nodes)
```

**Rules:**
- All subsystems listed at same indentation level
- Use fully-qualified paths for children
- Parent subsystems included in list
- Alphabetical sort by full path

### 3. Affected Commands

**jigy status:**
- Show subsystem tree in overview section
- Display nested structure by default
- Support `--flat` flag

**jigy graph list:**
- Filter by subsystem path (e.g., `--subsystem crdt.ser`)
- Show subsystem context in output
- Support `--recursive` with nested paths

### 4. Node Count Aggregation

**Parent subsystems:**
- Total = sum of all descendant nodes
- Include in display for overview

**Leaf subsystems:**
- Direct node count only
- Actual nodes reside here

### 5. Output Format

Use Rich library for tree rendering:
- Tree characters: `├──`, `└──`, `│`
- Color coding: Subsystem names in blue, counts in dim
- Consistent indentation (2 spaces per level)

## Implementation Notes

**Location:** `src/jig/cli/status.py:21` (C-NESTED-004)

**Dependencies:**
- Rich library for tree rendering
- S-NESTED-002 (path resolution and node collection)

**Rendering Logic:**
```python
def render_subsystem_tree(subsystem: Subsystem, depth: int = 0):
    """Recursively render subsystem tree."""
    # Print current subsystem with indentation
    # Recurse into children
```

## Test Coverage

- T-NESTED-007: Verify hierarchical tree display in status
- T-NESTED-008: Verify flat view with `--flat` option
- Visual regression: Compare output formatting

## References

- Implementation: `src/jig/cli/status.py:21`
- Related: S-NESTED-002 (path resolution), S-GRAPH-001 (status logic)
