
Code Sharing Analysis: Implementation-Graph vs Verification-Graph

  Summary

  | Category             | Component                      | Reusability | Notes                               |
  |----------------------|--------------------------------|-------------|-------------------------------------|
  | Core Infrastructure  | Graph class                    | 100%        | Completely generic                  |
  |                      | NDJSONWriter                   | 100%        | Completely generic                  |
  |                      | write_ndjson()                 | 100%        | Generic wrapper                     |
  | Hashing              | compute_hash()                 | 100%        | Generic                             |
  |                      | hash_function()                | 100%        | Works for test functions too        |
  |                      | hash_test()                    | 100%        | Already exists, calls hash_function |
  |                      | git_blob_hash()                | 100%        | Generic file hashing                |
  | Builder Pattern      | GraphBuilder                   | 90%         | Same pattern, different defaults    |
  | Registry             | AnalyzerRegistry               | 100%        | Can register test analyzer          |
  | Base Classes         | LanguageAnalyzer               | 95%         | Minor interface extension           |
  |                      | ParseError                     | 100%        | Generic error class                 |
  | Decorator Extraction | _extract_implements_decorators | 95%         | Clone for @jig.verifies             |
  |                      | _validate_spec_id              | 100%        | Same validation                     |
  | File Discovery       | Discovery logic                | 70%         | Different patterns                  |
  | AST Visitor          | PythonStructureVisitor         | 30%         | Much simpler for tests              |
  | File Analyzer        | PythonAnalyzer.analyze_file()  | 20%         | Mostly impl-specific                |

  ---
  Detailed Breakdown

  1. 100% Reusable - Use As-Is

  src/jig/impl_graph/graph.py          → Use directly for verification graph
  src/jig/impl_graph/ndjson_writer.py  → Use directly for verification graph
  src/jig/hashing.py                   → Use hash_test() directly

  Graph class (93 lines) - Completely generic:
  class Graph:
      nodes: List[Dict[str, Any]]
      edges: List[Dict[str, Any]]
      # Methods: add_node, add_edge, add_nodes, add_edges, node_count, edge_count, get_nodes, get_edges, clear

  NDJSONWriter (142 lines) - Graph-type agnostic:
  - Writes metadata line
  - Sorts nodes by ID
  - Sorts edges by (source, target, type)
  - Deterministic output

  2. Highly Reusable - Parameterize or Subclass

  GraphBuilder pattern (220 lines) - Can be generalized:

  | Aspect             | Implementation-Graph | Verification-Graph   | Solution  |
  |--------------------|----------------------|----------------------|-----------|
  | Default source dir | src/                 | tests/               | Parameter |
  | File patterns      | **/*.py              | test_*.py, *_test.py | Parameter |
  | Exclude patterns   | ["**/test_*.py"]     | ["__pycache__"]      | Parameter |
  | Analyzer type      | PythonAnalyzer       | TestAnalyzer         | Registry  |

  Option A: Parameterize existing GraphBuilder
  builder = GraphBuilder(
      project_root=root,
      source_dir=root / "tests",
      file_patterns=["test_*.py", "*_test.py"],  # NEW
  )

  Option B: Create thin subclass
  class VerificationGraphBuilder(GraphBuilder):
      def __init__(self, project_root, test_dir=None):
          super().__init__(project_root, source_dir=test_dir or project_root / "tests")
          self.registry.register(TestAnalyzer(project_root))  # Different analyzer

  3. Clone & Modify - 95% Similar

  Decorator extraction - Nearly identical for @jig.verifies:

  | Current (@jig.implements)        | Verification (@jig.verifies)   |
  |----------------------------------|--------------------------------|
  | _extract_implements_decorators() | _extract_verifies_decorators() |
  | Looks for implements             | Looks for verifies             |
  | Returns implements_specs         | Returns verifies_specs         |
  | Same spec ID validation          | Same spec ID validation        |

  Changes needed:
  # Line 345: "implements" → "verifies"
  # Line 352: "implements" → "verifies"
  # Line 333: implements_specs → verifies_specs

  Recommendation: Extract to shared utility:
  def _extract_jig_decorator(node, decorator_name: str) -> List[str]:
      """Extract @jig.{decorator_name}() arguments."""
      # Generic implementation

  4. Simpler for Verification - New Code Needed

  Test file discovery - Different patterns but similar logic:

  # Current (impl_graph/builder.py)
  def _discover_files(self, exclude_patterns):
      for ext in self.registry.supported_extensions():
          for file_path in self.source_dir.rglob(f"**/*{ext}"):
              # ...

  # Verification-specific
  def discover_test_files(test_dir: Path) -> List[Path]:
      patterns = ["test_*.py", "*_test.py"]
      for pattern in patterns:
          for file_path in test_dir.rglob(pattern):
              # ...

  TestAnalyzer - Much simpler than PythonAnalyzer:

  | PythonAnalyzer (~480 lines) | TestAnalyzer (~100 lines)  |
  |-----------------------------|----------------------------|
  | Module nodes                | ❌ Not needed               |
  | Class nodes                 | ❌ Not needed (or minimal)  |
  | Function nodes              | ✅ Test function nodes only |
  | Import tracking             | ❌ Not needed               |
  | Call tracking               | ❌ Not needed               |
  | Inheritance                 | ❌ Not needed               |
  | Containment edges           | ❌ Not needed               |
  | @jig.implements             | @jig.verifies              |
  | Complex edge building       | Simple T→S edges only      |

  ---
  Recommended Architecture

  src/jig/
  ├── common/                    # NEW: Shared infrastructure
  │   ├── __init__.py
  │   ├── graph.py              # Move from impl_graph (100% shared)
  │   ├── ndjson_writer.py      # Move from impl_graph (100% shared)
  │   └── decorator_utils.py    # NEW: Extract decorator parsing
  │
  ├── hashing.py                # Keep as-is (100% shared)
  │
  ├── impl_graph/               # Implementation graph (existing)
  │   ├── builder.py           # Uses common/graph.py
  │   ├── analyzers/
  │   │   ├── python.py        # Full analyzer
  │   │   └── python_visitor.py
  │   └── ...
  │
  └── verification_graph/       # NEW: Verification graph
      ├── __init__.py
      ├── builder.py           # Thin wrapper, uses common/graph.py
      ├── discovery.py         # Test file discovery
      └── analyzer.py          # Simple test analyzer (~100 lines)

  OR (simpler, no refactoring):

  src/jig/
  ├── impl_graph/              # Existing (unchanged)
  │   ├── graph.py            # Import from here
  │   ├── ndjson_writer.py    # Import from here
  │   └── ...
  │
  └── verification_graph/      # NEW
      ├── __init__.py
      ├── builder.py          # Import Graph, write_ndjson from impl_graph
      ├── discovery.py        # Test-specific discovery
      └── analyzer.py         # Simple test analyzer

  ---
  Code Reuse Summary Chart

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                    CODE REUSE BREAKDOWN                                  │
  ├─────────────────────────────────────────────────────────────────────────┤
  │                                                                         │
  │  ████████████████████████████████████████  100% Reusable (420 lines)   │
  │  ┌────────────────────────────────────────┐                            │
  │  │ Graph class              (93 lines)   │                            │
  │  │ NDJSONWriter            (142 lines)   │                            │
  │  │ hashing.py              (166 lines)   │                            │
  │  │ ParseError               (19 lines)   │                            │
  │  └────────────────────────────────────────┘                            │
  │                                                                         │
  │  ████████████████████████  90% Reusable (180 lines → ~20 new)          │
  │  ┌────────────────────────────────────────┐                            │
  │  │ GraphBuilder pattern    (180 lines)   │ → Parameterize             │
  │  │ AnalyzerRegistry        (176 lines)   │ → Use directly             │
  │  │ LanguageAnalyzer base    (86 lines)   │ → Extend or use            │
  │  └────────────────────────────────────────┘                            │
  │                                                                         │
  │  ████████████  30% Reusable (480 lines → ~100 new)                     │
  │  ┌────────────────────────────────────────┐                            │
  │  │ PythonAnalyzer          (480 lines)   │ → TestAnalyzer ~100 lines  │
  │  │ PythonStructureVisitor  (479 lines)   │ → TestVisitor ~80 lines    │
  │  │ decorator extraction     (60 lines)   │ → Clone for @jig.verifies  │
  │  └────────────────────────────────────────┘                            │
  │                                                                         │
  │  ████  Verification-Specific (New code ~200 lines total)               │
  │  ┌────────────────────────────────────────┐                            │
  │  │ Test discovery           (~50 lines)  │                            │
  │  │ Test analyzer           (~100 lines)  │                            │
  │  │ CLI integration          (~50 lines)  │                            │
  │  └────────────────────────────────────────┘                            │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  TOTAL EXISTING CODE:  ~1,500 lines in impl_graph
  REUSABLE DIRECTLY:    ~600 lines (40%)
  NEW CODE NEEDED:      ~200-250 lines

  ---
  Key Insight

  The verification-graph is dramatically simpler than implementation-graph because:

  5. No structural analysis - Just need test functions, not modules/classes/inheritance
  6. No call graph - Just decorator → spec edges
  7. Single edge type - Only T→S (verifies), not imports/calls/extends/contains
  8. Simple discovery - Standard test patterns, not general source files

  Estimate:
  - With code reuse: 200-250 lines of new code
  - Without code reuse: 800-1000 lines (duplicating patterns)

  The verification-graph should take ~6-8 hours instead of the estimated 10-14 hours in B010 by leveraging
  existing infrastructure.