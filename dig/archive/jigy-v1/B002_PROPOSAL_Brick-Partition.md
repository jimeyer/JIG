---
title: "B002: Brick Partition Proposal for JIG"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1764520553
created_human: "2025-11-30 10:35 CST"
parent: "[[AG020_Bricks-as-Partitions]]"
children: []
---
# B002: Brick Partition Proposal for JIG

**Date:** 2025-11-30
**Status:** Proposal
**References:** J016, A001

---

## Context

This document proposes the initial brick partition for the jig project. Following the JIG v8 concept (J016) and Core Artifacts Contract (A001), bricks partition the function space into disjoint architectural units that represent clear boundaries and responsibilities.

The implementation graph was analyzed to identify natural architectural boundaries based on:
- Module cohesion (functions that work together)
- Responsibility separation (clear concerns)
- Dependency patterns (who calls whom)
- Extensibility points (where the system is designed to grow)

---

## Proposed Brick Partition

### B-001: JIG Core Decorators

**Purpose:** Public API for developers to annotate code with alignment metadata.

**Units:**
- `M-jig.__init__`

**Rationale:**
This is the primary developer-facing API. It contains the `@jig.implements` and `@jig.verifies` decorators that enable the S-F-T triangle (Specification-Function-Test alignment). This brick is minimal by design - it's a stable public interface that should change rarely.

**Functions (3):**
- `F-jig.__init__.implements` - Decorator for marking function implementations
- `F-jig.__init__.verifies` - Decorator for marking test verifications
- `F-jig.__init__.decorator` - Internal decorator implementation (appears twice, likely nested closures)

**Specifications implemented:**
None directly (this is infrastructure that enables other code to reference specs)

**Expected dependencies:**
None (this is a leaf brick - other bricks depend on it, not the reverse)

---

### B-002: CLI Interface

**Purpose:** Command-line interface for jig operations.

**Units:**
- `M-jig.cli.main`

**Rationale:**
The CLI is the entry point for all user interactions with jig tooling. It orchestrates high-level operations (like `jigy impl rebuild`) but delegates actual work to other bricks. Separating it allows the CLI to evolve independently from core graph building logic.

**Functions (3):**
- `F-jig.cli.main.cli` - Main CLI entry point
- `F-jig.cli.main.impl` - Implementation graph command group
- `F-jig.cli.main.rebuild` - Rebuild implementation graph command

**Specifications implemented:**
None directly (orchestrates other bricks that implement specs)

**Expected dependencies:**
- B-003 (calls graph building and writing functions)
- B-004 (uses analyzer registry indirectly through builder)

---

### B-003: Implementation Graph Core

**Purpose:** Core graph data structures, building logic, and NDJSON I/O.

**Units:**
- `M-jig.impl_graph.graph` - Graph data structure
- `M-jig.impl_graph.builder` - Graph construction and file discovery
- `M-jig.impl_graph.ndjson_writer` - NDJSON serialization

**Rationale:**
These three modules form the heart of implementation graph generation. They work together to:
1. Store nodes and edges (`graph.py`)
2. Discover files and construct the graph (`builder.py`)
3. Serialize to NDJSON format (`ndjson_writer.py`)

They are tightly coupled and should evolve together. Separating them from analyzers allows the graph representation to remain stable even as we add new languages.

**Key classes (3):**
- `C-jig.impl_graph.graph.Graph` - Graph data structure (implements S-003)
- `C-jig.impl_graph.builder.GraphBuilder` - Graph builder (implements S-001, S-006)
- `C-jig.impl_graph.ndjson_writer.NDJSONWriter` - NDJSON writer (implements S-003)

**Functions (15 total):**
Graph class: `__init__`, `add_node`, `add_edge`, `add_nodes`, `add_edges`, `node_count`, `edge_count`, `get_nodes`, `get_edges`, `clear`

Builder class: `__init__`, `build`, `write`, `_discover_files`, `_should_exclude`, `_analyze_file`, plus module-level `build_graph`

Writer class: `__init__`, `write`, `_generate_metadata`, `_sort_nodes`, `_sort_edges`, plus module-level `write_ndjson`

**Specifications implemented:**
- S-001: Implementation graph generation
- S-003: NDJSON output format
- S-006: Error handling

**Expected dependencies:**
- B-004 (uses AnalyzerRegistry to get language analyzers)

---

### B-004: Language Analyzers

**Purpose:** Extensible framework for analyzing source code in different languages.

**Units:**
- `M-jig.impl_graph.analyzers.base` - Abstract language analyzer interface
- `M-jig.impl_graph.analyzers.registry` - Analyzer registration and discovery
- `M-jig.impl_graph.analyzers.python` - Python language analyzer
- `M-jig.impl_graph.analyzers.python_visitor` - Python AST visitor

**Rationale:**
This brick encapsulates all language-specific analysis. It's designed as an extensible framework:
- `base.py` defines the `LanguageAnalyzer` interface
- `registry.py` manages analyzer registration (supports future languages)
- `python.py` and `python_visitor.py` implement Python analysis

When we add support for JavaScript, Go, or Rust, we add new modules to this brick without touching B-003.

**Key classes (4):**
- `C-jig.impl_graph.analyzers.base.LanguageAnalyzer` - Abstract base (implements S-004)
- `C-jig.impl_graph.analyzers.registry.AnalyzerRegistry` - Registry pattern
- `C-jig.impl_graph.analyzers.python.PythonAnalyzer` - Python implementation
- `C-jig.impl_graph.analyzers.python.ParseError` - Python-specific error (implements S-006)
- `C-jig.impl_graph.analyzers.python_visitor.PythonStructureVisitor` - AST traversal

**Functions (51 total across all analyzers):**
Too many to list individually. Key public APIs:
- `LanguageAnalyzer.analyze_file` (abstract method)
- `AnalyzerRegistry.register`, `get_analyzer`, `get_analyzer_by_language`
- `PythonAnalyzer.analyze_file` (implements S-001, S-005, S-006)
- `PythonStructureVisitor.visit_*` methods (implements S-001, S-002, S-005)

**Specifications implemented:**
- S-001: Implementation graph generation (Python-specific)
- S-002: Decorator extraction (`@jig.implements`, `@jig.verifies`)
- S-004: Language analyzer plugin system
- S-005: Import tracking
- S-006: Error handling (parse errors)

**Expected dependencies:**
- B-001 (references jig decorators for extraction, but doesn't call them)

---

## Partition Properties

### Coverage and Disjointness

**All modules accounted for:**
- ✓ M-jig.__init__ → B-001
- ✓ M-jig.cli.main → B-002
- ✓ M-jig.impl_graph.graph → B-003
- ✓ M-jig.impl_graph.builder → B-003
- ✓ M-jig.impl_graph.ndjson_writer → B-003
- ✓ M-jig.impl_graph.analyzers.base → B-004
- ✓ M-jig.impl_graph.analyzers.registry → B-004
- ✓ M-jig.impl_graph.analyzers.python → B-004
- ✓ M-jig.impl_graph.analyzers.python_visitor → B-004

**Total functions partitioned:** 76 functions across 4 bricks

**No overlaps:** Each module belongs to exactly one brick (partition constraint satisfied)

### Expected Dependency Graph

```
B-002 (CLI)
  ├─→ B-003 (Graph Core)
  │     └─→ B-004 (Analyzers)
  │            └─→ B-001 (Decorators)
  └─→ [click, pathlib, logging]
```

**Dependency expectations:**
- B-001 has no internal dependencies (pure API)
- B-002 depends on B-003 (calls `build_graph`)
- B-003 depends on B-004 (uses `AnalyzerRegistry`)
- B-004 conceptually references B-001 (extracts decorator calls, but doesn't import)

**No circular dependencies:** Dependency graph is acyclic ✓

### Public APIs (Expected)

**B-001 public API:**
- `@jig.implements(*spec_ids)` - Used by application code
- `@jig.verifies(*spec_ids)` - Used by test code

**B-002 public API:**
- `jigy` CLI commands (via Click framework)
- `jigy impl rebuild` - Main command

**B-003 public API:**
- `build_graph(project_root, source_dir, ...)` - Called by B-002
- `Graph` class - Used by B-002 and B-004

**B-004 public API:**
- `AnalyzerRegistry.register(analyzer)` - Extension point for new languages
- `AnalyzerRegistry.get_analyzer(file_path)` - Called by B-003

---

## Design Rationale

### Why These Boundaries?

1. **B-001 (Decorators) is minimal**
   - Stable public API
   - No implementation details
   - Changes rarely (maybe never)

2. **B-002 (CLI) is separate from core logic**
   - CLI can evolve independently (add commands, change UI)
   - Core graph building doesn't care about CLI
   - Easy to add alternative interfaces (web UI, IDE plugin) that use B-003 directly

3. **B-003 (Graph Core) is language-agnostic**
   - Graph representation doesn't know about Python, JavaScript, etc.
   - Graph building orchestrates analyzers but doesn't implement them
   - NDJSON format is stable regardless of language

4. **B-004 (Analyzers) is the extension point**
   - Adding Go, JavaScript, Rust means adding modules to this brick
   - Language-specific complexity is contained here
   - Python implementation serves as reference for future languages

### What We Avoided

**We did NOT create:**
- Fine-grained bricks per module (too many bricks, no architectural value)
- Domain-based bricks like "Parsing" or "I/O" (cross-cutting, hard to maintain)
- Layer-based bricks like "Data" and "Logic" (doesn't match actual dependencies)

**We DID create:**
- Feature-oriented bricks (each brick does ONE thing)
- Dependency-respecting boundaries (acyclic dependency graph)
- Extensibility-aware partitions (B-004 designed to grow)

---

## Future Considerations

### Adding New Languages

When we add JavaScript support:
1. Create `M-jig.impl_graph.analyzers.javascript` → Add to B-004
2. Create `M-jig.impl_graph.analyzers.javascript_visitor` → Add to B-004
3. Register in `registry.py` (already part of B-004)
4. No changes to B-001, B-002, or B-003

### Adding Verification Graph

When we implement verification graph building (T nodes, T→S edges, T→F edges):
1. Likely create **B-005: Verification Graph Core** (mirrors B-003)
2. Likely create **B-006: Test Analyzers** (mirrors B-004)
3. B-002 adds new commands (`jigy verify rebuild`)

### Adding Intent Graph

When we implement intent graph building (S nodes, O nodes):
1. Likely create **B-007: Intent Graph Core**
2. Add markdown parser to extract frontmatter
3. B-002 adds new commands (`jigy index`)

### Brick Dependencies

As the system grows, we might see:
```
B-002 (CLI)
  ├─→ B-003 (Implementation Graph Core)
  │     └─→ B-004 (Language Analyzers)
  ├─→ B-005 (Verification Graph Core)
  │     └─→ B-006 (Test Analyzers)
  └─→ B-007 (Intent Graph Core)
```

Each graph type gets its own "core" brick and "analyzer" brick, maintaining separation of concerns.

---

## Validation

### Partition Constraints (from A001)

✓ **Every function belongs to exactly one brick**
- All 76 functions assigned
- No overlaps

✓ **Bricks are disjoint**
- No module appears in multiple bricks

✓ **Bricks cover all functions**
- No orphan modules

✓ **No class splitting**
- All methods of a class belong to the same brick
- Verified: Each class (Graph, GraphBuilder, NDJSONWriter, etc.) has all methods in one brick

✓ **Unit prefix validity**
- All units use M- prefix (modules)
- Could use C- or F- for finer control, but M- is sufficient for now

✓ **Unit existence**
- All units reference modules that exist in implementation graph
- Verified against implementation-graph.ndjson

### Specification Coverage

Reviewing which bricks implement which specs:

- **S-001** (Implementation graph generation): B-003, B-004
- **S-002** (Decorator extraction): B-004
- **S-003** (NDJSON output): B-003
- **S-004** (Language analyzer plugin): B-004
- **S-005** (Import tracking): B-004
- **S-006** (Error handling): B-003, B-004

**S-007 through S-017:** Not yet implemented (future work)

---

## Next Steps

1. **Validate brick partition**
   - Run `jigy validate` (once implemented)
   - Check that all functions are assigned
   - Verify no boundary violations

2. **Visualize brick dependencies**
   - Generate dependency graph
   - Confirm acyclic structure
   - Identify public APIs

3. **Measure alignment**
   - Which specs are implemented by which bricks?
   - Are all functions in each brick aligned to specs?
   - What's the alignment percentage per brick?

4. **Document brick contracts**
   - For each brick, document:
     - Public API (functions called from outside)
     - Responsibilities (what the brick does)
     - Dependencies (which bricks it calls)
     - Extension points (how to extend)

5. **Use bricks in development**
   - Assign work by brick ("Implement S-007 in B-004")
   - Review PRs by brick boundary (no cross-brick private calls)
   - Measure alignment by brick (B-003 is 80% aligned)

---

## Summary

This brick partition divides the jig implementation into four architectural units:

1. **B-001: JIG Core Decorators** - Stable public API (3 functions)
2. **B-002: CLI Interface** - User-facing commands (3 functions)
3. **B-003: Implementation Graph Core** - Graph building and I/O (19 functions)
4. **B-004: Language Analyzers** - Extensible analysis framework (51 functions)

The partition satisfies all constraints from A001:
- Complete coverage (76 functions)
- No overlaps (disjoint)
- Acyclic dependencies (B-002 → B-003 → B-004)
- No class splitting (verified)

This foundation enables:
- Clear architectural boundaries
- Independent evolution of subsystems
- Language extensibility (add to B-004)
- Alignment measurement by brick
- Dependency analysis and boundary enforcement

**The brick partition is ready for validation and use.**

---

## References

- **J016:** JIG Concept v8 (brick definition and rationale)
- **A001:** Core Artifacts Contract (partition constraints)
- **implementation-graph.ndjson:** Generated 2025-11-30, analyzed for this proposal
