---
id: S-084
title: Supports Goal Edges
type: specification
outcomes: [O-025]
architecture: [A-001]
---

# Supports Goal Edges

## Constraints

1. **Intent graph MUST include A→Goal edges (supports_goal)**
   - Edge type: "supports_goal"
   - Source: Architecture node
   - Target: Goal node
   - One edge per goal in architecture.goals array

2. **Intent graph MUST include O→Goal edges (supports_goal)**
   - Edge type: "supports_goal"
   - Source: Outcome node
   - Target: Goal node
   - One edge per goal in outcome.goals array

3. **Edge format**
   - source: artifact ID (A-001 or O-001)
   - target: goal ID (G-001, etc.)
   - type: "supports_goal"

## NDJSON Format

```json
{"source":"A-001","target":"G-001","type":"supports_goal"}
{"source":"A-001","target":"G-003","type":"supports_goal"}
{"source":"O-001","target":"G-001","type":"supports_goal"}
{"source":"O-001","target":"G-002","type":"supports_goal"}
```

## Edge Count

Total supports_goal edges = sum of all (architecture.goals + outcome.goals) arrays

## Rationale

The supports_goal relationship enables traceability from architecture and outcomes up to goals. This answers queries like "which outcomes support G-003?" and enables impact analysis when goals change.

