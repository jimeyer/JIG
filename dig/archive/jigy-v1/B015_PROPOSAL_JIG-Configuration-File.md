---
title: "B015: PROPOSAL - JIG Configuration File System"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1765378531
created_human: "2025-12-10 08:55 CST"
parent: null
children: ['[[B016_PLAN_JIG-Configuration-MVP]]']
---
# B015: PROPOSAL - JIG Configuration File System

**Date:** 2025-12-10
**Status:** Proposal
**Author:** Claude (with human direction)
**References:** J017 (JIG Concept v9), A001 (Core Artifacts Contract)

---

## Problem Statement

JIG currently has hardcoded paths and assumptions:
- Test directory assumed to be `test/` or `tests/`
- Specification directory assumed to be `jig/specifications/`
- Source directory assumed to be `src/`
- No way to customize validation behavior
- No way to exclude files/directories from analysis

**User request:** The test directory must be configurable. Other JIG settings should also be reviewed for configurability.

---

## Proposal: `jig.toml` Configuration File

### Why TOML?

| Format | Pros | Cons |
|--------|------|------|
| **TOML** | Python standard (pyproject.toml), clear sections, no type coercion issues, good tooling | Different from existing YAML in JIG |
| **YAML** | Already used (bricks.yaml), familiar to JIG users | Type coercion gotchas (`yes`→`true`), multiline strings awkward |
| **JSON** | Universal, strict | Verbose, no comments |
| **INI** | Simple | Too limited for nested config |

**Recommendation: TOML**

Rationale:
1. **Python ecosystem standard** - `pyproject.toml` is universal
2. **Configuration-optimized** - Designed for config, not data interchange
3. **No YAML gotchas** - `on: true` vs `on: "true"` issues don't exist
4. **Clear section syntax** - `[section.subsection]` is unambiguous
5. **Comments supported** - `# inline documentation`
6. **Excellent tooling** - `tomllib` in Python 3.11+ stdlib

The bricks.yaml file is *data* (list of brick definitions), not configuration. TOML is better suited for the *configuration* use case.

---

## Configuration Schema

### File Location

**Primary:** `jig.toml` in project root (alongside `pyproject.toml`)

**Fallback search order:**
1. `jig.toml`
2. `.jig.toml` (hidden file alternative)
3. `jig/config.toml` (inside jig directory)
4. `pyproject.toml` under `[tool.jig]` section

### Full Configuration Example

```toml
# jig.toml - JIG Configuration File
# See: https://jig.example.com/docs/configuration

[jig]
# Project-level settings
version = "1"  # Config schema version

[jig.paths]
# Directory containing source code
source = "src"

# Directory containing tests
tests = "test"

# Directory containing JIG artifacts
jig_root = "jig"

# Specification files location (relative to jig_root)
specifications = "specifications"

# Outcome files location (relative to jig_root)
outcomes = "outcomes"

# Brick definitions file (relative to jig_root)
bricks = "bricks.yaml"

# Generated graph files location (relative to jig_root)
generated = "generated"

[jig.discovery]
# Glob patterns for source files (relative to source directory)
source_include = ["**/*.py"]
source_exclude = ["**/__pycache__/**", "**/.*"]

# Glob patterns for test files (relative to tests directory)
test_include = ["**/test_*.py", "**/*_test.py"]
test_exclude = ["**/__pycache__/**", "**/conftest.py"]

# Module prefix to strip from function IDs
# e.g., "src.jig" → F-validation.bricks.validate becomes F-validation.bricks.validate
#       without stripping, it would be F-src.jig.validation.bricks.validate
module_prefix_strip = "src"

[jig.validation]
# Enable/disable specific validation rules
[jig.validation.bricks]
enabled = true
strict_id_format = true      # Require B-kebab-case format
require_layer_field = true   # Require layer field on all bricks
validate_layer_constraints = true
detect_cycles = true

[jig.validation.specifications]
enabled = true
require_frontmatter = true   # Require YAML frontmatter in spec files
validate_references = true   # Check that referenced specs exist

[jig.validation.implementation]
enabled = true
warn_orphan_functions = false  # Warn on functions with no @jig.implements
warn_missing_docstrings = false

[jig.validation.verification]
enabled = true
warn_low_coverage = true
coverage_threshold = 80  # Warn if spec coverage below this %

[jig.cli]
# CLI behavior defaults
color = "auto"  # "auto", "always", "never"
verbose = false
quiet = false

[jig.layers]
# Layer-specific settings
default_layer = 0  # Default layer for new bricks without explicit layer
allow_layer_0_interdeps = true  # Allow layer 0 bricks to depend on each other

[jig.graph]
# Graph generation settings
include_private_functions = false  # Include _private and __dunder__ functions
include_nested_functions = false   # Include functions defined inside other functions
call_graph_depth = -1  # -1 = unlimited, or positive int for max depth
```

### Minimal Configuration Example

For most projects, only a few settings need customization:

```toml
# jig.toml - Minimal example

[jig.paths]
source = "src"
tests = "tests"  # Changed from default "test"
```

### pyproject.toml Integration

Configuration can also live in `pyproject.toml`:

```toml
# pyproject.toml

[tool.jig]
# All settings go under [tool.jig] instead of [jig]

[tool.jig.paths]
source = "src"
tests = "tests"
```

---

## Configuration Categories

### 1. Path Configuration (Required Feature)

**Addresses user's explicit requirement for configurable test directory.**

| Setting | Default | Description |
|---------|---------|-------------|
| `paths.source` | `"src"` | Source code directory |
| `paths.tests` | `"test"` | Test directory |
| `paths.jig_root` | `"jig"` | JIG artifacts directory |
| `paths.specifications` | `"specifications"` | Spec files (relative to jig_root) |
| `paths.outcomes` | `"outcomes"` | Outcome files (relative to jig_root) |
| `paths.bricks` | `"bricks.yaml"` | Bricks file (relative to jig_root) |
| `paths.generated` | `"generated"` | Generated graphs (relative to jig_root) |

### 2. Discovery Configuration

Controls how JIG finds source and test files.

| Setting | Default | Description |
|---------|---------|-------------|
| `discovery.source_include` | `["**/*.py"]` | Glob patterns for source files |
| `discovery.source_exclude` | `["**/__pycache__/**"]` | Patterns to exclude from source |
| `discovery.test_include` | `["**/test_*.py", "**/*_test.py"]` | Glob patterns for test files |
| `discovery.test_exclude` | `["**/__pycache__/**"]` | Patterns to exclude from tests |
| `discovery.module_prefix_strip` | `""` | Module prefix to remove from IDs |

### 3. Validation Configuration

Controls validation strictness.

| Setting | Default | Description |
|---------|---------|-------------|
| `validation.bricks.enabled` | `true` | Enable brick validation |
| `validation.bricks.strict_id_format` | `true` | Require B-kebab-case |
| `validation.bricks.require_layer_field` | `true` | Require layer on all bricks |
| `validation.specifications.enabled` | `true` | Enable spec validation |
| `validation.specifications.require_frontmatter` | `true` | Require YAML frontmatter |

### 4. CLI Configuration

Controls CLI defaults (can be overridden by flags).

| Setting | Default | Description |
|---------|---------|-------------|
| `cli.color` | `"auto"` | Color output mode |
| `cli.verbose` | `false` | Default verbose output |
| `cli.quiet` | `false` | Default quiet output |

### 5. Layer Configuration

Controls layer behavior.

| Setting | Default | Description |
|---------|---------|-------------|
| `layers.default_layer` | `0` | Default layer for bricks without explicit layer |
| `layers.allow_layer_0_interdeps` | `true` | Allow layer 0 bricks to depend on each other |

### 6. Graph Configuration

Controls graph generation behavior.

| Setting | Default | Description |
|---------|---------|-------------|
| `graph.include_private_functions` | `false` | Include `_private` functions |
| `graph.include_nested_functions` | `false` | Include nested function definitions |
| `graph.call_graph_depth` | `-1` | Maximum call graph traversal depth |

---

## Implementation Plan

### Phase 1: Core Configuration (MVP)

**Specifications to create:**
- S-050: Configuration file discovery and loading
- S-051: Path configuration (source, tests, jig_root)
- S-052: Default value fallbacks

**Implementation:**
1. Add `jig/config.py` module for configuration loading
2. Use `tomllib` (Python 3.11+) or `tomli` (fallback) for parsing
3. Implement config discovery (jig.toml → .jig.toml → pyproject.toml)
4. Wire paths into existing commands

**Acceptance criteria:**
- `jigy` commands respect `paths.tests` setting
- Missing config file uses sensible defaults
- Invalid config produces clear error messages

### Phase 2: Discovery Configuration

**Specifications to create:**
- S-053: Source file discovery patterns
- S-054: Test file discovery patterns
- S-055: Module prefix stripping

### Phase 3: Validation Configuration

**Specifications to create:**
- S-056: Configurable validation rules
- S-057: Validation strictness levels

### Phase 4: CLI and Advanced

**Specifications to create:**
- S-058: CLI default configuration
- S-059: Graph generation configuration

---

## API Design

### Configuration Loading

```python
from jig.config import load_config, JigConfig

# Load from default locations
config: JigConfig = load_config()

# Load from specific file
config = load_config(path="custom/jig.toml")

# Access settings
print(config.paths.tests)  # "test"
print(config.paths.source)  # "src"
print(config.validation.bricks.enabled)  # True
```

### Configuration Class Structure

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class PathsConfig:
    source: str = "src"
    tests: str = "test"
    jig_root: str = "jig"
    specifications: str = "specifications"
    outcomes: str = "outcomes"
    bricks: str = "bricks.yaml"
    generated: str = "generated"

@dataclass
class ValidationBricksConfig:
    enabled: bool = True
    strict_id_format: bool = True
    require_layer_field: bool = True
    validate_layer_constraints: bool = True
    detect_cycles: bool = True

@dataclass
class JigConfig:
    version: str = "1"
    paths: PathsConfig = field(default_factory=PathsConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    cli: CliConfig = field(default_factory=CliConfig)
    # ...
```

---

## Migration Path

### For Existing Projects

1. JIG continues to work without `jig.toml` (defaults apply)
2. Users can add `jig.toml` incrementally
3. No breaking changes to existing behavior

### Example Migration

**Before (hardcoded):**
```
project/
├── src/
├── test/           # Hardcoded assumption
├── jig/
│   ├── bricks.yaml
│   └── specifications/
```

**After (configurable):**
```
project/
├── jig.toml        # New: configuration file
├── src/
├── tests/          # Now configurable!
├── jig/
│   ├── bricks.yaml
│   └── specifications/
```

```toml
# jig.toml
[jig.paths]
tests = "tests"  # Override the default "test"
```

---

## Alternatives Considered

### Alternative 1: YAML Configuration

```yaml
# jig.yaml
jig:
  paths:
    source: src
    tests: tests
  validation:
    bricks:
      enabled: true
```

**Rejected because:**
- YAML type coercion issues (`on: true` vs `on: "true"`)
- Less clear section boundaries
- Though consistent with bricks.yaml, config has different needs than data

### Alternative 2: JSON Configuration

```json
{
  "jig": {
    "paths": {
      "source": "src",
      "tests": "tests"
    }
  }
}
```

**Rejected because:**
- No comments
- Verbose syntax
- Not idiomatic for Python projects

### Alternative 3: Python Configuration

```python
# jig_config.py
config = {
    "paths": {
        "source": "src",
        "tests": "tests",
    }
}
```

**Rejected because:**
- Security concerns (arbitrary code execution)
- Harder to validate schema
- Not declarative

### Alternative 4: Environment Variables Only

```bash
JIG_TESTS_DIR=tests jigy validate
```

**Rejected as primary config because:**
- Hard to version control
- Verbose for multiple settings
- No project-level defaults

**But:** Environment variables should override file config for CI/CD flexibility.

---

## Environment Variable Override

All config values can be overridden by environment variables:

```bash
# Pattern: JIG_SECTION_KEY=value
JIG_PATHS_TESTS=tests jigy validate
JIG_VALIDATION_BRICKS_ENABLED=false jigy validate
```

**Precedence (highest to lowest):**
1. CLI flags (`--tests-dir tests`)
2. Environment variables (`JIG_PATHS_TESTS=tests`)
3. Config file (`jig.toml`)
4. Default values

---

## CLI Integration

### New `jigy config` Command

```bash
# Show current configuration
jigy config show

# Show specific setting
jigy config get paths.tests

# Validate configuration file
jigy config validate

# Initialize config file with defaults
jigy config init
```

### Flag Overrides

```bash
# Override test directory for single command
jigy validate --tests-dir tests

# Override source directory
jigy impl rebuild --source-dir src
```

---

## Open Questions

1. **Should `jig.toml` be auto-created?**
   - Proposal: No. Work without config, create only when needed.

2. **Should we support multiple config files (base + overrides)?**
   - Proposal: No for v1. Keep it simple.

3. **Should validation config affect exit codes?**
   - Proposal: Yes. Disabled validations don't fail the build.

4. **How to handle config file in monorepos?**
   - Proposal: Search upward from current directory, stop at git root.

---

## Success Criteria

1. **Test directory configurable** (primary requirement)
2. **Zero-config default** - JIG works without config file
3. **Discoverable** - Config locations follow conventions
4. **Documented** - Clear reference for all options
5. **Type-safe** - Invalid config produces clear errors
6. **Extensible** - Easy to add new settings later

---

## Next Steps

1. **Review proposal** - Gather feedback on format choice and schema
2. **Create specifications** - S-050 through S-055 for Phase 1
3. **Implement MVP** - Path configuration only
4. **Iterate** - Add more config options based on user needs

---

## References

- [TOML Specification](https://toml.io/en/)
- [PEP 518 - pyproject.toml](https://peps.python.org/pep-0518/)
- J017: JIG Concept v9
- A001: Core Artifacts Contract
