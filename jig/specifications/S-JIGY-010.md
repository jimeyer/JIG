---
id: S-JIGY-010
type: specification
title: Annotation validation checks all @jig references
subsystem: jigy-tool
status: active
created: 2025-11-21
implements:
  - O-JIGY-003
---

# Specification: Annotation Validation

## Purpose

Validate that `@jig` annotations in code and tests reference valid Intent nodes, have correct format, and maintain consistency with the Intent graph. Enable CI/CD integration to catch drift between code and Intent.

## Requirements

### 1. Validation Command

**Command:** `jigy validate --check-annotations [--strict]`

```bash
$ jigy validate --check-annotations

Validating @jig annotations...

Scanning:
  ✓ src/ (24 code nodes)
  ✓ test/ (37 test nodes)

Checks (61 annotations):
  ✓ All node IDs valid format
  ✓ All relationship targets exist
  ✓ All subsystem assignments match graph
  ✗ 2 broken references found
  ⚠ 3 orphaned Intent nodes (no implementations)

Errors (2):
  ✗ src/auth/jwt.py:42
    C-AUTH-001 implements:S-AUTH-099
    Target S-AUTH-099 doesn't exist in Intent graph
  
  ✗ test/auth/test_jwt.py:18
    T-AUTH-042 verifies:S-AUTH-099
    Target S-AUTH-999 doesn't exist in Intent graph

Warnings (3):
  ⚠ S-PERF-001 has no code implementation (no C node found)
  ⚠ S-GATEWAY-003 has no code implementation
  ⚠ S-PROTOCOL-008 has no test verification (no T node found)

Summary:
  ✓ 59 annotations valid
  ✗ 2 errors (broken references)
  ⚠ 3 warnings (missing implementations)

Exit code: 1 (errors found)
```

### 2. Validation Checks

#### Check 1: Node ID Format

All `@jig` node IDs must match pattern:

```regex
[CT]-[A-Z]+-\d+
```

**Valid:** `C-AUTH-001`, `T-PROTOCOL-042`  
**Invalid:** `C-001`, `AUTH-001`, `C-auth-001`, `C-AUTH-1`

**Severity:** ERROR

#### Check 2: Relationship Target Existence

All relationship targets must exist in Intent graph:

```python
# @jig C-AUTH-001 implements:S-AUTH-001
#                  ^^^^^^^^^ Must exist in graph
```

For each annotation:
- Extract relationship targets (implements:, verifies:, depends:)
- Check each target exists in NodeRegistry
- Report if target not found

**Severity:** ERROR (broken reference)

#### Check 3: Edge Type Validity

Relationship types must be semantically valid:

```python
# @jig C-AUTH-001 implements:S-AUTH-001  ✓ Code implements Spec
# @jig T-AUTH-001 verifies:S-AUTH-001    ✓ Test verifies Spec
# @jig C-AUTH-001 verifies:S-AUTH-001    ✗ Code should implement, not verify
```

**Severity:** ERROR (invalid relationship type)

#### Check 4: Subsystem Consistency

Annotation subsystem should match Intent graph:

```python
# In annotation:
# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:auth

# In S-AUTH-001 markdown:
# subsystem: authentication  # Mismatch!
```

**Severity:** WARNING (suggest fixing annotation or Intent node)

#### Check 5: Duplicate Annotations

Same node ID in multiple locations:

```python
# src/auth/jwt.py:42
# @jig C-AUTH-001 implements:S-AUTH-001

# src/auth/token.py:18
# @jig C-AUTH-001 implements:S-AUTH-002  # Duplicate!
```

**Severity:** ERROR (ambiguous implementation location)

#### Check 6: Orphaned Intent Nodes

Intent nodes (O/S) with no implementations or tests:

```python
# S-PERF-001 exists in jig/specifications/
# But no C node implements it
# And no T node verifies it
```

**Severity:** WARNING (may be intentional for new specs)

**Filters:**
- Ignore deprecated/archived specs
- Ignore specs marked `status: planned`

### 3. Strict Mode

**Command:** `jigy validate --check-annotations --strict`

In strict mode:
- Warnings become ERRORS (fail build)
- Requires 100% coverage (all S nodes have C implementations)
- Requires all S nodes have T verifications
- No orphaned nodes allowed

Use in CI/CD to enforce strict alignment.

### 4. JSON Output for CI

**Command:** `jigy validate --check-annotations --json`

```json
{
  "valid": false,
  "annotations_checked": 61,
  "errors": [
    {
      "type": "broken_reference",
      "file": "src/auth/jwt.py",
      "line": 42,
      "node_id": "C-AUTH-001",
      "target": "S-AUTH-099",
      "message": "Target S-AUTH-099 doesn't exist"
    }
  ],
  "warnings": [
    {
      "type": "orphaned_spec",
      "node_id": "S-PERF-001",
      "message": "No code implementation found"
    }
  ],
  "summary": {
    "valid_annotations": 59,
    "error_count": 2,
    "warning_count": 3
  }
}
```

### 5. Coverage Metrics

Report coverage statistics:

```bash
$ jigy validate --check-annotations --coverage

Annotation Coverage:

Specifications (47):
  ✓ 44 implemented (93.6%)
  ✗ 3 not implemented (S-PERF-001, S-GATEWAY-003, S-PROTOCOL-008)

Specifications with tests:
  ✓ 42 verified (89.4%)
  ✗ 5 not verified

Code nodes:
  ✓ 24 annotated
  ? Unknown (can't detect non-annotated code)

Test nodes:
  ✓ 37 annotated
  ? Unknown (can't detect non-annotated tests)

Target: >90% specification coverage
Status: PASS (93.6% implementation, 89.4% verification)
```

### 6. Fix Suggestions

Provide actionable fix suggestions:

```bash
$ jigy validate --check-annotations

Error: C-AUTH-001 implements:S-AUTH-099 (target doesn't exist)
  File: src/auth/jwt.py:42
  
  Suggestions:
    - Did you mean S-AUTH-001? (similar name)
    - Create S-AUTH-099 in jig/specifications/
    - Remove relationship if no longer needed
  
  Fix:
    # Change annotation to:
    # @jig C-AUTH-001 implements:S-AUTH-001 subsystem:auth
```

## Implementation Notes

**Location:** `jigy/validators/annotation_validator.py`

**Dependencies:**
- AnnotationScanner (S-JIGY-008) - discover annotations
- NodeRegistry (S-JIGY-003) - check targets exist
- GraphValidator (S-JIGY-004) - edge type rules

**Validation Process:**
```python
# @jig C-JIGY-010 implements:S-JIGY-010 subsystem:jigy-tool interface:public
def validate_annotations(registry):
    """Validate all @jig annotations against Intent graph"""
    
    # 1. Scan for annotations
    annotations = scan_annotations(['src', 'test'])
    
    errors = []
    warnings = []
    
    # 2. Check each annotation
    for annotation in annotations:
        # Check node ID format
        if not is_valid_node_id(annotation.id):
            errors.append(f"Invalid node ID: {annotation.id}")
        
        # Check relationship targets exist
        for rel_type, targets in annotation.relationships.items():
            for target in targets:
                if not registry.has_node(target):
                    errors.append(f"{annotation.id} {rel_type}:{target} - target doesn't exist")
        
        # Check edge type validity
        for rel_type, targets in annotation.relationships.items():
            for target in targets:
                target_node = registry.get_node(target)
                if not is_valid_edge_type(annotation.type, rel_type, target_node.type):
                    errors.append(f"Invalid relationship: {annotation.type} {rel_type} {target_node.type}")
        
        # Check for duplicates
        if registry.has_node(annotation.id):
            existing = registry.get_node(annotation.id)
            if existing.file != annotation.file:
                errors.append(f"Duplicate node ID: {annotation.id} in {annotation.file} and {existing.file}")
    
    # 3. Check for orphaned Intent nodes
    for spec in registry.get_nodes_by_type("specification"):
        if spec.status in ["active"]:
            # Check for implementation
            implementations = registry.get_edges_to(spec.id, type="implements")
            if len(implementations) == 0:
                warnings.append(f"{spec.id} has no code implementation")
            
            # Check for tests
            verifications = registry.get_edges_to(spec.id, type="verifies")
            if len(verifications) == 0:
                warnings.append(f"{spec.id} has no test verification")
    
    return ValidationResult(errors, warnings)
```

**Performance Target:** <1 second for 1000 annotations

## Test Cases

```python
# @jig T-JIGY-027 verifies:S-JIGY-010 subsystem:jigy-tool
def test_validate_broken_reference():
    """Test detection of annotation pointing to non-existent Intent node"""
    registry = create_test_registry()
    annotations = [
        Annotation(id="C-TEST-001", implements=["S-NONEXISTENT-999"], ...)
    ]
    
    result = validate_annotations(registry, annotations)
    
    assert not result.valid
    assert "S-NONEXISTENT-999" in result.errors[0]

# @jig T-JIGY-028 verifies:S-JIGY-010 subsystem:jigy-tool
def test_validate_orphaned_specs():
    """Test detection of specs without implementations"""
    registry = NodeRegistry()
    registry.add_node(Node(id="S-TEST-001", type="specification", status="active"))
    # No C node implements S-TEST-001
    
    result = validate_annotations(registry, [])
    
    assert "S-TEST-001" in result.warnings[0]
    assert "no code implementation" in result.warnings[0]

# @jig T-JIGY-029 verifies:S-JIGY-010 subsystem:jigy-tool
def test_validate_duplicate_annotations():
    """Test detection of duplicate node IDs in annotations"""
    annotations = [
        Annotation(id="C-TEST-001", file="src/a.py", line=10),
        Annotation(id="C-TEST-001", file="src/b.py", line=20)  # Duplicate!
    ]
    
    result = validate_annotations(registry, annotations)
    
    assert not result.valid
    assert "Duplicate" in result.errors[0]
```

## CI/CD Integration

**GitHub Actions example:**

```yaml
# .github/workflows/jig-validate.yml
name: JIG Validation

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install jigy
        run: pip install jigy
      - name: Validate JIG alignment
        run: |
          jigy validate --check-all
          jigy validate --check-annotations
```

**Exit codes:**
- 0: All validations passed
- 1: Errors found (fail build)
- 2: Warnings only (optionally fail with --strict)

## References

- O-JIGY-003: Code and Intent stay synchronized
- S-JIGY-003: Unified node registry (provides Intent data)
- S-JIGY-004: Edge validation (reuses edge type rules)
- S-JIGY-008: Annotation scanner (discovers annotations)
- S017 Analysis: Part 3.4.3 (Annotation validation)
- JIG v6.1 Spec: §1.3 (Reality annotations), §7.4 (Validate alignment)

