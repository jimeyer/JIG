---
title: JIG Init and Skills
type: scope
status: implemented
decision: completed
created: 1737151200
created_human: 2026-01-17 16:00 CST
parent: "[[jig/dig/archive/DJ002_SCOPE_CLI_Recommendations]]"
children: []
---
# JIG Init and Skills

## Executive Summary

Define `jigy init` command and a single JIG skill for Claude Code integration. `jigy init` bootstraps a project with idempotent directory/file creation. One skill (`/jig`) bootstraps agent awareness; CLI tools (`context`, `validate`, `mend`) do the heavy lifting.

---

## Problem Statement

### Current State

| Component | Status |
|-----------|--------|
| `jigy init` | Not implemented (DIG has `digy init`) |
| JIG skills | None defined |
| Project bootstrap | Manual directory creation |

### Requirements (from DJ002)

1. `jigy init` creates `jig.toml` with `[integration]` section
2. Config lives in project root for discoverability
3. Parallel structure with `digy init`
4. Minimal skill surface — agent intelligence + CLI tools do the work

---

## Scope of Work

### 1. `jigy init` Command

**Behavior:** Idempotent project initialization. Create missing structure, never clobber existing content. Install agent skills by default (parallel to `digy init`).

**Creates:**

```
myproject/
├── jig.toml                           # config with integration settings
├── jig/
│   ├── Charter_myproject.md           # template with G-1 placeholder
│   ├── architecture/                  # empty directory
│   ├── outcomes/                      # empty directory
│   ├── specifications/                # empty directory
│   ├── bricks.yaml                    # empty scaffold
│   └── generated/                     # empty directory (machine-written)
└── .agent/skills/jig/
    ├── SKILL.md                       # skill definition
    └── contextJIG.md                  # universal JIG mental model
```

Skill is self-contained. Universal knowledge (contextJIG.md) bundled with skill. Project-specific data (bricks.yaml, existing specs) read from `jig/`.

**Flags (parallel to `digy init`):**

| Flag | Purpose |
|------|---------|
| `--project NAME` | Project name for Charter filename (default: parent directory name) |
| `--no-skills` | Skip skill installation |
| `--skills-only` | Only install skills, skip jig/ structure |
| `--global-skills` | Install to `~/.agent/skills/` instead of project |
| `--force` | Overwrite existing files |

**`jig.toml` template:**
```toml
[integration]
include_dig = true   # Set false if dig/ not detected

[scan]
# Directories to exclude from @jig.implements / @jig.verifies scanning
ignore = [
    ".venv/",
    "__pycache__/",
    "node_modules/",
    "dist/",
    "build/",
]
```

This replaces `.jigignore` — all config lives in one file. Clean break, no fallback.

**`jig/Charter_<project>.md` template:**

Filename convention: `Charter_<project_name>.md` (e.g., `Charter_jig.md`, `Charter_myapp.md`)

The `Charter_` prefix is required. Project name is inferred from:
1. `--project` flag if provided
2. Parent directory name otherwise

```markdown
---
id: Charter
type: charter
goals: [G-1]
---
# Charter

## G-1: [Define your first goal]
```

**`jig/bricks.yaml` scaffold:**
```yaml
bricks: []
```

**Idempotent rules:**
- Create directories if missing
- Create files only if missing (unless `--force`)
- Never overwrite Charter or `bricks.yaml` with content
- Always ensure `generated/` exists (gets wiped by rebuild)
- Detect `dig/` or `dig.toml` to set `include_dig`
- Skills always overwrite (they're templates, not user content)
- Append `jig/generated/` to `.gitignore` if not already present

**Output:**
```bash
$ cd myproject
$ jigy init
JIG initialized successfully!

Created:
  jig.toml
  jig/Charter_myproject.md
  jig/specifications/
  jig/outcomes/
  jig/architecture/
  jig/bricks.yaml
  jig/generated/
  .agent/skills/jig/SKILL.md
  .agent/skills/jig/contextJIG.md

Updated:
  .gitignore (added jig/generated/)

Next steps:
  - Edit jig/Charter_myproject.md to define your goals
  - Use /jig to bootstrap agent awareness

$ jigy init --project acme
JIG initialized successfully!

Created:
  jig/Charter_acme.md
  ...

$ jigy init  # second run - idempotent
JIG initialized successfully!

Created:
  (nothing new)

$ jigy init --skills-only
JIG initialized successfully!

Created:
  .agent/skills/jig/SKILL.md
  .agent/skills/jig/contextJIG.md

$ jigy init -j
{"success":true,"paths_created":["jig.toml","jig/Charter_myproject.md",...]}
```

### 2. JIG Skill

One skill bootstraps agent awareness. CLI tools do the work.

**Philosophy:** Agents are smart. They don't need hand-holding through "create a spec" or "implement a spec" — they can figure that out from `contextJIG.md`. What they need is:
1. The mental model (what JIG is, how it works)
2. The CLI tools (how to query, diagnose, repair)

**The `/jig` skill:**

`.agent/skills/jig/SKILL.md`:
```markdown
---
name: jig
description: Work with JIG intent graphs. Invoke with /jig.
---

# jig

Manage alignment between specifications, code, and tests.

## Bootstrap

Read `contextJIG.md` (in this skill folder) for universal JIG knowledge:
- G-A-O-S-C-T hierarchy (goals → outcomes → specs → code → tests)
- Frontmatter schemas for each artifact type
- Decorator syntax (`@jig.implements`, `@jig.verifies`)
- Validation rules

Read project-specific files:
- `jig/bricks.yaml` — brick definitions, layer/tower structure
- `jig/specifications/*.md` — existing specs as examples
- `jig/outcomes/*.md` — existing outcomes

## CLI Commands

| Command | Purpose |
|---------|---------|
| `jigy context` | Project overview |
| `jigy context <id>` | Understand any artifact (S-###, O-###, file path) |
| `jigy validate -j` | Diagnose issues, get fix templates |
| `jigy mend --auto` | Auto-fix safe issues |
| `jigy mend --apply fixes.json` | Apply explicit fixes |

## Workflows

**Understand something:**
```bash
jigy context S-042        # spec and its neighborhood
jigy context src/foo.py   # file's specs and tests
```

**Fix graph issues (validate/mend contract):**
```bash
jigy validate -j > errors.json   # get errors with fix templates
# Fill in ??? values in the fix templates
jigy mend --apply fixes.json     # apply fixes
```

**Create artifacts:**
Read `contextJIG.md` for schemas. Use standard file operations.

**Add decorators:**
```python
@jig.implements("S-042")
def my_function(): ...

@jig.verifies("S-042")
def test_my_function(): ...
```
```

**That's it.** One skill. Agent reads the mental model, uses CLI tools, does the thinking.

---

## Design Decisions

### Why idempotent init?

Running `jigy init` in an existing project should be safe. Common scenarios:
- CI/CD pipelines that ensure project structure
- Onboarding scripts that run init defensively
- Recovery after partial directory deletion

Clobber-on-exist would be destructive. Error-on-exist would be annoying.

### Why only one skill?

Agents are intelligent. They don't need separate skills for "create spec", "implement spec", "verify spec" — that's hand-holding. They need:

1. **Mental model** — `contextJIG.md` explains JIG completely
2. **Query tool** — `jigy context` answers "what is X?"
3. **Diagnosis tool** — `jigy validate` answers "what's wrong?"
4. **Repair tool** — `jigy mend` answers "how do I fix it?"

With these primitives, the agent can figure out any workflow. More skills would just be redundant documentation of what the agent can already derive.

### Why validate/mend instead of many small skills?

The validate/mend contract (see [[E008_CONCEPT_Validate_Mend_Contract]]) provides:
- Structured diagnosis with fix templates
- Agent fills in decisions, tool executes
- Separation of "what's wrong" from "what to do about it"

This is more powerful than individual skills because it handles ALL graph maintenance in one pattern, not just the cases we thought to write skills for.

### Why contextJIG.md in the skill folder?

The mental model is universal JIG knowledge:
- G-A-O-S-C-T hierarchy
- Frontmatter schemas
- Decorator syntax
- Validation rules

Project-specific data (bricks, existing specs) lives in `jig/`. Bundling contextJIG.md with the skill makes it self-contained — `jigy init --skills-only` gives you everything you need.

---

## Implementation Notes

### CLI Changes

Add to `src/jig/cli/`:
- `init.py` — New `jigy init` command with flags
- Update `main.py` — Register command

### Templates Module

Add to `src/jig/templates/`:
- `__init__.py` — Module init
- `templates.py` — All templates as string constants:
  - `CHARTER_MD` — Charter.md template
  - `BRICKS_YAML` — bricks.yaml scaffold
  - `SKILL_MD` — The /jig skill definition
  - `CONTEXT_JIG_MD` — contextJIG.md (bundled with skill)

### Init Module

Add to `src/jig/`:
- `init.py` — Core init logic, returns `InitResult` dataclass

```python
@dataclass
class InitResult:
    success: bool
    paths_created: list[Path]
    error: str | None = None
```

### Testing

- Unit tests for init idempotency (run twice, second creates nothing)
- Unit tests for each flag combination
- Integration test: init → validate → mend cycle

### Version Bump

Bump JIG version to 0.2.0 (from 0.1.0):
- `src/jig/__init__.py` → `__version__ = "0.2.0"`
- `pyproject.toml` → `version = "0.2.0"`

---

## Out of Scope

- `jigy context` command (see [[E007_CONCEPT_Context_Command_Design]])
- `jigy new` command (DJ002 P2)
- Cross-tool context integration (DJ003)

---

## References

- [[jig/dig/archive/DJ002_SCOPE_CLI_Recommendations]] — Command structure, init requirements
- [[jig/dig/archive/DJ001_CONCEPT_CLI_Design_Manifesto]] — Output format principles
- [[E007_CONCEPT_Context_Command_Design]] — `jigy context` design
- [[E008_CONCEPT_Validate_Mend_Contract]] — `jigy validate` / `jigy mend` contract
