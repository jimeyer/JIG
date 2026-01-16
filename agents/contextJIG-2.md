# JIG Context for AI Agents

JIG measures alignment between **intent** (specifications), **implementation** (code), and **verification** (tests) through a seven-level hierarchy.

---

## The G-A-O-S-C-T Pyramid

```
                      CHARTER
                     (defines G-#)
                    /            \
                   /              \
          ARCHITECTURE          OUTCOMES
               A-###               O-###
              goals               goals
                │                   │
                │ specifications    │ specifications
                │    ┌──────────────┘
                ▼    ▼
            SPECIFICATIONS
                 S-###
           (outcomes, architecture)
               /      \
              /        \
         verifies   implements
            /            \
           /              \
       TESTS              CODE
        T-###              C-###
```

Every function should trace upward through this hierarchy to the Charter. Breaks indicate misalignment.

---

## ID Formats

| Type | Format | Example |
|------|--------|---------|
| Charter | `Charter` | `Charter` (singleton) |
| Goal | `G-{number}` | G-1, G-2, G-3 |
| Architecture | `A-{number}` | A-010, A-030 |
| Outcome | `O-{number}` | O-101, O-107 |
| Specification | `S-{number}` | S-001, S-042 |
| Brick | `B-{kebab-case}` | B-auth-session |
| Code | `C-{path}` | C-jig.cli.main |
| Module | `M-{path}` | M-auth.session |
| Class | `C-{path}` | C-auth.tokens.TokenValidator |
| Test | `T-{path}` | T-test_auth.test_token_expiration |

---

## Seven Artifact Types

| # | Artifact | Location | Authored By |
|---|----------|----------|-------------|
| 1 | Charter | `jig/Charter.md` | Human |
| 2 | Architecture | `jig/architecture/A-###.md` | Human |
| 3 | Outcome | `jig/outcomes/O-###.md` | Human |
| 4 | Specification | `jig/specifications/S-###.md` | Human |
| 5 | Brick definitions | `jig/bricks.yaml` | Human |
| 6 | @jig annotations | Source code | Human |
| 7 | Graph files | `jig/generated/*.ndjson` | Machine (NEVER EDIT) |

### Frontmatter Schema

Frontmatter contains **graph edges** (identity + relationships). Operational metadata goes in body.

**Charter:**
```yaml
---
id: Charter
type: charter
goals: [G-1, G-2, G-3]
---
```

**Architecture:**
```yaml
---
id: A-030
type: architecture
title: ANK Architecture
goals: [G-1, G-3]
specifications: [S-001, S-004, S-006]
---
```

**Outcome:**
```yaml
---
id: O-101
type: outcome
title: Distributed State Convergence
goals: [G-2, G-3]
architecture: [A-022, A-030]
specifications: [S-001, S-002]
---
```

**Specification:**
```yaml
---
id: S-001
type: specification
title: CID Properties
outcomes: [O-101, O-103]
architecture: [A-030, A-022]
---
```

**Not in frontmatter** (goes in body if needed): `status`, `related`, `brick`, `consolidates`

### Decorators (in source code)

```python
@jig.implements("S-001")
def authenticate(user: str, password: str) -> Token: ...

@jig.verifies("S-001")
def test_token_expiration(): ...
```

---

## Bricks: Layer × Tower Model

### Partition Property
- Every function in exactly ONE brick (no gaps, no overlaps)
- All methods of a class in SAME brick

### Brick Definition

```yaml
bricks:
  - id: B-cli
    name: CLI Commands
    layer: 1
    tower: server        # Optional
    units:
      - M-jig.cli.main   # All functions in module
      - C-jig.Parser     # All methods of class
```

### Layers (Horizontal Stratification)

Brick at layer N depends ONLY on layers < N. Violations are errors.

```
Layer 0: Foundation (external libs only)
Layer 1: Core logic (depends on Layer 0)
Layer 2: Interface (depends on Layers 0-1)
```

### Towers (Vertical Partitioning)

Cross-tower dependencies are **FORBIDDEN**. Towers communicate through shared specifications, not code imports.

```
          │  server  │  harness  │  device  │
Layer 2   │   B-s2   │   B-h2    │          │
Layer 1   │   B-s1   │   B-h1    │   B-d1   │
Layer 0   │   B-s0   │   B-h0    │   B-d0   │
```

Single-tower projects omit `tower` field from all bricks.

### FORBIDDEN Bricks (Per-JIGPLAN)

Scope constraint for specific work. If sub-agent needs FORBIDDEN brick: STOP, escalate, wait for scope revision.

---

## Writing Evergreen Artifacts

O and S nodes remain true FOREVER, not just until PR merges.

### Outcomes = Business Value

- [ ] WHY the system behaves this way
- [ ] `goals` links to Charter goals
- [ ] Remains true after project completes
- [ ] NOT: project goals, refactoring tasks

❌ BAD: "Achieve 90% test coverage"  
✓ GOOD: "Critical behaviors verified to prevent production regressions"

### Specifications = Behavioral Requirements

- [ ] Observable behavior with acceptance criteria
- [ ] Can use `@jig.implements` on code
- [ ] Can use `@jig.verifies` on tests
- [ ] NOT: file paths, implementation details

❌ BAD: "Relocate file X to location Y"  
✓ GOOD: "EraLamportClock state persists across restarts"

**Test:** Can you write a decorator for it? If no, rewrite.

### Specification Body Structure

Specs are lean behavioral contracts. Architecture docs own structure/relationships; specs own invariants.

**Title:** `S-###: {Invariant Name}` — names the property, not the implementation.

| Section | Required | Content |
|---------|----------|---------|
| **Statement** | Yes | 1-3 sentences. What must be true. No "how." |
| **Invariants** | Yes | Bullet list of always-true conditions. Each falsifiable. |
| **Verification** | Yes | Acceptance criteria. What would a test assert? |
| **Boundaries** | No | What's explicitly out of scope. |

**Exclude:** Rationale (→ Outcome), architecture discussion (→ arch doc link), implementation hints, history.

**Example:**
```markdown
# S-042: Staleness Tracking

Heartbeat absence triggers staleness state within bounded time.

## Invariants
- Device marked stale after 2× heartbeat interval without contact
- Staleness merge uses min-timestamp (earliest evidence wins)
- Stale→fresh transition requires new heartbeat, not timeout

## Verification
- [ ] Device receiving heartbeat at t₀, none by t₀+2T → stale
- [ ] Two hosts disagree on staleness → merge produces stale
- [ ] Stale device sends heartbeat → immediately fresh
```

Target: ~50 lines max. Architecture link in frontmatter handles the rest.

---

## CLI Commands

```bash
jigy validate       # Check references, partition, layers
jigy impl rebuild   # Generate implementation graph
jigy intent rebuild # Generate intent graph
jigy layers         # Show layer structure
jigy rebuild        # Runs validate, rebuild, layers
```

---

## Validation Rules

- All IDs unique within type, match required patterns
- `@jig.implements` / `@jig.verifies` reference existing specs
- `goals` references goals defined in Charter
- `specifications` references existing specs
- `outcomes` / `architecture` reference existing outcomes/arch docs
- Every function in exactly one brick
- Brick at layer N depends only on layers < N
- Cross-tower dependencies forbidden (if towers used)
- No circular dependencies

---

## For AI Agents

1. **Read before writing** — Query graphs to understand what exists
2. **Link your work** — Use `@jig.implements()` and `@jig.verifies()`
3. **Validate continuously** — Run `jigy validate` before committing
4. **Understand intent first** — Read S-### and O-### before modifying code
5. **Respect architecture** — Check layer and tower constraints
6. **Trace to goals** — Know which G-### your work supports

---

## Quick Reference

| Task | Action |
|------|--------|
| Add requirement | Create `jig/specifications/S-{next}.md` |
| Group specs into value | Create `jig/outcomes/O-{next}.md` |
| Mark function implements | `@jig.implements("S-001")` |
| Mark test verifies | `@jig.verifies("S-001")` |
| Assign to brick | Add to `units` in `bricks.yaml` |
| Check validity | `jigy rebuild` |
