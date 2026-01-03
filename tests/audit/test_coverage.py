"""Tests for coverage collection functionality.

These tests verify S-066: T→F Edge Collection via Coverage.
"""

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import jig
from click.testing import CliRunner

from jig.audit.coverage import (
    TFEdge,
    _build_function_index,
    _context_to_test_id,
    _find_function_at_line,
    ensure_audits_directory,
    extract_tf_edges,
    run_coverage_collection,
)
from jig.cli.main import cli
from jig.config import JigConfig, PathsConfig


def _make_test_config(tmp_path: Path) -> JigConfig:
    """Create a test JigConfig pointing to a temporary directory."""
    jig_root = tmp_path / "jig"
    jig_root.mkdir(parents=True, exist_ok=True)

    paths = PathsConfig(
        source=tmp_path / "src",
        tests=tmp_path / "tests",
        jig_root=jig_root,
        specifications=jig_root / "specifications",
        outcomes=jig_root / "outcomes",
        bricks=jig_root / "bricks.yaml",
        generated=jig_root / "generated",
    )

    return JigConfig(
        paths=paths,
        project_root=tmp_path,
        config_file_path=None,
        has_config_file=False,
    )


@jig.verifies("S-066")
def test_audit_command_group_exists():
    """jigy audit command group exists and shows help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["audit", "--help"])

    assert result.exit_code == 0
    assert "coverage" in result.output
    assert "audit" in result.output.lower()


@jig.verifies("S-066")
def test_audit_coverage_command_exists():
    """jigy audit coverage command exists and shows help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["audit", "coverage", "--help"])

    assert result.exit_code == 0
    assert "coverage" in result.output.lower()
    assert "T→F" in result.output or "test" in result.output.lower()


@jig.verifies("S-066")
def test_audit_bare_shows_help():
    """jigy audit (bare) shows help with available subcommands."""
    runner = CliRunner()
    result = runner.invoke(cli, ["audit"])

    assert result.exit_code == 0
    assert "coverage" in result.output


@jig.verifies("S-066")
def test_ensure_audits_directory_creates_path(tmp_path):
    """ensure_audits_directory creates jig/audits/records/ if missing."""
    config = _make_test_config(tmp_path)

    # Ensure directory doesn't exist yet
    audits_dir = config.paths.jig_root / "audits" / "records"
    assert not audits_dir.exists()

    # Call function
    result_path = ensure_audits_directory(config)

    # Verify directory was created
    assert result_path.exists()
    assert result_path.is_dir()
    assert result_path == audits_dir


@jig.verifies("S-066")
def test_ensure_audits_directory_idempotent(tmp_path):
    """ensure_audits_directory is idempotent (can be called multiple times)."""
    config = _make_test_config(tmp_path)

    # Create directory twice
    path1 = ensure_audits_directory(config)
    path2 = ensure_audits_directory(config)

    # Both should succeed and return same path
    assert path1 == path2
    assert path1.exists()


@jig.verifies("S-066")
def test_run_coverage_collection_builds_correct_command(tmp_path):
    """run_coverage_collection builds pytest command with coverage flags."""
    config = _make_test_config(tmp_path)

    # Create minimal test directory
    config.paths.tests.mkdir(parents=True, exist_ok=True)
    (config.paths.tests / "test_dummy.py").write_text("def test_pass(): pass")

    # Mock subprocess.run to capture the command
    with patch("jig.audit.coverage.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        run_coverage_collection(config)

        # Verify subprocess.run was called
        assert mock_run.called
        call_args = mock_run.call_args

        # Check command contains expected flags
        cmd = call_args[0][0]  # First positional arg is the command list
        cmd_str = " ".join(cmd)

        assert "pytest" in cmd_str
        assert "--cov=" in cmd_str
        assert "--cov-context=test" in cmd_str


@jig.verifies("S-066")
def test_run_coverage_collection_returns_coverage_path(tmp_path):
    """run_coverage_collection returns path to .coverage file."""
    config = _make_test_config(tmp_path)

    # Create minimal test directory
    config.paths.tests.mkdir(parents=True, exist_ok=True)

    with patch("jig.audit.coverage.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        exit_code, coverage_path = run_coverage_collection(config)

        assert coverage_path == config.project_root / ".coverage"
        assert exit_code == 0


@jig.verifies("S-066")
def test_run_coverage_collection_captures_test_failures(tmp_path):
    """run_coverage_collection returns non-zero exit code on test failures."""
    config = _make_test_config(tmp_path)

    # Create minimal test directory
    config.paths.tests.mkdir(parents=True, exist_ok=True)

    with patch("jig.audit.coverage.subprocess.run") as mock_run:
        # Simulate test failure
        mock_run.return_value = MagicMock(returncode=1)

        exit_code, coverage_path = run_coverage_collection(config)

        # Exit code should be non-zero but coverage path still returned
        assert exit_code == 1
        assert coverage_path is not None


@jig.verifies("S-066")
def test_help_shows_audit_command():
    """Main CLI help shows audit command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "audit" in result.output


# ============================================================================
# T→F Extraction Tests (WU2)
# ============================================================================


@jig.verifies("S-066")
def test_context_to_test_id_simple():
    """_context_to_test_id converts simple test context to test ID."""
    context = "tests/audit/test_coverage.py::test_foo|run"
    result = _context_to_test_id(context)

    assert result == "T-test_coverage.test_foo"


@jig.verifies("S-066")
def test_context_to_test_id_with_class():
    """_context_to_test_id handles test methods in classes."""
    context = "tests/unit/test_analyzer.py::TestPythonAnalyzer::test_parse|run"
    result = _context_to_test_id(context)

    assert result == "T-test_analyzer.TestPythonAnalyzer.test_parse"


@jig.verifies("S-066")
def test_context_to_test_id_strips_parametrization():
    """_context_to_test_id strips parametrization suffixes."""
    context = "tests/unit/test_math.py::test_add[1-2-3]|run"
    result = _context_to_test_id(context)

    assert result == "T-test_math.test_add"


@jig.verifies("S-066")
def test_context_to_test_id_complex_params():
    """_context_to_test_id handles complex parametrization."""
    context = "tests/unit/test_math.py::test_divide[value1-value2]|run"
    result = _context_to_test_id(context)

    assert result == "T-test_math.test_divide"


@jig.verifies("S-066")
def test_context_to_test_id_invalid_format():
    """_context_to_test_id returns None for invalid format."""
    # Missing |run suffix
    assert _context_to_test_id("tests/test_foo.py::test_bar") is None

    # Empty string
    assert _context_to_test_id("") is None

    # No :: separator
    assert _context_to_test_id("test_foo|run") is None


@jig.verifies("S-066")
def test_build_function_index(tmp_path):
    """_build_function_index builds correct index from impl graph."""
    # Create a mock implementation graph
    impl_graph = tmp_path / "impl-graph.ndjson"

    # Create source file for path resolution
    src_dir = tmp_path / "src" / "mymodule"
    src_dir.mkdir(parents=True)
    (src_dir / "code.py").write_text("# placeholder")

    nodes = [
        {"_meta": {"version": "1.0"}},
        {
            "type": "function",
            "id": "F-mymodule.code.func_a",
            "file": "src/mymodule/code.py",
            "line": 10,
        },
        {
            "type": "function",
            "id": "F-mymodule.code.func_b",
            "file": "src/mymodule/code.py",
            "line": 25,
        },
        {
            "type": "class",
            "id": "C-mymodule.code.MyClass",
            "file": "src/mymodule/code.py",
            "line": 5,
        },
    ]

    with open(impl_graph, "w") as f:
        for node in nodes:
            f.write(json.dumps(node) + "\n")

    # Build index
    index = _build_function_index(impl_graph, tmp_path)

    # Check index structure
    abs_path = str((tmp_path / "src/mymodule/code.py").resolve())
    assert abs_path in index

    functions = index[abs_path]
    assert len(functions) == 2
    assert functions[0] == (10, "F-mymodule.code.func_a")
    assert functions[1] == (25, "F-mymodule.code.func_b")


@jig.verifies("S-066")
def test_find_function_at_line_exact_match():
    """_find_function_at_line finds function at exact start line."""
    index = {
        "/path/to/file.py": [
            (10, "F-module.func_a"),
            (25, "F-module.func_b"),
        ]
    }

    result = _find_function_at_line(index, "/path/to/file.py", 10)
    assert result == "F-module.func_a"


@jig.verifies("S-066")
def test_find_function_at_line_within_function():
    """_find_function_at_line finds function containing a line."""
    index = {
        "/path/to/file.py": [
            (10, "F-module.func_a"),
            (25, "F-module.func_b"),
        ]
    }

    # Line 15 is within func_a (starts at 10, next function at 25)
    result = _find_function_at_line(index, "/path/to/file.py", 15)
    assert result == "F-module.func_a"

    # Line 30 is within func_b
    result = _find_function_at_line(index, "/path/to/file.py", 30)
    assert result == "F-module.func_b"


@jig.verifies("S-066")
def test_find_function_at_line_before_any_function():
    """_find_function_at_line returns None for lines before any function."""
    index = {
        "/path/to/file.py": [
            (10, "F-module.func_a"),
        ]
    }

    result = _find_function_at_line(index, "/path/to/file.py", 5)
    assert result is None


@jig.verifies("S-066")
def test_find_function_at_line_unknown_file():
    """_find_function_at_line returns None for unknown files."""
    index = {
        "/path/to/file.py": [
            (10, "F-module.func_a"),
        ]
    }

    result = _find_function_at_line(index, "/other/file.py", 15)
    assert result is None


@jig.verifies("S-066")
def test_find_function_at_line_nested_functions():
    """_find_function_at_line returns innermost function for nested."""
    # With nested functions, the innermost one starts later
    index = {
        "/path/to/file.py": [
            (10, "F-module.outer"),
            (15, "F-module.outer.inner"),  # Nested function
            (30, "F-module.other"),
        ]
    }

    # Line 20 is within inner (which is nested in outer)
    result = _find_function_at_line(index, "/path/to/file.py", 20)
    assert result == "F-module.outer.inner"


def _create_mock_coverage_db(db_path: Path, coverage_data: dict) -> None:
    """Create a mock .coverage SQLite database.

    Args:
        db_path: Path to create the database.
        coverage_data: Dict mapping context -> file -> list of lines.
    """
    from coverage.numbits import nums_to_numbits

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create schema
    cursor.execute("CREATE TABLE coverage_schema (version INTEGER)")
    cursor.execute("INSERT INTO coverage_schema VALUES (7)")

    cursor.execute("CREATE TABLE file (id INTEGER PRIMARY KEY, path TEXT)")
    cursor.execute("CREATE TABLE context (id INTEGER PRIMARY KEY, context TEXT)")
    cursor.execute(
        "CREATE TABLE line_bits (file_id INTEGER, context_id INTEGER, numbits BLOB)"
    )

    # Build file and context mappings
    file_ids = {}
    context_ids = {}

    file_id = 1
    context_id = 1

    for context, file_lines in coverage_data.items():
        if context not in context_ids:
            cursor.execute("INSERT INTO context VALUES (?, ?)", (context_id, context))
            context_ids[context] = context_id
            context_id += 1

        for file_path, lines in file_lines.items():
            if file_path not in file_ids:
                cursor.execute("INSERT INTO file VALUES (?, ?)", (file_id, file_path))
                file_ids[file_path] = file_id
                file_id += 1

            numbits = nums_to_numbits(lines)
            cursor.execute(
                "INSERT INTO line_bits VALUES (?, ?, ?)",
                (file_ids[file_path], context_ids[context], numbits),
            )

    conn.commit()
    conn.close()


@jig.verifies("S-066")
def test_extract_tf_edges_basic(tmp_path):
    """extract_tf_edges produces correct edges from coverage data."""
    # Create mock implementation graph
    impl_graph = tmp_path / "impl-graph.ndjson"
    src_file = tmp_path / "src" / "module" / "code.py"
    src_file.parent.mkdir(parents=True)
    src_file.write_text("# placeholder")

    abs_src_path = str(src_file.resolve())

    nodes = [
        {"_meta": {"version": "1.0"}},
        {
            "type": "function",
            "id": "F-module.code.func_a",
            "file": "src/module/code.py",
            "line": 10,
        },
        {
            "type": "function",
            "id": "F-module.code.func_b",
            "file": "src/module/code.py",
            "line": 25,
        },
    ]

    with open(impl_graph, "w") as f:
        for node in nodes:
            f.write(json.dumps(node) + "\n")

    # Create mock coverage database
    coverage_db = tmp_path / ".coverage"
    coverage_data = {
        "tests/test_module.py::test_calls_func_a|run": {
            abs_src_path: [10, 11, 12],  # Lines in func_a
        },
        "tests/test_module.py::test_calls_both|run": {
            abs_src_path: [10, 11, 25, 26, 27],  # Lines in both functions
        },
    }
    _create_mock_coverage_db(coverage_db, coverage_data)

    # Extract edges
    edges = extract_tf_edges(coverage_db, impl_graph, tmp_path)

    # Verify edges
    edge_tuples = {(e.test_id, e.function_id) for e in edges}

    assert ("T-test_module.test_calls_func_a", "F-module.code.func_a") in edge_tuples
    assert ("T-test_module.test_calls_both", "F-module.code.func_a") in edge_tuples
    assert ("T-test_module.test_calls_both", "F-module.code.func_b") in edge_tuples

    # test_calls_func_a should NOT have an edge to func_b
    assert (
        "T-test_module.test_calls_func_a",
        "F-module.code.func_b",
    ) not in edge_tuples


@jig.verifies("S-066")
def test_extract_tf_edges_parametrized_collapsed(tmp_path):
    """extract_tf_edges collapses parametrized test variants."""
    # Create mock implementation graph
    impl_graph = tmp_path / "impl-graph.ndjson"
    src_file = tmp_path / "src" / "module" / "math.py"
    src_file.parent.mkdir(parents=True)
    src_file.write_text("# placeholder")

    abs_src_path = str(src_file.resolve())

    nodes = [
        {"_meta": {"version": "1.0"}},
        {
            "type": "function",
            "id": "F-module.math.add",
            "file": "src/module/math.py",
            "line": 5,
        },
    ]

    with open(impl_graph, "w") as f:
        for node in nodes:
            f.write(json.dumps(node) + "\n")

    # Create mock coverage with parametrized test variants
    coverage_db = tmp_path / ".coverage"
    coverage_data = {
        "tests/test_math.py::test_add[1-2-3]|run": {
            abs_src_path: [5, 6, 7],
        },
        "tests/test_math.py::test_add[0-0-0]|run": {
            abs_src_path: [5, 6, 7],
        },
        "tests/test_math.py::test_add[10-20-30]|run": {
            abs_src_path: [5, 6],
        },
    }
    _create_mock_coverage_db(coverage_db, coverage_data)

    # Extract edges
    edges = extract_tf_edges(coverage_db, impl_graph, tmp_path)

    # All three parametrized variants should collapse to single test ID
    test_ids = {e.test_id for e in edges}
    assert test_ids == {"T-test_math.test_add"}

    # Should have exactly one edge (collapsed)
    assert len(edges) == 1
    assert edges[0].test_id == "T-test_math.test_add"
    assert edges[0].function_id == "F-module.math.add"
