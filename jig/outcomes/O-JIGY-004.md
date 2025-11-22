---
id: O-JIGY-004
type: outcome
title: JIG scanning excludes test fixtures and template files
subsystem: jigy-tool
status: active
created: 2025-11-21
---

# Outcome: Clean Node Index Without Pollution

## Value Proposition

Developers using JIG need a clean, trustworthy node index that reflects only real Intent (O/S) and implementation (C/T) nodes. The index should not be polluted by:
- Test fixture annotations (mock @jig tags in test string literals)
- Template markdown files (examples, placeholders)
- Build artifacts and generated files

**User Impact:**
- Developers trust the index as source of truth for "what actually exists"
- No duplicate node warnings from test fixtures
- No confusion from template files appearing in active node counts
- Clean `jigy index rebuild` output without noise

## Current Problem

Running `jigy index rebuild` on the jig project reveals:
1. **Test fixture pollution:** Test files contain @jig annotations in string literals (test fixtures) that are scanned as real nodes - e.g., `C-TEST-001` appears in 9 different test files, generating duplicate warnings
2. **Template file inclusion:** Template/example markdown files (e.g., `O-PERF-001.md` with `subsystem: null`) are included in the index despite not being real Intent nodes

This pollutes the index and makes it unreliable.

## Success Criteria

1. **Zero Test Fixture Duplicates**
   - `jigy index rebuild` produces zero duplicate node warnings from test fixtures
   - Fixture patterns like `C-TEST-*`, `T-TEST-*`, `C-MOCK-*` excluded automatically
   - Real implementation nodes still discovered correctly (<5% false negatives)

2. **Zero Template File Pollution**
   - Template files with `status: template` not included in index
   - Example files with `status: draft` excluded from active counts
   - Deprecated nodes properly filtered

3. **User Control via .jigignore**
   - `.jigignore` file patterns exclude specified paths
   - Gitignore-style syntax for familiarity
   - Project-specific exclusions supported

## Acceptance Tests

```bash
# Against jig project itself
cd ~/Code/jig

# Should create .jigignore if missing
jig init

# Should produce clean output with zero fixture duplicates
jigy index rebuild
# Expected: No warnings about C-TEST-*, T-TEST-*, C-MOCK-* duplicates

# Verify filtering works
grep -r "C-TEST-001" tests/  # Should find fixtures in test files
jigy index rebuild --dry-run | grep "C-TEST-001"  # Should NOT appear in index
```

## Related Specifications

- S-JIGY-011: Exclusion filtering prevents test fixture pollution

## Metrics

- **Accuracy:** 0 duplicate warnings from test fixtures
- **Precision:** <5% false negatives (real nodes incorrectly excluded)
- **Usability:** Clean index build without manual intervention

## Discovery Context

**Discovered during:** WU8-10 implementation (annotation scanning and index rebuild)
**Root cause:** Scanner treats all @jig annotations equally, doesn't distinguish between real nodes and test fixtures
**Impact:** Unreliable index, confusing validation output, loss of developer trust
