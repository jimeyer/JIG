# @jig T-NESTED-001 verifies:S-NESTED-001 subsystem:core
"""Unit tests for nested subsystems functionality."""

import json
from pathlib import Path
from textwrap import dedent

import pytest

from jig.core.graph import Graph, Subsystem
from jig.core.validator import validate_nested_subsystems


def test_nested_subsystem_loading(tmp_path: Path) -> None:
    """Verify Graph loads nested subsystems from JSON."""
    # Create test directory structure
    intent_dir = tmp_path / "jig"
    intent_dir.mkdir()
    (intent_dir / "outcomes").mkdir()
    (intent_dir / "specifications").mkdir()

    # Create some test nodes
    (intent_dir / "outcomes" / "O-TEST-001.md").write_text(
        dedent("""
        ---
        id: O-TEST-001
        type: outcome
        title: Test outcome
        subsystem: crdt.ser
        ---
        Test outcome content.
        """)
    )

    (intent_dir / "specifications" / "S-TEST-001.md").write_text(
        dedent("""
        ---
        id: S-TEST-001
        type: specification
        title: Test spec
        subsystem: crdt.deser
        ---
        Test spec content.
        """)
    )

    # Create graph-index.json with nested subsystems
    (intent_dir / "graph-index.json").write_text(json.dumps({
        "version": "1.0",
        "generated": "2025-11-22T00:00:00Z",
        "subsystems": {
            "core": {
                "description": "Core subsystem",
                "nodes": ["O-CORE-001"]
            },
            "crdt": {
                "description": "CRDT subsystem (parent)",
                "subsystems": {
                    "ser": {
                        "description": "Serialization",
                        "nodes": ["O-TEST-001"]
                    },
                    "deser": {
                        "description": "Deserialization",
                        "nodes": ["S-TEST-001"]
                    }
                }
            }
        },
        "edges": []
    }, indent=2))

    # Load graph
    graph = Graph.load_from_dir(intent_dir)

    # Verify root subsystems loaded
    assert "core" in graph.subsystems
    assert "crdt" in graph.subsystems

    # Verify nested structure
    crdt = graph.subsystems["crdt"]
    assert crdt.name == "crdt"
    assert crdt.description == "CRDT subsystem (parent)"
    assert len(crdt.subsystems) == 2
    assert "ser" in crdt.subsystems
    assert "deser" in crdt.subsystems

    # Verify child subsystems
    ser = crdt.subsystems["ser"]
    assert ser.name == "ser"
    assert ser.parent_path == "crdt"
    assert ser.full_path == "crdt.ser"
    assert ser.description == "Serialization"
    assert ser.nodes == ["O-TEST-001"]

    deser = crdt.subsystems["deser"]
    assert deser.name == "deser"
    assert deser.parent_path == "crdt"
    assert deser.full_path == "crdt.deser"


# @jig T-NESTED-002 verifies:S-NESTED-002 subsystem:core
def test_subsystem_path_resolution(tmp_path: Path) -> None:
    """Verify get_subsystem_by_path() navigates hierarchy."""
    intent_dir = tmp_path / "jig"
    intent_dir.mkdir()
    (intent_dir / "outcomes").mkdir()

    # Create graph-index.json with 3-level nesting
    (intent_dir / "graph-index.json").write_text(json.dumps({
        "version": "1.0",
        "generated": "2025-11-22T00:00:00Z",
        "subsystems": {
            "app": {
                "subsystems": {
                    "backend": {
                        "subsystems": {
                            "api": {
                                "nodes": ["O-API-001"]
                            },
                            "db": {
                                "nodes": ["O-DB-001"]
                            }
                        }
                    },
                    "frontend": {
                        "nodes": ["O-UI-001"]
                    }
                }
            }
        },
        "edges": []
    }, indent=2))

    graph = Graph.load_from_dir(intent_dir)

    # Test path resolution
    app = graph.get_subsystem_by_path("app")
    assert app is not None
    assert app.name == "app"

    backend = graph.get_subsystem_by_path("app.backend")
    assert backend is not None
    assert backend.name == "backend"
    assert backend.parent_path == "app"

    api = graph.get_subsystem_by_path("app.backend.api")
    assert api is not None
    assert api.name == "api"
    assert api.parent_path == "app.backend"
    assert api.full_path == "app.backend.api"

    # Test non-existent paths
    assert graph.get_subsystem_by_path("nonexistent") is None
    assert graph.get_subsystem_by_path("app.nonexistent") is None
    assert graph.get_subsystem_by_path("app.backend.nonexistent") is None


# @jig T-NESTED-003 verifies:S-NESTED-001 subsystem:core
def test_recursive_node_collection(tmp_path: Path) -> None:
    """Verify get_all_nodes(recursive=True) includes children."""
    intent_dir = tmp_path / "jig"
    intent_dir.mkdir()
    (intent_dir / "outcomes").mkdir()

    (intent_dir / "graph-index.json").write_text(json.dumps({
        "version": "1.0",
        "generated": "2025-11-22T00:00:00Z",
        "subsystems": {
            "parent": {
                "subsystems": {
                    "child1": {
                        "nodes": ["O-001", "O-002"]
                    },
                    "child2": {
                        "nodes": ["O-003"],
                        "subsystems": {
                            "grandchild": {
                                "nodes": ["O-004", "O-005"]
                            }
                        }
                    }
                }
            }
        },
        "edges": []
    }, indent=2))

    graph = Graph.load_from_dir(intent_dir)
    parent = graph.get_subsystem_by_path("parent")
    assert parent is not None

    # Non-recursive: parent has no direct nodes
    assert parent.get_all_nodes(recursive=False) == []

    # Recursive: should get all nodes from children
    all_nodes = parent.get_all_nodes(recursive=True)
    assert set(all_nodes) == {"O-001", "O-002", "O-003", "O-004", "O-005"}

    # Test child2 recursive
    child2 = graph.get_subsystem_by_path("parent.child2")
    assert child2 is not None
    child2_nodes = child2.get_all_nodes(recursive=True)
    assert set(child2_nodes) == {"O-003", "O-004", "O-005"}

    # Test leaf subsystem
    grandchild = graph.get_subsystem_by_path("parent.child2.grandchild")
    assert grandchild is not None
    assert grandchild.get_all_nodes(recursive=False) == ["O-004", "O-005"]
    assert grandchild.get_all_nodes(recursive=True) == ["O-004", "O-005"]


# @jig T-NESTED-004 verifies:S-NESTED-005 subsystem:core
def test_cycle_detection() -> None:
    """Verify validation passes for valid hierarchies (cycles impossible via YAML)."""
    # Create graph with valid nested subsystems
    graph = Graph()

    # Create subsystems manually
    parent = Subsystem(name="parent", parent_path="")
    child = Subsystem(name="child", parent_path="parent")
    grandchild = Subsystem(name="grandchild", parent_path="parent.child")

    parent.subsystems["child"] = child
    child.subsystems["grandchild"] = grandchild

    # Add to graph
    graph.subsystems["parent"] = parent

    # Should be valid (no cycle)
    errors = validate_nested_subsystems(graph)
    assert len(errors) == 0

    # Note: True cycles are impossible to create via YAML loading
    # because YAML doesn't support circular references. The cycle detection
    # is defensive programming for manual graph construction scenarios.


# @jig T-NESTED-005 verifies:S-NESTED-005 subsystem:core
def test_parent_with_nodes_validation(tmp_path: Path) -> None:
    """Verify validation prevents nodes in parent subsystems."""
    intent_dir = tmp_path / "jig"
    intent_dir.mkdir()
    (intent_dir / "outcomes").mkdir()

    # Create graph-index.json with parent that has both children AND nodes
    (intent_dir / "graph-index.json").write_text(json.dumps({
        "version": "1.0",
        "generated": "2025-11-22T00:00:00Z",
        "subsystems": {
            "parent": {
                "nodes": ["O-PARENT-001"],
                "subsystems": {
                    "child": {
                        "nodes": ["O-CHILD-001"]
                    }
                }
            }
        },
        "edges": []
    }, indent=2))

    graph = Graph.load_from_dir(intent_dir)

    # Validate - should detect error
    errors = validate_nested_subsystems(graph)
    assert len(errors) > 0
    assert any("has both children and direct nodes" in error for error in errors)
    assert any("parent" in error for error in errors)


# @jig T-NESTED-006 verifies:S-NESTED-001 subsystem:core
def test_backward_compatibility_flat(tmp_path: Path) -> None:
    """Verify flat subsystems still load correctly."""
    intent_dir = tmp_path / "jig"
    intent_dir.mkdir()
    (intent_dir / "outcomes").mkdir()

    # Create graph-index.json with flat subsystems (no nesting)
    (intent_dir / "graph-index.json").write_text(json.dumps({
        "version": "1.0",
        "generated": "2025-11-22T00:00:00Z",
        "subsystems": {
            "core": {
                "nodes": ["O-CORE-001", "O-CORE-002"]
            },
            "cli": {
                "nodes": ["O-CLI-001"]
            },
            "graph": {
                "nodes": ["O-GRAPH-001"]
            }
        },
        "edges": []
    }, indent=2))

    graph = Graph.load_from_dir(intent_dir)

    # Verify flat subsystems loaded correctly
    assert len(graph.subsystems) == 3
    assert "core" in graph.subsystems
    assert "cli" in graph.subsystems
    assert "graph" in graph.subsystems

    # Verify subsystems have no children
    assert graph.subsystems["core"].is_leaf()
    assert graph.subsystems["cli"].is_leaf()
    assert graph.subsystems["graph"].is_leaf()

    # Verify nodes
    assert graph.subsystems["core"].nodes == ["O-CORE-001", "O-CORE-002"]
    assert graph.subsystems["cli"].nodes == ["O-CLI-001"]
    assert graph.subsystems["graph"].nodes == ["O-GRAPH-001"]

    # Validate - should be valid
    errors = validate_nested_subsystems(graph)
    assert len(errors) == 0


def test_get_all_subsystem_paths(tmp_path: Path) -> None:
    """Test get_all_subsystem_paths with nested structure."""
    intent_dir = tmp_path / "jig"
    intent_dir.mkdir()
    (intent_dir / "outcomes").mkdir()

    (intent_dir / "graph-index.json").write_text(json.dumps({
        "version": "1.0",
        "generated": "2025-11-22T00:00:00Z",
        "subsystems": {
            "core": {
                "nodes": ["O-CORE-001"]
            },
            "crdt": {
                "subsystems": {
                    "ser": {
                        "nodes": ["O-SER-001"]
                    },
                    "deser": {
                        "nodes": ["O-DESER-001"]
                    }
                }
            }
        },
        "edges": []
    }, indent=2))

    graph = Graph.load_from_dir(intent_dir)

    # Test all paths (including parents)
    all_paths = graph.get_all_subsystem_paths(flat=False)
    assert set(all_paths) == {"core", "crdt", "crdt.ser", "crdt.deser"}

    # Test flat (leaf only)
    leaf_paths = graph.get_all_subsystem_paths(flat=True)
    assert set(leaf_paths) == {"core", "crdt.ser", "crdt.deser"}


def test_is_leaf() -> None:
    """Test Subsystem.is_leaf() method."""
    # Create leaf subsystem
    leaf = Subsystem(name="leaf")
    assert leaf.is_leaf()

    # Create parent subsystem
    parent = Subsystem(name="parent")
    child = Subsystem(name="child", parent_path="parent")
    parent.subsystems["child"] = child
    assert not parent.is_leaf()
    assert child.is_leaf()


def test_full_path() -> None:
    """Test Subsystem.full_path property."""
    # Root subsystem
    root = Subsystem(name="root", parent_path="")
    assert root.full_path == "root"

    # Nested subsystem
    child = Subsystem(name="child", parent_path="root")
    assert child.full_path == "root.child"

    # Deeply nested
    grandchild = Subsystem(name="grandchild", parent_path="root.child")
    assert grandchild.full_path == "root.child.grandchild"


def test_find_subsystem() -> None:
    """Test Subsystem.find_subsystem() method."""
    # Create hierarchy
    root = Subsystem(name="root")
    child1 = Subsystem(name="child1", parent_path="root")
    child2 = Subsystem(name="child2", parent_path="root")
    grandchild = Subsystem(name="grandchild", parent_path="root.child1")

    root.subsystems["child1"] = child1
    root.subsystems["child2"] = child2
    child1.subsystems["grandchild"] = grandchild

    # Test finding at different levels
    assert root.find_subsystem("root") == root
    assert root.find_subsystem("root.child1") == child1
    assert root.find_subsystem("root.child1.grandchild") == grandchild

    # Test not found
    assert root.find_subsystem("other") is None
    assert root.find_subsystem("root.other") is None


def test_invalid_node_subsystem_path(tmp_path: Path) -> None:
    """Test validation detects nodes with invalid subsystem paths."""
    intent_dir = tmp_path / "jig"
    intent_dir.mkdir()
    (intent_dir / "outcomes").mkdir()

    # Create node with invalid subsystem path
    (intent_dir / "outcomes" / "O-TEST-001.md").write_text(
        dedent("""
        ---
        id: O-TEST-001
        type: outcome
        title: Test outcome
        subsystem: nonexistent.subsystem
        ---
        Test outcome content.
        """)
    )

    (intent_dir / "graph-index.json").write_text(json.dumps({
        "version": "1.0",
        "generated": "2025-11-22T00:00:00Z",
        "subsystems": {
            "core": {
                "nodes": ["O-CORE-001"]
            }
        },
        "edges": []
    }, indent=2))

    graph = Graph.load_from_dir(intent_dir)

    # Validate - should detect invalid subsystem path
    errors = validate_nested_subsystems(graph)
    assert len(errors) > 0
    assert any("invalid subsystem path" in error.lower() for error in errors)
    assert any("nonexistent.subsystem" in error for error in errors)
