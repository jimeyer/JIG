# Task: Create PLAN Document (taskMakePLAN)

**Version:** 2.0.0
**Date:** 2026-01-08
**Audience:** AI coding agents
**Status:** Active
**Related:** JigPlanOrchWorkflow.md, taskMakeJIGPLAN.md, taskDoPLAN.md, taskDoWU.md, contextBricks.md

## Objective

Create a PLAN document that breaks an approved JIGPLAN into sequenced, executable Work Units. The PLAN is a pure execution plan - all architectural decisions were made in JIGPLAN.

**You receive:** SCOPE + approved JIGPLAN
**You produce:** PLAN document with Work Units ready for orchestrated execution

---

## Inputs

Before creating a PLAN, you need:

1. **SCOPE Document** (`docs/wip/SCOPE-<feature>.md`)
   - Original problem description
   - Backwards compat requirements (if any)

2. **Approved JIGPLAN** (`docs/wip/JIGPLAN-<feature>.md`)
   - O/S node reconciliation (specs to implement)
   - Brick scope (FORBIDDEN bricks, layer constraints)
   - @jig decorator changes (what to ADD/REMOVE)
   - Clean break actions (what to delete)

**Critical:** JIGPLAN must be human-approved before creating PLAN.

**Note:** During execution, orchestrator creates `JOURNAL-<feature>.md` alongside the PLAN. You don't create this file - it's created by taskDoPLAN.md.

---

## Key Concepts

### Specifications

Specifications (S-nodes) are testable behavioral requirements. Each WU implements one or more specs from JIGPLAN.

When writing WUs, reference specs by ID (e.g., "S-147"). The spec's acceptance criteria become your WU's acceptance criteria.

### Constraints

JIGPLAN defines constraints that flow into every WU:
- **FORBIDDEN bricks**: Code sub-agents must not touch
- **Layer constraints**: Dependency direction rules
- **Clean break**: No compatibility shims (unless JIGPLAN says otherwise)

**See:** `docs/jig/contextBricks.md` for brick/layer fundamentals.

### Fresh Agent Review (New in v2)

The agent creating the PLAN has JIGPLAN context in working memory. The executing agent won't. This context gap causes friction during execution.

**Solution:** Before human approval, spawn a fresh agent to review the PLAN cold. This agent identifies ambiguities that would block execution. Resolve them via codebase exploration and update the PLAN.

**Lens:** Execution readiness (types, locations, dependencies, naming consistency).

---

## Process

### Step 1: Extract Constraints from JIGPLAN

Pull these into PLAN header:

```markdown
## Constraints from JIGPLAN

**FORBIDDEN Bricks** (do not modify):
- B-protocol-core
- B-data-models

**Layer Constraints:**
- B-new-brick at layer 1
- B-existing at layer 2
- No upward dependencies
```

### Step 2: Identify Work Unit Boundaries

Review JIGPLAN's O/S Node Reconciliation and @jig Decorator Changes. Group work into WUs based on:

**Cohesion:**
- One spec per WU (ideal)
- Related specs that must be implemented together (acceptable)
- Never mix unrelated specs

**Dependencies:**
- What must exist before this can be built?
- Foundation code before code that uses it
- Tests verify specs, so spec's code must exist first

**Size:**
- Target 60-90 minutes per WU
- Single testable goal
- If WU feels too big, split it

### Step 3: Sequence Work Units

Order WUs by dependency:

```
WU1: Foundation (no dependencies)
  ↓
WU2: Core logic (depends on WU1)
  ↓
WU3: Integration (depends on WU1, WU2)
  ↓
WU4: Cleanup (delete legacy code - always last)
```

**Rules:**
- Layer 0 code before layer 1 code
- New modules before code that imports them
- Implementation before integration tests
- Cleanup/deletion WUs go last

### Step 4: Write Each Work Unit

Each WU needs these sections:

#### Goal
Single sentence. What does this WU accomplish?

```markdown
**Goal**: Implement CRDT value observation with subscribe/unsubscribe lifecycle.
```

#### Specs Addressed
Which S-nodes from JIGPLAN does this WU implement?

```markdown
**Specs Addressed**: S-147, S-148
```

#### Acceptance Criteria
Copy from spec's acceptance criteria. Add implementation-specific criteria.

```markdown
**Acceptance Criteria**:
- [ ] subscribe(key, callback) registers observer for specific key
- [ ] Callback invoked with (key, old_value, new_value) on change
- [ ] unsubscribe(key, callback) removes observer
- [ ] Tests with @jig.verifies decorators
- [ ] Code with @jig.implements decorators
- [ ] jigy rebuild && jigy validate passes
```

#### Success Gates
Pass/fail conditions the orchestrator verifies:

```markdown
**Success Gates** (all must pass):
- [ ] All tests pass: pytest test/crdt/test_observe.py -v
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors
```

#### Escalation Triggers
When sub-agent must stop and ask:

```markdown
**Escalation Triggers** (stop and ask human if):
- Test failures persist after 2 retry attempts
- Implementation approach must deviate from JIGPLAN
- FORBIDDEN brick modification needed
- Layer constraint violation detected
- Ambiguity in spec acceptance criteria
- Discovered need for backwards compatibility (not in SCOPE)
```

#### Implementation Notes
Guidance for sub-agent:

```markdown
**Implementation Notes**:
- Files: src/ase/crdt/observe.py (new), test/crdt/test_observe.py (new)
- Pattern: Follow existing Registry patterns in codebase
- Decorators to add: @jig.implements("S-147") on subscribe(), notify()
- Decorators to add: @jig.verifies("S-147") on test_subscribe_*
```

#### Resolved Context (New in v2)
Findings from Fresh Agent Review - types, locations, decisions verified against codebase:

```markdown
**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| bike_elements type | Dict[str, Union[LWW, ORSet, PNCounter]] | bike_state.py:132 |
| Posture location | device_state.py:32 (must extract) | grep class Posture |
```

#### Human Verification
Commands human can run to verify:

```markdown
**Human Verification**:
```bash
pytest test/crdt/test_observe.py -v
jigy rebuild && jigy validate
```
```

### Step 5: Create Checklist

Summary at top of PLAN:

```markdown
## Work Unit Checklist

- [ ] WU1: ObserverRegistry core — tests ☐ / code ☐ / docs ☐
- [ ] WU2: Subscribe/unsubscribe lifecycle — tests ☐ / code ☐ / docs ☐
- [ ] WU3: SimOps integration — tests ☐ / code ☐ / docs ☐
- [ ] WU4: Delete legacy polling — tests ☐ / code ☐ / docs ☐
```

### Step 6: Add Execution Log and Completion Sections

These are filled in during/after execution, but create the structure:

```markdown
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
```

### Step 7: Fresh Agent Review (Required)

**Purpose:** Verify the PLAN is self-contained before human approval. The creating agent has context the executing agent won't have.

**Why this matters:**
- Fresh eyes catch assumptions baked into creator's mental model
- Questions expose missing context the executor will need
- Resolution via exploration grounds the plan in actual code
- Updated PLAN is self-contained (no hidden context required)

#### 7.1: Spawn Review Agent

**Review agent has full codebase access** via Glob, Grep, Read tools.

Use this exact prompt:

```
You are reviewing a PLAN document before execution.

Read: <path to PLAN file>

Your task: Identify anything that would block or confuse an agent executing this plan.

Categories:
1. **Type ambiguity** - field mentioned but type unclear
2. **Location unknown** - "import X" but from where?
3. **Existence uncertain** - "use Y" but does Y exist?
4. **Naming inconsistency** - plan says "lamport" but code says "counter"
5. **Hidden dependency** - WU3 needs WU1 but not stated
6. **Missing context** - assumes knowledge not in the document

For each finding:
- State the issue clearly
- Classify: (A) resolvable via codebase exploration, (B) needs human input
- If (A), suggest what to search for

Do NOT execute any WU. Review only.
```

#### 7.2: Resolve Category (A) Issues

For each issue the review agent marks as (A) resolvable:

1. **Launch exploration agents** in parallel to investigate
2. **Gather concrete answers** with file:line references
3. **Update relevant WU sections** with findings

Add findings to the **Resolved Context** table in each affected WU, or to a **Key Existing Code References** section if broadly applicable.

#### 7.3: Escalate Category (B) Issues

Issues requiring human input:
- Present to human with context
- Get decision
- Document in PLAN

#### 7.4: Re-Review If Needed

If changes affected ≥3 WUs or introduced new dependencies, run another review pass. Maximum 2 re-review iterations - if still finding blocking issues after 2 passes, escalate to human.

Exit when review agent reports no blocking ambiguities.

#### 7.5: Exit Criteria

Fresh Agent Review is complete when:
- [ ] Review agent identifies no category (A) or (B) issues, OR review agent reports no issues at all → proceed directly to human approval
- [ ] All (A) issues resolved via codebase exploration
- [ ] All (B) issues resolved via human input OR escalated with documented rationale
- [ ] All resolved context is documented in PLAN
- [ ] PLAN is self-contained (executor needs no external context)

---

## PLAN Template

```markdown
# PLAN: <Feature Name>

- **SCOPE**: docs/wip/SCOPE-<feature>.md
- **JIGPLAN**: docs/wip/JIGPLAN-<feature>.md
- **Start**: <YYYY-MM-DD>
- **Status**: Draft | In-Progress | Complete
- **Branch**: <git-branch-name>

---

## Constraints from JIGPLAN

**FORBIDDEN Bricks** (do not modify):
- <brick-id>

**Layer Constraints:**
- <brick> at layer N
- No upward dependencies

**Clean Break:**
- <what to delete, no compat shims>

---

## Key Existing Code References

(Populated during Fresh Agent Review)

| Concern | Location | Notes |
|---------|----------|-------|
| <type/module> | <file:line> | <relevant context> |

---

## Execution Order

(Dependency graph for parallel execution)

```
WU1 ──┬── WU3
      └── WU4 ── WU5
WU2 ────────────┘
```

---

## Test Strategy

- **New tests**: <what gets fresh tests>
- **Existing tests**: <what must keep passing>
- **Deleted tests**: <what goes away in cleanup>

---

## Work Unit Checklist

- [ ] WU1: <title> — tests ☐ / code ☐
- [ ] WU2: <title> — tests ☐ / code ☐
- [ ] WU(N-1): Validation — SCOPE verified ☐
- [ ] WUN: Cleanup — legacy deleted ☐ (if applicable)

---

## Work Units

### Work Unit 1: <Title>

**Goal**: <single testable goal>

**Specs Addressed**: S-NNN

**Acceptance Criteria**:
- [ ] <from spec>
- [ ] Tests with @jig.verifies decorators
- [ ] Code with @jig.implements decorators
- [ ] jigy rebuild && jigy validate passes

**Success Gates** (all must pass):
- [ ] All tests pass: pytest <path> -v
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors

**Escalation Triggers** (stop and ask human if):
- Test failures persist after 2 retry attempts
- Implementation approach must deviate from JIGPLAN
- FORBIDDEN brick modification needed
- Layer constraint violation detected
- Ambiguity in spec acceptance criteria
- Discovered need for backwards compatibility

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| <what was unclear> | <concrete answer> | <file:line> |

**Implementation Notes**:
- Files: <paths>
- Pattern: <guidance>
- Decorators: <what to add>

**Human Verification**:
```bash
pytest <path> -v
jigy rebuild && jigy validate
```

---

### Work Unit N: <Title>

(Same structure)

---

## Execution Log

(Filled in by orchestrator)

### WU1 Execution

**Sub-Agent Report:**
```
(paste report)
```

**Parent Verification:**
```bash
(verification output)
```

**Decision:** CONTINUE | STOP | RETRY

**Commit:** <hash>

---

## Completion Summary

**Scope Delivered:**
- <summary>

**JIG Summary:**
(See JigPlanOrchWorkflow.md for format)

**Clean Break Actions:**
- [ ] Deleted deprecated O/S nodes
- [ ] Deleted legacy code modules
- [ ] Final jigy rebuild && jigy validate passed

**Reflection Roll-Up:**
- Repeatable wins: <patterns that worked>
- Systemic frictions: <process issues>
- Open questions: <items for future work>
```

---

## Work Unit Sizing Guidelines

### Too Small (combine with another)
- "Add import statement"
- "Create empty file"
- "Add single decorator"

### Right Size (60-90 min)
- "Implement subscribe() with tests"
- "Add observation event routing to SimOps"
- "Delete legacy polling module and update imports"

### Too Large (split)
- "Implement entire CRDT observation layer"
- "Refactor all event handling"
- "Add feature with UI, API, and database changes"

### Splitting Large WUs

If a WU is too large, split by:

1. **Vertical slice**: Foundation → usage
   - WU1: Core data structure
   - WU2: Operations on that structure
   - WU3: Integration with other systems

2. **Horizontal slice**: By spec
   - WU1: S-147 (subscribe)
   - WU2: S-148 (unsubscribe)
   - WU3: S-149 (filtering)

---

## Common Patterns

### Pattern: New Module

```markdown
### Work Unit 1: Create ObserverRegistry Core

**Goal**: Create ObserverRegistry class with basic registration.

**Specs Addressed**: S-147

**Implementation Notes**:
- Files: src/ase/crdt/observe.py (new)
- Add to brick B-crdt-observe in bricks.yaml: M-ase.crdt.observe
```

### Pattern: Integration

```markdown
### Work Unit 3: SimOps Observer Integration

**Goal**: Route CRDT observation events through SimOps event system.

**Specs Addressed**: S-143 (updated)

**Implementation Notes**:
- Files: src/ase/simops/events.py (modify)
- This WU modifies existing code - verify no FORBIDDEN brick touched
```

### Pattern: Validation WU (MUST - Before Cleanup)

**Purpose:** Verify SCOPE problem is solved, not just specs implemented.

Unit tests verify specs. Validation WU verifies SCOPE. Specs can be implemented perfectly while SCOPE remains unsolved (wiring bugs, missing lifecycle hooks). Validation WU catches this by testing at system boundaries.

**Quality hierarchy:**
- **BEST:** Integration Test - evergreen, automated, catches regressions forever
- **BETTER:** Demo Script - repeatable, can be run by human or agent
- **OKAY:** Manual Checklist - works but not automated, doesn't catch regressions

**Prefer Integration Test.** If not feasible, document why.

```markdown
### Work Unit N: Validation

**Goal**: Verify SCOPE problem is solved at system boundary.

**SCOPE Reference**:
"<quote the core need from SCOPE>"

**Validation Approach**: Integration Test (preferred) | Demo Script | Manual Checklist

**Verification Steps**:
```bash
# What to run / do to verify SCOPE is satisfied
```

**Expected Result**:
<what success looks like in user/system terms>

**Deliverable**:
- [ ] Integration test added: test/<path> (BEST)
- OR Demo script documented below (BETTER)
- OR Checklist completed, findings in JOURNAL (OKAY)

**If Validation Approach is not Integration Test**:
Reason: <why integration test isn't feasible for this feature>

**If Validation Fails**:
- Investigate root cause (likely wiring/integration gap)
- Fix the issue
- Add regression test (upgrade to Integration Test if possible)
- Re-run validation
```

### Pattern: Cleanup (After Validation)

```markdown
### Work Unit N+1: Delete Legacy Code

**Goal**: Remove deprecated module and all references.

**Specs Addressed**: (none - cleanup)

**Implementation Notes**:
- Delete: src/ase/legacy/poller.py
- Delete: test/legacy/test_polling.py
- Remove imports from: src/ase/simops/core.py
- After this WU: delete jig/specifications/S-089.md
```

**Note:** Cleanup comes AFTER Validation so old code is available for comparison if Validation reveals issues.

---

## Validation

Before submitting PLAN:

- [ ] All specs from JIGPLAN have at least one WU
- [ ] WUs are properly sequenced (dependencies respected)
- [ ] Each WU has single testable goal
- [ ] FORBIDDEN bricks listed in constraints
- [ ] **Validation WU included** (verifies SCOPE is solved)
- [ ] Validation WU comes before Cleanup WU
- [ ] Cleanup WU is last (if applicable)
- [ ] Checklist matches WU list
- [ ] **Fresh Agent Review completed** (Step 7)
- [ ] All resolved context documented in WUs
- [ ] Key Existing Code References populated

---

## Constraints

### DO NOT

- **Include architectural decisions** - Those belong in JIGPLAN
- **Create WUs for specs not in JIGPLAN** - Stay in scope
- **Skip escalation triggers** - Sub-agents need guardrails
- **Combine unrelated specs** - Keep WUs focused
- **Skip Fresh Agent Review** - Executor needs self-contained plan

### MUST

- **Include Validation WU** - Verifies SCOPE is solved, not just specs implemented
- **Reference JIGPLAN constraints** - FORBIDDEN bricks, layers
- **Sequence by dependency** - Foundation before usage
- **Include success gates** - Orchestrator needs verification criteria
- **Size appropriately** - 60-90 min target
- **Complete Fresh Agent Review** - Resolve ambiguities before human approval

### PREFER

- **One spec per WU** - Easier to verify
- **Conservative sizing** - Split if uncertain
- **Explicit implementation notes** - Help sub-agents succeed
- **Parallel exploration** - Batch codebase lookups for efficiency

---

## Version History

- **2.0.0** (2026-01-08): Added Fresh Agent Review (Step 7). PLANs must be reviewed by fresh agent before human approval. Added Resolved Context section to WU template. Added Key Existing Code References, Execution Order, and Test Strategy sections to PLAN template. Added max iteration limit (2) on re-review loops. Clarified exit criteria for clean-pass case.
- **1.1.0** (2025-12-18): Added Validation WU pattern (MUST). Verifies SCOPE is solved, not just specs implemented. Prefer Integration Test over Demo Script over Manual Checklist.
- **1.0.1** (2025-12-18): Added note about JOURNAL file created during execution
- **1.0.0** (2025-12-18): Initial version

---

**Next:** After PLAN is created and Fresh Agent Review completed, execute with taskDoPLAN.md. The orchestrator:
- Launches sub-agents following taskDoWU.md
- Maintains JOURNAL-<feature>.md throughout execution (see taskDoPLAN.md)
