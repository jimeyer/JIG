---
title: "JIGPLAN: Wire Up Validation Functions"
type: jigplan
status: draft
created: 1736217600
created_human: "2026-01-06 19:40 CST"
parent: "C018_SCOPE_Wire_Up_Validation_Functions"
children: ["C020_PLAN_Wire_Up_Validation_Functions"]
---

# JIGPLAN: Wire Up Validation Functions

**SCOPE:** dig/wip/C018_SCOPE_Wire_Up_Validation_Functions.md
**Date:** 2026-01-06
**Status:** Draft
**Author:** Claude (agent)

---

## Summary

Wire 4 existing validation functions into CLI commands. All specs and validation functions already exist with proper @jig decorators. This is a pure "plumbing" change in B-cli to call functions that already exist in B-validation. Also update A-001 to reference A-004.

**Changes:**
- 0 new O/S nodes (all specs already exist)
- 0 new bricks (wiring within existing B-cli)
- 1 architecture document update (A-001)
- ~50 lines of code changes in validate.py

---

## O/S Node Reconciliation

### Outcomes

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | O-004 | Early Error Detection in Artifact Validation | Covers S-023, S-024, S-025 (validation CLI commands) |
| REUSE | O-023 | Charter Establishes Project Goals | Covers S-072-S-075 (Charter/Goal validation) |
| REUSE | O-024 | Architecture Constrains Specifications | Covers S-076-S-079 (Architecture validation) |
| REUSE | O-026 | Towers Enforce Component Isolation | Covers S-086-S-089 (Tower validation) |

### Specifications

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | S-023 | Intent Validation CLI Command | Already implemented; wiring adds more validations to it |
| REUSE | S-024 | Brick Validation CLI Command | Already implemented; wiring adds tower validation to it |
| REUSE | S-025 | Full Validation CLI Command | Already implemented; calls S-023 and S-024 |
| REUSE | S-072 | Charter File Structure | Implemented by `validate_charter_file()` |
| REUSE | S-073 | Charter Defines Goals Field | Implemented by `validate_charter_file()` |
| REUSE | S-074 | Goal Header Format | Implemented by `validate_charter_file()` |
| REUSE | S-075 | Goal ID Format | Implemented by `validate_goal_references()` |
| REUSE | S-076 | Architecture File Location | Implemented by `validate_architecture_files()` |
| REUSE | S-077 | Architecture ID Format | Implemented by `validate_architecture_files()` |
| REUSE | S-078 | Architecture Supports Goals Required | Implemented by `validate_architecture_files()` |
| REUSE | S-079 | Architecture Constrains References | Implemented by `validate_architecture_files()` |
| REUSE | S-086 | Brick Tower Field Optional | Implemented by `validate_tower_format()` |
| REUSE | S-087 | Tower Value Format | Implemented by `validate_tower_format()` |
| REUSE | S-088 | Cross Tower Isolation | Implemented by `validate_tower_isolation()` |
| REUSE | S-089 | Tower Isolation Validation | Implemented by `validate_tower_isolation()` |

**No UPDATE, DELETE, or CREATE actions.** All required specs already exist with proper implementations.

---

## O/S Node Details

### No Nodes to CREATE, UPDATE, or DELETE

This JIGPLAN requires no changes to O/S nodes. All specifications already exist and are implemented by validation functions in `src/jig/validation/`. The work is purely wiring these functions into CLI commands.

---

## Architecture Document Changes

### A-001 Update

**File:** `jig/architecture/A-001_JIG_Core_Architecture.md`

**Changes:**
1. Remove "Validation Rules" section (lines 157-197) — superseded by A-004
2. Add specs S-080-S-085 to `constrains` list (intent graph representation)
3. Add reference to A-004 in place of removed section

**Before (constrains):**
```yaml
constrains: [S-072, S-073, S-074, S-075, S-076, S-077, S-078, S-079, S-086, S-087, S-088]
```

**After (constrains):**
```yaml
constrains: [S-072, S-073, S-074, S-075, S-076, S-077, S-078, S-079, S-080, S-081, S-082, S-083, S-084, S-085, S-086, S-087, S-088]
```

**Replace Validation Rules section with:**
```markdown
## Validation

Validation of JIG artifacts is governed by A-004 (Validation Architecture).
See A-004 for the complete validation model, rules, and spec mappings.

This document (A-001) defines WHAT the structure IS. A-004 defines HOW to VALIDATE that structure.
```

---

## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| MODIFY | B-cli | 1 | Add function calls to validate.py |
| UNAFFECTED | B-validation | 0 | Functions already exist; no changes |
| FORBIDDEN | B-decorators | 0 | Foundation - no changes needed |
| FORBIDDEN | B-impl-graph | 0 | Foundation - no changes needed |
| FORBIDDEN | B-intent-graph | 0 | Foundation - no changes needed |
| FORBIDDEN | B-config | 0 | Foundation - no changes needed |
| FORBIDDEN | B-hashing | 0 | Foundation - no changes needed |
| FORBIDDEN | B-languages | 0 | Foundation - no changes needed |
| FORBIDDEN | B-verification-graph | 1 | Unrelated - no changes needed |
| FORBIDDEN | B-audit | 1 | Unrelated - no changes needed |
| FORBIDDEN | B-staleness | 0 | Foundation - no changes needed |

---

### Brick Details

#### B-cli Modifications

- **Layer:** 1 (unchanged)
- **File:** `src/jig/cli/validate.py`
- **Changes:**
  1. Add imports for 4 validation functions
  2. Add function calls in `validate_intent_command()`:
     - `validate_charter_file()`
     - `validate_goal_references()`
     - `validate_architecture_files()`
  3. Add function calls in `validate_bricks_command()`:
     - `validate_tower_format()`
     - `validate_tower_isolation()` (conditional on towers being declared)
  4. Add helper functions:
     - `_get_charter_goals()` — extract goals from Charter frontmatter
     - `_get_all_spec_ids()` — collect spec IDs for architecture validation
     - `_has_towers()` — check if any brick declares tower field

- **New dependencies:** None (B-validation is already a dependency)

#### FORBIDDEN Bricks

These bricks MUST NOT be modified by any work unit:

- **B-validation** (layer 0): Functions already exist with @jig.implements; only B-cli changes
- **All other bricks**: Scope discipline — this work only touches B-cli

**Sub-agent constraint:** Any modification to FORBIDDEN bricks is an immediate escalation trigger.

---

## Layer/Dependency Analysis

### Layer Structure (Affected Bricks)

```
Layer 0: UNAFFECTED
  B-validation ← functions already exist
    validate_charter_file()
    validate_goal_references()
    validate_architecture_files()
    validate_tower_format()
    validate_tower_isolation()

Layer 1: AFFECTED
  B-cli (MODIFY)
    └─► depends on: B-validation ✓ (already exists)
    └─► changes: validate.py adds calls to layer 0 functions
```

### Dependency Constraints

- B-cli (layer 1) depends on B-validation (layer 0) ✓
- No new dependencies introduced
- No circular dependencies possible (simple layer 1 → layer 0 call)

### Validation Commands

After implementation, verify with:
```bash
jigy rebuild && jigy validate
jigy layers  # Confirm layer structure unchanged
```

---

## @jig Decorator Changes

### No Decorator Changes Required

All validation functions already have `@jig.implements` decorators:

| Function | Decorators |
|----------|------------|
| `validate_charter_file()` | `@jig.implements("S-072", "S-073", "S-074")` |
| `validate_goal_references()` | `@jig.implements("S-075")` |
| `validate_architecture_files()` | `@jig.implements("S-076", "S-077", "S-078", "S-079")` |
| `validate_tower_format()` | `@jig.implements("S-086", "S-087")` |
| `validate_tower_isolation()` | `@jig.implements("S-088", "S-089")` |

CLI commands already have decorators:

| Function | Decorators |
|----------|------------|
| `validate_intent_command()` | `@jig.implements("S-023", "S-065", "S-070")` |
| `validate_bricks_command()` | `@jig.implements("S-024", "S-065", "S-070")` |
| `validate_full_command()` | `@jig.implements("S-025", "S-065", "S-070")` |

**No decorators to ADD, REMOVE, or MODIFY.**

---

## Clean Break Actions

This work follows clean break protocol:

- [x] No old code paths to delete (wiring only)
- [x] No old tests to delete (adding calls to existing functions)
- [x] No backwards compatibility shims needed
- [x] Unimplemented features will raise NotImplementedError (N/A)
- [x] No O/S nodes to delete

### Code to Delete

None. This is additive work only.

### O/S Nodes to Delete (After Validation)

None.

---

## Integration Tests

New tests to add in `tests/cli/test_validate_integration.py`:

| Test | Verifies |
|------|----------|
| `test_validate_catches_invalid_charter()` | S-072, S-073, S-074 |
| `test_validate_catches_invalid_architecture()` | S-076, S-077, S-078, S-079 |
| `test_validate_catches_invalid_goal_reference()` | S-075 |
| `test_validate_catches_invalid_tower_format()` | S-087, S-088, S-089 |

Pattern: Use `CliRunner` + `runner.isolated_filesystem()` per existing tests.

---

## Work Unit Mapping

| C018 Work Unit | JIGPLAN Action |
|----------------|----------------|
| WU-1: Finalize A-004 | ✓ COMPLETED |
| WU-2: Update A-001 | Architecture Document Changes section |
| WU-3: Wire Charter Validation | B-cli Modifications (validate_intent_command) |
| WU-4: Wire Architecture Validation | B-cli Modifications (validate_intent_command) |
| WU-5: Wire Goal Reference Validation | B-cli Modifications (validate_intent_command) |
| WU-6: Wire Tower Validation | B-cli Modifications (validate_bricks_command) |
| WU-7: End-to-End Verification | Integration Tests section |

---

## Approval Checklist

Before human approval:

- [x] All existing specs reviewed for REUSE opportunities — all REUSE
- [x] New specs follow evergreen guidelines — N/A (no new specs)
- [x] Brick layer constraints validated — B-cli (layer 1) → B-validation (layer 0) ✓
- [x] FORBIDDEN bricks identified — all except B-cli
- [x] @jig decorator plan complete — no changes needed
- [x] Clean break actions specified — N/A (additive work)

---

**Awaiting human approval before proceeding to implementation.**
