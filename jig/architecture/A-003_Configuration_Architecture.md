---
id: A-003
type: architecture
title: Configuration Architecture
status: active
supports_goals: [G-001]
constrains: [S-062, S-063, S-064, S-065]
---

# Configuration Architecture

## Context

JIG is designed to work out of the box with zero configuration. However, real projects have diverse structures: `tests/` vs `test/`, `lib/` vs `src/`, monorepos with nested projects. A configuration system enables JIG adoption across this variety without compromising the zero-config experience for standard layouts.

This document establishes the enduring architecture of JIG configuration: its philosophy, schema, and contract. It is evergreen—the authoritative reference for all configuration development.

---

## Philosophy

### Configuration is Optional

The defining principle: **JIG SHALL work without any configuration file.**

Every setting has a sensible default. Configuration exists only to override defaults when a project's structure differs from conventions. Projects using standard layouts (`src/`, `test/`, `jig/`) need no configuration.

### Convention Over Configuration

JIG follows established conventions:

| Convention | Default |
|------------|---------|
| Source code | `src/` |
| Tests | `test/` |
| JIG artifacts | `jig/` |
| Specifications | `jig/specifications/` |
| Outcomes | `jig/outcomes/` |
| Architecture | `jig/architecture/` |
| Charter | `jig/Charter.md` |
| Bricks | `jig/bricks.yaml` |
| Generated graphs | `jig/generated/` |

Configuration overrides conventions; it does not replace them.

### Explicit Over Implicit

When configuration IS used:
- Settings are explicit, not inferred from environment
- No magic discovery of config from unrelated files
- No implicit inheritance from parent directories
- What you see in the config file is what you get

### Fail Fast on Invalid Config

Invalid configuration fails immediately with clear error messages:
- Unknown keys are errors (catches typos)
- Invalid values explain what's wrong and what's expected
- Missing required fields (when a section is present) are explicit errors

---

## Design Principles

### 1. TOML Format

All JIG configuration uses TOML:

**Why TOML over YAML:**
- No type coercion surprises (`on: true` vs `on: "true"`)
- Clear section syntax (`[section.subsection]`)
- Comments are first-class (`# inline documentation`)
- Python ecosystem standard (pyproject.toml)
- `tomllib` in stdlib since Python 3.11

**Why TOML over JSON:**
- Comments supported
- Less verbose
- Human-writable, not just machine-writable

**Note:** `bricks.yaml` remains YAML because it's data (list of brick definitions), not configuration. Configuration and data have different requirements.

### 2. Single Project Config

One configuration file per project. No cascading configs, no inheritance, no merging multiple files. This eliminates:
- "Where did this setting come from?"
- Order-dependent configuration
- Debugging inheritance chains

### 3. Flat When Possible

Prefer flat structures over deep nesting:

```toml
# Good: Flat and clear
[jig.paths]
source = "src"
tests = "tests"

# Avoid: Unnecessary nesting
[jig.paths.directories.source]
path = "src"
```

### 4. Explicit Section Activation

Sections are independent. Specifying `[jig.paths]` doesn't require specifying other sections. Each section has complete defaults.

### 5. No Computed Defaults

Defaults are static values, not computed from other settings:

```toml
# Wrong: specifications depends on jig_root
jig_root = "jig"
specifications = "${jig_root}/specifications"  # NO variable interpolation

# Right: Each path is independent (relative to jig_root by convention)
[jig.paths]
jig_root = "jig"
specifications = "specifications"  # Relative to jig_root
```

---

## Configuration Contract

This section defines the complete configuration schema. All settings listed here are **contractual**—they will not be removed without a major version bump and migration path.

### File Discovery

JIG searches for configuration in this order (first found wins):

1. `jig.toml` — Dedicated JIG config (recommended)
2. `.jig.toml` — Hidden file variant
3. `pyproject.toml` — Under `[tool.jig]` section (only if section exists)

Search starts from the current directory and walks up to the filesystem root, stopping at the first file found.

**Project root** is determined by:
1. Directory containing the config file, OR
2. Directory containing `jig/` or `.jig/` if no config file

### Path Configuration

**Section:** `[jig.paths]`

| Key | Type | Default | Relative To |
|-----|------|---------|-------------|
| `source` | string | `"src"` | project root |
| `tests` | string | `"test"` | project root |
| `jig_root` | string | `"jig"` | project root |
| `specifications` | string | `"specifications"` | jig_root |
| `outcomes` | string | `"outcomes"` | jig_root |
| `architecture` | string | `"architecture"` | jig_root |
| `charter` | string | `"Charter.md"` | jig_root |
| `bricks` | string | `"bricks.yaml"` | jig_root |
| `generated` | string | `"generated"` | jig_root |

**Path resolution:**
- `source`, `tests`, `jig_root`: Relative to project root
- All others: Relative to `jig_root`
- Absolute paths are respected but discouraged

**Example:**
```toml
[jig.paths]
source = "lib"           # Project uses lib/ instead of src/
tests = "tests"          # Project uses tests/ instead of test/
```

---

## Minimal Configuration Examples

### Override Test Directory Only

```toml
# jig.toml
[jig.paths]
tests = "tests"
```

### Non-Standard Project Layout

```toml
# jig.toml
[jig.paths]
source = "lib"
tests = "tests"
jig_root = ".jig"
```

### pyproject.toml Integration

```toml
# pyproject.toml
[tool.jig.paths]
tests = "tests"
```

---

## API Contract

### Loading Configuration

```python
from jig.config import load_config, JigConfig

# Load from discovered location (recommended)
config: JigConfig = load_config()

# Load with explicit project root
config = load_config(project_root=Path("/path/to/project"))
```

### Accessing Configuration

```python
# Path configuration (resolved to absolute paths)
config.paths.source      # Path("/project/src")
config.paths.tests       # Path("/project/test")
config.paths.jig_root    # Path("/project/jig")
config.paths.specifications  # Path("/project/jig/specifications")

# Check if using defaults
config.has_config_file   # True if config file was found
config.config_file_path  # Path to config file or None
```

### Configuration Dataclass

```python
@dataclass
class PathsConfig:
    source: Path
    tests: Path
    jig_root: Path
    specifications: Path
    outcomes: Path
    architecture: Path
    charter: Path
    bricks: Path
    generated: Path

@dataclass
class JigConfig:
    paths: PathsConfig
    project_root: Path
    config_file_path: Path | None
    has_config_file: bool
```

---

## Error Handling

### Missing Config File

Not an error. JIG works without configuration:

```
$ jigy align
# Works with defaults, no warning about missing config
```

### Invalid TOML Syntax

```
$ jigy align
Error: Invalid configuration file: jig.toml

  Line 3, column 5: Unexpected character '='

  [jig.paths
       ^

  Expected ']' to close section header
```

### Path Does Not Exist

Warning, not error (path may be created later):

```
$ jigy validate
Warning: Configured path does not exist: tests/
  Configured in: jig.toml [jig.paths.tests]

Validating...
```

---

## Extensibility

### Adding New Configuration

New configuration settings SHALL:

1. Have a sensible default (config remains optional)
2. Be documented in this contract before implementation
3. Use flat structure unless nesting is semantically required
4. Include type, default, and description
5. Produce clear errors for invalid values

### Reserved Top-Level Sections

The following `[jig.*]` sections are reserved:

| Section | Purpose |
|---------|---------|
| `[jig.paths]` | File and directory paths |
| `[jig.discovery]` | File discovery patterns (future) |
| `[jig.validation]` | Validation behavior (future) |
| `[jig.cli]` | CLI defaults (future) |
| `[jig.audit]` | Audit system settings (future) |
| `[jig.graph]` | Graph generation settings (future) |

Third-party extensions SHOULD use `[jig.x.*]` namespace.

---

## Consequences

### Benefits

- **Zero-config default** — Works immediately with sensible defaults
- **Single source of truth** — One config file, no inheritance complexity
- **Python ecosystem aligned** — TOML format, pyproject.toml support
- **Explicit and predictable** — No magic, no surprises
- **Clear errors** — Invalid config fails fast with actionable messages

### Trade-offs

- **No cascading config** — Can't share settings across monorepo projects
- **No environment interpolation** — No `${VAR}` in config values
- **TOML learning curve** — Users unfamiliar with TOML must learn syntax
- **Separate from bricks.yaml** — Two files to maintain (config + bricks)

### Mitigations

- **Monorepo:** Each subproject has its own `jig.toml`
- **Environment needs:** Use environment variable overrides (future)
- **TOML unfamiliarity:** Provide examples and clear documentation
- **Two files:** bricks.yaml is data, jig.toml is config—separation is intentional

---

## Compliance

All configuration development SHALL comply with this architecture. New settings, sections, or behaviors SHALL be documented here before implementation. Deviations require explicit amendment to this document.

This contract is evergreen—it evolves with JIG but maintains backward compatibility within major versions.

---

## Summary

JIG configuration follows one principle: **optional but explicit**.

```toml
# The simplest config: override just what you need
[jig.paths]
tests = "tests"
```

No configuration required for standard projects. Full control available when needed. No surprises either way.
