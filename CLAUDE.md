# @T2:START (auto-generated, do not edit)
# JIG/DIG Primer

**JIG** = Intent graph. Tracks alignment: Specs ↔ Code ↔ Tests. Evergreen.
**DIG** = Deliberation graph. Captures reasoning behind decisions. Archival.

## When to Read Full Context

**Read `agents/contextJIG.md` when:**
- Creating/modifying O-###, S-###, A-### documents
- Working with bricks, layers, towers
- Validation errors about references or partition
- Need ID format patterns or frontmatter schema

**Read `agents/contextDIG.md` when:**
- User says "dig this" (or "dig that", "dig it")
- Creating deliberation documents
- Changing document status to terminal
- Need frontmatter schema or anti-patterns

## JIG Cheat Sheet

**Hierarchy:** Charter → Goals (G-###) → Architecture/Outcomes (A/O-###) → Specs (S-###) → Tests/Code

**Decorators:**
```python
@jig.implements("S-001")  # code
@jig.verifies("S-001")    # tests
```

**Commands:**
```bash
jigy validate       # check alignment
jigy rebuild        # regenerate graphs
```

**Rules:**
- Every T/C links to S or O
- Specs = observable behavior, not implementation
- H1 heading must match frontmatter `title` exactly
- Filename: `S-001_Title_In_Snake_Case.md`

## DIG Cheat Sheet

**Types:** exploration, concept, scope, jigplan, plan, journal, wu, retrospective

**Statuses:** `active` → `parked` | `implemented` | `abandoned` | `superseded`

**Terminal statuses require `decision:`** → completed | replaced | deferred | rejected

**Commands:**
```bash
digy new <type> "<title>"
digy validate
```

**Mistakes:**
- `status: draft` → use `active`
- `status: complete` → use `implemented` + `decision: completed`
- Specs in frontmatter → put `[[S-###]]` in body text


# JIG Workflow Tasks

**Flow:** SCOPE → JIGPLAN → PLAN → Execution

| Task | Role | When to Use |
|------|------|-------------|
| `taskMakeJIGPLAN` | Architect | Create O/S nodes, brick changes, decorator plan. Requires human approval. |
| `taskMakePLAN` | Planner | Break approved JIGPLAN into sequenced Work Units. |
| `taskDoPLAN` | Orchestrator | Launch sub-agents for each WU, verify gates, maintain JOURNAL. |
| `taskDoWU` | Worker | Execute single WU with TDD. Return structured report. |

**Key constraints:**
- JIGPLAN creates O/S files, not PLAN
- Clean break default (no compat shims unless SCOPE requests)
- FORBIDDEN bricks = immediate escalation if touched
- Validation WU before Cleanup WU
- Sub-agents return structured reports, orchestrator verifies independently

**Escalate if:**
- FORBIDDEN brick needed
- Layer violation
- Spec ambiguity
- Need for backwards compat not in SCOPE


# Development Environment

**CRITICAL**: Activate venv before any Python/JIG commands.

```bash
source .venv/bin/activate
which python  # must show .venv/bin/python
```

Commands require venv: `python`, `pytest`, `jigy`, `digy`


# Testing

- Align tests to JIG specs. Mismatch → STOP and ask.
- TEST OUTPUT MUST BE PRISTINE.
- Never ignore logs - they contain critical info.
- Must have unit + integration + e2e tests.

## Mocking Policy

**Never mock domain types** (effects, dataclasses, value objects) - use real instances.
**Only mock external I/O** (network, filesystem, database, external services).
# @T2:END
# @T3 (project-specific, edit freely)
