---
id: S-102
title: Init Idempotent Behavior
type: specification
outcomes: [O-028]
---
# Init Idempotent Behavior

The `jigy init` command is idempotent - running it multiple times is safe and produces consistent results.

## Acceptance Criteria

1. Create directories only if they don't exist

2. Create files only if they don't exist (except skills, see below)

3. Never overwrite:
   - Charter (user content)
   - `bricks.yaml` (user content)
   - `jig.toml` (unless `--force`)

4. Always overwrite:
   - Skill files (`SKILL.md`, `contextJIG.md`) - they are templates, not user content

5. Always ensure `jig/generated/` exists (it may be wiped by rebuild operations)

6. `--force` flag allows overwriting existing files (except user content in jig/)

7. Second run on initialized project outputs "(nothing new)" in created list

8. Second run returns success exit code (not an error)
