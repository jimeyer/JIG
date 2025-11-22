---
id: S-CLI-023
type: specification
title: "Status exit codes configurable via flags"
subsystem: cli
implements:
  - O-CLI-007
created: 2025-11-22
---

# S-CLI-023: Status exit codes configurable via flags

## Specification

The `jigy status` command SHALL provide flags to control exit code behavior, enabling different validation strategies for development vs CI environments.

## Flags

### --warn-only

**Behavior**: Always exit 0, even if errors present
**Use case**: Preview mode, non-blocking validation
**Example**:
```bash
jigy status --warn-only
# Shows errors but always exits 0
```

### --strict

**Behavior**: Exit 1 on errors OR warnings
**Use case**: High-quality enforcement, strict CI gates
**Example**:
```bash
jigy status --strict
# Fails if ANY warnings or errors present
```

### --quiet

**Behavior**: Suppress metrics, show only validation results
**Use case**: Focused validation output, CI logs
**Example**:
```bash
jigy status --quiet
# Only shows validation section, no node counts or metrics
```

## Exit Code Logic

```python
if warn_only:
    return 0
if strict and (validation_result.errors or validation_result.warnings):
    return 1
if validation_result.errors:
    return 1
return 0
```

## Default Behavior (No Flags)

- **Exit 0**: No errors (warnings OK)
- **Exit 1**: Errors present
- Shows full output (metrics + validation)

## Flag Combinations

Flags work independently and can be combined:

- `jigy status --quiet --strict`: Show only validation, fail on warnings
- `jigy status --quiet --warn-only`: Show only validation, never fail
- `jigy status --warn-only --strict`: Conflicting - `--warn-only` takes precedence (exit 0)

## Help Text

```
Usage: jigy status [OPTIONS]

  Show graph health metrics and validation results.

Options:
  --warn-only  Always exit 0 (show warnings but don't fail)
  --strict     Exit 1 on errors OR warnings (quality gate)
  --quiet      Only show validation results (suppress metrics)
  --verbose    Show detailed information (all nodes, edges)
  --flat       Flatten nested subsystems in output
  --help       Show this message and exit

Examples:
  jigy status                  # Default: fail on errors, pass on warnings
  jigy status --strict         # Fail on any warnings or errors
  jigy status --warn-only      # Never fail (preview mode)
  jigy status --quiet          # Only show validation (no metrics)
```

## Implementation Requirements

- Add Click options to `status_command()` in `src/jig/cli/status.py`
- Implement exit code logic after validation completes
- Document flag behavior in docstrings
- Test all flag combinations in unit tests

## Rationale

Different environments need different validation strategies:
- **Development**: Default (warnings OK, errors fail)
- **CI standard**: Default or `--strict` (quality gate)
- **CI preview**: `--warn-only` (see errors without blocking)
- **Focused debugging**: `--quiet` (reduce noise)

Flags provide escape hatches without requiring separate commands.

## References

- Implementation: `src/jig/cli/status.py`
- Tests: `tests/unit/test_status_flags.py` (to be created in WU3)

## Related Nodes

- Implements: O-CLI-007
- Related: S-CLI-022 (status validation), S-CLI-024 (validate removal)
