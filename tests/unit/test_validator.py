# @jig T-CORE-005 verifies:S-JIG-002 subsystem:core
"""Unit tests for OSTC node validation."""

from datetime import date
from pathlib import Path

from jig.core.parser import OSTCNode
from jig.core.validator import ValidationResult, validate_graph, validate_node, validate_node_file


def test_validate_node_valid() -> None:
    """Verify validation passes for valid node."""
    node = OSTCNode(
        id="O-TEST-001",
        type="outcome",
        title="Test Outcome",
        subsystem="core",
        created=date(2025, 11, 19),
    )

    result = validate_node(node)

    assert result.valid
    assert len(result.errors) == 0
    # May have warnings about optional fields, but should be valid


# @jig T-CORE-006 verifies:S-JIG-002 subsystem:core
def test_validate_node_missing_required_field() -> None:
    """Verify validation detects missing 'title' field."""
    node = OSTCNode(
        id="O-TEST-002",
        type="outcome",
        title="",  # Empty title
    )

    result = validate_node(node)

    assert not result.valid
    assert any("title" in error.lower() for error in result.errors)


def test_validate_node_missing_id() -> None:
    """Verify validation detects missing 'id' field."""
    node = OSTCNode(
        id="",
        type="outcome",
        title="Test",
    )

    result = validate_node(node)

    assert not result.valid
    assert any("id" in error.lower() for error in result.errors)


def test_validate_node_missing_type() -> None:
    """Verify validation detects missing 'type' field."""
    node = OSTCNode(
        id="O-TEST-003",
        type="",
        title="Test",
    )

    result = validate_node(node)

    assert not result.valid
    assert any("type" in error.lower() for error in result.errors)


# @jig T-CORE-007 verifies:S-JIG-002 subsystem:core
def test_validate_node_invalid_id_format() -> None:
    """Verify validation detects invalid ID format (underscore)."""
    node = OSTCNode(
        id="O_TEST_001",  # Underscores instead of hyphens
        type="outcome",
        title="Test",
    )

    result = validate_node(node)

    assert not result.valid
    assert any("invalid id format" in error.lower() for error in result.errors)


def test_validate_node_invalid_id_lowercase() -> None:
    """Verify validation detects lowercase in ID."""
    node = OSTCNode(
        id="o-test-001",  # Lowercase
        type="outcome",
        title="Test",
    )

    result = validate_node(node)

    assert not result.valid
    assert any("invalid id format" in error.lower() for error in result.errors)


def test_validate_node_invalid_id_no_number() -> None:
    """Verify validation detects ID without trailing number."""
    node = OSTCNode(
        id="O-TEST",  # No number
        type="outcome",
        title="Test",
    )

    result = validate_node(node)

    assert not result.valid
    assert any("invalid id format" in error.lower() for error in result.errors)


# @jig T-CORE-008 verifies:S-JIG-002 subsystem:core
def test_validate_node_type_mismatch() -> None:
    """Verify validation detects ID prefix mismatch (O- with type:specification)."""
    node = OSTCNode(
        id="O-TEST-001",  # O prefix
        type="specification",  # But type is specification (should be S-)
        title="Test",
    )

    result = validate_node(node)

    assert not result.valid
    assert any(
        "prefix" in error.lower() and "doesn't match" in error.lower()
        for error in result.errors
    )


def test_validate_node_invalid_type_value() -> None:
    """Verify validation detects invalid type value."""
    node = OSTCNode(
        id="X-TEST-001",
        type="invalid_type",  # Invalid type
        title="Test",
    )

    result = validate_node(node)

    assert not result.valid
    assert any("invalid type" in error.lower() for error in result.errors)


def test_validate_node_warnings_for_optional_fields() -> None:
    """Verify warnings generated for missing optional but recommended fields."""
    node = OSTCNode(
        id="O-TEST-004",
        type="outcome",
        title="Test",
        # No subsystem, no created date
    )

    result = validate_node(node)

    # Should be valid (fields are optional)
    assert result.valid
    # But should have warnings
    assert len(result.warnings) > 0
    assert any("subsystem" in warning.lower() for warning in result.warnings)


def test_validate_node_all_types_with_correct_prefixes() -> None:
    """Verify all markdown node types (O/S/C) validate with correct prefix."""
    test_cases = [
        ("O-TEST-001", "outcome"),
        ("S-TEST-001", "specification"),
        ("C-TEST-001", "constraint"),
    ]

    for node_id, node_type in test_cases:
        node = OSTCNode(
            id=node_id,
            type=node_type,
            title=f"Test {node_type}",
            subsystem="core",
            created=date(2025, 11, 19),
        )

        result = validate_node(node)

        assert result.valid, f"Expected {node_id} with type {node_type} to be valid"
        assert len(result.errors) == 0


def test_validate_node_test_type_rejected_with_helpful_error() -> None:
    """Verify test type is rejected with helpful error message about annotations."""
    node = OSTCNode(
        id="T-TEST-001",
        type="test",
        title="Test node",
        subsystem="core",
        created=date(2025, 11, 19),
    )

    result = validate_node(node)

    assert not result.valid
    assert len(result.errors) > 0
    # Check for helpful error message mentioning annotations and OSTCX model
    error_text = " ".join(result.errors).lower()
    assert "test" in error_text
    assert "annotation" in error_text
    assert "jig-concept-v7" in error_text


# @jig T-CORE-009 verifies:S-JIG-002 subsystem:core
def test_validate_graph_duplicate_ids(tmp_path: Path) -> None:
    """Verify validation detects duplicate node IDs."""
    # Create JIG structure
    outcomes_dir = tmp_path / "outcomes"
    outcomes_dir.mkdir(parents=True)

    # Create two nodes with same ID
    node1_content = """---
id: O-TEST-001
type: outcome
title: "First node"
---
Content
"""
    node2_content = """---
id: O-TEST-001
type: outcome
title: "Second node with duplicate ID"
---
Different content
"""

    (outcomes_dir / "first.md").write_text(node1_content)
    (outcomes_dir / "second.md").write_text(node2_content)

    result = validate_graph(tmp_path)

    assert not result.valid
    assert any("duplicate" in error.lower() for error in result.errors)
    assert any("O-TEST-001" in error for error in result.errors)


# @jig T-CORE-010 verifies:S-JIG-002 subsystem:core
def test_validate_graph_orphaned_references() -> None:
    """Verify validation detects references to non-existent nodes."""
    # This test would require graph-index.yaml with references to missing nodes
    # Will be covered in integration test with actual graph index
    pass  # Placeholder for now


def test_validate_graph_missing_intent_dir(tmp_path: Path) -> None:
    """Verify validation handles missing intent directory."""
    nonexistent_dir = tmp_path / "nonexistent"

    result = validate_graph(nonexistent_dir)

    assert not result.valid
    assert any("not found" in error.lower() for error in result.errors)


def test_validate_graph_empty_directory(tmp_path: Path) -> None:
    """Verify validation handles empty intent directory."""
    # Create empty directories
    (tmp_path / "outcomes").mkdir(parents=True)
    (tmp_path / "specifications").mkdir(parents=True)
    (tmp_path / "tests").mkdir(parents=True)
    (tmp_path / "constraints").mkdir(parents=True)

    result = validate_graph(tmp_path)

    # Should be valid but may have warnings
    assert result.valid
    # No nodes to validate


def test_validate_graph_with_valid_nodes(tmp_path: Path) -> None:
    """Verify validation passes with valid nodes."""
    outcomes_dir = tmp_path / "outcomes"
    outcomes_dir.mkdir(parents=True)

    # Create valid nodes
    node1_content = """---
id: O-TEST-001
type: outcome
title: "First outcome"
subsystem: core
created: 2025-11-19
---
Content
"""
    node2_content = """---
id: O-TEST-002
type: outcome
title: "Second outcome"
subsystem: core
created: 2025-11-19
---
Content
"""

    (outcomes_dir / "O-TEST-001.md").write_text(node1_content)
    (outcomes_dir / "O-TEST-002.md").write_text(node2_content)

    result = validate_graph(tmp_path)

    assert result.valid
    assert len(result.errors) == 0


def test_validate_graph_with_invalid_node(tmp_path: Path) -> None:
    """Verify validation detects errors in individual nodes within graph."""
    outcomes_dir = tmp_path / "outcomes"
    outcomes_dir.mkdir(parents=True)

    # Create node with invalid ID format
    node_content = """---
id: O_TEST_001
type: outcome
title: "Invalid ID format"
---
Content
"""

    (outcomes_dir / "invalid.md").write_text(node_content)

    result = validate_graph(tmp_path)

    assert not result.valid
    assert any("invalid id format" in error.lower() for error in result.errors)


def test_validate_graph_with_malformed_yaml(tmp_path: Path) -> None:
    """Verify validation handles malformed YAML in node files."""
    outcomes_dir = tmp_path / "outcomes"
    outcomes_dir.mkdir(parents=True)

    # Create node with malformed YAML
    node_content = """---
id: O-TEST-001
type: outcome
title: [malformed yaml
---
Content
"""

    (outcomes_dir / "malformed.md").write_text(node_content)

    result = validate_graph(tmp_path)

    assert not result.valid
    assert any("failed to parse" in error.lower() for error in result.errors)


def test_validate_graph_index_nonexistent_node(tmp_path: Path) -> None:
    """Verify validation detects graph index referencing non-existent nodes."""
    import yaml

    outcomes_dir = tmp_path / "outcomes"
    outcomes_dir.mkdir(parents=True)

    # Create one real node
    node_content = """---
id: O-TEST-001
type: outcome
title: "Real node"
---
Content
"""
    (outcomes_dir / "O-TEST-001.md").write_text(node_content)

    # Create graph index referencing non-existent node
    graph_index = {
        "version": "1.0",
        "nodes": [
            {"id": "O-TEST-001", "type": "outcome"},
            {"id": "O-MISSING-001", "type": "outcome"},  # Doesn't exist
        ],
    }
    (tmp_path / "graph-index.yaml").write_text(yaml.dump(graph_index))

    result = validate_graph(tmp_path)

    assert not result.valid
    assert any("non-existent node" in error.lower() for error in result.errors)
    assert any("O-MISSING-001" in error for error in result.errors)


def test_validate_graph_orphaned_nodes_warning(tmp_path: Path) -> None:
    """Verify validation warns about nodes not in graph index."""
    import yaml

    outcomes_dir = tmp_path / "outcomes"
    outcomes_dir.mkdir(parents=True)

    # Create two nodes
    node1_content = """---
id: O-TEST-001
type: outcome
title: "Indexed node"
---
Content
"""
    node2_content = """---
id: O-TEST-002
type: outcome
title: "Orphaned node"
---
Content
"""
    (outcomes_dir / "O-TEST-001.md").write_text(node1_content)
    (outcomes_dir / "O-TEST-002.md").write_text(node2_content)

    # Create graph index with only one node
    graph_index = {
        "version": "1.0",
        "nodes": [
            {"id": "O-TEST-001", "type": "outcome"},
        ],
    }
    (tmp_path / "graph-index.yaml").write_text(yaml.dump(graph_index))

    result = validate_graph(tmp_path)

    # Should be valid but have warning
    assert result.valid
    assert len(result.warnings) > 0
    assert any("not referenced in graph index" in warning.lower() for warning in result.warnings)
    assert any("O-TEST-002" in warning for warning in result.warnings)


def test_validate_node_file_success(tmp_path: Path) -> None:
    """Verify validate_node_file works for valid file."""
    node_file = tmp_path / "O-TEST-001.md"
    node_content = """---
id: O-TEST-001
type: outcome
title: "Test outcome"
subsystem: core
created: 2025-11-19
---
Content
"""
    node_file.write_text(node_content)

    result = validate_node_file(node_file)

    assert result.valid
    assert len(result.errors) == 0


def test_validate_node_file_not_found(tmp_path: Path) -> None:
    """Verify validate_node_file handles missing file."""
    node_file = tmp_path / "nonexistent.md"

    result = validate_node_file(node_file)

    assert not result.valid
    assert any("not found" in error.lower() for error in result.errors)


def test_validate_node_file_invalid_content(tmp_path: Path) -> None:
    """Verify validate_node_file detects invalid node content."""
    node_file = tmp_path / "invalid.md"
    node_content = """---
id: O_INVALID_001
type: outcome
title: "Invalid ID"
---
Content
"""
    node_file.write_text(node_content)

    result = validate_node_file(node_file)

    assert not result.valid
    assert any("invalid id format" in error.lower() for error in result.errors)


def test_validation_result_dataclass() -> None:
    """Verify ValidationResult dataclass works correctly."""
    # Test with no errors or warnings
    result1 = ValidationResult(valid=True)
    assert result1.valid
    assert result1.errors == []
    assert result1.warnings == []

    # Test with errors
    result2 = ValidationResult(
        valid=False,
        errors=["Error 1", "Error 2"],
        warnings=["Warning 1"],
    )
    assert not result2.valid
    assert len(result2.errors) == 2
    assert len(result2.warnings) == 1


# @jig T-JIGY-040 verifies:S-JIGY-012 subsystem:jigy-tool
def test_validate_graph_with_ct_nodes(tmp_path: Path) -> None:
    """Verify validator understands C/T nodes from graph-index.yaml.

    This test verifies that the validator doesn't generate false errors
    for C (code) and T (test) nodes that exist in graph-index.yaml but
    not as markdown files.
    """
    import yaml

    # Create markdown nodes (O/S/X)
    outcomes_dir = tmp_path / "outcomes"
    outcomes_dir.mkdir(parents=True)

    outcome_content = """---
id: O-TEST-001
type: outcome
title: "Test outcome"
subsystem: test
created: 2025-11-21
---
Content
"""
    (outcomes_dir / "O-TEST-001.md").write_text(outcome_content)

    specs_dir = tmp_path / "specifications"
    specs_dir.mkdir(parents=True)

    spec_content = """---
id: S-TEST-001
type: specification
title: "Test specification"
subsystem: test
created: 2025-11-21
---
Content
"""
    (specs_dir / "S-TEST-001.md").write_text(spec_content)

    # Add C/T nodes to graph-index.yaml
    graph_index = {
        "version": "1.0",
        "nodes": [
            {"id": "O-TEST-001", "type": "outcome", "subsystem": "test"},
            {"id": "S-TEST-001", "type": "specification", "subsystem": "test"},
            {"id": "C-TEST-001", "type": "code", "subsystem": "test", "file": "src/test.py", "line": 10},
            {"id": "T-TEST-001", "type": "test", "subsystem": "test", "file": "tests/test_test.py", "line": 5},
        ],
        "edges": []
    }
    (tmp_path / "graph-index.yaml").write_text(yaml.dump(graph_index))

    # Validate
    result = validate_graph(tmp_path)

    # Should pass (no false errors for C/T)
    assert result.valid, f"Validation failed with errors: {result.errors}"

    # Should NOT have errors about C/T nodes being non-existent
    error_text = " ".join(result.errors).lower()
    assert "c-test-001" not in error_text, "False error for C-TEST-001"
    assert "t-test-001" not in error_text, "False error for T-TEST-001"
    assert "non-existent node" not in error_text, "False 'non-existent node' errors"
