---
id: S-080
title: Charter Node In Intent Graph
type: specification
outcome: O-025
outcomes: [O-025]
architecture: [A-001]
---

# Charter Node In Intent Graph

## Constraints

1. **Intent graph MUST include Charter node**
   - Single node with type: "charter"
   - Node id: "Charter"
   - Includes goals array from frontmatter

2. **Charter node MUST have required fields**
   - id: "Charter"
   - type: "charter"
   - goals: [G-001, G-002, ...]
   - file: relative path to charter file

3. **Charter node MUST be generated from charter file**
   - Parsed from YAML frontmatter
   - Discovers `Charter.md` or `Charter_<project>.md` per S-072
   - File existence is prerequisite

## NDJSON Format

```json
{"id":"Charter","type":"charter","goals":["G-001","G-002","G-003","G-004","G-005"],"file":"jig/Charter_MyProject.md"}
```

## Validation Rules

- `jigy rebuild intent` MUST generate Charter node
- Intent graph without Charter node is incomplete
- Charter node appears after metadata line in NDJSON

## Rationale

The Charter is the root of the intent hierarchy. Including it in the intent graph enables complete traceability queries from any node back to the project's foundational goals.

