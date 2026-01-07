---
title: PLAN JIG CLI Phase 0 and 1
type: plan
status: draft
created: 1736207400
created_human: 2026-01-06 17:00 CST
parent: "[[DJ007_JIGPLAN_JIG_CLI_Phase_0_1]]"
children: []
---

# PLAN: JIG CLI Phase 0 and 1

- **SCOPE**: dig/wip/DJ006_SCOPE_JIG_Phase_0_1.md
- **JIGPLAN**: dig/wip/DJ007_JIGPLAN_JIG_CLI_Phase_0_1.md
- **Start**: 2026-01-06
- **Status**: Draft
- **Branch**: feature/cli-phase-0-1

---

## Constraints from JIGPLAN

**FORBIDDEN Bricks** (do not modify):
- B-decorators (layer 0)
- B-impl-graph (layer 0)
- B-intent-graph (layer 0)
- B-config (layer 0)
- B-hashing (layer 0)
- B-languages (layer 0)
- B-verification-graph (layer 1)
- B-audit (layer 1)
- B-staleness (layer 0)

**Layer Constraints:**
- B-cli at layer 1 (depends on B-validation, B-config, B-staleness)
- B-validation at layer 0
- No upward dependencies (layer 1 → layer 0 only)

**Clean Break:**
- No deprecation warnings for old command names
- Old commands (`jigy towers`, `jigy matrix`) simply won't exist
- Orphaned files deleted without migration

---

## Work Unit Checklist

- [x] WU1: OutputFormat Infrastructure — code ☑ / tests ☑
- [x] WU2: Markdown Formatter — code ☑ / tests ☑
- [x] WU3: Validate Commands with Flags — code ☑ / tests ☑
- [x] WU4: Rebuild and Align with Flags — code ☑ / tests ☑
- [x] WU5: Show Commands with Flags — code ☑ / tests ☑
- [x] WU6: Move Towers/Matrix to Show — code ☑ / tests ☑
- [x] WU7: Audit Commands with Flags — code ☑ / tests ☑
- [x] WU8: Validation — SCOPE verified ☑
- [x] WU9: Cleanup — orphaned files deleted ☑

---

## Work Units

### Work Unit 1: OutputFormat Infrastructure

**Goal**: Create the shared output formatting infrastructure that all commands will use.

**Specs Addressed**: S-093

**Acceptance Criteria**:
- [ ] `OutputFormat` enum with `HUMAN`, `JSON`, `MARKDOWN` values
- [ ] `add_output_options` decorator adds `-j/-m/-v` flags to commands
- [ ] `resolve_format()` validates mutual exclusivity (`-j -m` errors)
- [ ] `resolve_format()` returns correct `OutputFormat` for flag combinations
- [ ] Code with `@jig.implements("S-093")` decorators
- [ ] Tests with `@jig.verifies("S-093")` decorators
- [ ] `jigy rebuild && jigy validate` passes

**Success Gates** (all must pass):
- [ ] All tests pass: `pytest tests/cli/test_output.py -v`
- [ ] `jigy rebuild && jigy validate` passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors

**Escalation Triggers** (stop and ask human if):
- Click decorator pattern doesn't work as expected
- Need to modify B-config for flag handling
- Mutual exclusivity check requires global state

**Implementation Notes**:
- Files: `src/jig/cli/output.py` (new), `tests/cli/test_output.py` (new)
- Pattern: Click decorator stacking (`@click.option` wrapped in custom decorator)
- Add to bricks.yaml: `M-jig.cli.output` under B-cli
- Decorators: `@jig.implements("S-093")` on `OutputFormat`, `add_output_options`, `resolve_format`

**Human Verification**:
```bash
pytest tests/cli/test_output.py -v
jigy rebuild && jigy validate
```

---

### Work Unit 2: Markdown Formatter

**Goal**: Add markdown output formatting capability to validation reporting.

**Specs Addressed**: S-094

**Acceptance Criteria**:
- [ ] `format_as_markdown()` function in `reporting.py`
- [ ] Markdown output includes headers, bullets, emphasis
- [ ] Validation results format with status, checked counts, error list
- [ ] Verbose mode adds additional detail sections
- [ ] Code with `@jig.implements("S-094")` decorators
- [ ] Tests with `@jig.verifies("S-094")` decorators
- [ ] `jigy rebuild && jigy validate` passes

**Success Gates** (all must pass):
- [ ] All tests pass: `pytest tests/validation/test_reporting.py -v`
- [ ] `jigy rebuild && jigy validate` passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] Markdown output is valid (parseable)

**Escalation Triggers** (stop and ask human if):
- Need to modify validation models (B-validation core)
- Markdown format requirements unclear
- Verbose mode scope ambiguous

**Implementation Notes**:
- Files: `src/jig/validation/reporting.py` (modify), `tests/validation/test_reporting.py` (modify)
- Pattern: Follow existing `format_as_json()` structure
- Decorators: `@jig.implements("S-094")` on `format_as_markdown`
- Consider: Generic markdown builder or string templates

**Human Verification**:
```bash
pytest tests/validation/test_reporting.py -v
jigy rebuild && jigy validate
```

---

### Work Unit 3: Validate Commands with Flags

**Goal**: Wire output format flags to all validate commands.

**Specs Addressed**: S-026, S-093

**Acceptance Criteria**:
- [ ] `jigy validate -j` produces JSON output
- [ ] `jigy validate -m` produces markdown output
- [ ] `jigy validate -v` produces verbose output
- [ ] `jigy validate -j -v` produces verbose JSON
- [ ] `jigy validate -m -v` produces verbose markdown
- [ ] `jigy validate -j -m` produces clear error message
- [ ] Same flags work on `validate intent`, `validate bricks`, `validate full`
- [ ] `jigy rebuild && jigy validate` passes

**Success Gates** (all must pass):
- [ ] All tests pass: `pytest tests/cli/test_validate.py -v`
- [ ] `jigy rebuild && jigy validate` passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] JSON output is valid JSON (single-line)

**Escalation Triggers** (stop and ask human if):
- Existing `output_format` parameter incompatible with new pattern
- Need to change validation function signatures significantly
- Error output format unclear

**Implementation Notes**:
- Files: `src/jig/cli/validate.py` (modify), `tests/cli/test_validate.py` (modify)
- Pattern: Add `@add_output_options` decorator, wire to existing `output_format` param
- Existing: `validate_*_command()` functions already accept `output_format` parameter
- Key change: Expose parameter via CLI flags instead of hardcoded "human"

**Human Verification**:
```bash
jigy validate -j | python -m json.tool  # Should parse as JSON
jigy validate -m  # Should show markdown headers
jigy validate -j -m  # Should show error
pytest tests/cli/test_validate.py -v
```

---

### Work Unit 4: Rebuild and Align with Flags

**Goal**: Add output format flags to rebuild and align commands.

**Specs Addressed**: S-093

**Acceptance Criteria**:
- [ ] `jigy rebuild -j` produces JSON output with graphs rebuilt, duration
- [ ] `jigy rebuild -m` produces markdown output
- [ ] `jigy align -j` produces combined JSON (rebuild + validate)
- [ ] `jigy align -m` produces combined markdown
- [ ] Flags work on all rebuild subcommands (impl, intent, verify)
- [ ] `jigy rebuild && jigy validate` passes

**Success Gates** (all must pass):
- [ ] All tests pass: `pytest tests/cli/test_rebuild.py -v`
- [ ] `jigy rebuild && jigy validate` passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] JSON output is valid JSON

**Escalation Triggers** (stop and ask human if):
- Rebuild output structure unclear (what metrics to include)
- Align command coordination with validate output complex
- Need to modify graph builders (FORBIDDEN)

**Implementation Notes**:
- Files: `src/jig/cli/rebuild.py` (modify), `tests/cli/test_rebuild.py` (modify)
- Pattern: Add `@add_output_options` decorator
- JSON schema: `{"status": "success", "graphs": [...], "duration_ms": N}`
- Align combines rebuild and validate output

**Human Verification**:
```bash
jigy rebuild -j | python -m json.tool
jigy align -m
pytest tests/cli/test_rebuild.py -v
```

---

### Work Unit 5: Show Commands with Flags

**Goal**: Add output format flags to all show commands.

**Specs Addressed**: S-060, S-093

**Acceptance Criteria**:
- [ ] `jigy show -j` produces JSON output
- [ ] `jigy show layers -j` produces JSON layer structure
- [ ] `jigy show bricks -j` produces JSON brick list
- [ ] `jigy show charter -m` produces markdown
- [ ] `jigy show goals -m` produces markdown
- [ ] `jigy show architecture -j` produces JSON
- [ ] All show subcommands support `-j/-m/-v` flags
- [ ] `jigy rebuild && jigy validate` passes

**Success Gates** (all must pass):
- [ ] All tests pass: `pytest tests/cli/test_show.py -v`
- [ ] `jigy rebuild && jigy validate` passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] JSON output is valid JSON

**Escalation Triggers** (stop and ask human if):
- Show command output structure significantly different per subcommand
- Charter/goals markdown format unclear
- Need to modify intent graph reading (FORBIDDEN)

**Implementation Notes**:
- Files: `src/jig/cli/show.py` (modify), `tests/cli/test_show.py` (modify)
- Pattern: Add `@add_output_options` decorator to each subcommand
- Each subcommand may need custom JSON schema
- Prepare for towers/matrix move in next WU

**Human Verification**:
```bash
jigy show layers -j | python -m json.tool
jigy show bricks -m
pytest tests/cli/test_show.py -v
```

---

### Work Unit 6: Move Towers/Matrix to Show

**Goal**: Move towers and matrix commands under the show command group.

**Specs Addressed**: S-060, S-090, S-091

**Acceptance Criteria**:
- [ ] `jigy show towers` works (same output as old `jigy towers`)
- [ ] `jigy show towers <id>` works for specific tower
- [ ] `jigy show matrix` works (same output as old `jigy matrix`)
- [ ] `jigy show towers -j` produces JSON
- [ ] `jigy show matrix -j` produces JSON (2D grid data)
- [ ] Old commands removed from CLI (no `jigy towers` at root)
- [ ] `jigy rebuild && jigy validate` passes

**Success Gates** (all must pass):
- [ ] All tests pass: `pytest tests/cli/test_show.py -v`
- [ ] `jigy rebuild && jigy validate` passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] `jigy towers` returns command not found
- [ ] `jigy matrix` returns command not found

**Escalation Triggers** (stop and ask human if):
- Tower/matrix logic tightly coupled to towers.py structure
- Need to preserve towers.py for other reasons
- Command argument handling differs between standalone and subcommand

**Implementation Notes**:
- Files: `src/jig/cli/show.py` (modify), `src/jig/cli/towers.py` (source), `src/jig/cli/main.py` (modify)
- Move `towers_command()` and `matrix_command()` to show.py
- Register as `show.command(name="towers")` and `show.command(name="matrix")`
- Remove standalone registration from main.py
- Update `@jig.implements` decorators to reference S-090, S-091
- Delete towers.py after move complete

**Human Verification**:
```bash
jigy show towers
jigy show matrix
jigy towers  # Should fail
jigy matrix  # Should fail
pytest tests/cli/test_show.py -v
```

---

### Work Unit 7: Audit Commands with Flags

**Goal**: Add output format flags to audit commands.

**Specs Addressed**: S-093

**Acceptance Criteria**:
- [ ] `jigy audit coverage -j` produces JSON output
- [ ] `jigy audit coverage -m` produces markdown output
- [ ] `jigy audit coverage -v` produces verbose output
- [ ] `jigy rebuild && jigy validate` passes

**Success Gates** (all must pass):
- [ ] All tests pass: `pytest tests/cli/test_audit.py -v`
- [ ] `jigy rebuild && jigy validate` passes
- [ ] No modifications to FORBIDDEN bricks (B-audit is FORBIDDEN but B-cli audit.py is allowed)
- [ ] JSON output is valid JSON

**Escalation Triggers** (stop and ask human if):
- Audit coverage output structure complex
- Need to modify B-audit brick (FORBIDDEN)
- Coverage data format unclear

**Implementation Notes**:
- Files: `src/jig/cli/audit.py` (modify), `tests/cli/test_audit.py` (modify)
- Pattern: Add `@add_output_options` decorator
- Note: B-audit brick is FORBIDDEN, but `src/jig/cli/audit.py` is in B-cli (allowed)
- JSON schema: coverage metrics, gaps, recommendations

**Human Verification**:
```bash
jigy audit coverage -j | python -m json.tool
jigy audit coverage -m
pytest tests/cli/test_audit.py -v
```

---

### Work Unit 8: Validation

**Goal**: Verify SCOPE problem is solved at system boundary.

**SCOPE Reference**:
"All commands support the universal output flags consistently... Every command accepts `-j`, `-m`, and `-v` flags... `jigy show towers` works (same output as old `jigy towers`)"

**Validation Approach**: Integration Test

**Verification Steps**:
```bash
# Test every command with every flag combination
pytest tests/cli/test_output_modes.py -v

# Manual spot checks
jigy validate -j
jigy rebuild -m
jigy show layers -j -v
jigy show towers -m
jigy show matrix -j
jigy audit coverage -m -v
jigy align -j

# Verify mutual exclusivity
jigy validate -j -m  # Should error

# Verify old commands gone
jigy towers  # Should fail
jigy matrix  # Should fail
```

**Expected Result**:
- All commands accept `-j/-m/-v` flags
- JSON output is single-line and parseable
- Markdown output has headers and structure
- Verbose adds detail to any format
- `-j -m` produces clear error
- Old standalone commands no longer exist

**Deliverable**:
- [ ] Integration test added: `tests/cli/test_output_modes.py`
- [ ] Test covers every command × flag combination matrix

**If Validation Fails**:
- Check if flag wiring missed on specific command
- Verify output formatter called correctly
- Check command registration in main.py

**Human Verification**:
```bash
pytest tests/cli/test_output_modes.py -v
jigy validate -j | python -m json.tool
```

---

### Work Unit 9: Cleanup

**Goal**: Delete orphaned files and finalize brick definitions.

**Specs Addressed**: (none - cleanup)

**Acceptance Criteria**:
- [ ] `src/jig/cli/towers.py` deleted (code moved to show.py)
- [ ] `src/jig/cli/layers.py` deleted (orphaned, functionality in show.py)
- [ ] `src/jig/cli/verify.py` deleted (orphaned, redundant with rebuild)
- [ ] `bricks.yaml` updated to remove deleted modules
- [ ] No imports reference deleted files
- [ ] `jigy rebuild && jigy validate` passes

**Success Gates** (all must pass):
- [ ] All tests pass: `pytest tests/ -v`
- [ ] `jigy rebuild && jigy validate` passes
- [ ] No import errors when running any jigy command
- [ ] Deleted files don't exist

**Escalation Triggers** (stop and ask human if):
- Deleted file has code not present elsewhere
- Import cleanup breaks unexpected module
- bricks.yaml validation fails after update

**Implementation Notes**:
- Files to delete:
  - `src/jig/cli/towers.py`
  - `src/jig/cli/layers.py`
  - `src/jig/cli/verify.py`
- Update `jig/bricks.yaml`: Remove `M-jig.cli.towers`, `M-jig.cli.layers`, `M-jig.cli.verify`
- Search for imports: `grep -r "from jig.cli.towers" src/`
- Run full test suite to catch any breaks

**Human Verification**:
```bash
ls src/jig/cli/towers.py  # Should not exist
ls src/jig/cli/layers.py  # Should not exist
ls src/jig/cli/verify.py  # Should not exist
jigy rebuild && jigy validate
pytest tests/ -v
```

---

## Execution Log

(Filled in by orchestrator during execution)

---

## Completion Summary

(Filled in after all WUs complete)

**Scope Delivered:**
- <to be filled>

**JIG Summary:**
- <to be filled>

**Clean Break Actions:**
- [ ] Deleted orphaned CLI modules (towers.py, layers.py, verify.py)
- [ ] Updated bricks.yaml
- [ ] Final `jigy rebuild && jigy validate` passed

**Reflection Roll-Up:**
- Repeatable wins: <patterns that worked>
- Systemic frictions: <process issues>
- Open questions: <items for future work>
