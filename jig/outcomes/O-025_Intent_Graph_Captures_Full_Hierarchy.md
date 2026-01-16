---
id: O-025
type: outcome
title: Intent Graph Captures Full Hierarchy
goals: [G-005, G-002]
specifications: [S-080, S-081, S-082, S-083, S-084, S-085]
---

# Intent Graph Captures Full Hierarchy

**Value:** The intent graph includes Charter, Goal, and Architecture nodes in addition to Outcomes, Specifications, and Bricks.

**Acceptance:** jigy rebuild intent generates graph with all node types; grep confirms Charter, Goal, Architecture nodes present.

## AI Agent Benefit

Agents can traverse the complete intent hierarchy from any node to the Charter. This enables queries like "which code supports G-003?" and "trace this function to its goals."

## Rationale

All six node types are represented:
1. **Charter**: Root document defining goals
2. **Goals**: Individual goal nodes extracted from Charter
3. **Architecture**: Structural constraint documents
4. **Outcomes**: Business value groupings
5. **Specifications**: Behavioral requirements
6. **Bricks**: Implementation partitions

All relationship types are represented as edges:
- defines_goal: Charter → Goal
- supports_goal: Architecture/Outcome → Goal
- constrains: Architecture → Specification
- specifies: Outcome → Specification
- implements: Function → Specification

## Success Criteria

The intent graph must:
1. Include one Charter node
2. Include one Goal node per defined goal
3. Include one Architecture node per architecture document
4. Include defines_goal, supports_goal, and constrains edges
5. Be version 2.0 (metadata.version)

## Specified By

This outcome is delivered through:
- **S-080**: Charter node in intent graph
- **S-081**: Goal nodes in intent graph
- **S-082**: Architecture nodes in intent graph
- **S-083**: defines_goal edges
- **S-084**: supports_goal edges
- **S-085**: constrains edges

## Constitution Linkage

This outcome serves: **Full Traceability (G-005)**, **Continuity Across Sessions (G-002)**
Enables: Complete hierarchy queries, goal impact analysis
Without this: Traceability stops at Outcome level

