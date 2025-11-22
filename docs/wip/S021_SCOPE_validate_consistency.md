# S021 SCOPE: Fix Validation and Command Consistency

**Created:** 2025-11-21
**Status:** Draft
**Priority:** High (blocking validation workflow)
**Estimated Effort:** 3-5 days

---

## Problem Statement

The three core JIG commands (`jigy index rebuild`, `jigy validate`, `jigy status`) report inconsistent data about the Intent Graph, causing user confusion and breaking the validation workflow. The primary issue is that `jigy validate` generates 159 false errors for all C (Code) and T (Test) nodes because it doesn't understand annotation-based nodes.

### Current Behavior (Broken)

| Metric | `index rebuild` | `validate` | `status` |
|--------|----------------|------------|----------|
| **Total Nodes** | 211 | 56 (O/S/X only) | 215 (all types) |
| **Validation** | ✅ Pass | ❌ 159 false errors | ⚠ 16 orphans |
| **Edges** | ~422 | Not shown | 183 |
| **Subsystems** | Not shown | Not shown | 0 |

### Example Error Output

```bash
$ jigy validate
❌ 159 errors

Errors found:
  ✗ Graph index references non-existent node: C-CLI-003
  ✗ Graph index references non-existent node: T-JIGY-012
  ✗ Graph index references non-existent node: C-AUTH-001
  # ... 156 more false errors for all C/T nodes
```

**These nodes DO exist** - they're just in `src/` and `tests/` as `@jig` annotations, not markdown files.

---

## Root Cause Analysis

### Issue 1: Validator Only Scans Markdown Files

**Location:** `src/jig/core/validator.py:130-186`

**Problem:**
The `validate_graph()` function uses a different code path than `status` and manually scans only markdown directories:

```python
# Current (BROKEN) logic
for node_dir in ["outcomes", "specifications", "constraints"]:
    for node_file in node_dir.glob("*.md"):
        node = parse_ostc_node(node_file)
        node_ids[node.id] = node_file  # Only O/S/X nodes

# Then validates against graph-index.yaml (contains ALL nodes)
indexed_ids = {n["id"] for n in graph_data["nodes"]}  # O/S/X/C/T

for indexed_id in indexed_ids:
    if indexed_id not in node_ids:  # C/T missing!
        errors.append(f"Graph index references non-existent node: {indexed_id}")
```

**Why this is wrong:**
- `validate` scans markdown files → finds 56 nodes (O/S/X)
- `graph-index.yaml` contains 215 nodes (O/S/X/C/T)
- 215 - 56 = 159 "missing" nodes (all the C/T nodes)

**Correct approach:**
Use `Graph.load_from_dir()` like `status` does, which:
1. Loads markdown files (O/S/X)
2. Loads graph-index.yaml (C/T nodes)
3. Gets complete node set (215 nodes)

### Issue 2: Index Rebuild Doesn't Export Subsystems

**Location:** `src/jig/cli/index.py` (index rebuild command)

**Problem:**
The `jigy index rebuild` command writes nodes and edges to `graph-index.yaml` but doesn't write a `subsystems:` section.

**Current output:**
```yaml
version: '1.0'
nodes:
  - id: C-AUTH-001
    subsystem: auth  # ← subsystem metadata on node
    ...
# Missing: subsystems section
```

**Expected output:**
```yaml
version: '1.0'
nodes:
  - id: C-AUTH-001
    subsystem: auth
    ...
subsystems:  # ← MISSING
  auth:
    nodes: [C-AUTH-001, C-AUTH-002]
  core:
    nodes: [C-GRAPH-001, C-NESTED-001, ...]
```

**Impact:**
- `status` loads graph and reports "0 subsystems"
- Subsystem-based commands fail silently
- Metrics can't be calculated by subsystem

### Issue 3: Edge Count Discrepancy

**Problem:**
- `index rebuild` reports "~422 edges"
- `status` reports "183 edges"
- Unclear if this is duplicate counting or data loss

**Investigation needed:**
- Are edges being double-counted during annotation scanning?
- Are edges being deduplicated on write?
- Is the "~422" number accurate?

### Issue 4: Node Count Mismatch

**Problem:**
- `index rebuild` says: 211 nodes (14 O, 38 S, 37 C, 122 T)
- `status` says: 215 nodes (16 O, 39 S, 1 X, 37 C, 122 T)
- Missing: 2 outcomes, 1 spec, 1 constraint

**Possible causes:**
- Index rebuild not scanning all markdown files?
- Parsing errors silently swallowed?
- Incorrect counting logic?

---

## Proposed Changes

### Change 1: Refactor Validator to Use Unified Graph Loading

**File:** `src/jig/core/validator.py`
**Function:** `validate_graph(intent_dir: Path) -> ValidationResult`

**Current logic:**
```python
# Manual scanning (WRONG)
for node_dir in ["outcomes", "specifications", "constraints"]:
    for node_file in node_dir.glob("*.md"):
        node = parse_ostc_node(node_file)
        node_ids[node.id] = node_file
```

**New logic:**
```python
# Use unified graph loading (CORRECT)
from jig.core.graph import Graph

graph = Graph.load_from_dir(intent_dir)
all_node_ids = set(graph.nodes.keys())  # All 215 nodes

# Validate that nodes are parseable and well-formed
errors = []
warnings = []

# Validate markdown nodes (O/S/X)
for node_dir in ["outcomes", "specifications", "constraints"]:
    for node_file in (intent_dir / node_dir).glob("*.md"):
        try:
            node = parse_ostc_node(node_file)
            result = validate_node(node)
            errors.extend(result.errors)
            warnings.extend(result.warnings)
        except Exception as e:
            errors.append(f"Failed to parse {node_file}: {e}")

# C/T nodes are validated indirectly (they're in graph-index.yaml)
# If they loaded successfully, they're valid

# Check for duplicates (across all node types)
node_id_counts = {}
for node_id in all_node_ids:
    node_id_counts[node_id] = node_id_counts.get(node_id, 0) + 1

for node_id, count in node_id_counts.items():
    if count > 1:
        errors.append(f"Duplicate node ID: {node_id} (found {count} times)")

return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
```

**Benefits:**
- Uses same loading logic as `status` (consistency)
- Understands C/T nodes from graph-index.yaml
- No false errors
- Validates that graph loading succeeds (if load fails, graph is broken)

### Change 2: Export Subsystems in Index Rebuild

**File:** `src/jig/cli/index.py`
**Function:** `rebuild()` command

**Add logic to:**
1. Group nodes by `subsystem` metadata field
2. Build subsystem hierarchy from dot-notation paths (e.g., `crdt.ser`)
3. Write `subsystems:` section to graph-index.yaml

**Implementation:**
```python
def build_subsystems_from_nodes(nodes: list[dict]) -> dict:
    """Build subsystem hierarchy from node metadata.

    Args:
        nodes: List of node dicts with 'subsystem' field

    Returns:
        Subsystems dict for graph-index.yaml
    """
    subsystems = {}

    for node in nodes:
        subsystem_path = node.get("subsystem")
        if not subsystem_path:
            continue

        # Handle nested paths (e.g., "crdt.ser")
        if "." in subsystem_path:
            parts = subsystem_path.split(".")
            parent = parts[0]
            child = parts[1]

            if parent not in subsystems:
                subsystems[parent] = {"subsystems": {}}
            if child not in subsystems[parent]["subsystems"]:
                subsystems[parent]["subsystems"][child] = {"nodes": []}

            subsystems[parent]["subsystems"][child]["nodes"].append(node["id"])
        else:
            # Top-level subsystem
            if subsystem_path not in subsystems:
                subsystems[subsystem_path] = {"nodes": []}

            subsystems[subsystem_path]["nodes"].append(node["id"])

    return subsystems

# In rebuild() command:
subsystems_data = build_subsystems_from_nodes(all_nodes)

graph_index = {
    "version": "1.0",
    "generated": datetime.now(timezone.utc).isoformat(),
    "nodes": all_nodes,
    "subsystems": subsystems_data,  # ← ADD THIS
}
```

**Output:**
```yaml
subsystems:
  core:
    nodes: [C-GRAPH-001, C-NESTED-001, T-STATUS-001, ...]
  cli:
    nodes: [C-CLI-001, C-CLI-002, C-CLI-010, ...]
  crdt:
    subsystems:
      ser:
        nodes: [C-SER-001, C-SER-002]
      merge:
        nodes: [C-MERGE-001]
```

### Change 3: Investigate and Fix Edge Count Discrepancy

**Tasks:**
1. Add debug logging to index rebuild to show edge deduplication
2. Verify edges are being written correctly to graph-index.yaml
3. Verify edges are being loaded correctly by Graph.load_from_dir()
4. Add test to ensure edge counts match across commands

**Hypothesis:**
The "~422 edges" is likely counting edges before deduplication. Many relationships appear multiple times:
- In frontmatter of O/S nodes
- In `@jig` annotations
- In graph-index.yaml edges section

**Fix:**
Deduplicate edges and report accurate count:
```python
# In index rebuild
unique_edges = {(e["from"], e["to"], e["type"]) for e in all_edges}
click.echo(f"Total edges: {len(unique_edges)}")
```

### Change 4: Fix Node Count Reporting

**Tasks:**
1. Add verbose logging to index rebuild showing counts per type
2. Verify all markdown files are being scanned
3. Add test with known node counts

**Expected output:**
```bash
$ jigy index rebuild

Scanning sources:
  ✓ jig/outcomes/*.md (16 nodes)  # ← Show actual counts
  ✓ jig/specifications/*.md (39 nodes)
  ✓ jig/constraints/*.md (1 node)
  ✓ src/ for @jig annotations (37 code nodes)
  ✓ test/ for @jig annotations (122 test nodes)

Total nodes: 215 (16 O, 39 S, 1 X, 37 C, 122 T)
```

---

## Out of Scope

The following are **NOT** included in this scope:

1. **Edge type validation** - Checking that `implements:` edges go from S→O, etc. (separate feature)
2. **Subsystem constraint validation** - Checking coupling ratios, forbidden dependencies (separate feature)
3. **Dead node detection** - Finding nodes that should be deleted (separate feature)
4. **Performance optimization** - Making validation faster (not broken, just slow)
5. **Graph visualization** - Rendering subsystem hierarchies visually (separate feature)

---

## Success Criteria

### Functional Requirements

**MUST:**
1. `jigy validate` reports 0 errors on a valid graph with C/T nodes
2. `jigy validate`, `jigy status`, and `jigy index rebuild` report consistent node counts
3. `jigy status` shows correct subsystem count (not 0)
4. All three commands agree on edge count

**SHOULD:**
1. Validation errors are clear and actionable
2. Commands complete in <2 seconds for 200+ nodes
3. Subsystem hierarchy (nested) is preserved in graph-index.yaml

### Test Coverage

**Unit tests:**
- `test_validate_graph_with_ct_nodes()` - Validate graph with all node types
- `test_build_subsystems_from_nodes()` - Build subsystem hierarchy
- `test_edge_deduplication()` - Verify edges aren't double-counted

**Integration tests:**
- `test_command_consistency()` - Run all 3 commands, verify consistent output
- `test_nested_subsystems_export()` - Verify nested subsystems in graph-index.yaml

### Regression Prevention

**Before:**
```bash
$ jigy validate
❌ 159 errors
```

**After:**
```bash
$ jigy validate
✓ All 215 nodes valid
✓ 183 edges validated
✓ 7 subsystems verified
```

---

## Implementation Plan

### Phase 1: Fix Validator (Blocking)

**Priority:** P0 (breaks validation workflow)
**Effort:** 1 day

**Tasks:**
- [ ] Refactor `validate_graph()` to use `Graph.load_from_dir()`
- [ ] Update tests to include C/T nodes
- [ ] Verify 0 false errors on current codebase
- [ ] Update error messages to be clearer

**Deliverable:** `jigy validate` passes on current codebase

### Phase 2: Export Subsystems

**Priority:** P1 (needed for metrics)
**Effort:** 2 days

**Tasks:**
- [ ] Implement `build_subsystems_from_nodes()`
- [ ] Handle nested subsystem paths (dot notation)
- [ ] Write subsystems section to graph-index.yaml
- [ ] Update `Graph.load_from_dir()` to verify subsystems load correctly
- [ ] Add tests for nested subsystems

**Deliverable:** `jigy status` shows correct subsystem count

### Phase 3: Fix Edge and Node Counting

**Priority:** P2 (nice to have)
**Effort:** 1 day

**Tasks:**
- [ ] Add debug logging to index rebuild
- [ ] Investigate edge count discrepancy
- [ ] Fix node count reporting
- [ ] Add integration test verifying counts match

**Deliverable:** All three commands report same counts

### Phase 4: Integration Testing

**Priority:** P1
**Effort:** 1 day

**Tasks:**
- [ ] Add `test_command_consistency()` integration test
- [ ] Run all three commands in CI
- [ ] Verify output matches expected format
- [ ] Update documentation with consistent examples

**Deliverable:** CI catches consistency regressions

---

## Testing Strategy

### Manual Testing Checklist

```bash
# 1. Clean state
rm jig/graph-index.yaml

# 2. Rebuild index
jigy index rebuild
# Expected: ✅ Pass, subsystems written

# 3. Validate
jigy validate
# Expected: ✅ 0 errors

# 4. Check status
jigy status
# Expected: 215 nodes, 183 edges, 7 subsystems

# 5. Verify counts match
# All three commands should agree on node/edge counts
```

### Automated Tests

**File:** `tests/integration/test_command_consistency.py`

```python
def test_validate_status_index_consistency(tmp_path):
    """Verify validate, status, and index report consistent data."""
    # Setup: Create test graph with O/S/X/C/T nodes
    create_test_graph(tmp_path)

    # Run index rebuild
    result = runner.invoke(cli, ["index", "rebuild"])
    assert result.exit_code == 0

    # Parse output for counts
    rebuild_counts = parse_node_counts(result.output)

    # Run validate
    result = runner.invoke(cli, ["validate"])
    assert result.exit_code == 0  # No errors
    assert "Graph index references non-existent node" not in result.output

    # Run status
    result = runner.invoke(cli, ["status"])
    status_counts = parse_node_counts(result.output)

    # Verify consistency
    assert rebuild_counts == status_counts
    assert status_counts["subsystems"] > 0
```

---

## Dependencies

**Code files to modify:**
- `src/jig/core/validator.py` (validate_graph function)
- `src/jig/cli/index.py` (rebuild command)
- `tests/integration/test_command_consistency.py` (new file)

**Related specifications:**
- S-JIGY-002: Graph loading and indexing
- S-JIGY-004: Edge validation
- S-CLI-008: Validate command

**Blocked by:** None
**Blocking:** WU11+ (any work requiring reliable validation)

---

## Risks and Mitigation

### Risk 1: Breaking Changes to Graph Structure

**Risk:** Changing graph-index.yaml format might break existing tools

**Mitigation:**
- Add `subsystems:` section without removing/changing existing fields
- Maintain backward compatibility (missing subsystems = empty dict)
- Version graph-index.yaml format (`version: "1.0"` → `"1.1"`)

### Risk 2: Performance Regression

**Risk:** Loading full graph in validator might be slower than scanning files

**Mitigation:**
- Benchmark before/after
- Target: <2 seconds for 1000 nodes
- Graph loading is already optimized (used by status)

### Risk 3: Test Fragility

**Risk:** Integration tests might be flaky if they depend on exact counts

**Mitigation:**
- Use controlled test fixtures with known counts
- Don't test against production jig/ directory
- Mock or use temporary directories

---

## Open Questions

1. **Edge deduplication:** Should we deduplicate edges from multiple sources (frontmatter + annotations + edges section)?
   - **Proposed answer:** Yes, deduplicate by (from, to, type) tuple

2. **Subsystem inference:** If a node has `subsystem: "crdt.ser"` but we've never seen "crdt", should we create it?
   - **Proposed answer:** Yes, auto-create parent subsystems

3. **Validation strictness:** Should `validate` fail if subsystems section is missing?
   - **Proposed answer:** Warning, not error (backward compatibility)

4. **Node count discrepancy:** Are the 4 missing nodes (2 O, 1 S, 1 X) real or a counting bug?
   - **Action:** Investigate during implementation

---

## References

- **Analysis:** `/tmp/consistency_analysis.md` (generated 2025-11-21)
- **JIG Concept:** `docs/jig-concept/JIG-Concept-v6.1.md`
- **Current implementation:**
  - `src/jig/core/validator.py:110-188`
  - `src/jig/core/graph.py:121-258`
  - `src/jig/cli/index.py`

---

## Sign-off

**Author:** Claude (via user request)
**Reviewer:** TBD
**Approved:** TBD
**Implementation Start:** TBD
