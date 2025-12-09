"""Test file and function discovery for the verification graph.

Discovers test files following pytest conventions and parses test functions
using AST analysis. This is purely static - no test execution required.
"""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import jig

# Directories to always exclude from test discovery
DEFAULT_EXCLUDE_DIRS = frozenset({
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".git",
    ".tox",
    ".nox",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
    "*.egg-info",
})


@dataclass
class TestInfo:
    """Information about a discovered test function.

    Attributes:
        id: Test ID in format T-{module}.{function} or T-{module}.{Class}.{method}
        file: Relative path to test file from project root
        name: Test function name (e.g., "test_login")
        class_name: Class name if this is a test method, None otherwise
    """

    id: str
    file: Path
    name: str
    class_name: Optional[str] = None


@jig.implements("S-051")
def discover_test_files(
    project_root: Path,
    test_dir: Optional[Path] = None,
    exclude_patterns: Optional[List[str]] = None,
) -> List[Path]:
    """Discover all test files in the project.

    Finds files matching pytest conventions:
    - test_*.py (prefix pattern)
    - *_test.py (suffix pattern)

    Args:
        project_root: Root directory of the project.
        test_dir: Directory to search for tests (defaults to project_root/tests).
        exclude_patterns: Additional glob patterns to exclude.

    Returns:
        List of test file paths, sorted alphabetically for determinism.
    """
    if test_dir is None:
        test_dir = project_root / "tests"

    if not test_dir.exists():
        return []

    files: List[Path] = []

    # Find test_*.py files
    for file_path in test_dir.rglob("test_*.py"):
        if _should_include(file_path):
            files.append(file_path)

    # Find *_test.py files
    for file_path in test_dir.rglob("*_test.py"):
        if _should_include(file_path) and file_path not in files:
            files.append(file_path)

    # Sort for deterministic output
    return sorted(files)


def _should_include(file_path: Path) -> bool:
    """Check if a file should be included in discovery.

    Excludes files in __pycache__, .venv, node_modules, etc.

    Args:
        file_path: Path to check.

    Returns:
        True if the file should be included.
    """
    # Check each part of the path for excluded directories
    for part in file_path.parts:
        if part in DEFAULT_EXCLUDE_DIRS:
            return False
    return True


def discover_tests(
    test_files: List[Path],
    project_root: Optional[Path] = None,
) -> List[TestInfo]:
    """Discover test functions and methods from test files.

    Parses test files using AST to find:
    - Functions starting with test_ at module level
    - Methods starting with test_ in classes starting with Test

    Args:
        test_files: List of test file paths to analyze.
        project_root: Project root for computing relative paths.

    Returns:
        List of TestInfo objects, sorted by ID for determinism.
    """
    tests: List[TestInfo] = []

    for file_path in test_files:
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError):
            # Skip files that can't be parsed
            continue

        # Compute module name from file path
        module_name = file_path.stem

        # Compute relative path for the file field
        if project_root:
            try:
                relative_path = file_path.relative_to(project_root)
            except ValueError:
                relative_path = file_path
        else:
            relative_path = file_path

        # Find test functions and methods
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if this is a top-level test function
                if node.name.startswith("test_") and _is_top_level(tree, node):
                    test_id = f"T-{module_name}.{node.name}"
                    tests.append(
                        TestInfo(
                            id=test_id,
                            file=relative_path,
                            name=node.name,
                            class_name=None,
                        )
                    )

            elif isinstance(node, ast.ClassDef):
                # Check if this is a test class (starts with Test)
                if node.name.startswith("Test"):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name.startswith(
                            "test_"
                        ):
                            test_id = f"T-{module_name}.{node.name}.{item.name}"
                            tests.append(
                                TestInfo(
                                    id=test_id,
                                    file=relative_path,
                                    name=item.name,
                                    class_name=node.name,
                                )
                            )

    # Sort by ID for deterministic output
    return sorted(tests, key=lambda t: t.id)


def _is_top_level(tree: ast.Module, node: ast.FunctionDef) -> bool:
    """Check if a function is defined at module level (not inside a class).

    Args:
        tree: The AST module.
        node: The function definition node.

    Returns:
        True if the function is at module level.
    """
    return node in tree.body
