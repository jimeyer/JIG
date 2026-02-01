---
id: S-085
title: Specifications Edges
type: specification
outcomes: [O-025]
architecture: [A-001]
---

# Specifications Edges

## Constraints

1. **Intent graph MUST include A→S edges for specifications relationships**
   - Edge type: "specifications"
   - Source: Architecture node
   - Target: Specification node
   - One edge per spec in architecture.specifications array

2. **Edge format**
   - source: architecture ID (A-001)
   - target: spec ID (S-072, etc.)
   - type: "specifications"

3. **Edges only generated when specifications array is present**
   - Architecture without specifications field generates no specifications edges
   - Empty specifications array generates no edges

## NDJSON Format

```json
{"source":"A-001","target":"S-072","type":"specifications"}
{"source":"A-001","target":"S-073","type":"specifications"}
{"source":"A-001","target":"S-086","type":"specifications"}
```

## Edge Count

Total specifications edges = sum of all architecture.specifications array lengths

## Rationale

The specifications relationship captures how architecture governs specifications. This enables impact analysis when architecture changes - all related specs may need review - and answers queries like "which architecture specifies S-072?"

