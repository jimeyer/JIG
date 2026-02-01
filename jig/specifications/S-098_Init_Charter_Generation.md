---
id: S-098
title: Init Charter Generation
type: specification
outcomes: [O-028]
---
# Init Charter Generation

The `jigy init` command generates a charter file with a placeholder goal.

## Acceptance Criteria

1. Charter filename is `Charter_<project_name>.md` where project_name is:
   - Value of `--project` flag if provided
   - Parent directory name otherwise

2. Charter is created at `jig/Charter_<project_name>.md`

3. Generated charter contains:
   ```markdown
   ---
   id: Charter
   type: charter
   goals: [G-1]
   ---
   # Charter

   ## G-1: [Define your first goal]
   ```

4. The `Charter_` prefix is required in the filename

5. Charter file uses valid YAML frontmatter
