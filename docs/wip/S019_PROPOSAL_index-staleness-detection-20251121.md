---
type: proposal
created: 2025-11-21
status: draft
prompt: |
  I don't want fallbacks because that will start to create unexplained behavior in the system.
  There should be a single first-class way to do things, other things should be corrected at 
  their source or fail in a way that they can be corrected.
  
  WU9 will include "rebuild index from sources". I think this is the way.
  The source files are the TRUTH. The index gets built from the sources.
  
  Is there a way we can detect the index is out of date prior to running any of these commands?
  And then if the index needs a rebuild, we could do so on the fly?
  
  Make a PROPOSAL for how this should be done. Include in the proposal document draft outcomes
  and specifications. And a concept (or 3) of how this would be implemented.
---

# PROPOSAL: Index Staleness Detection & Auto-Rebuild

## Problem Statement

**Current Issue:**
- Commands like `jigy graph list --subsystem airspace` work (via fallback to frontmatter)
- Commands like `jigy decompose metrics --subsystem airspace` fail (no fallback, requires index)
- Inconsistent behavior creates confusion and unpredictability

**Root Cause:**
- `graph-index.yaml` is out of sync with source files (markdown O/S nodes, code annotations)
- No mechanism to detect when index is stale
- Commands have inconsistent fallback strategies

**Why Fallbacks Are Problematic:**
1. Create unexplained behavior (why does one work and not the other?)
2. Hide the real problem (stale index)
3. Make debugging harder (which source of truth is being used?)
4. Lead to subtle bugs (different commands see different data)

## Guiding Principle

**Single Source of Truth:**
- Markdown files (O/S nodes) are the primary truth for Intent
- Code/test files with `@jig` annotations are the primary truth for C/T nodes
- `graph-index.yaml` is a DERIVED artifact (cache/index) built from sources
- When index is stale, either rebuild it or fail with a clear error

## Draft Outcomes

### O-INDEX-001: Index stays synchronized with source files

**Value:**
Developers never encounter "subsystem not found" errors when subsystems exist in source files. The tool automatically detects and corrects index staleness, providing a consistent and predictable experience.

**Acceptance Criteria:**
- `jigy` commands detect stale index before executing
- User is notified when index is stale (clear, actionable message)
- Index can be rebuilt automatically or on-demand
- All commands use the same staleness detection logic (no special cases)

### O-INDEX-002: Developers understand when and why rebuilds happen

**Value:**
Rebuild operations are transparent and predictable. Developers know what triggers a rebuild, how long it takes, and what changed. No mysterious behavior or hidden cache invalidation.

**Acceptance Criteria:**
- Rebuild shows progress for large codebases (>1000 files)
- Rebuild reports what changed (X nodes added, Y edges updated)
- Rebuild performance is acceptable (<5s for typical projects)
- Clear documentation explains staleness detection algorithm

### O-INDEX-003: Index rebuilds are safe and reliable

**Value:**
Rebuilding the index never loses data or corrupts the graph. The operation is idempotent and can be safely interrupted. Developers can trust that `jigy` will always present accurate information.

**Acceptance Criteria:**
- Rebuild is atomic (writes to temp file, then renames)
- Failed rebuild doesn't corrupt existing index
- Rebuild can be interrupted (Ctrl-C) safely
- Rebuild validation ensures correctness (no broken edges)

## Draft Specifications

### S-INDEX-001: Detect index staleness before graph loading

**Purpose:**
Provide a fast, reliable mechanism to detect when `graph-index.yaml` is out of sync with source files, preventing commands from operating on stale data.

**Rationale:**
Commands should never use stale data. Detecting staleness early (before full graph load) enables fast-path operations and clear error messages.

**Acceptance Criteria:**
- Staleness check completes in <50ms for typical projects (100 files)
- Detects:
  - Source files newer than index (mtime comparison)
  - Nodes in source files not in index (quick scan)
  - Index references nodes that no longer exist
- Returns structured result: `IndexStatus { is_stale: bool, reason: str, affected_files: list }`

**Implementation Notes:**
```python
@dataclass
class IndexStatus:
    is_stale: bool
    reason: str  # "source_files_newer", "missing_nodes", "orphaned_refs", "index_missing"
    affected_files: list[Path]
    last_index_time: datetime
    
def check_index_staleness(intent_dir: Path) -> IndexStatus:
    """Fast staleness check without full graph load."""
    graph_index_path = intent_dir / "graph-index.yaml"
    
    if not graph_index_path.exists():
        return IndexStatus(True, "index_missing", [], None)
    
    index_mtime = graph_index_path.stat().st_mtime
    
    # Check if any source files are newer
    for node_dir in ["outcomes", "specifications", "constraints"]:
        dir_path = intent_dir / node_dir
        if not dir_path.exists():
            continue
        for md_file in dir_path.glob("*.md"):
            if md_file.stat().st_mtime > index_mtime:
                return IndexStatus(True, "source_files_newer", [md_file], index_mtime)
    
    # TODO: Check for missing nodes (requires partial index read)
    # TODO: Check for orphaned references
    
    return IndexStatus(False, "up_to_date", [], index_mtime)
```

### S-INDEX-002: Auto-rebuild index on staleness detection

**Purpose:**
Automatically regenerate `graph-index.yaml` when staleness is detected, ensuring commands always operate on current data without manual intervention.

**Rationale:**
Manual `jigy index --rebuild` is easy to forget. Auto-rebuild provides a seamless experience while maintaining transparency (users see what's happening).

**Acceptance Criteria:**
- Commands call `ensure_index_fresh()` before loading graph
- User is notified: "⚠ Index is stale (source files newer), rebuilding..."
- Rebuild progress shown for large operations (>100 files)
- Rebuild can be disabled via flag: `--no-auto-rebuild` (for CI/automation)
- Failed rebuild shows clear error with recovery instructions

**Implementation Notes:**
```python
def ensure_index_fresh(intent_dir: Path, auto_rebuild: bool = True) -> None:
    """Ensure index is up-to-date before graph operations."""
    status = check_index_staleness(intent_dir)
    
    if not status.is_stale:
        return
    
    if not auto_rebuild:
        raise IndexStaleError(
            f"Index is stale: {status.reason}\n"
            f"Run 'jigy index --rebuild' to update, or use --auto-rebuild"
        )
    
    # Notify user
    click.echo(click.style(
        f"⚠ Index is stale ({status.reason}), rebuilding...",
        fg="yellow"
    ))
    
    # Rebuild
    from jig.core.index_builder import rebuild_index
    try:
        result = rebuild_index(intent_dir, show_progress=True)
        click.echo(click.style(
            f"✓ Index rebuilt: {result.nodes_added} nodes added, "
            f"{result.edges_added} edges added",
            fg="green"
        ))
    except Exception as e:
        raise IndexRebuildError(
            f"Failed to rebuild index: {e}\n"
            f"Try 'jigy index --rebuild --verbose' for details"
        ) from e
```

### S-INDEX-003: Rebuild index from all sources

**Purpose:**
Regenerate complete `graph-index.yaml` by scanning markdown files and code annotations, ensuring the index accurately reflects current source state.

**Rationale:**
The index is a derived artifact. Rebuilding from sources is the authoritative way to ensure correctness. This is the implementation for WU9.

**Acceptance Criteria:**
- Scans `jig/outcomes/*.md`, `jig/specifications/*.md`, `jig/constraints/*.md`
- Scans source code for `@jig` annotations (C/T nodes) - see WU8
- Extracts all relationships from frontmatter and annotations
- Generates valid list-format `graph-index.yaml`
- Validates result (no broken edges, all nodes have required fields)
- Atomic write (temp file + rename)

**Implementation Notes:**
```python
def rebuild_index(intent_dir: Path, show_progress: bool = False) -> RebuildResult:
    """Rebuild graph-index.yaml from all sources."""
    nodes = []
    edges = []
    
    # Load O/S/X nodes from markdown
    for node_dir in ["outcomes", "specifications", "constraints"]:
        dir_path = intent_dir / node_dir
        if not dir_path.exists():
            continue
        
        for md_file in dir_path.glob("*.md"):
            node = parse_ostc_node(md_file)
            nodes.append({
                "id": node.id,
                "type": node.type,
                "title": node.title,
                "subsystem": node.subsystem,
                "file": str(md_file.relative_to(intent_dir.parent)),
            })
            
            # Extract edges from frontmatter
            edges.extend(extract_edges_from_node(node))
    
    # Load C/T nodes from code annotations (WU8)
    # TODO: Implement after annotation scanner is ready
    
    # Build subsystems from node.subsystem fields
    subsystems = build_subsystem_tree(nodes)
    
    # Generate graph-index.yaml
    index_data = {
        "version": "1.0.0",
        "generated": datetime.now().isoformat(),
        "nodes": nodes,
        "edges": [{"from": e.from_node, "to": e.to_node, "type": e.type} for e in edges],
        "subsystems": subsystems,
    }
    
    # Atomic write
    temp_file = intent_dir / "graph-index.yaml.tmp"
    final_file = intent_dir / "graph-index.yaml"
    
    dump_yaml(index_data, temp_file)
    temp_file.rename(final_file)
    
    return RebuildResult(
        nodes_added=len(nodes),
        edges_added=len(edges),
        subsystems_found=len(subsystems),
    )
```

## Implementation Concepts

### Concept 1: Eager Check + Manual Rebuild (Conservative)

**How It Works:**
- Every `jigy` command starts by calling `check_index_staleness()`
- If stale, command immediately fails with helpful error:
  ```
  ✗ Error: Index is out of sync with source files
  
  Reason: Source files modified after index was built
  Affected files:
    - jig/specifications/S-AIR-005.md (modified 2 minutes ago)
    - jig/outcomes/O-AIR-003.md (modified 5 minutes ago)
  
  To fix: jigy index --rebuild
  ```
- User runs `jigy index --rebuild` manually
- Command retries and succeeds

**Pros:**
- ✅ Explicit and predictable (no surprises)
- ✅ User always knows when rebuild happens
- ✅ Fast check (just mtime comparison)
- ✅ Works well in CI (deterministic)

**Cons:**
- ❌ Extra manual step required
- ❌ Can be annoying in active development
- ❌ Requires user to understand index concept

**Best For:** Production environments, CI/CD, teams that prefer explicit control

### Concept 2: Smart Auto-Rebuild (Intelligent)

**How It Works:**
- Every `jigy` command calls `ensure_index_fresh(auto_rebuild=True)`
- If stale, automatically rebuilds with progress indicator:
  ```
  ⚠ Index is stale (2 source files modified), rebuilding...
  Scanning: ████████████████████ 100% (42 files)
  ✓ Index rebuilt: 2 nodes updated, 3 edges added (0.3s)
  
  [continues with original command]
  ```
- User can opt-out with `--no-auto-rebuild` flag
- Rebuild failures show clear error with manual recovery option

**Pros:**
- ✅ Seamless developer experience
- ✅ Always operates on current data
- ✅ Transparent (shows what's happening)
- ✅ Can be disabled for CI/production

**Cons:**
- ❌ Slightly slower (rebuild overhead)
- ❌ Might surprise users first time
- ❌ Could be annoying if index is constantly stale

**Best For:** Development workflows, iterative work, small to medium projects

### Concept 3: Lazy Rebuild + Fallback Cache (Hybrid)

**How It Works:**
- Commands check staleness but distinguish severity:
  - **Critical stale**: Index missing or corrupt → immediate rebuild required
  - **Minor stale**: Few files modified → load index + patch with file data
  - **Fresh**: Use index as-is
- For minor staleness, use in-memory patch:
  ```python
  graph = Graph.load_from_dir(intent_dir)  # Loads stale index
  
  # Patch with changed files
  for changed_file in status.affected_files:
      node = parse_ostc_node(changed_file)
      graph.nodes[node.id] = node  # Override stale data
  ```
- Background thread rebuilds index while command runs
- Next command uses fresh index

**Pros:**
- ✅ Best performance (no rebuild delays)
- ✅ Gracefully handles minor changes
- ✅ Eventually consistent

**Cons:**
- ❌ Complex implementation (patching logic)
- ❌ Potential race conditions (background rebuild)
- ❌ Harder to debug (what data am I seeing?)
- ❌ Violates "no fallbacks" principle

**Best For:** Large projects where rebuild is slow, teams comfortable with complexity

## Recommendation

**Choose Concept 2: Smart Auto-Rebuild**

**Rationale:**
1. **Aligns with "single source of truth" principle**: Always uses current source data
2. **No fallbacks**: One clear path - sources → index → commands
3. **Developer-friendly**: Works seamlessly in active development
4. **Production-ready**: Can disable auto-rebuild in CI with `--no-auto-rebuild`
5. **Transparent**: Users see what's happening and why
6. **Enables WU9**: `jigy index --rebuild` command becomes the implementation
7. **Fixes the airspace bug**: Both `graph list` and `decompose metrics` would auto-rebuild and see the subsystem

**Implementation Priority:**
1. ✅ WU8: Annotation scanner (so we can find C/T nodes)
2. ✅ WU9: Index rebuild command (core rebuild logic)
3. 🔄 Post-WU9: Add staleness detection (`check_index_staleness`)
4. 🔄 Post-WU9: Add auto-rebuild wrapper (`ensure_index_fresh`)
5. 🔄 Post-WU9: Update all CLI commands to call `ensure_index_fresh`
6. 🔄 Post-WU9: Remove fallback logic from `graph list` (use single path)

## Migration Path

**Phase 1: Add Rebuild Command (WU9)**
- Implement `jigy index --rebuild`
- Users can manually rebuild when needed
- No behavior changes to existing commands

**Phase 2: Add Staleness Detection**
- Implement `check_index_staleness()`
- Add warning messages to commands: "⚠ Index may be stale, run 'jigy index --rebuild'"
- Still allows commands to proceed (backward compatible)

**Phase 3: Enable Auto-Rebuild**
- Add `ensure_index_fresh()` to all commands
- Default: auto-rebuild enabled
- Flag to disable: `--no-auto-rebuild`
- Remove fallback logic from `graph list`

**Phase 4: Refine**
- Optimize staleness check performance
- Add more intelligent rebuild triggers
- Implement incremental rebuild for large codebases (if needed)

## Open Questions

1. **How often to check staleness?**
   - Every command? (simple, consistent)
   - Cache check results for N seconds? (performance optimization)
   - **Recommendation:** Every command, optimize later if needed

2. **What to do with stale index in read-only environments?**
   - CI systems might not have write access to rebuild
   - **Recommendation:** Commands fail with clear error, require pre-built index

3. **Should rebuild be incremental or full?**
   - Full: Simple, reliable, but slower
   - Incremental: Fast, but complex and error-prone
   - **Recommendation:** Start with full, add incremental in v2 if needed

4. **Should we keep old index as backup?**
   - `graph-index.yaml.bak` before rebuild?
   - **Recommendation:** Yes, for debugging and rollback

## Success Metrics

- ✅ Zero "subsystem not found" errors when subsystem exists in sources
- ✅ All commands use consistent data (no fallback paths)
- ✅ Rebuild completes in <5s for typical projects (100 files)
- ✅ Staleness check completes in <50ms
- ✅ User feedback: "behavior is predictable and understandable"

## Related Documents

- `S018_PLAN_jigy-core-graph-annotations-20251121.md` - Implementation plan including WU8 (scanner) and WU9 (rebuild)
- `JIG-Concept-v6.1.md` - Source files as primary truth
- `S017_ANALYSIS_jig-alignment-gap-20251121.md` - Gap analysis identifying index issues

## Decision Record

**Date:** 2025-11-21

**Decision:** Adopt Smart Auto-Rebuild (Concept 2)

**Participants:** [To be filled]

**Status:** PROPOSAL (awaiting approval)

**Next Steps:**
1. Review this proposal
2. Approve implementation approach
3. Complete WU8 (annotation scanner)
4. Complete WU9 (rebuild command)
5. Implement staleness detection (post-WU9)
6. Deploy and gather feedback

