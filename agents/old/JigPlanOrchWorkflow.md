# JIG Plan Orchestration Workflow

**Version:** 1.0.0
**Date:** 2025-12-18
**Status:** Draft
**Audience:** AI coding agents + Human developers

---

## Overview

This document describes the complete workflow for executing JIG-aligned development using parent-agent orchestration with sub-agents. The workflow separates architectural planning (requiring human judgment) from implementation execution (automatable with guardrails).

**Core Philosophy:**
- Intent and architecture planning happens BEFORE implementation
- Human approval gates prevent runaway automation
- **Clean break is the DEFAULT** - burn ships, no backwards compatibility hacks
- Sub-agents execute within explicit constraints
- Existing O/S nodes are reused/updated, not proliferated

---

## Clean Break as Default

### Why Clean Break is Default

AI agents tend to add compatibility shims and slow deprecation patterns by default (this behavior is heavily represented in training data). To counter this bias, this workflow **defaults to clean break** for all work.

**Clean break means:**
- Old code paths are DELETED, not feature-flagged
- Old tests are DELETED and new tests written from scratch
- No backwards compatibility shims or adapters
- Unimplemented features raise `NotImplementedError` (fail loudly)
- Deprecated O/S nodes are deleted after validation

### When Backwards Compatibility is Needed

Backwards compatibility is **sometimes legitimate**, but it must be **explicitly planned**. Valid reasons include:

- Public API with external consumers who need migration time
- Critical path code where rollback capability is required
- Multi-team coordination where not everyone can migrate simultaneously
- Regulatory/compliance requirements

**These cases are rare in a single-codebase context.**

### How to Request Backwards Compatibility

If backwards compatibility is needed, it **MUST be articulated in the SCOPE document**:

```markdown
## Backwards Compatibility Requirement

**What needs backwards compat:** Legacy polling API
**Who needs it:** External monitoring tools (Datadog integration)
**Why:** External tools can't be updated simultaneously
**Duration:** 2 sprints (until external tools migrate)
**Migration path:** Deprecation warning in v1, removal in v2
```

If SCOPE does not articulate backwards compatibility requirements, **clean break is assumed**.

### How JIGPLAN Handles Backwards Compatibility

When SCOPE requests backwards compatibility, JIGPLAN must plan for it explicitly:

```markdown
## Backwards Compatibility Plan

**Parallel implementation duration:** 2 sprints
**Old code to preserve:** src/ase/legacy/poller.py
**Deprecation signals:**
- DeprecationWarning on import
- Log warning on each poll() call
**Migration documentation:** docs/migration/polling-to-observation.md
**Deletion timeline:** After v2.0 release
**Compat consumer list:**
- Datadog integration (external)
- Legacy test harness (internal - migrate in sprint 1)
```

**Note:** This is the EXCEPTION, not the rule. Most work should follow clean break.

### Escalation: Discovered Need for Backwards Compatibility

If during implementation you discover that backwards compatibility is needed (not anticipated in SCOPE):

1. **STOP immediately** - this is an escalation trigger
2. **Do not implement compatibility shims** without approval
3. **Report to human** with:
   - What needs backwards compat
   - Who/what depends on the old behavior
   - Proposed approach
4. **Wait for human decision:**
   - Update SCOPE and JIGPLAN to include compat plan, OR
   - Proceed with clean break (human confirms old consumers can migrate)

---

## Workflow Phases

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PLANNING PHASE                                   │
│                    (Human + Agent Collaboration)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   SCOPE ──────────────► JIGPLAN ──────────────► PLAN                    │
│   (Human)               (Agent drafts,          (Agent)                  │
│                          Human approves)                                 │
│                               │                                          │
│                               ▼                                          │
│                        ⛔ HUMAN GATE                                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       EXECUTION PHASE                                    │
│                  (Parent Agent Orchestrates)                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Create Branch ──► WU1 ──► WU2 ──► ... ──► WUN ──► Cleanup ──► Report  │
│                     │       │               │         │           │      │
│                     ▼       ▼               ▼         ▼           ▼      │
│                 Sub-agent Sub-agent    Sub-agent   Delete     JIG        │
│                 executes  executes     executes    deprecated Summary    │
│                     │       │               │       O/S nodes            │
│                     ▼       ▼               ▼                            │
│                 Update PLAN + commit after each WU                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Bricks and Layers Fundamentals

**See:** `docs/jig/contextBricks.md` for complete brick/layer reference.

### Key Concepts

**Bricks** partition functions into architectural units:
- **No gaps** - every function is assigned to exactly one brick
- **No overlaps** - no function in multiple bricks
- **Class integrity** - all methods of a class must be in same brick

**Layers** stratify bricks vertically:
- A brick at layer N may depend ONLY on layers 0..(N-1)
- Dependencies flow DOWN, never up
- Violations are errors, not warnings

### Brick Definition

```yaml
bricks:
  - id: B-core-utils        # Semantic kebab-case naming
    name: Core Utilities
    layer: 0                # Foundation
    units:
      - M-utils.io          # All functions in module
      - C-utils.Parser      # All methods of class
      - F-utils.helpers.foo # Single function
```

**Unit prefixes:** `M-` (module), `C-` (class), `F-` (function)

### Derived vs Stored Properties

**Stored in bricks.yaml:** brick ID, name, layer, unit membership

**Computed (not stored):**
- Specs assigned (from `@jig.implements` decorators)
- Dependencies (from call graph)
- Public API (functions called from outside brick)

### FORBIDDEN Bricks

FORBIDDEN is a **per-work-scope** constraint, NOT a permanent brick property.

Each JIGPLAN defines which bricks are off-limits for that specific work:
- Prevents scope creep ("while I'm here...")
- Provides sub-agent guardrails
- Limits blast radius of changes

**Any brick can be FORBIDDEN regardless of layer.** The constraint is "don't touch during THIS work."

If modification needed → STOP and escalate.

---

## Artifact Locations

All planning artifacts live in the same working directory (side-by-side):

```
docs/wip/
├── SCOPE-<feature>.md      # Problem description (human-authored)
├── JIGPLAN-<feature>.md    # Architecture + intent plan (agent-drafted, human-approved)
├── PLAN-<feature>.md       # Implementation work units (agent-authored)
└── JOURNAL-<feature>.md    # Execution journal (orchestrator-maintained)
```

**Note:** These are NOT JIG artifacts. They are working documents that drive JIG artifact changes.

---

## Phase 1: SCOPE Document

### Purpose

Freeform problem description authored by the human. Provides the "why" and "what" that drives all subsequent planning.

### Author

Human (possibly with agent assistance for research)

### Content

Freeform. May include:
- Problem statement
- Business context and value
- User stories or use cases
- Technical constraints
- References to existing code, specs, or documentation
- Sketches of desired behavior
- Known risks or concerns
- **Backwards compatibility requirements** (if any - see below)

### Backwards Compatibility in SCOPE

**If SCOPE does not mention backwards compatibility, clean break is assumed.**

If backwards compatibility IS needed, SCOPE must articulate:
- What needs backwards compat
- Who/what depends on the old behavior
- Why they can't migrate immediately
- Proposed duration of parallel support
- Migration path

See "Clean Break as Default" section for details.

### Quality Gate

The SCOPE must be rich enough to drive JIGPLAN creation. If context is lacking, the agent drafting JIGPLAN should ask clarifying questions rather than guess.

### Example

```markdown
# SCOPE: CRDT Observable Layer

## Problem

SimOps needs to observe CRDT state changes for the trace viewer. Currently,
state polling is inefficient and misses transient states.

## Desired Behavior

- Subscribe to specific CRDT keys or patterns
- Receive callbacks when values change
- Support both sync and async observers
- Integrate with existing SimOps event system

## Constraints

- Must not modify B-protocol-core (foundation layer)
- Must work with existing LWWRegister and PNCounter types
- Performance: <1ms overhead per state change

## References

- Existing CRDT impl: src/ase/crdt/
- SimOps event system: src/ase/simops/events.py
- Related spec: S-142 (CRDT state access)
```

---

## Phase 2: JIGPLAN Document

### Purpose

The key architectural planning artifact. Specifies the complete future state of bricks, O/S nodes, and @jig decorators. Drafted by agent, approved by human.

### Author

Agent drafts based on SCOPE + codebase analysis. Human reviews and approves.

### Content Sections

#### Section 1: Summary

Brief overview of what the JIGPLAN covers.

```markdown
## Summary

This JIGPLAN defines the architecture for adding CRDT observation capabilities
to support SimOps trace viewing. Creates one new brick (B-crdt-observe) at
layer 1, modifies one existing brick (B-simops-core), reuses two existing
specs, and creates three new specs.
```

#### Section 2: O/S Node Reconciliation

Explicit mapping of what happens to Outcomes and Specifications.

**Strong preference for REUSE and UPDATE over CREATE.**

```markdown
## O/S Node Reconciliation

### Outcomes

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | O-012 | Observable System State | Existing outcome covers observation needs |

### Specifications

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | S-142 | CRDT State Access | Covers basic read operations |
| UPDATE | S-143 | Transport Event Emission | Add observation event types |
| DELETE | S-089 | Legacy State Polling | Superseded by observation pattern |
| CREATE | S-147 | CRDT Value Observation | New behavior (see below) |
| CREATE | S-148 | Observer Lifecycle | New behavior (see below) |
| CREATE | S-149 | Observation Filtering | New behavior (see below) |
```

**For UPDATE nodes:** Include before/after diff or describe changes:

```markdown
### S-143 Update Details

**Current acceptance criteria:**
- Transport emits connection events
- Transport emits message events

**Add acceptance criteria:**
- Transport emits observation events for CRDT state changes
- Observation events include key, old_value, new_value
```

**For CREATE nodes:** Full spec content following evergreen guidelines:

```markdown
### S-147: CRDT Value Observation (NEW)

---
id: S-147
type: specification
implements: [O-012]
---

# CRDT Value Observation

Clients can subscribe to CRDT value changes and receive callbacks when
observed values are modified.

**Acceptance Criteria:**
- subscribe(key, callback) registers observer for specific key
- Callback invoked with (key, old_value, new_value) on change
- Multiple observers per key supported
- Observer receives current value on subscription (initial callback)

**Rationale:** Enables reactive UI updates without polling.
```

**For DELETE nodes:** Specify what supersedes or why obsolete:

```markdown
### S-089 Deletion Rationale

S-089 (Legacy State Polling) is deleted because:
- Behavior is replaced by S-147 (observation pattern)
- No code should implement polling after this work
- Git history preserves the spec if needed

**Clean break:** All code with @jig.implements("S-089") will be deleted.
```

#### Section 3: Brick Scope

Explicit mapping of what happens to bricks.

```markdown
## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| CREATE | B-crdt-observe | 1 | New observation layer |
| MODIFY | B-simops-core | 2 | Add observer integration |
| FORBIDDEN | B-protocol-core | 0 | Foundation - must not touch |
| FORBIDDEN | B-data-models | 0 | Foundation - must not touch |
| UNAFFECTED | B-cli | 2 | No changes needed |
```

**For CREATE bricks:** Specify units and layer:

```markdown
### B-crdt-observe (NEW)

- **Layer:** 1
- **Purpose:** CRDT observation and subscription management
- **Units:**
  - M-ase.crdt.observe
  - C-ase.crdt.observe.ObserverRegistry
- **Dependencies:** B-core-utils (layer 0), B-data-models (layer 0)
```

**For MODIFY bricks:** Specify what changes:

```markdown
### B-simops-core Modifications

- **Current units:** M-ase.simops.core, M-ase.simops.events
- **Add units:** (none - using existing modules)
- **Layer change:** (none - stays at layer 2)
- **New dependencies:** B-crdt-observe (layer 1)
- **Changes:** Add observation event routing to events.py
```

**FORBIDDEN bricks:** Explicitly constrain sub-agents:

```markdown
### FORBIDDEN Bricks

These bricks MUST NOT be modified by any work unit:

- **B-protocol-core** (layer 0): Foundation CRDT types. Changes here cascade everywhere.
- **B-data-models** (layer 0): Core data structures. Stable API.

**Sub-agent constraint:** Any modification to FORBIDDEN bricks is an immediate
escalation trigger. Stop and ask human.
```

#### Section 4: Layer/Dependency Analysis

Verify architectural constraints.


```
## Layer/Dependency Analysis

### Current Layer Structure (Affected Bricks)

Layer 0: FORBIDDEN
  B-core-utils ← no changes
  B-data-models ← no changes

Layer 1: AFFECTED
  B-crdt-observe (NEW)
    └─► depends on: B-core-utils, B-data-models ✓

Layer 2: AFFECTED
  B-simops-core (MODIFY)
    └─► depends on: B-core-utils, B-crdt-observe ✓


### Dependency Constraints

- B-crdt-observe (layer 1) MUST NOT depend on B-simops-core (layer 2)
- No circular dependencies between B-crdt-observe and B-simops-core
- B-simops-core MAY depend on B-crdt-observe (layer 2 → layer 1 is valid)

### Validation Commands

After implementation, verify with:

jigy rebuild && jigy validate
jigy layers  # Confirm layer structure
```


#### Section 5: @jig Decorator Changes

Explicit guidance on decorator modifications.

```markdown
## @jig Decorator Changes

### Decorators to ADD

| Type | Location | Spec |
|------|----------|------|
| implements | F-ase.crdt.observe.subscribe | S-147 |
| implements | F-ase.crdt.observe.unsubscribe | S-148 |
| implements | F-ase.crdt.observe.ObserverRegistry.notify | S-147 |
| verifies | T-test_observe.test_subscribe_receives_changes | S-147 |
| verifies | T-test_observe.test_unsubscribe_stops_callbacks | S-148 |
| verifies | T-test_observe.test_filter_by_pattern | S-149 |

### Decorators to REMOVE

| Type | Location | Spec | Reason |
|------|----------|------|--------|
| implements | F-ase.legacy.poller.poll_state | S-089 | Spec deleted |
| verifies | T-test_legacy.test_polling_interval | S-089 | Spec deleted |

### Decorators to MODIFY

| Type | Location | Old Spec | New Spec | Reason |
|------|----------|----------|----------|--------|
| implements | F-ase.simops.events.emit | S-143 | S-143 | Spec updated (same ID) |

**Note:** When spec is updated but ID unchanged, decorator stays same. Just
ensure implementation matches updated acceptance criteria.
```

#### Section 6: Clean Break Checklist

Explicit acknowledgment of clean break approach.

```markdown
## Clean Break Checklist

This work follows the Clean Break Protocol (taskCleanBreak.md):

- [ ] Old code paths will be DELETED, not feature-flagged
- [ ] Old tests will be DELETED and new tests written from scratch
- [ ] No backwards compatibility shims
- [ ] Unimplemented features will raise NotImplementedError (fail loudly)
- [ ] Deleted O/S nodes removed after final validation

### Code to Delete

- `src/ase/legacy/poller.py` (entire module)
- `test/legacy/test_polling.py` (entire module)
- Any imports of legacy.poller

### O/S Nodes to Delete (After Validation)

- `jig/specifications/S-089.md`
```

---

## Phase 3: PLAN Document

### Purpose

Implementation work units with success gates and escalation triggers. Pure execution plan - no architectural decisions (those are in JIGPLAN).

### Author

Agent, after JIGPLAN is human-approved.

### Relationship to JIGPLAN

- PLAN references JIGPLAN for architectural constraints
- Sub-agents receive PLAN for execution context
- JIGPLAN's FORBIDDEN bricks become sub-agent constraints
- JIGPLAN's decorator guidance informs test/code structure

### Template

```markdown
# PLAN: <Feature Name>

- **SCOPE**: docs/wip/SCOPE-<feature>.md
- **JIGPLAN**: docs/wip/JIGPLAN-<feature>.md
- **Start**: <YYYY-MM-DD>
- **Status**: Draft | In-Progress | Complete
- **Branch**: <git-branch-name>

## Constraints from JIGPLAN

**FORBIDDEN Bricks** (do not modify):
- B-protocol-core
- B-data-models

**Layer Constraints:**
- B-crdt-observe at layer 1
- B-simops-core at layer 2
- No upward dependencies

## Work Unit Checklist

- [ ] WU1: <title> — tests ☐ / code ☐ / docs ☐
- [ ] WU2: <title> — tests ☐ / code ☐ / docs ☐
- [ ] WU3: <title> — tests ☐ / code ☐ / docs ☐

## Work Units

### Work Unit 1: <Title>

**Goal**: <Single, testable goal>

**Specs Addressed**: S-147

**Acceptance Criteria**:
- [ ] Tests for S-147 acceptance criteria written and passing
- [ ] @jig.verifies("S-147") decorators added to tests
- [ ] Implementation code written
- [ ] @jig.implements("S-147") decorators added to code
- [ ] jigy rebuild && jigy validate passes

**Success Gates** (all must pass):
- [ ] All tests pass: pytest test/crdt/test_observe.py -v
- [ ] jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors

**Escalation Triggers** (stop and ask human if):
- Test failures persist after 2 retry attempts
- Implementation approach must deviate from JIGPLAN
- FORBIDDEN brick modification needed
- Layer constraint violation detected
- Ambiguity in spec acceptance criteria
- Discovered need for backwards compatibility (not in SCOPE)

**Implementation Notes**:
- Files: src/ase/crdt/observe.py (new)
- Tests: test/crdt/test_observe.py (new)
- Pattern: Follow existing ObserverRegistry patterns in codebase

**Human Verification**:
```bash
pytest test/crdt/test_observe.py -v
jigy rebuild && jigy validate
```

---

### Work Unit N: <Title>

(Same structure as WU1)

---

## Execution Log

(Filled in during orchestration)

### WU1 Execution

**Sub-Agent Report:**
```
Status: COMPLETE
Gates: 4/4 passed
...
```

**Parent Verification:**
```bash
$ pytest test/crdt/test_observe.py -v
18 passed in 0.5s ✓
```

**Decision:** CONTINUE

**Commit:** abc1234

---

## Completion Summary

(Filled in after all WUs complete)

**Scope Delivered:**
- <Summary of what was accomplished>

**JIG Summary:**
(See Section: JIG Summary Report)

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

## Phase 4: Orchestrated Execution

### Parent Agent Role

The parent agent orchestrates execution:

1. **Create branch** at start of execution
2. **Create JOURNAL file** for execution logging
3. **Launch sub-agents** for each WU sequentially
4. **Verify gates** independently after each WU
5. **Write journal entry** after each WU (synthesize sub-agent report + own observations)
6. **Update PLAN** with execution log after each WU
7. **Commit** after each WU (gives next sub-agent context)
8. **Decide** CONTINUE / STOP / RETRY based on gates and triggers
9. **Execute cleanup** (delete deprecated nodes) after all WUs pass
10. **Write journal synthesis** (patterns, friction, suggestions)
11. **Generate JIG Summary** as final confirmation

### Sub-Agent Role

Sub-agents execute individual WUs:

1. **Receive**: Full PLAN document + "Execute Work Unit N"
2. **Execute**: TDD loop (test first, then implement)
3. **Respect**: FORBIDDEN bricks, layer constraints, decorator guidance
4. **Return**: Structured report (status, gates, issues, questions)

### Sub-Agent Constraints

From JIGPLAN, sub-agents operate under explicit constraints:

- **FORBIDDEN bricks**: Immediate escalation if touched
- **Layer constraints**: Verify no upward dependencies
- **Decorator guidance**: Follow ADD/REMOVE/MODIFY table
- **O/S scope**: Only implement specs listed in JIGPLAN
- **Clean break default**: Do NOT add compatibility shims unless JIGPLAN explicitly includes a Backwards Compatibility Plan

### Validation WU

**Every PLAN includes a Validation WU** (second-to-last, before Cleanup WU).

**Purpose:** Verify SCOPE problem is solved, not just specs implemented. Unit tests verify specs; Validation WU verifies SCOPE.

**Sequence:** Implementation WUs → **Validation WU** → Cleanup WU → Post-execution

**Quality hierarchy:**
- **BEST:** Integration Test (evergreen, automated)
- **BETTER:** Demo Script (repeatable)
- **OKAY:** Manual Checklist (not automated)

**See:** taskMakePLAN.md for Validation WU template, taskDoPLAN.md for handling failures.

### Decision Framework

**CONTINUE when:**
- Sub-agent status = COMPLETE
- All success gates passed
- No escalation triggers fired
- No questions for human
- Changes match WU scope

**STOP when:**
- Any success gate failed after retry
- Any escalation trigger fired
- Sub-agent has questions
- FORBIDDEN brick touched
- Layer violation detected
- Discovered need for backwards compatibility not in SCOPE

**RETRY when (max 2 attempts):**
- Transient test failures
- Missing @jig decorators
- Simple linting errors

### Commit Cadence

After each WU:

```bash
git add src/ test/ jig/ docs/wip/PLAN-<feature>.md
git commit -m "WU<N>: <title> (S-<specs>)

Implements: S-147
Tests: T-test_observe.test_subscribe_receives_changes
Alignment: verified

See: docs/wip/PLAN-<feature>.md → Work Unit N"
```

---

## Phase 5: Cleanup and JIG Summary

### Cleanup Actions

After all WUs complete successfully:

1. **Delete deprecated O/S nodes** (as specified in JIGPLAN)
2. **Delete legacy code** (as specified in JIGPLAN clean break section)
3. **Run final validation**:
   ```bash
   jigy rebuild && jigy validate
   ```

### JIG Summary Report

The JIG Summary is a confirmation report responding to the JIGPLAN. It confirms what was actually done vs. what was planned.

Add to PLAN completion section:

```markdown
## JIG Summary Report

### O/S Node Changes (vs JIGPLAN)

| Planned | Actual | Node | Notes |
|---------|--------|------|-------|
| REUSE | ✓ REUSED | O-012 | |
| REUSE | ✓ REUSED | S-142 | |
| UPDATE | ✓ UPDATED | S-143 | Added observation event criteria |
| DELETE | ✓ DELETED | S-089 | Removed after final validation |
| CREATE | ✓ CREATED | S-147 | |
| CREATE | ✓ CREATED | S-148 | |
| CREATE | ✓ CREATED | S-149 | |

### Brick Changes (vs JIGPLAN)

| Planned | Actual | Brick | Notes |
|---------|--------|-------|-------|
| CREATE | ✓ CREATED | B-crdt-observe | Layer 1, 3 units |
| MODIFY | ✓ MODIFIED | B-simops-core | Added observer integration |
| FORBIDDEN | ✓ UNTOUCHED | B-protocol-core | |
| FORBIDDEN | ✓ UNTOUCHED | B-data-models | |

### @jig Decorator Changes (vs JIGPLAN)

**Added:** 6 decorators (3 implements, 3 verifies)
**Removed:** 2 decorators (1 implements, 1 verifies)
**Modified:** 0 decorators

| Planned | Actual | Type | Location | Spec |
|---------|--------|------|----------|------|
| ADD | ✓ ADDED | implements | F-ase.crdt.observe.subscribe | S-147 |
| ADD | ✓ ADDED | implements | F-ase.crdt.observe.unsubscribe | S-148 |
| ADD | ✓ ADDED | implements | F-ase.crdt.observe.ObserverRegistry.notify | S-147 |
| ADD | ✓ ADDED | verifies | T-test_observe.test_subscribe_receives_changes | S-147 |
| ADD | ✓ ADDED | verifies | T-test_observe.test_unsubscribe_stops_callbacks | S-148 |
| ADD | ✓ ADDED | verifies | T-test_observe.test_filter_by_pattern | S-149 |
| REMOVE | ✓ REMOVED | implements | F-ase.legacy.poller.poll_state | S-089 |
| REMOVE | ✓ REMOVED | verifies | T-test_legacy.test_polling_interval | S-089 |

### Validation Results

```bash
$ jigy rebuild && jigy validate
Rebuilding intent graph... done
Rebuilding implementation graph... done
Validating references... ✓
Validating brick partition... ✓
Validating layer constraints... ✓
All validations passed.

$ jigy layers
Layer 0: Foundation (2 bricks)
  B-core-utils, B-data-models

Layer 1: Core Logic (2 bricks)
  B-crdt-core
  B-crdt-observe (NEW)

Layer 2: Interface (2 bricks)
  B-simops-core (MODIFIED)
  B-cli
```

### Deviations from JIGPLAN

(List any differences between planned and actual)

- None. All planned changes executed as specified.

OR

- S-150 was created (unplanned) to cover edge case discovered in WU3.
  Human approved during WU3 escalation.
```

### Execution Journal

The orchestrator maintains a JOURNAL file (`docs/wip/JOURNAL-<feature>.md`) throughout execution. This captures reasoning, friction, and insights - not just outcomes.

**Purpose:**
- Record decision rationale (why CONTINUE vs STOP)
- Capture friction points for process improvement
- Preserve insights for future work
- Enable pattern analysis across executions

**Entry categories:** observation, decision, friction, insight, deviation, question, suggestion, outcome

**Sub-agent contribution:** Sub-agents include a "Notable" field in their reports. Orchestrator synthesizes this into journal entries.

**Synthesis:** At end of execution, orchestrator writes synthesis section covering patterns, friction summary, suggestions, and wins.

**See:** taskDoPLAN.md for full journal format and entry structure.

---

## Human Checkpoints

### Checkpoint 1: JIGPLAN Approval

**Before:** Agent drafts JIGPLAN based on SCOPE
**Gate:** Human reviews and approves JIGPLAN
**After:** Agent creates PLAN

**Human reviews:**
- O/S node reconciliation (reuse vs create decisions)
- Brick scope (especially FORBIDDEN constraints)
- Layer/dependency analysis
- Clean break scope (what gets deleted)

### Checkpoint 2: Escalation During Execution

**Trigger:** Sub-agent fires escalation trigger
**Gate:** Human answers question or approves deviation
**After:** Execution resumes or PLAN is revised

### Checkpoint 3: Final Review (Optional)

**After:** All WUs complete, JIG Summary generated
**Gate:** Human reviews JIG Summary for unexpected deviations
**After:** Merge to main

---

## Integration with Existing JIG Workflow

### Relationship to taskMakePLAN.md and taskDoWU.md

This workflow **supersedes** the WU0 pattern. Instead of WU0 creating O/S nodes inline with implementation, JIGPLAN separates intent planning from implementation.

- **taskMakePLAN.md**: How to create PLAN from SCOPE + JIGPLAN
- **taskDoWU.md**: How sub-agents execute individual WUs

**Old workflow:**
```
SCOPE → WU0 (create O/S) → WU1-N (TDD)
```

**New workflow:**
```
SCOPE → JIGPLAN (architecture + intent) → PLAN (WUs are pure TDD)
```

### Relationship to taskDoPLAN.md

This workflow incorporates taskDoPLAN.md's orchestration patterns:
- Parent/sub-agent model
- Success gates and escalation triggers
- Structured sub-agent reports
- Independent parent verification

### Relationship to Clean Break

This workflow incorporates clean break philosophy:
- No feature flags or backwards compatibility
- Delete old code completely
- Fail loudly for unimplemented features
- Delete deprecated O/S nodes after validation

### JIG Commands

```bash
# After each WU
jigy rebuild && jigy validate

# At completion
jigy rebuild && jigy validate
jigy layers  # Confirm layer structure
```

---

## Example: Complete Workflow

### 1. Human Creates SCOPE

`docs/wip/SCOPE-crdt-observe.md`:
```markdown
# SCOPE: CRDT Observable Layer

SimOps needs to observe CRDT state changes...
(freeform content)
```

### 2. Agent Drafts JIGPLAN

`docs/wip/JIGPLAN-crdt-observe.md`:
```markdown
## Summary
Creates B-crdt-observe brick, reuses O-012, creates S-147/148/149...

## O/S Node Reconciliation
...

## Brick Scope
...

## Layer/Dependency Analysis
...

## @jig Decorator Changes
...

## Clean Break Checklist
...
```

### 3. Human Reviews JIGPLAN

Human approves or requests changes.

### 4. Agent Creates PLAN

`docs/wip/PLAN-crdt-observe.md`:
```markdown
# PLAN: CRDT Observable Layer

## Constraints from JIGPLAN
...

## Work Unit Checklist
- [ ] WU1: ObserverRegistry core
- [ ] WU2: Subscribe/unsubscribe lifecycle
- [ ] WU3: Observation filtering
- [ ] WU4: SimOps integration
- [ ] WU5: Cleanup legacy polling

## Work Units
...
```

### 5. Parent Agent Executes

```
Create branch: feat/crdt-observe
Execute WU1 → sub-agent → verify → commit
Execute WU2 → sub-agent → verify → commit
Execute WU3 → sub-agent → verify → commit
Execute WU4 → sub-agent → verify → commit
Execute WU5 → sub-agent → verify → commit (includes legacy deletion)
Delete S-089.md
Run jigy rebuild && jigy validate
Generate JIG Summary
Update PLAN with completion
Final commit
```

### 6. Human Reviews JIG Summary

Human confirms deviations (if any) are acceptable.

---

## Constraints

### DO NOT

- **Skip JIGPLAN review** - Human must approve architecture before implementation
- **Proliferate O/S nodes** - Strongly prefer REUSE/UPDATE over CREATE
- **Touch FORBIDDEN bricks** - Immediate escalation, no exceptions
- **Add compatibility shims without approval** - Clean break is default; if you discover need for compat, STOP and ask
- **Continue past failed gates** - Stop and ask human

### MUST

- **Draft JIGPLAN before PLAN** - Architecture before implementation
- **Get human approval on JIGPLAN** - Critical gate
- **Follow clean break by default** - Burn ships, fail loudly; backwards compat only if explicitly in SCOPE/JIGPLAN
- **Update PLAN after each WU** - Maintains context for next sub-agent
- **Generate JIG Summary at end** - Confirmation against JIGPLAN

### PREFER

- **REUSE existing O/S nodes** - Prevent specification sprawl
- **Small focused WUs** - 60-90 minutes each
- **Conservative escalation** - Stop and ask when in doubt
- **Explicit constraints** - FORBIDDEN bricks, layer limits

---

## Version History

- **1.2.0** (2025-12-18): Added Validation WU (MUST) - verifies SCOPE is solved before Cleanup WU
- **1.1.0** (2025-12-18): Added Execution Journal to Phase 5; JOURNAL file in artifact locations; orchestrator maintains journal
- **1.0.2** (2025-12-18): Added "Bricks and Layers Fundamentals" section with partition property, derived properties, FORBIDDEN per-scope
- **1.0.1** (2025-12-18): Added "Clean Break as Default" section; backwards compat requires explicit SCOPE articulation
- **1.0.0** (2025-12-18): Initial version capturing Jim + Claude design session

---

**Next:** Apply this workflow to your next feature. Start with SCOPE, draft JIGPLAN, get approval, then execute.
