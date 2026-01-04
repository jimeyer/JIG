---
id: S-083
title: Defines Goal Edges
type: specification
outcome: O-025
---

# Defines Goal Edges

## Constraints

1. **Intent graph MUST include Charter→Goal edges**
   - Edge type: "defines_goal"
   - Source: Charter node
   - Target: Goal node
   - One edge per goal in defines_goals array

2. **Edge format**
   - source: "Charter"
   - target: goal ID (G-001, etc.)
   - type: "defines_goal"

3. **Edges MUST match defines_goals array exactly**
   - One edge per array element
   - No extra edges
   - No missing edges

## NDJSON Format

```json
{"source":"Charter","target":"G-001","type":"defines_goal"}
{"source":"Charter","target":"G-002","type":"defines_goal"}
```

## Edge Count

Number of defines_goal edges = length of Charter.defines_goals array

## Rationale

The defines_goal relationship captures the primary hierarchy: Charter defines what goals exist. These edges enable upward traversal from any goal to the Charter root.

