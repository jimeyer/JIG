---
id: S-085
title: Constrains Edges
type: specification
outcome: O-025
outcomes: [O-025]
architecture: [A-001]
---

# Constrains Edges

## Constraints

1. **Intent graph MUST include A→S edges for constrains relationships**
   - Edge type: "constrains"
   - Source: Architecture node
   - Target: Specification node
   - One edge per spec in architecture.constrains array

2. **Edge format**
   - source: architecture ID (A-001)
   - target: spec ID (S-072, etc.)
   - type: "constrains"

3. **Edges only generated when constrains array is present**
   - Architecture without constrains field generates no constrains edges
   - Empty constrains array generates no edges

## NDJSON Format

```json
{"source":"A-001","target":"S-072","type":"constrains"}
{"source":"A-001","target":"S-073","type":"constrains"}
{"source":"A-001","target":"S-086","type":"constrains"}
```

## Edge Count

Total constrains edges = sum of all architecture.constrains array lengths

## Rationale

The constrains relationship captures how architecture governs specifications. This enables impact analysis when architecture changes - all constrained specs may need review - and answers queries like "which architecture constrains S-072?"

