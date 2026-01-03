# PLAN: Verification Graph Implementation

- **SCOPE**: docs/wip/B010_SCOPE_Verification-Graph.md
- **Start**: 2025-12-08
- **Status**: Draft
- **Branch**: verification-graph

## Overview

Complete the S-F-T triangle by implementing the verification graph, which tracks T→S edges (tests verifying specifications via `@jig.verifies` decorators).

**Key Simplification:** T→F coverage edges are NOT part of the verification graph—they're handled by the Audit system (J023). This keeps verification graph purely static (no test execution required).

**Code Reuse Strategy:** ~220 lines of new code by leveraging existing infrastructure:
- Import `Graph`, `NDJSONWriter` from `impl_graph` (100% reuse)
- Import `hash_function()` from `hashing.py` (100% reuse)
- Clone `_extract_implements_decorators()` pattern for `@jig.verifies`

---

## Known Intent (Created in WU0)

### Outcome

| ID | Name | File |
|----|------|------|
| O-018 | Test Alignment Tracking | `jig/outcomes/O-018.md` |

### Specifications

| ID | Name | File |
|----|------|------|
| S-051 | Test Discovery | `jig/specifications/S-051.md` |
| S-052 | Test Node Schema | `jig/specifications/S-052.md` |
| S-053 | @jig.verifies Extraction | `jig/specifications/S-053.md` |
| S-054 | Test Hashing | `jig/specifications/S-054.md` |
| S-055 | Verification Graph Generation | `jig/specifications/S-055.md` |
| S-056 | CLI jigy verify rebuild | `jig/specifications/S-056.md` |

**Note:** S-057 (A001 Contract Update) was not created as a specification per O-S Writing Guide — it describes a documentation task, not behavioral requirements. The A001 update is captured directly in A001.

### Brick

**B-verification-graph** (new brick, layer 1)
- Depends on: B-hashing (layer 0)
- Units: `M-jig.verification_graph`

---

## Work Unit Checklist

- [x] WU0: Create Intent nodes (O/S) and update A001
- [x] WU1: Test Discovery — tests ✅ / code ✅ / docs ✅
- [x] WU2: Test Analyzer — tests ✅ / code ✅ / docs ✅
- [x] WU3: Verification Graph Builder — tests ✅ / code ✅ / docs ✅
- [x] WU4: CLI Integration — tests ✅ / code ✅ / docs ✅

---

## Work Units

### Work Unit 0: Create Known Intent + Update A001

**Goal**: Capture all verification graph requirements as O/S nodes, and update A001 to remove `covers` field from verification graph schema.

**Planned Effort**: 1 hour

**Acceptance Criteria**:
- [x] O-018 created in `jig/outcomes/O-018.md`
- [x] S-051 through S-056 created in `jig/specifications/`
- [x] A001 updated: verification graph schema removes `covers`, adds `jig_hash`
- [x] `jig/bricks.yaml` updated with B-verification-graph brick
- [x] All files have proper YAML frontmatter
- [x] `jigy validate intent` passes
- [x] Intent committed before any code

**Actions**:

1. Create O-018 (Test Alignment Tracking)
2. Create S-051 (Test Discovery)
3. Create S-052 (Test Node Schema)
4. Create S-053 (@jig.verifies Extraction)
5. Create S-054 (Test Hashing)
6. Create S-055 (Verification Graph Generation)
7. Create S-056 (CLI jigy verify rebuild)
8. ~~Create S-057 (A001 Contract Update)~~ — SKIPPED: Per O-S Writing Guide, this is a documentation task, not behavioral requirement
9. Update A001 Section 6.3 to remove `covers` field
10. Update `jig/bricks.yaml` with new brick

**A001 Changes** (Section 6.3):

Before:
```json
{"id":"T-test_auth.test_token_expiration","type":"test","file":"tests/unit/test_auth.py","verifies":["S-001"],"covers":["F-auth.session.authenticate"]}
```

After:
```json
{"id":"T-test_auth.test_token_expiration","type":"test","file":"tests/unit/test_auth.py","verifies":["S-001"],"jig_hash":"a1b2c3d4e5f6"}
```

**Human Verification**:
```bash
jigy validate intent
ls jig/outcomes/O-018.md
ls jig/specifications/S-05*.md
```

**Reflect**:
- O-S Writing Guide helped: Skipped S-057 (documentation task, not behavioral spec)
- O-018 `specifies:` list correctly references S-051–S-056 only
- A001 update was straightforward: removed `covers`, added `jig_hash`, added design note
- All 6 specs follow behavioral pattern: testable acceptance criteria

**Links**:
- Commit: (see git log)

---

### Work Unit 1: Test Discovery

**Goal**: Create test file discovery that finds all test files and parses test functions.

**Implements**: S-051

**Planned Effort**: 1 hour

**Reuses**: Standard library only (`pathlib.rglob`). Simpler than impl_graph discovery.

**Est. New Code**: ~50 lines

**Acceptance Criteria**:
- [x] `discover_test_files()` finds `test_*.py` and `*_test.py` patterns
- [x] `discover_tests()` finds `def test_*` and `class Test*` methods
- [x] Excludes `__pycache__`, `.venv`, `node_modules`
- [x] Returns deterministic ordering (sorted by path)
- [x] Unit tests with >80% coverage (93.55% achieved)
- [x] `@jig.implements("S-051")` decorator on discovery function

**New Files**:
- `src/jig/verification_graph/__init__.py`
- `src/jig/verification_graph/discovery.py`
- `tests/unit/verification_graph/test_discovery.py`

**Test Plan** (TDD - write first):
```python
@jig.verifies("S-051")
def test_discover_test_files_finds_test_prefix():
    """Discovers files matching test_*.py pattern."""

@jig.verifies("S-051")
def test_discover_test_files_finds_test_suffix():
    """Discovers files matching *_test.py pattern."""

@jig.verifies("S-051")
def test_discover_test_files_excludes_pycache():
    """Excludes __pycache__ directories."""

@jig.verifies("S-051")
def test_discover_tests_finds_functions():
    """Finds test functions (def test_*)."""

@jig.verifies("S-051")
def test_discover_tests_finds_methods():
    """Finds test methods in TestClass."""

@jig.verifies("S-051")
def test_discover_tests_deterministic_order():
    """Returns tests in deterministic alphabetical order."""
```

**Implementation Notes**:
```python
# src/jig/verification_graph/discovery.py
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class TestInfo:
    id: str           # T-test_auth.test_login
    file: Path        # tests/unit/test_auth.py
    name: str         # test_login
    class_name: Optional[str]  # TestAuth (if method)

@jig.implements("S-051")
def discover_test_files(
    project_root: Path,
    test_dir: Optional[Path] = None,
    exclude_patterns: Optional[List[str]] = None,
) -> List[Path]:
    """Discover all test files in project."""

def discover_tests(test_files: List[Path]) -> List[TestInfo]:
    """Discover test functions/methods from test files."""
```

**Human Verification**:
```bash
pytest tests/unit/verification_graph/test_discovery.py -v
python -c "from jig.verification_graph.discovery import discover_test_files; print(len(discover_test_files(Path('.'))))"
```

**Reflect**:
- TDD worked well: 15 tests written first, all passed after implementation
- ~60 lines of new code (slightly over estimate due to docstrings)
- 93.55% coverage achieved (target was >80%)
- AST parsing for test discovery is cleaner than regex matching
- `TestInfo` dataclass provides good structure for downstream WU2/WU3

**Links**:
- Commit: (see git log)

---

### Work Unit 2: Test Analyzer (Parse + @jig.verifies)

**Goal**: Create AST-based test analyzer that extracts `@jig.verifies` decorators and computes `jig_hash`.

**Implements**: S-052, S-053, S-054

**Planned Effort**: 2 hours

**Reuses**:
- `hash_function()` from `hashing.py` (100% reuse)
- `_extract_implements_decorators()` pattern (clone & modify)
- `_validate_spec_id()` (100% reuse or copy)

**Est. New Code**: ~100 lines

**Acceptance Criteria**:
- [x] Parses `@jig.verifies("S-001")` single spec
- [x] Parses `@jig.verifies("S-001", "S-002")` multiple specs
- [x] Parses `@verifies("S-001")` short form (if imported)
- [x] Validates spec ID format (`^[SO]-\d+$`)
- [x] Logs warning for invalid spec IDs (does not fail)
- [x] Computes `jig_hash` using existing `hash_test()` from hashing.py
- [x] Returns T nodes conforming to S-052 schema
- [x] Unit tests with >80% coverage (90.28% achieved)
- [x] `@jig.implements("S-052", "S-053", "S-054")` decorator on analyze_file()

**New Files**:
- `src/jig/verification_graph/analyzer.py`
- `tests/unit/verification_graph/test_analyzer.py`
- `tests/fixtures/python/test_with_verifies.py` (fixture)

**Test Plan** (TDD - write first):
```python
@jig.verifies("S-053")
def test_extract_verifies_single_spec():
    """Extracts @jig.verifies("S-001") decorator."""

@jig.verifies("S-053")
def test_extract_verifies_multiple_specs():
    """Extracts @jig.verifies("S-001", "S-002") decorator."""

@jig.verifies("S-053")
def test_extract_verifies_short_form():
    """Extracts @verifies("S-001") short form."""

@jig.verifies("S-053")
def test_validates_spec_id_format():
    """Warns on invalid spec IDs like 'SPEC-001'."""

@jig.verifies("S-052")
def test_node_schema_has_required_fields():
    """T nodes have id, type, file, verifies, jig_hash."""

@jig.verifies("S-052")
def test_node_schema_excludes_covers():
    """T nodes do NOT have covers field (Audit domain)."""

@jig.verifies("S-054")
def test_hash_changes_when_logic_changes():
    """jig_hash changes when test function body changes."""

@jig.verifies("S-054")
def test_hash_stable_across_whitespace():
    """jig_hash stable across whitespace/comment changes."""
```

**Test Fixture** (`tests/fixtures/python/test_with_verifies.py`):
```python
import jig

@jig.verifies("S-001")
def test_simple():
    assert True

@jig.verifies("S-001", "S-002")
def test_multiple_specs():
    assert True

class TestWithClass:
    @jig.verifies("S-003")
    def test_method(self):
        assert True

def test_no_decorator():
    """Test without @jig.verifies - should have empty verifies array."""
    assert True
```

**Implementation Notes**:
```python
# src/jig/verification_graph/analyzer.py
import ast
from pathlib import Path
from typing import Dict, List, Any
from jig.hashing import hash_function

class TestAnalyzer:
    """Analyze test files for @jig.verifies decorators."""

    @jig.implements("S-052", "S-053")
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze test file and return test nodes."""
        return {
            "nodes": [...],  # T nodes
        }

    def _extract_verifies_decorators(self, node: ast.FunctionDef) -> List[str]:
        """Extract spec IDs from @jig.verifies decorators.

        Cloned from python_visitor._extract_implements_decorators
        with 'implements' -> 'verifies'.
        """
```

**Human Verification**:
```bash
pytest tests/unit/verification_graph/test_analyzer.py -v --cov=jig.verification_graph.analyzer
```

**Reflect**:
- TDD worked well: 21 tests written first, all passed after implementation
- ~72 lines of analyzer code (under ~100 line estimate)
- 90.28% coverage achieved (target was >80%)
- Code reuse: `hash_test()` from hashing.py, pattern from `_extract_implements_decorators`
- Test fixture file useful for integration testing

**Links**:
- Commit: (see git log)

---

### Work Unit 3: Verification Graph Builder

**Goal**: Create graph builder that orchestrates discovery, analysis, and NDJSON output.

**Implements**: S-055

**Planned Effort**: 1 hour

**Reuses**:
- `Graph` class from `impl_graph/graph.py` (100% reuse)
- `NDJSONWriter` from `impl_graph/ndjson_writer.py` (100% reuse)
- `write_ndjson()` from `impl_graph/ndjson_writer.py` (100% reuse)

**Est. New Code**: ~40 lines (thin orchestration layer)

**Acceptance Criteria**:
- [x] Orchestrates discovery → analysis → serialization
- [x] Generates `jig/generated/verification-graph.ndjson`
- [x] Uses existing `Graph` class (no new dataclass)
- [x] Uses existing `write_ndjson()` for output
- [x] Deterministic output (sorted by test ID)
- [x] Includes metadata line with node/edge counts
- [x] Integration tests verify end-to-end
- [x] `@jig.implements("S-055")` decorator on builder function

**New Files**:
- `src/jig/verification_graph/builder.py`
- `tests/unit/verification_graph/test_builder.py`

**Test Plan** (TDD - write first):
```python
@jig.verifies("S-055")
def test_build_verification_graph_creates_ndjson():
    """Builder creates verification-graph.ndjson file."""

@jig.verifies("S-055")
def test_build_verification_graph_has_metadata():
    """First line is metadata with node_count, edge_count."""

@jig.verifies("S-055")
def test_build_verification_graph_nodes_sorted():
    """Nodes are sorted alphabetically by ID."""

@jig.verifies("S-055")
def test_build_verification_graph_edges_sorted():
    """Edges are sorted by (source, target, type)."""

@jig.verifies("S-055")
def test_build_verification_graph_deterministic():
    """Same input produces identical output."""

@jig.verifies("S-055")
def test_build_verification_graph_uses_graph_class():
    """Uses existing Graph class from impl_graph."""
```

**Implementation Notes**:
```python
# src/jig/verification_graph/builder.py
from pathlib import Path
from typing import Optional, List
from jig.impl_graph.graph import Graph
from jig.impl_graph.ndjson_writer import write_ndjson
from jig.verification_graph.discovery import discover_test_files, discover_tests
from jig.verification_graph.analyzer import TestAnalyzer

@jig.implements("S-055")
def build_verification_graph(
    project_root: Path,
    test_dir: Optional[Path] = None,
    output_path: Optional[Path] = None,
    exclude_patterns: Optional[List[str]] = None,
    include_timestamp: bool = True,
) -> Graph:
    """Build verification graph from test files.

    Returns the existing Graph class — no new dataclass needed.
    """
    graph = Graph()

    # 1. Discover test files
    test_files = discover_test_files(project_root, test_dir, exclude_patterns)

    # 2. Analyze each file
    analyzer = TestAnalyzer()
    for file_path in test_files:
        result = analyzer.analyze_file(file_path)
        for node in result["nodes"]:
            graph.add_node(node)
            # Add T→S edges for each verified spec
            for spec_id in node.get("verifies", []):
                graph.add_edge({
                    "source": node["id"],
                    "target": spec_id,
                    "type": "verifies"
                })

    # 3. Write to NDJSON
    if output_path is None:
        output_path = project_root / "jig/generated/verification-graph.ndjson"
    write_ndjson(graph, output_path, include_timestamp=include_timestamp)

    return graph
```

**Human Verification**:
```bash
pytest tests/unit/verification_graph/test_builder.py -v
python -c "
from pathlib import Path
from jig.verification_graph.builder import build_verification_graph
g = build_verification_graph(Path('.'), output_path=Path('/tmp/test-vg.ndjson'))
print(f'Nodes: {g.node_count()}, Edges: {g.edge_count()}')
"
cat /tmp/test-vg.ndjson | head -5
```

**Reflect**:
- TDD worked well: 11 tests written first, all passed after implementation
- ~22 lines of builder code (well under ~40 line estimate)
- 100% coverage achieved on builder (target was >80%)
- Code reuse: 100% reuse of `Graph`, `write_ndjson()` from impl_graph
- Thin orchestration layer as designed—discovery/analyzer do the heavy lifting

**Links**:
- Commit: (see git log)

---

### Work Unit 4: CLI Integration

**Goal**: Add `jigy verify rebuild` command and integrate with `jigy rebuild`.

**Implements**: S-056

**Planned Effort**: 1 hour

**Reuses**:
- CLI patterns from `src/jig/cli/main.py`
- `impl` subcommand as template for `verify` subcommand

**Est. New Code**: ~30 lines

**Acceptance Criteria**:
- [x] `jigy verify rebuild` generates verification-graph.ndjson
- [x] `jigy verify rebuild --test-dir TESTS/` specifies test directory
- [x] `jigy verify rebuild --no-timestamp` for deterministic testing
- [x] `jigy rebuild` includes verification graph as final step (step 4/5)
- [x] CLI tests verify command behavior (8 tests)
- [x] Progress output shows discovery/analysis/write phases
- [x] `@jig.implements("S-056")` decorator on CLI function

**Modified Files**:
- `src/jig/cli/main.py` — Add `verify` subcommand group
- `src/jig/cli/verify.py` — New file for verify commands

**New Files**:
- `src/jig/cli/verify.py`
- `tests/unit/cli/test_verify.py`

**Test Plan** (TDD - write first):
```python
@jig.verifies("S-056")
def test_cli_verify_rebuild_creates_file():
    """jigy verify rebuild creates verification-graph.ndjson."""

@jig.verifies("S-056")
def test_cli_verify_rebuild_custom_test_dir():
    """jigy verify rebuild --test-dir works."""

@jig.verifies("S-056")
def test_cli_verify_rebuild_no_timestamp():
    """jigy verify rebuild --no-timestamp produces deterministic output."""

@jig.verifies("S-056")
def test_cli_rebuild_includes_verification():
    """jigy rebuild includes verification graph generation."""
```

**Implementation Notes**:
```python
# src/jig/cli/verify.py
import click
from pathlib import Path
from jig.verification_graph.builder import build_verification_graph

@click.group()
def verify():
    """Verification graph commands."""
    pass

@verify.command()
@click.option("--test-dir", type=click.Path(exists=True), help="Test directory")
@click.option("--no-timestamp", is_flag=True, help="Omit timestamp for deterministic output")
@jig.implements("S-056")
def rebuild(test_dir: str, no_timestamp: bool):
    """Rebuild verification graph from test files."""
    click.echo("[1] Discovering tests...")
    # ... implementation
```

**CLI Output Example**:
```
$ jigy verify rebuild
[1] Discovering tests...
    Found 42 test files
[2] Analyzing test functions...
    Found 320 tests
    Found 87 @jig.verifies edges
[3] Writing verification-graph.ndjson...
    Wrote 320 nodes, 87 edges

Verification graph written to: jig/generated/verification-graph.ndjson
```

**Human Verification**:
```bash
jigy verify rebuild --help
jigy verify rebuild
cat jig/generated/verification-graph.ndjson | head -5
jigy verify rebuild --no-timestamp
```

**Reflect**:
- TDD worked well: 8 tests written first, all passed after implementation
- ~24 lines of verify.py + ~40 lines in main.py (under ~30 estimate for verify.py)
- 100% coverage achieved on verify CLI (target was >80%)
- CLI pattern matches impl/intent subcommands exactly
- `jigy rebuild` now includes verification graph as step 4/5
- Progress output matches S-056 spec: files discovered, tests found, edges extracted

**Links**:
- Commit: (see git log)

---

## Clean Break Notes

Per `taskCleanBreak.md`, this implementation:

1. **No backwards compatibility hacks**: The verification graph is new—no old code to burn
2. **Fail loudly**: Invalid `@jig.verifies` decorators log warnings with clear messages
3. **Full commitment**: T→F coverage is explicitly NOT included (Audit domain)—no "just in case" fields

**If we discover old verification-related code**:
- Delete it completely
- Don't preserve commented code
- Reference git history if needed

---

## Validation Commands

```bash
# After each work unit
jigy validate intent          # Check O/S files
pytest -v                     # Run all tests
jigy impl rebuild             # Update implementation graph
jigy verify rebuild           # Generate verification graph (after WU4)
jigy status                   # Check alignment

# Final validation
jigy validate
pytest --cov=src/jig/verification_graph --cov-report=term-missing
```

---

## Success Criteria

- [ ] All O/S nodes from SCOPE created (`O-018`, `S-051`–`S-057`)
- [ ] All specifications have `@jig.implements` decorators in code
- [ ] All specifications have `@jig.verifies` decorators in tests
- [ ] `jigy validate` passes with no errors
- [ ] `jigy status` shows expected alignment
- [ ] All tests passing with >80% coverage on new code
- [ ] `jigy verify rebuild` generates valid verification-graph.ndjson
- [ ] A001 updated to reflect no `covers` field
- [ ] PLAN document has completion summary

---

## Completion Summary

(To be filled after all work units complete)

**Scope Delivered**:
- (pending)

**Metrics**:
- Work Units: 5
- Specifications Created: 7
- Specifications Implemented: (pending)
- Alignment: (pending)

**Key Decisions**:
- (pending)

**Deltas from Original Scope**:
- (pending)

**Reflection Roll-Up**:
- **Repeatable wins**: (pending)
- **Systemic frictions**: (pending)
- **Open questions**: (pending)

**Final Validation**:
- [ ] All work unit checklists complete
- [ ] `jigy validate` passes
- [ ] `jigy status` shows expected alignment
- [ ] All tests passing
- [ ] Documentation updated
