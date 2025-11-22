---
id: S-NESTED-002
type: specification
title: Subsystem path resolution and recursive node queries
subsystem: core
status: active
created: 2025-11-21
---

# Specification: Subsystem Path Resolution

## Purpose

Enable navigation of nested subsystem hierarchies using dot-notation paths and support recursive node collection for aggregate queries.

## Requirements

### 1. Path Notation

Support dot-notation for subsystem addressing:
- `auth` - Top-level subsystem
- `crdt.ser` - Child subsystem "ser" under "crdt"
- `protocol.v2.messages` - Multi-level nesting (3 levels)

### 2. Path Resolution Method

```python
def find_subsystem(self, path: str) -> Subsystem | None:
    """Navigate hierarchy by path.

    Args:
        path: Subsystem path using dot notation (e.g., 'crdt.ser')

    Returns:
        Subsystem object or None if not found
    """
```

**Algorithm:**
1. Split path on `.` separator
2. Match first segment to current subsystem name
3. If single segment, return self
4. If multiple segments, recurse into child subsystems
5. Return None if no match found

### 3. Recursive Node Collection

```python
def get_all_nodes(self, recursive: bool = False) -> list[str]:
    """Return all nodes in subsystem.

    Args:
        recursive: If True, include nodes from all descendant subsystems

    Returns:
        List of node IDs
    """
```

**Behavior:**
- `recursive=False`: Return only direct nodes (leaf subsystems only)
- `recursive=True`: Return nodes from self and all descendants

### 4. Use Cases

**Display Aggregates:**
```bash
# Show all nodes under 'crdt' (including crdt.ser, crdt.merge)
jigy graph list --subsystem crdt --recursive
```

**Scoped Queries:**
```python
# Get all nodes in specific subsystem
subsystem = graph.find_subsystem("crdt.ser")
nodes = subsystem.get_all_nodes(recursive=False)
```

### 5. Edge Cases

- **Non-existent path:** Return None (caller handles error)
- **Partial match:** Return None (e.g., "crdt.missing" when "missing" doesn't exist)
- **Empty subsystem:** Valid (return empty list)
- **Root lookup:** Support lookup by name from root context

## Implementation Notes

**Location:** `src/jig/core/graph.py:81-100`, `src/jig/core/graph.py:438`

**Dependencies:**
- S-NESTED-001 (subsystem data structure)
- String splitting/navigation logic

**Performance:**
- Path lookup: O(depth) - proportional to nesting level
- Recursive collection: O(n) - visits each subsystem once

## Test Coverage

- T-NESTED-002: Path resolution through hierarchy
- T-NESTED-009: Recursive node collection in graph list
- Integration: CLI commands using `--subsystem` with nested paths

## References

- Implementation: `src/jig/core/graph.py:438` (get_subsystem_by_path)
- CLI usage: `src/jig/cli/graph.py:263` (list command)
- Related: S-NESTED-001 (data structure), S-NESTED-003 (display)
