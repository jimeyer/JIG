---
id: S-JIGY-005
type: specification
title: Graph query commands (node, edges, list)
subsystem: jigy-tool
status: active
created: 2025-11-21
implements:
  - O-JIGY-002
---

# Specification: Graph Query Commands

## Purpose

Provide command-line interface for querying individual nodes, their relationships, and listing nodes by type or subsystem. Enable developers to explore the Intent graph interactively.

## Requirements

### 1. Node Details Command

**Command:** `jigy node <node-id>`

**Output:** Display complete node information with all relationships

```bash
$ jigy node S-AIR-001

S-AIR-001: BikeState messages use operation_type field directly
Type: specification
Subsystem: airspace
Status: active
File: jig/specifications/S-AIR-001.md

Implements (2):
  → O-AIR-001: Track bike states across multiple devices
  → O-AIR-002: BikeState changes propagate within 100ms

Implemented by (1):
  ← C-AIR-003: BikeState class in airspace/bike_state.py:42

Verified by (2):
  ← T-AIR-005: test_bike_state_operation_type
  ← T-AIR-007: test_bike_state_propagation
```

**Performance:** <100ms response time

### 2. Edge Listing Command

**Command:** `jigy edges <node-id> [--incoming|--outgoing]`

**Output:** List all edges for a node

```bash
$ jigy edges S-AIR-001

Edges for S-AIR-001:

Outgoing (2):
  S-AIR-001 --implements--> O-AIR-001
  S-AIR-001 --implements--> O-AIR-002

Incoming (3):
  C-AIR-003 --implements--> S-AIR-001
  T-AIR-005 --verifies--> S-AIR-001
  T-AIR-007 --verifies--> S-AIR-001

$ jigy edges S-AIR-001 --outgoing
  S-AIR-001 --implements--> O-AIR-001
  S-AIR-001 --implements--> O-AIR-002
```

**Performance:** <100ms response time

### 3. Node Listing Command

**Command:** `jigy list <type> [--subsystem <name>] [--status <status>]`

**Output:** List all nodes matching criteria

```bash
$ jigy list specification

Specifications (47):
  S-AIR-001: BikeState messages use operation_type field
  S-AIR-002: BikeState includes device_id field
  ...

$ jigy list specification --subsystem airspace

Specifications in airspace (12):
  S-AIR-001: BikeState messages use operation_type field
  S-AIR-002: BikeState includes device_id field
  ...

$ jigy list code --status active

Active Code Nodes (24):
  C-PS-001: EraLamportClock
  C-PS-002: ProtocolStack
  ...
```

**Performance:** <200ms response time

### 4. Output Formats

Support multiple output formats via `--format` flag:

**Text (Default):** Human-readable, colorized terminal output

**JSON:** Machine-readable for scripting
```bash
$ jigy node S-AIR-001 --format json
{
  "id": "S-AIR-001",
  "type": "specification",
  "title": "BikeState messages use operation_type field",
  "subsystem": "airspace",
  "status": "active",
  "file": "jig/specifications/S-AIR-001.md",
  "implements": ["O-AIR-001", "O-AIR-002"],
  "implemented_by": ["C-AIR-003"],
  "verified_by": ["T-AIR-005", "T-AIR-007"]
}
```

**YAML:** Configuration-friendly
```bash
$ jigy node S-AIR-001 --format yaml
id: S-AIR-001
type: specification
title: BikeState messages use operation_type field
...
```

### 5. Error Handling

**Node not found:**
```bash
$ jigy node S-NONEXISTENT-001
Error: Node S-NONEXISTENT-001 not found

Suggestions:
  - Check node ID format (e.g., S-SUBSYSTEM-NNN)
  - List all nodes: jigy list specification
  - Search: jigy search "keyword"
```

**Invalid type:**
```bash
$ jigy list invalid-type
Error: Unknown node type: invalid-type

Valid types: outcome, specification, code, test
```

## Implementation Notes

**Location:** `jigy/cli/query_commands.py`

**CLI Framework:** Use Click or Typer for command-line interface

**Dependencies:**
- NodeRegistry (S-JIGY-003)
- Rich or colorama for colored terminal output
- json/yaml libraries for format conversion

**Command Structure:**
```python
# @jig C-JIGY-005 implements:S-JIGY-005 subsystem:jigy-tool interface:public
@cli.command()
def node(node_id: str, format: str = "text"):
    """Display details for a specific node"""
    registry = load_registry()
    node = registry.get_node(node_id)
    
    if not node:
        error(f"Node {node_id} not found")
        return 1
    
    # Get relationships
    implements = registry.get_edges_from(node_id, type="implements")
    implemented_by = registry.get_edges_to(node_id, type="implements")
    verifies = registry.get_edges_to(node_id, type="verifies")
    
    # Format output
    if format == "json":
        output_json(node, implements, implemented_by, verifies)
    elif format == "yaml":
        output_yaml(node, implements, implemented_by, verifies)
    else:
        output_text(node, implements, implemented_by, verifies)
```

**Performance Optimization:**
- Cache registry between commands (CLI session)
- Use indices for fast edge queries
- Lazy load node content (only when needed)

## Test Cases

```python
# @jig T-JIGY-012 verifies:S-JIGY-005 subsystem:jigy-tool
def test_node_command():
    """Test node details command"""
    result = run_cli(["node", "S-AIR-001"])
    assert result.exit_code == 0
    assert "S-AIR-001" in result.output
    assert "BikeState" in result.output
    assert "Implements" in result.output

# @jig T-JIGY-013 verifies:S-JIGY-005 subsystem:jigy-tool
def test_node_command_json():
    """Test node command with JSON output"""
    result = run_cli(["node", "S-AIR-001", "--format", "json"])
    data = json.loads(result.output)
    assert data["id"] == "S-AIR-001"
    assert "implements" in data

# @jig T-JIGY-014 verifies:S-JIGY-005 subsystem:jigy-tool
def test_list_command_with_filter():
    """Test list command with subsystem filter"""
    result = run_cli(["list", "specification", "--subsystem", "airspace"])
    assert result.exit_code == 0
    assert "airspace" in result.output
    # Should not include other subsystems
    assert "protocol" not in result.output
```

## User Experience

**Discoverability:**
```bash
$ jigy --help
# Shows all commands

$ jigy node --help
# Shows node command options
```

**Tab Completion (Future):**
- Node IDs from registry
- Subsystem names
- Node types

## References

- O-JIGY-002: Developers can navigate Intent graph efficiently
- S-JIGY-003: Unified node registry (provides data)
- S017 Analysis: Part 3.2.1 (Graph queries)
- JIG v6.1 Spec: §5 (Tool design philosophy)

