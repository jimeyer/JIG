---
id: S-113
title: Context Response Schema
type: specification
outcomes: [O-030]
---

# Context Response Schema

The context command returns a flat node list with metadata for agent consumption.

## JSON Schema

```json
{
  "root": "S-042",
  "nodes": [
    {
      "id": "O-012",
      "type": "outcome",
      "file": "jig/outcomes/O-012_Realtime.md",
      "edge": "parent",
      "depth": -1
    },
    {
      "id": "G-001",
      "type": "goal",
      "file": "jig/Charter_JIG.md",
      "edge": "parent",
      "depth": -2
    },
    {
      "id": "F-jig.crdt.subscribe",
      "type": "function",
      "file": "src/crdt/observe.py:45",
      "edge": "implements",
      "depth": 1
    }
  ],
  "more": 75
}
```

## Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `root` | string | The queried identifier |
| `nodes` | array | Flat list of related nodes |
| `more` | integer | Count of descendants not included (0 = complete) |

## Node Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Node identifier (S-###, O-###, F-*, etc.) |
| `type` | string | Node type: charter, goal, architecture, outcome, specification, function, test, brick, class |
| `file` | string | File path, with optional `:line` for functions/tests |
| `edge` | string | Edge type from graph: specifies, implements, verifies, defines_goal, supports_goal, specifications |
| `depth` | integer | Signed distance from root. Negative = ancestor, positive = descendant |

## Depth Semantics

- `depth = 0` — the root node itself (not included in nodes array)
- `depth < 0` — ancestors (e.g., -1 = immediate parent, -2 = grandparent)
- `depth > 0` — descendants (e.g., 1 = immediate child, 2 = grandchild)

## Acceptance Criteria

1. JSON output matches schema above
2. `root` is the queried identifier exactly as provided
3. `nodes` contains all returned nodes (ancestors + descendants)
4. Each node has `id`, `type`, `file`, `edge`, `depth` fields
5. `depth` is negative for ancestors, positive for descendants
6. `more` is 0 when neighborhood is complete, > 0 when truncated
7. Nodes are sorted by depth (ancestors first), then by ID

## Rationale

Flat structure is simple to parse. Per-node metadata tells the agent the relationship and direction. Signed depth encodes both distance and direction in one field. The agent uses `more` to decide whether to drill down into a child node.
