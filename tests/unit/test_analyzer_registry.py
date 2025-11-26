"""Unit tests for AnalyzerRegistry.

Tests verify that the registry correctly manages language analyzers,
routes files by extension, and handles edge cases appropriately.
"""

from pathlib import Path
from typing import Any, Dict, List

import pytest

from jig.impl_graph.analyzers import (
    AnalyzerRegistry,
    LanguageAnalyzer,
    get_global_registry,
    reset_global_registry,
)


class MockPythonAnalyzer(LanguageAnalyzer):
    """Mock Python analyzer for testing."""

    def language_name(self) -> str:
        return "python"

    def file_extensions(self) -> List[str]:
        return [".py", ".pyx"]

    def analyze_file(self, file_path: Path) -> Dict[str, List[Dict[str, Any]]]:
        return {"nodes": [], "edges": []}


class MockTypeScriptAnalyzer(LanguageAnalyzer):
    """Mock TypeScript analyzer for testing."""

    def language_name(self) -> str:
        return "typescript"

    def file_extensions(self) -> List[str]:
        return [".ts", ".tsx"]

    def analyze_file(self, file_path: Path) -> Dict[str, List[Dict[str, Any]]]:
        return {"nodes": [], "edges": []}


class EmptyAnalyzer(LanguageAnalyzer):
    """Analyzer with no file extensions (for testing edge cases)."""

    def language_name(self) -> str:
        return "empty"

    def file_extensions(self) -> List[str]:
        return []

    def analyze_file(self, file_path: Path) -> Dict[str, List[Dict[str, Any]]]:
        return {"nodes": [], "edges": []}


class BadExtensionAnalyzer(LanguageAnalyzer):
    """Analyzer with malformed extension (missing dot)."""

    def language_name(self) -> str:
        return "bad"

    def file_extensions(self) -> List[str]:
        return ["bad"]  # Missing leading dot

    def analyze_file(self, file_path: Path) -> Dict[str, List[Dict[str, Any]]]:
        return {"nodes": [], "edges": []}


@pytest.fixture
def registry() -> AnalyzerRegistry:
    """Create a fresh registry for each test."""
    return AnalyzerRegistry()


def test_registry_initialization(registry: AnalyzerRegistry) -> None:
    """Test that registry initializes empty.

    Verifies S-004: AnalyzerRegistry manages language analyzer registration.
    """
    assert registry.supported_extensions() == []
    assert registry.supported_languages() == []


def test_registry_registration(registry: AnalyzerRegistry) -> None:
    """Test that analyzers can be registered.

    Verifies S-004: AnalyzerRegistry manages language analyzer registration.
    """
    analyzer = MockPythonAnalyzer()
    registry.register(analyzer)

    # Verify registration
    assert "python" in registry.supported_languages()
    assert ".py" in registry.supported_extensions()
    assert ".pyx" in registry.supported_extensions()


def test_registry_auto_detection(registry: AnalyzerRegistry) -> None:
    """Test that registry routes files by extension.

    Verifies S-004: Language detector routes by file extension.
    """
    py_analyzer = MockPythonAnalyzer()
    ts_analyzer = MockTypeScriptAnalyzer()

    registry.register(py_analyzer)
    registry.register(ts_analyzer)

    # Test Python files
    assert registry.get_analyzer(Path("foo.py")) is py_analyzer
    assert registry.get_analyzer(Path("bar.pyx")) is py_analyzer

    # Test TypeScript files
    assert registry.get_analyzer(Path("foo.ts")) is ts_analyzer
    assert registry.get_analyzer(Path("bar.tsx")) is ts_analyzer

    # Test unknown extension
    assert registry.get_analyzer(Path("foo.unknown")) is None


def test_registry_case_insensitive_extensions(registry: AnalyzerRegistry) -> None:
    """Test that extension matching is case-insensitive."""
    analyzer = MockPythonAnalyzer()
    registry.register(analyzer)

    # All case variations should work
    assert registry.get_analyzer(Path("foo.py")) is analyzer
    assert registry.get_analyzer(Path("foo.PY")) is analyzer
    assert registry.get_analyzer(Path("foo.Py")) is analyzer


def test_registry_get_analyzer_by_language(registry: AnalyzerRegistry) -> None:
    """Test retrieval of analyzer by language name."""
    py_analyzer = MockPythonAnalyzer()
    ts_analyzer = MockTypeScriptAnalyzer()

    registry.register(py_analyzer)
    registry.register(ts_analyzer)

    # Test by language name
    assert registry.get_analyzer_by_language("python") is py_analyzer
    assert registry.get_analyzer_by_language("typescript") is ts_analyzer
    assert registry.get_analyzer_by_language("java") is None

    # Test case insensitivity
    assert registry.get_analyzer_by_language("Python") is py_analyzer
    assert registry.get_analyzer_by_language("TYPESCRIPT") is ts_analyzer


def test_registry_multiple_analyzers(registry: AnalyzerRegistry) -> None:
    """Test registry with multiple analyzers registered."""
    py_analyzer = MockPythonAnalyzer()
    ts_analyzer = MockTypeScriptAnalyzer()

    registry.register(py_analyzer)
    registry.register(ts_analyzer)

    # Verify all languages registered
    languages = registry.supported_languages()
    assert "python" in languages
    assert "typescript" in languages
    assert len(languages) == 2

    # Verify all extensions registered
    extensions = registry.supported_extensions()
    assert ".py" in extensions
    assert ".pyx" in extensions
    assert ".ts" in extensions
    assert ".tsx" in extensions
    assert len(extensions) == 4


def test_registry_override_warning(registry: AnalyzerRegistry, caplog: pytest.LogCaptureFixture) -> None:
    """Test that re-registering an extension logs a warning."""
    py_analyzer1 = MockPythonAnalyzer()
    py_analyzer2 = MockPythonAnalyzer()

    registry.register(py_analyzer1)
    registry.register(py_analyzer2)

    # Should have warning about override
    assert "already registered" in caplog.text.lower()

    # Second analyzer should win
    assert registry.get_analyzer_by_language("python") is py_analyzer2


def test_registry_empty_extensions_warning(registry: AnalyzerRegistry, caplog: pytest.LogCaptureFixture) -> None:
    """Test that analyzer with no extensions logs warning."""
    analyzer = EmptyAnalyzer()
    registry.register(analyzer)

    # Should log warning
    assert "no file extensions" in caplog.text.lower()

    # Should not be registered
    assert "empty" not in registry.supported_languages()


def test_registry_bad_extension_autocorrect(registry: AnalyzerRegistry, caplog: pytest.LogCaptureFixture) -> None:
    """Test that extensions without leading dot are auto-corrected."""
    analyzer = BadExtensionAnalyzer()
    registry.register(analyzer)

    # Should log warning about missing dot
    assert "should start with" in caplog.text.lower()

    # Should auto-correct and work
    assert ".bad" in registry.supported_extensions()
    assert registry.get_analyzer(Path("foo.bad")) is analyzer


def test_registry_clear(registry: AnalyzerRegistry) -> None:
    """Test that clear() removes all registered analyzers."""
    registry.register(MockPythonAnalyzer())
    registry.register(MockTypeScriptAnalyzer())

    # Verify registration
    assert len(registry.supported_languages()) == 2

    # Clear
    registry.clear()

    # Verify empty
    assert registry.supported_languages() == []
    assert registry.supported_extensions() == []


def test_global_registry_singleton() -> None:
    """Test that global registry maintains singleton-like behavior."""
    reset_global_registry()

    registry1 = get_global_registry()
    registry2 = get_global_registry()

    # Should be same instance
    assert registry1 is registry2


def test_global_registry_reset() -> None:
    """Test that reset creates a fresh global registry."""
    reset_global_registry()

    registry1 = get_global_registry()
    registry1.register(MockPythonAnalyzer())

    # Verify registration
    assert "python" in registry1.supported_languages()

    # Reset
    reset_global_registry()
    registry2 = get_global_registry()

    # Should be different instance and empty
    assert registry2 is not registry1
    assert registry2.supported_languages() == []


def test_registry_supported_extensions_sorted(registry: AnalyzerRegistry) -> None:
    """Test that supported_extensions returns sorted list."""
    registry.register(MockTypeScriptAnalyzer())  # .ts, .tsx
    registry.register(MockPythonAnalyzer())  # .py, .pyx

    extensions = registry.supported_extensions()

    # Should be sorted
    assert extensions == sorted(extensions)
    assert extensions == [".py", ".pyx", ".ts", ".tsx"]


def test_registry_supported_languages_sorted(registry: AnalyzerRegistry) -> None:
    """Test that supported_languages returns sorted list."""
    registry.register(MockTypeScriptAnalyzer())
    registry.register(MockPythonAnalyzer())

    languages = registry.supported_languages()

    # Should be sorted
    assert languages == sorted(languages)
    assert languages == ["python", "typescript"]


def test_registry_file_path_with_no_extension(registry: AnalyzerRegistry) -> None:
    """Test handling of file paths with no extension."""
    registry.register(MockPythonAnalyzer())

    # File with no extension
    assert registry.get_analyzer(Path("Makefile")) is None
    assert registry.get_analyzer(Path("README")) is None


def test_registry_file_path_with_multiple_dots(registry: AnalyzerRegistry) -> None:
    """Test handling of file paths with multiple dots."""
    registry.register(MockPythonAnalyzer())

    # Only last extension should matter
    assert registry.get_analyzer(Path("foo.bar.py")) is not None
    assert registry.get_analyzer(Path("foo.bar.baz")) is None


def test_registry_end_to_end_integration(registry: AnalyzerRegistry) -> None:
    """Integration test: register analyzers and process multiple files.

    Verifies S-004: Complete plugin architecture workflow.
    """
    py_analyzer = MockPythonAnalyzer()
    ts_analyzer = MockTypeScriptAnalyzer()

    registry.register(py_analyzer)
    registry.register(ts_analyzer)

    # Simulate processing multiple files
    files = [
        Path("src/main.py"),
        Path("src/utils.pyx"),
        Path("src/app.ts"),
        Path("src/component.tsx"),
        Path("README.md"),
    ]

    results = []
    for file in files:
        analyzer = registry.get_analyzer(file)
        if analyzer:
            result = analyzer.analyze_file(file)
            results.append((file, analyzer.language_name(), result))

    # Verify results
    assert len(results) == 4  # 4 files with analyzers, 1 skipped
    assert results[0][1] == "python"  # main.py
    assert results[1][1] == "python"  # utils.pyx
    assert results[2][1] == "typescript"  # app.ts
    assert results[3][1] == "typescript"  # component.tsx
