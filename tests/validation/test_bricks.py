"""
Tests for brick validation (definitions and partition).
"""

import json
import tempfile
from pathlib import Path

import jig
from jig.validation.bricks import validate_brick_definitions, validate_brick_partition
from jig.validation.models import ValidationResult


def _create_implementation_graph(graph_file: Path, nodes: list[dict]) -> None:
    """Helper to create test implementation graph."""
    with graph_file.open("w") as f:
        for node in nodes:
            f.write(json.dumps(node) + "\n")


@jig.verifies("S-021")
def test_validate_brick_definitions_valid():
    """Valid brick definitions pass validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create implementation graph
        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            [
                {"id": "M-auth.session", "type": "module"},
                {"id": "F-auth.session.login", "type": "function"},
                {"id": "C-auth.tokens.Token", "type": "class"},
            ],
        )

        # Create bricks.yaml (S-035: use kebab-case ID)
        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-authentication
  name: Authentication
  units:
    - M-auth.session
    - C-auth.tokens.Token
"""
        )

        result = validate_brick_definitions(bricks_file, impl_graph)
        assert result.passed
        assert len(result.errors) == 0
        assert result.items_checked == 1


@jig.verifies("S-021")
def test_validate_brick_definitions_missing_impl_graph():
    """Error if implementation graph not found."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-test
  name: Test
  units:
    - M-test
"""
        )

        impl_graph = tmpdir / "implementation-graph.ndjson"  # doesn't exist

        result = validate_brick_definitions(bricks_file, impl_graph)
        assert not result.passed
        assert len(result.errors) == 1
        assert "not found" in result.errors[0].message.lower() or "missing" in result.errors[0].message.lower()


@jig.verifies("S-021")
def test_validate_brick_definitions_missing_required_field():
    """Missing required field detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(impl_graph, [])

        # Missing 'name' field
        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-test
  units:
    - M-test
"""
        )

        result = validate_brick_definitions(bricks_file, impl_graph)
        assert not result.passed
        assert any("name" in err.message.lower() for err in result.errors)


@jig.verifies("S-035")
def test_validate_brick_definitions_valid_kebab_case_ids():
    """Valid kebab-case brick IDs pass validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(impl_graph, [{"id": "M-test", "type": "module"}])

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-auth
  name: Authentication
  units:
    - M-test

- id: B-core-utils
  name: Core Utilities
  units:
    - M-test

- id: B-rest-api
  name: REST API
  units:
    - M-test

- id: B-cli-interface
  name: CLI Interface
  units:
    - M-test

- id: B-a
  name: Short
  units:
    - M-test

- id: B-user-management
  name: User Management
  units:
    - M-test

- id: B-with-many-hyphens
  name: Many Hyphens
  units:
    - M-test

- id: B-api-v2
  name: API Version 2
  units:
    - M-test
"""
        )

        result = validate_brick_definitions(bricks_file, impl_graph)
        assert result.passed, f"Expected validation to pass but got errors: {[e.message for e in result.errors]}"
        assert len(result.errors) == 0


@jig.verifies("S-035")
def test_validate_brick_definitions_invalid_old_numeric_format():
    """Old numeric format (B-001) rejected with clear error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(impl_graph, [])

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-001
  name: Test
  units:
    - M-test
"""
        )

        result = validate_brick_definitions(bricks_file, impl_graph)
        assert not result.passed
        assert any("B-001" in err.message for err in result.errors)
        assert any("kebab-case" in err.message.lower() for err in result.errors)


@jig.verifies("S-035")
def test_validate_brick_definitions_invalid_uppercase():
    """Uppercase letters in brick ID rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(impl_graph, [])

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-Auth
  name: Test
  units:
    - M-test
"""
        )

        result = validate_brick_definitions(bricks_file, impl_graph)
        assert not result.passed
        assert any("B-Auth" in err.message for err in result.errors)
        assert any("kebab-case" in err.message.lower() or "lowercase" in err.message.lower() for err in result.errors)


@jig.verifies("S-035")
def test_validate_brick_definitions_invalid_underscore():
    """Underscores in brick ID rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(impl_graph, [])

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-core_utils
  name: Test
  units:
    - M-test
"""
        )

        result = validate_brick_definitions(bricks_file, impl_graph)
        assert not result.passed
        assert any("B-core_utils" in err.message for err in result.errors)
        assert any("kebab-case" in err.message.lower() or "hyphen" in err.message.lower() for err in result.errors)


@jig.verifies("S-035")
def test_validate_brick_definitions_invalid_empty_name():
    """Empty brick name (just 'B-') rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(impl_graph, [])

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-
  name: Test
  units:
    - M-test
"""
        )

        result = validate_brick_definitions(bricks_file, impl_graph)
        assert not result.passed
        assert any("B-" in err.message for err in result.errors)


@jig.verifies("S-035")
def test_validate_brick_definitions_invalid_missing_prefix():
    """Missing 'B-' prefix rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(impl_graph, [])

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: auth
  name: Test
  units:
    - M-test
"""
        )

        result = validate_brick_definitions(bricks_file, impl_graph)
        assert not result.passed
        assert any("auth" in err.message for err in result.errors)


@jig.verifies("S-035")
def test_validate_brick_definitions_invalid_wrong_prefix():
    """Wrong prefix (not B-) rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(impl_graph, [])

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: INVALID-auth
  name: Test
  units:
    - M-test
"""
        )

        result = validate_brick_definitions(bricks_file, impl_graph)
        assert not result.passed
        assert any("INVALID-auth" in err.message for err in result.errors)


@jig.verifies("S-021")
def test_validate_brick_definitions_duplicate_ids():
    """Duplicate brick IDs detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(impl_graph, [])

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-first
  name: First
  units:
    - M-first

- id: B-first
  name: Duplicate
  units:
    - M-second
"""
        )

        result = validate_brick_definitions(bricks_file, impl_graph)
        assert not result.passed
        assert any("duplicate" in err.message.lower() or "unique" in err.message.lower() for err in result.errors)


@jig.verifies("S-021")
def test_validate_brick_definitions_invalid_unit_prefix():
    """Invalid unit prefix rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(impl_graph, [])

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-test
  name: Test
  units:
    - auth.session  # Missing prefix!
"""
        )

        result = validate_brick_definitions(bricks_file, impl_graph)
        assert not result.passed
        assert any("prefix" in err.message.lower() for err in result.errors)


@jig.verifies("S-021")
def test_validate_brick_definitions_unit_not_in_graph():
    """Unit reference not found in implementation graph detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            [
                {"id": "M-auth.session", "type": "module"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-test
  name: Test
  units:
    - M-nonexistent.module  # Not in graph!
"""
        )

        result = validate_brick_definitions(bricks_file, impl_graph)
        assert not result.passed
        assert any("not found" in err.message.lower() or "exist" in err.message.lower() for err in result.errors)


@jig.verifies("S-021")
def test_validate_brick_definitions_excluded_fields():
    """Excluded fields detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(impl_graph, [])

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-test
  name: Test
  units:
    - M-test
  depends_on:
    - B-other
  public_api:
    - some_function
  specs:
    - S-001
"""
        )

        result = validate_brick_definitions(bricks_file, impl_graph)
        assert not result.passed
        error_messages = " ".join(err.message for err in result.errors)
        assert "depends_on" in error_messages.lower()
        assert "public_api" in error_messages.lower()
        assert "specs" in error_messages.lower()


@jig.verifies("S-022")
def test_validate_brick_partition_valid():
    """Valid partition (every function in exactly one brick) passes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create implementation graph with functions
        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            [
                {"id": "M-auth.session", "type": "module"},
                {"id": "F-auth.session.login", "type": "function"},
                {"id": "F-auth.session.logout", "type": "function"},
                {"id": "M-cli.main", "type": "module"},
                {"id": "F-cli.main.run", "type": "function"},
            ],
        )

        # Create bricks with complete partition
        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-auth
  name: Authentication
  units:
    - M-auth.session  # Covers both login and logout

- id: B-cli
  name: CLI
  units:
    - F-cli.main.run
"""
        )

        result = validate_brick_partition(bricks_file, impl_graph)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-022")
def test_validate_brick_partition_gap():
    """Gap detected (function in zero bricks)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            [
                {"id": "F-auth.session.login", "type": "function"},
                {"id": "F-auth.session.logout", "type": "function"},  # Not in any brick!
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-auth
  name: Auth
  units:
    - F-auth.session.login  # Only login, not logout
"""
        )

        result = validate_brick_partition(bricks_file, impl_graph)
        assert not result.passed
        assert any("gap" in err.message.lower() or "F-auth.session.logout" in err.message for err in result.errors)


@jig.verifies("S-022")
def test_validate_brick_partition_overlap():
    """Overlap detected (function in multiple bricks)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            [
                {"id": "F-auth.session.login", "type": "function"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-auth
  name: Auth
  units:
    - F-auth.session.login

- id: B-security
  name: Security
  units:
    - F-auth.session.login  # Duplicate!
"""
        )

        result = validate_brick_partition(bricks_file, impl_graph)
        assert not result.passed
        assert any("overlap" in err.message.lower() or "multiple" in err.message.lower() for err in result.errors)


@jig.verifies("S-022")
def test_validate_brick_partition_class_splitting():
    """Class splitting detected (class methods in different bricks)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            [
                {"id": "C-auth.Token", "type": "class"},
                {"id": "F-auth.Token.__init__", "type": "function", "parent_class": "C-auth.Token"},
                {"id": "F-auth.Token.validate", "type": "function", "parent_class": "C-auth.Token"},
            ],
        )

        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-token-init
  name: TokenInit
  units:
    - F-auth.Token.__init__  # Only __init__

- id: B-token-validation
  name: TokenValidation
  units:
    - F-auth.Token.validate  # Only validate - CLASS SPLIT!
"""
        )

        result = validate_brick_partition(bricks_file, impl_graph)
        assert not result.passed
        assert any("class" in err.message.lower() and "split" in err.message.lower() for err in result.errors)


@jig.verifies("S-022")
def test_validate_brick_partition_module_expansion():
    """Module units expand to all contained functions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            [
                {"id": "M-auth.session", "type": "module"},
                {"id": "F-auth.session.login", "type": "function"},
                {"id": "F-auth.session.logout", "type": "function"},
                {"id": "F-auth.session.refresh", "type": "function"},
            ],
        )

        # M-auth.session should expand to cover all three functions
        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-auth
  name: Auth
  units:
    - M-auth.session  # Should expand to all F-auth.session.*
"""
        )

        result = validate_brick_partition(bricks_file, impl_graph)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-022")
def test_validate_brick_partition_class_expansion():
    """Class units expand to all methods."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        impl_graph = tmpdir / "implementation-graph.ndjson"
        _create_implementation_graph(
            impl_graph,
            [
                {"id": "C-auth.Token", "type": "class"},
                {"id": "F-auth.Token.__init__", "type": "function"},
                {"id": "F-auth.Token.validate", "type": "function"},
                {"id": "F-auth.Token.refresh", "type": "function"},
            ],
        )

        # C-auth.Token should expand to cover all methods
        bricks_file = tmpdir / "bricks.yaml"
        bricks_file.write_text(
            """
- id: B-token
  name: Token
  units:
    - C-auth.Token  # Should expand to all F-auth.Token.*
"""
        )

        result = validate_brick_partition(bricks_file, impl_graph)
        assert result.passed
        assert len(result.errors) == 0
