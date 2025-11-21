---
id: S-JIG-012
type: Specification
title: Deterministic Orphan Detection
subsystem: jig-graph
implements:
  - O-JIG-006
  - O-JIG-007
created: 2025-11-21
status: active
---

# Specification: Deterministic Orphan Detection

## Purpose

Provide fast, reliable detection of three types of graph integrity issues: dangling references, unreferenced nodes, and malformed structures.

## Requirements

### Detection Types

1. **Dangling References**
   - Detect: Node A references Node B, but B does not exist in the graph
   - Check relationship fields: `implements`, `specifies`, `contributes_to`, `depends_on`
   - Handle both string and list formats: `specifies: "O-001"` and `specifies: ["O-001", "O-002"]`

2. **Unreferenced Nodes**
   - Detect: Node exists but is never referenced by any other node
   - Algorithm: Set difference (all_node_ids - referenced_node_ids)
   - Context-aware: Flag as "potentially intentional" if node is root-level Outcome

3. **Malformed Structures**
   - Detect: Relationship fields with null values, invalid types, or empty lists
   - Examples: `implements: null`, `specifies: 123`, `depends_on: []`

### Performance

- **Latency**: <100ms for graphs up to 1000 nodes
- **Scalability**: O(n) complexity where n = number of nodes
- **Memory**: <50MB for typical graphs (<500 nodes)

### Output Format

Structured JSON:
```json
{
  "timestamp": "2025-11-21T10:30:00Z",
  "graph_file": "jig/graph-index.yaml",
  "total_nodes": 42,
  "findings": {
    "dangling_references": [{
      "node_id": "S-JIG-001",
      "node_type": "Specification",
      "field": "specifies",
      "missing_reference": "O-JIG-999",
      "node_context": {"description": "..."}
    }],
    "unreferenced_nodes": [{
      "node_id": "T-JIG-042",
      "node_type": "Technical Component",
      "node_data": {"description": "...", "status": "deprecated"},
      "potential_reason": "isolated"
    }],
    "malformed_structures": [{
      "node_id": "W-JIG-005",
      "issue": "relationship_field_empty",
      "field": "implements",
      "value": null
    }]
  },
  "statistics": {
    "total_relationships": 87,
    "relationship_density": 2.07,
    "node_type_distribution": {"Outcome": 5, "Specification": 12}
  }
}
```

### Edge Cases

- **Empty graph**: Return zero findings with message "No nodes to analyze"
- **Circular references**: A→B→A is valid, not flagged as orphan
- **Self-references**: Node references itself (flag as unusual but not error)
- **Mixed field formats**: Normalize lists and strings to consistent format

## Interface

```python
def check_graph_integrity(
    graph_path: Path,
    subsystems_path: Path,
    include_node_context: bool = True
) -> Dict[str, Any]:
    """
    Analyze graph integrity and return structured findings.

    Args:
        graph_path: Path to graph-index.yaml
        subsystems_path: Path to subsystems.yaml
        include_node_context: Include node descriptions in output

    Returns:
        Dictionary with findings, statistics, and metadata

    Raises:
        FileNotFoundError: If graph files don't exist
        YAMLError: If files have invalid YAML syntax
    """
```

## Rationale

Deterministic detection (set operations, schema validation) is:
- Fast: <100ms vs seconds for AI analysis
- Reliable: 100% consistent results, no LLM variability
- Cost-effective: Zero API costs
- Testable: Unit tests verify all edge cases

This forms the foundation for AI-powered analysis (S-JIG-013).

## Dependencies

- Python 3.9+
- PyYAML for parsing
- No external API dependencies

## Testing

- Unit tests for each detection type with fixtures
- Performance benchmarks (pytest-benchmark)
- Edge case validation (empty graph, circular refs, self-refs)
- Integration test with real jig graph

## References

- Analysis: `docs/wip/S013_deterministic-orphan-detection-analysis.md`
- SCOPE: `docs/wip/S014_SCOPE_ai_repair_orphaned_nodes.md`
