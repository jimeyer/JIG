---
id: S-112
title: Context Graph Traversal
type: specification
outcomes: [O-030]
---

# Context Graph Traversal

Graph traversal respects the asymmetry between upward (bounded) and downward (unbounded) directions.

## Traversal Rules

### Upward (Ancestors)

All ancestors are always included. The graph is bounded upward:
- Max depth: ~5 hops (F/T → S → O/A → G → Charter)
- Low fanout: each node has 1-2 parents
- Total ancestors: typically < 10 nodes

### Downward (Descendants)

Descendants are budget-limited:
1. **Immediate children** (depth 1) — always included
2. **Deeper descendants** — breadth-first by layer until budget exhausted
3. **Truncation** — stop when total nodes reach `--max N`

### Budget Accounting

- `--max N` counts all nodes in response (ancestors + descendants + root)
- Ancestors and immediate children consume budget first
- Remaining budget fills deeper layers breadth-first
- When budget exhausted, set `more` to count of omitted descendants

## Acceptance Criteria

1. All ancestors from root to Charter are always included
2. Immediate children (depth 1 descendants) are always included
3. Deeper descendants are added breadth-first by depth layer
4. Total nodes in response ≤ `--max N`
5. `more` field reports count of descendants not included
6. `more = 0` means complete neighborhood (no truncation)

## Edge Types

Traversal follows these edges:

| Edge | Direction | Description |
|------|-----------|-------------|
| `defines_goal` | Charter → Goal | Charter defines goals |
| `supports_goal` | A/O → Goal | Architecture/Outcome supports goal |
| `specifications` | A → S | Architecture constrains specs |
| `specifies` | O → S | Outcome specifies specs |
| `implements` | F → S | Function implements spec |
| `verifies` | T → S | Test verifies spec |

## Rationale

Agents navigate by drilling down, not paginating. Return complete ancestors (always useful for "why does this exist?"), immediate children (shape of the subtree), and budget-limited deeper descendants. The agent can then query a child node to zoom in.
