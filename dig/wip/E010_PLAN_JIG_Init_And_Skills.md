---
title: "PLAN: JIG Init and Skills"
type: plan
status: active
created: 1737237600
created_human: "2026-01-18 16:00 CST"
parent: "[[E009_JIGPLAN_JIG_Init_And_Skills]]"
children: []
---
# PLAN: JIG Init and Skills

- **SCOPE**: dig/wip/E006_SCOPE_JIG_Init_And_Skills.md
- **JIGPLAN**: dig/wip/E009_JIGPLAN_JIG_Init_And_Skills.md
- **Start**: 2026-01-18
- **Status**: Ready
- **Branch**: feature/jigy-init

---

## Constraints from JIGPLAN

**FORBIDDEN Bricks** (do not modify):
- B-decorators (layer 0): Core decorator infrastructure
- B-validation (layer 0): Validation engine
- B-impl-graph (layer 0): Implementation graph generation
- B-intent-graph (layer 0): Intent graph generation
- B-config (layer 0): May read, must not modify

**Layer Constraints:**
- B-templates at layer 0 (no dependencies)
- B-init at layer 0 (depends on B-templates, B-config)
- B-cli at layer 1 (depends on B-init)
- No upward dependencies

**Clean Break:**
- Greenfield feature, no legacy code to delete
- No backwards compatibility needed

---

## Key Existing Code References

(Populated during Fresh Agent Review)

| Concern | Location | Notes |
|---------|----------|-------|
| CLI main entry | src/jig/cli/main.py | Uses Click, OrderedGroup for command ordering |
| Command registration | src/jig/cli/main.py | Search for `@cli.command` pattern |
| Output options | src/jig/cli/output.py | add_output_options decorator, resolve_format() |
| Config loading | src/jig/cli/main.py | get_config(ctx) pattern in file |
| Project root discovery | src/jig/cli/discovery.py | find_project_root() |
| Test patterns | tests/cli/test_*.py | CliRunner, @jig.verifies pattern |
| COMMAND_ORDER | src/jig/cli/main.py | OrderedGroup.COMMAND_ORDER list (add "init" first) |
| Bricks already defined | jig/bricks.yaml | B-templates, B-init, M-jig.cli.init already in file |
| contextJIG source | agents/contextJIG.md | Copy verbatim as CONTEXT_JIG_MD_TEMPLATE |
| Mutual exclusivity | Click callback pattern | Check both flags, raise click.UsageError if both set |

---

## Execution Order

```
WU1 (Templates) ──┬── WU2 (Core Init) ── WU4 (CLI) ── WU5 (Validation) ── WU6 (Version Bump)
                  │
                  └── WU3 (Skill Installation) ─────┘
```

**Dependencies:**
- WU2, WU3 both depend on WU1 (templates)
- WU4 depends on WU2 and WU3 (init logic complete)
- WU5 depends on WU4 (CLI wired)
- WU6 depends on WU5 (validation passed)

---

## Test Strategy

- **New tests**:
  - tests/unit/test_templates.py - Template validity (YAML/TOML parsing)
  - tests/unit/test_init.py - Core init logic, idempotency
  - tests/cli/test_init.py - CLI flags, output modes
  - tests/integration/test_init_integration.py - Full init → validate cycle

- **Existing tests**: All must keep passing

- **Deleted tests**: None (greenfield)

---

## Work Unit Checklist

- [ ] WU1: Template Content Module — tests ☐ / code ☐
- [ ] WU2: Core Init Logic — tests ☐ / code ☐
- [ ] WU3: Skill Installation — tests ☐ / code ☐
- [ ] WU4: CLI Command Integration — tests ☐ / code ☐
- [ ] WU5: Validation — SCOPE verified ☐
- [ ] WU6: Version Bump — version 0.2.0 ☐

---

## Work Units

### Work Unit 1: Template Content Module

**Goal**: Create template constants module with all scaffolding content.

**Specs Addressed**: S-097 (partial), S-098 (partial), S-099 (partial), S-101 (partial)

**Acceptance Criteria**:
- [ ] JIG_TOML_TEMPLATE contains valid TOML with [integration] and [scan] sections
- [ ] CHARTER_MD_TEMPLATE contains valid frontmatter with G-1 placeholder
- [ ] BRICKS_YAML_TEMPLATE contains valid YAML (`bricks: []`)
- [ ] SKILL_MD_TEMPLATE contains /jig skill definition per SCOPE
- [ ] CONTEXT_JIG_MD_TEMPLATE contains contextJIG.md content (copied from agents/contextJIG.md)
- [ ] Tests verify template validity (parse without error)
- [ ] Tests with @jig.verifies("S-097"), @jig.verifies("S-098"), @jig.verifies("S-099") decorators
- [ ] jigy rebuild && jigy validate passes

**Success Gates** (all must pass):
- [ ] All tests pass: pytest tests/unit/test_templates.py -v
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors: ruff check src/jig/templates/

**Escalation Triggers** (stop and ask human if):
- Template content from SCOPE is ambiguous
- TOML/YAML syntax issues in templates
- Test failures persist after 2 retry attempts

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| TOML template content | See S-097 and E006 SCOPE | jig/specifications/S-097*.md |
| Charter template content | See S-098 and E006 SCOPE | jig/specifications/S-098*.md |
| SKILL.md content | Defined in E006 SCOPE | dig/wip/E006*.md lines 182-241 |
| contextJIG.md content | Copy verbatim from agents/contextJIG.md | agents/contextJIG.md |
| jig.toml include_dig comment | Implementation guidance, not in template | Set dynamically based on dig/ detection |

**Implementation Notes**:
- Files:
  - src/jig/templates/__init__.py (new)
  - src/jig/templates/templates.py (new)
  - tests/unit/test_templates.py (new)
- Templates are string constants, not Jinja2
- Use triple-quoted strings with .strip() for cleanliness
- **No @jig decorators on templates** - templates are data, not functions
- Decorators go on functions that USE templates (in WU2/WU3)

**Human Verification**:
```bash
pytest tests/unit/test_templates.py -v
ruff check src/jig/templates/
```

---

### Work Unit 2: Core Init Logic

**Goal**: Implement core initialization logic with idempotent behavior.

**Specs Addressed**: S-096, S-100, S-102

**Acceptance Criteria**:
- [ ] init_project() creates jig.toml, jig/ directory structure
- [ ] init_project() creates Charter_<project>.md with correct naming
- [ ] init_project() creates bricks.yaml scaffold
- [ ] init_project() creates jig/generated/ directory
- [ ] update_gitignore() appends jig/generated/ if not present
- [ ] Running twice creates nothing new (idempotent)
- [ ] Never overwrites Charter or bricks.yaml with content
- [ ] Detects dig/ or dig.toml to set include_dig in jig.toml
- [ ] Returns InitResult dataclass with success, paths_created, error
- [ ] Tests with @jig.verifies decorators
- [ ] Code with @jig.implements decorators

**Success Gates** (all must pass):
- [ ] All tests pass: pytest tests/unit/test_init.py -v
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors: ruff check src/jig/init.py

**Escalation Triggers** (stop and ask human if):
- Idempotency edge case unclear
- File permission issues in tests
- Test failures persist after 2 retry attempts
- FORBIDDEN brick modification needed

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| InitResult fields | success: bool, paths_created: list[Path], error: str \| None | E009 JIGPLAN |
| Project name derivation | --project flag or parent directory name | S-096, S-098 |
| dig detection | Check for dig/ directory or dig.toml file | S-097 |

**Implementation Notes**:
- Files:
  - src/jig/init.py (new)
  - tests/unit/test_init.py (new)
- Use pathlib.Path throughout
- InitResult is a dataclass
- init_project(project_root: Path, project_name: str | None, force: bool) -> InitResult
- Decorators: @jig.implements("S-096", "S-100", "S-102") on init_project

**Human Verification**:
```bash
pytest tests/unit/test_init.py -v
ruff check src/jig/init.py
```

---

### Work Unit 3: Skill Installation

**Goal**: Implement skill file installation with global/local options.

**Specs Addressed**: S-101

**Acceptance Criteria**:
- [ ] install_skills() creates .agent/skills/jig/SKILL.md
- [ ] install_skills() creates .agent/skills/jig/contextJIG.md
- [ ] --global-skills installs to ~/.agent/skills/ instead
- [ ] Skills always overwrite (they are templates, not user content)
- [ ] Works independently of jig/ structure existence
- [ ] Returns list of created paths
- [ ] Tests with @jig.verifies decorators
- [ ] Code with @jig.implements decorators

**Success Gates** (all must pass):
- [ ] All tests pass: pytest tests/unit/test_init.py::test_skill* -v
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks

**Escalation Triggers** (stop and ask human if):
- Home directory expansion issues
- Permission issues with ~/.agent/
- Test failures persist after 2 retry attempts

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| Local skill path | .agent/skills/jig/ relative to project root | E006 SCOPE |
| Global skill path | ~/.agent/skills/jig/ | E006 SCOPE |
| Skill always overwrites | Yes, templates not user content | S-102 |

**Implementation Notes**:
- Add to src/jig/init.py (extend existing module)
- install_skills(project_root: Path, global_install: bool = False) -> list[Path]
- Use Path.home() for global installation
- Decorators: @jig.implements("S-101") on install_skills

**Human Verification**:
```bash
pytest tests/unit/test_init.py -k skill -v
```

---

### Work Unit 4: CLI Command Integration

**Goal**: Wire jigy init command with all flags into CLI.

**Specs Addressed**: S-103

**Acceptance Criteria**:
- [ ] `jigy init` command registered in main.py
- [ ] --project / -p flag sets project name
- [ ] --no-skills flag skips skill installation
- [ ] --skills-only flag installs only skills
- [ ] --global-skills flag uses ~/.agent/skills/
- [ ] --force / -f flag allows overwriting
- [ ] --no-skills and --skills-only are mutually exclusive
- [ ] Standard -j/--json, -m/--markdown flags work
- [ ] Human-readable output lists created paths
- [ ] JSON output returns {success, paths_created} structure
- [ ] Tests with @jig.verifies decorators
- [ ] Code with @jig.implements decorators

**Success Gates** (all must pass):
- [ ] All tests pass: pytest tests/cli/test_init.py -v
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors

**Escalation Triggers** (stop and ask human if):
- Click decorator issues
- Mutual exclusivity enforcement unclear
- Test failures persist after 2 retry attempts

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| Command registration | Search for `@cli.command` pattern | main.py |
| Output format handling | add_output_options decorator + resolve_format() | output.py |
| Mutual exclusivity | Check flags in function, raise click.UsageError | See pattern below |
| COMMAND_ORDER update | Add "init" as first item in list | main.py OrderedGroup.COMMAND_ORDER |

**Mutual exclusivity pattern:**
```python
if no_skills and skills_only:
    raise click.UsageError("--no-skills and --skills-only are mutually exclusive")
```

**Implementation Notes**:
- Files:
  - src/jig/cli/init.py (new)
  - src/jig/cli/main.py (modify: add import, register command, update COMMAND_ORDER)
  - tests/cli/test_init.py (new)
- Pattern: Follow rebuild_group pattern from main.py
- Decorators: @jig.implements("S-103") on init_command
- Use CliRunner for testing

**Human Verification**:
```bash
pytest tests/cli/test_init.py -v
jigy init --help
```

---

### Work Unit 5: Validation

**Goal**: Verify SCOPE problem is solved at system boundary.

**SCOPE Reference**:
"jigy init bootstraps a project with idempotent directory/file creation. One skill (/jig) bootstraps agent awareness"

**Validation Approach**: Integration Test (preferred)

**Verification Steps**:
```bash
# Create temp directory
cd /tmp && mkdir test_init_validation && cd test_init_validation

# Run init
jigy init --project testproj

# Verify structure exists
ls -la jig/
ls -la .agent/skills/jig/
cat jig.toml
cat jig/Charter_testproj.md

# Run jigy validate (should pass on fresh project)
jigy rebuild && jigy validate

# Run init again (idempotent - should succeed with no new files)
jigy init --project testproj

# Cleanup
cd /tmp && rm -rf test_init_validation
```

**Expected Result**:
- All directories and files created on first run
- jig.toml has correct [integration] and [scan] sections
- Charter has G-1 placeholder
- Skills installed in .agent/skills/jig/
- jigy validate passes
- Second run reports "(nothing new)"

**Deliverable**:
- [x] Integration test added: tests/integration/test_init_integration.py

**Implementation Notes**:
- Integration test uses temp directory
- Verifies full init → validate cycle
- Verifies idempotency (run twice)
- Verifies --skills-only, --no-skills flags

**Human Verification**:
```bash
pytest tests/integration/test_init_integration.py -v
```

---

### Work Unit 6: Version Bump

**Goal**: Bump JIG version to 0.2.0 to mark init feature release.

**Specs Addressed**: (none - administrative)

**Acceptance Criteria**:
- [ ] src/jig/__init__.py has `__version__ = "0.2.0"`
- [ ] pyproject.toml has `version = "0.2.0"`
- [ ] jigy --version shows 0.2.0
- [ ] Final jigy rebuild && jigy validate passes

**Success Gates** (all must pass):
- [ ] jigy --version shows "0.2.0"
- [ ] All tests pass: pytest -v
- [ ] jigy rebuild && jigy validate passes

**Escalation Triggers** (stop and ask human if):
- Version conflict or unexpected version format
- Test failures unrelated to init

**Implementation Notes**:
- Files:
  - src/jig/__init__.py (modify line 5)
  - pyproject.toml (modify version field)
- Simple string replacement

**Human Verification**:
```bash
jigy --version
pytest -v
jigy rebuild && jigy validate
```

---

## Fresh Agent Review Results

**Review completed:** 2026-01-18

**Issues identified and resolved:**

| Issue | Resolution |
|-------|------------|
| Template constants can't have decorators | Removed decorator guidance from WU1; decorators go on functions that USE templates (WU2/WU3) |
| contextJIG.md source unclear | Clarified: copy verbatim from agents/contextJIG.md |
| WU3 parallel with WU1 incorrect | Fixed: WU3 depends on WU1 (needs templates) |
| COMMAND_ORDER position unspecified | Resolved: add "init" as first item |
| Line number references fragile | Changed to pattern-based references |
| Mutual exclusivity pattern vague | Added concrete code pattern |
| jig.toml comment confusion | Clarified: comment is implementation guidance, not in template |
| Spec files existence | Verified: S-096 through S-103 and O-028 exist (created in JIGPLAN) |
| Bricks already defined | Noted: B-templates, B-init, M-jig.cli.init already in bricks.yaml |

**No remaining blocking issues.**

---

## Execution Log

(Filled in by orchestrator during execution)

---

## Completion Summary

(Filled in after all WUs complete)

**Scope Delivered:**
- <to be filled>

**JIG Summary:**
- <to be filled>

**Clean Break Actions:**
- [x] No deprecated O/S nodes to delete (greenfield)
- [x] No legacy code to delete (greenfield)
- [ ] Final jigy rebuild && jigy validate passed

**Reflection Roll-Up:**
- Repeatable wins: <patterns that worked>
- Systemic frictions: <process issues>
- Open questions: <items for future work>
