---
title: "PROBLEM: Multiple Validation Functions Not Wired Up"
type: problem
status: active
created: 1736202000
created_human: "2026-01-06 15:20 CST"
parent: null
children: ["C018_SCOPE_Wire_Up_Validation_Functions"]
---
# PROBLEM: Multiple Validation Functions Not Wired Up

**ID:** C017
**Status:** Active
**Date:** 2026-01-06

---

## Summary

Multiple validation functions exist in `src/jig/validation/` but are never called from CLI commands. This affects **Charter**, **Goals**, **Architecture**, and **Tower** validation. The implementation graph shows complete traceability, but the validation chain is broken.

## Dead Code Inventory

| Function | File:Line | Specs Claimed | Actually Called? |
|----------|-----------|---------------|------------------|
| `validate_charter_file()` | `intent.py:788` | S-072, S-073, S-074 | **NO** |
| `validate_goal_references()` | `intent.py:968` | S-075 | **NO** |
| `validate_architecture_files()` | `intent.py:1051` | S-076, S-077, S-078, S-079 | **NO** |
| `validate_tower_format()` | `bricks.py:875` | S-087 | **NO** |
| `validate_tower_isolation()` | `bricks.py:1011` | S-088, S-089 | **NO** |

**Total: 5 validation functions, 9 specs, all dead code.**

---

## A-001 Validation Rules vs Reality

A-001_JIG_Core_Architecture.md defines 22 validation rules. Here's the status:

### Charter Validation (Rules 1-4)

| # | Rule | Spec | Implemented? | Called? |
|---|------|------|--------------|---------|
| 1 | Charter `id` SHALL be exactly `"Charter"` | S-072 | YES | **NO** |
| 2 | Charter `defines_goals` SHALL be non-empty | S-073 | YES | **NO** |
| 3 | All goal IDs SHALL match `G-{number}` format | S-074 | YES | **NO** |
| 4 | All goal IDs SHALL have corresponding headers in body | S-074 | YES | **NO** |

### Architecture Validation (Rules 5-8)

| # | Rule | Spec | Implemented? | Called? |
|---|------|------|--------------|---------|
| 5 | Architecture `id` SHALL match pattern `A-{NNN}` | S-077 | YES | **NO** |
| 6 | Architecture `supports_goals` SHALL be non-empty | S-078 | YES | **NO** |
| 7 | Architecture `supports_goals` SHALL reference goals in Charter | S-078 | YES | **NO** |
| 8 | Architecture `constrains` SHALL reference existing specs | S-079 | YES | **NO** |

### Outcome Validation (Rules 9-12)

| # | Rule | Spec | Implemented? | Called? |
|---|------|------|--------------|---------|
| 9 | Outcome `id` SHALL match pattern `O-{NNN}` | S-018 | YES | YES |
| 10 | Outcome `supports_goals` SHALL be non-empty | S-018 | YES | YES |
| 11 | Outcome `supports_goals` SHALL reference goals in Charter | S-075 | YES | **NO** |
| 12 | Outcome `specifies` SHALL reference existing specs | S-042 | YES | YES |

### Specification Validation (Rules 13-14)

| # | Rule | Spec | Implemented? | Called? |
|---|------|------|--------------|---------|
| 13 | Specification `id` SHALL match pattern `S-{NNN}` | S-016 | YES | YES |
| 14 | Specification `status` SHALL be valid enum | S-017 | YES | YES |

### Brick Validation (Rules 15-19)

| # | Rule | Spec | Implemented? | Called? |
|---|------|------|--------------|---------|
| 15 | Brick `id` SHALL match pattern `B-[a-z0-9-]+` | S-030 | YES | YES |
| 16 | Brick `layer` SHALL be non-negative integer | S-030 | YES | YES |
| 17 | Brick `units` SHALL reference nodes in impl graph | S-034 | YES | YES |
| 18 | Every function SHALL belong to exactly one brick | S-035 | YES | YES |
| 19 | Brick dependencies SHALL respect layer hierarchy | S-038 | YES | YES |

### Tower Validation (Rules 20-22)

| # | Rule | Spec | Implemented? | Called? |
|---|------|------|--------------|---------|
| 20 | Tower values SHALL match kebab-case pattern | S-087 | YES | **NO** |
| 21 | Cross-tower dependencies SHALL be errors | S-088 | YES | **NO** |
| 22 | Single-tower projects skip tower validation | S-089 | YES | **NO** |

---

## Impact Summary

| Category | Rules | Implemented | Called | Gap |
|----------|-------|-------------|--------|-----|
| Charter | 4 | 4 | 0 | **4** |
| Architecture | 4 | 4 | 0 | **4** |
| Outcome | 4 | 4 | 3 | **1** |
| Specification | 2 | 2 | 2 | 0 |
| Brick | 5 | 5 | 5 | 0 |
| Tower | 3 | 3 | 0 | **3** |
| **Total** | **22** | **22** | **10** | **12** |

**55% of A-001 validation rules are not enforced.**

---

## Evidence

### validate_intent_command() - What It Calls

```python
# src/jig/cli/validate.py lines 30-107
def validate_intent_command(...):
    results["specifications"] = validate_specification_files(spec_dir)      # YES
    results["outcomes"] = validate_outcome_files(outcome_dir)               # YES
    results["outcome_completeness"] = validate_outcome_completeness(...)    # YES
    results["specification_coverage"] = validate_specification_coverage(...) # YES
    results["decorators"] = validate_decorator_files(...)                   # YES

    # MISSING:
    # validate_charter_file()
    # validate_goal_references()
    # validate_architecture_files()
```

### validate_bricks_command() - What It Calls

```python
# src/jig/cli/validate.py lines 126-192
def validate_bricks_command(...):
    results["definitions"] = validate_brick_definitions(...)      # YES
    results["partition"] = validate_brick_partition(...)          # YES
    results["layer_constraints"] = validate_brick_layer_constraints(...)  # YES
    results["cycles"] = validate_brick_cycles(...)                # YES

    # MISSING:
    # validate_tower_format()
    # validate_tower_isolation()
```

### Grep Confirms No Callers

```bash
$ grep -r "validate_charter_file\|validate_goal_references\|validate_architecture_files\|validate_tower_format\|validate_tower_isolation" src/jig/cli/
# No results
```

---

## Charter Goal Violations

| Goal | Violation |
|------|-----------|
| **G-003: Enforcing Constraints** | 12 validation rules exist but aren't enforced |
| **G-005: Full Traceability** | Charter, Architecture, Goals escape validation chain |

---

## Root Cause

The functions were implemented during C003 (Extended Intent Hierarchy and Towers) but the CLI integration was never completed. The specs (S-072 through S-091) were created, the functions were written with `@jig.implements()` decorators, but the final step of wiring them into `validate_intent_command()` and `validate_bricks_command()` was missed.

---

## Expected Fix

### In validate_intent_command():

```python
# Charter validation
charter_path = config.paths.charter
if charter_path.exists():
    results["charter"] = validate_charter_file(charter_path)
    charter_goals = get_charter_goals(charter_path)
else:
    charter_goals = set()

# Goal reference validation (outcomes + architecture)
if charter_goals:
    results["goal_references"] = validate_goal_references(
        outcome_dir, arch_dir, charter_goals
    )

# Architecture validation
arch_dir = config.paths.architecture
if arch_dir.exists():
    spec_ids = get_all_spec_ids(spec_dir)
    results["architecture"] = validate_architecture_files(
        arch_dir, charter_goals, spec_ids
    )
```

### In validate_bricks_command():

```python
# Tower format validation
tower_format_result = validate_tower_format(bricks_file)
results["tower_format"] = tower_format_result

# Tower isolation (only if towers are used)
if has_towers(bricks_file):
    results["tower_isolation"] = validate_tower_isolation(bricks_file, impl_graph)
```

---

## Specifications Affected

| Spec | Title | Status |
|------|-------|--------|
| S-072 | Charter File Structure | Dead code |
| S-073 | Charter defines_goals Field | Dead code |
| S-074 | Goal Header Format | Dead code |
| S-075 | Goal Reference Validation | Dead code |
| S-076 | Architecture Document Location and Naming | Dead code |
| S-077 | Architecture ID Format | Dead code |
| S-078 | Architecture Required Fields | Dead code |
| S-079 | Architecture Reference Validation | Dead code |
| S-087 | Tower Value Format | Dead code |
| S-088 | Cross-Tower Isolation | Dead code |
| S-089 | Tower Validation in jigy validate | Dead code |

---

## Resolution Checklist

### Intent Validation
- [ ] Wire `validate_charter_file()` into `validate_intent_command()`
- [ ] Wire `validate_goal_references()` into `validate_intent_command()`
- [ ] Wire `validate_architecture_files()` into `validate_intent_command()`
- [ ] Add tests for charter validation in CLI
- [ ] Add tests for goal reference validation in CLI
- [ ] Add tests for architecture validation in CLI

### Brick Validation
- [ ] Wire `validate_tower_format()` into `validate_bricks_command()`
- [ ] Wire `validate_tower_isolation()` into `validate_bricks_command()`
- [ ] Add tests for tower validation in CLI

### Verification
- [ ] Run `jigy validate` on JIG repo — expect new errors to surface
- [ ] Run `jigy validate` on ASE-A repo — expect new errors to surface
- [ ] Fix any legitimate validation failures discovered
- [ ] Verify all 22 A-001 rules are now enforced

---

## References

- A-001_JIG_Core_Architecture.md — Validation rules (section "Validation Rules")
- C003_SCOPE_Extended-Intent-Hierarchy-and-Towers.md — Original implementation scope
- S-072 through S-091 — Specifications for extended validation
