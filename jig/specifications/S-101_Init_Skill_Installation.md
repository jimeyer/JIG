---
id: S-101
title: Init Skill Installation
type: specification
outcomes: [O-028]
---
# Init Skill Installation

The `jigy init` command installs agent skills by default.

## Acceptance Criteria

1. By default, skills are installed to `.claude/skills/` with five skill directories:
   - `jig/` — `/jig` general reference skill (`SKILL.md` + `contextJIG.md`)
   - `jig-context/` — auto-loaded background knowledge (`SKILL.md` + `contextJIG.md`, `user-invocable: false`)
   - `jigplan/` — `/jigplan` workflow skill (`SKILL.md` + `instructions.md` + `contextJIG.md`)
   - `plan/` — `/plan` workflow skill (`SKILL.md` + `instructions.md` + `contextJIG.md`)
   - `do-plan/` — `/do-plan` workflow skill (`SKILL.md` + `instructions.md` + `do-wu.md`)

2. `--no-skills` flag skips skill installation entirely

3. `--skills-only` flag installs only skills, skipping jig/ structure creation

4. `--global-skills` flag installs to `~/.claude/skills/` instead of project-local

5. Skills are always overwritten (they are templates, not user content)

6. Skill installation works independently of jig/ structure existence
