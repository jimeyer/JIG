---
id: S-070
title: Auto-Rebuild Before Commands
type: specification
---

# Auto-Rebuild Before Commands

Commands that depend on graph data automatically rebuild stale graphs before execution.

**Acceptance Criteria:**
- `jigy validate` rebuilds all stale graphs before validating
- `jigy validate intent` rebuilds stale intent graph only
- `jigy validate bricks` rebuilds stale impl + intent graphs
- `jigy show` rebuilds all stale graphs before displaying
- `jigy show layers` rebuilds stale impl + intent graphs
- `jigy show bricks` rebuilds stale impl + intent graphs
- `jigy audit coverage` rebuilds stale impl + verify graphs
- Each graph rebuilt independently based on its own staleness
- Auto-rebuild uses same logic as `jigy rebuild {graph}`

**Output Format:**

When graphs are stale:
```
Graphs stale, rebuilding...
  impl: 423 nodes, 671 edges
  verify: up to date
  intent: up to date
Validating...
```

When nothing stale:
```
Validating...
```

**Rationale:** Automatic rebuilding eliminates "forgot to rebuild" errors while
selective per-graph rebuild minimizes unnecessary work.

