---
title: "Clean Breaks and Cross-Brick Refactoring"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1763934216
created_human: "2025-11-23 15:43 CST"
parent: "[[AG001_Alignment-Graph-Bricks]]"
children: ['[[AG007_Clean-Breaks-Quick-Reference]]']
---
# Clean Breaks and Cross-Brick Refactoring

**How to make breaking changes across Brick boundaries during active development**

---

## The Tension

**Brick philosophy says:**
- Versioned schemas for shared artifacts
- Migration paths for breaking changes
- Backward compatibility for interfaces
- Stable contracts between Bricks

**Development reality says:**
- I don't know the right answer yet (iterating)
- Only one user (me!)
- Everything's in git (can always revert)
- Want to fail hard and fix everything at once
- No feature flags, no dual implementations, no technical debt

**Question:** How do Bricks work in "burn the ships" mode?

---

## Answer: Development Mode vs. Production Mode

Bricks support **two operational modes**:

### Production Mode (External Consumers)
- Versioned interfaces
- Migration scripts
- Backward compatibility
- Deprecation warnings
- Gradual rollouts

**Use when:**
- Library with external users
- Published API
- Multiple teams consuming your Bricks
- Can't coordinate simultaneous changes

### Development Mode (Single Team / Pre-1.0)
- Clean breaks
- Fail everywhere immediately
- Fix all at once
- No compatibility layer
- Burn the ships

**Use when:**
- Single developer or tight team
- Full control of codebase
- Pre-1.0 / active design iteration
- Can change everything simultaneously

**For JIG (currently): We're in Development Mode.**

---

## Why Bricks HELP with Clean Breaks

Traditional codebases:
```
❌ Change interface → Silent failures everywhere
❌ Grep for usages → Miss indirect calls
❌ Fix what you find → Miss what you don't find
❌ Deploy → Runtime errors
```

With Bricks:
```
✅ Change interface → Validation shows ALL affected Bricks
✅ Brick boundaries explicit → Know exactly what to fix
✅ Fix all Brick interfaces → Validation passes
✅ Fail fast → No silent drift
```

**Bricks make clean breaks EASIER because they make dependencies EXPLICIT.**

---

## The Clean Break Protocol for Bricks

### Phase 1: Decide to Break

**Document the decision:**

```markdown
# In active Delta: PLAN_refactor_graph_api.md

#DECISION "Burn ships: Graph.load_from_dir() now requires Config object"

**Current:** `Graph.load_from_dir(intent_dir: Path) -> Graph`
**New:** `Graph.load_from_dir(config: JigConfig) -> Graph`

**Rationale:**
- Need access to annotation_dirs from config
- Current approach requires passing paths separately
- Simpler to pass whole config object

**Tradeoffs:**
- Breaking change to BRICK-GRAPH public interface
- All consumers (CLI, Index Builder) must update
- No backward compatibility

**Affected Bricks:**
- BRICK-GRAPH (interface change)
- BRICK-CLI (consumer, must update)
- BRICK-INDEX (consumer, must update)

**Migration:** Change all call sites simultaneously (3 files)
```

---

### Phase 2: Make the Break

**1. Update the interface Brick:**

```python
# src/jig/core/graph.py (BRICK-GRAPH)

class Graph:
    @staticmethod
    def load_from_dir(config: JigConfig) -> "Graph":  # ← Changed signature
        """Load graph from intent directory.

        Args:
            config: JIG configuration (provides intent_dir, annotation_dirs)

        Returns:
            Loaded graph

        Raises:
            ValueError: If config invalid
        """
        intent_dir = config.intent_dir
        # ... implementation
```

**2. Update Brick definition:**

```yaml
# bricks/graph-core.brick.yaml

brick:
  id: BRICK-GRAPH
  version: "2.0.0"  # ← Bump major version (breaking change)

interface:
  public:
    functions:
      - name: load_from_dir
        signature: "load_from_dir(config: JigConfig) -> Graph"
        stability: stable
        breaking_changes:
          - version: "2.0.0"
            date: "2025-11-23"
            description: "Now requires JigConfig instead of Path"
            old_signature: "load_from_dir(intent_dir: Path) -> Graph"
```

**3. Let it fail everywhere:**

```bash
$ jigy brick validate BRICK-GRAPH

✓ BRICK-GRAPH itself is valid

Cross-Brick Impact Analysis:
============================

❌ BRICK-CLI depends on changed interface:
   - cli/status.py:42: graph = Graph.load_from_dir(Path("jig/"))
   - cli/index.py:67: graph = Graph.load_from_dir(intent_dir)
   - cli/validate.py:28: graph = Graph.load_from_dir(config.intent_dir)

❌ BRICK-INDEX depends on changed interface:
   - core/index_builder.py:234: graph = Graph.load_from_dir(project_root / "jig")

Breaking Change Detected!
--------------------------
BRICK-GRAPH interface changed in version 2.0.0
3 call sites in 2 dependent Bricks require updates

Suggested Fix:
  1. Update BRICK-CLI call sites (3 files)
  2. Update BRICK-INDEX call sites (1 file)
  3. Re-run validation

$ echo $?
1  # Exit with error
```

**Perfect! We want this to fail loudly.**

---

### Phase 3: Fix All Consumers

**Update each affected Brick:**

```python
# src/jig/cli/status.py (BRICK-CLI)

def status():
    config = load_config()  # ← Get config
    graph = Graph.load_from_dir(config)  # ← Use new signature
    # ...

# src/jig/cli/index.py (BRICK-CLI)

def rebuild():
    config = load_config()  # ← Get config
    graph = Graph.load_from_dir(config)  # ← Use new signature
    # ...

# src/jig/core/index_builder.py (BRICK-INDEX)

def build_graph_index(project_root: Path) -> RebuildResult:
    config = load_config(project_root / "jig.toml")  # ← Get config
    graph = Graph.load_from_dir(config)  # ← Use new signature
    # ...
```

---

### Phase 4: Validate Clean

```bash
$ jigy brick validate --all

Validating All Bricks (Development Mode)
=========================================

✓ BRICK-UTILS: No changes
✓ BRICK-CONFIG: No changes
✓ BRICK-PARSER: No changes
✓ BRICK-VALIDATOR: No changes
✓ BRICK-GRAPH: Interface changed (v2.0.0)
✓ BRICK-SCANNER: No changes
✓ BRICK-ANNOT-VALIDATOR: No changes
✓ BRICK-INDEX: Updated for BRICK-GRAPH v2.0.0
✓ BRICK-DECOMPOSE: No changes
✓ BRICK-CLI: Updated for BRICK-GRAPH v2.0.0

Cross-Brick Dependencies:
-------------------------
✓ All call sites updated
✓ No breaking changes pending
✓ All Brick interfaces consistent

System Health: Excellent (100/100)

Ready to commit? (y/n)
```

---

### Phase 5: Commit the Break

```bash
$ git add -A
$ git commit -m "refactor(graph)!: load_from_dir now requires JigConfig

BREAKING CHANGE: Graph.load_from_dir() signature changed

Before:
  Graph.load_from_dir(intent_dir: Path) -> Graph

After:
  Graph.load_from_dir(config: JigConfig) -> Graph

Rationale: Need access to full config (annotation_dirs, etc.)

Affected Bricks:
  - BRICK-GRAPH v2.0.0 (interface change)
  - BRICK-CLI (3 call sites updated)
  - BRICK-INDEX (1 call site updated)

Migration: All consumers updated simultaneously.
No backward compatibility. Burn the ships.

Validation: jigy brick validate --all ✓"
```

**Note the conventional commit format:**
- `!` indicates breaking change
- `BREAKING CHANGE:` in body
- Clear before/after
- Document what changed

---

## Cross-Brick Refactoring Mode

Sometimes you need to change multiple Bricks simultaneously to make an architectural shift.

**Example:** Extracting a new Brick from an existing one.

### Scenario: Split BRICK-GRAPH into BRICK-GRAPH-DATA and BRICK-GRAPH-QUERIES

**Current:**
```
BRICK-GRAPH (696 LOC)
  - Graph/Edge/Subsystem classes (data)
  - load_from_dir (loading)
  - get_dependencies, find_path (queries)
```

**Target:**
```
BRICK-GRAPH-DATA (400 LOC)
  - Graph/Edge/Subsystem classes
  - load_from_dir

BRICK-GRAPH-QUERIES (300 LOC)
  - get_dependencies, find_path
  - Depends on BRICK-GRAPH-DATA
```

### Workflow: Cross-Brick Refactoring

**1. Enter Cross-Brick Mode:**

```bash
$ jigy brick refactor start \
    --bricks BRICK-GRAPH \
    --plan "Split graph into data and queries Bricks"

Cross-Brick Refactoring Session Started
========================================

Affected Bricks: BRICK-GRAPH
Validation: SUSPENDED (will check on complete)

Working in: cross-brick mode
Restrictions: RELAXED (can modify multiple Bricks)

Plan: Split graph into data and queries Bricks

Commands:
  jigy brick refactor status    # Show what changed
  jigy brick refactor validate  # Check if changes valid
  jigy brick refactor complete  # Finish and validate
  jigy brick refactor abort     # Abandon changes
```

**2. Make structural changes:**

```bash
# Create new Brick definitions
$ cat > bricks/graph-data.brick.yaml << EOF
brick:
  id: BRICK-GRAPH-DATA
  name: "Graph Data Structures"
  version: "1.0.0"
  split_from: BRICK-GRAPH v1.0.0
  ...
EOF

$ cat > bricks/graph-queries.brick.yaml << EOF
brick:
  id: BRICK-GRAPH-QUERIES
  name: "Graph Query Operations"
  version: "1.0.0"
  split_from: BRICK-GRAPH v1.0.0
  ...
EOF

# Move code
$ mkdir -p src/jig/core/graph/
$ mv src/jig/core/graph.py src/jig/core/graph/data.py
$ git mv ... # reorganize files

# Update imports everywhere
# (Agent or refactoring tool does this)
```

**3. Check status:**

```bash
$ jigy brick refactor status

Cross-Brick Refactoring Status
===============================

Changes:
  - BRICK-GRAPH: Deleted (split into 2 Bricks)
  - BRICK-GRAPH-DATA: Created (new)
  - BRICK-GRAPH-QUERIES: Created (new)

File Movements:
  - src/jig/core/graph.py → src/jig/core/graph/data.py
  - (new) src/jig/core/graph/queries.py

Import Updates Required:
  - BRICK-CLI: 8 files need import updates
  - BRICK-INDEX: 2 files need import updates
  - BRICK-VALIDATOR: 1 file needs import update

Tests:
  ⚠ Test Bricks need restructuring
  ⚠ 4 test files reference old structure

Recommendation: Update imports, then validate
```

**4. Fix all dependencies:**

```python
# Old imports (everywhere)
from jig.core.graph import Graph, Edge, Subsystem
from jig.core.graph import get_dependencies, find_path

# New imports (updated everywhere)
from jig.core.graph.data import Graph, Edge, Subsystem
from jig.core.graph.queries import get_dependencies, find_path
```

**5. Validate refactoring:**

```bash
$ jigy brick refactor validate

Cross-Brick Refactoring Validation
===================================

Structural Changes:
  ✓ BRICK-GRAPH-DATA properly formed
  ✓ BRICK-GRAPH-QUERIES properly formed
  ✓ Dependency graph valid (QUERIES depends on DATA)

Boundary Compliance:
  ✓ All imports updated
  ✓ No dangling references to old BRICK-GRAPH
  ✓ All Brick definitions consistent

Test Coverage:
  ✓ All tests migrated to new structure
  ✓ Test coverage maintained (78%)

Breaking Changes:
  ⚠ External import paths changed:
    Old: from jig.core.graph import Graph
    New: from jig.core.graph.data import Graph

  Impact: Any external code importing jig.core.graph will break

  Recommendation: This is a clean break. Acceptable for dev mode.

System Health: Good (85/100)
Ready to complete? (y/n)
```

**6. Complete refactoring:**

```bash
$ jigy brick refactor complete

Cross-Brick Refactoring Complete
=================================

Summary:
  - Split BRICK-GRAPH into 2 Bricks
  - Updated 11 files across 3 dependent Bricks
  - Migrated 4 test files
  - Breaking change: Import paths changed

Commit message generated:
---
refactor(core)!: split graph Brick into data and queries

BREAKING CHANGE: Graph module restructured

Split BRICK-GRAPH (696 LOC) into:
  - BRICK-GRAPH-DATA (400 LOC): Data structures, loading
  - BRICK-GRAPH-QUERIES (300 LOC): Traversal, search

Import changes:
  Before: from jig.core.graph import Graph
  After: from jig.core.graph.data import Graph

Rationale: Improve modularity, reduce Brick size

Affected Bricks:
  - BRICK-GRAPH-DATA v1.0.0 (new)
  - BRICK-GRAPH-QUERIES v1.0.0 (new)
  - BRICK-CLI (8 files updated)
  - BRICK-INDEX (2 files updated)
  - BRICK-VALIDATOR (1 file updated)

Migration: All consumers updated simultaneously.
Burn the ships.

Cross-brick refactoring validated: jigy brick refactor validate ✓
---

Create commit? (y/n)
```

---

## Development Mode: No Compatibility Layer

In development mode, **do not create compatibility layers**.

### ❌ Anti-Pattern: Compatibility Shim

```python
# DON'T DO THIS in development mode
def load_from_dir(
    intent_dir_or_config: Path | JigConfig
) -> Graph:
    """Load graph (supports both old and new signatures)."""

    # Detect which signature
    if isinstance(intent_dir_or_config, Path):
        warnings.warn(
            "Passing Path is deprecated, use JigConfig",
            DeprecationWarning
        )
        config = JigConfig(intent_dir=intent_dir_or_config)
    else:
        config = intent_dir_or_config

    return _load_graph(config)
```

**Problems:**
- Complexity: Now you have two code paths
- Testing: Must test both paths
- Cognitive load: Which is the "real" way?
- Technical debt: When do you remove the shim?
- Obscures design: Hard to see clean architecture

### ✅ Best Practice: Clean Break

```python
# DO THIS in development mode
def load_from_dir(config: JigConfig) -> Graph:
    """Load graph from configuration.

    Args:
        config: JIG configuration

    Returns:
        Loaded graph

    Raises:
        TypeError: If config is not JigConfig (old code path removed)
    """
    if not isinstance(config, JigConfig):
        raise TypeError(
            f"load_from_dir requires JigConfig, got {type(config).__name__}. "
            f"Old signature load_from_dir(Path) removed in v2.0.0. "
            f"Update call site to use JigConfig."
        )

    return _load_graph(config)
```

**Benefits:**
- Simplicity: One code path
- Fail fast: Breaks immediately at call site
- Clear error: Tells you exactly what to fix
- No debt: Nothing to remove later
- Clean design: Interface is what it is

---

## Brick Validation for Clean Breaks

### Enhanced Validation Commands

**Standard validation (single Brick):**
```bash
$ jigy brick validate BRICK-GRAPH
# Checks: This Brick's boundaries, coupling, etc.
```

**Cross-Brick validation (check dependencies):**
```bash
$ jigy brick validate BRICK-GRAPH --check-dependents

Validating: BRICK-GRAPH
=======================

✓ Brick health: Good

Checking Dependents:
--------------------

❌ BRICK-CLI (3 call sites broken)
  - cli/status.py:42: TypeError expected
  - cli/index.py:67: TypeError expected
  - cli/validate.py:28: TypeError expected

❌ BRICK-INDEX (1 call site broken)
  - core/index_builder.py:234: TypeError expected

Breaking Change Impact:
-----------------------
2 Bricks affected by interface change
4 call sites need updates

Abort or fix? (a/f)
```

**Full system validation:**
```bash
$ jigy brick validate --all

# Validates every Brick
# Checks all cross-Brick dependencies
# Reports system-wide health
```

---

## Integration with taskCleanBreak

The Brick system **enhances** the Clean Break Protocol:

### taskCleanBreak: Complete Deletion

From `agents/taskCleanBreak.md`:
- Delete all old code paths completely
- Remove old tests entirely
- Fail loudly with clear errors
- Full commitment to new approach

### How Bricks Help:

**1. Know What to Delete**

Brick boundaries tell you exactly what's old:

```yaml
# In Brick definition
deprecated:
  - function: old_parse_method
    removed_in: v2.0.0
    replacement: new_parse_method
    last_commit: abc123f
```

**2. Know What Depends On It**

Validation shows all consumers:

```bash
$ jigy brick validate BRICK-PARSER --show-consumers

BRICK-PARSER Consumers:
-----------------------
- BRICK-INDEX (uses parse_ostc_node)
- BRICK-GRAPH (uses OSTCNode)
- BRICK-VALIDATOR (uses parse_ostc_node)

If you delete parse_ostc_node, 3 Bricks break.
```

**3. Fail Loudly Everywhere**

After deletion, validation shows ALL breaks:

```bash
$ jigy brick validate --all

❌ BRICK-INDEX: Missing import 'parse_ostc_node'
❌ BRICK-GRAPH: Missing type 'OSTCNode'
❌ BRICK-VALIDATOR: Missing import 'parse_ostc_node'

Fix all 3 Bricks to use new parser interface.
```

**4. Document the Decision**

In your Delta:

```markdown
#DECISION "Burn ships: Deleted old OSTC parser"

**Removed:**
- BRICK-PARSER old implementation (core/old_parser.py)
- 12 old tests (tests/unit/test_old_parser.py)
- Legacy YAML frontmatter support

**Added:**
- New ripgrep-based parser (core/parser.py)
- 15 new tests (faster, clearer)
- Simpler API: parse_ostc_node(path: Path) -> OSTCNode

**Breaking Changes:**
- Removed parse_with_yaml_fallback()
- Removed legacy_mode parameter
- Removed backwards compatibility shims

**Bricks Updated:**
- BRICK-PARSER v2.0.0 (clean implementation)
- BRICK-INDEX (updated to new API)
- BRICK-GRAPH (updated to new OSTCNode)
- BRICK-VALIDATOR (updated to new API)

**Validation:** jigy brick validate --all ✓

#LEARNED "Bricks make clean breaks easier"
Knowing exact boundaries meant I could delete confidently.
Validation showed every dependent call site.
Fixed all 3 Bricks in 20 minutes. No surprises.
```

---

## Practical Workflow

### Daily Development with Clean Breaks

**Morning: Decide to refactor**
```bash
$ jigy brick show BRICK-GRAPH
# Review what's in the Brick

$ jigy brick validate BRICK-GRAPH --show-dependents
# See what depends on it

# Document decision
$ cat >> deltas/active/dev/PLAN_graph_refactor.md << EOF
#DECISION "Refactor graph loading to use config object"
...
EOF
```

**Midday: Make the break**
```bash
# Change the interface
$ claude
You: @brick-context-graph.md
You: Change Graph.load_from_dir to require JigConfig instead of Path.
     Delete the old signature. Fail loudly if wrong type.

# Let it break
$ jigy brick validate BRICK-GRAPH --check-dependents
# Shows what broke (expected!)
```

**Afternoon: Fix everything**
```bash
# Fix each dependent Brick
$ claude
You: @brick-context-cli.md
You: Update all Graph.load_from_dir calls to pass config.
     There are 3 call sites (validation showed them).

$ claude
You: @brick-context-index.md
You: Update Graph.load_from_dir call to pass config.

# Validate clean
$ jigy brick validate --all
# All green!
```

**Evening: Commit**
```bash
$ git add -A
$ git commit -m "refactor(graph)!: clean break to config-based loading

BREAKING CHANGE: Graph.load_from_dir now requires JigConfig

All consumers updated simultaneously.
Validation: jigy brick validate --all ✓

Closes #123"
```

**No compatibility layer. No feature flags. No hesitation.**

---

## When to Use Each Mode

### Development Mode (Clean Breaks)

**Use when:**
- ✅ Pre-1.0 / active iteration
- ✅ Single developer or tight team
- ✅ Can change entire codebase at once
- ✅ Iterating on architecture
- ✅ Learning what works

**Characteristics:**
- No versioned artifacts (or version is always `dev`)
- Breaking changes anytime
- Fail fast, fix everywhere
- Validation shows impact
- Git is your safety net

### Production Mode (Compatibility)

**Use when:**
- ✅ Published library (1.0+)
- ✅ External consumers
- ✅ Multiple teams
- ✅ Can't coordinate simultaneous changes
- ✅ Stable architecture

**Characteristics:**
- Semver versioning
- Migration scripts
- Deprecation warnings
- Gradual rollouts
- Backward compatibility

### Hybrid Mode (Pre-Release)

**Use when:**
- ✅ Approaching 1.0
- ✅ Limited external users (beta testers)
- ✅ Architecture stabilizing
- ✅ Want some compatibility but not full commitment

**Characteristics:**
- Version artifacts, but allow breaking changes
- Document migrations, but don't automate
- Deprecation notices, but short window
- "Beta" disclaimer

---

## Brick Definition: Development Mode

Mark Bricks as "development mode":

```yaml
# bricks/graph-core.brick.yaml
brick:
  id: BRICK-GRAPH
  name: "Graph Core"
  version: "dev"  # or "0.x.x" for semver pre-1.0
  mode: development

  development_mode:
    allow_breaking_changes: true
    validation:
      fail_on_incompatible_dependents: true  # Fail if consumers break
      require_simultaneous_updates: true     # All must update together
    compatibility:
      enabled: false  # No backward compatibility required
      migration_scripts: false
      deprecation_warnings: false

interface:
  stability: unstable  # Can change anytime
  versioning: none     # Or: semver-pre-1.0

  public:
    functions:
      - name: load_from_dir
        signature: "load_from_dir(config: JigConfig) -> Graph"
        stability: unstable
        can_break: true
        breaking_changes:
          - version: "dev-2025-11-23"
            description: "Changed from Path to JigConfig parameter"
            reason: "Need access to full config"
            migration: "Update all call sites manually"
```

---

## Commands Summary

### New Commands for Clean Breaks

```bash
# Enter cross-Brick refactoring mode
jigy brick refactor start --bricks BRICK-A,BRICK-B --plan "description"

# Check refactoring status
jigy brick refactor status

# Validate cross-Brick changes
jigy brick refactor validate

# Complete and commit refactoring
jigy brick refactor complete

# Abort refactoring
jigy brick refactor abort

# Validate with dependent impact
jigy brick validate BRICK-X --check-dependents

# Validate entire system
jigy brick validate --all

# Show what depends on a Brick
jigy brick show BRICK-X --dependents

# Set Brick to development mode
jigy brick set-mode BRICK-X --mode development
```

---

## Checklist: Clean Break Across Bricks

When making a breaking change:

- [ ] Document decision in Delta with `#DECISION`
- [ ] Identify affected Bricks (`jigy brick validate --check-dependents`)
- [ ] If cross-Brick, start refactoring session (`jigy brick refactor start`)
- [ ] Make the breaking change in interface Brick
- [ ] Update Brick version (if versioned)
- [ ] Delete old code path completely (no compatibility layer)
- [ ] Add error for old usage (fail loudly)
- [ ] Run validation to see what broke (`jigy brick validate --all`)
- [ ] Fix all dependent Bricks (shown by validation)
- [ ] Update all tests (delete old, write new)
- [ ] Validate clean (`jigy brick validate --all`)
- [ ] Commit with breaking change marker (`feat!:` or `refactor!:`)
- [ ] Document learning in Delta with `#LEARNED`

**No lingering compatibility. No "just in case" code. Burn the ships.**

---

## Benefits of Clean Breaks with Bricks

### Without Bricks (Traditional)
```
Change interface
  ↓
? What broke? (grep, hope, pray)
  ↓
? Fix what you found (miss some)
  ↓
? Tests pass? (maybe)
  ↓
Deploy
  ↓
Runtime errors (surprise!)
```

### With Bricks + Clean Breaks
```
Change interface
  ↓
Validation shows EXACTLY what broke
  ↓
Fix ALL listed call sites
  ↓
Validation passes (complete)
  ↓
Commit
  ↓
No runtime surprises
```

**Bricks give you confidence to break things.**

---

## Example: Real JIG Refactoring

### Scenario: Change Annotation Syntax

**Current:** `@jig C-CLI-001 implements:S-JIG-002 subsystem:core`
**New:** `@jig[C-CLI-001] implements(S-JIG-002) subsystem(core)`

**Decision:**
```markdown
#DECISION "Burn ships: New annotation syntax"

Old: @jig C-CLI-001 implements:S-JIG-002
New: @jig[C-CLI-001] implements(S-JIG-002)

Rationale: Clearer, more parseable, supports nesting
Tradeoff: All annotations in codebase must update
```

**Execution:**

1. **Update parser (BRICK-SCANNER):**
```python
# Old
ANNOTATION_PATTERN = r'@jig\s+([A-Z]-[A-Z]+-\d+)'

# New (delete old, fail on old syntax)
ANNOTATION_PATTERN = r'@jig\[([A-Z]-[A-Z]+-\d+)\]'

def parse_annotation_line(line: str) -> Annotation | None:
    match = re.search(ANNOTATION_PATTERN, line)
    if match:
        return Annotation(...)

    # Fail loudly if old syntax detected
    if re.search(r'@jig\s+[A-Z]-[A-Z]+-\d+', line):
        raise ValueError(
            f"Old annotation syntax detected: {line}\n"
            f"Update to new syntax: @jig[NODE-ID] implements(...)  \n"
            f"See docs/migration/annotation-syntax-v2.md"
        )

    return None
```

2. **Validation shows impact:**
```bash
$ jigy brick validate BRICK-SCANNER --check-dependents

✓ BRICK-SCANNER implementation valid

⚠ Breaking change in annotation syntax

Files with old syntax:
  - src/jig/cli/main.py:1
  - src/jig/cli/init.py:1
  - src/jig/cli/status.py:1
  - src/jig/core/graph.py:1
  ... (25 files total)

Run: jigy migrate annotations --to-v2
  (Will update all annotations automatically)
```

3. **Automated migration:**
```bash
$ jigy migrate annotations --to-v2

Migrating Annotations to v2 Syntax
===================================

Found 47 annotations in 25 files

Updating:
  ✓ src/jig/cli/main.py (1 annotation)
  ✓ src/jig/cli/init.py (1 annotation)
  ...

Complete!
  - 47 annotations updated
  - 25 files modified
  - 0 errors

Review changes: git diff
```

4. **Validate clean:**
```bash
$ jigy brick validate --all
✓ All Bricks valid
✓ All annotations use v2 syntax
✓ System health: Excellent
```

5. **Commit:**
```bash
$ git add -A
$ git commit -m "refactor(scanner)!: new annotation syntax

BREAKING CHANGE: Annotation syntax changed

Old: @jig C-CLI-001 implements:S-JIG-002
New: @jig[C-CLI-001] implements(S-JIG-002)

All 47 annotations across 25 files updated.

Migration: jigy migrate annotations --to-v2 (automated)
No backward compatibility. Clean break.

BRICK-SCANNER v2.0.0"
```

**Zero backward compatibility. Zero feature flags. Clean.**

---

## Summary

**Key Principles:**

1. **Development Mode ≠ Production Mode**
   - Dev mode: Clean breaks, fail fast, fix everywhere
   - Prod mode: Compatibility, migrations, gradual rollout

2. **Bricks HELP Clean Breaks**
   - Explicit boundaries show what to change
   - Validation shows ALL impact
   - No surprises

3. **Cross-Brick Refactoring**
   - Intentionally violate boundaries for systemic changes
   - Use refactoring mode
   - Validate before completing

4. **No Compatibility Layers in Dev**
   - Delete old code completely
   - Fail loudly with clear errors
   - Fix everything at once
   - Burn the ships

5. **Validation is Your Safety Net**
   - Shows exactly what broke
   - Confirms when fixed
   - Enables confident breaking changes

**For JIG (currently):**
- We're in Development Mode
- Clean breaks are the right choice
- Bricks make them safer and faster
- Git is our rollback mechanism

**When JIG reaches 1.0:**
- Switch to Production Mode
- Add versioning and migrations
- Maintain backward compatibility
- But the Brick structure remains

---

## Related Documents

- `taskCleanBreak.md` - Clean Break Protocol (general)
- `Brick-Context-Enforcement-Proposal.md` - Brick boundaries and enforcement
- `Shared-Artifacts-And-Bricks.md` - Interface contracts
- `Brick-Analysis-JIG-System.md` - JIG's 10 Bricks

---

**TL;DR:**

In development mode:
1. Make breaking changes without compatibility layers
2. Let validation show what broke
3. Fix all at once
4. Commit the clean break

Bricks make this **easier** because boundaries are explicit and violations are detected automatically.

**Burn the ships. Fix the fleet. Sail forward.**
