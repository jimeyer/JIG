---
id: Charter
type: charter
defines_goals: [G-001, G-002, G-003, G-004, G-005]
---

# JIG Charter

## Purpose

JIG exists to enable AI coding agents to work effectively on complex codebases by providing essential capabilities that address fundamental limitations of AI-assisted development.

## Charter Goals

### G-001: Grounding in Reality

AI agents hallucinate. They claim functions exist that don't, invent APIs, and make confident assertions about code they haven't read. JIG grounds agent work in verifiable truth by automatically extracting actual code structure, explicit specifications, and test relationships. Agents don't guess—they query.

### G-002: Continuity Across Sessions

AI agents lose context between sessions. The next agent (or the same agent tomorrow) starts from scratch, unaware of architectural decisions, in-progress work, or why code exists. JIG provides persistent, machine-readable context through intent graphs, implementation graphs, and traceability links that survive session boundaries.

### G-003: Enforcing Constraints

AI agents violate architecture. Without explicit constraints, agents introduce circular dependencies, break layering rules, and create coupling that humans would never approve. JIG enforces architectural boundaries automatically, validating that every change respects defined constraints before code is committed.

### G-004: Intent Alignment

AI agents change HOW without understanding WHY. They optimize code without knowing business requirements, refactor without understanding purpose, and fix bugs without verifying intended behavior. JIG requires explicit intent (specifications, outcomes, bricks) that agents must read before modifying implementation.

### G-005: Full Traceability

Every function traces upward to specifications, specifications to outcomes, outcomes to goals, goals to this Charter. Breaks in this chain indicate misalignment between intent and reality. Complete traceability enables queries like "which code supports G-003?" and "what is the purpose of this function?"

---

## The Intent Hierarchy

JIG establishes a seven-level hierarchy that connects human intent to machine execution:

```
Charter (this document)
    ↓ defines
Goals (G-001 through G-005)
    ↓ supported by
Architecture (A-001, ...)
    ↓ constrains
Outcomes (O-001 through O-026)
    ↓ specifies
Specifications (S-001 through S-091)
    ↓ implemented by
Functions (F-XXX)
    ↓ verified by
Tests (T-XXX)
```

Every function should trace upward through this hierarchy to this Charter. Breaks in this chain indicate misalignment between intent and reality.

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

This Charter is the foundation. When goals change, all downstream artifacts must be re-evaluated for alignment. When this document changes, a new version is created and announced.

**Version History:**
- v1.0 (2026-01-04): Charter created from Constitution.md, adding explicit goals (G-001 through G-005)

