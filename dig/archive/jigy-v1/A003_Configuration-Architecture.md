---
title: "A003: Configuration Architecture"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1765378531
created_human: "2025-12-10 08:55 CST"
parent: "[[B015_PROPOSAL_JIG-Configuration-File]]"
children: []
---
# A003: Configuration Architecture

**Status:** Accepted
**Date:** 2025-12-10
**Related:** A001 (Core Artifacts Contract), A002 (CLI Command Architecture), B015 (Configuration Proposal)

---

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

## Role Models

### pyproject.toml — The Python Standard

```toml
[tool.black]
line-length = 88
target-version = ['py39']

[tool.pytest.ini_options]
testpaths = ["tests"]
```

pyproject.toml establishes the pattern: tool-specific configuration under `[tool.name]`. JIG adopts this for `[tool.jig]` in pyproject.toml integration.

### Cargo.toml — Rust's Exemplar

```toml
[package]
name = "my-project"
version = "0.1.0"

[dependencies]
serde = "1.0"
```

Cargo demonstrates clear section organization, minimal required fields, and TOML as the format of choice for build tools.

### .gitconfig — Layered Defaults

```ini
[core]
    editor = vim
[user]
    name = Developer
    email = dev@example.com
```

Git shows layered configuration (system → global → local) with sensible defaults at each level. JIG adopts the principle but simplifies to a single project-level config.

### EditorConfig — Discovery Convention

```ini
root = true

[*.py]
indent_style = space
indent_size = 4
```

EditorConfig demonstrates upward directory search until a marker is found. JIG uses similar discovery for project root.

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

Sections are independent. Specifying `[jig.paths]` doesn't require specifying `[jig.validation]`. Each section has complete defaults.

### 5. No Computed Defaults

Defaults are static values, not computed from other settings:

```toml
# Wrong: specifications depends on jig_root
jig_root = "jig"
specifications = "${jig_root}/specifications"  # NO variable interpolation

# Right: Each path is independent
[jig.paths]
jig_root = "jig"
specifications = "jig/specifications"  # Explicit full path
```

Exception: Some paths are relative to `jig_root` by documented convention, but this is semantic, not string interpolation.

### 6. Schema Versioned

Configuration includes a schema version for forward compatibility:

```toml
[jig]
version = "1"  # Schema version, not JIG version
```

This enables future schema migrations while maintaining backward compatibility.

---

## Configuration Contract

This section defines the complete configuration schema. All settings listed here are **contractual**—they will not be removed without a major version bump and migration path.

### File Discovery

JIG searches for configuration in this order (first found wins):

1. `jig.toml` — Dedicated JIG config (recommended)
2. `.jig.toml` — Hidden file variant
3. `pyproject.toml` — Under `[tool.jig]` section

Search starts from the current directory and walks up to the filesystem root, stopping at the first file found.

**Project root** is determined by:
1. Directory containing the config file, OR
2. Directory containing `jig/` or `.jig/` if no config file

### Schema Structure

```
[jig]
├── version                    # Schema version (required if config exists)
├── [paths]                    # Path configuration
│   ├── source                 # Source code directory
│   ├── tests                  # Test directory
│   ├── jig_root              # JIG artifacts root
│   ├── specifications        # Specs directory (relative to jig_root)
│   ├── outcomes              # Outcomes directory (relative to jig_root)
│   ├── bricks                # Bricks file (relative to jig_root)
│   └── generated             # Generated graphs (relative to jig_root)
├── [discovery]               # File discovery patterns (future)
├── [validation]              # Validation settings (future)
└── [cli]                     # CLI defaults (future)
```

### Path Configuration

**Section:** `[jig.paths]`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `source` | string | `"src"` | Source code directory |
| `tests` | string | `"test"` | Test directory |
| `jig_root` | string | `"jig"` | JIG artifacts root directory |
| `specifications` | string | `"specifications"` | Specs directory (relative to jig_root) |
| `outcomes` | string | `"outcomes"` | Outcomes directory (relative to jig_root) |
| `bricks` | string | `"bricks.yaml"` | Bricks file (relative to jig_root) |
| `generated` | string | `"generated"` | Generated graphs (relative to jig_root) |

**Path resolution:**
- `source`, `tests`, `jig_root`: Relative to project root
- `specifications`, `outcomes`, `bricks`, `generated`: Relative to `jig_root`
- Absolute paths are respected but discouraged

**Example:**
```toml
[jig]
version = "1"

[jig.paths]
source = "lib"           # Project uses lib/ instead of src/
tests = "tests"          # Project uses tests/ instead of test/
```

### Reserved Sections (Future)

The following sections are reserved for future implementation:

#### Discovery Configuration (Future)

```toml
[jig.discovery]
source_include = ["**/*.py"]
source_exclude = ["**/__pycache__/**", "**/migrations/**"]
test_include = ["**/test_*.py", "**/*_test.py"]
test_exclude = ["**/conftest.py"]
```

#### Validation Configuration (Future)

```toml
[jig.validation]
strict = true  # Fail on warnings

[jig.validation.bricks]
require_layer_field = true
validate_layer_constraints = true
```

#### CLI Configuration (Future)

```toml
[jig.cli]
color = "auto"  # "auto", "always", "never"
```

---

## Precedence Rules

When multiple sources can provide a value, precedence is (highest to lowest):

1. **CLI flags** — Explicit command-line arguments
2. **Environment variables** — `JIG_*` prefixed variables (future)
3. **Configuration file** — `jig.toml` or equivalent
4. **Default values** — Built-in sensible defaults

**Rationale:** CLI flags enable one-off overrides. Environment variables enable CI/CD customization. Config files enable project-wide settings. Defaults ensure zero-config works.

### Environment Variables (Future)

Pattern: `JIG_SECTION_KEY=value`

```bash
JIG_PATHS_TESTS=tests jigy validate
JIG_PATHS_SOURCE=lib jigy rebuild impl
```

Environment variables are uppercase, underscores replace dots and hyphens.

---

## Minimal Configuration Examples

### Override Test Directory Only

```toml
# jig.toml
[jig]
version = "1"

[jig.paths]
tests = "tests"
```

### Non-Standard Project Layout

```toml
# jig.toml
[jig]
version = "1"

[jig.paths]
source = "lib"
tests = "tests"
jig_root = ".jig"
```

### pyproject.toml Integration

```toml
# pyproject.toml
[tool.jig]
version = "1"

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

# Load from specific path
config = load_config(path=Path("custom/jig.toml"))

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

# Raw configuration (as specified in file)
config.raw["jig"]["paths"]["source"]  # "src"

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
    bricks: Path
    generated: Path

@dataclass
class JigConfig:
    version: str
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

### Unknown Configuration Key

```
$ jigy align
Error: Unknown configuration key in jig.toml

  [jig.paths]
  soruce = "src"
  ^^^^^^

  Did you mean 'source'?
```

### Invalid Value Type

```
$ jigy align
Error: Invalid configuration value in jig.toml

  [jig.paths]
  tests = 123
          ^^^

  Expected string, got integer
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

## Migration

### From Hardcoded Paths

Projects using JIG before configuration support:

1. If using standard layout (`src/`, `test/`, `jig/`): No action needed
2. If using custom layout: Create `jig.toml` with path overrides

### Adding Configuration to Existing Project

```bash
# 1. Check current behavior
jigy align

# 2. Create minimal config
cat > jig.toml << 'EOF'
[jig]
version = "1"

[jig.paths]
tests = "tests"  # Or whatever your test dir is
EOF

# 3. Verify behavior unchanged
jigy align
```

### Configuration Schema Upgrades

When schema version changes:

1. JIG reads old schema version
2. JIG applies documented migrations
3. JIG warns about deprecated settings
4. JIG suggests config file update

```
$ jigy align
Warning: Configuration schema version "1" is outdated.
  Current schema version: "2"

  Migration available:
    - [jig.validation.strict] moved to [jig.validation.mode]

  Run 'jigy config migrate' to update your configuration.
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
| `[jig.discovery]` | File discovery patterns |
| `[jig.validation]` | Validation behavior |
| `[jig.cli]` | CLI defaults |
| `[jig.audit]` | Audit system settings |
| `[jig.graph]` | Graph generation settings |

Third-party extensions SHOULD use `[jig.x.*]` namespace.

---

## Consequences

### Benefits

- **Zero-config default** — Works immediately with sensible defaults
- **Single source of truth** — One config file, no inheritance complexity
- **Python ecosystem aligned** — TOML format, pyproject.toml support
- **Explicit and predictable** — No magic, no surprises
- **Forward compatible** — Schema versioning enables migrations
- **Clear errors** — Invalid config fails fast with actionable messages

### Trade-offs

- **No cascading config** — Can't share settings across monorepo projects
- **No environment interpolation** — No `${VAR}` in config values
- **TOML learning curve** — Users unfamiliar with TOML must learn syntax
- **Separate from bricks.yaml** — Two files to maintain (config + bricks)

### Mitigations

- **Monorepo:** Each subproject has its own `jig.toml`
- **Environment needs:** Use environment variable overrides
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
[jig]
version = "1"

[jig.paths]
tests = "tests"
```

No configuration required for standard projects. Full control available when needed. No surprises either way.

---

_Configure only what differs. `jigy align` works either way._
