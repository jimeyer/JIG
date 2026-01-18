---
id: S-100
title: Init Generated Directory Management
type: specification
outcomes: [O-028]
---
# Init Generated Directory Management

The `jigy init` command creates the generated directory and configures git to ignore it.

## Acceptance Criteria

1. `jig/generated/` directory is created if missing

2. If `.gitignore` exists:
   - Append `jig/generated/` if not already present
   - Do not modify if already present

3. If `.gitignore` does not exist:
   - Create it with `jig/generated/` as content

4. Appending to `.gitignore` preserves existing content and adds a newline before the entry if needed

5. Output indicates whether `.gitignore` was updated
