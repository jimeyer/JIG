"""
Tests for brick layer constraint validation (S-038).
"""

import json
import tempfile
from pathlib import Path

import jig
from jig.validation.bricks import validate_brick_layer_constraints
from jig.validation.models import ValidationResult


def _create_implementation_graph(graph_file: Path, nodes: list[dict], edges: list[dict]) -> None:
    """Helper to create test implementation graph with nodes and edges."""
    with graph_file.open("w") as f:
        for node in nodes:
            f.write(json.dumps(node) + "\n")
        for edge in edges:
            f.write(json.dumps(edge) + "\n")


@jig.verifies("S-038")
def test_validate_layer_constraints_valid_layer1_to_layer0():
    """Valid: Layer 1 brick depends on layer 0 brick."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create implementation graph with function call
        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-core.utils.helper", "type": "function"},
                {"id": "F-api.handler.process", "type": "function"},
            ],
            edges=[
                {"type": "calls", "source": "F-api.handler.process", "target": "F-core.utils.helper"},
            ],
        )

        # Create bricks: B-core (layer 0), B-api (layer 1)
        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-core
  name: Core
  layer: 0
  units:
    - F-core.utils.helper

- id: B-api
  name: API
  layer: 1
  units:
    - F-api.handler.process
"""
        )

        result = validate_brick_layer_constraints(bricks_file, impl_graph)
        assert result.passed, f"Expected validation to pass but got errors: {[e.message for e in result.errors]}"
        assert len(result.errors) == 0


@jig.verifies("S-038")
def test_validate_layer_constraints_valid_layer2_to_layer1():
    """Valid: Layer 2 brick depends on layer 1 brick."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-api.handler.process", "type": "function"},
                {"id": "F-cli.main.run", "type": "function"},
            ],
            edges=[
                {"type": "calls", "source": "F-cli.main.run", "target": "F-api.handler.process"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-api
  name: API
  layer: 1
  units:
    - F-api.handler.process

- id: B-cli
  name: CLI
  layer: 2
  units:
    - F-cli.main.run
"""
        )

        result = validate_brick_layer_constraints(bricks_file, impl_graph)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-038")
def test_validate_layer_constraints_valid_layer2_to_layer0():
    """Valid: Layer 2 brick depends on layer 0 brick (skip layer 1)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-core.utils.helper", "type": "function"},
                {"id": "F-cli.main.run", "type": "function"},
            ],
            edges=[
                {"type": "calls", "source": "F-cli.main.run", "target": "F-core.utils.helper"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-core
  name: Core
  layer: 0
  units:
    - F-core.utils.helper

- id: B-cli
  name: CLI
  layer: 2
  units:
    - F-cli.main.run
"""
        )

        result = validate_brick_layer_constraints(bricks_file, impl_graph)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-038")
def test_validate_layer_constraints_valid_layer0_to_layer0():
    """Valid: Layer 0 brick depends on another layer 0 brick."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-core.utils.helper", "type": "function"},
                {"id": "F-core.data.load", "type": "function"},
            ],
            edges=[
                {"type": "calls", "source": "F-core.data.load", "target": "F-core.utils.helper"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-core-utils
  name: Core Utils
  layer: 0
  units:
    - F-core.utils.helper

- id: B-core-data
  name: Core Data
  layer: 0
  units:
    - F-core.data.load
"""
        )

        result = validate_brick_layer_constraints(bricks_file, impl_graph)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-038")
def test_validate_layer_constraints_invalid_layer1_to_layer2():
    """Invalid: Layer 1 brick depends on layer 2 brick (upward dependency)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-cli.main.run", "type": "function"},
                {"id": "F-api.handler.process", "type": "function"},
            ],
            edges=[
                {"type": "calls", "source": "F-api.handler.process", "target": "F-cli.main.run"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-api
  name: API
  layer: 1
  units:
    - F-api.handler.process

- id: B-cli
  name: CLI
  layer: 2
  units:
    - F-cli.main.run
"""
        )

        result = validate_brick_layer_constraints(bricks_file, impl_graph)
        assert not result.passed
        assert len(result.errors) >= 1
        error = result.errors[0]
        assert "B-api" in error.message
        assert "B-cli" in error.message
        assert "layer 1" in error.message.lower() or "layer: 1" in error.message
        assert "layer 2" in error.message.lower() or "layer: 2" in error.message
        assert "F-api.handler.process" in error.message
        assert "F-cli.main.run" in error.message


@jig.verifies("S-038")
def test_validate_layer_constraints_invalid_layer0_to_layer1():
    """Invalid: Layer 0 brick depends on layer 1 brick (foundation depending on higher layer)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-api.handler.process", "type": "function"},
                {"id": "F-core.utils.helper", "type": "function"},
            ],
            edges=[
                {"type": "calls", "source": "F-core.utils.helper", "target": "F-api.handler.process"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-core
  name: Core
  layer: 0
  units:
    - F-core.utils.helper

- id: B-api
  name: API
  layer: 1
  units:
    - F-api.handler.process
"""
        )

        result = validate_brick_layer_constraints(bricks_file, impl_graph)
        assert not result.passed
        assert len(result.errors) >= 1
        error = result.errors[0]
        assert "B-core" in error.message
        assert "B-api" in error.message
        assert "layer 0" in error.message.lower() or "layer: 0" in error.message


@jig.verifies("S-038")
def test_validate_layer_constraints_invalid_layer1_to_layer1():
    """Invalid: Layer 1 brick depends on another layer 1 brick (same-layer dependency, only allowed at layer 0)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-api.handler.process", "type": "function"},
                {"id": "F-api.auth.verify", "type": "function"},
            ],
            edges=[
                {"type": "calls", "source": "F-api.handler.process", "target": "F-api.auth.verify"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-api-handler
  name: API Handler
  layer: 1
  units:
    - F-api.handler.process

- id: B-api-auth
  name: API Auth
  layer: 1
  units:
    - F-api.auth.verify
"""
        )

        result = validate_brick_layer_constraints(bricks_file, impl_graph)
        assert not result.passed
        assert len(result.errors) >= 1
        error = result.errors[0]
        assert "same layer" in error.message.lower() or "layer 1" in error.message.lower()


@jig.verifies("S-038")
def test_validate_layer_constraints_invalid_layer2_to_layer2():
    """Invalid: Layer 2 brick depends on another layer 2 brick (same-layer dependency, only allowed at layer 0)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-cli.main.run", "type": "function"},
                {"id": "F-cli.config.load", "type": "function"},
            ],
            edges=[
                {"type": "calls", "source": "F-cli.main.run", "target": "F-cli.config.load"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-cli-main
  name: CLI Main
  layer: 2
  units:
    - F-cli.main.run

- id: B-cli-config
  name: CLI Config
  layer: 2
  units:
    - F-cli.config.load
"""
        )

        result = validate_brick_layer_constraints(bricks_file, impl_graph)
        assert not result.passed
        assert len(result.errors) >= 1


@jig.verifies("S-038")
def test_validate_layer_constraints_multiple_violations():
    """Multiple layer constraint violations reported."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-core.utils.helper", "type": "function"},
                {"id": "F-api.handler.process", "type": "function"},
                {"id": "F-cli.main.run", "type": "function"},
            ],
            edges=[
                # Violation 1: core (L0) → api (L1)
                {"type": "calls", "source": "F-core.utils.helper", "target": "F-api.handler.process"},
                # Violation 2: api (L1) → cli (L2)
                {"type": "calls", "source": "F-api.handler.process", "target": "F-cli.main.run"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-core
  name: Core
  layer: 0
  units:
    - F-core.utils.helper

- id: B-api
  name: API
  layer: 1
  units:
    - F-api.handler.process

- id: B-cli
  name: CLI
  layer: 2
  units:
    - F-cli.main.run
"""
        )

        result = validate_brick_layer_constraints(bricks_file, impl_graph)
        assert not result.passed
        assert len(result.errors) == 2


@jig.verifies("S-038")
def test_validate_layer_constraints_no_dependencies():
    """Bricks with no dependencies pass validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-core.utils.helper", "type": "function"},
                {"id": "F-api.handler.process", "type": "function"},
            ],
            edges=[],  # No edges, no dependencies
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-core
  name: Core
  layer: 0
  units:
    - F-core.utils.helper

- id: B-api
  name: API
  layer: 1
  units:
    - F-api.handler.process
"""
        )

        result = validate_brick_layer_constraints(bricks_file, impl_graph)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-038")
def test_validate_layer_constraints_self_dependency_allowed():
    """Function calling another function in same brick is allowed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-core.utils.helper", "type": "function"},
                {"id": "F-core.utils.internal", "type": "function"},
            ],
            edges=[
                # Same brick dependency (internal call)
                {"type": "calls", "source": "F-core.utils.helper", "target": "F-core.utils.internal"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-core
  name: Core
  layer: 0
  units:
    - F-core.utils.helper
    - F-core.utils.internal
"""
        )

        result = validate_brick_layer_constraints(bricks_file, impl_graph)
        assert result.passed
        assert len(result.errors) == 0
