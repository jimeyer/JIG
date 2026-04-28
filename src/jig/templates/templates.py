"""Template constants for JIG project scaffolding.

These templates are used by `jigy init` to create new JIG projects.
Templates are plain string constants, not Jinja2 templates.
"""

JIG_TOML_TEMPLATE = """\
name = "{name}"

[integration]
include_dig = true

[scan]
# Directories to exclude from @jig.implements / @jig.verifies scanning
ignore = [
    ".venv/",
    "__pycache__/",
    "node_modules/",
    "dist/",
    "build/",
]
"""

CHARTER_MD_TEMPLATE = """\
---
id: Charter
type: charter
goals: [G-1]
---
# Charter

## G-1: [Define your first goal]
"""

BRICKS_YAML_TEMPLATE = """\
bricks: []
"""

SKILL_MD_TEMPLATE = """\
---
name: jig
description: Work with JIG intent graphs. Invoke with /jig.
---

# jig

Manage alignment between specifications, code, and tests.

## Bootstrap

Read `contextJIG.md` (in this skill folder) for universal JIG knowledge:
- G-A-O-S-C-T hierarchy (goals -> outcomes -> specs -> code -> tests)
- Frontmatter schemas for each artifact type
- Decorator syntax (`@jig.implements`, `@jig.verifies`)
- Validation rules

Read project-specific files:
- `jig/bricks.yaml` - brick definitions, layer/tower structure
- `jig/specifications/*.md` - existing specs as examples
- `jig/outcomes/*.md` - existing outcomes

## CLI Commands

| Command | Purpose |
|---------|---------|
| `jigy context` | Project overview |
| `jigy context <id>` | Understand any artifact (S-###, O-###, file path) |
| `jigy validate -j` | Diagnose issues, get fix templates |
| `jigy mend --auto` | Auto-fix safe issues |
| `jigy mend --apply fixes.json` | Apply explicit fixes |

## Workflows

**Understand something:**
```bash
jigy context S-042        # spec and its neighborhood
jigy context src/foo.py   # file's specs and tests
```

**Fix graph issues (validate/mend contract):**
```bash
jigy validate -j > errors.json   # get errors with fix templates
# Fill in ??? values in the fix templates
jigy mend --apply fixes.json     # apply fixes
```

**Create artifacts:**
Read `contextJIG.md` for schemas. Use standard file operations.

**Add decorators:**
```python
@jig.implements("S-042")
def my_function(): ...

@jig.verifies("S-042")
def test_my_function(): ...
```
"""

CONTEXT_JIG_MD_TEMPLATE = """\
# JIG Context for AI Agents

JIG measures alignment between **intent** (specifications), **implementation** (code), and **verification** (tests) through a seven-level hierarchy.

---

## The G-A-O-S-C-T Pyramid

```
                      CHARTER
                     (defines G-#)
                    /            \\
                   /              \\
          ARCHITECTURE          OUTCOMES
               A-###               O-###
              goals               goals
                |                   |
                | specifications    |
                |    +--------------+
                v    v
            SPECIFICATIONS
                 S-###
           (outcomes, architecture)
               /      \\
              /        \\
         verifies   implements
            /            \\
           /              \\
       TESTS              CODE
        T-###              C-###
```

Every function should trace upward through this hierarchy to the Charter. Breaks indicate misalignment.

---

## ID Formats

| Type | Format | Example |
|------|--------|---------|
| Charter | `Charter` | `Charter` (singleton) |
| Goal | `G-{number}` | G-1, G-2, G-3 |
| Architecture | `A-{number}` | A-010, A-030 |
| Outcome | `O-{number}` | O-101, O-107 |
| Specification | `S-{number}` | S-001, S-042 |
| Brick | `B-{kebab-case}` | B-auth-session |
| Code | `C-{path}` | C-jig.cli.main |
| Module | `M-{path}` | M-auth.session |
| Class | `C-{path}` | C-auth.tokens.TokenValidator |
| Test | `T-{path}` | T-test_auth.test_token_expiration |

---

## Seven Artifact Types

| # | Artifact | Location | Authored By |
|---|----------|----------|-------------|
| 1 | Charter | `jig/Charter.md` | Human |
| 2 | Architecture | `jig/architecture/A-###_{Title}.md` | Human |
| 3 | Outcome | `jig/outcomes/O-###_{Title}.md` | Human |
| 4 | Specification | `jig/specifications/S-###_{Title}.md` | Human |
| 5 | Brick definitions | `jig/bricks.yaml` | Human |
| 6 | @jig annotations | Source code | Human |
| 7 | Graph files | `jig/generated/*.ndjson` | Machine (NEVER EDIT) |

### Filename Format

Files must match: `{TYPE}-{NNN}_{Title_In_Snake_Case}.md`

- Title derived from frontmatter `title` field
- Spaces become underscores, hyphens preserved
- Example: title `"Multi-Device State"` -> `O-152_Multi-Device_State.md`

### Frontmatter Schema

Frontmatter contains **graph edges** (identity + relationships). Operational metadata goes in body.

**Charter:**
```yaml
---
id: Charter
type: charter
goals: [G-1, G-2, G-3]
---
```

**Architecture:**
```yaml
---
id: A-030
type: architecture
title: ANK Architecture
goals: [G-1, G-3]
specifications: [S-001, S-004, S-006]
---
```

**Outcome:**
```yaml
---
id: O-101
type: outcome
title: Distributed State Convergence
goals: [G-2, G-3]
architecture: [A-022, A-030]
specifications: [S-001, S-002]
---
```

**Specification:**
```yaml
---
id: S-001
type: specification
title: CID Properties
outcomes: [O-101, O-103]
architecture: [A-030, A-022]
---
```

**Not in frontmatter** (goes in body if needed): `status`, `related`, `brick`, `consolidates`

### Decorators (in source code)

```python
@jig.implements("S-001")
def authenticate(user: str, password: str) -> Token: ...

@jig.verifies("S-001")
def test_token_expiration(): ...
```

---

## Bricks: Layer x Tower Model

### Partition Property
- Every function in exactly ONE brick (no gaps, no overlaps)
- All methods of a class in SAME brick

### Brick Definition

```yaml
bricks:
  - id: B-cli
    name: CLI Commands
    layer: 1
    tower: server        # Optional
    units:
      - M-jig.cli.main   # All functions in module
      - C-jig.Parser     # All methods of class
```

### Layers (Horizontal Stratification)

Brick at layer N depends ONLY on layers < N. Violations are errors.

```
Layer 0: Foundation (external libs only)
Layer 1: Core logic (depends on Layer 0)
Layer 2: Interface (depends on Layers 0-1)
```

### Towers (Vertical Partitioning)

Cross-tower dependencies are **FORBIDDEN**. Towers communicate through shared specifications, not code imports.

```
          |  server  |  harness  |  device  |
Layer 2   |   B-s2   |   B-h2    |          |
Layer 1   |   B-s1   |   B-h1    |   B-d1   |
Layer 0   |   B-s0   |   B-h0    |   B-d0   |
```

Single-tower projects omit `tower` field from all bricks.

### FORBIDDEN Bricks (Per-JIGPLAN)

Scope constraint for specific work. If sub-agent needs FORBIDDEN brick: STOP, escalate, wait for scope revision.

---

## Writing Evergreen Artifacts

O and S nodes remain true FOREVER, not just until PR merges.

### Outcomes = Business Value

- [ ] WHY the system behaves this way
- [ ] `goals` links to Charter goals
- [ ] Remains true after project completes
- [ ] NOT: project goals, refactoring tasks

X BAD: "Achieve 90% test coverage"
V GOOD: "Critical behaviors verified to prevent production regressions"

### Specifications = Behavioral Requirements

- [ ] Observable behavior with acceptance criteria
- [ ] Can use `@jig.implements` on code
- [ ] Can use `@jig.verifies` on tests
- [ ] NOT: file paths, implementation details

X BAD: "Relocate file X to location Y"
V GOOD: "EraLamportClock state persists across restarts"

**Test:** Can you write a decorator for it? If no, rewrite.

### Specification Body Structure

Specs are lean behavioral contracts. Architecture docs own structure/relationships; specs own invariants.

**H1 Title:** Must exactly match frontmatter `title` field. Do NOT include ID prefix.

| Section | Required | Content |
|---------|----------|---------|
| **Statement** | Yes | 1-3 sentences. What must be true. No "how." |
| **Invariants** | Yes | Bullet list of always-true conditions. Each falsifiable. |
| **Verification** | Yes | Acceptance criteria. What would a test assert? |
| **Boundaries** | No | What's explicitly out of scope. |

**Exclude:** Rationale (-> Outcome), architecture discussion (-> arch doc link), implementation hints, history.

**Example:**
```markdown
# Staleness Tracking

Heartbeat absence triggers staleness state within bounded time.

## Invariants
- Device marked stale after 2x heartbeat interval without contact
- Staleness merge uses min-timestamp (earliest evidence wins)
- Stale->fresh transition requires new heartbeat, not timeout

## Verification
- [ ] Device receiving heartbeat at t0, none by t0+2T -> stale
- [ ] Two hosts disagree on staleness -> merge produces stale
- [ ] Stale device sends heartbeat -> immediately fresh
```

Target: ~50 lines max. Architecture link in frontmatter handles the rest.

---

## CLI Commands

```bash
jigy validate       # Check references, partition, layers
jigy impl rebuild   # Generate implementation graph
jigy intent rebuild # Generate intent graph
jigy layers         # Show layer structure
jigy rebuild        # Runs validate, rebuild, layers
```

---

## Validation Rules

### Identity & References
- All IDs unique within type, match required patterns
- `@jig.implements` / `@jig.verifies` reference existing specs
- `goals` references goals defined in Charter
- `specifications` references existing specs
- `outcomes` / `architecture` reference existing outcomes/arch docs

### File Format
- Filename matches `{TYPE}-{NNN}_{Title_Snake_Case}.md`
- H1 exactly matches frontmatter `title` (no ID prefix)

### Graph Integrity
- **Bidirectional O<->S**: If spec lists outcome in `outcomes`, that outcome must list spec in `specifications`
- **Outcome completeness**: Every outcome must have non-empty `specifications` array
- **Spec coverage**: Every spec must appear in at least one outcome's `specifications` array

### Brick Constraints
- Every function in exactly one brick
- Brick at layer N depends only on layers < N
- Cross-tower dependencies forbidden (if towers used)
- No circular dependencies

---

## For AI Agents

1. **Read before writing** - Query graphs to understand what exists
2. **Link your work** - Use `@jig.implements()` and `@jig.verifies()`
3. **Validate continuously** - Run `jigy validate` before committing
4. **Understand intent first** - Read S-### and O-### before modifying code
5. **Respect architecture** - Check layer and tower constraints
6. **Trace to goals** - Know which G-### your work supports

---

## Quick Reference

| Task | Action |
|------|--------|
| Add requirement | Create `jig/specifications/S-{next}.md` |
| Group specs into value | Create `jig/outcomes/O-{next}.md` |
| Mark function implements | `@jig.implements("S-001")` |
| Mark test verifies | `@jig.verifies("S-001")` |
| Assign to brick | Add to `units` in `bricks.yaml` |
| Check validity | `jigy rebuild` |
"""

JIG_CONTEXT_SKILL_MD_TEMPLATE = """\
---
name: jig-context
description: Full JIG schema reference. Use when creating or editing O/S/A nodes, writing bricks.yaml, interpreting jigy validate errors, or checking frontmatter schemas and ID formats.
user-invocable: false
---

See `contextJIG.md` in this skill folder for full JIG schema reference.
"""

JIGPLAN_SKILL_MD_TEMPLATE = """\
---
name: jigplan
description: Create a JIGPLAN architectural plan for a feature. Use when user asks to plan a new feature, create a JIGPLAN, or start the SCOPE→JIGPLAN phase.
disable-model-invocation: true
argument-hint: [scope-path]
---

Read `instructions.md` and `contextJIG.md` in this skill folder, then follow the instructions to create a JIGPLAN document for the given scope.
"""

JIGPLAN_INSTRUCTIONS_TEMPLATE = """\
# Task: Create JIGPLAN Document (taskMakeJIGPLAN)

**Version:** 2.0.0
**Date:** 2026-01-08
**Audience:** AI coding agents
**Status:** Active
**Related:** JigPlanOrchWorkflow.md, taskMakePLAN.md, taskDoPLAN.md, taskDoWU.md, contextBricks.md

## Objective

Create a JIGPLAN document that defines the complete architectural plan for a feature before any implementation begins. The JIGPLAN specifies what O/S nodes, bricks, and @jig decorators will be created, updated, or deleted.

**JIGPLAN is the architectural gate between SCOPE and implementation.**

---

## Inputs

Before creating a JIGPLAN, you need:

1. **SCOPE Document**: Problem description (human-authored)
   - Located in `docs/wip/SCOPE-<feature>.md`
   - May request backwards compatibility (if so, plan for it)

2. **Existing JIG Artifacts**: Review before planning
   - `jig/specifications/*.md` - existing specs (prefer REUSE over CREATE)
   - `jig/outcomes/*.md` - existing outcomes
   - `jig/bricks.yaml` - current brick structure

3. **Codebase Analysis**: Understand what exists
   - Relevant source code
   - Existing @jig decorators
   - Current layer structure

4. **Charter Decision Philosophy**: Read before making architectural choices
   - `jig/Charter.md` - Section "Decision Philosophy"
   - Decision heuristics for resolving tradeoffs
   - Anti-goals to avoid optimizing for

---

## Key Concepts

### The S-F-T Triangle

JIG measures alignment between **intent** (specifications), **implementation** (functions), and **verification** (tests):

```
         S (Specification)
        / \\
       /   \\
implements  verifies
     /       \\
    F ————————→ T
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

### ID Formats

| Type | Format | Example |
|------|--------|---------|
| Specification | `S-{number}` | S-001, S-042 |
| Outcome | `O-{number}` | O-001 |
| Brick | `B-{kebab-case}` | B-auth-session |
| Function | `F-{path}` | F-auth.session.authenticate |
| Module | `M-{path}` | M-auth.session |
| Class | `C-{path}` | C-auth.tokens.TokenValidator |
| Test | `T-{path}` | T-test_auth.test_token_expiration |

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

**Brick ID format:** `B-{kebab-case-name}` — semantic naming (NOT numeric IDs)

#### Derived Properties (Not Stored)

Brick properties are computed, not declared:

| Property | Derived From |
|----------|--------------|
| Specs assigned | Functions' `@jig.implements` decorators |
| Dependencies | Call graph (F in brick A calls F in brick B) |
| Public API | Functions called from outside the brick |

**Single source of truth:** `bricks.yaml` defines membership only. Everything else is computed.

#### Layer Constraint

**A brick at layer N may depend ONLY on layers 0..(N-1).**

Dependencies flow DOWN, never up. Violations are errors, not warnings.

**Layer 0 special rules:**
- MAY depend on external libraries and other layer 0 bricks
- MUST NOT depend on any brick at layer 1+
- Cycles rejected even within layer 0

#### When to Create vs Extend Bricks

**Create new brick when:**
- Functions form cohesive unit with distinct responsibility
- Clear boundary exists (different concern, different rate of change)
- Dependency isolation is valuable (testing, deployment)

**Extend existing brick when:**
- Functions naturally belong to existing boundary
- No clear separation of concerns
- Would create artificial split

#### Layer Assignment

Layer = max(dependency layers) + 1

**Decision process:**
1. List brick's dependencies (what does it call?)
2. Find max layer among dependencies
3. Assign layer = max + 1
4. If no dependencies, layer = 0

Or: Use `jigy layers suggest` to compute from actual dependencies.

#### FORBIDDEN Bricks (Per-JIGPLAN)

FORBIDDEN is a per-work-scope constraint, NOT a permanent brick property.

Each JIGPLAN defines which bricks are off-limits for that specific work:
- **Scope discipline** - Prevents "while I'm here, let me also fix..."
- **Sub-agent guardrails** - Clear boundaries for automated execution
- **Change isolation** - Limits blast radius of modifications

Any brick can be FORBIDDEN regardless of layer. The constraint is "don't touch during THIS work."

---

## Clean Break as Default

**AI agents tend to add compatibility shims by default. This workflow counters that bias.**

### Clean Break Means

- Old code paths are DELETED, not feature-flagged
- Old tests are DELETED and new tests written from scratch
- No backwards compatibility shims or adapters
- Unimplemented features raise `NotImplementedError` (fail loudly)
- Deprecated O/S nodes are deleted after validation

### When Backwards Compatibility is Needed

Backwards compat must be **explicitly requested in SCOPE**. Valid reasons:
- Public API with external consumers
- Critical path code requiring rollback capability
- Multi-team coordination constraints
- Regulatory/compliance requirements

**If SCOPE does not request backwards compat, clean break is assumed.**

---

## Process

### Step 1: Analyze SCOPE

Read the SCOPE document carefully. Extract:

1. **Behavioral requirements** → Map to specifications
2. **Business value statements** → Map to outcomes
3. **Architectural scope** → Which bricks affected
4. **Backwards compat requests** → Plan if present (rare)

**If SCOPE is unclear**, ask clarifying questions rather than guess.

### Step 2: Audit Existing O/S Nodes

Before creating new nodes, search existing specs and outcomes:

```bash
# Find specs that might already cover this behavior
grep -r "token" jig/specifications/
grep -r "authentication" jig/specifications/

# Check outcomes for related business value
grep -r "security" jig/outcomes/
```

**Strong preference for REUSE and UPDATE over CREATE.**

Questions to ask:
- Does an existing spec already cover this behavior?
- Can I update an existing spec instead of creating new?
- Is there an existing outcome this work supports?
- Are any existing specs now obsolete (DELETE)?

### Step 3: Audit Existing Bricks

Analyze brick structure:

```bash
# View current layer structure
jigy layers

# Check which bricks contain related code
grep -r "related_module" jig/bricks.yaml
```

Questions to ask:
- Which bricks will this work touch?
- Do we need a new brick, or extend existing?
- What layer should new code be at?
- Are there FORBIDDEN bricks (foundation that shouldn't change)?

### Step 4: Plan @jig Decorator Changes

For each spec being implemented:
- What functions will implement it? (`@jig.implements`)
- What tests will verify it? (`@jig.verifies`)
- What existing decorators become orphaned (spec deleted)?

### Step 5: Write O/S Node Files

**CREATE nodes:** Write actual spec/outcome files to disk.

**UPDATE nodes:** Edit existing files in place.

**DELETE nodes:** Do NOT delete yet - deletion happens after implementation validates.

### Step 6: Update bricks.yaml (If Needed)

If creating new bricks or modifying existing, update `jig/bricks.yaml`.

### Step 7: Validate

Run JIG validation to ensure no broken references:

```bash
jigy rebuild && jigy validate
jigy layers  # Verify layer structure
```

**All validation must pass before proceeding.**

### Step 8: Write JIGPLAN Document

Create `docs/wip/JIGPLAN-<feature>.md` using the template below.

The JIGPLAN references the O/S nodes you created - it does NOT embed their full content.

### Step 9: Fresh Agent Review (Required)

**Purpose:** Verify the JIGPLAN is complete and internally consistent before human approval.

**Why a fresh agent:** The creating agent has JIGPLAN context in working memory. A fresh agent tests whether the document is self-contained.

Spawn a fresh agent to review the JIGPLAN for:
1. Spec Audit Completeness
2. Anti-Pattern Detection
3. Brick/Layer Validation
4. Decorator Completeness
5. Internal Consistency

Resolve MECHANICAL issues autonomously. Apply Charter philosophy to JUDGMENT issues. Escalate only when heuristics conflict or situation is truly novel.

---

## JIGPLAN Template

```markdown
# JIGPLAN: <Feature Name>

**SCOPE:** docs/wip/SCOPE-<feature>.md
**Date:** <YYYY-MM-DD>
**Status:** Draft | Approved
**Author:** <agent/human>

---

## Summary

<2-3 sentences describing what this JIGPLAN covers.>

---

## O/S Node Reconciliation

### Outcomes

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | O-001 | <title> | <why reusing> |
| CREATE | O-004 | <title> | <why new> |

### Specifications

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | S-001 | <title> | <why reusing> |
| CREATE | S-004 | <title> | <why new> |

---

## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| FORBIDDEN | B-foundation | 0 | <why must not touch> |

---

## @jig Decorator Changes

### Decorators to ADD

| Type | Location | Spec |
|------|----------|------|
| implements | F-module.function_name | S-004 |
| verifies | T-test_module.test_function | S-004 |

---

## Clean Break Actions

- [ ] Old code paths will be DELETED, not feature-flagged
- [ ] No backwards compatibility shims

---

## Approval Checklist

- [ ] All existing specs reviewed for REUSE opportunities
- [ ] New specs follow evergreen guidelines
- [ ] Brick layer constraints validated
- [ ] FORBIDDEN bricks identified
- [ ] Fresh Agent Review completed

---

**Awaiting human approval before proceeding to PLAN.**
```

---

## Constraints

### MUST
- Read Charter Decision Philosophy before architectural choices
- Write O/S node files to disk
- Run jigy validate before submitting
- Audit existing O/S nodes first
- Identify FORBIDDEN bricks
- Complete Fresh Agent Review

### PREFER
- REUSE over UPDATE over CREATE
- DELETE obsolete specs
- Conservative FORBIDDEN list

---

**Next:** After JIGPLAN is approved, create PLAN document using /plan skill.
"""

PLAN_SKILL_MD_TEMPLATE = """\
---
name: plan
description: Break an approved JIGPLAN into sequenced Work Units. Use when user asks to create a PLAN or start the JIGPLAN→PLAN phase.
disable-model-invocation: true
argument-hint: [jigplan-path]
---

Read `instructions.md` and `contextJIG.md` in this skill folder, then follow the instructions to create a PLAN document for the given JIGPLAN.
"""

PLAN_INSTRUCTIONS_TEMPLATE = """\
# Task: Create PLAN Document (taskMakePLAN)

**Version:** 2.0.0
**Date:** 2026-01-08
**Audience:** AI coding agents
**Status:** Active
**Related:** taskMakeJIGPLAN.md, taskDoPLAN.md, taskDoWU.md

## Objective

Create a PLAN document that breaks an approved JIGPLAN into sequenced, executable Work Units. The PLAN is a pure execution plan - all architectural decisions were made in JIGPLAN.

**You receive:** SCOPE + approved JIGPLAN
**You produce:** PLAN document with Work Units ready for orchestrated execution

---

## Inputs

1. **SCOPE Document** (`docs/wip/SCOPE-<feature>.md`)
2. **Approved JIGPLAN** (`docs/wip/JIGPLAN-<feature>.md`)
   - O/S node reconciliation
   - Brick scope (FORBIDDEN bricks, layer constraints)
   - @jig decorator changes
   - Clean break actions

**Critical:** JIGPLAN must be human-approved before creating PLAN.

---

## Process

### Step 1: Extract Constraints from JIGPLAN

Pull FORBIDDEN bricks and layer constraints into PLAN header.

### Step 2: Identify Work Unit Boundaries

Group work into WUs based on cohesion, dependencies, and size (target 60-90 min per WU).

### Step 3: Sequence Work Units

Order by dependency: Foundation → Core → Integration → Validation → Cleanup.

### Step 4: Write Each Work Unit

Each WU needs: Goal, Specs Addressed, Acceptance Criteria, Success Gates, Escalation Triggers, Implementation Notes.

### Step 5: Create Checklist

Summary at top of PLAN.

### Step 6: Add Execution Log and Completion Sections

Create structure to be filled during/after execution.

### Step 7: Fresh Agent Review (Required)

Spawn fresh agent to identify ambiguities. Resolve (A) issues via codebase exploration. Escalate (B) issues to human.

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

**Clean Break:**
- <what to delete>

---

## Work Unit Checklist

- [ ] WU1: <title> — tests ☐ / code ☐
- [ ] WU(N-1): Validation — SCOPE verified ☐
- [ ] WUN: Cleanup — legacy deleted ☐

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
- FORBIDDEN brick modification needed
- Layer constraint violation detected

**Implementation Notes**:
- Files: <paths>
- Decorators: <what to add>

---

## Execution Log

(Filled in by orchestrator)

---

## Completion Summary

**Scope Delivered:**
- <to be filled>

**Clean Break Actions:**
- [ ] Deleted deprecated O/S nodes
- [ ] Final jigy rebuild && jigy validate passed
```

---

## Constraints

### MUST
- Include Validation WU (verifies SCOPE is solved)
- Reference JIGPLAN constraints
- Sequence by dependency
- Complete Fresh Agent Review

### PREFER
- One spec per WU
- Conservative sizing

---

**Next:** After PLAN is created and Fresh Agent Review completed, execute with /do-plan skill.
"""

DO_PLAN_SKILL_MD_TEMPLATE = """\
---
name: do-plan
description: Execute a PLAN by orchestrating Work Units with sub-agents. Use when user asks to execute or run a PLAN.
disable-model-invocation: true
argument-hint: [plan-path]
---

Read `instructions.md` in this skill folder, then follow the instructions to orchestrate execution of the given PLAN. The `do-wu.md` file in this folder contains the sub-agent instructions to pass when launching Work Unit agents.
"""

DO_PLAN_INSTRUCTIONS_TEMPLATE = """\
# Task: Execute PLAN with Sub-Agents (taskDoPLAN)

**Version:** 2.2.0
**Date:** 2025-12-18
**Audience:** AI coding agents (parent orchestrator)
**Status:** Active
**Related:** taskMakeJIGPLAN.md, taskMakePLAN.md, taskDoWU.md

## Objective

Orchestrate execution of a PLAN by launching sub-agents sequentially, verifying their outputs, and deciding when to continue vs stop and ask human.

**You are the Plan Execution Orchestrator.** Sub-agents execute WUs in fresh context. You maintain continuity, verify outputs, and escalate when needed.

---

## Your Process

### Before Starting

1. **Create branch** for this work
2. **Verify prerequisites**: JIGPLAN is human-approved, PLAN exists, branch is clean
3. **Create JOURNAL file** (`docs/wip/JOURNAL-<feature>.md`)

### Per Work Unit

1. **Launch sub-agent** with: Full PLAN + `do-wu.md` instructions + JIGPLAN constraints
2. **Receive sub-agent report**
3. **Independently verify** critical gates:
   ```bash
   pytest -xvs
   jigy rebuild && jigy validate
   git diff --stat
   ```
4. **Make decision**: CONTINUE | STOP | RETRY
5. **Update PLAN** (mark WU complete, add report to execution log)
6. **Commit** after each WU
7. **Write journal entry**

### After All WUs Complete

1. Delete deprecated O/S nodes (from JIGPLAN Clean Break Actions)
2. Run final validation: `jigy rebuild && jigy validate && pytest`
3. Generate JIG Summary
4. Write journal synthesis
5. Update PLAN with completion summary
6. Final commit (include JOURNAL file)

---

## Decision Framework

### CONTINUE when:
- Sub-agent status = COMPLETE
- All Success Gates passed
- No Escalation Triggers fired
- Your verification matches sub-agent report

### STOP when:
- Any Success Gate failed after retry
- Any Escalation Trigger fired
- FORBIDDEN brick touched
- Layer violation detected
- Compatibility shim added

### RETRY (max 2) for transient issues:
- Timing/import test failures
- Missing @jig decorators
- Simple linting errors

---

## Sub-Agent Output Format

```markdown
**Status**: COMPLETE | BLOCKED | FAILED

**Gates**: 4/4 passed
- ✓ Tests: N/N passed
- ✓ jigy validate: PASS
- ✓ FORBIDDEN bricks: untouched
- ✓ Linting: no new errors

**Specs Implemented**: S-001, S-002
**Decorators Added**: X implements, Y verifies

**Issues**: (none)
**Questions for Human**: (none)
**Recommendation**: CONTINUE | STOP_AND_ASK
```

---

## Constraints

### MUST
- Create branch at start
- Create JOURNAL file at start
- Verify independently after each WU
- Write journal entry after each WU
- Stop when uncertain
- Generate JIG Summary at end

### DO NOT
- Continue past failed quality gates
- Trust sub-agent reports without verification
- Make architectural decisions autonomously
- Allow compatibility shims (unless in JIGPLAN)

---

**Next:** Launch first sub-agent with WU1 following `do-wu.md` instructions.
"""

DO_WU_TEMPLATE = """\
# Task: Execute Work Unit (taskDoWU)

**Version:** 3.0.3
**Date:** 2025-12-18
**Audience:** AI coding agents (sub-agents executing WUs)
**Status:** Active
**Related:** taskMakeJIGPLAN.md, taskMakePLAN.md, taskDoPLAN.md

## Objective

Execute a single Work Unit from a PLAN document using Test-Driven Development while maintaining JIG alignment.

**You receive:** A PLAN document with a specific WU to execute.
**You produce:** Working code + tests + structured report.

---

## JIG Fundamentals

### Decorator Syntax

```python
@jig.implements("S-001")
def my_function(): ...

@jig.verifies("S-001")
def test_my_function(): ...
```

### JIG Commands

```bash
jigy rebuild && jigy validate   # Rebuild graphs, check integrity
jigy layers                     # Show layer structure
```

---

## Clean Break Protocol

Clean break is the DEFAULT. Do NOT add compatibility shims unless explicitly instructed.

- Old code paths are DELETED, not feature-flagged
- No backwards compatibility shims
- Unimplemented features raise `NotImplementedError`

If you discover need for backwards compatibility: STOP immediately, set Status = BLOCKED, report to orchestrator.

---

## TDD Process

### Step 1: Understand the WU
Read goal, specs, acceptance criteria, FORBIDDEN bricks.

### Step 2: Write Tests First (RED)
```python
@jig.verifies("S-001")
def test_behavior():
    # Write failing test
    assert expected_behavior()
```
Run tests: **Expected to FAIL**.

### Step 3: Implement Code (GREEN)
```python
@jig.implements("S-001")
def behavior():
    # Minimal implementation
    ...
```
Run tests: **Expected to PASS**.

### Step 4: Refactor (If Needed)

### Step 5: Verify JIG Alignment
```bash
jigy rebuild && jigy validate
```

### Step 6: Verify Success Gates
All gates from WU must pass.

### Step 7: Return Structured Report

---

## Structured Report Format

```markdown
**Status**: COMPLETE | BLOCKED | FAILED

**Gates**: X/Y passed
- ✓ Tests: N/N passed
- ✓ jigy validate: PASS
- ✓ FORBIDDEN bricks: untouched
- ✓ Linting: no new errors

**Specs Implemented**: S-001, S-002
**Decorators Added**: X implements, Y verifies
**Files Changed**: src/path/module.py (new)

**Issues**: (none)
**Questions for Human**: (none)
**Notable**: <friction, insights, near-misses>
**Recommendation**: CONTINUE | STOP_AND_ASK
**Reflection**: <what worked, what was tricky>
```

---

## Escalation Triggers

Set Status = BLOCKED and recommend STOP_AND_ASK if:
- Test failures persist after 2 attempts
- FORBIDDEN brick modification needed
- Layer constraint violation detected
- Ambiguity in spec acceptance criteria
- Discovered need for backwards compatibility
- Security concerns arise

---

## Success Criteria

- [ ] All acceptance criteria met
- [ ] Tests with `@jig.verifies` decorators
- [ ] Code with `@jig.implements` decorators
- [ ] All tests passing
- [ ] `jigy rebuild && jigy validate` passes
- [ ] No FORBIDDEN bricks modified
- [ ] Clean break maintained
- [ ] Structured report returned

---

**Next:** Return structured report to orchestrator (taskDoPLAN.md).
"""
