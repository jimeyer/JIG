---
id: S-CLI-004
type: specification
title: jigy init verifies and repairs missing config files
subsystem: cli
implements:
  - O-CLI-001
  - O-CLI-002
created: 2025-11-21
---

# S-CLI-004: jigy init verifies and repairs missing config files

## Specification

The `jigy init` command SHALL verify the existence of required JIG configuration files and create any that are missing with appropriate defaults.

## Required Files

1. `jig/graph-index.yaml` - Graph index tracking all nodes
2. `jig/subsystems.yaml` - Subsystem definitions
3. `jig.toml` - Project configuration (root level)

## Behavior

### File Creation Rules

**graph-index.yaml:**
- Create if missing with default:
  ```yaml
  version: "1.0"
  nodes: []
  ```

**subsystems.yaml:**
- Create if missing with default:
  ```yaml
  subsystems:
    - name: core
      description: Core subsystem
  ```

**jig.toml:**
- Create if missing with default project config
- **NEVER overwrite if exists** (preserves user configuration)

### Feedback

- Track which files were created/repaired
- Report separately from directory creation
- Clear distinction between "created" (first run) and "repaired" (missing files restored)

## Implementation Requirements

- Check file existence before attempting creation: `if not file_path.exists()`
- Use existing `write_file()` utility from `jig.utils.io`
- Preserve existing files exactly as-is (no updates or merges)
- Handle file permission errors gracefully

## Rationale

Missing `graph-index.yaml` causes validation warnings. Missing `subsystems.yaml` prevents subsystem-aware operations. Missing `jig.toml` prevents any JIG commands from working. Auto-repair enables self-healing after accidental deletion.

## Edge Cases

- **Corrupted files**: This spec only handles missing files, not corrupted ones (future: `jigy repair --validate`)
- **Permission errors**: Report clearly, don't fail silently
- **Partial deletion**: If only some files missing, repair just those

## References

- Current implementation: `src/jig/cli/init.py:44-65`
- Validation check: `src/jig/core/validator.py:164-186`

## Related Nodes

- Implements: O-CLI-001, O-CLI-002
- Related: S-CLI-003 (directory verification), S-CLI-005 (user feedback)

