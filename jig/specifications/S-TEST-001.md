---
id: S-TEST-001
type: specification
title: Generic test specification for fixtures and examples
subsystem: test-fixtures
status: test-fixture
implements:
  - O-TEST-001
created: 2025-11-21
---

# Specification: Generic Test Fixture

## Purpose

This is a generic specification node used in test fixtures, examples, and documentation. It serves as a placeholder for testing graph operations, validation logic, and annotation parsing.

## Context

This node is referenced in:
- Unit tests for annotation parsing
- Edge validation tests
- Graph traversal examples
- Documentation examples

**Not for production use.** This specification exists solely to support testing infrastructure.

## Test Usage Examples

### Annotation Parsing
```python
# @jig C-TESTING-001 implements:S-TEST-001 subsystem:test
# @jig T-TESTABLE-001 verifies:S-TEST-001 subsystem:test
```

### Edge Validation
```python
graph.edges.append(Edge("C-001", "S-TEST-001", "implements"))
graph.edges.append(Edge("T-001", "S-TEST-001", "verifies"))
```

### Integration Tests
Used in temporary test graphs for decompose metrics and coupling analysis.

## References

- Tests: `tests/unit/test_annotation_scanner.py`
- Tests: `tests/unit/test_edge_validation.py`
- Tests: `tests/integration/test_decompose_commands.py`
