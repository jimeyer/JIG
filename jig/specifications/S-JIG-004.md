---
id: S-JIG-004
type: specification
title: "Subsystems export <5 interfaces"
subsystem: core
implements:
  - O-JIG-005
created: 2025-11-18
---

# Specification: Subsystem Interface Limits

Each JIG subsystem exports at most 5 public interfaces to enforce deep modules (Ousterhout principle).

## Requirements

### Interface Limits

Each subsystem directory exports maximum 5 public functions/classes:
- `src/jig/core/`: ≤5 exports
- `src/jig/cli/`: ≤5 exports (commands are internal)
- `src/jig/graph/`: ≤5 exports
- `src/jig/harvest/`: ≤5 exports
- `src/jig/metrics/`: ≤5 exports

### Public Interface Marking

Use `@jig` annotations to mark public interfaces:

```python
# @jig C-CORE-001 implements:S-JIG-004 subsystem:core interface:public
def load_config(path: Path) -> JigConfig:
    """Public API: Load JIG configuration"""
    pass

# @jig C-CORE-002 implements:S-JIG-004 subsystem:core interface:internal
def _parse_toml(path: Path) -> dict:
    """Internal helper: Parse TOML file"""
    pass
```

### Module Depth Target

Module depth = LOC / exports ≥ 100:1

For a 500 LOC module:
- 5 exports = 100:1 depth ✓
- 10 exports = 50:1 depth ✗ (too shallow)

### Enforcement

`jig decompose --validate` checks:
- Count `interface:public` annotations per subsystem
- Fail if any subsystem >5 public interfaces
- Report module depth for each subsystem

## Rationale

**Deep modules** (Ousterhout): Best modules have simple interfaces hiding complex implementations.

Benefits:
- Reduced coupling (fewer connection points)
- Easier to understand (small API surface)
- Easier to change (large internal flexibility)
- Better abstraction (complexity hidden)

JIG enforces this on itself as dogfooding.

## Examples

### Good (Deep Module)
```python
# subsystem:auth - 3 public exports
# @jig interface:public
def authenticate(user: str, password: str) -> Token: ...

# @jig interface:public
def validate_token(token: Token) -> Claims: ...

# @jig interface:public
def revoke_token(token: Token) -> None: ...

# 15 internal helpers (interface:internal)
# Total: 500 LOC / 3 exports = 167:1 depth ✓
```

### Bad (Shallow Module)
```python
# subsystem:auth - 12 public exports (too many!)
# @jig interface:public
def hash_password(...): ...  # Should be internal

# @jig interface:public
def validate_email(...): ...  # Should be internal

# ... 10 more exports
# Total: 500 LOC / 12 exports = 42:1 depth ✗
```

## Acceptance Criteria

- Each subsystem has ≤5 `interface:public` annotations
- `jig decompose --validate` enforces this limit
- CI fails if limit exceeded
- Module depth ≥100:1 for all subsystems

## Related

- implements: O-JIG-005 (modularity >0.7)
- subsystem: core
- references: John Ousterhout "A Philosophy of Software Design"

## History

- 2025-11-18: Created during WU0 bootstrap (known constraint from SCOPE)
