# Slice 0: Bootstrap - Scope of Work

**Project:** JIG (Jig Intent Graph)
**Phase:** Slice 0 - Bootstrap Infrastructure
**Duration:** Week 1 (3-5 days)
**Status:** Ready to Start
**Date:** 2025-11-18

---

## Executive Summary

This document defines the scope of work for **Slice 0: Bootstrap**, the foundational phase of JIG development. The goal is to create minimal infrastructure that enables us to start dogfooding JIG immediately—building JIG using JIG principles from Day 1.

**Success Criteria:** By the end of this slice, we can manually create OSTC nodes, validate their structure, and initialize the JIG graph for the JIG project itself.

---

## 1. Objectives

### Primary Objectives
1. **Initialize project structure** - Set up Python package with subsystem boundaries
2. **Implement `jigy init`** - Create `jig/` directory structure for a project
3. **Implement `jigy node create`** - Generate OSTC nodes from templates
4. **Implement `jigy validate`** - Basic YAML frontmatter and reference validation
5. **Start dogfooding** - Create initial OSTC nodes for JIG itself

### Secondary Objectives
- Establish development tooling (pytest, ruff, mypy)
- Set up CI/CD skeleton (GitHub Actions)
- Document initial design decisions in Delta

---

## 2. Deliverables

### 2.1 Code Deliverables

#### Core Infrastructure
- [ ] `src/jig/__init__.py` - Package initialization
- [ ] `src/jig/core/config.py` - Configuration loader for `jig.toml`
- [ ] `src/jig/core/parser.py` - YAML frontmatter + Markdown parser
- [ ] `src/jig/core/validator.py` - Schema validation for OSTC nodes
- [ ] `src/jig/utils/io.py` - File I/O utilities
- [ ] `src/jig/utils/yaml_utils.py` - YAML helper functions

#### CLI Commands
- [ ] `src/jig/cli/main.py` - CLI entry point (`jigy` command)
- [ ] `src/jig/cli/init.py` - `jigy init` command implementation
- [ ] `src/jig/cli/node.py` - `jigy node create` command implementation
- [ ] `src/jig/cli/validate.py` - `jigy validate` command implementation

#### Configuration & Templates
- [ ] `pyproject.toml` - Python package configuration (PEP 621)
- [ ] `jig.toml` - JIG's own configuration (dogfooding)
- [ ] `templates/outcome_template.md` - Template for Outcome nodes
- [ ] `templates/specification_template.md` - Template for Specification nodes
- [ ] `templates/test_template.md` - Template for Test nodes
- [ ] `templates/constraint_template.md` - Template for Constraint nodes

#### Testing
- [ ] `tests/unit/test_config.py` - Config loader tests (uses `@jig` decorator)
- [ ] `tests/unit/test_parser.py` - Parser tests (uses `@jig` decorator)
- [ ] `tests/unit/test_validator.py` - Validator tests (uses `@jig` decorator)
- [ ] `tests/integration/test_init_command.py` - `jigy init` integration test (uses `@jig` decorator)
- [ ] `tests/integration/test_node_create.py` - `jigy node create` integration test (uses `@jig` decorator)
- [ ] `tests/integration/test_validate_command.py` - `jigy validate` integration test (uses `@jig` decorator)

#### Documentation
- [ ] `README.md` - Project README with quick start
- [ ] `jig/deltas/active/bootstrap/PLAN_bootstrap.md` - Delta documenting this slice
- [ ] `docs/architecture/DATA_FORMATS.md` - YAML schema documentation

### 2.2 Dogfooding Deliverables

#### JIG's Own Intent Graph
- [ ] `jig/` directory structure created via `jigy init`
- [ ] `jig.toml` - JIG's configuration file
- [ ] `jig/outcomes/O-JIG-001.md` - "JIG tools run in <1 second"
- [ ] `jig/outcomes/O-JIG-002.md` - "JIG uses simple text formats"
- [ ] `jig/outcomes/O-JIG-003.md` - "JIG is composable (pipes work)"
- [ ] `jig/outcomes/O-JIG-004.md` - "JIG requires no external services"
- [ ] `jig/outcomes/O-JIG-005.md` - "JIG demonstrates modularity >0.7"
- [ ] `jig/specifications/S-JIG-001.md` - "Marker extraction <1s for 1000 files"
- [ ] `jig/specifications/S-JIG-002.md` - "OSTC nodes use YAML + Markdown"
- [ ] `jig/specifications/S-JIG-003.md` - "Commands output valid YAML"
- [ ] `jig/specifications/S-JIG-004.md` - "Subsystems export <5 interfaces"
- [ ] `jig/graph-index.yaml` - Master graph index
- [ ] `jig/subsystems.yaml` - Subsystem definitions

---

## 3. Technical Specifications

### 3.1 Command Specifications

#### `jigy init`

**Purpose:** Initialize JIG structure in a project.

**Usage:**
```bash
jigy init [--path PATH]
```

**Behavior:**
1. Create `jig/` directory structure:
   ```
   jig/
   ├── outcomes/
   ├── specifications/
   ├── constraints/
   ├── graph-index.yaml
   └── subsystems.yaml
   ```
2. Create `jig.toml` configuration file with defaults
3. Initialize `graph-index.yaml` with empty graph
4. Initialize `subsystems.yaml` with empty subsystems
5. Exit with success message

**Note:** Tests are NOT stored in `jig/tests/`. Instead, test files use the `@jig` decorator to link to OSTC test nodes.

**Exit Codes:**
- `0` - Success
- `1` - Directory already exists (error)
- `2` - Permission denied

**Tests:**
- Creates all directories (except tests directory)
- Creates configuration files
- Idempotency check (fails if already initialized)
- Works with custom path

---

#### `jigy node create`

**Purpose:** Create a new OSTC node from template.

**Usage:**
```bash
jigy node create --type TYPE --id ID --title TITLE [--subsystem SUBSYSTEM]
```

**Arguments:**
- `--type` (required): `outcome`, `specification`, `test`, `constraint`
- `--id` (required): Node ID (e.g., `O-JIG-001`, `S-AUTH-042`)
- `--title` (required): Human-readable title
- `--subsystem` (optional): Subsystem name

**Behavior:**
1. Validate ID format: `[OSTC]-[A-Z0-9]+-[0-9]{3}`
2. Load appropriate template from `templates/`
3. Substitute placeholders: `{id}`, `{title}`, `{subsystem}`, `{date}`
4. Write file to `jig/{type}s/{id}.md`
5. Update `graph-index.yaml` with new node
6. Print success message with file path

**Exit Codes:**
- `0` - Success
- `1` - Invalid ID format
- `2` - File already exists
- `3` - JIG not initialized (no `jig/` directory)

**Tests:**
- Creates valid node file
- Updates graph index
- Validates ID format
- Handles duplicate IDs
- Template substitution works correctly

---

#### `jigy validate`

**Purpose:** Validate OSTC nodes and graph consistency.

**Usage:**
```bash
jigy validate [--check-all] [--verbose]
```

**Behavior:**
1. Load all OSTC node files from `jig/`
2. For each node:
   - Parse YAML frontmatter
   - Validate required fields: `id`, `type`, `title`
   - Validate ID format matches type
   - Check for duplicate IDs
3. Validate graph-index.yaml:
   - All referenced nodes exist
   - No orphaned references
4. Report errors and warnings
5. Exit with code 0 if valid, 1 if errors found

**Validation Rules:**
- **Required fields:** `id`, `type`, `title`
- **Optional fields:** `subsystem`, `status`, `created`, `updated`
- **ID format:** `[OSTC]-[A-Z0-9]+-[0-9]{3}`
- **Type values:** `outcome`, `specification`, `test`, `constraint`

**Output Format:**
```
Validating JIG graph...

✓ jig/outcomes/O-JIG-001.md
✓ jig/specifications/S-JIG-001.md
✗ jig/specifications/S-JIG-002.md
  - Missing required field: title
  - Invalid ID format: S_JIG_002

Graph Index:
✓ All 47 nodes referenced in graph-index.yaml exist
⚠ Warning: 3 nodes not referenced in graph

Summary: 45/47 nodes valid
```

**Exit Codes:**
- `0` - All validations passed
- `1` - Validation errors found

**Tests:**
- Detects missing required fields
- Detects invalid ID formats
- Detects duplicate IDs
- Validates graph consistency
- Performance: <1s for 1000 nodes

---

### 3.2 Data Format Specifications

#### OSTC Node File Format

**File:** `jig/{type}s/{id}.md`

**Format:** YAML frontmatter + Markdown body

**Example:**
```markdown
---
id: S-JIG-001
type: specification
title: "Marker extraction runs in <1s for 1000 files"
subsystem: core
status: draft
created: 2025-11-18
updated: 2025-11-18
---

# Specification: Marker extraction runs in <1s for 1000 files

The extractor MUST process 1000 Delta files in under 1 second.

## Rationale
Fast feedback enables developers to harvest frequently without friction.

## Implementation
- Use ripgrep for file scanning
- Regex for marker parsing
- Parallel processing for large repos

## References
- Implements: [[O-JIG-001]]
- Tested by: [[T-JIG-005]]
```

**YAML Schema:**
```yaml
id: string (required, pattern: [OSTC]-[A-Z0-9]+-[0-9]{3})
type: enum (required, values: outcome|specification|test|constraint)
title: string (required, 1-200 chars)
subsystem: string (optional)
status: enum (optional, values: draft|active|deprecated)
created: date (optional, ISO 8601)
updated: date (optional, ISO 8601)
```

---

#### Configuration File Format

**File:** `jig.toml`

**Format:** TOML

**Example:**
```toml
[project]
name = "jig"
version = "0.1.0"

[paths]
intent_dir = "jig"
delta_dir = "jig/deltas"
templates_dir = "templates"

[validation]
require_subsystems = false
strict_id_format = true

[tools]
extractor = "ripgrep"
```

**Schema:**
```toml
[project]
name = string (required)
version = string (optional)

[paths]
intent_dir = string (default: "jig")
delta_dir = string (default: "jig/deltas")
templates_dir = string (default: "templates")

[validation]
require_subsystems = boolean (default: false)
strict_id_format = boolean (default: true)

[tools]
extractor = string (default: "ripgrep")
```

---

#### Graph Index Format

**File:** `jig/graph-index.yaml`

**Purpose:** Master index of all OSTC nodes and relationships.

**Example:**
```yaml
version: 1.0
updated: 2025-11-18T10:30:00Z

nodes:
  - id: O-JIG-001
    type: outcome
    title: "JIG tools run in <1 second"
    file: outcomes/O-JIG-001.md
    subsystem: null

  - id: S-JIG-001
    type: specification
    title: "Marker extraction <1s for 1000 files"
    file: specifications/S-JIG-001.md
    subsystem: core

edges:
  - from: S-JIG-001
    to: O-JIG-001
    type: implements
```

---

### 3.3 Template Specifications

#### Outcome Template

**File:** `templates/outcome_template.md`

```markdown
---
id: {id}
type: outcome
title: "{title}"
subsystem: {subsystem}
status: draft
created: {date}
updated: {date}
---

# Outcome: {title}

## Description
[Describe the desired business outcome]

## Success Metrics
- [ ] Metric 1
- [ ] Metric 2

## Related Specifications
- [[S-XXX-001]] - [Specification title]

## Status
Current status: Draft

## History
- {date}: Created
```

#### Specification Template

**File:** `templates/specification_template.md`

```markdown
---
id: {id}
type: specification
title: "{title}"
subsystem: {subsystem}
status: draft
created: {date}
updated: {date}
---

# Specification: {title}

## Summary
[One-paragraph summary of this specification]

## Requirements
### Functional Requirements
- MUST: [Requirement]
- SHOULD: [Requirement]
- MAY: [Requirement]

### Non-Functional Requirements
- Performance: [Requirement]
- Security: [Requirement]
- Usability: [Requirement]

## Rationale
[Why this specification exists]

## Implementation Notes
[Technical guidance for implementers]

## References
- Implements: [[O-XXX-001]]
- Tested by: [[T-XXX-001]]
- Related: [[S-XXX-002]]

## History
- {date}: Created
```

---

## 4. Implementation Plan

### 4.1 Task Breakdown

**Day 1: Project Setup**
1. Create project structure (`src/jig/`, `tests/`, `docs/`)
2. Write `pyproject.toml` with dependencies
3. Set up virtual environment and install dependencies
4. Configure development tools (ruff, mypy, pytest)
5. Write initial `README.md`

**Day 2: Core Infrastructure**
6. Implement `src/jig/utils/io.py` (file operations)
7. Implement `src/jig/utils/yaml_utils.py` (YAML helpers)
8. Implement `src/jig/core/config.py` (config loader)
9. Implement `src/jig/core/parser.py` (YAML frontmatter parser)
10. Write unit tests for utils and core modules

**Day 3: CLI Commands (Part 1)**
11. Implement `src/jig/cli/main.py` (Click CLI setup)
12. Implement `src/jig/cli/init.py` (`jigy init`)
13. Implement `src/jig/cli/node.py` (`jigy node create`)
14. Create templates (`outcome_template.md`, `specification_template.md`)
15. Write integration tests for `init` and `node create`

**Day 4: Validation & Testing**
16. Implement `src/jig/core/validator.py` (OSTC validation)
17. Implement `src/jig/cli/validate.py` (`jigy validate`)
18. Write comprehensive tests for validator
19. Write integration test for `validate` command
20. Achieve >80% test coverage

**Day 5: Dogfooding & Documentation**
21. Run `jigy init` in JIG project root
22. Create `jig.toml` for JIG
23. Create initial OSTC nodes (O-JIG-001 through O-JIG-005)
24. Create specifications (S-JIG-001 through S-JIG-004)
25. Write `jig/deltas/active/bootstrap/PLAN_bootstrap.md`
26. Document data formats in `docs/architecture/DATA_FORMATS.md`
27. Document `@jig` decorator usage for tests
28. Run `jigy validate` on JIG's own graph
29. Tag release: `v0.1.0-bootstrap`

---

### 4.2 Dependencies

**External Dependencies (Python packages):**
- `click` (>=8.1.0) - CLI framework
- `pyyaml` (>=6.0) - YAML parsing
- `python-frontmatter` (>=1.0.0) - Markdown frontmatter parsing
- `toml` (>=0.10.0) - TOML configuration parsing

**Development Dependencies:**
- `pytest` (>=7.4.0) - Testing framework
- `pytest-cov` (>=4.1.0) - Coverage reporting
- `ruff` (>=0.1.0) - Linting and formatting
- `mypy` (>=1.5.0) - Type checking

**System Dependencies:**
- Python 3.11+
- Git (for version control)

---

### 4.3 Testing Strategy

#### Unit Tests
- `test_config.py` - Configuration loading, validation
- `test_parser.py` - YAML frontmatter parsing
- `test_validator.py` - Schema validation, ID format validation
- `test_io.py` - File operations
- `test_yaml_utils.py` - YAML helper functions

**Coverage Target:** >80% for all core modules

#### Integration Tests
- `test_init_command.py` - Full `jigy init` workflow
- `test_node_create.py` - Full `jigy node create` workflow
- `test_validate_command.py` - Full `jigy validate` workflow

**Coverage Target:** >70% for CLI modules

#### Manual Testing
- Run all commands on JIG project itself (dogfooding)
- Verify templates generate correct output
- Check error messages are clear and actionable

---

### 4.4 Performance Targets

| Operation | Target | Rationale |
|-----------|--------|-----------|
| `jigy init` | <500ms | One-time setup, should be instant |
| `jigy node create` | <200ms | Frequent operation, must be fast |
| `jigy validate` | <1s | Must validate quickly for 1000 nodes |
| Template loading | <50ms | Should not add noticeable delay |

---

## 5. Success Criteria

### 5.1 Functional Success

- [ ] `jigy init` creates correct directory structure
- [ ] `jigy node create` generates valid OSTC nodes from templates
- [ ] `jigy validate` correctly validates YAML schema
- [ ] `jigy validate` detects duplicate IDs
- [ ] `jigy validate` detects missing required fields
- [ ] All commands have `--help` documentation
- [ ] Error messages are clear and actionable

### 5.2 Quality Success

- [ ] Test coverage >80% overall
- [ ] All tests pass (`pytest`)
- [ ] No type errors (`mypy`)
- [ ] No linting errors (`ruff check`)
- [ ] Code formatted (`ruff format`)

### 5.3 Performance Success

- [ ] `jigy init` completes in <500ms
- [ ] `jigy node create` completes in <200ms
- [ ] `jigy validate` completes in <1s for 100 nodes

### 5.4 Dogfooding Success

- [ ] JIG project has `jig/` directory (not hidden)
- [ ] Created 5+ Outcome nodes for JIG
- [ ] Created 4+ Specification nodes for JIG
- [ ] `jigy validate` passes on JIG's own graph
- [ ] Delta written: `jig/deltas/active/bootstrap/PLAN_bootstrap.md`
- [ ] All design decisions captured in Delta
- [ ] `@jig` decorator documented and ready for use

---

## 6. Risks & Mitigations

### 6.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| YAML parsing errors with complex frontmatter | Medium | High | Use battle-tested libraries (python-frontmatter), write extensive tests |
| Template substitution bugs | Low | Medium | Simple string replacement, test edge cases |
| File I/O permission issues | Low | High | Graceful error handling, clear error messages |
| Performance degrades with large graphs | Medium | Medium | Benchmark early, optimize if needed (deferred to later slices) |

### 6.2 Process Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep (adding features) | High | Medium | Strict adherence to deliverables, defer features to later slices |
| Over-engineering early infrastructure | Medium | Medium | YAGNI principle, only build what's needed now |
| Insufficient dogfooding | Low | High | Mandatory use of JIG on JIG from Day 1 |

---

## 7. Out of Scope

The following items are **explicitly excluded** from Slice 0 and deferred to later slices:

- **Marker extraction** (Slice 1)
- **Harvest reports** (Slice 1)
- **LLM synthesis** (Slice 4)
- **Git integration** (Slice 8)
- **Delta lifecycle management** (Slice 6)
- **Decomposability analysis** (Slice 7)
- **Graph visualization** (deferred, possible plugin)
- **Advanced validation** (reference checking, constraint validation)
- **OSTC node editing** (use text editor)
- **OSTC node deletion** (manual for now)
- **Search/query capabilities** (use grep)

---

## 8. Definition of Done

Slice 0 is complete when:

1. **All deliverables shipped** (see Section 2)
2. **All tests pass** with >80% coverage (tests use `@jig` decorator)
3. **Dogfooding successful** - JIG has its own `jig/` directory with 5+ nodes
4. **Performance targets met** (see Section 4.4)
5. **Documentation complete:**
   - README.md updated
   - DATA_FORMATS.md written
   - PLAN_bootstrap.md Delta written
   - `@jig` decorator usage documented
6. **Code quality gates passed:**
   - `pytest` - all tests pass
   - `ruff check` - no linting errors
   - `mypy` - no type errors
7. **Tagged release:** `v0.1.0-bootstrap`
8. **Ready for Slice 1** - Can begin marker extraction work

---

## 9. Next Steps (After Slice 0)

**Immediate Next Slice:** Slice 1 - Deterministic Extraction

**Handoff Requirements:**
- Working `jigy` CLI installed and in PATH
- JIG project has validated `jig/` structure
- Delta template exists for Slice 1 planning
- Development environment set up for next developer (if applicable)
- `@jig` decorator ready for linking tests to OSTC test nodes

**Slice 1 Preview:**
- Implement marker extraction from Deltas
- Generate harvest reports (YAML)
- Extract all marker types: VIB, OSTC, DISCOVERY, DECISION, LEARNED
- Target: <1s for 1000 files

---

## 10. Approval & Sign-off

**Scope Approved By:** [Name/Date]
**Ready to Start:** YES / NO
**Estimated Effort:** 3-5 days (1 developer, part-time)
**Target Completion:** [Date]

---

## Appendix A: Example Workflows

### Workflow 1: Initialize JIG for a New Project

```bash
# Create new project
mkdir my-project
cd my-project
git init

# Initialize JIG
jigy init

# Verify structure
ls -la jig/
# Output:
# jig/
# ├── outcomes/
# ├── specifications/
# ├── constraints/
# ├── graph-index.yaml
# └── subsystems.yaml

# Validate (should pass with empty graph)
jigy validate
# Output: ✓ Graph is valid (0 nodes)
```

### Workflow 2: Create OSTC Nodes

```bash
# Create an Outcome
jigy node create --type outcome \
  --id O-AUTH-001 \
  --title "Users can authenticate in <2s" \
  --subsystem auth

# Output: ✓ Created jig/outcomes/O-AUTH-001.md

# Create a Specification
jigy node create --type specification \
  --id S-AUTH-001 \
  --title "JWT token expiry is 24 hours" \
  --subsystem auth

# Output: ✓ Created jig/specifications/S-AUTH-001.md

# Validate
jigy validate
# Output:
# ✓ jig/outcomes/O-AUTH-001.md
# ✓ jig/specifications/S-AUTH-001.md
# Summary: 2/2 nodes valid
```

### Workflow 3: Dogfooding JIG on JIG

```bash
# Navigate to JIG project root
cd /path/to/jig

# Initialize JIG's own graph
jigy init

# Create initial Outcomes
jigy node create --type outcome --id O-JIG-001 \
  --title "JIG tools run in <1 second for most operations"

jigy node create --type outcome --id O-JIG-002 \
  --title "JIG uses simple text formats (YAML + Markdown)"

# Create initial Specifications
jigy node create --type specification --id S-JIG-001 \
  --title "Marker extraction processes 1000 files in <1s" \
  --subsystem core

jigy node create --type specification --id S-JIG-002 \
  --title "OSTC nodes use YAML frontmatter + Markdown" \
  --subsystem core

# Validate JIG's own graph
jigy validate --check-all

# Output:
# ✓ jig/outcomes/O-JIG-001.md
# ✓ jig/outcomes/O-JIG-002.md
# ✓ jig/specifications/S-JIG-001.md
# ✓ jig/specifications/S-JIG-002.md
# Summary: 4/4 nodes valid
```

---

## Appendix B: File Structure (Post-Bootstrap)

```
jig/
├── jig/                            # JIG's own Intent Graph (visible, not hidden)
│   ├── outcomes/
│   │   ├── O-JIG-001.md
│   │   ├── O-JIG-002.md
│   │   ├── O-JIG-003.md
│   │   ├── O-JIG-004.md
│   │   └── O-JIG-005.md
│   ├── specifications/
│   │   ├── S-JIG-001.md
│   │   ├── S-JIG-002.md
│   │   ├── S-JIG-003.md
│   │   └── S-JIG-004.md
│   ├── constraints/
│   ├── graph-index.yaml
│   └── subsystems.yaml
│
├── jig/deltas/                     # JIG's own Deltas
│   └── active/
│       └── bootstrap/
│           └── PLAN_bootstrap.md
│
├── src/jig/                        # Source code
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── init.py
│   │   ├── node.py
│   │   └── validate.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── parser.py
│   │   └── validator.py
│   └── utils/
│       ├── __init__.py
│       ├── io.py
│       └── yaml_utils.py
│
├── tests/
│   ├── unit/
│   │   ├── test_config.py
│   │   ├── test_parser.py
│   │   ├── test_validator.py
│   │   ├── test_io.py
│   │   └── test_yaml_utils.py
│   └── integration/
│       ├── test_init_command.py
│       ├── test_node_create.py
│       └── test_validate_command.py
│
├── templates/
│   ├── outcome_template.md
│   ├── specification_template.md
│   ├── test_template.md
│   └── constraint_template.md
│
├── docs/
│   ├── architecture/
│   │   └── DATA_FORMATS.md
│   └── wip/
│       ├── JIG_DEVELOPMENT_STRATEGY.md
│       └── SLICE_0_BOOTSTRAP_SCOPE.md
│
├── pyproject.toml
├── jig.toml                        # JIG configuration (not hidden)
├── README.md
└── .gitignore
```

**Notes:**
- `jig/` directory is **visible** (not `.jig/`) - makes outcomes and specs easier to read
- No `jig/tests/` folder - tests use `@jig` decorator to link to OSTC test nodes
- Command is consistently `jigy` throughout

---

**Document Version:** 1.1
**Last Updated:** 2025-11-18
**Status:** Ready for Implementation
