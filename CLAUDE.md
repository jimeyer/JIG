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
# CLAUDE.md - Agent Context for JIG

This file provides guidance for AI agents working on the JIG codebase.

## Project Overview

JIG (Just-In-Graph) is a traceability and alignment tool that connects specifications to implementations to tests. It enables AI agents to understand and navigate complex codebases by providing machine-readable intent graphs.

## Key Commands

```bash
jigy rebuild        # Rebuild all graphs (implementation, verification, intent)
jigy validate       # Validate all artifacts against JIG rules
jigy layers         # Show brick layer structure
jigy align          # Check alignment between intent, implementation, and tests
```

## Creating JIG Intent Documents

When creating specifications, outcomes, or architecture documents:

### Filename Format

All intent documents must use the format: `{S/O/A}-{NNN}_{Title_In_Snake_Case}.md`

Examples:
- `S-001_Python_Code_Structure_Extraction.md`
- `O-015_Completeness_Validation_for_Intent_Graph.md`
- `A-001_JIG_Core_Architecture.md`

### Title Selection

**DO:**
- Describe BEHAVIOR or CAPABILITY, not implementation
- Use noun phrases that complete "This spec defines..."
- Be specific enough to distinguish from other specs
- Choose stable titles that won't change as implementation evolves

**DON'T:**
- Include version numbers (`User_Auth_v2`)
- Use temporal words (`New_Cache`, `Old_Parser`)
- Describe implementations (`Redis_Cache_Layer`)
- Describe tasks (`Fix_Auth_Bug`)
- Use vague comparatives (`Better_Error_Handling`)

### Examples

| Bad | Problem | Good |
|-----|---------|------|
| `New_Redis_Cache` | Temporal + implementation | `Response_Caching` |
| `Fix_Auth_Bug` | Task description | `Session_Persistence` |
| `User_Model_v2` | Version in title | `User_Profile_Schema` |
| `Better_Logging` | Vague comparative | `Structured_Log_Output` |
| `The_Main_Config` | Leading article | `Configuration_Loading` |

### Title Stability

Titles are semi-permanent. Changing a title causes:
- File rename → appears as delete + add in git history
- Broken external references (bookmarks, documentation links)
- Potential merge conflicts

Only rename when scope genuinely changed, not for stylistic preferences.

### H1 Header

The first H1 in the document body MUST match the frontmatter `title` exactly:

```markdown
---
id: S-001
title: Python Code Structure Extraction
type: specification
---

# Python Code Structure Extraction

...content...
```

## JIG Decorators

Use decorators to link code to specifications:

```python
import jig

@jig.implements("S-001")
def extract_functions(source: str) -> list:
    """Extract function definitions from Python source."""
    ...

@jig.verifies("S-001")
def test_extract_functions():
    """Verify function extraction works correctly."""
    ...
```

## Project Structure

```
jig/                    # Intent artifacts
  Charter.md            # Project goals (G-001 through G-005)
  architecture/         # A-NNN documents
  outcomes/             # O-NNN documents
  specifications/       # S-NNN documents
  bricks.yaml           # Brick definitions
  generated/            # Machine-generated graphs (never edit)

src/jig/                # Implementation code
tests/                  # Test code
```

## Validation

Before committing, always run:

```bash
jigy rebuild && jigy validate
```

If validation fails, fix the errors before proceeding.
