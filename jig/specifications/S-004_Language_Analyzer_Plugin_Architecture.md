---
id: S-004
title: Language Analyzer Plugin Architecture
type: specification
---

# Language Analyzer Plugin Architecture

## Constraints

1. **All analyzers implement LanguageAnalyzer base class**
   - Abstract base class defines required interface
   - Type system enforces implementation of all required methods
   - Enables polymorphic analyzer usage in graph builder

2. **`analyze_file()` returns language-agnostic dict with nodes/edges**
   - Input: `file_path: Path`
   - Output: `Dict[str, List[Dict]]` with keys `"nodes"` and `"edges"`
   - Node dicts must have: `id`, `type`, `language`, plus language-specific metadata
   - Edge dicts must have: `source`, `target`, `type`
   - Analyzer is responsible for generating correct IDs per naming scheme

3. **Language detector routes by file extension**
   - `.py` → PythonAnalyzer
   - `.ts`, `.tsx` → TypeScriptAnalyzer (future)
   - `.java` → JavaAnalyzer (future)
   - `.go` → GoAnalyzer (future)
   - Unknown extensions: skip with debug log (don't fail build)

## Interface Definition

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List

class LanguageAnalyzer(ABC):
    """Base class for language-specific code analyzers."""

    @abstractmethod
    def language_name(self) -> str:
        """Return the language name (e.g., 'python', 'typescript')."""
        pass

    @abstractmethod
    def file_extensions(self) -> List[str]:
        """Return list of file extensions handled by this analyzer (e.g., ['.py', '.pyx'])."""
        pass

    @abstractmethod
    def analyze_file(self, file_path: Path) -> Dict[str, List[Dict]]:
        """
        Analyze a source file and return nodes and edges.

        Returns:
            {
                "nodes": [{"id": "...", "type": "...", "language": "...", ...}, ...],
                "edges": [{"source": "...", "target": "...", "type": "..."}, ...]
            }
        """
        pass
```

## Registry Pattern

```python
class AnalyzerRegistry:
    """Singleton registry for language analyzers."""

    def register(self, analyzer: LanguageAnalyzer) -> None:
        """Register an analyzer for its file extensions."""
        pass

    def get_analyzer(self, file_path: Path) -> Optional[LanguageAnalyzer]:
        """Get appropriate analyzer for file based on extension."""
        pass

    def supported_extensions(self) -> List[str]:
        """Return list of all supported file extensions."""
        pass
```

## Usage Example

```python
# Register analyzers (typically at module import time)
registry = AnalyzerRegistry()
registry.register(PythonAnalyzer())
registry.register(TypeScriptAnalyzer())  # future

# Use in graph builder
for file in source_files:
    analyzer = registry.get_analyzer(file)
    if analyzer:
        result = analyzer.analyze_file(file)
        graph.add_nodes(result["nodes"])
        graph.add_edges(result["edges"])
    else:
        logger.debug(f"No analyzer for {file.suffix}, skipping")
```

## Rationale

The plugin architecture enables:
1. **Language independence**: Core graph infrastructure doesn't know about Python, TypeScript, etc.
2. **Easy extension**: Add new language by implementing one class, no changes to core
3. **Testability**: Mock analyzers for testing graph builder logic
4. **Parallel development**: Multiple people can work on different language analyzers independently

This design follows the Strategy pattern: the graph builder delegates language-specific analysis to pluggable analyzer strategies.

## V1 Scope

V1 ships with only `PythonAnalyzer` to validate the architecture. The plugin system is designed for future expansion but not used for multiple languages initially.

## Non-Goals (V1)

- Mixed-language project support (e.g., Python calling TypeScript via RPC): tracked at module level only
- Cross-language type compatibility: deferred to V2+
- Language auto-detection beyond file extension: deferred to V2+ (would handle shebangs, magic comments)
