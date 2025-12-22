# Brick and Layer Context for AI Agents

Bricks partition functions into architectural units. Layers stratify bricks vertically. Together they enforce architectural boundaries and dependency discipline.

---

## Bricks: Spatial Partitioning

### The Partition Property

Every function belongs to exactly ONE brick:
- **No gaps** - every function is assigned
- **No overlaps** - no function in multiple bricks
- **Class integrity** - all methods of a class must be in same brick

### Brick Definition

Bricks are defined in `jig/bricks.yaml`:

```yaml
bricks:
  - id: B-core-utils
    name: Core Utilities
    layer: 0
    units:
      - M-utils.io           # All functions in module
      - C-utils.Parser       # All methods of class
      - F-utils.helpers.foo  # Single function
```

**Unit prefixes:**
- `M-{path}` — module (all functions)
- `C-{path}` — class (all methods)
- `F-{path}` — single function

### Brick ID Format

`B-{kebab-case-name}` — semantic naming

- `B-crdt-observe` (descriptive)
- `B-protocol-core` (descriptive)
- NOT `B-001` (numeric IDs deprecated)

### Derived Properties (Not Stored)

Brick properties are computed, not declared:

| Property | Derived From |
|----------|--------------|
| Specs assigned | Functions' `@jig.implements` decorators |
| Dependencies | Call graph (F in brick A calls F in brick B) |
| Public API | Functions called from outside the brick |
| Test coverage | Tests that cover brick's functions |

**Single source of truth:** `bricks.yaml` defines membership only. Everything else is computed.

---

## Layers: Vertical Stratification

### Layer Constraint

**A brick at layer N may depend ONLY on layers 0..(N-1).**

```
Layer 0: [B-core-utils] [B-data-models]    ← Foundation
              ↓               ↓
Layer 1: [B-crdt-core] [B-validation]      ← Core logic
              ↓               ↓
Layer 2: [B-simops] [B-cli]                ← Interface
```

Dependencies flow DOWN. Never up.

### Layer Field

Layer is REQUIRED (integer ≥ 0):

```yaml
bricks:
  - id: B-core-utils
    layer: 0              # Foundation

  - id: B-crdt-core
    layer: 1              # Depends on layer 0

  - id: B-cli
    layer: 2              # Depends on layers 0-1
```

### Layer 0 Special Rules

Layer 0 bricks are foundation:

**MAY depend on:**
- External libraries (stdlib, pip packages)
- Other layer 0 bricks (mutual cooperation allowed)

**MUST NOT depend on:**
- Any brick at layer 1+

**Cycles rejected:** Even within layer 0, circular dependencies are errors.

### Flat Architecture

If ALL bricks are layer 0, layering is effectively disabled. Valid for small projects but provides no stratification benefits. Cycles still rejected.

### Layer Violations are Errors

Layer constraints are enforced, not advisory:
- Upward dependency → ERROR
- Circular dependency → ERROR
- Validation fails → Build fails

---

## Determining Brick Structure

### When to Create a New Brick

Create new brick when:
- Functions form cohesive unit with distinct responsibility
- Clear boundary exists (different concern, different rate of change)
- Dependency isolation is valuable (testing, deployment)

Extend existing brick when:
- Functions naturally belong to existing boundary
- No clear separation of concerns
- Would create artificial split

### When to Determine Layer Assignment

Layer = max(dependency layers) + 1

Or: Use `jigy layers suggest` to compute from actual dependencies.

**Decision process:**
1. List brick's dependencies (what does it call?)
2. Find max layer among dependencies
3. Assign layer = max + 1
4. If no dependencies, layer = 0

---

## FORBIDDEN Bricks (Per-JIGPLAN)

### What FORBIDDEN Means

FORBIDDEN is a per-work-scope constraint, NOT a permanent brick property.

Each JIGPLAN defines which bricks are off-limits for that specific work:

```markdown
## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| CREATE | B-crdt-observe | 1 | New observation layer |
| MODIFY | B-simops-core | 2 | Add observer integration |
| FORBIDDEN | B-protocol-core | 0 | Not in scope |
| FORBIDDEN | B-data-models | 0 | Not in scope |
```

### Why FORBIDDEN Exists

1. **Scope discipline** - Prevents "while I'm here, let me also fix..."
2. **Sub-agent guardrails** - Clear boundaries for automated execution
3. **Change isolation** - Limits blast radius of modifications
4. **Review focus** - Reviewer knows exactly what should/shouldn't change

### FORBIDDEN is Not About Layer

Any brick can be FORBIDDEN regardless of layer:
- Work on layer 0? Other layer 0 bricks might be FORBIDDEN
- Work on layer 2? Some layer 1 bricks might be FORBIDDEN
- The constraint is "don't touch during THIS work"

### Escalation Trigger

If sub-agent discovers it needs to modify a FORBIDDEN brick:
1. STOP immediately
2. Report to orchestration agent or human with rationale
3. Wait for scope revision or alternative approach

---

## Validation

### Brick Validation Rules

- All unit references exist in codebase
- No class split across bricks
- Brick IDs match `B-[a-z0-9-]+`
- Every function assigned to exactly one brick

### Layer Validation Rules

- Every brick has layer field (integer ≥ 0)
- No upward dependencies (layer N → layer M where M ≥ N)
- No circular dependencies at any layer
- Layer 0 bricks don't depend on higher layers

### Validation Commands

```bash
jigy validate        # Check all constraints
jigy layers          # Show layer structure
jigy layers suggest  # Compute layers from dependencies
```

---

## Impact Analysis

### Change Impact by Layer

| Change Location | Test Scope |
|-----------------|------------|
| Layer 0 brick | Test ALL layers |
| Layer N brick | Test layers ≥ N only |

Changes flow upward, never downward.

### Work Sequencing

Build order follows layers:
1. Complete layer 0 first
2. Then layer 1
3. Then layer 2
4. Continue upward

Can't implement layer N until layer N-1 is stable.

---

## Quick Reference

| Concept | Rule |
|---------|------|
| Partition | Every function in exactly one brick |
| Class integrity | All methods in same brick |
| Layer constraint | Brick N depends only on layers < N |
| Layer 0 | May depend on other layer 0 (no cycles) |
| Cycles | Rejected at ALL layers |
| Dependencies | Computed from call graph, not stored |
| FORBIDDEN | Per-JIGPLAN scope boundary, not permanent |
| Violations | Errors, not warnings |
