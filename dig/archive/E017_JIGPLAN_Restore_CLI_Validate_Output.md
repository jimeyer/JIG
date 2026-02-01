---
title: JIGPLAN Restore CLI Validate Output
type: jigplan
status: implemented
decision: completed
created: 1737234600
created_human: 2026-01-18 15:10 CST
parent: "[[E016_SCOPE_Restore_CLI_Validate_Output_Per_E005]]"
children: ["[[E018_PLAN_Restore_CLI_Validate_Output]]"]
---
# JIGPLAN Restore CLI Validate Output

**SCOPE:** dig/wip/E016_SCOPE_Restore_CLI_Validate_Output_Per_E005.md
**Date:** 2026-01-18
**Status:** Draft
**Author:** Agent

---

## Summary

Restores `jigy validate` output to match E005 specification. Updates S-025 to specify human output format with artifact counts. Modifies B-validation (add counts to return value) and B-cli (format output). No new specs created - existing S-026 and S-094 already specify correct JSON/markdown formats.

---

## O/S Node Reconciliation

### Outcomes

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | O-004 | Early Error Detection | Validation command supports this outcome |
| REUSE | O-016 | CI and Tooling Integration | JSON/markdown output serves this outcome |

### Specifications

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| UPDATE | S-025 | Full Validation CLI Command | Add human output format with artifact counts |
| REUSE | S-026 | JSON Output Format for CI Integration | Already specifies correct schema with counts |
| REUSE | S-094 | Markdown Output Format | Already specifies correct format with counts |
| REUSE | S-093 | Universal Output Format Flags | Flag handling unchanged |

---

## O/S Node Details

### Nodes to UPDATE

#### S-025 Update Details

**Current acceptance criteria:**
- Command runs full validation
- Exit codes for success/failure/error
- Summary line shows "All validations passed" or "Validation failed"

**Changes:**
- ADD: Human output format section specifying one-line summary with counts
- ADD: Verbose output format section with category breakdown
- REMOVE: Generic "summary line" criterion (replaced with specific format)

**File:** `jig/specifications/S-025_Full_Validation_CLI_Command.md` (updated)

---

## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| MODIFY | B-validation | 0 | Add artifact counts to validate() return value |
| MODIFY | B-cli | 1 | Update output formatting in validate.py |
| FORBIDDEN | B-rules | 0 | Rules engine unchanged - only returns errors |
| FORBIDDEN | B-decorators | 0 | Foundation layer |
| FORBIDDEN | B-mend | 0 | Mend actions unchanged |
| UNAFFECTED | B-impl-graph | 0 | No changes needed |
| UNAFFECTED | B-intent-graph | 0 | No changes needed |

---

### Brick Details

#### B-validation Modifications

- **Current units:** M-jig.validation.models, M-jig.validation.reporting, M-jig.validation.engine
- **Add units:** (none)
- **Layer change:** (none - stays at layer 0)
- **New dependencies:** (none)
- **Changes:**
  - `validate()` in engine.py returns `counts` dict with artifact counts
  - Counts extracted from ValidationContext before returning

#### B-cli Modifications

- **Current units:** M-jig.cli.validate, M-jig.cli.main, etc.
- **Add units:** (none)
- **Layer change:** (none - stays at layer 1)
- **New dependencies:** (none)
- **Changes:**
  - `_output_human_results()` updated to include counts in success message
  - Rebuild summary combined with validation summary on one line
  - `_format_engine_results_as_json()` uses counts from result
  - `_format_engine_results_as_markdown()` uses counts from result

#### FORBIDDEN Bricks

These bricks MUST NOT be modified by any work unit:

- **B-rules** (layer 0): Rules engine returns violations only, not counts
- **B-decorators** (layer 0): Core decorator infrastructure
- **B-mend** (layer 0): Mend actions unrelated to output formatting

**Sub-agent constraint:** Any modification to FORBIDDEN bricks is an immediate escalation trigger.

---

## Layer/Dependency Analysis

### Layer Structure (Affected Bricks)

```
Layer 0: AFFECTED
  B-validation (MODIFY)
    └─► depends on: B-rules ✓

Layer 1: AFFECTED
  B-cli (MODIFY)
    └─► depends on: B-validation ✓

Layer 0: FORBIDDEN
  B-rules ← no changes
  B-decorators ← no changes
  B-mend ← no changes
```

### Dependency Constraints

- B-cli (layer 1) depends on B-validation (layer 0) - valid
- B-validation (layer 0) depends on B-rules (layer 0) - valid
- No circular dependencies

### Validation Commands

After implementation, verify with:
```bash
jigy rebuild && jigy validate
jigy layers  # Confirm layer structure unchanged
```

---

## @jig Decorator Changes

### Decorators to ADD

None - existing decorators on validate functions remain correct.

### Decorators to REMOVE

None.

### Decorators to MODIFY

| Type | Location | Old Spec | New Spec | Reason |
|------|----------|----------|----------|--------|
| implements | F-jig.cli.validate.validate_full_command | S-025 | S-025 | Spec updated (same ID) |

---

## Clean Break Actions

This work follows clean break protocol:

- [x] No backwards compatibility needed (internal output format change)
- [x] No feature flags
- [x] Tests updated to expect new output format

### Code to Delete

None - this is a modification, not replacement.

### O/S Nodes to Delete (After Validation)

None.

---

## Implementation Notes

### validate() Return Value Change

Current:
```python
return {
    "errors": [...],
    "summary": {"total": N, "auto_fixable": N, "manual": N}
}
```

After:
```python
return {
    "errors": [...],
    "summary": {"total": N, "auto_fixable": N, "manual": N},
    "counts": {
        "specs": len(ctx.specifications),
        "outcomes": len(ctx.outcomes),
        "architectures": len(ctx.architectures),
        "bricks": len(ctx.bricks),
    }
}
```

### Human Output Format

```python
def _output_human_results(result: dict, rebuild_summary: str | None = None, ...) -> None:
    if not errors:
        parts = []
        if rebuild_summary:
            parts.append(rebuild_summary.rstrip('.'))

        counts = result.get("counts", {})
        validated = []
        if counts.get("specs"):
            validated.append(f"{counts['specs']} specs")
        if counts.get("outcomes"):
            validated.append(f"{counts['outcomes']} outcomes")
        if counts.get("bricks"):
            validated.append(f"{counts['bricks']} bricks")

        if validated:
            parts.append(f"Validated {', '.join(validated)}")

        click.echo(". ".join(parts) + ".")
```

---

## Fresh Agent Review Summary

(To be populated during review)

### Review Findings

| Category | Type | Severity | Issue | Resolution |
|----------|------|----------|-------|------------|
| 1 | - | - | No issues - existing specs S-026 and S-094 already specify correct format | REUSE confirmed |
| 2 | - | - | No issues - S-025 update describes behavior, not implementation | Spec is evergreen |
| 3 | - | - | No issues - layer structure unchanged | Validated |
| 4 | - | - | No issues - existing decorators sufficient | No changes needed |
| 5 | - | - | No issues - specs consistent | Validated |

### Judgment Decisions

None required - straightforward bug fix to match existing specs.

---

## Approval Checklist

Before human approval:

- [x] All existing specs reviewed for REUSE opportunities (S-026, S-094 already correct)
- [x] Updated spec (S-025) follows evergreen guidelines (behavior, not implementation)
- [x] Brick layer constraints validated (no changes to layer structure)
- [x] FORBIDDEN bricks identified (B-rules, B-decorators, B-mend)
- [x] @jig decorator plan complete (no changes needed)
- [x] Clean break actions specified (N/A - modification only)
- [ ] Fresh Agent Review completed
- [ ] All MECHANICAL issues resolved
- [ ] All JUDGMENT issues resolved

---

**Awaiting human approval before proceeding to PLAN.**
