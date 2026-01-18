---
id: S-111
title: Context Identifier Resolution
type: specification
outcomes: [O-030]
---

# Context Identifier Resolution

Identifiers are resolved to graph nodes by pattern matching and lookup.

## Identifier Patterns

| Pattern | Node Type | Example |
|---------|-----------|---------|
| `S-###` | Specification | S-042 |
| `O-###` | Outcome | O-012 |
| `G-###` | Goal | G-001 |
| `A-###` | Architecture | A-001 |
| `B-*` | Brick | B-cli |
| `F-*` | Function | F-jig.cli.main.run |
| `T-*` | Test | T-test_cli.test_validate |
| `Charter` | Charter | Charter |
| File path | File → Functions | src/jig/cli/main.py |

## Resolution Priority

1. **Exact ID match** — pattern-based (S-###, O-###, G-###, A-###, B-*, F-*, T-*, Charter)
2. **File path** — if path exists on disk, resolve to functions in file
3. **Error** — if no match, return clear error with valid patterns

## Acceptance Criteria

1. Specification IDs (`S-\d+`) resolve to spec nodes in intent graph
2. Outcome IDs (`O-\d+`) resolve to outcome nodes in intent graph
3. Goal IDs (`G-\d+`) resolve to goal nodes in intent graph
4. Architecture IDs (`A-\d+`) resolve to architecture nodes in intent graph
5. Brick IDs (`B-[\w-]+`) resolve to brick nodes in intent graph
6. Function IDs (`F-.+`) resolve to function nodes in impl graph
7. Test IDs (`T-.+`) resolve to test nodes in verify graph
8. `Charter` resolves to the Charter node
9. Existing file paths resolve to the file (context shows functions within)
10. Unresolved identifiers produce error with list of valid patterns

## Rationale

Agents and humans need a universal entry point for graph queries. Any identifier—spec, function, file path—should work. Pattern matching provides fast, unambiguous resolution without fuzzy search complexity.
