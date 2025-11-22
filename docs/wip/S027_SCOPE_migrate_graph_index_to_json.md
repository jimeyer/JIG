# S027 SCOPE: Migrate Graph Index from YAML to JSON

**Created:** 2025-11-22  
**Status:** Draft  
**Priority:** Medium (performance optimization, not blocking)  
**Estimated Effort:** 2-4 hours  
**Related Analysis:** S025_ANALYSIS_graph_index_format_options.md

---

## Problem Statement

The graph-index is currently stored as YAML (`jig/graph-index.yaml`), which was chosen for human-readability when it was expected to be hand-edited. Now that it's a fully generated artifact (via `jigy index rebuild`), the format choice should prioritize:

1. **Performance** - Faster parsing (loaded on every CLI command)
2. **Tooling** - Better ecosystem support
3. **Git-friendliness** - Diff-able for code review (still required)
4. **Safety** - No security concerns

**Current Performance**: 15-20ms parse time for 23KB YAML file (~100 nodes)

**Expected Performance at Scale**: 75-320ms at 2,000 nodes (becomes painful)

---

## Analysis Summary (from S025)

JSON emerged as the optimal format:

| Metric | YAML (current) | JSON (proposed) | Improvement |
|--------|---------------|-----------------|-------------|
| **Parse Time** | 15-20ms | 3-5ms | **3-5x faster** |
| **File Size** | 23KB | 20KB | 13% smaller |
| **Git Diffs** | ✅ Excellent | ✅ Excellent | Maintained |
| **Tooling** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Better |
| **Security** | ⚠️ Safe with safe_load | ✅ Safe by design | Better |
| **Dependencies** | PyYAML (external) | json (stdlib) | Removed dep |

**Key Benefits:**
- 70% reduction in parse time (15ms → 3-5ms)
- Standard library only (remove PyYAML dependency)
- Universal tooling support (jq, JSON Schema, IDE validation)
- Scales to 2,000+ nodes while staying fast (<65ms)

**Trade-offs:**
- Slightly more verbose (more quotes)
- No comment support (not needed for generated files)
- Migration effort required (2-4 hours)

---

## Goals

### Primary Goal
**Migrate graph-index storage format from YAML to JSON** while maintaining full backward compatibility during transition.

### Success Criteria
1. ✅ `jigy index rebuild` generates `graph-index.json` instead of `graph-index.yaml`
2. ✅ All commands load from `graph-index.json` with 3-5x faster parse times
3. ✅ Backward compatibility: Commands can still read legacy `graph-index.yaml` files
4. ✅ All existing tests pass with JSON format
5. ✅ Git diffs remain clean and reviewable
6. ✅ PyYAML dependency removed from core index loading (still needed for node frontmatter)

### Performance Targets
- Current: 15-20ms → Target: 3-5ms (at ~100 nodes)
- At scale (2,000 nodes): <65ms (vs 75-320ms with YAML)

---

## Non-Goals

### Out of Scope for This Change
1. ❌ **Binary formats** (MessagePack, Pickle) - Not git-friendly, deferred to S026 evaluation
2. ❌ **Database storage** (SQLite) - Overkill at current scale
3. ❌ **Incremental index updates** - Separate performance optimization
4. ❌ **Compressed formats** - Adds complexity without clear benefit at current scale
5. ❌ **Multi-file index** - Keep single-file simplicity
6. ❌ **Index caching layer** - May consider later if profiling shows need
7. ❌ **Changing node frontmatter format** - Markdown nodes stay YAML frontmatter

### Explicitly Preserved
- ✅ Git-tracked index (remains in version control)
- ✅ Human-readable format (JSON is still text)
- ✅ Single source of truth (no distributed index files)
- ✅ Diff-able for code review
- ✅ Merge-able (text format enables conflict resolution)

---

## Current State Analysis

### File Structure (graph-index.yaml)
```yaml
version: '1.0'
generated: '2025-11-22T04:26:16.872230+00:00'
nodes:
- id: C-CLI-001
  type: code
  title: C-CLI-001
  subsystem: core
  status: active
  file: /Users/jamesmeyer/Code/jig/src/jig/cli/main.py
  line: 1
  implements:
  - S-JIG-002
# ... ~100 nodes
subsystems:
  core:
    nodes:
    - C-CLI-001
    # ... more nodes
```

**Stats:**
- Size: 23KB (745 lines)
- Nodes: ~100 (mix of O/S/T/C types)
- Subsystems: 5 (core, cli, jigy-tool, decompose, test-fixtures)
- Structure: Hierarchical with nodes array + subsystems map

### Code Locations Using YAML Format

#### 1. Index Builder (Generator)
**File:** `src/jig/core/index_builder.py`
```python
def save(self, output_path: Path):
    """Save index to YAML."""
    with open(output_path, 'w') as f:
        yaml.safe_dump(self.to_dict(), f, sort_keys=False)
```

#### 2. Graph Loader (Consumer)
**File:** `src/jig/core/graph.py`
```python
@classmethod
def load_from_dir(cls, jig_root: Path) -> "Graph":
    """Load graph from directory."""
    index_path = jig_root / "jig" / "graph-index.yaml"
    
    if index_path.exists():
        with open(index_path) as f:
            index_data = yaml.safe_load(f)  # ← YAML parsing
```

#### 3. CLI Commands (Consumers)
**Files:**
- `src/jig/cli/status.py` - Loads index for status display
- `src/jig/cli/validate.py` - Loads index for validation
- `src/jig/cli/graph.py` - Loads index for graph queries
- `src/jig/cli/index.py` - Saves index after rebuild

#### 4. Tests (Fixtures)
**Locations:**
- `tests/integration/test_index_rebuild.py`
- `tests/unit/test_graph.py`
- Test fixtures in `tests/fixtures/` (if any)

---

## Proposed Changes

### Change 1: Update Index Builder to Generate JSON

**File:** `src/jig/core/index_builder.py`

**Before:**
```python
import yaml

def save(self, output_path: Path):
    """Save index to YAML."""
    with open(output_path, 'w') as f:
        yaml.safe_dump(self.to_dict(), f, sort_keys=False)
```

**After:**
```python
import json

def save(self, output_path: Path):
    """Save index to JSON with pretty-printing."""
    with open(output_path, 'w') as f:
        json.dump(
            self.to_dict(), 
            f, 
            indent=2,
            ensure_ascii=False,
            sort_keys=False
        )
```

**Rationale:**
- `indent=2`: Pretty-print for git diffs (2-space standard)
- `ensure_ascii=False`: Allow Unicode characters
- `sort_keys=False`: Preserve logical ordering (version/generated first)

---

### Change 2: Update Graph Loader with Backward Compatibility

**File:** `src/jig/core/graph.py`

**Before:**
```python
@classmethod
def load_from_dir(cls, jig_root: Path) -> "Graph":
    """Load graph from directory."""
    index_path = jig_root / "jig" / "graph-index.yaml"
    
    if index_path.exists():
        with open(index_path) as f:
            index_data = yaml.safe_load(f)
```

**After:**
```python
@classmethod
def load_from_dir(cls, jig_root: Path) -> "Graph":
    """Load graph from directory, supporting both JSON and YAML."""
    json_path = jig_root / "jig" / "graph-index.json"
    yaml_path = jig_root / "jig" / "graph-index.yaml"
    
    # Prefer JSON (new format)
    if json_path.exists():
        with open(json_path) as f:
            index_data = json.load(f)
    # Fallback to YAML (legacy format)
    elif yaml_path.exists():
        import yaml  # Lazy import for legacy support
        with open(yaml_path) as f:
            index_data = yaml.safe_load(f)
    else:
        index_data = None
```

**Rationale:**
- Try JSON first (fast path for new installs)
- Fallback to YAML (supports existing repos)
- Lazy import of yaml (only when needed)
- No breaking changes for existing users

---

### Change 3: Update CLI Index Command

**File:** `src/jig/cli/index.py`

**Before:**
```python
output_path = jig_root / "jig" / "graph-index.yaml"
builder.save(output_path)
click.echo(f"✓ Index rebuilt: {output_path}")
```

**After:**
```python
output_path = jig_root / "jig" / "graph-index.json"
builder.save(output_path)

# Clean up legacy YAML file if it exists
legacy_path = jig_root / "jig" / "graph-index.yaml"
if legacy_path.exists():
    legacy_path.rename(jig_root / "jig" / "graph-index.yaml.bak")
    click.echo(f"ℹ Legacy YAML backed up to graph-index.yaml.bak")

click.echo(f"✓ Index rebuilt: {output_path}")
```

**Rationale:**
- Generate JSON by default
- Preserve legacy YAML as backup (user can delete manually)
- Clear migration messaging

---

### Change 4: Update .gitignore (if needed)

**File:** `.gitignore`

**Check for:**
```
jig/graph-index.yaml
```

**Update to:**
```
jig/graph-index.yaml.bak  # Backup from migration
# Note: graph-index.json IS tracked (replaces graph-index.yaml)
```

**Rationale:**
- Backup files shouldn't be committed
- Primary index (JSON) remains tracked

---

### Change 5: Update Tests

**Files:** All test files that create or read graph-index

**Changes:**
1. Update fixture generation to use JSON
2. Update assertions to check for `.json` extension
3. Keep backward compatibility tests for YAML loading

**Example Test Update:**
```python
# Before
def test_index_rebuild(tmp_path):
    index_path = tmp_path / "jig" / "graph-index.yaml"
    # ... test code

# After
def test_index_rebuild(tmp_path):
    index_path = tmp_path / "jig" / "graph-index.json"
    # ... test code
    
def test_legacy_yaml_loading(tmp_path):
    """Ensure backward compatibility with YAML."""
    yaml_path = tmp_path / "jig" / "graph-index.yaml"
    # ... test YAML fallback
```

---

### Change 6: Update Documentation

**Files to Update:**
- `README.md` - Mention JSON format
- `docs/architecture/GRAPH_SUBSYSTEM.md` - Update format references
- `docs/user-guide/*.md` - Update any examples

**Example:**
```markdown
# Before
The graph index is stored in `jig/graph-index.yaml`

# After
The graph index is stored in `jig/graph-index.json` (generated by `jigy index rebuild`)
```

---

## Migration Strategy

### Phase 1: Implementation (2 hours)
1. Update `IndexBuilder.save()` to generate JSON
2. Update `Graph.load_from_dir()` with backward compatibility
3. Update CLI command to use `.json` extension
4. Run local tests

### Phase 2: Testing (1 hour)
1. Update unit tests for JSON format
2. Add backward compatibility test for YAML
3. Test migration path:
   - Start with `graph-index.yaml`
   - Run `jigy index rebuild`
   - Verify `graph-index.json` created
   - Verify commands work with JSON
4. Verify git diffs are clean

### Phase 3: Migration (30 min)
1. Run `jigy index rebuild` on jig project itself
2. Verify `graph-index.json` generated
3. Backup `graph-index.yaml`
4. Commit new JSON format
5. Update documentation

### Phase 4: Cleanup (30 min)
1. Monitor for issues
2. After grace period (1 week), consider removing YAML fallback
3. Update dependency list (PyYAML still needed for frontmatter)

---

## Backward Compatibility

### Supported Scenarios

#### Scenario 1: Fresh Clone (New Users)
```bash
$ git clone jig-repo
$ jigy status
  # Loads graph-index.json (fast, no YAML code path)
```
**Impact:** None, works out of the box

#### Scenario 2: Existing Repo with YAML (Existing Users)
```bash
$ git pull  # Gets code update
  # Still has graph-index.yaml locally

$ jigy status
  # Falls back to graph-index.yaml (works)

$ jigy index rebuild
  # Generates graph-index.json
  # Backs up graph-index.yaml → graph-index.yaml.bak
  
$ jigy status
  # Now uses graph-index.json (faster!)
```
**Impact:** Seamless transition, no breaking changes

#### Scenario 3: Mixed Team (During Rollout)
```bash
# Developer A (updated code)
$ jigy index rebuild
  # Generates graph-index.json
$ git add jig/graph-index.json
$ git commit -m "Migrate to JSON format"

# Developer B (old code, hasn't pulled yet)
$ jigy status  # Still works with local YAML

$ git pull  # Gets new JSON file
$ jigy status  # Old code can't read JSON → error

# Developer B updates their code
$ git pull  # Gets updated jigy command
$ jigy status  # Works with JSON
```
**Impact:** ⚠️ Requires coordinated update (code + data together)

**Mitigation:**
- Document in PR: "Requires jigy code update"
- Or: Keep YAML fallback indefinitely (minimal cost)

---

## Risk Assessment

### Low Risks ✅

1. **Data Loss**
   - Risk: Conversion loses data
   - Mitigation: JSON and YAML are isomorphic for this data structure
   - Testing: Compare parsed data before/after

2. **Git Conflicts**
   - Risk: JSON more conflict-prone than YAML
   - Mitigation: Both are text formats, similar conflict resolution
   - Testing: Merge test branches with different changes

3. **Performance Regression**
   - Risk: JSON slower than expected
   - Mitigation: Benchmark shows 3-5x improvement
   - Testing: Performance benchmarks in tests

### Medium Risks ⚠️

4. **Team Coordination**
   - Risk: Mixed old/new code during rollout
   - Mitigation: Keep YAML fallback for grace period
   - Timeline: 1 week grace period, then remove fallback

5. **Tooling Dependencies**
   - Risk: External tools expect YAML
   - Mitigation: Survey shows no external tools currently
   - Testing: Check CI/CD scripts

### No Identified High Risks

---

## Testing Strategy

### Unit Tests

1. **Test JSON Generation**
```python
def test_index_builder_generates_json():
    builder = IndexBuilder()
    # ... add nodes
    builder.save(tmp_path / "graph-index.json")
    
    with open(tmp_path / "graph-index.json") as f:
        data = json.load(f)
    
    assert data["version"] == "1.0"
    assert len(data["nodes"]) == expected_count
```

2. **Test JSON Loading**
```python
def test_graph_loads_from_json():
    graph = Graph.load_from_dir(jig_root)
    assert len(graph.nodes) == expected_count
```

3. **Test YAML Backward Compatibility**
```python
def test_graph_loads_from_yaml_legacy():
    # Remove JSON, keep only YAML
    (jig_root / "jig" / "graph-index.json").unlink()
    
    graph = Graph.load_from_dir(jig_root)
    assert len(graph.nodes) == expected_count
```

4. **Test JSON Preference**
```python
def test_json_preferred_over_yaml():
    # Create both files with different data
    create_json_index(nodes=10)
    create_yaml_index(nodes=5)
    
    graph = Graph.load_from_dir(jig_root)
    assert len(graph.nodes) == 10  # Loaded from JSON
```

### Integration Tests

5. **Test Full Rebuild Workflow**
```bash
$ jigy index rebuild
$ test -f jig/graph-index.json  # JSON created
$ jigy status  # Can read it
$ jigy validate  # Can read it
$ jigy graph show S-CLI-001  # Can read it
```

6. **Test Migration Workflow**
```bash
# Start with YAML
$ cp jig/graph-index.yaml.bak jig/graph-index.yaml
$ rm jig/graph-index.json

$ jigy index rebuild
$ test -f jig/graph-index.json  # JSON created
$ test -f jig/graph-index.yaml.bak  # YAML backed up
```

### Performance Tests

7. **Benchmark Parse Time**
```python
def test_json_faster_than_yaml():
    yaml_time = timeit(lambda: load_yaml_index(), number=100)
    json_time = timeit(lambda: load_json_index(), number=100)
    
    assert json_time < yaml_time * 0.5  # At least 2x faster
```

---

## Performance Benchmarking

### Benchmark Script
```python
# scripts/benchmark_index_parsing.py

import timeit
import json
import yaml
from pathlib import Path

def benchmark_formats(index_path: Path):
    """Compare YAML vs JSON parsing performance."""
    
    # Load YAML (if exists)
    yaml_path = index_path.parent / "graph-index.yaml"
    if yaml_path.exists():
        yaml_data = yaml_path.read_text()
        yaml_time = timeit.timeit(
            lambda: yaml.safe_load(yaml_data),
            number=1000
        ) / 1000
        print(f"YAML:  {yaml_time*1000:.2f}ms per parse")
    
    # Load JSON
    json_path = index_path.parent / "graph-index.json"
    if json_path.exists():
        json_data = json_path.read_text()
        json_time = timeit.timeit(
            lambda: json.loads(json_data),
            number=1000
        ) / 1000
        print(f"JSON:  {json_time*1000:.2f}ms per parse")
        
        if yaml_path.exists():
            speedup = yaml_time / json_time
            print(f"Speedup: {speedup:.1f}x faster")
```

**Expected Results:**
```
YAML:  15.3ms per parse
JSON:   3.8ms per parse
Speedup: 4.0x faster
```

---

## Documentation Updates

### README.md
```markdown
## Architecture

JIG stores its intent graph in `jig/graph-index.json`, which is automatically 
generated by scanning code annotations and markdown node files.

### Rebuilding the Index

```bash
jigy index rebuild
```

This regenerates `jig/graph-index.json` from source files.
```

### Changelog Entry
```markdown
## [Unreleased]

### Changed
- **BREAKING**: Graph index format changed from YAML to JSON for 3-5x faster parsing
  - Old: `jig/graph-index.yaml`
  - New: `jig/graph-index.json`
  - Backward compatibility: Commands can still read legacy YAML files
  - Migration: Run `jigy index rebuild` to generate new JSON format

### Improved
- Graph index parsing is now 3-5x faster (15ms → 3-5ms at ~100 nodes)
- Removed runtime dependency on PyYAML for index loading
- Better tooling support (JSON Schema validation, jq compatibility)

### Removed
- PyYAML is no longer required for core operations (still used for node frontmatter)
```

---

## Rollback Plan

### If Issues Arise

**Step 1: Immediate Rollback (Revert Code)**
```bash
git revert <commit-hash>
git push
```

**Step 2: Restore YAML Index**
```bash
cp jig/graph-index.yaml.bak jig/graph-index.yaml
git add jig/graph-index.yaml
git commit -m "Rollback to YAML format"
```

**Step 3: Communicate to Team**
- Notify team of rollback
- Document issues encountered
- Plan remediation

### Rollback Criteria
Rollback if:
- ❌ Performance regression (JSON slower than YAML)
- ❌ Data corruption (nodes missing after conversion)
- ❌ Breaking changes for team (coordination issues)
- ❌ Git diff quality degraded
- ❌ Critical bug in JSON loading/saving

---

## Success Metrics

### Quantitative Metrics
1. ✅ Parse time reduced by >50% (target: 70%)
2. ✅ File size reduced by >10% (target: 13%)
3. ✅ All tests passing (100%)
4. ✅ No regressions in git diff size

### Qualitative Metrics
5. ✅ Git diffs remain clean and reviewable
6. ✅ No team member reports issues during migration
7. ✅ Documentation updated and clear
8. ✅ Backward compatibility preserved

### Performance Validation
```bash
# Before (YAML)
$ time jigy status >/dev/null
real    0m0.055s  # ~55ms total

# After (JSON)
$ time jigy status >/dev/null
real    0m0.040s  # ~40ms total (27% faster)
```

---

## Dependencies

### Code Dependencies
- **Remove:** Runtime dependency on PyYAML for index operations
- **Keep:** PyYAML still required for markdown node frontmatter parsing
- **Add:** None (json is stdlib)

### External Dependencies
- None (JSON is universal)

### Team Dependencies
- Developers must update to new code before pulling JSON index
- **OR** keep YAML fallback indefinitely (minimal cost)

---

## Timeline

### Recommended Schedule

**Day 1 (2 hours):**
- Implement IndexBuilder JSON generation
- Implement Graph JSON loading with YAML fallback
- Update CLI commands

**Day 1-2 (1 hour):**
- Write/update tests
- Run test suite
- Fix any failures

**Day 2 (30 min):**
- Run migration on jig project itself
- Generate graph-index.json
- Test all commands
- Commit changes

**Day 2-3 (30 min):**
- Update documentation
- Write PR description
- Team review

**Week 1 (grace period):**
- Monitor for issues
- Keep YAML fallback active

**Week 2+ (optional):**
- Remove YAML fallback code
- Update benchmarks
- Close migration ticket

---

## Open Questions

### For Discussion

1. **Graceful Degradation:**
   - Should we keep YAML fallback indefinitely or remove after grace period?
   - **Recommendation:** Keep indefinitely (minimal cost, max compatibility)

2. **Backup Strategy:**
   - Should we auto-backup YAML → .bak or let user delete manually?
   - **Recommendation:** Auto-backup with message

3. **Performance Baseline:**
   - Should we add performance regression tests?
   - **Recommendation:** Yes, add benchmark to CI

4. **JSON Schema:**
   - Should we add JSON Schema validation now or later?
   - **Recommendation:** Later (separate enhancement)

5. **Pretty-Print Settings:**
   - 2-space indent (current standard) or 4-space?
   - **Recommendation:** 2-space (more compact, Python standard)

---

## References

- **S025**: Analysis of format options (this decision basis)
- **S026**: Binary format evaluation (deferred alternative)
- **RFC 8259**: JSON specification
- **O-JIG-001**: Performance outcome (<1s operations)
- **O-JIG-002**: Simple text formats outcome

---

## Approval Checklist

Before implementation:
- [ ] Technical approach reviewed
- [ ] Migration strategy approved
- [ ] Backward compatibility confirmed
- [ ] Testing strategy validated
- [ ] Team coordination plan agreed
- [ ] Documentation scope approved
- [ ] Timeline realistic
- [ ] Success metrics defined

---

**Status:** Ready for review and approval

**Next Steps:**
1. Review this scope document
2. Approve or request changes
3. Create implementation task
4. Execute migration

---

## Appendix A: File Size Comparison

**Current (YAML):**
```bash
$ ls -lh jig/graph-index.yaml
-rw-r--r--  23K  graph-index.yaml
```

**After (JSON, estimated):**
```bash
$ ls -lh jig/graph-index.json
-rw-r--r--  20K  graph-index.json  # ~13% smaller
```

---

## Appendix B: Example Format Comparison

**YAML:**
```yaml
nodes:
- id: C-CLI-001
  type: code
  title: C-CLI-001
  subsystem: core
  status: active
  file: /path/to/file.py
  line: 1
  implements:
  - S-JIG-002
```

**JSON:**
```json
{
  "nodes": [
    {
      "id": "C-CLI-001",
      "type": "code",
      "title": "C-CLI-001",
      "subsystem": "core",
      "status": "active",
      "file": "/path/to/file.py",
      "line": 1,
      "implements": ["S-JIG-002"]
    }
  ]
}
```

**Diff Quality (both formats):**
- ✅ Line-by-line changes visible
- ✅ Field additions/removals clear
- ✅ Array changes tracked
- ✅ Merge conflicts resolvable

---

**End of Scope Document**

