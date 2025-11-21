---
id: O-CLI-002
type: outcome
title: Missing JIG structure components are automatically repaired
subsystem: cli
created: 2025-11-21
---

# O-CLI-002: Missing JIG structure components are automatically repaired

## Value Proposition

If a user accidentally deletes a JIG directory or file (e.g., `jig/constraints/`, `graph-index.yaml`), they should be able to restore the structure by simply running `jigy init` again, rather than searching documentation or manually recreating files.

## User Impact

- **Current State**: If `jig/constraints/` is deleted, user must manually recreate it or destroy and reinitialize entire JIG structure
- **Desired State**: Running `jigy init` detects and repairs missing directories and files
- **Benefit**: Self-healing, reduced support burden, improved developer experience

## Acceptance Criteria

- [ ] Missing directories (outcomes, specifications, tests, constraints) are recreated
- [ ] Missing files (graph-index.yaml, subsystems.yaml) are recreated with defaults
- [ ] Existing files and directories are preserved (no overwriting)
- [ ] User receives clear feedback about what was repaired
- [ ] `jigy validate` warnings are cleared after repair

## Example Scenario

```bash
# User accidentally deletes constraints directory
rm -rf jig/constraints

# Validation detects the issue
jigy validate
# Output: ⚠ Directory not found: jig/constraints

# Init repairs the structure
jigy init
# Output: ✓ Repaired JIG structure
#         Repaired:
#           - jig/constraints/

# Validation now passes
jigy validate
# Output: ✓ All 65 nodes valid
```

## Related Nodes

- Implements: (user need, not derived from other nodes)
- Supports: S-CLI-003, S-CLI-004, S-CLI-005

