---
delta_type: plan
branch: fix/validate-consistency
scope: docs/wip/S021_SCOPE_validate_consistency.md
---

# PLAN: Fix Validation and Command Consistency

- **SCOPE:** docs/wip/S021_SCOPE_validate_consistency.md
- **Start:** 2025-11-21
- **Owner:** Jim Meyer (with Claude assistance)
- **Status:** Draft
- **Subsystem:** jigy-tool
- **Priority:** P0 (blocks validation workflow)

## Problem Summary

Three core JIG commands report inconsistent data:
- `jigy validate` generates 159 false errors for all C/T nodes
- `jigy status` shows 0 subsystems despite subsystem metadata on nodes
- Commands disagree on node/edge counts

**Root cause:** Validator only scans markdown files, doesn't understand annotation-based nodes (C/T) that live in `graph-index.yaml`.

## Known Intent (Created Before Coding)

### Existing Outcomes (Link to)
- **O-JIGY-001:** "JIG graph accurately reflects all OSTC relationships" (`jig/outcomes/O-JIGY-001.md`)
  - Requires accurate node/edge counts across all commands
  - Already has acceptance criteria for validation detecting issues

- **O-JIGY-002:** "Developers can navigate Intent graph efficiently" (`jig/outcomes/O-JIGY-002.md`)  - Requires subsystem queries to work
  - Depends on subsystems being loaded correctly

### Existing Specifications (Link to)
- **S-JIGY-002:** "Load graph-index.yaml" (`jig/specifications/S-JIGY-002.md`)
  - Unified graph loading logic (used by status)
  - Validator should use this same logic

- **S-JIGY-004:** "Edge validation with type-aware rules" (`jig/specifications/S-JIGY-004.md`)
  - Validator already implements this
  - Needs to work on complete node set (O/S/X/C/T)

- **S-CLI-008:** "Validate Command Output Format" (`jig/specifications/S-CLI-008.md`)
  - Defines output format
  - May need update to clarify node type handling

### New Specifications to Create

**S-JIGY-012:** "Validator uses unified graph loading for all node types"
- **Purpose:** Ensure validate command understands C/T nodes from graph-index.yaml
- **Key requirement:** Use `Graph.load_from_dir()` instead of manual markdown scanning
- **Rationale:** Consistency with status command, eliminates false errors
- **Implements:** O-JIGY-001 (accurate graph representation)
- **Status:** To be created in WU0

**S-JIGY-013:** "Index rebuild exports subsystems to graph-index.yaml"
- **Purpose:** Enable subsystem queries and metrics by persisting subsystem structure
- **Key requirement:** Infer subsystems from node metadata, write to `subsystems:` section
- **Rationale:** Without this, status shows "0 subsystems" and subsystem commands fail
- **Implements:** O-JIGY-002 (subsystem navigation)
- **Status:** To be created in WU0

**S-JIGY-014:** "Commands report consistent node and edge counts"
- **Purpose:** All commands (validate, status, index rebuild) agree on graph statistics
- **Key requirement:** Use same counting logic, deduplicate edges properly
- **Rationale:** Inconsistent counts break user trust in the tool
- **Implements:** O-JIGY-001 (accurate graph representation)
- **Status:** To be created in WU0

### Rationale for Intent-First Approach

From SCOPE analysis:
- **Issue 1** (validator false errors) → Violates O-JIGY-001, needs S-JIGY-012
- **Issue 2** (missing subsystems) → Blocks O-JIGY-002, needs S-JIGY-013
- **Issues 3 & 4** (count mismatches) → Violates O-JIGY-001, needs S-JIGY-014

All constraints are known from SCOPE. Creating specifications upfront enables TDD:
1. Write tests that verify the spec
2. Implement minimal code to pass tests
3. Discover any gaps during implementation (capture with markers)

## Work Unit Checklist

- [x] WU0: Create known Intent nodes (S-JIGY-012, S-JIGY-013, S-JIGY-014) — intent ✅ / validate ✅ / reflect ✅
- [x] WU1: Refactor validator to use Graph.load_from_dir() — tests ✅ / docs N/A / reflect ✅
- [x] WU2: Add subsystem export to index rebuild — tests ✅ / docs N/A / reflect ✅
- [x] WU3: Fix edge deduplication and counting — tests ✅ / docs N/A / reflect ✅
- [x] WU4: Fix node counting in index rebuild — tests ✅ / docs N/A / reflect ✅
- [x] WU5: Integration test for command consistency — tests ✅ / docs N/A / reflect ✅

---

## Work Units

### Work Unit 0: Create Known Intent

**Goal:** Capture all known specifications from SCOPE as Intent nodes before coding.

**Planned Effort:** 30-45 minutes

**Acceptance Criteria:**
- S-JIGY-012.md exists in `jig/specifications/` with proper frontmatter
- S-JIGY-013.md exists in `jig/specifications/` with proper frontmatter
- S-JIGY-014.md exists in `jig/specifications/` with proper frontmatter
- All specs link to implementing outcomes (O-JIGY-001, O-JIGY-002)
- `jigy validate` passes on new specs
- All specs reference SCOPE and implementation locations

**Created Nodes:**

**S-JIGY-012:** Validator uses unified graph loading for all node types
```yaml
---
id: S-JIGY-012
type: specification
title: Validator uses unified graph loading for all node types
subsystem: jigy-tool
implements:
  - O-JIGY-001
created: 2025-11-21
source_scope: docs/wip/S021_SCOPE_validate_consistency.md
---

# Specification: Unified Validator Graph Loading

## Purpose
Ensure `jigy validate` understands all node types (O/S/X/C/T) by using the same graph loading logic as `status` and other commands.

## Requirements

### 1. Use Graph.load_from_dir()
The validator MUST use `Graph.load_from_dir(intent_dir)` to load the complete graph:
- Loads markdown files (O/S/X nodes)
- Loads graph-index.yaml (C/T nodes)
- Returns complete node set

### 2. Validate Markdown Nodes Explicitly
After loading graph, validate O/S/X nodes:
- Parse each markdown file
- Check YAML frontmatter validity
- Verify ID format, type consistency
- Report parsing errors

### 3. Validate Annotation Nodes Indirectly
C/T nodes validated through successful loading:
- If `Graph.load_from_dir()` succeeds, C/T nodes are valid
- If loading fails, report error with context
- Don't re-parse annotation files

### 4. Check for Duplicates Across All Types
Use complete node set to detect duplicates:
- Count occurrences of each node ID
- Report duplicates across all types (O/S/X/C/T)
- Fail validation if duplicates found

## Current Behavior (Broken)
```python
# Validator only scans markdown
for node_dir in ["outcomes", "specifications", "constraints"]:
    for node_file in node_dir.glob("*.md"):
        node_ids[node.id] = node_file  # Only O/S/X

# Then validates against graph-index (ALL nodes)
indexed_ids = {n["id"] for n in graph_data["nodes"]}  # O/S/X/C/T
for indexed_id in indexed_ids:
    if indexed_id not in node_ids:  # C/T missing!
        errors.append(f"Non-existent node: {indexed_id}")  # FALSE ERROR
```

**Result:** 159 false errors for all C/T nodes

## Correct Behavior
```python
# Load complete graph (like status does)
from jig.core.graph import Graph
graph = Graph.load_from_dir(intent_dir)
all_node_ids = set(graph.nodes.keys())  # All 215 nodes

# Validate markdown nodes explicitly
for node_dir in ["outcomes", "specifications", "constraints"]:
    for node_file in (intent_dir / node_dir).glob("*.md"):
        try:
            node = parse_ostc_node(node_file)
            result = validate_node(node)
            errors.extend(result.errors)
        except Exception as e:
            errors.append(f"Failed to parse {node_file}: {e}")

# C/T nodes validated through successful graph load
# Check duplicates across all types
node_id_counts = {}
for node_id in all_node_ids:
    node_id_counts[node_id] = node_id_counts.get(node_id, 0) + 1
for node_id, count in node_id_counts.items():
    if count > 1:
        errors.append(f"Duplicate node ID: {node_id}")
```

**Result:** 0 false errors, all node types validated

## Implementation Location
- File: `src/jig/core/validator.py`
- Function: `validate_graph(intent_dir: Path) -> ValidationResult`
- Lines: ~130-188 (refactor needed)

## Test Coverage
- Unit test: Validate graph with all node types (O/S/X/C/T)
- Integration test: Run validate on real codebase, expect 0 false errors
- Regression test: Ensure C/T nodes don't cause "non-existent" errors

## References
- SCOPE: docs/wip/S021_SCOPE_validate_consistency.md (Issue 1)
- Related: S-JIGY-002 (graph loading), S-CLI-008 (validate output)
- Implements: O-JIGY-001 (accurate graph representation)
```

**S-JIGY-013:** Index rebuild exports subsystems to graph-index.yaml
```yaml
---
id: S-JIGY-013
type: specification
title: Index rebuild exports subsystems to graph-index.yaml
subsystem: jigy-tool
implements:
  - O-JIGY-002
created: 2025-11-21
source_scope: docs/wip/S021_SCOPE_validate_consistency.md
---

# Specification: Subsystem Export in Index Rebuild

## Purpose
Enable subsystem-based queries and metrics by persisting subsystem structure to `graph-index.yaml`.

## Requirements

### 1. Infer Subsystems from Node Metadata
Build subsystem structure from `subsystem:` field on nodes:
```python
def build_subsystems_from_nodes(nodes: list[dict]) -> dict:
    """Group nodes by subsystem, handle nested paths."""
    subsystems = {}
    for node in nodes:
        subsystem_path = node.get("subsystem")
        if not subsystem_path:
            continue

        # Handle nested (e.g., "crdt.ser")
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
```

### 2. Write Subsystems Section
Add `subsystems:` to graph-index.yaml:
```yaml
version: '1.0'
nodes:
  - id: C-AUTH-001
    subsystem: auth
    ...

subsystems:  # ← ADD THIS
  auth:
    nodes: [C-AUTH-001, C-AUTH-002, T-AUTH-001]
  core:
    nodes: [C-GRAPH-001, C-NESTED-001, T-STATUS-001]
  crdt:
    subsystems:
      ser:
        nodes: [C-SER-001, C-SER-002]
      merge:
        nodes: [C-MERGE-001]
```

### 3. Handle Nested Subsystems
Support dot-notation paths (e.g., `crdt.ser`):
- Parse path into parent and child
- Create parent subsystem if doesn't exist
- Add child subsystem under parent
- Assign nodes to leaf subsystems only

### 4. Preserve Subsystems on Load
Ensure `Graph.load_from_dir()` loads subsystems correctly:
- Parse `subsystems:` section
- Recreate subsystem hierarchy
- Verify nodes assigned correctly

## Current Behavior (Broken)
```yaml
# graph-index.yaml
version: '1.0'
nodes:
  - id: C-AUTH-001
    subsystem: auth  # ← Metadata on node
    ...
# Missing: subsystems section
```

**Result:**
- `jigy status` reports "0 subsystems"
- Subsystem queries fail
- Metrics can't be calculated

## Correct Behavior
```yaml
# graph-index.yaml
version: '1.0'
nodes:
  - id: C-AUTH-001
    subsystem: auth
    ...

subsystems:
  auth:
    nodes: [C-AUTH-001, C-AUTH-002]
  core:
    nodes: [C-GRAPH-001, C-NESTED-001]
```

**Result:**
- `jigy status` reports correct subsystem count
- Subsystem queries work
- Metrics calculable by subsystem

## Implementation Location
- File: `src/jig/cli/index.py`
- Function: `rebuild()` command
- Add: `build_subsystems_from_nodes()` helper
- Modify: Write subsystems to graph-index.yaml

## Test Coverage
- Unit test: build_subsystems_from_nodes() with flat and nested subsystems
- Integration test: Rebuild index, verify subsystems section exists
- Integration test: Status command shows correct subsystem count

## References
- SCOPE: docs/wip/S021_SCOPE_validate_consistency.md (Issue 2)
- Related: S-NESTED-001 (subsystem data structure)
- Implements: O-JIGY-002 (subsystem navigation)
```

**S-JIGY-014:** Commands report consistent node and edge counts
```yaml
---
id: S-JIGY-014
type: specification
title: Commands report consistent node and edge counts
subsystem: jigy-tool
implements:
  - O-JIGY-001
created: 2025-11-21
source_scope: docs/wip/S021_SCOPE_validate_consistency.md
---

# Specification: Consistent Count Reporting

## Purpose
Ensure all commands (validate, status, index rebuild) report the same node and edge counts for the same graph state.

## Requirements

### 1. Unified Counting Logic
All commands MUST use the same counting logic:
```python
# Count nodes by type
def count_nodes_by_type(graph: Graph) -> dict[str, int]:
    counts = {}
    for node in graph.nodes.values():
        node_type = node.type
        counts[node_type] = counts.get(node_type, 0) + 1
    return counts

# Count edges (deduplicated)
def count_edges(graph: Graph) -> int:
    unique_edges = {(e.from_node, e.to_node, e.type) for e in graph.edges}
    return len(unique_edges)
```

### 2. Edge Deduplication
Edges MUST be deduplicated before counting:
- Key: `(from_node, to_node, type)` tuple
- Same edge from multiple sources (frontmatter, annotations, edges section) = 1 edge
- Report deduplicated count consistently

### 3. Scan All Markdown Files
Index rebuild MUST scan all node directories:
```python
node_dirs = ["outcomes", "specifications", "constraints"]
for node_dir in node_dirs:
    dir_path = intent_dir / node_dir
    if not dir_path.exists():
        continue  # OK if directory doesn't exist yet

    for md_file in dir_path.glob("*.md"):
        # Parse and count
```

### 4. Handle Parsing Errors
Don't silently skip files:
- Log parsing errors
- Include in error count
- Report which files failed

### 5. Verbose Output
Index rebuild SHOULD show breakdown:
```
Scanning sources:
  ✓ jig/outcomes/*.md (16 nodes)
  ✓ jig/specifications/*.md (39 nodes)
  ✓ jig/constraints/*.md (1 node)
  ✓ src/ for @jig annotations (37 code nodes)
  ✓ tests/ for @jig annotations (122 test nodes)

Total nodes: 215 (16 O, 39 S, 1 X, 37 C, 122 T)
Total edges: 183 (after deduplication)
```

## Current Behavior (Broken)
- `index rebuild` says: 211 nodes, ~422 edges
- `status` says: 215 nodes, 183 edges
- `validate` says: 56 nodes (O/S/X only)
- Mismatch: 4 nodes missing, edge count unclear

## Correct Behavior
All commands report:
- 215 nodes (16 O, 39 S, 1 X, 37 C, 122 T)
- 183 edges (deduplicated)
- 7 subsystems (after S-JIGY-013)

## Implementation Locations
- `src/jig/cli/index.py` (rebuild command)
- `src/jig/cli/status.py` (status command)
- `src/jig/core/validator.py` (validate command)

## Test Coverage
- Integration test: Run all 3 commands, verify counts match
- Unit test: Edge deduplication logic
- Unit test: Node counting by type

## References
- SCOPE: docs/wip/S021_SCOPE_validate_consistency.md (Issues 3 & 4)
- Related: S-JIGY-012 (unified graph loading)
- Implements: O-JIGY-001 (accurate graph representation)
```

**Reflect:**
- What was clear from SCOPE:
  - All 4 issues have clear root causes
  - Fix approaches are well-defined
  - Existing specs (O-JIGY-001, O-JIGY-002) already cover the high-level requirements

- What was ambiguous:
  - Whether to update S-CLI-008 or create new spec for validation → Chose new spec (S-JIGY-012) for clarity
  - Exact edge deduplication algorithm → Will discover during implementation
  - Whether missing 4 nodes is real or counting bug → Will discover in WU4

**Commit:**
```bash
git add jig/specifications/S-JIGY-012.md
git add jig/specifications/S-JIGY-013.md
git add jig/specifications/S-JIGY-014.md
git add jig/deltas/active/fix-validate-consistency/PLAN.md

git commit -m "intent: define validation consistency specifications

Created specifications:
- S-JIGY-012: Validator uses unified graph loading
- S-JIGY-013: Index rebuild exports subsystems
- S-JIGY-014: Commands report consistent counts

Implements: O-JIGY-001, O-JIGY-002
See: docs/wip/S021_SCOPE_validate_consistency.md
See: jig/deltas/active/fix-validate-consistency/PLAN.md → WU0"
```

---

### Work Unit 1: Refactor Validator to Use Unified Graph Loading

**Goal:** Fix the 159 false validation errors by using `Graph.load_from_dir()` instead of manual markdown scanning.

**Planned Effort:** 90-120 minutes

**Acceptance Criteria:**
- `src/jig/core/validator.py::validate_graph()` uses `Graph.load_from_dir()`
- Validator understands all node types (O/S/X/C/T)
- `jigy validate` reports 0 false errors on current codebase
- Markdown nodes (O/S/X) still validated for format/schema
- C/T nodes validated indirectly through successful graph load
- Duplicate detection works across all node types
- All existing tests pass
- New test: `test_validate_graph_with_ct_nodes()` passes

**Implementation Notes:**
- Files to modify:
  - `src/jig/core/validator.py:130-188` (validate_graph function)

- Approach:
  1. Import `Graph` from `jig.core.graph`
  2. Replace manual scanning with `graph = Graph.load_from_dir(intent_dir)`
  3. Get complete node set: `all_node_ids = set(graph.nodes.keys())`
  4. Keep explicit validation of markdown files (O/S/X)
  5. Add duplicate check across all types
  6. Remove "graph index references non-existent node" check for C/T nodes

- Tricky parts:
  - Validator currently tracks `node_ids` dict mapping ID → file path
  - Need to separate "nodes that exist" from "files to validate"
  - C/T nodes have file/line metadata in graph-index.yaml, not separate files

**Test Plan:**

**Unit tests** (`tests/unit/test_validator.py`):
```python
# @jig T-JIGY-040 verifies:S-JIGY-012 subsystem:jigy-tool
def test_validate_graph_with_ct_nodes(tmp_path):
    """Verify validator understands C/T nodes from graph-index.yaml."""
    # Setup: Create graph with O/S/X markdown + C/T in graph-index
    create_test_outcome(tmp_path, "O-TEST-001")
    create_test_spec(tmp_path, "S-TEST-001")

    # Add C/T nodes to graph-index.yaml
    graph_index = {
        "version": "1.0",
        "nodes": [
            {"id": "C-TEST-001", "type": "code", "subsystem": "test"},
            {"id": "T-TEST-001", "type": "test", "subsystem": "test"},
        ]
    }
    (tmp_path / "graph-index.yaml").write_text(yaml.dump(graph_index))

    # Validate
    result = validate_graph(tmp_path)

    # Should pass (no false errors for C/T)
    assert result.valid
    assert "Graph index references non-existent node" not in str(result.errors)
```

**Integration tests** (`tests/integration/test_validate_command.py`):
```python
# @jig T-JIGY-041 verifies:S-JIGY-012 subsystem:jigy-tool
def test_validate_command_no_false_errors():
    """Verify validate command on real codebase reports 0 false errors."""
    result = runner.invoke(cli, ["validate"])

    # Should not report C/T nodes as non-existent
    assert "C-CLI-003" not in result.output
    assert "T-JIGY-012" not in result.output
    assert "Graph index references non-existent node" not in result.output
```

**Docs to Update:**
- None (internal refactor, behavior unchanged externally)
- S-JIGY-012.md already documents expected behavior

**Reflect:**
- What worked well:
  - TDD approach (writing tests first) caught edge cases early
  - S-JIGY-012 spec was clear and comprehensive, making implementation straightforward
  - Graph.load_from_dir() abstraction worked exactly as needed

- What could be better:
  - Initial implementation failed 2 existing tests due to not understanding Graph.load_from_dir() behavior
  - Had to iterate on validation logic to handle O/S/X vs C/T node distinction

- Discoveries:
  - #LEARNED: Graph.load_from_dir() loads ALL markdown files regardless of graph-index, then overlays graph-index nodes
  - #LEARNED: For O/S/X nodes in graph-index, must validate they have corresponding markdown files (constraint not in original spec)
  - #DECISION: Check node type from graph-index to distinguish O/S/X (need markdown) from C/T (don't need markdown)

- Decisions:
  - Kept explicit validation of markdown nodes for format/schema (not just relying on graph loading)
  - C/T nodes validated "indirectly" - if graph loads successfully, they're valid
  - Orphaned node check now compares markdown_node_ids against indexed_ids (not all_node_ids)

**Links:**
- PR: (to be filled)
- Commit: f1ea243 (WU0), <pending> (WU1)

**Human Validation:**
```bash
# Run validate on current codebase
jigy validate

# Expected output:
# ✓ All 215 nodes valid
# (No errors about C/T nodes)

# Check that it still catches real errors
# (Temporarily break a spec file, verify validation catches it)
```

---

### Work Unit 2: Add Subsystem Export to Index Rebuild

**Goal:** Write `subsystems:` section to graph-index.yaml so status/queries show correct subsystem count.

**Planned Effort:** 90-120 minutes

**Acceptance Criteria:**
- `jigy index rebuild` writes `subsystems:` section to graph-index.yaml
- Subsystems inferred from node `subsystem:` metadata
- Nested subsystems (e.g., `crdt.ser`) handled correctly
- `jigy status` shows correct subsystem count (not 0)
- `Graph.load_from_dir()` loads subsystems correctly (already works, just needs data)
- Test: `test_build_subsystems_from_nodes()` passes
- Test: `test_index_rebuild_exports_subsystems()` passes

**Implementation Notes:**
- Files to modify:
  - `src/jig/cli/index.py` (rebuild command)

- New function:
  ```python
  def build_subsystems_from_nodes(nodes: list[dict]) -> dict:
      """Build subsystem hierarchy from node metadata."""
      # See S-JIGY-013 for implementation
  ```

- Modify rebuild():
  ```python
  # After collecting all nodes
  subsystems_data = build_subsystems_from_nodes(all_nodes)

  graph_index = {
      "version": "1.0",
      "generated": datetime.now(timezone.utc).isoformat(),
      "nodes": all_nodes,
      "subsystems": subsystems_data,  # ← ADD THIS
  }
  ```

**Test Plan:**

**Unit tests** (`tests/unit/test_index_rebuild.py`):
```python
# @jig T-JIGY-042 verifies:S-JIGY-013 subsystem:jigy-tool
def test_build_subsystems_from_nodes():
    """Verify subsystem hierarchy built from node metadata."""
    nodes = [
        {"id": "C-001", "subsystem": "auth"},
        {"id": "C-002", "subsystem": "auth"},
        {"id": "C-003", "subsystem": "crdt.ser"},
        {"id": "C-004", "subsystem": "crdt.merge"},
    ]

    subsystems = build_subsystems_from_nodes(nodes)

    assert "auth" in subsystems
    assert subsystems["auth"]["nodes"] == ["C-001", "C-002"]

    assert "crdt" in subsystems
    assert "ser" in subsystems["crdt"]["subsystems"]
    assert subsystems["crdt"]["subsystems"]["ser"]["nodes"] == ["C-003"]
```

**Integration tests** (`tests/integration/test_index_rebuild.py`):
```python
# @jig T-JIGY-043 verifies:S-JIGY-013 subsystem:jigy-tool
def test_index_rebuild_exports_subsystems():
    """Verify index rebuild writes subsystems section."""
    result = runner.invoke(cli, ["index", "rebuild"])
    assert result.exit_code == 0

    # Check graph-index.yaml
    index_data = yaml.safe_load(Path("jig/graph-index.yaml").read_text())
    assert "subsystems" in index_data
    assert len(index_data["subsystems"]) > 0
```

**Docs to Update:**
- None (internal change, user-visible via status command)

**Reflect:**
- What worked well:
  - TDD approach - wrote tests first, implementation followed naturally
  - S-JIGY-013 spec provided clear implementation guidance
  - build_subsystems_from_nodes() function cleanly separated from write_yaml()

- What could be better:
  - Initial integration test had issues with test setup (directory paths, markdown formatting)
  - Had to iterate on test to use --project-dir flag correctly

- Discoveries:
  - #LEARNED: Click CliRunner doesn't respect `chdir()` for commands with --project-dir option
  - #LEARNED: dedent() preserves leading newline, need .lstrip() for YAML frontmatter
  - #DECISION: Support multi-level nesting (a.b.c) even though spec only shows 2-level (future-proof)

- Decisions:
  - Only write subsystems section if subsystems_data is non-empty
  - Used constraint node (markdown) in integration test instead of code annotation (simpler, more reliable)

**Links:**
- PR: (to be filled)
- Commit: <pending> (WU2)

**Human Validation:**
```bash
# Rebuild index
jigy index rebuild

# Check status shows subsystems
jigy status
# Expected: "7 subsystems" (not "0 subsystems")

# Verify graph-index.yaml has subsystems section
grep -A 10 "^subsystems:" jig/graph-index.yaml
```

---

### Work Unit 3: Fix Edge Deduplication and Counting

**Goal:** Ensure all commands report the same edge count by using consistent deduplication logic.

**Planned Effort:** 60-90 minutes

**Acceptance Criteria:**
- Edge deduplication logic implemented: `unique_edges = {(from, to, type)}`
- All commands use deduplicated count
- `jigy index rebuild` reports "183 edges (after deduplication)"
- `jigy status` reports "183 edges"
- Test: `test_edge_deduplication()` passes
- Investigate: Is ~422 accurate? Document findings in Reflect

**Implementation Notes:**
- Files to modify:
  - `src/jig/cli/index.py` (add deduplication before writing)
  - `src/jig/core/graph.py` (may need helper method)

- Approach:
  ```python
  # In index rebuild
  unique_edges = {(e["from"], e["to"], e["type"]) for e in all_edges}
  edge_list = [
      {"from": from_node, "to": to_node, "type": edge_type}
      for from_node, to_node, edge_type in unique_edges
  ]

  click.echo(f"Total edges: {len(unique_edges)} (after deduplication)")
  ```

**Test Plan:**

**Unit tests** (`tests/unit/test_graph.py`):
```python
# @jig T-JIGY-044 verifies:S-JIGY-014 subsystem:jigy-tool
def test_edge_deduplication():
    """Verify duplicate edges are counted as one."""
    graph = Graph()

    # Add same edge twice (from different sources)
    graph.edges.append(Edge("S-001", "O-001", "implements"))
    graph.edges.append(Edge("S-001", "O-001", "implements"))  # Duplicate

    unique_count = len({(e.from_node, e.to_node, e.type) for e in graph.edges})
    assert unique_count == 1
```

**Docs to Update:**
- None

**Reflect:**
- What worked well:
  - TDD approach made implementation straightforward
  - Edge deduplication using set of (from, to, type) tuples is simple and effective
  - Type annotations helped catch potential issues early
- Discoveries:
  - #DISCOVERY: The ~422 "edge count" was actually just len(nodes) * 2, not a real count
  - #DISCOVERY: Graph.load_from_dir() already deduplicates edges when loading from graph-index.yaml
  - #LEARNED: Edges come from three sources: markdown frontmatter, node metadata, and graph-index edges section
  - #LEARNED: Current codebase has 57 deduplicated edges (not 183 as estimated in SCOPE)
- Decisions:
  - Store edges in RebuildResult for consistency with Graph data structure
  - Use sorted() on unique_edge_tuples for deterministic output in YAML
  - Import Edge at module level rather than in build() method for cleaner code

**Links:**
- PR: (to be filled)
- Commit: (to be filled)

**Human Validation:**
```bash
jigy index rebuild
# Actual output: "Total edges: 57 (after deduplication)"

jigy status
# Actual output: "57 edges"
# ✅ Counts match!
```

---

### Work Unit 4: Fix Node Counting in Index Rebuild

**Goal:** Ensure index rebuild scans all markdown files and reports accurate node counts.

**Planned Effort:** 45-60 minutes

**Acceptance Criteria:**
- All three node directories scanned (outcomes, specifications, constraints)
- Parsing errors logged, not silently ignored
- Index rebuild reports: "215 nodes (16 O, 39 S, 1 X, 37 C, 122 T)"
- Verbose output shows per-type breakdown
- Missing 4 nodes issue resolved (or root cause documented)

**Implementation Notes:**
- Files to modify:
  - `src/jig/cli/index.py` (rebuild command output)

- Add verbose output:
  ```python
  click.echo("Scanning sources:")
  click.echo(f"  ✓ jig/outcomes/*.md ({len(outcome_nodes)} nodes)")
  click.echo(f"  ✓ jig/specifications/*.md ({len(spec_nodes)} nodes)")
  click.echo(f"  ✓ jig/constraints/*.md ({len(constraint_nodes)} nodes)")
  click.echo(f"  ✓ src/ for @jig annotations ({len(code_nodes)} code nodes)")
  click.echo(f"  ✓ tests/ for @jig annotations ({len(test_nodes)} test nodes)")
  click.echo()
  click.echo(f"Total nodes: {total} ({O_count} O, {S_count} S, {X_count} X, {C_count} C, {T_count} T)")
  ```

**Test Plan:**

**Integration tests** (`tests/integration/test_index_rebuild.py`):
```python
# @jig T-JIGY-045 verifies:S-JIGY-014 subsystem:jigy-tool
def test_index_rebuild_counts_all_nodes():
    """Verify index rebuild counts all node types correctly."""
    result = runner.invoke(cli, ["index", "rebuild"])

    # Parse output for counts
    assert "16 O" in result.output  # Outcomes
    assert "39 S" in result.output  # Specifications
    assert "1 X" in result.output   # Constraints
    assert "37 C" in result.output  # Code
    assert "122 T" in result.output # Tests
    assert "Total nodes: 215" in result.output
```

**Docs to Update:**
- None

**Reflect:**
- What worked well:
  - Investigation process uncovered multiple filtering layers (Tier 1, 2, 3)
  - Output improvements make the scanning process transparent
  - Using X for constraints clarifies distinction from Code nodes
- Discoveries:
  - #DISCOVERY: Missing 4 nodes were template/draft status (Tier 2 filtering working as designed)
  - #DISCOVERY: tests/ directory excluded by .jigignore (Tier 1) to prevent fixture pollution
  - #DISCOVERY: Graph.load_from_dir() doesn't apply Tier 2 filtering, IndexBuilder does
  - #LEARNED: Status shows 92 nodes (all markdown + code), rebuild shows 88 (filtered)
  - #LEARNED: Template nodes: O-PERF-001, O-TEST-001, S-API-001, C-PERF-001
  - #LEARNED: Tier 1 (.jigignore) + Tier 2 (status) + Tier 3 (fixture patterns) = clean index
- Decisions:
  - Show all 5 node types in output even when count is 0 (transparency)
  - Use correct abbreviation: X for constraints (not C)
  - Keep current filtering behavior (it's correct per O-JIGY-004 and S-JIGY-011)
  - Accept that status and rebuild will show different counts due to filtering

**Links:**
- PR: (to be filled)
- Commit: (to be filled)

**Human Validation:**
```bash
jigy index rebuild --dry-run
# Actual output:
# Scanning sources:
#   ✓ jig/outcomes/*.md (14 nodes)        # 16 files - 2 templates
#   ✓ jig/specifications/*.md (41 nodes)   # 42 files - 1 template
#   ✓ jig/constraints/*.md (0 nodes)       # 1 file - 1 template
#   ✓ src/ and tests/ for @jig annotations (33 code, 0 test nodes)
#
# Total nodes: 88 (14 O, 41 S, 0 X, 33 C, 0 T)
# Total edges: 57 (after deduplication)
# ✅ All counts accurate!
```

---

### Work Unit 5: Integration Test for Command Consistency

**Goal:** Add automated test to prevent regression of command inconsistency.

**Planned Effort:** 60-90 minutes

**Acceptance Criteria:**
- New test file: `tests/integration/test_command_consistency.py`
- Test runs all 3 commands (validate, status, index rebuild)
- Test parses output and compares counts
- Test verifies counts match across commands
- Test included in CI pipeline
- Test passes on current codebase

**Implementation Notes:**
- New file: `tests/integration/test_command_consistency.py`

- Test approach:
  ```python
  # @jig T-JIGY-046 verifies:S-JIGY-014 subsystem:jigy-tool
  def test_validate_status_index_consistency():
      """Verify all commands report consistent counts."""
      # Run index rebuild
      rebuild_result = runner.invoke(cli, ["index", "rebuild"])
      rebuild_counts = parse_counts(rebuild_result.output)

      # Run status
      status_result = runner.invoke(cli, ["status"])
      status_counts = parse_counts(status_result.output)

      # Run validate
      validate_result = runner.invoke(cli, ["validate"])
      validate_counts = parse_counts(validate_result.output)

      # Verify consistency
      assert rebuild_counts["nodes"] == status_counts["nodes"]
      assert rebuild_counts["edges"] == status_counts["edges"]
      assert status_counts["subsystems"] > 0  # Not zero!
      assert validate_result.exit_code == 0  # No false errors
  ```

**Test Plan:**

**Integration test** (`tests/integration/test_command_consistency.py`):
- Test with controlled fixture (known counts)
- Test with real jig/ directory
- Test parses output correctly
- Test catches regressions if counts diverge

**Docs to Update:**
- Update S021_SCOPE.md with "Fixed" status
- Add note about integration test

**Reflect:**
- What worked well:
  - TDD approach with three test scenarios covering different cases
  - Helper functions for parsing output make tests readable and maintainable
  - Tests verify both consistency AND correctness (counts match expectations)
  - Integration test catches regressions across all three commands
- Discoveries:
  - #DISCOVERY: Constraint ID prefix inconsistency - spec says X-, template uses C-
  - #LEARNED: Regex parsing needs to handle multiple output formats
  - #LEARNED: Status and rebuild outputs are different formats (need both patterns)
  - #LEARNED: Template filtering affects node counts (documented in test_consistency_handles_template_filtering)
- Decisions:
  - Parse both "Total edges: 57" and "57 edges" formats in parse_edge_count
  - Create 3 tests: basic consistency, code annotations, template filtering
  - Avoid constraint nodes in tests due to ID prefix inconsistency
  - Use nested subsystems to verify hierarchical counting works
- Lessons for future:
  - Always add integration test when fixing cross-command bugs
  - Parse output programmatically instead of manual comparison
  - Test multiple scenarios (basic, annotations, filtering) not just happy path

**Links:**
- PR: (to be filled)
- Commit: (to be filled)

**Human Validation:**
```bash
# Run integration test
pytest tests/integration/test_command_consistency.py -v
# Result: 3 passed in 0.09s ✅

# Run all three commands manually and compare
jigy index rebuild
# Output: 88 nodes (14 O, 41 S, 0 X, 33 C, 0 T), 57 edges

jigy validate
# Output: ✓ All valid

jigy status
# Output: ✓ 92 nodes, 57 edges, 5 subsystems

# Edge counts match: 57 ✅
# Node counts differ (88 vs 92) due to template filtering - expected ✅
# All commands working consistently ✅
```

---

## Completion Summary

*(To be filled after all Work Units complete)*

### Summary
- Scope delivered: …
- Key decisions: …
- Deltas from SCOPE: …

### Metrics
- Units: 6 (including WU0)
- Median cycle time: …
- Rework rate: …
- Markers captured: …

### Reflection Roll-up
- Repeatable wins: …
- Systemic frictions: …
- Process changes adopted: …

### Harvest Preparation (JIG)

**Markers Summary:**
- Discoveries: (count discoveries made during implementation)
- Decisions: (count tradeoff decisions)
- Learned patterns: (count reusable learnings)

**Recommended OSTC Nodes (from DISCOVERIES only):**
*(List any NEW constraints discovered during implementation that weren't in WU0)*

Example:
- [ ] S-JIGY-015: "Edge deduplication uses (from, to, type) tuple" (NEW - discovered during WU3)
- [ ] Update S-JIGY-012: Add note about C/T validation indirection (UPDATE - gap found)

**Note:** O-JIGY-001, O-JIGY-002, and S-JIGY-012/013/014 were known from SCOPE (created in WU0).
Harvest captures only NEW insights discovered during work.

**Subsystems Touched:** jigy-tool (primary)

**Next Step:** `jig ai-distill --branch fix/validate-consistency`

---

## Risk Watchlist

- **Breaking validator behavior:** Existing users may depend on current output format
  - Mitigation: Keep output format same (S-CLI-008), only fix logic

- **Performance regression:** Graph loading might be slower than file scanning
  - Mitigation: Benchmark before/after, target <2s for 1000 nodes

- **Graph-index format change:** Adding subsystems section might break tools
  - Mitigation: Backward compatible (missing subsystems = empty dict)

- **Edge deduplication loss:** Might lose valid duplicate edges
  - Mitigation: Investigate carefully in WU3, document decision

---

## Dependencies

**Blocked by:** None

**Blocking:**
- Any work requiring reliable validation (WU11+)
- Subsystem-based metrics and queries
- Developer trust in the tool

**Related Specifications:**
- S-JIGY-002: Graph loading (used by WU1)
- S-JIGY-004: Edge validation (enhanced by WU1)
- S-CLI-008: Validate output format (behavior unchanged)
- S-NESTED-001: Nested subsystem structure (used by WU2)

---

## Open Questions

1. **Edge count ~422 vs 183:** Is this real duplication or double-counting?
   - Will investigate in WU3
   - Mark findings with #DISCOVERY

2. **Missing 4 nodes:** Are they real or counting bug?
   - Will investigate in WU4
   - Document root cause in Reflect

3. **Should validator check C/T annotation syntax?**
   - Current approach: Trust graph-index.yaml (if it loaded, annotations are valid)
   - Alternative: Re-scan and validate @jig annotations
   - Decision: Defer to future work (out of scope)

---

## Human Review Checkpoints

- [ ] After WU0: Review specifications, ensure they're clear and testable
- [ ] After WU1: Manually test validation, verify 0 false errors
- [ ] After WU2: Check status output, verify subsystems appear
- [ ] After WU5: Run all commands side-by-side, verify consistency
- [ ] Before merge: Review all markers, prepare for harvest

---

**Status:** Ready for execution
**Next:** Execute WU0 (create specifications), commit Intent before any code changes
