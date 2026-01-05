---
title: "Brick-First File Organization"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1763956181
created_human: "2025-11-23 21:49 CST"
parent: "[[AG001_Alignment-Graph-Bricks]]"
children: []
---
# Brick-First File Organization

_Physical Structure Aligned with Logical Architecture_

**Date:** 2025-11-23
**Status:** Exploration
**Author:** Claude + Jim Meyer

---

## Executive Summary

This document explores organizing project files **by Brick** rather than by technical concern (src/, tests/, docs/). In a brick-first structure, each brick becomes a self-contained directory containing its code, tests, intent nodes, and metadata.

**Key Question:** Should physical file structure mirror logical architectural boundaries?

**Short Answer:** It depends on your priorities. Brick-first organization offers profound advantages for architectural clarity, agent safety, and cognitive simplicity—but comes with significant practical challenges in build systems, imports, and migration cost.

This document explores both deeply.

---

## 1. The Two Organizational Philosophies

### 1.1 Traditional: Organization by Technical Concern

Most software projects organize by **what things are**:

```
project/
├── src/           # all implementation
├── tests/         # all verification
├── docs/          # all documentation
├── config/        # all configuration
└── scripts/       # all tooling
```

This is the **technical separation** model. It groups similar artifacts together.

**Rationale:**
- Developers look for "all the code" or "all the tests"
- Build tools expect src/ and tests/
- Package managers expect certain layouts
- Historical convention (Unix, Python, Java)

### 1.2 Brick-First: Organization by Architectural Unit

A brick-first structure organizes by **what things mean**:

```
bricks/
├── foundation-utilities/
│   ├── brick.yaml
│   ├── code/
│   ├── tests/
│   └── intent/
├── graph-core/
│   ├── brick.yaml
│   ├── code/
│   ├── tests/
│   └── intent/
└── cli-commands/
    ├── brick.yaml
    ├── code/
    ├── tests/
    └── intent/
```

This is the **semantic cohesion** model. It groups related artifacts together.

**Rationale:**
- Architects think in architectural units, not file types
- Agents need bounded context, not global file trees
- Changes happen within bricks, not across technical layers
- Ownership and responsibility are clearer
- Physical boundaries enforce logical boundaries

---

## 2. What Brick-First File Organization Looks Like

### 2.1 Complete Example: Foundation Utilities Brick

```
bricks/foundation-utilities/
├── brick.yaml                          # Brick definition
├── README.md                           # Brick-level documentation
├── code/
│   ├── __init__.py
│   ├── io.py                           # read_file, write_file, ensure_dir
│   └── yaml_utils.py                   # load_yaml, dump_yaml
├── tests/
│   ├── __init__.py
│   ├── test_io.py                      # 12 tests
│   └── test_yaml_utils.py              # 12 tests
└── intent/
    ├── outcomes/
    │   └── O-UTILS-001-reliable-io.md
    └── specifications/
        ├── S-UTILS-001-file-operations.md
        └── S-UTILS-002-yaml-operations.md
```

**Everything for this brick is co-located.**

### 2.2 Complete Example: Graph Core Brick

```
bricks/graph-core/
├── brick.yaml
├── README.md
├── code/
│   ├── __init__.py
│   ├── graph.py                        # Graph, Subsystem classes
│   ├── relationships.py                # Edge extraction
│   └── types.py                        # Shared types
├── tests/
│   ├── __init__.py
│   ├── test_graph.py
│   ├── test_graph_queries.py
│   ├── test_graph_traversal.py
│   └── test_relationship_parsing.py
└── intent/
    ├── outcomes/
    │   └── O-GRAPH-001-query-intent.md
    └── specifications/
        ├── S-GRAPH-001-data-structures.md
        ├── S-GRAPH-002-queries.md
        └── S-GRAPH-003-traversal.md
```

### 2.3 Complete Example: CLI Commands Brick

```
bricks/cli-commands/
├── brick.yaml
├── README.md
├── code/
│   ├── __init__.py
│   ├── main.py
│   ├── init.py
│   ├── node.py
│   ├── validate.py
│   ├── status.py
│   ├── graph.py
│   ├── index.py
│   ├── decompose.py
│   └── formatting.py
├── tests/
│   ├── unit/
│   │   ├── test_formatting.py
│   │   ├── test_graph_commands.py
│   │   ├── test_status_logic.py
│   │   └── test_templates.py
│   └── integration/
│       ├── test_cli_init.py
│       ├── test_cli_node.py
│       ├── test_cli_validate.py
│       ├── test_cli_status.py
│       ├── test_cli_graph.py
│       └── test_cli_index.py
└── intent/
    ├── outcomes/
    │   ├── O-CLI-001-user-interface.md
    │   ├── O-CLI-002-command-discoverability.md
    │   └── O-CLI-005-helpful-errors.md
    └── specifications/
        ├── S-CLI-004-init-command.md
        ├── S-CLI-005-node-command.md
        ├── S-CLI-006-validate-command.md
        └── S-CLI-007-status-command.md
```

### 2.4 Root Project Structure

```
jig/
├── bricks/                             # All bricks here
│   ├── foundation-utilities/
│   ├── configuration/
│   ├── intent-parser/
│   ├── intent-validator/
│   ├── graph-core/
│   ├── index-builder/
│   ├── annotation-scanner/
│   ├── annotation-validator/
│   ├── decomposition-analysis/
│   └── cli-commands/
├── shared/                             # Shared artifacts (see Section 5)
│   ├── types/
│   ├── protocols/
│   └── constants/
├── tools/                              # Build and dev tools
│   ├── brick_validator.py
│   ├── dependency_checker.py
│   └── context_builder.py
├── graph-index.json                    # Generated index
├── pyproject.toml                      # Package metadata
├── README.md
└── docs/
    ├── architecture/
    ├── guides/
    └── jig-concept/
```

---

## 3. Import Paths and Module Structure

### 3.1 The Import Path Challenge

**Problem:** How do bricks import from each other?

#### Option A: Flat Brick Namespace

```python
# From cli-commands brick
from bricks.graph_core.code.graph import Graph
from bricks.foundation_utilities.code.io import read_file
from bricks.intent_parser.code.parser import OSTCNode
```

**Pros:** Clear brick boundaries in every import
**Cons:** Verbose, includes implementation detail ("code")

#### Option B: Brick-Level Packages

```python
# Each brick exports via __init__.py
# bricks/graph_core/code/__init__.py
from .graph import Graph, Subsystem, Edge
from .relationships import extract_edges

# From cli-commands brick
from bricks.graph_core import Graph
from bricks.foundation_utilities import read_file
from bricks.intent_parser import OSTCNode
```

**Pros:** Clean imports, brick boundaries clear
**Cons:** Requires careful __init__.py management

#### Option C: Brick Aliases (Recommended)

```python
# pyproject.toml or setup.py creates aliases
# "jig.graph" -> "bricks/graph-core/code"
# "jig.utils" -> "bricks/foundation-utilities/code"

# From cli-commands brick
from jig.graph import Graph
from jig.utils import read_file
from jig.parser import OSTCNode
```

**Pros:** Familiar import style, brick abstraction
**Cons:** Indirection, requires build configuration

### 3.2 Enforcing Brick Boundaries

With brick-first organization, import violations become **physically obvious**:

```python
# VIOLATION: CLI reaching into Graph internals
from bricks.graph_core.code._internal_helpers import private_function
# This should trigger a linter error

# CORRECT: CLI using Graph's public interface
from bricks.graph_core import Graph
```

Tooling can enforce:
1. Only import from brick-level `__init__.py`
2. Never import from another brick's `tests/` or `intent/`
3. Only import from declared dependencies in `brick.yaml`

---

## 4. Advantages of Brick-First Organization

### 4.1 Architectural Advantages

#### A. Physical = Logical Alignment

**Principle:** Structure should follow architecture (Conway's Law in reverse)

With brick-first organization:
- Brick boundaries are **physically enforced** by directory structure
- Violations require deliberately reaching across directories
- Architecture is **visible** in the file tree
- Drift is **obvious** (files in wrong places)

**Example:**
```
# Traditional structure - architecture is invisible
src/jig/core/
├── graph.py          # Which brick?
├── parser.py         # Which brick?
├── validator.py      # Which brick?
└── scanner.py        # Which brick?

# Brick-first - architecture is explicit
bricks/
├── graph-core/
├── intent-parser/
├── intent-validator/
└── annotation-scanner/
```

#### B. Dependency Visibility

All brick dependencies are **explicit and traceable**:

```yaml
# bricks/cli-commands/brick.yaml
dependencies:
  bricks:
    - graph-core
    - intent-parser
    - foundation-utilities
```

Tooling can verify:
- Actual imports match declared dependencies
- No circular dependencies
- Dependency depth is reasonable
- Coupling metrics align with declarations

#### C. Easier Extraction and Composition

**Want to make a brick a separate package?**

Traditional structure:
1. Find all relevant code scattered across src/
2. Find all relevant tests scattered across tests/
3. Find all relevant docs scattered across docs/
4. Create new package structure
5. Update imports everywhere
6. Hope you didn't miss anything

Brick-first structure:
1. Copy `bricks/graph-core/` to new repo
2. Add `pyproject.toml`
3. Done

**Want to compose multiple projects?**

```
my-project/
├── bricks/
│   ├── my-brick-1/
│   ├── my-brick-2/
│   └── vendor/
│       ├── jig-graph-core/      # Imported brick
│       └── jig-utils/            # Imported brick
```

### 4.2 Agent Workflow Advantages

#### A. Perfect Context Boundaries

**Problem with traditional structure:**
Agent needs to implement a feature in the Graph brick.

Traditional context:
```
- All of src/jig/core/ (mixed bricks)
- All of src/jig/utils/ (mixed bricks)
- All of tests/unit/ (mixed bricks)
- Brick definition files (separate location)
```

**Agent sees too much, gets distracted, may edit wrong files.**

Brick-first context:
```
- bricks/graph-core/
  - brick.yaml
  - code/
  - tests/
  - intent/
- Public interfaces of dependency bricks
```

**Agent sees exactly what it needs, nothing more.**

#### B. Simpler Context Loading

```python
# tools/agent_context.py

def load_brick_context(brick_name: str) -> Context:
    """Load complete context for a brick."""
    brick_dir = Path(f"bricks/{brick_name}")

    return Context(
        definition=load_yaml(brick_dir / "brick.yaml"),
        code=load_all_files(brick_dir / "code"),
        tests=load_all_files(brick_dir / "tests"),
        intent=load_all_files(brick_dir / "intent"),
        dependencies=load_dependency_interfaces(brick_name)
    )
```

**One directory = complete context.**

#### C. Clear Task Scoping

Tasks naturally align with brick boundaries:

- "Implement feature X in the Graph brick" → Work in `bricks/graph-core/`
- "Fix bug in CLI status command" → Work in `bricks/cli-commands/`
- "Add validation rule" → Work in `bricks/intent-validator/`

**No ambiguity about scope.**

### 4.3 Human Workflow Advantages

#### A. Cognitive Clarity

Humans naturally think in **wholes**, not fragments:

- "I need to understand the Graph brick" → Open one directory
- "Where are the tests for Parser?" → `bricks/intent-parser/tests/`
- "What are the responsibilities of Scanner?" → Read `bricks/annotation-scanner/brick.yaml`

**Everything related is together.**

#### B. Onboarding and Navigation

New team member asks: "How does the annotation scanner work?"

Traditional structure:
1. Read `src/jig/core/scanner.py` (code)
2. Find tests in `tests/unit/test_annotation_scanner.py` (different tree)
3. Find intent in `jig/specifications/S-CLI-008.md` (another tree)
4. Find brick definition in `jig/bricks/annotation-scanner.brick.yaml` (yet another tree)
5. Mentally reconstruct the full picture

Brick-first structure:
1. Open `bricks/annotation-scanner/`
2. Everything is there

**Cognitive load: minimal.**

#### C. Clear Ownership

In a team environment:

```
bricks/
├── graph-core/           # Team: Core Platform
├── cli-commands/         # Team: User Experience
├── decomposition/        # Team: Analytics
```

Each team owns a directory. CODEOWNERS file is simple:

```
# CODEOWNERS
bricks/graph-core/          @platform-team
bricks/cli-commands/        @ux-team
bricks/decomposition/       @analytics-team
```

**No coordination needed for internal changes.**

#### D. Parallel Development

Multiple developers can work simultaneously without merge conflicts:

- Alice: refactoring `bricks/graph-core/code/graph.py`
- Bob: adding tests to `bricks/cli-commands/tests/`
- Carol: writing specs in `bricks/intent-validator/intent/`

**Minimal overlap, minimal conflicts.**

### 4.4 Testing and CI Advantages

#### A. Brick-Level Test Isolation

Each brick has its own test suite:

```bash
# Test a single brick
pytest bricks/graph-core/tests/

# Test all bricks in parallel
for brick in bricks/*/; do
    pytest "$brick/tests/" &
done
wait
```

#### B. Incremental CI

```yaml
# .github/workflows/test.yml
- name: Detect changed bricks
  run: |
    CHANGED=$(git diff --name-only HEAD~1 | grep '^bricks/' | cut -d/ -f2 | sort -u)

- name: Test changed bricks
  run: |
    for brick in $CHANGED; do
      pytest bricks/$brick/tests/
    done
```

**Only test what changed.**

#### C. Brick-Level Coverage

```bash
# Coverage report per brick
coverage run --source=bricks/graph-core/code -m pytest bricks/graph-core/tests/
coverage report
```

**Clear accountability for test quality.**

---

## 5. Challenges of Brick-First Organization

### 5.1 Shared Artifacts Problem

**Question:** Where do shared types, interfaces, and constants go?

#### The Problem

Many bricks need common definitions:

```python
# Multiple bricks need this
class NodeType(Enum):
    OUTCOME = "O"
    SPECIFICATION = "S"
    TASK = "T"
    CONSTRAINT = "C"
```

**Where does it live?**

#### Solution 1: Shared Brick

Create a special `shared/` or `common/` brick:

```
bricks/
├── _shared/
│   ├── brick.yaml
│   ├── code/
│   │   ├── types.py
│   │   ├── protocols.py
│   │   └── constants.py
│   └── tests/
```

**Pros:** Follows brick pattern
**Cons:** Creates a "god brick" that everything depends on

#### Solution 2: Root-Level Shared

```
jig/
├── bricks/
├── shared/
│   ├── types.py
│   ├── protocols.py
│   └── constants.py
```

**Pros:** Clearly special, not pretending to be a brick
**Cons:** Breaks the "everything is a brick" model

#### Solution 3: Duplicate Strategically

Accept some controlled duplication:

```
bricks/intent-parser/code/types.py    # Defines NodeType
bricks/graph-core/code/types.py       # Imports from parser OR duplicates
```

**Pros:** Each brick is more self-contained
**Cons:** Duplication, potential drift

**Recommended:** Solution 2 (root-level shared/) for true cross-cutting concerns, with strict governance.

### 5.2 Build System Complexity

#### Python Package Structure

Traditional Python packages expect:

```
src/
  package_name/
    __init__.py
    module.py
```

Brick-first structure needs build configuration:

```toml
# pyproject.toml
[tool.setuptools.packages.find]
where = ["bricks/*/code"]

[tool.setuptools.package-dir]
"jig.graph" = "bricks/graph-core/code"
"jig.utils" = "bricks/foundation-utilities/code"
# ... etc for each brick
```

**Challenge:** More complex build configuration
**Mitigation:** Generate build config from brick definitions

#### Import Path Configuration

Need to configure Python to find bricks:

```python
# setup.py or pyproject.toml
import sys
from pathlib import Path

# Add all brick code directories to Python path
bricks_dir = Path(__file__).parent / "bricks"
for brick in bricks_dir.iterdir():
    if brick.is_dir():
        code_dir = brick / "code"
        if code_dir.exists():
            sys.path.insert(0, str(code_dir))
```

**Challenge:** Non-standard Python setup
**Mitigation:** Provide tooling and documentation

### 5.3 IDE and Tooling Support

#### Problem: IDEs Expect Traditional Structure

Most Python IDEs assume:
- Code is in `src/` or project root
- Tests are in `tests/`
- One package per project

#### Solutions:

**PyCharm/IntelliJ:**
- Mark each `bricks/*/code` as "Sources Root"
- Mark each `bricks/*/tests` as "Test Sources Root"
- Configure in `.idea/jig.iml`

**VSCode:**
```json
// .vscode/settings.json
{
    "python.analysis.extraPaths": [
        "bricks/*/code"
    ],
    "python.testing.pytestPaths": [
        "bricks/*/tests"
    ]
}
```

**Challenge:** Manual configuration per developer
**Mitigation:** Check in IDE config, provide setup script

### 5.4 Integration and Cross-Brick Tests

**Question:** Where do tests that span multiple bricks go?

#### Scenario: End-to-End CLI Test

Test involves:
- CLI brick (user input)
- Index Builder brick (rebuilding)
- Graph brick (querying)
- Validator brick (checking)

**Where does this test live?**

#### Solution 1: Integration Tests Directory

```
jig/
├── bricks/
└── tests/
    └── integration/
        ├── test_e2e_cli.py
        ├── test_full_pipeline.py
        └── test_cross_brick_workflows.py
```

**Pros:** Clear separation of integration vs. unit tests
**Cons:** Breaks the "everything in bricks" model

#### Solution 2: Tests Live in Top-Level Brick

```
bricks/cli-commands/
└── tests/
    ├── unit/
    └── integration/
        └── test_full_pipeline.py
```

**Pros:** Tests with the orchestrator brick
**Cons:** CLI brick now "owns" tests for other bricks

**Recommended:** Solution 1 (separate integration/ directory) for true cross-brick tests.

### 5.5 Package Distribution

**Question:** How do you publish this to PyPI?

#### Option A: Single Package

```bash
pip install jig
```

Installs all bricks as one package:

```
site-packages/
└── jig/
    ├── graph/
    ├── utils/
    ├── cli/
    └── ...
```

**Pros:** Simple for users
**Cons:** Can't install individual bricks

#### Option B: Multiple Packages

```bash
pip install jig-graph
pip install jig-cli
pip install jig-utils
```

Each brick is a separate package.

**Pros:** Modular, reusable bricks
**Cons:** Complex to maintain, version compatibility issues

#### Option C: Hybrid (Recommended)

Main package with optional extras:

```bash
pip install jig              # Core bricks only
pip install jig[decompose]   # + decomposition analysis
pip install jig[all]         # Everything
```

```toml
# pyproject.toml
[project.optional-dependencies]
decompose = ["networkx>=2.6"]
all = ["networkx>=2.6", "click>=8.0", ...]
```

### 5.6 Migration Cost

**Challenge:** Moving from traditional to brick-first is a massive refactor.

For an existing project like JIG:

1. Create brick directories
2. Move code files
3. Move test files
4. Move intent files
5. Update all imports (hundreds of files)
6. Update build configuration
7. Update CI/CD
8. Update documentation
9. Update developer workflows
10. Retrain team

**Estimated effort:** 2-4 weeks for a project JIG's size

**Risk:** Breaking changes, lost productivity during transition

---

## 6. Hybrid Approaches

### 6.1 Virtual Brick Views

**Concept:** Keep traditional structure, but provide brick-filtered views

```bash
# Traditional structure on disk
src/jig/core/graph.py
tests/unit/test_graph.py

# Virtual brick view (symlinks or tool)
jigy view graph-core
# Shows:
#   - src/jig/core/graph.py
#   - src/jig/core/relationships.py
#   - tests/unit/test_graph.py
#   - ...
```

**Pros:** No migration needed, best of both worlds
**Cons:** Requires tooling, not "real" physical boundaries

### 6.2 Brick-Aware Tooling Over Traditional Structure

Keep traditional structure, but add brick-aware tools:

```bash
# Enforce brick boundaries without moving files
jigy check-boundaries

# Load brick context for agent
jigy context --brick graph-core > context.txt

# Test a brick
jigy test --brick cli-commands
```

**Pros:** Minimal disruption, gradual adoption
**Cons:** Boundaries are policy, not structure

### 6.3 Progressive Migration

Adopt brick-first for new bricks only:

```
jig/
├── src/jig/                 # Old code (traditional)
│   ├── core/
│   └── cli/
├── tests/                   # Old tests
├── bricks/                  # New bricks (brick-first)
│   ├── new-feature-1/
│   └── new-feature-2/
```

**Pros:** Gradual transition, prove value before full commitment
**Cons:** Inconsistent structure, two systems to maintain

---

## 7. Examples from Other Ecosystems

### 7.1 Rust Workspaces

Rust uses a workspace model similar to brick-first:

```
my-project/
├── Cargo.toml              # Workspace manifest
├── crates/
│   ├── core/
│   │   ├── Cargo.toml
│   │   ├── src/
│   │   └── tests/
│   ├── cli/
│   │   ├── Cargo.toml
│   │   ├── src/
│   │   └── tests/
│   └── utils/
│       ├── Cargo.toml
│       ├── src/
│       └── tests/
```

Each "crate" is self-contained, like a brick.

**Lessons:**
- Works well with strong module system
- Each crate has own manifest (like brick.yaml)
- Dependencies explicitly declared
- Tooling (`cargo`) understands workspace structure

### 7.2 Go Modules

Go modules organize by package, similar to bricks:

```
my-project/
├── go.mod
├── graph/
│   ├── graph.go
│   ├── graph_test.go
│   └── relationships.go
├── parser/
│   ├── parser.go
│   └── parser_test.go
└── cli/
    ├── main.go
    └── commands_test.go
```

Tests live next to code (`_test.go` files).

**Lessons:**
- Co-located tests work well
- Package = architectural unit
- Import paths enforce boundaries
- Simple, clear structure

### 7.3 Java Maven Multi-Module Projects

```
my-project/
├── pom.xml                 # Parent POM
├── core/
│   ├── pom.xml
│   └── src/
│       ├── main/java/
│       └── test/java/
├── cli/
│   ├── pom.xml
│   └── src/
│       ├── main/java/
│       └── test/java/
```

Each module is a separate Maven project.

**Lessons:**
- Module-per-unit works for large projects
- Build tool orchestrates modules
- Clear dependency management (POMs)
- Standard structure within modules

### 7.4 Nx Monorepo (TypeScript/JavaScript)

```
my-project/
├── nx.json
├── apps/
│   └── cli/
└── libs/
    ├── graph/
    │   ├── src/
    │   ├── test/
    │   └── README.md
    ├── parser/
    │   ├── src/
    │   ├── test/
    │   └── README.md
```

Each "lib" is a publishable unit.

**Lessons:**
- Tooling is critical (Nx understands lib boundaries)
- Dependency graph visualization
- Affected tests detection
- Clear app vs. lib distinction

---

## 8. Decision Framework

### 8.1 When Brick-First Makes Sense

**Strong indicators:**

✅ **Agent-heavy development** - Agents need clear context boundaries
✅ **Strong architectural vision** - You want physical enforcement of design
✅ **Modular system** - Bricks may become separate packages
✅ **Team ownership** - Different teams own different bricks
✅ **Greenfield project** - No migration cost
✅ **High architectural discipline** - Team values clarity over convention

### 8.2 When Traditional Structure Makes Sense

**Strong indicators:**

✅ **Conventional Python project** - Standard tools, standard expectations
✅ **Small codebase** - Overhead not worth it
✅ **Low modularity** - Everything tightly coupled anyway
✅ **Existing project** - Migration cost too high
✅ **External contributors** - Familiar structure lowers barrier
✅ **Quick prototyping** - Don't know final architecture yet

### 8.3 When Hybrid Makes Sense

**Strong indicators:**

✅ **Transitioning to brick model** - Gradual adoption
✅ **Want brick benefits without restructure** - Tooling over structure
✅ **Mixed team preferences** - Some want traditional, some want brick-first
✅ **Uncertain about commitment** - Want to experiment first

---

## 9. Recommendations for JIG

### 9.1 Current State Assessment

JIG is currently:
- ✅ Well-structured traditional Python project
- ✅ Clear brick boundaries (logical, not physical)
- ✅ Small enough to navigate easily
- ✅ Established workflows
- ✅ Intent nodes in jig/ directory

**Migration cost:** High (2-4 weeks)
**Current pain:** Low (project is navigable)

### 9.2 Recommendation: Hybrid Approach (Phase 1)

**Don't migrate the file structure yet.**

Instead:

1. **Keep brick definitions in jig/bricks/**
   - We already created these
   - Low cost, high value

2. **Build brick-aware tooling**
   ```bash
   jigy brick list                    # List all bricks
   jigy brick show graph-core         # Show brick details
   jigy brick deps graph-core         # Show dependencies
   jigy brick check graph-core        # Validate boundaries
   jigy brick context graph-core      # Load agent context
   ```

3. **Enforce boundaries via linting**
   - Check imports against brick.yaml dependencies
   - Warn on boundary violations
   - Gradually tighten rules

4. **Provide virtual views**
   - Agent tooling loads brick context from traditional structure
   - Human tooling shows brick-filtered file lists

**Benefit:** All the advantages of bricks, without migration cost

### 9.3 Future: Full Brick-First (Phase 2)

**If and when:**
- JIG becomes a platform (multiple projects use it)
- Bricks need to be published separately
- Team grows (ownership becomes important)
- Agent workflows become primary development mode

**Then:** Migrate to full brick-first structure

**Migration strategy:**
1. Create `bricks/` directory structure
2. Use git mv to preserve history
3. Set up import aliases
4. Update build configuration
5. Migrate one brick at a time
6. Keep both structures working during transition
7. Cut over when all bricks migrated

---

## 10. Conclusion

### 10.1 The Core Tension

Brick-first file organization embodies a fundamental tension:

**Logical Architecture vs. Physical Convention**

- Bricks are logical architectural units
- File systems are physical organizational tools
- Should physical structure mirror logical structure?

**The answer depends on your values:**

- Value **architectural clarity** → Brick-first
- Value **conventional simplicity** → Traditional
- Value **both** → Hybrid

### 10.2 What Brick-First Provides

✅ **Physical enforcement** of architectural boundaries
✅ **Cognitive clarity** - one brick = one directory
✅ **Agent safety** - context boundaries are directory boundaries
✅ **Extraction ease** - bricks can become packages
✅ **Ownership clarity** - teams own directories
✅ **Dependency visibility** - imports cross directories explicitly
✅ **Parallel development** - minimal file conflicts

### 10.3 What Brick-First Costs

❌ **Migration effort** - significant refactoring for existing projects
❌ **Build complexity** - non-standard Python structure
❌ **Tooling configuration** - IDEs need setup
❌ **Shared artifacts** - need special handling
❌ **Integration tests** - need special location
❌ **Learning curve** - unfamiliar to new developers
❌ **Package distribution** - more complex than traditional

### 10.4 The Pragmatic Path

For most projects:

1. **Start with logical bricks** (brick definitions, tooling)
2. **Enforce boundaries via linting** (policy, not structure)
3. **Provide brick context views** (virtual views over traditional structure)
4. **Migrate to physical brick-first** only if/when:
   - Project grows significantly
   - Agent workflows dominate
   - Bricks need separate publication
   - Team ownership becomes critical

**Brick-first file organization is powerful—but use it when the benefits outweigh the costs.**

---

## References

- **Conway's Law**: Melvin Conway, 1967
- **Domain-Driven Design**: Eric Evans, 2003
- **Clean Architecture**: Robert C. Martin, 2012
- **The Architecture of Open Source Applications**, Vol. 1 & 2
- **Rust Cargo Book**: https://doc.rust-lang.org/cargo/reference/workspaces.html
- **Nx Monorepo**: https://nx.dev/concepts/more-concepts/applications-and-libraries
- **Go Modules**: https://go.dev/blog/using-go-modules

---

**Document Status:** Exploratory - not a directive, but a thorough analysis to inform decision-making.

**Next Steps:**
1. Review with architect
2. Decide on approach for JIG
3. If hybrid: implement brick-aware tooling
4. If brick-first: create migration plan
5. Document chosen approach for contributors