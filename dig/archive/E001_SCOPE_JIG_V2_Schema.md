---
type: scope
title: "JIG V2 Schema Migration"
status: implemented
decision: completed
created: 1768594897
created_human: "2026-01-16 10:21 PST"
parent: null
children: ["[[E002_JIGPLAN_JIG_V2_Schema]]"]
prompt: |
  read @agents/contextJIG.md and @agents/contextJIG-2.md
  what are the deltas between these?
  create a SCOPE of work to update the jig system to the behaviors in JIG-2
---

# JIG V2 Schema Migration

Align JIG implementation with the V2 schema defined in `agents/contextJIG-2.md`.

## Problem Statement

The current JIG implementation uses V1 field naming and unidirectional references. V2 introduces:

1. **Normalized field names** — shorter, consistent naming
2. **Bidirectional spec links** — specs know their parents
3. **Strict frontmatter boundary** — operational metadata excluded
4. **Prescribed spec body structure** — Statement/Invariants/Verification

The implementation and ~50+ existing markdown files need migration.

---

## Delta Summary

### Field Naming Changes

| Artifact | V1 Field | V2 Field |
|----------|----------|----------|
| Charter | `defines_goals` | `goals` |
| Architecture | `supports_goals` | `goals` |
| Architecture | `constrains` | `specifications` |
| Outcome | `supports_goals` | `goals` |
| Outcome | `specifies` | `specifications` |

### New Fields (Bidirectional References)

| Artifact | New V2 Field | Points To |
|----------|--------------|-----------|
| Specification | `outcomes` | O-### array (required) |
| Specification | `architecture` | A-### array (required) |

### Removed Fields

V2 removes these fields from JIG's concern entirely:
- `status` — outside JIG scope (projects may track status separately)
- `related`
- `brick`
- `consolidates`

### Spec Body Structure (New)

V2 prescribes specification body format:

| Section | Required | Purpose |
|---------|----------|---------|
| Statement | Yes | 1-3 sentences, what must be true |
| Invariants | Yes | Falsifiable bullet list |
| Verification | Yes | Acceptance criteria |
| Boundaries | No | Explicit out-of-scope |

Target: ~50 lines max per spec.

---

## Affected Components

### Code Changes

| File | Concern | Changes |
|------|---------|---------|
| `src/jig/validation/intent.py` | Validation logic | Field name changes, new fields, exclusion checks |
| `src/jig/intent_graph/generator.py` | Graph generation | Edge field names, bidirectional edges |
| `agents/contextJIG.md` | Agent context | Replace with V2 content |

### Content Migration

| Location | Count | Migration |
|----------|-------|-----------|
| `jig/Charter.md` | 1 | `defines_goals` → `goals` |
| `jig/architecture/A-*.md` | ~10 | `supports_goals` → `goals`, `constrains` → `specifications` |
| `jig/outcomes/O-*.md` | ~15 | `supports_goals` → `goals`, `specifies` → `specifications` |
| `jig/specifications/S-*.md` | ~80 | Add required `outcomes`, `architecture` back-refs |

### Test Updates

Tests in `tests/unit/` and `tests/integration/` that assert on field names need updates:
- Fixtures with V1 frontmatter
- Assertions checking `supports_goals`, `specifies`, `constrains`

---

## Constraints

1. **Clean break** — No backwards compatibility layer. V1 fields become validation errors.
2. **Atomic migration** — All files migrate in single commit to avoid mixed state.
3. **Spec body structure optional** — V2 body format is guidance, not validated (yet).

---

## Out of Scope

- Body structure validation (future enhancement)
- Automated body rewriting for existing specs
- New CLI commands
- Changes to brick/layer/tower semantics (unchanged in V2)

---

## Success Criteria

1. `jigy validate` passes with V2 schema
2. `jigy rebuild` generates correct graph edges
3. All existing tests pass (after fixture updates)
4. `agents/contextJIG.md` matches V2 spec

---

## Risk

| Risk | Mitigation |
|------|------------|
| Large migration surface (~100 files) | Script-assisted bulk rename |
| Bidirectional consistency | Validation checks both directions |
| Broken external tooling | N/A — JIG is internal |

---

## Decisions

1. **Back-references required** — `outcomes` and `architecture` mandatory on specs. Easier to understand a spec in isolation; scripts maintain consistency.
2. **Status removed entirely** — Not frontmatter, not body. Outside JIG's scope. Projects may track status independently if needed.
