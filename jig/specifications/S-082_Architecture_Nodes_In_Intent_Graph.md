---
id: S-082
title: Architecture Nodes In Intent Graph
type: specification
outcomes: [O-025]
architecture: [A-001]
---

# Architecture Nodes In Intent Graph

## Constraints

1. **Intent graph MUST include Architecture nodes**
   - One node per architecture document in jig/architecture/
   - Node type: "architecture"
   - Node id matches document ID (A-001, etc.)

2. **Architecture nodes MUST have required fields**
   - id: A-{NNN}
   - type: "architecture"
   - title: from frontmatter
   - goals: array from frontmatter
   - file: relative path to architecture file

3. **Optional fields included when present**
   - specifications: array of spec IDs (if defined)

## NDJSON Format

```json
{"id":"A-001","type":"architecture","title":"JIG Core Architecture","goals":["G-001","G-003","G-004","G-005"],"specifications":["S-072","S-073"],"file":"jig/architecture/A-001_JIG_Core_Architecture.md"}
```

## Validation Rules

- `jigy rebuild intent` MUST scan jig/architecture/ directory
- Each valid architecture file generates one node
- Invalid files trigger warnings, not failures

## Rationale

Architecture nodes bridge goals to specifications in the intent hierarchy. Including them in the graph enables traceability from specifications through architecture to goals.

