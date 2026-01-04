---
title: Constitution
version: 1
date: 2025-12-13
---

# JIG: Architecture for AI-Augmented Development

## Purpose

JIG exists to enable AI coding agents to work effectively on complex codebases by providing four essential capabilities that address fundamental limitations of AI-assisted development:

### 1. Grounding in Reality
AI agents hallucinate. They claim functions exist that don't, invent APIs, and make confident assertions about code they haven't read. JIG grounds agent work in verifiable truth by automatically extracting actual code structure, explicit specifications, and test relationships. Agents don't guess—they query.

### 2. Continuity Across Sessions
AI agents lose context between sessions. The next agent (or the same agent tomorrow) starts from scratch, unaware of architectural decisions, in-progress work, or why code exists. JIG provides persistent, machine-readable context through intent graphs, implementation graphs, and traceability links that survive session boundaries.

### 3. Enforcing Constraints
AI agents violate architecture. Without explicit constraints, agents introduce circular dependencies, break layering rules, and create coupling that humans would never approve. JIG enforces architectural boundaries automatically, validating that every change respects defined constraints before code is committed.

### 4. Intent Alignment
AI agents change HOW without understanding WHY. They optimize code without knowing business requirements, refactor without understanding purpose, and fix bugs without verifying intended behavior. JIG requires explicit intent (specifications, outcomes, bricks) that agents must read before modifying implementation.

---

## The Constitution Hierarchy

JIG establishes a five-level hierarchy that connects human intent to machine execution:

```
Constitution (this document)
    ↓
Outcomes (O-001 through O-022)
    ↓
Specifications (S-001 through S-0XX)
    ↓
Tests (T-XXX)
    ↓
Functions (F-XXX)
```

Every function should trace upward to a specification, every specification to an outcome, every outcome to this constitution's purpose. Breaks in this chain indicate misalignment between intent and reality.

---

## Outcomes

JIG delivers its purpose through 18 measurable outcomes. Each outcome specifies concrete success criteria and links to detailed specifications.

### Discovery & Extraction

**[O-001: Implementation structure is discoverable from source code](outcomes/O-001.md)**
Developers can query actual code structure without manual documentation. `jig impl rebuild` generates complete implementation graph in <2s for 10K LOC.
*Enables: Grounding in Reality, Continuity Across Sessions*

**[O-002: Code-to-specification traceability is automated](outcomes/O-002.md)**
No manual tracking needed—decorators link code to specs automatically. All `@jig.implements()` decorators appear in implementation graph with correct relationships.
*Enables: Intent Alignment, Grounding in Reality*

**[O-003: Implementation graphs support multi-language codebases](outcomes/O-003.md)**
Single graph representation works across Python, TypeScript, Java, Go. Adding a new language requires only implementing LanguageAnalyzer interface.
*Enables: Grounding in Reality (in polyglot systems)*

### Validation & Error Detection

**[O-004: Early Error Detection in Artifact Validation](outcomes/O-004.md)**
Developers discover validation errors before attempting graph generation, reducing wasted time from cryptic runtime failures.
*Enables: Enforcing Constraints*

**[O-005: Clear Actionable Error Messages](outcomes/O-005.md)**
Validation error messages include file paths, line numbers, and actionable descriptions. Developers resolve 80%+ of validation issues from error messages alone.
*Enables: Continuity Across Sessions (agents can self-correct)*

**[O-006: Fast Project Validation](outcomes/O-006.md)**
Full project validation completes in <5 seconds. Fast validation enables integration into pre-commit hooks, CI pipelines, and watch mode workflows.
*Enables: Enforcing Constraints (fast feedback loops)*

### Intent Graph Management

**[O-009: Generate Intent Graph from Specifications and Bricks](outcomes/O-009.md)**
Developers can generate a complete intent graph containing specifications, outcomes, and brick definitions from human-authored artifacts.
*Enables: Intent Alignment, Continuity Across Sessions*

### Architecture Enforcement

**[O-012: Brick definitions comply with A001 format requirements](outcomes/O-012.md)**
Developers receive immediate feedback when brick definitions violate A001 contracts. `jigy validate bricks` detects ID format violations, missing layer fields, and invalid layer values in <1s.
*Enables: Enforcing Constraints*

**[O-013: Layer architecture is enforced and validated](outcomes/O-013.md)**
Architectural violations (upward dependencies, circular dependencies) are automatically detected before they degrade system structure. Function-level detail shows exactly which calls violate constraints.
*Enables: Enforcing Constraints*

**[O-014: Layer structure is visible and manageable](outcomes/O-014.md)**
Developers can visualize current layer structure and automatically discover appropriate layer assignments from dependency analysis. `jigy layers` displays structure; `jigy layers suggest` recommends assignments.
*Enables: Intent Alignment (architectural visibility), Continuity Across Sessions*

### Completeness & Traceability

**[O-015: Completeness validation for intent graph](outcomes/O-015.md)**
Developers discover incomplete intent definitions (orphaned outcomes or specifications) before they cause confusion or misalignment. `jigy validate intent` detects orphans in <1s.
*Enables: Intent Alignment, Enforcing Constraints*

**[O-016: CI and Tooling Integration](outcomes/O-016.md)**
Validation integrates seamlessly into CI pipelines and editor tooling via machine-parseable output. `jigy validate --format json` produces structured output that CI systems and editors consume programmatically.
*Enables: Enforcing Constraints (automated quality gates)*

**[O-017: Artifact Change Detection](outcomes/O-017.md)**
JIG detects when specifications, implementations, or tests change, enabling automated drift detection between intent and reality.
*Enables: Continuity Across Sessions, Grounding in Reality*

**[O-018: Test-to-Specification Traceability](outcomes/O-018.md)**
Tests that verify specifications are discoverable and queryable, completing the S-F-T alignment triangle. Enables queries like "which specs have no verifying tests?"
*Enables: Grounding in Reality (verification), Intent Alignment*

**[O-021: Verifiable Test-to-Implementation Coverage](outcomes/O-021.md)**
Tests that claim to verify specifications demonstrably execute the implementing code. Completes the S-F-T triangle with objective, execution-based evidence—detecting cases where tests pass but don't actually execute relevant implementation.
*Enables: Grounding in Reality (verification), Intent Alignment*

### Developer Experience

**[O-019: Intuitive CLI Experience](outcomes/O-019.md)**
Users interact with JIG through a memorable, verb-first command structure requiring zero configuration. Run `jigy align` from anywhere in the project.
*Enables: Continuity Across Sessions (low cognitive overhead)*

**[O-020: Configurable Project Structure](outcomes/O-020.md)**
JIG adapts to diverse project layouts without requiring projects to reorganize their code. Enables adoption in existing projects with non-standard directory structures.
*Enables: Grounding in Reality (works with real projects as-is)*

**[O-022: Commands Operate on Current Data](outcomes/O-022.md)**
JIG commands operate on up-to-date graph data without requiring manual rebuild invocation. Developers receive correct results from `validate`, `show`, and `audit` commands without remembering to run `jigy rebuild` first.
*Enables: Continuity Across Sessions (correct results), Grounding in Reality*

---

## For AI Agents Reading This

If you are an AI agent working on this codebase:

1. **Read before writing**: Query the implementation graph to understand what exists before claiming anything about code structure.

2. **Link your work**: Use `@jig.implements()` and `@jig.verifies()` decorators to create explicit traceability from your code to specifications.

3. **Validate continuously**: Run `jigy validate` before committing. If validation fails, you have violated constraints that humans have deemed important.

4. **Understand intent first**: Read the specification (S-XXX) and outcome (O-XXX) before modifying implementation. Know WHY before changing HOW.

5. **Respect architecture**: Run `jigy validate bricks` to ensure your changes don't violate layer constraints or introduce circular dependencies.

6. **Document what you learn**: When you discover system structure or architectural decisions, that knowledge should flow into specifications, not just session memory.

7. **Check alignment**: Before claiming a task is complete, run `jigy align` to verify that implementation, intent, and tests form a coherent triangle.

JIG exists because you exist. Use it.

---

## Maintenance

This constitution is the foundation. When outcomes change, this document must be updated to reflect the new reality. When this document's purpose changes, a new version must be created and all downstream outcomes re-evaluated for alignment.

**Version History:**
- v1.0 (2025-12-13): Initial constitution establishing purpose for AI-augmented development
