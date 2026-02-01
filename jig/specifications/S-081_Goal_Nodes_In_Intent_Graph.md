---
id: S-081
title: Goal Nodes In Intent Graph
type: specification
outcome: O-025
outcomes: [O-025]
architecture: [A-001]
---

# Goal Nodes In Intent Graph

## Constraints

1. **Intent graph MUST include Goal nodes extracted from Charter**
   - One node per goal defined in Charter
   - Node type: "goal"
   - Node id matches goal ID (G-001, etc.)

2. **Goal nodes MUST have required fields**
   - id: G-{number}
   - type: "goal"
   - title: extracted from Charter header
   - file: path to charter file (source file)

3. **Goal nodes MUST correspond to Charter.goals**
   - One-to-one mapping
   - No orphan goals in graph
   - No missing goals

## NDJSON Format

```json
{"id":"G-001","type":"goal","title":"Grounding in Reality","file":"jig/Charter_MyProject.md"}
{"id":"G-002","type":"goal","title":"Continuity Across Sessions","file":"jig/Charter_MyProject.md"}
```

## Extraction Process

1. Read charter file body content (discovered per S-072)
2. Find all `### G-{number}: {Title}` headers
3. Extract goal ID and title from each
4. Generate one Goal node per header

## Rationale

Goal nodes enable queries like "which outcomes support G-003?" and "what code implements goals related to constraints?" The intent graph becomes the queryable index of the full hierarchy.

