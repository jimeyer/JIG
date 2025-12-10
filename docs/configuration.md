# JIG Configuration

JIG uses a configuration file to customize project paths. This allows teams to adapt JIG to their existing project structure without renaming directories.

## Configuration File Locations

JIG searches for configuration in the following order (first found wins):

1. `jig.toml` - Dedicated JIG configuration file
2. `.jig.toml` - Hidden configuration file
3. `pyproject.toml` - Python project configuration (under `[tool.jig]`)

If no configuration file is found, JIG uses sensible defaults.

## Configuration Format

### jig.toml / .jig.toml

```toml
[jig.paths]
source = "src"
tests = "test"
jig_root = "jig"
specifications = "specifications"
outcomes = "outcomes"
bricks = "bricks.yaml"
generated = "generated"
```

### pyproject.toml

```toml
[tool.jig.paths]
source = "src"
tests = "test"
jig_root = "jig"
```

## Path Settings

All paths are relative to the project root (where the `jig/` directory is located).

| Setting | Default | Description |
|---------|---------|-------------|
| `source` | `src` | Directory containing source code to analyze |
| `tests` | `test` | Directory containing test files |
| `jig_root` | `jig` | Root directory for JIG artifacts |
| `specifications` | `specifications` | Specifications directory (relative to `jig_root`) |
| `outcomes` | `outcomes` | Outcomes directory (relative to `jig_root`) |
| `bricks` | `bricks.yaml` | Bricks definition file (relative to `jig_root`) |
| `generated` | `generated` | Generated graphs directory (relative to `jig_root`) |

### Path Resolution

- `source` and `tests` are resolved relative to **project root**
- `specifications`, `outcomes`, `bricks`, and `generated` are resolved relative to **jig_root**

For example, with this configuration:

```toml
[jig.paths]
jig_root = "custom_jig"
specifications = "specs"
```

JIG will look for specifications in `<project_root>/custom_jig/specs/`.

## Examples

### Standard Python Project

No configuration needed - defaults match standard layout:

```
my-project/
├── src/
│   └── my_package/
├── test/
│   └── test_module.py
└── jig/
    ├── specifications/
    ├── outcomes/
    └── bricks.yaml
```

### Project with "tests" Directory

```toml
# jig.toml
[jig.paths]
tests = "tests"
```

```
my-project/
├── src/
├── tests/           # Custom test directory
└── jig/
```

### Project with "lib" Source Directory

```toml
# jig.toml
[jig.paths]
source = "lib"
```

```
my-project/
├── lib/             # Custom source directory
├── test/
└── jig/
```

### Fully Custom Layout

```toml
# jig.toml
[jig.paths]
source = "lib"
tests = "tests"
jig_root = ".jig"
specifications = "specs"
outcomes = "goals"
bricks = "architecture.yaml"
generated = "graphs"
```

```
my-project/
├── lib/
├── tests/
└── .jig/
    ├── specs/
    ├── goals/
    ├── architecture.yaml
    └── graphs/
```

### Using pyproject.toml

```toml
# pyproject.toml
[project]
name = "my-project"
version = "1.0.0"

[tool.jig.paths]
source = "src/main"
tests = "src/test"
```

## Partial Configuration

You only need to specify settings that differ from defaults. JIG merges your configuration with defaults:

```toml
# Only override tests directory
[jig.paths]
tests = "tests"
# source defaults to "src"
# jig_root defaults to "jig"
# etc.
```

## Migration Guide

### Existing Projects

If you're adding JIG to an existing project with non-standard paths:

1. Create a `jig.toml` file in your project root
2. Configure paths to match your existing structure
3. Run `jigy validate intent` to verify configuration works

### From Hardcoded Paths

If you were previously modifying JIG source code to change paths:

1. Revert any source code modifications
2. Create a `jig.toml` with your custom paths
3. Configuration takes effect immediately for all commands

## Troubleshooting

### Configuration Not Found

JIG searches from the current directory upward for a `jig/` directory to identify the project root. Ensure you're running commands from within your project.

### Invalid TOML Syntax

If you see "Invalid TOML syntax" errors, check your configuration file for:
- Missing closing brackets `]`
- Unquoted strings with special characters
- Incorrect nesting

### Paths Not Resolving

Remember:
- `source` and `tests` are relative to **project root**
- Other paths are relative to **jig_root**

Use absolute paths for debugging, then convert to relative paths.

## Related

- [S-062: Configuration File Discovery](../jig/specifications/S-062.md)
- [S-063: TOML Configuration Parsing](../jig/specifications/S-063.md)
- [S-064: Path Configuration with Defaults](../jig/specifications/S-064.md)
- [S-065: CLI Integration with Configuration](../jig/specifications/S-065.md)
