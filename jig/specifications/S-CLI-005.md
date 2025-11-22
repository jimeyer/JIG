---
id: S-CLI-005
type: specification
title: jigy init reports created vs repaired components
subsystem: cli
implements:
  - O-CLI-001
  - O-CLI-002
created: 2025-11-21
---

# S-CLI-005: jigy init reports created vs repaired components

## Specification

The `jigy init` command SHALL provide clear, actionable feedback that distinguishes between three scenarios: first-time initialization, verification of existing structure, and repair of missing components.

## Message Scenarios

### Scenario 1: First-Time Initialization

**Condition:** `jig/` directory does not exist

**Output:**
```
✓ Initialized JIG in /path/to/project

Created:
  - jig/outcomes/
  - jig/specifications/
  - jig/tests/
  - jig/constraints/
  - jig/graph-index.yaml
  - jig/subsystems.yaml
  - jig.toml

Next steps:
  1. Create your first node: jigy node create --type outcome --id O-PROJ-001 --title "Your outcome"
  2. Validate your graph: jigy validate
```

### Scenario 2: Verification (All Present)

**Condition:** `jig/` exists and all components present

**Output:**
```
JIG already initialized in /path/to/project
Checking structure...
✓ JIG structure verified - all components present
```

### Scenario 3: Repair (Some Missing)

**Condition:** `jig/` exists but some components missing

**Output:**
```
JIG already initialized in /path/to/project
Checking structure...
✓ Repaired JIG structure

Repaired:
  - jig/constraints/
  - jig/graph-index.yaml
```

## Implementation Requirements

### State Tracking

- Track `already_initialized` flag: `jig_dir.exists()`
- Maintain two separate lists:
  - `created: list[str]` - components created on first run
  - `repaired: list[str]` - components restored on subsequent run

### Message Selection Logic

```python
if not already_initialized:
    # Scenario 1: First-time init
    print("✓ Initialized JIG in {path}")
    print("\nCreated:")
    for item in created:
        print(f"  - {item}")
    print("\nNext steps:...")
elif repaired:
    # Scenario 3: Repair
    print("✓ Repaired JIG structure")
    print("\nRepaired:")
    for item in repaired:
        print(f"  - {item}")
else:
    # Scenario 2: Verification
    print("✓ JIG structure verified - all components present")
```

### Visual Design

- Use `✓` (checkmark) for success states
- Use indentation for list items (2 spaces)
- Keep messages concise and scannable
- No error-like messaging for normal operations

## User Experience Goals

- **Clarity**: User immediately knows what happened
- **Confidence**: Green checkmarks indicate success
- **Actionability**: Next steps provided on first init
- **Non-disruptive**: Verification messages are brief
- **Informative**: Repair messages show exactly what was fixed

## Rationale

Clear feedback reduces user confusion and support burden. Distinguishing creation vs repair vs verification helps users understand system state. Following conventions from tools like `git init` reduces cognitive load.

## References

- Current implementation: `src/jig/cli/init.py:68-79`
- Click styling utilities: `click.echo()`, `click.style()`

## Related Nodes

- Implements: O-CLI-001, O-CLI-002
- Related: S-CLI-003 (directory verification), S-CLI-004 (file verification)

