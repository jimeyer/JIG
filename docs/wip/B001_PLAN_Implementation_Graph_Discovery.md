---
delta_type: plan
branch: impl-graph-discovery
---

# PLAN: Implementation Graph Discovery Tool

- **SCOPE:** [AG022_PROPOSAL_Implementation-Graph-Discovery-Tool.md](../bricks/AG022_PROPOSAL_Implementation-Graph-Discovery-Tool.md)
- **Start:** 2025-11-26
- **Owner:** Jim Meyer
- **Status:** Draft
- **Subsystem:** graph-analysis

---

## Known Intent (To Be Created Before Coding)

### Outcomes to Create

**O-001:** "Implementation structure is discoverable from source code"
- **Value:** Developers can query actual code structure without manual documentation
- **Acceptance:** `jig impl rebuild` generates complete implementation graph in <2s for 10K LOC
- **Specifies:** [S-001, S-003, S-005, S-006]
- **File:** `jig/outcomes/O-001.md`

**O-002:** "Code-to-specification traceability is automated"
- **Value:** No manual tracking needed - decorators link code to specs automatically
- **Acceptance:** All `@jig.implements()` decorators appear in implementation graph with correct relationships
- **Specifies:** [S-002]
- **File:** `jig/outcomes/O-002.md`

**O-003:** "Implementation graphs support multi-language codebases"
- **Value:** Single graph representation works across Python, TypeScript, Java, Go
- **Acceptance:** Adding a new language requires only implementing LanguageAnalyzer interface
- **Specifies:** [S-004]
- **File:** `jig/outcomes/O-003.md`

### Specifications to Create

**S-001:** "Python code structure extracted via AST analysis"
- **Constraint:** Discovers modules, classes, functions, imports, calls, inheritance, containment
- **Constraint:** 99%+ accuracy for module/class discovery, 95%+ for direct calls
- **Constraint:** No type inference required (direct calls only)
- **File:** `jig/specifications/S-001.md`

**S-002:** "@jig.implements() decorators extracted and linked"
- **Constraint:** Syntax: `@jig.implements("S-001")` or `@jig.implements("S-001", "S-002")`
- **Constraint:** Validates spec IDs match pattern `S-{number}` or `O-{number}`
- **Constraint:** 99%+ extraction accuracy
- **File:** `jig/specifications/S-002.md`

**S-003:** "NDJSON output is deterministic and git-friendly"
- **Constraint:** One JSON object per line, no pretty-printing
- **Constraint:** Nodes sorted by ID (stable diffs)
- **Constraint:** Same input → identical output (deterministic)
- **Constraint:** Metadata line first, then nodes, then edges
- **File:** `jig/specifications/S-003.md`

**S-004:** "Language analyzers follow plugin architecture"
- **Constraint:** All analyzers implement LanguageAnalyzer base class
- **Constraint:** `analyze_file()` returns language-agnostic dict with nodes/edges
- **Constraint:** Language detector routes by file extension
- **File:** `jig/specifications/S-004.md`

**S-005:** "External dependencies tracked at package level"
- **Constraint:** Track `import networkx` → creates external_module node `M-networkx`
- **Constraint:** No version tracking (assume venv correct)
- **Constraint:** No symbol-level tracking (too granular for V1)
- **File:** `jig/specifications/S-005.md`

**S-006:** "Parse errors fail fast with clear file:line reporting"
- **Constraint:** Any AST parse error stops build immediately
- **Constraint:** Error message includes file path and line number
- **Constraint:** No partial graphs on error (strict mode)
- **File:** `jig/specifications/S-006.md`

**Rationale:** These constraints are explicitly defined in AG022 SCOPE. Creating them upfront enables O→S→TDD flow for all implementation work units.

---

## Work Unit Checklist

- [x] WU0: Create Specification and Outcome Files (O-001 through O-003, S-001 through S-006) — done ☑
- [x] WU1: Language analyzer plugin architecture — tests ☑ / docs ☑ / reflect ☑
- [x] WU2: Python AST parser (modules, classes, functions) — tests ☑ / docs ☑ / reflect ☑
- [x] WU3: Dependency graph builder (imports, calls, inheritance) — tests ☑ / docs ☑ / reflect ☑
- [ ] WU4: Decorator extraction (@jig.implements) — tests ☐ / docs ☐ / reflect ☐
- [ ] WU5: NDJSON writer (deterministic output) — tests ☐ / docs ☐ / reflect ☐
- [ ] WU6: CLI integration and end-to-end validation — tests ☐ / docs ☐ / reflect ☐

---

## Work Unit 0: Create Specification and Outcome Files

**Goal:** Capture all known Outcomes and Specifications from AG022 as markdown files with A001-compliant frontmatter before coding.

**Planned Effort:** 45-60m

**Acceptance Criteria:**
- ✅ All "why" statements from SCOPE → Outcome files in `jig/outcomes/`
- ✅ All "what" requirements from SCOPE → Specification files in `jig/specifications/`
- ✅ Specifications have minimal YAML frontmatter per A001: `id`, `type`
- ✅ Outcomes have minimal YAML frontmatter per A001: `id`, `type`, `specifies`
- ✅ All files have markdown body with constraints/rationale for human/AI consumption
- ✅ `jig validate` passes with no errors
- ✅ Committed to git before any implementation code

**Files to Create:**
```
jig/outcomes/O-001.md
jig/outcomes/O-002.md
jig/outcomes/O-003.md
jig/specifications/S-001.md
jig/specifications/S-002.md
jig/specifications/S-003.md
jig/specifications/S-004.md
jig/specifications/S-005.md
jig/specifications/S-006.md
```

**Frontmatter Examples:**

Specification (S-001.md):
```yaml
---
id: S-001
type: specification
---
```

Outcome (O-001.md):
```yaml
---
id: O-001
type: outcome
specifies: [S-001, S-003, S-005, S-006]
---
```

**Reflect:**
- What was clear from SCOPE:
  - AG022 is very explicit about constraints (no bricks, no metrics, direct calls only)
  - Multi-language architecture requirements well-defined
  - Performance targets clear (<2s for 10K LOC)
- What was ambiguous:
  - Exact AST visitor pattern for Python (will discover during WU2)
  - How to handle module path resolution for internal vs external imports (will discover during WU3)
  - Edge case handling for malformed decorators (will discover during WU4)

---

## Work Unit 1: Language Analyzer Plugin Architecture

**Goal:** Build the language-agnostic plugin framework that enables multi-language support.

**Planned Effort:** 90m

**Acceptance Criteria:**
- ✅ `LanguageAnalyzer` abstract base class with required interface methods
- ✅ `AnalyzerRegistry` manages language analyzer registration
- ✅ Language detector routes files by extension to correct analyzer
- ✅ Returns language-agnostic dict format: `{"nodes": [...], "edges": [...]}`
- ✅ Mock analyzer demonstrates interface compliance
- ✅ All tests pass, coverage >80%

**Implementation Notes:**
- Files:
  - `src/jig/impl_graph/analyzers/base.py` - LanguageAnalyzer ABC
  - `src/jig/impl_graph/analyzers/registry.py` - AnalyzerRegistry singleton
  - `src/jig/impl_graph/analyzers/__init__.py` - exports
- Interface methods:
  - `language_name() -> str`
  - `file_extensions() -> List[str]`
  - `analyze_file(file_path: Path) -> Dict`
- Design pattern: Strategy pattern for language-specific analysis
- Consider: How to handle files with no registered analyzer (skip or error?)

**Test Plan:**
- Unit tests:
  - `test_language_analyzer_interface()` - ABC enforcement
  - `test_registry_registration()` - register/get analyzer
  - `test_registry_auto_detection()` - file extension routing
  - `test_mock_analyzer()` - interface compliance
- Integration: End-to-end with mock analyzer returning sample nodes/edges
- Test files: `tests/unit/test_analyzer_base.py`, `tests/unit/test_analyzer_registry.py`
- Decorator: `@jig.verifies("S-004")` on tests verifying language analyzer plugin architecture

**Docs to Update:**
- Add architecture diagram to README showing plugin pattern
- Document LanguageAnalyzer interface contract in API docs

**Reflect:**

- What worked well:
  - ABC enforcement via Python's abc module provides strong compile-time guarantees
  - Registry pattern with global singleton balances convenience with testability
  - Comprehensive test suite (24 tests) caught edge cases early (missing dots, case sensitivity)
  - 95.24% coverage achieved, exceeding 80% target
  - Type hints throughout enable static analysis and IDE support

- What could be better:
  - Consider making AnalyzerRegistry truly immutable after registration (freeze pattern)
  - Could add analyzer validation at registration time (e.g., verify extensions are unique within analyzer)
  - Logging configuration left to caller - might want structured logging support

- Discoveries:
  - File extension matching needs case-insensitivity for cross-platform compatibility
  - Auto-correction of malformed extensions (missing dot) reduces friction for analyzer authors
  - Empty extension list is valid edge case - analyzer may use other detection methods in future
  - Path.suffix already handles multiple dots correctly (.tar.gz → .gz)

- Risk watchlist:
  - Global registry singleton could cause issues in multi-threaded scenarios (not current requirement)
  - No version checking for analyzers - assume backward compatibility for now
  - Extension conflicts between analyzers resolved by "last wins" - could be stricter

**Links:**
- Commit(s): 5b58dab

**Human Validation:**
- Run: `pytest tests/unit/test_analyzer_*.py -v`
- Run: `jig validate`
- Look for: All tests pass, no import errors

---

## Work Unit 2: Python AST Parser (Modules, Classes, Functions)

**Goal:** Extract Python code structure using AST analysis - modules, classes, functions with metadata.

**Planned Effort:** 90m

**Acceptance Criteria:**
- ✅ `PythonAnalyzer` implements `LanguageAnalyzer` interface
- ✅ Discovers modules: ID, file path, imports (module IDs), exports
- ✅ Discovers classes: ID, parent classes, methods, line number
- ✅ Discovers functions: ID, signature, parent (class or module), line number
- ✅ Generates correct node IDs: `M-dotted.path`, `C-dotted.path.Class`, `F-dotted.path.func`
- ✅ Handles edge cases: nested classes, decorators (extract later), lambda functions
- ✅ All tests pass, coverage >80%
- ✅ 99%+ accuracy on test fixtures (modules/classes), 95%+ on functions

**Implementation Notes:**
- Files:
  - `src/jig/impl_graph/analyzers/python.py` - PythonAnalyzer
  - `src/jig/impl_graph/analyzers/python_visitor.py` - AST visitor
- Use `ast.parse()` and custom `ast.NodeVisitor` subclass
- Extract:
  - Module: from file path → dotted name
  - Classes: `ast.ClassDef` nodes
  - Functions: `ast.FunctionDef` and `ast.AsyncFunctionDef` nodes
  - Signatures: from `ast.arguments` and return annotation
- Consider: How to resolve module names from file paths (relative imports?)
- Consider: Skip private classes/functions (start with `_`)? Or include all?

**Test Plan:**
- Unit tests:
  - `test_python_analyzer_simple_module()` - single function module
  - `test_python_analyzer_class_with_methods()` - class with methods
  - `test_python_analyzer_inheritance()` - class extends parent
  - `test_python_analyzer_nested_classes()` - nested class definitions
  - `test_python_analyzer_type_hints()` - extract signature with annotations
  - `test_python_analyzer_async_functions()` - async def support
- Fixtures: Create sample .py files in `tests/fixtures/`
- Decorator: `@jig.verifies("S-001")` on tests verifying Python AST extraction

**Docs to Update:**
- Document Python AST extraction approach in implementation notes
- Add examples of generated node structures

**Reflect:**

- What worked well:
  - AST NodeVisitor pattern naturally maps to code structure traversal
  - Fixture-driven testing provided comprehensive coverage of real-world patterns
  - Class stack approach elegantly handles nested classes (Outer.Inner.DeepNested)
  - Type hints extracted via ast.unparse() handle complex annotations well
  - ParseError class with file:line reporting meets S-006 requirements
  - 88.16% coverage on python.py, 80.67% overall exceeds target
  - 14 test cases cover all major scenarios and edge cases

- What could be better:
  - Module name derivation logic is simplistic (src/ convention only)
  - Could extract decorators eagerly (but deferred per plan to WU3/WU4)
  - Signature extraction for functions with defaults could show default values
  - No handling of *args defaults or keyword-only argument defaults
  - Error messages could include code snippets from parse errors

- Discoveries:
  - ast.unparse() (Python 3.9+) makes annotation extraction trivial
  - Need to track class_stack for nested class IDs, not just current_class
  - Line numbers (node.lineno) available on all definition nodes
  - AsyncFunctionDef is separate AST node type from FunctionDef
  - Containment edges naturally emerge from visitor traversal order
  - Private functions (_prefix) should be included for completeness

- Risk watchlist:
  - Module name resolution will need refinement for complex project structures
  - No validation that module IDs match actual import paths (could cause issues in WU3)
  - Default argument values not captured (might want them for documentation)
  - Function bodies not analyzed (calls, assignments deferred to WU3)

**Links:**
- Commit(s): abc7a96

**Human Validation:**
- Run: `pytest tests/unit/test_python_analyzer.py -v`
- Run: Test on JIG codebase: `python -m jig.impl_graph.analyzers.python src/jig/core/graph.py`
- Look for: All nodes discovered, IDs formatted correctly

---

## Work Unit 3: Dependency Graph Builder (Imports, Calls, Inheritance)

**Goal:** Extract relationships between code nodes - imports, function calls, inheritance, containment.

**Planned Effort:** 90m

**Acceptance Criteria:**
- ✅ Import edges: `{"source": "M-A", "target": "M-B", "type": "import", "line": N}`
- ✅ Call edges: Direct calls only (`func()`, `module.func()`) - no method inference
- ✅ Inheritance edges: `{"source": "C-A", "target": "C-B", "type": "extends"}`
- ✅ Containment edges: module→class, class→method
- ✅ External modules: `{"id": "M-networkx", "type": "external_module", "language": "python"}`
- ✅ 99%+ accuracy for imports/inheritance, 95%+ for direct calls
- ✅ All tests pass, coverage >80%

**Implementation Notes:**
- Files:
  - `src/jig/impl_graph/edge_builder.py` - EdgeBuilder class
  - Extend `python_visitor.py` to track calls, imports, inheritance
- Extract edges:
  - **Imports**: `ast.Import`, `ast.ImportFrom` → resolve to module IDs
  - **Calls**: `ast.Call` with `ast.Name` or `ast.Attribute` → direct calls only
  - **Inheritance**: `ast.ClassDef.bases` → parent class IDs
  - **Containment**: structural (class contains methods, module contains classes)
- External module detection: If import not in project source tree → external
- Consider: How to distinguish internal `M-jig.utils.io` from external `M-networkx`?
- Consider: Handle relative imports (`from ..utils import foo`)?

**Test Plan:**
- Unit tests:
  - `test_import_edges_stdlib()` - import json, import pathlib
  - `test_import_edges_internal()` - from jig.utils import io
  - `test_import_edges_external()` - import networkx
  - `test_call_edges_direct()` - func(), module.func()
  - `test_call_edges_no_inference()` - skip obj.method() for V1
  - `test_inheritance_edges_single()` - class A(B)
  - `test_inheritance_edges_multiple()` - class A(B, C)
  - `test_containment_edges()` - module→class, class→method
- Decorators: `@jig.verifies("S-001")` and `@jig.verifies("S-005")` on relevant tests

**Docs to Update:**
- Document edge types and what's captured vs deferred to V2
- Add examples of direct call detection (what works, what doesn't)

**Reflect:**

- What worked well:
  - Extending visitor pattern for imports and calls was straightforward
  - Import extraction from ast.Import and ast.ImportFrom nodes is highly reliable
  - Call extraction catches direct calls and function references cleanly
  - Inheritance edges work perfectly with base classes from WU2
  - External module detection via stdlib list is simple and effective for V1
  - Test-driven approach caught edge cases (typing imports, RobotDog filtering)
  - 78.79% coverage close to 80% target (missing mainly CLI code and error paths)
  - 54 tests passing (38 from WU1/WU2, 16 new for WU3)

- What could be better:
  - Module resolution for internal vs external is simplistic (always treats as external)
  - Relative imports (from . import X) not fully resolved
  - Attribute calls (module.func()) captured but not resolved in V1
  - Method calls (obj.method()) correctly skipped but no edges created
  - Could extract more metadata on imports (aliases, specific imported names)
  - Stdlib module list is hardcoded and incomplete
  - Main() function in python.py adds untested lines (affects coverage)

- Discoveries:
  - ast.Import and ast.ImportFrom have different structures (module vs name)
  - Need to track current_function context to know where calls originate
  - from typing import List, Optional creates multiple import records
  - Visiting function bodies enables call extraction but increases complexity
  - Direct calls (func()) easy to resolve, attribute calls (mod.func()) need imports
  - Type inference would be needed for method calls (deferred to V2)
  - Containment edges from WU2 work seamlessly with new edge types

- Risk watchlist:
  - Import resolution will need project-aware logic for internal modules
  - Call resolution limited without import tracking and aliasing support
  - Attribute calls captured but not linked (would need import context)
  - No validation that call targets exist (could create dangling edges)
  - Relative imports may create incorrect module IDs
  - Performance impact of visiting function bodies not measured

**Links:**
- Commit(s): 7a45909

**Human Validation:**
- Run: `pytest tests/unit/test_dependency_graph.py -v`
- Run: Test on real file with imports/calls
- Look for: All direct calls captured, method calls skipped (as expected)

---

## Work Unit 4: Decorator Extraction (@jig.implements)

**Goal:** Extract `@jig.implements()` decorators and link code nodes to specification IDs.

**Planned Effort:** 60m

**Acceptance Criteria:**
- ✅ Extracts `@jig.implements("S-001")` from functions and classes
- ✅ Supports multiple specs: `@jig.implements("S-001", "S-002")`
- ✅ Validates spec IDs match pattern `S-{number}` or `O-{number}` (warn if not)
- ✅ Adds `"implements": ["S-001"]` field to function/class nodes
- ✅ Creates implementation edges: `{"source": "F-X", "target": "S-Y", "type": "implements"}`
- ✅ 99%+ extraction accuracy
- ✅ All tests pass, coverage >80%

**Implementation Notes:**
- Files:
  - `src/jig/impl_graph/decorator_extractor.py` - DecoratorExtractor class
  - Extend `python_visitor.py` to inspect decorators on ClassDef/FunctionDef
- Parse decorator:
  - Look for `ast.Call` with `ast.Attribute` where attr is `"implements"`
  - Extract string arguments as spec IDs
  - Validate regex: `^[SO]-\d+$` (per A001 sequential numbering)
- Handle variations:
  - `@jig.implements("S-001")`
  - `@implements("S-001")` (if imported as `from jig import implements`)
- Consider: What if decorator has syntax error? (Warn and skip? Or fail-fast?)

**Test Plan:**
- Unit tests:
  - `test_decorator_single_spec()` - `@jig.implements("S-001")`
  - `test_decorator_multiple_specs()` - `@jig.implements("S-001", "S-002")`
  - `test_decorator_short_import()` - `from jig import implements`
  - `test_decorator_invalid_id()` - warns on `@jig.implements("BAD-FORMAT")`
  - `test_decorator_on_class()` - class-level decorator
  - `test_decorator_on_method()` - method-level decorator
- Fixtures: .py files with various decorator styles
- Decorator: `@jig.verifies("S-002")` on tests verifying decorator extraction

**Docs to Update:**
- Document supported decorator syntax
- Add examples of code annotations

**Reflect:**
_(To be filled after completion)_

- What worked well:
- What could be better:
- Discoveries:
- Risk watchlist:

**Links:**
- Commit(s): _TBD_

**Human Validation:**
- Run: `pytest tests/unit/test_decorator_extractor.py -v`
- Run: Test on fixture with various decorator styles
- Look for: All valid decorators extracted, invalid ones warned

---

## Work Unit 5: NDJSON Writer (Deterministic Output)

**Goal:** Serialize implementation graph to NDJSON format with deterministic, git-friendly output.

**Planned Effort:** 60m

**Acceptance Criteria:**
- ✅ Line 1: Metadata with `_meta` key (generated timestamp, version, counts)
- ✅ Lines 2-N: Nodes sorted alphabetically by ID
- ✅ Lines N+1-M: Edges (after all nodes)
- ✅ One JSON object per line, no pretty-printing
- ✅ Deterministic: same input → identical output (same order)
- ✅ Valid JSON on every line (can parse with `json.loads()`)
- ✅ Output file: `jig/generated/implementation-graph.ndjson` (per A001)
- ✅ All tests pass, coverage >80%

**Implementation Notes:**
- Files:
  - `src/jig/impl_graph/ndjson_writer.py` - NDJSONWriter class
  - `src/jig/impl_graph/graph.py` - Graph in-memory representation
- Algorithm:
  1. Collect all nodes and edges in Graph object
  2. Sort nodes by ID (lexicographic)
  3. Write metadata line: `{"_meta": {...}}`
  4. Write each node as JSON line: `json.dumps(node, sort_keys=True)`
  5. Write each edge as JSON line
- Ensure determinism:
  - Sort node IDs before writing
  - Use `sort_keys=True` in json.dumps
  - Exclude timestamp from determinism check (optional field)

**Test Plan:**
- Unit tests:
  - `test_ndjson_deterministic()` - same graph → identical output twice
  - `test_ndjson_format()` - one object per line, valid JSON
  - `test_ndjson_node_ordering()` - nodes sorted by ID
  - `test_ndjson_metadata_first()` - _meta on line 1
  - `test_ndjson_edges_after_nodes()` - edges after all nodes
  - `test_ndjson_round_trip()` - write → read → identical graph
- Decorator: `@jig.verifies("S-003")` on tests verifying NDJSON output format

**Docs to Update:**
- Document NDJSON schema in detail
- Add example output with annotations

**Reflect:**
_(To be filled after completion)_

- What worked well:
- What could be better:
- Discoveries:
- Risk watchlist:

**Links:**
- Commit(s): _TBD_

**Human Validation:**
- Run: `pytest tests/unit/test_ndjson_writer.py -v`
- Run: Check output is valid NDJSON: `cat jig/generated/implementation-graph.ndjson | while read line; do echo "$line" | python -m json.tool > /dev/null; done`
- Look for: No errors, all lines parse as JSON

---

## Work Unit 6: CLI Integration and End-to-End Validation

**Goal:** Integrate all components into `jig impl rebuild` CLI command and validate on real codebase.

**Planned Effort:** 90m

**Acceptance Criteria:**
- ✅ CLI command: `jig impl rebuild` works with all options
- ✅ Options: `--project-root`, `--source-dir`, `--exclude`, `--output`, `--verbose`, `--strict`
- ✅ Auto-detects Python files, runs PythonAnalyzer, generates NDJSON
- ✅ Error handling: parse errors fail-fast with file:line
- ✅ Progress output: shows file count, analysis progress, output location
- ✅ End-to-end test on JIG codebase: generates complete graph in <2s
- ✅ All tests pass (unit + integration), coverage >80%
- ✅ Documentation complete: README, CLI help, API docs

**Implementation Notes:**
- Files:
  - `src/jig/impl_graph/builder.py` - GraphBuilder orchestrator
  - `src/jig/impl_graph/cli.py` - CLI command (integrate with existing jig CLI)
- Builder workflow:
  1. Scan source directory for files matching extensions
  2. Detect language, route to appropriate analyzer
  3. Collect all nodes/edges into Graph object
  4. Write to NDJSON
- CLI integration:
  - Add `impl` subcommand group to main jig CLI
  - `jig impl rebuild` → calls GraphBuilder
  - Use `click` for CLI (already in dependencies)
- Error handling:
  - AST parse errors: catch, report file:line, exit 1 (strict mode)
  - IO errors: report clearly, suggest fixes
  - Validation errors: warn or error based on severity

**Test Plan:**
- Unit tests:
  - `test_builder_python_files()` - discovers .py files
  - `test_builder_excludes_tests()` - respects --exclude
  - `test_builder_language_routing()` - routes to PythonAnalyzer
  - `test_builder_fail_fast()` - parse error stops build
- Integration tests:
  - `test_cli_rebuild_simple()` - small fixture, generates graph
  - `test_cli_rebuild_jig()` - run on JIG codebase itself
  - `test_cli_rebuild_options()` - all CLI flags work
  - `test_cli_rebuild_performance()` - <2s for 10K LOC (measure on JIG)
- Decorators: `@jig.verifies("S-001")` and `@jig.verifies("S-006")` on relevant integration tests

**Docs to Update:**
- README with quickstart example
- CLI help text (`jig impl rebuild --help`)
- Architecture overview document
- API reference for programmatic use

**Reflect:**
_(To be filled after completion)_

- What worked well:
- What could be better:
- Discoveries:
- Risk watchlist:

**Links:**
- Commit(s): _TBD_

**Human Validation:**
- Run: `pytest tests/ -v` (all tests)
- Run: `jig impl rebuild --project-root ~/Code/jig --verbose`
- Run: `jig validate`
- Look for:
  - All tests pass
  - JIG codebase analyzed successfully
  - `jig/generated/implementation-graph.ndjson` created (per A001 contract)
  - Contains ~667 nodes (87 modules, 124 classes, 456 functions per AG022 estimate)
  - Build completes in <2s

---

## Completion Summary

_(To be filled when all units are complete)_

### Summary
- Scope delivered:
- Key decisions:
- Deltas from SCOPE:

### Metrics
- Units: 6 (excluding WU0); median cycle time: _TBD_
- Rework rate (units reopened): _TBD_
- Flaky test events: _TBD_
- Docs lag: _TBD_

### Reflection Roll-up
- Repeatable wins:
- Systemic frictions (top 3):
- Process changes adopted:
- Open questions for next plan:


---

**Status:** Draft - Ready for WU0 execution
**Next Action:** Create specification and outcome files (O-001 through O-003, S-001 through S-006) with A001-compliant frontmatter before writing any code
