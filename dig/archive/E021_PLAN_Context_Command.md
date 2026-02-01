---
title: "Context Command PLAN"
type: plan
status: implemented
decision: completed
created: 1737244800
created_human: "2026-01-18 19:00 CST"
parent: "[[E020_JIGPLAN_Context_Command]]"
children: []
---

# Context Command PLAN

- **SCOPE**: dig/wip/E019_SCOPE_Context_Command_Node_List.md
- **JIGPLAN**: dig/wip/E020_JIGPLAN_Context_Command.md
- **Start**: 2026-01-18
- **Status**: Draft
- **Branch**: context-command

---

## Constraints from JIGPLAN

**FORBIDDEN Bricks** (do not modify):
- B-decorators (layer 0)
- B-intent-graph (layer 0) — read only
- B-impl-graph (layer 0) — read only
- B-verification-graph (layer 1) — read only

**Layer Constraints:**
- B-cli at layer 1
- Context module reads from layer 0 graphs, no upward dependencies

**Clean Break:**
- New feature, nothing to delete
- No backwards compatibility concerns

---

## Key Existing Code References

| Concern | Location | Notes |
|---------|----------|-------|
| CLI command pattern | src/jig/cli/main.py:401-424 | show_group pattern for command |
| Output format handling | src/jig/cli/output.py:20-33 | `OutputFormat` enum, `resolve_format()`, `add_output_options` |
| Config + project root | src/jig/cli/main.py:63-72 | `get_config()` helper |
| Graph files | jig/generated/*.ndjson | intent-graph, implementation-graph, verification-graph |

## Graph Structure (from Fresh Agent Review)

**NDJSON format**: First line is `_meta`, then node objects, then edge objects.

**Node types by graph**:
- Intent: `charter`, `goal`, `architecture`, `specification`, `outcome`, `brick`
- Impl: `class`, `function`
- Verify: `test`

**Edge types and direction** (critical for traversal):

| Edge Type | Source → Target | Parent is... |
|-----------|-----------------|--------------|
| `defines_goal` | Charter → Goal | source |
| `supports_goal` | O/A → Goal | **target** (reversed!) |
| `specifications` | A → S | source |
| `specifies` | O → S | source |
| `implements` | F → S | **target** (reversed!) |
| `verifies` | T → S | **target** (reversed!) |

**For ancestor traversal**: Follow edges where `source = parent` forward, or `source = child` backward.
**For descendant traversal**: Opposite direction.

**Cross-graph linking**: `implements` edges in impl graph and `verifies` edges in verify graph reference spec IDs from intent graph. Load all three graphs and union edges.

**File path resolution**: No "file" node type exists. File paths → return all F-* nodes whose `file` field matches.

---

## Execution Order

```
WU1 (Core) ─── WU2 (CLI) ─── WU3 (Validation)
```

Sequential - each WU depends on the previous.

---

## Test Strategy

- **New tests**: tests/cli/test_context.py (unit + integration)
- **Existing tests**: Must keep passing (pytest tests/)
- **Deleted tests**: None

---

## Work Unit Checklist

- [x] WU1: Core context module — tests ✓ / code ✓
- [x] WU2: CLI integration — tests ✓ / code ✓
- [x] WU3: Validation — SCOPE verified ✓

---

## Work Units

### Work Unit 1: Core Context Module

**Goal**: Implement identifier resolution and graph traversal logic.

**Specs Addressed**: S-111, S-112

**Acceptance Criteria**:
- [ ] `resolve_identifier(id)` parses S-###, O-###, G-###, A-###, B-*, F-*, T-*, Charter patterns
- [ ] `resolve_identifier(path)` resolves file paths to nodes
- [ ] `resolve_identifier(invalid)` raises clear error with valid patterns
- [ ] `traverse_graph(node, max)` returns all ancestors
- [ ] `traverse_graph(node, max)` returns immediate children
- [ ] `traverse_graph(node, max)` fills descendants breadth-first up to budget
- [ ] `traverse_graph(node, max)` returns `more` count for truncated results
- [ ] Tests with @jig.verifies decorators
- [ ] Code with @jig.implements decorators
- [ ] jigy rebuild && jigy validate passes

**Success Gates** (all must pass):
- [ ] All tests pass: pytest tests/cli/test_context.py -v
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors: ruff check src/jig/cli/context.py

**Escalation Triggers** (stop and ask human if):
- Test failures persist after 2 retry attempts
- Need to modify graph loading in B-intent-graph
- Identifier pattern ambiguity discovered
- Graph structure doesn't match expected edges

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| Graph loading utility | None exists—parse NDJSON manually with json.loads() per line | grep -r "ndjson" src/jig/ |
| Node type field values | Raw from graph: `specification` not `spec` | intent-graph.ndjson line 12 |
| Edge direction varies | See Graph Structure table above—some reversed | intent-graph.ndjson edges |
| File path → nodes | Return F-* nodes whose `file` field matches path | No file node type exists |
| Test pattern | tests/cli/test_show.py | Glob tests/cli/*.py |

**Implementation Notes**:
- Files: src/jig/cli/context.py (new), tests/cli/test_context.py (new)
- Load graphs from jig/generated/*.ndjson with `json.loads()` per line
- Skip `_meta` line (has no `id` field)
- Pattern: regex for ID formats, Path.exists() for file paths
- Traversal: build node index from all three graphs, follow edges per direction table
- Decorators: @jig.implements("S-111") on resolve_identifier(), @jig.implements("S-112") on traverse_graph()

**Human Verification**:
```bash
pytest tests/cli/test_context.py -v
jigy rebuild && jigy validate
```

---

### Work Unit 2: CLI Integration

**Goal**: Add `jigy context` command with output formatting.

**Specs Addressed**: S-110, S-113

**Acceptance Criteria**:
- [ ] `jigy context <identifier>` command exists
- [ ] `--max N` flag controls budget (default 50)
- [ ] `-j` flag produces JSON per S-113 schema
- [ ] `-m` flag produces markdown output
- [ ] Human output is readable terminal format
- [ ] Error on invalid identifier shows valid patterns
- [ ] Auto-discovers project root per S-057
- [ ] Tests with @jig.verifies decorators
- [ ] Code with @jig.implements decorators
- [ ] jigy rebuild && jigy validate passes

**Success Gates** (all must pass):
- [ ] All tests pass: pytest tests/cli/test_context.py -v
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors: ruff check src/jig/cli/context.py

**Escalation Triggers** (stop and ask human if):
- Test failures persist after 2 retry attempts
- Output format unclear for edge cases
- Click integration issues

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| Import for output | `from jig.cli.output import add_output_options, resolve_format, OutputFormat` | src/jig/cli/output.py |
| Command registration | Add to main.py like show_group (line 401-424) | src/jig/cli/main.py |
| Node type in JSON | Use raw graph type: `specification`, not `spec` | intent-graph.ndjson |
| Edge field in JSON | Use raw graph edge type: `specifies`, `implements`, etc. | Keep as-is from graph |

**Implementation Notes**:
- Files: src/jig/cli/context.py (modify), src/jig/cli/main.py (add command), tests/cli/test_context.py (extend)
- Follow show_group pattern in main.py for command registration
- Use @add_output_options decorator and resolve_format()
- JSON output: `{"root": ..., "nodes": [...], "more": N}`
- Response schema: each node has id, type, file, edge, depth (use raw values from graph)
- Decorators: @jig.implements("S-110") on context_command(), @jig.implements("S-113") on format functions

**Human Verification**:
```bash
jigy context S-001 -j | jq .  # Should show valid JSON
jigy context Charter          # Should show human output
pytest tests/cli/test_context.py -v
```

---

### Work Unit 3: Validation

**Goal**: Verify SCOPE problem is solved at system boundary.

**SCOPE Reference**:
"jigy context <identifier> traverses the graph and gives you a list of related nodes"

**Validation Approach**: Integration Test (preferred)

**Verification Steps**:
```bash
# Verify the core use case from SCOPE
jigy context G-001 -j | jq '.nodes | length'  # Should return nodes
jigy context S-110 -j | jq '.root'            # Should be "S-110"
jigy context S-110 -j | jq '.nodes[] | select(.depth < 0)'  # Should show ancestors

# Verify budget limiting
jigy context Charter --max 5 -j | jq '.more'  # Should show truncation count

# Verify error handling
jigy context INVALID 2>&1 | grep -i "pattern\|error"  # Should show valid patterns
```

**Expected Result**:
- `jigy context G-001` returns Charter as ancestor, outcomes/specs as descendants
- `jigy context S-110` returns O-030 as parent, shows depth correctly
- `--max` limiting works and `more` count is accurate
- Invalid identifiers produce helpful error messages

**Deliverable**:
- [ ] Integration test added: tests/cli/test_context_integration.py

**If Validation Fails**:
- Investigate graph loading or traversal logic
- Check edge types match what's in NDJSON files
- Add regression test for failing case

**Human Verification**:
```bash
pytest tests/cli/test_context_integration.py -v
jigy context G-001
```

---

## Execution Log

| WU | Status | Commit | Notes |
|----|--------|--------|-------|
| WU1 | COMPLETE | 4d3b809 | Core context module (S-111, S-112) |
| WU2 | COMPLETE | 08ba98f | CLI integration (S-110, S-113) |
| WU3 | COMPLETE | e3a8674 | Validation - SCOPE verified |

---

## Completion Summary

**Scope Delivered:**
- `jigy context <identifier>` command with `--max/-j/-m` flags
- Graph neighborhood exploration for specs, outcomes, goals, functions, tests
- Asymmetric traversal: full ancestors, budget-limited descendants
- JSON response per S-113 schema

**JIG Summary:**

| Planned | Actual | Node | Notes |
|---------|--------|------|-------|
| CREATE | ✓ CREATED | O-030 | Graph Neighborhood Exploration |
| CREATE | ✓ CREATED | S-110 | Context CLI Command |
| CREATE | ✓ CREATED | S-111 | Context Identifier Resolution |
| CREATE | ✓ CREATED | S-112 | Context Graph Traversal |
| CREATE | ✓ CREATED | S-113 | Context Response Schema |
| REUSE | ✓ REUSED | O-019 | Intuitive CLI Experience |
| REUSE | ✓ REUSED | S-057 | Project Root Auto-Discovery |
| REUSE | ✓ REUSED | S-093 | Universal Output Format Flags |

| Planned | Actual | Brick | Notes |
|---------|--------|-------|-------|
| MODIFY | ✓ MODIFIED | B-cli | Added M-jig.cli.context |
| FORBIDDEN | ✓ UNTOUCHED | B-decorators | |
| FORBIDDEN | ✓ UNTOUCHED | B-intent-graph | |
| FORBIDDEN | ✓ UNTOUCHED | B-impl-graph | |
| FORBIDDEN | ✓ UNTOUCHED | B-verification-graph | |

Decorators added: 4 implements, 27 verifies (46 tests total)

Final validation: Validated 96 specs, 26 outcomes, 15 bricks. 1088 tests passed.

**Clean Break Actions:**
- [x] No deprecated O/S nodes to delete (new feature)
- [x] No legacy code to delete (new feature)
- [x] Final jigy rebuild && jigy validate passed

**Reflection Roll-Up:**
- Repeatable wins: TDD approach kept WUs focused; sub-agent reports accurate
- Systemic frictions: None significant
- Open questions: None
