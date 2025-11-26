"""Python language analyzer for implementation graph generation.

This module provides a Python-specific implementation of the LanguageAnalyzer
interface, using AST parsing to extract code structure.
"""

import ast
import logging
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

        # Add module node at the beginning
        all_nodes = [module_node] + nodes

        # For now, no edges (imports, calls, etc. will be added in WU3)
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
