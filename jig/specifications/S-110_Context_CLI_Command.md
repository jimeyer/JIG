---
id: S-110
title: Context CLI Command
type: specification
outcomes: [O-030]
---

# Context CLI Command

The `jigy context <identifier>` command returns graph neighbors for any valid identifier.

## Command Syntax

```bash
jigy context <identifier>           # default --max 50
jigy context <identifier> --max N   # explicit budget
jigy context S-042 -j               # JSON output (agent mode)
```

## Flags

| Flag | Description |
|------|-------------|
| `--max N` | Maximum total nodes in response (default: 50) |
| `-j` | JSON output (S-093) |
| `-m` | Markdown output (S-093) |
| `-v` | Verbose output (S-093) |

## Acceptance Criteria

1. Command accepts any valid identifier as positional argument
2. `--max N` controls total node count in response (includes ancestors and descendants)
3. Default `--max` is 50
4. Command errors with clear message if identifier cannot be resolved
5. Output format flags work per S-093
6. Auto-discovers project root per S-057

## Behavior

1. Parse and resolve identifier (S-111)
2. Traverse graphs to collect neighborhood (S-112)
3. Format response per schema (S-113)
4. Output in requested format

## Rationale

Graph exploration is a core agent capability. Agents need to understand context before modifying code. The context command provides a single entry point for "what is this connected to?" queries across all three JIG graphs.
