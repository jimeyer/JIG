---
id: O-023
type: outcome
title: Charter Establishes Project Goals
goals: [G-005, G-004]
specifications: [S-072, S-073, S-074, S-075]
---

# Charter Establishes Project Goals

**Value:** A single Charter document defines all project goals, creating the root of the intent hierarchy.

**Acceptance:** jig/Charter.md exists with valid frontmatter and goal definitions; jigy validate confirms Charter structure.

## AI Agent Benefit

Agents can query the Charter to understand project purpose before making changes. Without explicit goals, agents optimize for local concerns without understanding broader context. The Charter provides the "why" that guides the "how."

## Rationale

All downstream artifacts (Architecture, Outcomes) reference Charter goals, enabling complete top-down traceability. This answers questions like:
- "Which goals does this code support?"
- "What is the purpose of this outcome?"
- "Why does this specification exist?"

## Success Criteria

The Charter must:
1. Exist as a single file at jig/Charter.md
2. Define all project goals in frontmatter (defines_goals array)
3. Have goal headers matching `### G-{number}: {Title}` format
4. Pass jigy validate charter checks

## Specified By

This outcome is delivered through:
- **S-072**: Charter file structure
- **S-073**: Charter defines_goals field
- **S-074**: Goal header format
- **S-075**: Goal ID format

## Constitution Linkage

This outcome serves: **Full Traceability (G-005)**, **Intent Alignment (G-004)**
Enables: Root node for intent hierarchy, goal-based queries
Without this: No single source of truth for project direction

