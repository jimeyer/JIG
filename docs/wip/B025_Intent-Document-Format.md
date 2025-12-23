---
title: Intent Document Format Specification
date: 2025-12-22
status: draft
purpose: Canonical format and voice guidance for JIG outcome and specification documents
---

# Intent Document Format Specification

_How to write outcomes and specifications that serve AI agents, humans, and the intent graph._

---

## Overview

JIG's intent hierarchy flows from Constitution → Outcomes → Specifications → Tests → Functions.
This document defines the format for **Outcomes** (O-*) and **Specifications** (S-*).

| Document | Purpose | Answers | Scope |
|----------|---------|---------|-------|
| **Outcome** | Business value that persists | WHY does this matter? | Broad capability |
| **Specification** | Observable system behavior | WHAT does the system do? | Specific, testable |

Both document types share formatting conventions and voice guidelines, but differ in
structure and content focus.

---

# Part I: Outcomes

## Outcome Frontmatter

Every outcome MUST begin with YAML frontmatter:

```yaml
---
id: O-013
title: Layer Architecture Enforcement
type: outcome
specifies: [S-027, S-028]
---
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique identifier: `O-NNN` (zero-padded 3 digits) |
| `title` | string | ✅ | Authoritative title (noun phrase describing value) |
| `type` | string | ✅ | Always `outcome` |
| `specifies` | array | ✅ | Specification IDs that deliver this outcome |

The `title` field is **authoritative**. The H1 heading repeats it exactly.

---

## Outcome Section Structure

Each outcome MUST contain these sections in order:

```markdown
# [Title from frontmatter]

**Value:** [One sentence: what pain this solves]

**Acceptance:** [One measurable criterion: minimum bar for "done"]

## Why This Matters

[2-3 paragraphs explaining agent and human benefit]

## Rationale

[3-5 paragraphs: problem, failed approaches, solution, downstream benefits]

## Success Criteria

[Numbered list: 3-8 measurable, testable criteria]

## Specified By

[List of specs with one-sentence descriptions]

## Constitution Linkage

[How this connects to JIG's purpose]
```

---

## Outcome Section Details

### Title (Outcomes)

The title is a **noun phrase describing delivered value**.

✅ **Good outcome titles:**
- `Implementation Structure Discovery`
- `Automated Code-to-Specification Traceability`
- `Layer Architecture Enforcement`
- `Fast Project Validation`

❌ **Bad outcome titles:**
- `Discover Implementation Structure` — imperative verb
- `O-001: Implementation` — includes ID
- `Make graphs work faster` — describes work, not value

---

### Value Statement

One sentence explaining what pain this outcome eliminates.

**Format:** `[Who] can [do what] without [the old pain point].`

```markdown
**Value:** Agents can query actual code structure instead of guessing from file names.
```

```markdown
**Value:** Developers discover layer violations at edit time, not after deployment.
```

---

### Acceptance Statement

One measurable criterion defining the minimum bar for "done."

**Must include:** A number, time bound, or percentage.

```markdown
**Acceptance:** `jigy impl rebuild` generates a complete graph in <2 seconds for 10K LOC.
```

```markdown
**Acceptance:** 99%+ of decorator links are captured without manual intervention.
```

---

### Why This Matters (Outcomes)

2-3 paragraphs explaining the outcome's importance. **Lead with agents.**

**Structure:**
1. **Agent perspective** — How agents use this, what failure modes it prevents
2. **Human perspective** — How developers benefit
3. **System perspective** — What becomes possible

---

### Rationale (Outcomes)

3-5 paragraphs explaining the deeper reasoning.

**Structure:**
1. **The problem** — What goes wrong without this outcome
2. **Failed approaches** — Why alternatives don't work
3. **The solution** — How this outcome addresses the root cause
4. **Downstream benefits** — What else becomes possible

---

### Success Criteria (Outcomes)

A numbered list of 3-8 measurable criteria.

**Format:**

```markdown
## Success Criteria

The [system/command/validator] must:

1. [Action] [measurable outcome] in [time/accuracy bound]
2. [Action] [measurable outcome] [specific detail]
3. [Continue for 3-8 items]
```

Each criterion MUST:
- Start with an action verb (`detect`, `report`, `validate`, `generate`)
- Include a measurable bound
- Be independently verifiable

---

### Specified By

Lists the specifications that deliver this outcome.

**Format:**

```markdown
## Specified By

This outcome is delivered through:

- **S-027**: [One sentence describing this spec's contribution]
- **S-028**: [One sentence describing this spec's contribution]
```

**Do not:** Just list spec IDs without descriptions.

---

### Constitution Linkage

**Format:**

```markdown
## Constitution Linkage

**Serves:** [One sentence: how this advances JIG's purpose]

**Enables:** [One sentence: what becomes possible downstream]

**Without this:** [One sentence: what breaks for agents and humans]
```

---

# Part II: Specifications

## Specification Frontmatter

Every specification MUST begin with YAML frontmatter:

```yaml
---
id: S-027
title: Layer Constraint Validation
type: specification
---
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique identifier: `S-NNN` (zero-padded 3 digits) |
| `title` | string | ✅ | Authoritative title (noun phrase describing behavior) |
| `type` | string | ✅ | Always `specification` |

The `title` field is **authoritative**. The H1 heading repeats it exactly.

---

## Specification Section Structure

Each specification MUST contain these sections in order:

```markdown
# [Title from frontmatter]

[1-2 sentence summary of the observable behavior]

## Acceptance Criteria

[Bulleted list of observable, testable criteria]

## Rationale

[1-2 paragraphs explaining why this behavior matters]
```

Specifications are **shorter and more focused** than outcomes. They describe
behavior precisely enough that:
- A developer can implement it (`@jig.implements`)
- A tester can verify it (`@jig.verifies`)

---

## Specification Section Details

### Title (Specifications)

The title is a **noun phrase describing observable behavior or capability**.

**Outcome titles** describe **delivered value** — the WHY.
**Specification titles** describe **observable behavior** — the WHAT.

**Pattern:** `[Subject] [Behavior]` or `[Behavior] [Scope]`

✅ **Good specification titles:**
- `Token Expiration` — names a behavior
- `Layer Constraint Validation` — names a capability
- `Brick ID Format Compliance` — names a contract
- `Graph Generation Performance` — names a measurable behavior
- `Decorator Link Extraction` — names what the system does
- `Orphan Detection for Specifications` — names a specific capability

❌ **Bad specification titles:**
- `Validate Layer Constraints` — imperative verb
- `S-027: Layers` — includes ID
- `Make sure bricks are valid` — informal
- `Fast Validation` — too vague (outcome or spec?)
- `Authentication` — too broad to implement directly

**Test:** Can you write `@jig.implements("S-XXX")` on a function? If yes, it's
a good specification title. If too broad, it belongs as an outcome.

---

### Summary Statement

1-2 sentences describing the observable behavior. This is the specification's
core contract.

**Format:** `[System/Component] [MUST/SHALL] [behavior] [condition/constraint].`

```markdown
# Token Expiration

Authentication tokens MUST expire after 15 minutes of inactivity.
```

```markdown
# Layer Constraint Validation

The layer validator MUST detect and report all upward dependencies where a
brick at layer N calls a brick at layer N+1 or higher.
```

Use **MUST**, **SHALL**, **SHOULD** per RFC 2119 conventions:
- **MUST/SHALL** — absolute requirement
- **SHOULD** — recommended but exceptions possible
- **MAY** — optional

---

### Acceptance Criteria

A bulleted list of observable, testable criteria. Each criterion should be
verifiable by a test.

**Format:**

```markdown
## Acceptance Criteria

- [Observable behavior with specific inputs/outputs]
- [Edge case handling]
- [Performance or accuracy bound if applicable]
```

**Example:**

```markdown
## Acceptance Criteria

- Token created with `expires_at = now() + 15 minutes`
- Any authenticated operation updates `last_activity` timestamp
- Token rejected if `now() > last_activity + 15 minutes`
- Expired tokens return 401 Unauthorized, not 403 Forbidden
```

**Each criterion MUST:**
- Describe observable behavior (not implementation)
- Be testable with `@jig.verifies`
- Avoid implementation details (use Redis, call function X)

---

### Rationale (Specifications)

1-2 paragraphs explaining why this behavior matters. Shorter than outcome
rationale—just enough context for implementers.

**Format:**

```markdown
## Rationale

[Why this behavior exists. What problem it solves. What breaks without it.]
```

**Example:**

```markdown
## Rationale

Token expiration limits the exposure window if a token is compromised. The
15-minute inactivity timeout balances security (short window) with usability
(users aren't logged out during normal workflows). Activity-based refresh
means active users stay authenticated while idle sessions expire.
```

---

## Distinguishing Outcomes from Specifications

| Aspect | Outcome | Specification |
|--------|---------|---------------|
| **Describes** | Value delivered | Behavior exhibited |
| **Answers** | Why does this matter? | What does the system do? |
| **Scope** | Broad capability | Specific, testable behavior |
| **Length** | 30-60 lines | 15-30 lines |
| **Sections** | 7 sections | 3 sections |
| **Tests** | Indirectly via specs | Directly (`@jig.verifies`) |
| **Implementation** | Too broad | Directly (`@jig.implements`) |

**Hierarchy:** One outcome decomposes into multiple specifications.

---

# Part III: Formatting Guidelines

These conventions apply to **both** outcomes and specifications.

## Markdown Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Code/commands | Backticks | `jigy validate` |
| File paths | Backticks | `jig/outcomes/O-001.md` |
| Specs/Outcomes | Bold + ID | **S-001**, **O-012** |
| Emphasis | Italics sparingly | _not_ a refactoring task |
| Key terms | Bold on first use | **alignment graph** |
| Lists | Dashes for bullets | `- Item one` |
| Numbers | Spell out < 10 | "three criteria" not "3 criteria" |
| Metrics | Always numeric | "<2 seconds" not "under two seconds" |

## Line Length

- Wrap prose at ~80 characters for readable diffs
- Do not hard-wrap within code blocks
- Do not hard-wrap table rows

## Whitespace

- One blank line between sections
- One blank line before and after code blocks
- No trailing whitespace
- No multiple consecutive blank lines

## Lists

- Use numbered lists only for ordered/sequential items
- Use bullets for unordered items
- Indent nested lists with 2 spaces
- End list items without periods unless complete sentences

## Code Blocks

- Always specify language: ` ```yaml `, ` ```markdown `
- Use inline backticks for short references
- Use fenced blocks for multi-line examples

---

# Part IV: Voice and Content Guidance

These principles apply to **both** outcomes and specifications.

## Evergreen Principle

Outcomes and specifications are **permanent documentation**. They are NOT:
- Project goals ("achieve 90% test coverage")
- Work unit objectives ("add missing tests")
- Refactoring tasks ("reorganize code")
- Process improvements ("improve code organization")

**Test:** Remove all references to the work that created this. Does it still
make sense? If no, rewrite.

**Test:** Would a new developer in two years understand this? If no, add context.

## Agent-First Framing

JIG exists to enable AI coding agents. Every document should consider:

1. **How agents use it** — What queries, commands, or data agents consume
2. **What agent failures it prevents** — Hallucination, invalid dependencies
3. **How humans benefit** — Developer productivity follows from agent correctness

## Value Over Activity

Describe **what exists** (value), not **what was done** (activity).

❌ **Bad:** We added validation for brick definitions.
✅ **Good:** Brick definition validation catches format errors before graph generation.

## Concrete Over Abstract

Use specific examples, actual command names, real metrics.

❌ **Bad:** Validation is fast enough for development workflows.
✅ **Good:** `jigy validate` completes in <5 seconds for 10K LOC.

## Quantify Everything

Replace vague words with numbers:

| Vague | Quantified |
|-------|------------|
| fast | <5 seconds |
| most | 80%+ |
| many | 6+ items |
| quickly | in <1 second |
| reliable | 99%+ accuracy |

## Active Voice

Prefer active constructions that name the actor.

❌ **Bad:** Errors are reported with line numbers.
✅ **Good:** The validator reports errors with file:line precision.

## Present Tense

Describe current system behavior, not future plans or past work.

❌ **Bad:** This will enable... / We added...
✅ **Good:** This enables... / The system detects...

---

# Part V: Anti-Patterns

## Outcome Anti-Patterns

### Project Goals as Outcomes

❌ **Bad:**
```markdown
# Test Coverage
Critical paths have comprehensive tests.
```

✅ **Good:**
```markdown
# System Reliability Through Verification
Critical behaviors are verified to prevent regressions in production.

**Value:** Reduces customer-facing bugs and deployment risk.
```

### Process Improvements as Outcomes

❌ **Bad:**
```markdown
# Code Organization
Related code co-located in correct bricks.
```

✅ **Good:**
```markdown
# Clear Architectural Boundaries
Authentication logic is isolated from business logic.

**Value:** Reduces time to implement auth changes without breaking other systems.
```

### Implementation Details as Outcomes

❌ **Bad:**
```markdown
# Decorator Support
Functions can be annotated with @jig.implements decorators.
```

✅ **Good:**
```markdown
# Automated Code-to-Specification Traceability
Code-to-specification links are captured automatically from source annotations.

**Value:** Traceability is a byproduct of development, not a maintenance burden.
```

---

## Specification Anti-Patterns

### Refactoring Tasks as Specifications

❌ **Bad:**
```markdown
# Relocate era_persistence
era_persistence.py moved from utils to protocol-core.
```

✅ **Good:**
```markdown
# EraLamportClock Persistence

EraLamportClock state MUST persist across process restarts without clock regression.

## Acceptance Criteria
- `get_era()` returns last saved era + 1 on process start
- `save_era()` writes era to persistent storage
- Clock never returns same timestamp after restart
```

### Implementation Instructions as Specifications

❌ **Bad:**
```markdown
# Use Redis for Caching
Implement caching using Redis with 5-minute TTL.
```

✅ **Good:**
```markdown
# Query Result Caching

Repeated identical queries MUST return cached results within 10ms.

## Acceptance Criteria
- First query executes full computation
- Subsequent identical queries return in <10ms
- Cache invalidates when underlying data changes
- Cache entries expire after 5 minutes of staleness
```

### Tooling Requirements as Specifications

❌ **Bad:**
```markdown
# Functions Have Decorators
add_device() and remove_device() have @jig.implements decorators.
```

✅ **Good:**
```markdown
# Airspace Device Lifecycle

Devices can be added and removed from shared airspace CRDT.

## Acceptance Criteria
- `add_device(id, metadata)` creates device entry with vector clock
- `remove_device(id)` tombstones device, preserves history
- Operations are commutative and idempotent
```

### Meta-Specifications

❌ **Bad:**
```markdown
# Specification Completeness
All public APIs have specifications.
```

✅ **Good:**
```markdown
# Catalog Query Interface Contract

DataDictionaryCatalog provides deterministic query results for device metadata.

## Acceptance Criteria
- `get_data_element(id)` returns element or None, never throws
- `get_gui_metadata(id)` returns display info or default values
- Query results consistent across repeated calls with same state
```

---

# Part VI: Complete Examples

## Outcome Example

```markdown
---
id: O-013
title: Layer Architecture Enforcement
type: outcome
specifies: [S-027, S-028]
---

# Layer Architecture Enforcement

**Value:** Agents cannot introduce upward dependencies even when changes seem
locally beneficial.

**Acceptance:** `jigy validate layers` detects all layer violations in <1 second
with file:line precision.

## Why This Matters

AI agents optimizing for local correctness may introduce dependencies that
violate architectural boundaries. An agent adding a "helpful" import from
a feature module into a foundation module creates coupling that compounds
over time. Without enforcement, these violations are invisible until the
architecture is unmaintainable.

Human developers face the same temptation: taking a shortcut that "works"
but violates intended structure. Layer enforcement makes the cost of
shortcuts immediate and visible.

The system benefits from consistent enforcement: build order is predictable,
foundation modules remain stable, and features evolve independently.

## Rationale

Software architectures decay through accumulation of small violations. Each
individual upward dependency seems harmless—"just this once"—but the compound
effect creates circular dependencies and modules that cannot be modified
independently.

Manual code review catches obvious violations but misses subtle ones. A
function call three levels deep may create an upward dependency that no
reviewer notices. Layer enforcement automates exhaustive checking of every
call site against declared layer constraints.

## Success Criteria

The layer validator must:

1. Detect upward dependencies (layer N calling layer N+1) in <1 second
2. Detect circular dependencies at any layer depth
3. Report violating call sites with file:line:function precision
4. Suggest specific remediation (move function, add interface, adjust layer)
5. Pass validation only when architecture is acyclic and downward-only
6. Integrate with `jigy validate` for single-command verification

## Specified By

This outcome is delivered through:

- **S-027**: Layer constraint validation — Checks every call site against layers
- **S-028**: Layer violation reporting — Formats violations with actionable detail

## Constitution Linkage

**Serves:** Prevents architectural decay by making layer violations visible.

**Enables:** Confident refactoring—agents and developers know architecture is consistent.

**Without this:** Agents introduce coupling that compounds until unmaintainable.
```

---

## Specification Example

```markdown
---
id: S-027
title: Layer Constraint Validation
type: specification
---

# Layer Constraint Validation

The layer validator MUST detect all architectural violations where a brick at
layer N depends on a brick at layer N+1 or higher.

## Acceptance Criteria

- Upward dependencies detected: layer N calling layer N+1 or higher
- Circular dependencies detected at any layer depth, including layer 0
- Validation completes in <1 second for projects with 100+ bricks
- Each violation reported with:
  - Source brick ID and layer
  - Target brick ID and layer
  - Specific function call creating the dependency
  - File and line number of the call site
- Exit code non-zero when violations exist
- Exit code zero when architecture is valid

## Rationale

Layer constraints prevent architectural decay. Without automated validation,
upward dependencies accumulate invisibly until refactoring becomes impossible.
Fast validation (<1 second) enables pre-commit hooks and continuous checking.
Precise violation reporting (file:line) enables immediate remediation.
```

---

# Part VII: Checklists

## Outcome Checklist

Before committing an outcome, verify:

### Structure
- [ ] Frontmatter has `id`, `title`, `type`, `specifies`
- [ ] H1 title matches frontmatter `title` exactly
- [ ] Title is noun phrase describing value (not imperative)
- [ ] Value statement is one sentence with clear benefit
- [ ] Acceptance has a measurable criterion
- [ ] "Why This Matters" leads with agent perspective
- [ ] Rationale has 3-5 paragraphs with problem→solution arc
- [ ] Success Criteria has 3-8 numbered, measurable items
- [ ] "Specified By" has descriptions, not just IDs
- [ ] Constitution Linkage has Serves/Enables/Without this

### Content
- [ ] Describes evergreen value, not project state
- [ ] Would make sense to new developer in 2 years
- [ ] All claims are quantified
- [ ] Agent benefit is explicit, not implied

---

## Specification Checklist

Before committing a specification, verify:

### Structure
- [ ] Frontmatter has `id`, `title`, `type`
- [ ] H1 title matches frontmatter `title` exactly
- [ ] Title is noun phrase describing behavior (not imperative)
- [ ] Summary uses MUST/SHALL/SHOULD appropriately
- [ ] Acceptance Criteria are bulleted and testable
- [ ] Rationale explains why (1-2 paragraphs)

### Content
- [ ] Describes observable behavior, not implementation
- [ ] Can be implemented (`@jig.implements`)
- [ ] Can be verified (`@jig.verifies`)
- [ ] No file paths or implementation details
- [ ] No refactoring tasks or tooling requirements

### Testability
- [ ] Each acceptance criterion is independently testable
- [ ] Criteria specify inputs, outputs, or observable effects
- [ ] Edge cases are explicit

---

# References

- [Constitution v2](../../jig/Constitution_v2.md) — The governing document
- [A001 Core Artifacts Contract](../architecture/A001_Core-Artifacts-Contract.md) — Artifact schemas
- [Evergreen Intent Guidance](../../agents/contextEvergreenIntent.md) — O/S principles
- [Outcome Audit Report](./B019_AUDIT_outcomes-2025-12-13.md) — Analysis informing this spec
