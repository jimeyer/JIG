# S026: Evaluation - Binary Index with Rebuild-on-Demand Strategy

**Date**: 2025-11-22  
**Status**: Evaluation  
**Context**: Analyzing gitignored binary index with on-demand rebuilding at massive scale (100,000 nodes)

## Executive Summary

This evaluation analyzes treating `graph-index.msgpack` as a **build artifact** (like compiled binaries) rather than tracked source. At massive scale (100,000 nodes), this approach offers significant benefits but introduces critical workflow challenges.

**Key Finding**: Binary-only with rebuild-on-demand is viable at massive scale (100K+ nodes) but requires sophisticated staleness detection and cache invalidation to avoid developer frustration.

**Recommendation**: Implement **hybrid architecture** - gitignored binary index with intelligent rebuild triggers and fallback source-of-truth scanning.

---

## Scale Assumptions (1000x Current)

### Current Scale (JIG project)
- **Nodes**: ~100
- **YAML size**: 23KB
- **Parse time**: 15-20ms

### Massive Scale (Hypothetical large project)
- **Nodes**: 100,000
- **JSON size**: ~23MB (1000x)
- **MessagePack size**: ~10MB (compressed)
- **Parse time estimates**:
  - YAML: 15-20 seconds ❌ (unacceptable)
  - JSON: 3-5 seconds ⚠️ (painful)
  - MessagePack: 100-300ms ✅ (acceptable)

**Conclusion**: At 100K nodes, binary format becomes **necessary** for usability.

---

## Proposed Architecture: Gitignored Binary Index

### Core Concept
```
# .gitignore
jig/.graph-index.msgpack
jig/.graph-index.msgpack.timestamp

# Workflow
1. Developer runs: jigy status
2. System checks if .graph-index.msgpack exists
3. If missing/stale, rebuild from annotations
4. Load binary index (fast)
5. Execute command
```

### Comparison to Current Approach
| Aspect | Current (Git-tracked YAML) | Proposed (Gitignored Binary) |
|--------|---------------------------|------------------------------|
| **In Git** | ✅ Yes (23KB tracked) | ❌ No (build artifact) |
| **Parse Time** | 15-20ms @ 100 nodes | 100-300ms @ 100K nodes |
| **Rebuild Time** | N/A (committed) | ⚠️ Critical factor |
| **Developer Sync** | Automatic (git pull) | ⚠️ Manual/automatic rebuild |
| **Disk Space** | 23KB | 10MB (but gitignored) |
| **CI/CD** | No build step | ⚠️ Must rebuild on CI |

---

## Critical Analysis: Rebuild Time

### Rebuild Performance at Scale

The viability of this approach **hinges on rebuild speed**. Let's estimate:

#### Scanner Performance (S-JIGY-008 spec: <2s for 10K files)
```
Current spec: Scan 10,000 files in <2s
Projected:    Scan 100,000 files in <20s (linear scaling)
```

#### Index Build Performance
```python
# Components of index rebuild:
1. Scan codebase for @jig annotations
   - 100,000 source files
   - ~100,000 @jig-implements annotations
   - Estimated: 15-25 seconds

2. Load markdown nodes (O/S/T/C)
   - ~5,000 markdown files (5% ratio)
   - Parse YAML frontmatter
   - Estimated: 2-5 seconds

3. Build graph structure
   - 100,000 nodes
   - ~200,000 edges (avg 2 per node)
   - Estimated: 1-3 seconds

4. Serialize to MessagePack
   - 10MB output
   - Estimated: 0.5-1 second

TOTAL REBUILD TIME: 20-35 seconds
```

### Rebuild Frequency Analysis

**When does rebuild happen?**

| Scenario | Frequency | User Impact |
|----------|-----------|-------------|
| First clone | Once per clone | ⚠️ 20-35s delay |
| Git branch switch | Every branch switch | ❌ **PAINFUL** if frequent |
| Git pull with changes | Every pull | ❌ **PAINFUL** |
| File edit (local dev) | Continuous | ⚠️ Must detect staleness |
| CI/CD pipeline | Every pipeline run | ⚠️ 20-35s added to CI time |

### Developer Workflow Impact

#### Scenario 1: Morning Sync
```bash
$ git checkout main
$ git pull origin main
  Updated 15 files, 200 insertions(+), 150 deletions(-)

$ jigy status
  [Rebuilding graph index: 0/100000 files scanned...]
  [████████░░░░░░░░░░░░░░░░░░░░ 25%]
  [⏱️  23 seconds remaining]
```

**Impact**: 😤 **Frustrating** - User must wait 20-35s before ANY command works

#### Scenario 2: Quick Status Check
```bash
$ jigy status
  [Index stale, rebuilding...]
  ⏱️  27 seconds...

$ jigy status   # 5 seconds later, during rebuild
  ERROR: Index rebuild in progress, please wait...
```

**Impact**: 😤 **Very frustrating** - Blocks all JIG commands during rebuild

#### Scenario 3: CI/CD Pipeline
```yaml
# .github/workflows/test.yml
jobs:
  test:
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
      - name: Install dependencies
      - name: Rebuild JIG index
        run: jigy index rebuild  # ← 20-35 seconds added
      - name: Run tests
        run: pytest
```

**Impact**: ⚠️ **Acceptable** in CI, but adds cost

---

## Staleness Detection Strategies

The **hardest problem** is determining when to rebuild. Poor detection = wasted time or stale data.

### Strategy 1: Timestamp-Based (Naive)

```python
def is_index_stale(jig_root):
    """Check if any source file is newer than index."""
    index_path = jig_root / 'jig' / '.graph-index.msgpack'
    
    if not index_path.exists():
        return True
    
    index_mtime = index_path.stat().st_mtime
    
    # Check all source files
    for file in scan_all_files(jig_root):
        if file.stat().st_mtime > index_mtime:
            return True  # ← Found newer file
    
    return False
```

**Problems**:
- ❌ **Slow**: Must stat() 100,000 files (2-5 seconds)
- ❌ **False positives**: Any file touch triggers rebuild
- ❌ **Cross-machine**: Timestamps unreliable across git clones
- ❌ **Git operations**: Branch switches don't always update mtimes correctly

**Verdict**: ❌ **Unreliable** - Don't use timestamps alone

---

### Strategy 2: Git-Based Staleness (Better)

```python
def get_git_head_sha(jig_root):
    """Get current git HEAD SHA."""
    result = subprocess.run(
        ['git', 'rev-parse', 'HEAD'],
        cwd=jig_root,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def is_index_stale_git(jig_root):
    """Check if index was built for different git HEAD."""
    index_meta = jig_root / 'jig' / '.graph-index.meta.json'
    
    if not index_meta.exists():
        return True
    
    with open(index_meta) as f:
        meta = json.load(f)
    
    current_sha = get_git_head_sha(jig_root)
    return meta['git_sha'] != current_sha
```

**Metadata file**: `.graph-index.meta.json`
```json
{
  "built_at": "2025-11-22T10:30:00Z",
  "git_sha": "a1b2c3d4e5f6...",
  "node_count": 100000,
  "build_duration_ms": 23450,
  "scanner_version": "1.2.0"
}
```

**Advantages**:
- ✅ Fast check (just compare SHAs)
- ✅ Accurate for git operations (pull, checkout, merge)
- ✅ Cross-machine reliable
- ✅ Works with CI/CD

**Problems**:
- ⚠️ **Local edits**: Doesn't detect unstaged changes
- ⚠️ **Non-git projects**: Fails without git
- ⚠️ **Working tree dirty**: Need additional detection

**Verdict**: ✅ **Good foundation** - Use as primary method

---

### Strategy 3: Content Hash (Most Accurate)

```python
def compute_source_hash(jig_root):
    """Hash all relevant source files."""
    import hashlib
    
    hasher = hashlib.sha256()
    
    # Hash markdown nodes
    for md_file in sorted(jig_root.glob('jig/**/*.md')):
        hasher.update(md_file.read_bytes())
    
    # Hash code annotations (expensive!)
    scanner = AnnotationScanner(jig_root)
    for annotation in sorted(scanner.scan()):
        hasher.update(f"{annotation.file}:{annotation.line}".encode())
    
    return hasher.hexdigest()

def is_index_stale_content(jig_root):
    """Check if source content changed."""
    index_meta = jig_root / 'jig' / '.graph-index.meta.json'
    
    if not index_meta.exists():
        return True
    
    with open(index_meta) as f:
        meta = json.load(f)
    
    current_hash = compute_source_hash(jig_root)  # ← EXPENSIVE
    return meta['content_hash'] != current_hash
```

**Problems**:
- ❌ **Very slow**: Must read 100,000 files (15-20s)
- ❌ **Nearly as slow as rebuild**: Defeats the purpose
- ❌ **I/O intensive**: Hammers disk

**Verdict**: ❌ **Too slow** - Only use as fallback verification

---

### Strategy 4: Hybrid Staleness Detection (Recommended)

```python
def check_index_freshness(jig_root):
    """Multi-level staleness check (fast → slow fallback)."""
    
    # Level 1: Does index exist? (1ms)
    if not index_exists(jig_root):
        return RebuildReason.MISSING
    
    # Level 2: Git HEAD changed? (5-10ms)
    if git_head_changed(jig_root):
        return RebuildReason.GIT_HEAD_CHANGED
    
    # Level 3: Working tree dirty with relevant changes? (50-100ms)
    if working_tree_has_jig_changes(jig_root):
        return RebuildReason.DIRTY_WORKING_TREE
    
    # Level 4: Manual invalidation flag? (1ms)
    if manual_invalidation_exists(jig_root):
        return RebuildReason.MANUAL_INVALIDATION
    
    # Index is fresh
    return None

def working_tree_has_jig_changes(jig_root):
    """Check if uncommitted changes affect JIG nodes."""
    # Fast git check for modified files
    result = subprocess.run(
        ['git', 'diff', '--name-only', 'HEAD'],
        cwd=jig_root,
        capture_output=True,
        text=True
    )
    
    modified_files = result.stdout.splitlines()
    
    # Check if any modified file contains JIG annotations or is markdown node
    for file in modified_files:
        if file.endswith('.md') and 'jig/' in file:
            return True  # Markdown node changed
        if file.endswith(('.py', '.js', '.ts', '.java')):
            # Quick grep for @jig in changed files (fast)
            if has_jig_annotations(jig_root / file):
                return True
    
    return False
```

**Performance**:
- Fast path (index fresh): 10-20ms
- Slow path (dirty tree): 50-200ms
- Rebuild path: 20-35 seconds

**Advantages**:
- ✅ Fast common case (git HEAD check)
- ✅ Accurate for most scenarios
- ✅ Handles local edits (working tree check)
- ✅ Manual escape hatch (invalidation flag)

**Verdict**: ✅ **Best approach** - Recommended implementation

---

## User Experience Patterns

### Pattern 1: Automatic Background Rebuild

```python
# When staleness detected, offer choice:
$ jigy status

Graph index is stale (git HEAD changed: a1b2c3 → d4e5f6)
Rebuild options:
  [1] Rebuild now (estimated 25s)
  [2] Rebuild in background, use stale index (may be inaccurate)
  [3] Skip rebuild, scan on-demand (slower commands)

Choice [1]:
```

**Background rebuild**:
```bash
$ jigy status --background-rebuild
  [Using stale index, rebuilding in background...]
  [Status output shown immediately]
  
  Background: [████████░░░░░░░░] 45% - 12s remaining
```

**Advantages**:
- ✅ Doesn't block user
- ✅ Commands work immediately (with warning)
- ✅ Index fresh for next command

**Disadvantages**:
- ⚠️ Stale data shown (could be wrong)
- ⚠️ Concurrent access complexity
- ⚠️ May confuse users

---

### Pattern 2: Lazy Rebuild on First Access

```python
$ git checkout feature-branch
  Switched to branch 'feature-branch'

$ jigy status
  [Graph index stale, rebuilding... ⏱️  25s]
  [████████████████████████████ 100%]
  
  Status: 142 nodes OK, 3 unimplemented

# Second command is fast
$ jigy graph show S-CLI-001
  [Using cached index]
  [Output shown immediately]
```

**Advantages**:
- ✅ Simple mental model
- ✅ Always fresh data
- ✅ No background process complexity

**Disadvantages**:
- ❌ First command after branch switch is SLOW
- ❌ Blocks user workflow

---

### Pattern 3: Prebuild Hook (CI/CD Focused)

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    steps:
      - uses: actions/checkout@v2
      
      - name: Restore JIG index cache
        uses: actions/cache@v3
        with:
          path: jig/.graph-index.msgpack
          key: jig-index-${{ hashFiles('jig/**/*.md', 'src/**/*.py') }}
      
      - name: Rebuild if cache miss
        run: |
          if [ ! -f jig/.graph-index.msgpack ]; then
            jigy index rebuild
          fi
      
      - name: Run tests
        run: pytest
```

**Advantages**:
- ✅ CI cache avoids rebuild most of the time
- ✅ Explicit control over rebuild timing
- ✅ Parallelizable (build index while installing deps)

**Disadvantages**:
- ⚠️ Cache key must be accurate
- ⚠️ Added CI complexity

---

## Failure Modes and Edge Cases

### Failure Mode 1: Corrupted Binary Index

**Scenario**: Power loss during rebuild writes corrupt MessagePack file

```python
$ jigy status
  ERROR: Failed to parse graph index (corrupted MessagePack)
  
  Attempting automatic repair...
  [Rebuilding from source... ⏱️  27s]
```

**Mitigation**:
- Write to `.graph-index.msgpack.tmp`, then atomic rename
- Store checksum in metadata file
- Auto-rebuild on corruption detection

---

### Failure Mode 2: Concurrent Rebuild Attempts

**Scenario**: Two terminal windows both trigger rebuild simultaneously

```bash
# Terminal 1
$ jigy status
  [Rebuilding... ████░░░░░░]

# Terminal 2
$ jigy validate
  [Rebuild in progress by PID 12345, waiting...]
  [Rebuild completed by other process]
  [Loading index...]
```

**Mitigation**:
- File-based lock (`.graph-index.lock`)
- Second process waits or fails gracefully
- Timeout after 60s (in case lock stale)

```python
import fcntl

def rebuild_with_lock(jig_root):
    lock_file = jig_root / 'jig' / '.graph-index.lock'
    
    try:
        with open(lock_file, 'w') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            # Got lock, proceed with rebuild
            perform_rebuild(jig_root)
    except BlockingIOError:
        # Another process is rebuilding
        wait_for_rebuild_completion(jig_root, timeout=60)
```

---

### Failure Mode 3: Stale Index After Git Operations

**Scenario**: User manually resolves merge conflict in annotated file, but git HEAD hasn't changed

```bash
$ git merge feature
  Auto-merging src/core/graph.py
  CONFLICT (content): Merge conflict in src/core/graph.py

$ vim src/core/graph.py  # Resolve conflict, edit @jig annotations

$ git add src/core/graph.py
$ git commit -m "Merge feature"
  # ← git HEAD NOW changes, staleness detected ✓

# But if user doesn't commit yet:
$ jigy status  # ← Index stale but git HEAD unchanged
```

**Mitigation**:
- Include working tree staleness check (Strategy 4)
- Manual `jigy index rebuild --force` command
- Warn if git working tree is dirty

---

### Failure Mode 4: Non-Git Projects

**Scenario**: User uses JIG in directory without git

```bash
$ jigy status
  ERROR: Cannot determine index freshness (no git repository)
  
  Options:
    1. Initialize git: git init
    2. Use timestamp-based staleness (less accurate)
    3. Always rebuild (slow)
  
  Set behavior: jigy config set staleness-check timestamp
```

**Mitigation**:
- Fallback to timestamp checks
- Config option for staleness strategy
- Warn about reduced accuracy

---

## Comparison: Binary vs Tracked JSON

Let's compare at massive scale (100K nodes):

| Aspect | Tracked JSON (S025) | Gitignored Binary (S026) |
|--------|---------------------|--------------------------|
| **Parse Time** | 3-5 seconds ❌ | 100-300ms ✅ |
| **Git Diff** | ✅ Yes (reviewable) | ❌ No (gitignored) |
| **Git Repo Size** | +23MB per commit ⚠️ | No impact ✅ |
| **First Clone** | Instant ✅ | 20-35s rebuild ⚠️ |
| **Branch Switch** | Instant ✅ | 20-35s rebuild ❌ |
| **Local Edit** | 3-5s parse | 20-35s rebuild if stale ⚠️ |
| **CI/CD** | No build step ✅ | Must rebuild ⚠️ |
| **Merge Conflicts** | Resolvable ✅ | Never happen ✅ |
| **Developer UX** | Slow parse, always fresh ⚠️ | Fast parse, occasional rebuild ⚠️ |

### Hybrid Score at 100K Nodes

**Tracked JSON**: 
- ⚠️ Tolerable if caching is aggressive
- ⚠️ Git bloat becomes issue (23MB × commits)
- ✅ Simple developer workflow

**Gitignored Binary**:
- ✅ Best runtime performance
- ⚠️ Rebuild friction in workflow
- ⚠️ Requires sophisticated staleness detection

**Winner at 100K scale**: Binary with smart staleness detection

---

## Alternative: Hybrid Source of Truth

### Architecture: Distributed Source with Binary Cache

```
Source of Truth (git-tracked):
  jig/
    specifications/*.md  ← Git tracked, human-edited
    outcomes/*.md        ← Git tracked, human-edited
    code-annotations.json ← Git tracked, generated from @jig scan
    
Build Artifacts (gitignored):
  jig/
    .graph-index.msgpack  ← Fast binary cache
    .graph-index.meta.json ← Build metadata
```

#### Key Insight: Separate Scanning from Graph Building

**Phase 1: Scan Code (Slow)**
```bash
$ jigy scan
  Scanning 100,000 source files for @jig annotations...
  [████████████████████] 100% - 18s
  
  Found 100,000 code annotations
  Exported to: jig/code-annotations.json (1.2MB)
```

**Phase 2: Build Graph (Fast)**
```bash
$ jigy index rebuild
  Loading markdown nodes... (2s)
  Loading code annotations... (0.5s)
  Building graph... (1s)
  Serializing to MessagePack... (0.5s)
  
  Total: 4 seconds
```

### Workflow Benefits

```bash
# Scenario: Code changes during development
$ vim src/core/graph.py  # Edit code with @jig annotations

$ jigy status
  [Code annotations may be stale]
  Scanning changed files... (0.2s)
  Rebuilding graph... (4s)

# Scenario: Markdown changes only
$ vim jig/specifications/S-NEW-001.md

$ jigy status
  [Markdown nodes changed]
  Rebuilding graph... (4s)  ← No full scan needed!
```

**Key Advantage**: Incremental scanning of changed files (0.2s) vs full scan (18s)

### Should code-annotations.json be tracked?

**Option A: Track in Git**
- ✅ Faster rebuilds (no scanning)
- ✅ Reviewable (see what code annotations changed)
- ❌ Git bloat (1.2MB per commit)
- ⚠️ Merge conflicts (but auto-resolvable)

**Option B: Gitignore**
- ✅ No git bloat
- ❌ Must rescan after every pull/checkout
- ❌ Slower first build after clone

**Recommendation**: 
- **Track if <5MB and updated rarely** (low churn)
- **Gitignore if >5MB or high churn** (continuous updates)
- At 100K nodes: 1.2MB is borderline, lean toward **tracking**

---

## Performance Model: Rebuild vs Parse Trade-offs

### Cost Function

```python
# Total time spent on index operations per day

def daily_cost_tracked_json(
    node_count: int,
    commands_per_day: int,
    git_pulls_per_day: int
):
    """Time cost with tracked JSON index."""
    parse_time_ms = node_count * 0.03  # 3-5s per 100K nodes
    
    total_parse_time = (commands_per_day * parse_time_ms) / 1000
    total_git_time = 0  # No rebuild needed
    
    return total_parse_time + total_git_time


def daily_cost_binary_rebuild(
    node_count: int,
    commands_per_day: int,
    git_pulls_per_day: int
):
    """Time cost with gitignored binary index."""
    parse_time_ms = node_count * 0.002  # 100-300ms per 100K nodes
    rebuild_time_s = (node_count / 100_000) * 25  # 25s per 100K nodes
    
    total_parse_time = (commands_per_day * parse_time_ms) / 1000
    total_rebuild_time = git_pulls_per_day * rebuild_time_s
    
    return total_parse_time + total_rebuild_time


# Example: 100K nodes, 50 commands/day, 5 git pulls/day
tracked = daily_cost_tracked_json(100_000, 50, 5)
binary = daily_cost_binary_rebuild(100_000, 50, 5)

print(f"Tracked JSON:  {tracked:.1f} seconds/day")
print(f"Binary Rebuild: {binary:.1f} seconds/day")
```

### Results

| Scenario | Node Count | Cmds/Day | Pulls/Day | Tracked JSON | Binary | Winner |
|----------|------------|----------|-----------|--------------|--------|--------|
| **Small project** | 1,000 | 50 | 5 | 1.5s | 1.25s | Tracked JSON ✅ |
| **Medium project** | 10,000 | 50 | 5 | 15s | 6.25s | Binary ✅ |
| **Large project** | 100,000 | 50 | 5 | 150s (2.5min) ❌ | 126s (2.1min) | Binary ✅ |
| **Huge project** | 100,000 | 100 | 10 | 300s (5min) ❌ | 255s (4.25min) | Binary ✅ |
| **CI/CD** | 100,000 | 10 | 1 | 30s | 26s | Binary ✅ |

**Crossover Point**: ~5,000 nodes (where binary becomes worthwhile)

---

## Developer Experience Scenarios (100K Nodes)

### Scenario A: Fresh Clone (First Time Setup)

**Tracked JSON**:
```bash
$ git clone repo.git
  Cloning... done (1.2GB)  ← Includes 23MB JSON in history

$ jigy status
  [Loading graph index... 4.2s]
  Status: 142 nodes OK, 3 unimplemented
```
**Time**: 4.2s

**Binary Rebuild**:
```bash
$ git clone repo.git
  Cloning... done (1.18GB)  ← 20MB smaller without index

$ jigy status
  [Graph index missing, rebuilding...]
  [Scanning 100,000 files... ⏱️  22s]
  [Building graph... 3s]
  Total: 25s
  
  Status: 142 nodes OK, 3 unimplemented
```
**Time**: 25s

**Winner**: Tracked JSON ✅ (21s faster first time)

---

### Scenario B: Daily Development (10 commands, no git operations)

**Tracked JSON**:
```bash
$ jigy status      # 4.2s parse
$ jigy validate    # 4.2s parse
$ jigy graph show  # 4.2s parse
... (10 commands × 4.2s)
```
**Time**: 42s total

**Binary Rebuild**:
```bash
$ jigy status      # 0.15s parse (index fresh)
$ jigy validate    # 0.15s parse
$ jigy graph show  # 0.15s parse
... (10 commands × 0.15s)
```
**Time**: 1.5s total

**Winner**: Binary ✅ (40s faster, 27x speedup)

---

### Scenario C: Feature Branch Workflow

**Tracked JSON**:
```bash
$ git checkout feature-auth
  Switched to branch 'feature-auth'

$ jigy status
  [Loading graph index... 4.2s]
  Status: ...

$ git checkout feature-payments
  Switched to branch 'feature-payments'

$ jigy status
  [Loading graph index... 4.2s]
  Status: ...
```
**Time per switch**: 4.2s

**Binary Rebuild**:
```bash
$ git checkout feature-auth
  Switched to branch 'feature-auth'

$ jigy status
  [Git HEAD changed, rebuilding... ⏱️  25s]
  Status: ...

$ git checkout feature-payments
  Switched to branch 'feature-payments'

$ jigy status
  [Git HEAD changed, rebuilding... ⏱️  25s]
  Status: ...
```
**Time per switch**: 25s

**Winner**: Tracked JSON ✅ (21s faster per switch)

---

### Scenario D: Hot Development Loop (Iterating on code)

**Tracked JSON**:
```bash
# Edit code with @jig annotations
$ vim src/core/graph.py

$ jigy validate
  [Loading graph index... 4.2s]
  Warning: Stale annotations in git-tracked index
  Run: jigy index rebuild

$ jigy index rebuild
  [Scanning... 22s]
  [Building... 3s]
  
  [Loading graph index... 4.2s]
  Validation: 2 errors found
```
**Time per iteration**: 4.2s parse + 25s rebuild = 29.2s

**Binary Rebuild**:
```bash
# Edit code with @jig annotations
$ vim src/core/graph.py

$ jigy validate
  [Modified files detected, rebuilding... ⏱️  3s]  ← Incremental!
  Validation: 2 errors found
```
**Time per iteration**: 3s (incremental scan)

**Winner**: Binary ✅ (26s faster with incremental scanning)

---

## Incremental Rebuild Strategy (Critical Optimization)

The key to making binary viable is **incremental rebuilds**:

```python
def incremental_rebuild(jig_root, changed_files):
    """Rebuild only affected parts of graph."""
    
    # 1. Load existing index
    existing_graph = load_msgpack_index(jig_root)  # 0.15s
    
    # 2. Scan only changed files
    scanner = AnnotationScanner(jig_root)
    new_annotations = scanner.scan_files(changed_files)  # 0.5s for 10 files
    
    # 3. Update affected nodes
    for annotation in new_annotations:
        existing_graph.update_node(annotation)
    
    # 4. Revalidate affected edges
    affected_nodes = get_affected_nodes(changed_files)
    existing_graph.revalidate_edges(affected_nodes)  # 0.3s
    
    # 5. Save updated index
    save_msgpack_index(jig_root, existing_graph)  # 0.5s
    
    # Total: ~1.5-2s instead of 25s

# Example: Edit one file
$ vim src/core/graph.py

$ jigy status
  [1 file changed, incremental rebuild... ⏱️  1.8s]
  Status: ...
```

**Impact**: Reduces rebuild from 25s → 2s for local edits (12x speedup)

---

## Recommendation: Adaptive Strategy

### Recommended Architecture

**Use different strategies based on scale and context:**

| Node Count | Primary Strategy | Rationale |
|------------|------------------|-----------|
| **< 1,000** | Tracked JSON | Fast enough (0.03-0.15s parse), simple workflow |
| **1K-10K** | Tracked JSON + Binary cache (optional) | JSON tolerable (0.15-0.5s), binary available for power users |
| **10K-50K** | Binary with smart rebuild | Parse time becomes painful (>0.5s), rebuild cost justified |
| **> 50K** | Binary with incremental rebuild | Essential for usability, invest in incremental scanning |

### Implementation Roadmap

#### Phase 1: Current (< 1,000 nodes)
- ✅ Tracked YAML (already implemented)
- ✅ Works fine at current scale

#### Phase 2: Optimization (1K-10K nodes)
- 📋 Migrate to tracked JSON (S025 recommendation)
- 📋 Optional binary cache (gitignored, auto-rebuild)
- 📋 Config: `jigy config set index-format json` or `binary-cached`

#### Phase 3: Scale (10K-50K nodes)
- 📋 Default to gitignored binary
- 📋 Smart git-based staleness detection
- 📋 Prebuild hooks for CI/CD

#### Phase 4: Massive Scale (> 50K nodes)
- 📋 Incremental rebuild engine
- 📋 Background rebuild with progress indication
- 📋 Distributed index (multiple msgpack files per subsystem)

---

## Hybrid Approach: Best of Both Worlds

### Proposed Solution: Dual-Format Repository

**Git-Tracked** (source of truth):
```
jig/
  specifications/*.md       ← Human-edited intent
  outcomes/*.md             ← Human-edited intent
  constraints/*.md          ← Human-edited intent
  code-annotations.yaml     ← Generated, but tracked (for review)
```

**Gitignored** (build artifacts):
```
jig/
  .graph-index.msgpack      ← Fast binary cache
  .graph-index.meta.json    ← Build metadata
  .graph-index.lock         ← Rebuild lock file
```

### Build Process
```bash
# Step 1: Scan code (occasional, track results)
$ jigy scan --export jig/code-annotations.yaml
  Scanning 100,000 files... 22s
  Exported: jig/code-annotations.yaml (1.2MB)

$ git add jig/code-annotations.yaml
$ git commit -m "Update code annotations"

# Step 2: Build binary (fast, always from tracked sources)
$ jigy index rebuild
  Loading annotations from jig/code-annotations.yaml... 0.5s
  Loading markdown nodes... 2s
  Building graph... 1s
  Saved to: jig/.graph-index.msgpack
  Total: 3.5s
```

### Advantages
- ✅ **Git-tracked annotations** (reviewable, diffable)
- ✅ **Fast rebuilds** (3.5s vs 25s, no full scan needed)
- ✅ **Fast commands** (0.15s parse from binary)
- ✅ **Incremental scanning** (only rescan changed files)
- ✅ **CI/CD friendly** (deterministic builds from tracked sources)

### Workflow Impact
```bash
# Morning sync
$ git pull
  Updated: jig/code-annotations.yaml

$ jigy status
  [Rebuilding from tracked annotations... 3.5s]
  Status: ...

# Local development
$ vim src/core/graph.py  # Edit code

$ jigy validate
  [Rescanning modified file... 0.5s]
  [Incremental rebuild... 1.5s]
  Validation: ...
  
$ git add src/core/graph.py

$ jigy scan --incremental  # Rescan only changed files
  [1 file changed, scanning... 0.3s]
  [Updated: jig/code-annotations.yaml]

$ git add jig/code-annotations.yaml
$ git commit -m "Implement S-CLI-015"
```

---

## Final Evaluation: Binary-Only with Rebuild-on-Demand

### Strengths ✅
1. **Best runtime performance**: 100-300ms parse at 100K nodes
2. **No git bloat**: Saves 20-23MB per commit
3. **Viable at massive scale**: Only approach that scales to 100K+ nodes
4. **Deterministic**: Always rebuilds from source (no staleness)

### Weaknesses ❌
1. **Rebuild friction**: 20-35s delay after branch switches
2. **CI/CD overhead**: Must rebuild in every pipeline
3. **First clone penalty**: 25s setup time
4. **Complex staleness detection**: Git-based heuristics required
5. **Loss of reviewability**: Can't see graph changes in PRs

### Viability Score (at 100K nodes)

| Criteria | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Runtime Performance | 10/10 | 30% | 3.0 |
| Developer Workflow | 5/10 | 30% | 1.5 |
| CI/CD Integration | 6/10 | 20% | 1.2 |
| Debugging/Review | 3/10 | 10% | 0.3 |
| Implementation Complexity | 6/10 | 10% | 0.6 |
| **TOTAL** | **6.6/10** | | **6.6** |

**Verdict**: ⚠️ **Viable but with caveats** - Requires investment in incremental rebuilding and smart staleness detection to be developer-friendly.

---

## Final Recommendation

### For JIG Project (Current ~100 nodes)
✅ **Stick with tracked JSON** (S025 recommendation)
- Fast enough (<5ms parse)
- Simple workflow
- Reviewable changes

### For Massive Scale (10K+ nodes)
✅ **Hybrid: Tracked annotations + Binary cache**
- Track `code-annotations.yaml` (1-2MB, low churn)
- Gitignore `.graph-index.msgpack` (fast binary)
- Rebuild from annotations (3-5s) not full scan (25s)
- Incremental scanning for local dev

### Pure Binary-Only?
⚠️ **Only if**:
- Annotations change constantly (high churn)
- Git size is critical concern
- Willing to invest in sophisticated staleness detection
- Willing to accept 20-35s rebuild cost after git operations

**Conclusion**: Binary-only is technically viable at massive scale but hybrid approach (tracked annotations + binary cache) offers better developer experience with similar performance benefits.

---

## Appendix: Implementation Sketch

```python
# src/jig/core/index_loader.py

class GraphIndexLoader:
    """Load graph index with automatic rebuild."""
    
    def __init__(self, jig_root: Path):
        self.jig_root = jig_root
        self.binary_path = jig_root / 'jig' / '.graph-index.msgpack'
        self.meta_path = jig_root / 'jig' / '.graph-index.meta.json'
        self.annotations_path = jig_root / 'jig' / 'code-annotations.yaml'
    
    def load(self, force_rebuild=False):
        """Load index with staleness checking."""
        
        if force_rebuild or self._is_stale():
            return self._rebuild_and_load()
        
        return self._load_binary()
    
    def _is_stale(self) -> bool:
        """Check if index needs rebuild."""
        
        # Level 1: Binary missing?
        if not self.binary_path.exists():
            return True
        
        # Level 2: Git HEAD changed?
        if self._git_head_changed():
            return True
        
        # Level 3: Tracked annotations changed?
        if self._annotations_changed():
            return True
        
        # Level 4: Working tree dirty?
        if self._working_tree_dirty():
            return True
        
        return False
    
    def _rebuild_and_load(self):
        """Rebuild index and load."""
        
        with rebuild_lock(self.jig_root):
            logger.info("Rebuilding graph index...")
            
            # Load tracked annotations (fast)
            annotations = load_yaml(self.annotations_path)
            
            # Build graph
            graph = GraphBuilder().build(
                annotations=annotations,
                markdown_nodes=self._load_markdown_nodes()
            )
            
            # Save binary
            with open(self.binary_path, 'wb') as f:
                f.write(msgpack.packb(graph.to_dict()))
            
            # Save metadata
            self._save_metadata()
            
            return graph
    
    def _load_binary(self):
        """Load from binary cache."""
        with open(self.binary_path, 'rb') as f:
            data = msgpack.unpackb(f.read())
        return Graph.from_dict(data)
```

---

## Questions for Decision

1. **At what node count does JIG expect to operate?**
   - < 1,000: Stay with JSON
   - 1K-10K: Hybrid approach
   - 10K+: Binary with tracked annotations

2. **How often do code annotations change?**
   - Low churn: Track annotations
   - High churn: Gitignore everything, scan on demand

3. **Is PR reviewability of graph changes important?**
   - Yes: Track annotations or JSON
   - No: Pure binary approach

4. **What's the acceptable first-clone setup time?**
   - < 5s: Must track index
   - < 30s: Binary rebuild acceptable
   - < 60s: Full scan acceptable

---

**Status**: Ready for architectural decision based on scale requirements

