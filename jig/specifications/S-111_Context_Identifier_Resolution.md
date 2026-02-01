---
id: S-111
title: Context Identifier Resolution
type: specification
outcomes: [O-030]
---

# Context Identifier Resolution

Identifiers are resolved to graph nodes by pattern matching. Invalid identifiers trigger graceful fallback.

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
| File path | File | src/jig/cli/main.py |

## Resolution Process

1. **Empty/None** - Return Project Overview (bare mode)
2. **Pattern match** - Check against ID patterns above
3. **Existence check** - Verify node exists in appropriate graph
4. **File path check** - If pattern fails, check if path exists on disk
5. **Fallback** - If all fail, return Project Overview + "not found" note

## Resolution Outcomes

| Input | Outcome |
|-------|---------|
| (none) | Project Overview |
| Valid ID that exists | Graph traversal from node |
| Valid pattern, node not found | Overview + "S-999 not found" |
| Invalid pattern, not a file | Overview + "foo is not a jig node" |
| Reserved word (bricks, layers) | Overview + "bricks is not a jig node" |

## Acceptance Criteria

1. Specification IDs (`S-\d+`) resolve to spec nodes if they exist
2. Outcome IDs (`O-\d+`) resolve to outcome nodes if they exist
3. Goal IDs (`G-\d+`) resolve to goal nodes if they exist
4. Architecture IDs (`A-\d+`) resolve to architecture nodes if they exist
5. Brick IDs (`B-[\w-]+`) resolve to brick nodes if they exist
6. Function IDs (`F-.+`) resolve to function nodes if they exist
7. Test IDs (`T-.+`) resolve to test nodes if they exist
8. `Charter` resolves to the Charter node
9. Existing file paths resolve to the file
10. Non-existent nodes return Overview + "not found" note (NOT error)
11. Unrecognized patterns return Overview + "not a jig node" note (NOT error)

## Rationale

Agents should never get stuck on "command not found" or "invalid identifier" errors. Any input to context produces useful output. Graceful fallback ensures agents can always re-orient.
