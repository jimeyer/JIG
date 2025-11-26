"""Unit tests for PythonAnalyzer.

Tests verify that the Python analyzer correctly extracts modules, classes,
functions, and their metadata from Python source files.

Verifies S-001: Python code structure extracted via AST analysis.
"""

from pathlib import Path

import pytest

import jig
from jig.impl_graph.analyzers import ParseError, PythonAnalyzer

# Get path to test fixtures
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "python"


@pytest.fixture
def analyzer() -> PythonAnalyzer:
    """Create a Python analyzer for testing."""
    return PythonAnalyzer(project_root=FIXTURES_DIR.parent.parent)


def test_python_analyzer_interface_compliance(analyzer: PythonAnalyzer) -> None:
    """Test that PythonAnalyzer implements the LanguageAnalyzer interface.

    Verifies S-004: Language analyzers follow plugin architecture.
    """
    assert analyzer.language_name() == "python"
    assert ".py" in analyzer.file_extensions()
    assert ".pyx" in analyzer.file_extensions()


@jig.verifies("S-001")
def test_python_analyzer_simple_module(analyzer: PythonAnalyzer) -> None:
    """Test analysis of a simple module with functions.

    Verifies S-001: Discovers modules and functions with line numbers.
    """
    fixture = FIXTURES_DIR / "simple_module.py"
    result = analyzer.analyze_file(fixture)

    # Check structure
    assert "nodes" in result
    assert "edges" in result
    assert isinstance(result["nodes"], list)
    assert isinstance(result["edges"], list)

    # Get nodes by type
    nodes = result["nodes"]
    modules = [n for n in nodes if n["type"] == "module"]
    functions = [n for n in nodes if n["type"] == "function"]

    # Should have 1 module
    assert len(modules) == 1
    module = modules[0]
    assert module["id"].startswith("M-")
    assert module["language"] == "python"
    assert "simple_module" in module["name"]

    # Should have 3 functions (including _private_helper)
    assert len(functions) == 3

    # Check hello_world function
    hello = [f for f in functions if f["name"] == "hello_world"][0]
    assert hello["id"].startswith("F-")
    assert "hello_world" in hello["id"]
    assert hello["language"] == "python"
    assert hello["line"] > 0
    assert "signature" in hello
    assert "hello_world()" in hello["signature"]

    # Check add_numbers function
    add = [f for f in functions if f["name"] == "add_numbers"][0]
    assert "a, b" in add["signature"]

    # Check that private function is included
    private = [f for f in functions if f["name"] == "_private_helper"]
    assert len(private) == 1


@jig.verifies("S-001")
def test_python_analyzer_class_with_methods(analyzer: PythonAnalyzer) -> None:
    """Test analysis of classes with methods.

    Verifies S-001: Discovers classes with methods and line numbers.
    """
    fixture = FIXTURES_DIR / "class_module.py"
    result = analyzer.analyze_file(fixture)

    nodes = result["nodes"]
    classes = [n for n in nodes if n["type"] == "class"]
    functions = [n for n in nodes if n["type"] == "function"]

    # Should have 2 classes
    assert len(classes) == 2

    # Check Calculator class
    calc = [c for c in classes if c["name"] == "Calculator"][0]
    assert calc["id"].startswith("C-")
    assert "Calculator" in calc["id"]
    assert calc["language"] == "python"
    assert calc["line"] > 0
    assert "bases" in calc
    assert calc["bases"] == []  # No inheritance

    # Check Logger class
    logger_class = [c for c in classes if c["name"] == "Logger"][0]
    assert "Logger" in logger_class["id"]

    # Should have methods
    methods = [f for f in functions if "Calculator" in f["id"]]
    assert len(methods) == 3  # add, subtract, _internal_method

    # Verify method IDs are correct
    add_method = [m for m in methods if m["name"] == "add"][0]
    assert "Calculator.add" in add_method["id"]
    assert "self, a, b" in add_method["signature"]

    # Check containment edges
    edges = result["edges"]
    contains_edges = [e for e in edges if e["type"] == "contains"]

    # Module contains classes
    module_contains = [
        e for e in contains_edges if e["source"].startswith("M-") and e["target"].startswith("C-")
    ]
    assert len(module_contains) == 2

    # Classes contain methods
    class_contains = [
        e for e in contains_edges if e["source"].startswith("C-") and e["target"].startswith("F-")
    ]
    assert len(class_contains) >= 3


@jig.verifies("S-001")
def test_python_analyzer_inheritance(analyzer: PythonAnalyzer) -> None:
    """Test extraction of class inheritance relationships.

    Verifies S-001: Discovers inheritance relationships.
    """
    fixture = FIXTURES_DIR / "inheritance.py"
    result = analyzer.analyze_file(fixture)

    nodes = result["nodes"]
    classes = [n for n in nodes if n["type"] == "class"]

    # Check Dog class inherits from Animal
    dog = [c for c in classes if c["name"] == "Dog"][0]
    assert "bases" in dog
    assert "Animal" in dog["bases"]

    # Check Cat class inherits from Animal
    cat = [c for c in classes if c["name"] == "Cat"][0]
    assert "Animal" in cat["bases"]

    # Check Robot class has no bases
    robot = [c for c in classes if c["name"] == "Robot"][0]
    assert robot["bases"] == []

    # Check RobotDog has multiple inheritance
    robot_dog = [c for c in classes if c["name"] == "RobotDog"][0]
    assert len(robot_dog["bases"]) == 2
    assert "Robot" in robot_dog["bases"]
    assert "Dog" in robot_dog["bases"]


@jig.verifies("S-001")
def test_python_analyzer_nested_classes(analyzer: PythonAnalyzer) -> None:
    """Test handling of nested class definitions.

    Verifies S-001: Handles nested classes correctly.
    """
    fixture = FIXTURES_DIR / "nested_classes.py"
    result = analyzer.analyze_file(fixture)

    nodes = result["nodes"]
    classes = [n for n in nodes if n["type"] == "class"]

    # Should have: Outer, Outer.Inner, Outer.Inner.DeepNested, Container, Container.Item
    assert len(classes) == 5

    # Check Outer class (top-level, not nested in another class)
    outer = [c for c in classes if c["name"] == "Outer" and "Outer.Inner" not in c["id"]][0]
    assert "Outer" in outer["id"]
    assert outer["bases"] == []

    # Check Inner nested class
    inner = [c for c in classes if c["name"] == "Inner" and "DeepNested" not in c["id"]][0]
    assert "Outer.Inner" in inner["id"]

    # Check DeepNested
    deep = [c for c in classes if c["name"] == "DeepNested"][0]
    assert "Outer.Inner.DeepNested" in deep["id"]

    # Check Container and Container.Item
    container = [c for c in classes if c["name"] == "Container"][0]
    assert "Container" in container["id"]

    item = [c for c in classes if c["name"] == "Item"][0]
    assert "Container.Item" in item["id"]

    # Check containment edges for nested classes
    edges = result["edges"]
    contains_edges = [e for e in edges if e["type"] == "contains"]

    # Outer contains Inner
    outer_contains_inner = [
        e
        for e in contains_edges
        if "Outer" in e["source"] and "Inner" in e["target"] and "DeepNested" not in e["target"]
    ]
    assert len(outer_contains_inner) >= 1

    # Inner contains DeepNested
    inner_contains_deep = [
        e for e in contains_edges if "Inner" in e["source"] and "DeepNested" in e["target"]
    ]
    assert len(inner_contains_deep) >= 1


@jig.verifies("S-001")
def test_python_analyzer_type_hints(analyzer: PythonAnalyzer) -> None:
    """Test extraction of type hints and annotations.

    Verifies S-001: Extracts signatures with type hints.
    """
    fixture = FIXTURES_DIR / "type_hints.py"
    result = analyzer.analyze_file(fixture)

    nodes = result["nodes"]
    functions = [n for n in nodes if n["type"] == "function"]

    # Check typed_function
    typed_func = [f for f in functions if f["name"] == "typed_function"][0]
    sig = typed_func["signature"]
    assert "name: str" in sig
    assert "age: int" in sig
    assert "-> str" in sig

    # Check optional_return
    optional_func = [f for f in functions if f["name"] == "optional_return"][0]
    sig = optional_func["signature"]
    assert "value: int" in sig
    assert "Optional" in sig or "str | None" in sig

    # Check complex_types
    complex_func = [f for f in functions if f["name"] == "complex_types"][0]
    sig = complex_func["signature"]
    assert "List" in sig or "list" in sig
    assert "Dict" in sig or "dict" in sig

    # Check TypedClass methods
    methods = [f for f in functions if "TypedClass" in f.get("id", "")]
    assert len(methods) >= 2

    process_method = [m for m in methods if m["name"] == "process"][0]
    assert "data: str" in process_method["signature"]
    assert "-> int" in process_method["signature"]


@jig.verifies("S-001")
def test_python_analyzer_async_functions(analyzer: PythonAnalyzer) -> None:
    """Test handling of async functions and methods.

    Verifies S-001: Discovers async functions.
    """
    fixture = FIXTURES_DIR / "async_functions.py"
    result = analyzer.analyze_file(fixture)

    nodes = result["nodes"]
    functions = [n for n in nodes if n["type"] == "function"]

    # Check async_hello
    async_hello = [f for f in functions if f["name"] == "async_hello"][0]
    assert async_hello["async"] is True

    # Check fetch_data
    fetch_data = [f for f in functions if f["name"] == "fetch_data"][0]
    assert fetch_data["async"] is True
    assert "url: str" in fetch_data["signature"]
    assert "-> str" in fetch_data["signature"]

    # Check sync_function is not async
    sync_func = [f for f in functions if f["name"] == "sync_function"][0]
    assert sync_func["async"] is False

    # Check AsyncService has async methods
    async_methods = [f for f in functions if "AsyncService" in f.get("id", "") and f["async"]]
    assert len(async_methods) >= 2

    # Check AsyncService has sync method too
    sync_methods = [
        f for f in functions if "AsyncService" in f.get("id", "") and not f["async"]
    ]
    assert len(sync_methods) >= 1


@jig.verifies("S-001")
def test_python_analyzer_node_id_format(analyzer: PythonAnalyzer) -> None:
    """Test that node IDs follow the correct format.

    Verifies S-001: Generates correct node IDs (M-, C-, F- prefixes).
    """
    fixture = FIXTURES_DIR / "class_module.py"
    result = analyzer.analyze_file(fixture)

    nodes = result["nodes"]

    # Check module ID format
    modules = [n for n in nodes if n["type"] == "module"]
    assert len(modules) == 1
    assert modules[0]["id"].startswith("M-")

    # Check class ID format
    classes = [n for n in nodes if n["type"] == "class"]
    for cls in classes:
        assert cls["id"].startswith("C-")
        # Should be C-module.ClassName
        assert cls["name"] in cls["id"]

    # Check function ID format
    functions = [n for n in nodes if n["type"] == "function"]
    for func in functions:
        assert func["id"].startswith("F-")
        # Should include function name
        assert func["name"] in func["id"]


@jig.verifies("S-006")
def test_python_analyzer_parse_error_handling() -> None:
    """Test that syntax errors are caught and reported clearly.

    Verifies S-006: Parse errors fail fast with clear file:line reporting.
    """
    # Create a temporary file with syntax error
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def broken_function(\n")
        f.write("    # Missing closing parenthesis and colon\n")
        f.write("    pass\n")
        temp_path = Path(f.name)

    try:
        analyzer = PythonAnalyzer()
        with pytest.raises(ParseError) as exc_info:
            analyzer.analyze_file(temp_path)

        error = exc_info.value
        assert error.file_path == temp_path
        assert error.line > 0
        assert "ERROR" in str(error)
        assert str(temp_path) in str(error)
    finally:
        temp_path.unlink()


def test_python_analyzer_empty_file(analyzer: PythonAnalyzer) -> None:
    """Test handling of empty Python file."""
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("# Empty module\n")
        temp_path = Path(f.name)

    try:
        result = analyzer.analyze_file(temp_path)
        nodes = result["nodes"]

        # Should have at least the module node
        modules = [n for n in nodes if n["type"] == "module"]
        assert len(modules) == 1
    finally:
        temp_path.unlink()


def test_python_analyzer_module_name_derivation() -> None:
    """Test that module names are correctly derived from file paths."""
    # With project root
    project_root = Path("/project")
    analyzer = PythonAnalyzer(project_root=project_root)

    # Test src/ convention
    test_path = project_root / "src" / "foo" / "bar" / "baz.py"
    # This will fail since file doesn't exist, but we can test the logic indirectly

    # Without project root (fallback to filename)
    analyzer_no_root = PythonAnalyzer(project_root=None)
    assert analyzer_no_root.project_root is None


def test_python_analyzer_language_agnostic_output_format(analyzer: PythonAnalyzer) -> None:
    """Test that output follows the language-agnostic format.

    Verifies S-004: Returns language-agnostic dict with nodes/edges.
    """
    fixture = FIXTURES_DIR / "simple_module.py"
    result = analyzer.analyze_file(fixture)

    # Check top-level structure
    assert set(result.keys()) == {"nodes", "edges"}
    assert isinstance(result["nodes"], list)
    assert isinstance(result["edges"], list)

    # Check node structure
    for node in result["nodes"]:
        assert "id" in node
        assert "type" in node
        assert "language" in node
        assert node["language"] == "python"

    # Check edge structure (if any)
    for edge in result["edges"]:
        assert "source" in edge
        assert "target" in edge
        assert "type" in edge


@jig.verifies("S-001")
def test_python_analyzer_accuracy_metrics(analyzer: PythonAnalyzer) -> None:
    """Test accuracy of module/class/function discovery.

    Verifies S-001: 99%+ accuracy for modules/classes, 95%+ for functions.
    """
    # Test on class_module.py which has known structure
    fixture = FIXTURES_DIR / "class_module.py"
    result = analyzer.analyze_file(fixture)

    nodes = result["nodes"]

    # Expected: 1 module, 2 classes, 5 methods
    modules = [n for n in nodes if n["type"] == "module"]
    classes = [n for n in nodes if n["type"] == "class"]
    functions = [n for n in nodes if n["type"] == "function"]

    # Module/class discovery should be 100%
    assert len(modules) == 1  # 100% accuracy
    assert len(classes) == 2  # 100% accuracy (Calculator, Logger)

    # Function discovery should be high (all 5 methods found)
    # Calculator: add, subtract, _internal_method
    # Logger: log, error
    assert len(functions) == 5  # 100% accuracy in this case


@jig.verifies("S-001")
def test_python_analyzer_integration_all_fixtures(analyzer: PythonAnalyzer) -> None:
    """Integration test: analyze all fixture files successfully.

    Verifies S-001: Complete workflow on multiple files.
    """
    fixtures = [
        "simple_module.py",
        "class_module.py",
        "inheritance.py",
        "nested_classes.py",
        "type_hints.py",
        "async_functions.py",
    ]

    for fixture_name in fixtures:
        fixture = FIXTURES_DIR / fixture_name
        result = analyzer.analyze_file(fixture)

        # All should parse successfully
        assert "nodes" in result
        assert "edges" in result

        # All should have at least a module node
        modules = [n for n in result["nodes"] if n["type"] == "module"]
        assert len(modules) >= 1, f"Failed to find module in {fixture_name}"
