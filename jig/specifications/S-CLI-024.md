---
id: S-CLI-024
type: specification
title: "Validate command removed completely"
subsystem: cli
implements:
  - O-CLI-006
  - O-CLI-007
created: 2025-11-22
---

# S-CLI-024: Validate command removed completely

## Specification

The `jigy validate` command SHALL be removed entirely with no deprecation period. This is a clean break following the taskCleanBreak.md protocol.

## Scope of Deletion

### Files Deleted Completely

1. `src/jig/cli/validate.py` - Entire file
2. `tests/unit/test_validate.py` - Entire file
3. `tests/integration/test_validate.py` - Entire file (if exists)

### Code Removed

1. Validate subcommand registration in `src/jig/cli/main.py`
2. Any validate-specific imports or references
3. Any validate command documentation

### What Remains

- Validation logic moves to `src/jig/core/validation.py` (created in WU1)
- Validation is called by `status` command (merged in WU2)
- No backward compatibility code
- No deprecation warnings
- No feature flags

## Behavior After Removal

```bash
$ jigy validate
Error: No such command 'validate'.

Did you mean one of these?
    status
```

(Click provides this automatically)

## Migration Path

**Old:**
```bash
jigy index rebuild
jigy status
jigy validate
```

**New:**
```bash
jigy index rebuild
jigy status  # Now includes validation
```

**One-line change in scripts:**
- Change: `jigy validate` → `jigy status`
- Or: Delete `jigy validate` line entirely

## Breaking Change Notice

This is an intentional breaking change:
- **Target users**: Pre-1.0 software, reference implementation
- **Justification**: Clean architecture > backward compatibility
- **Mitigation**: Trivial migration (one-line change)
- **Timeline**: No deprecation period (clean break)

## Rationale

**Why clean break over gradual deprecation:**

1. **JIG is pre-1.0**: Breaking changes expected
2. **Reference implementation**: Demonstrates clean architecture principles
3. **No technical debt**: Deprecation periods create dual implementations
4. **Clear mental model**: Two commands (rebuild, status) not three
5. **Simpler codebase**: One validation path, easier to maintain
6. **Trivial migration**: One-line change in scripts

**Tradeoffs accepted:**
- Users with `jigy validate` in scripts will get immediate errors
- CI pipelines must be updated (but fix is one line)
- No gradual transition period

**Why acceptable:**
- JIG users expect breaking changes (pre-1.0)
- Migration cost is minimal (1-2 minutes)
- Clear error message guides users to solution
- Clean codebase benefits future development

## Implementation Protocol

Following `agents/taskCleanBreak.md`:

1. ✓ Document decision with `#DECISION` marker in plan
2. Delete files completely (no commenting out)
3. Remove subcommand registration from main.py
4. Update graph index if validate had annotations
5. Run `jigy status` to verify no broken references
6. Update documentation with breaking change notice
7. NO feature flags, NO deprecation warnings
8. Commit: `refactor(cli): burn ships - remove validate command`

## Verification Checklist

After deletion:
- [ ] `jigy validate` produces error (command not found)
- [ ] `jigy --help` does not list validate
- [ ] No `validate` references in `src/` (except validation.py module)
- [ ] No `validate` test files remain in `tests/`
- [ ] Documentation updated to remove validate examples
- [ ] CI examples updated to use `status` only

## References

- Protocol: `agents/taskCleanBreak.md`
- Plan: `docs/wip/S030_PLAN_merge_validate_into_status.md`
- Implementation: WU4

## Related Nodes

- Implements: O-CLI-006 (single command), O-CLI-007 (consistent CI)
- Related: S-CLI-022 (status validation), S-CLI-025 (validation separation)
