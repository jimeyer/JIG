---
title: "SCOPE: Wire Up Validation Functions and Create A-004"
type: scope
status: implemented
decision: "All 5 validation functions wired into CLI commands"
created: 1736206800
created_human: "2026-01-06 16:40 CST"
updated: 1736217600
updated_human: "2026-01-06 19:40 CST"
parent: "[[C017_PROBLEM_Validation_Functions_Not_Wired_Up]]"
children: ["[[C019_JIGPLAN_Wire_Up_Validation_Functions]]"]
---
# SCOPE: Wire Up Validation Functions and Create A-004

**ID:** C018
**Status:** Active
**Date:** 2026-01-06
**Problem:** C017_PROBLEM_Validation_Functions_Not_Wired_Up.md

---

## Executive Summary

This scope addresses two related issues:

1. **Bug:** Four validation functions exist but are never called from CLI commands (decorator validation is already wired)
2. **Architecture Gap:** A-001 defines validation rules without spec traceability, and mixes concerns (hierarchy structure + validation)

**Solution:**

- Create **A-004_Validation_Architecture.md** as the authoritative reference for all validation
- Remove validation rules from A-001 (superseded by A-004)
- Update A-001's `constrains` list to remove validation specs (moved to A-004)
- Wire the 4 dead validation functions into CLI commands
- Add integration tests that prove validation actually runs

---

## Investigation Findings (2026-01-06)

Pre-implementation audit revealed several discrepancies that must be addressed:

### Finding 1: Decorator Validation Already Wired

**Status:** NOT a dead function

`validate_decorator_files()` is ALREADY called in `validate_intent_command()` at `src/jig/cli/validate.py:73-84`. This removes it from scope.

**Actual dead functions (4, not 5):**
1. `validate_charter_file()` — intent.py:788
2. `validate_goal_references()` — intent.py:968
3. `validate_architecture_files()` — intent.py:1051
4. `validate_tower_format()` — bricks.py:875
5. `validate_tower_isolation()` — bricks.py:1011

### Finding 2: `validate_goal_references` Signature Mismatch

**A-004 documents:**
```python
validate_goal_references(
    outcome_dir: Path | None,
    arch_dir: Path | None,
    charter_goals: set[str]
) -> ValidationResult
```

**Actual implementation:**
```python
validate_goal_references(
    charter_path: Path,
    outcome_dir: Path,
    architecture_dir: Optional[Path] = None,
) -> ValidationResult
```

**Resolution:** The actual function loads goals internally from charter_path. This is self-contained and better. **Update A-004 to match actual signature** and adjust B.1 wiring code accordingly.

### Finding 3: Specs S-080 through S-085 Confirmed

All specs exist:
- S-080_Charter_Node_In_Intent_Graph.md
- S-081_Goal_Nodes_In_Intent_Graph.md
- S-082_Architecture_Nodes_In_Intent_Graph.md
- S-083_Defines_Goal_Edges.md
- S-084_Supports_Goal_Edges.md
- S-085_Constrains_Edges.md

### Finding 4: Test Infrastructure Pattern

Existing tests use `CliRunner` + `runner.isolated_filesystem()` pattern (see `tests/cli/test_validate.py`). No `tmp_jig_project` fixture needed.

**Pattern:**
```python
runner = CliRunner()
with runner.isolated_filesystem():
    Path("jig/specifications").mkdir(parents=True)
    # ... create test files ...
    result = runner.invoke(cli, ["validate"])
```

### Finding 5: Helper `_get_charter_goals` May Be Unnecessary

Since `validate_goal_references` loads goals internally, we may not need `_get_charter_goals()` for that function. However, `validate_architecture_files` DOES require `charter_goals: set[str]` as a parameter, so the helper is still needed.

---

## PART A: Architecture Changes

### A.1 Create A-004 Validation Architecture

**File:** `jig/architecture/A-004_Validation_Architecture.md`

**Status:** Draft created (needs finalization)

**A-004 provides:**

| Feature | Benefit |
|---------|---------|
| All validation rules in one place | Single source of truth |
| Rule→Spec→Function traceability | G-005 compliance |
| Execution model documented | Clear contract for what validates when |
| Domain separation | Charter, Architecture, Outcome, Spec, Brick, Tower, Decorator |

**A-004 constrains:** S-016, S-017, S-018, S-020, S-023, S-024, S-025, S-030, S-034, S-035, S-038, S-039, S-042, S-043, S-072, S-073, S-074, S-075, S-076, S-077, S-078, S-079, S-086, S-087, S-088, S-089

### A.2 Update A-001

**File:** `jig/architecture/A-001_JIG_Core_Architecture.md`

**Changes:**

1. **Remove "Validation Rules" section** (lines 157-197) — superseded by A-004
2. **Expand `constrains` list** — add intent graph specs (S-080-S-085) that implement A-001's hierarchy
3. **Add reference to A-004** — note that validation is governed by A-004

**Before:**
```yaml
constrains: [S-072, S-073, S-074, S-075, S-076, S-077, S-078, S-079, S-086, S-087, S-088]
```

**After:**
```yaml
constrains: [S-072, S-073, S-074, S-075, S-076, S-077, S-078, S-079, S-080, S-081, S-082, S-083, S-084, S-085, S-086, S-087, S-088]
```

**Rationale:** A-001 defines the intent hierarchy structure. Specs S-072-S-079 define Charter/Architecture structure, S-080-S-085 define how the intent graph represents that structure, S-086-S-088 define tower structure. Some specs (S-072-S-079, S-086-S-088) are ALSO constrained by A-004 for their validation aspects — that's intentional overlap.

**Add to A-001 body (replacing Validation Rules section):**
```markdown
## Validation

Validation of JIG artifacts is governed by A-004 (Validation Architecture).
See A-004 for the complete validation model, rules, and spec mappings.

This document (A-001) defines WHAT the structure IS. A-004 defines HOW to VALIDATE that structure.
```

### A.3 Finalize A-004

The draft A-004 needs:

1. **Status change:** `draft` → `active`
2. **Review:** Ensure all rules match actual function behavior
3. **Spec verification:** Confirm spec IDs in `constrains` list exist

---

## PART B: Wire Validation Functions

### B.1 Intent Validation Functions

**File:** `src/jig/cli/validate.py`

**Function:** `validate_intent_command()`

#### Add Imports

```python
from jig.validation.intent import (
    validate_charter_file,           # ADD
    validate_goal_references,        # ADD
    validate_architecture_files,     # ADD
    validate_decorator_files,
    validate_outcome_completeness,
    validate_outcome_files,
    validate_specification_coverage,
    validate_specification_files,
)
```

#### Add Charter Validation

```python
# Validate charter (per A-004 rules C-1 through C-4)
charter_path = config.paths.charter
if charter_path.exists():
    results["charter"] = validate_charter_file(charter_path)
    charter_goals = _get_charter_goals(charter_path)
else:
    results["charter"] = ValidationResult(passed=True, phase_name="charter", items_checked=0)
    charter_goals = set()
```

#### Add Architecture Validation

```python
# Validate architecture files (per A-004 rules A-1 through A-7)
arch_dir = config.paths.architecture
if arch_dir.exists() and charter_goals:
    spec_ids = _get_all_spec_ids(spec_dir) if spec_dir.exists() else set()
    results["architecture"] = validate_architecture_files(arch_dir, charter_goals, spec_ids)
else:
    results["architecture"] = ValidationResult(passed=True, phase_name="architecture", items_checked=0)
```

#### Add Goal Reference Validation

**NOTE:** Actual function signature differs from A-004 draft. Use actual signature:

```python
# Validate goal references (per A-004 rules GR-1 and GR-2)
# NOTE: Function loads charter goals internally from charter_path
charter_path = config.paths.charter
if charter_path.exists() and outcome_dir.exists():
    results["goal_references"] = validate_goal_references(
        charter_path,
        outcome_dir,
        arch_dir if arch_dir.exists() else None,
    )
else:
    results["goal_references"] = ValidationResult(passed=True, phase_name="goal references", items_checked=0)
```

#### Add Helper Functions

```python
def _get_charter_goals(charter_path: Path) -> set[str]:
    """Extract goal IDs from Charter frontmatter."""
    import yaml
    content = charter_path.read_text()
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            return set(frontmatter.get("defines_goals", []))
    return set()


def _get_all_spec_ids(spec_dir: Path) -> set[str]:
    """Get all specification IDs from spec directory."""
    import yaml
    spec_ids = set()
    for spec_file in spec_dir.glob("S-*.md"):
        content = spec_file.read_text()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                if "id" in frontmatter:
                    spec_ids.add(frontmatter["id"])
    return spec_ids
```

### B.2 Brick Validation Functions

**File:** `src/jig/cli/validate.py`

**Function:** `validate_bricks_command()`

#### Add Imports

```python
from jig.validation.bricks import (
    validate_brick_cycles,
    validate_brick_definitions,
    validate_brick_layer_constraints,
    validate_brick_partition,
    validate_tower_format,      # ADD
    validate_tower_isolation,   # ADD
)
```

#### Add Tower Format Validation

```python
# Validate tower format (per A-004 rule T-1)
tower_format_result = validate_tower_format(bricks_file)
results["tower_format"] = tower_format_result
```

#### Add Tower Isolation Validation

```python
# Validate tower isolation (per A-004 rules T-2 and T-3)
if _has_towers(bricks_file):
    results["tower_isolation"] = validate_tower_isolation(bricks_file, impl_graph)
```

#### Add Helper Function

```python
def _has_towers(bricks_file: Path) -> bool:
    """Check if any brick declares a tower field."""
    import yaml
    if not bricks_file.exists():
        return False
    content = yaml.safe_load(bricks_file.read_text())
    bricks = content.get("bricks", [])
    return any("tower" in brick for brick in bricks)
```

---

## PART C: Integration Tests

**File:** `tests/cli/test_validate_integration.py` (new)

Tests that **prove validation actually runs** by deliberately breaking artifacts and verifying errors are caught.

**Pattern:** Use `CliRunner` + `runner.isolated_filesystem()` (per Finding 4).

### C.1 Charter Validation Test

```python
from pathlib import Path
from click.testing import CliRunner
import jig
from jig.cli.main import cli

@jig.verifies("S-072", "S-073", "S-074")
def test_validate_catches_invalid_charter():
    """Verify jigy validate actually runs charter validation."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("jig").mkdir()
        (Path("jig") / "Charter.md").write_text(
            "---\nid: Charter\ntype: charter\n---\n# Charter\n"
        )
        # Missing defines_goals

        result = runner.invoke(cli, ["validate"])

        assert result.exit_code != 0
        assert "defines_goals" in result.output.lower() or "charter" in result.output.lower()
```

### C.2 Architecture Validation Test

```python
@jig.verifies("S-076", "S-077", "S-078", "S-079")
def test_validate_catches_invalid_architecture():
    """Verify jigy validate actually runs architecture validation."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Need valid charter first (architecture validation needs charter goals)
        Path("jig").mkdir()
        (Path("jig") / "Charter.md").write_text(
            "---\nid: Charter\ntype: charter\ndefines_goals: [G-001]\n---\n"
            "# Charter\n\n### G-001: Test Goal\n"
        )

        arch_dir = Path("jig/architecture")
        arch_dir.mkdir()
        (arch_dir / "bad_name.md").write_text(
            "---\nid: A-001\ntype: architecture\ntitle: Test\n"
            "status: active\nsupports_goals: [G-001]\n---\n# Test\n"
        )
        # Filename doesn't match A-{NNN}_{Title}.md pattern

        result = runner.invoke(cli, ["validate"])

        assert result.exit_code != 0
        assert "filename" in result.output.lower() or "A-001" in result.output
```

### C.3 Goal Reference Validation Test

```python
@jig.verifies("S-075")
def test_validate_catches_invalid_goal_reference():
    """Verify jigy validate catches invalid goal references."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("jig").mkdir()
        # Charter defines G-001 only
        (Path("jig") / "Charter.md").write_text(
            "---\nid: Charter\ntype: charter\ndefines_goals: [G-001]\n---\n"
            "# Charter\n\n### G-001: Test Goal\n"
        )

        outcome_dir = Path("jig/outcomes")
        outcome_dir.mkdir()
        (outcome_dir / "O-001_Test.md").write_text(
            "---\nid: O-001\ntype: outcome\ntitle: Test\n"
            "supports_goals: [G-999]\nspecifies: [S-001]\n---\n# Test\n"
        )
        # G-999 doesn't exist in Charter

        result = runner.invoke(cli, ["validate"])

        assert result.exit_code != 0
        assert "G-999" in result.output
```

### C.4 Tower Validation Test

```python
@jig.verifies("S-087", "S-088", "S-089")
def test_validate_catches_invalid_tower_format():
    """Verify jigy validate bricks catches invalid tower format."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("jig").mkdir()
        Path("jig/generated").mkdir(parents=True)
        # Need mock implementation graph
        (Path("jig/generated") / "implementation-graph.ndjson").write_text(
            '{"id": "M-test", "type": "module"}\n'
        )

        (Path("jig") / "bricks.yaml").write_text(
            "- id: B-test\n"
            "  name: Test\n"
            "  layer: 0\n"
            "  tower: InvalidCamelCase\n"
            "  units:\n"
            "    - M-test\n"
        )
        # Tower should be kebab-case

        result = runner.invoke(cli, ["--no-rebuild", "validate", "bricks"])

        assert result.exit_code != 0
        assert "tower" in result.output.lower() or "kebab" in result.output.lower()
```

---

## PART D: Verification

### D.1 Run on JIG Repo

```bash
jigy rebuild && jigy validate
# Must pass with no errors (no false positives)
```

### D.2 Verify A-004 Rules Are Enforced

For each domain, create a deliberately invalid artifact and verify it's caught:

| Domain | Break | Expected Error |
|--------|-------|----------------|
| Charter | Remove `defines_goals` | "defines_goals" missing |
| Architecture | Bad filename | Filename pattern error |
| Goal Reference | Reference G-999 | Invalid goal reference |
| Tower | Use CamelCase tower | Kebab-case required |

### D.3 Verify A-004 Traceability

```bash
# Every rule in A-004 should trace to a spec, and every spec to a function
grep -E "^\\| [A-Z]+-[0-9]+" jig/architecture/A-004_Validation_Architecture.md
```

---

## Work Units

### WU-1: Audit and Finalize A-004 ✓ COMPLETED

**Scope:** Audit function behavior against A-004 rules, then activate A-004

**Status:** Completed 2026-01-06

**Actions Taken:**

1. **Fixed `validate_goal_references` signature** — Updated A-004 to match actual implementation:
   ```python
   validate_goal_references(charter_path: Path, outcome_dir: Path, architecture_dir: Path | None = None)
   ```

2. **Verified all other function signatures match** — All 13 validation functions audited, signatures correct.

3. **Fixed non-existent spec references** — A-004 originally referenced specs that don't exist:
   | Original | Replaced With | Reason |
   |----------|---------------|--------|
   | S-016, S-017 | S-018 | Specification validation covered by S-018 |
   | S-030, S-034 | S-021, S-022 | Brick validation covered by S-021 (definition) and S-022 (partition) |

4. **Updated constrains list** — Changed from:
   ```
   [S-016, S-017, S-018, S-020, S-023, S-024, S-025, S-030, S-034, S-035, ...]
   ```
   To:
   ```
   [S-018, S-020, S-021, S-022, S-023, S-024, S-025, S-035, ...]
   ```

5. **Updated Domain Overview, Rules tables, and Traceability Matrix** to use correct spec IDs.

6. **Reduced Specification rules from 6 to 5** — Removed redundant status rule (already covered by S-018).

7. **Changed status from `draft` to `active`** and added changelog entry.

8. **Verified `jigy validate intent` passes** — No validation errors.

**Acceptance Criteria:**
- [x] A-004 `validate_goal_references` signature fixed
- [x] Each validation function audited against A-004 rules
- [x] All spec IDs in `constrains` verified to exist
- [x] A-004 status changed from `draft` to `active`

---

### WU-2: Update A-001

**Scope:** Remove validation rules section, expand constrains, add A-004 reference

**Acceptance Criteria:**
- [ ] "Validation Rules" section (lines 157-197) removed from A-001
- [ ] `constrains` list expanded to include S-080-S-085 (intent graph specs)
- [ ] Reference to A-004 added in place of removed section
- [ ] `jigy validate` still passes

---

### WU-3: Wire Charter Validation

**Scope:** Add `validate_charter_file()` call to `validate_intent_command()`

**Acceptance Criteria:**
- [ ] Function imported
- [ ] Function called in correct order (first, to extract goals)
- [ ] Helper `_get_charter_goals()` added
- [ ] Integration test proves it runs

---

### WU-4: Wire Architecture Validation

**Scope:** Add `validate_architecture_files()` call to `validate_intent_command()`

**Acceptance Criteria:**
- [ ] Function imported
- [ ] Function called with charter_goals and spec_ids
- [ ] Helper `_get_all_spec_ids()` added
- [ ] Integration test proves it runs

---

### WU-5: Wire Goal Reference Validation

**Scope:** Add `validate_goal_references()` call to `validate_intent_command()`

**NOTE:** Actual function signature is `(charter_path, outcome_dir, architecture_dir)` — it loads goals internally. See Finding 2.

**Acceptance Criteria:**
- [ ] Function imported
- [ ] Function called with charter_path, outcome_dir, arch_dir (actual signature)
- [ ] A-004 updated to document actual signature
- [ ] Integration test proves it runs

---

### WU-6: Wire Tower Validation

**Scope:** Add `validate_tower_format()` and `validate_tower_isolation()` calls

**Acceptance Criteria:**
- [ ] Both functions imported
- [ ] `validate_tower_format()` always called
- [ ] `validate_tower_isolation()` called only if towers declared
- [ ] Helper `_has_towers()` added
- [ ] Integration test proves it runs

---

### WU-7: End-to-End Verification

**Scope:** Verify complete validation suite works

**Acceptance Criteria:**
- [ ] `jigy validate` passes on JIG repo
- [ ] `jigy validate` passes on ASE-A repo (if available)
- [ ] All integration tests pass
- [ ] All A-004 rules map to running code

---

## Success Criteria

| Criterion | Metric |
|-----------|--------|
| **Architecture** | A-004 is active and authoritative for validation |
| **A-001 Cleanup** | A-001 no longer duplicates validation rules |
| **Functional** | All 4 dead validation functions are called from CLI (decorator already wired) |
| **Testable** | Integration tests prove validation runs |
| **Traceable** | Every A-004 rule traces to spec and function |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| New validation catches existing errors | Run on JIG/ASE repos first, fix issues |
| A-004 rules don't match function behavior | Audit function code during WU-1 |
| Helper functions duplicate existing logic | Search for existing helpers before adding |
| Breaking change to A-001 | A-001 changes are additive (reference to A-004) + removal (validation section) |

---

## Decisions Made

| Question | Decision |
|----------|----------|
| **A-001 constrains list** | A-001 keeps and expands constrains (adds S-080-S-085). Some specs constrained by both A-001 and A-004 — intentional overlap. |
| **Decorator validation** | Added to A-004 as "Decorator Validation" domain with rules D-1 through D-3. |
| **S-043 (Specification Coverage)** | Changed from SHOULD to SHALL. Produces errors (fail validation). |
| **Existing validation specs** | No change. A points to S, but S does not point back to A. |
| **Audit before wiring** | Yes. WU-1 includes audit of function behavior vs A-004 rules. |
| **Decorator validation** | Already wired (Finding 1). Scope reduced from 5 to 4 functions. |
| **Goal references signature** | Keep actual signature (self-contained). Update A-004 to match (Finding 2). |
| **Test pattern** | Use `CliRunner` + `isolated_filesystem()` per existing tests (Finding 4). |
| **A-004 spec references** | Fixed non-existent specs: S-016/S-017→S-018, S-030/S-034→S-021/S-022. Specs already covered functionality. |

## Open Questions

*None remaining — WU-1 complete, ready to proceed with WU-2 (update A-001).*

---

## References

- **Problem:** C017_PROBLEM_Validation_Functions_Not_Wired_Up.md
- **Original Implementation:** C008_PLAN_Extended-Intent-Hierarchy-and-Towers.md
- **New Architecture:** A-004_Validation_Architecture.md
- **Updated Architecture:** A-001_JIG_Core_Architecture.md
