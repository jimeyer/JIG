"""Python language analyzer for implementation graph generation.

This module provides a Python-specific implementation of the LanguageAnalyzer
interface, using AST parsing to extract code structure.
"""

import ast
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

from .base import LanguageAnalyzer
from .python_visitor import PythonStructureVisitor

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """Raised when a Python file cannot be parsed."""

    def __init__(
        self, file_path: Path, line: int, column: int, message: str, text: str = ""
    ) -> None:
        """Initialize parse error.

        Args:
            file_path: Path to the file that failed to parse.
            line: Line number where error occurred.
            column: Column number where error occurred.
            message: Error message.
            text: The problematic line of code.
        """
        self.file_path = file_path
        self.line = line
        self.column = column
        self.message = message
        self.text = text
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format a clear, actionable error message."""
        msg = f"ERROR: Failed to parse Python file\n"
        msg += f"  File: {self.file_path}\n"
        msg += f"  Line: {self.line}, Column: {self.column}\n"
        msg += f"\n  Syntax error: {self.message}\n"
        if self.text:
            msg += f"\n  {self.text}\n"
        return msg


class PythonAnalyzer(LanguageAnalyzer):
    """Analyzer for Python source code.

    Extracts modules, classes, functions, and their relationships using
    AST parsing. Implements the LanguageAnalyzer interface for integration
    with the implementation graph builder.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        """Initialize the Python analyzer.

        Args:
            project_root: Root directory of the project, used for resolving
                module names. If None, module names will be derived from
                file paths.
        """
        self.project_root = project_root

    def language_name(self) -> str:
        """Return the language name.

        Returns:
            'python'
        """
        return "python"

    def file_extensions(self) -> List[str]:
        """Return list of file extensions handled by this analyzer.

        Returns:
            List containing '.py' and '.pyx' (Cython).
        """
        return [".py", ".pyx"]

    def analyze_file(self, file_path: Path) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze a Python source file and return nodes and edges.

        Parses the file using Python's ast module, extracts modules, classes,
        and functions, and returns them in the language-agnostic format.

        Args:
            file_path: Path to the Python file to analyze.

        Returns:
            Dictionary with 'nodes' and 'edges' keys containing extracted
            structure information.

        Raises:
            ParseError: If the file cannot be parsed (syntax errors).
            IOError: If the file cannot be read.
        """
        # Read source code
        try:
            source = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Try with latin-1 as fallback
            try:
                source = file_path.read_text(encoding="latin-1")
                logger.warning(
                    f"File {file_path} is not UTF-8, read with latin-1 encoding"
                )
            except Exception as e:
                raise IOError(f"Could not read {file_path}: {e}") from e
        except Exception as e:
            raise IOError(f"Could not read {file_path}: {e}") from e

        # Parse AST
        try:
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError as e:
            raise ParseError(
                file_path=file_path,
                line=e.lineno or 0,
                column=e.offset or 0,
                message=e.msg,
                text=e.text or "",
            ) from e

        # Derive module name from file path
        module_name = self._derive_module_name(file_path)

        # Create module node
        module_node: Dict[str, Any] = {
            "id": f"M-{module_name}",
            "type": "module",
            "language": "python",
            "name": module_name,
            "file": str(file_path),
        }

        # Extract structure using visitor
        visitor = PythonStructureVisitor(file_path, module_name)
        visitor.visit(tree)
        nodes = visitor.get_nodes()
        imports = visitor.get_imports()
        calls = visitor.get_calls()

        # Track external modules and add them as nodes
        external_modules: Dict[str, Dict[str, Any]] = {}

        # Add module node at the beginning
        all_nodes = [module_node] + nodes

        # Initialize edges list
        edges: List[Dict[str, Any]] = []

        # Build containment edges
        for node in nodes:
            if node["type"] == "class" and not node["id"].count(".") > module_name.count(".") + 1:
                # Top-level class, contained by module
                edges.append(
                    {
                        "source": module_node["id"],
                        "target": node["id"],
                        "type": "contains",
                    }
                )
            elif node["type"] == "class":
                # Nested class - find parent
                parts = node["id"].split(".")
                # C-module.Outer.Inner -> parent is C-module.Outer
                parent_id = ".".join(parts[:-1])
                edges.append(
                    {"source": parent_id, "target": node["id"], "type": "contains"}
                )
            elif node["type"] == "function":
                # Function - contained by class or module
                if "parent_class" in node:
                    edges.append(
                        {
                            "source": node["parent_class"],
                            "target": node["id"],
                            "type": "contains",
                        }
                    )
                else:
                    # Module-level function
                    edges.append(
                        {
                            "source": module_node["id"],
                            "target": node["id"],
                            "type": "contains",
                        }
                    )

        # Build import edges
        for imp in imports:
            if imp["type"] == "import":
                # import os, import networkx
                imported_module = imp["module"]
                target_id = f"M-{imported_module}"

                # Create external module node if not in project
                if not self._is_internal_module(imported_module):
                    if target_id not in external_modules:
                        external_modules[target_id] = {
                            "id": target_id,
                            "type": "external_module",
                            "language": "python",
                            "name": imported_module,
                        }

                # Create import edge
                edges.append(
                    {
                        "source": module_node["id"],
                        "target": target_id,
                        "type": "imports",
                        "line": imp["line"],
                    }
                )

            elif imp["type"] == "from_import":
                # from pathlib import Path, from . import utils
                imported_module = imp["module"]

                # Handle relative imports
                if imp["level"] > 0:
                    # Relative import - resolve relative to current module
                    # For now, we'll just mark it as internal
                    # TODO: Properly resolve relative imports
                    pass
                elif imported_module:
                    target_id = f"M-{imported_module}"

                    # Create external module node if not in project
                    if not self._is_internal_module(imported_module):
                        if target_id not in external_modules:
                            external_modules[target_id] = {
                                "id": target_id,
                                "type": "external_module",
                                "language": "python",
                                "name": imported_module,
                            }

                    # Create import edge
                    edges.append(
                        {
                            "source": module_node["id"],
                            "target": target_id,
                            "type": "imports",
                            "line": imp["line"],
                        }
                    )

        # Build call edges
        for call in calls:
            caller_id = call["caller"]
            callee_name = call["callee"]

            # Try to resolve the callee to a function ID
            if call["type"] == "direct_call":
                # Direct call - could be to a function in this module or imported
                # Try to find the function in this module first
                target_id = f"F-{module_name}.{callee_name}"

                # Check if this function exists in our nodes
                func_exists = any(n["id"] == target_id for n in nodes)

                if func_exists:
                    edges.append(
                        {
                            "source": caller_id,
                            "target": target_id,
                            "type": "calls",
                            "line": call["line"],
                        }
                    )
                # Otherwise, skip (might be imported, would need more context)

            elif call["type"] == "attribute_call":
                # Attribute call like json.dumps() or module.func()
                # For V1, we'll try to match against imports
                # This is simplified - full resolution would need import tracking
                parts = callee_name.split(".")
                if len(parts) >= 2:
                    # Could be module.func() or obj.method()
                    # For now, we'll skip these as they require type inference
                    # or import resolution
                    pass

        # Build inheritance edges
        for node in nodes:
            if node["type"] == "class" and "bases" in node:
                for base_class_name in node["bases"]:
                    # Try to resolve base class to a class ID
                    # First, check if it's a class in this module
                    target_id = f"C-{module_name}.{base_class_name}"

                    # Check if this class exists in our nodes
                    class_exists = any(n["id"] == target_id for n in nodes)

                    if class_exists:
                        edges.append(
                            {
                                "source": node["id"],
                                "target": target_id,
                                "type": "extends",
                            }
                        )
                    # Otherwise, it might be imported or external
                    # Would need import resolution to handle properly

        # Add external module nodes to the node list
        all_nodes.extend(external_modules.values())

        return {"nodes": all_nodes, "edges": edges}

    def _derive_module_name(self, file_path: Path) -> str:
        """Derive a module name from a file path.

        Uses the project root if available, otherwise uses the file's
        directory structure.

        Args:
            file_path: Path to the Python file.

        Returns:
            Dotted module name (e.g., 'foo.bar.baz').
        """
        # Remove .py or .pyx extension
        module_path = file_path.with_suffix("")

        if self.project_root:
            try:
                # Get path relative to project root
                rel_path = module_path.relative_to(self.project_root)

                # Handle src/ directory convention
                parts = list(rel_path.parts)
                if parts and parts[0] == "src":
                    parts = parts[1:]

                # Convert path to dotted name
                return ".".join(parts)
            except ValueError:
                # File is not under project root, fall back to filename
                pass

        # Fallback: use the file stem as module name
        return module_path.stem

    def _is_internal_module(self, module_name: str) -> bool:
        """Check if a module is internal to the project or external.

        Args:
            module_name: The module name to check (e.g., 'os', 'jig.core.graph').

        Returns:
            True if the module is internal to the project, False if external.
        """
        # Python standard library modules are external
        # This is a simplified list - a complete implementation would use
        # sys.stdlib_module_names (Python 3.10+) or a comprehensive list
        stdlib_modules = {
            "abc",
            "argparse",
            "ast",
            "asyncio",
            "collections",
            "datetime",
            "functools",
            "io",
            "itertools",
            "json",
            "logging",
            "os",
            "pathlib",
            "re",
            "sys",
            "typing",
            "unittest",
        }

        # Get the top-level module name
        top_level = module_name.split(".")[0]

        # Check if it's stdlib
        if top_level in stdlib_modules:
            return False

        # For now, assume anything not in stdlib could be either internal or external
        # A more sophisticated approach would:
        # 1. Check if the module exists in the project source tree
        # 2. Parse package imports to know what's external
        # For V1, we'll treat non-stdlib as potentially external
        return False


def main() -> None:
    """Command-line interface for testing the Python analyzer."""
    if len(sys.argv) < 2:
        print("Usage: python -m jig.impl_graph.analyzers.python <file.py>")
        print("\nAnalyzes a Python file and prints the extracted structure as JSON.")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    if not file_path.suffix in [".py", ".pyx"]:
        print(f"Error: Not a Python file: {file_path}")
        sys.exit(1)

    # Analyze the file
    analyzer = PythonAnalyzer(project_root=Path.cwd())
    try:
        result = analyzer.analyze_file(file_path)

        # Print results as formatted JSON
        print(json.dumps(result, indent=2))

        # Print summary
        nodes = result["nodes"]
        edges = result["edges"]
        modules = [n for n in nodes if n["type"] == "module"]
        classes = [n for n in nodes if n["type"] == "class"]
        functions = [n for n in nodes if n["type"] == "function"]

        print("\n" + "=" * 60, file=sys.stderr)
        print(f"Summary:", file=sys.stderr)
        print(f"  Modules:   {len(modules)}", file=sys.stderr)
        print(f"  Classes:   {len(classes)}", file=sys.stderr)
        print(f"  Functions: {len(functions)}", file=sys.stderr)
        print(f"  Edges:     {len(edges)}", file=sys.stderr)
        print("=" * 60, file=sys.stderr)

    except ParseError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
