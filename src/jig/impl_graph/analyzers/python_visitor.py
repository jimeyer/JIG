"""AST visitor for extracting Python code structure.

This module provides a visitor that traverses Python AST nodes and extracts
modules, classes, functions, and their relationships.
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional


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
        self.current_class: Optional[str] = None
        self.class_stack: List[str] = []  # For tracking nested classes

    def get_nodes(self) -> List[Dict[str, Any]]:
        """Return the collected nodes.

        Returns:
            List of node dictionaries with structure information.
        """
        return self.nodes

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

        self.nodes.append(func_node)

        # Don't visit nested functions (could be complex, defer to V2)
        # self.generic_visit(node)

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
