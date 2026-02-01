# Task: Execute PLAN with Sub-Agents (taskDoPLAN)

**Version:** 2.2.0
**Date:** 2025-12-18
**Audience:** AI coding agents (parent orchestrator)
**Status:** Active
**Related:** JigPlanOrchWorkflow.md, taskMakeJIGPLAN.md, taskMakePLAN.md, taskDoWU.md, contextBricks.md

## Objective

Orchestrate execution of a PLAN by launching sub-agents sequentially, verifying their outputs, and deciding when to continue vs stop and ask human.

**You are the Plan Execution Orchestrator.** Sub-agents execute WUs in fresh context. You maintain continuity, verify outputs, and escalate when needed.

---

## JIG Fundamentals

### The S-F-T Triangle

JIG measures alignment between **intent** (specifications), **implementation** (functions), and **verification** (tests):

```
         S (Specification)
        / \
       /   \
implements  verifies
     /       \
    F ———————→ T
       covers
```

- **F → S** (implements): `@jig.implements("S-001")`
- **T → S** (verifies): `@jig.verifies("S-001")`
- **T → F** (covers): Automatic via test coverage

### JIG Commands

```bash
jigy rebuild && jigy validate   # Rebuild graphs, check integrity
jigy layers                     # Show layer structure
```

### Bricks and Layers

**See:** `docs/jig/contextBricks.md` for full brick/layer reference.

**Bricks** partition functions into architectural units. Every function belongs to exactly ONE brick (no gaps, no overlaps).

**Layers** stratify bricks vertically. A brick at layer N may depend ONLY on layers 0..(N-1). Dependencies flow DOWN, never up. Violations are errors.

**FORBIDDEN bricks** are per-work-scope constraints defined in JIGPLAN. If a sub-agent touches a FORBIDDEN brick, this is an immediate escalation trigger.

**Validation:**
```bash
jigy validate        # Check all constraints
jigy layers          # Show layer structure
jigy layers suggest  # Compute layers from dependencies
```

### Project Structure

```
src/ase/           # Implementation code with @jig.implements
test/              # Test code with @jig.verifies
jig/               # Intent nodes (O/S)
jig/generated/     # Machine-generated graphs (NEVER edit)
docs/wip/          # SCOPE, JIGPLAN, PLAN documents
```

---

## Clean Break as Default

**AI agents tend to add compatibility shims. This workflow counters that bias.**

### Clean Break Means

- Old code paths are DELETED, not feature-flagged
- Old tests are DELETED and new tests written from scratch
- No backwards compatibility shims
- Unimplemented features raise `NotImplementedError`
- Deprecated O/S nodes deleted after validation

### Sub-Agent Constraint

Sub-agents MUST NOT add compatibility shims unless JIGPLAN explicitly includes a Backwards Compatibility Plan.

If sub-agent discovers need for backwards compat not in SCOPE → **STOP immediately**.

---

## Workflow Context

You operate in Phase 4 of the JIG Plan Orchestration Workflow:

```
SCOPE → JIGPLAN → PLAN → [You Are Here: Orchestrated Execution]
```

### Your Inputs

1. **PLAN document** (`docs/wip/PLAN-<feature>.md`)
   - Work units with success gates and escalation triggers
   - References JIGPLAN for architectural constraints

2. **JIGPLAN document** (`docs/wip/JIGPLAN-<feature>.md`)
   - O/S node reconciliation (what specs change)
   - Brick scope (FORBIDDEN bricks, layer constraints)
   - @jig decorator guidance
   - O/S nodes must be evergreen (behavior, not project tasks)

3. **SCOPE document** (`docs/wip/SCOPE-<feature>.md`)
   - Original problem description
   - Backwards compat requirements (if any)

---

## Your Process

### Before Starting

1. **Create branch** for this work
2. **Verify prerequisites**:
   - JIGPLAN is human-approved
   - PLAN document exists with all WUs defined
   - Current branch is clean
3. **Create JOURNAL file**
   - Create `docs/wip/JOURNAL-<feature>.md`
   - Add header with PLAN reference, start timestamp
   - See "Execution Journal" section below for format

### Per Work Unit

1. **Launch sub-agent**
   - Instruct: "Execute Work Unit N following taskDoWU.md"
   - Provide: Full PLAN document + taskDoWU.md
   - Include: JIGPLAN constraints (FORBIDDEN bricks, layer limits)
   - Sub-agent has fresh context window

2. **Receive sub-agent report**
   - Structured output (see format below)
   - Status, gates, issues, questions, recommendation

3. **Independently verify** critical gates
   ```bash
   pytest -xvs                      # All tests, stop on first failure
   jigy rebuild && jigy validate    # Rebuild and validate
   git diff --stat                  # What files changed
   ```
   - Compare your results vs sub-agent's report
   - Mismatch = escalation trigger

4. **Make decision**: CONTINUE | STOP | RETRY

5. **Update PLAN**
   - Mark WU checklist complete
   - Add sub-agent report to execution log

6. **Commit**
   ```bash
   git add src/ test/ jig/ docs/wip/PLAN-<feature>.md
   git commit -m "WU<N>: <title> (S-<specs>)

   Implements: S-001, S-002
   Alignment: verified

   See: docs/wip/PLAN-<feature>.md → WU<N>"
   ```

   **Commit Hash Recording:** Use "update-on-next-WU" pattern to avoid infinite loops:
   - Current WU completion record uses placeholder: `**Commit:** (this commit)`
   - When next WU starts, first action is update previous WU's hash
   - Hash update gets committed as part of the next WU's work

   This avoids the loop where updating the hash dirties the file, requiring another commit.

7. **Write journal entry**
   - Synthesize sub-agent report into journal entry
   - Include sub-agent's "Notable" observations
   - Add your own observations (timing, patterns, cross-WU context)
   - Tag with appropriate category (see "Execution Journal" section)

8. **If STOP**: Report to human (see format below)

### Validation WU (Special Handling)

The Validation WU verifies SCOPE is solved, not just specs implemented. It comes second-to-last (before Cleanup WU).

**Sequence:** Implementation WUs → **Validation WU** → Cleanup WU → Post-execution

**If Validation WU fails:**
1. Sub-agent investigates root cause (likely wiring/integration gap)
2. Sub-agent proposes fix
3. Fix is applied
4. **Regression test added** (upgrade to Integration Test if possible)
5. Validation re-run
6. Only proceed to Cleanup WU after Validation passes

**Quality hierarchy for Validation approach:**
- **BEST:** Integration Test added to test suite (evergreen)
- **BETTER:** Demo Script documented (repeatable)
- **OKAY:** Manual Checklist completed (not automated)

Validation failure is NOT immediate STOP - it's RETRY with investigation. Only STOP if fix requires FORBIDDEN brick changes or unclear what "correct" looks like.

### After All WUs Complete

**Note:** This happens after Cleanup WU (if any) has completed. Cleanup WU deletes legacy code; this step deletes deprecated O/S node files.

1. **Delete deprecated O/S nodes** (from JIGPLAN Clean Break Actions)
   - Delete spec files: `jig/specifications/S-*.md`
   - Delete outcome files: `jig/outcomes/O-*.md`

2. **Run final validation**
   ```bash
   jigy rebuild && jigy validate
   jigy layers
   pytest
   ```

3. **Generate JIG Summary** (see format below)

4. **Write journal synthesis**
   - Patterns observed across WUs
   - Friction summary (what slowed progress)
   - Process improvement suggestions
   - Wins worth repeating

5. **Update PLAN** with completion summary

6. **Final commit** (include JOURNAL file)

---

## Work Unit Requirements

Each WU in the PLAN must have:

### Required Sections

- **Goal**: Single, testable objective
- **Specs Addressed**: Which S-nodes this WU implements
- **Acceptance Criteria**: What defines success
- **Success Gates**: Pass/fail conditions you verify
- **Escalation Triggers**: When to stop and ask human
- **Implementation Notes**: Approach, files, patterns

### Success Gates (All Must Pass)

```markdown
**Success Gates** (all must pass):
- [ ] All tests pass: pytest test/path/test_module.py -v
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors
- [ ] Clean break maintained (no compat shims added)
```

### Escalation Triggers

```markdown
**Escalation Triggers** (stop and ask human if):
- Test failures persist after 2 retry attempts
- Implementation approach must deviate from JIGPLAN
- FORBIDDEN brick modification needed
- Layer constraint violation detected
- Ambiguity in spec acceptance criteria
- Discovered need for backwards compatibility (not in SCOPE)
```

---

## Sub-Agent Output Format

Sub-agents must return structured reports:

```markdown
**Status**: COMPLETE | BLOCKED | FAILED

**Gates**: 4/4 passed
- ✓ Tests: 18/18 passed
- ✓ jigy validate: PASS
- ✓ FORBIDDEN bricks: untouched
- ✓ Linting: no new errors

**Specs Implemented**: S-001, S-002
**Decorators Added**: 3 implements, 2 verifies

**Issues**:
- Minor: <non-blocking observations>
- Warning: <potential concerns>

**Decisions Made**:
- <implementation choices within WU scope>

**Questions for Human**:
- (none)

**Notable** (for journal):
- <friction encountered>
- <insights discovered>
- <near-misses or confusion>
- <process suggestions>

**Recommendation**: CONTINUE | STOP_AND_ASK

**Reflection**:
- <what worked well>
- <what was tricky>
```

---

## Decision Framework

### ✅ CONTINUE (to next WU) when:

All conditions met:
- Sub-agent status = COMPLETE
- All Success Gates passed (your independent verification)
- No Escalation Triggers fired
- No questions for human
- Changes match WU scope (no scope creep)
- Your verification matches sub-agent's report
- Clean break maintained (no compat shims added)

### ⛔ STOP (ask human) when:

Any condition met:
- Sub-agent status = BLOCKED or FAILED
- Any Success Gate failed after retry
- Any Escalation Trigger fired
- Sub-agent has questions for human
- Your independent verification contradicts sub-agent report
- Security/architectural decisions made by sub-agent
- Scope drift detected (changes beyond WU scope)
- 2 consecutive WU failures
- FORBIDDEN brick touched
- Layer violation detected
- Compatibility shim added (not in JIGPLAN)

### 🔄 RETRY (same WU, max 2 attempts) when:

Transient issues sub-agent can fix:
- Test failures due to timing/imports
- Missing @jig decorators
- Graph regeneration issues
- Simple linting errors

---

## When You Stop

Provide human with:

```markdown
## 🛑 STOPPED at Work Unit N: <Title>

**Reason**: <Specific gate failed or trigger fired>

**Sub-Agent Report**:
<paste full structured report>

**Your Independent Verification**:
```bash
$ pytest -xvs
<output>

$ jigy rebuild && jigy validate
<output>
```

**Mismatch**: <If your verification differs from sub-agent report>

**Recommendation**: <What human should look at>

**Plan State**:
- Completed: WU1-WU(N-1) ✅
- Stopped: WUN ⛔
- Remaining: WU(N+1)-WU(end)
```

---

## JIG Summary Report

After all WUs complete, generate JIG Summary as confirmation against JIGPLAN:

```markdown
## JIG Summary Report

### O/S Node Changes (vs JIGPLAN)

| Planned | Actual | Node | Notes |
|---------|--------|------|-------|
| REUSE | ✓ REUSED | O-001 | |
| UPDATE | ✓ UPDATED | S-002 | Added new criterion |
| DELETE | ✓ DELETED | S-003 | Removed after validation |
| CREATE | ✓ CREATED | S-004 | |

### Brick Changes (vs JIGPLAN)

| Planned | Actual | Brick | Notes |
|---------|--------|-------|-------|
| CREATE | ✓ CREATED | B-new-brick | Layer 1, 3 units |
| MODIFY | ✓ MODIFIED | B-existing | Added observer integration |
| FORBIDDEN | ✓ UNTOUCHED | B-foundation | |

### @jig Decorator Changes (vs JIGPLAN)

**Added:** N decorators (X implements, Y verifies)
**Removed:** N decorators
**Modified:** N decorators

| Planned | Actual | Type | Location | Spec |
|---------|--------|------|----------|------|
| ADD | ✓ ADDED | implements | F-module.func | S-004 |
| ADD | ✓ ADDED | verifies | T-test.test_func | S-004 |
| REMOVE | ✓ REMOVED | implements | F-old.func | S-003 |

### Validation Results

```bash
$ jigy rebuild && jigy validate
<output>

$ jigy layers
<output>
```

### Deviations from JIGPLAN

<List any differences between planned and actual, or "None">
```

---

## Execution Journal

You maintain a JOURNAL file throughout execution. This captures reasoning, friction, and insights - not just outcomes.

### Journal Location

`docs/wip/JOURNAL-<feature>.md`

### Entry Format

Each entry has a structured header (parseable) + freeform narrative:

```markdown
## Entry N | <timestamp> | <context>

```yaml
type: observation | decision | friction | insight | deviation | question | suggestion | outcome
wu: WU1 | null
spec: S-NNN | null
escalated: true | false
```

<Freeform narrative explaining the entry>
```

### Entry Categories

| Tag | Emoji | When to Use |
|-----|-------|-------------|
| observation | 🔬 | Something noticed about codebase, patterns, or state |
| decision | 🤔 | CONTINUE/STOP/RETRY choice and rationale |
| friction | ⚠️ | Something that slowed progress or caused confusion |
| insight | 💡 | Understanding gained that helps future work |
| deviation | 🔄 | Difference from plan and why |
| question | ❓ | Uncertainty requiring escalation to human |
| suggestion | 📝 | Process improvement idea |
| outcome | ✅ | WU result summary |

### Synthesizing Sub-Agent Reports

After each WU, create journal entry by:

1. **Extract from sub-agent report:**
   - Status and gate results → `outcome` entry
   - Issues/Warnings → `friction` entries if significant
   - Notable field → `observation`, `insight`, or `suggestion` entries
   - Questions → `question` entries

2. **Add orchestrator observations:**
   - Timing (was WU faster/slower than expected?)
   - Cross-WU patterns (similar friction across WUs?)
   - Decision rationale (why CONTINUE vs RETRY?)

### Journal Template

```markdown
# Execution Journal: <Feature Name>

**PLAN:** docs/wip/PLAN-<feature>.md
**Started:** <YYYY-MM-DD HH:MM>
**Status:** In Progress | Complete

---

## Entries

### Entry 1 | <timestamp> | Pre-Execution

```yaml
type: observation
wu: null
```

<Initial observations before WU1>

---

### Entry 2 | <timestamp> | WU1 Complete

```yaml
type: outcome
wu: WU1
spec: S-147
```

<WU1 result summary and observations>

---

(Additional entries...)

---

## Synthesis

### Patterns
- <Patterns observed across WUs>

### Friction Summary
- <Things that slowed progress>

### Suggestions
- <Process improvement ideas>

### Wins
- <What worked well, worth repeating>
```

---

## Risk Calibration

### Always Stop (🔴) for:
- Security concerns
- FORBIDDEN brick modifications
- Layer constraint violations
- Compatibility shims added (not in JIGPLAN)
- Architectural decisions beyond WU scope
- Data loss potential

### Propose and Continue (🟡) for:
- Test additions beyond plan (good thing)
- Minor implementation details (equivalent approach)
- Documentation improvements
- Refactoring within WU scope

### Auto-Continue (🟢) for:
- Clean execution, all gates passed
- No human-level decisions made
- Changes match plan exactly
- Clean break maintained

---

## Sub-Agent Constraints

Communicate these constraints when launching sub-agents:

1. **FORBIDDEN bricks**: List from JIGPLAN - immediate escalation if touched
2. **Layer constraints**: No upward dependencies
3. **Decorator guidance**: Follow JIGPLAN ADD/REMOVE/MODIFY tables
4. **O/S scope**: Only implement specs listed in JIGPLAN
5. **Clean break default**: NO compatibility shims unless JIGPLAN includes Backwards Compatibility Plan

---

## Success Criteria

Orchestration succeeds when:

- [ ] All WUs completed sequentially
- [ ] All Success Gates passed for each WU
- [ ] No Escalation Triggers fired without human review
- [ ] PLAN checklist fully marked
- [ ] Clean break actions executed (deprecated nodes deleted)
- [ ] Final jigy rebuild && jigy validate passes
- [ ] JIG Summary matches JIGPLAN expectations
- [ ] All tests passing
- [ ] Human aware of all architectural decisions made
- [ ] JOURNAL file complete with synthesis section

---

## Constraints

### DO NOT

- **Continue past failed quality gates** (always stop and ask)
- **Trust sub-agent reports without verification** (always verify independently)
- **Make architectural decisions autonomously** (always stop and ask)
- **Skip WUs** (must execute sequentially)
- **Allow compatibility shims** (unless in JIGPLAN)
- **Forget to delete deprecated O/S nodes** (clean break)

### MUST

- **Create branch** at start of execution
- **Create JOURNAL file** at start of execution
- **Verify independently** after each WU
- **Write journal entry** after each WU
- **Stop when uncertain** (over-escalate rather than under-escalate)
- **Maintain PLAN state** (update after each WU, commit)
- **Execute cleanup** after all WUs (delete deprecated nodes)
- **Generate JIG Summary** (confirmation against JIGPLAN)
- **Write journal synthesis** at end of execution

### PREFER

- **Conservative decisions** (stop and ask when in doubt)
- **Clear stop reports** (human needs to understand why)
- **Atomic WU execution** (complete one fully before next)
- **Immediate commits** (after each WU for context persistence)

---

## Version History

- **2.2.0** (2025-12-18): Added Validation WU special handling - verifies SCOPE is solved before Cleanup WU
- **2.1.0** (2025-12-18): Added Execution Journal - orchestrator maintains JOURNAL file with structured entries, synthesis
- **2.0.2** (2025-12-18): Added Bricks and Layers section with partition property, layer constraints, FORBIDDEN
- **2.0.1** (2025-12-18): Added evergreen O/S node note
- **2.0.0** (2025-12-18): Aligned with JIG Plan Orchestration Workflow
  - Added: JIGPLAN integration, clean break default, JIG Summary
  - Updated: Decision framework, escalation triggers
  - Removed: WU0 pattern (intent now in JIGPLAN phase)

- **1.0.0** (2025-12-15): Initial version for parent agent orchestration

---

**Next:** Launch first sub-agent with WU1 (sub-agent follows taskDoWU.md), verify output, decide continue/stop.
