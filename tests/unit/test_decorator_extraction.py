"""Unit tests for @jig.implements decorator extraction.

Tests verify that the Python analyzer correctly extracts @jig.implements
decorators from functions and classes, validates spec IDs, and creates
implementation edges.

Verifies S-002: @jig.implements() decorators extracted and linked.
"""

from pathlib import Path

import pytest

import jig
from jig.impl_graph.analyzers import PythonAnalyzer

# Get path to test fixtures
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "python"


@pytest.fixture
def analyzer() -> PythonAnalyzer:
    """Create a Python analyzer for testing."""
    return PythonAnalyzer(project_root=FIXTURES_DIR.parent.parent)


@jig.verifies("S-002")
def test_decorator_single_spec(analyzer: PythonAnalyzer) -> None:
    """Test extraction of single @jig.implements decorator.

    Verifies S-002: Extracts @jig.implements("S-001").
    """
    fixture = FIXTURES_DIR / "decorators_single.py"
    result = analyzer.analyze_file(fixture)

    nodes = result["nodes"]

    # Find simple_function
    func_nodes = [n for n in nodes if n["type"] == "function" and n["name"] == "simple_function"]
    assert len(func_nodes) == 1
    func_node = func_nodes[0]

    # Check implements field
    assert "implements" in func_node
    assert func_node["implements"] == ["S-001"]


@jig.verifies("S-002")
def test_decorator_multiple_specs(analyzer: PythonAnalyzer) -> None:
    """Test extraction of multiple specs in one decorator.

    Verifies S-002: Supports @jig.implements("S-001", "S-002").
    """
    fixture = FIXTURES_DIR / "decorators_multiple.py"
    result = analyzer.analyze_file(fixture)

    nodes = result["nodes"]

    # Find multi_spec_function
    func_nodes = [n for n in nodes if n["type"] == "function" and n["name"] == "multi_spec_function"]
    assert len(func_nodes) == 1
    func_node = func_nodes[0]

    # Check implements field
    assert "implements" in func_node
    assert set(func_node["implements"]) == {"S-001", "S-002", "S-003"}


@jig.verifies("S-002")
def test_decorator_on_class(analyzer: PythonAnalyzer) -> None:
    """Test decorator extraction on classes.

    Verifies S-002: Class-level @jig.implements decorators.
    """
    fixture = FIXTURES_DIR / "decorators_single.py"
    result = analyzer.analyze_file(fixture)

    nodes = result["nodes"]

    # Find SimpleClass
    class_nodes = [n for n in nodes if n["type"] == "class" and n["name"] == "SimpleClass"]
    assert len(class_nodes) == 1
    class_node = class_nodes[0]

    # Check implements field
    assert "implements" in class_node
    assert class_node["implements"] == ["S-002"]


@jig.verifies("S-002")
def test_decorator_on_method(analyzer: PythonAnalyzer) -> None:
    """Test decorator extraction on methods.

    Verifies S-002: Method-level @jig.implements decorators.
    """
    fixture = FIXTURES_DIR / "decorators_single.py"
    result = analyzer.analyze_file(fixture)

    nodes = result["nodes"]

    # Find decorated_method
    method_nodes = [n for n in nodes if n["type"] == "function" and n["name"] == "decorated_method"]
    assert len(method_nodes) == 1
    method_node = method_nodes[0]

    # Check implements field
    assert "implements" in method_node
    assert method_node["implements"] == ["S-003"]


@jig.verifies("S-002")
def test_decorator_short_import(analyzer: PythonAnalyzer) -> None:
    """Test decorator extraction with short import form.

    Verifies S-002: Supports 'from jig import implements'.
    """
    fixture = FIXTURES_DIR / "decorators_short_import.py"
    result = analyzer.analyze_file(fixture)

    nodes = result["nodes"]

    # Find function_with_short_import
    func_nodes = [n for n in nodes if n["type"] == "function" and n["name"] == "function_with_short_import"]
    assert len(func_nodes) == 1
    func_node = func_nodes[0]

    # Check implements field
    assert "implements" in func_node
    assert func_node["implements"] == ["S-001"]

    # Find ClassWithShortImport
    class_nodes = [n for n in nodes if n["type"] == "class" and n["name"] == "ClassWithShortImport"]
    assert len(class_nodes) == 1
    class_node = class_nodes[0]

    # Check implements field
    assert "implements" in class_node
    assert class_node["implements"] == ["S-002"]


@jig.verifies("S-002")
def test_decorator_invalid_id_warning(analyzer: PythonAnalyzer, caplog: pytest.LogCaptureFixture) -> None:
    """Test that invalid spec IDs generate warnings.

    Verifies S-002: Warns on invalid spec ID format.
    """
    fixture = FIXTURES_DIR / "decorators_invalid.py"
    result = analyzer.analyze_file(fixture)

    nodes = result["nodes"]

    # Find invalid_spec_id function
    func_nodes = [n for n in nodes if n["type"] == "function" and n["name"] == "invalid_spec_id"]
    assert len(func_nodes) == 1
    func_node = func_nodes[0]

    # Should not have implements field (all invalid)
    assert "implements" not in func_node or func_node["implements"] == []

    # Check that warning was logged
    assert any("Invalid spec ID format 'BAD-FORMAT'" in record.message for record in caplog.records)


@jig.verifies("S-002")
def test_decorator_mixed_valid_invalid(analyzer: PythonAnalyzer, caplog: pytest.LogCaptureFixture) -> None:
    """Test handling of mixed valid/invalid spec IDs.

    Verifies S-002: Accepts valid specs, warns on invalid ones.
    """
    fixture = FIXTURES_DIR / "decorators_invalid.py"
    result = analyzer.analyze_file(fixture)

    nodes = result["nodes"]

    # Find mixed_valid_invalid function
    func_nodes = [n for n in nodes if n["type"] == "function" and n["name"] == "mixed_valid_invalid"]
    assert len(func_nodes) == 1
    func_node = func_nodes[0]

    # Should have only valid specs
    assert "implements" in func_node
    assert set(func_node["implements"]) == {"S-001", "S-002"}

    # Check that warning was logged for invalid spec
    assert any("Invalid spec ID format 'INVALID'" in record.message for record in caplog.records)


@jig.verifies("S-002")
def test_decorator_outcome_id(analyzer: PythonAnalyzer) -> None:
    """Test that outcome IDs (O-xxx) are valid.

    Verifies S-002: Validates spec IDs match pattern O-{number}.
    """
    fixture = FIXTURES_DIR / "decorators_multiple.py"
    result = analyzer.analyze_file(fixture)

    nodes = result["nodes"]

    # Find MultiSpecClass
    class_nodes = [n for n in nodes if n["type"] == "class" and n["name"] == "MultiSpecClass"]
    assert len(class_nodes) == 1
    class_node = class_nodes[0]

    # Check implements field includes O-001
    assert "implements" in class_node
    assert "O-001" in class_node["implements"]
    assert "S-010" in class_node["implements"]


@jig.verifies("S-002")
def test_implementation_edges_created(analyzer: PythonAnalyzer) -> None:
    """Test that implementation edges are created.

    Verifies S-002: Creates edges {"source": "F-X", "target": "S-Y", "type": "implements"}.
    """
    fixture = FIXTURES_DIR / "decorators_single.py"
    result = analyzer.analyze_file(fixture)

    edges = result["edges"]

    # Find implementation edges
    impl_edges = [e for e in edges if e["type"] == "implements"]

    # Should have at least 3 implementation edges (function, class, method)
    assert len(impl_edges) >= 3

    # Check edge structure
    for edge in impl_edges:
        assert "source" in edge
        assert "target" in edge
        assert "type" in edge
        assert edge["type"] == "implements"

        # Target should be a spec ID (S-xxx or O-xxx)
        assert edge["target"].startswith("S-") or edge["target"].startswith("O-")


@jig.verifies("S-002")
def test_implementation_edge_targets(analyzer: PythonAnalyzer) -> None:
    """Test that implementation edges point to correct spec IDs.

    Verifies S-002: Edge targets match decorator arguments.
    """
    fixture = FIXTURES_DIR / "decorators_single.py"
    result = analyzer.analyze_file(fixture)

    edges = result["edges"]
    nodes = result["nodes"]

    # Find simple_function node
    func_nodes = [n for n in nodes if n["type"] == "function" and n["name"] == "simple_function"]
    assert len(func_nodes) == 1
    func_id = func_nodes[0]["id"]

    # Find implementation edge from this function
    func_impl_edges = [e for e in edges if e["type"] == "implements" and e["source"] == func_id]
    assert len(func_impl_edges) == 1

    # Check target is S-001
    assert func_impl_edges[0]["target"] == "S-001"


@jig.verifies("S-002")
def test_no_decorator_no_implements_field(analyzer: PythonAnalyzer) -> None:
    """Test that functions without decorators don't have implements field.

    Verifies S-002: Only decorated functions have 'implements' field.
    """
    fixture = FIXTURES_DIR / "decorators_single.py"
    result = analyzer.analyze_file(fixture)

    nodes = result["nodes"]

    # Find method without decorator (SimpleClass.method)
    method_nodes = [n for n in nodes if n["type"] == "function" and n["name"] == "method"]
    assert len(method_nodes) == 1
    method_node = method_nodes[0]

    # Should not have implements field
    assert "implements" not in method_node or method_node["implements"] == []


@jig.verifies("S-002")
def test_accuracy_99_percent(analyzer: PythonAnalyzer) -> None:
    """Test 99%+ accuracy for decorator extraction.

    Verifies S-002: 99%+ extraction accuracy.
    """
    # Test all decorator fixtures
    fixtures = [
        FIXTURES_DIR / "decorators_single.py",
        FIXTURES_DIR / "decorators_multiple.py",
        FIXTURES_DIR / "decorators_short_import.py",
    ]

    total_expected = 0
    total_found = 0

    for fixture in fixtures:
        result = analyzer.analyze_file(fixture)

        # Count implementation edges
        impl_edges = [e for e in result["edges"] if e["type"] == "implements"]

        # Expected counts based on fixtures:
        # decorators_single.py: 3 (function, class, method)
        # decorators_multiple.py: 5 (function with 3, class with 2, method with 2)
        # decorators_short_import.py: 3 (function, class, method)

        if "decorators_single" in str(fixture):
            total_expected += 3
        elif "decorators_multiple" in str(fixture):
            total_expected += 7  # 3 + 2 + 2
        elif "decorators_short_import" in str(fixture):
            total_expected += 3

        total_found += len(impl_edges)

    # Calculate accuracy
    accuracy = total_found / total_expected if total_expected > 0 else 0
    assert accuracy >= 0.99, f"Decorator extraction accuracy {accuracy:.1%} below 99% target"
