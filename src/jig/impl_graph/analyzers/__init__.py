"""Language-specific code analyzers for implementation graph generation.

This package provides a plugin architecture for analyzing source code in different
programming languages. Each language has its own analyzer that implements the
LanguageAnalyzer interface.

Example:
    from jig.impl_graph.analyzers import LanguageAnalyzer, AnalyzerRegistry

    # Create a custom analyzer
    class MyLanguageAnalyzer(LanguageAnalyzer):
        def language_name(self) -> str:
            return "mylang"

        def file_extensions(self) -> List[str]:
            return [".ml"]

        def analyze_file(self, file_path: Path) -> Dict:
            # ... implementation ...
            return {"nodes": [], "edges": []}

    # Register it
    registry = AnalyzerRegistry()
    registry.register(MyLanguageAnalyzer())
"""

from .base import LanguageAnalyzer
from .python import ParseError, PythonAnalyzer
from .registry import AnalyzerRegistry, get_global_registry, reset_global_registry

__all__ = [
    "LanguageAnalyzer",
    "AnalyzerRegistry",
    "get_global_registry",
    "reset_global_registry",
    "PythonAnalyzer",
    "ParseError",
]
