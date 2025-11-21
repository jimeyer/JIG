---
id: S-JIGY-007
type: specification
title: Subsystem queries with internal/external edge classification
subsystem: jigy-tool
status: active
created: 2025-11-21
implements:
  - O-JIGY-002
---

# Specification: Subsystem Queries

## Purpose

Enable subsystem-level analysis: list nodes in a subsystem, show internal vs external edges, calculate coupling metrics. Support architectural analysis and boundary enforcement.

## Requirements

### 1. Subsystem Details Command

**Command:** `jigy subsystem <name>`

**Output:** Complete subsystem information

```bash
$ jigy subsystem airspace

Subsystem: airspace
Description: Manages distributed bike state with CRDT

Nodes: 33 total
  Outcomes: 10
  Specifications: 12
  Code: 6
  Tests: 5

Files:
  - jig/outcomes/O-AIR-*.md (10 files)
  - jig/specifications/S-AIR-*.md (12 files)
  - src/airspace/ (6 code nodes)
  - test/airspace/ (5 test nodes)

Related subsystems:
  protocol (8 edges)
  gateway (2 edges)
  crdt (5 edges)
```

**Performance:** <200ms response time

### 2. Subsystem List Command

**Command:** `jigy subsystems`

**Output:** List all subsystems with node counts

```bash
$ jigy subsystems

Subsystems (7):
  airspace           33 nodes (10 O, 12 S,  6 C,  5 T)
  protocol-stack     28 nodes ( 4 O, 12 S,  8 C,  4 T)
  multi-plane-server 24 nodes ( 4 O,  8 S,  6 C,  6 T)
  gateway            16 nodes ( 2 O,  6 S,  4 C,  4 T)
  crdt               18 nodes ( 3 O,  7 S,  5 C,  3 T)
  protocol            8 nodes ( 0 O,  4 S,  3 C,  1 T)
  testing             5 nodes ( 0 O,  2 S,  2 C,  1 T)

Total: 126 nodes across 7 subsystems
```

### 3. Edge Classification

Classify edges as internal (within subsystem) or external (cross-subsystem):

**Internal edge:** source.subsystem == target.subsystem

**External edge:** source.subsystem != target.subsystem

```bash
$ jigy subsystem airspace --edges

Subsystem: airspace

Internal edges: 28
  S-AIR-001 --implements--> O-AIR-001 (both airspace)
  S-AIR-002 --implements--> O-AIR-001 (both airspace)
  C-AIR-003 --implements--> S-AIR-001 (both airspace)
  ...

External edges: 15
  To protocol (8):
    C-AIR-003 --depends_on--> C-PROTOCOL-001 (airspace → protocol)
    S-AIR-005 --depends_on--> S-PROTOCOL-002 (airspace → protocol)
    ...
  
  To gateway (2):
    S-AIR-008 --depends_on--> S-GATEWAY-001 (airspace → gateway)
    ...
  
  To crdt (5):
    C-AIR-010 --depends_on--> C-CRDT-001 (airspace → crdt)
    ...

Coupling ratio: 1.87:1 (internal / external)
```

### 4. Coupling Metrics

Calculate subsystem coupling metrics:

**Coupling Ratio:** internal_edges / external_edges
- Target: >10:1 (from JIG v6.1 Nearly Decomposable Systems)
- Higher = better modularity

**External Edge Count:** Number of cross-subsystem dependencies
- Lower = better isolation

**External Subsystem Count:** Number of other subsystems depended on
- Lower = simpler interfaces

```bash
$ jigy subsystem airspace --metrics

Subsystem: airspace
  Internal edges: 28
  External edges: 15
  Coupling ratio: 1.87:1  ⚠ (target: >10:1)
  
  External dependencies (3 subsystems):
    protocol       (8 edges)  ← primary dependency
    crdt           (5 edges)
    gateway        (2 edges)
  
Health: Moderate coupling (below 10:1 target)
Recommendation: Review dependencies on protocol subsystem
```

### 5. Subsystem Filtering

Filter nodes by subsystem in other commands:

```bash
$ jigy list specification --subsystem airspace
$ jigy trace O-AIR-001 --subsystem airspace  # Only traverse within subsystem
```

### 6. Load subsystems.yaml

Load subsystem definitions from `jig/subsystems.yaml`:

```yaml
subsystems:
  - name: airspace
    description: Manages distributed bike state with CRDT
    owner: team-airspace
  - name: protocol
    description: Low-level protocol implementation
    owner: team-protocol
```

If file doesn't exist: Infer subsystems from node metadata

## Implementation Notes

**Location:** `jigy/cli/subsystem_commands.py`

**Dependencies:**
- NodeRegistry (S-JIGY-003)
- subsystems.yaml loader

**Edge Classification Algorithm:**
```python
# @jig C-JIGY-007 implements:S-JIGY-007 subsystem:jigy-tool interface:public
def classify_subsystem_edges(registry, subsystem_name):
    """Classify edges as internal or external for a subsystem"""
    nodes = registry.get_nodes_by_subsystem(subsystem_name)
    node_ids = set(n.id for n in nodes)
    
    internal_edges = []
    external_edges = []
    
    for node in nodes:
        # Check outgoing edges
        for edge in registry.get_edges_from(node.id):
            target = registry.get_node(edge.target)
            
            if target.subsystem == subsystem_name:
                internal_edges.append(edge)
            else:
                external_edges.append(edge)
    
    return internal_edges, external_edges
```

**Coupling Ratio Calculation:**
```python
def calculate_coupling_ratio(internal_edges, external_edges):
    """Calculate coupling ratio (internal / external)"""
    if len(external_edges) == 0:
        return float('inf')  # Perfect isolation
    return len(internal_edges) / len(external_edges)
```

**Performance Optimization:**
- Cache subsystem node lists
- Build subsystem edge indices on load
- Lazy compute metrics (only when requested)

## Test Cases

```python
# @jig T-JIGY-018 verifies:S-JIGY-007 subsystem:jigy-tool
def test_subsystem_details():
    """Test subsystem details command"""
    result = run_cli(["subsystem", "airspace"])
    assert result.exit_code == 0
    assert "airspace" in result.output
    assert "Nodes:" in result.output

# @jig T-JIGY-019 verifies:S-JIGY-007 subsystem:jigy-tool
def test_edge_classification():
    """Test internal vs external edge classification"""
    internal, external = classify_subsystem_edges(registry, "airspace")
    
    # All internal edges should have source and target in same subsystem
    for edge in internal:
        source = registry.get_node(edge.source)
        target = registry.get_node(edge.target)
        assert source.subsystem == target.subsystem == "airspace"
    
    # External edges cross subsystem boundaries
    for edge in external:
        source = registry.get_node(edge.source)
        target = registry.get_node(edge.target)
        assert source.subsystem != target.subsystem

# @jig T-JIGY-020 verifies:S-JIGY-007 subsystem:jigy-tool
def test_coupling_ratio():
    """Test coupling ratio calculation"""
    internal = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # 10 internal
    external = [1, 2]  # 2 external
    ratio = calculate_coupling_ratio(internal, external)
    assert ratio == 5.0  # 10/2
```

## References

- O-JIGY-002: Developers can navigate Intent graph efficiently
- S-JIGY-003: Unified node registry (provides subsystem data)
- S017 Analysis: Part 3.2.3 (Subsystem queries)
- JIG v6.1 Spec: §2 (Nearly Decomposable Systems)

