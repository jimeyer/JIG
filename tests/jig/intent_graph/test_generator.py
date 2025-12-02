"""Tests for intent graph generator."""

import json
from pathlib import Path

import pytest

from jig.intent_graph.generator import generate_intent_graph


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure with spec/outcome/brick files."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()

    # Create specifications directory with sample specs
    spec_dir = project_root / "jig" / "specifications"
    spec_dir.mkdir(parents=True)

    (spec_dir / "S-001.md").write_text(
        """---
id: S-001
type: specification
---

# Test Spec 1

Test specification content.
"""
    )

    (spec_dir / "S-002.md").write_text(
        """---
id: S-002
type: specification
---

# Test Spec 2

Another test specification.
"""
    )

    # Create outcomes directory with sample outcomes
    outcome_dir = project_root / "jig" / "outcomes"
    outcome_dir.mkdir(parents=True)

    (outcome_dir / "O-001.md").write_text(
        """---
id: O-001
type: outcome
specifies: [S-001, S-002]
---

# Test Outcome 1

Test outcome content.
"""
    )

    # Create bricks.yaml
    (project_root / "jig" / "bricks.yaml").write_text(
        """bricks:
  - id: B-001
    name: Test Brick
    units:
      - M-test.module
      - C-test.Class
      - F-test.function
"""
    )

    return project_root


def test_generate_intent_graph_basic(temp_project):
    """Test basic intent graph generation."""
    output_path = temp_project / "jig" / "generated" / "intent-graph.ndjson"

    result_path, node_count, edge_count = generate_intent_graph(
        project_root=temp_project,
        output_path=output_path,
        include_timestamp=False,
    )

    assert result_path == output_path
    assert output_path.exists()
    assert node_count == 4  # 2 specs + 1 outcome + 1 brick
    assert edge_count == 2  # 2 specifies edges from O-001

    # Read and parse the generated file
    lines = output_path.read_text().strip().split("\n")

    # First line: metadata
    metadata = json.loads(lines[0])
    assert "_meta" in metadata
    assert metadata["_meta"]["version"] == "1.0"
    assert metadata["_meta"]["spec_count"] == 2
    assert metadata["_meta"]["outcome_count"] == 1
    assert metadata["_meta"]["brick_count"] == 1
    assert "generated" not in metadata["_meta"]  # timestamp excluded

    # Parse all nodes and edges
    nodes = []
    edges = []
    for line in lines[1:]:
        obj = json.loads(line)
        if "source" in obj and "target" in obj:
            edges.append(obj)
        else:
            nodes.append(obj)

    # Check spec nodes
    spec_nodes = [n for n in nodes if n["type"] == "specification"]
    assert len(spec_nodes) == 2
    assert spec_nodes[0]["id"] == "S-001"
    assert spec_nodes[0]["file"] == "jig/specifications/S-001.md"
    assert spec_nodes[1]["id"] == "S-002"

    # Check outcome nodes
    outcome_nodes = [n for n in nodes if n["type"] == "outcome"]
    assert len(outcome_nodes) == 1
    assert outcome_nodes[0]["id"] == "O-001"
    assert outcome_nodes[0]["file"] == "jig/outcomes/O-001.md"
    assert outcome_nodes[0]["specifies"] == ["S-001", "S-002"]

    # Check brick nodes
    brick_nodes = [n for n in nodes if n["type"] == "brick"]
    assert len(brick_nodes) == 1
    assert brick_nodes[0]["id"] == "B-001"
    assert brick_nodes[0]["name"] == "Test Brick"
    assert brick_nodes[0]["file"] == "jig/bricks.yaml"
    assert brick_nodes[0]["units"] == ["M-test.module", "C-test.Class", "F-test.function"]

    # Check edges (O-001 → S-001, O-001 → S-002)
    assert len(edges) == 2
    assert {"source": "O-001", "target": "S-001", "type": "specifies"} in edges
    assert {"source": "O-001", "target": "S-002", "type": "specifies"} in edges


def test_generate_intent_graph_with_timestamp(temp_project):
    """Test intent graph generation includes timestamp when requested."""
    output_path = temp_project / "jig" / "generated" / "intent-graph.ndjson"

    generate_intent_graph(
        project_root=temp_project,
        output_path=output_path,
        include_timestamp=True,
    )

    lines = output_path.read_text().strip().split("\n")
    metadata = json.loads(lines[0])

    assert "generated" in metadata["_meta"]
    assert metadata["_meta"]["generated"].endswith("+00:00")  # ISO format with UTC


def test_generate_intent_graph_no_outcomes(temp_project):
    """Test intent graph generation when outcomes directory doesn't exist."""
    # Remove outcomes directory
    outcome_dir = temp_project / "jig" / "outcomes"
    for f in outcome_dir.glob("*"):
        f.unlink()
    outcome_dir.rmdir()

    output_path = temp_project / "jig" / "generated" / "intent-graph.ndjson"

    generate_intent_graph(
        project_root=temp_project,
        output_path=output_path,
        include_timestamp=False,
    )

    lines = output_path.read_text().strip().split("\n")
    metadata = json.loads(lines[0])

    assert metadata["_meta"]["spec_count"] == 2
    assert metadata["_meta"]["outcome_count"] == 0
    assert metadata["_meta"]["brick_count"] == 1

    # Parse nodes
    nodes = []
    for line in lines[1:]:
        obj = json.loads(line)
        if "source" not in obj:  # not an edge
            nodes.append(obj)

    outcome_nodes = [n for n in nodes if n["type"] == "outcome"]
    assert len(outcome_nodes) == 0


def test_generate_intent_graph_missing_bricks_file(temp_project):
    """Test that missing bricks.yaml raises FileNotFoundError."""
    # Remove bricks.yaml
    (temp_project / "jig" / "bricks.yaml").unlink()

    output_path = temp_project / "jig" / "generated" / "intent-graph.ndjson"

    with pytest.raises(FileNotFoundError, match="Bricks file not found"):
        generate_intent_graph(
            project_root=temp_project,
            output_path=output_path,
        )


def test_generate_intent_graph_invalid_bricks_yaml(temp_project):
    """Test that invalid bricks.yaml raises ValueError."""
    # Write invalid YAML
    (temp_project / "jig" / "bricks.yaml").write_text("invalid: yaml: content:")

    output_path = temp_project / "jig" / "generated" / "intent-graph.ndjson"

    with pytest.raises(ValueError, match="Failed to parse bricks.yaml"):
        generate_intent_graph(
            project_root=temp_project,
            output_path=output_path,
        )


def test_generate_intent_graph_deterministic_output(temp_project):
    """Test that output is deterministic (same input = same output)."""
    output_path1 = temp_project / "jig" / "generated" / "intent-graph-1.ndjson"
    output_path2 = temp_project / "jig" / "generated" / "intent-graph-2.ndjson"

    # Generate twice
    generate_intent_graph(
        project_root=temp_project,
        output_path=output_path1,
        include_timestamp=False,
    )
    generate_intent_graph(
        project_root=temp_project,
        output_path=output_path2,
        include_timestamp=False,
    )

    # Outputs should be identical
    assert output_path1.read_text() == output_path2.read_text()


def test_generate_intent_graph_sorted_output(temp_project):
    """Test that nodes and edges are sorted for deterministic output."""
    output_path = temp_project / "jig" / "generated" / "intent-graph.ndjson"

    generate_intent_graph(
        project_root=temp_project,
        output_path=output_path,
        include_timestamp=False,
    )

    lines = output_path.read_text().strip().split("\n")

    # Parse nodes (skip metadata line)
    spec_nodes = []
    outcome_nodes = []
    brick_nodes = []
    edges = []

    for line in lines[1:]:
        obj = json.loads(line)
        if "source" in obj:
            edges.append(obj)
        elif obj.get("type") == "specification":
            spec_nodes.append(obj)
        elif obj.get("type") == "outcome":
            outcome_nodes.append(obj)
        elif obj.get("type") == "brick":
            brick_nodes.append(obj)

    # Specs should be sorted by ID
    spec_ids = [n["id"] for n in spec_nodes]
    assert spec_ids == sorted(spec_ids)

    # Outcomes should be sorted by ID
    outcome_ids = [n["id"] for n in outcome_nodes]
    assert outcome_ids == sorted(outcome_ids)

    # Bricks should be sorted by ID
    brick_ids = [n["id"] for n in brick_nodes]
    assert brick_ids == sorted(brick_ids)

    # Edges should be sorted by (source, target, type)
    edge_tuples = [(e["source"], e["target"], e["type"]) for e in edges]
    assert edge_tuples == sorted(edge_tuples)
