---
title: "PLAN: Restore CLI Validate Output"
type: plan
status: active
created: 1737235200
created_human: "2026-01-18 15:20 CST"
parent: "[[E017_JIGPLAN_Restore_CLI_Validate_Output]]"
children: []
---
# PLAN: Restore CLI Validate Output

- **SCOPE**: dig/wip/E016_SCOPE_Restore_CLI_Validate_Output_Per_E005.md
- **JIGPLAN**: dig/wip/E017_JIGPLAN_Restore_CLI_Validate_Output.md
- **Start**: 2026-01-18
- **Status**: Draft
- **Branch**: rules-validate-mend

---

## Constraints from JIGPLAN

**FORBIDDEN Bricks** (do not modify):
- B-rules (layer 0): Rules engine returns violations only
- B-decorators (layer 0): Core decorator infrastructure
- B-mend (layer 0): Mend actions unrelated to output

**Layer Constraints:**
- B-validation at layer 0
- B-cli at layer 1
- B-cli depends on B-validation (valid)

**Clean Break:**
- No backwards compatibility needed
- No feature flags
- Tests updated to expect new output format

---

## Key Existing Code References

| Concern | Location | Notes |
|---------|----------|-------|
| validate() function | src/jig/validation/engine.py:22 | Returns {errors, summary}, needs to add counts |
| ValidationContext | src/jig/rules/context.py | Has specifications, outcomes, architectures, bricks dicts |
| validate_full_command | src/jig/cli/validate.py:286 | Calls validate(), formats output |
| _output_human_results | src/jig/cli/validate.py:110 | Human output, needs rebuild_summary param |
| _format_engine_results_as_json | src/jig/cli/validate.py:21 | JSON output, uses result["summary"] |
| _format_engine_results_as_markdown | src/jig/cli/validate.py:54 | Markdown output, has placeholder counts |
| ensure_graphs_current | src/jig/cli/auto_rebuild.py | Returns rebuild summary string |

---

## Execution Order

```
WU1 (Engine) ── WU2 (CLI) ── WU3 (Validation)
```

**Dependencies:**
- WU2 depends on WU1 (CLI needs counts from engine)
- WU3 depends on WU2 (validation verifies full stack)

---

## Test Strategy

- **New tests**: None - existing test structure sufficient
- **Existing tests**: Update expectations in tests/cli/test_validate.py, tests/unit/test_validation_engine.py
- **Deleted tests**: None

---

## Work Unit Checklist

- [x] WU1: Validation Engine Counts — tests ✓ / code ✓
- [x] WU2: CLI Output Formatting — tests ✓ / code ✓
- [ ] WU3: Validation — SCOPE verified ☐

---

## Work Units

### Work Unit 1: Validation Engine Counts

**Goal**: Add artifact counts to validate() return value.

**Specs Addressed**: S-025 (partial), S-026 (partial)

**Acceptance Criteria**:
- [ ] validate() returns `counts` dict with specs, outcomes, architectures, bricks
- [ ] Counts extracted from ValidationContext
- [ ] Existing tests updated for new return shape
- [ ] Code with @jig.implements decorator unchanged (already has S-104)
- [ ] jigy rebuild && jigy validate passes

**Success Gates** (all must pass):
- [ ] All tests pass: pytest tests/unit/test_validation_engine.py -v
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors: ruff check src/jig/validation/

**Escalation Triggers** (stop and ask human if):
- ValidationContext doesn't have expected attributes
- Test failures persist after 2 retry attempts
- FORBIDDEN brick modification needed

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| ValidationContext attrs | specifications, outcomes, architectures, bricks, charter, goals | src/jig/rules/context.py:226 |
| Current return shape | {"errors": [...], "summary": {...}} | src/jig/validation/engine.py:76-79 |

**Implementation Notes**:
- File: src/jig/validation/engine.py
- After building summary dict, add counts dict:
```python
counts = {
    "specs": len(ctx.specifications),
    "outcomes": len(ctx.outcomes),
    "architectures": len(ctx.architectures),
    "bricks": len(ctx.bricks),
}
```
- Return: `{"errors": errors, "summary": summary, "counts": counts}`
- Update tests/unit/test_validation_engine.py to check for counts key

**Human Verification**:
```bash
pytest tests/unit/test_validation_engine.py -v
ruff check src/jig/validation/
```

---

### Work Unit 2: CLI Output Formatting

**Goal**: Update CLI to output E005-compliant format with artifact counts.

**Specs Addressed**: S-025, S-026, S-094

**Acceptance Criteria**:
- [ ] Human output: single line "Rebuilt N graphs. Validated X specs, Y outcomes, Z bricks."
- [ ] JSON output: summary includes specs, outcomes, bricks counts
- [ ] Markdown output: counts in summary line (not placeholders)
- [ ] Rebuild summary combined with validation on one line
- [ ] Tests with @jig.verifies decorators updated
- [ ] jigy rebuild && jigy validate passes

**Success Gates** (all must pass):
- [ ] All tests pass: pytest tests/cli/test_validate.py -v
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors: ruff check src/jig/cli/

**Escalation Triggers** (stop and ask human if):
- Test failures persist after 2 retry attempts
- Output format unclear from S-025 spec
- FORBIDDEN brick modification needed

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| rebuild_summary source | ensure_graphs_current() return value | src/jig/cli/validate.py:308 |
| Human output function | _output_human_results() | src/jig/cli/validate.py:110 |
| JSON format function | _format_engine_results_as_json() | src/jig/cli/validate.py:21 |
| Markdown format function | _format_engine_results_as_markdown() | src/jig/cli/validate.py:54 |

**Implementation Notes**:
- File: src/jig/cli/validate.py
- Modify `_output_human_results()`:
  - Add `rebuild_summary: str | None = None` parameter
  - On success: combine rebuild + counts in one line
  - Pattern: `". ".join(parts) + "."`
- Modify `_format_engine_results_as_json()`:
  - Add counts to summary from result["counts"]
- Modify `_format_engine_results_as_markdown()`:
  - Use result["counts"] instead of placeholder 0s (leave coverage as 0)
- Modify `validate_full_command()`:
  - REMOVE the separate `click.echo(rebuild_summary)` call (line 323-324)
  - Pass rebuild_summary to _output_human_results() instead

**Human Verification**:
```bash
pytest tests/cli/test_validate.py -v
jigy validate  # Should show: "Rebuilt N graphs. Validated X specs, Y outcomes, Z bricks."
jigy validate -j  # Should include counts in summary
```

---

### Work Unit 3: Validation

**Goal**: Verify SCOPE problem is solved at system boundary.

**SCOPE Reference**:
"The output doesn't match E005 spec - should show artifact counts"

**Validation Approach**: Integration Test (preferred)

**Verification Steps**:
```bash
# Run jigy validate and check output format
jigy validate

# Expected: One-line summary with counts
# "Rebuilt N graphs. Validated 92 specs, 25 outcomes, 15 bricks."

# Check JSON output
jigy validate -j | python -c "import sys,json; d=json.load(sys.stdin); print('specs' in d.get('summary',{}))"
# Expected: True

# Check markdown output
jigy validate -m | head -5
# Expected: "# JIG Validation: Passed" with counts line
```

**Expected Result**:
- Human output is one line with rebuild info and artifact counts
- JSON output has summary.specs, summary.outcomes, summary.bricks
- Markdown output has actual counts, not zeros

**Deliverable**:
- [x] Existing integration tests updated to verify output format

**Human Verification**:
```bash
jigy validate
jigy validate -j
jigy validate -m
```

---

## Fresh Agent Review Summary

Completed 2026-01-18.

### Review Findings

| # | Issue | Category | Classification | Resolution |
|---|-------|----------|----------------|------------|
| 1 | Line number hints may drift | Existence uncertain | (A) | Acceptable - use as hints, not absolutes |
| 2 | Goals count in counts dict? | Type ambiguity | (B) | Excluded per S-025 - goals only in verbose mode |
| 3 | bricks type labeled "dict" | Type ambiguity | (A) | It's a list; len(ctx.bricks) is correct |
| 4 | Rebuild summary integration | Hidden dependency | (A) | WU2 must remove separate echo and pass to _output_human_results |
| 5 | Coverage counts in markdown | Missing context | (B) | Deferred per SCOPE - leave as 0 |
| 6 | Test assertion updates | Missing context | (A) | Update assertions in WU2 to match E005 format |

### Judgment Decisions

1. **Goals in counts**: Per S-025 spec, the main summary line shows "X specs, Y outcomes, Z bricks" - no goals. Goals appear only in verbose mode (`-v`). Verbose mode is OUT OF SCOPE per E016. Counts dict excludes goals.

2. **Coverage in markdown**: SCOPE explicitly states "may defer to future work if complex". Coverage requires impl_graph + verify_graph queries. Leaving as 0 placeholder for this work.

---

## Execution Log

### WU1: Validation Engine Counts
**Status:** COMPLETE
**Gates:** 4/4 passed
- Tests: 16/16 passed
- jigy validate: PASS
- FORBIDDEN bricks: untouched
- Linting: no new errors (pre-existing UP045 in models.py)

**Commit:** 9555cbf

### WU2: CLI Output Formatting
**Status:** COMPLETE
**Gates:** 4/4 passed
- Tests: 30/30 passed
- jigy validate: PASS
- FORBIDDEN bricks: untouched
- Linting: no new errors (4 pre-existing unused imports)

**Commit:** (this commit)

---

## Completion Summary

**Scope Delivered:**
- (to be filled)

**JIG Summary:**
- (to be filled)

**Clean Break Actions:**
- [ ] No deprecated O/S nodes to delete
- [ ] No legacy code to delete
- [ ] Final jigy rebuild && jigy validate passed

**Reflection Roll-Up:**
- Repeatable wins: (to be filled)
- Systemic frictions: (to be filled)
- Open questions: (to be filled)
