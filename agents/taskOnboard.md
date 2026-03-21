# Task: Onboard Project into JIG (taskOnboard)

**Version:** 1.0.0
**Date:** 2026-03-21
**Audience:** AI coding agents
**Status:** Active
**Related:** contextJIG.md, taskMakeJIGPLAN.md

## Objective

Bootstrap JIG into an existing project. Starting from a codebase with no JIG artifacts, produce a complete intent graph: bricks, charter, architecture docs, and specifications — all validated and aligned.

**Onboarding is a conversation, not a script.** Each step proposes artifacts to the user, incorporates their feedback, and writes files only after approval. The agent discovers structure; the human provides intent.

---

## When to Use This Task

- New project adopting JIG for the first time
- Existing project with code but no `jig/` directory
- Project with partial JIG setup that needs completion

**Prerequisites:**
- JIG is installed (`pip install jig` or equivalent)
- Agent has access to the project's source code and tests
- Human is available for interactive review at each step

---

## Process Overview

```
Step 1: Initialize ──→ jigy init (scaffold)
Step 2: Discover   ──→ Explore codebase, propose bricks.yaml
Step 3: Charter    ──→ Interview user, draft Charter + Goals
Step 4: Architect  ──→ Propose architecture docs from charter + bricks
Step 5: Specify    ──→ Write specs per brick, bottom-up by layer
Step 6: Validate   ──→ Run jigy validate, fix errors, confirm alignment
```

**Validation is continuous.** Run `jigy validate` after every step that writes artifacts, not just at the end. Fix errors before proceeding.

---

## Step 1: Initialize Project Structure

### Goal

Create the JIG directory scaffold and configuration.

### Process

1. Run `jigy init -p "<ProjectName>"` to create:
   - `jig.toml` — configuration
   - `jig/` — directory structure (architecture/, outcomes/, specifications/, generated/)
   - `jig/Charter_<Project>.md` — empty charter template
   - `jig/bricks.yaml` — empty brick definitions
   - `.gitignore` — updated to exclude `jig/generated/`

2. Install agent skills: `jigy init --skills-only`

3. Review `jig.toml` and adjust paths if the project uses non-standard layout:
   ```toml
   [jig.paths]
   source = "src"      # adjust if different
   tests = "tests"     # adjust if different
   ```

### Gate

- `jig.toml` exists and is valid
- `jig/` directory structure exists
- No errors from `jigy validate` (empty project is valid)

---

## Step 2: Discover and Propose Bricks

### Goal

Analyze the codebase and produce a `bricks.yaml` that partitions all code into architectural units with correct layering.

### Discovery Process

#### 2.1: Find Existing Documentation

Search for existing architecture/design docs that reveal intent:

```
README.md, ARCHITECTURE.md, DESIGN.md, docs/**/*.md
```

Summarize key findings — these inform brick naming and charter goals.

#### 2.2: Explore Codebase Structure

Analyze the source tree:
- Package/module hierarchy (directories = natural brick candidates)
- Test directory structure (often mirrors brick boundaries)
- Entry points (CLI, API, main modules = top-layer bricks)
- Shared utilities and base classes (= bottom-layer bricks)

#### 2.3: Analyze Dependencies (Large Projects)

For projects with >20 modules, perform deeper analysis:

- **Import graph**: Map which modules import from which. This reveals:
  - Natural layers (A imports B but not vice versa → B is lower layer)
  - Clusters (modules that import each other heavily → same brick)
  - Bridges (modules imported by many → foundation layer candidates)

- **AST clustering** (optional, for very large projects):
  - Extract class/function definitions per module
  - Group by semantic similarity and call patterns
  - Propose brick boundaries at natural seams

For smaller projects (<20 modules), package boundaries are usually sufficient.

#### 2.4: Determine Layers

Assign layers by dependency direction:

```
Layer 0: Foundation — no internal dependencies (utils, models, config)
Layer 1: Core logic — depends on foundation only
Layer 2: Integration — depends on core + foundation
Layer 3: Interface — CLI, API, UI (depends on everything below)
```

**Rule:** `layer = max(dependency layers) + 1`. If no internal dependencies, `layer = 0`.

#### 2.5: Determine Towers (If Applicable)

Most projects are single-tower. Use towers only when:
- Project has clearly independent subsystems (e.g., server vs client)
- Cross-subsystem code sharing happens only through shared specs, not imports
- Subsystems could reasonably be separate repos

If single-tower, omit `tower` field from all bricks.

#### 2.6: Propose to User

Present the proposed bricks as a structured table:

```markdown
## Proposed Bricks

| Brick ID | Name | Layer | Units | Rationale |
|----------|------|-------|-------|-----------|
| B-models | Data Models | 0 | M-project.models | Pure data, no deps |
| B-core | Core Logic | 1 | M-project.engine, M-project.rules | Business logic |
| B-api | REST API | 2 | M-project.api, M-project.routes | Depends on core |
```

**Ask the user:**
- Do these groupings match your mental model?
- Are there boundaries you'd draw differently?
- Any modules that feel like they belong together but are split here?
- Any planned future boundaries I should account for?

#### 2.7: Write bricks.yaml

After user approval, write `jig/bricks.yaml`:

```yaml
bricks:
  - id: B-models
    name: Data Models
    layer: 0
    units:
      - M-project.models
  - id: B-core
    name: Core Logic
    layer: 1
    units:
      - M-project.engine
      - M-project.rules
```

### Gate

- `jigy validate bricks` passes (partition complete, layers valid)
- Every source module is assigned to exactly one brick
- No layer violations in actual import graph

---

## Step 3: Draft Charter and Goals

### Goal

Create the project charter with goals that capture the *why* behind the project.

### Process

#### 3.1: Interview the User

The charter is the one artifact that must come primarily from the human. The code reveals *what* was built; only the human knows *why*.

**Ask:**
- What problem does this project solve? For whom?
- What are the 3-5 most important things this project must do well?
- What are the anti-goals — things you explicitly don't optimize for?
- If a new developer joins, what should they understand first?

#### 3.2: Propose Charter Draft

Based on user input + codebase analysis, draft:

```markdown
---
id: Charter
type: charter
goals: [G-1, G-2, G-3]
---
# Charter: <ProjectName>

## Purpose

<2-3 sentences: what problem this solves, for whom>

## Goals

### G-1: <Goal Name>
<What this means, why it matters>

### G-2: <Goal Name>
<What this means, why it matters>

### G-3: <Goal Name>
<What this means, why it matters>

## Anti-Goals
- <Things explicitly out of scope or deprioritized>

## Decision Philosophy
<Heuristics for resolving tradeoffs — which goals win when they conflict>
```

#### 3.3: Iterate with User

Present the draft. Expect 1-2 rounds of revision. Common adjustments:
- Combining or splitting goals
- Sharpening language from vague ("be reliable") to specific ("fail loudly and recover automatically")
- Adding anti-goals the user forgot to mention

#### 3.4: Write Charter

After approval, write to `jig/Charter_<Project>.md`.

### Gate

- Charter file exists with valid frontmatter
- Every goal ID in `goals:` array has a corresponding `## G-N:` section
- `jigy validate intent` passes

---

## Step 4: Propose Architecture Documents

### Goal

Create architecture documents that describe the structural decisions and constraints of the project. These bridge between high-level goals and detailed specifications.

### Process

#### 4.1: Determine Architecture Doc Scope

Read the charter goals and brick structure. Propose architecture docs based on:

**Always get their own architecture doc:**
- External interfaces (APIs, protocols, file formats) — useful to other projects
- Cross-cutting concerns (auth, logging, error handling) — affect many bricks

**Group together into fewer docs:**
- Internal subsystems that share the same goal alignment
- Related bricks at the same layer

**Segmentation heuristic:** Split when a doc would exceed ~200 lines, or when an external consumer would need to read internal details they don't care about. Otherwise, keep fewer docs.

#### 4.2: Propose to User

```markdown
## Proposed Architecture Documents

| Doc | Title | Covers Bricks | Goals | Rationale |
|-----|-------|---------------|-------|-----------|
| A-001 | Core Architecture | B-models, B-core | G-1, G-2 | Internal structure |
| A-002 | REST API Contract | B-api | G-1, G-3 | External interface |
| A-003 | Auth System | B-auth | G-2 | Cross-cutting concern |
```

**Ask the user:**
- Does this grouping make sense?
- Are there architectural decisions or constraints not captured here?
- Any external interfaces I missed?

#### 4.3: Write Architecture Documents

For each approved doc:

```markdown
---
id: A-001
type: architecture
title: <Title>
goals: [G-1, G-2]
specifications: []  # populated in Step 5
---
# <Title>

## Overview
<What this architecture covers and why>

## Structure
<Key components and their relationships>

## Constraints
<Rules that must hold — layer constraints, dependency rules, protocols>

## Interfaces
<If external-facing: API contracts, wire formats, extension points>
```

Leave `specifications: []` empty — it gets populated in Step 5 as specs are written.

### Gate

- All architecture files have valid frontmatter
- Every architecture doc links to at least one charter goal
- Architecture docs collectively cover all bricks
- `jigy validate intent` passes

---

## Step 5: Write Specifications

### Goal

Create specification documents that describe observable behavior, working bottom-up from lowest-layer bricks to highest. Specs are written for the tests — they define what verification looks like.

### Process

#### 5.1: Plan Specification Batches

Group bricks into batches for specification writing:

- **Start at layer 0** — foundation bricks have no internal dependencies, so specs are self-contained
- **Work up by layer** — each layer's specs can reference lower-layer behavior
- **Small batches** — 1-3 bricks per batch, manageable review units for the user
- **Individual bricks** for complex or large bricks

```markdown
## Specification Plan

| Batch | Bricks | Layer | Est. Specs |
|-------|--------|-------|------------|
| 1 | B-models | 0 | 3-4 |
| 2 | B-config | 0 | 2-3 |
| 3 | B-core | 1 | 5-7 |
| 4 | B-api | 2 | 4-5 |
```

#### 5.2: Write Specs Per Batch

For each batch:

**a) Analyze the code:**
- What public functions/classes exist?
- What behavior do they exhibit?
- What edge cases matter?

**b) Analyze existing tests (if any):**
- Test names reveal intended behavior: `test_parser_handles_nested_blocks` → spec about nested block handling
- Test assertions reveal acceptance criteria
- Test fixtures reveal expected data shapes

**c) If no tests exist:**
- Read the code and infer behavioral contracts
- Write specs in anticipation of future tests
- Note which specs lack verification (these become priorities for test writing)

**d) Draft specifications:**

Each spec follows the lean body format:

```markdown
---
id: S-001
type: specification
title: <Behavioral Title>
outcomes: []           # linked when outcomes are created
architecture: [A-001]  # which arch doc this falls under
---
# <Behavioral Title>

<1-3 sentence statement of what must be true.>

## Invariants
- <Always-true condition, falsifiable>
- <Always-true condition, falsifiable>

## Verification
- [ ] <What a test would assert>
- [ ] <What a test would assert>
```

**e) Propose decorator placement:**

For each spec, identify which functions implement it and which tests verify it:

```markdown
### S-001: Token Expiration

**Implements:**
- `@jig.implements("S-001")` on `src/auth/tokens.py::is_expired()`
- `@jig.implements("S-001")` on `src/auth/tokens.py::check_token()`

**Verifies:**
- `@jig.verifies("S-001")` on `tests/auth/test_tokens.py::test_expired_token()`
- `@jig.verifies("S-001")` on `tests/auth/test_tokens.py::test_fresh_token()`
```

**f) Present batch to user:**

Show the specs and proposed decorators. Ask:
- Do these specs capture the right behaviors?
- Are any specs too granular or too broad?
- Should any behaviors be split or merged?
- Are the decorator placements correct?

**g) Write files and place decorators:**

After approval:
1. Write spec files to `jig/specifications/`
2. Add `@jig.implements` decorators to source code
3. Add `@jig.verifies` decorators to test code
4. Update architecture doc `specifications:` arrays
5. Run `jigy rebuild && jigy validate`

#### 5.3: Create Outcomes (After Specs)

Once specs exist, group them into outcomes. Outcomes describe *business value*, not project goals:

```markdown
---
id: O-001
type: outcome
title: <Value Statement>
goals: [G-1]
architecture: [A-001]
specifications: [S-001, S-002, S-003]
---
# <Value Statement>

<What value this delivers and why it matters.>

## Specified By
- [[S-001]] — <brief description>
- [[S-002]] — <brief description>
```

Update spec frontmatter to add `outcomes: [O-001]` back-references.

#### 5.4: Repeat Per Batch

Work through all batches, layer by layer. Validate after each batch.

### Gate (Per Batch)

- All spec files have valid frontmatter
- Bidirectional O<->S links are consistent
- Architecture docs' `specifications:` arrays updated
- `@jig.implements` decorators placed on code
- `@jig.verifies` decorators placed on tests (where tests exist)
- `jigy rebuild && jigy validate` passes

---

## Step 6: Final Validation and Summary

### Goal

Confirm the complete intent graph is aligned and report coverage status.

### Process

1. **Full rebuild and validation:**
   ```bash
   jigy rebuild && jigy validate
   ```

2. **Review alignment:**
   ```bash
   jigy show              # project overview
   jigy show layers       # layer hierarchy
   jigy show bricks       # brick details
   ```

3. **Identify gaps:**
   - Specs without `@jig.implements` → code needs decorators
   - Specs without `@jig.verifies` → tests need decorators (or tests need writing)
   - Functions not in any brick → `bricks.yaml` needs updating
   - Bricks without specs → may need specifications or may be scaffolding

4. **Report to user:**

   ```markdown
   ## Onboarding Summary

   **Project:** <name>
   **Charter Goals:** N goals defined
   **Architecture Docs:** N docs covering N bricks
   **Specifications:** N specs written
   **Outcomes:** N outcomes grouping specs
   **Brick Coverage:** N/N bricks have specifications
   **Decorator Coverage:**
   - N functions with @jig.implements
   - N tests with @jig.verifies
   - N specs fully covered (both implements + verifies)
   - N specs partially covered (implements only, no tests yet)

   **Validation:** PASS / N warnings

   **Recommended Next Steps:**
   - <Write tests for specs lacking @jig.verifies>
   - <Add specs for uncovered bricks>
   - <etc.>
   ```

### Gate

- `jigy validate` passes with zero errors
- Every brick has at least one specification
- Every specification links to at least one outcome and one architecture doc
- Charter goals trace through architecture to specs

---

## Adapting to Project Size

### Small Projects (< 10 modules)

- Steps 2-4 can collapse into a single conversation
- Bricks ≈ packages (1:1 mapping common)
- 1-2 architecture docs sufficient
- Specs per module, not per brick
- Total time: ~1 session

### Medium Projects (10-50 modules)

- Full process as described
- AST analysis helpful but not required
- 2-4 architecture docs typical
- Spec batches of 2-3 bricks
- Total time: 2-3 sessions

### Large Projects (50+ modules)

- Import graph analysis essential for accurate layering
- AST clustering to discover non-obvious brick boundaries
- May need 5+ architecture docs
- Spec batches of 1 brick each
- Consider onboarding subsystems independently
- Total time: 3-5 sessions

---

## Skill Decomposition

Each step can be invoked independently as a skill for partial or resumed onboarding:

| Skill | Step | Preconditions |
|-------|------|---------------|
| `/jig-onboard` | All | None — detects state and resumes |
| `/jig-discover` | 2 | `jig.toml` exists |
| `/jig-charter` | 3 | `bricks.yaml` populated |
| `/jig-architect` | 4 | Charter written |
| `/jig-specify` | 5 | Architecture docs exist |

Each skill checks preconditions, detects what already exists, and picks up where the last session left off. The master `/jig-onboard` skill orchestrates all steps and skips completed ones.

---

## Anti-Patterns

### Don't Invent Intent

The agent proposes structure based on code analysis. It does NOT invent business goals, project values, or architectural rationale. If the code doesn't reveal intent, ask the user.

### Don't Over-Specify

Not every function needs its own spec. Specs describe *observable behavior*, not implementation details. A module with 20 private helper functions and 3 public functions probably needs 2-4 specs, not 20.

### Don't Skip Layers

Resist the urge to start at the top ("let me write the API specs first"). Bottom-up ordering ensures each spec can reference stable lower-layer behaviors.

### Don't Batch Too Large

A batch of 10+ specs is too large for meaningful user review. Keep batches at 3-8 specs. The user needs to actually read and approve each one.

### Don't Defer Validation

"I'll validate at the end" means you'll have cascading errors that are hard to untangle. Validate after every artifact-writing step.

---

## Constraints

### DO NOT

- **Invent charter goals** from code alone — interview the user
- **Write specs for implementation details** — only observable behavior
- **Place decorators without user approval** — propose first
- **Skip validation between steps** — errors compound
- **Create outcomes before specs** — outcomes group specs, not the reverse

### MUST

- **Start with bricks** — everything else depends on code structure
- **Work bottom-up** for specs — layer 0 before layer 1
- **Get explicit user approval** before writing each artifact type
- **Run `jigy validate` after every step** that writes files
- **Propose before writing** — show tables/drafts, get feedback, then write

### PREFER

- **Fewer architecture docs** over more — split only when necessary
- **Behavioral spec titles** over structural ones — "Token Expiration" not "Token Module"
- **Existing test names** as spec inspiration — tests reveal intended behavior
- **Interactive questions** over assumptions — when unsure, ask

---

## Version History

- **1.0.0** (2026-03-21): Initial version

---

**Next:** After onboarding is complete, use the standard JIG workflow (taskMakeJIGPLAN → taskMakePLAN → taskDoPLAN) for ongoing development.
