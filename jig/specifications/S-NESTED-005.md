---
id: S-NESTED-005
type: specification
title: Nested subsystem validation rules and constraint checking
subsystem: core
status: active
created: 2025-11-21
---

# Specification: Nested Subsystem Validation

## Purpose

Enforce structural constraints on nested subsystem hierarchies to prevent common errors and maintain architectural integrity.

## Requirements

### 1. Node Assignment Validation

**Rule:** Parent subsystems MUST NOT contain direct nodes

```python
# INVALID: Parent has both nodes and children
subsystems:
  crdt:
    nodes: [C-CRDT-001]          # ❌ Parent has nodes
    subsystems:
      ser: {...}                  # ❌ Also has children
```

```python
# VALID: Only leaves have nodes
subsystems:
  crdt:                           # ✓ Parent has no direct nodes
    subsystems:
      ser:
        nodes: [C-SER-001]        # ✓ Leaf has nodes
```

**Error Message:**
```
❌ Subsystem 'crdt' has both nodes and child subsystems
   Parent subsystems must delegate nodes to children
   Move nodes to leaf subsystems: crdt.ser, crdt.merge
```

### 2. Cycle Detection

**Rule:** Subsystem hierarchy MUST be acyclic (tree structure)

**Implementation:**
- YAML structure inherently prevents cycles (tree-based)
- Parser validates parent-child relationships
- No runtime cycle detection needed (structural guarantee)

**Test Coverage:**
- T-NESTED-004: Verify validation accepts valid hierarchies

### 3. Path Uniqueness

**Rule:** Subsystem paths MUST be unique within scope

**Examples:**
```yaml
# VALID: Unique paths
subsystems:
  crdt:
    subsystems:
      ser: {...}
  network:
    subsystems:
      ser: {...}   # OK: Different parent (network.ser ≠ crdt.ser)
```

```yaml
# INVALID: Duplicate child name
subsystems:
  crdt:
    subsystems:
      ser: {...}
      ser: {...}   # ❌ Duplicate key (YAML error)
```

### 4. Node Subsystem Reference Validation

**Rule:** Node annotations MUST reference existing subsystem paths

```python
# @jig C-SER-001 implements:S-SER-001 subsystem:crdt.ser  # ✓ Valid path
# @jig C-BAD-001 implements:S-BAD-001 subsystem:crdt.missing  # ❌ Invalid
```

**Error Message:**
```
❌ Node C-BAD-001 references non-existent subsystem 'crdt.missing'
   Available subsystems: crdt.ser, crdt.merge, crdt.conflict
```

### 5. Validation Integration

**When to validate:**
- During `jigy index rebuild` (full validation)
- During `jigy validate` (explicit check)
- On graph load (fail fast)

**Validation order:**
1. Parse YAML structure
2. Check parent-node constraint
3. Validate node subsystem references
4. Report all errors (don't stop at first)

## Implementation Notes

**Location:** `src/jig/core/validator.py:305` (C-NESTED-003)

**Dependencies:**
- S-NESTED-001 (subsystem data structure)
- Graph loading and parsing logic

**Error Handling:**
- Collect all validation errors
- Report with context (file, line, path)
- Exit with code 1 if errors found

## Test Coverage

- T-NESTED-004: Cycle detection (structural guarantee)
- T-NESTED-005: Parent-with-nodes validation

## References

- Implementation: `src/jig/core/validator.py:305`
- Related: S-NESTED-001 (data structure), S-NESTED-002 (path resolution)
