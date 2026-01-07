---
id: S-090
title: Jigy Towers Command
type: specification
outcome: O-026
---

# Jigy Towers Command

## Command

```bash
jigy show towers           # List all towers
jigy show towers <tower_id>  # Show specific tower details
```

## Constraints

1. **CLI provides command to list towers and their bricks**
   - Command: `jigy show towers` (under show group per S-060)
   - Lists all declared towers
   - Shows brick count per tower by layer

2. **Tower listing format**
   - Tower name
   - Brick count
   - Bricks grouped by layer within tower

3. **Single-tower project message**
   - When no towers declared: "single-tower project"
   - Lists all bricks without tower grouping

4. **Optional tower filter**
   - `jigy show towers <tower_id>` shows specific tower details
   - Shows all bricks in that tower with their layers

5. **Output format flags**
   - Supports `-j/-m/-v` flags (S-093)

## Output Format (Multi-Tower)

```
Towers (2):
  backend
    Layer 0: B-data (2 units)
    Layer 1: B-api (5 units)
  frontend
    Layer 0: B-state (3 units)
    Layer 1: B-ui (8 units)
```

## Output Format (Single-Tower)

```
Single-tower project
  Layer 0: B-decorators, B-validation, B-impl-graph, ...
  Layer 1: B-cli, B-verification-graph, B-audit
```

## Rationale

Tower visibility enables developers to understand component boundaries and verify architectural partitioning. Grouped under `show` for consistent verb-first structure.
