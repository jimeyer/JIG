"""Tests for intent graph generator."""

import json
from pathlib import Path

import pytest

import jig
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
specifications: [S-001, S-002]
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
    assert metadata["_meta"]["version"] == "2.0"
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
    assert outcome_nodes[0]["specifications"] == ["S-001", "S-002"]

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


class TestIntentGraphHashing:
    """Tests for S-050: Graph Schema Hash Fields."""

    @jig.verifies("S-050")
    def test_spec_nodes_have_jig_hash(self, temp_project):
        """Specification nodes have jig_hash field."""
        output_path = temp_project / "jig" / "generated" / "intent-graph.ndjson"

        generate_intent_graph(
            project_root=temp_project,
            output_path=output_path,
            include_timestamp=False,
        )

        lines = output_path.read_text().strip().split("\n")
        spec_nodes = [
            json.loads(line)
            for line in lines[1:]
            if '"type": "specification"' in line
        ]

        assert len(spec_nodes) == 2
        for node in spec_nodes:
            assert "jig_hash" in node
            assert len(node["jig_hash"]) == 12
            assert all(c in "0123456789abcdef" for c in node["jig_hash"])

    @jig.verifies("S-050")
    def test_outcome_nodes_have_jig_hash(self, temp_project):
        """Outcome nodes have jig_hash field."""
        output_path = temp_project / "jig" / "generated" / "intent-graph.ndjson"

        generate_intent_graph(
            project_root=temp_project,
            output_path=output_path,
            include_timestamp=False,
        )

        lines = output_path.read_text().strip().split("\n")
        outcome_nodes = [
            json.loads(line) for line in lines[1:] if '"type": "outcome"' in line
        ]

        assert len(outcome_nodes) == 1
        for node in outcome_nodes:
            assert "jig_hash" in node
            assert len(node["jig_hash"]) == 12
            assert all(c in "0123456789abcdef" for c in node["jig_hash"])

    @jig.verifies("S-050")
    def test_brick_nodes_have_jig_hash(self, temp_project):
        """Brick nodes have jig_hash field."""
        output_path = temp_project / "jig" / "generated" / "intent-graph.ndjson"

        generate_intent_graph(
            project_root=temp_project,
            output_path=output_path,
            include_timestamp=False,
        )

        lines = output_path.read_text().strip().split("\n")
        brick_nodes = [
            json.loads(line) for line in lines[1:] if '"type": "brick"' in line
        ]

        assert len(brick_nodes) == 1
        for node in brick_nodes:
            assert "jig_hash" in node
            assert len(node["jig_hash"]) == 12
            assert all(c in "0123456789abcdef" for c in node["jig_hash"])

    @jig.verifies("S-050")
    def test_spec_hash_changes_when_content_changes(self, temp_project):
        """Hash changes when specification content changes."""
        output_path = temp_project / "jig" / "generated" / "intent-graph.ndjson"

        # Generate first graph
        generate_intent_graph(
            project_root=temp_project,
            output_path=output_path,
            include_timestamp=False,
        )

        lines = output_path.read_text().strip().split("\n")
        spec_nodes_before = {
            json.loads(line)["id"]: json.loads(line)["jig_hash"]
            for line in lines[1:]
            if '"type": "specification"' in line
        }

        # Modify S-001 content
        spec_file = temp_project / "jig" / "specifications" / "S-001.md"
        spec_file.write_text(
            """---
id: S-001
type: specification
---

# Test Spec 1 MODIFIED

Different content now.
"""
        )

        # Generate again
        generate_intent_graph(
            project_root=temp_project,
            output_path=output_path,
            include_timestamp=False,
        )

        lines = output_path.read_text().strip().split("\n")
        spec_nodes_after = {
            json.loads(line)["id"]: json.loads(line)["jig_hash"]
            for line in lines[1:]
            if '"type": "specification"' in line
        }

        # S-001 hash should change, S-002 should stay same
        assert spec_nodes_before["S-001"] != spec_nodes_after["S-001"]
        assert spec_nodes_before["S-002"] == spec_nodes_after["S-002"]

    @jig.verifies("S-050")
    def test_hash_deterministic_across_runs(self, temp_project):
        """Same content produces same hash across runs."""
        output_path1 = temp_project / "jig" / "generated" / "intent-graph-1.ndjson"
        output_path2 = temp_project / "jig" / "generated" / "intent-graph-2.ndjson"

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

        # Parse hashes from both
        lines1 = output_path1.read_text().strip().split("\n")
        lines2 = output_path2.read_text().strip().split("\n")

        hashes1 = {
            json.loads(line).get("id"): json.loads(line).get("jig_hash")
            for line in lines1[1:]
            if "jig_hash" in line
        }
        hashes2 = {
            json.loads(line).get("id"): json.loads(line).get("jig_hash")
            for line in lines2[1:]
            if "jig_hash" in line
        }

        assert hashes1 == hashes2


class TestIntentGraphGitBlob:
    """Tests for S-049: Git Blob Optimization in intent graph."""

    @jig.verifies("S-049")
    def test_git_blob_optional_on_spec_nodes(self, temp_project):
        """Specification nodes may have optional git_blob field."""
        output_path = temp_project / "jig" / "generated" / "intent-graph.ndjson"

        generate_intent_graph(
            project_root=temp_project,
            output_path=output_path,
            include_timestamp=False,
        )

        lines = output_path.read_text().strip().split("\n")
        spec_nodes = [
            json.loads(line)
            for line in lines[1:]
            if '"type": "specification"' in line
        ]

        # git_blob is optional - may or may not be present depending on git context
        # If present, should be 12 hex chars
        for node in spec_nodes:
            if "git_blob" in node:
                assert len(node["git_blob"]) == 12
                assert all(c in "0123456789abcdef" for c in node["git_blob"])

    @jig.verifies("S-049")
    def test_git_blob_optional_on_outcome_nodes(self, temp_project):
        """Outcome nodes may have optional git_blob field."""
        output_path = temp_project / "jig" / "generated" / "intent-graph.ndjson"

        generate_intent_graph(
            project_root=temp_project,
            output_path=output_path,
            include_timestamp=False,
        )

        lines = output_path.read_text().strip().split("\n")
        outcome_nodes = [
            json.loads(line)
            for line in lines[1:]
            if '"type": "outcome"' in line
        ]

        # git_blob is optional - may or may not be present depending on git context
        for node in outcome_nodes:
            if "git_blob" in node:
                assert len(node["git_blob"]) == 12
                assert all(c in "0123456789abcdef" for c in node["git_blob"])

    @jig.verifies("S-049")
    def test_git_blob_optional_on_brick_nodes(self, temp_project):
        """Brick nodes may have optional git_blob field."""
        output_path = temp_project / "jig" / "generated" / "intent-graph.ndjson"

        generate_intent_graph(
            project_root=temp_project,
            output_path=output_path,
            include_timestamp=False,
        )

        lines = output_path.read_text().strip().split("\n")
        brick_nodes = [
            json.loads(line)
            for line in lines[1:]
            if '"type": "brick"' in line
        ]

        # git_blob is optional - may or may not be present depending on git context
        for node in brick_nodes:
            if "git_blob" in node:
                assert len(node["git_blob"]) == 12
                assert all(c in "0123456789abcdef" for c in node["git_blob"])

    @jig.verifies("S-049")
    def test_git_blob_deterministic_across_runs(self, temp_project):
        """Same file produces same git_blob across runs."""
        output_path1 = temp_project / "jig" / "generated" / "intent-graph-1.ndjson"
        output_path2 = temp_project / "jig" / "generated" / "intent-graph-2.ndjson"

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

        lines1 = output_path1.read_text().strip().split("\n")
        lines2 = output_path2.read_text().strip().split("\n")

        # Collect git_blobs from both runs
        blobs1 = {
            json.loads(line).get("id"): json.loads(line).get("git_blob")
            for line in lines1[1:]
            if "git_blob" in line
        }
        blobs2 = {
            json.loads(line).get("id"): json.loads(line).get("git_blob")
            for line in lines2[1:]
            if "git_blob" in line
        }

        # If git_blob is present, it should be the same across runs
        assert blobs1 == blobs2


class TestIntentGraphV2Schema:
    """Tests for V2 schema field names (S-028, S-084, S-085)."""

    @pytest.fixture
    def v2_project(self, tmp_path):
        """Create a project with Charter, Goals, Architecture, Outcomes, and Specs."""
        project_root = tmp_path / "v2_project"
        project_root.mkdir()

        # Create Charter.md with goals field (V2 schema)
        charter_dir = project_root / "jig"
        charter_dir.mkdir(parents=True)

        (charter_dir / "Charter.md").write_text(
            """---
id: Charter
goals: [G-001, G-002]
---

# Test Charter

## Goals

### G-001: First Goal

First goal description.

### G-002: Second Goal

Second goal description.
"""
        )

        # Create architecture directory with A-001.md (V2 schema)
        arch_dir = project_root / "jig" / "architecture"
        arch_dir.mkdir(parents=True)

        (arch_dir / "A-001.md").write_text(
            """---
id: A-001
title: Test Architecture
type: architecture
goals: [G-001]
specifications: [S-001, S-002]
---

# Test Architecture

Architecture content.
"""
        )

        # Create specifications directory
        spec_dir = project_root / "jig" / "specifications"
        spec_dir.mkdir(parents=True)

        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
type: specification
---

# Spec 1
"""
        )

        (spec_dir / "S-002.md").write_text(
            """---
id: S-002
type: specification
---

# Spec 2
"""
        )

        # Create outcomes directory with V2 schema fields
        outcome_dir = project_root / "jig" / "outcomes"
        outcome_dir.mkdir(parents=True)

        (outcome_dir / "O-001.md").write_text(
            """---
id: O-001
type: outcome
goals: [G-002]
specifications: [S-001]
---

# Test Outcome

Outcome content.
"""
        )

        # Create bricks.yaml
        (project_root / "jig" / "bricks.yaml").write_text(
            """bricks:
  - id: B-001
    name: Test Brick
    units:
      - M-test.module
"""
        )

        return project_root

    @jig.verifies("S-028")
    def test_charter_node_uses_goals_field(self, v2_project):
        """Charter nodes use 'goals' field instead of 'defines_goals' (V2 schema)."""
        output_path = v2_project / "jig" / "generated" / "intent-graph.ndjson"

        generate_intent_graph(
            project_root=v2_project,
            output_path=output_path,
            include_timestamp=False,
        )

        lines = output_path.read_text().strip().split("\n")
        charter_nodes = [
            json.loads(line)
            for line in lines[1:]
            if '"type": "charter"' in line
        ]

        assert len(charter_nodes) == 1
        charter = charter_nodes[0]
        assert charter["id"] == "Charter"
        assert charter["type"] == "charter"
        # V2 schema: uses 'goals', not 'defines_goals'
        assert "goals" in charter
        assert charter["goals"] == ["G-001", "G-002"]
        assert "defines_goals" not in charter

    @jig.verifies("S-028", "S-082")
    def test_architecture_node_uses_v2_field_names(self, v2_project):
        """Architecture nodes use V2 field names: goals, specifications, no status."""
        output_path = v2_project / "jig" / "generated" / "intent-graph.ndjson"

        generate_intent_graph(
            project_root=v2_project,
            output_path=output_path,
            include_timestamp=False,
        )

        lines = output_path.read_text().strip().split("\n")
        arch_nodes = [
            json.loads(line)
            for line in lines[1:]
            if '"type": "architecture"' in line
        ]

        assert len(arch_nodes) == 1
        arch = arch_nodes[0]
        assert arch["id"] == "A-001"
        # V2 schema: 'goals' instead of 'supports_goals'
        assert "goals" in arch
        assert arch["goals"] == ["G-001"]
        assert "supports_goals" not in arch
        # V2 schema: 'specifications' instead of 'constrains'
        assert "specifications" in arch
        assert arch["specifications"] == ["S-001", "S-002"]
        assert "constrains" not in arch
        # V2 schema: no 'status' field
        assert "status" not in arch

    @jig.verifies("S-028")
    def test_outcome_node_uses_v2_field_names(self, v2_project):
        """Outcome nodes use V2 field names: goals, specifications."""
        output_path = v2_project / "jig" / "generated" / "intent-graph.ndjson"

        generate_intent_graph(
            project_root=v2_project,
            output_path=output_path,
            include_timestamp=False,
        )

        lines = output_path.read_text().strip().split("\n")
        outcome_nodes = [
            json.loads(line)
            for line in lines[1:]
            if '"type": "outcome"' in line
        ]

        assert len(outcome_nodes) == 1
        outcome = outcome_nodes[0]
        assert outcome["id"] == "O-001"
        # V2 schema: 'goals' instead of 'supports_goals'
        assert "goals" in outcome
        assert outcome["goals"] == ["G-002"]
        assert "supports_goals" not in outcome
        # V2 schema: 'specifications' instead of 'specifies'
        assert "specifications" in outcome
        assert outcome["specifications"] == ["S-001"]
        assert "specifies" not in outcome

    @jig.verifies("S-084")
    def test_supports_goal_edges_generated(self, v2_project):
        """supports_goal edges generated from goals field in A/O nodes."""
        output_path = v2_project / "jig" / "generated" / "intent-graph.ndjson"

        generate_intent_graph(
            project_root=v2_project,
            output_path=output_path,
            include_timestamp=False,
        )

        lines = output_path.read_text().strip().split("\n")
        edges = [
            json.loads(line)
            for line in lines[1:]
            if "source" in line and "target" in line
        ]

        supports_goal_edges = [e for e in edges if e["type"] == "supports_goal"]

        # A-001 has goals: [G-001], so one A->G edge
        # O-001 has goals: [G-002], so one O->G edge
        assert len(supports_goal_edges) == 2
        assert {"source": "A-001", "target": "G-001", "type": "supports_goal"} in supports_goal_edges
        assert {"source": "O-001", "target": "G-002", "type": "supports_goal"} in supports_goal_edges

    @jig.verifies("S-085")
    def test_specifications_edges_replace_constrains(self, v2_project):
        """Edge type 'specifications' replaces 'constrains' (V2 schema)."""
        output_path = v2_project / "jig" / "generated" / "intent-graph.ndjson"

        generate_intent_graph(
            project_root=v2_project,
            output_path=output_path,
            include_timestamp=False,
        )

        lines = output_path.read_text().strip().split("\n")
        edges = [
            json.loads(line)
            for line in lines[1:]
            if "source" in line and "target" in line
        ]

        # A-001 has specifications: [S-001, S-002]
        # V2 schema: edge type is 'specifications', not 'constrains'
        spec_edges = [e for e in edges if e["type"] == "specifications"]
        constrains_edges = [e for e in edges if e["type"] == "constrains"]

        assert len(constrains_edges) == 0, "V2 schema should not have 'constrains' edge type"
        assert len(spec_edges) == 2
        assert {"source": "A-001", "target": "S-001", "type": "specifications"} in spec_edges
        assert {"source": "A-001", "target": "S-002", "type": "specifications"} in spec_edges

    @jig.verifies("S-083")
    def test_defines_goal_edges_use_goals_field(self, v2_project):
        """defines_goal edges use 'goals' field from Charter (V2 schema)."""
        output_path = v2_project / "jig" / "generated" / "intent-graph.ndjson"

        generate_intent_graph(
            project_root=v2_project,
            output_path=output_path,
            include_timestamp=False,
        )

        lines = output_path.read_text().strip().split("\n")
        edges = [
            json.loads(line)
            for line in lines[1:]
            if "source" in line and "target" in line
        ]

        defines_goal_edges = [e for e in edges if e["type"] == "defines_goal"]

        # Charter has goals: [G-001, G-002]
        assert len(defines_goal_edges) == 2
        assert {"source": "Charter", "target": "G-001", "type": "defines_goal"} in defines_goal_edges
        assert {"source": "Charter", "target": "G-002", "type": "defines_goal"} in defines_goal_edges
