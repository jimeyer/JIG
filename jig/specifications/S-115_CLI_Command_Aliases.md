---
id: S-115
title: CLI Command Aliases
type: specification
outcomes: [O-019]
architecture: [A-002]
---

# CLI Command Aliases

Commonly hallucinated command names are mapped to core commands, reducing agent errors.

## Alias Mappings

| Alias | Target | Behavior |
|-------|--------|----------|
| `graph` | `context` | Bare or with identifier |
| `list` | `context` | Bare or with identifier |
| `show` | `context` | Bare or with identifier |
| `bricks` | `context` | Bare only (overview) |
| `layers` | `context` | Bare only (overview) |
| `towers` | `context` | Bare only (overview) |
| `fix` | `mend` | All mend flags supported |

## Behavior

### Full Aliases (graph, list, show)

These aliases accept optional identifiers and all context flags:

```bash
jigy graph              # → jigy context (overview)
jigy graph S-042        # → jigy context S-042 (traversal)
jigy list               # → jigy context
jigy show               # → jigy context
jigy show S-042         # → jigy context S-042
```

### Bare-Only Aliases (bricks, layers, towers)

These aliases only invoke the overview (bare context):

```bash
jigy bricks             # → jigy context (overview)
jigy layers             # → jigy context (overview)
jigy towers             # → jigy context (overview)
```

Arguments to bare-only aliases are ignored (no error, just overview).

### Mend Alias (fix)

```bash
jigy fix                # → jigy mend
jigy fix --auto         # → jigy mend --auto
jigy fix --dry-run      # → jigy mend --dry-run
```

## Acceptance Criteria

1. `jigy graph` invokes context command
2. `jigy graph <id>` invokes context with identifier
3. `jigy list` invokes context command (bare)
4. `jigy show` invokes context command (bare)
5. `jigy show <id>` invokes context with identifier
6. `jigy bricks` invokes context (bare only)
7. `jigy layers` invokes context (bare only)
8. `jigy towers` invokes context (bare only)
9. `jigy fix` invokes mend command
10. All aliases support appropriate flags from target command
11. Aliases appear in `jigy --help` with "(alias)" marker

## Rationale

Agents hallucinate commands based on mental models. Rather than error, map reasonable names to useful outputs. "Did you mean X?" is worse than just doing X.
