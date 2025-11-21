---
id: O-JIGY-003
type: outcome
title: Code and Intent stay synchronized
subsystem: jigy-tool
status: active
created: 2025-11-21
---

# Outcome: Code-Intent Synchronization

## Value Proposition

Intent graphs become stale if they're not connected to actual code. When code changes but Intent nodes aren't updated, the graph becomes misleading. When new code is added without annotations, it becomes invisible to the Intent system.

Developers need automatic synchronization: code annotations (`@jig`) link to Intent nodes, validation catches drift, index rebuild regenerates graph from sources.

**User Impact:**
- Code changes trigger validation failures if Intent isn't updated
- New code without @jig annotations gets caught in review
- Refactoring preserves Intent traceability
- CI/CD can enforce Intent alignment

## Current Problem

jigy v0.1.0 doesn't discover `@jig` annotations in code/tests, can't validate that annotations reference valid Intent nodes, can't rebuild the graph index from sources. This means:
- Code and Intent drift apart over time
- No automated way to detect missing annotations
- Manual graph-index.yaml maintenance is error-prone

## Success Criteria

1. **Annotation Discovery** (<2s for 10k files)
   - Fast scan of src/ and test/ directories
   - Find all `@jig C-XXX-NNN` and `@jig T-XXX-NNN` annotations
   - Extract node ID, relationships, metadata, file location

2. **Index Rebuild** (<3s for 1000-node graph)
   - Regenerate graph-index.yaml from sources
   - Source of truth: Markdown frontmatter (O/S) + code annotations (C/T)
   - Warns on conflicts (duplicate IDs, missing references)
   - Validates before writing

3. **Annotation Validation** (<1s for 1000 annotations)
   - Check all @jig node IDs exist in Intent graph
   - Check relationship targets exist
   - Check no duplicate annotations (same ID in multiple locations)
   - Check format is valid

4. **CI/CD Integration**
   - `jigy validate --check-annotations` in CI pipeline
   - Fails build if annotations broken
   - Fails if new code missing @jig annotations (configurable)

## Use Cases

**UC1: Discovering Code Nodes**
```bash
jigy scan
# Finds all @jig annotations in src/ and test/
# Reports: 24 code nodes, 37 test nodes discovered
```

**UC2: Rebuilding Index**
```bash
jigy index --rebuild
# Regenerates graph-index.yaml from:
# - jig/outcomes/*.md (frontmatter)
# - jig/specifications/*.md (frontmatter)
# - src/**/*.py (@jig annotations)
# - test/**/*.py (@jig annotations)
```

**UC3: Validating Annotations**
```bash
jigy validate --check-annotations
# Checks:
# ✓ All @jig node IDs exist in Intent graph
# ✓ All relationship targets valid
# ✗ C-AUTH-099 references non-existent S-AUTH-099
# ✗ No annotation found for code implementing S-PERF-001
```

**UC4: CI Pipeline**
```bash
# In .github/workflows/ci.yml
- name: Validate JIG alignment
  run: |
    jigy validate --check-all
    jigy validate --check-annotations
```

## Acceptance Tests

```bash
# Scan performance
cd ~/Code/ASE-A
time jigy scan
# Should complete in <2 seconds

# Rebuild performance
time jigy index --rebuild
# Should complete in <3 seconds

# Validation performance
time jigy validate --check-annotations
# Should complete in <1 second

# Detect broken annotations
echo '# @jig C-TEST-999 implements:S-NONEXISTENT-999' >> test_file.py
jigy validate --check-annotations
# Should report error: S-NONEXISTENT-999 not found
```

## Related Specifications

- S-JIGY-008: Fast annotation scanner
- S-JIGY-009: Index rebuild from sources
- S-JIGY-010: Annotation validation

## Metrics

- **Scan Speed:** <2 seconds for 10,000 files
- **Rebuild Speed:** <3 seconds for 1000-node graph
- **Validation Speed:** <1 second for 1000 annotations
- **Coverage:** 100% of code with Intent linkage has @jig annotations
- **Accuracy:** 0% false positives in validation (only report real issues)

