# PLAN: JIG Configuration File MVP

- **SCOPE**: Implement minimal `jig.toml` configuration with path settings only
- **Start**: 2025-12-10
- **Status**: Draft
- **Branch**: config-file-mvp
- **References**: B015 (Proposal), J017 (JIG Concept v9), agents/taskPlan.md

## Known Intent (Created Before Coding)

**Outcomes**:
- O-020: Configurable Project Structure (jig/outcomes/O-020.md)

**Specifications**:
- S-062: Configuration File Discovery (jig/specifications/S-062.md)
- S-063: TOML Configuration Parsing (jig/specifications/S-063.md)
- S-064: Path Configuration with Defaults (jig/specifications/S-064.md)
- S-065: CLI Integration with Configuration (jig/specifications/S-065.md)

**Bricks Affected**:
- B-cli: CLI Interface (existing) - will use config
- B-config: Configuration (NEW) - core config loading

## Work Unit Checklist
- [x] WU0: Create Intent nodes (O/S)
- [ ] WU1: Configuration file discovery — tests ☐ / code ☐ / docs ☐
- [ ] WU2: TOML parsing and schema validation — tests ☐ / code ☐ / docs ☐
- [ ] WU3: Path configuration with defaults — tests ☐ / code ☐ / docs ☐
- [ ] WU4: CLI integration — tests ☐ / code ☐ / docs ☐
- [ ] WU5: Integration testing & documentation — tests ☐ / code ☐ / docs ☐

## Work Units

### Work Unit 0: Create Known Intent

**Goal**: Capture all known Outcomes and Specifications from B015 scope before writing any code.

**Acceptance Criteria**:
- [x] Outcome O-020 created in `jig/outcomes/`
- [x] Specifications S-062 through S-065 created in `jig/specifications/`
- [x] All files have proper YAML frontmatter
- [x] `jigy validate intent` passes

**Created Nodes**:
- O-020: Configurable Project Structure (jig/outcomes/O-020.md)
- S-062: Configuration File Discovery (jig/specifications/S-062.md)
- S-063: TOML Configuration Parsing (jig/specifications/S-063.md)
- S-064: Path Configuration with Defaults (jig/specifications/S-064.md)
- S-065: CLI Integration with Configuration (jig/specifications/S-065.md)

**Reflect** (≤5 bullets):
- Used sequential IDs (O-020, S-062-S-065) per J017 instead of domain prefixes (O-MPS-001)
- Specs must NOT have `implements` field in frontmatter - only outcomes have `specifies`
- Clear separation: O-020 describes value (WHY), S-062-S-065 describe behavior (WHAT)
- All specs are evergreen and testable per O-S Writing Guide
- Validation passed on first corrected attempt

---

### Work Unit 1: Configuration File Discovery

**Goal**: Implement configuration file discovery with fallback chain

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [ ] S-062 is implemented by discovery function(s)
- [ ] S-062 is verified by comprehensive tests
- [ ] Tests cover all discovery locations (jig.toml, .jig.toml, pyproject.toml)
- [ ] Tests cover missing config (returns None, uses defaults later)
- [ ] Clear error messages for file access errors

**Implementation Notes**:
- Approach:
  1. Create `src/jig/config/__init__.py` module
  2. Implement `find_config_file() -> Path | None`
  3. Search order: jig.toml → .jig.toml → pyproject.toml
  4. For pyproject.toml, check for [tool.jig] section existence
  5. Return None if no config found (caller uses defaults)
- Files: `src/jig/config/__init__.py`, `src/jig/config/discovery.py`
- Decorators added: `@jig.implements("S-062")`

**Test Plan**:
- Unit tests:
  - jig.toml exists → returns jig.toml path
  - Only .jig.toml exists → returns .jig.toml path
  - Only pyproject.toml with [tool.jig] → returns pyproject.toml path
  - pyproject.toml without [tool.jig] → returns None
  - No config files → returns None
  - Multiple exist → returns first in priority order
- Test file: `test/config/test_discovery.py`
- Decorators added: `@jig.verifies("S-062")`

**Docs Updated**:
- None yet (docs in WU5)

**Human Verification**:
- Create jig.toml in project root, verify discovery finds it
- Remove jig.toml, verify fallback to defaults

**Reflect** (≤5 bullets):
- (To be filled after implementation)

**Links**:
- Commit: (TBD)
- PR: (TBD)

---

### Work Unit 2: TOML Parsing and Schema Validation

**Goal**: Parse TOML configuration files with error handling

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [ ] S-063 is implemented by parsing function(s)
- [ ] S-063 is verified by comprehensive tests
- [ ] Tests cover valid TOML parsing
- [ ] Tests cover invalid TOML (syntax errors)
- [ ] Tests cover pyproject.toml [tool.jig] extraction
- [ ] Clear error messages with file location

**Implementation Notes**:
- Approach:
  1. Add `src/jig/config/parser.py`
  2. Implement `parse_config_file(path: Path) -> dict`
  3. Use `tomllib` (Python 3.11+) with `tomli` fallback for <3.11
  4. For pyproject.toml, extract [tool.jig] section
  5. For jig.toml/.jig.toml, use [jig] section (or root if no section)
  6. Return raw dict (schema validation in WU3)
- Files: `src/jig/config/parser.py`
- Decorators added: `@jig.implements("S-063")`
- Dependencies: `tomli` for Python <3.11 compatibility (optional)

**Test Plan**:
- Unit tests:
  - Valid jig.toml → returns parsed dict
  - Valid pyproject.toml with [tool.jig] → returns tool.jig section
  - Invalid TOML syntax → raises ConfigError with message
  - Empty file → returns empty dict
  - File not found → raises ConfigError
- Test file: `test/config/test_parser.py`
- Decorators added: `@jig.verifies("S-063")`

**Docs Updated**:
- None yet (docs in WU5)

**Human Verification**:
- Create valid jig.toml, verify parsing
- Create invalid TOML, verify error message is clear

**Reflect** (≤5 bullets):
- (To be filled after implementation)

**Links**:
- Commit: (TBD)
- PR: (TBD)

---

### Work Unit 3: Path Configuration with Defaults

**Goal**: Implement path configuration with sensible defaults

**Planned Effort**: 90 minutes

**Acceptance Criteria**:
- [ ] S-064 is implemented by config class/dataclass
- [ ] S-064 is verified by comprehensive tests
- [ ] Tests cover all path settings
- [ ] Tests cover default values when not specified
- [ ] Tests cover partial configuration (some paths set, others default)
- [ ] Config object provides resolved absolute paths

**Implementation Notes**:
- Approach:
  1. Add `src/jig/config/schema.py`
  2. Create `PathsConfig` dataclass with defaults
  3. Create `JigConfig` main dataclass
  4. Implement `load_config(project_root: Path) -> JigConfig`
  5. Merge parsed dict with defaults
  6. Resolve all paths to absolute (relative to project_root)
  7. Expose both raw config and resolved paths
- Files: `src/jig/config/schema.py`
- Decorators added: `@jig.implements("S-064")`

**Test Plan**:
- Unit tests:
  - No config → all defaults
  - paths.tests = "tests" → overrides default "test"
  - paths.source = "lib" → overrides default "src"
  - Partial config → defaults for unset, overrides for set
  - Resolved paths are absolute
  - jig_root relative paths resolve correctly (specifications, outcomes, etc.)
- Test file: `test/config/test_schema.py`
- Decorators added: `@jig.verifies("S-064")`

**Docs Updated**:
- None yet (docs in WU5)

**Human Verification**:
- Create minimal jig.toml with `[jig.paths]\ntests = "tests"`
- Load config, verify tests path changed, others defaulted

**Reflect** (≤5 bullets):
- (To be filled after implementation)

**Links**:
- Commit: (TBD)
- PR: (TBD)

---

### Work Unit 4: CLI Integration

**Goal**: Wire configuration into existing CLI commands

**Planned Effort**: 90 minutes

**Acceptance Criteria**:
- [ ] S-065 is implemented across CLI commands
- [ ] S-065 is verified by integration tests
- [ ] `jigy validate` uses configured paths
- [ ] `jigy impl rebuild` uses configured source path
- [ ] `jigy layers` uses configured bricks path
- [ ] Commands work without config file (defaults)
- [ ] Commands report which config file is being used (verbose mode)

**Implementation Notes**:
- Approach:
  1. Add config loading to CLI entry point
  2. Pass config to subcommands via Click context
  3. Update `validate` command to use config.paths
  4. Update `impl rebuild` to use config.paths.source
  5. Update `layers` to use config.paths.bricks
  6. Add --config flag for explicit config file override
  7. Add config info to --verbose output
- Files: `src/jig/cli/main.py`, `src/jig/cli/validate.py`, `src/jig/cli/impl.py`, `src/jig/cli/layers.py`
- Decorators added: `@jig.implements("S-065")`

**Test Plan**:
- Integration tests:
  - Run `jigy validate` with custom test directory config
  - Run `jigy impl rebuild` with custom source directory
  - Run commands without config file (verify defaults work)
  - Run with --config flag pointing to custom location
- Test file: `test/config/test_cli_integration.py`
- Decorators added: `@jig.verifies("S-065")`

**Docs Updated**:
- None yet (docs in WU5)

**Human Verification**:
- Rename `test/` to `tests/`
- Add jig.toml with `tests = "tests"`
- Run `jigy validate` - should find tests
- Remove jig.toml - should fail to find tests (or use default)

**Reflect** (≤5 bullets):
- (To be filled after implementation)

**Links**:
- Commit: (TBD)
- PR: (TBD)

---

### Work Unit 5: Integration Testing & Documentation

**Goal**: End-to-end testing and documentation

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [ ] Full workflow tested (config → commands)
- [ ] Documentation complete
- [ ] README updated with configuration section
- [ ] Example jig.toml created
- [ ] Migration guide for existing users
- [ ] All tests passing

**Implementation Notes**:
- Approach:
  1. Create integration test scenarios
  2. Test: create config → run commands → verify behavior
  3. Write configuration documentation
  4. Add example jig.toml to docs
  5. Update README with configuration section
  6. Add troubleshooting for common config issues
- Files: `docs/configuration.md`, `README.md`, example files
- Decorators added: None (integration/docs only)

**Test Plan**:
- Integration tests:
  - Fresh project with jig.toml → all commands work
  - Migrate existing project: add jig.toml → commands respect it
  - Invalid config → clear error messages
  - pyproject.toml integration → works as expected
- Test file: `test/integration/test_config_workflow.py`
- Decorators added: Integration tests (no specific S- node)

**Docs Updated**:
- `docs/configuration.md` - Full configuration reference
- `README.md` - Configuration section
- `docs/examples/jig.toml` - Example configuration file

**Human Verification**:
- Follow documentation to configure a project
- Verify instructions are clear and accurate
- Test example jig.toml works as documented

**Reflect** (≤5 bullets):
- (To be filled after implementation)

**Links**:
- Commit: (TBD)
- PR: (TBD)

---

## Notes

### Current State

**Hardcoded paths in codebase**:
- Need to audit where paths are currently hardcoded
- Key locations: validation, impl rebuild, layers commands

**Python version consideration**:
- `tomllib` is stdlib in Python 3.11+
- May need `tomli` as fallback for 3.10 support
- Check project's minimum Python version

### Design Decisions

1. **Config structure**: `[jig.paths]` section for paths
2. **File priority**: jig.toml > .jig.toml > pyproject.toml
3. **Defaults**: Match current hardcoded values (src, test, jig)
4. **No environment variables yet**: Keep MVP simple, add later
5. **No CLI config settings yet**: Only paths in MVP

### Out of Scope (Future Work)

- Environment variable overrides (JIG_PATHS_TESTS=...)
- CLI default configuration (color, verbose)
- Validation configuration (enable/disable rules)
- Discovery patterns (source_include, test_include)
- `jigy config` command (show, init, validate)

### Testing Strategy

**Unit tests**: Fast, isolated, use tmp directories
- Config discovery
- TOML parsing
- Schema/defaults

**Integration tests**: Real CLI invocations
- Full workflow with config
- Error handling

### Open Questions

1. Should missing directories be an error or warning?
   - Proposal: Warning at config load, error when command needs the path

2. Should we validate paths exist at config load time?
   - Proposal: No, validate lazily when path is used

3. Minimum Python version for tomllib?
   - Check: If 3.11+, use stdlib. If 3.10, add tomli dependency.
