---
title: Constitution
version: 2
date: 2025-12-22
---

# JIG Constitution

_The governing contract for AI-augmented software development._

---

## Why JIG Exists

Software systems drift. Intent diverges from implementation. Implementation diverges from verification. Without measurement, this drift is invisible until catastrophic.

JIG exists to make alignment **explicit**, **measurable**, and **enforceable**.

We commit to solving three fundamental problems:

**1. The Alignment Problem**
We cannot measure whether code implements what we intended, or whether tests verify what we specified. JIG provides this measurement through the S-F-T alignment graph.

**2. The Architecture Problem**
Without explicit boundaries, circular dependencies accumulate. Foundation code depends on features. Architectural decay is invisible until catastrophic. JIG enforces boundaries through bricks and layers.

**3. The Continuity Problem**
Context is lost between sessions. The next developer (or AI agent) starts from scratch, unaware of decisions already made. JIG persists machine-readable context that survives session boundaries.

---

## The Constitution Hierarchy

This document is the root of JIG's intent graph. Every artifact traces upward to this purpose:

```
Constitution (this document)
    ↓
Outcomes (what JIG delivers)
    ↓
Specifications (testable requirements)
    ↓
Tests (verification)
    ↓
Functions (implementation)
```

Breaks in this chain indicate misalignment. If an outcome cannot trace to this purpose, it is orphaned. If a specification cannot trace to an outcome, it is adrift. JIG makes these gaps visible.

---

## Part I: The Alignment Graph

JIG's core commitment is the **S-F-T alignment triangle**: Specifications, Functions, and Tests connected by measurable relationships.

```
         S (Specification)
        ╱   ╲
       ╱     ╲
implements  verifies
     ╱         ╲
    F ─covers──► T
```

**Perfect alignment** exists when:
- A specification (S) is implemented by a function (F)
- The specification is verified by a test (T)
- The test actually executes the function

JIG makes this triangle **discoverable**, **traceable**, and **verifiable**.

### Discovering Implementation

Before we can measure alignment, we must know what exists.

**[O-001: Implementation Structure is Discoverable](outcomes/O-001.md)**
JIG extracts actual code structure automatically. Developers query what exists rather than guessing. `jigy impl rebuild` generates a complete implementation graph in <2 seconds for 10K LOC. No manual documentation required.

**[O-002: Code-to-Specification Traceability is Automated](outcomes/O-002.md)**
Decorators (`@jig.implements`, `@jig.verifies`) create explicit links from code to specifications. These links appear in the graph automatically. Traceability is a byproduct of development, not a separate maintenance burden.

**[O-003: Multi-Language Support](outcomes/O-003.md)**
The alignment graph works across Python, TypeScript, Java, Go—any language with a JIG analyzer. One graph representation for polyglot codebases. Adding a new language requires only implementing the `LanguageAnalyzer` interface.

### Connecting Intent to Code

The alignment graph connects human intent (specifications) to machine reality (functions and tests).

**[O-009: Intent Graph Generation](outcomes/O-009.md)**
JIG generates a complete intent graph from specifications, outcomes, and brick definitions. Human-authored markdown becomes machine-queryable nodes. The gap between documentation and code closes.

**[O-018: Test-to-Specification Traceability](outcomes/O-018.md)**
Tests that verify specifications are discoverable and queryable. "Which specs have no verifying tests?" becomes a graph query with a precise answer. The T→S edge of the alignment triangle is explicit.

### Closing the Triangle

The alignment triangle is incomplete without objective evidence that tests execute implementations.

**[O-021: Verifiable Test-to-Implementation Coverage](outcomes/O-021.md)**
Tests that claim to verify specifications demonstrably execute the implementing code. Coverage analysis provides the T→F edge—objective, execution-based evidence. This detects "testing theater": tests that pass without validating behavior.

---

## Part II: Architectural Boundaries

Alignment at scale requires structure. JIG partitions the function space into **bricks** and stratifies bricks into **layers**.

### Bricks: Spatial Partitioning

A brick is a named partition of the function space:
- Every function belongs to exactly one brick
- Bricks are disjoint (no overlap)
- Bricks cover all functions (no gaps)

Bricks enable scoped queries ("Is B-auth aligned?"), visible dependencies ("B-auth depends on B-core"), and boundary enforcement ("B-auth cannot call private functions in B-users").

**[O-012: Brick Definition Compliance](outcomes/O-012.md)**
Brick definitions comply with A001 format requirements. `jigy validate bricks` detects ID format violations, missing layer fields, and invalid values in <1 second. Malformed bricks fail fast.

### Layers: Vertical Stratification

Each brick has a layer (0, 1, 2, ...). The layer constraint:
- A brick at layer N may depend only on layers 0..(N-1)
- Layer 0 bricks may depend on each other (no cycles)
- Circular dependencies are rejected at all layers

Layers prevent architectural decay: foundation code cannot depend on features, upward dependencies are blocked, build order is clear.

**[O-013: Layer Enforcement](outcomes/O-013.md)**
Architectural violations are detected automatically. Upward dependencies, circular dependencies—JIG catches them before they degrade system structure. Function-level detail shows exactly which calls violate constraints.

**[O-014: Layer Visibility](outcomes/O-014.md)**
`jigy layers` displays the current layer structure. `jigy layers suggest` recommends assignments based on actual dependencies. Architecture is visible, not inferred from reading code.

---

## Part III: Validation

JIG catches errors early, provides actionable feedback, and validates fast enough for continuous use.

### Early Detection

**[O-004: Early Error Detection](outcomes/O-004.md)**
Validation errors surface before graph generation, not as cryptic runtime failures. Developers discover problems at the point of introduction, not hours later in CI.

**[O-005: Actionable Error Messages](outcomes/O-005.md)**
Error messages include file paths, line numbers, and specific remediation steps. Developers resolve 80%+ of validation issues from the error message alone. AI agents can self-correct without human intervention.

### Fast Feedback

**[O-006: Fast Validation](outcomes/O-006.md)**
Full project validation completes in <5 seconds. This speed enables pre-commit hooks, watch mode workflows, and CI integration without friction. Slow validation is ignored; fast validation is used.

### Complete Coverage

**[O-015: Intent Graph Completeness](outcomes/O-015.md)**
JIG detects orphaned outcomes (not linked to specifications) and orphaned specifications (not linked to outcomes). Incomplete intent definitions surface before they cause confusion. `jigy validate intent` detects orphans in <1 second.

---

## Part IV: Continuity

JIG maintains context across sessions, enabling developers and AI agents to pick up where they left off.

### Integration

**[O-016: CI and Tooling Integration](outcomes/O-016.md)**
Validation integrates with CI pipelines and editor tooling via machine-parseable output. `jigy validate --format json` produces structured output that CI systems and editors consume programmatically. JIG fits into existing workflows.

### Change Detection

**[O-017: Artifact Change Detection](outcomes/O-017.md)**
JIG detects when specifications, implementations, or tests change. This enables drift detection: has intent changed? Has implementation changed? Are they still aligned? Changes are tracked, not lost.

### Current Data

**[O-022: Commands Operate on Current Data](outcomes/O-022.md)**
JIG commands operate on up-to-date graph data without requiring manual rebuild invocation. Stale graphs lead to false confidence; JIG automatically rebuilds when needed. When nothing changed, staleness check completes in <200ms.

---

## Part V: Developer Experience

JIG must be usable to be used. We commit to intuitive interaction and flexible adoption.

**[O-019: Intuitive CLI](outcomes/O-019.md)**
Users interact with JIG through a memorable, verb-first command structure. `jigy validate`, `jigy layers`, `jigy align`—commands that read like English. Zero configuration required to start.

**[O-020: Configurable Project Structure](outcomes/O-020.md)**
JIG adapts to diverse project layouts. Existing projects adopt JIG without reorganizing code. Non-standard directory structures are configurable, not forbidden.

---

## For AI Agents

If you are an AI agent working on this codebase, these are your obligations:

### Before Writing Code

1. **Query the graph.** Run `jigy show` or read `jig/generated/*.ndjson` to understand what exists. Do not claim functions exist without evidence.

2. **Read the specification.** Before modifying any function with `@jig.implements("S-XXX")`, read the specification file. Understand WHY before changing HOW.

3. **Check the layer.** Know which brick you're working in and which layer it occupies. You may only depend on lower layers.

### While Writing Code

4. **Link your work.** Add `@jig.implements("S-XXX")` to functions that implement specifications. Add `@jig.verifies("S-XXX")` to tests that verify them. Unlinked code is invisible to alignment measurement.

5. **Respect boundaries.** Do not call private functions across brick boundaries. Do not introduce upward dependencies.

### Before Committing

6. **Validate.** Run `jigy validate`. If it fails, you have violated constraints. Fix them before proceeding.

7. **Check alignment.** Run `jigy align` to verify the S-F-T triangle is complete for specifications you touched. Incomplete triangles indicate unfinished work.

### Always

8. **Persist what you learn.** When you discover system structure or make architectural decisions, that knowledge belongs in specifications or outcomes—not just session memory.

**JIG exists because you exist. Use it.**

---

## Maintenance

This Constitution is the foundation of JIG's intent hierarchy. It is maintained according to these rules:

**Adding Outcomes**
When a new outcome is created, it MUST be added to this document in the appropriate section. An outcome not listed here is orphaned.

**Removing Outcomes**
When an outcome is deprecated, it MUST be removed from this document. Dead links indicate decay.

**Changing Purpose**
If the fundamental purpose of JIG changes, a new Constitution version MUST be created and all outcomes re-evaluated for alignment.

**Version History**
- v1.0 (2025-12-13): Initial constitution
- v2.0 (2025-12-22): Restructured to follow Manifesto narrative; outcomes organized by logical flow

---

## Summary

JIG delivers **18 measurable outcomes** organized into five commitments:

| Commitment | Outcomes | What We Deliver |
|------------|----------|-----------------|
| **Alignment Graph** | O-001, O-002, O-003, O-009, O-018, O-021 | Discoverable structure, automated traceability, complete S-F-T triangle |
| **Architecture** | O-012, O-013, O-014 | Validated bricks, enforced layers, visible structure |
| **Validation** | O-004, O-005, O-006, O-015 | Early detection, actionable errors, fast feedback, completeness |
| **Continuity** | O-016, O-017, O-022 | CI integration, change detection, current data |
| **Experience** | O-019, O-020 | Intuitive CLI, flexible project structure |

Every outcome traces to this Constitution. Every specification traces to an outcome. Every function traces to a specification. 

**Alignment is measurable. Architecture is enforced. Context is preserved.**

This is the contract.
