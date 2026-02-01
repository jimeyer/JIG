---
id: A-004
type: architecture
title: Validation Architecture
goals: [G-003, G-005]
specifications: [S-018, S-020, S-021, S-022, S-023, S-024, S-025, S-035, S-038, S-039, S-042, S-043, S-072, S-073, S-074, S-075, S-076, S-077, S-078, S-079, S-086, S-087, S-088, S-089, S-095, S-104, S-105, S-106, S-107, S-108, S-109]
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

## Rules-Based Architecture

Validation is implemented using a declarative rules engine. Each validation concern is expressed as a rule type that can be instantiated with configuration.

### Rule Types

| Rule Type | Purpose | Specs |
|-----------|---------|-------|
| RequiredFieldRule | Validate required frontmatter fields | S-018, S-019 |
| IdFormatRule | Validate ID patterns (S-###, O-###) | S-018, S-019 |
| UniquenessRule | Validate unique IDs | S-018, S-019 |
| FilenameSyncRule | Validate filename matches frontmatter | S-018, S-019 |
| HeaderSyncRule | Validate H1 matches title | S-018, S-019 |
| ReferenceValidityRule | Validate cross-references | S-020, S-079 |
| BidirectionalLinkRule | Validate bidirectional references | S-095 |
| CoverageRule | Validate coverage (specs by outcomes) | S-043 |
| PartitionRule | Validate partition property (brick partition) | S-022 |
| DAGRule | Validate acyclic graphs (brick dependencies) | S-039 |
| LayerConstraintRule | Validate layer hierarchy | S-038 |
| IsolationRule | Validate tower isolation | S-088, S-089 |

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| ValidationContext | `src/jig/rules/context.py` | Loads all artifacts into queryable structure |
| Rule Registry | `src/jig/rules/registry.py` | Instantiates and indexes all rules |
| Validation Engine | `src/jig/validation/engine.py` | Runs all rules, produces structured output |

### Domain Overview

| Domain | Specs | Rule Types Used |
|--------|-------|-----------------|
| Specification | S-018, S-043 | RequiredFieldRule, IdFormatRule, UniquenessRule, FilenameSyncRule, HeaderSyncRule, CoverageRule |
| Outcome | S-019, S-079 | RequiredFieldRule, IdFormatRule, UniquenessRule, FilenameSyncRule, HeaderSyncRule, ReferenceValidityRule |
| Bidirectional | S-095 | BidirectionalLinkRule |
| Brick Partition | S-022 | PartitionRule |
| Brick Dependencies | S-038, S-039 | LayerConstraintRule, DAGRule |
| Tower | S-088, S-089 | IsolationRule |

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

### Rule Instances

Brick validation uses the rules-based engine with these rule instances:

| Rule Instance | Type | Spec |
|---------------|------|------|
| BRICK_PARTITION | PartitionRule | S-022 |
| BRICK_DAG | DAGRule | S-039 |
| BRICK_LAYER_CONSTRAINT | LayerConstraintRule | S-038 |

**Location:** `src/jig/rules/registry.py`

**Called by:** Validation engine via `validate()` in `src/jig/validation/engine.py`

---

## Tower Validation

Towers partition the codebase vertically. Cross-tower dependencies are forbidden.

### Rules

| # | Rule | Spec |
|---|------|------|
| T-1 | Tower field (if present) SHALL match kebab-case pattern | S-087 |
| T-2 | Cross-tower dependencies SHALL be detected and reported as errors | S-088 |
| T-3 | Single-tower projects (no tower fields declared) SHALL skip tower validation | S-089 |

### Rule Instances

Tower validation uses the rules-based engine:

| Rule Instance | Type | Spec |
|---------------|------|------|
| TOWER_ISOLATION | IsolationRule | S-088, S-089 |

**Location:** `src/jig/rules/registry.py`

**Called by:** Validation engine via `validate()` in `src/jig/validation/engine.py`

**Note:** IsolationRule with `skip_if_single=True` handles S-089 (skip validation for single-tower projects).

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
| `jigy validate` | All rules from registry |
| `jigy validate intent` | Rules for specs S-018, S-019, S-020, S-042, S-043, S-079, S-095 |
| `jigy validate bricks` | Rules for specs S-021, S-022, S-035-S-039, S-086-S-089 |
| `jigy mend` | Run validation, then auto-apply fixes for fixable errors |
| `jigy align` | Full rebuild + `jigy validate` |

### Unified Validation Engine

All CLI commands use the unified validation engine (`src/jig/validation/engine.py`):

```python
result = validate(project_root)
# result = {
#   "errors": [...],
#   "summary": {"total": N, "auto_fixable": N, "manual": N}
# }
```

The CLI commands filter errors by spec ID to show domain-specific results.

### Rule Execution

The validation engine iterates over all rules in the registry:

```
1. Load ValidationContext (artifacts, bricks, impl graph)
2. For each rule in RULES:
   a. Call rule.violations(ctx) to get violations
   b. For each violation, compute error ID and fix template
3. Return aggregated errors and summary
```

### Error Aggregation

Validation does not short-circuit on first error. All rules are evaluated and all errors are reported together. Each error includes:
- Stable ID (per S-108)
- Spec reference (per S-109)
- Fix template (per S-104)

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
| 2.0 | 2026-01-18 | Migrated to rules-based architecture. Added rule types table. Updated brick/tower sections to reference rule instances. Updated execution model for unified engine. |
| 1.0 | 2026-01-06 | Activated. Fixed spec references (S-016/S-017→S-018, S-030/S-034→S-021/S-022). Fixed `validate_goal_references` signature. |
| Draft | 2026-01-06 | Initial creation from A-001 validation rules + C018 analysis |
