# SCOPE: Remove jig/tests/ Directory and Test Node Type

**Author:** Jim Meyer  
**Date:** 2025-11-20  
**Status:** Draft  
**Related:** JIG-Concept-v6.1.md, S-JIG-002

---

## Problem Statement

The `jig/tests/` directory and `type: test` node type are redundant in the current JIG architecture.

**Current State:**
- ❌ `jig/tests/` directory exists but contains only template file `T-UNIT-001.md`
- ❌ `type: test` is a valid node type in parser, validator, and CLI
- ❌ Code scans `jig/tests/` directory for markdown test specification files
- ✅ All actual tests use `@jig T-XXX` decorators in Python test files
- ✅ Test nodes are already tracked via annotations, not markdown files

**Why This is Redundant:**

1. **Tests are code, not specifications** - Test nodes (T-XXX) are discovered via `@jig` annotations in actual test files (`tests/unit/`, `tests/integration/`)
2. **Markdown test files duplicate information** - Writing a `jig/tests/T-GRAPH-001.md` file duplicates what's already in the annotated test function
3. **Single source of truth violated** - Test behavior is defined in code; markdown files would be documentation that drifts
4. **All existing tests use decorators** - 60+ tests in codebase use `@jig T-XXX` annotations, zero use markdown files

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
   - Remove `"test"` from `VALID_TYPES`
   - Remove `"test": "T"` from `TYPE_PREFIX_MAP`
   - Update validation error messages

3. **`src/jig/cli/node.py`** (Line 27)
   - Remove `"test"` from `click.Choice` options
   - Update help text to clarify only O/S/C nodes can be created

4. **`src/jig/core/parser.py`** (Line 18)
   - Update `OSTCNode` docstring to remove "Test" from list
   - Rename to `OSCNode` or keep as `OSTCNode` for backwards compatibility

### 2. Remove Test Template and Directory

**Files to Delete:**

1. **`templates/test_template.md`** - Template for test markdown files
2. **`jig/tests/T-UNIT-001.md`** - Example test node file
3. **`jig/tests/`** - Empty directory after file removal

### 3. Update Documentation

**Files to Update:**

1. **`README.md`** - Update OSTC description to clarify:
   - O/S/C nodes are markdown files in `jig/`
   - T nodes are `@jig` annotations in test code
   
2. **`agents/jig-agent-instructions.md`** - Already correct, no changes needed

3. **`docs/jig-concept/JIG-Concept-v6.1.md`** - Update to clarify:
   - Tests are discovered via `@jig` annotations
   - No markdown files for test nodes

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

The `graph-index.yaml` can still contain test node references:

```yaml
nodes:
  - id: T-GRAPH-001
    type: test
    file: tests/unit/test_graph.py:79
    subsystem: core
```

These are **discovered** from annotations, not loaded from markdown files.

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

Test nodes (T-XXX) still exist in the **graph model** and **annotations**, they just don't have markdown files:

- **Outcomes (O)**: Business value → `jig/outcomes/*.md`
- **Specifications (S)**: Technical requirements → `jig/specifications/*.md`
- **Tests (T)**: Verification → `@jig T-XXX` in test code
- **Code (C)**: Implementation → `@jig C-XXX` in source code
- **Constraints (C)**: Cross-cutting requirements → `jig/constraints/*.md`

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
- [ ] Documentation updated to clarify O/S/C are markdown, T/C are annotations

### Should Have

- [ ] Error message explains: "Test nodes use @jig annotations, not markdown files"
- [ ] README clearly distinguishes markdown nodes (O/S/C) from annotation nodes (T/C)
- [ ] Validator provides clear error if someone manually creates `jig/tests/T-XXX.md`

### Could Have

- [ ] Migration guide for projects that might have created test markdown files
- [ ] Deprecation warning in `jig validate` if `jig/tests/` directory exists

---

## Open Questions

### 1. Should we rename `OSTCNode` to `OSCNode`?

**Options:**
- A) Keep `OSTCNode` for backwards compatibility (T still exists in graph model)
- B) Rename to `OSCNode` to reflect only markdown node types
- C) Rename to `IntentNode` to clarify purpose (intent vs. implementation)

**Recommendation:** Keep `OSTCNode` - Test nodes still exist in the graph, just not as markdown files.

### 2. Should we keep `type: test` validation for future use?

**Options:**
- A) Remove entirely - test nodes never use markdown
- B) Keep validation but block file creation - allow in graph index only
- C) Keep but add warning - "Test nodes should use @jig annotations"

**Recommendation:** Remove entirely - if test nodes are in graph index, they don't need frontmatter validation.

### 3. What about Constraint nodes (C-XXX)?

**Current State:**
- Constraints use markdown files in `jig/constraints/`
- Constraints are cross-cutting requirements (performance, security, etc.)
- Constraints are NOT code implementations

**Decision:** Keep constraint markdown files - they are specifications, not code.

---

## Related Work

### Existing Patterns

1. **Outcome/Specification nodes** - Already markdown-only
2. **Test annotations** - Already decorator-based in all 60+ tests
3. **Code annotations** - Future feature for C-XXX nodes (not yet implemented)

### Future Features (Out of Scope)

1. **Test discovery** - `jig index --scan-code` to find `@jig T-XXX` annotations
2. **Code discovery** - `jig index --scan-code` to find `@jig C-XXX` annotations
3. **Traceability queries** - `jig graph show T-GRAPH-001` displays test from code
4. **Coverage analysis** - `jig coverage` shows which S nodes lack T nodes

---

## Implementation Notes

### Validation Changes

**Before:**
```python
VALID_TYPES = {"outcome", "specification", "test", "constraint"}
```

**After:**
```python
VALID_TYPES = {"outcome", "specification", "constraint"}
```

### Graph Loading Changes

**Before:**
```python
node_dirs = ["outcomes", "specifications", "constraints", "tests"]
```

**After:**
```python
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
# Error: Test nodes must use @jig annotations in test code.
# See: docs/jig-concept/JIG-Concept-v6.1.md#test-annotations
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

- **JIG-Concept-v6.1.md** - Current architecture (tests via annotations)
- **S-JIG-002** - OSTC node parsing specification
- **agents/jig-agent-instructions.md** - Already shows correct pattern
- **tests/** - All 60+ tests use `@jig T-XXX` annotations

