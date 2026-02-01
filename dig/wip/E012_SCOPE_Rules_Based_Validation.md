---
title: "Rules-Based Validation System"
type: scope
status: active
created: 1737244800
created_human: "2026-01-18 18:00 CST"
parent: "[[E008_CONCEPT_Validate_Mend_Contract]]"
children: []
---
# Rules-Based Validation System

## Executive Summary

Migrate JIG validation from procedural functions to a rules-based architecture where each **rule is the unit of abstraction**. A rule knows how to detect violations, describe repairs, and execute fixes. This eliminates divergence between `validate` and `mend` by construction — both derive from the same rule definition.

---

## Problem Statement

### Current State

Validation is implemented as procedural functions in `src/jig/validation/`:

| File | Functions | Checks |
|------|-----------|--------|
| `intent.py` | 12 functions | ~25 distinct validation checks |
| `bricks.py` | 6 functions | ~15 distinct validation checks |

Each function:
- Iterates over artifacts
- Checks conditions
- Emits `ValidationError` with message and code
- Returns `ValidationResult`

**Problems:**

1. **No fix information** — Errors say what's wrong but not how to fix it
2. **Validation and repair are separate concerns** — Must implement `mend` as independent code
3. **Guaranteed drift** — Nothing ensures mend handlers match validation rules
4. **Repeated boilerplate** — Same patterns (required field, ID format, bidirectional link) implemented ad-hoc each time

### Requirements (from E008)

The validate/mend contract requires:
1. `validate -j` outputs errors with **fix templates**
2. Agent/human fills in `???` values
3. `mend --apply` executes filled templates
4. Fix templates are structurally tied to validation rules

---

## Core Insight: Rules as Data

A **rule** is a first-class object that encapsulates:

| Responsibility | Method |
|----------------|--------|
| Detect violations | `violations(ctx) → Iterator[Violation]` |
| Describe repair | `fix_for(v) → Fix` |
| Execute repair | `apply(fix, ctx) → None` |

Validate and mend become thin orchestrators:

```python
# validate
for rule in RULES:
    for v in rule.violations(ctx):
        yield Error(code=rule.code, fix=rule.fix_for(v), ...)

# mend
for f in fixes:
    RULES_BY_CODE[f.code].apply(f.fix, ctx)
```

**Key property:** Same object produces check and fix. Drift is impossible.

---

## Rule Type Taxonomy

Analysis of current validation reveals **15 distinct rule patterns**. Most rules instantiate from a small set of **rule types** with parameters.

### 1. RequiredFieldRule

**Constraint:** Field must exist in frontmatter.

| Parameter | Type | Description |
|-----------|------|-------------|
| `artifact_type` | str | "specification", "outcome", etc. |
| `field` | str | Field name |
| `inferrable` | Callable | Optional: derive value from context |

**Detection:** Field missing from frontmatter.
**Fix:** `set_field` with inferred value or `???`.
**Auto:** True if `inferrable` provided and deterministic.

**Current rules mapping:**
- `id` required on all artifacts
- `type` required on all artifacts (inferrable from directory)
- `title` required on specs/outcomes/architecture
- `goals` required on charter/architecture
- `specifications` required on outcomes
- `layer` required on bricks

### 2. IdFormatRule

**Constraint:** ID field matches pattern.

| Parameter | Type | Description |
|-----------|------|-------------|
| `artifact_type` | str | "specification", "outcome", etc. |
| `pattern` | regex | Expected ID pattern |
| `normalizer` | Callable | Transform invalid → valid |

**Detection:** ID doesn't match pattern.
**Fix:** `set_field` with normalized value.
**Auto:** True (normalization is deterministic).

**Current rules mapping:**
- Spec ID: `S-\d+` (normalize to zero-padded `S-NNN`)
- Outcome ID: `O-\d+`
- Architecture ID: `A-\d{3}`
- Goal ID: `G-\d+`
- Brick ID: `B-[a-z0-9-]+` (kebab-case)
- Tower: `^[a-z][a-z0-9-]*$`

### 3. UniquenessRule

**Constraint:** Field value unique within scope.

| Parameter | Type | Description |
|-----------|------|-------------|
| `artifact_type` | str | Scope of uniqueness |
| `field` | str | Field to check |

**Detection:** Duplicate value found.
**Fix:** None (requires human decision).
**Auto:** False.

**Current rules mapping:**
- Spec ID uniqueness
- Outcome ID uniqueness
- Architecture ID uniqueness
- Brick ID uniqueness
- Goal ID uniqueness (within Charter)

### 4. FilenameSyncRule

**Constraint:** Filename matches frontmatter fields.

| Parameter | Type | Description |
|-----------|------|-------------|
| `artifact_type` | str | Type to check |
| `pattern` | str | Filename template, e.g., `{id}_{title}.md` |
| `title_transform` | Callable | e.g., `to_snake_case` |

**Detection:** Actual filename != expected filename.
**Fix:** `rename_file` to expected name.
**Auto:** True.

**Current rules mapping:**
- `S-NNN_Title.md` for specifications
- `O-NNN_Title.md` for outcomes
- `A-NNN_Title.md` for architecture

### 5. HeaderSyncRule

**Constraint:** H1 header matches frontmatter title.

| Parameter | Type | Description |
|-----------|------|-------------|
| `artifact_type` | str | Type to check |
| `source` | str | "h1" or "frontmatter" |

**Detection:** H1 != frontmatter title.
**Fix:** `sync_title` (H1 is source of truth).
**Auto:** True.

**Current rules mapping:**
- Specs: H1 must match title
- Outcomes: H1 must match title
- Architecture: H1 must match title

### 6. ExcludedFieldRule

**Constraint:** Field must NOT exist in frontmatter.

| Parameter | Type | Description |
|-----------|------|-------------|
| `artifact_type` | str | Type to check |
| `field` | str | Forbidden field |

**Detection:** Field present.
**Fix:** `delete_field`.
**Auto:** True.

**Current rules mapping:**
- Specs: `brick`, `depends_on`, `content`, `implements` excluded
- Outcomes: `brick` excluded
- Bricks: `depends_on`, `public_api`, `specs` excluded

### 7. FieldTypeRule

**Constraint:** Field has expected type.

| Parameter | Type | Description |
|-----------|------|-------------|
| `artifact_type` | str | Type to check |
| `field` | str | Field name |
| `expected_type` | type | list, str, int, etc. |
| `coercer` | Callable | Optional: convert to expected type |

**Detection:** `type(value) != expected_type`.
**Fix:** Coerce if possible, else `???`.
**Auto:** True if coercer works.

**Current rules mapping:**
- `goals` must be array
- `specifications` must be array
- `layer` must be int
- `tower` must be string

### 8. FieldValueRule

**Constraint:** Field value meets criteria.

| Parameter | Type | Description |
|-----------|------|-------------|
| `artifact_type` | str | Type to check |
| `field` | str | Field name |
| `predicate` | Callable | Value → bool |
| `fixer` | Callable | Optional: compute fix value |

**Detection:** `not predicate(value)`.
**Fix:** Apply fixer or `???`.
**Auto:** Depends on fixer.

**Current rules mapping:**
- `layer >= 0`
- `goals` non-empty
- `specifications` non-empty
- Unit prefix valid (`M-`, `C-`, `F-`)

### 9. ReferenceValidityRule

**Constraint:** Reference points to existing entity.

| Parameter | Type | Description |
|-----------|------|-------------|
| `source_type` | str | Artifact containing reference |
| `field` | str | Field containing references |
| `target_type` | str | Expected target type |

**Detection:** Referenced ID doesn't exist.
**Fix:** `change_reference` with suggestions, or `create_artifact`.
**Auto:** False (multiple valid fixes).

**Current rules mapping:**
- Decorator refs → specs/outcomes
- Goal refs in outcomes → Charter goals
- Goal refs in architecture → Charter goals
- Spec refs in architecture → specifications
- Unit refs in bricks → impl graph nodes

### 10. BidirectionalLinkRule

**Constraint:** If A.field contains B, then B.reverse_field contains A.

| Parameter | Type | Description |
|-----------|------|-------------|
| `forward_type` | str | Type containing forward ref |
| `forward_field` | str | Field with forward refs |
| `reverse_type` | str | Type containing back ref |
| `reverse_field` | str | Field with back refs |

**Detection:** Forward ref exists but back ref missing (or vice versa).
**Fix:** `add_field_value` to add missing link.
**Auto:** False (agent decides which direction to fix).

**Current rules mapping:**
- `O.specifications` ↔ `S.outcomes`
- `A.specifications` ↔ `S.architecture`

### 11. CoverageRule

**Constraint:** Every item in set A is referenced by at least one item in set B.

| Parameter | Type | Description |
|-----------|------|-------------|
| `covered_type` | str | Items that must be covered |
| `covering_type` | str | Items that provide coverage |
| `covering_field` | str | Field containing refs |

**Detection:** Item in A not referenced by any item in B.
**Fix:** `add_field_value` to suggested parent.
**Auto:** False (requires choosing parent).

**Current rules mapping:**
- All specs covered by at least one outcome

### 12. PartitionRule

**Constraint:** Every item in universe belongs to exactly one set.

| Parameter | Type | Description |
|-----------|------|-------------|
| `universe` | str | Set of items to partition |
| `partitions` | str | Sets that partition universe |
| `expansion` | Callable | Expand partition definition |

**Detection:** Item in 0 partitions (gap) or 2+ partitions (overlap).
**Fix:** Assign to suggested partition (gap) or remove from one (overlap).
**Auto:** False.

**Current rules mapping:**
- Functions partitioned by bricks

### 13. DAGRule

**Constraint:** Dependency graph is acyclic.

| Parameter | Type | Description |
|-----------|------|-------------|
| `node_type` | str | Node type |
| `edge_derivation` | Callable | How to derive edges |

**Detection:** Cycle found via DFS.
**Fix:** None (requires architectural decision).
**Auto:** False.

**Current rules mapping:**
- Brick dependencies form DAG

### 14. LayerConstraintRule

**Constraint:** Dependencies respect layer hierarchy.

| Parameter | Type | Description |
|-----------|------|-------------|
| `node_type` | str | Node type with layers |
| `layer_field` | str | Field containing layer |
| `edge_derivation` | Callable | How to derive dependencies |

**Detection:** Layer N depends on layer >= N (for N > 0).
**Fix:** None (requires architectural decision).
**Auto:** False.

**Current rules mapping:**
- Brick layer constraints

### 15. IsolationRule

**Constraint:** No dependencies cross boundary.

| Parameter | Type | Description |
|-----------|------|-------------|
| `node_type` | str | Node type |
| `boundary_field` | str | Field defining boundary (e.g., "tower") |
| `edge_derivation` | Callable | How to derive dependencies |

**Detection:** Edge crosses boundary.
**Fix:** None (requires architectural decision).
**Auto:** False.

**Current rules mapping:**
- Tower isolation (no cross-tower dependencies)

---

## Rule Registry

All rules defined in single registry:

```python
RULES: list[Rule] = [
    # Intent validation - Specifications (A-004 rules S-1 through S-5)
    RequiredFieldRule(code="MISSING_ID", spec="S-018", artifact_type="specification", field="id"),
    RequiredFieldRule(code="MISSING_TYPE", spec="S-018", artifact_type="specification", field="type",
                      inferrable=lambda ctx, a: "specification"),
    RequiredFieldRule(code="MISSING_TITLE", spec="S-018", artifact_type="specification", field="title"),
    IdFormatRule(code="INVALID_SPEC_ID", spec="S-018", artifact_type="specification",
                 pattern=r"^S-\d+$", normalizer=normalize_spec_id),
    FilenameSyncRule(code="SPEC_FILENAME_MISMATCH", spec="S-018", artifact_type="specification",
                     pattern="{id}_{title}.md", title_transform=to_snake_case),
    HeaderSyncRule(code="SPEC_H1_MISMATCH", spec="S-018", artifact_type="specification", source="h1"),

    # Coverage (A-004 rule S-5)
    CoverageRule(code="UNCOVERED_SPEC", spec="S-043", covered_type="specification",
                 covering_type="outcome", covering_field="specifications"),

    # Bidirectional consistency (A-004 rules O-4, O-5)
    BidirectionalLinkRule(
        code="ORPHAN_OUTCOME_SPEC_LINK", spec="S-042",
        forward_type="outcome", forward_field="specifications",
        reverse_type="specification", reverse_field="outcomes",
    ),

    # Brick validation (A-004 rules B-1 through B-8)
    IdFormatRule(code="INVALID_BRICK_ID", spec="S-035", artifact_type="brick",
                 pattern=r"^B-[a-z0-9-]+$", normalizer=normalize_brick_id),
    PartitionRule(code="PARTITION_VIOLATION", spec="S-022", universe="functions",
                  partitions="bricks", expansion=expand_brick_units),
    DAGRule(code="BRICK_CYCLE", spec="S-039", node_type="brick",
            edge_derivation=derive_brick_dependencies),
    LayerConstraintRule(code="LAYER_VIOLATION", spec="S-038", node_type="brick",
                        layer_field="layer", edge_derivation=derive_brick_dependencies),

    # Tower validation (A-004 rules T-1 through T-3)
    IdFormatRule(code="INVALID_TOWER_ID", spec="S-087", artifact_type="tower",
                 pattern=r"^[a-z][a-z0-9-]*$", normalizer=None),
    IsolationRule(code="TOWER_VIOLATION", spec="S-088", node_type="brick",
                  boundary_field="tower", edge_derivation=derive_brick_dependencies),
]

RULES_BY_CODE = {r.code: r for r in RULES}
RULES_BY_SPEC = defaultdict(list)
for r in RULES:
    RULES_BY_SPEC[r.spec].append(r)
```

---

## Fix Action Primitives

Rules compose these atomic operations:

### Frontmatter Actions

| Action | Parameters | Effect |
|--------|------------|--------|
| `set_field` | target, field, value | Set field to value |
| `add_field_value` | target, field, value | Append to array field |
| `remove_field_value` | target, field, value | Remove from array field |
| `delete_field` | target, field | Remove field entirely |

### File Actions

| Action | Parameters | Effect |
|--------|------------|--------|
| `rename_file` | old_path, new_path | Rename file |
| `sync_title` | target, source ("h1" or "frontmatter") | Sync title between H1 and frontmatter |
| `set_h1` | target, value | Set H1 heading |

### Decorator Actions (Future)

| Action | Parameters | Effect |
|--------|------------|--------|
| `change_decorator` | file, line, old_ref, new_ref | Change decorator reference |
| `remove_decorator` | file, line | Remove decorator |

---

## Validation Context

Rules operate on a read-only context:

```python
@dataclass
class ValidationContext:
    """Immutable snapshot of project state for validation."""

    # Loaded artifacts by type
    specifications: dict[str, Artifact]
    outcomes: dict[str, Artifact]
    architectures: dict[str, Artifact]
    charter: Artifact | None
    bricks: list[Brick]

    # Graphs
    impl_graph: Graph | None

    # Lookup helpers
    def get(self, artifact_id: str) -> Artifact | None: ...
    def of_type(self, artifact_type: str) -> Iterator[Artifact]: ...
    def exists(self, artifact_id: str) -> bool: ...
```

---

## Mend Context

Mend operates on a mutable context:

```python
class MendContext:
    """Mutable context for applying fixes."""

    def set_field(self, artifact_id: str, field: str, value: Any) -> None: ...
    def add_to_field(self, artifact_id: str, field: str, value: Any) -> None: ...
    def remove_from_field(self, artifact_id: str, field: str, value: Any) -> None: ...
    def delete_field(self, artifact_id: str, field: str) -> None: ...
    def rename_file(self, old_path: Path, new_path: Path) -> None: ...
    def set_h1(self, artifact_id: str, title: str) -> None: ...

    def commit(self) -> list[Change]: ...
```

Key behaviors:
- Batches changes, writes on `commit()`
- Preserves YAML formatting where possible
- Git-aware file renames
- Returns list of changes made

---

## CLI Changes

### `jigy validate -j`

JSON output gains `fix` field per error:

```json
{
  "errors": [
    {
      "id": "err_001",
      "code": "ORPHAN_OUTCOME_SPEC_LINK",
      "message": "O-001 references S-034, but S-034 doesn't reference O-001",
      "file": "jig/outcomes/O-001_Easy_Onboarding.md",
      "context": {
        "forward": {"from": "O-001", "field": "specifications", "to": "S-034"},
        "reverse": {"from": "S-034", "field": "outcomes", "to": null}
      },
      "fix": {
        "action": "add_field_value",
        "target": "S-034",
        "field": "outcomes",
        "value": "???"
      },
      "auto": false,
      "suggestions": ["O-001"]
    }
  ],
  "summary": {
    "total": 5,
    "auto_fixable": 3,
    "manual": 2
  }
}
```

### `jigy mend` (New Command)

```bash
# Apply all auto-fixable errors
jigy mend --auto

# Apply explicit fixes from file
jigy mend --apply fixes.json

# Both: auto-fix + explicit
jigy mend --auto --apply fixes.json

# Dry run: show what would change
jigy mend --dry-run --auto
jigy mend --dry-run --apply fixes.json

# JSON output
jigy mend --auto -j
```

Output:
```bash
$ jigy mend --auto
Applied 3 fixes:
  ✓ err_001: Set S-034.type = "specification"
  ✓ err_002: Synced S-042 title from H1
  ✓ err_005: Renamed S-043_Foo.md → S-042_Foo.md
Skipped 2 fixes (require manual decision):
  ⊘ err_003: ORPHAN_OUTCOME_SPEC_LINK (fill in value)
  ⊘ err_004: PARTITION_GAP (assign to brick)

$ jigy mend --apply fixes.json
Applied 2 fixes:
  ✓ err_003: Added O-001 to S-034.outcomes
  ✓ err_004: Added F-auth.login to B-auth.units
```

---

## Implementation Architecture

### File Structure

```
src/jig/
├── rules/
│   ├── __init__.py          # Rule protocol, registry
│   ├── base.py              # Base rule classes
│   ├── types/
│   │   ├── __init__.py
│   │   ├── required_field.py
│   │   ├── id_format.py
│   │   ├── uniqueness.py
│   │   ├── filename_sync.py
│   │   ├── header_sync.py
│   │   ├── excluded_field.py
│   │   ├── field_type.py
│   │   ├── field_value.py
│   │   ├── reference_validity.py
│   │   ├── bidirectional_link.py
│   │   ├── coverage.py
│   │   ├── partition.py
│   │   ├── dag.py
│   │   ├── layer_constraint.py
│   │   └── isolation.py
│   ├── registry.py          # RULES list, RULES_BY_CODE
│   └── context.py           # ValidationContext, MendContext
├── validation/
│   ├── __init__.py
│   ├── models.py            # ValidationError, ValidationResult (keep)
│   ├── engine.py            # New: runs rules, produces results
│   └── reporting.py         # Keep: output formatting
├── mend/
│   ├── __init__.py
│   ├── engine.py            # Mend execution engine
│   ├── actions.py           # Fix action implementations
│   └── yaml_editor.py       # YAML-preserving frontmatter editor
└── cli/
    ├── validate.py          # Updated: use rule engine
    └── mend.py              # New: mend command
```

### Rule Protocol

```python
from typing import Protocol, Iterator
from dataclasses import dataclass

@dataclass
class Violation:
    """A detected rule violation."""
    rule_code: str
    artifact_id: str
    file: str
    line: int | None
    message: str
    context: dict  # Rule-specific data: used for fix generation AND error ID stability

@dataclass
class Fix:
    """A fix template for a violation."""
    action: str
    target: str
    params: dict
    auto: bool
    suggestions: list[str]

class Rule(Protocol):
    code: str
    spec: str  # A-004 spec this rule enforces, e.g., "S-072"

    def violations(self, ctx: ValidationContext) -> Iterator[Violation]: ...
    def fix_for(self, v: Violation) -> Fix: ...
    def apply(self, fix: Fix, ctx: MendContext) -> None: ...
```

### Rule Type Base Classes

```python
@dataclass
class RequiredFieldRule:
    code: str
    spec: str  # A-004 spec reference for traceability
    artifact_type: str
    field: str
    inferrable: Callable[[ValidationContext, Artifact], Any] | None = None

    def violations(self, ctx: ValidationContext) -> Iterator[Violation]:
        for artifact in ctx.of_type(self.artifact_type):
            if self.field not in artifact.frontmatter:
                # Compute inferred value during violation detection
                inferred = None
                if self.inferrable:
                    inferred = self.inferrable(ctx, artifact)
                yield Violation(
                    rule_code=self.code,
                    artifact_id=artifact.id,
                    file=artifact.file,
                    line=None,
                    message=f"Missing required field: '{self.field}'",
                    context={
                        "artifact_type": self.artifact_type,
                        "field": self.field,
                        "inferred_value": inferred,
                    },
                )

    def fix_for(self, v: Violation) -> Fix:
        # Extract pre-computed inferred value from context
        inferred = v.context.get("inferred_value")
        value = inferred if inferred is not None else "???"
        auto = inferred is not None
        return Fix(
            action="set_field",
            target=v.artifact_id,
            params={"field": self.field, "value": value},
            auto=auto,
            suggestions=[],
        )

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        ctx.set_field(fix.target, fix.params["field"], fix.params["value"])
```

---

## Migration Strategy

### Phase 1: Infrastructure (No Behavior Change)

1. Create `src/jig/rules/` module structure
2. Implement `ValidationContext` loader
3. Implement `MendContext` with YAML-preserving editor
4. Implement fix action primitives
5. Add `Fix` field to `ValidationError` model

**Deliverable:** Infrastructure ready, existing validation unchanged.

### Phase 2: Rule Types

1. Implement each rule type class
2. Unit test each rule type in isolation
3. Create `RULES` registry with all current validations

**Deliverable:** All rule types implemented and tested.

### Phase 3: Validation Engine

1. Create `validation/engine.py` that runs rules
2. Wire `jigy validate` to use rule engine
3. Ensure identical error output (regression test)
4. Add `-j` output with fix templates

**Deliverable:** `jigy validate` produces fix templates.

### Phase 4: Mend Command

1. Implement `mend/engine.py`
2. Implement `cli/mend.py` with `--auto` and `--apply`
3. Integration tests for validate → mend → validate cycle

**Deliverable:** Full validate/mend workflow operational.

### Phase 5: Cleanup

1. Remove old `validation/intent.py` functions (replaced by rules)
2. Remove old `validation/bricks.py` functions (replaced by rules)
3. Update documentation

**Deliverable:** Clean codebase with single validation path.

---

## Testing Strategy

### Rule Type Tests

Each rule type has isolated tests:

```python
def test_required_field_rule_detects_missing():
    rule = RequiredFieldRule(code="TEST", artifact_type="specification", field="title")
    ctx = make_context(specs=[{"id": "S-001"}])  # no title
    violations = list(rule.violations(ctx))
    assert len(violations) == 1
    assert violations[0].rule_code == "TEST"

def test_required_field_rule_fix_template():
    rule = RequiredFieldRule(...)
    violation = Violation(...)
    fix = rule.fix_for(violation)
    assert fix.action == "set_field"
    assert fix.params["field"] == "title"
    assert fix.auto == False
```

### Engine Tests

```python
def test_validation_engine_runs_all_rules():
    ctx = make_context(...)
    results = validate(ctx)
    # Assert expected errors

def test_mend_engine_applies_fixes():
    ctx = make_mend_context(...)
    fixes = [Fix(...)]
    apply_fixes(fixes, ctx)
    ctx.commit()
    # Assert file changes
```

### Integration Tests

```python
def test_validate_mend_cycle():
    # Setup: create files with issues
    # Run validate, capture errors
    # Fill in fixes (auto where possible)
    # Run mend
    # Run validate again
    # Assert no errors
```

### Regression Tests

```python
def test_validation_output_matches_legacy():
    # Run new engine, run old functions
    # Compare error sets (ignoring order)
```

---

## Affected Bricks

| Brick | Changes |
|-------|---------|
| `B-validation` | Major rewrite: rules engine replaces procedural functions |
| `B-cli` | Add `mend.py`, update `validate.py` |
| New: `B-rules` | New brick for rule types and registry |
| New: `B-mend` | New brick for mend engine and YAML editor |

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| YAML formatting corruption | Medium | High | Preserve-formatting YAML editor with extensive tests |
| Rule type explosion | Low | Medium | Most rules fit 15 types; add new types sparingly |
| Performance regression | Low | Low | Rules are O(n) same as current; profile if concerned |
| Missing edge cases | Medium | Medium | Regression tests against current validation output |

---

## Success Criteria

1. `jigy validate -j` outputs structured errors with fix templates
2. `jigy mend --auto` fixes all auto-fixable issues
3. `jigy mend --apply` applies agent-filled fix templates
4. Zero regression in validation coverage
5. All existing tests pass
6. New rule types are unit-tested in isolation

---

## Out of Scope

- Body structure validation (spec Statement/Invariants/Verification sections)
- Decorator modification actions (AST-level Python editing)
- Interactive `mend --interactive` mode
- Undo/rollback functionality
- Conflict detection (file changed since validate)

---

## Design Decisions

### D-1: Context propagation for `fix_for()`

**Decision:** Embed computed values in `Violation.context` during detection.

Rules compute everything needed during `violations()` and store it in `Violation.context`. The `fix_for()` method extracts from context rather than requiring `ValidationContext` as a parameter.

**Rationale:** Keeps the API clean. Violations are self-contained and serializable. No protocol change needed.

**Example:** See updated `RequiredFieldRule` implementation above.

---

### D-2: Rule ordering and cascading errors

**Decision:** Run all rules, report all errors. Accept cascading errors.

The engine runs every rule regardless of earlier failures. Users fix iteratively via `validate` → `mend --auto` → `validate` loop. This matches ESLint's model.

**Rationale:** Dependency-aware ordering adds complexity for marginal UX gain. Agents iterate anyway. Cascading errors self-resolve after fixing root causes.

**Future option:** If too noisy, add optional `phase: int` to rules (0=schema, 1=format, 2=refs, 3=structural). Engine runs phases sequentially, skips artifact in later phases if fatal error. But start without this.

---

### D-3: Conflicting fixes on same artifact

**Decision:** Mend iterates to fixed point.

`mend --auto` applies all auto-fixes, then re-validates. If new auto-fixable errors appear (because state changed), apply those too. Repeat until stable or max iterations (3) reached.

```python
def mend_auto(ctx, max_iterations=3):
    for _ in range(max_iterations):
        errors = validate(ctx)
        auto_fixes = [e.fix for e in errors if e.fix.auto]
        if not auto_fixes:
            break
        for fix in auto_fixes:
            apply(fix, ctx)
        ctx.commit()
```

**Rationale:** Handles dependent fixes naturally (e.g., `IdFormatRule` normalizes ID, then `FilenameSyncRule` sees new ID on next pass).

---

### D-4: Error ID generation

**Decision:** Hash of `(rule_code, artifact_id, context_discriminator)`.

```python
def error_id(violation: Violation) -> str:
    context_str = json.dumps(violation.context, sort_keys=True)
    return hashlib.sha256(
        f"{violation.rule_code}:{violation.artifact_id}:{context_str}".encode()
    ).hexdigest()[:12]
```

Each rule type naturally populates context with its discriminator:
- `RequiredFieldRule`: `{"field": "title"}`
- `DAGRule`: `{"cycle": ["B-a", "B-b", "B-c"]}`
- `BidirectionalLinkRule`: `{"forward": "O-001", "reverse": "S-034"}`

**Rationale:** Stable across runs. Handles rules without `field` param. Handles multiple violations from same rule on same artifact.

---

### D-5: Decorator reference errors (no executable fix for v1)

**Decision:** Report-only with descriptive fix template. No executable action.

Decorator reference errors get `auto: false` with a fix template that describes what to do, but mend engine skips unimplemented actions gracefully.

```python
Fix(
    action="change_decorator",  # action type exists but not yet executable
    target="src/foo.py:42",
    params={"old_ref": "S-999", "new_ref": "???"},
    auto=False,
    suggestions=["S-001", "S-002"]
)
```

**Rationale:** Agent reads fix template, manually edits decorator, re-validates. Decorator actions can be implemented later without changing rule architecture.

---

### D-6: Git commits

**Decision:** Mend does not create git commits.

Mend changes files; commit is a separate concern. Users/agents run `git add && git commit` after mend if desired.

**Rationale:** Separation of concerns. Users may want to review changes before committing. Agents have their own commit workflows.

---

### D-7: Rule ↔ Spec traceability

**Decision:** Rules include `spec` field referencing A-004 spec they enforce.

```python
class Rule(Protocol):
    code: str
    spec: str  # e.g., "S-018", "S-072"
```

Registry provides `RULES_BY_SPEC` index for querying which rules enforce a given spec.

**Rationale:** Maintains traceability from A-004's logical rules to E012's implementation objects. Enables queries like "which rules enforce S-022?"

---

## JIG Document Updates

This scope requires updates to JIG architecture documents:

### A-004 (Validation Architecture) — Major Rewrite

A-004 currently documents procedural validation functions. Must be rewritten to describe rules-based architecture:

| Section | Change |
|---------|--------|
| Domain Overview table | Replace function column with rule type column |
| Per-domain sections | Replace "Function" subsections with "Rule Instances" |
| Execution Model | Describe rule engine, iteration to fixed point |
| New: Mend Architecture | Add section for mend command, fix actions, MendContext |
| New: Fix Action Primitives | Document frontmatter/file/decorator actions |
| Spec Traceability Matrix | Rewrite: Rule → Spec → Rule Instance |
| Validation Order | Update to reflect flat rule list + cascading errors |

**Key structural change:** A-004 currently maps A-004 rules (C-1, B-1, etc.) → specs → functions. New mapping: A-004 rules → specs → rule instances (with `spec` field back-reference).

### A-001 (JIG Core Architecture) — No Changes

A-001 defines WHAT the structure IS. Lines 156-161 already delegate validation behavior to A-004. No changes needed.

### Charter — No Changes

Charter defines goals, not implementation. No changes needed.

### New Specs Required

The mend command and rules engine need specification coverage:

| Spec | Description | Covers |
|------|-------------|--------|
| S-NEW-1 | Mend command applies auto-fixable errors | `jigy mend --auto` |
| S-NEW-2 | Mend command applies explicit fixes | `jigy mend --apply` |
| S-NEW-3 | Validation outputs fix templates | `-j` output format |
| S-NEW-4 | Fix templates are structurally tied to rules | Rule/Fix coupling |
| S-NEW-5 | Mend iterates to fixed point | D-3 behavior |

These specs should be created during JIGPLAN phase, assigned to appropriate outcomes (likely O-NEW for "Automated Repair" or similar).

---

## References

- [[E008_CONCEPT_Validate_Mend_Contract]] — Original concept for fix templates
- [[E007_CONCEPT_Context_Command_Design]] — Related context command
- [[DJ001_CONCEPT_CLI_Design_Manifesto]] — Output format principles
- Terraform Plan/Apply — Inspiration for structured change plans
- ESLint Rule Architecture — Each rule self-contained with check + fix
