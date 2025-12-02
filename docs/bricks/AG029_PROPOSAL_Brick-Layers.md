# AG029: Brick Layers - Architectural Stratification (Proposal)

**Date:** 2025-12-01
**Status:** Proposal
**Related:** A001 (Core Artifacts Contract), AG020 (Bricks as Partitions), AG028 (Brick Detection Workflow)

---

## Context

Bricks partition the function space (AG020), and brick dependencies are derived from the implementation graph: if any function in B-core-utils calls any function in B-validation, then B-core-utils depends on B-validation.

However, **dependency direction is currently unconstrained**. This allows:
- Circular dependencies between bricks (B-auth ↔ B-users)
- Unclear build/work order (which brick should be implemented first?)
- Hidden architectural coupling (foundation code depending on high-level features)
- Difficulty reasoning about system structure

**The problem:** While bricks partition code spatially (what functions belong together), they don't organize it temporally (what should be built first) or hierarchically (what depends on what).

**Additional problem:** Brick IDs using sequential numbers (B-001, B-002) provide no semantic meaning. Looking at B-003 tells you nothing about what that brick does.

---

## Proposal

### Core Concept: Architectural Layers

**Add explicit layering to brick definitions:**

Each brick SHALL have a `layer` number (0, 1, 2, ...) that defines its position in the architectural hierarchy.

**Layer constraint:** A brick at layer N MAY depend only on bricks at layers 0..(N-1), or other bricks at layer N if N=0.

**Stratification property:**
- Layer 0: Foundation bricks with no dependencies on higher layers (external libraries OK, other layer 0 bricks OK if no cycles)
- Layer 1: Bricks that depend only on layer 0
- Layer 2: Bricks that depend on layers 0-1
- Layer N: Bricks that depend on layers 0..(N-1)

**Flat architecture:** ALL bricks MAY be assigned layer 0 to effectively disable layering constraints (valid but provides no stratification benefits).

**Work sequencing:** Development, testing, and refactoring SHALL proceed from lowest layer upward.

**Semantic brick IDs:** Brick IDs SHALL use the format `B-{kebab-case-name}` instead of `B-{number}` to provide semantic meaning at a glance.

---

## Decision

### 1. Brick Definition Changes

**Updated bricks.yaml schema:**

```yaml
bricks:
  - id: B-core-utils
    name: Core Utilities
    layer: 0          # NEW FIELD (REQUIRED)
    units:
      - M-jig.utils.io
      - M-jig.utils.yaml_utils

  - id: B-impl-graph
    name: Implementation Graph Core
    layer: 1          # Depends only on B-core-utils (layer 0)
    units:
      - M-jig.impl_graph.graph
      - M-jig.impl_graph.builder

  - id: B-cli
    name: CLI Interface
    layer: 2          # Depends on B-core-utils, B-impl-graph
    units:
      - M-jig.cli.main
```

**Field contract (additions to A001 Section 4):**

**`id` field format change:**
- `id` (string, REQUIRED): Format SHALL be `B-{kebab-case-name}` (e.g., `B-core-utils`, `B-cli-interface`)
- Kebab case: lowercase words separated by hyphens
- Semantic: ID should indicate brick purpose (not sequential number)
- Examples: `B-auth`, `B-user-management`, `B-rest-api`

**New `layer` field:**
- `layer` (integer, REQUIRED): SHALL be non-negative integer (0, 1, 2, ...)
- `layer` (semantics): SHALL reflect the architectural depth of the brick
- `layer: 0` (foundation): Brick MAY depend on other layer 0 bricks (no cycles) or external libraries, but NOT on higher layers
- `layer: N` (dependent): Brick MAY depend only on bricks at layers < N

**Excluded fields:**
- `depends_on` - SHALL NOT be present (still derived from implementation graph)
- Layer dependencies are validated, not declared

**Migration note:** Existing brick IDs using `B-001`, `B-002` format are deprecated. Projects adopting this proposal SHALL migrate to semantic kebab-case IDs.

---

### 2. Validation Rules (Addition to A001 Section 10)

**New validation: Layer Constraint Compliance**

```python
def validate_layer_constraints(bricks, implementation_graph):
    """Validate that brick dependencies respect declared layers."""

    # Derive actual brick dependencies from implementation graph
    brick_deps = derive_brick_dependencies(implementation_graph)

    # Check each brick's dependencies respect layer constraints
    violations = []

    for brick in bricks:
        brick_layer = brick["layer"]
        dependencies = brick_deps.get(brick["id"], set())

        for dep_brick_id in dependencies:
            dep_brick = find_brick(dep_brick_id)
            dep_layer = dep_brick["layer"]

            # Constraint: can only depend on lower layers (or same layer if layer 0)
            if dep_layer > brick_layer:
                violations.append({
                    "brick": brick["id"],
                    "layer": brick_layer,
                    "depends_on": dep_brick_id,
                    "dep_layer": dep_layer,
                    "violation": f"Layer {brick_layer} brick depends on layer {dep_layer} brick"
                })
            elif dep_layer == brick_layer and brick_layer != 0:
                violations.append({
                    "brick": brick["id"],
                    "layer": brick_layer,
                    "depends_on": dep_brick_id,
                    "dep_layer": dep_layer,
                    "violation": f"Layer {brick_layer} brick depends on same-layer brick (only allowed at layer 0)"
                })

    return violations
```

**Validation SHALL check:**

1. **Layer field presence:** All bricks SHALL have a `layer` field (REQUIRED)
2. **Layer non-negative:** All layer values SHALL be >= 0
3. **Brick ID format:** All brick IDs SHALL match pattern `B-[a-z0-9-]+` (kebab-case)
4. **Layer constraint:** For brick B at layer L:
   - All bricks that B depends on SHALL have layer < L
   - Exception: Layer 0 bricks MAY depend on other layer 0 bricks (no cycles)
   - Derived dependencies (from impl graph) SHALL respect declared layers
5. **No circular dependencies:** Cycles SHALL be detected and rejected (including within layer 0)

**Error severity (all are ERRORS, not warnings):**
- Missing `layer` field: ERROR (brick definition invalid)
- Invalid `layer` value: ERROR (must be non-negative integer)
- Invalid brick ID format: ERROR (must be kebab-case)
- Layer constraint violation: ERROR (architectural contract broken)
- Circular dependency: ERROR (at any layer, including layer 0)

---

### 3. Layer 0 Special Constraints

**Layer 0 bricks are the foundation:**

```yaml
- id: B-core-utils
  name: Core Utilities
  layer: 0
  units:
    - M-jig.utils.io
    - M-jig.utils.yaml_utils
```

**Layer 0 constraint:**
- MAY depend on other layer 0 bricks (they form the foundation together)
- SHALL NOT depend on bricks in higher layers (layer 1+)
- MAY depend on external libraries (standard library, pip packages)
- SHALL NOT have circular dependencies (cycles detected and rejected)

**Rationale:** Layer 0 forms a "foundation layer" of cooperating bricks. They can use each other's functionality, but form a directed acyclic graph (DAG) among themselves.

**Examples:**

**Valid layer 0 dependencies:**
```
B-data-models (layer 0) → B-core-utils (layer 0) ✓
B-validation (layer 0) → B-data-models (layer 0) ✓
B-core-utils (layer 0) → [no internal deps] ✓
```

**Invalid layer 0 dependencies:**
```
B-data-models (layer 0) ↔ B-validation (layer 0) ✗ (cycle)
B-core-utils (layer 0) → B-cli (layer 2) ✗ (upward dependency)
```

**Flat architecture:** If ALL bricks are layer 0, this effectively disables layering (all bricks at foundation level). This is valid but provides no stratification benefits. Cycles are still rejected.

---

### 4. Impact on A001 Core Artifacts Contract

**Section 4: Brick Definitions** - Update `id` format and add `layer` field:

```yaml
bricks:
  - id: B-auth-session          # CHANGED: kebab-case instead of B-001
    name: Authentication & Session Management
    layer: 1                    # ADDED: layer field (REQUIRED)
    units:
      - M-auth.session
      - M-auth.tokens
```

**Field contract changes:**
- `id` (string, REQUIRED): Format `B-{kebab-case-name}` (was `B-{number}`)
- `layer` (integer, REQUIRED): Non-negative integer indicating architectural layer
- Layer 0 = foundation (may depend on other layer 0 bricks or external libraries)
- Layer N = depends only on layers 0..(N-1)

**Section 6.1: Intent Graph** - Brick nodes include layer:

```json
{"id":"B-auth-session","type":"brick","name":"Auth & Session","layer":1,"file":"jig/bricks.yaml"}
```

**Note:** Layer IS included in intent-graph.ndjson because:
- It's human-authored metadata about architectural intent
- It's useful for visualization and querying
- It's small (one integer per brick)
- It doesn't create circular dependencies (it's declarative, not derived)

**Section 9: Derivation Contract** - Update:

Brick dependencies are still derived from implementation graph, but:
- Dependencies SHALL be validated against declared layers
- Layer violations SHALL be reported as errors
- Layer assignment is NOT derived (it's declared by humans)

**Section 7: ID Format Contract** - Update brick ID format:

```
| Type | Format | Example | Notes |
|------|--------|---------|-------|
| Brick | B-{kebab-case} | B-auth, B-core-utils | Semantic name (was B-{number}) |
```

**Section 10: Validation Contract** - Add layer validation:

8. **Brick ID format:** All brick IDs SHALL match `B-[a-z0-9-]+` (kebab-case)
9. **Layer presence:** All bricks SHALL have a `layer` field (REQUIRED)
10. **Layer constraint:** All brick dependencies SHALL respect layer hierarchy (dep_layer < brick_layer, OR both at layer 0 with no cycles)
11. **Circular dependencies:** Cycles SHALL be detected and rejected at all layers (including layer 0)

---

### 5. Work Sequencing by Layer

**Principle:** Work proceeds from lowest layer upward.

**Rationale:**
- Layer 0 bricks are prerequisites for everything else
- Can't implement layer N until layer N-1 is complete (dependencies!)
- Testing follows same order (can't test layer 2 until layer 1 works)
- Refactoring is safer when done bottom-up (changes propagate upward)

**Implementation in CLI:**

Work planning SHALL prioritize by layer:
1. Group work units by brick
2. Group bricks by layer
3. Execute lowest layer first
4. Within a layer, order by dependencies (if any)
5. Within independent bricks, parallel execution is safe

**Example work sequence:**

```
Layer 0: [B-core-utils, B-data-models] (parallel, both layer 0)
  ↓
Layer 1: [B-parser, B-validator] (parallel, both depend on L0)
  ↓
Layer 2: [B-cli] (depends on B-parser, B-validator)
```

---

### 6. CLI Command Changes

#### 6.1 `jigy validate bricks` - Enhanced Validation

**Current:**
```bash
$ jigy validate bricks
Validating brick partition... ✓
Validating no class splits... ✓
Validating unit references... ✓
```

**Proposed:**
```bash
$ jigy validate bricks
Validating brick partition... ✓
Validating no class splits... ✓
Validating unit references... ✓
Validating brick ID format... ✓
Validating layer constraints... ✓
  B-core-utils (layer 0): No dependencies ✓
  B-impl-graph (layer 1): Depends on [B-core-utils] (all layer 0) ✓
  B-cli (layer 2): Depends on [B-core-utils, B-impl-graph] (all layer <2) ✓
```

**Error example:**
```bash
$ jigy validate bricks
Validating brick ID format... ✗

ERROR: Invalid brick ID format:
  B-001: Must use kebab-case format (e.g., B-core-utils)

Validating layer constraints... ✗

ERROR: Layer constraint violations detected:

  B-impl-graph (layer 1) depends on B-cli (layer 2)
    → F-jig.impl_graph.builder.build calls F-jig.cli.main.run
    → Violation: Layer 1 cannot depend on layer 2
    → Fix: Either raise B-impl-graph to layer 3, or lower B-cli to layer 0

  B-core-utils (layer 0) depends on B-validation (layer 1)
    → F-jig.utils.io.read_file calls F-jig.validation.intent.validate
    → Violation: Layer 0 cannot depend on layer 1
    → Fix: Move B-validation to layer 0, or refactor dependency
```

**Validation output SHALL include:**
- Which bricks violate layer constraints
- What the actual dependency is (F → F call)
- What layers are involved
- Suggested fixes

---

#### 6.2 New Command: `jigy layers` - Layer Visualization

**Purpose:** Visualize brick layer structure.

```bash
$ jigy layers
```

**Output:**

```
Brick Layer Structure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Layer 0: Foundation (2 bricks)
─────────────────────────────────────────────
  B-core-utils: Core Utilities (23 functions)
  B-data-models: Data Models (15 functions)

Layer 1: Core Logic (3 bricks)
─────────────────────────────────────────────
  B-impl-graph: Implementation Graph Core (31 functions)
    ↓ depends on: B-core-utils

  B-validation: Artifact Validation (28 functions)
    ↓ depends on: B-core-utils, B-data-models

  B-analyzers: Language Analyzers (18 functions)
    ↓ depends on: B-core-utils, B-impl-graph

Layer 2: Interface (1 brick)
─────────────────────────────────────────────
  B-cli: CLI Interface (12 functions)
    ↓ depends on: B-core-utils, B-impl-graph, B-validation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 6 bricks, 3 layers, 127 functions
Dependency graph: DAG ✓ (no cycles)
```

**Options:**

```bash
# Show only layer summary
jigy layers --summary

# Show dependencies in detail
jigy layers --verbose

# Export as DOT for visualization
jigy layers --export-dot > bricks.dot
```

---

#### 6.3 `jigy brick status` - Show Layer Context (Future)

**Proposed enhancement:**

```bash
$ jigy brick status B-impl-graph
```

**Output includes layer context:**

```
B-impl-graph: Implementation Graph Core
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Layer: 1 (Core Logic)
Functions: 31
Specs implemented: S-015, S-016, S-017

Dependencies (layer 0):
  B-core-utils: Core Utilities
    ↓ F-jig.impl_graph.builder.build → F-jig.utils.io.read_file

Dependents (layer 2):
  B-cli: CLI Interface
    ↑ F-jig.cli.main.rebuild → F-jig.impl_graph.builder.build

Layer constraint: ✓ Valid
  All dependencies are in layer 0 (< 1)
```

---

#### 6.4 Work Planning Commands (Future)

**New command: `jigy work plan`**

**Purpose:** Generate work plan respecting layer order.

```bash
$ jigy work plan --incomplete-specs
```

**Output:**

```
Work Plan: Implement Incomplete Specifications
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1: Layer 0 (Foundation)
  • S-001: File I/O utilities (B-core-utils)
  • S-002: YAML parsing (B-core-utils)
  Status: 2 specs, estimated 4 hours

Phase 2: Layer 1 (Core Logic)  [BLOCKED: Phase 1 incomplete]
  • S-015: AST parsing (B-impl-graph)
  • S-016: Call graph extraction (B-impl-graph)
  • S-023: Spec validation (B-validation)
  Status: 3 specs, estimated 8 hours

Phase 3: Layer 2 (Interface)  [BLOCKED: Phase 2 incomplete]
  • S-030: CLI rebuild command (B-cli)
  Status: 1 spec, estimated 2 hours

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 6 specs, 3 phases, estimated 14 hours
```

**Sequencing logic:**
1. Group specs by brick
2. Group bricks by layer
3. Order phases by layer (0, 1, 2, ...)
4. Within layer, suggest parallel work if independent
5. Mark phases as blocked if lower layers incomplete

---

### 7. Layer Assignment Heuristics

**How should layers be assigned to bricks?**

**Manual assignment is primary** (human declares architectural intent).

**But we can suggest layers** based on dependency analysis:

```bash
$ jigy layers suggest
```

**Algorithm:**

```python
def suggest_layers(bricks, implementation_graph):
    """Suggest layer assignments based on dependency structure."""

    # 1. Derive brick dependencies
    brick_deps = derive_brick_dependencies(implementation_graph)

    # 2. Topological sort of brick dependency graph
    topo_order = topological_sort(brick_deps)

    # 3. Assign layers by longest path from root
    layers = {}
    for brick in topo_order:
        if not brick_deps[brick]:
            # No dependencies → layer 0
            layers[brick] = 0
        else:
            # Layer = max(dependency layers) + 1
            dep_layers = [layers[dep] for dep in brick_deps[brick]]
            layers[brick] = max(dep_layers) + 1

    return layers
```

**Example output:**

```bash
$ jigy layers suggest

Suggested layer assignments based on dependencies:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

B-core-utils: Core Utilities
  Current layer: (not set)
  Suggested: 0 (no dependencies)

B-data-models: Data Models
  Current layer: (not set)
  Suggested: 0 (no dependencies)

B-impl-graph: Implementation Graph Core
  Current layer: (not set)
  Suggested: 1 (depends on B-core-utils at layer 0)

B-cli: CLI Interface
  Current layer: (not set)
  Suggested: 2 (depends on B-impl-graph at layer 1, B-validation at layer 1)

Apply suggestions? [y/N]
```

**Use cases:**
- Initial brick creation (discover structure, suggest layers)
- Validation (check if current layers match dependency structure)
- Refactoring (re-suggest layers after code changes)

---

### 8. Integration with Brick Detection (AG028)

**AG028 proposes `jigy brick propose` for discovering bricks.**

**Layer integration:**

When discovering new bricks, also suggest layers:

```bash
$ jigy brick propose --mode=discover
```

**Enhanced workflow:**

Phase 1-3: Same as AG028 (cluster detection, semantic validation)

**Phase 4: Layer Suggestion** (NEW)

```
Suggesting layer assignments...
  Cluster 0 (Core Utils): layer 0 (no dependencies)
  Cluster 1 (Parser): layer 1 (depends on Cluster 0)
  Cluster 2 (CLI): layer 2 (depends on Cluster 1)
```

**Phase 5: User Review**

```
Brick Proposal Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

+ CREATE (3 new bricks)

  B-core-utils: Core Utilities
    Layer: 0 (suggested)
    Functions: 23
    Dependencies: none

  B-parser: Parser Core
    Layer: 1 (suggested)
    Functions: 31
    Dependencies: B-core-utils

  B-cli: CLI Interface
    Layer: 2 (suggested)
    Functions: 12
    Dependencies: B-core-utils, B-parser

Apply this proposal? [y/N]
```

**Layer suggestions are included in brick proposals.**

---

### 9. Examples

#### Example 1: JIG System Itself

**Current bricks.yaml (old format, without layers):**

```yaml
bricks:
  - id: B-001
    name: JIG Core Decorators
    units: [M-jig.__init__]

  - id: B-002
    name: CLI Interface
    units: [M-jig.cli.main, M-jig.cli.validate]

  - id: B-003
    name: Artifact Validation
    units: [M-jig.validation.intent, M-jig.validation.bricks]

  - id: B-004
    name: Implementation Graph Core
    units: [M-jig.impl_graph.graph, M-jig.impl_graph.builder]
```

**Proposed with layers and semantic IDs:**

```yaml
bricks:
  - id: B-decorators
    name: JIG Core Decorators
    layer: 0  # Foundation: decorators have no dependencies
    units: [M-jig.__init__]

  - id: B-impl-graph
    name: Implementation Graph Core
    layer: 0  # Foundation: graph structures are independent
    units: [M-jig.impl_graph.graph, M-jig.impl_graph.builder]

  - id: B-validation
    name: Artifact Validation
    layer: 1  # Uses graph structures from B-impl-graph
    units: [M-jig.validation.intent, M-jig.validation.bricks]

  - id: B-cli
    name: CLI Interface
    layer: 2  # Uses validation and graphs
    units: [M-jig.cli.main, M-jig.cli.validate]
```

**Dependency structure:**

```
Layer 0:  [B-decorators]  [B-impl-graph]
                ↓               ↓
Layer 1:        [B-validation]
                      ↓
Layer 2:            [B-cli]
```

**Work order:**
1. Implement B-decorators, B-impl-graph (can be parallel)
2. Implement B-validation (depends on B-impl-graph)
3. Implement B-cli (depends on B-validation, B-impl-graph)

---

#### Example 2: Web Application

```yaml
bricks:
  # Layer 0: Foundation
  - id: B-db-models
    name: Database Models
    layer: 0
    units: [M-models]

  - id: B-core-utils
    name: Core Utilities
    layer: 0
    units: [M-utils.crypto, M-utils.validation]

  # Layer 1: Domain Logic
  - id: B-auth
    name: Authentication
    layer: 1
    units: [M-auth.session, M-auth.tokens]
    # Depends on: B-db-models (models), B-core-utils (crypto)

  - id: B-user-mgmt
    name: User Management
    layer: 1
    units: [M-users.crud, M-users.permissions]
    # Depends on: B-db-models (models), B-core-utils (validation)

  # Layer 2: API
  - id: B-rest-api
    name: REST API
    layer: 2
    units: [M-api.endpoints, M-api.middleware]
    # Depends on: B-auth, B-user-mgmt

  # Layer 3: Interface
  - id: B-web-ui
    name: Web Interface
    layer: 3
    units: [M-web.routes, M-web.templates]
    # Depends on: B-rest-api
```

**Dependency graph:**

```
Layer 0:  [B-db-models]  [B-core-utils]
              ↓        ↓      ↓       ↓
Layer 1:      [B-auth]    [B-user-mgmt]
                  ↓            ↓
Layer 2:         [B-rest-api]
                      ↓
Layer 3:         [B-web-ui]
```

**Benefits:**
- Clear build order (DB models first, then domain logic, then API, then UI)
- Prevents leaky abstractions (API can't depend on UI, domain can't depend on API)
- Enables parallel work (Auth and Users are independent within layer 1)
- Documents architecture (3-tier structure is explicit)

---

#### Example 3: Layer Violation Detection

**Scenario:** Developer accidentally introduces upward dependency.

**Code change:**

```python
# src/utils/crypto.py (B-core-utils, layer 0)
from auth.session import get_current_user  # OOPS: depends on layer 1!

def hash_password(password: str) -> str:
    user = get_current_user()  # BAD: layer 0 calling layer 1
    salt = user.salt
    return hashlib.sha256(password + salt).hexdigest()
```

**Detection:**

```bash
$ jigy validate bricks

Validating layer constraints... ✗

ERROR: Layer constraint violations detected:

  B-core-utils (layer 0) depends on B-auth (layer 1)
    → F-utils.crypto.hash_password calls F-auth.session.get_current_user
    → Violation: Layer 0 cannot depend on layer 1
    → Fix: Refactor to pass salt as parameter instead of fetching current user

Validation failed.
```

**Fix:**

```python
# src/utils/crypto.py (B-core-utils, layer 0)
def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256(password + salt).hexdigest()
```

**Result:** Layer 0 brick no longer depends on layer 1. Validation passes.

---

### 10. Benefits

**Architectural clarity:**
- Explicit stratification makes system structure visible
- Layer diagram shows dependencies at a glance
- New developers understand architecture faster

**Dependency discipline:**
- Prevents upward dependencies (foundation depending on features)
- Prevents circular dependencies (enforced by layer constraint)
- Makes accidental coupling visible immediately

**Work sequencing:**
- Clear build order (layer 0 first, then layer 1, etc.)
- Enables parallel work (bricks within same layer can be parallel)
- Prioritizes foundation work (can't build layer 2 without layer 1)

**Testing strategy:**
- Test layer 0 first (no dependencies to mock)
- Test layer N with layer N-1 as fixtures
- Integration tests run top-down (layer N → 0)

**Refactoring safety:**
- Changes in layer 0 → test all layers
- Changes in layer N → test only layers ≥ N
- Impact analysis is bounded by layer structure

**Incremental development:**
- Implement MVP as layer 0 only (core functions)
- Add layer 1 for basic features
- Add layer 2 for advanced features
- Each layer is independently usable

**AI agent guidance:**
- Agents work layer by layer (bottom-up)
- Agents can't introduce upward dependencies
- Layer violations are caught in validation (before merge)

---

### 11. Constraints and Trade-offs

**Constraints this imposes:**

1. **Manual layer assignment:** Developers must declare layers (can't be fully automated)
2. **Refactoring overhead:** Moving code between layers requires validation
3. **Layer count growth:** Deep systems may have many layers (complexity)
4. **Granularity tension:** Too fine → many layers, too coarse → weak constraint

**Trade-offs:**

**Pro:**
- Explicit architecture
- Dependency discipline
- Work ordering

**Con:**
- Additional metadata to maintain
- Validation complexity
- Refactoring friction

**When to use layers (stratified architecture):**
- Large systems (>10 bricks)
- Multi-developer teams
- Long-lived codebases
- AI-assisted development
- Clear architectural boundaries needed

**When flat architecture may be appropriate (all layer 0):**
- Small projects (<5 bricks)
- Prototypes (architecture not settled)
- Exploratory codebases
- Rapid iteration without constraints

**Decision:** Make `layer` field REQUIRED in A001. Projects that don't need stratification can set all bricks to `layer: 0` (flat architecture). This keeps the schema simple while supporting both use cases.

---

### 12. Migration Path

**For existing projects adopting layers:**

**Step 1: Analyze current structure**

```bash
$ jigy layers suggest
```

This analyzes the implementation graph and suggests layers based on actual dependencies.

**Step 2: Review suggestions**

```
Suggested layer assignments:
  B-core-utils: layer 0 (no dependencies)
  B-data-models: layer 0 (no dependencies)
  B-parser: layer 1 (depends on B-core-utils)
  B-cli: layer 2 (depends on B-core-utils, B-parser)
```

**Step 3: Apply to bricks.yaml**

```bash
$ jigy layers suggest --apply
```

Or manually edit `jig/bricks.yaml` to add `layer` fields.

**Step 4: Validate**

```bash
$ jigy validate bricks
```

If violations exist, either:
- Fix code (remove upward dependencies)
- Adjust layers (raise dependent bricks to higher layers)

**Step 5: Commit**

```bash
$ git add jig/bricks.yaml
$ git commit -m "docs: Add layer assignments to brick definitions"
```

**For new projects:**

Layers are assigned during initial brick creation:

```bash
$ jigy brick propose --mode=discover
```

Brick proposals include suggested layers automatically.

---

### 13. Future Enhancements

#### 13.1 Layer-Aware Visualization

**Generate dependency graph with layers:**

```bash
$ jigy layers visualize --output layers.svg
```

Creates SVG showing bricks arranged by layer (vertical stratification).

#### 13.2 Layer Budget Constraints

**Limit layer depth:**

```yaml
# .jig/config.yaml
layer_constraints:
  max_depth: 4  # No brick can be layer 5 or higher
  max_fanout: 8  # No brick can depend on >8 bricks
```

**Rationale:** Prevent over-layering (too deep → brittle, too wide → coupled)

#### 13.3 Layer-Scoped Context (AI Agents)

**Give AI agent context for layer N:**

```
You are working on B-rest-api (layer 2).
You may use functions from:
  - B-core-utils (layer 0): Core Utilities
  - B-auth (layer 1): Authentication
  - B-user-mgmt (layer 1): User Management

You MUST NOT use functions from:
  - B-web-ui (layer 3): Web Interface (higher layer)
```

**Prevents agents from introducing layer violations.**

#### 13.4 Layer-Based Test Suites

```bash
# Run tests for layer 0 only (fast, no dependencies)
pytest --jig-layer=0

# Run tests for layers 0-2 (excludes layer 3+)
pytest --jig-layer=0..2
```

**Use case:** CI pipelines can test foundation first, then incrementally add layers.

---

## Consequences

### What This Enables

1. **Architectural visibility:** Layers make system structure explicit
2. **Dependency discipline:** Upward dependencies are prevented
3. **Work sequencing:** Clear order for development/testing/refactoring
4. **Parallel work:** Bricks within same layer can be developed independently
5. **Impact analysis:** Changes in layer N affect only layers ≥ N
6. **AI guidance:** Agents work layer by layer, respecting constraints
7. **Incremental development:** Build foundation first, add features layer by layer

### What This Constrains

1. **Layer assignment required:** All bricks must declare a layer
2. **Dependency direction:** Can only depend on lower layers
3. **Refactoring friction:** Moving code may change layers
4. **Validation overhead:** Layer constraints checked on every build

### What Remains Open

1. **How many layers is appropriate?** (Project-dependent)
2. **Should layers map to teams?** (Organizational question)
3. **Can layers be automatically derived?** (Yes, via `jigy layers suggest`, but human approval recommended)
4. **Should layer violations be warnings or errors?** (Proposal: errors, but configurable)

---

## Decisions Made

1. **Layer 0 bricks MAY depend on each other** (cycles still rejected)
   - Rationale: Allows foundation layer to have internal structure
   - Validation: Cycle detection applies to all layers including 0

2. **Layers ARE included in intent-graph.ndjson**
   - Rationale: Architectural metadata useful for visualization
   - Format: `{"id":"B-cli","type":"brick","layer":2,...}`

3. **Layer field is REQUIRED**
   - Rationale: Forces architectural thinking
   - Escape hatch: Set all bricks to `layer: 0` for flat architecture

4. **External dependencies don't affect layer**
   - Rationale: Only internal brick dependencies matter
   - Example: Layer 0 brick can use pip packages freely

5. **Brick IDs use kebab-case format**
   - Format: `B-{kebab-case-name}` (e.g., `B-core-utils`, `B-rest-api`)
   - Rationale: Semantic IDs readable at a glance
   - Migration: Existing `B-001` format is deprecated

6. **Named layers NOT supported**
   - Rationale: Integer layers are sufficient, less complexity
   - Future: Could add aliases if needed, but start simple

7. **Validation errors, not warnings**
   - Rationale: Layer constraints are architectural contracts
   - Enforcement: Validation failures block builds/commits

---

## Implementation Checklist

### Phase 1: Core Implementation
- [ ] Update A001 to include `layer` field in brick definitions (REQUIRED)
- [ ] Update A001 to change brick ID format to `B-{kebab-case}`
- [ ] Update brick YAML schema validation to require `layer`
- [ ] Add brick ID format validation (kebab-case pattern)
- [ ] Implement layer constraint validation in `jigy validate bricks`
- [ ] Update intent graph generator to include `layer` in brick nodes
- [ ] Write tests for layer validation logic
- [ ] Write tests for brick ID format validation

### Phase 2: CLI Commands
- [ ] Enhance `jigy validate bricks` with layer violation reporting
- [ ] Implement `jigy layers` command for layer visualization
- [ ] Implement `jigy layers suggest` for layer assignment suggestions
- [ ] Update `jigy brick propose` to suggest layers (AG028 integration)

### Phase 3: Documentation
- [ ] Update A001 with layer specification and brick ID format change
- [ ] Add layer examples to documentation
- [ ] Write migration guide for existing projects (layers + ID format)
- [ ] Create tutorial on layer-driven development
- [ ] Document brick ID naming conventions (kebab-case best practices)

### Phase 4: Ecosystem Integration
- [ ] Update visualization tools to show layers
- [ ] Add layer-aware context for AI agents
- [ ] Layer-scoped test suites
- [ ] Layer budgets and constraints

---

## References

- **A001:** Core Artifacts Contract (brick definitions)
- **AG020:** Bricks as Partitions (brick fundamentals)
- **AG028:** Brick Detection Workflow (brick discovery)
- **AG019:** Irreducible Core (S-F-T triangle)
- **Parnas (1972):** "On the Criteria To Be Used in Decomposing Systems into Modules" (information hiding, layering)
- **Martin (2000):** "Design Principles and Design Patterns" (Acyclic Dependencies Principle)
- **Simon (1962):** "The Architecture of Complexity" (hierarchical systems)

---

## Approval Status

**Status:** Proposal (awaiting review)

**Reviewers:** TBD

**Next steps:**
1. Review this proposal
2. Validate layer concept on JIG codebase
3. Implement phase 1 (core validation)
4. Accept or reject based on practical experience

---

_Layers make architecture explicit, dependencies intentional, and work sequential._
