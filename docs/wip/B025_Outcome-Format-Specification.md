---
title: Intent Document Format Specification
date: 2025-12-22
status: draft
purpose: Canonical format and voice guidance for JIG outcome and specification documents
---

# Intent Document Format Specification

_How to write outcomes and specifications that serve AI agents, humans, and the intent graph._

---

## Part I: Document Structure

### Frontmatter (Required)

Every outcome MUST begin with YAML frontmatter containing these fields:

```yaml
---
id: O-XXX
title: Layer Architecture Enforcement
type: outcome
specifies: [S-XXX, S-YYY, S-ZZZ]
---
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique identifier in format `O-NNN` (zero-padded 3 digits) |
| `title` | string | ✅ | Authoritative title of the outcome (noun phrase describing the value) |
| `type` | string | ✅ | Always `outcome` |
| `specifies` | array | ✅ | Specification IDs that deliver this outcome |

The `title` field is the **authoritative** title. The H1 heading in the document body repeats this title exactly.

---

### Section Structure (Required)

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

[How this connects to JIG's purpose and which theme(s) it serves]
```

---

### Section Details

#### Title

The H1 title **repeats the `title` field from frontmatter exactly**. The frontmatter
is authoritative; the H1 provides human-readable display.

The title is a **noun phrase** describing the delivered value, not an action or task.

✅ **Good titles:**
- `Implementation Structure Discovery`
- `Automated Code-to-Specification Traceability`
- `Layer Architecture Enforcement`
- `Fast Project Validation`

❌ **Bad titles:**
- `Discover Implementation Structure` — imperative verb
- `O-001: Implementation` — includes ID (redundant with frontmatter)
- `Make graphs work faster` — describes work, not value

---

### Specification Titles

Specifications also have a `title` field in frontmatter. However, specification titles
follow a different pattern than outcome titles.

**Outcome titles** describe **delivered value** — the WHY.
**Specification titles** describe **observable behavior** — the WHAT.

#### Form

A specification title is a **noun phrase describing a capability, behavior, or contract**
that the system exhibits. It names what the system does, not why it matters or how to
build it.

**Pattern:** `[Subject] [Behavior/Capability]` or `[Behavior] [Constraint/Scope]`

#### Examples

✅ **Good specification titles:**
- `Token Expiration` — names a behavior
- `Layer Constraint Validation` — names a capability
- `Brick ID Format Compliance` — names a contract
- `Graph Generation Performance` — names a measurable behavior
- `Decorator Link Extraction` — names what the system does
- `Orphan Detection for Specifications` — names a specific capability

❌ **Bad specification titles:**
- `Validate Layer Constraints` — imperative verb (describes work, not behavior)
- `S-027: Layers` — includes ID (redundant with frontmatter)
- `Make sure bricks are valid` — informal, describes activity
- `Fast Validation` — too vague, could be outcome or spec
- `Authentication` — too broad, not specific to a behavior

#### Distinguishing Outcomes from Specifications

| Aspect | Outcome Title | Specification Title |
|--------|---------------|---------------------|
| **Describes** | Value delivered | Behavior exhibited |
| **Answers** | Why does this matter? | What does the system do? |
| **Scope** | Broad capability | Specific, testable behavior |
| **Can you write a test for it?** | Indirectly (via specs) | Directly (`@jig.verifies`) |
| **Can you implement it?** | No (too broad) | Yes (`@jig.implements`) |

**Test:** Can you write `@jig.implements("S-XXX")` on a function? If yes, it's a good
specification title. If the title is too broad to implement directly, it belongs as
an outcome.

#### Specification Frontmatter

```yaml
---
id: S-027
title: Layer Constraint Validation
type: specification
---
```

The `title` field is authoritative. The H1 heading repeats it exactly, just as with outcomes.

---

#### Value Statement

One sentence explaining what pain this outcome eliminates.

**Format:** `[Who] can [do what] without [the old pain point].`

**Examples:**

```markdown
**Value:** Agents can query actual code structure instead of guessing from file names.
```

```markdown
**Value:** Developers discover layer violations at edit time, not after deployment.
```

---

#### Acceptance Statement

One measurable criterion that defines the minimum bar for "done."

**Must include:** A number, time bound, or percentage.

**Examples:**

```markdown
**Acceptance:** `jigy impl rebuild` generates a complete graph in <2 seconds for 10K LOC.
```

```markdown
**Acceptance:** 99%+ of decorator links are captured without manual intervention.
```

---

#### Why This Matters

2-3 paragraphs explaining the outcome's importance to both AI agents and humans. **Lead with agents.**

**Structure:**
1. **Agent perspective** — How agents use this, what failure modes it prevents
2. **Human perspective** — How developers benefit
3. **System perspective** — What becomes possible in the overall architecture

**Example:**

```markdown
## Why This Matters

AI agents working in unfamiliar codebases cannot reliably infer structure from
file names or directory conventions. Without explicit discovery, agents
hallucinate function signatures, miss dependencies, and produce code that
compiles but doesn't integrate. This outcome gives agents ground truth.

Human developers face the same problem at smaller scale: understanding a
new codebase requires reading every file or trusting stale documentation.
Automated discovery provides answers in seconds, not hours.

Together, agent and human can query the same graph. The agent's understanding
is verifiable. The human's intuition is backed by data.
```

---

#### Rationale

3-5 paragraphs explaining the deeper reasoning. This section answers "why this approach?"

**Structure:**
1. **The problem** — What goes wrong without this outcome
2. **Failed approaches** — Why alternatives don't work
3. **The solution** — How this outcome addresses the root cause
4. **Downstream benefits** — What else becomes possible

**Tone:** Explanatory, not defensive. Assume the reader wants to understand, not be convinced.

---

#### Success Criteria

A numbered list of 3-8 measurable, testable criteria. Each criterion should be verifiable by code or test.

**Format:**

```markdown
## Success Criteria

The [system/command/graph/validator] must:

1. [Action] [measurable outcome] in [time/accuracy bound]
2. [Action] [measurable outcome] [specific detail]
3. [Continue for 3-8 items]
```

**Each criterion MUST:**
- Start with an action verb (`detect`, `report`, `validate`, `generate`)
- Include a measurable bound (time, count, percentage)
- Be independently verifiable

**Example:**

```markdown
## Success Criteria

The layer validator must:

1. Detect upward dependencies (layer N calling layer N+1) in <1 second
2. Report violating call sites with file:line precision
3. Suggest specific fixes (move function or add interface)
4. Fail validation if cycles exist at any layer
5. Pass validation if architecture is acyclic and downward-only
```

---

#### Specified By

Lists the specifications that deliver this outcome. Each spec gets a one-sentence description of its contribution.

**Format:**

```markdown
## Specified By

This outcome is delivered through:

- **S-XXX**: [One sentence describing this spec's contribution]
- **S-YYY**: [One sentence describing this spec's contribution]
```

**Do not:** Just list spec IDs without descriptions. The description explains the _why_ of each spec's presence.

---

#### Constitution Linkage

Explicit connection to JIG's constitutional purpose and themes.

**Format:**

```markdown
## Constitution Linkage

**Serves:** [One sentence: how this outcome advances JIG's purpose]

**Enables:** [One sentence: what becomes possible downstream]

**Without this:** [One sentence: what breaks for agents and humans]
```

---

## Part II: Formatting Guidelines

### Markdown Conventions

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

### Line Length

- Wrap prose at ~80 characters for readable diffs
- Do not hard-wrap within code blocks
- Do not hard-wrap table rows

### Whitespace

- One blank line between sections
- One blank line before and after code blocks
- No trailing whitespace
- No multiple consecutive blank lines

### Lists

- Use numbered lists only for ordered/sequential items
- Use bullets for unordered items
- Indent nested lists with 2 spaces
- End list items without periods unless they are complete sentences

### Code Blocks

- Always specify language: ` ```yaml `, ` ```markdown `
- Use inline backticks for short references: `jigy validate`
- Use fenced blocks for multi-line examples

---

## Part III: Voice and Content Guidance

### Evergreen Principle

Outcomes are **permanent documentation of system value**. They are NOT:
- Project goals ("achieve 90% test coverage")
- Work unit objectives ("add missing tests")
- Refactoring tasks ("reorganize code")
- Process improvements ("improve code organization")

**Test:** Remove all references to the work that created this outcome. Does it still make sense? If no, rewrite.

**Test:** Would a new developer in two years understand why this matters? If no, add context.

### Agent-First Framing

JIG exists to enable AI coding agents. Every outcome should explain:

1. **How agents use it** — What queries, commands, or data agents consume
2. **What agent failures it prevents** — Hallucination, invalid dependencies, stale context
3. **How humans benefit secondarily** — Developer productivity follows from agent correctness

❌ **Bad (human-first):**
> Developers can visualize the dependency graph to understand architecture.

✅ **Good (agent-first):**
> Agents query the dependency graph to validate proposed changes before generating code. Developers visualize the same data to review agent work.

### Value Over Activity

Describe **what exists** (value), not **what was done** (activity).

❌ **Bad (activity):**
> We added validation for brick definitions.

✅ **Good (value):**
> Brick definition validation catches format errors before graph generation.

### Concrete Over Abstract

Use specific examples, actual command names, real metrics.

❌ **Bad (abstract):**
> Validation is fast enough for development workflows.

✅ **Good (concrete):**
> `jigy validate` completes in <5 seconds for 10K LOC, enabling pre-commit hooks.

### Problem-Solution Structure

Every rationale section should follow this arc:

1. **What goes wrong** — Paint the pain clearly
2. **Why workarounds fail** — Show that obvious solutions don't work
3. **How this solves it** — Explain the mechanism, not just the claim
4. **What becomes possible** — Show downstream benefits

### Quantify Everything

Replace vague words with numbers:

| Vague | Quantified |
|-------|------------|
| fast | <5 seconds |
| most | 80%+ |
| many | 6+ items |
| quickly | in <1 second |
| reliable | 99%+ accuracy |
| small projects | <10K LOC |
| large projects | 100K+ LOC |

### Active Voice

Prefer active constructions that name the actor.

❌ **Bad (passive):**
> Errors are reported with line numbers.

✅ **Good (active):**
> The validator reports errors with file:line precision.

### Present Tense

Describe current system behavior, not future plans or past work.

❌ **Bad (future/past):**
> This will enable... / We added...

✅ **Good (present):**
> This enables... / The system detects...

---

## Part IV: Anti-Patterns

### Project Goals as Outcomes

❌ **Bad:**
```markdown
# Test Coverage
Critical paths have comprehensive tests.
```

This describes project state, not system value.

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

This describes code structure, not delivered value.

✅ **Good:**
```markdown
# Clear Architectural Boundaries
Authentication logic is isolated from business logic, enabling independent modification.

**Value:** Reduces time to implement auth changes without breaking other systems.
```

### Implementation Details as Outcomes

❌ **Bad:**
```markdown
# Decorator Support
Functions can be annotated with @jig.implements decorators.
```

This describes a mechanism, not value.

✅ **Good:**
```markdown
# Automated Code-to-Specification Traceability
Code-to-specification links are captured automatically from source annotations.

**Value:** Traceability is a byproduct of development, not a maintenance burden.
```

### Missing Agent Perspective

❌ **Bad:**
```markdown
## Why This Matters

Developers can visualize dependencies to understand the architecture.
```

✅ **Good:**
```markdown
## Why This Matters

Agents query the dependency graph to validate proposed changes match actual
architecture. Without this, agents generate code that compiles but violates
layering constraints, creating technical debt.

Developers visualize the same graph to review agent-proposed changes and
understand unfamiliar codebases.
```

---

## Part V: Complete Example

```markdown
---
id: O-013
title: Layer Architecture Enforcement
type: outcome
specifies: [S-027, S-028]
---

# Layer Architecture Enforcement

**Value:** Agents cannot introduce upward dependencies even when changes seem locally beneficial.

**Acceptance:** `jigy validate layers` detects all layer violations in <1 second with file:line precision.

## Why This Matters

AI agents optimizing for local correctness may introduce dependencies that
violate architectural boundaries. An agent adding a "helpful" import from
a feature module into a foundation module creates coupling that compounds
over time. Without enforcement, these violations are invisible until the
architecture is unmaintainable.

Human developers face the same temptation in reverse: taking a shortcut that
"works" but violates the intended structure. Layer enforcement makes the
cost of shortcuts immediate and visible.

The system benefits from consistent enforcement: build order is predictable,
foundation modules remain stable, and features can evolve independently.

## Rationale

Software architectures decay through accumulation of small violations. Each
individual upward dependency seems harmless—"just this once"—but the compound
effect creates circular dependencies, unclear build order, and modules that
cannot be modified independently.

Manual code review catches obvious violations but misses subtle ones. A
function call three levels deep may create an upward dependency that no
reviewer notices. The violation is discovered months later when a refactoring
breaks unexpectedly.

Layer enforcement automates what code review cannot: exhaustive checking of
every call site against declared layer constraints. The check runs in
milliseconds, making it practical to run on every save.

With enforcement in place, the architecture self-documents. The layer
definitions declare intent; the validator proves compliance.

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

- **S-027**: Layer constraint validation — Checks every call site against declared layers
- **S-028**: Layer violation reporting — Formats violations with actionable detail

## Constitution Linkage

**Serves:** Prevents architectural decay by making layer violations immediately visible.

**Enables:** Confident refactoring—developers and agents know the architecture is consistent.

**Without this:** Agents introduce coupling that compounds until architecture is unmaintainable.
```

---

## Part VI: Checklist

Before committing an outcome, verify:

### Structure
- [ ] Frontmatter has `id`, `title`, `type`, `specifies`
- [ ] H1 title matches frontmatter `title` exactly
- [ ] Title is a noun phrase (not imperative)
- [ ] Value statement is one sentence with clear benefit
- [ ] Acceptance has a measurable criterion
- [ ] "Why This Matters" leads with agent perspective
- [ ] Rationale has 3-5 paragraphs with problem→solution arc
- [ ] Success Criteria has 3-8 numbered, measurable items
- [ ] "Specified By" has descriptions, not just IDs
- [ ] Constitution Linkage references purpose and consequences

### Content
- [ ] Describes evergreen value, not project state
- [ ] Would make sense to new developer in 2 years
- [ ] All claims are quantified (no "fast" without "<Xs")
- [ ] Agent benefit is explicit, not implied
- [ ] No implementation details or file paths in value statement

### Format
- [ ] Prose wrapped at ~80 characters
- [ ] Code/commands in backticks
- [ ] One blank line between sections
- [ ] No trailing whitespace
- [ ] Active voice, present tense

---

## References

- [Constitution v2](../../jig/Constitution_v2.md) — The governing document this format serves
- [Evergreen Intent Guidance](../../agents/contextEvergreenIntent.md) — Principles for O and S nodes
- [Outcome Audit Report](./B019_AUDIT_outcomes-2025-12-13.md) — Analysis that informed this specification
