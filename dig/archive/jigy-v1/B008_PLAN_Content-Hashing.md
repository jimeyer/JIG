---
title: "PLAN: J022 Content Hashing Implementation"
type: plan
status: implemented
decision: "Superseded by newer deliberation"
created: 1765242592
created_human: "2025-12-08 19:09 CST"
parent: "[[J022_Content-Hashing]]"
children: []
---
# PLAN: J022 Content Hashing Implementation

- **SCOPE**: docs/jig-concept/J022_Content-Hashing.md
- **Start**: 2025-12-08
- **Status**: Draft
- **Branch**: content-hashing

## Context

J022 defines how JIG computes and stores content identity through semantic hashing. This enables change detection by fingerprinting each artifact's meaningful content.

**Key Requirements from J022:**
1. SHA-256 truncated to 12 hex chars for all `jig_hash` values
2. Semantic hashing — capture meaningful content, ignore formatting
3. Cross-platform determinism — same content = same hash everywhere
4. Git-optimized — `git_blob` enables fast-path during rebuild
5. S-F-T coverage — hash specs, functions, and tests

**Clean Break Protocol:**
- No backwards compatibility with unhashed graphs
- Old graphs without hashes will simply be regenerated
- All graph nodes get hashes — no partial migration

---

## Known Intent (Created Before Coding)

**Outcomes:**
- O-017: Change Detection Foundation (jig/outcomes/O-017.md) — NEW

**Specifications:**
- S-044: Hash Algorithm Standard (jig/specifications/S-044.md) — NEW
- S-045: Intent Artifact Hashing (jig/specifications/S-045.md) — NEW
- S-046: Function Hashing via AST (jig/specifications/S-046.md) — NEW
- S-047: Test Hashing via AST (jig/specifications/S-047.md) — NEW
- S-048: Brick Definition Hashing (jig/specifications/S-048.md) — NEW
- S-049: Git Blob Integration (jig/specifications/S-049.md) — NEW
- S-050: Graph Schema with Hashes (jig/specifications/S-050.md) — NEW

**Bricks Affected:**
- B-impl-graph: Add hashing to implementation graph builder
- B-intent-graph: Add hashing to intent graph generator
- B-languages: Add hash computation in python_visitor
- NEW B-hashing: Core hashing module

---

## Work Unit Checklist

- [x] WU0: Create Intent nodes (O/S)
- [x] WU1: Core hashing module — tests ✅ / code ✅ / docs ☐
- [x] WU2: Intent graph hashing — tests ✅ / code ✅ / docs ☐
- [x] WU3: Implementation graph hashing — tests ✅ / code ✅ / docs ☐
- [x] WU4: Git blob optimization — tests ✅ / code ✅ / docs ☐

---

## Work Units

### Work Unit 0: Create Known Intent

**Goal**: Capture all J022 requirements as O/S nodes before writing any code.

**Acceptance Criteria**:
- [x] O-017 created for change detection foundation
- [x] S-044 through S-050 created for hashing specifications
- [x] All files have proper YAML frontmatter
- [x] `jigy validate` passes

**Created Nodes**:
- O-017: Artifact Change Detection
- S-044: Content Hash Format
- S-045: Intent Artifact Hashing
- S-046: Function Hashing via AST
- S-047: Test Hashing via AST
- S-048: Brick Definition Hashing
- S-049: Git Blob Optimization
- S-050: Graph Schema Hash Fields

**Actions**:

1. Create `jig/outcomes/O-017.md`:
```markdown
---
id: O-017
type: outcome
---

# Change Detection Foundation

Enable JIG to detect when artifacts change by computing stable content fingerprints.

**Value**: Allows automated detection of spec/code/test drift without manual tracking.

**Acceptance Criteria**:
- Every artifact has a deterministic hash
- Hash changes only when semantic content changes
- Same content produces same hash across platforms
```

2. Create specifications S-044 through S-050 (see detailed specs below)

3. ~~Update bricks.yaml~~ — Moved to WU1 (brick validation requires module to exist)

**Reflect**:
- Clean separation: O/S nodes capture intent before code exists
- Brick definition deferred to WU1 since validation checks module existence
- All 8 intent nodes created with proper frontmatter

---

### Work Unit 1: Core Hashing Module

**Goal**: Create `src/jig/hashing.py` with all hash functions per J022.

**Acceptance Criteria**:
- [x] S-044 is implemented by `compute_hash()`
- [x] S-045 is implemented by `hash_intent_artifact()`
- [x] S-046 is implemented by `hash_function()`
- [x] S-047 is implemented by `hash_test()` (same as hash_function)
- [x] S-048 is implemented by `hash_brick()`
- [x] S-049 is implemented by `git_blob_hash()`
- [x] Tests verify determinism and cross-platform stability (27 tests)
- [x] `jigy validate` passes

**Implementation Notes**:

Create `src/jig/hashing.py`:
```python
"""Content hashing for JIG artifacts.

Implements J022: Content Hashing specification.
All hashes are SHA-256 truncated to 12 hex characters.
"""
import ast
import hashlib
import json
from pathlib import Path
from typing import Union

import yaml


def compute_hash(content: str) -> str:
    """Compute SHA-256 hash truncated to 12 hex chars.

    Args:
        content: UTF-8 string to hash

    Returns:
        12-character hex string
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:12]


def hash_intent_artifact(path: Path) -> str:
    """Hash a specification or outcome file.

    Computes canonical JSON of frontmatter + normalized body.
    Ignores trailing whitespace and line ending differences.

    Args:
        path: Path to .md file with YAML frontmatter

    Returns:
        12-character jig_hash
    """
    content = path.read_text(encoding='utf-8')
    # Normalize line endings
    content = content.replace('\r\n', '\n').replace('\r', '\n')

    # Parse frontmatter and body
    parts = content.split('---', 2)
    if len(parts) >= 3:
        frontmatter = yaml.safe_load(parts[1]) or {}
        body = parts[2].strip()
    else:
        frontmatter = {}
        body = content.strip()

    # Canonical representation
    canonical = json.dumps(
        {"frontmatter": frontmatter, "body": body},
        sort_keys=True,
        separators=(',', ':')
    )

    return compute_hash(canonical)


def hash_function(node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> str:
    """Hash function signature + body, excluding decorators.

    Decorators are tracked separately in 'implements' field.
    Uses ast.unparse() for canonical representation.

    Args:
        node: AST function node

    Returns:
        12-character jig_hash
    """
    # Clone node without decorators
    if isinstance(node, ast.AsyncFunctionDef):
        node_copy = ast.AsyncFunctionDef(
            name=node.name,
            args=node.args,
            body=node.body,
            decorator_list=[],
            returns=node.returns,
            type_comment=getattr(node, 'type_comment', None),
        )
    else:
        node_copy = ast.FunctionDef(
            name=node.name,
            args=node.args,
            body=node.body,
            decorator_list=[],
            returns=node.returns,
            type_comment=getattr(node, 'type_comment', None),
        )

    # Canonical source via ast.unparse
    canonical = ast.unparse(node_copy)
    return compute_hash(canonical)


# Alias for semantic clarity
hash_test = hash_function


def hash_brick(brick_dict: dict) -> str:
    """Hash a single brick's definition.

    Args:
        brick_dict: Brick definition dict (id, name, layer, units)

    Returns:
        12-character jig_hash
    """
    canonical = json.dumps(brick_dict, sort_keys=True, separators=(',', ':'))
    return compute_hash(canonical)
```

**Test Plan**:
- Unit tests: `tests/unit/test_hashing.py`
- Test determinism: same input = same output
- Test normalization: different whitespace = same hash
- Test isolation: decorator changes don't affect function hash
- Decorators added: `@jig.verifies("S-044")`, `@jig.verifies("S-045")`, etc.

**Files**:
- NEW: `src/jig/hashing.py`
- NEW: `tests/unit/test_hashing.py`
- UPDATE: `jig/bricks.yaml` — add B-hashing brick:
```yaml
  - id: B-hashing
    name: Content Hashing
    layer: 0
    units:
      - M-jig.hashing
```
  **Placement**: After B-intent-graph (layer 0, foundational utility)

**Human Verification**:
```bash
# After implementation:
python -c "from jig.hashing import hash_intent_artifact; print(hash_intent_artifact(Path('jig/specifications/S-001.md')))"
# Should print 12-char hex string

# Run tests:
pytest tests/unit/test_hashing.py -v
```

**Reflect**:
- AST node cloning requires `ast.copy_location()` + `ast.fix_missing_locations()` for `ast.unparse()` to work
- All 6 hash functions have @jig.implements decorators tracked in implementation graph
- 27 tests cover determinism, normalization, and edge cases
- Brick definition added and validated successfully

---

### Work Unit 2: Intent Graph Hashing

**Goal**: Integrate hashing into `intent_graph/generator.py` for specs, outcomes, and bricks.

**Acceptance Criteria**:
- [x] S-050 is implemented (graph schema with jig_hash)
- [x] Specification nodes have `jig_hash` field
- [x] Outcome nodes have `jig_hash` field
- [x] Brick nodes have `jig_hash` field
- [x] Regenerated intent-graph.ndjson includes hashes
- [x] `jigy validate` passes
- [x] 5 new tests verify hash fields in graph

**Implementation Notes**:

Modify `src/jig/intent_graph/generator.py`:
```python
from jig.hashing import hash_intent_artifact, hash_brick

# In generate_specification_nodes():
for spec_file in spec_files:
    node = {
        "id": spec_id,
        "type": "specification",
        "file": str(spec_file.relative_to(project_root)),
        "jig_hash": hash_intent_artifact(spec_file),  # NEW
    }
    nodes.append(node)

# In generate_outcome_nodes():
for outcome_file in outcome_files:
    node = {
        "id": outcome_id,
        "type": "outcome",
        "file": str(outcome_file.relative_to(project_root)),
        "specifies": [...],
        "jig_hash": hash_intent_artifact(outcome_file),  # NEW
    }
    nodes.append(node)

# In generate_brick_nodes():
for brick in bricks_config["bricks"]:
    node = {
        "id": brick["id"],
        "type": "brick",
        "name": brick["name"],
        "layer": brick["layer"],
        "file": "jig/bricks.yaml",
        "jig_hash": hash_brick(brick),  # NEW
    }
    nodes.append(node)
```

**Test Plan**:
- Integration test: generate intent graph, verify hashes present
- Test file: `tests/integration/test_intent_graph_hashing.py`
- Decorators: `@jig.verifies("S-050")`

**Files**:
- UPDATE: `src/jig/intent_graph/generator.py`
- UPDATE: `tests/jig/intent_graph/test_generator.py` (added TestIntentGraphHashing class)

**Human Verification**:
```bash
# Regenerate intent graph:
jigy intent rebuild

# Check for hashes in output:
head -20 jig/generated/intent-graph.ndjson | grep jig_hash
# Should see jig_hash fields in each node
```

**Reflect**:
- Added @jig.implements("S-050") to generate_intent_graph for traceability
- Imported hash_intent_artifact and hash_brick from jig.hashing
- 5 new tests verify spec/outcome/brick nodes all have jig_hash
- Tests verify hash changes when content changes, determinism across runs

---

### Work Unit 3: Implementation Graph Hashing

**Goal**: Add `jig_hash` to function nodes that have `implements` decorators.

**Acceptance Criteria**:
- [x] S-046 verified by tests
- [x] Function nodes with `implements` have `jig_hash` field
- [x] Decorators are excluded from hash computation
- [x] Regenerated implementation-graph.ndjson includes hashes
- [x] `jigy validate` passes
- [x] 5 new tests verify hash behavior

**Note**: Class nodes with `implements` do not get `jig_hash` per J022 (only functions specified).

**Implementation Notes**:

Modify `src/jig/impl_graph/analyzers/python_visitor.py`:
```python
from jig.hashing import hash_function

class PythonStructureVisitor(ast.NodeVisitor):
    # In visit_FunctionDef and visit_AsyncFunctionDef:
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        implements = self._extract_implements_decorators(node)

        func_node = {
            "id": func_id,
            "type": "function",
            "name": node.name,
            "file": self.file_path,
            "line": node.lineno,
            # ... existing fields ...
        }

        if implements:
            func_node["implements"] = implements
            func_node["jig_hash"] = hash_function(node)  # NEW

        self.nodes.append(func_node)
```

**Key Detail**: Hash is computed on the AST node **before** we strip decorators for the hash computation. The `hash_function()` internally clones without decorators.

**Test Plan**:
- Unit test: verify function hash excludes decorators
- Integration test: rebuild graph, verify hashes
- Test file: `tests/unit/test_impl_graph_hashing.py`
- Decorators: `@jig.verifies("S-046")`

**Files**:
- UPDATE: `src/jig/impl_graph/analyzers/python_visitor.py`
- UPDATE: `tests/unit/test_python_analyzer.py` (added TestImplementationGraphHashing class)

**Human Verification**:
```bash
# Rebuild implementation graph:
jigy impl rebuild

# Check for hashes:
grep '"implements"' jig/generated/implementation-graph.ndjson | grep '"type": "function"' | head -5
# Should see jig_hash field on function nodes with implements

# Verify decorator exclusion:
# Change a @jig.implements decorator target, rebuild
# The jig_hash should NOT change (only implements field changes)
```

**Reflect**:
- Imported hash_function from jig.hashing into python_visitor.py
- Added jig_hash computation in _visit_function() when implements is non-empty
- 5 tests verify: functions have hash, plain functions don't, decorators excluded, body changes hash, async works
- Classes with implements intentionally don't get hash (per J022 spec)

---

### Work Unit 4: Git Blob Optimization

**Goal**: Add `git_blob` field for tiered rebuild optimization.

**Acceptance Criteria**:
- [x] S-049 is implemented
- [x] `git_blob_hash()` function works in git repos
- [x] Intent graph nodes have optional `git_blob` field
- [x] Implementation graph nodes have optional `git_blob` field
- [x] Non-git environments gracefully omit `git_blob`
- [ ] Tiered rebuild uses git_blob for fast-path (deferred to future work)

**Implementation Notes**:

Add to `src/jig/hashing.py`:
```python
import subprocess

def git_blob_hash(file: Path) -> str | None:
    """Get git blob hash for file.

    Returns None if not in a git repo or file not tracked.

    Args:
        file: Path to file

    Returns:
        12-character git blob hash, or None
    """
    try:
        result = subprocess.run(
            ["git", "hash-object", str(file)],
            capture_output=True,
            text=True,
            cwd=file.parent,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()[:12]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None
```

Modify graph generators to include `git_blob`:
```python
git_blob = git_blob_hash(file_path)
if git_blob:
    node["git_blob"] = git_blob
```

**Tiered Rebuild Logic** (in builder.py):
```python
def rebuild_with_tiered_detection(previous_graph, files):
    for file in files:
        current_blob = git_blob_hash(file)
        prev_node = previous_graph.get_by_file(file) if previous_graph else None

        if prev_node and current_blob and prev_node.get("git_blob") == current_blob:
            # Fast path: reuse previous jig_hash
            new_node = {**prev_node, "git_blob": current_blob}
        else:
            # Slow path: recompute jig_hash
            jig_hash = compute_jig_hash(file)
            new_node = {..., "jig_hash": jig_hash}
            if current_blob:
                new_node["git_blob"] = current_blob
```

**Test Plan**:
- Unit test: git_blob_hash returns valid hash in git repo
- Unit test: git_blob_hash returns None outside git repo
- Integration test: tiered rebuild skips unchanged files
- Test file: `tests/unit/test_git_blob.py`

**Files**:
- UPDATE: `src/jig/hashing.py`
- UPDATE: `src/jig/intent_graph/generator.py`
- UPDATE: `src/jig/impl_graph/builder.py`
- NEW: `tests/unit/test_git_blob.py`

**Human Verification**:
```bash
# Check git_blob in generated graph:
jigy index && jigy impl rebuild
grep git_blob jig/generated/intent-graph.ndjson | head -3
# Should see git_blob fields

# Test tiered rebuild (timing):
time jigy impl rebuild  # First run
time jigy impl rebuild  # Second run (should be faster)
```

**Reflect**:
- git_blob_hash() already existed from WU1 with @jig.implements("S-049")
- Fixed path handling: resolve relative paths before calling git hash-object
- Added git_blob to intent graph: spec, outcome, and brick nodes
- Added git_blob to impl graph: class and function nodes
- 8 new tests verify git_blob presence and format in both graphs
- Tiered rebuild optimization deferred to future work (foundation in place)

---

## Detailed Specifications

### S-044: Hash Algorithm Standard

```markdown
---
id: S-044
type: specification
implements: [O-017]
---

# Hash Algorithm Standard

All JIG content hashes (`jig_hash`) SHALL use SHA-256 truncated to 12 hexadecimal characters.

**Acceptance Criteria**:
- Hash function accepts UTF-8 string input
- Output is exactly 12 lowercase hex characters
- Same input always produces same output (deterministic)

**Rationale**: 12 chars provides ~281 trillion values (collision negligible for change detection).
```

### S-045: Intent Artifact Hashing

```markdown
---
id: S-045
type: specification
implements: [O-017]
---

# Intent Artifact Hashing

Specifications and Outcomes SHALL be hashed using canonical JSON of frontmatter + body.

**Acceptance Criteria**:
- YAML frontmatter parsed and included in hash
- Body text stripped of trailing whitespace
- Line endings normalized to \n before hashing
- JSON uses sort_keys=True, separators=(',', ':')

**Rationale**: Semantic content changes detected while ignoring formatting noise.
```

### S-046: Function Hashing via AST

```markdown
---
id: S-046
type: specification
implements: [O-017]
---

# Function Hashing via AST

Functions with `@jig.implements` SHALL be hashed using AST normalization.

**Acceptance Criteria**:
- Function name, args, body, return type included in hash
- Decorators EXCLUDED from hash (tracked separately in implements field)
- Comments excluded (not in AST)
- Whitespace/formatting excluded (normalized by ast.unparse)

**Rationale**: Logic changes detected; formatting changes ignored.
```

### S-047: Test Hashing via AST

```markdown
---
id: S-047
type: specification
implements: [O-017]
---

# Test Hashing via AST

Tests with `@jig.verifies` SHALL use same hashing as functions (S-046).

**Acceptance Criteria**:
- Same algorithm as S-046
- Applied to test functions in verification graph

**Rationale**: Tests are code; same semantic hashing applies.
```

### S-048: Brick Definition Hashing

```markdown
---
id: S-048
type: specification
implements: [O-017]
---

# Brick Definition Hashing

Each brick SHALL be hashed independently using canonical JSON.

**Acceptance Criteria**:
- Each brick dict (id, name, layer, units) hashed separately
- Changing one brick doesn't affect others' hashes
- JSON uses sort_keys=True, separators=(',', ':')

**Rationale**: Fine-grained change tracking for architectural partitions.
```

### S-049: Git Blob Integration

```markdown
---
id: S-049
type: specification
implements: [O-017]
---

# Git Blob Integration

JIG MAY use git blob hashes for tiered rebuild optimization.

**Acceptance Criteria**:
- git_blob field is OPTIONAL on all nodes
- If git_blob unchanged, jig_hash can be reused (fast path)
- Non-git environments omit git_blob entirely
- All JIG functionality works without git_blob

**Rationale**: Performance optimization without correctness dependency.
```

### S-050: Graph Schema with Hashes

```markdown
---
id: S-050
type: specification
implements: [O-017]
---

# Graph Schema with Hashes

Graph nodes SHALL include jig_hash per J022 schema extensions.

**Acceptance Criteria**:
- Specification nodes: jig_hash REQUIRED
- Outcome nodes: jig_hash REQUIRED
- Brick nodes: jig_hash REQUIRED
- Function nodes with implements: jig_hash REQUIRED
- Test nodes with verifies: jig_hash REQUIRED
- git_blob OPTIONAL on all node types

**Rationale**: Content identity enables change detection in J023.
```

---

## Dependencies

**Internal**:
- Existing `intent_graph/generator.py`
- Existing `impl_graph/analyzers/python_visitor.py`
- Existing `impl_graph/builder.py`

**External**:
- Python 3.9+ (for `ast.unparse()`)
- PyYAML (already a dependency)
- Git (optional, for git_blob optimization)

---

## Risks

1. **AST stability**: Different Python versions may produce slightly different `ast.unparse()` output
   - Mitigation: Pin minimum Python version, test across versions

2. **Performance**: Computing hashes adds overhead to rebuild
   - Mitigation: git_blob optimization skips unchanged files

3. **Edge cases**: Malformed YAML frontmatter, encoding issues
   - Mitigation: Clear error messages, UTF-8 with fallback

---

## Success Criteria

- [ ] All S-044 through S-050 have @jig.implements in code
- [ ] All specs have @jig.verifies in tests
- [ ] `jigy validate` passes
- [ ] `jigy status` shows alignment for all new specs
- [ ] All tests pass
- [ ] Regenerated graphs include jig_hash fields
- [ ] J022 design decisions faithfully implemented

---

## Completion Summary

(To be filled after implementation)

**Scope Delivered**:
-

**Metrics**:
- Work Units:
- Specifications Created:
- Alignment:

**Reflection Roll-Up**:
-

---

_J022 enables content identity. J023 will use these hashes to detect changes._
