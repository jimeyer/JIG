# What Beads Can Teach JIG

## Executive Summary

[Beads](https://github.com/steveyegge/beads) is a distributed, git-backed issue tracker designed specifically for AI coding agents. While JIG focuses on **alignment between specification, implementation, and tests**, Beads focuses on **persistent, structured memory for agent workflows**. The two systems are complementary, and Beads offers several architectural patterns that could enhance JIG.

---

## Key Lessons from Beads

### 1. Hash-Based IDs for Multi-Agent Workflows

**Beads Pattern:**
- Uses content-based hash IDs (e.g., `bd-a1b2`) instead of sequential IDs
- Prevents merge collisions when multiple agents create issues concurrently
- IDs start at 4 characters and scale progressively

**JIG Current State:**
- Uses sequential IDs: `S-001`, `O-001`, `B-auth`
- Works fine for single-developer workflows
- Could cause conflicts in multi-agent parallel development

**Potential Application:**
Consider hybrid IDs that preserve human readability while avoiding collisions:
```
S-auth-7f3a     # Semantic prefix + hash suffix
S-001-7f3a     # Sequential + hash for disambiguation
```

---

### 2. Three-Layer Data Model (SQLite Caching)

**Beads Pattern:**
```
CLI → SQLite (fast local) → JSONL (git-tracked) → Remote
```
- SQLite provides fast queries with indexes
- JSONL is the git-tracked source of truth
- 5-second debounce batches multiple operations before export

**JIG Current State:**
- NDJSON files are the only data layer
- Every query requires parsing the full graph files
- Rebuilds regenerate entire graphs from source

**Potential Application:**
Add a SQLite cache layer for JIG queries:
```
jig/generated/
├── intent-graph.ndjson      # Git-tracked source of truth
├── implementation-graph.ndjson
├── verification-graph.ndjson
└── .cache/
    └── jig.db              # SQLite cache (gitignored)
```

Benefits:
- Fast graph queries without full file parsing
- Incremental updates instead of full rebuilds
- Complex queries (e.g., "all specs in brick B-cli without tests")

---

### 3. Agent-Optimized Context Injection

**Beads Pattern:**
- `bd prime` injects ~1-2k tokens of workflow context
- Hooks auto-refresh context at SessionStart and PreCompact
- JSON output mode for machine parsing
- Explicitly avoids heavy context (10-50k token MCP schemas)

**JIG Current State:**
- No specific agent-facing commands
- Graph output is machine-readable but not agent-optimized
- No built-in context summarization

**Potential Application:**
Add a `jig prime` command that outputs:
```json
{
  "focus_brick": "B-cli",
  "ready_specs": ["S-071", "S-072"],
  "blocked_specs": [{"id": "S-073", "blocked_by": "S-071"}],
  "coverage_gaps": ["S-045 has no tests"],
  "recent_drift": ["F-main.py:parse_args no longer implements S-012"]
}
```

This gives agents actionable context in minimal tokens.

---

### 4. "Ready Work" Detection

**Beads Pattern:**
- `bd ready` lists tasks with no open blockers
- Dependency types: `blocks`, `parent-child`, `related`
- Agents cycle: get ready → claim → execute → close → repeat

**JIG Current State:**
- Specs exist but no "readiness" concept
- No explicit blocking relationships between specs
- Agents must manually determine what to work on

**Potential Application:**
Add spec dependencies and `jig ready` command:
```yaml
# In S-072.md frontmatter
---
id: S-072
type: specification
depends_on: [S-071]  # Blocked until S-071 is implemented
---
```

```bash
$ jig ready
Ready to implement (no blockers, no implementation):
  S-045: CLI error formatting
  S-078: Configuration validation

Blocked (waiting on dependencies):
  S-072: depends on S-071 (in progress)
```

---

### 5. Ephemeral Tracking (Wisps)

**Beads Pattern:**
- **Wisps**: Ephemeral child issues for execution steps
- Local-only (never exported to JSONL)
- Hard-deleted when squashed (no tombstones)
- Enables fast iteration without sync overhead

**JIG Current State:**
- All graph data is persistent and committed
- No concept of "work in progress" tracking
- Agent progress is invisible until decorators are added

**Potential Application:**
Add local-only tracking for implementation progress:
```
jig/local/           # gitignored
├── wip-specs.json   # Specs being worked on
├── claimed.json     # Agent-claimed work
└── session.json     # Current session context
```

This lets agents track their own progress without polluting the graph.

---

### 6. Daemon Architecture for Performance

**Beads Pattern:**
- Background daemon handles auto-sync
- RPC server via Unix socket (`.beads/bd.sock`)
- CLI tries daemon first, falls back to direct access
- Deferred background tasks

**JIG Current State:**
- All operations are synchronous CLI calls
- Every rebuild parses all source files
- No background processing

**Potential Application:**
Consider a `jig daemon` for:
- Watching source files for changes
- Incremental graph updates
- Pre-computed query results
- Background validation

---

### 7. Stealth Mode for Experimentation

**Beads Pattern:**
- `bd init --stealth` for local-only usage
- Doesn't commit `.beads/` to shared repo
- Contributor mode routes to separate location

**JIG Current State:**
- All JIG artifacts expected to be committed
- No way to experiment without affecting the repo

**Potential Application:**
```bash
$ jig init --local    # Creates jig/ but gitignores it
$ jig init --sandbox  # Uses ~/.jig-sandbox/ instead
```

Useful for:
- Trying JIG on existing projects
- Personal spec drafts before team review
- Agent experimentation

---

### 8. Molecule/Compound Workflow Concept

**Beads Pattern:**
- **Molecules**: Epics with workflow semantics
- Children execute in parallel unless dependencies exist
- "Bonding" connects molecules into compound workflows
- Agents traverse seamlessly across bonded work

**JIG Current State:**
- Outcomes → Specs hierarchy exists
- No explicit "workflow" or execution ordering
- No concept of parallel vs. sequential spec implementation

**Potential Application:**
Enhance Outcomes as "Implementation Plans":
```yaml
# O-005.md
---
id: O-005
type: outcome
specifies: [S-071, S-072, S-073]
execution:
  parallel: [S-071, S-072]  # Can be implemented together
  sequential:
    - after: [S-071, S-072]
      then: S-073           # Must wait for both
---
```

This guides agents on implementation order.

---

### 9. Content-Addressed Change Detection

**Beads Pattern:**
- Each entity carries a content hash
- Import logic: same ID + same hash = skip
- Different hash = update needed
- Enables efficient sync without full comparison

**JIG Current State:**
- `hashing.py` exists for staleness detection
- Used for rebuild optimization
- Could be extended for fine-grained change tracking

**Potential Application:**
Track content hashes per spec/function for:
- Detecting when spec text changed but implementation didn't update
- Identifying stale `@implements` decorators after function changes
- Efficient incremental validation

---

### 10. Explicit Separation of Human vs. Machine Artifacts

**Beads Pattern:**
- JSONL is machine-generated from SQLite
- Human edits happen through CLI, not file editing
- Clear boundary between user intent and system state

**JIG Current State:**
- Specs/Outcomes are human-authored (good)
- Graphs are machine-generated (good)
- `bricks.yaml` is human-edited but feels machine-like

**Potential Application:**
Consider making brick assignment more discoverable:
```python
# Instead of editing bricks.yaml directly
$ jig brick assign F-main.py:parse_args B-cli
$ jig brick move F-utils.py:helper B-core --dry-run
```

---

## Architectural Comparison

| Aspect | Beads | JIG |
|--------|-------|-----|
| **Primary Purpose** | Task tracking for agents | Alignment tracking |
| **Data Model** | Issue graph with dependencies | S-F-T triangle |
| **Storage** | JSONL + SQLite cache | NDJSON only |
| **IDs** | Hash-based (`bd-a1b2`) | Sequential (`S-001`) |
| **Agent Integration** | First-class (`bd prime`) | Implicit |
| **Local-only Mode** | Yes (stealth/contributor) | No |
| **Background Processing** | Daemon architecture | Synchronous CLI |
| **Conflict Prevention** | Content-addressed hashes | None (relies on git) |

---

## Recommended Priorities for JIG

### High Value, Lower Effort
1. **`jig prime` command** - Agent context injection (~1 day)
2. **`jig ready` command** - Identify unimplemented specs (~1 day)
3. **Spec dependencies** - `depends_on` in frontmatter (~2 days)

### High Value, Higher Effort
4. **SQLite cache layer** - Fast queries, incremental updates (~1 week)
5. **Local/ephemeral tracking** - WIP without commits (~3 days)
6. **Hash-based ID option** - Multi-agent collision prevention (~3 days)

### Nice to Have
7. **Daemon mode** - Background rebuilds and watching
8. **Stealth mode** - Local-only experimentation
9. **Molecule-style workflows** - Execution ordering in outcomes

---

## Conclusion

Beads and JIG solve different but complementary problems:

- **Beads**: "What should the agent work on next?"
- **JIG**: "Does the code align with its specifications?"

The most impactful lessons from Beads are:
1. **Token-conscious agent integration** - `jig prime` for minimal context
2. **Ready work detection** - `jig ready` for actionable next steps
3. **SQLite caching** - Performance without sacrificing git-native storage
4. **Hash-based IDs** - Collision prevention for multi-agent workflows

These additions would make JIG significantly more useful for AI-assisted development while preserving its core focus on specification-implementation-test alignment.
