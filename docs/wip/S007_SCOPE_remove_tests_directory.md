# SCOPE: Remove jig/tests/ Directory and Test Node Type

**Author:** Jim Meyer  
**Date:** 2025-11-20  
**Status:** Draft  
**Related:** JIG-Concept-v7.md, S-JIG-002

---

## Problem Statement

The `jig/tests/` directory and `type: test` node type are redundant in the JIG v7 OSTCX architecture.

**Current State:**
- ❌ `jig/tests/` directory exists but contains only template file `T-UNIT-001.md`
- ❌ `type: test` is a valid node type in parser, validator, and CLI
- ❌ Code scans `jig/tests/` directory for markdown test specification files
- ✅ All actual tests use `@jig T-XXX` annotations in Python test files
- ✅ Test nodes (T) are discovered via annotations, not markdown files (per v7 design)

**JIG v7 Context:**

The OSTCX model (Outcome/Specification/Test/Code/Constraint) has five representations:
- **O, S, X**: Markdown files in `jig/` subdirectories (timeless intent)
- **T, C**: Annotations in code with `@jig` decorators (executable reality)

This separation reflects the fundamental distinction: O/S/X are **about** what the system should do; T/C are what it **actually does**. Tests and code are executable; their source of truth is the running implementation, not documentation.

**Why This is Redundant:**

1. **Tests are code, not specifications** - In the OSTCX model, Test nodes (T) represent "Empirical truth (verify)" and are discovered via `@jig` annotations in actual test files (`tests/unit/`, `tests/integration/`)
2. **Markdown test files duplicate information** - Writing a `jig/tests/T-GRAPH-001.md` file duplicates what's already in the annotated test function
3. **Single source of truth violated** - Test behavior is defined in code; markdown files would be documentation that drifts
4. **All existing tests use annotations** - 60+ tests in codebase use `@jig T-XXX` annotations, zero use markdown files
5. **JIG v7 design intent** - The OSTCX model explicitly stores T nodes as annotations, not markdown (see JIG-Concept-v7.md §1.1)

**Example of Current Pattern (Correct):**

```python
# @jig T-GRAPH-001 verifies:S-GRAPH-002 subsystem:core
def test_load_from_dir_success():
    """Verify Graph loads from jig/ directory with valid nodes."""
    # Test implementation
```

**What We Don't Need (Redundant):**

```markdown
---
id: T-GRAPH-001
type: test
title: "Graph loads from directory"
subsystem: core
---

# Test: Graph loads from directory

Test that Graph.load_from_dir() works...
```

---

## Scope of Changes

### 1. Remove Test Node Type from Code

**Files to Modify:**

1. **`src/jig/core/graph.py`** (Line 89)
   - Remove `"tests"` from `node_dirs` list
   - Update comment explaining only O/S/C nodes are in markdown

2. **`src/jig/core/validator.py`** (Lines 29, 32-36)
   - Remove `"test"` from `VALID_TYPES` (should only contain: outcome, specification, constraint)
   - Remove `"test": "T"` from `TYPE_PREFIX_MAP`
   - Update validation error messages

3. **`src/jig/cli/node.py`** (Line 27)
   - Remove `"test"` from `click.Choice` options
   - Update help text to clarify only O/S/C nodes can be created

4. **`src/jig/core/parser.py`** (Line 18)
   - Update `OSTCNode` docstring to clarify: parses O/S/C markdown nodes (not T/X)
   - Keep name as `OSTCNode` - represents markdown-based Intent nodes in OSTCX model

### 2. Remove Test Template and Directory

**Files to Delete:**

1. **`templates/test_template.md`** - Template for test markdown files
2. **`jig/tests/T-UNIT-001.md`** - Example test node file
3. **`jig/tests/`** - Empty directory after file removal

### 3. Update Documentation

**Files to Update:**

1. **`README.md`** - Update OSTCX description to clarify:
   - O/S/X nodes are markdown files in `jig/` subdirectories
   - T/C nodes are `@jig` annotations in test/source code
   
2. **`agents/jig-agent-instructions.md`** - Verify alignment with v7 model

3. **`docs/jig-concept/JIG-Concept-v7.md`** - Already correct (Tests via annotations per §1.1, §1.3)

### 4. Update Tests

**Files to Review:**

1. **`tests/unit/test_graph.py`** - Update test that verifies directory scanning
2. **`tests/unit/test_templates.py`** - Remove test for test_template.md
3. **`tests/unit/test_validator.py`** - Remove tests validating `type: test`
4. **`tests/integration/test_node_create.py`** - Remove tests creating test nodes

---

## What Stays (No Changes)

### 1. Test Annotations Stay Exactly the Same

All `@jig T-XXX` annotations in test files remain unchanged:

```python
# @jig T-GRAPH-001 verifies:S-GRAPH-002 subsystem:core
def test_load_from_dir_success():
    """Verify Graph loads from jig/ directory with valid nodes."""
```

### 2. Test Discovery (Future Feature)

The ability to **discover and index test nodes from annotations** is a future feature:

```bash
# Future: Scan codebase for @jig annotations
jig index --rebuild
# Extracts T-XXX nodes from test files
# Builds graph with T → S edges
```

This SCOPE only removes the redundant markdown test files, not the annotation-based test tracking.

### 3. Graph Index Can Still Reference Tests

The `graph-index.yaml` can still contain test node (T) references per OSTCX model:

```yaml
nodes:
  T-GRAPH-001:
    file: tests/unit/test_graph.py
    line: 79
    type: test
    subsystem: core
```

These are **discovered** from `@jig` annotations, not loaded from markdown files.

---

## Migration Path

### Phase 1: Remove Code Support (This SCOPE)

1. Remove `"tests"` directory scanning from `graph.py`
2. Remove `"test"` type from validator and CLI
3. Delete template and example files
4. Update documentation

**Impact:** Zero - no existing functionality uses markdown test files

### Phase 2: Add Annotation Discovery (Future)

1. Implement `jig index --scan-code` to find `@jig T-XXX` annotations
2. Build graph index with test nodes pointing to source files
3. Enable `jig graph show T-GRAPH-001` to display test details from code

**Impact:** New feature - enables test node queries and traceability

---

## Rationale

### Why Remove Test Markdown Files?

1. **Tests are executable code** - The source of truth is the test function, not a markdown description
2. **Avoid duplication** - Markdown files would duplicate docstrings and annotations
3. **Prevent drift** - Documentation files drift from implementation; code is truth
4. **Simplify mental model** - O/S/C are "intent" (markdown), T is "verification" (code)

### Why Keep Test Node Type in Graph?

Test nodes (T) still exist in the **OSTCX graph model** and **annotations**, they just don't have markdown files:

- **Outcomes (O)**: Narrative truth (why) → `jig/outcomes/*.md`
- **Specifications (S)**: Logical truth (what) → `jig/specifications/*.md`
- **Tests (T)**: Empirical truth (verify) → `@jig T-XXX` in test code
- **Code (C)**: Operational truth (how) → `@jig C-XXX` in source code
- **Constraints (X)**: System properties (must) → `jig/constraints/*.md` *(predicates, not nodes)*

### Why This is Safe

1. **No existing usage** - Only one template file exists, no real test nodes
2. **All tests use annotations** - 60+ tests already use `@jig T-XXX` pattern
3. **Graceful degradation** - Code already handles missing `jig/tests/` directory
4. **Future-proof** - Annotation-based discovery is the planned approach

---

## Success Criteria

### Must Have

- [ ] `jig/tests/` directory removed
- [ ] `templates/test_template.md` removed
- [ ] `jigy node create --type test` returns error with helpful message
- [ ] `src/jig/core/graph.py` no longer scans `tests/` directory
- [ ] All existing tests pass (no functionality broken)
- [ ] Documentation updated to clarify OSTCX model: O/S/X are markdown, T/C are annotations

### Should Have

- [ ] Error message explains: "Test nodes use @jig annotations, not markdown files. See JIG-Concept-v7.md"
- [ ] README clearly distinguishes markdown nodes (O/S/X) from annotation nodes (T/C) per OSTCX model
- [ ] Validator provides clear error if someone manually creates `jig/tests/T-XXX.md`

### Could Have

- [ ] Migration guide for projects that might have created test markdown files
- [ ] Deprecation warning in `jig validate` if `jig/tests/` directory exists

---

## Open Questions

### 1. Should we rename `OSTCNode`?

**Options:**
- A) Keep `OSTCNode` - reflects OSTCX model (parses O/S/X markdown, T/C are annotations)
- B) Rename to `OSXNode` - reflects only markdown node types
- C) Rename to `IntentNode` - clarifies purpose (intent vs. implementation)

**Recommendation:** Keep `OSTCNode` - established name, T/C still part of OSTCX model, just stored differently. Name indicates "Intent Graph nodes that are markdown-based" within the broader OSTCX model.
**JIM REPLY**: A) Keep `OSTCNode` - reflects OSTCX model 

### 2. Should we keep `type: test` validation for future use?

**Options:**
- A) Remove entirely - test nodes never use markdown
- B) Keep validation but block file creation - allow in graph index only
- C) Keep but add warning - "Test nodes should use @jig annotations"

**Recommendation:** Remove entirely - if test nodes are in graph index, they don't need frontmatter validation.
**JIM REPLY**: A) Remove entirely - test nodes never use markdown


### 3. What about Constraint nodes (X-XXX)?

**Current State (v7):**
- Constraints use markdown files in `jig/constraints/`
- Constraints are cross-cutting system properties (performance, security, compliance)
- Constraints are **predicates over the OSTCX graph**, not regular nodes
- Prefix changed from C-XXX to X-XXX to avoid confusion with Code nodes

**Decision:** Keep constraint markdown files - they are system-wide properties, stored as markdown with query-based scope selectors. This SCOPE only affects Test nodes, not Constraints.
**JIM REPLY**: Agree.
---

## Related Work

### Existing Patterns

1. **Outcome/Specification/Constraint nodes (O/S/X)** - Already markdown-only
2. **Test annotations (T)** - Already annotation-based in all 60+ tests
3. **Code annotations (C)** - Future feature for C-XXX nodes (not yet implemented)

### Future Features (Out of Scope)

1. **Test discovery** - `jig index --scan-code` to find `@jig T-XXX` annotations in test files
2. **Code discovery** - `jig index --scan-code` to find `@jig C-XXX` annotations in source files
3. **Traceability queries** - `jig graph show T-GRAPH-001` displays test node details from code
4. **Coverage analysis** - `jig coverage` shows which S nodes lack T nodes
5. **Constraint validation** - `jig validate --constraints` checks X node compliance (v7 feature)

---

## Implementation Notes

### Validation Changes

**Before:**
```python
VALID_TYPES = {"outcome", "specification", "test", "constraint"}
```

**After:**
```python
# Only markdown-based node types (O/S/X in OSTCX model)
# T and C are annotation-based, not validated as markdown frontmatter
VALID_TYPES = {"outcome", "specification", "constraint"}
```

### Graph Loading Changes

**Before:**
```python
node_dirs = ["outcomes", "specifications", "constraints", "tests"]
```

**After:**
```python
# Load only markdown-based nodes (O/S/X in OSTCX model)
# T/C nodes discovered via @jig annotations (future feature)
node_dirs = ["outcomes", "specifications", "constraints"]
```

### CLI Changes

**Before:**
```bash
jigy node create --type test --id T-GRAPH-001 --title "Test graph loading"
# Creates jig/tests/T-GRAPH-001.md
```

**After:**
```bash
jigy node create --type test --id T-GRAPH-001 --title "Test graph loading"
# Error: Test nodes (T) must use @jig annotations in test code, not markdown files.
# In the OSTCX model, only O/S/X nodes use markdown.
# See: docs/jig-concept/JIG-Concept-v7.md§1.3 (Test annotations)
```

---

## Risks and Mitigations

### Risk 1: Someone Already Created Test Markdown Files

**Likelihood:** Low (only template exists in repo)  
**Impact:** Low (files ignored, no functionality broken)  
**Mitigation:** Add deprecation warning in `jig validate` if `jig/tests/*.md` files found

### Risk 2: Future Confusion About Test Nodes

**Likelihood:** Medium (new users might expect markdown files)  
**Impact:** Low (clear error message guides to correct pattern)  
**Mitigation:** Update documentation and error messages to be explicit

### Risk 3: Breaking External Tools

**Likelihood:** Low (project is early stage, no known external tools)  
**Impact:** Medium (tools expecting `jig/tests/` directory would break)  
**Mitigation:** Version this change, document in CHANGELOG

---

## Timeline Estimate

**Total Effort:** ~4 hours

1. **Code changes** - 1 hour
   - Remove test type from validator, parser, CLI
   - Update graph loading logic
   - Update error messages

2. **Test updates** - 1 hour
   - Remove test template tests
   - Update graph loading tests
   - Verify all existing tests pass

3. **Documentation** - 1.5 hours
   - Update README
   - Update JIG-Concept docs
   - Update agent instructions (if needed)

4. **Cleanup** - 0.5 hours
   - Delete template and example files
   - Remove empty directory
   - Final validation

---

## Approval Checklist

Before implementing:

- [ ] Confirm no external projects depend on `jig/tests/` directory
- [ ] Verify all tests use `@jig T-XXX` annotations (not markdown files)
- [ ] Review impact on future test discovery feature
- [ ] Decide on `OSTCNode` vs `OSCNode` naming
- [ ] Approve error message wording for `jigy node create --type test`

---

## References

- **JIG-Concept-v7.md** - Current architecture (OSTCX model, tests via annotations §1.3)
- **S-JIG-002** - OSTC node parsing specification (to be updated for OSX markdown nodes)
- **agents/jig-agent-instructions.md** - Should reflect v7 OSTCX model
- **tests/** - All 60+ tests use `@jig T-XXX` annotations (correct pattern)

