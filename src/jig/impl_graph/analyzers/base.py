"""Base class for language-specific code analyzers.

This module defines the abstract interface that all language analyzers must implement.
The plugin architecture enables multi-language support while maintaining a language-agnostic
graph representation.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

import jig


@jig.implements("S-004")
class LanguageAnalyzer(ABC):
    """Abstract base class for language-specific code analyzers.

    All language analyzers must implement this interface to participate in the
    implementation graph generation. The analyzer is responsible for:

    1. Identifying which file extensions it handles
    2. Parsing source files in its language
    3. Extracting code structure (modules, classes, functions)
    4. Generating language-agnostic node and edge representations

    The output format is standardized across all languages to enable uniform
    graph processing regardless of source language.
    """

    @abstractmethod
    def language_name(self) -> str:
        """Return the language name (e.g., 'python', 'typescript', 'java').

        Returns:
            Language name as a lowercase string.
        """
        pass

    @abstractmethod
    def file_extensions(self) -> List[str]:
        """Return list of file extensions handled by this analyzer.

        Extensions should include the leading dot (e.g., ['.py', '.pyx']).

        Returns:
            List of file extensions this analyzer can process.
        """
        pass

    @abstractmethod
    def analyze_file(self, file_path: Path) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze a source file and return nodes and edges.

        Parses the source file and extracts:
        - Nodes: Modules, classes, functions, external dependencies
        - Edges: Imports, calls, inheritance, containment relationships

        All nodes must have: id, type, language (plus language-specific metadata)
        All edges must have: source, target, type

        Args:
            file_path: Path to the source file to analyze.

        Returns:
            Dictionary with two keys:
                "nodes": List of node dictionaries
                "edges": List of edge dictionaries

        Raises:
            ParseError: If the file cannot be parsed (syntax errors, encoding issues)
            IOError: If the file cannot be read

        Example:
            {
                "nodes": [
                    {"id": "M-foo.bar", "type": "module", "language": "python", ...},
                    {"id": "F-foo.bar.func", "type": "function", "language": "python", ...}
                ],
                "edges": [
                    {"source": "M-foo.bar", "target": "M-foo.baz", "type": "imports"}
                ]
            }
        """
        pass
