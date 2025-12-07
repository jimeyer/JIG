# JIG Context for AI Agents

JIG measures alignment between **intent** (specifications), **implementation** (functions), and **verification** (tests). These form the S-F-T triangle:

```
         S (Specification)
        / \
       /   \
implements  verifies
     /       \
    F ——————→ T
      covers
```

Three relationships:
- **F → S** (implements): Function implements specification via `@jig.implements("S-001")`
- **T → S** (verifies): Test verifies specification via `@jig.verifies("S-001")`
- **T → F** (covers): Test executes function (automatic via coverage)

**Bricks** partition functions into architectural units. **Layers** stratify bricks (layer N depends only on layers < N).

---

## Artifacts

### Specifications (`jig/specifications/S-{number}.md`)

```yaml
---
id: S-001
type: specification
---
```

```markdown
# Token Expiration

Authentication tokens MUST expire after 15 minutes of inactivity.

**Acceptance Criteria:**
- Token created with expires_at = now() + 15 minutes
- Token rejected if now() > last_activity + 15 minutes
```

### Outcomes (`jig/outcomes/O-{number}.md`) — OPTIONAL

```yaml
---
id: O-001
type: outcome
specifies: [S-001, S-002]
---
```

```markdown
# Secure Authentication

Users authenticate without managing passwords.

**Value:** Reduces support burden and improves security.
```

### Bricks (`jig/bricks.yaml`)

```yaml
bricks:
  - id: B-core-utils
    name: Core Utilities
    layer: 0
    units:
      - M-utils.io
      - M-utils.yaml_utils

  - id: B-auth-session
    name: Authentication
    layer: 1
    units:
      - M-auth.session
      - C-auth.tokens.TokenValidator
```

Unit prefixes:
- `M-{path}` — all functions in module
- `C-{path}` — all methods of class
- `F-{path}` — single function

### Decorators (in source code)

```python
@jig.implements("S-001")
def authenticate(user: str, password: str) -> Token:
    ...

@jig.verifies("S-001")
def test_token_expiration():
    ...
```

### Generated Files (`jig/generated/`) — NEVER EDIT

- `intent-graph.ndjson` — specs, outcomes, bricks
- `implementation-graph.ndjson` — functions, calls
- `verification-graph.ndjson` — tests, coverage

---

## ID Formats

| Type | Format | Example |
|------|--------|---------|
| Specification | `S-{number}` | S-001, S-042 |
| Outcome | `O-{number}` | O-001 |
| Brick | `B-{kebab-case}` | B-auth-session |
| Function | `F-{path}` | F-auth.session.authenticate |
| Module | `M-{path}` | M-auth.session |
| Class | `C-{path}` | C-auth.tokens.TokenValidator |
| Test | `T-{path}` | T-test_auth.test_token_expiration |

---

## Writing Outcomes & Specifications

### Outcomes = Evergreen Business Value

**Checklist:**
- [ ] Describes WHY the system behaves this way
- [ ] Remains true after project completes
- [ ] Would make sense to new developer in 2 years
- [ ] NOT: project goals, refactoring tasks, process improvements

**Test:** Remove all project references. Does it still make sense?

### Specifications = Evergreen Behavioral Requirements

**Checklist:**
- [ ] Describes observable system behavior
- [ ] Has testable acceptance criteria
- [ ] Can use `@jig.implements` on code
- [ ] Can use `@jig.verifies` on tests
- [ ] NOT: file paths, implementation details, refactoring tasks

**Test:** Can you write a decorator for it? If no, rewrite.

---

## CLI Commands

```bash
jigy validate       # Check references, partition, layers
jigy impl rebuild   # Generate implementation graph from code
jigy intent rebuild # Generate intent graph from JIG artifacts
jigy layers         # Show layer structure
jigy rebuild        # Runs validate, rebuild, layers commands in order
```

---

## Validation Rules

- All IDs unique within type
- Brick IDs match `B-[a-z0-9-]+`
- `@jig.implements` references existing spec IDs
- `@jig.verifies` references existing spec or outcome IDs
- Outcome `specifies` references existing spec IDs
- Every function in exactly one brick (no gaps, no overlaps)
- All methods of a class in same brick
- Brick at layer N depends only on layers < N
- No circular dependencies between bricks

---

## Anti-patterns

**Refactoring task as specification:**
```
BAD:  "Relocate era_persistence.py to protocol-core"
GOOD: "EraLamportClock state persists across restarts"
```

**Project goal as outcome:**
```
BAD:  "Achieve 90% test coverage"
GOOD: "Critical behaviors verified to prevent production regressions"
```

**Implementation detail as specification:**
```
BAD:  "Functions have @jig.implements decorators"
GOOD: "Devices can be added, removed, and updated in shared CRDT"
```

**Process improvement as outcome:**
```
BAD:  "Code organization improved"
GOOD: "Auth logic isolated, enabling independent modification"
```

---

## File Structure

```
project-root/
├── jig/
│   ├── specifications/     # Human-authored
│   │   ├── S-001.md
│   │   └── S-002.md
│   ├── outcomes/           # Human-authored, optional
│   │   └── O-001.md
│   ├── bricks.yaml         # Human-authored
│   └── generated/          # Machine-generated
│       ├── intent-graph.ndjson
│       ├── implementation-graph.ndjson
│       └── verification-graph.ndjson
├── src/                    # @jig.implements decorators
└── tests/                  # @jig.verifies decorators
```

---

## Quick Reference

| Task                          | Action                                                    |
| ----------------------------- | --------------------------------------------------------- |
| Add new requirement           | Create `jig/specifications/S-{next}.md`                   |
| Group specs into value        | Create `jig/outcomes/O-{next}.md` with `specifies: [...]` |
| Mark function implements spec | Add `@jig.implements("S-001")` decorator                  |
| Mark test verifies spec       | Add `@jig.verifies("S-001")` decorator                    |
| Assign functions to brick     | Add module/class/function to `units` in `bricks.yaml`     |
| Check everything valid        | Run `jigy rebuild`                                        |

