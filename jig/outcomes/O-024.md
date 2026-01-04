---
id: O-024
type: outcome
title: Architecture Constrains Specifications
supports_goals: [G-003, G-005]
specifies: [S-076, S-077, S-078, S-079]
---

# Architecture Constrains Specifications

**Value:** Architecture documents define structural boundaries that constrain how specifications may be implemented.

**Acceptance:** jig/architecture/ directory contains valid A-{NNN} documents; jigy validate confirms structure and references.

## AI Agent Benefit

Agents can read architecture documents to understand structural constraints before implementing specifications. Without explicit architecture, agents make ad-hoc structural decisions that may conflict with established patterns.

## Rationale

This enables separation of concerns between:
- **Intent** (Outcomes/Specs): What we want to achieve
- **Structure** (Architecture): How we organize to achieve it

Architecture documents answer questions like:
- "What constraints apply to this specification?"
- "Which architecture governs this area of the codebase?"
- "What specs need review if this architecture changes?"

## Success Criteria

Architecture documents must:
1. Reside in jig/architecture/ directory
2. Follow A-{NNN}_{Title}.md naming pattern
3. Have valid frontmatter with id, type, title, status, supports_goals
4. Reference only existing specs in constrains field (if present)

## Specified By

This outcome is delivered through:
- **S-076**: Architecture file location
- **S-077**: Architecture ID format
- **S-078**: Architecture supports_goals required
- **S-079**: Architecture constrains references

## Constitution Linkage

This outcome serves: **Enforcing Constraints (G-003)**, **Full Traceability (G-005)**
Enables: Architectural visibility, constraint propagation
Without this: Structural decisions are implicit and untraceable

