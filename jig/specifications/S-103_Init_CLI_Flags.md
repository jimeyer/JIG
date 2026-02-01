---
id: S-103
title: Init CLI Flags
type: specification
outcomes: [O-028]
---
# Init CLI Flags

The `jigy init` command supports flags for customizing initialization behavior.

## Acceptance Criteria

1. `--project NAME` - Sets project name for Charter filename
   - Default: parent directory name

2. `--no-skills` - Skip skill installation
   - Mutually exclusive with `--skills-only`

3. `--skills-only` - Only install skills, skip jig/ structure
   - Mutually exclusive with `--no-skills`

4. `--global-skills` - Install skills to `~/.agent/skills/` instead of `.agent/skills/`
   - Can combine with other flags

5. `--force` - Overwrite existing files
   - Does not overwrite user content (Charter, bricks.yaml with content)

6. All flags have short forms where appropriate:
   - `--project` / `-p`
   - `--force` / `-f`

7. Standard global flags apply: `-j/--json`, `-m/--markdown`, `--help`
