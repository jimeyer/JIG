# Graph Storage Strategy

_Optimizing for Incremental Updates and Git Workflow_

**Date:** 2025-11-25
**Status:** Proposal
**Related:** AG017 (Minimal Graph Schema), AG014 (Implementation & Verification Graphs)

---

## The Core Problem

The Alignment Graph represents a codebase that changes constantly. Every code edit potentially invalidates parts of the graph. We need a storage strategy that:

1. **Minimizes git churn** - Small code changes shouldn't rewrite entire graph files
2. **Enables fast incremental updates** - Only re-analyze what changed
3. **Supports efficient queries** - Compute metrics on demand
4. **Stays simple** - Don't over-engineer for problems we don't have yet
5. **Remains human-inspectable** - Developers should understand what's stored

The naive approach (one big JSON file, rebuild everything) fails criteria #1 and #2. Let's explore alternatives.

---

## Question 1: Storage Format

### Option A: JSON (Current Proposal)

**Format:**
```json
{
  "nodes": {
    "F-auth.session.authenticate": {
      "type": "function",
      "file": "src/auth/session.py",
      "brick": "BRICK-AUTH",
      "implements": ["S-AUTH-001"],
      "calls": ["F-auth.tokens.validate"]
    }
  }
}
```

**Pros:**
- ✓ Human-readable
- ✓ Universal tooling (jq, parsers in every language)
- ✓ Simple to generate and parse
- ✓ Good git diff visualization

**Cons:**
- ✗ Must rewrite entire file on any change
- ✗ No incremental update support
- ✗ No indexing (full scan to find node)
- ✗ Large files (though gzip compresses well)

**Verdict:** Good for **intent-graph** (changes rarely), problematic for **implementation-graph** (changes constantly).

---

### Option B: NDJSON (Newline-Delimited JSON)

**Format:**
```json
{"id":"F-auth.session.authenticate","type":"function","file":"src/auth/session.py","brick":"BRICK-AUTH","implements":["S-AUTH-001"],"calls":["F-auth.tokens.validate"]}
{"id":"F-auth.session.logout","type":"function","file":"src/auth/session.py","brick":"BRICK-AUTH","implements":[],"calls":[]}
{"id":"F-auth.tokens.validate","type":"function","file":"src/auth/tokens.py","brick":"BRICK-AUTH","implements":["S-AUTH-001"],"calls":[]}
```

**Pros:**
- ✓ One node per line
- ✓ Git diff shows exactly which nodes changed
- ✓ Can grep/sed/awk individual nodes
- ✓ Streaming processing (don't load entire file)
- ✓ Can sort by ID for stable diffs
- ✓ Easy to update specific lines

**Cons:**
- ✗ Not as human-readable (no pretty-printing)
- ✗ Still rewrites entire file (but diff is clean)
- ✗ No schema validation (must validate per-line)

**Verdict:** **Much better git diffs** than regular JSON. Still requires full rewrite but changes are localized to specific lines.

**Example git diff:**
```diff
 {"id":"F-auth.session.authenticate","type":"function","calls":["F-auth.tokens.validate"]}
-{"id":"F-auth.session.logout","type":"function","calls":[]}
+{"id":"F-auth.session.logout","type":"function","calls":["F-utils.cleanup"]}
 {"id":"F-auth.tokens.validate","type":"function","calls":[]}
```

Only the changed node shows in the diff, not the entire file.

---

### Option C: SQLite Database

**Format:**
```sql
-- Tables
CREATE TABLE impl_nodes (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  file TEXT NOT NULL,
  brick TEXT,
  data JSON  -- rest of node as JSON blob
);

CREATE TABLE edges (
  source TEXT,
  target TEXT,
  edge_type TEXT,
  PRIMARY KEY (source, target, edge_type)
);

-- Indexes for fast queries
CREATE INDEX idx_brick ON impl_nodes(brick);
CREATE INDEX idx_file ON impl_nodes(file);
CREATE INDEX idx_edge_source ON edges(source);
CREATE INDEX idx_edge_target ON edges(target);
```

**Pros:**
- ✓ **True incremental updates** (INSERT/UPDATE only changed rows)
- ✓ **Indexed queries** (instant lookups by brick, file, etc.)
- ✓ **Transactions** (atomic updates)
- ✓ **SQL queries** (no custom graph traversal code)
- ✓ **Single file** (portable, easy to manage)
- ✓ **Fast** (orders of magnitude faster than JSON parsing)

**Cons:**
- ✗ **Not human-readable** (binary format)
- ✗ **Bad git diffs** (binary changes, no meaningful diff)
- ✗ **Merge conflicts impossible to resolve** (binary)

**Verdict:** Excellent for **working storage**, terrible for **version control**.

---

### Option D: SQLite + JSON Export (Hybrid)

**Workflow:**
```
Development:
  .jig/graph.db               (SQLite, not committed, in .gitignore)

Commit time:
  jig/intent-graph.json       (exported from SQLite, committed)
  jig/implementation-graph.json
  jig/verification-graph.json
```

**How it works:**
1. Tools work with `.jig/graph.db` (fast, incremental)
2. Before commit: `jigy export` generates JSON files from SQLite
3. Commit JSON files to git (human-readable, diff-friendly)
4. After clone/pull: `jigy import` rebuilds `.jig/graph.db` from JSON

**Pros:**
- ✓ **Fast incremental updates** (SQLite during dev)
- ✓ **Good git diffs** (JSON in commits)
- ✓ **Human-inspectable** (JSON for review)
- ✓ **Fast queries** (SQLite for computation)
- ✓ **Best of both worlds**

**Cons:**
- ✗ More complex (two formats to maintain)
- ✗ Export step required (can automate with pre-commit hook)
- ✗ Potential for SQLite/JSON to get out of sync

**Verdict:** **Most practical for production use.** Complexity is manageable with good tooling.

---

### Option E: Per-Module Files

**Format:**
```
jig/impl/modules/
  auth.session.json          (all nodes from auth.session module)
  auth.tokens.json
  utils.io.json
  ...
jig/impl/index.json          (registry of all module files)
```

**auth.session.json:**
```json
{
  "module": "M-auth.session",
  "file": "src/auth/session.py",
  "brick": "BRICK-AUTH",
  "imports": ["M-auth.tokens", "M-utils.time"],
  "functions": {
    "F-auth.session.authenticate": {
      "type": "function",
      "implements": ["S-AUTH-001"],
      "calls": ["F-auth.tokens.validate"]
    },
    "F-auth.session.logout": {
      "type": "function",
      "implements": [],
      "calls": []
    }
  }
}
```

**index.json:**
```json
{
  "modules": [
    "jig/impl/modules/auth.session.json",
    "jig/impl/modules/auth.tokens.json",
    "jig/impl/modules/utils.io.json"
  ],
  "generated": "2025-11-25T12:00:00Z"
}
```

**Pros:**
- ✓ **Minimal git churn** (only changed modules rewritten)
- ✓ **Fine-grained diffs** (git shows which modules changed)
- ✓ **Parallel processing** (analyze/update modules independently)
- ✓ **Human-inspectable** (small JSON files)
- ✓ **Natural granularity** (module = file = unit of change)

**Cons:**
- ✗ More files to manage (but matches code structure)
- ✗ Cross-module queries require loading multiple files
- ✗ Index file still needs updating (but small)

**Verdict:** **Excellent middle ground.** Minimal git churn, still human-readable, natural granularity.

---

## Comparison Table

| Criterion | JSON | NDJSON | SQLite | SQLite+JSON | Per-Module |
|-----------|------|--------|--------|-------------|------------|
| Human-readable | ✓✓ | ✓ | ✗ | ✓✓ | ✓✓ |
| Git-friendly diffs | ✗ | ✓ | ✗✗ | ✓✓ | ✓✓ |
| Incremental updates | ✗ | ✗ | ✓✓ | ✓✓ | ✓ |
| Query performance | ✗ | ✗ | ✓✓ | ✓✓ | ✓ |
| Simplicity | ✓✓ | ✓✓ | ✓ | ✗ | ✓ |
| Minimal churn | ✗ | ✓ | ✗✗ | ✓✓ | ✓✓ |
| Tooling support | ✓✓ | ✓ | ✓✓ | ✓ | ✓ |

**Legend:** ✓✓ Excellent, ✓ Good, ✗ Poor, ✗✗ Very Poor

---

## Question 2: One File vs Three Files?

### Scenario 1: One Combined File

```
jig/alignment-graph.json
```

**Contains:** All three graphs (intent, implementation, verification) in one file.

**Pros:**
- ✓ Simpler to manage (one file to track)
- ✓ Cross-graph queries trivial (already loaded)
- ✓ Single source of truth
- ✓ Atomic updates (all graphs consistent)

**Cons:**
- ✗ **High git churn** - every code change rewrites the entire file (including intent)
- ✗ **Mixed update frequencies** - intent (rare) and impl (frequent) in same file
- ✗ **Large file** - harder to inspect, slower to parse
- ✗ **Can't rebuild parts** - must rebuild everything

**Git diff example:**
```diff
 {
   "intent": { ... },
-  "implementation": { "nodes": { ... 500 nodes ... } },
+  "implementation": { "nodes": { ... 500 nodes ... } },
   "verification": { ... }
 }
```

The entire file shows as changed even if only one function was modified.

---

### Scenario 2: Three Separate Files

```
jig/intent-graph.json
jig/implementation-graph.json
jig/verification-graph.json
```

**Pros:**
- ✓ **Minimal git churn** - only changed graph shows in diff
- ✓ **Matched to update frequency** - intent stable, impl volatile
- ✓ **Partial rebuilds** - rebuild impl without touching intent
- ✓ **Parallel processing** - rebuild all three graphs concurrently
- ✓ **Smaller files** - easier to inspect

**Cons:**
- ✗ More files to manage
- ✗ Cross-graph queries require loading all three
- ✗ Potential for inconsistency (if rebuilds fail mid-process)

**Git diff example:**
```diff
# Only implementation-graph.json shows changes
# intent-graph.json and verification-graph.json unchanged
```

Clean diffs that reflect actual changes.

---

### Verdict: Three Files

**Rationale:**
1. **Intent changes rarely** (design decisions, specs) - shouldn't trigger git diffs on every code edit
2. **Implementation changes constantly** - should show diffs, but not pollute intent history
3. **Verification changes on test runs** - separate lifecycle from code changes
4. **Git history clarity** - see which layer is changing: design vs implementation vs testing

**Example workflow:**
```bash
# Edit code
$ vim src/auth/session.py

# Rebuild only implementation graph
$ jigy impl rebuild
# Only implementation-graph.json changed

# Git diff shows:
modified: jig/implementation-graph.json
# intent-graph.json unchanged
# verification-graph.json unchanged
```

Clear separation of concerns in version control.

---

## Question 3: Fast Incremental Rebuilds

The key question: **How do we only rebuild what changed?**

### Strategy 1: File-Level Change Detection

**Algorithm:**
```python
def rebuild_implementation_graph():
    # Load previous graph
    prev_graph = load_json("jig/implementation-graph.json")
    new_graph = {"nodes": {}}

    # Get all Python files
    for py_file in glob("src/**/*.py"):
        # Check if file changed since last build
        current_hash = hash_file(py_file)
        prev_hash = prev_graph.get("file_hashes", {}).get(py_file)

        if current_hash == prev_hash:
            # File unchanged - copy nodes from prev_graph
            copy_nodes_from_file(prev_graph, new_graph, py_file)
        else:
            # File changed - re-analyze
            analyze_file(py_file, new_graph)

    # Store file hashes for next rebuild
    new_graph["file_hashes"] = {f: hash_file(f) for f in all_files}

    save_json("jig/implementation-graph.json", new_graph)
```

**Optimization:** Only parse changed files. For large codebases, this reduces rebuild time from 10s → <1s.

**Caveat:** Still rewrites entire JSON file (but computation is fast).

---

### Strategy 2: Per-Module Files + Change Detection

**Algorithm:**
```python
def rebuild_implementation_graph():
    for py_file in glob("src/**/*.py"):
        module_id = file_to_module_id(py_file)
        module_json = f"jig/impl/modules/{module_id}.json"

        # Check if file changed
        current_hash = hash_file(py_file)
        prev_hash = load_hash_from_module_json(module_json)

        if current_hash != prev_hash:
            # Re-analyze this module only
            nodes = analyze_file(py_file)
            save_json(module_json, {
                "module": module_id,
                "hash": current_hash,
                "nodes": nodes
            })
            # Only this file written

    # Update index (just list of modules)
    update_index("jig/impl/index.json")
```

**Result:**
- Only changed module files are rewritten
- Git shows exactly which modules changed
- Very fast rebuilds

**Example git diff:**
```diff
modified: jig/impl/modules/auth.session.json
# All other module files unchanged
```

---

### Strategy 3: SQLite Incremental Updates

**Algorithm:**
```python
def rebuild_implementation_graph():
    db = sqlite3.connect(".jig/graph.db")

    for py_file in glob("src/**/*.py"):
        # Check if file changed (store hash in DB)
        current_hash = hash_file(py_file)
        prev_hash = db.execute(
            "SELECT hash FROM file_hashes WHERE file = ?",
            (py_file,)
        ).fetchone()

        if current_hash != prev_hash:
            # Delete old nodes from this file
            db.execute(
                "DELETE FROM impl_nodes WHERE file = ?",
                (py_file,)
            )

            # Insert new nodes
            nodes = analyze_file(py_file)
            db.executemany(
                "INSERT INTO impl_nodes VALUES (?, ?, ?, ?, ?)",
                [(n.id, n.type, n.file, n.brick, json.dumps(n)) for n in nodes]
            )

            # Update hash
            db.execute(
                "REPLACE INTO file_hashes VALUES (?, ?)",
                (py_file, current_hash)
            )

    db.commit()
```

**Result:**
- Only changed rows in SQLite (true incremental)
- Instant rebuilds (just a few SQL INSERTs)
- No JSON rewriting during development

**Before commit:**
```bash
$ jigy export
# Exports SQLite → JSON for git
```

---

## Benchmark Estimates

**Scenario:** 1000 Python files, 10,000 functions, 1 file changed

| Strategy | Rebuild Time | Git Diff Size |
|----------|--------------|---------------|
| JSON (full rebuild) | 10s | 500 KB (entire file) |
| JSON (smart rebuild) | 0.5s | 500 KB (entire file) |
| NDJSON (smart rebuild) | 0.5s | 2 KB (changed lines) |
| Per-Module JSON | 0.1s | 5 KB (one module file) |
| SQLite (incremental) | 0.05s | N/A (export 500 KB) |
| SQLite + JSON export | 0.05s + 2s export | 500 KB (entire file) or 5 KB (NDJSON) |

**Takeaway:** Per-module JSON offers the best balance of speed and git-friendliness without complexity.

---

## Recommended Approach (Phased)

### Phase 1: MVP (Simplest)

**Storage:**
```
jig/intent-graph.json           (regular JSON)
jig/implementation-graph.ndjson  (NDJSON for better diffs)
jig/verification-graph.ndjson
```

**Rebuild strategy:**
- Parse only changed files (file hash tracking)
- Rewrite entire NDJSON file (but diff is clean)
- Accept 0.5s rebuild time

**Pros:**
- Simple to implement
- Good git diffs (NDJSON)
- Fast enough for most projects

---

### Phase 2: Optimization (If Needed)

**Storage:**
```
jig/impl/modules/
  auth.session.json
  auth.tokens.json
  ...
jig/impl/index.json
```

**Rebuild strategy:**
- Per-module granularity
- Only rewrite changed module files
- Very fast (<0.1s for single file change)

**Pros:**
- Minimal git churn
- Fast rebuilds
- Still human-readable

---

### Phase 3: Advanced (If Scaling Issues)

**Storage:**
```
.jig/graph.db                    (SQLite, in .gitignore)
jig/intent-graph.json            (exported)
jig/impl/modules/*.json          (exported per-module)
jig/verification-graph.json      (exported)
```

**Rebuild strategy:**
- SQLite for incremental updates
- Export to JSON on commit (pre-commit hook)
- Per-module export for implementation graph

**Pros:**
- Fastest rebuilds (true incremental)
- Minimal git churn
- Powerful queries

**Cons:**
- More complexity
- Two representations to maintain

---

## Specific Recommendations

### For Intent Graph
**Format:** Regular JSON (single file)
**Rationale:** Changes when markdown files or brick definitions change (not as frequently as code), needs pretty-printing for review

```
jig/intent-graph.json
```

**Source artifacts (human-authored):**
- `jig/outcomes/*.md` (YAML frontmatter)
- `jig/specs/*.md` (YAML frontmatter)
- `bricks/*.brick.yaml` (brick definitions)
- `jig/subsystems.yaml` (optional subsystem groupings)

**Rebuild triggers:**
- New/modified/deleted markdown files in `jig/`
- Changes to brick definitions
- Changes to subsystem groupings

---

### For Implementation Graph
**Phase 1:** NDJSON (single file)
**Phase 2:** Per-module JSON

**Rationale:** Changes frequently (every code edit), needs good git diffs, benefits from per-module granularity

```
# Phase 1
jig/implementation-graph.ndjson

# Phase 2 (if git diffs still too large)
jig/impl/modules/*.json
jig/impl/index.json
```

**Source artifacts (human-authored):**
- `src/**/*.py` (code structure via AST)
- `@jig.implements("S-*")` decorators on functions
- `@jig.brick("BRICK-*")` decorators on functions (optional)

**Rebuild triggers:**
- Code file changes (new/modified/deleted `.py` files)
- New/modified `@jig.implements` decorators
- New/modified `@jig.brick` decorators

---

### For Verification Graph
**Format:** NDJSON (single file)
**Rationale:** Changes with test runs (not as frequently as implementation), NDJSON sufficient

```
jig/verification-graph.ndjson
```

**Source artifacts (human-authored):**
- `tests/**/*.py` (test structure via pytest discovery)
- `@jig.verifies("S-*", "O-*")` decorators on test functions
- `@jig.brick("BRICK-*")` decorators on tests (optional)
- Coverage data (from pytest-cov or coverage.py)

**Rebuild triggers:**
- Test code changes
- New/modified `@jig.verifies` decorators
- Test execution (coverage data changes)

---

## Handling Cross-Graph Queries

With three separate files, how do cross-graph queries work?

### Option 1: Load All Three (Simple)

```python
def load_alignment_graph():
    intent = load_json("jig/intent-graph.json")
    impl = load_ndjson("jig/implementation-graph.ndjson")
    verify = load_ndjson("jig/verification-graph.ndjson")

    return AlignmentGraph(intent, impl, verify)

# All queries work in memory
ag = load_alignment_graph()
ag.query("unverified_specs")
```

**Performance:** Fine for <100K nodes. Modern machines load/parse JSON fast.

---

### Option 2: Lazy Loading (Optimized)

```python
class AlignmentGraph:
    def __init__(self):
        self._intent = None
        self._impl = None
        self._verify = None

    @property
    def intent(self):
        if self._intent is None:
            self._intent = load_json("jig/intent-graph.json")
        return self._intent

    # Only load graphs when needed
```

---

### Option 3: Unified Query API (SQLite)

```python
# If using SQLite backend
db = sqlite3.connect(".jig/graph.db")

# Cross-graph query
unverified_specs = db.execute("""
    SELECT s.id, s.content
    FROM intent_nodes s
    LEFT JOIN verification_edges ve ON s.id = ve.intent_id
    WHERE s.type = 'specification'
      AND ve.test_id IS NULL
""").fetchall()
```

**Performance:** Instant (indexed queries).

---

## File Hash Tracking for Incremental Rebuilds

**Problem:** How do we know which files changed since last rebuild?

**Solution:** Store file hashes in the graph metadata.

### In NDJSON Format:

```json
{"_meta":{"file_hashes":{"src/auth/session.py":"a3f2e9d7...","src/auth/tokens.py":"b8c1f4e2..."}}}
{"id":"F-auth.session.authenticate","type":"function",...}
{"id":"F-auth.session.logout","type":"function",...}
```

First line is metadata (prefixed with `_meta`), rest are nodes.

### In Per-Module Format:

**auth.session.json:**
```json
{
  "module": "M-auth.session",
  "file": "src/auth/session.py",
  "file_hash": "a3f2e9d7...",
  "nodes": { ... }
}
```

Hash stored per module file.

### Rebuild Algorithm:

```python
def rebuild():
    for py_file in all_python_files():
        current_hash = sha256(read_file(py_file))
        stored_hash = get_stored_hash(py_file)

        if current_hash != stored_hash:
            # Re-analyze this file
            analyze_and_update(py_file)
```

---

## Example: Complete Workflow (Phase 1)

### Initial Build

```bash
$ jigy index
Scanning jig/ directory for Outcome/Spec markdown files...
  Found 15 Outcomes, 45 Specifications
Loading brick definitions from bricks/...
  Found 10 bricks
Parsing YAML frontmatter...
Building intent graph...
Writing jig/intent-graph.json... Done.
Rebuild complete in 0.8s

$ jigy impl rebuild
Scanning src/ for Python files...
  Found 87 files, 456 functions
Parsing AST and extracting @jig decorators...
  Found 142 @jig.implements annotations
  Found 24 @jig.brick annotations
  Analyzing... 100% [====================]
Writing jig/implementation-graph.ndjson... Done.
Rebuild complete in 2.3s

$ jigy verify rebuild --run-tests
Running tests with coverage...
  320 tests passed
  Coverage: 81.4%
Discovering tests and parsing @jig decorators...
  Found 89 @jig.verifies annotations
Analyzing test coverage...
Writing jig/verification-graph.ndjson... Done.
Rebuild complete in 6.8s

$ git status
modified: jig/intent-graph.json
modified: jig/implementation-graph.ndjson
modified: jig/verification-graph.ndjson
```

---

### Incremental Update (After Code Edit)

```bash
$ vim src/auth/session.py  # Edit one function, add @jig.implements decorator

$ jigy impl rebuild
Checking for changes...
  1 file changed: src/auth/session.py
  Re-analyzing 1 file...
  Extracting @jig decorators...
Writing jig/implementation-graph.ndjson... Done.
Rebuild complete in 0.3s

$ git diff jig/implementation-graph.ndjson
-{"id":"F-auth.session.authenticate","calls":["F-auth.tokens.validate"],"implements":[]}
+{"id":"F-auth.session.authenticate","calls":["F-auth.tokens.validate","F-utils.log"],"implements":["S-AUTH-001"]}

# Clean diff - only the changed function
```

---

### Incremental Update (After Markdown Edit)

```bash
$ vim jig/specs/auth.md  # Modify a specification

$ jigy index
Checking for changes...
  1 file changed: jig/specs/auth.md
  Re-parsing frontmatter...
Writing jig/intent-graph.json... Done.
Rebuild complete in 0.1s

$ git diff jig/intent-graph.json
-  "S-AUTH-001": {"type":"specification","content":"Token expiration after 15min",...}
+  "S-AUTH-001": {"type":"specification","content":"Token expiration after 20min",...}

# Only the changed spec node shows in diff
```

---

### Query Example

```bash
$ jigy status
Loading graphs...
  intent-graph.json (60 nodes)
  implementation-graph.ndjson (667 nodes)
  verification-graph.ndjson (320 nodes)

Computing alignment metrics...
  Intent → Implementation: 95.6%
  Intent → Verification: 84.4%
  Implementation → Verification: 85.3%

Overall Alignment: 85.1% (good)
```

All metrics computed on-demand from the three graph files.

---

## Decision Matrix

| If your codebase is... | Use this storage |
|------------------------|------------------|
| < 100 files, just starting | Regular JSON (3 files) |
| 100-500 files, active development | NDJSON (3 files) |
| 500-2000 files, team workflow | Per-module JSON |
| 2000+ files, complex queries | SQLite + JSON export |

---

## Open Questions

1. **Should we commit the graphs to git at all?**
   - Alternative: Generate on CI, keep `.jig/` in `.gitignore`
   - Pro: Smaller repo, no stale graphs
   - Con: Can't diff graph changes, can't browse without rebuild
   - **Recommendation:** Commit graphs - they ARE the derived build artifacts, like compiled binaries, but remain human-inspectable

2. **Should we use git hooks to auto-rebuild?**
   - `post-checkout`: Rebuild after branch switch
   - `post-merge`: Rebuild after pull
   - `pre-commit`: Rebuild and validate graphs before commit
   - Pro: Always up-to-date
   - Con: Slows down git operations
   - **Recommendation:** Optional, user-configurable (document how to set up)

3. **How do we handle merge conflicts in graph files?**
   - **Answer:** Regenerate from source artifacts (markdown, code, tests)
   - Source artifacts are authoritative, graphs are derived
   - On merge conflict: `jigy index && jigy impl rebuild && jigy verify rebuild`
   - Git never needs to merge graph files - just regenerate
   - **Strategy:** Add `.git/attributes` entry: `jig/*.json merge=union` or just regenerate on conflict

4. **What if @jig decorator and frontmatter are inconsistent?**
   - Example: Function has `@implements("S-AUTH-001")` but S-AUTH-001 doesn't exist in markdown
   - **Validation:** `jigy status` reports orphaned implementations
   - Intent graph is source of truth for spec IDs
   - Lint/CI should fail if decorators reference non-existent specs

---

## Conclusion

### Recommended Approach

**For MVP (Phase 1):**
- **Three separate files** (intent, implementation, verification)
- **Format:**
  - Intent: Regular JSON (pretty-printed, generated from markdown + brick definitions)
  - Implementation: NDJSON (good diffs, generated from code + `@jig` decorators)
  - Verification: NDJSON (good diffs, generated from tests + coverage + `@jig` decorators)
- **Source artifacts (human-authored):**
  - Markdown files with YAML frontmatter (`jig/outcomes/*.md`, `jig/specs/*.md`)
  - Brick definitions (`bricks/*.brick.yaml`)
  - `@jig.implements()` decorators on code
  - `@jig.verifies()` decorators on tests
- **Rebuild strategy:** File hash tracking, parse only changed files
- **Commit:** All three graph files + source artifacts to git

**For Production (Phase 2, if needed):**
- **Implementation graph:** Per-module JSON files
- **Verification graph:** NDJSON or per-module
- **Rebuild strategy:** Module-level granularity
- **Commit:** Per-module files (minimal git churn)

**For Scale (Phase 3, if needed):**
- **Working storage:** SQLite (`.jig/graph.db`, not committed)
- **Git storage:** JSON export (committed)
- **Rebuild strategy:** Incremental SQLite updates + export on commit
- **Commit:** Exported JSON (or per-module JSON for fine-grained diffs)

### Why Not One File?

Three files minimize git churn by separating concerns:
- **Intent** (design) changes when markdown/brick definitions change (infrequent)
- **Implementation** (code) changes when code is edited (frequent)
- **Verification** (tests) changes when tests run (test-run frequency)

**Source artifacts change at different rates:**
- Markdown files (design decisions) → stable
- Code files → constantly evolving
- Test runs → on-demand or CI

Combining them would create unnecessary git churn.

### Next Steps

1. Implement Phase 1 (NDJSON, three files)
2. Measure rebuild times and git diff sizes on real codebase
3. If git churn is manageable, stop there
4. If git churn is problematic, upgrade to Phase 2 (per-module)
5. If query performance is problematic, upgrade to Phase 3 (SQLite backend)

**Principle:** Start simple, optimize based on real-world pain points.

---

## References

- Git object storage: `.git/objects/` (content-addressed, incremental)
- NDJSON spec: http://ndjson.org/
- SQLite as application file format: https://sqlite.org/appfileformat.html
- AG017: Minimal Graph Schema
