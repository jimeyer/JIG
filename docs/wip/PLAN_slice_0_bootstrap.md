---
delta_type: plan
branch: bootstrap-slice-0
---

# PLAN: Slice 0 - Bootstrap Infrastructure

- **SCOPE:** docs/wip/SCOPE_SLICE_0_BOOTSTRAP.md
- **Start:** 2025-11-18
- **Owner:** Jim Meyer
- **Status:** Draft
- **Subsystem:** core

## Known Intent (Created Before Coding)

**Outcomes Created:**
- O-JIG-001: "JIG tools run in <1 second for most operations" (jig/outcomes/O-JIG-001.md)
- O-JIG-002: "JIG uses simple text formats (YAML + Markdown)" (jig/outcomes/O-JIG-002.md)
- O-JIG-003: "JIG is composable (pipes work)" (jig/outcomes/O-JIG-003.md)
- O-JIG-004: "JIG requires no external services" (jig/outcomes/O-JIG-004.md)
- O-JIG-005: "JIG demonstrates modularity >0.7" (jig/outcomes/O-JIG-005.md)

**Specifications Created:**
- S-JIG-001: "Marker extraction processes 1000 files in <1s" (jig/specifications/S-JIG-001.md)
- S-JIG-002: "OSTC nodes use YAML frontmatter + Markdown" (jig/specifications/S-JIG-002.md)
- S-JIG-003: "Commands output valid YAML" (jig/specifications/S-JIG-003.md)
- S-JIG-004: "Subsystems export <5 interfaces" (jig/specifications/S-JIG-004.md)

**Rationale:** These constraints are explicitly defined in SCOPE (Section 2.2). Creating them upfront enables O→S→TDD flow and dogfooding from Day 1.

## Work Unit Checklist
- [x] WU0: Create known Intent nodes (O/S) — done ☑
- [x] WU1: Project setup & infrastructure — tests ☑ / docs ☑ / reflect ☑
- [ ] WU2: Core utilities (io, yaml_utils) — tests ☐ / docs ☐ / reflect ☐
- [ ] WU3: Config loader & parser — tests ☐ / docs ☐ / reflect ☐
- [ ] WU4: `jigy init` command — tests ☐ / docs ☐ / reflect ☐
- [ ] WU5: Node templates — tests ☐ / docs ☐ / reflect ☐
- [ ] WU6: `jigy node create` command — tests ☐ / docs ☐ / reflect ☐
- [ ] WU7: OSTC validator — tests ☐ / docs ☐ / reflect ☐
- [ ] WU8: `jigy validate` command — tests ☐ / docs ☐ / reflect ☐
- [ ] WU9: Dogfooding - create JIG's own nodes — tests ☐ / docs ☐ / reflect ☐
- [ ] WU10: Documentation & release — tests ☐ / docs ☐ / reflect ☐

---

## Work Units

### Work Unit 0: Create Known Intent

**Goal:** Capture all known Outcomes and Specifications from SCOPE as Intent nodes before coding.

**Planned Effort:** 60m

**Acceptance Criteria:**
- All 5 Outcome nodes created in jig/outcomes/ with proper YAML frontmatter
- All 4 Specification nodes created in jig/specifications/ with proper YAML frontmatter
- Each O node has clear value proposition and success metrics
- Each S node has rationale, requirements, and links to parent O nodes
- `jig validate` passes (manual validation for bootstrap)
- Initial graph-index.yaml and subsystems.yaml created

**Implementation Notes:**
- Create directory structure: jig/outcomes/, jig/specifications/, jig/constraints/
- Follow OSTC node format from SCOPE Section 3.2
- Use ID pattern: O-JIG-NNN, S-JIG-NNN
- Link S nodes to O nodes via "implements" relationship
- Mark subsystem as "core" for all bootstrap nodes

**Created Nodes:**
- O-JIG-001.md - Performance outcome (<1s operations)
- O-JIG-002.md - Simple text formats outcome
- O-JIG-003.md - Composability outcome (Unix philosophy)
- O-JIG-004.md - No external services outcome
- O-JIG-005.md - Modularity outcome (>0.7 decomposability)
- S-JIG-001.md - Marker extraction performance spec
- S-JIG-002.md - OSTC node format spec
- S-JIG-003.md - YAML output format spec
- S-JIG-004.md - Subsystem interface limit spec

**Test Plan:**
- Manual validation: Read each file, verify format
- Check YAML frontmatter parses correctly
- Verify all required fields present (id, type, title)
- Confirm markdown content is clear and actionable

**Docs to Update:**
- jig/graph-index.yaml - Initialize with 9 nodes
- jig/subsystems.yaml - Define "core" subsystem

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [clarity] SCOPE clearly defined these constraints upfront
  - [process] Creating Intent nodes before code clarifies design goals
  - [format] YAML frontmatter + Markdown is clean and readable
- What could be better:
  - [tooling] Manual creation tedious - validates need for `jigy node create` command
- Discoveries:
  - [format] Including "History" section in nodes provides useful audit trail

**Links:**
- Commit: ad56a9532a2a5c2dcb2eaff0426cde6c00a1515d

**Human Validation:**
- Commands: `ls -la jig/outcomes/ jig/specifications/`, `cat jig/outcomes/O-JIG-001.md`
- Look for: 9 files created, proper YAML frontmatter, readable markdown

---

### Work Unit 1: Project Setup & Infrastructure

**Goal:** Initialize Python package structure with development tooling and dependencies.

**Planned Effort:** 60m

**Acceptance Criteria:**
- `pyproject.toml` created with PEP 621 format
- Dependencies installed: click, pyyaml, python-frontmatter, toml
- Dev dependencies installed: pytest, pytest-cov, ruff, mypy
- Virtual environment activated and working
- Directory structure: src/jig/, tests/, templates/, docs/
- Initial README.md with project overview and quick start
- All tools run successfully: `ruff check`, `mypy src/`, `pytest`

**Implementation Notes:**
- Python 3.11+ required (use pyproject.toml to enforce)
- Use Click for CLI framework (>= 8.1.0)
- Set up entry point: `jigy` → `jig.cli.main:cli`
- Configure ruff for linting and formatting
- Configure mypy for strict type checking
- Files to create:
  - `pyproject.toml` - Package metadata and dependencies
  - `src/jig/__init__.py` - Package initialization
  - `README.md` - Project introduction
  - `.gitignore` - Python, IDE, JIG-specific ignores

**Test Plan:**
- Unit: N/A (infrastructure setup)
- Integration: Verify tools run without errors
- Commands to test:
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install -e ".[dev]"
  ruff check src/
  mypy src/
  pytest
  ```

**Docs to Update:**
- README.md - Add installation instructions, quick start guide
- Document required Python version
- List key dependencies and their purpose

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [tools] pyproject.toml modern config format is clean and expressive
  - [process] Virtual environment setup smooth with Python 3.12
  - [tools] ruff and mypy strict configs work well together
- What could be better:
  - [scope] templates/ directory not created yet (deferred to WU5)
- Discoveries:
  - [tools] Python 3.12.10 available, exceeds 3.11+ requirement

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands: `pip list | grep click`, `pytest --version`, `jigy --version`
- Look for: All tools installed, no import errors, entry point works

---

### Work Unit 2: Core Utilities (io, yaml_utils)

**Goal:** Implement file I/O and YAML helper functions for loading/saving OSTC nodes.

**Planned Effort:** 60m

**Acceptance Criteria:**
- `src/jig/utils/io.py` implemented with file read/write functions
- `src/jig/utils/yaml_utils.py` implemented with YAML load/dump helpers
- Error handling for missing files, permission errors, invalid paths
- Type hints on all functions (mypy passes)
- Unit tests >80% coverage for both modules
- Functions are pure (no side effects beyond I/O)

**Implementation Notes:**
- Files to create:
  - `src/jig/utils/__init__.py`
  - `src/jig/utils/io.py`:
    ```python
    # @jig C-UTIL-001 implements:S-JIG-002 subsystem:core interface:internal
    def read_file(path: Path) -> str:
        """Read file contents, raise clear error if missing."""

    def write_file(path: Path, content: str) -> None:
        """Write file, create parent dirs if needed."""

    def ensure_dir(path: Path) -> None:
        """Create directory and parents if they don't exist."""
    ```
  - `src/jig/utils/yaml_utils.py`:
    ```python
    # @jig C-UTIL-002 implements:S-JIG-002 subsystem:core interface:internal
    def load_yaml(path: Path) -> dict:
        """Load YAML file, raise on parse errors."""

    def dump_yaml(data: dict, path: Path) -> None:
        """Write YAML with consistent formatting."""
    ```
- Use pathlib.Path throughout (not strings)
- Clear error messages with actionable guidance

**Test Plan:**
- Unit tests in `tests/unit/test_io.py`:
  ```python
  # @jig T-UTIL-001 verifies:S-JIG-002 subsystem:core
  def test_read_file_success():
      """Verify read_file loads file contents correctly."""

  # @jig T-UTIL-002 verifies:S-JIG-002 subsystem:core
  def test_read_file_missing():
      """Verify read_file raises FileNotFoundError with clear message."""
  ```
- Unit tests in `tests/unit/test_yaml_utils.py`:
  ```python
  # @jig T-UTIL-003 verifies:S-JIG-002 subsystem:core
  def test_load_yaml_valid():
      """Verify YAML parsing of valid frontmatter."""

  # @jig T-UTIL-004 verifies:S-JIG-002 subsystem:core
  def test_load_yaml_invalid():
      """Verify helpful error on malformed YAML."""
  ```
- Coverage target: >80%

**Docs to Update:**
- Add docstrings to all public functions
- Document error conditions and exceptions

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [tests]
- What could be better:
  - [scope]
- Discoveries:
  - [scope]

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands: `pytest tests/unit/test_io.py -v`, `pytest tests/unit/test_yaml_utils.py -v`
- Look for: All tests pass, coverage >80%, mypy clean

---

### Work Unit 3: Config Loader & Parser

**Goal:** Implement configuration loading (jig.toml) and OSTC node parsing (YAML frontmatter + Markdown).

**Planned Effort:** 90m

**Acceptance Criteria:**
- `src/jig/core/config.py` loads and validates jig.toml
- `src/jig/core/parser.py` parses OSTC node files (YAML frontmatter + Markdown body)
- Default configuration if jig.toml missing
- Parser handles all valid OSTC formats from SCOPE Section 3.2
- Unit tests >80% coverage for both modules
- Type-safe dataclasses for config and parsed nodes

**Implementation Notes:**
- Files to create:
  - `src/jig/core/__init__.py`
  - `src/jig/core/config.py`:
    ```python
    # @jig C-CORE-001 implements:S-JIG-002 subsystem:core interface:internal
    @dataclass
    class JigConfig:
        project_name: str
        intent_dir: Path
        delta_dir: Path
        templates_dir: Path
        # ... other config fields

    def load_config(path: Path = Path("jig.toml")) -> JigConfig:
        """Load config from jig.toml, use defaults if missing."""
    ```
  - `src/jig/core/parser.py`:
    ```python
    # @jig C-CORE-002 implements:S-JIG-002 subsystem:core interface:internal
    @dataclass
    class OSTCNode:
        id: str
        type: str  # outcome, specification, test, constraint
        title: str
        subsystem: str | None
        status: str | None
        created: date | None
        updated: date | None
        body: str  # Markdown content

    def parse_ostc_node(path: Path) -> OSTCNode:
        """Parse YAML frontmatter + Markdown from OSTC node file."""
    ```
- Use python-frontmatter library for parsing
- Use toml library for config loading
- Validate required fields at parse time

**Test Plan:**
- Unit tests in `tests/unit/test_config.py`:
  ```python
  # @jig T-CORE-001 verifies:S-JIG-002 subsystem:core
  def test_load_config_valid():
      """Verify config loads from valid jig.toml."""

  # @jig T-CORE-002 verifies:S-JIG-002 subsystem:core
  def test_load_config_defaults():
      """Verify defaults used when jig.toml missing."""
  ```
- Unit tests in `tests/unit/test_parser.py`:
  ```python
  # @jig T-CORE-003 verifies:S-JIG-002 subsystem:core
  def test_parse_outcome_node():
      """Verify parsing of Outcome node with all fields."""

  # @jig T-CORE-004 verifies:S-JIG-002 subsystem:core
  def test_parse_node_missing_required_field():
      """Verify error on missing required field (id, type, title)."""
  ```
- Coverage target: >80%

**Docs to Update:**
- Document JigConfig dataclass fields
- Document OSTCNode dataclass fields
- Add examples of valid jig.toml format

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [tools]
- What could be better:
  - [scope]
- Discoveries:
  - [scope]

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands: `pytest tests/unit/test_config.py tests/unit/test_parser.py -v`
- Look for: All tests pass, coverage >80%, clean type checking

---

### Work Unit 4: `jigy init` Command

**Goal:** Implement CLI command to initialize JIG directory structure in a project.

**Planned Effort:** 75m

**Acceptance Criteria:**
- `src/jig/cli/main.py` sets up Click CLI with help text
- `src/jig/cli/init.py` implements `jigy init` command
- Creates directory structure per SCOPE Section 3.1:
  - jig/outcomes/, jig/specifications/, jig/constraints/
  - jig/graph-index.yaml, jig/subsystems.yaml
  - jig.toml configuration file
- Command is idempotent (fails gracefully if already initialized)
- Exit codes: 0 (success), 1 (already exists), 2 (permission denied)
- Integration test verifies full workflow
- Performance: <500ms (measured in test)

**Implementation Notes:**
- Files to create:
  - `src/jig/cli/main.py`:
    ```python
    # @jig C-CLI-001 implements:S-JIG-002 subsystem:core interface:public
    import click

    @click.group()
    def cli():
        """JIG (Jig Intent Graph) - constraint-driven development tool."""

    # Import and register subcommands
    from jig.cli.init import init
    cli.add_command(init)
    ```
  - `src/jig/cli/init.py`:
    ```python
    # @jig C-CLI-002 implements:S-JIG-002 subsystem:core interface:public
    @click.command()
    @click.option('--path', default='.', help='Directory to initialize (default: current)')
    def init(path: str):
        """Initialize JIG structure in a project."""
    ```
- Check if jig/ exists before creating (idempotency)
- Create empty graph-index.yaml with version and empty nodes list
- Create empty subsystems.yaml
- Create jig.toml with default values
- Print success message with next steps

**Test Plan:**
- Integration test in `tests/integration/test_init_command.py`:
  ```python
  # @jig T-CLI-001 verifies:S-JIG-002 subsystem:core
  def test_jigy_init_creates_structure(tmp_path):
      """Verify jigy init creates correct directory structure."""
      # Run: jigy init --path tmp_path
      # Assert: All directories and files created

  # @jig T-CLI-002 verifies:S-JIG-002 subsystem:core
  def test_jigy_init_idempotent(tmp_path):
      """Verify jigy init fails gracefully if already initialized."""
      # Run twice, second should fail with exit code 1

  # @jig T-CLI-003 verifies:S-JIG-001 subsystem:core
  def test_jigy_init_performance(tmp_path, benchmark):
      """Verify jigy init completes in <500ms."""
      # Use pytest-benchmark if available
  ```

**Docs to Update:**
- README.md - Add "Getting Started" section with `jigy init` example
- Add `--help` text to command

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [tools]
- What could be better:
  - [scope]
- Discoveries:
  - [scope]

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands:
  ```bash
  jigy init --help
  cd /tmp/test-project
  jigy init
  ls -la jig/
  cat jig.toml
  jigy init  # Should fail with clear message
  ```
- Look for: Directory structure created, config file present, idempotency works

---

### Work Unit 5: Node Templates

**Goal:** Create OSTC node templates for outcome, specification, test, and constraint types.

**Planned Effort:** 45m

**Acceptance Criteria:**
- Four template files created in templates/ directory
- Templates follow formats from SCOPE Section 3.3
- Placeholders: {id}, {title}, {subsystem}, {date}
- Templates include helpful comments and structure guidance
- Templates validated by parsing with parser from WU3

**Implementation Notes:**
- Files to create:
  - `templates/outcome_template.md` (from SCOPE Section 3.3)
  - `templates/specification_template.md` (from SCOPE Section 3.3)
  - `templates/test_template.md` (create similar to spec template)
  - `templates/constraint_template.md` (create similar to spec template)
- Include sections:
  - YAML frontmatter with all required/optional fields
  - Markdown body with section headers
  - Placeholder links to related nodes
  - History section with creation date
- Use consistent formatting across all templates

**Test Plan:**
- Unit test in `tests/unit/test_templates.py`:
  ```python
  # @jig T-TPL-001 verifies:S-JIG-002 subsystem:core
  def test_templates_parse_correctly():
      """Verify all templates parse with valid YAML frontmatter."""
      # Load each template
      # Substitute placeholders with test values
      # Parse with OSTCNode parser
      # Assert: No parse errors
  ```

**Docs to Update:**
- Add comments in templates explaining each section
- Document placeholder format in templates/README.md

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [scope]
- What could be better:
  - [scope]
- Discoveries:
  - [scope]

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands: `ls templates/`, `cat templates/outcome_template.md`
- Look for: 4 template files, clear structure, helpful comments

---

### Work Unit 6: `jigy node create` Command

**Goal:** Implement CLI command to create new OSTC nodes from templates.

**Planned Effort:** 90m

**Acceptance Criteria:**
- `src/jig/cli/node.py` implements `jigy node create` command
- Required args: --type, --id, --title
- Optional args: --subsystem
- Validates ID format: [OSTC]-[A-Z0-9]+-[0-9]{3}
- Loads appropriate template from templates/
- Substitutes placeholders: {id}, {title}, {subsystem}, {date}
- Writes file to jig/{type}s/{id}.md
- Updates graph-index.yaml with new node entry
- Exit codes: 0 (success), 1 (invalid ID), 2 (already exists), 3 (not initialized)
- Performance: <200ms (measured in test)

**Implementation Notes:**
- File to create: `src/jig/cli/node.py`:
  ```python
  # @jig C-CLI-003 implements:S-JIG-002 subsystem:core interface:public
  @click.command()
  @click.option('--type', required=True, type=click.Choice(['outcome', 'specification', 'test', 'constraint']))
  @click.option('--id', 'node_id', required=True, help='Node ID (e.g., O-JIG-001)')
  @click.option('--title', required=True, help='Human-readable title')
  @click.option('--subsystem', default=None, help='Subsystem name')
  def create(type: str, node_id: str, title: str, subsystem: str | None):
      """Create a new OSTC node from template."""
  ```
- ID format validation regex: `^[OSTC]-[A-Z0-9]+-\d{3}$`
- Check ID prefix matches type: O→outcome, S→specification, T→test, C→constraint
- Template substitution:
  - {id} → node_id
  - {title} → title
  - {subsystem} → subsystem or "null"
  - {date} → datetime.now().strftime("%Y-%m-%d")
- Update graph-index.yaml by appending to nodes list
- Print success message with file path

**Test Plan:**
- Integration test in `tests/integration/test_node_create.py`:
  ```python
  # @jig T-CLI-004 verifies:S-JIG-002 subsystem:core
  def test_jigy_node_create_outcome(tmp_path):
      """Verify jigy node create generates valid Outcome node."""
      # Run: jigy init, then jigy node create --type outcome --id O-TEST-001 --title "Test"
      # Assert: File created, valid YAML, graph-index updated

  # @jig T-CLI-005 verifies:S-JIG-002 subsystem:core
  def test_jigy_node_create_invalid_id(tmp_path):
      """Verify jigy node create rejects invalid ID format."""
      # Run with invalid ID: "O_TEST_001"
      # Assert: Exit code 1, clear error message

  # @jig T-CLI-006 verifies:S-JIG-001 subsystem:core
  def test_jigy_node_create_performance(tmp_path, benchmark):
      """Verify jigy node create completes in <200ms."""
  ```

**Docs to Update:**
- README.md - Add example usage of `jigy node create`
- Document ID format requirements
- Add `--help` text to command

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [tools]
- What could be better:
  - [scope]
- Discoveries:
  - [scope]

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands:
  ```bash
  jigy node create --help
  jigy node create --type outcome --id O-TEST-001 --title "Users complete tasks quickly"
  cat jig/outcomes/O-TEST-001.md
  cat jig/graph-index.yaml
  jigy node create --type outcome --id O_TEST_002 --title "Bad ID"  # Should fail
  ```
- Look for: Node created, valid format, graph updated, validation works

---

### Work Unit 7: OSTC Validator

**Goal:** Implement validation logic for OSTC nodes and graph consistency.

**Planned Effort:** 90m

**Acceptance Criteria:**
- `src/jig/core/validator.py` implements validation functions
- Validates required fields: id, type, title
- Validates ID format matches type (O→outcome, etc.)
- Validates type values: outcome, specification, test, constraint
- Detects duplicate IDs across all nodes
- Validates graph-index.yaml references (all nodes exist)
- Returns structured validation results (errors, warnings)
- Unit tests >80% coverage

**Implementation Notes:**
- File to create: `src/jig/core/validator.py`:
  ```python
  # @jig C-CORE-003 implements:S-JIG-002 subsystem:core interface:internal
  @dataclass
  class ValidationResult:
      valid: bool
      errors: list[str]
      warnings: list[str]

  def validate_node(node: OSTCNode) -> ValidationResult:
      """Validate single OSTC node schema."""
      # Check required fields
      # Check ID format
      # Check type value

  def validate_graph(intent_dir: Path) -> ValidationResult:
      """Validate all OSTC nodes and graph consistency."""
      # Load all nodes
      # Check for duplicate IDs
      # Validate graph-index.yaml references
      # Check for orphaned nodes
  ```
- ID format regex: `^[OSTC]-[A-Z0-9]+-\d{3}$`
- Type prefix mapping: O→outcome, S→specification, T→test, C→constraint
- Collect all errors before returning (don't fail on first error)

**Test Plan:**
- Unit tests in `tests/unit/test_validator.py`:
  ```python
  # @jig T-CORE-005 verifies:S-JIG-002 subsystem:core
  def test_validate_node_valid():
      """Verify validation passes for valid node."""

  # @jig T-CORE-006 verifies:S-JIG-002 subsystem:core
  def test_validate_node_missing_required_field():
      """Verify validation detects missing 'title' field."""

  # @jig T-CORE-007 verifies:S-JIG-002 subsystem:core
  def test_validate_node_invalid_id_format():
      """Verify validation detects invalid ID format (underscore)."""

  # @jig T-CORE-008 verifies:S-JIG-002 subsystem:core
  def test_validate_node_type_mismatch():
      """Verify validation detects ID prefix mismatch (O- with type:specification)."""

  # @jig T-CORE-009 verifies:S-JIG-002 subsystem:core
  def test_validate_graph_duplicate_ids():
      """Verify validation detects duplicate node IDs."""

  # @jig T-CORE-010 verifies:S-JIG-002 subsystem:core
  def test_validate_graph_orphaned_references():
      """Verify validation detects references to non-existent nodes."""
  ```
- Coverage target: >80%

**Docs to Update:**
- Document validation rules in docs/architecture/DATA_FORMATS.md
- Add docstrings explaining each validation check

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [tests]
- What could be better:
  - [scope]
- Discoveries:
  - [scope]

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands: `pytest tests/unit/test_validator.py -v`
- Look for: All tests pass, edge cases covered, clear error messages

---

### Work Unit 8: `jigy validate` Command

**Goal:** Implement CLI command to validate OSTC nodes and graph consistency.

**Planned Effort:** 60m

**Acceptance Criteria:**
- `src/jig/cli/validate.py` implements `jigy validate` command
- Options: --check-all, --verbose
- Loads all OSTC nodes from jig/
- Calls validator from WU7 for each node and overall graph
- Prints validation results with clear formatting (per SCOPE Section 3.1)
- Exit codes: 0 (valid), 1 (errors found)
- Performance: <1s for 100 nodes (measured in test)
- Colorized output (✓ green, ✗ red, ⚠ yellow)

**Implementation Notes:**
- File to create: `src/jig/cli/validate.py`:
  ```python
  # @jig C-CLI-004 implements:S-JIG-002 subsystem:core interface:public
  @click.command()
  @click.option('--check-all', is_flag=True, help='Check all nodes including warnings')
  @click.option('--verbose', is_flag=True, help='Show detailed validation info')
  def validate(check_all: bool, verbose: bool):
      """Validate OSTC nodes and graph consistency."""
  ```
- Output format from SCOPE Section 3.1:
  ```
  Validating JIG graph...

  ✓ jig/outcomes/O-JIG-001.md
  ✓ jig/specifications/S-JIG-001.md
  ✗ jig/specifications/S-JIG-002.md
    - Missing required field: title

  Graph Index:
  ✓ All 47 nodes referenced in graph-index.yaml exist
  ⚠ Warning: 3 nodes not referenced in graph

  Summary: 45/47 nodes valid
  ```
- Use click.style() for colors
- Exit with code 1 if any errors found

**Test Plan:**
- Integration test in `tests/integration/test_validate_command.py`:
  ```python
  # @jig T-CLI-007 verifies:S-JIG-002 subsystem:core
  def test_jigy_validate_all_valid(tmp_path):
      """Verify jigy validate passes for valid graph."""
      # Create valid nodes
      # Run: jigy validate
      # Assert: Exit code 0, success message

  # @jig T-CLI-008 verifies:S-JIG-002 subsystem:core
  def test_jigy_validate_detects_errors(tmp_path):
      """Verify jigy validate detects invalid nodes."""
      # Create node with missing required field
      # Run: jigy validate
      # Assert: Exit code 1, error message shown

  # @jig T-CLI-009 verifies:S-JIG-001 subsystem:core
  def test_jigy_validate_performance(tmp_path, benchmark):
      """Verify jigy validate completes in <1s for 100 nodes."""
      # Create 100 valid nodes
      # Benchmark validation
  ```

**Docs to Update:**
- README.md - Add validation example
- Document validation rules and error messages

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [tools]
- What could be better:
  - [scope]
- Discoveries:
  - [scope]

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands:
  ```bash
  jigy validate --help
  jigy validate
  jigy validate --verbose
  jigy validate --check-all
  ```
- Look for: Clear output, correct exit codes, performance <1s

---

### Work Unit 9: Dogfooding - Create JIG's Own Nodes

**Goal:** Use jigy commands to create JIG's own Intent Graph nodes, demonstrating dogfooding.

**Planned Effort:** 75m

**Acceptance Criteria:**
- JIG project has jig/ directory initialized via `jigy init`
- All 5 Outcome nodes from WU0 created via `jigy node create`
- All 4 Specification nodes from WU0 created via `jigy node create`
- Each node has meaningful content (not just templates)
- Specifications link to Outcomes they implement
- `jigy validate` passes on JIG's own graph
- graph-index.yaml contains all 9 nodes
- jig.toml configured for JIG project

**Implementation Notes:**
- Run in JIG project root (not a test directory)
- Commands to execute:
  ```bash
  jigy init

  # Create Outcomes
  jigy node create --type outcome --id O-JIG-001 --title "JIG tools run in <1 second for most operations" --subsystem core
  jigy node create --type outcome --id O-JIG-002 --title "JIG uses simple text formats (YAML + Markdown)" --subsystem core
  # ... (repeat for O-JIG-003 through O-JIG-005)

  # Create Specifications
  jigy node create --type specification --id S-JIG-001 --title "Marker extraction processes 1000 files in <1s" --subsystem core
  # ... (repeat for S-JIG-002 through S-JIG-004)
  ```
- Edit each node file to add:
  - Full description in markdown body
  - Success metrics for Outcomes
  - Requirements and rationale for Specifications
  - Links between S and O nodes (implements relationship)
- Validate after all nodes created

**Test Plan:**
- Manual validation (not automated tests):
  - Read each node file, verify content quality
  - Check all required fields present
  - Verify links between nodes are correct
  - Run `jigy validate` to confirm no errors

**Docs to Update:**
- jig/outcomes/O-JIG-001.md through O-JIG-005.md - Full content
- jig/specifications/S-JIG-001.md through S-JIG-004.md - Full content
- jig.toml - Project-specific configuration

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [process] Dogfooding revealed usability issues early
- What could be better:
  - [tools] Commands worked as expected or had issues?
- Discoveries:
  - [scope] Any missing features discovered during dogfooding?
- Next experiment:
  - [process]

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands:
  ```bash
  ls -la jig/
  cat jig/outcomes/O-JIG-001.md
  cat jig/specifications/S-JIG-001.md
  jigy validate --check-all
  ```
- Look for: 9 high-quality node files, validation passes, clear relationships

---

### Work Unit 10: Documentation & Release

**Goal:** Complete documentation, ensure quality gates pass, and tag v0.1.0-bootstrap release.

**Planned Effort:** 75m

**Acceptance Criteria:**
- README.md complete with:
  - Project overview and philosophy
  - Installation instructions
  - Quick start guide (init, create, validate)
  - Link to full documentation
- docs/architecture/DATA_FORMATS.md written:
  - OSTC node format specification
  - graph-index.yaml format
  - jig.toml configuration format
  - Template format and placeholders
- PLAN_slice_0_bootstrap.md completed with:
  - All Work Units marked complete
  - Completion Summary filled
  - Reflection roll-up
  - Harvest Preparation section
- All quality gates pass:
  - `pytest` - all tests pass
  - `ruff check` - no linting errors
  - `mypy src/` - no type errors
  - Test coverage >80%
- Git tag: v0.1.0-bootstrap

**Implementation Notes:**
- Files to create/update:
  - `README.md` - Complete rewrite with full content
  - `docs/architecture/DATA_FORMATS.md` - New file documenting formats
  - `jig/deltas/active/bootstrap-slice-0/PLAN_slice_0_bootstrap.md` - Copy from docs/wip/
- Quality checks to run:
  ```bash
  pytest --cov=src/jig --cov-report=term-missing
  ruff check src/ tests/
  mypy src/
  ```
- Ensure coverage >80% (add tests if needed)
- Fix any linting or type errors
- Create git tag:
  ```bash
  git tag -a v0.1.0-bootstrap -m "Slice 0: Bootstrap infrastructure complete"
  ```

**Test Plan:**
- Manual review:
  - Read README.md for clarity and completeness
  - Read DATA_FORMATS.md for technical accuracy
  - Verify all examples in docs work
- Automated checks:
  - Run all tests with coverage report
  - Run linters and type checker
  - Verify no errors or warnings

**Docs to Update:**
- README.md - Complete overhaul
- docs/architecture/DATA_FORMATS.md - New comprehensive documentation
- PLAN_slice_0_bootstrap.md - Mark all units complete, add Completion Summary

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [process] PLAN workflow effectiveness
  - [tools] Development tooling quality
- What could be better:
  - [scope] Any scope gaps discovered?
  - [process] PLAN template improvements needed?
- Discoveries:
  - [scope] Unexpected requirements or constraints
- Learned patterns:
  - [process] Reusable patterns from bootstrap
- Risk watchlist:
  - [risk] Known issues or technical debt

**Links:**
- Commit: [to be filled]
- Tag: v0.1.0-bootstrap

**Human Validation:**
- Commands:
  ```bash
  pytest --cov=src/jig --cov-report=term-missing
  ruff check src/ tests/
  mypy src/
  git tag -l
  ```
- Look for: All tests pass, coverage >80%, no errors, tag created

---

## Completion Summary

### Summary
- Scope delivered: [To be filled on completion]
- Key decisions: [To be filled]
- Deltas from SCOPE: [To be filled]

### Metrics
- Units: 11 (including WU0); median cycle time: [TBD]
- Rework rate (units reopened): [TBD]
- Flaky test events: [TBD]
- Docs lag: [TBD]
- Markers captured: [TBD] (#DISCOVERY, #DECISION, #LEARNED)

### Reflection Roll-up
- Repeatable wins: [To be filled]
- Systemic frictions (top 3): [To be filled]
- Process changes adopted: [To be filled]
- Open questions for next plan: [To be filled]

### Harvest Preparation (JIG)

**Markers Summary:**
- Discoveries: [TBD]
- Decisions: [TBD]
- Learned patterns: [TBD]

**Recommended OSTC Nodes (from DISCOVERIES only):**
(To be filled based on #DISCOVERY markers found during implementation - these are NEW constraints learned, not the ones created in WU0)

**Subsystems Touched:** core (primary)

**Next Step:** `jig ai-distill --branch bootstrap-slice-0`

**Note:** The 9 Outcome and Specification nodes created in WU0 represent KNOWN constraints from SCOPE. Harvest will capture NEW insights discovered during implementation (WU1-WU10).

---

**Document Version:** 1.0
**Last Updated:** 2025-11-18
**Status:** Draft - Ready to Execute
