"""Coverage collection for T→F edge discovery.

Runs pytest with coverage instrumentation to determine which tests
execute which functions.
"""

import json
import re
import sqlite3
import subprocess
import sys
from bisect import bisect_right
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import jig
from jig.config import JigConfig


@jig.implements("S-066")
def run_coverage_collection(
    config: JigConfig,
    coverage_file: Optional[Path] = None,
) -> tuple[int, Path]:
    """Run pytest with coverage instrumentation.

    Executes the test suite with line-level coverage tracking and
    per-test context recording. Coverage data is written to a SQLite
    database that can be queried for T→F relationships.

    Args:
        config: JIG configuration with project paths.
        coverage_file: Optional path for .coverage file. Defaults to
                      project_root/.coverage.

    Returns:
        Tuple of (pytest_exit_code, coverage_file_path).
        Exit code 0 means all tests passed; non-zero means some failed
        but coverage was still collected.
    """
    project_root = config.project_root
    source_dir = config.paths.source

    # Default coverage file location
    if coverage_file is None:
        coverage_file = project_root / ".coverage"

    # Ensure audits/records directory exists
    audits_dir = config.paths.jig_root / "audits" / "records"
    audits_dir.mkdir(parents=True, exist_ok=True)

    # Build pytest command with coverage flags
    # --cov: Track coverage for source directory
    # --cov-context=test: Record which test caused each line to execute
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        f"--cov={source_dir}",
        "--cov-context=test",
        f"--cov-report=",  # Suppress report output, we just want .coverage
        str(config.paths.tests),
    ]

    # Set COVERAGE_FILE env var to control output location
    env = {"COVERAGE_FILE": str(coverage_file)}

    # Run pytest with coverage
    result = subprocess.run(
        cmd,
        cwd=project_root,
        env={**subprocess.os.environ, **env},
        capture_output=False,  # Let output go to terminal
    )

    return result.returncode, coverage_file


@jig.implements("S-066")
def ensure_audits_directory(config: JigConfig) -> Path:
    """Ensure jig/audits/records/ directory exists.

    Args:
        config: JIG configuration with project paths.

    Returns:
        Path to the audits/records directory.
    """
    audits_dir = config.paths.jig_root / "audits" / "records"
    audits_dir.mkdir(parents=True, exist_ok=True)
    return audits_dir


@dataclass
class TFEdge:
    """Represents a T→F edge (test covers function)."""

    test_id: str
    function_id: str
    result: str = "covered"


@jig.implements("S-066")
def extract_tf_edges(
    coverage_file: Path,
    impl_graph_path: Path,
    project_root: Path,
) -> list[TFEdge]:
    """Extract T→F edges from coverage data and implementation graph.

    Parses the .coverage SQLite database and maps covered lines to
    function IDs using the implementation graph.

    Args:
        coverage_file: Path to .coverage SQLite database.
        impl_graph_path: Path to implementation-graph.ndjson.
        project_root: Project root for resolving relative paths.

    Returns:
        List of TFEdge objects representing test→function coverage.
    """
    # Load function index from implementation graph
    function_index = _build_function_index(impl_graph_path, project_root)

    # Parse coverage database
    test_coverage = _parse_coverage_database(coverage_file)

    # Map coverage to function IDs
    # Use a set to deduplicate (handles parametrized test collapsing)
    edge_set: set[tuple[str, str]] = set()

    for test_context, file_lines in test_coverage.items():
        # Convert test context to test ID
        test_id = _context_to_test_id(test_context)
        if not test_id:
            continue

        # Find all functions covered by this test
        for file_path, lines in file_lines.items():
            for line in lines:
                func_id = _find_function_at_line(function_index, file_path, line)
                if func_id:
                    edge_set.add((test_id, func_id))

    # Convert to TFEdge objects
    edges = [TFEdge(test_id=t, function_id=f) for t, f in edge_set]

    return edges


@jig.implements("S-066")
def _build_function_index(
    impl_graph_path: Path,
    project_root: Path,
) -> dict[str, list[tuple[int, str]]]:
    """Build an index mapping file paths to sorted (line, function_id) tuples.

    Args:
        impl_graph_path: Path to implementation-graph.ndjson.
        project_root: Project root for resolving relative paths.

    Returns:
        Dict mapping absolute file paths to sorted list of (line, function_id).
    """
    index: dict[str, list[tuple[int, str]]] = defaultdict(list)

    with open(impl_graph_path) as f:
        for line in f:
            node = json.loads(line)
            if node.get("type") != "function":
                continue

            # Get file path and convert to absolute
            file_path = node.get("file", "")
            if not file_path:
                continue

            abs_path = str((project_root / file_path).resolve())
            func_line = node.get("line", 0)
            func_id = node.get("id", "")

            if func_id and func_line > 0:
                index[abs_path].append((func_line, func_id))

    # Sort each file's functions by line number
    for file_path in index:
        index[file_path].sort(key=lambda x: x[0])

    return dict(index)


@jig.implements("S-066")
def _find_function_at_line(
    function_index: dict[str, list[tuple[int, str]]],
    file_path: str,
    line: int,
) -> Optional[str]:
    """Find the function containing a given line.

    Uses binary search to find the function with the largest start line
    that is <= the given line. This handles nested functions by returning
    the innermost (most recently started) function.

    Args:
        function_index: Index from _build_function_index.
        file_path: Absolute path to the file.
        line: Line number to look up.

    Returns:
        Function ID if found, None otherwise.
    """
    functions = function_index.get(file_path)
    if not functions:
        return None

    # Binary search for the rightmost function starting at or before this line
    lines = [f[0] for f in functions]
    idx = bisect_right(lines, line)

    if idx == 0:
        # Line is before any function
        return None

    # Return the function that starts at or before this line
    return functions[idx - 1][1]


@jig.implements("S-066")
def _parse_coverage_database(
    coverage_file: Path,
) -> dict[str, dict[str, set[int]]]:
    """Parse .coverage SQLite database to extract test→file→lines mapping.

    Args:
        coverage_file: Path to .coverage SQLite database.

    Returns:
        Dict mapping test context → file path → set of covered lines.
    """
    from coverage.numbits import numbits_to_nums

    result: dict[str, dict[str, set[int]]] = defaultdict(lambda: defaultdict(set))

    conn = sqlite3.connect(coverage_file)
    cursor = conn.cursor()

    # Query for all coverage data with file paths and contexts
    cursor.execute("""
        SELECT f.path, c.context, lb.numbits
        FROM line_bits lb
        JOIN file f ON lb.file_id = f.id
        JOIN context c ON lb.context_id = c.id
        WHERE c.context != ''
    """)

    for file_path, context, numbits in cursor.fetchall():
        lines = numbits_to_nums(numbits)
        result[context][file_path].update(lines)

    conn.close()
    return dict(result)


# Regex to extract test ID from pytest context string
# Format: "tests/path/test_file.py::test_name|run" or
#         "tests/path/test_file.py::TestClass::test_name|run" or
#         "tests/path/test_file.py::test_name[param]|run"
_CONTEXT_PATTERN = re.compile(
    r"^(?P<file>.*?)::(?P<test_path>[^|]+)\|run$"
)

# Pattern to strip parametrization suffixes like [param1-param2]
_PARAM_PATTERN = re.compile(r"\[.*\]$")


@jig.implements("S-066")
def _context_to_test_id(context: str) -> Optional[str]:
    """Convert pytest context string to JIG test ID.

    Handles parametrized tests by stripping parameter suffixes to
    collapse variants into a single test ID.

    Args:
        context: Pytest context string like
                "tests/audit/test_coverage.py::test_foo[param]|run"

    Returns:
        Test ID like "T-test_coverage.test_foo", or None if invalid.
    """
    match = _CONTEXT_PATTERN.match(context)
    if not match:
        return None

    file_path = match.group("file")
    test_path = match.group("test_path")

    # Strip parametrization suffix
    test_path = _PARAM_PATTERN.sub("", test_path)

    # Extract module name from file path
    # e.g., "tests/audit/test_coverage.py" -> "test_coverage"
    file_name = Path(file_path).stem

    # Build test ID
    # test_path might be "test_foo" or "TestClass::test_method"
    test_name = test_path.replace("::", ".")

    return f"T-{file_name}.{test_name}"
