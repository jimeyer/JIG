# Task: Onboard Project into JIG (taskOnboard)

**Version:** 1.0.0
**Date:** 2026-03-21
**Audience:** AI coding agents
**Status:** Active
**Related:** contextJIG.md, taskMakeJIGPLAN.md

## Objective

Bootstrap JIG into an existing project. Starting from a codebase with no JIG artifacts, produce a complete intent graph: bricks, charter, architecture docs, specifications, and outcomes — all validated and aligned.

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
Step 3: Charter    ──→ Interview user, draft Charter + Goals + outcome sketches
Step 4: Architect  ──→ Propose architecture docs from charter + bricks
Step 5: Specify    ──→ Write specs per brick, bottom-up by layer
Step 6: Outcomes   ──→ Formalize outcomes from specs + charter sketches
Step 7: Validate   ──→ Run jigy validate, fix errors, confirm alignment
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

The charter is the one artifact that must come primarily from the human. The code reveals *what* was built; only the human knows *why*. Asking "what are your goals?" directly produces platitudes. Instead, use three discovery lenses that progressively sharpen from concrete to abstract.

#### 3.1: Lens 1 — Purpose and Stakeholders

Establish the factual foundation. Most users can answer these easily.

**Ask:**
1. **"In one sentence, what does this project do?"** — Forces clarity. If they can't say it in one sentence, explore until they can.
2. **"Who depends on it?"** — End users, other developers, other systems, operators. List them all.
3. **"What would break if this project disappeared tomorrow?"** — More revealing than "what does it do" because it identifies what's *uniquely valuable*, not just what exists.

The answers give you the **purpose statement** and a **stakeholder list**. The "what would break" answer often reveals the real purpose better than the project's README.

#### 3.2: Lens 2 — Quality Priorities

Move from description to prioritization. Present quality dimensions and ask the user to **rank and reject** — not check boxes.

**Present this table:**

| Quality | Meaning | Example Signal |
|---------|---------|----------------|
| Correctness | Produces right answers, always | Financial calculations, medical |
| Reliability | Keeps working under adversity | Infrastructure, uptime-critical |
| Performance | Fast enough for its use case | Real-time, high-throughput |
| Extensibility | Easy to add new capabilities | Plugin systems, frameworks |
| Operability | Easy to deploy, monitor, debug | Production services |
| Usability | Easy for end users | Developer tools, APIs |
| Security | Resists unauthorized access | Auth, data handling |
| Maintainability | Easy for developers to change | Long-lived codebases |

**Ask:**
- **"Pick your top 3-4. Which matter MOST for this project?"**
- **"Which ones do you explicitly NOT care about?"**

**Rules:** "All of them" is not allowed. The user must choose. Qualities they reject become anti-goals. The ranking reveals real priorities — everyone wants everything, but the ordering is what matters for architectural decisions.

#### 3.3: Lens 3 — Tensions and Tradeoffs

This is the most revealing lens. Based on the user's top qualities from Lens 2, present concrete tension pairs and ask which side wins.

**Generate 2-4 tension pairs from the user's top qualities. Examples:**

- **Correctness vs Speed:** "Do you validate exhaustively, or accept occasional errors for throughput?"
- **Flexibility vs Simplicity:** "Do you support every edge case, or keep the API surface small?"
- **Backwards Compatibility vs Clean Design:** "Do you preserve old interfaces, or break them for better abstractions?"
- **Developer Experience vs Runtime Performance:** "Do you optimize for the person writing code, or the machine running it?"
- **Completeness vs Ship Date:** "Do you cover every case before releasing, or ship the 80% and iterate?"

**Tailor tensions to the codebase.** If you see elaborate plugin systems, ask about flexibility vs simplicity. If you see defensive error handling everywhere, ask about correctness vs speed. The code informs which tensions are live for this project.

Each resolved tension becomes a **decision heuristic** in the Decision Philosophy section.

#### 3.4: Synthesize Goals

Each goal should follow this structure:

```
[Specific problem this project faces] → [How the project addresses it]
```

**For each of the user's top 3-4 qualities, write a goal that:**
1. Names the specific problem or challenge (not a generic aspiration)
2. States how the project addresses it (not just "be good at X")
3. Implies what success looks like (testable, not vague)

**Example synthesis:**

User said: "Correctness matters most. We do financial calculations. Performance matters but correctness always wins."

> **G-1: Calculation Integrity**
> Financial calculations must produce provably correct results. When correctness conflicts with performance or convenience, correctness wins. All calculation paths have explicit test coverage with known-good reference values.

Compare to the bad version: "G-1: Be Correct — The system should produce correct results." This tells you nothing — every project wants correct results. The good version names the domain (financial calculations), takes a side on a tension (correctness over performance), and implies verification criteria (reference values).

#### 3.5: Propose Charter Draft

Assemble purpose (Lens 1), goals (synthesized from Lenses 2-3), anti-goals (rejected qualities from Lens 2), and decision philosophy (tension resolutions from Lens 3):

```markdown
---
id: Charter
type: charter
goals: [G-1, G-2, G-3]
---
# Charter: <ProjectName>

## Purpose

<2-3 sentences from Lens 1: what problem this solves, for whom, what breaks without it>

## Goals

### G-1: <Goal Name>
<Problem statement → how the project addresses it>

### G-2: <Goal Name>
<Problem statement → how the project addresses it>

### G-3: <Goal Name>
<Problem statement → how the project addresses it>

## Anti-Goals
- <Rejected qualities from Lens 2, stated as explicit non-priorities>
- <Things the project deliberately does NOT optimize for>

## Decision Philosophy
<Tension resolutions from Lens 3, stated as heuristics>
<e.g., "When correctness conflicts with performance, correctness wins.">
<e.g., "Prefer clean breaks over backwards compatibility unless external consumers depend on the interface.">
```

#### 3.6: Sketch Outcome Candidates

Before leaving the charter conversation, capture lightweight outcome sketches while the user is still in "big picture" mode. These are *not* formal outcome documents — they're informal notes that guide spec writing in Step 5.

**For each goal, ask:**
> "For G-N, what 2-3 capabilities would tell you this goal is being met in practice?"

The user's answers become outcome sketches — one-line descriptions attached to goals:

```markdown
## Outcome Sketches (informal — formalized in Step 6)

- G-1 (Calculation Integrity):
  - "All arithmetic operations produce exact decimal results"
  - "Rounding rules are explicit and auditable"
- G-2 (Developer Experience):
  - "New contributors can run tests within 5 minutes of cloning"
  - "Error messages point to the fix, not just the failure"
```

**Why now:** The user just finished articulating goals and tensions — outcome thinking is a natural continuation. These sketches cost very little (a few bullet points per goal) but provide top-down guidance that keeps spec writing oriented toward value delivery.

**Why not formal yet:** You don't know what specs exist. Formal outcomes group specs, and you can't group what doesn't exist yet. These sketches will be revisited and formalized in Step 6 after specs are written.

#### 3.7: Iterate with User

Present the draft. Expect 1-2 rounds of revision. Common adjustments:
- Combining or splitting goals
- Sharpening language from vague ("be reliable") to specific ("fail loudly and recover automatically")
- Adding anti-goals the user forgot to mention
- Adjusting tension resolutions after seeing them written down

#### 3.8: Write Charter

After approval, write to `jig/Charter_<Project>.md`.

### Gate

- Charter file exists with valid frontmatter
- Every goal ID in `goals:` array has a corresponding `## G-N:` section
- Goals follow problem→mechanism structure, not generic aspirations
- Anti-goals section is populated (at least 1 rejected quality)
- Decision philosophy section has at least 1 tension resolution
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

#### 5.3: Repeat Per Batch

Work through all batches, layer by layer. Validate after each batch.

### Gate (Per Batch)

- All spec files have valid frontmatter
- Architecture docs' `specifications:` arrays updated
- `@jig.implements` decorators placed on code
- `@jig.verifies` decorators placed on tests (where tests exist)
- `jigy rebuild && jigy validate` passes

---

## Step 6: Formalize Outcomes

### Goal

Synthesize specifications into formal outcome documents that measure whether charter goals are being achieved. Outcomes are the KPI layer — they answer "how do we know goal G-N is being served?" by grouping the specs that collectively deliver a capability.

### Why Outcomes Come After Specs

Outcomes group specs. Writing them before specs exist forces you to guess at groupings, which inevitably need heavy revision. By waiting until specs are written:

- **Natural clusters are visible** — after writing 15 specs, you can see "these 4 are all about the same user-facing capability"
- **Grounded in reality** — you're codifying patterns that already emerged, not speculating
- **Less revision** — formal outcomes are right the first time because they describe what actually exists
- **Gaps surface naturally** — "we have specs for X and Y but no outcome captures their combined value" reveals missing outcomes

The outcome sketches from Step 3.6 provide top-down guidance; this step grounds them in the actual spec landscape.

### Process

#### 6.1: Revisit Outcome Sketches

Retrieve the outcome sketches captured during Step 3.6. For each sketch:

1. **Match to actual specs** — Which specs from Step 5 correspond to this sketch?
2. **Evaluate fit** — Does the sketch still make sense given what specs were actually written?
3. **Note gaps** — Are there spec clusters that don't map to any sketch? These suggest new outcomes.

#### 6.2: Identify Spec Clusters

Beyond the original sketches, look for natural groupings:

- Specs within the same brick that serve the same user-facing capability
- Specs across bricks that collaborate on a single observable feature
- Specs that a stakeholder (from Lens 1 of the charter) would group together when asking "does feature X work?"

#### 6.3: Draft Outcome Documents

For each outcome:

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

<What capability this delivers, why it matters, and how it serves the linked goal(s).>

## Specified By
- [[S-001]] — <brief description>
- [[S-002]] — <brief description>
- [[S-003]] — <brief description>
```

**Guidelines:**
- An outcome title is a *value statement*, not a feature name: "Calculations Produce Exact Decimal Results" not "Calculator Module"
- Every outcome links to at least one goal — if it doesn't serve a goal, question whether it belongs
- Every spec should appear in at least one outcome — orphan specs indicate a missing outcome or an unnecessary spec
- Outcomes can share specs (a spec can serve multiple capabilities)

#### 6.4: Propose to User

Present outcomes as a summary table showing how they bridge goals to specs:

```markdown
## Proposed Outcomes

| Outcome | Title | Goals | Specs | Rationale |
|---------|-------|-------|-------|-----------|
| O-001 | Exact Decimal Arithmetic | G-1 | S-001, S-002, S-005 | Core calculation correctness |
| O-002 | Auditable Rounding | G-1 | S-003, S-004 | Rounding transparency |
| O-003 | Fast Test Feedback | G-2 | S-010, S-011 | Developer experience |
```

**Ask the user:**
- Do these outcomes capture the right value clusters?
- Are any specs orphaned (not in any outcome)?
- Do the goal linkages feel right?
- Should any outcomes be split or merged?

#### 6.5: Write Outcome Files and Update Back-References

After approval:
1. Write outcome files to `jig/outcomes/`
2. Update spec frontmatter to add `outcomes: [O-001]` back-references
3. Run `jigy rebuild && jigy validate`

### Gate

- All outcome files have valid frontmatter
- Every outcome links to at least one goal and at least one spec
- Bidirectional O↔S links are consistent (outcome lists spec, spec lists outcome)
- Every spec appears in at least one outcome
- `jigy validate intent` passes

---

## Step 7: Final Validation and Summary

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
| `/jig-outcomes` | 6 | Specs written |

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
- **Formalize outcomes before specs exist** — sketch outcomes in Step 3, but formal O-### documents come after specs in Step 6

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
