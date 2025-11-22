---
id: S-CLI-003
type: specification
title: jigy init verifies and repairs missing directories
subsystem: cli
implements:
  - O-CLI-001
  - O-CLI-002
created: 2025-11-21
---

# S-CLI-003: jigy init verifies and repairs missing directories

## Specification

The `jigy init` command SHALL verify the existence of all required JIG directories and create any that are missing.

## Required Directories

1. `jig/outcomes/` - Outcome nodes (O-*)
2. `jig/specifications/` - Specification nodes (S-*)
3. `jig/constraints/` - Constraint nodes (C-*)

Note: Test (T) and Code (C) nodes are discovered via `@jig` annotations in code, not stored as markdown files. See JIG-Concept-v7.md for OSTCX model details.

## Behavior

### First Run (New Initialization)
- Create all three directories (outcomes, specifications, constraints)
- Report: "✓ Initialized JIG in <path>"
- List all created directories

### Subsequent Run (All Present)
- Verify all three directories exist
- Report: "✓ JIG structure verified - all components present"

### Repair Run (Some Missing)
- Detect which directories are missing
- Create missing directories only
- Report: "✓ Repaired JIG structure"
- List repaired directories

## Implementation Requirements

- Track existing vs created directories separately
- Use existing `ensure_dir()` utility from `jig.utils.io`
- Maintain consistent directory permissions
- Exit code 0 in all success cases (init, verify, repair)

## Rationale

Directory structure is foundational to JIG. Missing directories cause validation warnings and prevent node creation. Auto-repair reduces friction and follows principle of least surprise.

## References

- Current implementation: `src/jig/cli/init.py:39-42`
- Validation check: `src/jig/core/validator.py:133-135`

## Related Nodes

- Implements: O-CLI-001, O-CLI-002
- Related: S-CLI-004 (file verification), S-CLI-005 (user feedback)

