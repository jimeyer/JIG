
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

Create a `jigy validate` command with three distinct validation phases that align with the natural development workflow:

### Phase 1: Validate Intent (Pre-Graph)
**Can run WITHOUT graphs existing**

Validates human-authored artifacts before any graph generation:
- Specification files (`jig/specifications/S-*.md` YAML frontmatter)
- Outcome files (`jig/outcomes/O-*.md` YAML frontmatter) if present
- Decorator references (`@jig.implements`, `@jig.verifies` point to valid IDs)

**CLI:** `jigy validate intent`

**Use case:** "Are my human-authored artifacts well-formed?"

### Phase 2: Build Graphs (with Auto-Validation)
**Graph generation IS validation**

When rebuilding graphs, auto-validate intent first:
- `jigy intent rebuild` → validates specs/outcomes, builds intent-graph.ndjson
- `jigy impl rebuild` → validates decorators, builds implementation-graph.ndjson
- `jigy verify rebuild` → validates test decorators, builds verification-graph.ndjson

**Auto-validation:** All rebuild commands validate intent artifacts BEFORE building. Use `--skip-validation` flag to bypass.

**Graph validation:** If graph generation succeeds, graphs are structurally valid (valid by construction). No separate validation needed unless graphs are hand-edited (which violates A001).

### Phase 3: Validate Bricks (Post-Graph)
**REQUIRES implementation graph to exist**

Validates brick definitions against generated implementation graph:
- Brick definitions (`bricks.yaml` structure and required fields)
- Brick partition (every function in exactly one brick, no class splitting)
- Unit references (all brick units point to existing graph nodes)

**CLI:** `jigy validate bricks`

**Use case:** "Do my brick definitions match the codebase?"

---

## Three Validation Phases

### Clear Separation of Concerns

**Phase 1: Validate Intent (Pre-Graph)**
- **What:** Specs, outcomes, decorator references
- **When:** Before graphs exist
- **Requires:** Only human-authored files
- **Command:** `jigy validate intent`
- **Use case:** "Are my inputs valid?"

**Phase 2: Build Graphs (with Auto-Validation)**
- **What:** Generate graph files from valid artifacts
- **When:** After intent validation passes
- **Requires:** Valid intent artifacts
- **Commands:** `jigy intent rebuild`, `jigy impl rebuild`, `jigy verify rebuild`
- **Auto-validates:** Intent artifacts before building
- **Use case:** "Build the data from validated inputs"

**Phase 3: Validate Bricks (Post-Graph)**
- **What:** Bricks.yaml against implementation graph
- **When:** After implementation graph exists
- **Requires:** implementation-graph.ndjson
- **Command:** `jigy validate bricks`
- **Use case:** "Do my bricks align with the implementation?"

**No circular dependencies:** Intent validates without graphs → Graphs generated from valid intent → Bricks validated against graphs.

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
# Pre-graph validation (Phase 1)
jigy validate intent
  # Validates: specs, outcomes, decorator references
  # Can run: anytime, before graphs exist
  # Use case: "are my human-authored artifacts well-formed?"

# Post-graph validation (Phase 3)
jigy validate bricks
  # Validates: bricks.yaml against implementation-graph.ndjson
  # Requires: implementation graph exists
  # Use case: "do my brick definitions match the codebase?"

# Full validation (smart)
jigy validate
  # Runs: intent validation, then brick validation (if graphs exist)
  # Can run: anytime (skips brick validation if no graphs)
  # Use case: "check everything that's possible to check"

# Granular intent validation
jigy validate intent specs       # only specifications
jigy validate intent outcomes    # only outcomes
jigy validate intent decorators  # only decorators

# Granular brick validation
jigy validate bricks definitions # only bricks.yaml structure
jigy validate bricks partition   # only partition constraint

# Auto-validation in rebuild commands (Phase 2)
jigy impl rebuild                     # validates decorators first
jigy impl rebuild --skip-validation   # skip validation (power users)

# JSON output for CI/tooling
jigy validate --format json
jigy validate intent --format json
jigy validate bricks --format json

# Exit codes
# 0 = all validations passed
# 1 = validation failures
# 2 = validation errors (malformed YAML, missing files, etc.)
```

---

## Output Format

### Success Case (Intent Validation)
```
$ jigy validate intent
✓ Validating specifications (3 files)
✓ Validating outcomes (2 files)
✓ Validating implementation decorators (24 functions)
✓ Validating verification decorators (18 tests)

Intent validation passed.
```

### Success Case (Brick Validation)
```
$ jigy validate bricks
✓ Validating brick definitions (1 file, 4 bricks)
✓ Validating brick partition (no gaps, no overlaps)

Brick validation passed.
```

### Success Case (Full Validation)
```
$ jigy validate
✓ Validating intent
  ✓ Specifications (3 files)
  ✓ Outcomes (2 files)
  ✓ Implementation decorators (24 functions)
  ✓ Verification decorators (18 tests)
✓ Validating bricks
  ✓ Brick definitions (4 bricks)
  ✓ Brick partition (no gaps, no overlaps)

All validations passed.
```

### Failure Case (Intent Validation)
```
$ jigy validate intent
✓ Validating specifications (3 files)
✗ Validating outcomes (2 files)
  ERROR: jig/outcomes/O-002.md
    - Missing required field: 'specifies'

✗ Validating implementation decorators
  ERROR: src/auth/session.py:42
    - @jig.implements("S-999"): spec does not exist
  ERROR: src/cli/main.py:18
    - @jig.implements("S-001", invalid): expected string, got identifier

Intent validation failed: 2 phases failed, 3 errors total.
```

### Failure Case (Brick Validation)
```
$ jigy validate bricks
✗ Validating brick definitions (1 file, 4 bricks)
  ERROR: jig/bricks.yaml brick 'B-002'
    - Unit 'M-cli.invalid' not found in implementation graph
    - Unit 'auth.session' invalid: missing prefix (expected M-/C-/F-)

✗ Validating brick partition
  ERROR: Partition violations detected
    - Function 'F-auth.session.authenticate' in 2 bricks: B-001, B-003 (overlap)
    - Function 'F-cli.main.run' in 0 bricks (gap)
    - Class 'C-auth.tokens.TokenValidator' split across bricks B-001, B-004

Brick validation failed: 4 errors total.
```

### JSON Format (for CI/tooling)
```json
{
  "status": "failed",
  "intent": {
    "passed": false,
    "specifications": {
      "passed": true,
      "errors": []
    },
    "outcomes": {
      "passed": false,
      "errors": [
        {
          "file": "jig/outcomes/O-002.md",
          "line": null,
          "code": "MISSING_REQUIRED_FIELD",
          "field": "specifies",
          "message": "Missing required field: 'specifies'",
          "severity": "error"
        }
      ]
    },
    "decorators": {
      "passed": false,
      "errors": [
        {
          "file": "src/auth/session.py",
          "line": 42,
          "code": "INVALID_SPEC_REFERENCE",
          "decorator": "@jig.implements",
          "reference": "S-999",
          "message": "spec does not exist",
          "severity": "error"
        }
      ]
    }
  },
  "bricks": {
    "passed": false,
    "definitions": {
      "passed": false,
      "errors": [
        {
          "file": "jig/bricks.yaml",
          "brick": "B-002",
          "code": "UNIT_NOT_FOUND",
          "unit": "M-cli.invalid",
          "message": "Unit not found in implementation graph",
          "severity": "error"
        }
      ]
    },
    "partition": {
      "passed": false,
      "errors": [
        {
          "code": "PARTITION_OVERLAP",
          "function": "F-auth.session.authenticate",
          "bricks": ["B-001", "B-003"],
          "message": "Function in multiple bricks",
          "severity": "error"
        },
        {
          "code": "PARTITION_GAP",
          "function": "F-cli.main.run",
          "message": "Function in no bricks",
          "severity": "error"
        }
      ]
    }
  },
  "summary": {
    "total_errors": 5,
    "total_warnings": 0
  }
}
```

---

## Implementation Plan

### Work Unit Breakdown

**WU1: Intent Validators**
*Phase 1 validation - can run without graphs*

**1a. Specification File Validator**
- Parse YAML frontmatter from `jig/specifications/S-*.md` files
- Validate required fields: `id`, `type`
- Check ID format: `S-{number}`
- Check ID uniqueness across all specs
- Verify excluded fields NOT present: `brick`, `depends_on`, `content`
- Check filename matches ID (S-001.md → id: S-001)

**1b. Outcome File Validator** (optional artifacts)
- Parse YAML frontmatter from `jig/outcomes/O-*.md` files
- Validate required fields: `id`, `type`, `specifies`
- Check ID format: `O-{number}`
- Check ID uniqueness across all outcomes
- Verify `specifies` array references existing spec IDs
- Verify excluded fields NOT present: `brick`

**1c. Decorator Validator**
- Parse Python AST for `@jig.implements` decorators
- Validate decorator arguments are string literals
- Check referenced spec IDs exist in specifications
- Parse `@jig.verifies` decorators
- Check referenced spec/outcome IDs exist
- Report file path and line number for errors

**CLI:** `jigy validate intent`

---

**WU2: Brick Validators**
*Phase 3 validation - requires implementation graph*

**2a. Brick Definition Validator**
- Parse `jig/bricks.yaml`
- Validate structure (list of bricks with required fields)
- Check required fields: `id`, `name`, `units`
- Check ID format: `B-{number}`
- Check ID uniqueness across all bricks
- Validate unit prefix format: must start with `M-`, `C-`, or `F-`
- Check unit references exist in implementation-graph.ndjson
- Verify excluded fields NOT present: `depends_on`, `public_api`, `specs`

**2b. Brick Partition Validator**
- Load implementation-graph.ndjson
- Expand brick units (`M-auth.session` → all `F-auth.session.*`)
- Build function-to-brick mapping
- Check every function belongs to exactly one brick:
  - **Gap detection:** functions in 0 bricks
  - **Overlap detection:** functions in 2+ bricks
- Check no class split across bricks (all methods of same class in same brick)

**CLI:** `jigy validate bricks`

---

**WU3: CLI Integration**

- Add `jigy validate` command (smart: runs intent, then bricks if graphs exist)
- Add `jigy validate intent` subcommand
- Add `jigy validate bricks` subcommand
- Add granular subcommands:
  - `jigy validate intent specs`
  - `jigy validate intent outcomes`
  - `jigy validate intent decorators`
  - `jigy validate bricks definitions`
  - `jigy validate bricks partition`
- Support `--format json` for CI/tooling
- Implement exit codes (0=pass, 1=failures, 2=errors)
- Add `--skip-validation` flag to rebuild commands:
  - `jigy impl rebuild --skip-validation`

---

**WU4: Validation Reporting**

- Format human-readable error messages
- Include file paths and line numbers
- Group errors by validation phase (intent vs. bricks)
- Provide actionable suggestions
- Implement JSON output format with structured error codes
- Color-coded output (green ✓, red ✗)
- Summary line with total errors/warnings

---

## Acceptance Criteria

1. **Intent validation works:** `jigy validate intent` validates specs, outcomes, decorators WITHOUT graphs
2. **Brick validation works:** `jigy validate bricks` validates bricks.yaml AGAINST implementation graph
3. **Full validation works:** `jigy validate` runs both (skips bricks if no graph)
4. **Partition check works:** Detects gaps, overlaps, and class splitting in brick assignments
5. **Decorator check works:** Validates `@jig.implements` and `@jig.verifies` reference valid IDs
6. **Auto-validation works:** `jigy impl rebuild` validates intent first, errors if invalid
7. **Skip flag works:** `jigy impl rebuild --skip-validation` bypasses validation
8. **Exit codes:** Returns 0 on success, 1 on validation failures, 2 on errors
9. **Error messages:** Clear, actionable, include file paths and line numbers
10. **JSON output:** `--format json` produces structured, machine-readable output
11. **All A001 §10 rules:** All validation rules from contract enforced
12. **Documentation:** Usage documented in CLI help text

---

## Developer Workflow Example

```bash
# 1. Write specifications
vim jig/specifications/S-001.md
jigy validate intent specs        # ✓ check specs are well-formed

# 2. Write code with decorators
vim src/auth/session.py          # add @jig.implements("S-001")
jigy validate intent decorators   # ✓ check decorators reference valid specs

# 3. Build graphs (auto-validates intent first)
jigy intent rebuild               # validates specs/outcomes → builds intent-graph.ndjson
jigy impl rebuild                 # validates decorators → builds implementation-graph.ndjson
jigy verify rebuild               # validates test decorators → builds verification-graph.ndjson

# 4. Define bricks
vim jig/bricks.yaml              # add brick definitions
jigy validate bricks              # ✓ check bricks reference valid nodes, no gaps/overlaps

# 5. Full check before commit
jigy validate                     # ✓ check everything
```

---

## Dependencies

- **Implementation Graph:** WU2 (brick validators) requires implementation-graph.ndjson exists
- **Python AST Parser:** WU1c (decorator validator) requires AST parsing capability
- **CLI Framework:** Existing `jigy` CLI structure (Click-based)
- **YAML Parser:** PyYAML or similar for frontmatter parsing

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

## Design Decisions

### 1. Auto-Validation on Rebuild (DECIDED)
**Decision:** Graph rebuild commands auto-validate intent artifacts first.

**Rationale:**
- Prevents generating invalid graphs from malformed intent artifacts
- Fail fast with clear error messages before expensive graph generation
- Provides `--skip-validation` flag for power users who know artifacts are valid

**Implementation:**
```bash
jigy impl rebuild                     # validates @jig.implements first
jigy impl rebuild --skip-validation   # skip for speed (advanced usage)
```

### 2. Brick Validation Requires Persisted Graph (DECIDED)
**Decision:** Brick validation validates against `implementation-graph.ndjson`, not in-memory AST.

**Rationale:**
- Avoids duplicating graph generation logic
- Single source of truth (the persisted graph file)
- Clear dependency: must rebuild graph before validating bricks
- Simpler implementation

**Implementation:**
```bash
jigy impl rebuild                 # generates implementation-graph.ndjson
jigy validate bricks              # validates against persisted graph
# If no graph exists: error "implementation graph not found, run 'jigy impl rebuild' first"
```

### 3. Separate Intent and Brick Validation (DECIDED)
**Decision:** Intent and brick validation are separate commands with different requirements.

**Rationale:**
- Intent validation can run WITHOUT graphs (development workflow)
- Brick validation REQUIRES graphs (post-generation workflow)
- Clear separation of concerns (human artifacts vs. implementation alignment)
- Incremental validation during development

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
