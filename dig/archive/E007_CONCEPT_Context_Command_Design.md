---
title: "Context Command Design"
type: concept
status: implemented
decision: completed
created: 1737158400
created_human: "2026-01-17 18:00 CST"
parent: "[[E006_SCOPE_JIG_Init_And_Skills]]"
children: []
---
# Context Command Design

## Core Insight

`jigy context <foo>` is a universal graph lookup. Start from any identifier — spec, outcome, function, test, file path, keyword — and traverse the graph to show connected context. The "fill" is what's connected. Gaps are visible as absence.

This makes `jigy context` the workhorse of JIG. One command replaces:
- "What does this spec require?"
- "What implements this?"
- "Why does this code exist?"
- "What's untested?"
- "How does this file relate to the architecture?"

---

## The Three Graphs

JIG maintains three graphs that join on spec IDs:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INTENT GRAPH                                │
│  Charter ─► Goals ─► Outcomes ─► Specs ◄─ Architecture              │
│                         │           │                               │
│                         │           │ (join on spec ID)             │
└─────────────────────────┼───────────┼───────────────────────────────┘
                          │           │
              ┌───────────┘           └───────────┐
              │                                   │
              ▼                                   ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│      IMPL GRAPH             │   │      VERIFY GRAPH           │
│  Modules ─► Classes         │   │  Test Files ─► Test Funcs   │
│         ─► Functions        │   │                             │
│              │              │   │              │              │
│   @jig.implements("S-###")  │   │   @jig.verifies("S-###")    │
└─────────────────────────────┘   └─────────────────────────────┘
```

**Join keys:**
- Intent ↔ Impl: spec ID in `@jig.implements("S-###")`
- Intent ↔ Verify: spec ID in `@jig.verifies("S-###")`
- Impl ↔ Verify: function coverage (which tests exercise which functions)

---

## What `<foo>` Can Be

| Input Type | Examples | Resolution |
|------------|----------|------------|
| Spec ID | `S-042`, `S-001` | Direct lookup in intent graph |
| Outcome ID | `O-012`, `O-101` | Direct lookup in intent graph |
| Architecture ID | `A-030` | Direct lookup in intent graph |
| Goal ID | `G-1`, `G-2` | Direct lookup in intent graph (via Charter) |
| Brick ID | `B-cli`, `B-crdt` | Lookup in bricks.yaml |
| Function ID | `F-jig.cli.main.run` | Lookup in impl graph |
| Module ID | `M-jig.cli.main` | Lookup in impl graph, expand to functions |
| Class ID | `C-jig.Parser` | Lookup in impl graph, expand to methods |
| Test ID | `T-test_cli.test_validate` | Lookup in verify graph |
| File path | `src/jig/cli/main.py` | Find all functions in file |
| Line reference | `src/jig/cli/main.py:42` | Find function containing line |
| Keyword | `"validate"` | Fuzzy search across all graphs |

**Resolution priority:**
1. Exact ID match (pattern-based: S-###, O-###, F-*, etc.)
2. File path (if path exists on disk)
3. Keyword search (fallback)

---

## Approach 1: Node-Centric Traversal

**Philosophy:** Start from resolved node, expand outward along edges. Fixed depth, show immediate neighborhood.

```bash
$ jigy context S-042
```

**Algorithm:**
1. Parse input, resolve to node (S-042 → spec node)
2. Load relevant graph(s)
3. Traverse edges from node:
   - Upward: outcomes, architecture, goals
   - Downward: implementations, tests
   - Lateral: related specs (same outcome)
4. Format neighborhood as output

**Traversal depth:**
- Primary: immediate edges (depth 1)
- Secondary: one hop further for key relationships (depth 2)
- Configurable with `--depth N`

**Pros:**
- Simple mental model
- Predictable output size
- Easy to implement

**Cons:**
- Fixed depth may miss important distant nodes
- Doesn't handle "find path between X and Y"

**Example output:**
```
S-042: CRDT Value Observation
═══════════════════════════════
UPWARD
  Outcome: O-012 (Real-time Collaboration)
    Goal: G-2 (Distributed Consistency)

IMPLEMENTATIONS (2)
  F-jig.crdt.observe.subscribe  src/crdt/observe.py:45  B-crdt
  F-jig.crdt.observe.notify     src/crdt/observe.py:78  B-crdt

TESTS (1)
  T-test_observe.test_subscribe  tests/test_observe.py:23

RELATED (same outcome)
  S-040  Real-time Sync Protocol     2 impl, 2 tests
  S-044  Offline Queue               0 impl, 0 tests
```

---

## Approach 2: Query Language

**Philosophy:** Provide a mini DSL for graph traversal. Power users and agents can ask specific questions.

**Syntax:**
```
<start> [-> | <-] <edge_type> [-> | <-] <edge_type> ...
```

- `->` follow edge forward
- `<-` follow edge backward

**Examples:**
```bash
# What implements S-042?
jigy context "S-042 -> implements"

# What specs does O-012 contain, and what implements them?
jigy context "O-012 -> specs -> implements"

# What spec does this file implement? (reverse)
jigy context "src/foo.py <- implements <- specs"

# Full chain from goal to tests
jigy context "G-1 -> outcomes -> specs -> implements -> tests"
```

**Edge types:**
| Edge | Forward meaning | Reverse meaning |
|------|-----------------|-----------------|
| `outcomes` | goal/arch → outcomes | outcome → goal/arch |
| `specs` | outcome → specs | spec → outcome |
| `implements` | spec → functions | function → spec |
| `verifies` | spec → tests | test → spec |
| `brick` | function → brick | brick → functions |
| `layer` | brick → layer | layer → bricks |

**Pros:**
- Maximum flexibility
- Composable queries
- Agents can ask precise questions
- Supports path-finding

**Cons:**
- Learning curve
- Parser complexity
- Overkill for common cases
- Error handling for invalid paths

**Implementation complexity:** Medium-high. Need parser, path validator, cycle detection.

---

## Approach 3: Smart Resolution + Fixed Views

**Philosophy:** Resolve input to canonical node type, then display a view optimized for that type. No query language — just smart defaults.

**Views by node type:**

### Spec View (`S-###`)
```
S-042: CRDT Value Observation
═══════════════════════════════
Statement: Observers receive value updates within bounded time.

Invariants:
  • Subscription is idempotent
  • Notification order matches causal order
  • Unsubscribe stops all future notifications

Outcome: O-012 (Real-time Collaboration)
Architecture: A-030 (CRDT Design)

Implementations:
  ✓ F-jig.crdt.observe.subscribe   src/crdt/observe.py:45
  ✓ F-jig.crdt.observe.notify      src/crdt/observe.py:78

Tests:
  ✓ T-test_observe.test_subscribe  tests/test_observe.py:23
  ✗ (no test for notify)

Status: PARTIAL (2 impl, 1/2 tested)
```

### Outcome View (`O-###`)
```
O-012: Real-time Collaboration
════════════════════════════════
Goals: G-2 (Distributed Consistency)

Specs (4):
  S-040  Real-time Sync Protocol    COMPLETE    2/2 impl  2/2 tests
  S-042  CRDT Value Observation     PARTIAL     2/2 impl  1/2 tests
  S-043  Conflict Resolution        COMPLETE    3/3 impl  3/3 tests
  S-044  Offline Queue              NONE        0/2 impl  0/0 tests

Coverage: 7/9 functions implemented, 6/9 tested
```

### Function View (`F-*` or file path)
```
F-jig.crdt.observe.subscribe
══════════════════════════════
File: src/crdt/observe.py:45
Brick: B-crdt (layer 1, tower: core)

def subscribe(self, callback: Callable) -> Subscription:
    """Subscribe to value changes."""

Implements: S-042 (CRDT Value Observation)
Tested by: T-test_observe.test_subscribe

Spec requirements:
  • Subscription is idempotent
  • Unsubscribe stops all future notifications
```

### File View (path)
```
src/crdt/observe.py
═════════════════════
Brick: B-crdt (layer 1)
Functions: 5

  Line  Function                     Spec     Tests
  ────  ────────────────────────     ─────    ─────
   12   CrdtObserver.__init__        —        —
   28   CrdtObserver.subscribe       S-042    1
   45   CrdtObserver.unsubscribe     S-042    0 ⚠
   78   CrdtObserver.notify          S-042    0 ⚠
  102   CrdtObserver._cleanup        —        —

Coverage: 3/5 functions have specs, 1/3 have tests
Orphans: __init__, _cleanup (no spec — may be OK)
```

### Brick View (`B-*`)
```
B-crdt: CRDT Implementation
═════════════════════════════
Layer: 1 (Core)
Tower: core

Modules (2):
  M-jig.crdt.observe     5 functions    3 specs    1 test
  M-jig.crdt.merge       8 functions    4 specs    4 tests

Depends on: B-foundation (layer 0)
Depended by: B-sync (layer 2)

Specs covered: S-040, S-042, S-043, S-044
```

**Pros:**
- Optimized display per node type
- No learning curve
- "Just works" for common cases
- Easy to extend with new views

**Cons:**
- Less flexible than query language
- Views may not answer all questions
- Need to maintain per-type logic

---

## Approach 4: Contextual Relevance Scoring

**Philosophy:** Given a starting point, score all reachable nodes by relevance. Return top N most relevant.

**Algorithm:**
1. BFS/DFS from starting node
2. Score each reached node:
   - Distance penalty: `score = 1.0 / (1 + distance)`
   - Edge type weight: implements (1.0) > verifies (0.9) > related (0.5)
   - Node type weight: spec (1.0) > function (0.8) > test (0.7)
   - Recency bonus: recently modified files score higher
3. Sort by score, return top K

```bash
$ jigy context S-042 --top 10
Showing 10 most relevant nodes to S-042:

  Score  Node                              Relationship
  ─────  ────                              ────────────
  1.00   S-042                             (self)
  0.95   F-jig.crdt.observe.subscribe      implements
  0.95   F-jig.crdt.observe.notify         implements
  0.90   T-test_observe.test_subscribe     verifies
  0.85   O-012                             parent outcome
  0.60   S-040                             sibling spec
  0.60   S-043                             sibling spec
  0.55   B-crdt                            brick
  0.40   G-2                               transitive goal
  0.35   A-030                             architecture
```

**Pros:**
- Handles large graphs gracefully
- Finds non-obvious connections
- Configurable depth/breadth
- Good for "explore around X"

**Cons:**
- Scoring heuristics are arbitrary
- Hard to explain why something ranked high/low
- May miss important but distant nodes
- Computation cost for large graphs

---

## Approach 5: Diff-Based Context

**Philosophy:** Show what changed since a reference point. Useful for "what happened to this spec since last week?"

```bash
$ jigy context S-042 --since "3 days ago"
$ jigy context S-042 --since abc123f  # git commit
$ jigy context S-042 --diff HEAD~5
```

**Output shows:**
- New implementations added
- Tests added/removed
- Spec text changes
- Coverage changes

**Pros:**
- Answers "what changed?"
- Useful for code review
- Git-aware

**Cons:**
- Requires git integration
- Different use case than exploration
- Could be separate command (`jigy diff`?)

---

## Gap Detection as Absence

**Key insight:** Don't build separate audit logic. Gaps are visible as absence in context output.

| What you're viewing | Gap shows as |
|---------------------|--------------|
| Spec | "Implementations: (none)" or partial list |
| Spec | "Tests: (none)" or "⚠ no test for X" |
| Function | "Implements: (none)" → orphan |
| Function | "Tests: (none)" → untested |
| File | Functions without specs listed as orphans |
| Outcome | Specs with 0/N impl or 0/N tests |

**Example with gaps visible:**
```
S-044: Offline Queue
═════════════════════
Outcome: O-012 (Real-time Collaboration)

Implementations: (none)
Tests: (none)

Status: UNIMPLEMENTED

Hint: This spec has no implementations. Use @jig.implements("S-044")
      to link code, or /jig-implement S-044 to start.
```

The context command becomes diagnostic by showing what's missing alongside what's present. No separate `jigy audit` needed for basic gap detection.

---

## Bidirectional Traversal

The power comes from traversing both directions:

**Forward (top-down) — "What implements this?"**
```
Goal → Outcomes → Specs → Functions → Tests
```

**Backward (bottom-up) — "Why does this exist?"**
```
File → Functions → Specs → Outcomes → Goals
```

Same command, resolution determines direction:
```bash
jigy context G-1              # forward from goal
jigy context src/crdt/foo.py  # backward from file
jigy context S-042            # both directions (show parents and children)
```

---

## Output Formats

Per DJ001/DJ002, three modes:

### Human (default)
Rich terminal output with structure, status indicators, hints.

### JSON (`-j`)
```json
{
  "node": {
    "id": "S-042",
    "type": "spec",
    "title": "CRDT Value Observation"
  },
  "upward": {
    "outcome": {"id": "O-012", "title": "Real-time Collaboration"},
    "goals": [{"id": "G-2", "title": "Distributed Consistency"}]
  },
  "implements": [
    {"id": "F-jig.crdt.observe.subscribe", "file": "src/crdt/observe.py", "line": 45},
    {"id": "F-jig.crdt.observe.notify", "file": "src/crdt/observe.py", "line": 78}
  ],
  "verifies": [
    {"id": "T-test_observe.test_subscribe", "file": "tests/test_observe.py", "line": 23}
  ],
  "status": "partial",
  "gaps": [
    {"type": "missing_test", "function": "F-jig.crdt.observe.notify"}
  ]
}
```

### Markdown (`-m`)
```markdown
# S-042: CRDT Value Observation

**Outcome:** O-012 (Real-time Collaboration)
**Status:** PARTIAL (2 impl, 1/2 tested)

## Statement
Observers receive value updates within bounded time.

## Implementations
| Function | File | Line | Tested |
|----------|------|------|--------|
| `subscribe` | src/crdt/observe.py | 45 | ✓ |
| `notify` | src/crdt/observe.py | 78 | ✗ |

## Tests
- `T-test_observe.test_subscribe` — tests/test_observe.py:23

## Gaps
- ⚠️ `notify` function has no test
```

---

## Verbose Mode (`-v`)

Adds detail without changing structure:
- Full spec body (statement, invariants, verification criteria)
- Function signatures and docstrings
- Test assertions
- Brick layer/tower details
- File modification timestamps
- Git blame info (who last touched)

---

## Recommendation

**Approach 3 (Smart Resolution + Fixed Views)** with elements from others:

1. **Smart resolution** handles any input (Approach 3)
2. **Fixed views per node type** optimized for common questions (Approach 3)
3. **Bidirectional traversal** following edges (Approach 1)
4. **Gaps as absence** — no separate audit logic
5. **Three output formats** per DJ001

**Why not query language (Approach 2)?**
- 80/20 rule: fixed views handle 80% of questions
- Agents can make multiple calls instead of complex queries
- Lower implementation cost
- Can add query language later if needed

**Why not relevance scoring (Approach 4)?**
- Arbitrary heuristics hard to explain
- Fixed views are more predictable
- Can add as `--explore` mode later

---

## Implementation Sketch

```python
def context(identifier: str, format: OutputFormat, verbose: bool):
    # 1. Resolve identifier to node
    node = resolve(identifier)  # Returns (graph, node_type, node_id)

    # 2. Load relevant graphs
    intent = load_intent_graph()
    impl = load_impl_graph()
    verify = load_verify_graph()

    # 3. Dispatch to view based on node type
    match node.type:
        case "spec":
            data = build_spec_view(node, intent, impl, verify)
        case "outcome":
            data = build_outcome_view(node, intent, impl, verify)
        case "function":
            data = build_function_view(node, intent, impl, verify)
        case "file":
            data = build_file_view(node, intent, impl, verify)
        case "brick":
            data = build_brick_view(node, intent, impl, verify)
        # ... etc

    # 4. Format output
    match format:
        case OutputFormat.HUMAN:
            return format_human(data, verbose)
        case OutputFormat.JSON:
            return format_json(data, verbose)
        case OutputFormat.MARKDOWN:
            return format_markdown(data, verbose)
```

**Resolution logic:**
```python
def resolve(identifier: str) -> Node:
    # Pattern matching for IDs
    if re.match(r'^S-\d+$', identifier):
        return Node("spec", identifier, "intent")
    if re.match(r'^O-\d+$', identifier):
        return Node("outcome", identifier, "intent")
    if re.match(r'^F-', identifier):
        return Node("function", identifier, "impl")
    if re.match(r'^T-', identifier):
        return Node("test", identifier, "verify")
    if re.match(r'^B-', identifier):
        return Node("brick", identifier, "bricks")

    # File path
    if Path(identifier).exists():
        return Node("file", identifier, "impl")

    # Line reference (file:line)
    if ':' in identifier and Path(identifier.split(':')[0]).exists():
        return resolve_line_reference(identifier)

    # Keyword search fallback
    return fuzzy_search(identifier)
```

---

## Open Questions

1. **Should `jigy context` with no argument show project overview?**
   - Yes: convenient, matches `digy context`
   - No: explicit is better, use `jigy show` for overview

2. **How deep should traversal go by default?**
   - Immediate edges only (depth 1)?
   - Include grandparents/grandchildren (depth 2)?
   - Configurable with `--depth`?

3. **Should gaps include hints/suggestions?**
   - "No implementations" vs "No implementations. Try: @jig.implements('S-042')"
   - Hints helpful for humans, noisy for agents?
   - Only in human mode, not JSON/markdown?

4. **How to handle ambiguous resolution?**
   - Multiple matches for keyword → list them, ask to clarify?
   - Multiple functions in same file match → show all?

---

## References

- [[jig/dig/archive/DJ002_SCOPE_CLI_Recommendations]] — Command structure, output formats
- [[jig/dig/archive/DJ001_CONCEPT_CLI_Design_Manifesto]] — Output principles
- [[E006_SCOPE_JIG_Init_And_Skills]] — Skills that will use this command
- [[contextJIG]] — Graph structure, node types
