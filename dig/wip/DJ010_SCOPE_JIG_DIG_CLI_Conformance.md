---
title: "SCOPE: JIG & DIG CLI Full Conformance to DJ002"
type: scope
status: active
created: 1736646000
created_human: "2026-01-11 18:00 CST"
parent: "[[DJ002_SCOPE_CLI_Recommendations]]"
children: []
---
# SCOPE: JIG & DIG CLI Full Conformance to DJ002

## Executive Summary

This scope defines the remaining work to bring both JIG and DIG CLIs into full conformance with [[DJ002_SCOPE_CLI_Recommendations]]. Phase 0-1 (output flags, command restructuring) is complete for JIG. This scope covers:

- **JIG Phase 2-3**: Context commands, creation commands, integration
- **DIG Phase 1-3**: Show commands, audit commands, context enhancement, lifecycle commands, integration

**Central insight from DJ002**: The `context` command is "the most important command for agents." It synthesizes orientation, not just display. Both tools lack this capability at the artifact level.

---

## Part I: Current State

### JIG CLI (Post Phase 0-1)

```
jigy
├── align              ✓ Full workflow
├── validate           ✓ With -j/-m/-v flags
│   ├── intent         ✓
│   ├── bricks         ✓
│   └── full           ✓
├── show               ✓ With -j/-m/-v flags
│   ├── layers         ✓
│   ├── bricks         ✓
│   ├── charter        ✓
│   ├── goals          ✓
│   ├── architecture   ✓
│   ├── towers         ✓ (moved from root)
│   └── matrix         ✓ (moved from root)
├── audit
│   └── coverage       ✓ With -j/-m/-v flags
└── rebuild            ✓ With -j/-m/-v flags
```

**Missing (per DJ002):**
- `jigy init` — Project initialization
- `jigy context` — Project-level dynamic briefing
- `jigy context spec/brick/outcome <id>` — Artifact-level context with neighborhood
- `jigy new spec/outcome/architecture "Title"` — Artifact creation
- `jigy show spec <id>` — Single spec display with S-F-T triangle
- `jigy show specs [--search, --unimplemented]` — Filtered list
- `jigy show outcome <id>` — Single outcome display
- `jigy show outcomes` — List outcomes
- `jigy audit gaps` — Unimplemented/unverified/orphan report
- Cross-tool integration with DIG

### DIG CLI (Current)

```
digy
├── init               ✓ Project initialization
├── new <type>         ✓ Document creation
├── validate           ✓ With -j/-m/-v flags (global)
├── rebuild            ✓ With -j/-m/-v flags (global)
└── context            ✓ Project-level only
```

**Missing (per DJ002):**
- `--no-rebuild` global flag
- `digy context <type> <id>` — Artifact-level context with ancestry/children
- `digy context <jig-id>` — Returns DIG context related to JIG spec
- `digy show explorations [--active, --search]` — List explorations
- `digy show exploration <id>` — Single exploration display
- `digy show scopes`, `digy show scope <id>` — Scope display
- `digy show plans`, `digy show plan <id>` — Plan display
- `digy audit` — Overall deliberation health
- `digy audit stale` — Documents with no updates in 14+ days
- `digy audit orphan` — Orphan deliberation chains
- `digy promote <id> <type>` — Advance document lifecycle
- `digy close <id>` — Close deliberation with decision
- Config migration: `dig/digconfig.yaml` → `dig.toml` in project root
- Cross-tool integration with JIG

---

## Part II: Success Criteria

### JIG Success Criteria

**SC-J0: Bug Fix — JSON Single-Line Format**

Phase 0-1 left a deviation from S-026: `rebuild` and `align` commands produce pretty-printed JSON instead of single-line compact JSON.

```bash
# Current (broken):
jigy rebuild -j
{
  "status": "success",
  "graphs": [
    ...
  ]
}

# Expected (S-026 compliant):
jigy rebuild -j
{"status":"success","graphs":[...]}
```

Fix: Change `json.dumps()` calls in `rebuild.py` to use `separators=(",", ":")`.

**SC-J1: Context Command**
```bash
jigy context                    # Project overview with gaps
jigy context spec S-042         # Spec with S-F-T triangle and neighborhood
jigy context brick B-validation # Brick with functions and specs
jigy context outcome O-012      # Outcome with specs and completion status
jigy context -j                 # All contexts support -j/-m/-v
```

**SC-J2: Show Single-Artifact**
```bash
jigy show spec S-042            # Spec with implementations and tests
jigy show specs                 # List all specs
jigy show specs --search "CRDT" # Filter by keyword
jigy show specs --unimplemented # Filter by status
jigy show outcome O-012         # Outcome with supporting specs
jigy show outcomes              # List all outcomes
```

**SC-J3: Audit Gaps**
```bash
jigy audit gaps                 # Unimplemented, unverified, orphan functions
jigy audit gaps -j              # JSON format
```

**SC-J4: Creation Commands**
```bash
jigy new spec "Token Refresh"   # Creates S-094_Token_Refresh.md
jigy new outcome "Real-time"    # Creates O-013_Real_Time.md
jigy new architecture "Auth"    # Creates A-005_Auth.md
jigy init                       # Creates jig.toml with defaults
```

**SC-J5: Integration**
```bash
jigy context S-042              # Includes DIG deliberation history if available
# jig.toml contains: [integration] include_dig = true
```

### DIG Success Criteria

**SC-D1: Show Commands**
```bash
digy show explorations          # List all explorations
digy show explorations --active # Filter active only
digy show exploration DJ001     # Single with ancestry
digy show scopes                # List all scopes
digy show scope DJ002           # Single scope display
digy show plans                 # List all plans
digy show plan DJ008            # Single plan display
digy show -j                    # All show commands support -j/-m/-v
```

**SC-D2: Context Enhancement**
```bash
digy context exploration DJ001  # Artifact with ancestry and children
digy context scope DJ002        # Scope with related deliberations
digy context S-042              # DIG docs that produced this spec
```

**SC-D3: Audit Commands**
```bash
digy audit                      # Overall health: active, stale, abandoned
digy audit stale                # Documents with no updates in 14+ days
digy audit orphan               # Chains with no terminal status
digy audit -j                   # JSON format
```

**SC-D4: Lifecycle Commands**
```bash
digy promote DJ015 scope        # Advance exploration to scope
digy close DJ019 completed      # Close with decision
```

**SC-D5: Config Migration**
```bash
# dig.toml in project root (not dig/digconfig.yaml)
# Contains: [integration] include_jig = true
```

**SC-D6: Global Flag**
```bash
digy --no-rebuild validate      # Skip automatic graph rebuild
```

### Both: Integration Success Criteria

**SC-I1: Bidirectional Context**
```bash
jigy context S-042              # Shows DIG deliberations that produced S-042
digy context DJ017              # Shows JIG specs that DJ017 created
```

**SC-I2: Graceful Degradation**
```bash
# If DIG not installed: jigy context works, just no DIG section
# If JIG not installed: digy context works, just no JIG section
```

---

## Part III: Phased Deliverables

### Phase 0 Bug Fix: JIG JSON Single-Line Format

**Concern**: S-026 compliance for rebuild/align commands.

| Deliverable | Description |
|-------------|-------------|
| Fix `rebuild -j` | Use `separators=(",", ":")` in json.dumps() |
| Fix `align -j` | Same fix, propagates to combined output |
| Fix rebuild subcommands | `rebuild impl -j`, `rebuild intent -j`, `rebuild verify -j` |

**Effort**: ~30 minutes. Single file change in `src/jig/cli/rebuild.py`.

**Dependencies**: None.

### Phase 2A: JIG Show & Context (Foundation)

**Concern**: Static display before synthesis.

| Deliverable | Description |
|-------------|-------------|
| `show spec <id>` | Single spec with S-F-T triangle |
| `show specs` | List with `--search`, `--unimplemented` filters |
| `show outcome <id>` | Single outcome with supporting specs |
| `show outcomes` | List with optional filters |
| `context` (project) | Dynamic project briefing with gaps |
| `context spec <id>` | Spec context with neighborhood |
| `context brick <id>` | Brick context with functions |
| `context outcome <id>` | Outcome context with completion |

**Dependencies**: Requires reading intent graph, impl graph, verify graph.

### Phase 2B: DIG Show & Context (Parallel)

**Concern**: Static display and context enhancement.

| Deliverable | Description |
|-------------|-------------|
| `show explorations` | List with `--active`, `--search` filters |
| `show exploration <id>` | Single with ancestry/children |
| `show scopes` | List scopes |
| `show scope <id>` | Single scope display |
| `show plans` | List plans |
| `show plan <id>` | Single plan display |
| `context <type> <id>` | Artifact-level context |
| `--no-rebuild` flag | Global flag addition |

**Dependencies**: Requires reading deliberation graph.

### Phase 2C: JIG Audit & Creation

**Concern**: Health reporting and artifact creation.

| Deliverable | Description |
|-------------|-------------|
| `audit gaps` | Unimplemented, unverified, orphan report |
| `new spec "Title"` | Create specification with auto-ID |
| `new outcome "Title"` | Create outcome with auto-ID |
| `new architecture "Title"` | Create architecture doc with auto-ID |
| `init` | Create jig.toml with defaults |

**Dependencies**: `audit gaps` requires impl + verify graphs.

### Phase 2D: DIG Audit & Lifecycle

**Concern**: Health reporting and lifecycle management.

| Deliverable | Description |
|-------------|-------------|
| `audit` | Overall deliberation health |
| `audit stale` | Documents with no updates in 14+ days |
| `audit orphan` | Chains without terminal status |
| `promote <id> <type>` | Advance document type |
| `close <id> <decision>` | Close with required decision |
| Config migration | `dig/digconfig.yaml` → `dig.toml` |

**Dependencies**: `audit` requires deliberation graph timestamps.

### Phase 3: Cross-Tool Integration

**Concern**: Bidirectional context synthesis.

| Deliverable | Tool | Description |
|-------------|------|-------------|
| `[integration]` config | Both | `include_dig`/`include_jig` in toml |
| `context <peer-id>` | JIG | Return JIG context related to DIG doc |
| `context <peer-id>` | DIG | Return DIG context related to JIG spec |
| Graceful degradation | Both | Works when peer not installed |

**Dependencies**: Requires Phase 2A/2B context commands complete.

---

## Part IV: Constraints

### Architectural Constraints

1. **No cross-tool code dependencies** — JIG must not import DIG code, and vice versa. Integration happens via CLI subprocess calls.

2. **Config in project root** — Both `jig.toml` and `dig.toml` live in project root, not in `jig/` or `dig/` directories.

3. **Output flag semantics preserved** — All new commands must support `-j/-m/-v` with identical semantics to existing commands.

4. **Backward compatibility for DIG config** — During migration, DIG should read from both `dig/digconfig.yaml` (legacy) and `dig.toml` (new), preferring new.

### Implementation Constraints

1. **JIG bricks** — New JIG code must fit existing brick structure. Likely additions to `B-cli` brick only.

2. **Graph dependencies** — Context commands require all three graphs (intent, impl, verify) to be built. Must handle missing graphs gracefully.

3. **ID auto-assignment** — `jigy new spec` must read existing specs to assign next ID. Must handle concurrent creation (file locking or optimistic).

### Out of Scope

1. **Refactoring existing commands** — This scope adds new commands, not rewriting working ones.

2. **Performance optimization** — Context synthesis may be slow on large projects; optimization is separate work.

3. **GUI/TUI** — CLI only; no interactive interfaces.

---

## Part V: Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Context synthesis complexity | High | Start with simple neighborhood (1-hop), expand later |
| Graph loading performance | Medium | Lazy load graphs only when needed |
| DIG config migration breaks existing | Medium | Support both config locations during transition |
| Cross-tool integration complexity | High | Phase 3 is last; can be deferred if needed |
| ID collision in `new` command | Low | Read-then-write with filesystem locking |

---

## Part VI: Dependency Graph

```
                    DJ002 (Target Spec)
                           │
                    Phase 0 Bug Fix
                    (JIG JSON format)
                           │
              ┌────────────┼────────────┐
              │            │            │
         Phase 2A     Phase 2B     (parallel)
         JIG Show     DIG Show
         & Context    & Context
              │            │
              │            │
         Phase 2C     Phase 2D     (parallel)
         JIG Audit    DIG Audit
         & Creation   & Lifecycle
              │            │
              └─────┬──────┘
                    │
               Phase 3
            Integration
```

**Parallelism**: Phases 2A/2B can run in parallel. Phases 2C/2D can run in parallel. Phase 3 requires 2A+2B complete.

---

## Part VII: Verification Approach

### Per-Phase Verification

Each phase requires:
1. All new commands documented in `--help`
2. All commands support `-j/-m/-v` flags
3. JSON output is valid and parseable
4. Unit tests for new functions
5. Integration tests for CLI commands
6. `jigy rebuild && jigy validate` passes (for JIG phases)
7. `digy rebuild && digy validate` passes (for DIG phases)

### Final Verification

DJ002 conformance verified when:
1. All success criteria (SC-J0 through SC-J5, SC-D1 through SC-D6, SC-I1/SC-I2) pass
2. Manual spot-checks of DJ002 command examples work
3. "Learning one CLI teaches you the other" — command structure is parallel

---

## Part VIII: Open Questions

1. **JIG `context` data sources** — Should context pull from graphs only, or also read source files for richer detail?

2. **DIG `promote` semantics** — Does promote create a new document or modify the existing one?

3. **DIG staleness threshold** — DJ002 says 14 days. Should this be configurable?

4. **Cross-tool ID recognition** — How does JIG recognize `DJ017` as a DIG ID vs a typo? Prefix convention (`DJ` vs `S-`) seems sufficient.

5. **Integration subprocess timeout** — How long should `jigy context` wait for `digy context` subprocess?

---

## Appendix: DJ002 Compliance Checklist

### Global Flags (Both Tools)

- [x] `--help` / `-h`
- [x] `--version`
- [ ] `--no-rebuild` (DIG missing)

### Output Flags (Universal)

- [x] `-j` / `--json` on all commands (JIG)
- [x] `-m` / `--markdown` on all commands (JIG)
- [x] `-v` / `--verbose` on all commands (JIG)
- [x] `-j` / `--json` on all commands (DIG)
- [x] `-m` / `--markdown` on all commands (DIG)
- [x] `-v` / `--verbose` on all commands (DIG)
- [x] `-j -m` produces error (JIG)
- [ ] `-j -m` produces error (DIG — needs verification)
- [ ] JSON output is single-line compact (JIG rebuild/align — **bug fix needed**)

### JIG Commands

- [x] `jigy align`
- [x] `jigy validate` with subcommands
- [x] `jigy rebuild` with subcommands
- [x] `jigy show layers/bricks/charter/goals/architecture`
- [x] `jigy show towers` (moved from root)
- [x] `jigy show matrix` (moved from root)
- [x] `jigy audit coverage`
- [ ] `jigy init`
- [ ] `jigy context` (project)
- [ ] `jigy context spec/brick/outcome <id>`
- [ ] `jigy new spec/outcome/architecture`
- [ ] `jigy show spec <id>`
- [ ] `jigy show specs` with filters
- [ ] `jigy show outcome <id>`
- [ ] `jigy show outcomes`
- [ ] `jigy audit gaps`

### DIG Commands

- [x] `digy init`
- [x] `digy new <type>`
- [x] `digy validate`
- [x] `digy rebuild`
- [x] `digy context` (project)
- [ ] `digy context <type> <id>`
- [ ] `digy context <jig-id>`
- [ ] `digy show explorations/scopes/plans`
- [ ] `digy show <type> <id>`
- [ ] `digy audit`
- [ ] `digy audit stale`
- [ ] `digy audit orphan`
- [ ] `digy promote <id> <type>`
- [ ] `digy close <id>`

### Integration

- [ ] `jig.toml` with `[integration]` section
- [ ] `dig.toml` in project root (migrated from `dig/digconfig.yaml`)
- [ ] Cross-tool context calls
- [ ] Graceful degradation
