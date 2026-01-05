---
title: "PROPOSAL: Integrating Bricks and Alignment Graph into JIG"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1764025026
created_human: "2025-11-24 16:57 CST"
parent: "[[J013_JIG-Concept-v7]]"
children: []
---
# PROPOSAL: Integrating Bricks and Alignment Graph into JIG

_Unifying Nearly Decomposable Systems with Bounded Agent Context_

**Date:** 2025-11-24
**Status:** Design Proposal - Awaiting Direction
**Author:** Claude + Jim Meyer

---

## Executive Summary

This proposal explores integrating the **Alignment Graph (AG)** and **Bricks** concepts into JIG v7. The integration offers profound potential: unifying JIG's decomposability metrics with Bricks' agent-safety boundaries, creating a system that both **measures** architectural integrity and **enforces** it through bounded contexts.

**The central tension:** JIG v7 has **Subsystems** for organizational structure. Bricks serve a similar but distinct purpose. This proposal examines whether to:
1. **Replace** subsystems with Bricks
2. **Merge** the concepts (Bricks ARE leaf subsystems)
3. **Layer** them (Bricks operate within subsystems)

**Key innovations from integration:**
- Agent-safe bounded contexts (from Bricks)
- Static analysis of actual code structure (from AG Dependency Layer)
- Drift detection as alignment measurement (from AG)
- Maintained decomposability metrics (from JIG)
- Cross-cutting constraint validation (from JIG v7's X model)

---

## 1. Conceptual Analysis

### 1.1 What JIG v7 Has

| Concept | Description | Purpose |
|---------|-------------|---------|
| **OSTCX Model** | Outcomes, Specifications, Tests, Code, Constraints | Five representations of system truth |
| **Subsystems** | Nested organizational units (e.g., `identity.auth`) | Coupling metrics, modularity measurement |
| **@jig Annotations** | Code markers linking to Intent nodes | Explicit Intent→Code traceability |
| **Constraints (X)** | Query-based predicates over OSTC graph | Cross-cutting concerns without graph pollution |
| **Deltas** | Branch-scoped working documents | Temporal knowledge capture |
| **Harvest Pipeline** | Extract markers → synthesize → integrate | Knowledge lifecycle management |
| **graph-index.yaml** | Node registry with relationships | Fast lookups, decomposability analysis |

### 1.2 What Bricks/AG Adds

| Concept | Description | Purpose |
|---------|-------------|---------|
| **Bricks** | Bounded architectural units (Intent + Code + Tests) | Agent context fencing, ownership clarity |
| **Brick Context Contract** | What agents can/cannot see in a Brick | Safe, bounded agent operation |
| **Dependency Layer** | Auto-generated from static analysis | Ground truth of actual code structure |
| **Test Layer** | Test discovery + coverage mapping | Verification ground truth |
| **Alignment Checking** | Graph queries measuring drift | Objective drift detection |
| **Architecture Mode** | View of Brick-level design only | Design thinking without implementation noise |
| **Implementation Mode** | Full Brick context for coding | Coding within architectural constraints |

### 1.3 Key Overlaps

| JIG Concept | Bricks/AG Equivalent | Relationship |
|-------------|---------------------|--------------|
| Subsystem | Brick | Similar organizational unit, different emphasis |
| @jig annotation | AG Dependency Layer | JIG is explicit, AG is discovered |
| graph-index.yaml | Alignment Graph | Similar structure, AG adds layers |
| Constraint validation | Alignment checking | Both detect violations |
| T- nodes | AG Test Layer | Similar, AG adds coverage analysis |

### 1.4 Key Differences

| Aspect | JIG v7 | Bricks/AG |
|--------|--------|-----------|
| **Primary focus** | Measuring decomposability | Enforcing bounded contexts |
| **Code discovery** | Explicit (@jig annotations) | Automatic (static analysis) |
| **Agent support** | None | Core design goal |
| **Test integration** | Annotation-based | Discovery + coverage |
| **File organization** | Traditional (`jig/`, `src/`, `tests/`) | Optional brick-first (`bricks/brick-name/`) |
| **Coupling metrics** | Central feature | Present but secondary |
| **Constraints** | First-class (X nodes) | Implicit in alignment checking |

---

## 2. The Subsystems vs Bricks Question

This is the central design decision. Three options:

### Option A: Replace Subsystems with Bricks

**Model:** Bricks become the primary organizational unit. What was `subsystem:identity.auth` becomes Brick `identity-auth` (or nested `identity/auth`).

**Implications:**
- All JIG tooling rewritten around Bricks
- Nested subsystems → nested Bricks (or flat Bricks with naming convention)
- Coupling metrics apply to Bricks
- Brick Context Contract becomes core feature
- File organization could shift to brick-first

**Pros:**
- Conceptual simplicity (one organizational unit)
- Agent safety built into core model
- Ownership clarity (team owns Brick)

**Cons:**
- Major conceptual change to JIG
- "Brick" terminology may be unfamiliar
- Loses "subsystem" terminology from decomposability literature (Simon)

### Option B: Bricks ARE Leaf Subsystems

**Model:** Subsystems remain the hierarchical organization. Leaf subsystems (those without children) are Bricks. Parent subsystems are containers.

```
identity/              → Subsystem (container)
├── auth/              → Brick (leaf subsystem)
│   └── brick.yaml
└── user/              → Brick (leaf subsystem)
    └── brick.yaml
```

**Implications:**
- Subsystem hierarchy preserved for coupling metrics
- Only leaf subsystems have Brick properties (context contract, file mapping)
- Parent subsystems aggregate metrics but don't have Brick contracts
- Compatible with existing JIG tooling

**Pros:**
- Backward compatible with JIG v7 subsystem model
- Preserves Herbert Simon "nearly decomposable" terminology
- Hierarchical metrics still work
- Bricks add agent safety without replacing existing concepts

**Cons:**
- Two overlapping concepts (some subsystems are Bricks, some aren't)
- Potential confusion about when to use which term
- Parent subsystems aren't "fenced" for agents

### Option C: Bricks Operate Within Subsystems

**Model:** Subsystems and Bricks are orthogonal. A subsystem can contain multiple Bricks. Bricks can span parts of subsystems (cross-cutting).

```
identity/                    → Subsystem
├── core/                    → Part of BRICK-IDENTITY-CORE
├── auth/                    → BRICK-IDENTITY-AUTH
└── shared/                  → Part of BRICK-IDENTITY-CORE

# Or even cross-cutting:
BRICK-VALIDATION            → Contains code from multiple subsystems
```

**Implications:**
- Maximum flexibility
- Subsystems for metrics, Bricks for context
- Bricks can cross subsystem boundaries (for cross-cutting concerns)

**Pros:**
- Most flexible
- Allows gradual Brick adoption
- Doesn't force 1:1 mapping

**Cons:**
- Most complex mental model
- Potential for Brick/Subsystem misalignment
- Harder to reason about boundaries

---

## 3. Design Questions for Direction

Before proceeding, I need your decisions on these questions:

### Q1: Subsystem/Brick Relationship

**Which model do you prefer?**

- [ ] **A: Replace** - Bricks replace subsystems entirely
- [ ] **B: Merge** - Bricks ARE leaf subsystems (recommended)
- [ ] **C: Layer** - Bricks and subsystems are orthogonal
- [ ] **Other** - Describe your vision

**Considerations:**
- Option B preserves JIG's decomposability heritage while adding agent safety
- Option A is cleaner but requires more migration
- Option C is most flexible but most complex

---

### Q2: Code Discovery Model

JIG uses explicit `@jig` annotations. AG uses static analysis (parsing imports, building call graphs automatically).

**How should Code nodes be discovered?**

- [ ] **Annotations only** - Keep current @jig model (explicit, curated)
- [ ] **Static analysis only** - Auto-discover from code (ground truth, no annotation burden)
- [ ] **Both** - Static analysis for dependency layer, annotations for Intent links (recommended)
- [ ] **Annotations with static validation** - @jig annotations validated against static analysis

**Considerations:**
- Static analysis shows what actually exists (no drift)
- Annotations show what we intend to track (curated)
- Both together: static analysis for structure, annotations for Intent links

---

### Q3: Brick Definition Location

**Where should Brick definitions live?**

- [ ] **Brick-first organization** - Each Brick is a directory (`bricks/brick-name/brick.yaml, code/, tests/, intent/`)
- [ ] **Separate definitions** - `jig/bricks/brick-name.brick.yaml` with file mappings (like current approach)
- [ ] **Inline in subsystems.yaml** - Brick properties added to existing subsystem definitions
- [ ] **Hybrid** - New projects use brick-first, existing projects use separate definitions

**Considerations:**
- Brick-first provides physical enforcement but requires file reorganization
- Separate definitions work with existing structure but boundaries are "virtual"
- Current JIG uses separate `jig/` directory

---

### Q4: Agent Context Enforcement

**How strictly should Brick context boundaries be enforced?**

- [ ] **Hard enforcement** - Tools literally only provide Brick contents to agents
- [ ] **Soft enforcement** - Full access but validation warns on boundary violations
- [ ] **Tooling-based** - Context builders respect boundaries, but no runtime enforcement
- [ ] **Progressive** - Start soft, tighten over time

**Considerations:**
- Hard enforcement requires sophisticated tooling
- Soft enforcement is easier to implement
- Current AI agents don't have native Brick awareness

---

### Q5: Test Layer Enhancement

**Should JIG add AG's Test Layer features?**

- [ ] **Keep current** - Test nodes via @jig annotations only
- [ ] **Add coverage analysis** - Integrate coverage tools (pytest-cov) into graph
- [ ] **Add test discovery** - Auto-discover tests like AG does
- [ ] **Full AG test layer** - Discovery + coverage + verification edges (recommended)

**Considerations:**
- Coverage analysis provides objective verification metrics
- Auto-discovery reduces annotation burden
- Current @jig T- annotations are explicit but require maintenance

---

### Q6: Alignment Graph as Primary Structure

**Should the Alignment Graph (AG) become JIG's primary data model?**

- [ ] **No** - Keep graph-index.yaml as-is, add Brick features
- [ ] **Partial** - Add Dependency Layer from static analysis
- [ ] **Yes** - Full AG model (Intent + Dependency + Test + Brick layers)
- [ ] **Rename** - graph-index.yaml IS the Alignment Graph, just enhance it

**Considerations:**
- Current graph-index.yaml is similar to AG's Intent Layer
- Adding Dependency Layer (from static analysis) would be significant enhancement
- Full AG would require substantial tooling investment

---

### Q7: Terminology

**What should the primary unit be called?**

- [ ] **Brick** - From AG/Bricks literature
- [ ] **Subsystem** - From Simon's decomposability theory
- [ ] **Module** - Generic software term
- [ ] **Component** - Also generic
- [ ] **Domain** - From DDD
- [ ] **Keep both** - Subsystem for metrics, Brick for context

**Considerations:**
- "Brick" is novel but evocative (building blocks)
- "Subsystem" ties to academic literature
- Using both may cause confusion

---

### Q8: Constraints (X) Integration

**How should JIG's Constraint (X) model relate to Bricks?**

- [ ] **Unchanged** - Constraints remain predicates over OSTC graph
- [ ] **Brick-aware** - Constraints can target Bricks by ID
- [ ] **Brick contracts** - Brick Context Contracts become a type of Constraint
- [ ] **All of above** - Constraints, Brick contracts, and Brick-targeted queries

**Considerations:**
- JIG v7's X model is sophisticated and should be preserved
- Brick Context Contracts are similar to Constraints but for agent behavior
- Could unify: "What code must satisfy" (X) + "What agents can access" (Context Contract)

---

## 4. Proposed Integration Model (Pending Your Decisions)

Based on my analysis, here's my **recommended** integration model (subject to your decisions above):

### 4.1 Unified Model: Bricks as Leaf Subsystems

```
Subsystems (hierarchical, for metrics)
└── identity/                      [coupling ratio: 12.5:1]
    ├── auth/                      [Brick: BRICK-IDENTITY-AUTH]
    │   ├── brick.yaml             [Context contract, interfaces]
    │   ├── [Intent nodes]         [O-AUTH-*, S-AUTH-*]
    │   ├── [Code nodes]           [C-AUTH-*]
    │   └── [Test nodes]           [T-AUTH-*]
    └── user/                      [Brick: BRICK-IDENTITY-USER]
        └── ...
```

**Key properties:**
- Parent subsystems aggregate metrics (coupling, modularity)
- Leaf subsystems ARE Bricks with context contracts
- Bricks have all properties: Intent, Code, Tests, Dependencies
- Constraints (X) apply across Bricks via queries

### 4.2 Enhanced Graph Model

```yaml
# graph-index.yaml (enhanced as Alignment Graph)

layers:
  intent:
    nodes: [O-*, S-*]              # Outcomes, Specifications

  code:
    nodes: [C-*]                   # Code nodes (from @jig annotations)
    dependency_graph:               # NEW: from static analysis
      edges: [...]                  # import/call relationships

  test:
    nodes: [T-*]                   # Test nodes (from @jig annotations)
    coverage:                       # NEW: from coverage analysis
      T-AUTH-001:
        covers: [C-AUTH-001, C-AUTH-002]
        line_coverage: 0.87

  brick:
    bricks:
      BRICK-IDENTITY-AUTH:
        subsystem: identity.auth
        intent: [O-AUTH-001, S-AUTH-001, ...]
        code: [C-AUTH-001, C-AUTH-002, ...]
        tests: [T-AUTH-001, T-AUTH-002, ...]
        dependencies: [BRICK-UTILS, BRICK-CONFIG]
        context_contract: {...}

constraints:
  X-HIPAA-001:
    scope:
      bricks: [BRICK-IDENTITY-AUTH, BRICK-STORAGE]  # Brick-targeted
    # ... rest of constraint
```

### 4.3 Brick Definition

```yaml
# jig/bricks/identity-auth.brick.yaml
# OR bricks/identity-auth/brick.yaml (brick-first)

brick:
  id: BRICK-IDENTITY-AUTH
  subsystem: identity.auth
  name: "Identity Authentication"
  version: "1.0.0"
  layer: domain

responsibility: |
  JWT-based authentication with multi-device support.
  Token lifecycle management and session validation.

scope:
  intent:
    outcomes: [O-AUTH-001, O-AUTH-002]
    specifications: [S-AUTH-001, S-AUTH-002, S-AUTH-003]

  code:
    modules:
      - path: src/identity/auth/jwt.py
        nodes: [C-AUTH-001, C-AUTH-002]
      - path: src/identity/auth/session.py
        nodes: [C-AUTH-003, C-AUTH-004]

  tests:
    unit: tests/unit/identity/auth/
    integration: tests/integration/test_auth_*.py
    nodes: [T-AUTH-001, T-AUTH-002, T-AUTH-003]

interface:
  public:
    classes:
      - JWTAuthenticator
      - SessionManager
    functions:
      - authenticate_user(credentials: Credentials) -> Token
      - validate_token(token: str) -> Claims

  internal:
    # Not exposed outside Brick
    - _hash_password
    - _generate_token_id

dependencies:
  bricks:
    - BRICK-UTILS
    - BRICK-CONFIG
  external:
    - cryptography
    - pyjwt

context_contract:
  # For LLM/Agent use
  visible:
    - All code in scope.code
    - All tests in scope.tests
    - All Intent nodes in scope.intent
    - Public interfaces of dependency Bricks

  forbidden:
    - Code outside this Brick
    - Internal details of other Bricks
    - Repository structure outside mapped files

  constraints:
    - "MUST NOT introduce dependencies beyond declared"
    - "MUST maintain public interface signatures"
    - "MUST verify against T-AUTH-* tests"
```

### 4.4 Two Modes Operation

**Architecture Mode** (via `jig arch` or context flag):
- See all Brick definitions and relationships
- See all Constraint definitions
- See all public interfaces
- See decomposability metrics
- **Cannot see**: Implementation code, test code, internal details

**Implementation Mode** (via `jig context --brick BRICK-ID`):
- See full Brick contents (Intent, Code, Tests)
- See public interfaces of dependency Bricks
- See applicable Constraints
- **Cannot see**: Other Bricks' internals, global structure

---

## 5. What Changes in JIG

### 5.1 New Concepts

| Concept | Description |
|---------|-------------|
| **Brick** | Leaf subsystem with context contract |
| **Context Contract** | What agents can/cannot access |
| **Dependency Layer** | Auto-discovered from static analysis |
| **Coverage Layer** | Test coverage mapped to Code nodes |
| **Architecture Mode** | High-level design view |
| **Implementation Mode** | Brick-scoped coding view |

### 5.2 Enhanced Concepts

| Existing | Enhancement |
|----------|-------------|
| **Subsystem** | Leaf subsystems become Bricks |
| **graph-index.yaml** | Becomes full Alignment Graph |
| **@jig annotations** | Validated against static analysis |
| **Constraints (X)** | Can target Bricks by ID |
| **jig validate** | Adds Brick boundary validation |

### 5.3 New Commands

```bash
# Brick management
jig brick list                    # List all Bricks
jig brick show <brick-id>         # Show Brick details
jig brick deps <brick-id>         # Show dependencies
jig brick check <brick-id>        # Validate boundaries

# Context generation
jig context --brick <brick-id>    # Generate agent context
jig context --arch                # Architecture mode context

# Static analysis
jig analyze deps                  # Build dependency layer
jig analyze coverage              # Build coverage layer

# Alignment checking
jig align check                   # Check alignment across layers
jig align drift                   # Detect drift
```

### 5.4 File Structure Options

**Option A: Current structure + brick definitions**
```
jig/
├── outcomes/
├── specifications/
├── constraints/
├── bricks/                       # NEW
│   ├── identity-auth.brick.yaml
│   └── ...
├── graph-index.yaml
└── subsystems.yaml

src/                              # Unchanged
tests/                            # Unchanged
```

**Option B: Brick-first organization**
```
bricks/
├── identity-auth/
│   ├── brick.yaml
│   ├── intent/
│   │   ├── outcomes/
│   │   └── specifications/
│   ├── code/
│   │   ├── jwt.py
│   │   └── session.py
│   └── tests/
│       ├── test_jwt.py
│       └── test_session.py
├── ...

jig/
├── constraints/                  # Cross-cutting, not per-Brick
├── graph-index.yaml
└── config.toml

shared/                           # Shared types, protocols
```

---

## 6. Migration Path

### Phase 1: Add Brick Definitions (Non-Breaking)

1. Create `jig/bricks/` directory
2. Define Brick YAML files for existing leaf subsystems
3. Add `jig brick` commands (list, show, deps)
4. No changes to existing tooling

### Phase 2: Add Dependency Layer

1. Implement static analysis (import/call graph extraction)
2. Store in graph-index.yaml under `layers.dependency`
3. Add `jig analyze deps` command
4. Validate @jig annotations against actual dependencies

### Phase 3: Add Context Generation

1. Implement `jig context --brick <id>` command
2. Output: Markdown context for LLM consumption
3. Respects Brick Context Contract (what's visible/forbidden)
4. Add Architecture Mode (`jig context --arch`)

### Phase 4: Add Boundary Enforcement

1. `jig brick check` validates imports stay within boundaries
2. Add pre-commit hook for boundary checking
3. CI integration for boundary validation

### Phase 5: Add Coverage Layer (Optional)

1. Integrate with pytest-cov
2. Store coverage in graph-index.yaml under `layers.test.coverage`
3. Map coverage to Test and Code nodes
4. Add to alignment checking

### Phase 6: Consider Brick-First Organization (Optional)

1. Only if benefits outweigh migration cost
2. Provide migration tooling
3. Support both structures during transition

---

## 7. Open Questions

### 7.1 Granularity

What's the right size for a Brick?
- **Too small**: Many boundaries, high overhead
- **Too large**: Context too big for agents, weak isolation

**Proposed heuristics:**
- 200-1000 LOC per Brick
- 3-10 public interface items
- Single coherent responsibility
- Fits in LLM context window (~50KB with context)

### 7.2 Shared Code

Where does code that multiple Bricks need live?
- Shared utilities (e.g., types, protocols)
- Cross-cutting concerns (logging, errors)

**Options:**
- Foundation Brick (BRICK-UTILS, BRICK-CONFIG)
- `shared/` directory outside Bricks
- Accept controlled duplication

### 7.3 Integration Tests

Where do tests that span Bricks live?
- Cross-Brick integration tests
- End-to-end tests

**Options:**
- `tests/integration/` outside Bricks
- In orchestrating Brick (e.g., CLI Brick)
- Separate Integration Test Brick

### 7.4 Brick Evolution

How do Bricks change over time?
- Splitting a large Brick
- Merging related Bricks
- Moving code between Bricks

**Proposed:**
- Versioning on Brick definitions
- Migration tooling for refactoring
- Alignment checking catches inconsistencies

---

## 8. What I Need From You

Please provide decisions on the 8 questions in Section 3:

1. **Q1: Subsystem/Brick Relationship** - Replace, Merge, or Layer?
2. **Q2: Code Discovery Model** - Annotations, Static Analysis, or Both?
3. **Q3: Brick Definition Location** - Brick-first, Separate, or Inline?
4. **Q4: Agent Context Enforcement** - Hard, Soft, Tooling, or Progressive?
5. **Q5: Test Layer Enhancement** - Current, Add Coverage, Add Discovery, or Full AG?
6. **Q6: Alignment Graph as Primary** - No, Partial, Yes, or Rename?
7. **Q7: Terminology** - Brick, Subsystem, Module, Component, Domain, or Keep Both?
8. **Q8: Constraints Integration** - Unchanged, Brick-aware, Contracts, or All?

With your decisions, I can:
1. Refine this proposal into a concrete specification
2. Update JIG-Concept to v8 with the integration
3. Define implementation phases
4. Create detailed data model schemas

---

## 9. Summary

**The opportunity:**
Integrating Bricks and AG into JIG creates a system that doesn't just **measure** architectural integrity (decomposability, coupling) but **enforces** it through bounded contexts. This is especially valuable for agent-assisted development, where context boundaries are the primary defense against architectural erosion.

**The challenge:**
JIG already has a mature model (OSTCX + Subsystems + Deltas). Integration must enhance, not complicate. The Subsystem/Brick relationship is the key design decision.

**My recommendation:**
Option B (Bricks ARE leaf subsystems) with:
- Static analysis + annotations for code discovery
- Separate brick definitions (not brick-first) for compatibility
- Progressive enforcement (soft → hard over time)
- Full AG test layer (discovery + coverage)
- graph-index.yaml enhanced as Alignment Graph
- Keep both terms (Subsystem for hierarchy, Brick for leaves)
- Constraints unchanged but Brick-targetable

**Awaiting your direction.**

---

**Document Version:** 0.1.0 (Draft Proposal)
**Next Steps:**
1. Your decisions on Q1-Q8
2. Refined specification based on decisions
3. JIG-Concept v8 draft
