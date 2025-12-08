# Specification Audit: S-027
**Date**: 2025-12-07

## Summary
- **Specification**: Auto-Validation in Rebuild Commands
- **Alignment Status**: UNTESTED
- **Outcome Alignment**: ALIGNED
- **Upstream Outcome**: O-004 (Early Error Detection in Artifact Validation)
- **Implementing Functions**: 1
- **Verifying Tests**: 3

## Specification Review

### Quality Assessment: GOOD

**ID Format**: Valid - `S-027` matches required `S-NNN` pattern in frontmatter.

**Required Fields**: Complete - Contains both `id: S-027` and `type: specification` in YAML frontmatter.

**Clear Intent**: Strong - Specification clearly describes auto-validation behavior for rebuild commands with a fail-fast design and power-user bypass option.

**Testable Criteria**: Well-defined - Contains 8 specific acceptance criteria:
1. `jigy impl rebuild` validates decorators (S-020) before building implementation graph
2. `jigy intent rebuild` validates specs and outcomes (S-018, S-019) before building intent graph
3. `jigy verify rebuild` validates test decorators (S-020) before building verification graph
4. Validation failures prevent graph generation (fail fast with clear errors)
5. Flag `--skip-validation` bypasses auto-validation on all rebuild commands
6. Auto-validation uses same validators as `jigy validate intent`
7. Error messages indicate validation failed before graph generation
8. Exit code 1 on validation failure (consistent with validate commands)

**Language Precision**: Good use of imperative language, though not strict RFC 2119 terminology. Uses clear, testable requirements.

**Rationale**: Well-articulated rationale explaining the fail-fast approach and power-user escape hatch.

## Outcome Alignment

**Status**: ALIGNED

**Upstream Outcome**: O-004 - Early Error Detection in Artifact Validation

S-027 is one of four specifications (S-023, S-024, S-025, S-027) that collectively realize O-004. The specification directly supports the outcome's goal of failing fast with validation errors before expensive graph generation operations.

**Value Alignment**:
- O-004 seeks to reduce wasted time from cryptic runtime failures
- S-027 implements this by auto-validating before graph generation
- Both emphasize fail-fast feedback loop for developer productivity

**Coverage**: The specification properly addresses the "rebuild commands automatically validate artifacts before generating graphs" acceptance criterion from O-004.

## Implementation Analysis

| Function | File | Line | Covers Criteria |
|----------|------|------|-----------------|
| auto_validate_decorators | /Users/jamesmeyer/Code/jig/src/jig/cli/validate.py | 208 | Criterion 1 (partial), 4, 6, 7, 8 |

### Implementation Coverage Assessment

**Implemented** (1/8 criteria):
1. **Criterion 1**: `jigy impl rebuild` validates decorators - IMPLEMENTED
   - Line 235-236 in main.py calls `auto_validate_decorators()` before graph building
   - `--skip-validation` flag exists (line 199-201) and is respected (line 235)

**Not Implemented** (2/8 criteria):
2. **Criterion 2**: `jigy intent rebuild` validates specs and outcomes - NOT IMPLEMENTED
   - Intent rebuild command (line 283-320 in main.py) has no auto-validation
   - No call to validation functions before `generate_intent_graph()`
   - No `--skip-validation` flag on intent rebuild command

3. **Criterion 3**: `jigy verify rebuild` validates test decorators - NOT IMPLEMENTED
   - No `jigy verify` command group exists in the codebase
   - No verification graph rebuild command found

**Partially Implemented** (5/8 criteria):
4. **Criterion 4**: Validation failures prevent graph generation - PARTIAL
   - Implemented for `impl rebuild` (sys.exit(1) on line 237)
   - Missing for `intent rebuild` and `verify rebuild`

5. **Criterion 5**: `--skip-validation` flag bypasses auto-validation - PARTIAL
   - Implemented for `impl rebuild` only
   - Missing for `intent rebuild` and `verify rebuild`

6. **Criterion 6**: Uses same validators as `jigy validate intent` - PARTIAL
   - `impl rebuild` uses `validate_decorator_files()` (same as validate intent)
   - Missing for intent and verify rebuilds

7. **Criterion 7**: Error messages indicate validation failed before graph generation - PARTIAL
   - Implemented for `impl rebuild` (line 226, 230)
   - Missing for other rebuild commands

8. **Criterion 8**: Exit code 1 on validation failure - PARTIAL
   - Implemented for `impl rebuild` (sys.exit(1) on line 237)
   - Missing for other rebuild commands

### Architecture Notes

The `auto_validate_decorators()` function is well-designed:
- Returns boolean for success/failure
- Reuses existing validators (`validate_decorator_files`)
- Provides clear error messages with suggestion to use `--skip-validation`
- Properly handles missing directories

However, the implementation is incomplete as it only covers one of three rebuild commands.

## Verification Analysis

| Test | File | Line | Validates Criteria |
|------|------|------|-------------------|
| test_impl_rebuild_auto_validates | /Users/jamesmeyer/Code/jig/tests/cli/test_validate.py | 248 | Criterion 1, 4, 7, 8 |
| test_impl_rebuild_skip_validation | /Users/jamesmeyer/Code/jig/tests/cli/test_validate.py | 274 | Criterion 5 (partial) |
| test_impl_rebuild_validates_only_decorators | /Users/jamesmeyer/Code/jig/tests/cli/test_validate.py | 296 | Criterion 1, 6 |

### Test Coverage Assessment

**Well-Tested** (4/8 criteria for impl rebuild):
1. **Criterion 1**: Tests verify decorator validation on `impl rebuild` (line 248-271)
2. **Criterion 4**: Test confirms validation failures prevent graph generation (line 268-271)
3. **Criterion 5**: Test confirms `--skip-validation` bypasses validation for impl rebuild (line 274-293)
4. **Criterion 7**: Test checks error output mentions validation (line 271)
5. **Criterion 8**: Test verifies exit code 1 on validation failure (line 270)

**Partially Tested** (1/8 criteria):
6. **Criterion 6**: Test at line 296 verifies that impl rebuild only validates decorators (not full intent validation), confirming proper scope limitation

**Untested** (2/8 criteria):
2. **Criterion 2**: No tests for `intent rebuild` auto-validation (command doesn't implement it)
3. **Criterion 3**: No tests for `verify rebuild` auto-validation (command doesn't exist)

### Test Quality

The existing tests are well-structured:
- Use isolated filesystems for clean test environments
- Test both success and failure paths
- Verify error messages and exit codes
- Test the skip flag behavior
- Verify validation scope is correctly limited to decorators

However, tests only cover the implemented portion (`impl rebuild`). The specification promises functionality for `intent rebuild` and `verify rebuild` that neither exists nor is tested.

## Recommendations

### Critical Issues

1. **Complete Intent Rebuild Auto-Validation** (Criterion 2)
   - Add auto-validation to `jigy intent rebuild` command
   - Validate specs and outcomes (S-018, S-019) before calling `generate_intent_graph()`
   - Add `--skip-validation` flag to intent rebuild command
   - Follow the same pattern as `impl rebuild` (lines 235-237 in main.py)

2. **Implement Verify Rebuild Command** (Criterion 3)
   - Create `jigy verify` command group
   - Implement `jigy verify rebuild` command
   - Add auto-validation of test decorators (S-020)
   - Add `--skip-validation` flag
   - Follow existing patterns from `impl rebuild`

3. **Write Missing Tests**
   - Add tests for `intent rebuild` auto-validation once implemented
   - Add tests for `verify rebuild` auto-validation once implemented
   - Ensure all 8 criteria are tested across all three rebuild commands

### Enhancement Opportunities

4. **Create Shared Auto-Validation Helper**
   - Extract common auto-validation pattern from `impl rebuild`
   - Create reusable function that can be called by all rebuild commands
   - Reduces code duplication and ensures consistency

5. **Improve Error Messages**
   - Consider adding suggestion to run `jigy validate intent` for detailed errors
   - Show count of validation errors in fail-fast message

6. **Documentation**
   - Update command help text to mention auto-validation behavior
   - Document the `--skip-validation` flag use cases more clearly

### Specification Clarification

7. **Update Specification if Scope Changed**
   - If `verify rebuild` is not planned, remove Criterion 3 from S-027
   - If `intent rebuild` auto-validation is intentionally deferred, document why
   - Consider splitting into multiple specifications if phased implementation is intended

## Alignment Score

### Implementation Coverage
- **Fully Implemented**: 1/8 criteria (12.5%)
- **Partially Implemented**: 5/8 criteria (62.5%)
- **Not Implemented**: 2/8 criteria (25%)
- **Implementation Score**: 3.5/8 = **44%**

### Verification Coverage
- **Tested**: 5/8 criteria for impl rebuild (62.5%)
- **Untested**: 3/8 criteria (37.5% - waiting on implementation)
- **Verification Score**: 5/8 = **63%**

### Overall Alignment
- **Overall Score**: **50%** (average of implementation and verification)
- **Overall Status**: **UNTESTED** - Implementation exists but is incomplete; tests only cover the implemented portion

### Status Rationale

The specification receives an UNTESTED rating because:
1. Implementation exists and works correctly for `impl rebuild` (F→S edge exists)
2. Tests verify the `impl rebuild` implementation (T→S edge exists, T→F edge exists)
3. However, 2 of 3 rebuild commands specified are missing entirely
4. Only 44% of specified criteria are fully implemented
5. The implementation is a perfect triangle for criterion 1, but criteria 2-3 have no implementation or tests

This is better than UNVERIFIED (which has implementation but no tests) but not PERFECT (which requires all criteria implemented and tested). The partial implementation creates an UNTESTED status - some parts are perfect triangles, other parts are missing entirely.
