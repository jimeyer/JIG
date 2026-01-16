---
id: O-026
type: outcome
title: Towers Enforce Component Isolation
goals: [G-003]
specifications: [S-086, S-087, S-088, S-089, S-090, S-091]
---

# Towers Enforce Component Isolation

**Value:** Bricks are assigned to towers (vertical partitions). Cross-tower dependencies are forbidden, enforcing complete isolation between components.

**Acceptance:** jigy validate detects cross-tower dependencies; jigy towers and jigy matrix display tower structure.

## AI Agent Benefit

Agents working in one tower cannot accidentally create dependencies on another tower. This prevents hidden coupling and ensures components can be developed, tested, and deployed independently.

## Rationale

Towers provide vertical partitioning orthogonal to layers:
- **Layers**: Horizontal stratification (foundation → services → UI)
- **Towers**: Vertical isolation (backend, frontend, shared)

This enables:
- Independent development of components
- Multi-language freedom (tower can be rewritten)
- Clean testing (each tower tests against intent, not other towers)
- Clear ownership boundaries

## Note on JIG's Single Tower

JIG currently uses a single implicit tower since it is a cohesive tooling system. This demonstrates that the tower model is opt-in. Projects that don't need vertical partitioning simply omit the tower field from bricks. Future JIG extensions could introduce additional towers.

## Success Criteria

Tower enforcement must:
1. Allow optional tower field on bricks
2. Validate tower format as kebab-case
3. Detect cross-tower dependencies via implementation graph
4. Provide jigy towers command for tower listing
5. Provide jigy matrix command for layer×tower visualization
6. Skip tower validation for single-tower projects

## Specified By

This outcome is delivered through:
- **S-086**: Brick tower field optional
- **S-087**: Tower value format
- **S-088**: Cross-tower isolation
- **S-089**: Tower isolation validation
- **S-090**: jigy towers command
- **S-091**: jigy matrix command

## Constitution Linkage

This outcome serves: **Enforcing Constraints (G-003)**
Enables: Component isolation, independent deployment
Without this: Implicit coupling accumulates, component boundaries erode

