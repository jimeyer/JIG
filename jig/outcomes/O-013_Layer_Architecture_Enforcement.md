---
id: O-013
title: Layer Architecture Enforcement
type: outcome
theme: [Architecture]
supports_goals: [G-003]
specifies: [S-038, S-039]
---

# Layer Architecture Enforcement

**Value:** Architectural violations (upward dependencies, circular dependencies) are automatically detected before they degrade system structure.

**Acceptance:** `jigy validate bricks` detects layer constraint violations and circular dependencies, reporting function-level detail showing exactly which calls violate constraints, completing in <5s for projects with 100+ functions and 10+ bricks.

## AI Agent Benefit

Agents cannot violate layer constraints even if a change seems locally beneficial. When an agent's code introduces an upward dependency (layer 2 calling layer 3), validation fails immediately with function-level detail. This prevents agents from inadvertently coupling foundation to features, a common source of architectural decay.

## Rationale

Layer discipline prevents architectural decay. A001 Section 4 defines layer semantics: brick at layer N can only depend on bricks at layers < N (or other layer 0 bricks if N=0). Without automated validation, two categories of violations accumulate over time:

1. **Layer constraint violations**: Higher-layer bricks depending on lower layers (e.g., layer 1 → layer 2), or same-layer dependencies outside layer 0. These violations break the architectural hierarchy and make dependency flow unclear.

2. **Circular dependencies**: Cycles in the brick dependency graph (e.g., B-a → B-b → B-c → B-a), even at layer 0. Cycles create brittle coupling, prevent clear understanding of system structure, and violate A001 Section 10 rule 13.

Function-level detail enables developers to quickly locate violations. Instead of just "B-auth depends on B-cli", validation shows "F-auth.login calls F-cli.main.run", making fixes straightforward. Suggesting concrete remedies (raise layer, lower layer, or refactor) reduces time spent deciding how to fix violations.

## Success Criteria

The validation system must:
1. Derive brick dependencies from implementation graph function calls
2. For each brick B at layer L, verify all dependency bricks satisfy layer constraints (< L, or = 0 if L = 0)
3. Detect all circular dependencies in brick graph using cycle detection algorithm (DFS with recursion stack)
4. Report violations with function-level detail showing which specific calls create invalid dependencies
5. Show cycle paths clearly (B-a → B-b → B-c → B-a)
6. Suggest concrete fixes (raise source layer, lower dependency layer, or refactor to remove dependency)
7. Complete validation in under 5 seconds for graphs with 100+ functions and 10+ bricks
8. Work correctly at all layers including layer 0 (foundation bricks may depend on each other but no cycles)

## Specified By

This outcome is delivered through:
- **S-038**: Layer constraint validation ensuring brick dependencies respect hierarchy (layer N → layers < N, or layer 0 → layer 0)
- **S-039**: Circular dependency detection using DFS algorithm to ensure brick dependency graph is acyclic (DAG) at all layers

## Constitution Linkage

This outcome serves: **Part II: Architectural Boundaries** - Layers
Enables: Enforced dependency direction, prevented architectural decay
Without this: Upward dependencies and cycles accumulate silently
