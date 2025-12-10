# PLAN: CLI Command Restructure

- **SCOPE**: B012 (CLI Simplification Proposal)
- **Contract**: A002 (CLI Command Architecture)
- **Start**: 2025-12-09
- **Status**: Draft
- **Branch**: TBD

---

## Known Intent (Created Before Coding)

### Outcomes

- **O-019**: Intuitive CLI Experience — Users interact with JIG through a memorable, verb-first command structure requiring zero configuration

### Specifications

- **S-057**: Project Root Auto-Discovery — CLI automatically finds project root by walking up directories
- **S-058**: Verb-First Rebuild Commands — Graph rebuilds invoked as `jigy rebuild {target}`
- **S-059**: Align Command — Single command runs full workflow (rebuild + validate + summary)
- **S-060**: Show Command Structure — Structural information displayed via `jigy show {target}`
- **S-061**: Minimal Global Options — CLI accepts only `--help` and `--version` globally

### Bricks Affected

- **B-cli**: CLI Interface (layer 1) — Primary changes
- **B-validation**: May need signature updates for removed options

---

## Work Unit Checklist

- [x] WU0: Create Intent nodes (O/S) — specs ☑
- [ ] WU1: Project Root Discovery — tests ☐ / code ☐
- [ ] WU2: Restructure Rebuild Commands — tests ☐ / code ☐
- [ ] WU3: Create Align Command — tests ☐ / code ☐
- [ ] WU4: Restructure Show Commands — tests ☐ / code ☐
- [ ] WU5: Simplify Validate Commands — tests ☐ / code ☐
- [ ] WU6: Update Help & Root Command — tests ☐ / code ☐
- [ ] WU7: Clean Break - Remove Old Commands — tests ☐ / code ☐

---

## Work Units

### Work Unit 0: Create Known Intent

**Goal**: Capture all Outcomes and Specifications before writing any code.

**Acceptance Criteria**:
- [x] O-019 created in `jig/outcomes/O-019.md`
- [x] S-057 through S-061 created in `jig/specifications/`
- [x] All files have proper YAML frontmatter
- [x] `jigy validate` passes

**Created Nodes**:
- O-019: Intuitive CLI Experience
- S-057: Project Root Auto-Discovery
- S-058: Verb-First Rebuild Commands
- S-059: Align Command
- S-060: Show Command Structure
- S-061: Minimal Global Options

**Reflect**:
- (To be filled during execution)

---

### Work Unit 1: Project Root Discovery

**Goal**: Implement auto-discovery of project root (S-057)

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [ ] S-057 implemented by `find_project_root()` function
- [ ] S-057 verified by tests
- [ ] Walks up from current directory looking for `jig/`
- [ ] Returns project root path (parent of `jig/`)
- [ ] Raises clear error if not found

**Implementation Notes**:
- New file: `src/jig/cli/discovery.py`
- Function: `find_project_root(start_dir: Path = None) -> Path`
- Error message: "Not in a JIG project. No jig/ directory found."
- Decorator: `@jig.implements("S-057")`

**Test Plan**:
- Test file: `tests/cli/test_discovery.py`
- Cases: found in current dir, found in parent, found in grandparent, not found
- Decorator: `@jig.verifies("S-057")`

**Human Verification**:
```bash
cd /some/jig/project/src/deep/path
python -c "from jig.cli.discovery import find_project_root; print(find_project_root())"
# Should print: /some/jig/project
```

**Reflect**:
- (To be filled during execution)

---

### Work Unit 2: Restructure Rebuild Commands

**Goal**: Move rebuild from `jigy {noun} rebuild` to `jigy rebuild {noun}` (S-058)

**Planned Effort**: 90 minutes

**Acceptance Criteria**:
- [ ] S-058 implemented by new `rebuild` command group
- [ ] S-058 verified by tests
- [ ] `jigy rebuild` rebuilds all three graphs
- [ ] `jigy rebuild impl` rebuilds implementation graph
- [ ] `jigy rebuild intent` rebuilds intent graph
- [ ] `jigy rebuild verify` rebuilds verification graph
- [ ] No options on any rebuild command (uses discovery + defaults)

**Implementation Notes**:
- Modify: `src/jig/cli/main.py`
- Create `rebuild` group with `invoke_without_command=True`
- Add `impl`, `intent`, `verify` subcommands
- Use `find_project_root()` internally
- Canonical output paths per A001
- Decorator: `@jig.implements("S-058")` on each subcommand

**Test Plan**:
- Test file: `tests/cli/test_rebuild.py` (new)
- Cases: rebuild all, rebuild impl, rebuild intent, rebuild verify
- Verify exit codes and output file creation
- Decorator: `@jig.verifies("S-058")`

**Human Verification**:
```bash
jigy rebuild impl
# Should create jig/generated/implementation-graph.ndjson

jigy rebuild
# Should create all three graph files
```

**Reflect**:
- (To be filled during execution)

---

### Work Unit 3: Create Align Command

**Goal**: Implement `jigy align` as the "do everything" command (S-059)

**Planned Effort**: 90 minutes

**Acceptance Criteria**:
- [ ] S-059 implemented by `align` command
- [ ] S-059 verified by tests
- [ ] Rebuilds all graphs (impl → verify → intent)
- [ ] Validates all artifacts
- [ ] Displays summary per A002 format
- [ ] Exit 0 if aligned, non-zero on failure

**Implementation Notes**:
- Modify: `src/jig/cli/main.py`
- Reuse logic from current `rebuild` command
- Improved output format per A002:
  ```
  Rebuilding graphs...
    intent: 45 specs, 5 outcomes
    impl: 312 functions
    verify: 89 tests

  Validating...
    intent: OK
    bricks: OK (12 bricks, 3 layers)

  Summary:
    Specs: 45 total (42 implemented, 38 verified)
    Status: ALIGNED
  ```
- Decorator: `@jig.implements("S-059")`

**Test Plan**:
- Test file: `tests/cli/test_align.py` (new)
- Cases: successful align, validation failure stops, rebuild failure stops
- Verify output format matches A002
- Decorator: `@jig.verifies("S-059")`

**Human Verification**:
```bash
jigy align
# Should show rebuild progress, validation, and summary
```

**Reflect**:
- (To be filled during execution)

---

### Work Unit 4: Restructure Show Commands

**Goal**: Create `jigy show` group replacing `jigy layers` (S-060)

**Planned Effort**: 90 minutes

**Acceptance Criteria**:
- [ ] S-060 implemented by `show` command group
- [ ] S-060 verified by tests
- [ ] `jigy show` displays bricks + layers overview
- [ ] `jigy show layers` displays layer hierarchy
- [ ] `jigy show bricks` displays brick details
- [ ] No options (uses discovery)

**Implementation Notes**:
- Modify: `src/jig/cli/main.py`
- Create `show` group with `invoke_without_command=True`
- Default shows overview (bricks list + layer tree)
- Refactor existing `layers_command()` for `show layers`
- New function for `show bricks`
- Decorator: `@jig.implements("S-060")` on each subcommand

**Test Plan**:
- Test file: `tests/cli/test_show.py` (new)
- Cases: show default, show layers, show bricks
- Verify output format
- Decorator: `@jig.verifies("S-060")`

**Human Verification**:
```bash
jigy show
# Should display bricks overview and layer structure

jigy show layers
# Should display layer hierarchy only

jigy show bricks
# Should display brick details
```

**Reflect**:
- (To be filled during execution)

---

### Work Unit 5: Simplify Validate Commands

**Goal**: Remove `--format` and `--project-root` options from validate (S-061 partial)

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [ ] S-061 partially implemented for validate commands
- [ ] S-061 verified by tests
- [ ] `jigy validate` works without options
- [ ] `jigy validate intent` works without options
- [ ] `jigy validate bricks` works without options
- [ ] `jigy validate full` works without options
- [ ] Human-readable output only

**Implementation Notes**:
- Modify: `src/jig/cli/main.py`
- Modify: `src/jig/cli/validate.py`
- Remove `--project-root` and `--format` options
- Update function signatures to not require format
- Use `find_project_root()` internally
- Update decorators to include S-061

**Test Plan**:
- Update: `tests/cli/test_validate.py`
- Remove tests for `--format json`
- Remove tests for `--project-root`
- Verify human output
- Decorator: `@jig.verifies("S-061")`

**Human Verification**:
```bash
jigy validate
# Should work with no options

jigy validate --format json
# Should error: unrecognized option
```

**Reflect**:
- (To be filled during execution)

---

### Work Unit 6: Update Help & Root Command

**Goal**: Make `jigy` show help, complete S-061 (S-061 complete)

**Planned Effort**: 45 minutes

**Acceptance Criteria**:
- [ ] S-061 fully implemented
- [ ] S-061 verified by tests
- [ ] `jigy` (bare) shows help and exits 0
- [ ] `jigy --version` shows version
- [ ] `jigy --help` shows help
- [ ] No other global options exist
- [ ] Help text is concise and matches A002

**Implementation Notes**:
- Modify: `src/jig/cli/main.py`
- Update root group to `invoke_without_command=True`
- Show help when no subcommand
- Update docstrings for concise descriptions
- Decorator: `@jig.implements("S-061")` on cli group

**Test Plan**:
- Update: `tests/cli/test_cli.py`
- Cases: bare command shows help, --version works, --help works
- Verify no unexpected options in help output
- Decorator: `@jig.verifies("S-061")`

**Human Verification**:
```bash
jigy
# Should show help (not error)

jigy --version
# Should show version

jigy --unknown-flag
# Should error: unrecognized option
```

**Reflect**:
- (To be filled during execution)

---

### Work Unit 7: Clean Break - Remove Old Commands

**Goal**: Delete old command structure completely (per taskCleanBreak)

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [ ] `impl` group removed entirely
- [ ] `intent` group removed entirely
- [ ] `verify` group removed entirely
- [ ] `layers` group removed entirely
- [ ] `layers suggest` command removed
- [ ] All removed options deleted (no commented code)
- [ ] Old tests deleted and replaced
- [ ] `jigy impl rebuild` fails with "unknown command"
- [ ] `jigy layers` fails with "unknown command"

**Implementation Notes**:
- Delete old groups from `src/jig/cli/main.py`
- Delete `suggest_layers_command` from `src/jig/cli/layers.py`
- May rename `layers.py` → `show.py` for clarity
- No backwards compatibility code
- No deprecation warnings (clean break)
- Fail loudly if old commands attempted

**Test Plan**:
- Delete: `tests/cli/test_layers_suggest.py`
- Delete tests for old command invocations
- Add tests verifying old commands fail clearly
- No `@jig` decorators (testing removal, not behavior)

**Human Verification**:
```bash
jigy impl rebuild
# Should error: "Error: No such command 'impl'"

jigy layers
# Should error: "Error: No such command 'layers'"

jigy layers suggest
# Should error: "Error: No such command 'layers'"
```

**Reflect**:
- (To be filled during execution)

---

## Current → Target State Summary

### Commands

| Current | Target | Status |
|---------|--------|--------|
| `jigy rebuild` | `jigy align` | Rename |
| `jigy impl rebuild` | `jigy rebuild impl` | Restructure |
| `jigy intent rebuild` | `jigy rebuild intent` | Restructure |
| `jigy verify rebuild` | `jigy rebuild verify` | Restructure |
| — | `jigy rebuild` (all) | New |
| `jigy validate` | `jigy validate` | Unchanged |
| `jigy validate intent` | `jigy validate intent` | Unchanged |
| `jigy validate bricks` | `jigy validate bricks` | Unchanged |
| `jigy validate full` | `jigy validate full` | Unchanged |
| `jigy layers` | `jigy show layers` | Restructure |
| `jigy layers suggest` | — | **Removed** |
| — | `jigy show` | New |
| — | `jigy show bricks` | New |

### Options Removed

| Option | Was On | Removed In |
|--------|--------|------------|
| `--project-root` | All | WU1-6 |
| `--source-dir` | impl rebuild | WU2 |
| `--test-dir` | verify rebuild | WU2 |
| `--output` | rebuild | WU2 |
| `--exclude` | impl rebuild | WU2 |
| `--format` | validate | WU5 |
| `--verbose` | various | WU2-4 |
| `--strict/--lenient` | impl rebuild | WU2 |
| `--skip-validation` | impl rebuild | WU2 |
| `--no-timestamp` | rebuild | WU2 |
| `--summary` | layers | WU4 |
| `--apply` | layers suggest | WU7 |

---

## Validation Checklist

After implementation, verify:

**Commands work:**
- [ ] `jigy` shows help (exit 0)
- [ ] `jigy --version` shows version
- [ ] `jigy align` runs full workflow
- [ ] `jigy rebuild` rebuilds all graphs
- [ ] `jigy rebuild impl` rebuilds impl graph only
- [ ] `jigy rebuild intent` rebuilds intent graph only
- [ ] `jigy rebuild verify` rebuilds verify graph only
- [ ] `jigy validate` validates all
- [ ] `jigy validate intent` validates intent only
- [ ] `jigy validate bricks` validates bricks only
- [ ] `jigy validate full` validates all (explicit)
- [ ] `jigy show` shows bricks + layers overview
- [ ] `jigy show layers` shows layer hierarchy
- [ ] `jigy show bricks` shows brick details

**Old commands fail:**
- [ ] `jigy impl rebuild` fails clearly
- [ ] `jigy intent rebuild` fails clearly
- [ ] `jigy verify rebuild` fails clearly
- [ ] `jigy layers` fails clearly
- [ ] `jigy layers suggest` fails clearly

**Options removed:**
- [ ] No `--project-root` on any command
- [ ] No `--format` on any command
- [ ] No `--verbose` on any command
- [ ] No `--strict/--lenient` on any command

**JIG alignment:**
- [ ] `jigy validate` passes
- [ ] All new code has `@jig.implements` decorators
- [ ] All new tests have `@jig.verifies` decorators
- [ ] S-057 through S-061 are implemented and verified

---

## Completion Summary

_(To be filled after all work units complete)_

**Scope Delivered**:
-

**Metrics**:
- Work Units: 8 (including WU0)
- Specifications Created: 5 (S-057 through S-061)
- Outcomes Created: 1 (O-019)

**Key Decisions**:
-

**Deltas from Original Scope**:
-

**Final Validation**:
- [ ] All work unit checklists complete
- [ ] `jigy validate` passes
- [ ] All tests passing
- [ ] Documentation updated
