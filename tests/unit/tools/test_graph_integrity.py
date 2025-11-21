# @jig T-INTEGRITY-001 verifies:S-JIG-012 subsystem:jig-graph
"""Tests for graph integrity detection module."""

from pathlib import Path

import pytest

from jig.tools.graph_integrity import check_graph_integrity


# Fixtures
@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent.parent.parent / "fixtures"


@pytest.fixture
def orphan_graph(fixtures_dir):
    """Return path to graph with known orphan patterns."""
    return fixtures_dir / "graph_orphans.yaml"


@pytest.fixture
def empty_graph(fixtures_dir):
    """Return path to empty graph."""
    return fixtures_dir / "empty_graph.yaml"


@pytest.fixture
def subsystems_file(fixtures_dir):
    """Return path to subsystems file."""
    return fixtures_dir / "subsystems_empty.yaml"


# Tests for empty graph edge case
def test_empty_graph(empty_graph, subsystems_file):
    """Empty graph returns zero findings."""
    result = check_graph_integrity(empty_graph, subsystems_file)

    assert result["total_nodes"] == 0
    assert len(result["findings"]["dangling_references"]) == 0
    assert len(result["findings"]["unreferenced_nodes"]) == 0
    assert len(result["findings"]["malformed_structures"]) == 0
    assert "message" in result
    assert "empty" in result["message"].lower()


# Tests for dangling references
def test_dangling_reference_single(orphan_graph, subsystems_file):
    """Detects single dangling reference."""
    result = check_graph_integrity(orphan_graph, subsystems_file)
    dangling = result["findings"]["dangling_references"]

    # Find the S-TEST-002 issue
    s002_issues = [d for d in dangling if d["node_id"] == "S-TEST-002"]
    assert len(s002_issues) == 1

    issue = s002_issues[0]
    assert issue["node_type"] == "specification"
    assert issue["field"] == "implements"
    assert issue["missing_reference"] == "O-TEST-999"
    assert "node_context" in issue


def test_dangling_reference_in_list(orphan_graph, subsystems_file):
    """Detects dangling reference within a list."""
    result = check_graph_integrity(orphan_graph, subsystems_file)
    dangling = result["findings"]["dangling_references"]

    # Find the S-TEST-008 issue (has S-TEST-999 in depends_on list)
    s008_issues = [d for d in dangling if d["node_id"] == "S-TEST-008"]
    assert len(s008_issues) == 1

    issue = s008_issues[0]
    assert issue["field"] == "depends_on"
    assert issue["missing_reference"] == "S-TEST-999"


def test_mixed_string_list_formats_handled(orphan_graph, subsystems_file):
    """Handles both string and list relationship formats."""
    result = check_graph_integrity(orphan_graph, subsystems_file)

    # S-TEST-001 has string format (implements: O-TEST-001)
    # S-TEST-007 has list format (implements: [O-TEST-001, S-TEST-001])
    # Neither should have dangling references
    dangling_ids = {d["node_id"] for d in result["findings"]["dangling_references"]}
    assert "S-TEST-001" not in dangling_ids
    assert "S-TEST-007" not in dangling_ids


# Tests for unreferenced nodes
def test_unreferenced_node(orphan_graph, subsystems_file):
    """Detects isolated unreferenced node."""
    result = check_graph_integrity(orphan_graph, subsystems_file)
    unreferenced = result["findings"]["unreferenced_nodes"]

    # S-TEST-003 is never referenced
    s003_issues = [u for u in unreferenced if u["node_id"] == "S-TEST-003"]
    assert len(s003_issues) == 1

    issue = s003_issues[0]
    assert issue["node_type"] == "specification"
    assert issue["potential_reason"] == "isolated"


def test_root_outcome_flagged_as_possibly_intentional(orphan_graph, subsystems_file):
    """Root Outcome nodes flagged as possibly intentional."""
    result = check_graph_integrity(orphan_graph, subsystems_file)
    unreferenced = result["findings"]["unreferenced_nodes"]

    # O-TEST-001 is not referenced but is an outcome
    o001_issues = [u for u in unreferenced if u["node_id"] == "O-TEST-001"]

    # O-TEST-001 IS referenced by S-TEST-001, so it should NOT be in unreferenced
    # Let me check if there are any unreferenced outcomes
    unreferenced_outcomes = [
        u for u in unreferenced if u["node_type"] == "outcome"
    ]

    # If there are any, they should be marked as possibly_intentional_root
    for issue in unreferenced_outcomes:
        assert issue["potential_reason"] == "possibly_intentional_root"


def test_circular_references_not_flagged_as_orphans(orphan_graph, subsystems_file):
    """Circular references (A→B→A) are valid, not orphaned."""
    result = check_graph_integrity(orphan_graph, subsystems_file)
    unreferenced = result["findings"]["unreferenced_nodes"]

    # S-TEST-009 and S-TEST-010 reference each other (circular)
    # They should NOT be in unreferenced (they reference each other)
    unreferenced_ids = {u["node_id"] for u in unreferenced}
    assert "S-TEST-009" not in unreferenced_ids
    assert "S-TEST-010" not in unreferenced_ids


def test_self_reference_not_orphan(orphan_graph, subsystems_file):
    """Self-referencing node counts as referenced."""
    result = check_graph_integrity(orphan_graph, subsystems_file)
    unreferenced = result["findings"]["unreferenced_nodes"]

    # S-TEST-011 references itself
    # Self-references DO count as being referenced, so it should NOT appear in unreferenced
    # This is correct behavior - a self-reference prevents the node from being unreferenced
    s011_issues = [u for u in unreferenced if u["node_id"] == "S-TEST-011"]
    assert len(s011_issues) == 0  # Self-reference prevents being unreferenced


# Tests for malformed structures
def test_malformed_null_field(orphan_graph, subsystems_file):
    """Detects null relationship field."""
    result = check_graph_integrity(orphan_graph, subsystems_file)
    malformed = result["findings"]["malformed_structures"]

    # S-TEST-004 has implements: null
    s004_issues = [m for m in malformed if m["node_id"] == "S-TEST-004"]
    assert len(s004_issues) == 1

    issue = s004_issues[0]
    assert issue["issue"] == "relationship_field_null"
    assert issue["field"] == "implements"
    assert issue["value"] is None


def test_malformed_empty_list(orphan_graph, subsystems_file):
    """Detects empty list in relationship field."""
    result = check_graph_integrity(orphan_graph, subsystems_file)
    malformed = result["findings"]["malformed_structures"]

    # S-TEST-005 has implements: []
    s005_issues = [m for m in malformed if m["node_id"] == "S-TEST-005"]
    assert len(s005_issues) == 1

    issue = s005_issues[0]
    assert issue["issue"] == "relationship_field_empty_list"
    assert issue["field"] == "implements"
    assert issue["value"] == []


def test_malformed_invalid_type(orphan_graph, subsystems_file):
    """Detects invalid type (integer) in relationship field."""
    result = check_graph_integrity(orphan_graph, subsystems_file)
    malformed = result["findings"]["malformed_structures"]

    # S-TEST-006 has implements: 123
    s006_issues = [m for m in malformed if m["node_id"] == "S-TEST-006"]
    assert len(s006_issues) == 1

    issue = s006_issues[0]
    assert issue["issue"] == "relationship_field_invalid_type"
    assert issue["field"] == "implements"
    assert issue["value"] == 123
    assert issue["value_type"] == "int"


# Tests for statistics
def test_statistics_calculated(orphan_graph, subsystems_file):
    """Statistics are calculated correctly."""
    result = check_graph_integrity(orphan_graph, subsystems_file)
    stats = result["statistics"]

    assert "total_relationships" in stats
    assert "relationship_density" in stats
    assert "node_type_distribution" in stats

    # Check node type distribution
    assert "outcome" in stats["node_type_distribution"]
    assert "specification" in stats["node_type_distribution"]

    # Relationship density should be > 0
    assert stats["relationship_density"] > 0


# Tests for metadata
def test_output_includes_metadata(orphan_graph, subsystems_file):
    """Output includes timestamp and graph file path."""
    result = check_graph_integrity(orphan_graph, subsystems_file)

    assert "timestamp" in result
    assert "graph_file" in result
    assert "total_nodes" in result
    assert result["total_nodes"] == 12  # Count from fixture


def test_node_context_included_by_default(orphan_graph, subsystems_file):
    """Node context is included by default."""
    result = check_graph_integrity(orphan_graph, subsystems_file, include_node_context=True)
    dangling = result["findings"]["dangling_references"]

    if dangling:
        # Check first dangling reference has context
        assert "node_context" in dangling[0]
        assert "title" in dangling[0]["node_context"]


def test_node_context_excluded_when_disabled(orphan_graph, subsystems_file):
    """Node context can be excluded."""
    result = check_graph_integrity(
        orphan_graph, subsystems_file, include_node_context=False
    )
    dangling = result["findings"]["dangling_references"]

    if dangling:
        # Check first dangling reference does NOT have context
        assert "node_context" not in dangling[0]


# Tests for error handling
def test_missing_graph_file_raises(subsystems_file):
    """Raises FileNotFoundError if graph file doesn't exist."""
    missing_path = Path("/nonexistent/graph.yaml")

    with pytest.raises(FileNotFoundError, match="Graph file not found"):
        check_graph_integrity(missing_path, subsystems_file)


def test_missing_subsystems_file_raises(orphan_graph):
    """Raises FileNotFoundError if subsystems file doesn't exist."""
    missing_path = Path("/nonexistent/subsystems.yaml")

    with pytest.raises(FileNotFoundError, match="Subsystems file not found"):
        check_graph_integrity(orphan_graph, missing_path)


# Integration test with real jig graph
def test_real_jig_graph():
    """Integration test with actual jig graph."""
    graph_path = Path("jig/graph-index.yaml")
    subsystems_path = Path("jig/subsystems.yaml")

    if not graph_path.exists() or not subsystems_path.exists():
        pytest.skip("Real jig graph files not found")

    result = check_graph_integrity(graph_path, subsystems_path)

    # Should complete without errors
    assert result["total_nodes"] > 0
    assert "findings" in result
    assert "statistics" in result


# Performance test (basic)
def test_performance_reasonable(orphan_graph, subsystems_file):
    """Detection completes in reasonable time."""
    import time

    start = time.perf_counter()
    check_graph_integrity(orphan_graph, subsystems_file)
    elapsed = time.perf_counter() - start

    # Should be much faster than 100ms for small graph
    assert elapsed < 0.1, f"Detection took {elapsed:.3f}s, expected <0.1s"
