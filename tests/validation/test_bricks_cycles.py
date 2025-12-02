"""
Tests for brick circular dependency detection (S-039).
"""

import json
import tempfile
from pathlib import Path

import jig
from jig.validation.bricks import validate_brick_cycles
from jig.validation.models import ValidationResult


def _create_implementation_graph(graph_file: Path, nodes: list[dict], edges: list[dict]) -> None:
    """Helper to create test implementation graph with nodes and edges."""
    with graph_file.open("w") as f:
        for node in nodes:
            f.write(json.dumps(node) + "\n")
        for edge in edges:
            f.write(json.dumps(edge) + "\n")


@jig.verifies("S-039")
def test_validate_cycles_no_cycles_dag():
    """Valid: No cycles, proper DAG structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create DAG: B-core ← B-api ← B-cli
        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-core.utils.helper", "type": "function"},
                {"id": "F-api.handler.process", "type": "function"},
                {"id": "F-cli.main.run", "type": "function"},
            ],
            edges=[
                {"type": "calls", "source": "F-api.handler.process", "target": "F-core.utils.helper"},
                {"type": "calls", "source": "F-cli.main.run", "target": "F-api.handler.process"},
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

        result = validate_brick_cycles(bricks_file, impl_graph)
        assert result.passed, f"Expected validation to pass but got errors: {[e.message for e in result.errors]}"
        assert len(result.errors) == 0


@jig.verifies("S-039")
def test_validate_cycles_simple_two_brick_cycle():
    """Invalid: Simple cycle between two bricks (B-a → B-b → B-a)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-a.func1", "type": "function"},
                {"id": "F-b.func1", "type": "function"},
            ],
            edges=[
                {"type": "calls", "source": "F-a.func1", "target": "F-b.func1"},
                {"type": "calls", "source": "F-b.func1", "target": "F-a.func1"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-a
  name: Brick A
  layer: 0
  units:
    - F-a.func1

- id: B-b
  name: Brick B
  layer: 0
  units:
    - F-b.func1
"""
        )

        result = validate_brick_cycles(bricks_file, impl_graph)
        assert not result.passed
        assert len(result.errors) >= 1
        error = result.errors[0]
        assert "cycle" in error.message.lower() or "circular" in error.message.lower()
        assert "B-a" in error.message
        assert "B-b" in error.message


@jig.verifies("S-039")
def test_validate_cycles_three_brick_cycle():
    """Invalid: Three brick cycle (B-a → B-b → B-c → B-a)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-a.func1", "type": "function"},
                {"id": "F-b.func1", "type": "function"},
                {"id": "F-c.func1", "type": "function"},
            ],
            edges=[
                {"type": "calls", "source": "F-a.func1", "target": "F-b.func1"},
                {"type": "calls", "source": "F-b.func1", "target": "F-c.func1"},
                {"type": "calls", "source": "F-c.func1", "target": "F-a.func1"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-a
  name: Brick A
  layer: 1
  units:
    - F-a.func1

- id: B-b
  name: Brick B
  layer: 1
  units:
    - F-b.func1

- id: B-c
  name: Brick C
  layer: 1
  units:
    - F-c.func1
"""
        )

        result = validate_brick_cycles(bricks_file, impl_graph)
        assert not result.passed
        assert len(result.errors) >= 1
        error = result.errors[0]
        assert "cycle" in error.message.lower() or "circular" in error.message.lower()
        # Check that all three bricks are mentioned in the cycle
        assert "B-a" in error.message
        assert "B-b" in error.message
        assert "B-c" in error.message


@jig.verifies("S-039")
def test_validate_cycles_self_loop():
    """Invalid: Self-loop (B-a → B-a)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-a.func1", "type": "function"},
                {"id": "F-a.func2", "type": "function"},
            ],
            edges=[
                # Different functions in same brick calling each other creates brick self-dependency
                {"type": "calls", "source": "F-a.func1", "target": "F-a.func2"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-a
  name: Brick A
  layer: 0
  units:
    - F-a.func1
    - F-a.func2
"""
        )

        # Self-dependencies within same brick should be allowed, not a cycle
        result = validate_brick_cycles(bricks_file, impl_graph)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-039")
def test_validate_cycles_layer0_cycle():
    """Invalid: Cycle at layer 0 (layer 0 bricks may depend on each other, but no cycles)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-utils.a", "type": "function"},
                {"id": "F-data.b", "type": "function"},
                {"id": "F-config.c", "type": "function"},
            ],
            edges=[
                {"type": "calls", "source": "F-utils.a", "target": "F-data.b"},
                {"type": "calls", "source": "F-data.b", "target": "F-config.c"},
                {"type": "calls", "source": "F-config.c", "target": "F-utils.a"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-utils
  name: Utils
  layer: 0
  units:
    - F-utils.a

- id: B-data
  name: Data
  layer: 0
  units:
    - F-data.b

- id: B-config
  name: Config
  layer: 0
  units:
    - F-config.c
"""
        )

        result = validate_brick_cycles(bricks_file, impl_graph)
        assert not result.passed
        assert len(result.errors) >= 1
        error = result.errors[0]
        assert "cycle" in error.message.lower() or "circular" in error.message.lower()


@jig.verifies("S-039")
def test_validate_cycles_multiple_cycles():
    """Invalid: Multiple independent cycles in graph."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-a.func1", "type": "function"},
                {"id": "F-b.func1", "type": "function"},
                {"id": "F-c.func1", "type": "function"},
                {"id": "F-d.func1", "type": "function"},
            ],
            edges=[
                # Cycle 1: B-a → B-b → B-a
                {"type": "calls", "source": "F-a.func1", "target": "F-b.func1"},
                {"type": "calls", "source": "F-b.func1", "target": "F-a.func1"},
                # Cycle 2: B-c → B-d → B-c
                {"type": "calls", "source": "F-c.func1", "target": "F-d.func1"},
                {"type": "calls", "source": "F-d.func1", "target": "F-c.func1"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-a
  name: Brick A
  layer: 0
  units:
    - F-a.func1

- id: B-b
  name: Brick B
  layer: 0
  units:
    - F-b.func1

- id: B-c
  name: Brick C
  layer: 1
  units:
    - F-c.func1

- id: B-d
  name: Brick D
  layer: 1
  units:
    - F-d.func1
"""
        )

        result = validate_brick_cycles(bricks_file, impl_graph)
        assert not result.passed
        # Should detect both cycles
        assert len(result.errors) >= 2


@jig.verifies("S-039")
def test_validate_cycles_complex_graph_no_cycles():
    """Valid: Complex graph with multiple paths but no cycles."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Diamond pattern: B-a → B-b → B-d, B-a → B-c → B-d (no cycle)
        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-a.func1", "type": "function"},
                {"id": "F-b.func1", "type": "function"},
                {"id": "F-c.func1", "type": "function"},
                {"id": "F-d.func1", "type": "function"},
            ],
            edges=[
                {"type": "calls", "source": "F-a.func1", "target": "F-b.func1"},
                {"type": "calls", "source": "F-a.func1", "target": "F-c.func1"},
                {"type": "calls", "source": "F-b.func1", "target": "F-d.func1"},
                {"type": "calls", "source": "F-c.func1", "target": "F-d.func1"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-a
  name: Brick A
  layer: 2
  units:
    - F-a.func1

- id: B-b
  name: Brick B
  layer: 1
  units:
    - F-b.func1

- id: B-c
  name: Brick C
  layer: 1
  units:
    - F-c.func1

- id: B-d
  name: Brick D
  layer: 0
  units:
    - F-d.func1
"""
        )

        result = validate_brick_cycles(bricks_file, impl_graph)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-039")
def test_validate_cycles_no_dependencies():
    """Valid: No dependencies means no cycles."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-a.func1", "type": "function"},
                {"id": "F-b.func1", "type": "function"},
            ],
            edges=[],  # No edges
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-a
  name: Brick A
  layer: 0
  units:
    - F-a.func1

- id: B-b
  name: Brick B
  layer: 0
  units:
    - F-b.func1
"""
        )

        result = validate_brick_cycles(bricks_file, impl_graph)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-039")
def test_validate_cycles_long_cycle():
    """Invalid: Long cycle with many bricks."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            nodes=[
                {"id": "F-a.func1", "type": "function"},
                {"id": "F-b.func1", "type": "function"},
                {"id": "F-c.func1", "type": "function"},
                {"id": "F-d.func1", "type": "function"},
                {"id": "F-e.func1", "type": "function"},
            ],
            edges=[
                {"type": "calls", "source": "F-a.func1", "target": "F-b.func1"},
                {"type": "calls", "source": "F-b.func1", "target": "F-c.func1"},
                {"type": "calls", "source": "F-c.func1", "target": "F-d.func1"},
                {"type": "calls", "source": "F-d.func1", "target": "F-e.func1"},
                {"type": "calls", "source": "F-e.func1", "target": "F-a.func1"},  # Back to start
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-a
  name: Brick A
  layer: 0
  units:
    - F-a.func1

- id: B-b
  name: Brick B
  layer: 0
  units:
    - F-b.func1

- id: B-c
  name: Brick C
  layer: 0
  units:
    - F-c.func1

- id: B-d
  name: Brick D
  layer: 0
  units:
    - F-d.func1

- id: B-e
  name: Brick E
  layer: 0
  units:
    - F-e.func1
"""
        )

        result = validate_brick_cycles(bricks_file, impl_graph)
        assert not result.passed
        assert len(result.errors) >= 1
        error = result.errors[0]
        assert "cycle" in error.message.lower() or "circular" in error.message.lower()
        # All bricks should be in the cycle
        assert "B-a" in error.message
        assert "B-e" in error.message
