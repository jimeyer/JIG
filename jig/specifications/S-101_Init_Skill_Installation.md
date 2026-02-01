---
id: S-101
title: Init Skill Installation
type: specification
outcomes: [O-028]
---
# Init Skill Installation

The `jigy init` command installs agent skills by default.

## Acceptance Criteria

1. By default, skills are installed to `.agent/skills/jig/`:
   - `SKILL.md` - Skill definition for `/jig` command
   - `contextJIG.md` - Universal JIG mental model

2. `--no-skills` flag skips skill installation entirely

3. `--skills-only` flag installs only skills, skipping jig/ structure creation

4. `--global-skills` flag installs to `~/.agent/skills/` instead of project-local

5. Skills are always overwritten (they are templates, not user content)

6. Skill installation works independently of jig/ structure existence
