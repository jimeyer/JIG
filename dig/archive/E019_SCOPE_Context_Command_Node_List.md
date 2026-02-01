---
title: "Context Command: Node-List Design"
type: scope
status: implemented
decision: completed
created: 1737244800
created_human: "2026-01-18 18:00 CST"
parent: "[[E007_CONCEPT_Context_Command_Design]]"
children: []
---
# Context Command: Node-List Design

## Decision

Implement `jigy context` as a minimal graph traversal that returns a list of related nodes. The calling agent decides what to read—JIG just provides the neighborhood.

This is a refinement of Approach 1 (Node-Centric Traversal) from [[E007_CONCEPT_Context_Command_Design]], simplified to remove view logic.

---

## Core Insight

Agents are good at reading files and synthesizing. JIG should provide the graph structure, not pre-formatted views. The context command becomes a **graph neighborhood query**—minimal logic, maximum utility.

---

## Command Interface

```bash
jigy context <identifier>           # default --max 50
jigy context <identifier> --max N   # explicit budget
jigy context S-042 -j               # JSON output (agent mode)
```

**Identifier resolution** (unchanged from E007):
- Spec ID: `S-042` → direct lookup
- Outcome ID: `O-012` → direct lookup
- Goal ID: `G-1` → direct lookup
- File path: `src/foo.py` → find functions in file
- Function: `F-jig.cli.main.run` → direct lookup

---

## Response Schema

```json
{
  "root": "S-042",
  "nodes": [
    {"id": "O-012", "type": "outcome", "file": "jig/outcomes/O-012_Realtime.md", "edge": "parent", "depth": -1},
    {"id": "G-1", "type": "goal", "file": "jig/Charter.md", "edge": "parent", "depth": -2},
    {"id": "F-crdt.observe.subscribe", "type": "function", "file": "src/crdt/observe.py:45", "edge": "implements", "depth": 1},
    {"id": "T-test_observe.test_sub", "type": "test", "file": "tests/test_observe.py:23", "edge": "verifies", "depth": 1}
  ],
  "more": 75
}
```

### Fields

| Field | Description |
|-------|-------------|
| `root` | The queried identifier |
| `nodes` | Flat list of related nodes |
| `more` | Count of descendants not included (0 = complete) |

### Node Fields

| Field | Description |
|-------|-------------|
| `id` | Node identifier (S-###, O-###, F-*, T-*, etc.) |
| `type` | Node type: spec, outcome, goal, function, test, brick |
| `file` | File path, with optional `:line` for functions/tests |
| `edge` | Relationship to root: parent, implements, verifies, sibling |
| `depth` | Signed distance from root. Negative = ancestor, positive = descendant |

---

## Traversal Algorithm

### Asymmetry Insight

The graph is asymmetric:
- **Upward** (toward Charter): bounded, low fanout, max ~5 hops
- **Downward** (toward code): unbounded, high fanout, could be hundreds

### Rules

1. **Always include all ancestors** (full chain to Charter)
2. **Always include immediate children** (depth 1 descendants)
3. **Fill remaining budget breadth-first** by depth layer
4. **Stop when budget exhausted**, set `more` to remaining count

### Budget

- `--max N` controls total nodes in response (default: 50)
- Budget includes ancestors and descendants
- No magic values (no `-1` for unlimited—agent asks for 500 or 10000 explicitly)

### Example: `jigy context G-1 --max 50`

1. G-1 itself (1 node)
2. Ancestors: Charter (1 node) — always included
3. Immediate children: 3 outcomes (3 nodes)
4. Depth 2: 12 specs (12 nodes) — budget allows
5. Depth 3: 80 functions — only room for 33, set `more: 47`

Total: 50 nodes, `more: 47`

---

## Navigation Pattern

When `more > 0`, agent navigates by drilling down, not paginating:

```bash
jigy context G-1           # "more": 120, sees outcomes
jigy context O-012         # "more": 45, sees specs under this outcome
jigy context S-042         # "more": 0, complete picture of one spec
```

The graph structure IS the navigation. Agent picks a branch, zooms in.

For bulk queries, agent requests larger budget:

```bash
jigy context G-1 --max 500   # get everything
```

---

## Output Formats

Per DJ001/DJ002:

| Flag | Format | Use Case |
|------|--------|----------|
| (none) | Human | Interactive CLI use |
| `-j` | JSON | Agent consumption |
| `-m` | Markdown | Documentation |

Human format pretty-prints the same data. JSON is the primary agent interface.

---

## What This Doesn't Do

- **No view logic** — agent reads files it needs
- **No relevance scoring** — distance and edge type are sufficient
- **No query language** — navigate by drilling down
- **No pagination cursors** — graph structure provides navigation

---

## Open Questions

1. **Default MAX value** — 50 feels right, but may tune based on usage
2. **Human output format** — table? tree? indented list?
3. **Edge type vocabulary** — need complete list (parent, implements, verifies, sibling, ?)

---

## References

- [[E007_CONCEPT_Context_Command_Design]] — Original design exploration
- [[jig/dig/archive/DJ001_CONCEPT_CLI_Design_Manifesto]] — Output format principles
- [[jig/dig/archive/DJ002_SCOPE_CLI_Recommendations]] — Command structure
