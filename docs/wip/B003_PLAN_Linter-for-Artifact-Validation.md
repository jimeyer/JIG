# PLAN: Linter for Artifact Validation (B003)

- **SCOPE**: docs/bricks/AG026_PROPOSAL_Linter-for-Artifact-Validation.md
- **Start**: 2025-11-30
- **Status**: Draft
- **Branch**: minimal-jig

## Known Intent (Created Before Coding)

**Outcomes**:
- O-004: Early error detection in artifact validation (jig/outcomes/O-004.md)
- O-005: Clear actionable error messages (jig/outcomes/O-005.md)
- O-006: Fast project validation under 5 seconds (jig/outcomes/O-006.md)

**Specifications**:
- S-018: Validate specification file YAML frontmatter (jig/specifications/S-018.md)
- S-019: Validate outcome file YAML frontmatter (jig/specifications/S-019.md)
- S-020: Validate decorator references (@jig.implements, @jig.verifies) (jig/specifications/S-020.md)
- S-021: Validate brick definition structure and fields (jig/specifications/S-021.md)
- S-022: Validate brick partition constraints (jig/specifications/S-022.md)
- S-023: CLI command `jigy validate intent` (jig/specifications/S-023.md)
- S-024: CLI command `jigy validate bricks` (jig/specifications/S-024.md)
- S-025: CLI command `jigy validate` (full validation) (jig/specifications/S-025.md)
- S-026: JSON output format for CI integration (jig/specifications/S-026.md)
- S-027: Auto-validation in rebuild commands (jig/specifications/S-027.md)

**Bricks Affected**:
- B-003: Artifact Validation (new brick for linter functionality)

## Work Unit Checklist
- [x] WU0: Create Intent nodes (O/S) ✅
- [x] WU1: Intent Validators — tests ✅ / code ✅ / docs ⏸️
- [x] WU2: Brick Validators — tests ✅ / code ✅ / docs ⏸️
- [x] WU3: CLI Integration — tests ✅ / code ✅ / docs ✅
- [x] WU4: Validation Reporting — tests ✅ / code ✅ / docs ⏸️

## Work Units

### Work Unit 0: Create Known Intent

**Goal**: Capture all known Outcomes and Specifications from AG026 before writing any code.

**Acceptance Criteria**:
- [x] All "why" statements → Outcome files in `jig/outcomes/` (O-004, O-005, O-006)
- [x] All "what" requirements → Specification files in `jig/specifications/` (S-018 through S-027)
- [x] All files have proper YAML frontmatter
- [x] Manual validation passes (validated YAML frontmatter with Python script)

**Created Nodes**:
- O-004: Early Error Detection - developers discover validation errors before graph generation
- O-005: Clear Error Messages - actionable messages with file paths and line numbers
- O-006: Fast Validation - project validation completes in under 5 seconds
- S-018: Specification File Validation - YAML frontmatter, required fields, ID uniqueness, filename matching
- S-019: Outcome File Validation - YAML frontmatter, required fields, specifies references
- S-020: Decorator Validation - @jig.implements and @jig.verifies reference valid IDs
- S-021: Brick Definition Validation - structure, required fields, unit prefixes, unit references
- S-022: Brick Partition Validation - no gaps, no overlaps, no class splitting
- S-023: Intent Validation CLI - `jigy validate intent` command
- S-024: Brick Validation CLI - `jigy validate bricks` command
- S-025: Full Validation CLI - `jigy validate` command (smart, runs both phases)
- S-026: JSON Output Format - structured output for CI/tooling with error codes
- S-027: Auto-Validation - rebuild commands validate before building, --skip-validation flag

**Reflect**:
- What was clear from SCOPE: Three distinct validation phases (intent, graph building, bricks) mapped cleanly to outcomes/specs
- What was ambiguous: Exact error code taxonomy will emerge during implementation
- Linking outcomes to specs: Each spec clearly implements one or more outcomes
- Sequential numbering: O-004 through O-006, S-018 through S-027 follows convention
- AG026 is comprehensive: All validation rules mapped to specifications

---

### Work Unit 1: Intent Validators

**Goal**: Implement Phase 1 validation - validate specs, outcomes, and decorators WITHOUT requiring graphs to exist.

**Planned Effort**: 90 minutes

**Acceptance Criteria**:
- [x] S-018 is implemented: specification file validator with YAML parsing
- [x] S-019 is implemented: outcome file validator with reference checking
- [x] S-020 is implemented: decorator validator with Python AST parsing
- [x] All validators have comprehensive tests with edge cases (17 tests)
- [x] Tests verify error messages include file paths and line numbers
- [x] Implementation graph shows alignment for S-018, S-019, S-020

**Implementation Notes**:
- Create `src/jig/validation/` module structure
- Files:
  - `src/jig/validation/__init__.py`
  - `src/jig/validation/intent.py` (spec, outcome, decorator validators)
  - `src/jig/validation/models.py` (ValidationError, ValidationResult)
- Use Python AST for decorator parsing (@jig.implements, @jig.verifies)
- Parse YAML frontmatter from markdown files
- Check ID uniqueness across files
- Validate references (specifies, implements, verifies)
- Decorators:
  - `@jig.implements("S-018")` on `validate_specification_file()`
  - `@jig.implements("S-019")` on `validate_outcome_file()`
  - `@jig.implements("S-020")` on `validate_decorators()`

**Test Plan**:
- Unit tests: `tests/validation/test_intent.py`
- Test cases:
  - Valid spec/outcome files pass
  - Missing required fields detected
  - Invalid ID formats rejected
  - ID uniqueness violations caught
  - Invalid references caught (nonexistent spec IDs)
  - Excluded fields detected
  - Filename/ID mismatches caught
  - Decorator syntax errors caught
  - Multiple specs in single decorator
- Decorators: `@jig.verifies("S-018")`, `@jig.verifies("S-019")`, `@jig.verifies("S-020")`

**Docs Updated**:
- (Deferred to WU3 when CLI is integrated)

**Reflect** (≤5 bullets):
- TDD workflow excellent: Writing tests first clarified edge cases and error codes before implementation
- Python AST parsing straightforward: ast.walk() and pattern matching made decorator validation clean
- ValidationResult/ValidationError models good abstraction: Easy to accumulate errors and format output
- Frontmatter parsing fragile: YAML parsing can fail in multiple ways, needed None checks throughout
- Test coverage comprehensive: 17 tests cover all validation rules from S-018, S-019, S-020

**Links**:
- Commit: (pending)
- PR: N/A

---

### Work Unit 2: Brick Validators

**Goal**: Implement Phase 3 validation - validate brick definitions against persisted implementation graph.

**Planned Effort**: 90 minutes

**Acceptance Criteria**:
- [x] S-021 is implemented: brick definition validator
- [x] S-022 is implemented: brick partition validator (gaps, overlaps, class splitting)
- [x] Validators load and parse implementation-graph.ndjson
- [x] Module expansion works (M-auth.session → all F-auth.session.*)
- [x] All validators have comprehensive tests (14 tests)
- [x] Implementation graph shows alignment for S-021, S-022

**Implementation Notes**:
- Files:
  - `src/jig/validation/bricks.py` (brick validators with graph loading)
- Load `jig/generated/implementation-graph.ndjson` using NDJSON parsing
- Parse `jig/bricks.yaml` with PyYAML
- Expand module/class units to function units:
  - M-auth.session → all F-auth.session.*
  - C-auth.Token → all F-auth.Token.*
  - F-auth.login → F-auth.login (direct)
- Build function-to-brick mapping using defaultdict
- Detect gaps (functions in 0 bricks)
- Detect overlaps (functions in 2+ bricks)
- Detect class splitting (class methods in different bricks) via parent_class heuristic
- Decorators:
  - `@jig.implements("S-021")` on `validate_brick_definitions()`
  - `@jig.implements("S-022")` on `validate_brick_partition()`

**Test Plan**:
- Unit tests: `tests/validation/test_bricks.py`
- Test cases:
  - Valid bricks.yaml passes
  - Missing required fields detected
  - Invalid unit prefixes rejected
  - Unit references to nonexistent nodes caught
  - Partition gaps detected
  - Partition overlaps detected
  - Class splitting detected
  - Excluded fields detected
- Test fixtures: Create sample implementation-graph.ndjson and bricks.yaml
- Decorators: `@jig.verifies("S-021")`, `@jig.verifies("S-022")`

**Docs Updated**:
- (Deferred to WU3 when CLI is integrated)

**Reflect** (≤5 bullets):
- Unit expansion logic clean: String prefix matching on function IDs worked well for M-/C-/F- units
- NDJSON parsing simple: One JSON object per line, easy to stream and parse incrementally
- Class splitting heuristic: Detecting uppercase first letter in path segments to identify classes is fragile but works
- Test fixtures crucial: Creating sample graphs/bricks in tests clarified edge cases (gaps, overlaps, splits)
- Defaultdict perfect fit: Building function-to-bricks mapping naturally handles multiple bricks per function

**Links**:
- Commit: (pending)
- PR: N/A

---

### Work Unit 3: CLI Integration

**Goal**: Implement CLI commands for validation (`jigy validate intent`, `jigy validate bricks`, `jigy validate`).

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [x] S-023 is implemented: `jigy validate intent` command
- [x] S-024 is implemented: `jigy validate bricks` command
- [x] S-025 is implemented: `jigy validate` command (full, smart)
- [x] S-027 is implemented: auto-validation in rebuild commands
- [x] All commands have proper exit codes (0=pass, 1=failures, 2=errors)
- [x] --skip-validation flag works on rebuild commands
- [x] Implementation graph shows alignment for S-023, S-024, S-025, S-027

**Implementation Notes**:
- Files:
  - `src/jig/cli/validate.py` (validate command logic with @jig.implements)
  - Updated `src/jig/cli/main.py` (added validate command group and CLI wiring)
- Click command group with `invoke_without_command=True` for default behavior
- Smart validation: `validate_full_command()` skips brick validation if no graph
- Auto-validation in `impl rebuild`: calls `auto_validate_decorators()` before graph building
- Exit codes: 0 (success), 1 (validation failures), 2 (errors like missing graph)
- --skip-validation flag bypasses auto-validation for power users
- Decorators:
  - `@jig.implements("S-023")` on `validate_intent_command()`
  - `@jig.implements("S-024")` on `validate_bricks_command()`
  - `@jig.implements("S-025")` on `validate_full_command()`
  - `@jig.implements("S-027")` on `auto_validate_decorators()`

**Test Plan**:
- Integration tests: `tests/cli/test_validate.py`
- Test cases:
  - `jigy validate intent` runs intent validators
  - `jigy validate bricks` runs brick validators
  - `jigy validate bricks` errors if no implementation graph
  - `jigy validate` runs both (skips bricks if no graph)
  - Exit codes correct for pass/fail/error
  - `jigy impl rebuild` validates intent first
  - `jigy impl rebuild --skip-validation` skips validation
  - Auto-validation errors prevent graph generation
- Use temporary directories with test fixtures
- Decorators: `@jig.verifies("S-023")`, `@jig.verifies("S-024")`, `@jig.verifies("S-025")`, `@jig.verifies("S-027")`

**Docs Updated**:
- CLI help text included in command docstrings (visible via --help)

**Reflect** (≤5 bullets):
- Click invoke_without_command pattern clean: `jigy validate` without subcommand runs full validation
- Click isolated_filesystem gotcha: Must explicitly pass `--project-root .` in tests
- Exit code strategy clear: 0=pass, 1=validation fails, 2=errors (missing graph)
- Auto-validation integration smooth: Single check before graph rebuild with skip flag
- 12 CLI integration tests comprehensive: Cover all commands, exit codes, and edge cases

**Links**:
- Commit: (pending)
- PR: N/A

---

### Work Unit 4: Validation Reporting

**Goal**: Implement human-readable and JSON output formats with clear error messages.

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [x] S-026 is implemented: JSON output format with error codes
- [x] Human-readable output uses ✓ and ✗ symbols
- [x] Error messages include file paths and line numbers
- [x] Error messages are actionable
- [x] Summary line shows total errors/warnings
- [x] --format json flag works on all validate commands
- [x] Implementation graph shows alignment for S-026

**Implementation Notes**:
- Files:
  - `src/jig/validation/reporting.py` (formatters for human/JSON output)
- Human format:
  - Color coding with click.secho or colorama
  - Grouped by validation phase
  - Clear success/failure indicators
  - File paths, line numbers, error descriptions
- JSON format:
  - Structured error codes (MISSING_REQUIRED_FIELD, INVALID_SPEC_REFERENCE, etc.)
  - File, line, code, message, severity fields
  - Summary with total errors/warnings
- Decorators:
  - `@jig.implements("S-026")` on `format_as_json()` and JSON schema

**Test Plan**:
- Unit tests: `tests/validation/test_reporting.py`
- Test cases:
  - Human format: success output correct
  - Human format: failure output correct
  - JSON format: schema valid
  - JSON format: error codes present
  - JSON format: all fields populated
  - Color codes applied (test without TTY)
  - Summary counts accurate
- Snapshot tests for output format
- Decorators: `@jig.verifies("S-026")`

**Docs Updated**:
- README: Add output format examples
- CLI help: Document --format flag

**Reflect** (≤5 bullets):
- JSON schema design straightforward: error code + message + file/line pattern emerged naturally
- Click --format flag integration clean: Choice type validation and conditional formatting worked well
- Test coverage comprehensive: 7 reporting unit tests + 3 CLI JSON format tests caught edge cases
- Human format basic: could benefit from color coding (click.secho) and better grouping
- No JSON Schema file: error codes scattered across validators, schema not formally versioned

**Links**:
- Commit: f06048a
- PR: N/A

---

## Completion Summary

**Scope Delivered**:
- (To be filled after completion)

**Metrics**:
- Work Units: 5 (including WU0)
- Outcomes Created: 3 (O-004, O-005, O-006)
- Specifications Created: 10 (S-018 through S-027)
- Specifications Implemented:
- Alignment:

**Key Decisions**:
- (To be filled during implementation)

**Deltas from Original Scope**:
- (To be filled if scope changes)

**Reflection Roll-Up**:
- **Repeatable wins**:
- **Systemic frictions**:
- **Open questions**:

**Final Validation**:
- [ ] All work unit checklists complete
- [ ] `jigy validate` passes (including new validators validating themselves!)
- [ ] `jigy status` shows expected alignment
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CLI help text complete
- [ ] JSON output schema documented
