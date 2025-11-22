---
id: S-NESTED-006
type: specification
title: Constraint scopes with nested subsystem paths
subsystem: core
status: active
created: 2025-11-21
---

# Specification: Constraint Scopes for Nested Subsystems

## Purpose

Enable Constraint nodes (X-*) to specify architectural rules that apply to specific subsystems or subsystem hierarchies using nested path notation.

## Requirements

### 1. Constraint Scope Syntax

Constraints use `scope:` metadata to specify applicability:

```python
# @jig X-ARCH-001 subsystem:arch scope:crdt
# Applies to top-level 'crdt' subsystem only

# @jig X-ARCH-002 subsystem:arch scope:crdt.*
# Applies to all subsystems under 'crdt' (crdt.ser, crdt.merge, etc.)

# @jig X-ARCH-003 subsystem:arch scope:crdt.ser
# Applies only to 'crdt.ser' subsystem
```

### 2. Scope Matching Rules

**Exact match:** `scope:crdt.ser` matches only `crdt.ser`
**Wildcard match:** `scope:crdt.*` matches `crdt.ser`, `crdt.merge`, `crdt.conflict`
**Recursive match:** `scope:crdt.*` also matches `crdt.ser.v2` (if exists)
**Global scope:** `scope:*` matches all subsystems

### 3. Constraint Evaluation

When validating a subsystem:
1. Collect all constraints where scope matches subsystem path
2. Evaluate each constraint against subsystem structure
3. Report violations with constraint ID and details

**Example Constraint:**
```markdown
---
id: X-COUPLING-001
type: constraint
title: CRDT subsystems must maintain 10:1 coupling ratio
scope: crdt.*
---

# Constraint: CRDT Coupling Ratio

All CRDT subsystems must maintain at least 10:1 internal-to-external coupling ratio.
```

### 4. Scope Resolution with Hierarchy

**Hierarchical scoping:**
- Constraints can target parent subsystems
- Evaluation includes all descendant nodes
- Useful for architectural boundaries

**Example:**
```yaml
# Constraint on parent applies to aggregate metrics
X-ARCH-001: scope:crdt
  → Validates coupling ratio for entire 'crdt' subsystem tree
  → Includes crdt.ser, crdt.merge, crdt.conflict
```

### 5. Scope Display

**jigy graph show X-ARCH-001:**
```
Constraint: X-ARCH-001
Scope: crdt.*
Applies to:
  - crdt.ser
  - crdt.merge
  - crdt.conflict
```

**jigy validate:**
```
Checking constraints...
  ✓ X-ARCH-001 (scope: crdt.*)
    ✓ crdt.ser (12.5:1 coupling)
    ✗ crdt.conflict (8.2:1 coupling) - below 10:1 target
```

## Implementation Notes

**Location:** Integration tests in `tests/integration/test_nested_status.py:259`

**Scope Matching Algorithm:**
```python
def matches_scope(subsystem_path: str, scope: str) -> bool:
    """Check if subsystem matches constraint scope."""
    if scope == "*":
        return True
    if scope.endswith(".*"):
        prefix = scope[:-2]
        return subsystem_path.startswith(prefix + ".")
    return subsystem_path == scope
```

**Dependencies:**
- S-NESTED-002 (path resolution)
- Constraint evaluation framework

## Test Coverage

- T-NESTED-010: Constraint scope matching with nested subsystem paths

## References

- Test: `tests/integration/test_nested_status.py:259`
- Related: S-NESTED-002 (path resolution), Constraint system (future spec)
