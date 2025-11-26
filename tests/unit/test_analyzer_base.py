"""Unit tests for LanguageAnalyzer base class.

Tests verify that the abstract base class enforces the required interface
and that concrete implementations must provide all required methods.
"""

from pathlib import Path
from typing import Any, Dict, List

import pytest

import jig
from jig.impl_graph.analyzers import LanguageAnalyzer


class MockAnalyzer(LanguageAnalyzer):
    """Mock analyzer for testing interface compliance."""

    def language_name(self) -> str:
        return "mock"

    def file_extensions(self) -> List[str]:
        return [".mock", ".mck"]

    def analyze_file(self, file_path: Path) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "nodes": [
                {
                    "id": "M-mock.example",
                    "type": "module",
                    "language": "mock",
                    "file": str(file_path),
                }
            ],
            "edges": [],
        }


class IncompleteAnalyzer(LanguageAnalyzer):
    """Incomplete analyzer missing required methods (for testing ABC enforcement)."""

    def language_name(self) -> str:
        return "incomplete"

    # Missing file_extensions() and analyze_file()


@jig.verifies("S-004")
def test_language_analyzer_interface() -> None:
    """Test that LanguageAnalyzer defines the required abstract interface.

    Verifies S-004: Language analyzers follow plugin architecture.
    """
    # LanguageAnalyzer should be abstract
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        LanguageAnalyzer()  # type: ignore


@jig.verifies("S-004")
def test_incomplete_analyzer_cannot_be_instantiated() -> None:
    """Test that incomplete implementations cannot be instantiated.

    Verifies S-004: All analyzers must implement the complete interface.
    """
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        IncompleteAnalyzer()  # type: ignore


@jig.verifies("S-004")
def test_mock_analyzer_interface_compliance() -> None:
    """Test that MockAnalyzer correctly implements the interface.

    Verifies S-004: Concrete analyzers can implement the interface.
    """
    analyzer = MockAnalyzer()

    # Test language_name()
    assert analyzer.language_name() == "mock"
    assert isinstance(analyzer.language_name(), str)

    # Test file_extensions()
    extensions = analyzer.file_extensions()
    assert extensions == [".mock", ".mck"]
    assert isinstance(extensions, list)
    assert all(isinstance(ext, str) for ext in extensions)

    # Test analyze_file()
    result = analyzer.analyze_file(Path("test.mock"))
    assert isinstance(result, dict)
    assert "nodes" in result
    assert "edges" in result
    assert isinstance(result["nodes"], list)
    assert isinstance(result["edges"], list)


@jig.verifies("S-004")
def test_mock_analyzer_returns_language_agnostic_format() -> None:
    """Test that analyzer returns language-agnostic dict format.

    Verifies S-004: Returns language-agnostic dict with nodes/edges.
    """
    analyzer = MockAnalyzer()
    result = analyzer.analyze_file(Path("example.mock"))

    # Verify structure
    assert set(result.keys()) == {"nodes", "edges"}

    # Verify nodes have required fields
    assert len(result["nodes"]) == 1
    node = result["nodes"][0]
    assert "id" in node
    assert "type" in node
    assert "language" in node
    assert node["language"] == "mock"
    assert node["type"] == "module"

    # Verify edges format
    assert isinstance(result["edges"], list)


def test_mock_analyzer_consistent_language_name() -> None:
    """Test that language name is consistent across interface methods."""
    analyzer = MockAnalyzer()

    # Language name from method
    lang_name = analyzer.language_name()

    # Language name in returned nodes
    result = analyzer.analyze_file(Path("test.mock"))
    node_lang = result["nodes"][0]["language"]

    assert lang_name == node_lang
    assert lang_name == "mock"


def test_analyzer_with_multiple_extensions() -> None:
    """Test that analyzer can declare multiple file extensions."""
    analyzer = MockAnalyzer()
    extensions = analyzer.file_extensions()

    assert len(extensions) == 2
    assert ".mock" in extensions
    assert ".mck" in extensions


def test_analyzer_interface_has_required_methods() -> None:
    """Test that LanguageAnalyzer declares all required abstract methods."""
    # Get abstract methods
    abstract_methods = LanguageAnalyzer.__abstractmethods__

    # Verify required methods are present
    assert "language_name" in abstract_methods
    assert "file_extensions" in abstract_methods
    assert "analyze_file" in abstract_methods

    # Verify count (ensure we don't add methods without updating tests)
    assert len(abstract_methods) == 3
