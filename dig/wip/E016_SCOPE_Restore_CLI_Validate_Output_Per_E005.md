---
title: "Restore CLI Validate Output Per E005"
type: scope
status: active
created: 1737233400
created_human: "2026-01-18 14:50 CST"
parent: "[[E005_SCOPE_CLI_Validate_Output_Alignment]]"
children: []
---
# Restore CLI Validate Output Per E005

## Problem Statement

The rules-based validation rewrite (E011-E015) inadvertently regressed the `jigy validate` output format established in [[E005_SCOPE_CLI_Validate_Output_Alignment]].

### Current Output

```
Rebuilt 2 graphs.
Validation passed.
```

### Expected Output (per E005)

```
Rebuilt 3 graphs. Validated 78 specs, 23 outcomes, 11 bricks.
```

### Violations

| E005 Requirement | Current State |
|------------------|---------------|
| One-line summary with metrics | Two lines, no metrics |
| Artifact counts on success | Just "Validation passed." |
| Rebuild + validation combined | Separate lines |

---

## Root Cause

The new `validate()` function in `src/jig/validation/engine.py` only returns error information:

```python
return {
    "errors": [...],
    "summary": {"total": N, "auto_fixable": N, "manual": N}
}
```

It does not return artifact counts (specs, outcomes, architectures, bricks) because those aren't needed for error detection. The original implementation queried these counts separately.

---

## Scope of Work

### 1. Extend Validation Engine Return Value

**File:** `src/jig/validation/engine.py`

Add artifact counts to the return value:

```python
return {
    "errors": [...],
    "summary": {
        "total": N,
        "auto_fixable": N,
        "manual": N,
    },
    "counts": {
        "specs": len(ctx.specifications),
        "outcomes": len(ctx.outcomes),
        "architectures": len(ctx.architectures),
        "bricks": len(ctx.bricks),
        "goals": len(ctx.goals) if ctx.goals else len(ctx.charter.frontmatter.get("goals", [])) if ctx.charter else 0,
    }
}
```

### 2. Update Human Output Format

**File:** `src/jig/cli/validate.py`

Modify `_output_human_results()` to output E005-compliant format:

```python
def _output_human_results(result: dict, rebuild_summary: str | None = None, verbose: bool = False) -> None:
    errors = result.get("errors", [])
    counts = result.get("counts", {})

    if not errors:
        # One-line success summary per E005
        parts = []
        if rebuild_summary:
            parts.append(rebuild_summary.rstrip('.'))

        validated = []
        if counts.get("specs"):
            validated.append(f"{counts['specs']} specs")
        if counts.get("outcomes"):
            validated.append(f"{counts['outcomes']} outcomes")
        if counts.get("bricks"):
            validated.append(f"{counts['bricks']} bricks")

        if validated:
            parts.append(f"Validated {', '.join(validated)}")
        else:
            parts.append("Validation passed")

        click.echo(". ".join(parts) + ".")
        return

    # ... error output unchanged ...
```

### 3. Update Verbose Output

Per E005, `-v` should show category-based breakdown:

```
Intent: 106 artifacts
  ✓ 78 specifications
  ✓ 23 outcomes
  ✓ 5 goals
  ✓ 4 architecture docs

Bricks: 15 definitions
  ✓ 238 files partitioned
  ✓ 0 layer violations

Validated 78 specs, 23 outcomes, 15 bricks.
```

### 4. Update JSON Output

Add counts to JSON output per E005:

```json
{"valid":true,"summary":{"specs":78,"outcomes":23,"goals":5,"bricks":15},"errors":[]}
```

### 5. Update Markdown Output

Fix placeholder counts in `_format_engine_results_as_markdown()`:

```markdown
# JIG Validation: Passed

- **Specs:** 78 | **Outcomes:** 23 | **Bricks:** 15
- **Coverage:** 115 functions, 604 tests decorated
```

Note: Coverage counts (functions, tests) require querying impl/verify graphs - may defer to future work if complex.

---

## Files Modified

| File | Changes |
|------|---------|
| `src/jig/validation/engine.py` | Add `counts` to return value |
| `src/jig/cli/validate.py` | Update all three output functions |
| `tests/unit/test_validation_engine.py` | Add tests for counts |
| `tests/cli/test_validate.py` | Update expected output formats |

---

## Out of Scope

- Coverage counts (functions decorated, tests decorated) - requires additional graph queries
- Verbose mode detailed breakdown - can be follow-up work
- Changes to `jigy validate intent` or `jigy validate bricks` subcommands

---

## Acceptance Criteria

1. `jigy validate` outputs one-line summary with artifact counts on success
2. Rebuild summary combined with validation summary on same line
3. JSON output includes `summary.specs`, `summary.outcomes`, `summary.bricks`
4. All existing tests pass (with updated expectations)
5. E005 compliance restored

---

## References

- [[E005_SCOPE_CLI_Validate_Output_Alignment]] — Original output specification
- [[DJ001_CONCEPT_CLI_Design_Manifesto]] — CLI design principles
- [[E011_SCOPE_Rules_Based_Validation]] — Rules-based validation rewrite
