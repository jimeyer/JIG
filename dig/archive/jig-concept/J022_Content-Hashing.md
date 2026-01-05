---
title: "J022: Content Hashing"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1765161786
created_human: "2025-12-07 20:43 CST"
parent: "[[J017_JIG-Concept-v9]]"
children: ['[[B008_PLAN_Content-Hashing]]']
---
# J022: Content Hashing

**Status:** Proposal
**Date:** 2025-12-06
**Extends:** A001 (Core Artifacts Contract)

---

## Context

The JIG system measures alignment between specifications (S), functions (F), and tests (T). To detect when these artifacts change, JIG computes **content hashes** that fingerprint each artifact's semantic content.

**This document addresses one question: "How does JIG compute and store content identity?"**

J022 defines the hashing strategies and graph schema for storing hashes. The actual change detection logic (comparing current hashes to audit records) is defined in J023 (Audit Records and Triggers).

### What J022 Does

- Defines how to compute `jig_hash` for each artifact type
- Specifies graph schema extensions for storing hashes
- Describes `git_blob` optimization for faster rebuilds
- Guarantees cross-platform hash stability

### What J022 Does NOT Do

- Detect changes (that's J023 — requires audit records to compare against)
- Store audit decisions (that's J023)
- Define trigger CLI commands (that's J023)

### Design Goals

1. **Semantic hashing** — capture meaningful content, ignore formatting
2. **Deterministic** — same content always produces same hash
3. **Cross-platform** — identical results on Windows, macOS, Linux
4. **Git-optimized** — `git_blob` enables fast-path during rebuild
5. **S-F-T coverage** — hash specs, functions, and tests

---

## Decision

### 1. Content Hashing Strategy

All JIG content hashes (`jig_hash`) SHALL use **SHA-256 truncated to 12 hexadecimal characters** (48 bits).

**Rationale:**
- SHA-256 is standard, widely supported, and fast
- 12 chars provides ~281 trillion possible values (collision probability negligible)
- Matches git short hash conventions for familiarity
- Not for security—purely for change detection

**Terminology:**
- `jig_hash`: JIG's semantic content hash (AST-normalized code, canonical JSON for specs)
- `git_blob`: Git's byte-level hash of exact file contents (used for tiered optimization)
- `git_commit`: Git commit reference at audit time (used for auditor diff workflow, see J023)

#### 1.1 Intent Artifact Hashing

**Specifications and Outcomes:**

Hash the **canonical JSON representation** of parsed frontmatter plus normalized body:

```python
import hashlib
import json
import yaml

def hash_intent_artifact(path: Path) -> str:
    """Hash a specification or outcome file."""
    content = path.read_text()

    # Parse frontmatter and body
    parts = content.split('---', 2)
    frontmatter = yaml.safe_load(parts[1]) if len(parts) >= 3 else {}
    body = parts[2].strip() if len(parts) >= 3 else content.strip()

    # Canonical representation
    canonical = json.dumps(
        {"frontmatter": frontmatter, "body": body},
        sort_keys=True,
        separators=(',', ':')
    )

    return hashlib.sha256(canonical.encode()).hexdigest()[:12]
```

**Benefits:**
- Ignores trailing whitespace changes
- Stable across line ending differences (CRLF vs LF)
- Captures both metadata and content changes

**Bricks:**

Hash each **brick definition independently** (not the entire bricks.yaml):

```python
def hash_brick(brick_dict: dict) -> str:
    """Hash a single brick's definition."""
    canonical = json.dumps(brick_dict, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode()).hexdigest()[:12]
```

**Benefits:**
- Changing one brick doesn't invalidate others
- Moving a module between bricks shows exactly which two bricks changed
- Layer changes are detected per-brick

#### 1.2 Implementation Artifact Hashing

**Functions with `@jig.implements`:**

Hash the **AST-normalized function** excluding decorators:

```python
import ast

def hash_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Hash function signature + body, excluding decorators."""
    # Clone node without decorators
    node_copy = type(node)(
        name=node.name,
        args=node.args,
        body=node.body,
        decorator_list=[],  # Exclude - tracked separately in 'implements' field
        returns=node.returns,
        type_comment=getattr(node, 'type_comment', None),
    )

    # Canonical source via ast.unparse (Python 3.9+)
    canonical = ast.unparse(node_copy)
    return hashlib.sha256(canonical.encode()).hexdigest()[:12]
```

**What is hashed:**
- Function name
- Parameters and type annotations
- Return type annotation
- Function body (all statements)

**What is excluded:**
- Decorators (tracked in `implements` field, not content)
- Comments (not preserved in AST)
- Whitespace/formatting (normalized by AST)

**Benefits:**
- Formatting changes don't trigger false positives
- Actual logic changes are detected
- Decorator changes update the `implements` field, not the hash

#### 1.3 Verification Artifact Hashing

**Tests with `@jig.verifies`:**

Same strategy as implementation functions:

```python
def hash_test(node: ast.FunctionDef) -> str:
    """Hash test function, excluding decorators."""
    # Same approach as hash_function
    ...
```

**Rationale:** Tests are code. When test logic changes, we may need to re-verify that it still properly validates the specification.

---

### 2. Graph Schema Extensions

Hashes are stored in the graph files, computed during `jigy rebuild`.

#### 2.1 Intent Graph Changes

Add `jig_hash` and `git_blob` fields to all nodes:

**Specification Node:**
```json
{"id":"S-001","type":"specification","file":"jig/specifications/S-001.md","jig_hash":"a1b2c3d4e5f6","git_blob":"7f8e9d0c1b2a"}
```

**Outcome Node:**
```json
{"id":"O-001","type":"outcome","file":"jig/outcomes/O-001.md","specifies":["S-001","S-002"],"jig_hash":"b2c3d4e5f6a1","git_blob":"8a9b0c1d2e3f"}
```

**Brick Node:**
```json
{"id":"B-cli","type":"brick","name":"CLI Interface","layer":2,"file":"jig/bricks.yaml","jig_hash":"c3d4e5f6a1b2","git_blob":"9b0c1d2e3f4a"}
```

#### 2.2 Implementation Graph Changes

Add `jig_hash` and `git_blob` fields to function nodes that have `implements`:

```json
{"id":"F-jig.cli.layers.layers_command","type":"function","file":"src/jig/cli/layers.py","line":17,"implements":["S-040"],"signature":"layers_command(project_root: Path, ...) -> int","jig_hash":"d4e5f6a7b8c9","git_blob":"0c1d2e3f4a5b"}
```

**Note:** Functions without `@jig.implements` MAY omit the hash fields (no alignment to track).

#### 2.3 Verification Graph Changes

Add `jig_hash` and `git_blob` fields to test nodes that have `verifies`:

```json
{"id":"T-test_layers.test_layers_command","type":"test","file":"tests/unit/test_layers.py","verifies":["S-040"],"jig_hash":"e5f6a7b8c9d0","git_blob":"1d2e3f4a5b6c"}
```

**Note:** Tests without `@jig.verifies` MAY omit the hash fields.

---

### 3. Hash Stability Guarantees

To ensure hashes are stable across environments:

1. **Canonical JSON:** Always use `sort_keys=True, separators=(',', ':')`
2. **UTF-8 encoding:** All content SHALL be encoded as UTF-8 before hashing
3. **Normalized line endings:** Convert all line endings to `\n` before hashing
4. **Stripped whitespace:** Trailing whitespace removed from body content
5. **AST normalization:** Use `ast.unparse()` for consistent code representation

**Cross-platform guarantee:** The same source content SHALL produce the same hash on any platform (Windows, macOS, Linux).

---

### 4. Git Integration for Tiered Rebuild

JIG optionally integrates with git to optimize rebuild performance.

#### 4.1 The Optimization

Git already hashes every file. If git's blob hash hasn't changed, the file bytes are identical, so our `jig_hash` is also unchanged.

**The invariant:** If `git_blob` unchanged → file bytes unchanged → `jig_hash` unchanged.

#### 4.2 Tiered Rebuild Algorithm

```python
def rebuild_with_tiered_detection(previous_graph: Graph, files: list[Path]) -> Graph:
    """
    Rebuild graph with git_blob optimization.

    Uses git_blob to skip expensive parsing when file bytes unchanged.
    """
    new_nodes = []

    for file in files:
        current_blob = git_blob_hash(file)  # O(1) from git index
        prev_node = previous_graph.get_by_file(file)

        if prev_node and prev_node.git_blob == current_blob:
            # Fast path: reuse previous jig_hash (file bytes unchanged)
            new_nodes.append(prev_node.with_updated(git_blob=current_blob))
        else:
            # Slow path: parse file and compute semantic hash
            jig_hash = compute_jig_hash(file)
            new_nodes.append(Node(file=file, jig_hash=jig_hash, git_blob=current_blob))

    return Graph(new_nodes)

def git_blob_hash(file: Path) -> str:
    """Get git blob hash for file (from index or working tree)."""
    # Fast: reads from git index, no file I/O needed
    result = subprocess.run(
        ["git", "hash-object", str(file)],
        capture_output=True, text=True
    )
    return result.stdout.strip()[:12]  # Truncate to 12 chars for consistency
```

#### 4.3 Performance Benefit

- Level 1 (`git_blob` check): O(1) lookup from git index
- Level 2 (parse + hash): O(n) where n = file size + AST complexity
- In typical workflows, most files are unchanged → most files skip Level 2

#### 4.4 Non-Git Environments

This optimization is NOT required for correctness. In non-git environments:
- `git_blob` field is omitted from graph nodes
- Rebuild always uses slow path (parse every file)
- All other JIG functionality works normally

---

### 5. Edge Cases

#### 5.1 Function Implements Multiple Specs

```python
@jig.implements("S-001", "S-002")
def authenticate_and_log(user: str) -> Token:
    ...
```

The function has a single `jig_hash`. Both spec↔impl pairs share this hash. If the function changes, both pairs will show as changed (in J023 trigger detection).

#### 5.2 Multiple Functions Implement Same Spec

```python
@jig.implements("S-001")
def authenticate_password(user: str, password: str) -> Token: ...

@jig.implements("S-001")
def authenticate_oauth(provider: str, token: str) -> Token: ...
```

Each function has its own `jig_hash`. If the spec changes, J023 trigger detection will flag both pairs.

#### 5.3 Decorator Changed

If `@jig.implements("S-001")` changes to `@jig.implements("S-002")`:
- The function's `jig_hash` is **unchanged** (decorators excluded from hash)
- The `implements` field in the graph changes
- J023 trigger detection sees: old pair removed, new pair added

---

## Proposed Changes to A001

### Add jig_hash and git_blob fields to Intent Graph (Section 6.1)

```json
{"id":"S-001","type":"specification","file":"jig/specifications/S-001.md","jig_hash":"a1b2c3d4e5f6","git_blob":"7f8e9d0c1b2a"}
```

Add to field definitions:
- `jig_hash` (string, REQUIRED): SHA-256 hash (first 12 hex chars) of canonical content
- `git_blob` (string, OPTIONAL): Git blob hash (first 12 hex chars) for tiered rebuild optimization. Omitted in non-git environments.

### Add jig_hash and git_blob fields to Implementation Graph (Section 6.2)

```json
{"id":"F-auth.authenticate","type":"function","file":"src/auth.py","implements":["S-001"],"jig_hash":"d4e5f6a7b8c9","git_blob":"0c1d2e3f4a5b"}
```

Add to field definitions:
- `jig_hash` (string, CONDITIONAL): SHA-256 hash of AST-normalized function. REQUIRED if `implements` is non-empty.
- `git_blob` (string, OPTIONAL): Git blob hash for tiered rebuild optimization. Omitted in non-git environments.

### Add jig_hash and git_blob fields to Verification Graph (Section 6.3)

```json
{"id":"T-test_auth.test_authentication","type":"test","file":"tests/test_auth.py","verifies":["S-001"],"jig_hash":"e5f6a7b8c9d0","git_blob":"1d2e3f4a5b6c"}
```

Add to field definitions:
- `jig_hash` (string, CONDITIONAL): SHA-256 hash of AST-normalized test. REQUIRED if `verifies` is non-empty.
- `git_blob` (string, OPTIONAL): Git blob hash for tiered rebuild optimization. Omitted in non-git environments.

---

## Consequences

### What This Enables

1. **Content identity** — fingerprint artifacts for change detection
2. **Semantic comparison** — ignore formatting, detect logic changes
3. **Fast rebuilds** — `git_blob` optimization skips unchanged files
4. **Cross-platform consistency** — same hash everywhere

### What This Constrains

1. **Graph rebuild required** — must rebuild graphs to get current hashes
2. **Hash computation overhead** — minor, but present during rebuild
3. **Python 3.9+** — requires `ast.unparse()` for code normalization

### What This Does NOT Do

1. **Detect changes** — hashing computes identity; J025 compares to audit records
2. **Store audit decisions** — that's J025
3. **Define trigger workflow** — that's J025

---

## References

- **J023:** Audit Records and Triggers (uses hashes to detect changes)
- **A001:** Core Artifacts Contract (graph schemas)
- **J017:** JIG Concept v9 (S-F-T triangle)

---

_Hashing captures identity. Comparison detects change._
