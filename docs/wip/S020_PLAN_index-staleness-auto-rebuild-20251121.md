---
delta_type: plan
branch: index-staleness-detection
created: 2025-11-21
status: draft
prompt: |
  make a PLAN to implement @docs/wip/S019_PROPOSAL_index-staleness-detection-20251121.md
  Smart Auto-Rebuild (Intelligent) ⭐ RECOMMENDED
  use your recommendations for questions 1-4.
  create a PLAN according to @agents/taskPlan.md
  save as S020_PLAN
  include this prompt in the Frontmatter
---

# PLAN: Index Staleness Detection & Auto-Rebuild

- **SCOPE:** S019_PROPOSAL_index-staleness-detection-20251121.md
- **Start:** 2025-11-21
- **Owner:** Jim Meyer
- **Status:** Draft
- **Subsystem:** jigy-tool
- **Context:** Implement smart auto-rebuild to eliminate inconsistent subsystem behavior

## Problem Statement

**Current Issue:**
- `jigy graph list --subsystem airspace` works (has fallback to frontmatter)
- `jigy decompose metrics --subsystem airspace` fails (requires index)
- Inconsistent, unpredictable behavior confuses users

**Root Cause:**
- `graph-index.yaml` is out of sync with source files
- No mechanism to detect staleness
- Different commands have different fallback strategies

**Solution:**
- **Single source of truth**: Source files (markdown, code) are primary truth
- **Index is derived**: `graph-index.yaml` is a cache built from sources
- **Smart auto-rebuild**: Detect staleness, rebuild automatically, no fallbacks
- **Predictable behavior**: All commands work consistently

## Known Intent (Created Before Coding)

**Building JIG with JIG:** We create Intent nodes (O/S) BEFORE implementation to follow constraint-driven development.

**Outcomes Created (jig/outcomes/):**
- O-INDEX-001: "Index stays synchronized with source files"
  - Value: Developers never encounter "subsystem not found" errors when subsystems exist in source files
- O-INDEX-002: "Developers understand when and why rebuilds happen"
  - Value: Rebuild operations are transparent and predictable, no mysterious behavior
- O-INDEX-003: "Index rebuilds are safe and reliable"
  - Value: Rebuilding never loses data or corrupts the graph, can be interrupted safely

**Specifications Created (jig/specifications/):**
- S-INDEX-001: "Detect index staleness before graph loading"
  - Fast check (<50ms) comparing source mtimes vs index mtime
- S-INDEX-002: "Auto-rebuild index on staleness detection"
  - Seamless rebuild with progress indicator, can be disabled
- S-INDEX-003: "Rebuild index from all sources"
  - Regenerate graph-index.yaml from markdown + code annotations

**Rationale:** These constraints were identified in S019 PROPOSAL analysis. Creating them upfront enables O→S→TDD flow.

## Implementation Approach

**Concept Chosen:** Smart Auto-Rebuild (Concept 2 from S019)

**How It Works:**
1. Every `jigy` command calls `ensure_index_fresh()` before loading graph
2. If index is stale, automatically rebuilds with progress indicator
3. User sees: "⚠ Index is stale, rebuilding... ✓ Done (0.3s)"
4. Command continues with fresh data
5. Can be disabled with `--no-auto-rebuild` flag for CI/production

**Design Decisions (from S019 Open Questions):**

1. **How often to check staleness?**
   - **Decision:** Every command, optimize later if needed
   - **Rationale:** Simple, consistent, correctness over premature optimization

2. **What to do in read-only environments?**
   - **Decision:** Fail with clear error, require pre-built index
   - **Rationale:** Explicit failures better than silent wrong behavior

3. **Full or incremental rebuild?**
   - **Decision:** Start with full rebuild, add incremental in v2 if needed
   - **Rationale:** Simple, reliable, performance acceptable for typical projects

4. **Keep old index as backup?**
   - **Decision:** Yes, create `graph-index.yaml.bak` before rebuild
   - **Rationale:** Enables debugging and rollback if rebuild has issues

## Prerequisites

**Depends on S018 PLAN Work Units:**
- ✅ WU1-7: Core plumbing and graph navigation (COMPLETE)
- ⏭️ WU8: Fast Code Scanner (find @jig annotations) - **REQUIRED**
- ⏭️ WU9: Index Rebuild from Sources (core rebuild logic) - **REQUIRED**

**This PLAN extends WU9 with:**
- Staleness detection mechanism
- Auto-rebuild integration wrapper
- Removal of fallback logic
- Safety features (backup, atomic writes)

## Work Unit Checklist

**Phase 0: Intent-First**
- [ ] WU0: Create Intent nodes (O-INDEX-001/002/003, S-INDEX-001/002/003)

**Phase 1: Prerequisites (from S018)**
- [ ] WU1: Verify WU8 complete (annotation scanner exists)
- [ ] WU2: Verify WU9 complete (index rebuild command exists)

**Phase 2: Staleness Detection**
- [ ] WU3: Implement staleness detection (S-INDEX-001)
- [ ] WU4: Add staleness check tests

**Phase 3: Auto-Rebuild Integration**
- [ ] WU5: Implement auto-rebuild wrapper (S-INDEX-002)
- [ ] WU6: Integrate into all CLI commands
- [ ] WU7: Add backup and atomic write safety (S-INDEX-003 enhancement)

**Phase 4: Cleanup & Validation**
- [ ] WU8: Remove fallback logic from graph list
- [ ] WU9: ASE-A validation and testing
- [ ] WU10: Documentation and examples

---

## Work Units

### Work Unit 0: Create Known Intent

**Goal:** Capture all known Outcomes and Specifications from S019 PROPOSAL as Intent nodes before coding.

**Acceptance Criteria:**
- All known "why" statements → Outcome nodes in jig/outcomes/
- All known "what" requirements → Specification nodes in jig/specifications/
- All nodes have proper YAML frontmatter and markdown content
- `jigy validate` passes

**Created Nodes:**
- O-INDEX-001.md: Index stays synchronized with source files
- O-INDEX-002.md: Developers understand when/why rebuilds happen
- O-INDEX-003.md: Index rebuilds are safe and reliable
- S-INDEX-001.md: Detect index staleness before graph loading
- S-INDEX-002.md: Auto-rebuild index on staleness detection
- S-INDEX-003.md: Rebuild index from all sources (extends S-JIGY-009)

**Implementation Notes:**
- Extract content from S019 PROPOSAL draft outcomes/specifications sections
- Add proper frontmatter with implements relationships
- S-INDEX-001 implements O-INDEX-001 (detection enables sync)
- S-INDEX-002 implements O-INDEX-001, O-INDEX-002 (auto-rebuild + transparency)
- S-INDEX-003 implements O-INDEX-003 (safety and reliability)

**Reflect:**
- What was clear from SCOPE: Problem and solution well-defined in proposal
- What was ambiguous: Performance targets for large codebases (will discover during testing)

**Human Validation:**
```bash
cd /Users/jmeyer/Code/jig
jigy validate
ls -la jig/outcomes/O-INDEX-*.md
ls -la jig/specifications/S-INDEX-*.md
```

---

### Work Unit 1: Verify Annotation Scanner Complete

**Implements:** Prerequisite check for S018-WU8

**Goal:** Confirm annotation scanner exists and works before building on it

**Planned Effort:** 15m

**Acceptance Criteria:**
- `jig.core.scanner` module exists with `scan_annotations()` function
- Can scan Python files for `@jig` annotations
- Returns structured `Annotation` objects with id, type, relationships, subsystem
- Test suite exists and passes

**Implementation Notes:**
- Read `src/jig/core/scanner.py` to understand API
- Review test suite in `tests/unit/test_annotation_scanner.py`
- If missing or incomplete, pause and complete S018-WU8 first
- Document scanner API for use in this PLAN

**Test Plan:**
- Run existing scanner tests: `pytest tests/unit/test_annotation_scanner.py -v`
- Verify scanner finds annotations in jig codebase itself

**Docs to Update:**
- None (verification only)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Discoveries:

**Links:**
- Commit(s): (verification only, no new code)

**Human Validation:**
```bash
cd /Users/jmeyer/Code/jig
pytest tests/unit/test_annotation_scanner.py -v
python -c "from jig.core.scanner import scan_annotations; print('Scanner API available')"
```

---

### Work Unit 2: Verify Index Rebuild Complete

**Implements:** Prerequisite check for S018-WU9

**Goal:** Confirm index rebuild command exists and works before extending it

**Planned Effort:** 15m

**Acceptance Criteria:**
- `jigy index --rebuild` command exists
- Regenerates `graph-index.yaml` from markdown files
- Uses annotation scanner to include C/T nodes
- Validates generated index before writing
- Test suite exists and passes

**Implementation Notes:**
- Test `jigy index --rebuild --dry-run` in jig codebase
- Review implementation in `src/jig/cli/index.py` and `src/jig/core/index_builder.py`
- Review test suite in `tests/unit/test_index_rebuild.py`
- If missing or incomplete, pause and complete S018-WU9 first
- Document rebuild API for use in this PLAN

**Test Plan:**
- Run existing rebuild tests: `pytest tests/unit/test_index_rebuild.py -v`
- Test rebuild on jig codebase: `jigy index --rebuild --dry-run`

**Docs to Update:**
- None (verification only)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Discoveries:

**Links:**
- Commit(s): (verification only, no new code)

**Human Validation:**
```bash
cd /Users/jmeyer/Code/jig
jigy index --rebuild --dry-run
# Should show what would be generated without writing
pytest tests/unit/test_index_rebuild.py -v
```

---

### Work Unit 3: Implement Staleness Detection

**Implements:** S-INDEX-001

**Goal:** Fast, reliable mechanism to detect when graph-index.yaml is out of sync with source files

**Planned Effort:** 90m

**Acceptance Criteria:**
- Function `check_index_staleness(intent_dir: Path) -> IndexStatus` exists
- Completes in <50ms for typical projects (100 files)
- Detects:
  - Source files newer than index (mtime comparison)
  - Index missing entirely
  - (Optional) Nodes in sources not in index
- Returns structured result: `IndexStatus(is_stale: bool, reason: str, affected_files: list, last_index_time: datetime)`
- Reasons: "index_missing", "source_files_newer", "missing_nodes"

**Implementation Notes:**
- Create `src/jig/core/staleness.py` with:
  ```python
  @dataclass
  class IndexStatus:
      is_stale: bool
      reason: str  # "source_files_newer", "missing_nodes", "index_missing", "up_to_date"
      affected_files: list[Path]
      last_index_time: datetime | None
      
  def check_index_staleness(intent_dir: Path) -> IndexStatus:
      """Fast staleness check without full graph load."""
      graph_index_path = intent_dir / "graph-index.yaml"
      
      if not graph_index_path.exists():
          return IndexStatus(True, "index_missing", [], None)
      
      index_mtime = graph_index_path.stat().st_mtime
      index_dt = datetime.fromtimestamp(index_mtime)
      
      # Check if any markdown source files are newer
      for node_dir in ["outcomes", "specifications", "constraints"]:
          dir_path = intent_dir / node_dir
          if not dir_path.exists():
              continue
          for md_file in dir_path.glob("*.md"):
              if md_file.stat().st_mtime > index_mtime:
                  return IndexStatus(True, "source_files_newer", [md_file], index_dt)
      
      # TODO: Check code files (requires knowing source directories)
      # For now, only check markdown files (most common case)
      
      return IndexStatus(False, "up_to_date", [], index_dt)
  ```
- Performance: Use `glob()` and `stat()` only, no full file reads
- Focus on markdown files first (fastest common case)

**Test Plan:**
- Unit: Test index_missing scenario
- Unit: Test source_files_newer scenario (mock mtime)
- Unit: Test up_to_date scenario
- Unit: Test performance (should be <50ms for 100 files)
- Integration: Test on jig codebase
- Test file: `tests/unit/test_staleness_detection.py`

**Docs to Update:**
- None yet (internal API)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Next experiment:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
```bash
cd /Users/jmeyer/Code/jig
pytest tests/unit/test_staleness_detection.py -v
# Test manually
python -c "
from pathlib import Path
from jig.core.staleness import check_index_staleness
status = check_index_staleness(Path('jig'))
print(f'Is stale: {status.is_stale}, Reason: {status.reason}')
"
```

---

### Work Unit 4: Add Staleness Check Tests

**Implements:** S-INDEX-001 (validation)

**Goal:** Comprehensive test suite for staleness detection edge cases

**Planned Effort:** 60m

**Acceptance Criteria:**
- Test coverage >90% for `staleness.py`
- Tests for all scenarios:
  - Index missing
  - Index older than markdown files
  - Index up-to-date
  - Empty directories (no markdown files)
  - Mixed scenarios (some fresh, some stale)
- Tests verify performance (<50ms for 100 files)
- Tests use fixtures with controlled mtimes

**Implementation Notes:**
- Use `pytest` fixtures to create temporary test directories
- Use `freezegun` or manual mtime manipulation to control file times
- Test structure:
  ```python
  def test_index_missing(tmp_path):
      # No graph-index.yaml file
      assert check_index_staleness(tmp_path).is_stale
      
  def test_source_newer_than_index(tmp_path):
      # Create index, then create newer markdown file
      index_file = tmp_path / "graph-index.yaml"
      index_file.write_text("version: 1.0.0")
      time.sleep(0.01)
      
      outcomes_dir = tmp_path / "outcomes"
      outcomes_dir.mkdir()
      (outcomes_dir / "O-001.md").write_text("...")
      
      status = check_index_staleness(tmp_path)
      assert status.is_stale
      assert status.reason == "source_files_newer"
      
  def test_up_to_date(tmp_path):
      # Create markdown first, then index
      outcomes_dir = tmp_path / "outcomes"
      outcomes_dir.mkdir()
      (outcomes_dir / "O-001.md").write_text("...")
      time.sleep(0.01)
      
      index_file = tmp_path / "graph-index.yaml"
      index_file.write_text("version: 1.0.0")
      
      assert not check_index_staleness(tmp_path).is_stale
  ```

**Test Plan:**
- Unit: All scenarios covered
- Performance: Benchmark test with 100 files
- Edge cases: Empty dirs, missing dirs, symlinks

**Docs to Update:**
- None (test suite)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Discoveries:

**Links:**
- Commit(s): 

**Human Validation:**
```bash
cd /Users/jmeyer/Code/jig
pytest tests/unit/test_staleness_detection.py -v --cov=jig.core.staleness --cov-report=term-missing
# Should show >90% coverage
```

---

### Work Unit 5: Implement Auto-Rebuild Wrapper

**Implements:** S-INDEX-002

**Goal:** Seamless auto-rebuild wrapper that ensures index is fresh before graph operations

**Planned Effort:** 90m

**Acceptance Criteria:**
- Function `ensure_index_fresh(intent_dir: Path, auto_rebuild: bool = True) -> None`
- Checks staleness using `check_index_staleness()`
- If stale and `auto_rebuild=True`: rebuilds automatically with notification
- If stale and `auto_rebuild=False`: raises `IndexStaleError` with clear message
- If fresh: returns immediately (fast path)
- Shows progress: "⚠ Index is stale (source files newer), rebuilding..."
- Shows result: "✓ Index rebuilt: 2 nodes updated, 3 edges added (0.3s)"
- Handles rebuild failures gracefully with recovery instructions

**Implementation Notes:**
- Add to `src/jig/core/staleness.py`:
  ```python
  class IndexStaleError(Exception):
      """Raised when index is stale and auto-rebuild is disabled."""
      pass
      
  class IndexRebuildError(Exception):
      """Raised when index rebuild fails."""
      pass
      
  def ensure_index_fresh(
      intent_dir: Path,
      auto_rebuild: bool = True,
      show_progress: bool = True
  ) -> None:
      """Ensure index is up-to-date before graph operations.
      
      Args:
          intent_dir: Path to jig intent directory
          auto_rebuild: If True, rebuild stale index automatically
          show_progress: If True, show progress messages
          
      Raises:
          IndexStaleError: If stale and auto_rebuild=False
          IndexRebuildError: If rebuild fails
      """
      status = check_index_staleness(intent_dir)
      
      if not status.is_stale:
          return  # Fast path - index is fresh
      
      if not auto_rebuild:
          raise IndexStaleError(
              f"Index is stale: {status.reason}\n"
              f"Run 'jigy index --rebuild' to update, or use --auto-rebuild"
          )
      
      # Notify user
      if show_progress:
          click.echo(click.style(
              f"⚠ Index is stale ({status.reason}), rebuilding...",
              fg="yellow"
          ))
      
      # Rebuild
      from jig.core.index_builder import rebuild_index
      try:
          start_time = time.time()
          result = rebuild_index(intent_dir, show_progress=show_progress)
          duration = time.time() - start_time
          
          if show_progress:
              click.echo(click.style(
                  f"✓ Index rebuilt: {result.nodes_count} nodes, "
                  f"{result.edges_count} edges ({duration:.1f}s)",
                  fg="green"
              ))
      except Exception as e:
          raise IndexRebuildError(
              f"Failed to rebuild index: {e}\n"
              f"Try 'jigy index --rebuild --verbose' for details"
          ) from e
  ```

**Test Plan:**
- Unit: Test fresh index (fast path)
- Unit: Test stale index with auto_rebuild=True (rebuilds)
- Unit: Test stale index with auto_rebuild=False (raises error)
- Unit: Test rebuild failure handling
- Integration: Test with real jig codebase
- Test file: `tests/unit/test_auto_rebuild.py`

**Docs to Update:**
- None yet (internal API)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Next experiment:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
```bash
cd /Users/jmeyer/Code/jig
pytest tests/unit/test_auto_rebuild.py -v
# Test manually by touching a source file
touch jig/outcomes/O-JIGY-001.md
python -c "
from pathlib import Path
from jig.core.staleness import ensure_index_fresh
ensure_index_fresh(Path('jig'))
"
# Should see rebuild message
```

---

### Work Unit 6: Integrate Auto-Rebuild into CLI Commands

**Implements:** S-INDEX-002 (user-facing integration)

**Goal:** All CLI commands check and rebuild index before operating on graph

**Planned Effort:** 90m

**Acceptance Criteria:**
- Commands that load graph call `ensure_index_fresh()` before `Graph.load_from_dir()`
- Commands affected:
  - `jigy graph show`
  - `jigy graph list`
  - `jigy graph deps`
  - `jigy graph impact`
  - `jigy graph path`
  - `jigy decompose metrics`
  - `jigy validate` (with annotations)
- All commands get `--no-auto-rebuild` flag (default: False)
- Help text explains the flag
- Consistent user experience across all commands

**Implementation Notes:**
- Create helper in `src/jig/cli/common.py`:
  ```python
  def load_graph_with_freshness_check(
      config: JigConfig,
      auto_rebuild: bool
  ) -> Graph:
      """Load graph after ensuring index is fresh.
      
      Args:
          config: JIG configuration
          auto_rebuild: Whether to auto-rebuild stale index
          
      Returns:
          Loaded Graph object
          
      Raises:
          IndexStaleError: If stale and auto_rebuild=False
          IndexRebuildError: If rebuild fails
      """
      ensure_index_fresh(config.intent_dir, auto_rebuild=auto_rebuild)
      return Graph.load_from_dir(config.intent_dir)
  ```
- Update each CLI command:
  ```python
  @graph.command("list")
  @click.option("--no-auto-rebuild", is_flag=True, help="Disable automatic index rebuild")
  def list_nodes(..., no_auto_rebuild: bool):
      config = JigConfig.load()
      graph = load_graph_with_freshness_check(config, auto_rebuild=not no_auto_rebuild)
      # ... rest of command
  ```
- Consistent pattern across all commands

**Test Plan:**
- Integration: Test each command with stale index
- Integration: Test each command with `--no-auto-rebuild`
- Integration: Test rebuild message appears correctly
- Test file: `tests/integration/test_auto_rebuild_cli.py`

**Docs to Update:**
- CLI help text (automatic via click options)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Next experiment:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
```bash
cd /Users/jmeyer/Code/jig
# Make index stale
touch jig/outcomes/O-JIGY-001.md
# Test commands auto-rebuild
jigy graph list
# Should see rebuild message
jigy graph show O-JIGY-001
# Should NOT rebuild (already fresh)
jigy decompose metrics --subsystem jigy-tool
# Should work now (was the original bug!)
# Test --no-auto-rebuild flag
touch jig/outcomes/O-JIGY-001.md
jigy graph list --no-auto-rebuild
# Should fail with clear error message
```

---

### Work Unit 7: Add Backup and Atomic Write Safety

**Implements:** S-INDEX-003 (enhanced safety)

**Goal:** Ensure index rebuild is safe, atomic, and recoverable

**Planned Effort:** 60m

**Acceptance Criteria:**
- Before rebuild: create `graph-index.yaml.bak` backup
- Rebuild writes to `graph-index.yaml.tmp` first
- After successful rebuild: atomic rename (tmp → final)
- On failure: keep existing index, clean up tmp file
- Backup kept for debugging (not auto-deleted)
- Rebuild validates generated index before writing

**Implementation Notes:**
- Update `rebuild_index()` in `src/jig/core/index_builder.py`:
  ```python
  def rebuild_index(intent_dir: Path, show_progress: bool = False) -> RebuildResult:
      """Rebuild graph-index.yaml from all sources.
      
      Safety guarantees:
      - Creates backup before modifying
      - Atomic write (tmp file + rename)
      - Validates before committing
      - Cleans up on failure
      """
      graph_index_path = intent_dir / "graph-index.yaml"
      backup_path = intent_dir / "graph-index.yaml.bak"
      temp_path = intent_dir / "graph-index.yaml.tmp"
      
      try:
          # 1. Backup existing index
          if graph_index_path.exists():
              shutil.copy2(graph_index_path, backup_path)
          
          # 2. Build new index data
          nodes = []
          edges = []
          # ... scan markdown files
          # ... scan code annotations
          # ... extract relationships
          
          index_data = {
              "version": "1.0.0",
              "generated": datetime.now().isoformat(),
              "nodes": nodes,
              "edges": edges,
              # ... subsystems, etc
          }
          
          # 3. Validate before writing
          validate_index_structure(index_data)
          
          # 4. Write to temp file
          with temp_path.open('w') as f:
              yaml.dump(index_data, f)
          
          # 5. Validate temp file can be loaded
          test_graph = Graph.load_from_file(temp_path)
          
          # 6. Atomic rename
          temp_path.rename(graph_index_path)
          
          return RebuildResult(
              nodes_count=len(nodes),
              edges_count=len(edges),
              # ...
          )
          
      except Exception as e:
          # Cleanup on failure
          if temp_path.exists():
              temp_path.unlink()
          raise IndexRebuildError(f"Rebuild failed: {e}") from e
  ```

**Test Plan:**
- Unit: Test backup creation
- Unit: Test atomic write (simulate crash during write)
- Unit: Test validation failure (bad index rejected)
- Unit: Test cleanup on failure (no tmp file left)
- Integration: Test real rebuild creates backup

**Docs to Update:**
- None (internal safety feature)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
```bash
cd /Users/jmeyer/Code/jig
# Rebuild and check backup created
jigy index --rebuild
ls -la jig/graph-index.yaml.bak
# Should exist with previous content
# Check no tmp files left
ls -la jig/graph-index.yaml.tmp
# Should not exist
```

---

### Work Unit 8: Remove Fallback Logic from Graph List

**Implements:** O-INDEX-001 (single source of truth)

**Goal:** Remove fallback to node frontmatter in `jigy graph list`, use only index

**Planned Effort:** 45m

**Acceptance Criteria:**
- `jigy graph list --subsystem X` uses only `graph-index.yaml` subsystem data
- No fallback to reading individual node frontmatter
- Behavior consistent with `jigy decompose metrics`
- Warning message removed: "Subsystem 'X' not defined in graph-index.yaml..."
- If subsystem not in index: auto-rebuild detects stale index and rebuilds
- Tests updated to reflect new behavior

**Implementation Notes:**
- Update `src/jig/cli/graph.py` in `list_nodes()` function:
  ```python
  @graph.command("list")
  # ... options
  def list_nodes(...):
      config = JigConfig.load()
      g = load_graph_with_freshness_check(config, auto_rebuild=not no_auto_rebuild)
      
      if subsystem:
          # Only use hierarchical subsystem path resolution (v7)
          subsys = g.get_subsystem_by_path(subsystem)
          
          if not subsys:
              # No fallback - index should be up-to-date
              click.echo(
                  click.style(f"Error: Subsystem '{subsystem}' not found", fg="red")
              )
              sys.exit(1)
          
          node_ids = subsys.get_all_nodes(recursive=recursive)
          nodes = [g.nodes[nid] for nid in node_ids if nid in g.nodes]
          
          if node_type:
              nodes = [n for n in nodes if n.type == node_type]
      # ... rest of function
  ```
- Remove old fallback code block completely
- Update tests to expect consistent behavior

**Test Plan:**
- Unit: Test subsystem not found (should error, not fall back)
- Integration: Test with ASE-A (rebuild should populate subsystems)
- Regression: Ensure other commands still work

**Docs to Update:**
- None (behavior now consistent)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
```bash
cd /Users/jmeyer/Code/jig
# Should work (auto-rebuild populates subsystems)
jigy graph list --subsystem jigy-tool
# Should work now (was the bug!)
cd /Users/jmeyer/Code/ASE-A
jigy graph list --subsystem airspace
jigy decompose metrics --subsystem airspace
# Both should work consistently
```

---

### Work Unit 9: ASE-A Validation and Testing

**Validates:** O-INDEX-001, O-INDEX-002, O-INDEX-003

**Goal:** Verify auto-rebuild works correctly on ASE-A project, fixing original bug

**Planned Effort:** 90m

**Acceptance Criteria:**
- ASE-A subsystem "airspace" is discovered and populated in rebuilt index
- `jigy graph list --subsystem airspace` works (no longer uses fallback)
- `jigy decompose metrics --subsystem airspace` works (original bug fixed!)
- Both commands show consistent results
- Auto-rebuild performance acceptable (<5s for ASE-A size)
- All ASE-A JIG commands work with auto-rebuild

**Implementation Notes:**
- Test workflow in ASE-A:
  1. Delete or corrupt graph-index.yaml
  2. Run `jigy graph list --subsystem airspace`
  3. Should auto-rebuild and work
  4. Run `jigy decompose metrics --subsystem airspace`
  5. Should use fresh index and work (no rebuild needed)
- Verify subsystem population logic:
  - Scans markdown frontmatter `subsystem:` fields
  - Builds subsystem tree from node assignments
  - Includes in graph-index.yaml `subsystems:` section
- Document any ASE-A-specific issues found

**Test Plan:**
- Integration: Full test of ASE-A commands
- Performance: Measure rebuild time for ASE-A (126 nodes, 113 edges)
- Regression: Ensure all other ASE-A queries still work
- Validation: `jigy validate` passes

**Docs to Update:**
- S019 PROPOSAL: Add "Implementation Results" section

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
```bash
cd /Users/jmeyer/Code/ASE-A
# Test the original bug scenario
rm jig/graph-index.yaml  # Force rebuild
jigy graph list --subsystem airspace
# Should auto-rebuild and show airspace nodes
jigy decompose metrics --subsystem airspace
# Should work now! (was broken before)
# Verify performance
time jigy index --rebuild
# Should complete in <5s
# Full validation
jigy validate --check-all
jigy status
```

---

### Work Unit 10: Documentation and Examples

**Supports:** O-INDEX-002 (understanding rebuilds)

**Goal:** Document staleness detection, auto-rebuild behavior, and troubleshooting

**Planned Effort:** 60m

**Acceptance Criteria:**
- README.md updated with auto-rebuild explanation
- User guide section on index management
- Examples of:
  - Auto-rebuild in action
  - Using `--no-auto-rebuild` in CI
  - Manual rebuild with `jigy index --rebuild`
  - Recovering from failed rebuild (use backup)
- Troubleshooting guide for common issues
- Performance expectations documented

**Implementation Notes:**
- Documentation structure:
  ```markdown
  ## Index Management
  
  ### Automatic Rebuild
  
  jigy automatically detects when your index is stale and rebuilds it:
  
  ```bash
  $ jigy graph list
  ⚠ Index is stale (source files newer), rebuilding...
  ✓ Index rebuilt: 42 nodes, 38 edges (0.3s)
  
  [continues with command output]
  ```
  
  ### Disabling Auto-Rebuild
  
  For CI or production environments:
  
  ```bash
  jigy graph list --no-auto-rebuild
  # Fails if stale, requires pre-built index
  ```
  
  ### Manual Rebuild
  
  ```bash
  jigy index --rebuild
  # Regenerates graph-index.yaml from sources
  ```
  
  ### Recovery
  
  If rebuild fails, your previous index is backed up:
  
  ```bash
  cd jig/
  cp graph-index.yaml.bak graph-index.yaml
  ```
  ```
- Add FAQ section for common questions
- Performance expectations: <5s for 100 files, <50ms staleness check

**Test Plan:**
- Review: Have fresh eyes read docs
- Validation: Run all documented examples
- Completeness: Check all features documented

**Docs to Update:**
- README.md: Add "Index Management" section
- docs/user-guide.md: Add troubleshooting section
- CHANGELOG.md: Document auto-rebuild feature

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Discoveries:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
```bash
# Follow documentation examples from scratch
# Verify all commands work as documented
```

---

## Completion Summary

(To be filled after all work units complete)

### Summary
- Scope delivered: …
- Key decisions: …
- Deltas from SCOPE: …

### Metrics
- Units: <count>; median cycle time: <min>
- Rework rate (units reopened): <pct>
- Markers captured: <count> (#DISCOVERY, #DECISION, #LEARNED)

### Reflection Roll-up
- Repeatable wins: …
- Systemic frictions (top 3): …
- Open questions for next plan: …

### Harvest Preparation (JIG)
**Markers Summary:**
- Discoveries: <count>
- Decisions: <count>
- Learned patterns: <count>

**Recommended OSTC Nodes (from DISCOVERIES only):**
(AIA proposes based on #DISCOVERY markers - these are NEW constraints learned during implementation)

**Subsystems Touched:** jigy-tool

**Next Step:** `jig ai-distill --branch index-staleness-detection`

---

## Success Metrics

- ✅ Zero "subsystem not found" errors when subsystem exists in sources
- ✅ All commands use consistent data (no fallback paths)
- ✅ Rebuild completes in <5s for typical projects (100 files)
- ✅ Staleness check completes in <50ms
- ✅ User feedback: "behavior is predictable and understandable"

## Related Documents

- S019_PROPOSAL_index-staleness-detection-20251121.md - Original proposal
- S018_PLAN_jigy-core-graph-annotations-20251121.md - Prerequisites (WU8, WU9)
- JIG-Concept-v6.1.md - Source files as primary truth

---

**Status:** DRAFT (awaiting WU0 execution)
**Next Step:** Execute WU0 to create Intent nodes

