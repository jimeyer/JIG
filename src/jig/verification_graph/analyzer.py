"""Test analyzer for the verification graph.

Analyzes test files to extract @jig.verifies decorators and compute
content hashes for test functions. This is purely static analysis -
no test execution required.
"""

import ast
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import jig
from jig.hashing import hash_test

logger = logging.getLogger(__name__)


class TestAnalyzer:
    """Analyzes test files to extract verification information.

    Extracts:
    - Test function/method discovery
    - @jig.verifies decorator arguments (T→S edges)
    - Content hashes (jig_hash) for change detection
    """

    def __init__(self, project_root: Path):
        """Initialize the analyzer.

        Args:
            project_root: Root directory of the project for computing relative paths.
        """
        self.project_root = project_root

    @jig.implements("S-052", "S-053", "S-054")
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a test file and return test nodes.

        Args:
            file_path: Path to the test file to analyze.

        Returns:
            Dict with "nodes" key containing list of T node dicts.
            Each node has: id, type, file, verifies, jig_hash
        """
        nodes: List[Dict[str, Any]] = []

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return {"nodes": nodes}

        # Compute module name and relative path
        module_name = file_path.stem
        try:
            relative_path = file_path.relative_to(self.project_root)
        except ValueError:
            relative_path = file_path

        # Find top-level test functions
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("test_"):
                    test_node = self._create_test_node(
                        node=node,
                        module_name=module_name,
                        class_name=None,
                        relative_path=relative_path,
                        file_path=file_path,
                    )
                    nodes.append(test_node)

            elif isinstance(node, ast.ClassDef):
                # Check if this is a test class (starts with Test)
                if node.name.startswith("Test"):
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            if item.name.startswith("test_"):
                                test_node = self._create_test_node(
                                    node=item,
                                    module_name=module_name,
                                    class_name=node.name,
                                    relative_path=relative_path,
                                    file_path=file_path,
                                )
                                nodes.append(test_node)

        # Sort nodes by ID for deterministic output
        nodes.sort(key=lambda n: n["id"])

        return {"nodes": nodes}

    def _create_test_node(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        module_name: str,
        class_name: Optional[str],
        relative_path: Path,
        file_path: Path,
    ) -> Dict[str, Any]:
        """Create a test node dict from an AST node.

        Args:
            node: The AST function node.
            module_name: Name of the module (file stem).
            class_name: Name of the containing class, or None for top-level.
            relative_path: Relative path to the file.
            file_path: Absolute path to the file.

        Returns:
            Test node dict with id, type, file, verifies, jig_hash.
        """
        # Compute test ID
        if class_name:
            test_id = f"T-{module_name}.{class_name}.{node.name}"
        else:
            test_id = f"T-{module_name}.{node.name}"

        # Extract verifies decorators
        verifies = self._extract_verifies_decorators(node, file_path)

        # Compute content hash
        jig_hash = hash_test(node)

        return {
            "id": test_id,
            "type": "test",
            "file": str(relative_path),
            "verifies": verifies,
            "jig_hash": jig_hash,
        }

    def _extract_verifies_decorators(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        file_path: Path,
    ) -> List[str]:
        """Extract @jig.verifies() decorator arguments from a node.

        Looks for decorators matching:
        - @jig.verifies("S-001")
        - @jig.verifies("S-001", "S-002")
        - @verifies("S-001") (if imported as 'from jig import verifies')

        Args:
            node: The FunctionDef node to inspect.
            file_path: Path to the file (for warning messages).

        Returns:
            List of specification IDs found in @jig.verifies decorators.
            Empty list if no decorators found or all invalid.
        """
        verifies_specs: List[str] = []

        for decorator in node.decorator_list:
            # Look for Call nodes (decorators with arguments)
            if not isinstance(decorator, ast.Call):
                continue

            # Check if this is @jig.verifies(...) or @verifies(...)
            is_verifies = False

            if isinstance(decorator.func, ast.Attribute):
                # @jig.verifies(...) or @module.verifies(...)
                if decorator.func.attr == "verifies":
                    # Check if it's jig.verifies
                    if isinstance(decorator.func.value, ast.Name):
                        if decorator.func.value.id == "jig":
                            is_verifies = True
            elif isinstance(decorator.func, ast.Name):
                # @verifies(...) - short form
                if decorator.func.id == "verifies":
                    is_verifies = True

            if not is_verifies:
                continue

            # Extract string arguments (spec IDs)
            for arg in decorator.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    spec_id = arg.value
                    # Validate spec ID format: S-{number} or O-{number}
                    if self._validate_spec_id(spec_id):
                        verifies_specs.append(spec_id)
                    else:
                        logger.warning(
                            f"{file_path}:{node.lineno}: "
                            f"Invalid spec ID format '{spec_id}' in @jig.verifies(). "
                            f"Expected format: S-001 or O-001"
                        )

        return verifies_specs

    def _validate_spec_id(self, spec_id: str) -> bool:
        """Validate that a spec ID matches the expected format.

        Args:
            spec_id: The specification ID to validate.

        Returns:
            True if the spec ID matches pattern ^[SO]-\\d+$, False otherwise.
        """
        pattern = r"^[SO]-\d+$"
        return bool(re.match(pattern, spec_id))
