---
title: "PLAN: CLI Command Consolidation"
type: plan
status: implemented
decision: completed
created: 1737741600
created_human: "2026-01-24 14:30 CST"
parent: "[[E023_JIGPLAN_CLI_Command_Consolidation]]"
children: []
---

# PLAN: CLI Command Consolidation

- **SCOPE**: dig/wip/E023_SCOPE_CLI_Command_Consolidation.md
- **JIGPLAN**: dig/wip/E023_JIGPLAN_CLI_Command_Consolidation.md
- **Start**: 2026-01-24
- **Status**: Draft
- **Branch**: E023-cli-consolidation

---

## Constraints from JIGPLAN

**FORBIDDEN Bricks** (do not modify):
- B-validation
- B-impl-graph
- B-intent-graph
- B-rules

**Layer Constraints:**
- B-cli at layer 1
- No upward dependencies
- No layer changes

**Clean Break:**
- Delete show.py module entirely
- Delete align command
- Delete S-059, S-060 after validation
- No compatibility shims

---

## Key Existing Code References

| Concern | Location | Notes |
|---------|----------|-------|
| Context command | src/jig/cli/context.py:600-649 | `context_command()` entry point |
| Identifier resolution | src/jig/cli/context.py:104-162 | `resolve_identifier()` function |
| Show commands data | src/jig/cli/show.py | 8 show_* functions to extract logic from |
| OrderedGroup | src/jig/cli/main.py:13-57 | Custom Click group for command ordering |
| Output format | src/jig/cli/output.py | `add_output_options` decorator |
| Auto-rebuild | src/jig/cli/auto_rebuild.py:33-91 | `ensure_graphs_current()` |

---

## Execution Order

```
WU1 (Overview) ──┬── WU2 (Context modes)
                 └── WU3 (Aliases)
                     │
                     WU4 (Validation) ── WU5 (Cleanup)
```

WU1 must come first (provides overview function).
WU2 and WU3 can run after WU1 (both use overview).
WU4 validates before cleanup.
WU5 deletes legacy code last.

---

## Test Strategy

- **New tests**: test_overview.py, test_context_modes.py, test_aliases.py
- **Existing tests**: test_context.py (keep traversal tests)
- **Deleted tests**: test_show.py, test_align.py (if they exist)

---

## Work Unit Checklist

- [ ] WU1: Project Overview — tests ☐ / code ☐
- [ ] WU2: Context Modes — tests ☐ / code ☐
- [ ] WU3: CLI Aliases — tests ☐ / code ☐
- [ ] WU4: Validation — SCOPE verified ☐
- [ ] WU5: Cleanup — legacy deleted ☐

---

## Work Units

### Work Unit 1: Project Overview Implementation

**Goal**: Implement `build_overview()` that generates unified project context.

**Specs Addressed**: S-114

**Acceptance Criteria**:
- [ ] `build_overview()` returns dict with all 8 sections (charter, goals, architecture, outcomes, specs, bricks_by_layer, towers, traversal_keys)
- [ ] Charter extracted from Charter.md H1 heading
- [ ] Goals extracted from Charter frontmatter and content
- [ ] Spec counts computed (total/implemented/verified)
- [ ] Bricks grouped by layer number
- [ ] Traversal keys lists all valid identifiers
- [ ] Tests with @jig.verifies("S-114") decorators
- [ ] Code with @jig.implements("S-114") decorators
- [ ] jigy rebuild && jigy validate passes

**Success Gates** (all must pass):
- [ ] All tests pass: pytest tests/unit/cli/test_overview.py -v
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors

**Escalation Triggers** (stop and ask human if):
- Test failures persist after 2 retry attempts
- Need to modify FORBIDDEN brick
- Unclear how to extract data from existing show_* functions

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| Charter file location | jig/Charter_JIG.md | Glob pattern |
| Goals in Charter | G-001..G-005 in frontmatter | Charter_JIG.md:4 |
| Brick loading | `_load_bricks()` helper | show.py:65-87 |
| Layer names | `_get_layer_name()` helper | show.py:53-62 |
| Spec counts | Computed from graphs | show.py:91-212 |

**Implementation Notes**:
- Files: src/jig/cli/overview.py (new)
- Extract/refactor logic from show.py helper functions
- Do NOT import from show.py (it will be deleted)
- Copy needed helper functions into overview.py

**Human Verification**:
```bash
pytest tests/unit/cli/test_overview.py -v
jigy rebuild && jigy validate
```

---

### Work Unit 2: Context Command Enhancement

**Goal**: Update context command to support bare mode (overview) and graceful fallback.

**Specs Addressed**: S-110 (update), S-111 (update)

**Acceptance Criteria**:
- [ ] `jigy context` (bare) returns Project Overview
- [ ] `jigy context <valid-id>` returns graph traversal (existing behavior)
- [ ] `jigy context <invalid-id>` returns "not found" note + Overview
- [ ] `jigy context bricks` returns "bricks is not a jig node" + Overview
- [ ] All output formats work (-j, -m, -v)
- [ ] Tests with @jig.verifies decorators
- [ ] jigy rebuild && jigy validate passes

**Success Gates** (all must pass):
- [ ] All tests pass: pytest tests/unit/cli/test_context.py -v
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] Existing traversal tests still pass

**Escalation Triggers** (stop and ask human if):
- Test failures persist after 2 retry attempts
- Existing traversal behavior breaks
- Format output structure unclear

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| context_command entry | Lines 600-649 | context.py |
| resolve_identifier | Lines 104-162 | context.py |
| Current error handling | Raises error on invalid | context.py:158-162 |
| Output format handling | `add_output_options` decorator | output.py:36-83 |

**Implementation Notes**:
- Files: src/jig/cli/context.py (modify)
- Import `build_overview` from overview.py
- Change identifier from required to optional (Click)
- Replace error paths with graceful fallback
- Keep traversal logic unchanged

**Human Verification**:
```bash
jigy context                    # Should show overview
jigy context S-001              # Should show traversal
jigy context S-999              # Should show "not found" + overview
pytest tests/unit/cli/test_context.py -v
```

---

### Work Unit 3: CLI Command Aliases

**Goal**: Add alias commands that map to context and mend.

**Specs Addressed**: S-115

**Acceptance Criteria**:
- [ ] `jigy graph` → `jigy context`
- [ ] `jigy graph S-042` → `jigy context S-042`
- [ ] `jigy list` → `jigy context`
- [ ] `jigy show` → `jigy context`
- [ ] `jigy show S-042` → `jigy context S-042`
- [ ] `jigy bricks` → `jigy context` (bare only)
- [ ] `jigy layers` → `jigy context` (bare only)
- [ ] `jigy towers` → `jigy context` (bare only)
- [ ] `jigy fix` → `jigy mend`
- [ ] `jigy fix --auto` → `jigy mend --auto`
- [ ] Aliases appear in help with "(alias)" marker
- [ ] Tests with @jig.verifies("S-115") decorators
- [ ] jigy rebuild && jigy validate passes

**Success Gates** (all must pass):
- [ ] All tests pass: pytest tests/unit/cli/test_aliases.py -v
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] Aliases work end-to-end

**Escalation Triggers** (stop and ask human if):
- Test failures persist after 2 retry attempts
- Click alias implementation unclear
- Command ordering issues

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| OrderedGroup | Custom Click group | main.py:13-57 |
| Command ordering | Explicit list in OrderedGroup | main.py:19-21 |
| mend_command | Lines 618+ | main.py |
| Click alias pattern | `@cli.command(name="alias")` | Click docs |

**Implementation Notes**:
- Files: src/jig/cli/main.py (modify)
- Use Click's `@cli.command()` with `cls=` pointing to same implementation
- Or use callback that invokes the real command
- Add aliases to OrderedGroup's command list
- Mark aliases in help text

**Human Verification**:
```bash
jigy graph
jigy list
jigy show
jigy bricks
jigy fix --help
pytest tests/unit/cli/test_aliases.py -v
```

---

### Work Unit 4: Validation

**Goal**: Verify SCOPE problem is solved at system boundary.

**SCOPE Reference**:
"Agents hallucinate commands based on mental models. Instead of erroring, map all reasonable names to useful outputs."

**Validation Approach**: Integration Test (preferred)

**Verification Steps**:
```bash
# Test orientation (bare commands)
jigy context              # Overview
jigy graph                # Overview via alias
jigy show                 # Overview via alias
jigy bricks               # Overview via alias

# Test traversal
jigy context S-001        # Traversal works
jigy show S-001           # Traversal via alias

# Test graceful fallback
jigy context nonexistent  # Overview + "not found"
jigy context bricks       # Overview + "not a jig node"
jigy graph invalid        # Same behavior via alias

# Test mend alias
jigy fix --help           # Mend help
```

**Expected Result**:
- All commands produce useful output (never "command not found")
- Agents can orient with any reasonable command name
- Invalid identifiers still provide project context

**Deliverable**:
- [ ] Integration test added: tests/integration/test_cli_consolidation.py

**If Validation Fails**:
- Investigate wiring/integration gap
- Fix the issue
- Add regression test
- Re-run validation

---

### Work Unit 5: Cleanup

**Goal**: Delete legacy code and deprecated O/S nodes.

**Specs Addressed**: (none - cleanup)

**Acceptance Criteria**:
- [ ] Delete src/jig/cli/show.py (entire module)
- [ ] Delete align_command() from main.py
- [ ] Remove "show" group from OrderedGroup command list
- [ ] Remove "align" from OrderedGroup command list
- [ ] Update bricks.yaml: remove M-jig.cli.show
- [ ] Delete jig/specifications/S-059_Align_Command.md
- [ ] Delete jig/specifications/S-060_Show_Command_Structure.md
- [ ] Delete related test files (test_show.py, test_align.py if exist)
- [ ] jigy rebuild && jigy validate passes (clean)

**Success Gates** (all must pass):
- [ ] All tests pass: pytest -v
- [ ] jigy rebuild && jigy validate passes with 0 errors
- [ ] No modifications to FORBIDDEN bricks
- [ ] show.py file does not exist
- [ ] S-059.md and S-060.md files do not exist

**Escalation Triggers** (stop and ask human if):
- Unexpected import errors after deletion
- Tests fail that shouldn't depend on deleted code
- Validation errors other than expected

**Implementation Notes**:
- Files to delete:
  - src/jig/cli/show.py
  - jig/specifications/S-059_Align_Command.md
  - jig/specifications/S-060_Show_Command_Structure.md
  - tests/unit/cli/test_show.py (if exists)
- Files to modify:
  - src/jig/cli/main.py (remove align, show imports)
  - jig/bricks.yaml (remove M-jig.cli.show)

**Human Verification**:
```bash
ls src/jig/cli/show.py 2>&1  # Should not exist
ls jig/specifications/S-059* 2>&1  # Should not exist
ls jig/specifications/S-060* 2>&1  # Should not exist
jigy rebuild && jigy validate
pytest -v
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
- [ ] Deleted deprecated O/S nodes
- [ ] Deleted legacy code modules
- [ ] Final jigy rebuild && jigy validate passed

**Reflection Roll-Up:**
- Repeatable wins: <patterns that worked>
- Systemic frictions: <process issues>
- Open questions: <items for future work>
