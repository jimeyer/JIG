"""AST visitor for extracting Python code structure.

This module provides a visitor that traverses Python AST nodes and extracts
modules, classes, functions, and their relationships.
"""

import ast
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import jig
from jig.hashing import hash_function

logger = logging.getLogger(__name__)


class PythonStructureVisitor(ast.NodeVisitor):
    """AST visitor that extracts Python code structure.

    Traverses the AST and builds a list of nodes (modules, classes, functions)
    with their metadata. Handles nested classes, inheritance, and various
    function types (sync, async, methods).
    """

    def __init__(self, file_path: Path, module_name: str) -> None:
        """Initialize the visitor.

        Args:
            file_path: Path to the Python file being analyzed.
            module_name: Dotted module name (e.g., 'foo.bar.baz').
        """
        self.file_path = file_path
        self.module_name = module_name
        self.nodes: List[Dict[str, Any]] = []
        self.imports: List[Dict[str, Any]] = []
        self.calls: List[Dict[str, Any]] = []
        self.current_class: Optional[str] = None
        self.class_stack: List[str] = []  # For tracking nested classes
        self.current_function: Optional[str] = None  # For tracking function context

    def get_nodes(self) -> List[Dict[str, Any]]:
        """Return the collected nodes.

        Returns:
            List of node dictionaries with structure information.
        """
        return self.nodes

    def get_imports(self) -> List[Dict[str, Any]]:
        """Return the collected imports.

        Returns:
            List of import dictionaries.
        """
        return self.imports

    def get_calls(self) -> List[Dict[str, Any]]:
        """Return the collected function calls.

        Returns:
            List of call dictionaries.
        """
        return self.calls

    @jig.implements("S-001")
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition node.

        Extracts class name, base classes, and creates a class node.
        Then visits nested content.

        Args:
            node: The ClassDef AST node.
        """
        # Build class ID based on nesting
        if self.class_stack:
            # Nested class: C-module.OuterClass.InnerClass
            class_id = f"C-{self.module_name}.{'.'.join(self.class_stack)}.{node.name}"
        else:
            # Top-level class: C-module.ClassName
            class_id = f"C-{self.module_name}.{node.name}"

        # Extract base classes
        base_classes = []
        for base in node.bases:
            base_name = self._get_name_from_node(base)
            if base_name:
                base_classes.append(base_name)

        # Extract @jig.implements decorators
        implements_specs = self._extract_implements_decorators(node)

        # Create class node
        class_node: Dict[str, Any] = {
            "id": class_id,
            "type": "class",
            "language": "python",
            "name": node.name,
            "file": str(self.file_path),
            "line": node.lineno,
            "bases": base_classes,
        }

        # Add implements field if decorators found
        if implements_specs:
            class_node["implements"] = implements_specs

        self.nodes.append(class_node)

        # Visit nested content (methods, nested classes)
        self.class_stack.append(node.name)
        self.current_class = class_id
        self.generic_visit(node)
        self.class_stack.pop()
        self.current_class = (
            f"C-{self.module_name}.{'.'.join(self.class_stack)}"
            if self.class_stack
            else None
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition node.

        Handles both module-level functions and class methods.

        Args:
            node: The FunctionDef AST node.
        """
        self._visit_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit an async function definition node.

        Args:
            node: The AsyncFunctionDef AST node.
        """
        self._visit_function(node, is_async=True)

    @jig.implements("S-001")
    def _visit_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool
    ) -> None:
        """Process a function or method definition.

        Args:
            node: The function definition AST node.
            is_async: Whether this is an async function.
        """
        # Build function ID
        if self.current_class:
            # Method: F-module.ClassName.method_name
            func_id = f"F-{self.module_name}.{'.'.join(self.class_stack)}.{node.name}"
        else:
            # Module-level function: F-module.function_name
            func_id = f"F-{self.module_name}.{node.name}"

        # Extract signature
        signature = self._extract_signature(node)

        # Extract @jig.implements decorators
        implements_specs = self._extract_implements_decorators(node)

        # Create function node
        func_node: Dict[str, Any] = {
            "id": func_id,
            "type": "function",
            "language": "python",
            "name": node.name,
            "file": str(self.file_path),
            "line": node.lineno,
            "signature": signature,
            "async": is_async,
        }

        # Add parent reference
        if self.current_class:
            func_node["parent_class"] = self.current_class

        # Add implements field and jig_hash if decorators found (S-050)
        if implements_specs:
            func_node["implements"] = implements_specs
            func_node["jig_hash"] = hash_function(node)

        self.nodes.append(func_node)

        # Visit function body to extract calls
        old_function = self.current_function
        self.current_function = func_id
        self.generic_visit(node)
        self.current_function = old_function

    @jig.implements("S-001")
    def _extract_signature(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Extract function signature as a string.

        Includes parameter names and type hints if present.

        Args:
            node: The function definition node.

        Returns:
            String representation of the signature.
        """
        args = node.args

        # Collect parameters
        params: List[str] = []

        # Regular arguments
        for i, arg in enumerate(args.args):
            param = arg.arg
            # Add type annotation if present
            if arg.annotation:
                param += f": {self._get_annotation_string(arg.annotation)}"
            # Add default value if present
            defaults_offset = len(args.args) - len(args.defaults)
            if i >= defaults_offset:
                default_idx = i - defaults_offset
                # We have a default, but showing it would be complex
                # For now, just indicate there is one
                pass
            params.append(param)

        # *args
        if args.vararg:
            vararg = f"*{args.vararg.arg}"
            if args.vararg.annotation:
                vararg += f": {self._get_annotation_string(args.vararg.annotation)}"
            params.append(vararg)

        # Keyword-only arguments
        for arg in args.kwonlyargs:
            param = arg.arg
            if arg.annotation:
                param += f": {self._get_annotation_string(arg.annotation)}"
            params.append(param)

        # **kwargs
        if args.kwarg:
            kwarg = f"**{args.kwarg.arg}"
            if args.kwarg.annotation:
                kwarg += f": {self._get_annotation_string(args.kwarg.annotation)}"
            params.append(kwarg)

        signature = f"{node.name}({', '.join(params)})"

        # Add return type if present
        if node.returns:
            signature += f" -> {self._get_annotation_string(node.returns)}"

        return signature

    def _get_annotation_string(self, annotation: ast.expr) -> str:
        """Convert an annotation AST node to a string.

        Args:
            annotation: The annotation expression node.

        Returns:
            String representation of the annotation.
        """
        try:
            return ast.unparse(annotation)
        except Exception:
            # Fallback for complex annotations
            return self._get_name_from_node(annotation) or "Any"

    def _get_name_from_node(self, node: ast.expr) -> Optional[str]:
        """Extract a name from an AST node.

        Handles Name, Attribute, and other node types.

        Args:
            node: The AST node to extract a name from.

        Returns:
            The name as a string, or None if it can't be extracted.
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # For a.b.c, return "a.b.c"
            parts = []
            current = node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts)) if parts else None
        elif isinstance(node, ast.Subscript):
            # For List[str], return "List[str]"
            try:
                return ast.unparse(node)
            except Exception:
                return None
        else:
            try:
                return ast.unparse(node)
            except Exception:
                return None

    @jig.implements("S-002")
    def _extract_implements_decorators(
        self, node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
    ) -> List[str]:
        """Extract @jig.implements() decorator arguments from a node.

        Looks for decorators matching:
        - @jig.implements("S-001")
        - @jig.implements("S-001", "S-002")
        - @implements("S-001") (if imported as 'from jig import implements')

        Args:
            node: The ClassDef or FunctionDef node to inspect.

        Returns:
            List of specification IDs found in @jig.implements decorators.
            Empty list if no decorators found or all invalid.
        """
        implements_specs: List[str] = []

        for decorator in node.decorator_list:
            # Look for Call nodes (decorators with arguments)
            if not isinstance(decorator, ast.Call):
                continue

            # Check if this is @jig.implements(...) or @implements(...)
            is_implements = False

            if isinstance(decorator.func, ast.Attribute):
                # @jig.implements(...) or @module.implements(...)
                if decorator.func.attr == "implements":
                    # Check if it's jig.implements
                    if isinstance(decorator.func.value, ast.Name):
                        if decorator.func.value.id == "jig":
                            is_implements = True
            elif isinstance(decorator.func, ast.Name):
                # @implements(...) - short form
                if decorator.func.id == "implements":
                    is_implements = True

            if not is_implements:
                continue

            # Extract string arguments (spec IDs)
            for arg in decorator.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    spec_id = arg.value
                    # Validate spec ID format: S-{number} or O-{number}
                    if self._validate_spec_id(spec_id):
                        implements_specs.append(spec_id)
                    else:
                        logger.warning(
                            f"{self.file_path}:{node.lineno}: "
                            f"Invalid spec ID format '{spec_id}' in @jig.implements(). "
                            f"Expected format: S-001 or O-001"
                        )

        return implements_specs

    def _validate_spec_id(self, spec_id: str) -> bool:
        """Validate that a spec ID matches the expected format.

        Args:
            spec_id: The specification ID to validate.

        Returns:
            True if the spec ID matches pattern ^[SO]-\\d+$, False otherwise.
        """
        pattern = r"^[SO]-\d+$"
        return bool(re.match(pattern, spec_id))

    @jig.implements("S-005")
    def visit_Import(self, node: ast.Import) -> None:
        """Visit an import statement.

        Extracts imports like: import os, import sys

        Args:
            node: The Import AST node.
        """
        for alias in node.names:
            import_info: Dict[str, Any] = {
                "module": alias.name,
                "alias": alias.asname,
                "line": node.lineno,
                "type": "import",
            }
            self.imports.append(import_info)

        # Continue visiting
        self.generic_visit(node)

    @jig.implements("S-005")
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit a from...import statement.

        Extracts imports like: from pathlib import Path

        Args:
            node: The ImportFrom AST node.
        """
        module = node.module or ""  # Handle "from . import X"
        level = node.level  # Relative import level (0 = absolute, 1 = ., 2 = .., etc.)

        for alias in node.names:
            import_info: Dict[str, Any] = {
                "module": module,
                "name": alias.name,
                "alias": alias.asname,
                "line": node.lineno,
                "level": level,
                "type": "from_import",
            }
            self.imports.append(import_info)

        # Continue visiting
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Visit a function call.

        Extracts direct function calls like: func(), module.func()
        Skips method calls that require type inference: obj.method()

        Args:
            node: The Call AST node.
        """
        # Only track calls if we're inside a function
        if not self.current_function:
            self.generic_visit(node)
            return

        # Get the function being called
        func = node.func

        # Case 1: Direct name call - func()
        if isinstance(func, ast.Name):
            call_info: Dict[str, Any] = {
                "caller": self.current_function,
                "callee": func.id,
                "type": "direct_call",
                "line": node.lineno,
            }
            self.calls.append(call_info)

        # Case 2: Attribute call - module.func() or obj.method()
        # For V1, we only capture module.func() where we can statically resolve the module
        elif isinstance(func, ast.Attribute):
            # Try to get the full dotted name
            full_name = self._get_name_from_node(func)
            if full_name:
                # Check if it looks like a module call vs instance method
                # For V1, we'll capture all attribute calls and filter later
                # based on whether they resolve to known modules
                call_info: Dict[str, Any] = {
                    "caller": self.current_function,
                    "callee": full_name,
                    "type": "attribute_call",
                    "line": node.lineno,
                }
                self.calls.append(call_info)

        # Continue visiting child nodes
        self.generic_visit(node)
