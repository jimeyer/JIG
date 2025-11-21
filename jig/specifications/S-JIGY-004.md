---
id: S-JIGY-004
type: specification
title: Edge validation with type-aware rules
subsystem: jigy-tool
status: active
created: 2025-11-21
implements:
  - O-JIGY-001
  - O-JIGY-003
---

# Specification: Edge Validation

## Purpose

Validate that all edges in the Intent graph point to existing nodes, use valid relationship types for the node types involved, and follow JIG v6.1 semantic rules. Detect broken references and orphaned nodes.

## Requirements

### 1. Edge Target Existence

Every edge must point to an existing node:

```python
for edge in registry.get_all_edges():
    if not registry.has_node(edge.target):
        report_error(f"Broken reference: {edge.source} → {edge.target} (target doesn't exist)")
```

**Severity:** ERROR (blocks validation)

### 2. Type-Aware Relationship Rules

Validate edge types are semantically valid for source/target node types:

| Edge Type | Valid Patterns | Invalid Patterns |
|-----------|----------------|------------------|
| `implements` | S→O, C→S | O→S, T→anything |
| `satisfies` | S→O | O→S, C→O, T→anything |
| `verifies` | T→S, T→O | O→T, S→T, C→T |
| `depends_on` | Any→Any | (generic dependency, all valid) |

**Example Valid:**
- S-AUTH-001 `implements` O-AUTH-001 ✓ (Spec implements Outcome)
- C-AUTH-001 `implements` S-AUTH-001 ✓ (Code implements Spec)
- T-AUTH-001 `verifies` S-AUTH-001 ✓ (Test verifies Spec)

**Example Invalid:**
- O-AUTH-001 `implements` S-AUTH-001 ✗ (Outcome can't implement Spec)
- T-AUTH-001 `implements` S-AUTH-001 ✗ (Test should verify, not implement)

**Severity:** ERROR (semantic violation)

### 3. Orphan Detection

Identify nodes with no edges (degree = 0):

```python
def detect_orphans(registry):
    orphans = []
    for node in registry.get_all_nodes():
        incoming = registry.get_edges_to(node.id)
        outgoing = registry.get_edges_from(node.id)
        
        if len(incoming) == 0 and len(outgoing) == 0:
            # Exception: Root outcomes (no outgoing) are not orphans
            if node.type == "outcome" and len(incoming) > 0:
                continue
            orphans.append(node)
    return orphans
```

**Severity:** WARNING (may be intentional for new nodes)

### 4. Self-Loop Detection

Detect nodes that reference themselves:

```python
for edge in registry.get_all_edges():
    if edge.source == edge.target:
        report_warning(f"Self-loop detected: {edge.source} → {edge.target}")
```

**Severity:** WARNING (usually unintentional)

### 5. Validation Report

```
Validating JIG graph...

Errors (2):
  ✗ Broken reference: S-AIR-001 → O-AIR-999 (target doesn't exist)
  ✗ Invalid edge type: O-AUTH-001 implements S-AUTH-001 (Outcomes can't implement Specs)

Warnings (3):
  ⚠ Orphaned node: S-PERF-001 (no edges)
  ⚠ Orphaned node: C-GATEWAY-042 (no edges)
  ⚠ Self-loop: S-TEST-001 depends_on S-TEST-001

Summary:
  ✓ 124 nodes valid
  ✓ 111 edges valid
  ✗ 2 errors found
  ⚠ 3 warnings

Exit code: 1 (errors found)
```

### 6. Validation Command

```bash
# Basic validation (errors only)
jigy validate

# Check all issues (errors + warnings)
jigy validate --check-all

# Strict mode (warnings = errors)
jigy validate --strict

# JSON output (for CI)
jigy validate --json
```

## Implementation Notes

**Location:** `jigy/validators/graph_validator.py`

**Dependencies:**
- NodeRegistry (S-JIGY-003)
- Edge type rules (configurable via config file)

**Validation Sequence:**
1. Load complete graph (all nodes + edges)
2. Check target existence for all edges
3. Check edge type rules for all edges
4. Detect orphaned nodes
5. Detect self-loops
6. Generate report
7. Return exit code (0 = pass, 1 = errors)

**Performance Target:** <1 second for 1000-node graph

## Edge Type Rules (Configurable)

In `jig/config.toml`:

```toml
[validation.edge_rules]
# Define valid source→target type combinations per edge type
implements = [
    ["specification", "outcome"],
    ["code", "specification"]
]

satisfies = [
    ["specification", "outcome"]
]

verifies = [
    ["test", "specification"],
    ["test", "outcome"]
]

# depends_on allows any→any (no restrictions)
depends_on = []  # Empty = allow all
```

## Test Cases

```python
# @jig T-JIGY-009 verifies:S-JIGY-004 subsystem:jigy-tool
def test_validate_broken_reference():
    """Test detection of edge pointing to non-existent node"""
    registry = NodeRegistry()
    registry.add_node(Node(id="S-001", type="specification", ...))
    registry.add_edge(Edge(source="S-001", target="O-999", type="implements"))
    
    result = validate_graph(registry)
    assert not result.valid
    assert "O-999" in result.errors[0]

# @jig T-JIGY-010 verifies:S-JIGY-004 subsystem:jigy-tool
def test_validate_invalid_edge_type():
    """Test detection of semantically invalid edge type"""
    registry = NodeRegistry()
    registry.add_node(Node(id="O-001", type="outcome", ...))
    registry.add_node(Node(id="S-001", type="specification", ...))
    # Invalid: Outcome implementing Spec (should be reverse)
    registry.add_edge(Edge(source="O-001", target="S-001", type="implements"))
    
    result = validate_graph(registry)
    assert not result.valid
    assert "Invalid edge type" in result.errors[0]

# @jig T-JIGY-011 verifies:S-JIGY-004 subsystem:jigy-tool
def test_detect_orphaned_nodes():
    """Test orphan detection"""
    registry = NodeRegistry()
    registry.add_node(Node(id="S-001", type="specification", ...))
    registry.add_node(Node(id="S-002", type="specification", ...))
    registry.add_edge(Edge(source="S-002", target="O-001", type="implements"))
    
    result = validate_graph(registry)
    assert len(result.warnings) == 1
    assert "S-001" in result.warnings[0]  # Orphan
```

## References

- O-JIGY-001: JIG graph accurately reflects all OSTC relationships
- O-JIGY-003: Code and Intent stay synchronized
- S017 Analysis: Part 3.1.4 (Edge validation & orphan detection)
- JIG v6.1 Spec: §1.2 (Relationship types)

