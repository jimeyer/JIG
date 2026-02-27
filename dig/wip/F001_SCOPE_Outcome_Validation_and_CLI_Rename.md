---
type: scope
title: "Outcome Validation and CLI Rename"
status: active
created: 1772226587
created_human: "2026-02-27 22:09 PST"
parent: null
children: []
prompt: |
  @jig.validates — yes, new relationship type.

  verifies and validates are different things:

  ┌──────────────────────────┬───────┬────────────┬─────────┬──────────────────────────┐
  │        Decorator         │  Who  │    What    │ Against │           When           │
  ├──────────────────────────┼───────┼────────────┼─────────┼──────────────────────────┤
  │ @jig.implements("S-###") │ code  │ implements │ spec    │ —                        │
  ├──────────────────────────┼───────┼────────────┼─────────┼──────────────────────────┤
  │ @jig.verifies("S-###")   │ test  │ verifies   │ spec    │ pytest, fast, mocked I/O │
  ├──────────────────────────┼───────┼────────────┼─────────┼──────────────────────────┤
  │ @jig.validates("O-###")  │ assay │ validates  │ outcome │ live sim, slow, real I/O │
  └──────────────────────────┴───────┴────────────┴─────────┴──────────────────────────┘

  Tests verify that code matches a spec. Assays validate that the system achieves an outcome.
  Different level, different mechanism, different lifecycle. Overloading verifies conflates them.
  validates makes the distinction explicit in the JIG model — it's a third edge type in the graph.

  Additionally, `jigy validate` (CLI command) collides with `@jig.validates()` (decorator).
  Rename the CLI command to `jigy check`.
---

# Outcome Validation and CLI Rename

## Problem Statement

JIG's traceability model has two edge types connecting intent to reality: `implements` (code→spec) and `verifies` (test→spec). Both operate at the specification level. There is no edge type that connects reality back to outcomes.

This is a gap. Outcomes represent business value — "Discoverable Implementation Structure", "Automated Code-to-Specification Traceability", "Fast Validation". Specifications decompose outcomes into observable behaviors. Tests verify those behaviors in isolation. But nothing in the model says "the system, running end-to-end, actually achieves this outcome."

The missing concept is **outcome validation**: a third relationship type where a function (an "assay") validates that an outcome is achieved, typically through slow, real-I/O, system-level exercises rather than fast, mocked unit tests.

### The Three Relationships

```
┌──────────────────────────┬───────┬────────────┬─────────┬──────────────────────────┐
│        Decorator         │  Who  │    What    │ Against │           When           │
├──────────────────────────┼───────┼────────────┼─────────┼──────────────────────────┤
│ @jig.implements("S-###") │ code  │ implements │ spec    │ —                        │
├──────────────────────────┼───────┼────────────┼─────────┼──────────────────────────┤
│ @jig.verifies("S-###")   │ test  │ verifies   │ spec    │ pytest, fast, mocked I/O │
├──────────────────────────┼───────┼────────────┼─────────┼──────────────────────────┤
│ @jig.validates("O-###")  │ assay │ validates  │ outcome │ live sim, slow, real I/O │
└──────────────────────────┴───────┴────────────┴─────────┴──────────────────────────┘
```

Tests verify that code matches a spec. Assays validate that the system achieves an outcome. Different level, different mechanism, different lifecycle.

### Why This Matters

Without outcome-level validation, the traceability chain has a gap at the top:

```
Today:
  Charter → Goal → Outcome → Spec ←implements← Function
                                   ←verifies←  Test
                     ↑
                     (nothing validates this)

Proposed:
  Charter → Goal → Outcome → Spec ←implements← Function
                     ↑              ←verifies←  Test
                     └──validates── Assay
```

An outcome like O-006 "Fast Validation" might have specs S-044 through S-047 all verified by unit tests. Every spec passes. But does the system actually validate fast? Only an assay — running the real validation pipeline on a real project — can answer that. The specs verify pieces; the assay validates the whole.

### The Graph Model

The existing model has two triangles, both anchored at the spec level:

```
       S (Specification)
      / \
implements  verifies
    /       \
   F ———————— T
```

The new model adds a third relationship at the outcome level:

```
       O (Outcome)
      / \
specifies  validates
    /       \
   S         Assay
  / \
 F   T
```

`validates` is a third edge type in the graph, distinct from `implements` and `verifies`. It creates Assay→O edges in a new validation graph, parallel to how `verifies` creates T→S edges in the verification graph.

### Coexistence of Decorators

A single function can carry multiple decorators. An assay that validates an outcome might also verify specific specs along the way:

```python
@jig.validates("O-006")
@jig.verifies("S-044")
def assay_validation_speed():
    """Validate that full validation completes in <3 seconds on a real project."""
    ...
```

This is expected and encouraged. The decorators create edges at different levels of the hierarchy — `validates` points at outcomes, `verifies` points at specs. Both are true simultaneously.

Conversely, `@jig.validates` can appear on code that lives anywhere — inside `tests/`, inside a dedicated `assays/` directory, or in any other location the project chooses. JIG discovers `validates` decorators by scanning configured source directories, not by convention about where assay files live.

### Constraint: Target Enforcement

The decorator enforces which ID prefix it accepts:

| Decorator | Valid targets | Invalid targets |
|-----------|--------------|-----------------|
| `@jig.implements("S-###")` | `S-###`, `O-###` | — |
| `@jig.verifies("S-###")` | `S-###` | `O-###` |
| `@jig.validates("O-###")` | `O-###` | `S-###` |

`verifies` targets specs. `validates` targets outcomes. The analyzers enforce this at extraction time — a `@jig.validates("S-001")` is an error, not a valid edge. This prevents the conceptual distinction from eroding through misuse.

Note: `implements` currently accepts both S-### and O-### targets. This is unchanged.

---

## The CLI Naming Collision

Introducing `@jig.validates()` creates a naming collision with the existing CLI command `jigy validate`.

| Current | Meaning |
|---------|---------|
| `jigy validate` | CLI command: check alignment of all JIG artifacts |
| `@jig.validates("O-###")` | Decorator: this function validates an outcome |

These are different verbs in the domain. The CLI command checks JIG's internal consistency rules (required fields, bidirectional links, brick partition). The decorator declares that a function validates a system outcome. Same word, different levels, different semantics.

### Resolution: Rename CLI to `jigy check`

The CLI command becomes `jigy check`. This:

1. **Frees "validate"** entirely for the outcome-level concept
2. **Aligns with convention** — `ruff check`, `eslint --check`, `mypy` all use "check" for linting/consistency operations
3. **Is more accurate** — the CLI checks JIG's rules, it doesn't validate outcomes
4. **Is shorter** — `jigy check` vs `jigy validate`

After rename:

```bash
# CLI commands (checking JIG's rules)
jigy check              # was: jigy validate
jigy check intent       # was: jigy validate intent
jigy check bricks       # was: jigy validate bricks

# Decorators (connecting code to intent)
@jig.implements("S-001")   # code implements a spec
@jig.verifies("S-001")     # test verifies a spec
@jig.validates("O-003")    # assay validates an outcome
```

No collision. Each word means exactly one thing.

### Rename Scope

The rename touches:

| Location | Change |
|----------|--------|
| `src/jig/cli/main.py` | Command group name `validate` → `check` |
| `src/jig/cli/validate.py` | Module rename to `check.py`, function names updated |
| `src/jig/query/validate.py` | Module rename to `check.py` (query layer) |
| `jig/Charter_JIG.md` | Instructions reference `jigy check` instead of `jigy validate` |
| `CLAUDE.md` | All `jigy validate` references → `jigy check` |
| `agents/contextJIG.md` | References updated |
| All specs/outcomes mentioning `jigy validate` | Text updated |
| Tests | Updated to reflect new command names |

The `jigy align` command, which internally calls validation, also updates its delegation.

---

## Charter Alignment

This scope serves three Charter goals directly:

| Goal | How |
|------|-----|
| **G-001: Grounding in Reality** | Assays ground outcome claims in actual system behavior, not just spec-level tests. An outcome isn't "met" because its specs pass — it's met because an assay exercises the real system and confirms the result. |
| **G-005: Full Traceability** | Today the traceability chain breaks at outcomes — specs trace down to code and tests, but outcomes have no direct verification link. `validates` edges complete the chain: Charter → Goal → Outcome ← validates ← Assay. |
| **G-004: Intent Alignment** | Agents can now query "which outcomes have no validation?" to find gaps between claimed business value and demonstrated system behavior. The validates edge makes outcome-level intent queryable. |

G-002 (Continuity) is served indirectly — the validation graph persists across sessions like the other graphs.

G-003 (Enforcing Constraints) is served by the target enforcement constraint (`validates` must target `O-###`, `verifies` must target `S-###`).

---

## The Fourth Graph: Validation

JIG currently maintains three graphs:

| Graph | Source | Edges | Builder |
|-------|--------|-------|---------|
| Intent | `jig/specifications/`, `jig/outcomes/`, `jig/architecture/`, `jig/Charter.md` | defines_goal, supports_goal, specifies, specifications | `jigy rebuild intent` |
| Implementation | `src/**/*.py` | contains, imports, calls, extends, implements | `jigy rebuild impl` |
| Verification | `tests/**/*.py` | verifies | `jigy rebuild verify` |

This scope adds:

| Graph | Source | Edges | Builder |
|-------|--------|-------|---------|
| **Validation** | Configured source directories (project-specific) | validates | `jigy rebuild validation` |

### Why a Separate Graph

The validation graph is not an extension of the verification graph. They differ in:

- **Target level**: Verification targets specs (S-###). Validation targets outcomes (O-###).
- **Lifecycle**: Tests run on every commit (fast, mocked). Assays run periodically or on-demand (slow, real I/O).
- **Discovery scope**: Tests are discovered in `tests/`. Assays are discovered wherever the project configures — could be `assays/`, `tests/assays/`, `integration/`, or anywhere else.
- **Rebuild cadence**: Verification graph rebuilds frequently. Validation graph may rebuild less often if assay code changes slowly.

Separate graphs keep these concerns cleanly isolated. The query layer and traversal engine already handle multiple graphs — adding a fourth requires no structural changes to the traversal code.

### Discovery Configuration

The validation graph builder needs to know where to look for `@jig.validates` decorators. This is project-specific. Configuration in `jig.toml`:

```toml
[validation_graph]
sources = ["assays/", "tests/assays/"]   # project chooses
```

If no `[validation_graph]` section exists, the builder scans the same directories as the implementation graph (`src/` by default). This means projects that put assays alongside code get discovery for free. Projects that use a dedicated directory configure it explicitly.

### Graph Schema

Validation graph nodes and edges follow the same NDJSON format as the verification graph:

**Node:**
```json
{"type": "node", "id": "V-assay_validation_speed", "kind": "assay", "file": "assays/test_speed.py", "line": 42, "name": "assay_validation_speed", "hash": "abc123", "validates": ["O-006"]}
```

**Edge:**
```json
{"type": "edge", "source": "V-assay_validation_speed", "target": "O-006", "edge_type": "validates"}
```

The node ID prefix `V-` (for validation) distinguishes assay nodes from test nodes (`T-`) and function nodes (`F-`). The `kind` field is `"assay"` rather than `"test"` or `"function"`.

---

## Edge Directions and Traversal

The query engine's `EDGE_DIRECTIONS` mapping gains one entry:

```python
EDGE_DIRECTIONS = {
    "defines_goal": {"source_is_parent": True},
    "supports_goal": {"source_is_parent": False},
    "specifications": {"source_is_parent": True},
    "specifies": {"source_is_parent": True},
    "implements": {"source_is_parent": False},
    "verifies": {"source_is_parent": False},
    "validates": {"source_is_parent": False},     # NEW: Outcome is parent
}
```

`validates` follows the same pattern as `verifies` — the source (assay) points up to the target (outcome), so the target is the parent. This means:

- Traversing *up* from an assay reaches its outcome, then goals, then charter
- Traversing *down* from an outcome reaches both its specs (via `specifies`) and its assays (via `validates`)
- `jigy context O-006` shows both the specs that decompose it and the assays that validate it

---

## Coverage Measurement (Not Enforcement)

The validation graph enables a new coverage metric: **outcome validation coverage**.

```
Outcome Coverage:
  O-001: 0 assays (no validation)
  O-006: 1 assay  (validated)
  O-018: 2 assays (validated)
  ...
  Total: 3/27 outcomes validated (11%)
```

This is **measurement, not enforcement**. Unlike spec-level coverage (where every spec should have at least one `implements` and one `verifies`), outcome-level coverage is aspirational. Reasons:

1. **Assays are expensive** — they require real infrastructure, take time to write, and run slowly. Demanding 100% outcome coverage from day one is impractical.
2. **Some outcomes are hard to assay** — O-023 "Charter Establishes Project Goals" is validated by the existence of the charter, not by a runnable function.
3. **Coverage grows over time** — as a project matures, assays accumulate. The metric tracks progress without blocking commits.

The `jigy check` output can include a coverage summary. The `jigy show` output can display validation status per outcome. Neither gates on it.

---

## The Decorator Implementation

The `@jig.validates` decorator follows the exact pattern of `@jig.verifies`:

```python
# In src/jig/__init__.py

def validates(*outcome_ids: str) -> Callable[[T], T]:
    """Decorator to mark functions as validating outcomes.

    Usage:
        @jig.validates("O-006")
        def assay_validation_speed():
            pass

    Args:
        *outcome_ids: One or more outcome IDs (e.g., "O-006")
    """
    def decorator(func: T) -> T:
        if not hasattr(func, "__jig_validates__"):
            func.__jig_validates__: list[str] = []
        func.__jig_validates__.extend(outcome_ids)
        return func
    return decorator
```

At runtime, the decorator is a no-op passthrough — it attaches metadata to the function object. The validation graph builder reads this metadata via AST analysis (same as `implements` and `verifies`). The decorator itself doesn't execute validation logic; it declares an intent relationship.

### Analyzer Extraction

The validation graph analyzer extracts `@jig.validates` decorators using the same AST pattern as `_extract_verifies_decorators()` in the verification graph analyzer:

1. Walk the AST of each source file
2. For each function/class definition, check decorator list
3. Match `@jig.validates(...)` or `@validates(...)` (short form)
4. Extract string arguments
5. Validate against pattern `^O-\d+$` (outcomes only)
6. Emit as `validates` field on the node

The key difference from `verifies` extraction: the target ID validation pattern rejects `S-###` and accepts only `O-###`.

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| New edge type | `validates` | Distinct from `verifies` — different level (outcome vs spec), different lifecycle (slow vs fast), different semantics (system behavior vs code behavior). |
| CLI rename | `jigy validate` → `jigy check` | Resolves naming collision. "Check" aligns with linter conventions. Frees "validate" for domain concept. |
| Separate graph | Fourth graph: validation | Different discovery scope, rebuild cadence, and lifecycle than verification graph. Clean separation. |
| Target enforcement | `validates` only targets `O-###` | Prevents conceptual erosion. Specs are verified, outcomes are validated. Mixing them collapses the distinction this feature introduces. |
| Coverage not enforced | Measurement only | Assays are expensive and aspirational. Enforcement would block work unnecessarily. |
| Discovery via config | `[validation_graph] sources` in `jig.toml` | Projects choose where assays live. JIG doesn't dictate directory structure. |
| Node prefix `V-` | Assay nodes distinguished from `T-` and `F-` | Prevents ID collisions across graphs. Clear provenance in traversal output. |
| Coexisting decorators | `@jig.validates` + `@jig.verifies` allowed on same function | Decorators create edges at different hierarchy levels. Both can be true simultaneously. |

---

## Out of Scope

- **Assay execution** — JIG discovers and links assays. It does not run them. Execution is the project's concern (CI pipeline, manual invocation, dedicated runner).
- **Assay result storage** — Whether an assay passed or failed last time it ran is not tracked by JIG. JIG tracks the structural relationship (this function validates this outcome), not runtime results.
- **Outcome dependency/ordering** — Outcomes don't depend on each other in this model. `validates` is Assay→Outcome, not Outcome→Outcome.
- **MCP tool changes** — The `lookup_node` MCP tool will naturally expose `validates` edges through graph traversal. No new MCP tools are needed for this feature.
- **Migration tooling** — Projects using `jigy validate` in CI scripts need to update to `jigy check`. No automated migration tool is provided; it's a simple find-and-replace.
- **Deprecation period for `jigy validate`** — Could add a temporary alias that prints a warning, but this is a small-audience tool. Clean rename is preferred.
- **New outcomes or specs** — This scope defines the concept and integration points. Creating specific O-### and S-### documents for the validates feature is deferred to the JIGPLAN phase.

---

## Related Documents

- [[Charter_JIG]] — Goals G-001, G-004, G-005 served by this scope
- [[O-018_Test-to-Specification_Traceability]] — Parallel concept at spec level; this scope adds the outcome-level parallel
- [[O-031_Programmatic_JIG_Access_for_LLM_Agents]] — MCP tools will expose validates edges via existing traversal
- [[E030_SCOPE_MCP_Server]] — Query layer and graph traversal already support adding new edge types
- `src/jig/__init__.py` — Where `validates` decorator will be defined alongside `implements` and `verifies`
- `src/jig/verification_graph/` — Pattern for the validation graph builder
- `src/jig/query/node.py` — EDGE_DIRECTIONS mapping gains `validates` entry

---

**End of Scope**
