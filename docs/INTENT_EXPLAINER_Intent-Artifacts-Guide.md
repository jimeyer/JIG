---
title: "JIG Intent Artifacts Guide"
type: exploration
status: active
created: 1767412904
created_human: "2026-01-02 22:01 CST"
parent: "[[C003_SCOPE_Extended-Intent-Hierarchy-and-Towers]]"
children: []
---
# JIG Intent Artifacts Guide

**For developers new to JIG who need to understand the intent graph.**

---

## The Problem JIG Solves

Software systems drift. What we intended to build diverges from what we actually built. What tests verify diverges from what we specified. And tomorrow, no one remembers why any of it exists.

This drift is invisible until catastrophic. A function changes behavior but no test fails—because the test never verified that behavior. A specification gets outdated but no one notices—because nothing links it to code. A new developer joins and asks "why does this exist?" and no one can answer—because the context lived only in someone's head.

**JIG makes alignment explicit, measurable, and enforceable.**

It does this by connecting three things that usually exist in isolation:
- **Intent** (what we meant to build)
- **Implementation** (what we actually built)
- **Verification** (what we actually test)

When these three are connected, you can answer questions like:
- "Is this specification implemented?"
- "Is this specification tested?"
- "Why does this code exist?"
- "What breaks if I change this?"

---

## The Intent Graph: Quick Reference

```
                      CHARTER
                   (defines Goals)
                    /          \
                   /            \
          ARCHITECTURE         OUTCOMES
             A-###               O-###
         supports_goals      supports_goals
         constrains ──┐    ┌── specifies
                      │    │
                      ▼    ▼
                  SPECIFICATIONS
                       S-###
                     /      \
                    /        \
               verifies   implements
                  /            \
                 /              \
             TESTS              CODE
              T-###              C-###
```

### Artifact Summary

| Artifact | ID Format | Question Answered | Points To |
|----------|-----------|-------------------|-----------|
| **Charter** | `Charter` | Why does this project exist? | Goals |
| **Goal** | `G-#` | What problem are we solving? | (defined in Charter) |
| **Architecture** | `A-###` | What contracts must code honor? | Goals, Specs |
| **Outcome** | `O-###` | What value do users get? | Goals, Specs |
| **Specification** | `S-###` | What behavior must exist? | (referenced by A/O) |
| **Code** | `C-{path}` | How is it implemented? | Specs |
| **Test** | `T-{path}` | How is it verified? | Specs |

### Relationship Summary

| Relationship                  | Direction | Meaning                                      |
| ----------------------------- | --------- | -------------------------------------------- |
| Charter `defines_goals`       | down      | Charter declares which goals exist           |
| Goal                          | (none)    | Goals are leaf nodes; referenced by A/O      |
| Architecture `supports_goals` | up        | This contract serves these goals             |
| Architecture `constrains`     | down      | These specs must honor this contract         |
| Outcome `supports_goals`      | up        | This value serves these goals                |
| Outcome `specifies`           | down      | These specs deliver this value               |
| Specification                 | (none)    | Specs are leaf nodes; referenced by Code/Test |
| Code `implements`             | up        | This code implements this spec               |
| Test `verifies`               | up        | This test verifies this spec                 |

### The Core Insight

**Architecture and Outcomes are orthogonal.** They both feed into Specifications, but from different angles:
- **Architecture** says: "These specs must honor this structural contract"
- **Outcomes** says: "These specs must deliver this user value"

They meet at Specifications. There's no direct link between them.

---

## Charter: The Root of Everything

### What It Is

The Charter is the single root document that defines why your project exists. It contains Goals—the fundamental problems you're solving.

### Why It Exists

Without a Charter, outcomes and architecture float unanchored. Teams build features that don't serve any goal. Developers optimize code without knowing why it matters. The Charter is the anchor that keeps everything aligned.

### Format

```yaml
---
id: Charter
type: charter
defines_goals: [G-1, G-2, G-3]
---
```

Goals are defined in the markdown body:

```markdown
## Charter Goals

### G-1: Solve the Alignment Problem
We cannot measure whether code implements what we intended...

### G-2: Enforce Architectural Boundaries
Without explicit boundaries, circular dependencies accumulate...

### G-3: Preserve Context Across Sessions
Context is lost between sessions...
```

### Example

A bike software project might have:
- **G-1:** Discover correct design intent
- **G-2:** Model system behavior
- **G-3:** Enable cross-platform compliance testing

Every Architecture and Outcome must support at least one of these goals. If you can't link your work to a goal, question whether it belongs.

### Common Mistakes

- **Too many goals.** 3-7 is ideal. More than 10 means you haven't prioritized.
- **Goals that are actually features.** "Support dark mode" is a feature, not a goal. "Accessible user experience" is a goal.
- **Goals without clear success criteria.** If you can't tell when a goal is achieved, it's not actionable.

---

## Architecture: The Structural Contracts

### What It Is

An Architecture document is a **contract** that defines how parts of the system relate to each other. It's not just a list of rules—it's a holistic agreement that multiple parties (components, modules, teams) must conform to.

Think of it like an API contract: it defines the interface, the invariants, and the expectations. Both the provider and consumer must honor it.

### Why It Exists

Code without architectural contracts drifts toward chaos. Circular dependencies accumulate. Foundation code starts depending on features. Interfaces become inconsistent. Architecture documents make the contracts explicit so violations are detectable.

### The Key Question

> "What contracts must code honor to maintain system integrity?"

### Format

```yaml
---
id: A-001
type: architecture
title: Device Logic Contract
status: active
supports_goals: [G-1, G-3]
constrains: [S-116, S-117, S-118]
---
```

### What Goes In An Architecture Contract

- **Interface definitions** (what methods exist, what they accept/return)
- **Invariants** (properties that must always be true)
- **Dependency rules** (what can import what)
- **Design patterns** (functional core/imperative shell, etc.)
- **Naming conventions** (prefixes, case styles)
- **Anti-patterns** (what NOT to do)
- **Parties to the contract** (who/what must conform)

### Example

**A-003: Protocol Layering** might define:
- Five protocol layers (L1 through L5)
- Naming convention: all Layer 3 constructs use `L3_` prefix
- Invariant: Layer N can only depend on layers below it
- Anti-pattern: Never pass L3_PDU directly to application handlers

This architecture contract constrains specs like S-001 (L3_PDU structure), S-002 (L4_Message structure), etc. Those specs define the exact fields and validation rules; the architecture contract defines the overall structure, the parties involved, and the principles they must follow.

### Architecture Contract vs Specification

| Architecture Contract | Specification |
|-----------------------|---------------|
| Holistic agreement between parties | Single testable requirement |
| Coarse-grained (one per boundary) | Fine-grained (one per requirement) |
| Interface + invariants + rationale | Behaviors + validation rules + edge cases |
| "There are 5 layers; all parties use L3_ prefix" | "L3_sequence must be monotonically increasing" |
| Read first to understand the system | Implement against for correctness |

### Common Mistakes

- **Contract without constrained specs.** If an architecture doesn't constrain any specs, it's just documentation—not an enforceable contract.
- **Too detailed.** Contracts define WHAT the agreement is, not HOW to implement it. Leave implementation details to specs.
- **No parties identified.** A good contract makes clear who must conform (e.g., "Server and Device Logic both honor this interface").
- **No design rationale.** Good contracts explain WHY these terms exist, not just what they are.

---

## Outcomes: The Value Delivered

### What It Is

An Outcome describes value delivered to users or developers. It's a capability statement with acceptance criteria.

### Why It Exists

Specifications without outcomes are technical requirements disconnected from purpose. Outcomes answer "why does this matter?" and make the value explicit. When prioritizing work, outcomes tell you what's important.

### The Key Question

> "What value do users or developers get from this capability?"

### Format

```yaml
---
id: O-003
type: outcome
title: Distributed State Convergence
supports_goals: [G-2, G-3]
specifies: [S-005, S-006, S-007, S-009, S-010]
---
```

### What Goes In An Outcome Document

- **Value statement** (one sentence: what users get)
- **Acceptance criteria** (measurable success condition)
- **Rationale** (why this matters, what problem it solves)
- **Success criteria** (specific testable conditions)
- **Specified by** (links to specs that deliver this outcome)

### Example

**O-003: Distributed State Convergence**

> **Value:** Users experience consistent bike configuration across all gateways without confusion from network issues or concurrent updates.
>
> **Acceptance:** All gateways converge to identical BikeState within 1 second of network partition recovery.

This outcome specifies S-005 (OR-Map for device membership), S-006 (staleness-based presence detection), etc. Each spec is a technical requirement that contributes to delivering this user value.

### Outcome vs Specification

| Outcome | Specification |
|---------|---------------|
| User value | Technical requirement |
| "Users experience consistent state" | "CRDT merge uses LWW semantics" |
| Why we build | What we build |
| Acceptance criteria | Validation rules |

### Common Mistakes

- **Outcomes that are really specs.** "Use LWW-Register for bike_name" is a spec, not an outcome. "Users see consistent bike names" is an outcome.
- **No acceptance criteria.** "Better performance" is not measurable. "<2 second sync time" is.
- **Too many specs per outcome.** If an outcome specifies 30 specs, consider splitting it into multiple outcomes.

---

## Specifications: The Testable Requirements

### What It Is

A Specification is a single testable requirement. It's the atomic unit of the intent graph—the thing that code implements and tests verify.

### Why It Exists

Specifications are the bridge between intent and implementation. They're precise enough to test against, but abstract enough to allow implementation flexibility. They're what code claims to implement and what tests claim to verify.

### The Key Question

> "What specific behavior must exist, and how do we know it's correct?"

### Format

```yaml
---
id: S-007
type: specification
title: LWW-Register Merge Uses Timestamp Comparison
status: active
---
```

### What Goes In A Specification

- **Constraints** (what must be true)
- **Edge cases** (what happens in unusual situations)
- **Validation rules** (how to check correctness)
- **Rationale** (why this behavior, not some other)

### Example

**S-007: LWW-Register Merge Uses Timestamp Comparison**

```markdown
## Constraints

1. When merging two LWW-Register values, the value with the higher timestamp wins
2. Timestamps are compared lexicographically: (era, lamport, actor_id)
3. If timestamps are equal, the value is unchanged (stable sort)

## Edge Cases

- Merging with self returns unchanged register
- Merging with older timestamp returns unchanged register
- Merging with newer timestamp returns new register with new value and timestamp
```

### Specification Granularity

A specification should be:
- **Small enough** to implement in one function (usually)
- **Large enough** to be meaningful on its own
- **Testable** with a clear pass/fail condition

Too small: "Function accepts a string parameter"
Too large: "The entire CRDT subsystem works correctly"
Just right: "LWW-Register merge uses timestamp comparison"

### Common Mistakes

- **Specs without implementation links.** An unimplemented spec is a gap in your system.
- **Specs without test links.** An untested spec is unverified.
- **Vague specs.** "Handle errors appropriately" is not testable. "Return ErrorResult with error code and message" is.

---

## Code and Tests: The Implementation Layer

### Linking Code to Specs

Use the `@jig` decorator or comment annotation to link code to specifications:

```python
# @jig C-ase.crdt.lww.LWWRegister.merge implements:S-007
def merge(self, other: 'LWWRegister[T]') -> 'LWWRegister[T]':
    """Merge two registers, keeping the value with the higher timestamp."""
    if other.timestamp > self.timestamp:
        return LWWRegister(other.value, other.timestamp)
    return self
```

The format is:
```
# @jig C-{fully.qualified.path} implements:S-###
```

### Linking Tests to Specs

```python
# @jig T-test_lww.test_merge_higher_timestamp_wins verifies:S-007
def test_merge_higher_timestamp_wins():
    """Verify that merge keeps the value with the higher timestamp."""
    old = LWWRegister("old", Timestamp(1, 10, "a"))
    new = LWWRegister("new", Timestamp(1, 20, "b"))

    result = old.merge(new)

    assert result.value == "new"
    assert result.timestamp == new.timestamp
```

### Multiple Specs

A function can implement multiple specs:
```python
# @jig C-ase.crdt.lww.LWWRegister.merge implements:S-007,S-008
```

A test can verify multiple specs:
```python
# @jig T-test_lww.test_merge_complete verifies:S-007,S-008,S-009
```

### The S-F-T Triangle

The goal is a complete triangle for every specification:

```
         S-007
        /     \
    implements  verifies
      /           \
   merge()    test_merge()
       \         /
        \       /
         covers
```

**Perfect alignment** means:
1. The spec (S-007) is implemented by code (`merge()`)
2. The spec is verified by a test (`test_merge()`)
3. The test actually executes the implementing code

JIG can detect broken triangles:
- Spec with no implementing code (gap)
- Spec with no verifying test (unverified)
- Test that doesn't execute the implementing code (testing theater)

### Common Mistakes

- **Forgetting annotations.** Code without `@jig` is invisible to alignment measurement.
- **Wrong path in annotation.** The path must match the actual fully-qualified name.
- **Tests that don't exercise implementation.** A test can claim to verify S-007 but not actually call `merge()`. Coverage analysis catches this.

---

## Patterns

### Start With Outcomes

Don't start by writing specs. Start by asking: "What value are we delivering?"

1. Write the Outcome first (what users get)
2. Derive the Specifications (what behaviors are needed)
3. Check if Architecture constraints apply
4. Implement and test

This ensures everything traces to value.

### One Spec Per Testable Requirement

If you can write one test that covers it, it's one spec. If you need multiple independent tests, consider multiple specs.

### Contract Before Implementation

Write Architecture contracts before implementing new subsystems. This forces you to think through:
- Who are the parties to this contract?
- What are the interfaces between them?
- What invariants must all parties honor?

It's much cheaper to negotiate a contract than to refactor code after the fact.

### Every Spec Has a Complete Triangle

Before considering a spec "done," verify:
- [ ] At least one function implements it
- [ ] At least one test verifies it
- [ ] The test actually executes the implementing code

### Use Goals to Prioritize

When choosing what to build, ask: "Which goal does this support?" Work that doesn't support any goal should be questioned.

---

## Antipatterns

### Orphaned Specs

A specification that isn't specified by any Outcome or constrained by any Architecture.

**Symptom:** S-042 exists but no O-### specifies it and no A-### constrains it.

**Problem:** Why does this spec exist? What value does it deliver? It's disconnected from intent.

**Fix:** Either link it to an Outcome/Architecture or delete it.

### Orphaned Code

Code without `@jig` annotations.

**Symptom:** `merge()` implements something, but there's no `implements:S-###`.

**Problem:** This code is invisible to alignment measurement. We can't tell if it's tested or what it's for.

**Fix:** Add annotations linking to specs.

### Testing Theater

Tests that claim to verify specs but don't actually test the implementation.

**Symptom:** `test_merge verifies:S-007` but never calls `merge()`.

**Problem:** The spec appears verified but isn't. False confidence.

**Fix:** Coverage analysis reveals this. Rewrite the test to actually exercise the implementation.

### Contract Violation

Architecture contracts that describe an ideal structure that code doesn't follow.

**Symptom:** A-001 says "Layer N can only depend on layers below it" but code violates this.

**Problem:** The contract is aspirational, not honored. Parties are not conforming.

**Fix:** Either fix the code to honor the contract, or renegotiate the contract to reflect reality. A contract that isn't enforced isn't a contract.

### Outcome Inflation

Outcomes that specify too many specs, becoming meaningless umbrellas.

**Symptom:** O-001 specifies 40 specs covering unrelated functionality.

**Problem:** The outcome is too broad to be useful for prioritization or understanding.

**Fix:** Split into focused outcomes that each deliver a coherent piece of value.

### Spec Explosion

Too many tiny specs that don't provide meaningful abstraction.

**Symptom:** S-042: "Function accepts string" S-043: "Function returns int" S-044: "Function doesn't throw"

**Problem:** Specs should be meaningful requirements, not line-by-line descriptions.

**Fix:** Combine into meaningful behavioral requirements.

---

## Quick Reference: Writing Each Artifact

### Charter Checklist
- [ ] Single file at `jig/Charter.md`
- [ ] `defines_goals` lists all goal IDs
- [ ] Each goal has `### G-#: Title` header in body
- [ ] 3-7 goals (not too many)
- [ ] Goals are problems to solve, not features to build

### Architecture Contract Checklist
- [ ] File at `jig/architecture/A-###.md`
- [ ] `supports_goals` is non-empty
- [ ] `constrains` lists specs this contract governs
- [ ] Identifies parties to the contract (who must conform)
- [ ] Contains interface/invariants, not implementation details
- [ ] Includes rationale for why this contract exists

### Outcome Checklist
- [ ] File at `jig/outcomes/O-###.md`
- [ ] `supports_goals` is non-empty
- [ ] `specifies` lists specs that deliver this value
- [ ] Has clear value statement (what users get)
- [ ] Has measurable acceptance criteria

### Specification Checklist
- [ ] File at `jig/specifications/S-###.md`
- [ ] `status` is one of: draft, proposed, active, deprecated
- [ ] Referenced by at least one Outcome or Architecture
- [ ] Has testable constraints
- [ ] Has at least one implementing function
- [ ] Has at least one verifying test

### Code Annotation Checklist
- [ ] `# @jig C-{path} implements:S-###`
- [ ] Path matches fully-qualified function/method name
- [ ] Referenced spec exists

### Test Annotation Checklist
- [ ] `# @jig T-{path} verifies:S-###`
- [ ] Path matches test function name
- [ ] Referenced spec exists
- [ ] Test actually exercises implementing code

---

## Glossary

| Term | Definition |
|------|------------|
| **Intent Graph** | The graph of Charter, Goals, Architecture, Outcomes, and Specifications |
| **Implementation Graph** | The graph of modules, classes, functions, and their relationships |
| **Verification Graph** | The graph of tests, what they verify, and what they cover |
| **Alignment** | The state where intent, implementation, and verification are connected |
| **S-F-T Triangle** | Specification-Function-Test relationship that forms complete alignment |
| **Architecture Contract** | A holistic agreement defining how system parts relate; multiple parties must conform |
| **Orphan** | An artifact with no connections (orphaned spec, orphaned code) |
| **Drift** | When implementation diverges from intent over time |

---

## Further Reading

- **JIG Core Artifacts Contract** (C001) — Formal specification of all artifact types
- **Charter** — Your project's root intent document
- **Architecture Contracts** — Structural contracts for your specific system
- **Outcomes** — Value delivered by your specific system

---

*This document is part of the JIG documentation. For the authoritative specification of artifact formats, see the JIG Core Artifacts Contract.*
