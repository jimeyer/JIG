# Task: Execute Work Unit (taskDoWU)

**Version:** 3.0.3
**Date:** 2025-12-18
**Audience:** AI coding agents (sub-agents executing WUs)
**Status:** Active
**Related:** JigPlanOrchWorkflow.md, taskMakeJIGPLAN.md, taskMakePLAN.md, taskDoPLAN.md, contextBricks.md

## Objective

Execute a single Work Unit from a PLAN document using Test-Driven Development while maintaining JIG alignment. This task is for **sub-agents** launched by an orchestrator to implement individual WUs.

**You receive:** A PLAN document with a specific WU to execute.
**You produce:** Working code + tests + structured report.

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

Three relationships:
- **F → S** (implements): Function implements specification via `@jig.implements("S-001")`
- **T → S** (verifies): Test verifies specification via `@jig.verifies("S-001")`
- **T → F** (covers): Test executes function (automatic via coverage)

### JIG Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Specifications | `jig/specifications/S-{number}.md` | What we intend to build |
| Outcomes | `jig/outcomes/O-{number}.md` | Why we build it (optional) |
| Bricks | `jig/bricks.yaml` | Architectural partitions |
| Decorators | Source code | Links code/tests to specs |
| Generated graphs | `jig/generated/*.ndjson` | Machine-generated, NEVER edit |

**Note:** O/S nodes are EVERGREEN - they describe system behavior, not project tasks. Specs you implement should have testable acceptance criteria. If a spec reads like a refactoring task or implementation detail, escalate.

### Decorator Syntax

```python
# In implementation code
@jig.implements("S-001")
def my_function():
    pass

@jig.implements("S-001", "S-002")  # Multiple specs
def another_function():
    pass

# In test code
@jig.verifies("S-001")
def test_my_function():
    pass

@jig.verifies("S-001", "S-002")    # Multiple specs
def test_comprehensive():
    pass
```

### JIG Commands

```bash
jigy rebuild && jigy validate   # Rebuild graphs, check integrity
jigy layers                     # Show layer structure
```

### Bricks and Layers

**Bricks** partition functions into architectural units.
**Layers** stratify bricks vertically (layer N depends only on layers < N).

**See:** `docs/jig/contextBricks.md` for full brick/layer reference.

#### The Partition Property

Every function belongs to exactly ONE brick:
- **No gaps** - every function is assigned
- **No overlaps** - no function in multiple bricks
- **Class integrity** - all methods of a class must be in same brick

#### Brick Definition

```yaml
bricks:
  - id: B-core-utils
    name: Core Utilities
    layer: 0              # Foundation
    units:
      - M-utils.io           # All functions in module
      - C-utils.Parser       # All methods of class
      - F-utils.helpers.foo  # Single function
```

**Unit prefixes:**
- `M-{path}` — module (all functions)
- `C-{path}` — class (all methods)
- `F-{path}` — single function

#### Layer Constraint

**A brick at layer N may depend ONLY on layers 0..(N-1).**

Dependencies flow DOWN, never up. Violations are errors, not warnings.

#### FORBIDDEN Bricks (Per-JIGPLAN)

FORBIDDEN is a per-work-scope constraint, NOT a permanent brick property.

Each JIGPLAN defines which bricks are off-limits for that specific work. If you discover you need to modify a FORBIDDEN brick:
1. STOP immediately
2. Set Status = BLOCKED
3. Explain why in your report
4. This is an escalation trigger

---

## Clean Break Protocol

**Clean break is the DEFAULT. Do NOT add compatibility shims unless explicitly instructed.**

### Clean Break Means

- Old code paths are DELETED, not feature-flagged
- Old tests are DELETED and new tests written from scratch
- No backwards compatibility shims or adapters
- Unimplemented features raise `NotImplementedError` (fail loudly)

### Anti-Patterns to Avoid

```python
# BAD: Feature flag hell
if USE_NEW_PARSER:
    return new_parser.parse(content)
else:
    return old_parser.parse(content)  # "just in case"

# BAD: Commented old code
# def old_implementation():
#     ...  # keeping "just in case"

# BAD: Silent fallbacks
def get_value(key):
    try:
        return new_store.get(key)
    except:
        return old_store.get(key)  # silent fallback
```

```python
# GOOD: Clean break with clear errors
def parse(content: str) -> ParseResult:
    result = new_parser.parse(content)
    if has_legacy_markers(content):
        raise NotImplementedError(
            "Legacy markers no longer supported. Use new format."
        )
    return result

# GOOD: Fail loudly for unimplemented features
def advanced_feature():
    raise NotImplementedError(
        "Advanced feature requires X subsystem (not yet implemented)"
    )
```

### If You Discover Need for Backwards Compatibility

**STOP immediately.** Do not implement compatibility shims.

Report to orchestrator:
- What needs backwards compat
- Who/what depends on old behavior
- Why you discovered this mid-implementation

This is an escalation trigger. Wait for human decision.

---

## Your Inputs

When executing a WU, you receive:

1. **PLAN Document**: Contains your WU with:
   - Goal
   - Specs Addressed
   - Acceptance Criteria
   - Success Gates
   - Escalation Triggers
   - Implementation Notes

2. **Constraints from JIGPLAN**:
   - FORBIDDEN bricks (do not modify)
   - Layer constraints
   - Decorator guidance (what to ADD/REMOVE)

3. **Specific instruction**: "Execute Work Unit N"

---

## TDD Process

### Step 1: Understand the WU

Read the WU carefully:
- What specification(s) am I implementing?
- What are the acceptance criteria?
- What files will I create/modify?
- What are the FORBIDDEN bricks?

### Step 2: Write Tests First (RED)

Write tests that verify the specification's acceptance criteria:

```python
@jig.verifies("S-001")
def test_token_expiration():
    """Verify tokens expire after 15 minutes of inactivity."""
    token = create_token(user="test")
    token.last_activity = datetime.now() - timedelta(minutes=15, seconds=1)
    assert is_expired(token)
```

Run tests: **Expected to FAIL** (red) because implementation doesn't exist.

```bash
pytest test/path/test_module.py -v
```

### Step 3: Implement Code (GREEN)

Write minimal code to make tests pass:

```python
@jig.implements("S-001")
def is_expired(token: Token) -> bool:
    """Check if token has expired based on inactivity."""
    inactive_duration = datetime.now() - token.last_activity
    return inactive_duration > timedelta(minutes=15)
```

Run tests: **Expected to PASS** (green).

```bash
pytest test/path/test_module.py -v
```

### Step 4: Refactor (If Needed)

Improve code quality while keeping tests green. Do not change behavior.

### Step 5: Verify JIG Alignment

```bash
jigy rebuild && jigy validate
```

Expected: No errors. Specs show as implemented and verified.

### Step 6: Verify Success Gates

Check all success gates from the WU:

```bash
# All tests pass
pytest test/path/test_module.py -v

# JIG validation passes
jigy rebuild && jigy validate

# No modifications to FORBIDDEN bricks
git diff --name-only | grep -E "forbidden/path"  # Should be empty

# No new linting/type errors
# (run your linter)
```

### Step 7: Return Structured Report

Return report to orchestrator (see format below).

---

## Structured Report Format

After completing (or failing) a WU, return this report:

```markdown
**Status**: COMPLETE | BLOCKED | FAILED

**Gates**: X/Y passed
- ✓ Tests: N/N passed
- ✓ jigy validate: PASS
- ✓ FORBIDDEN bricks: untouched
- ✓ Linting: no new errors

**Specs Implemented**: S-001, S-002
**Decorators Added**: X implements, Y verifies

**Files Changed**:
- src/path/module.py (new)
- test/path/test_module.py (new)

**Issues**:
- Minor: <non-blocking observations>
- Warning: <potential concerns>

**Decisions Made**:
- <implementation choices within WU scope>

**Questions for Human**:
- <questions that need human input>
- (none if no questions)

**Notable** (for orchestrator awareness):
- <friction encountered during this WU>
- <insights discovered>
- <near-misses or confusion points>
- <process suggestions>

**Recommendation**: CONTINUE | STOP_AND_ASK

**Reflection**:
- <what worked well>
- <what was tricky>
- <edge cases discovered>
```

### Notable Field Guidance

The "Notable" field captures anything interesting that doesn't fit other categories. The orchestrator uses this to maintain the execution journal.

**Examples:**
- "Almost modified FORBIDDEN brick before re-reading constraints"
- "Spec S-147 wording was confusing - took 3 reads to understand"
- "Found existing pattern in events.py that could be reused"
- "This spec would benefit from example code in acceptance criteria"
- "Test setup took longer than implementation due to fixture complexity"

---

## Constraints You Must Respect

### FORBIDDEN Bricks

The PLAN will specify FORBIDDEN bricks from JIGPLAN. **Do not modify any code in FORBIDDEN bricks.**

If you need to modify a FORBIDDEN brick:
1. STOP immediately
2. Set Status = BLOCKED
3. Explain why in your report
4. Recommend escalation

### Layer Constraints

Code at layer N must not depend on code at layer N+1 or higher.

If you detect a layer violation:
1. STOP immediately
2. Set Status = BLOCKED
3. Explain the violation in your report

### Decorator Guidance

The PLAN references JIGPLAN decorator guidance:
- **ADD**: Add these decorators to your code
- **REMOVE**: Remove these decorators (if modifying existing code)
- **MODIFY**: Update spec references in decorators

### Clean Break

Do NOT add compatibility shims unless the PLAN explicitly includes a Backwards Compatibility Plan.

---

## Escalation Triggers

Set Status = BLOCKED and recommend STOP_AND_ASK if:

- Test failures persist after 2 attempts
- Implementation approach must deviate from PLAN
- FORBIDDEN brick modification needed
- Layer constraint violation detected
- Ambiguity in spec acceptance criteria
- Discovered need for backwards compatibility
- Security concerns arise
- You're unsure about an architectural decision
- Spec appears to be a refactoring task or implementation detail (not evergreen behavior)

**It is better to escalate than to make wrong assumptions.**

---

## Success Criteria

Your WU is complete when:

- [ ] All acceptance criteria from WU are met
- [ ] Tests written with `@jig.verifies` decorators
- [ ] Code written with `@jig.implements` decorators
- [ ] All tests passing
- [ ] `jigy rebuild && jigy validate` passes
- [ ] No FORBIDDEN bricks modified
- [ ] No layer violations
- [ ] Clean break maintained (no compat shims)
- [ ] Structured report returned

---

## Common Pitfalls

### Pitfall 1: Writing Code Before Tests

**Wrong:**
```bash
# Jump straight to implementation
vim src/module.py
```

**Right:**
```bash
# Write tests first (TDD)
vim test/test_module.py   # Write failing tests
pytest                    # Confirm they fail
vim src/module.py         # Now implement
pytest                    # Confirm they pass
```

### Pitfall 2: Skipping @jig Decorators

**Wrong:**
```python
def is_expired(token: Token) -> bool:
    # No decorator - alignment cannot be measured!
    return datetime.now() - token.last_activity > timedelta(minutes=15)
```

**Right:**
```python
@jig.implements("S-001")
def is_expired(token: Token) -> bool:
    # Decorator makes alignment measurable
    return datetime.now() - token.last_activity > timedelta(minutes=15)
```

### Pitfall 3: Adding Compatibility Shims

**Wrong:**
```python
def process(data):
    if hasattr(data, 'legacy_field'):
        return legacy_process(data)  # Compat shim
    return new_process(data)
```

**Right:**
```python
def process(data):
    if hasattr(data, 'legacy_field'):
        raise NotImplementedError(
            "Legacy data format no longer supported"
        )
    return new_process(data)
```

### Pitfall 4: Modifying FORBIDDEN Bricks

**Wrong:**
```bash
# FORBIDDEN: B-core-utils contains M-utils.io
vim src/utils/io.py  # Modifying forbidden brick!
```

**Right:**
```bash
# Check FORBIDDEN list before editing
# If you need to modify a FORBIDDEN brick, STOP and escalate
```

### Pitfall 5: Forgetting to Regenerate Graphs

**Wrong:**
```bash
vim src/module.py     # Add @jig.implements
# Forget to rebuild
```

**Right:**
```bash
vim src/module.py             # Add @jig.implements
jigy rebuild && jigy validate # Rebuild and validate
```

---

## Quick Reference

### TDD Cycle

```
1. Write test with @jig.verifies → Run (RED)
2. Write code with @jig.implements → Run (GREEN)
3. Refactor → Run (still GREEN)
4. jigy rebuild && jigy validate → Confirm alignment
5. Return report
```

### Essential Commands

```bash
# Run tests
pytest test/path/test_module.py -v

# Rebuild and validate JIG
jigy rebuild && jigy validate

# Check layer structure
jigy layers

# See what files changed
git diff --name-only
git diff --stat
```

### Report Statuses

| Status | Meaning |
|--------|---------|
| COMPLETE | All gates passed, WU done |
| BLOCKED | Cannot proceed, need human input |
| FAILED | Attempted but gates failed |

### Recommendations

| Recommendation | When to use |
|----------------|-------------|
| CONTINUE | Status=COMPLETE, no questions |
| STOP_AND_ASK | Any escalation trigger, or questions for human |

---

## Version History

- **3.0.3** (2025-12-18): Added "Notable" field to report format for orchestrator journal
- **3.0.2** (2025-12-18): Expanded Bricks and Layers section with partition property, unit prefixes, FORBIDDEN per-scope constraint
- **3.0.1** (2025-12-18): Added evergreen O/S node awareness and escalation trigger
- **3.0.0** (2025-12-18): Aligned with JIG Plan Orchestration Workflow
  - Refocused: Sub-agent execution of individual WUs
  - Removed: WU0 pattern (intent now in JIGPLAN phase)
  - Added: Clean break protocol, structured report format
  - Added: FORBIDDEN bricks, layer constraints
  - Updated: TDD process, escalation triggers

- **2.0.0** (2025-11-26): Aligned with JIG v8

- **1.0.0** (2024): Original version

---

**Next:** Execute your assigned WU using TDD. Return structured report to orchestrator (taskDoPLAN.md).
