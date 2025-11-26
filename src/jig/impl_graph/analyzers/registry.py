"""Registry for language analyzers.

This module provides a central registry where language analyzers can be registered
and looked up by file extension. The registry uses the Strategy pattern to route
files to the appropriate analyzer based on their extension.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import jig

from .base import LanguageAnalyzer

logger = logging.getLogger(__name__)


class AnalyzerRegistry:
    """Registry for language-specific code analyzers.

    This class manages the collection of language analyzers and routes files
    to the appropriate analyzer based on file extension. It implements a
    singleton-like pattern where a global instance is typically used.

    Example:
        registry = AnalyzerRegistry()
        registry.register(PythonAnalyzer())
        registry.register(TypeScriptAnalyzer())

        analyzer = registry.get_analyzer(Path("foo.py"))
        if analyzer:
            result = analyzer.analyze_file(Path("foo.py"))
    """

    def __init__(self) -> None:
        """Initialize an empty analyzer registry."""
        self._analyzers: Dict[str, LanguageAnalyzer] = {}
        self._extension_map: Dict[str, LanguageAnalyzer] = {}

    @jig.implements("S-004")
    def register(self, analyzer: LanguageAnalyzer) -> None:
        """Register an analyzer for its file extensions.

        The analyzer will be registered for all extensions it declares via
        file_extensions(). If an extension is already registered, the new
        analyzer will override the previous one (with a warning).

        Args:
            analyzer: The language analyzer to register.

        Example:
            registry.register(PythonAnalyzer())  # Registers .py, .pyx
        """
        language = analyzer.language_name()
        extensions = analyzer.file_extensions()

        if not extensions:
            logger.warning(
                f"Analyzer for {language} declares no file extensions, skipping registration"
            )
            return

        # Store analyzer by language name
        if language in self._analyzers:
            logger.warning(
                f"Analyzer for {language} already registered, replacing with new instance"
            )
        self._analyzers[language] = analyzer

        # Map each extension to this analyzer
        for ext in extensions:
            if not ext.startswith("."):
                logger.warning(
                    f"Extension '{ext}' for {language} should start with '.', "
                    f"auto-correcting to '.{ext}'"
                )
                ext = f".{ext}"

            if ext in self._extension_map:
                existing = self._extension_map[ext]
                logger.warning(
                    f"Extension {ext} already registered for {existing.language_name()}, "
                    f"overriding with {language}"
                )

            self._extension_map[ext] = analyzer

        logger.debug(
            f"Registered {language} analyzer for extensions: {', '.join(extensions)}"
        )

    @jig.implements("S-004")
    def get_analyzer(self, file_path: Path) -> Optional[LanguageAnalyzer]:
        """Get the appropriate analyzer for a file based on its extension.

        Args:
            file_path: Path to the file to analyze.

        Returns:
            The registered analyzer for this file extension, or None if no
            analyzer is registered for this extension.

        Example:
            analyzer = registry.get_analyzer(Path("foo.py"))
            if analyzer:
                result = analyzer.analyze_file(Path("foo.py"))
            else:
                logger.debug(f"No analyzer for {file_path.suffix}")
        """
        ext = file_path.suffix.lower()
        return self._extension_map.get(ext)

    def get_analyzer_by_language(self, language: str) -> Optional[LanguageAnalyzer]:
        """Get an analyzer by language name.

        Args:
            language: The language name (e.g., 'python', 'typescript').

        Returns:
            The registered analyzer for this language, or None if not found.
        """
        return self._analyzers.get(language.lower())

    def supported_extensions(self) -> List[str]:
        """Return list of all supported file extensions.

        Returns:
            Sorted list of file extensions that have registered analyzers.
        """
        return sorted(self._extension_map.keys())

    def supported_languages(self) -> List[str]:
        """Return list of all supported language names.

        Returns:
            Sorted list of language names that have registered analyzers.
        """
        return sorted(self._analyzers.keys())

    def clear(self) -> None:
        """Clear all registered analyzers.

        Useful for testing or resetting the registry state.
        """
        self._analyzers.clear()
        self._extension_map.clear()
        logger.debug("Cleared all registered analyzers")


# Global registry instance for convenience
_global_registry: Optional[AnalyzerRegistry] = None


def get_global_registry() -> AnalyzerRegistry:
    """Get the global analyzer registry instance.

    Creates the global registry on first call (lazy initialization).

    Returns:
        The global AnalyzerRegistry instance.
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = AnalyzerRegistry()
    return _global_registry


def reset_global_registry() -> None:
    """Reset the global registry to a fresh instance.

    Useful for testing to ensure clean state between tests.
    """
    global _global_registry
    _global_registry = None
