# Implementation Graph Discovery Tool

_A Multi-Language Static Analysis Engine for JIG Alignment Graphs_

**Date:** 2025-11-26
**Status:** Approved - Ready for Implementation
**Related:** AG014 (Implementation & Verification Graphs), AG015 (Feasibility), AG018 (Storage Strategy)

---

## Executive Summary

This document proposes a static analysis tool that discovers implementation structure from codebases and generates `jig/graph-implementation.ndjson`. The tool will:

1. **Parse source files** using language-specific analyzers (Python in V1)
2. **Extract code structure**: modules, classes, functions, and their relationships
3. **Discover `@jig.implements()` decorators** linking code to specifications
4. **Build dependency graph**: imports, calls, inheritance, containment
5. **Generate language-agnostic NDJSON output** for cross-language projects

**V1 Target Language:** Python only
**V1 Performance:** <2s for 10K LOC
**V1 Accuracy:** 90%+ for typed Python code
**Output Format:** NDJSON (one node per line, sorted by ID)
**Architecture:** Extensible for future languages (TypeScript, Java, Go, etc.)

---

## Scope Decisions

### What's IN Scope (V1)

✅ **Code structure discovery**
- Modules, classes, functions
- Import statements
- Direct function calls (`func()`, `module.func()`)
- Inheritance relationships
- Method containment (class → methods)

✅ **Decorator extraction**
- `@jig.implements("S-XXX-NNN")` linking code to specs

✅ **External dependency tracking**
- Package-level imports only (e.g., `import networkx`)

✅ **Deterministic NDJSON output**
- Sorted by ID for stable git diffs
- Fail-fast error handling (strict mode)

✅ **Multi-language architecture**
- Plugin-based analyzer framework
- Language-agnostic graph schema

### What's OUT of Scope (V1)

❌ **Brick detection** - Removed from scope
❌ **Brick boundary violations** - Removed from scope
❌ **Code metrics** (LOC, complexity) - Removed from scope
❌ **File hash tracking / incremental updates** - Removed from scope
❌ **Method call inference** - Direct calls only (no type inference)
❌ **Data flow analysis** - Not needed for V1

**Rationale:** Focus on core graph discovery. Ship fast, iterate based on real usage.

---

## Core Capabilities

### 1. Code Structure Discovery

**Input:** Python source files in `src/` (configurable)

**Extracts:**

#### Modules (one per `.py` file)
- **ID**: `M-<dotted.module.path>` (e.g., `M-jig.core.graph`)
- **File path**: Absolute path to source file
- **Imports**: List of imported module IDs
- **Exports**: Classes and functions defined in module
- **Language**: `python` (for multi-language support)

#### Classes
- **ID**: `C-<dotted.module.path>.<ClassName>` (e.g., `C-jig.core.graph.Graph`)
- **Module**: Parent module ID
- **File path**: Source file location
- **Parent classes**: Inheritance (list of class IDs)
- **Methods**: List of method function IDs
- **Implements**: Spec IDs from `@jig.implements()` decorators

#### Functions (and methods)
- **ID**: `F-<dotted.module.path>.<FunctionName>` or `F-<...>.<ClassName>.<method_name>`
- **Parent**: Class ID (if method) or module ID (if module-level function)
- **File path**: Source file location
- **Signature**: Function signature string (if type-hinted)
- **Calls**: List of function IDs called (direct calls only)
- **Implements**: Spec IDs from `@jig.implements()` decorators

#### External Modules (third-party packages)
- **ID**: `M-<package_name>` (e.g., `M-networkx`)
- **Type**: `external_module`
- **Language**: `python`

**Example nodes:**
```json
{"id":"M-jig.core.graph","type":"module","language":"python","file":"src/jig/core/graph.py","imports":["M-jig.core.parser","M-jig.utils.io"],"exports":["C-jig.core.graph.Graph","F-jig.core.graph.load_graph"]}
{"id":"C-jig.core.graph.Graph","type":"class","language":"python","module":"M-jig.core.graph","file":"src/jig/core/graph.py","line":45,"extends":[],"methods":["F-jig.core.graph.Graph.load_from_dir"],"implements":["S-GRAPH-002"]}
{"id":"F-jig.core.graph.Graph.load_from_dir","type":"function","language":"python","parent":"C-jig.core.graph.Graph","file":"src/jig/core/graph.py","line":89,"signature":"load_from_dir(cls, intent_dir: Path) -> Graph","implements":["S-GRAPH-002"]}
{"id":"M-networkx","type":"external_module","language":"python"}
```

---

### 2. Decorator Extraction

**Discovers `@jig.implements()` decorators:**

```python
from jig import implements

@jig.implements("S-GRAPH-002")
def load_from_dir(cls, intent_dir: Path) -> Graph:
    """Load graph from directory of markdown files."""
    ...
```

**Extracts:**
- Single spec: `@jig.implements("S-AUTH-001")` → `"implements": ["S-AUTH-001"]`
- Multiple specs: `@jig.implements("S-A-001", "S-A-002")` → `"implements": ["S-A-001", "S-A-002"]`
- Validation: Warn if spec IDs don't match pattern `S-*` 

**Decorator inheritance:**
- If class has `@jig.implements()`, it applies to the class node (not methods)
- Methods have their own decorators if present

**Example:**
```python
@jig.implements("S-AUTH-001")
class Authenticator:

    @jig.implements("S-AUTH-002")  # Method-level decorator
    def validate_token(self, token: str) -> bool:
        ...
```

Results in:
```json
{"id":"C-auth.Authenticator","type":"class","implements":["S-AUTH-001"]}
{"id":"F-auth.Authenticator.validate_token","type":"function","implements":["S-AUTH-002"]}
```

---

### 3. Dependency Graph Construction

**Edges extracted:**

#### 1. Import edges (`M-A imports M-B`)
```json
{"source":"M-jig.core.graph","target":"M-jig.core.parser","type":"import","line":8}
{"source":"M-jig.core.graph","target":"M-networkx","type":"import","line":10}
```

**Accuracy:** 99%+ (explicit in source)

---

#### 2. Call edges (`F-A calls F-B`)
```json
{"source":"F-jig.core.graph.Graph.load_from_dir","target":"F-jig.utils.io.read_file","type":"call","line":102}
```

**Scope:** Direct calls only
- `func()` ✓
- `module.func()` ✓
- `obj.method()` ✗ (requires type inference, not in V1)
- Callbacks ✗ (requires data flow analysis, not in V1)

**Accuracy:** 95%+ for direct calls

---

#### 3. Containment edges (`parent contains child`)
```json
{"source":"M-jig.core.graph","target":"C-jig.core.graph.Graph","type":"contains"}
{"source":"C-jig.core.graph.Graph","target":"F-jig.core.graph.Graph.load_from_dir","type":"contains"}
```

**Accuracy:** 99%+ (structural)

---

#### 4. Inheritance edges (`C-A extends C-B`)
```json
{"source":"C-jig.bike.BikeStateCRDT","target":"C-jig.core.CRDTBase","type":"extends"}
```

**Accuracy:** 99%+ (explicit in source)

---

#### 5. Implementation edges (`code implements spec`)
```json
{"source":"F-jig.core.graph.Graph.load_from_dir","target":"S-GRAPH-002","type":"implements"}
```

**Source:** `@jig.implements()` decorators
**Accuracy:** 99%+ (explicit in code)

---

### 4. External Dependency Tracking

**Scope:** Package-level only

**Example:**
```python
import networkx
from pathlib import Path
import yaml
```

**Generates:**
```json
{"id":"M-networkx","type":"external_module","language":"python"}
{"id":"M-pathlib","type":"external_module","language":"python"}
{"id":"M-yaml","type":"external_module","language":"python"}
{"source":"M-jig.core.graph","target":"M-networkx","type":"import","line":10}
{"source":"M-jig.core.graph","target":"M-pathlib","type":"import","line":11}
{"source":"M-jig.core.graph","target":"M-yaml","type":"import","line":12}
```

**Out of scope:**
- ❌ Version tracking (`networkx==3.1`) - Assume venv is correct
- ❌ Symbol tracking (`from networkx import Graph, DiGraph`) - Too granular for V1

---

## Multi-Language Architecture

### Design Principle: Language Analyzers as Plugins

The tool is structured so **any programming language can be added** by implementing a language analyzer plugin. The core graph representation is **language-agnostic**.

```
┌─────────────────────────────────────────────┐
│         jig impl rebuild                    │
│  (orchestrator - language agnostic)         │
└─────────────────┬───────────────────────────┘
                  │
      ┌───────────┴───────────┐
      │   Language Detector   │  (inspects file extensions)
      └───────────┬───────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┐
    │             │             │             │
    ▼             ▼             ▼             ▼
┌────────┐  ┌──────────┐  ┌────────┐  ┌────────┐
│Python  │  │TypeScript│  │  Java  │  │  Go    │
│Analyzer│  │ Analyzer │  │Analyzer│  │Analyzer│
│  (V1)  │  │  (V2)    │  │  (V3)  │  │  (V4)  │
└────┬───┘  └─────┬────┘  └───┬────┘  └───┬────┘
     │            │            │            │
     └────────────┴────────────┴────────────┘
                  │
         ┌────────▼────────────┐
         │  Language-Agnostic  │
         │  Graph Builder      │
         └────────┬────────────┘
                  │
         ┌────────▼────────────┐
         │ NDJSON Writer       │
         │ (deterministic)     │
         └────────┬────────────┘
                  │
                  ▼
        graph-implementation.ndjson
```

---

### Language Analyzer Interface

Each language analyzer implements this interface:

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict

class LanguageAnalyzer(ABC):
    """Base class for language-specific analyzers."""

    @abstractmethod
    def language_name(self) -> str:
        """Return language name (e.g., 'python', 'typescript', 'java')."""
        pass

    @abstractmethod
    def file_extensions(self) -> List[str]:
        """Return list of file extensions this analyzer handles (e.g., ['.py'])."""
        pass

    @abstractmethod
    def analyze_file(self, file_path: Path) -> Dict:
        """
        Analyze a single source file and return language-agnostic nodes/edges.

        Returns:
            {
                "nodes": [
                    {"id": "M-...", "type": "module", "language": "python", ...},
                    {"id": "C-...", "type": "class", "language": "python", ...},
                    {"id": "F-...", "type": "function", "language": "python", ...}
                ],
                "edges": [
                    {"source": "M-...", "target": "M-...", "type": "import", ...},
                    {"source": "F-...", "target": "F-...", "type": "call", ...}
                ]
            }
        """
        pass
```

---

### Python Analyzer (V1)

**Implementation:**
```python
class PythonAnalyzer(LanguageAnalyzer):
    def language_name(self) -> str:
        return "python"

    def file_extensions(self) -> List[str]:
        return [".py"]

    def analyze_file(self, file_path: Path) -> Dict:
        # 1. Parse AST
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        # 2. Extract modules, classes, functions
        visitor = PythonASTVisitor()
        visitor.visit(tree)

        # 3. Return language-agnostic format
        return {
            "nodes": visitor.nodes,
            "edges": visitor.edges
        }
```

**Uses:** Python's built-in `ast` module (AST = Abstract Syntax Tree)

---

### Future Language Analyzers (V2+)

**TypeScript Analyzer:**
- Uses TypeScript Compiler API (`tsc`)
- Extracts modules, classes, functions, interfaces
- Handles ES6 imports, type annotations

**Java Analyzer:**
- Uses JavaParser or Eclipse JDT
- Extracts packages, classes, methods
- Handles Maven/Gradle dependencies

**Go Analyzer:**
- Uses `go/ast` and `go/parser` standard library
- Extracts packages, structs, functions
- Handles go.mod dependencies

**Key point:** All analyzers emit the **same NDJSON schema**, enabling cross-language graphs.

---

## Output Format: NDJSON Schema

### Language-Agnostic Schema

**All nodes have these fields:**
- `id`: Unique identifier (format varies by language)
- `type`: `module`, `class`, `function`, `external_module`
- `language`: `python`, `typescript`, `java`, `go`, etc.
- `file`: Absolute path to source file (optional for external modules)
- `line`: Line number where defined (optional)
- `implements`: Array of spec IDs from `@jig.implements()` (optional)

**Language-specific fields:**
- Python: `signature` (type hints), `extends` (inheritance)
- TypeScript: `interface` (interface implementations)
- Java: `package`, `visibility` (public/private)
- Go: `package`, `receiver` (method receivers)

**Example cross-language graph:**
```json
{"_meta":{"generated":"2025-11-26T12:00:00Z","version":"1.0","languages":["python","typescript"],"total_nodes":1234}}
{"id":"M-jig.core.graph","type":"module","language":"python","file":"src/jig/core/graph.py","imports":["M-jig.utils.io"]}
{"id":"M-frontend.api.client","type":"module","language":"typescript","file":"frontend/src/api/client.ts","imports":["M-axios"]}
{"id":"F-jig.core.graph.load_graph","type":"function","language":"python","parent":"M-jig.core.graph","implements":["S-GRAPH-002"]}
{"id":"F-frontend.api.client.fetchGraph","type":"function","language":"typescript","parent":"M-frontend.api.client","implements":["S-GRAPH-002"]}
```

Backend (Python) and frontend (TypeScript) both implement the same spec!

---

### File Structure

```
Line 1: Metadata (prefixed with "_meta")
Lines 2-N: Nodes (sorted by ID)
Lines N+1-M: Edges
```

**Example:**
```json
{"_meta":{"generated":"2025-11-26T12:00:00Z","version":"1.0","project_root":"/Users/jmeyer/Code/jig","languages":["python"],"total_nodes":667,"total_edges":1845}}
{"id":"C-jig.core.graph.Graph","type":"class","language":"python","module":"M-jig.core.graph","file":"src/jig/core/graph.py","line":45,"extends":[],"methods":["F-jig.core.graph.Graph.load_from_dir"],"implements":["S-GRAPH-002"]}
{"id":"F-jig.core.graph.Graph.load_from_dir","type":"function","language":"python","parent":"C-jig.core.graph.Graph","file":"src/jig/core/graph.py","line":89,"signature":"load_from_dir(cls, intent_dir: Path) -> Graph","implements":["S-GRAPH-002"]}
{"id":"M-jig.core.graph","type":"module","language":"python","file":"src/jig/core/graph.py","imports":["M-jig.core.parser","M-jig.utils.io"],"exports":["C-jig.core.graph.Graph"]}
{"id":"M-networkx","type":"external_module","language":"python"}
{"source":"M-jig.core.graph","target":"M-jig.core.parser","type":"import","line":8}
{"source":"M-jig.core.graph","target":"M-jig.utils.io","type":"import","line":9}
{"source":"F-jig.core.graph.Graph.load_from_dir","target":"F-jig.utils.io.read_file","type":"call","line":102}
{"source":"C-jig.core.graph.Graph","target":"F-jig.core.graph.Graph.load_from_dir","type":"contains"}
```

**Schema rules:**
1. **One JSON object per line** (no pretty-printing)
2. **Nodes sorted by ID** (for stable git diffs)
3. **Edges after nodes** (for easier parsing)
4. **Deterministic output** (same input → same output, same order)

---

## Tool Architecture

### Command-Line Interface

**Primary command:**
```bash
jig impl rebuild [OPTIONS]
```

**Options:**
```
--project-root PATH      Project root directory (default: current dir)
--source-dir PATH        Source directory to scan (default: src/)
--exclude PATTERN        Exclude patterns (default: tests/*, .venv/*, __pycache__/*)
--output PATH            Output file (default: jig/graph-implementation.ndjson)
--language LANG          Language to analyze (default: auto-detect)
--verbose                Show detailed progress
--strict                 Fail on any parse error (default: true)
```

**Example:**
```bash
# Auto-detect Python files, rebuild graph
jig impl rebuild

# Explicit options
jig impl rebuild \
  --project-root ~/Code/jig \
  --source-dir src \
  --exclude "tests/*,*.pyc" \
  --output jig/graph-implementation.ndjson \
  --verbose
```

**Additional commands (future):**
```bash
jig impl validate            # Validate graph consistency
jig impl export --format json  # Convert NDJSON to pretty JSON
jig impl query QUERY         # Run graph query
```

---

### Internal Architecture

**Modules:**

```
src/jig/impl_graph/
  __init__.py

  # Core orchestration
  builder.py              # GraphBuilder - orchestrates the build
  graph.py                # Graph - in-memory graph representation

  # Language analyzers (plugin architecture)
  analyzers/
    __init__.py
    base.py               # LanguageAnalyzer - base class
    python.py             # PythonAnalyzer - AST parsing for Python
    registry.py           # AnalyzerRegistry - manages analyzers
    # Future: typescript.py, java.py, go.py, etc.

  # Decorator extraction
  decorator_extractor.py  # DecoratorExtractor - finds @jig.* decorators

  # I/O
  ndjson_writer.py        # NDJSONWriter - serializes to NDJSON
  ndjson_reader.py        # NDJSONReader - deserializes from NDJSON
```

**Data flow:**
```
Source Files (.py, .ts, .java, ...)
    ↓
Language Detector (by file extension)
    ↓
Python Analyzer (AST → nodes + edges)
    ↓
DecoratorExtractor (@jig.* → implements fields)
    ↓
Graph (in-memory representation)
    ↓
NDJSONWriter (serialize, sort by ID)
    ↓
jig/graph-implementation.ndjson
```

---

### Python API

**For programmatic use:**

```python
from jig.impl_graph import GraphBuilder

# Build graph
builder = GraphBuilder(
    project_root="/path/to/project",
    source_dir="src",
    exclude=["tests/*", ".venv/*"]
)
graph = builder.build()

# Save
graph.save_ndjson("jig/graph-implementation.ndjson")

# Query
functions = graph.get_nodes(type="function")
for func in functions:
    if func.implements:
        print(f"{func.id} implements {func.implements}")

# Get dependencies
deps = graph.get_dependencies("M-jig.core.graph")
print(f"Dependencies: {deps}")
```

---

## Implementation Plan

### Week 1-2: Core Discovery (Python V1)

**Deliverables:**
- [x] `LanguageAnalyzer` base class and registry
- [x] `PythonAnalyzer` - AST parsing for Python
  - Module discovery
  - Class discovery
  - Function discovery
  - Import edges
  - Direct call edges
  - Containment edges
  - Inheritance edges
- [x] `DecoratorExtractor` - finds `@jig.implements()`
- [x] `Graph` - in-memory representation
- [x] `NDJSONWriter` - deterministic serialization
- [x] CLI: `jig impl rebuild`

**Success criteria:**
- Can parse JIG codebase (87 files, 12K LOC) in <2s
- Output `jig/graph-implementation.ndjson` with all modules, classes, functions
- Deterministic output (same input → identical output)
- Test coverage >80%

**Test on:** JIG codebase itself

---

### Week 3: Polish & Validation

**Deliverables:**
- [x] Error handling (fail-fast on parse errors)
- [x] Validation (check spec IDs match pattern `S-*` or `O-*`)
- [x] Documentation (README, CLI help, API docs)
- [x] Unit tests for all components
- [x] Integration test on JIG + ASE codebases

**Success criteria:**
- All parse errors reported with file:line
- Invalid spec IDs flagged with warnings
- Complete documentation
- >80% test coverage

**Test on:** JIG, ASE

---

### Future: Multi-Language Support (V2+)

**Potential additions:**
- [x] TypeScript analyzer
- [x] Java analyzer
- [x] Go analyzer
- [x] Cross-language graph queries
- [x] Visualization export (Mermaid, Graphviz)

---

## Example Output

**For JIG codebase:**

```bash
$ jig impl rebuild --verbose

Implementation Graph Discovery
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/4] Scanning source files...
  Found 87 Python files in src/
  Excluding: tests/ (.venv/, __pycache__/)

[2/4] Detecting languages...
  Python: 87 files

[3/4] Analyzing Python files...
  Parsing AST... ━━━━━━━━━━━━━━━━━━━━━━━━ 100%
  Extracted: 87 modules, 124 classes, 456 functions
  Found 142 @jig.implements annotations
  Created 598 import edges
  Created 523 call edges
  Created 156 containment edges
  Created 67 inheritance edges

[4/4] Writing NDJSON...
  Sorting nodes by ID...
  Writing jig/graph-implementation.ndjson...
  667 nodes, 1344 edges

✓ Build complete in 1.8s

Graph location: jig/graph-implementation.ndjson
```

---

## Success Metrics

**Performance targets:**
| Codebase Size | Build Time |
|---------------|------------|
| 10K LOC       | <2s        |
| 100K LOC      | <20s       |

**Accuracy targets:**
| Metric                  | Target |
|-------------------------|--------|
| Module discovery        | 99%+   |
| Class/function discovery| 98%+   |
| Import edges            | 95%+   |
| Direct call edges       | 90%+   |
| Decorator extraction    | 99%+   |

**Quality targets:**
- Test coverage: >80%
- Deterministic output: 100% (same input → same output)
- NDJSON validity: 100% (every line valid JSON)
- Documentation: Complete CLI help, API docs, examples

---

## Dependencies

**Required:**
- Python 3.10+ (for AST features, pattern matching)
- Standard library: `ast`, `pathlib`, `json`
- Third-party: `click` (for CLI)

**Input artifacts:**
- Python source files in `src/` (or configured directory)
- Intent graph in `jig/intent-graph.json` (for cross-validation, optional)

**Output artifacts:**
- `jig/graph-implementation.ndjson` (committed to git)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Dynamic code unanalyzable** | Missing edges | Document limitations, focus on static code |
| **Call graph incomplete** (no method call inference) | Missing call edges | Start with direct calls (90%+ accurate), add inference in V2 |
| **Large codebases slow** | Poor UX | Profile and optimize, target <2s for 10K LOC |
| **Multi-language complexity** | Delayed V2+ | V1 is Python-only, architecture supports future languages |

---

## Decision Record

Based on user feedback, the following decisions were made:

1. ✅ **No brick detection** - Out of scope for V1
2. ✅ **No brick boundary violations** - Out of scope for V1
3. ✅ **No code metrics** (LOC, complexity) - Out of scope for V1
4. ✅ **No file hash tracking / incremental updates** - Out of scope for V1 (full rebuild every time)
5. ✅ **Direct calls only** - No method call inference (type analysis)
6. ✅ **`@jig.implements()` decorator** - Explicit namespace
7. ✅ **Exclude test code** - Only production code in implementation graph
8. ✅ **Package-level external deps** - No version/symbol tracking
9. ✅ **Manual rebuild** - No git hooks or watch mode
10. ✅ **Output to `jig/`** - Flat directory structure
11. ✅ **Fail-fast error handling** - Strict mode (parse errors stop build)
12. ✅ **Multi-language architecture** - Plugin-based, language-agnostic schema

---

## Next Steps

1. ✅ **Scope approved** - Decisions documented above
2. **Week 1-2:** Implement Python analyzer
3. **Week 3:** Polish, test, document
4. **Week 4:** Deploy V1, dogfood on JIG and ASE
5. **V2+:** Add TypeScript, Java, Go analyzers based on demand

---

**Status:** Ready for implementation.
