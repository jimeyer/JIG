---
id: S-110
title: Context CLI Command
type: specification
outcomes: [O-019, O-030]
architecture: [A-002]
---

# Context CLI Command

The `jigy context` command is the primary interface for project orientation and graph exploration.

## Command Syntax

```bash
jigy context                        # Project Overview (S-114)
jigy context <identifier>           # Graph traversal from identifier
jigy context <identifier> --max N   # Traversal with custom budget
jigy context S-042 -j               # JSON output (agent mode)
```

## Modes

### Bare Mode (no identifier)

Returns Project Overview per S-114:
- Charter, goals, architecture, outcomes
- Spec counts (total/implemented/verified)
- Bricks by layer
- Traversal keys for follow-up queries

### Traversal Mode (with identifier)

Returns graph neighborhood per S-112:
- Ancestors (complete chain to Charter)
- Immediate children (all)
- Deeper descendants (budget-limited)

### Graceful Fallback Mode (invalid identifier)

Returns Project Overview PLUS a note:
```
Note: "S-999" not found in project.

[Project Overview follows...]
```

Never errors on invalid identifiers. Agent always gets useful context.

## Flags

| Flag | Description |
|------|-------------|
| `--max N` | Maximum nodes in traversal response (default: 50) |
| `-j` | JSON output (S-093) |
| `-m` | Markdown output (S-093) |
| `-v` | Verbose output (S-093) |

## Acceptance Criteria

1. Bare `jigy context` returns Project Overview (S-114)
2. `jigy context <valid-id>` returns graph neighborhood (S-112, S-113)
3. `jigy context <invalid-id>` returns "not found" note + Project Overview
4. `--max N` controls traversal budget (only in traversal mode)
5. Default `--max` is 50
6. Output format flags work per S-093
7. Auto-discovers project root per S-057

## Rationale

Agents need to orient (understand project) and traverse (explore connections). One command handles both. Invalid identifiers gracefully fallback to orientation rather than error, ensuring agents never get stuck.
