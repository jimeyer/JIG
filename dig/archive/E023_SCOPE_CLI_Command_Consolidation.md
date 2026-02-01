---
title: "CLI Command Consolidation"
type: scope
status: implemented
decision: completed
created: 1737741600
created_human: "2026-01-24 12:00 CST"
parent: "[[E005_EXPLORATION_CLI_Tool_Usage_Analysis]]"
children: ["[[E023_JIGPLAN_CLI_Command_Consolidation]]"]
---
# CLI Command Consolidation

## Decision

Consolidate jigy CLI commands around **outputs**, not command names. Agents hallucinate commands based on mental models (`graph`, `list`, `fix`). Instead of erroring, map all reasonable names to useful outputs.

---

## Core Insight

From [[E005_EXPLORATION_CLI_Tool_Usage_Analysis]]:
- `jigy graph` hallucinated (agents expect it)
- `jigy list` hallucinated
- `jigy fix` hallucinated
- `jigy show` has 14.8% error rate from API confusion

Agents need two things:
1. **Orient** — understand project structure
2. **Traverse** — explore specific nodes

Everything else is aliases and graceful fallback.

---

## Output / Functionality Matrix

| Output | Description | Commands |
|--------|-------------|----------|
| **Project Overview** | Unified context: bricks, layers, towers, charter, goals, architecture, + traversal keys | `context`, `graph`, `show`, `list`, `bricks`, `layers`, `towers` (bare) |
| **Graph Traversal** | Ancestors/descendants from node | `context <id>` (valid id) |
| **Overview + "not found"** | Graceful fallback | `context <invalid-id>` |
| **Auto-fix Errors** | Apply validation fixes | `mend`, `fix` |
| **Validate** | Check alignment | `validate` |
| **Rebuild** | Regenerate graphs | `rebuild` |

---

## Graceful Fallback Behavior

Invalid identifiers return Project Overview with a note, never an error:

```bash
jigy context           # → Overview
jigy context S-042     # → Traversal (if S-042 exists)
jigy context S-999     # → "S-999 not found" + Overview
jigy context bricks    # → "bricks is not a jig node" + Overview
jigy show bricks       # → "bricks is not a jig node" + Overview
jigy graph foo         # → "foo is not a jig node" + Overview
```

Agent never gets stuck — always reorients with project context.

---

## Project Overview Contents

The unified overview includes:

1. **Charter** — project name, defined goals
2. **Goals** — G-### IDs with titles
3. **Architecture** — A-### documents
4. **Outcomes** — O-### with supporting goals
5. **Specifications** — S-### count by status
6. **Bricks** — brick IDs by layer
7. **Towers** — tower structure (if multi-tower)
8. **Traversal Keys** — list of valid identifiers for `context <id>`

This gives an agent everything needed to orient and know what to query next.

---

## Commands Removed

| Command | Replacement |
|---------|-------------|
| `align` | Use `validate` (already does rebuild if stale) |
| `show layers` | Folded into Project Overview |
| `show bricks` | Folded into Project Overview |
| `show towers` | Folded into Project Overview |
| `show matrix` | Folded into Project Overview |
| `show charter` | Folded into Project Overview |
| `show goals` | Folded into Project Overview |
| `show architecture` | Folded into Project Overview |

---

## Commands Added

| Command | Behavior |
|---------|----------|
| `graph` | Alias for `context` |
| `list` | Alias for `context` |
| `bricks` | Alias for `context` (bare) |
| `layers` | Alias for `context` (bare) |
| `towers` | Alias for `context` (bare) |
| `fix` | Alias for `mend` |

---

## Final Command Surface

**Core commands:**
- `context [<id>]` — orient (bare) or traverse (with id)
- `validate` — check alignment
- `mend` — auto-fix errors
- `rebuild` — regenerate graphs
- `init` — initialize project
- `audit` — run audits

**Aliases (all invoke core commands):**
- `graph`, `show`, `list` → `context`
- `bricks`, `layers`, `towers` → `context` (bare)
- `fix` → `mend`

---

## Implementation Notes

1. `context` becomes a Click command with optional argument, not a group
2. Identifier resolution attempts pattern match first, then returns overview + note
3. Project Overview combines data from multiple current `show_*_command` functions
4. All aliases use Click's `@cli.command(name="alias")` pointing to same handler

---

## References

- [[E005_EXPLORATION_CLI_Tool_Usage_Analysis]] — Usage data driving this consolidation
- [[E019_SCOPE_Context_Command_Node_List]] — Graph traversal design
- [[E007_CONCEPT_Context_Command_Design]] — Original context concept
