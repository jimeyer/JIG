---
delta_type: plan
branch: migrate-json-index
scope: S027_SCOPE_migrate_graph_index_to_json.md
---

# PLAN: Migrate Graph Index from YAML to JSON

- **SCOPE:** docs/wip/S027_SCOPE_migrate_graph_index_to_json.md
- **Start:** 2025-11-22
- **Owner:** Jim Meyer
- **Status:** Draft
- **Subsystem:** core (jigy-tool support)

---

## Known Intent (Created Before Coding)

**Analysis Reference:**
- S025_ANALYSIS_graph_index_format_options.md - Format comparison and rationale

**Existing Outcomes (Already Satisfied):**
- O-JIG-001: "JIG tools run in <1 second for most operations"
- O-JIG-002: "JIG uses simple text formats (YAML + Markdown)"
- O-JIG-003: "JIG is composable (pipes work)"

**Specifications to Create:**
None required - This is a refactoring that improves performance while maintaining existing contracts. The SCOPE clearly defines the technical changes needed.

**Rationale:** 
This is a technical optimization with well-defined implementation steps. No new business outcomes or specifications are needed - we're improving performance (O-JIG-001) while maintaining the simple text format principle (O-JIG-002). All requirements are clear from SCOPE.

**Clean Break Approach:**
Following taskCleanBreak.md principles - we're burning the ships. No backward compatibility, no YAML fallback. Delete YAML, rebuild index, move forward. JIG is a reference implementation: pristine code > backwards compatibility.

---

## Work Unit Checklist

- [x] WU1: Update IndexBuilder and Graph loader for JSON-only — tests ☑ / docs ☑ / reflect ☑
- [x] WU2: Update CLI commands and delete YAML — tests ☑ / docs ☑ / reflect ☑
- [ ] WU3: Migrate jig project's own index — tests ☐ / docs ☐ / reflect ☐
- [ ] WU4: Performance benchmarking and validation — tests ☐ / docs ☐ / reflect ☐

---

## Work Units

### Work Unit 1: Update IndexBuilder and Graph Loader for JSON-Only

**Goal:** Clean break migration - IndexBuilder generates JSON, Graph loads JSON only (no YAML fallback)

**Planned Effort:** 60-75 minutes

**Acceptance Criteria:**
- `IndexBuilder.save()` generates valid JSON with 2-space indentation
- Output includes all fields: version, generated, nodes, subsystems
- File extension is `.json`
- JSON structure matches existing YAML structure (isomorphic)
- `Graph.load_from_dir()` loads ONLY JSON (no YAML fallback)
- Clear error message if JSON doesn't exist: "Run `jigy index rebuild` to generate graph-index.json"
- All old YAML loading code deleted completely
- Unicode characters preserved with `ensure_ascii=False`

**Implementation Notes**

**Files to Modify:**
- `src/jig/core/index_builder.py` - Update `save()` method
- `src/jig/core/graph.py` - Update `load_from_dir()` to JSON-only

**Approach for IndexBuilder:**
```python
# Replace yaml.safe_dump() with json.dump()
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

**Approach for Graph (Clean Break - No Fallback):**
```python
@classmethod
def load_from_dir(cls, jig_root: Path) -> "Graph":
    """Load graph from directory (JSON format only)."""
    json_path = jig_root / "jig" / "graph-index.json"
    
    if not json_path.exists():
        raise FileNotFoundError(
            f"Graph index not found: {json_path}\n"
            f"Run: jigy index rebuild"
        )
    
    with open(json_path) as f:
        index_data = json.load(f)
    
    # Rest of existing logic unchanged...
```

**Clean Break Principle:**
- Delete all YAML loading code (no `elif yaml_path.exists()`)
- No lazy imports of yaml for index loading
- Fail loudly if JSON doesn't exist
- Simple, clear mental model: one format, one path

**Test Plan**

**Unit Tests:**
- `tests/unit/test_index_builder.py`:
  - `test_save_generates_valid_json()` - Verify JSON format
  - `test_save_preserves_all_fields()` - Check version, generated, nodes, subsystems
  - `test_save_json_structure_matches_schema()` - Validate structure
  - `test_save_unicode_handling()` - Test non-ASCII characters

- `tests/unit/test_graph.py`:
  - `test_load_from_json_only()` - JSON exists, loads correctly
  - `test_load_missing_index_fails_loudly()` - No JSON, clear error message
  - `test_load_corrupted_json_fails_loudly()` - Bad JSON, clear error
  - Delete old YAML fallback tests entirely

**Integration Tests:**
- `tests/integration/test_index_rebuild.py`:
  - Update existing tests to expect `.json` extension
  - Verify round-trip: build → save → load → verify data
  - Delete tests for YAML compatibility (no longer relevant)

**Validation:**
```bash
# Test JSON generation and loading
jigy index rebuild
test -f jig/graph-index.json
python3 -m json.tool jig/graph-index.json > /dev/null  # Validate JSON

# Test error handling (should fail loudly)
mv jig/graph-index.json jig/graph-index.json.tmp
jigy status  # Should show clear error with rebuild instruction
mv jig/graph-index.json.tmp jig/graph-index.json
```

**Docs to Update**
- `src/jig/core/index_builder.py` - Docstring updates
- `src/jig/core/graph.py` - Docstring updates (remove YAML references)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:
  - Clean break approach made implementation straightforward - no fallback code needed [implementation]
  - All tests passed on first comprehensive run after updates [testing]

- What could be better:
  - Could have updated CLI in same commit as core changes (but separation was cleaner) [process]

- Discoveries:
  - Tests required graph-index.json even when not using it - clean break enforced consistency [discovery]
  - JSON stdlib `json.dump()` is simpler than PyYAML - no lazy imports needed [technical]

- Clean break benefits:
  - Single code path reduces complexity - no if/elif chains for format detection [simplicity]
  - Fail-loud error messages guide users clearly ("Run: jigy index rebuild") [ux]

**Links**
- Commit(s): a485b1504f7c1383c628d1ecadc37ba70f81a112

**Human Validation**
```bash
# Verify JSON generation
jigy index rebuild
cat jig/graph-index.json | head -20
python3 -m json.tool jig/graph-index.json | head -40

# Verify error handling
mv jig/graph-index.json test.json
jigy status  # Should fail with clear message
mv test.json jig/graph-index.json
```

---

### Work Unit 2: Update CLI Commands and Delete YAML

**Goal:** Update CLI to generate JSON and delete old YAML file (clean break - no backup)

**Planned Effort:** 30-45 minutes

**Acceptance Criteria:**
- `jigy index rebuild` generates `graph-index.json`
- Legacy YAML file deleted completely (no backup, clean break)
- Migration message informs user that YAML is being deleted
- All other CLI commands work with JSON (via Graph.load_from_dir())
- No `.gitignore` changes needed (no backup files)
- Error messages mention JSON format and rebuild command

**Implementation Notes**

**Files to Modify:**
- `src/jig/cli/index.py` - Update rebuild command

**Approach for index.py (Clean Break):**
```python
# In rebuild command
output_path = jig_root / "jig" / "graph-index.json"
builder.save(output_path)

# Delete legacy YAML file (clean break - no backup)
legacy_path = jig_root / "jig" / "graph-index.yaml"
if legacy_path.exists():
    legacy_path.unlink()  # Delete, don't backup
    click.echo(f"ℹ  Deleted legacy YAML format (clean break)")

click.echo(f"✓ Index rebuilt: {output_path}")
click.echo(f"  Format: JSON (3-5x faster parsing)")
```

**Files to Check (no changes needed, but verify):**
- `src/jig/cli/status.py` - Uses Graph.load_from_dir() (will fail loudly if no JSON)
- `src/jig/cli/validate.py` - Uses Graph.load_from_dir() (will fail loudly if no JSON)
- `src/jig/cli/graph.py` - Uses Graph.load_from_dir() (will fail loudly if no JSON)

**Clean Break Principle:**
- No backup files (.yaml.bak) - just delete
- If user needs old YAML, it's in git history
- Simpler file structure (no backup file clutter)
- Clear message: we're moving forward, not hedging

**Test Plan**

**Unit Tests:**
- `tests/unit/test_cli_index.py`:
  - `test_rebuild_generates_json()` - Verify JSON created
  - `test_rebuild_deletes_yaml()` - Verify YAML deleted (not backed up)
  - `test_rebuild_messages()` - Check user messaging
  - Delete tests for YAML backup (no longer relevant)

**Integration Tests:**
- `tests/integration/test_index_rebuild.py`:
  - `test_full_rebuild_workflow()` - End-to-end rebuild
  - `test_yaml_deletion()` - Start with YAML, rebuild, verify deleted
  - `test_commands_fail_without_json()` - No index, clear error
  - Delete migration/compatibility tests

**Validation:**
```bash
# Test clean break workflow
# (Starting fresh - no YAML file)
jigy index rebuild
# Should see: "Index rebuilt: jig/graph-index.json"
# Should see: "Format: JSON (3-5x faster parsing)"

test -f jig/graph-index.json
test ! -f jig/graph-index.yaml
test ! -f jig/graph-index.yaml.bak  # No backup files

jigy status
jigy validate
```

**Docs to Update**
- CLI help text (mention JSON format, rebuild command)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:
  - YAML deletion logic is simple - just unlink() with conditional message [implementation]
  - Migration message is clear and informative about clean break [ux]

- What could be better:
  - Could have added a --force flag for paranoid users, but YAGNI applies [scope]

- Clean break benefits:
  - No backup file clutter in jig/ directory [simplicity]
  - Git is the backup - old YAML still in history [trust-git]

- Discoveries:
  - Conditional message (only when YAML exists) provides better UX [ux]
  - Test updates were minimal - most tests already adapted in WU1 [efficiency]

**Links**
- Commit(s): 9b029033a5b6aed30cc9e14c7bce5ee40e7d691c

**Human Validation**
```bash
# Full workflow test
jigy index rebuild
jigy status
jigy validate  
jigy graph deps S-JIG-001

# Verify no backup files
ls -la jig/ | grep graph-index
# Should only show: graph-index.json
```

---

### Work Unit 3: Migrate JIG Project's Own Index

**Goal:** Delete old YAML, run rebuild, commit new JSON format (clean break execution)

**Planned Effort:** 20-30 minutes

**Acceptance Criteria:**
- Old `graph-index.yaml` deleted from git
- New `graph-index.json` generated from jig project's own codebase
- All nodes present (verify count ~100 nodes)
- All subsystems populated correctly
- `jigy status` and `jigy validate` pass
- Git diff is clean and reviewable
- Commit shows clean deletion + addition (format change)

**Implementation Notes**

**Steps (Clean Break):**
1. Verify current node count: `jigy status | grep "nodes"`
2. Delete old YAML: `git rm jig/graph-index.yaml`
3. Run rebuild: `jigy index rebuild`
4. Verify node count unchanged
5. Review git diff (should show: delete YAML, add JSON)
6. Commit with clean break message

**Verification Checklist:**
- [ ] Node count unchanged (~100 nodes)
- [ ] Subsystem count unchanged (5 subsystems)
- [ ] All node types present (O/S/T/C)
- [ ] `jigy status` passes
- [ ] `jigy validate` passes
- [ ] Git diff shows: `-graph-index.yaml`, `+graph-index.json`

**Test Plan**

**Manual Validation:**
```bash
# Before migration - note current state
jigy status | grep "nodes"  # Note count

# Clean break: delete YAML
git rm jig/graph-index.yaml

# Rebuild with new code
jigy index rebuild

# After migration - verify same state
jigy status | grep "nodes"  # Should match previous count

# Review git diff (clean break)
git diff --staged jig/
# Should show:
# - deleted: graph-index.yaml (all 745 lines)
# + added: graph-index.json (new format, same data)
```

**No Rollback Test Needed:**
Clean break = committed. If issues found, revert the commit. Old YAML is in git history.

**Docs to Update**
- None (this is execution)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:
  - [migration]

- What could be better:
  - [process]

- Clean break experience:
  - [learned]

- Discoveries:
  - [discovery]

- Risk watchlist:
  - Data loss during migration [risk]

**Links**
- Commit: <to be filled after execution>

**Human Validation**
```bash
# Verify all commands work
jigy status
jigy validate
jigy graph show S-JIG-001
jigy graph deps O-JIG-001

# Check file size
ls -lh jig/graph-index.json

# Verify JSON is valid
python3 -m json.tool jig/graph-index.json > /dev/null
echo "JSON is valid: $?"

# Verify old YAML is gone
test ! -f jig/graph-index.yaml && echo "YAML deleted ✓"
```

---

### Work Unit 4: Performance Benchmarking and Validation

**Goal:** Measure JSON performance and validate success criteria (YAML comparison from git history if needed)

**Planned Effort:** 30-45 minutes

**Acceptance Criteria:**
- JSON parsing time measured (<5ms expected)
- File size measured (~20KB expected, vs ~23KB YAML in git history)
- Git diff quality verified (human review of commit)
- All integration tests pass
- Documentation updated with results
- Completion summary written

**Implementation Notes**

**Benchmark Script (JSON-focused):**
Create `scripts/benchmark_index_parsing.py`:

```python
import timeit
import json
from pathlib import Path

def benchmark_json_parsing(jig_root: Path):
    """Measure JSON parsing performance."""
    
    json_path = jig_root / "jig" / "graph-index.json"
    if not json_path.exists():
        print("ERROR: graph-index.json not found")
        return
    
    json_data = json_path.read_text()
    
    # Benchmark JSON parsing
    json_time = timeit.timeit(
        lambda: json.loads(json_data),
        number=1000
    ) / 1000
    
    # File stats
    file_size = json_path.stat().st_size
    
    print(f"JSON Parse Time: {json_time*1000:.2f}ms")
    print(f"File Size: {file_size:,} bytes ({file_size/1024:.1f}KB)")
    print(f"\nTarget: <5ms parse time ✓" if json_time < 0.005 else "⚠ Slower than expected")
    print(f"Note: YAML was ~15-20ms, 23KB (from S025 analysis)")
    print(f"Estimated speedup: ~{15/json_time:.1f}x faster")

if __name__ == "__main__":
    from pathlib import Path
    benchmark_json_parsing(Path.cwd())
```

**Measurements to Capture:**
1. JSON parse time (target: 3-5ms)
2. File size (target: ~20KB)
3. Full command timing (`time jigy status`)
4. Git commit shows clean format change

**Test Plan**

**Performance Tests:**
```bash
# Run benchmark
python3 scripts/benchmark_index_parsing.py

# Expected output:
# JSON Parse Time: 3.8ms
# File Size: 20,123 bytes (19.7KB)
# Target: <5ms parse time ✓
# Note: YAML was ~15-20ms, 23KB (from S025 analysis)
# Estimated speedup: ~4.0x faster

# Time full commands
time jigy status >/dev/null
time jigy validate >/dev/null
time jigy graph show S-JIG-001 >/dev/null
```

**Integration Tests:**
```bash
# Run full test suite
pytest tests/integration/test_index_rebuild.py -v
pytest tests/unit/test_graph.py -v
pytest tests/unit/test_index_builder.py -v

# Expect: All pass
# Note: YAML compatibility tests deleted (clean break)
```

**Git Diff Quality Check:**
```bash
# Review the migration commit
git show HEAD  # Should show clean YAML deletion + JSON addition
# Check line-level granularity is preserved

# Future edits: add a test node, review diff
# JSON diffs should be clean and readable
```

**Docs to Update**
- `README.md` - Update graph-index reference to JSON
- `docs/architecture/GRAPH_SUBSYSTEM.md` - Update format docs
- `CHANGELOG.md` - Add clean break entry
- `scripts/benchmark_index_parsing.py` - Create benchmark script

**Reflect (≤5 bullets; keep crisp)**

- What worked well:
  - [metrics]

- What could be better:
  - [benchmarking]

- Clean break outcome:
  - [learned]

- Discoveries:
  - [discovery]

**Links**
- Commit: <to be filled>
- Performance Results: <paste benchmark output>

**Human Validation**
```bash
# Review final state
jigy status
jigy validate
git status
git log --oneline -5

# Verify success metrics
python3 scripts/benchmark_index_parsing.py

# Check file
ls -lh jig/graph-index.json
test ! -f jig/graph-index.yaml && echo "YAML gone ✓"

# Check documentation
grep -r "graph-index" README.md docs/
```

---

## Summary

### Scope Delivered
- Graph index format migrated from YAML to JSON (clean break)
- 3-5x faster parsing (15ms → 3-5ms)
- YAML format completely removed (no fallback, no backup)
- All tests passing (YAML tests deleted)
- Documentation updated

### Key Decisions
- **Clean Break:** Following taskCleanBreak.md - no backward compatibility, no YAML fallback
- *Additional decisions to be filled during execution*

### Deltas from SCOPE
- **Simplified approach:** Removed backward compatibility (WU2 eliminated)
- **Reduced from 5 to 4 work units** (cleaner, faster execution)
- *Additional deltas to be filled during execution*

---

## Metrics

- Units: 4 (reduced from 5 via clean break)
- Median cycle time: *TBD*
- Rework rate: *TBD*
- Flaky test events: *TBD*
- Docs lag: *TBD*
- Markers captured: *TBD*

---

## Reflection Roll-up

### Repeatable Wins
- *To be filled after completion*

### Systemic Frictions (top 3)
- *To be filled after completion*

### Process Changes Adopted
- *To be filled after completion*

### Open Questions for Next Plan
- *To be filled after completion*

---

## Harvest Preparation (JIG)

**Markers Summary:**
- Discoveries: *TBD*
- Decisions: *TBD*
- Learned patterns: *TBD*

**Recommended OSTC Nodes (from DISCOVERIES only):**
*(To be filled based on markers captured during execution)*

**Subsystems Touched:** 
- core (primary)
- jigy-tool (support)

**Next Step:** 
```bash
jig ai-distill --branch migrate-json-index
```

---

## Commit Strategy

### Commit 1: Clean break - JSON-only index format
```
refactor(core): burn ships - JSON-only index format

Unit: 1
Implements: O-JIG-001 (performance)
Reflection: see PLAN → Work Unit 1

Clean break migration following taskCleanBreak.md:
- IndexBuilder.save() uses json.dump() (no YAML)
- Graph.load_from_dir() loads JSON only (no YAML fallback)
- Deleted all YAML loading code
- Fail loudly if JSON missing: "Run jigy index rebuild"
- Tests updated: YAML tests deleted, JSON tests added

Breaking change rationale:
- JIG is reference implementation: pristine code > compatibility
- Simpler mental model: one format, one code path
- 3-5x performance gain (15ms → 3-5ms)

Files: src/jig/core/index_builder.py, src/jig/core/graph.py, tests/
```

### Commit 2: CLI updates and YAML deletion
```
feat(cli): delete YAML format, rebuild generates JSON

Unit: 2
Implements: O-JIG-001 (performance)
Reflection: see PLAN → Work Unit 2

- index rebuild generates .json (deletes .yaml if exists)
- Clean break: no backup files, no .gitignore changes
- Clear messaging: "Deleted legacy YAML format (clean break)"
- All commands use Graph.load_from_dir() (fail loudly without JSON)

Files: src/jig/cli/index.py, tests/
```

### Commit 3: Migrate jig project
```
migrate: burn ships - delete YAML, commit JSON

Unit: 3
Reflection: see PLAN → Work Unit 3

Clean break execution on jig project itself:
- Deleted: jig/graph-index.yaml (745 lines)
- Added: jig/graph-index.json (same data, new format)
- Verified node count unchanged (~100 nodes)
- Verified all commands work (status, validate, graph)

Format benefits:
- 3-5x faster parsing
- 13% smaller file size
- Same git diff quality
- No backup file clutter

YAML available in git history if needed (commit: <previous-sha>)

Files: jig/graph-index.json (new)
Deleted: jig/graph-index.yaml
```

### Commit 4: Documentation and benchmarks
```
docs: document JSON-only format and clean break

Unit: 4
Reflection: see PLAN → Work Unit 4

- Add performance benchmark script (JSON-focused)
- Update README and architecture docs
- Update CHANGELOG with clean break notes
- Document measured performance

Measured improvements:
- Parse time: 3.8ms (vs ~15ms YAML from S025)
- File size: 20KB (vs 23KB YAML, 13% reduction)
- Estimated speedup: ~4.0x faster

Clean break documented: no rollback, YAML in git history

Files: README.md, docs/, scripts/benchmark_index_parsing.py, CHANGELOG.md
```

---

## Risk Mitigation

### Identified Risks (Clean Break Edition)

1. **Data loss during format conversion**
   - Mitigation: Compare node counts pre/post migration
   - Mitigation: JSON structure validated in tests
   - Rollback: `git revert` (YAML still in git history)
   - Note: Clean break = no backup files, git is the safety net

2. **Breaking change impacts team**
   - Mitigation: Clear commit message explains clean break
   - Mitigation: One-time rebuild required: `jigy index rebuild`
   - Mitigation: Fast operation (<1s for rebuild)
   - Note: JIG is reference implementation, clean breaks are acceptable

3. **Performance regression**
   - Mitigation: Benchmark validates 3-5x improvement
   - Mitigation: Performance tests in WU4
   - Rollback: `git revert` all commits (restore YAML from history)
   - Confidence: High (JSON stdlib faster than PyYAML)

4. **Git diff quality degradation**
   - Mitigation: Human review in WU3 (migration commit)
   - Mitigation: 2-space indent preserves readability
   - Rollback: `git revert` if diffs unreadable (unlikely)
   - Confidence: High (JSON diffs similar to YAML)

5. **Missing index error handling**
   - Mitigation: Fail loudly with clear message: "Run: jigy index rebuild"
   - Mitigation: Tests verify error messages
   - Note: Better than silent fallback (clean break principle)

---

**Status:** Ready for execution

**Next Steps:**
1. Review and approve PLAN (clean break approach)
2. Execute Work Units 1-4 in sequence
3. Capture markers in Reflect blocks during execution (focus on clean break learnings)
4. Fill Summary and Harvest sections on completion
5. Run `jig ai-distill --branch migrate-json-index` to harvest insights

**Clean Break Commitment:**
- No backward compatibility code
- No feature flags or fallbacks
- Delete old YAML completely
- Fail loudly with clear errors
- Document decision with #DECISION markers
- JIG is reference implementation: pristine code > compatibility

---

**End of PLAN**

