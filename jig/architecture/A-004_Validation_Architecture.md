---
id: A-004
type: architecture
title: Validation Architecture
status: active
supports_goals: [G-003, G-005]
constrains: [S-018, S-020, S-021, S-022, S-023, S-024, S-025, S-035, S-038, S-039, S-042, S-043, S-072, S-073, S-074, S-075, S-076, S-077, S-078, S-079, S-086, S-087, S-088, S-089]
---

# Validation Architecture

## Context

JIG enforces architectural constraints through validation. This document defines the complete validation model: what is validated, how rules map to specifications, and how validation is executed.

This architecture supersedes the "Validation Rules" section of A-001 and establishes the authoritative reference for all validation behavior.

---

## Validation Philosophy

### Fail Fast, Fail Clearly

Validation follows A-002's CLI philosophy:

1. **No silent failures** — Every rule violation produces an error
2. **Actionable messages** — Errors include file paths, line numbers, and fix suggestions
3. **Strict by default** — No `--lenient` mode; constraints are non-negotiable
4. **Exit codes matter** — 0 = valid, non-zero = invalid

### Defense in Depth

Validation happens at multiple layers:

| Layer | When | What |
|-------|------|------|
| **Parse-time** | Reading files | YAML syntax, required fields |
| **Reference-time** | After parsing | Cross-references between artifacts |
| **Structure-time** | After graph build | Brick partition, layer hierarchy |
| **Runtime** | On command | Full validation suite |

---

## Validation Domains

JIG validates seven artifact types. Each domain has:
- **Rules**: Normative statements in this document
- **Specs**: Formal specifications that implementations must satisfy
- **Functions**: Code that enforces the rules

### Domain Overview

| Domain | Rules | Specs | Function |
|--------|-------|-------|----------|
| Charter | 4 | S-072, S-073, S-074 | `validate_charter_file()` |
| Goal References | 2 | S-075 | `validate_goal_references()` |
| Architecture | 7 | S-076, S-077, S-078, S-079 | `validate_architecture_files()` |
| Outcome | 7 | S-018, S-042 | `validate_outcome_files()`, `validate_outcome_completeness()` |
| Specification | 5 | S-018, S-043 | `validate_specification_files()`, `validate_specification_coverage()` |
| Brick | 8 | S-021, S-022, S-035, S-038, S-039 | `validate_brick_*()` |
| Tower | 3 | S-086, S-087, S-088, S-089 | `validate_tower_format()`, `validate_tower_isolation()` |
| Decorator | 3 | S-020 | `validate_decorator_files()` |

---

## Charter Validation

The Charter is the root of the intent hierarchy. It must be structurally valid.

### Rules

| # | Rule | Spec |
|---|------|------|
| C-1 | Charter `id` SHALL be exactly `"Charter"` | S-072 |
| C-2 | Charter `defines_goals` SHALL be a non-empty array | S-073 |
| C-3 | All goal IDs in `defines_goals` SHALL match `G-{number}` pattern | S-074 |
| C-4 | Each goal ID SHALL have a corresponding `### G-{number}:` header in body | S-074 |

### Function

```
validate_charter_file(charter_path: Path) -> ValidationResult
```

**Location:** `src/jig/validation/intent.py`

**Called by:** `validate_intent_command()`

---

## Goal Reference Validation

Goals defined in Charter are referenced by Architecture and Outcome documents. References must be valid.

### Rules

| # | Rule | Spec |
|---|------|------|
| GR-1 | Architecture `supports_goals` SHALL only reference goals defined in Charter | S-075 |
| GR-2 | Outcome `supports_goals` SHALL only reference goals defined in Charter | S-075 |

### Function

```
validate_goal_references(
    charter_path: Path,
    outcome_dir: Path,
    architecture_dir: Path | None = None,
) -> ValidationResult
```

**Location:** `src/jig/validation/intent.py`

**Called by:** `validate_intent_command()`

**Note:** Function loads charter goals internally from `charter_path`.

---

## Architecture Validation

Architecture documents constrain specifications. They must follow naming conventions and reference valid artifacts.

### Rules

| # | Rule | Spec |
|---|------|------|
| A-1 | Architecture files SHALL be in `jig/architecture/` directory | S-076 |
| A-2 | Architecture filenames SHALL match `A-{NNN}_{Title}.md` pattern | S-076 |
| A-3 | Architecture `id` SHALL match `A-{NNN}` (zero-padded to 3 digits) | S-077 |
| A-4 | Architecture SHALL have required fields: `id`, `type`, `title`, `status`, `supports_goals` | S-078 |
| A-5 | Architecture `status` SHALL be one of: `draft`, `proposed`, `active`, `deprecated` | S-078 |
| A-6 | Architecture `supports_goals` SHALL be non-empty | S-078 |
| A-7 | Architecture `constrains` (if present) SHALL reference existing spec IDs | S-079 |

### Function

```
validate_architecture_files(
    architecture_dir: Path,
    charter_goals: set[str],
    spec_ids: set[str]
) -> ValidationResult
```

**Location:** `src/jig/validation/intent.py`

**Called by:** `validate_intent_command()`

**Dependency:** Requires charter goals and spec IDs

---

## Outcome Validation

Outcomes decompose goals into specifications. They must reference valid artifacts and be complete.

### Rules

| # | Rule | Spec |
|---|------|------|
| O-1 | Outcome `id` SHALL match `O-{NNN}` pattern (zero-padded to 3 digits) | S-018 |
| O-2 | Outcome SHALL have required fields: `id`, `type`, `title`, `supports_goals`, `specifies` | S-018 |
| O-3 | Outcome `supports_goals` SHALL be non-empty | S-018 |
| O-4 | Outcome `specifies` SHALL be non-empty | S-042 |
| O-5 | Outcome `specifies` SHALL reference existing spec IDs | S-042 |
| O-6 | Outcome filename SHALL match `O-{NNN}_{Title}.md` pattern | S-018 |
| O-7 | Outcome H1 header SHALL match frontmatter `title` | S-018 |

### Functions

```
validate_outcome_files(outcome_dir: Path) -> ValidationResult
validate_outcome_completeness(outcome_dir: Path) -> ValidationResult
```

**Location:** `src/jig/validation/intent.py`

**Called by:** `validate_intent_command()`

---

## Specification Validation

Specifications define testable requirements. They must follow naming conventions and be covered by outcomes.

### Rules

| # | Rule | Spec |
|---|------|------|
| S-1 | Specification `id` SHALL match `S-{NNN}` pattern (zero-padded to 3 digits) | S-018 |
| S-2 | Specification SHALL have required fields: `id`, `type`, `title` | S-018 |
| S-3 | Specification filename SHALL match `S-{NNN}_{Title}.md` pattern | S-018 |
| S-4 | Specification H1 header SHALL match frontmatter `title` | S-018 |
| S-5 | Every specification SHALL be referenced by at least one outcome | S-043 |

### Functions

```
validate_specification_files(spec_dir: Path) -> ValidationResult
validate_specification_coverage(spec_dir: Path, outcome_dir: Path) -> ValidationResult
```

**Location:** `src/jig/validation/intent.py`

**Called by:** `validate_intent_command()`

---

## Brick Validation

Bricks partition the codebase into architectural units. Every function must belong to exactly one brick, and dependencies must respect layer hierarchy.

### Rules

| # | Rule | Spec |
|---|------|------|
| B-1 | Brick `id` SHALL match `B-{kebab-case}` pattern | S-035 |
| B-2 | Brick SHALL have required fields: `id`, `name`, `layer`, `units` | S-021 |
| B-3 | Brick `layer` SHALL be a non-negative integer | S-021 |
| B-4 | Brick `units` SHALL reference nodes in implementation graph | S-021 |
| B-5 | Every function in implementation graph SHALL belong to exactly one brick | S-022 |
| B-6 | No function SHALL belong to multiple bricks (partition constraint) | S-022 |
| B-7 | Brick dependencies SHALL respect layer hierarchy (no upward deps) | S-038 |
| B-8 | Brick dependency graph SHALL be acyclic (DAG constraint) | S-039 |

### Functions

```
validate_brick_definitions(bricks_file: Path, impl_graph: Path) -> ValidationResult
validate_brick_partition(bricks_file: Path, impl_graph: Path) -> ValidationResult
validate_brick_layer_constraints(bricks_file: Path, impl_graph: Path) -> ValidationResult
validate_brick_cycles(bricks_file: Path, impl_graph: Path) -> ValidationResult
```

**Location:** `src/jig/validation/bricks.py`

**Called by:** `validate_bricks_command()`

---

## Tower Validation

Towers partition the codebase vertically. Cross-tower dependencies are forbidden.

### Rules

| # | Rule | Spec |
|---|------|------|
| T-1 | Tower field (if present) SHALL match kebab-case pattern | S-087 |
| T-2 | Cross-tower dependencies SHALL be detected and reported as errors | S-088 |
| T-3 | Single-tower projects (no tower fields declared) SHALL skip tower validation | S-089 |

### Functions

```
validate_tower_format(bricks_file: Path) -> ValidationResult
validate_tower_isolation(bricks_file: Path, impl_graph: Path) -> ValidationResult
```

**Location:** `src/jig/validation/bricks.py`

**Called by:** `validate_bricks_command()`

**Note:** `validate_tower_isolation()` is only called if any brick declares a `tower` field.

---

## Decorator Validation

`@jig.implements()` and `@jig.verifies()` decorators link code to specifications. References must be valid.

### Rules

| # | Rule | Spec |
|---|------|------|
| D-1 | `@jig.implements()` decorator SHALL reference existing spec IDs | S-020 |
| D-2 | `@jig.verifies()` decorator SHALL reference existing spec IDs | S-020 |
| D-3 | Decorator arguments SHALL be string literals (not variables) | S-020 |

### Function

```
validate_decorator_files(
    src_dir: Path,
    spec_dir: Path,
    outcome_dir: Path | None,
    test_dir: Path | None
) -> ValidationResult
```

**Location:** `src/jig/validation/intent.py`

**Called by:** `validate_intent_command()`

---

## Execution Model

### CLI Commands and Validation

| Command | Validations Executed |
|---------|---------------------|
| `jigy validate` | All intent + all bricks |
| `jigy validate intent` | Charter, goal refs, architecture, outcomes, specs, coverage, decorators |
| `jigy validate bricks` | Brick definitions, partition, layers, cycles, towers |
| `jigy align` | Full rebuild + `jigy validate` |

### Validation Order

Within `validate_intent_command()`:

```
1. Charter validation (extract goals)
2. Specification validation (extract spec IDs)
3. Architecture validation (uses goals, spec IDs)
4. Outcome validation
5. Goal reference validation (uses goals)
6. Specification coverage validation
7. Decorator validation
```

Within `validate_bricks_command()`:

```
1. Brick definitions validation
2. Tower format validation
3. Brick partition validation
4. Brick layer constraints validation
5. Brick cycles validation
6. Tower isolation validation (if towers declared)
```

### Error Aggregation

All validation functions return `ValidationResult` objects. Errors are aggregated and reported together—validation does not short-circuit on first error.

---

## Spec Traceability Matrix

Complete mapping from rules to specs to functions:

| Domain | Rule | Spec | Function |
|--------|------|------|----------|
| Charter | C-1 | S-072 | `validate_charter_file` |
| Charter | C-2 | S-073 | `validate_charter_file` |
| Charter | C-3 | S-074 | `validate_charter_file` |
| Charter | C-4 | S-074 | `validate_charter_file` |
| Goal Ref | GR-1 | S-075 | `validate_goal_references` |
| Goal Ref | GR-2 | S-075 | `validate_goal_references` |
| Architecture | A-1..A-7 | S-076, S-077, S-078, S-079 | `validate_architecture_files` |
| Outcome | O-1..O-7 | S-018, S-042 | `validate_outcome_files`, `validate_outcome_completeness` |
| Specification | S-1..S-5 | S-018, S-043 | `validate_specification_files`, `validate_specification_coverage` |
| Brick | B-1..B-8 | S-021, S-022, S-035, S-038, S-039 | `validate_brick_*` |
| Tower | T-1..T-3 | S-086, S-087, S-088, S-089 | `validate_tower_format`, `validate_tower_isolation` |
| Decorator | D-1..D-3 | S-020 | `validate_decorator_files` |

---

## Compliance

All validation behavior SHALL comply with this architecture. New validation rules SHALL be documented here before implementation.

This document supersedes the "Validation Rules" section of A-001. A-001 retains authority over the intent hierarchy structure and brick model; A-004 is authoritative for validation behavior.

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-01-06 | Activated. Fixed spec references (S-016/S-017→S-018, S-030/S-034→S-021/S-022). Fixed `validate_goal_references` signature. |
| Draft | 2026-01-06 | Initial creation from A-001 validation rules + C018 analysis |
