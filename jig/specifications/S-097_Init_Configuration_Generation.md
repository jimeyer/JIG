---
id: S-097
title: Init Configuration Generation
type: specification
outcomes: [O-028]
---
# Init Configuration Generation

The `jigy init` command generates a `jig.toml` configuration file with sensible defaults.

## Acceptance Criteria

1. Generated `jig.toml` contains:
   ```toml
   [integration]
   include_dig = true   # Set false if dig/ not detected

   [scan]
   ignore = [
       ".venv/",
       "__pycache__/",
       "node_modules/",
       "dist/",
       "build/",
   ]
   ```

2. `include_dig` is set to `true` if `dig/` directory or `dig.toml` exists, `false` otherwise

3. `[scan].ignore` replaces the former `.jigignore` file concept - all config lives in `jig.toml`

4. Generated file is valid TOML
