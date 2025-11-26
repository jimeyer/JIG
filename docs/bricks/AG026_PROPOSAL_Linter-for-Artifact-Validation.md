
# AG026: PROPOSAL - Linter for Artifact Validation

**Status:** Proposal
**Date:** 2025-11-26
**Depends on:** A001 (Core Artifacts Contract)

---

## Problem Statement

The jig system relies on precise artifact contracts (A001) to function correctly. Invalid artifacts cause failures during graph generation, analysis, or runtime. Currently, there is no automated way to validate artifacts before attempting graph generation.

**Pain points:**
- Developers discover validation errors late (during graph generation or CLI commands)
- Error messages may be cryptic or buried in stack traces
- No single command to check "is my jig project well-formed?"
- Manual validation is error-prone and time-consuming

**Need:** A dedicated linter that validates all jig artifacts against the A001 contract BEFORE graph generation, providing clear, actionable error messages.

---

## Proposed Solution

Create a `jigy validate` command that runs multi-phase validation:

### Phase 1: Specification Validation (Pre-Graph)
Validates artifacts that exist before any graph generation:
- Specification files (`jig/specifications/S-*.md`)
- Outcome files (`jig/outcomes/O-*.md`) if present
- Decorator syntax in source/test files

### Phase 2: Implementation Graph Validation (Post-AST)
After AST parsing (but before graph file generation):
- Verify implementation graph nodes can be constructed
- Validate `@jig.implements` references to specs
- Check for duplicate function IDs

### Phase 3: Brick Validation (Post-Implementation-Graph)
After implementation graph is available:
- Validate `bricks.yaml` structure
- Check unit prefixes (M-, C-, F-)
- Verify units reference existing graph nodes
- Validate brick partition (no gaps, no overlaps)
- Verify no class splitting across bricks

### Phase 4: Verification Validation (Post-Coverage)
After test discovery:
- Validate `@jig.verifies` references to specs/outcomes

---

## Validation Rules (from A001 §10)

The linter SHALL enforce:

1. **ID Uniqueness**
   - All spec IDs unique within specifications
   - All outcome IDs unique within outcomes
   - All brick IDs unique within bricks.yaml

2. **Reference Integrity**
   - `@jig.implements` references existing spec IDs
   - `@jig.verifies` references existing spec/outcome IDs
   - Outcome `specifies` references existing spec IDs
   - Brick units reference existing implementation graph nodes

3. **Brick Partition**
   - Every function belongs to exactly one brick
   - No function belongs to zero bricks (gaps)
   - No function belongs to multiple bricks (overlaps)

4. **No Class Splitting**
   - All methods of a class belong to same brick

5. **Unit Prefix Validity**
   - All brick units start with M-, C-, or F-
   - Format follows `{Prefix}-{path}` pattern

6. **Required Fields**
   - Specs: `id`, `type`
   - Outcomes: `id`, `type`, `specifies`
   - Bricks: `id`, `name`, `units`

7. **Excluded Fields**
   - Specs SHALL NOT have: `brick`, `depends_on`, `content`
   - Outcomes SHALL NOT have: `brick`
   - Bricks SHALL NOT have: `depends_on`, `public_api`, `specs`

8. **File Naming**
   - Specs: `S-{number}.md` format
   - Outcomes: `O-{number}.md` format
   - Spec IDs match filenames (S-001.md → id: S-001)

---

## CLI Interface

```bash
# Run full validation
jigy validate

# Validate specific phase
jigy validate --phase specs
jigy validate --phase bricks
jigy validate --phase decorators

# Validate specific file
jigy validate jig/specifications/S-001.md
jigy validate jig/bricks.yaml

# JSON output for CI/tooling
jigy validate --format json

# Exit codes
# 0 = all validations passed
# 1 = validation failures
# 2 = validation errors (malformed YAML, missing files, etc.)
```

---

## Output Format

### Success Case
```
✓ Validating specifications (3 files)
✓ Validating outcomes (2 files)
✓ Validating bricks (1 file, 4 bricks)
✓ Validating implementation decorators (24 functions)
✓ Validating verification decorators (18 tests)
✓ Validating brick partition (no gaps, no overlaps)

All validations passed.
```

### Failure Case
```
✗ Validating specifications (3 files)
  ERROR: jig/specifications/S-004.md
    - Missing required field: 'type'
    - ID format invalid: 'SPEC-4' (expected 'S-004')

✗ Validating bricks (1 file, 4 bricks)
  ERROR: jig/bricks.yaml brick 'B-002'
    - Unit 'M-cli.invalid' not found in implementation graph
    - Unit 'auth.session' invalid: missing prefix (expected M-/C-/F-)

  ERROR: Brick partition violation
    - Function 'F-auth.session.authenticate' in 2 bricks: B-001, B-003
    - Function 'F-cli.main.run' in 0 bricks (gap)

✗ Validating implementation decorators
  ERROR: src/auth/session.py:42
    - @jig.implements("S-999"): spec does not exist

3 validation failures, 6 errors total.
```

### JSON Format (for CI/tooling)
```json
{
  "status": "failed",
  "phases": {
    "specifications": {
      "passed": false,
      "errors": [
        {
          "file": "jig/specifications/S-004.md",
          "line": null,
          "code": "MISSING_REQUIRED_FIELD",
          "message": "Missing required field: 'type'",
          "severity": "error"
        }
      ]
    },
    "bricks": {
      "passed": false,
      "errors": [
        {
          "file": "jig/bricks.yaml",
          "brick": "B-002",
          "code": "UNIT_NOT_FOUND",
          "message": "Unit 'M-cli.invalid' not found in implementation graph",
          "severity": "error"
        }
      ]
    }
  },
  "summary": {
    "total_errors": 6,
    "total_warnings": 0
  }
}
```

---

## Implementation Plan

### Work Unit Breakdown

**WU1: Specification File Validator**
- Parse YAML frontmatter from S-*.md files
- Validate required fields (id, type)
- Check ID format (S-{number})
- Check ID uniqueness
- Verify excluded fields not present
- Check filename matches ID

**WU2: Outcome File Validator**
- Parse YAML frontmatter from O-*.md files
- Validate required fields (id, type, specifies)
- Check ID format (O-{number})
- Check ID uniqueness
- Verify `specifies` references existing specs
- Verify excluded fields not present

**WU3: Brick Definition Validator**
- Parse bricks.yaml
- Validate structure (list of bricks)
- Check required fields (id, name, units)
- Check ID format (B-{number})
- Check ID uniqueness
- Validate unit prefix format (M-/C-/F-)
- Verify excluded fields not present

**WU4: Brick Partition Validator**
- Requires implementation graph
- Expand brick units (M-* → all F- in module)
- Build function-to-brick mapping
- Check every function in exactly one brick
- Check no class split across bricks

**WU5: Decorator Validator**
- Parse Python AST for @jig.implements decorators
- Validate decorator arguments are strings
- Check referenced spec IDs exist
- Parse @jig.verifies decorators
- Check referenced spec/outcome IDs exist

**WU6: CLI Integration**
- Add `jigy validate` command
- Support phase filtering (--phase)
- Support file filtering
- Implement JSON output format
- Implement exit codes

**WU7: Validation Reporting**
- Format human-readable error messages
- Include file paths, line numbers
- Group errors by file/phase
- Provide actionable suggestions

---

## Acceptance Criteria

1. **Command exists:** `jigy validate` command available
2. **Phase 1 works:** Validates specs/outcomes before graphs exist
3. **Phase 3 works:** Validates bricks.yaml against implementation graph
4. **Partition check works:** Detects gaps and overlaps in brick assignments
5. **Decorator check works:** Validates @jig decorators reference valid IDs
6. **Exit codes:** Returns 0 on success, non-zero on failure
7. **Error messages:** Clear, actionable, include file paths
8. **JSON output:** `--format json` produces machine-readable output
9. **All A001 §10 rules:** All validation rules enforced
10. **Documentation:** Usage documented in CLI help

---

## Dependencies

- **Implementation Graph:** WU4 (partition validator) requires implementation graph
- **AST Parser:** WU5 (decorator validator) requires Python AST parsing capability
- **CLI Framework:** Existing `jigy` CLI structure

---

## Future Extensions

### Warnings (non-blocking)
- Specs with no implementing functions
- Functions with no tests
- Outcomes with no verifying tests
- Unused brick definitions

### Fix Mode
```bash
jigy validate --fix
```
- Auto-rename files to match IDs
- Auto-format YAML frontmatter
- Remove excluded fields

### Watch Mode
```bash
jigy validate --watch
```
- Re-validate on file changes
- Useful during development

---

## Comparison to Existing Work

This proposal builds on:
- **AG024:** Defined artifact contracts (now formalized in A001)
- **B001 (current brick):** Implementation graph generation (WU4 depends on this)

This differs from:
- **Graph generation:** Linter validates BEFORE graphs built
- **Status command:** Linter checks structure, not metrics/alignment

---

## Open Questions

1. **Should WU4 require full graph generation, or just AST parsing?**
   - Option A: Require `jigy index` first (validates against persisted graph)
   - Option B: Parse AST in-memory (faster, but duplicates work)
   - **Recommendation:** Option A (validate against actual graph files)

2. **How to handle transient state?**
   - During development, graphs may be stale
   - Should linter auto-regenerate graphs if needed?
   - **Recommendation:** Require explicit `jigy index` first, error if graphs missing

3. **Should validator run automatically before other commands?**
   - e.g., `jigy status` runs validator first
   - **Recommendation:** No (too slow), but add `--validate` flag to commands

---

## Success Metrics

- Developers can validate project in < 5 seconds
- All A001 violations caught before graph generation
- Error messages resolve 80%+ of issues without reading docs
- Zero false positives on compliant projects

---

## References

- **A001:** Core Artifacts Contract (defines what to validate)
- **AG024:** Core Artifacts Contract (Refined) - original rationale
