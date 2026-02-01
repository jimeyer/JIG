---
id: S-096
title: Jigy Init Command
type: specification
outcomes: [O-028]
---
# Jigy Init Command

The `jigy init` command bootstraps a new JIG project with the required directory structure, configuration files, and optional agent skills.

## Acceptance Criteria

1. `jigy init` creates the following structure from the current working directory:
   - `jig.toml` - Configuration file
   - `jig/Charter_<project>.md` - Project charter with G-1 placeholder
   - `jig/specifications/` - Empty directory
   - `jig/outcomes/` - Empty directory
   - `jig/architecture/` - Empty directory
   - `jig/bricks.yaml` - Empty scaffold
   - `jig/generated/` - Empty directory for machine-written files

2. Project name is derived from:
   - `--project NAME` flag if provided
   - Parent directory name otherwise

3. Command returns zero exit code on success, non-zero on failure

4. Human-readable output lists all created paths

5. JSON output (`-j`) returns structured result with success status and paths_created array
