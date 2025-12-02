# PLAN: Layer Validation and CLI Commands

- **SCOPE**: Implement A001 layer requirements: validation, visualization, and suggestion
- **Start**: 2025-12-01
- **Status**: Draft
- **Branch**: layer-validation-cli

## Known Intent (Created Before Coding)

**Specifications**:
- S-035: Brick ID format validation (kebab-case)
- S-036: Layer field presence validation
- S-037: Layer value validation (non-negative integers)
- S-038: Layer constraint validation (dependency hierarchy)
- S-039: Circular dependency detection (all layers)
- S-040: CLI command `jigy layers` visualization
- S-041: CLI command `jigy layers suggest`

**Bricks Affected**:
- B-validation: Artifact Validation (existing)
- B-cli: CLI Interface (existing)

## Work Unit Checklist
- [x] WU0: Create Intent nodes (Specifications S-035 through S-041)
- [x] WU1: Brick ID format validation — tests ☑ / code ☑ / docs ☐
- [ ] WU2: Layer field validation (presence & value) — tests ☐ / code ☐ / docs ☐
- [ ] WU3: Layer constraint validation — tests ☐ / code ☐ / docs ☐
- [ ] WU4: Circular dependency detection — tests ☐ / code ☐ / docs ☐
- [ ] WU5: CLI `jigy layers` command — tests ☐ / code ☐ / docs ☐
- [ ] WU6: CLI `jigy layers suggest` command — tests ☐ / code ☐ / docs ☐
- [ ] WU7: Integration testing & documentation — tests ☐ / code ☐ / docs ☐

## Work Units

### Work Unit 0: Create Known Intent

**Goal**: Capture all specifications for layer validation and CLI commands before writing any code.

**Acceptance Criteria**:
- [x] All requirements from A001 § 10 (validation rules 2, 10-13) → Specification files
- [x] All requirements from AG029 § 6 (CLI commands) → Specification files
- [x] All files have proper YAML frontmatter
- [x] `jigy validate` passes

**Created Nodes**:
- S-035: Brick ID format validation (jig/specifications/S-035.md)
- S-036: Layer field presence validation (jig/specifications/S-036.md)
- S-037: Layer value validation (jig/specifications/S-037.md)
- S-038: Layer constraint validation (jig/specifications/S-038.md)
- S-039: Circular dependency detection (jig/specifications/S-039.md)
- S-040: CLI `jigy layers` visualization (jig/specifications/S-040.md)
- S-041: CLI `jigy layers suggest` (jig/specifications/S-041.md)

**Reflect**:
- What was clear from SCOPE: A001 and AG029 provide precise contracts
- What was ambiguous: Error message format, CLI output formatting details
- All 7 specifications created with consistent structure and proper references
- Specifications properly categorize validation rules (ID format, layer presence/values, constraints, cycles)
- CLI command specs (S-040, S-041) clearly separate visualization from suggestion functionality

---

### Work Unit 1: Brick ID Format Validation

**Goal**: Validate that all brick IDs match pattern `B-[a-z0-9-]+` (kebab-case)

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [x] S-035 is implemented by validation function(s)
- [x] S-035 is verified by comprehensive tests
- [x] Tests cover valid and invalid brick ID patterns
- [x] Error messages clearly indicate the problem
- [x] `jigy validate bricks` reports ID format violations

**Implementation Notes**:
- Approach:
  1. Add `validate_brick_id_format()` function in `jig/validation/bricks.py`
  2. Use regex pattern `^B-[a-z0-9-]+$` to validate IDs
  3. Integrate into existing `validate_bricks()` workflow
  4. Return violations list with clear error messages
- Files: `src/jig/validation/bricks.py`
- Decorators added: `@jig.implements("S-035")`

**Test Plan**:
- Unit tests:
  - Valid IDs: `B-auth`, `B-core-utils`, `B-rest-api`, `B-cli-interface`
  - Invalid IDs: `B-001` (old format), `B-Auth` (uppercase), `B-core_utils` (underscore), `B-` (empty)
  - Edge cases: `B-a`, `B-123`, `B-with-many-hyphens`
- Test file: `tests/validation/test_bricks.py`
- Decorators added: `@jig.verifies("S-035")`

**Docs Updated**:
- Update validation documentation to mention ID format checking

**Human Verification**:
- Run `jigy validate bricks` on current codebase (should fail with B-001 style IDs)
- Create test bricks.yaml with invalid IDs and verify error reporting

**Reflect** (≤5 bullets):
- Regex pattern `^B-[a-z0-9-]*[a-z][a-z0-9-]*$` ensures at least one letter for semantic naming
- Updated existing tests to use kebab-case (B-auth, B-cli, etc.) instead of B-001 format
- Error message provides clear examples (B-auth, B-core-utils) to guide users
- Validation correctly detects all 5 old-format bricks in JIG codebase (B-001 through B-005)
- Test suite comprehensive: 7 new S-035 tests + updated 13 existing tests = 20 tests passing

**Links**:
- Commit: 8e76f2e
- PR: (TBD)

---

### Work Unit 2: Layer Field Validation (Presence & Value)

**Goal**: Validate that all bricks have `layer` field with non-negative integer values

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [ ] S-036 is implemented (layer field presence check)
- [ ] S-037 is implemented (layer value validation)
- [ ] S-036 and S-037 are verified by tests
- [ ] Tests cover missing layer, invalid types, negative values
- [ ] `jigy validate bricks` reports layer field violations

**Implementation Notes**:
- Approach:
  1. Add `validate_layer_field_presence()` function
  2. Add `validate_layer_values()` function
  3. Check type (must be int) and range (must be >= 0)
  4. Integrate into `validate_bricks()` workflow
- Files: `src/jig/validation/bricks.py`
- Decorators added: `@jig.implements("S-036")`, `@jig.implements("S-037")`

**Test Plan**:
- Unit tests:
  - Valid layers: 0, 1, 2, 10, 100
  - Missing layer field
  - Invalid types: "0", 1.5, null, []
  - Invalid values: -1, -10
- Test file: `tests/validation/test_bricks.py`
- Decorators added: `@jig.verifies("S-036")`, `@jig.verifies("S-037")`

**Docs Updated**:
- Update validation documentation with layer field requirements

**Human Verification**:
- Create bricks.yaml without layer fields, verify error
- Create bricks.yaml with invalid layer values, verify error messages

**Reflect** (≤5 bullets):
- (To be filled during execution)

**Links**:
- Commit: (TBD)
- PR: (TBD)

---

### Work Unit 3: Layer Constraint Validation

**Goal**: Validate that brick dependencies respect layer hierarchy

**Planned Effort**: 90 minutes

**Acceptance Criteria**:
- [ ] S-038 is implemented (layer constraint checking)
- [ ] S-038 is verified by comprehensive tests
- [ ] Tests cover valid and invalid layer dependencies
- [ ] Error messages show which brick violates constraints and how
- [ ] `jigy validate bricks` reports layer violations with function-level detail

**Implementation Notes**:
- Approach:
  1. Derive brick dependencies from implementation graph (existing logic)
  2. For each brick, check that all dependency bricks have lower layers
  3. Exception: Layer 0 bricks may depend on other layer 0 bricks
  4. Report violations with brick IDs, layers, and offending function calls
- Files: `src/jig/validation/bricks.py`
- Decorators added: `@jig.implements("S-038")`
- Requires: Implementation graph to be generated

**Test Plan**:
- Unit tests:
  - Valid: layer 1 → layer 0, layer 2 → layer 1, layer 2 → layer 0
  - Valid: layer 0 → layer 0 (no cycle)
  - Invalid: layer 1 → layer 2 (upward dependency)
  - Invalid: layer 1 → layer 1 (same layer, not layer 0)
  - Mock implementation graph with known call relationships
- Test file: `tests/validation/test_bricks_layers.py`
- Decorators added: `@jig.verifies("S-038")`

**Docs Updated**:
- Add examples of layer constraint violations
- Document error message format

**Human Verification**:
- Create test bricks.yaml with layer violations
- Run `jigy validate bricks` and verify error messages show function calls

**Reflect** (≤5 bullets):
- (To be filled during execution)

**Links**:
- Commit: (TBD)
- PR: (TBD)

---

### Work Unit 4: Circular Dependency Detection

**Goal**: Detect and report circular dependencies in brick dependency graph at all layers

**Planned Effort**: 90 minutes

**Acceptance Criteria**:
- [ ] S-039 is implemented (cycle detection)
- [ ] S-039 is verified by comprehensive tests
- [ ] Tests cover cycles at layer 0 and across layers
- [ ] Error messages show the cycle path (B-a → B-b → B-c → B-a)
- [ ] `jigy validate bricks` reports cycles with clear descriptions

**Implementation Notes**:
- Approach:
  1. Build directed graph from brick dependencies
  2. Use depth-first search (DFS) or Tarjan's algorithm to detect cycles
  3. When cycle found, extract the cycle path for error reporting
  4. Report all cycles found (not just first one)
- Files: `src/jig/validation/bricks.py`
- Decorators added: `@jig.implements("S-039")`
- Algorithm: DFS with visited/recursion stack or use networkx if available

**Test Plan**:
- Unit tests:
  - No cycles (DAG)
  - Simple cycle: B-a → B-b → B-a
  - Complex cycle: B-a → B-b → B-c → B-a
  - Multiple cycles in graph
  - Self-loop: B-a → B-a
  - Layer 0 cycle (should be caught)
- Test file: `tests/validation/test_bricks_cycles.py`
- Decorators added: `@jig.verifies("S-039")`

**Docs Updated**:
- Add cycle detection to validation documentation
- Provide example of cycle error message

**Human Verification**:
- Create bricks.yaml with circular dependencies
- Verify cycle path is clearly reported

**Reflect** (≤5 bullets):
- (To be filled during execution)

**Links**:
- Commit: (TBD)
- PR: (TBD)

---

### Work Unit 5: CLI `jigy layers` Command

**Goal**: Implement visualization command showing brick layer structure

**Planned Effort**: 90 minutes

**Acceptance Criteria**:
- [ ] S-040 is implemented (layers visualization)
- [ ] S-040 is verified by tests
- [ ] Command shows bricks grouped by layer
- [ ] Shows dependencies within each layer section
- [ ] Supports --summary, --verbose options
- [ ] Output is readable and well-formatted

**Implementation Notes**:
- Approach:
  1. Add `jigy layers` command in `src/jig/cli/main.py`
  2. Load bricks.yaml and implementation graph
  3. Group bricks by layer (0, 1, 2, ...)
  4. For each layer, show brick list with dependencies
  5. Use rich/click for formatted output
  6. Options: --summary (counts only), --verbose (show all details)
- Files: `src/jig/cli/main.py`, `src/jig/cli/layers.py` (new)
- Decorators added: `@jig.implements("S-040")`

**Test Plan**:
- Unit tests:
  - Parse and group bricks by layer
  - Format output correctly
  - Handle empty layers
  - Handle flat architecture (all layer 0)
- Integration tests:
  - Run command on real JIG codebase
  - Verify output format
- Test file: `tests/cli/test_layers.py`
- Decorators added: `@jig.verifies("S-040")`

**Docs Updated**:
- Add `jigy layers` to CLI documentation
- Add examples of command output
- Update README with layers command

**Human Verification**:
- Run `jigy layers` on current JIG codebase
- Run `jigy layers --summary` to see counts
- Verify output is readable and accurate

**Reflect** (≤5 bullets):
- (To be filled during execution)

**Links**:
- Commit: (TBD)
- PR: (TBD)

---

### Work Unit 6: CLI `jigy layers suggest` Command

**Goal**: Implement layer suggestion based on dependency analysis

**Planned Effort**: 90 minutes

**Acceptance Criteria**:
- [ ] S-041 is implemented (layer suggestion)
- [ ] S-041 is verified by tests
- [ ] Command analyzes brick dependencies and suggests layers
- [ ] Uses topological sort to assign layers
- [ ] Shows current vs suggested layers
- [ ] Supports --apply flag to update bricks.yaml

**Implementation Notes**:
- Approach:
  1. Add `jigy layers suggest` subcommand
  2. Load bricks.yaml and implementation graph
  3. Derive brick dependencies
  4. Perform topological sort of dependency graph
  5. Assign layers: layer = max(dependency layers) + 1
  6. Compare current vs suggested, show differences
  7. With --apply, update bricks.yaml in place
- Files: `src/jig/cli/layers.py`
- Decorators added: `@jig.implements("S-041")`
- Algorithm: Kahn's algorithm or DFS-based topological sort

**Test Plan**:
- Unit tests:
  - Topological sort on simple graphs
  - Layer assignment logic
  - Bricks with no dependencies → layer 0
  - Bricks with dependencies → correct layer calculation
  - Handle cycles (should report error)
- Integration tests:
  - Run on test bricks.yaml
  - Verify suggestions are correct
  - Test --apply functionality
- Test file: `tests/cli/test_layers_suggest.py`
- Decorators added: `@jig.verifies("S-041")`

**Docs Updated**:
- Add `jigy layers suggest` to CLI documentation
- Document --apply flag usage
- Add examples of suggestion workflow

**Human Verification**:
- Run `jigy layers suggest` on current codebase
- Verify suggestions match expected layer structure
- Test `jigy layers suggest --apply` on copy of bricks.yaml

**Reflect** (≤5 bullets):
- (To be filled during execution)

**Links**:
- Commit: (TBD)
- PR: (TBD)

---

### Work Unit 7: Integration Testing & Documentation

**Goal**: End-to-end testing and complete documentation updates

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [ ] All validation rules work together correctly
- [ ] CLI commands integrate with validation
- [ ] Full workflow documented (validation → layers → suggest → apply)
- [ ] Updated A001 references in code comments
- [ ] Migration guide for existing projects
- [ ] All tests passing

**Implementation Notes**:
- Approach:
  1. Create integration test scenarios
  2. Test full workflow: validate → fix issues → layers → suggest
  3. Update all relevant documentation
  4. Add examples to user guide
  5. Update CHANGELOG
- Files: Various documentation files
- Decorators added: None (integration/docs only)

**Test Plan**:
- Integration tests:
  - Start with invalid bricks.yaml (old format, no layers)
  - Run validation, see all errors
  - Fix brick IDs, add layers
  - Run validation, pass
  - Run `jigy layers` to see structure
  - Modify code to create layer violation
  - Run validation, see layer error
  - Run `jigy layers suggest` to get fix recommendation
- Test file: `tests/integration/test_layer_workflow.py`
- Decorators added: Integration tests (no specific S- node)

**Docs Updated**:
- Update validation.md with layer examples
- Update CLI reference with layers commands
- Add migration guide for old brick IDs + adding layers
- Update A001 compliance notes
- Add troubleshooting section for layer errors

**Human Verification**:
- Follow migration guide on a copy of JIG codebase
- Verify all commands work as documented
- Check that error messages are clear and actionable

**Reflect** (≤5 bullets):
- (To be filled during execution)

**Links**:
- Commit: (TBD)
- PR: (TBD)

---

## Completion Summary

(To be filled when all work units are complete)

**Scope Delivered**:
- (TBD)

**Metrics**:
- Work Units: 7
- Specifications Created: 7 (S-035 through S-041)
- Specifications Implemented: (TBD)
- Alignment: (TBD)

**Key Decisions**:
- (TBD)

**Deltas from Original Scope**:
- (TBD)

**Reflection Roll-Up**:
- **Repeatable wins**: (TBD)
- **Systemic frictions**: (TBD)
- **Open questions**: (TBD)

**Final Validation**:
- [ ] All work unit checklists complete
- [ ] `jigy validate` passes on JIG codebase
- [ ] `jigy status` shows expected alignment (S-035 through S-041)
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Migration guide tested

---

## Notes

### Current State

**Existing validation code**: `src/jig/validation/bricks.py`
- Already validates: partition, class splitting, unit references
- Missing: ID format, layer fields, layer constraints, cycles

**Existing CLI**: `src/jig/cli/main.py`, `src/jig/cli/validate.py`
- Commands: `jigy validate`, `jigy impl`, `jigy intent`
- Missing: `jigy layers` command group

**Existing bricks.yaml**: Uses B-001 format, no layer fields
- Will need migration after validation is implemented
- Current bricks: B-001 through B-005

### Dependencies

**Required for validation**:
- Implementation graph must be generated (`jigy impl rebuild`)
- Bricks.yaml must be parseable

**Required for layers command**:
- Valid bricks.yaml (passes new validation)
- Implementation graph with call relationships

### Testing Strategy

**Unit tests**: Fast, isolated, mock dependencies
- Validation logic
- Layer assignment algorithm
- CLI argument parsing

**Integration tests**: Real files, full workflow
- End-to-end validation
- CLI commands on real codebase
- Migration scenarios

### Migration Path

1. Implement validation (WU1-4)
2. Run validation on current codebase (will fail)
3. Update bricks.yaml:
   - Change B-001 → B-decorators
   - Change B-002 → B-cli
   - Change B-003 → B-validation
   - Change B-004 → B-impl-graph
   - Change B-005 → B-analyzers
   - Add layer fields (suggest via WU6)
4. Validation passes
5. Use `jigy layers` to visualize structure

### Open Questions

1. Should `jigy layers suggest --apply` require confirmation? (Propose: yes, with --force to skip)
2. Should validation be ERROR or WARNING for missing layers during transition period? (Propose: ERROR, but provide clear migration guide)
3. Export format for --export-dot? (Propose: standard GraphViz DOT format)
4. Should `jigy validate bricks` automatically suggest fixes? (Propose: yes, mention `jigy layers suggest`)
