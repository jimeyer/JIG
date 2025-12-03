# Guide: Delivering Context to AI Agents

**Purpose**: Best practices for providing background knowledge that enables effective work. This differs from task documents (which define what to do) - context documents establish how a system works so the agent can apply that knowledge across many tasks.

---

## Context vs. Task Documents

| Aspect | Task Document | Context Document |
|--------|---------------|------------------|
| Purpose | Define what to do | Enable doing anything |
| Scope | Single objective | Ongoing reference |
| Lifespan | One session | Many sessions |
| Tone | Imperative ("do X") | Declarative ("X works like...") |
| Structure | Steps to completion | Reference material |
| Success | Task completed | Agent makes correct decisions |

**Example**:
- Task: "Add a new specification for token expiration"
- Context: "How JIG specifications work, their format, and what makes a good one"

---

## Core Principles

### 1. Optimize for Repeated Use

Context documents are read many times. Every word costs tokens on every use.

**Do**:
- Front-load essential information
- Use terse, precise language
- Eliminate redundancy ruthlessly
- Prefer tables over prose for structured data

**Don't**:
- Include motivational text ("This is important because...")
- Repeat the same concept in different sections
- Add historical context unless it affects current behavior

### 2. Enable, Don't Prescribe

Context teaches the agent how the system works. The agent decides how to apply that knowledge.

**Do**:
- Explain the model (what exists, how it connects)
- State constraints (what must/must not happen)
- Provide examples of valid artifacts
- List common mistakes to avoid

**Don't**:
- Step-by-step instructions for specific tasks
- "If the user asks X, do Y" decision trees
- Workflow sequences (those belong in task docs)

### 3. Tier Information by Necessity

Not all information is equally important. Structure reflects priority.

**Tier 1 - Mental Model** (Always read):
- Core concepts the agent cannot function without
- 10-20% of the document

**Tier 2 - Reference Material** (Consulted as needed):
- Formats, conventions, rules
- 50-60% of the document

**Tier 3 - Edge Cases** (Rarely needed):
- Anti-patterns, pitfalls, exceptions
- 20-30% of the document

### 4. Make It Scannable

Agents (and humans) scan before reading. Visual structure matters.

**Do**:
- Use headers that describe content, not clever titles
- Use bullet lists for unordered items
- Use numbered lists only for sequences
- Use tables for structured data
- Use code blocks for exact syntax

**Don't**:
- Dense paragraphs
- Headers like "Important Notes" (what notes?)
- Nested lists beyond 2 levels

---

## Structure Template

```markdown
# [System] Context for AI Agents

## What [System] Does
[1-2 paragraphs: the mental model. What problem does it solve? What are the core concepts?]

## Key Concepts
[Define terms the agent will encounter. Keep definitions to 1-2 sentences each.]

### [Concept 1]
[Definition and essential behavior]

### [Concept 2]
[Definition and essential behavior]

## Artifacts
[What files/structures the agent will read and write]

### [Artifact Type 1]
- **Location**: [path pattern]
- **Format**: [structure]
- **Example**:
```
[minimal valid example]
```

## Conventions
[Tables of IDs, naming, formats]

## Rules & Constraints
[Bullet list of MUST/MUST NOT]

## Anti-patterns
[Common mistakes with brief explanation of why they're wrong]

## Quick Reference
[Optional: Cheat sheet for very common operations]
```

---

## Writing Guidelines

### Be Precise, Not Comprehensive

**Bad**: "Specifications describe what the system should do."
**Good**: "Specifications are markdown files in `jig/specifications/S-{number}.md` with YAML frontmatter containing `id` and `type: specification`."

The first requires interpretation. The second is actionable.

### Show, Don't Just Tell

**Bad**: "Brick IDs use kebab-case."
**Good**:
```
Brick IDs: B-{kebab-case}
Examples: B-auth-session, B-core-utils, B-rest-api
Invalid: B-001, B-AuthSession, B_auth
```

### State Constraints Explicitly

**Bad**: "Layer assignments should be reasonable."
**Good**: "Brick at layer N may only depend on bricks at layers 0..(N-1)."

### Include Negative Examples

When anti-patterns are common, show them:

```markdown
## Anti-patterns

**Refactoring tasks as specifications**:
- BAD: "Relocate era_persistence.py to protocol-core"
- GOOD: "EraLamportClock state persists across process restarts"

The first describes a file move. The second describes behavior.
```

---

## Token Efficiency Techniques

### 1. Use Tables for Structured Data

**Inefficient** (87 tokens):
> Specification IDs use the format S followed by a hyphen and then a number, like S-001 or S-042. Outcome IDs use O followed by a hyphen and a number. Brick IDs use B followed by a hyphen and a kebab-case name.

**Efficient** (40 tokens):
| Type | Format | Example |
|------|--------|---------|
| Spec | S-{number} | S-001 |
| Outcome | O-{number} | O-001 |
| Brick | B-{kebab-case} | B-auth |

### 2. Eliminate Redundant Framing

**Inefficient**: "It's important to note that you should always..."
**Efficient**: "Always..."

**Inefficient**: "In order to ensure proper operation..."
**Efficient**: [Just state the rule]

### 3. One Example, Not Three

If one example demonstrates the concept, additional examples waste tokens. Add more only when they show meaningfully different cases.

### 4. Code Blocks Over Prose

**Inefficient**: "The frontmatter should contain an id field with the specification ID and a type field with the value specification."

**Efficient**:
```yaml
---
id: S-001
type: specification
---
```

---

## Testing Your Context Document

### Completeness Test
Give an agent ONLY your context document. Ask it to:
1. Create a valid artifact from scratch
2. Identify what's wrong with an invalid artifact
3. Answer "when should I use X vs Y?"

If it fails or asks clarifying questions, the context is incomplete.

### Conciseness Test
Read every sentence. Ask: "If I remove this, will the agent make wrong decisions?"
- If yes: keep it
- If no: remove it
- If maybe: move to a lower tier or edge cases section

### Scanability Test
Skim the document for 10 seconds. Can you:
- Find the file format for X?
- Find the ID convention for Y?
- Find what not to do for Z?

If no, restructure with better headers and visual organization.

### Token Budget Test
Your context document competes with the actual work for context window space. Target sizes:
- Simple system: 500-800 words (~2KB)
- Moderate system: 800-1200 words (~4KB)
- Complex system: 1200-2000 words (~6KB)

Beyond 2000 words, consider splitting into multiple focused documents.

---

## Common Mistakes

### The Textbook Trap
Writing a complete tutorial instead of a reference. Agents don't need to "learn" - they need to "apply."

### The Changelog Trap
Including historical context ("Previously we did X, but now..."). Agents only need current state.

### The Edge Case Rabbit Hole
Exhaustively documenting every exception. Most sessions won't encounter them. Keep edge cases brief or omit entirely.

### The Implicit Knowledge Trap
Assuming the agent knows domain terms, conventions, or context from previous sessions. Each session starts fresh.

### The Over-Abstraction Trap
Describing the system philosophically instead of concretely. "JIG measures alignment" means nothing without explaining what alignment means and how it's measured.

---

## Summary

A good context document:

1. **Fits the budget** - Concise enough to leave room for work
2. **Enables action** - Agent can create valid artifacts immediately
3. **Prevents mistakes** - Common anti-patterns are called out
4. **Scans quickly** - Information is findable at a glance
5. **Stays evergreen** - No task-specific or temporal content

**The test**: An agent with only your context document should make the same decisions as an expert who knows the system deeply.
