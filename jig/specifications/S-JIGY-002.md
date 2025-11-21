---
id: S-JIGY-002
type: specification
title: Load graph-index.yaml for complete node registry
subsystem: jigy-tool
status: active
created: 2025-11-21
implements:
  - O-JIGY-001
---

# Specification: Graph Index Loading

## Purpose

Read `jig/graph-index.yaml` as a node registry to discover Code (C-*) and Test (T-*) nodes that aren't in separate markdown files. Support both node-centric and edge-centric relationship formats.

## Requirements

### 1. File Location

Load from: `jig/graph-index.yaml` (relative to project root)

If file doesn't exist: Continue with only O/S nodes (warn user)

### 2. Node-Centric Format (Primary)

Support relationships embedded in node definitions:

```yaml
version: '1.0'
nodes:
  - id: S-AIR-001
    type: specification
    title: BikeState messages use operation_type
    subsystem: airspace
    status: active
    file: jig/specifications/S-AIR-001.md
    implements:
      - O-AIR-001
      - O-AIR-002
  
  - id: C-AIR-003
    type: code
    title: BikeState class
    subsystem: airspace
    status: active
    file: src/airspace/bike_state.py
    line: 42
    implements:
      - S-AIR-001
```

### 3. Edge-Centric Format (Secondary)

Support separate edges section:

```yaml
version: '1.0'
nodes:
  - id: S-AIR-001
    type: specification
    file: jig/specifications/S-AIR-001.md

edges:
  - from: S-AIR-001
    to: O-AIR-001
    type: implements
  - from: C-AIR-003
    to: S-AIR-001
    type: implements
```

### 4. Node Type Discovery

Discover all OSTC node types from graph-index.yaml:
- **O nodes:** Point to `jig/outcomes/*.md` files
- **S nodes:** Point to `jig/specifications/*.md` files
- **C nodes:** Point to source files with line numbers
- **T nodes:** Point to test files with line numbers

### 5. Merge Strategy

When both markdown files and graph-index.yaml exist:

1. **Markdown takes precedence for O/S content**
   - Use markdown for title, body content
   - Use frontmatter for relationships
   
2. **graph-index.yaml provides C/T nodes**
   - C/T nodes only exist in graph-index (or as @jig annotations)
   - Add C/T nodes to registry
   
3. **Relationships union**
   - Combine edges from markdown frontmatter + graph-index
   - Warn on conflicts (same edge defined differently)

### 6. Required Node Fields

**All nodes must have:**
- `id`: Node identifier (e.g., "S-AIR-001")
- `type`: Node type (outcome, specification, code, test)
- `subsystem`: Subsystem name

**O/S nodes should have:**
- `file`: Path to markdown file (for traceability)
- `status`: active, deprecated, archived

**C/T nodes must have:**
- `file`: Path to source/test file
- `line`: Line number where node starts (optional but recommended)

## Implementation Notes

**Location:** `jigy/loaders/graph_index.py`

**Dependencies:**
- PyYAML for YAML parsing
- Path resolution (relative to project root)

**Data Flow:**
1. Check if graph-index.yaml exists
2. Load and parse YAML
3. Validate version (warn if not '1.0')
4. Parse nodes section
5. Extract relationships (node-centric or edge-centric)
6. Build node objects
7. Build edge list
8. Add to node registry (merge with markdown-discovered nodes)

**Performance Target:** <200ms to load 1000-node graph-index.yaml

## Error Handling

- **File not found:** Warn and continue with O/S nodes only
- **Invalid YAML:** Report parse error and exit
- **Missing required fields:** Warn and skip node
- **Invalid node ID format:** Warn and skip node
- **Duplicate node IDs:** Report conflict, use graph-index version

## Validation Rules

- Node IDs must match pattern: `[OSTC]-[A-Z]+-\d+`
- File paths should exist (warn if not found, don't fail)
- Edge targets will be validated separately (S-JIGY-004)

## Test Cases

```python
# @jig T-JIGY-004 verifies:S-JIGY-002 subsystem:jigy-tool
def test_load_node_centric_format():
    """Test loading graph-index with node-centric relationships"""
    yaml_content = """
version: '1.0'
nodes:
  - id: S-TEST-001
    type: specification
    implements: [O-TEST-001]
"""
    result = load_graph_index(yaml_content)
    assert len(result.nodes) == 1
    assert result.nodes[0].id == "S-TEST-001"
    assert len(result.edges) == 1

# @jig T-JIGY-005 verifies:S-JIGY-002 subsystem:jigy-tool
def test_load_edge_centric_format():
    """Test loading graph-index with separate edges section"""
    yaml_content = """
version: '1.0'
nodes:
  - id: S-TEST-001
    type: specification
edges:
  - from: S-TEST-001
    to: O-TEST-001
    type: implements
"""
    result = load_graph_index(yaml_content)
    assert len(result.edges) == 1
    assert result.edges[0].source == "S-TEST-001"

# @jig T-JIGY-006 verifies:S-JIGY-002 subsystem:jigy-tool
def test_merge_markdown_and_graph_index():
    """Test merging nodes from markdown and graph-index"""
    # Markdown has O/S nodes with relationships
    # graph-index has C/T nodes
    # Result should have all nodes, union of edges
```

## References

- O-JIGY-001: JIG graph accurately reflects all OSTC relationships
- S017 Analysis: Part 3.1.2 (Read graph-index.yaml)
- JIG v6.1 Spec: §8.2 (Graph index format)

