---
id: S-114
title: Project Overview Output
type: specification
outcomes: [O-019, O-030]
architecture: [A-002]
---

# Project Overview Output

The Project Overview provides unified context for agent orientation, combining data from multiple sources into a single output.

## Content Structure

The overview includes these sections:

1. **Charter** - Project name and summary from Charter.md
2. **Goals** - G-### IDs with titles from Charter
3. **Architecture** - A-### documents with titles
4. **Outcomes** - O-### with titles and supporting goal IDs
5. **Specifications** - Count by implementation/verification status
6. **Bricks** - Brick IDs organized by layer
7. **Towers** - Tower structure (if multi-tower project)
8. **Traversal Keys** - Valid identifiers for `context <id>` queries

## Output Formats

### Human (terminal)

```
JIG: JIG Project

Goals:
  G-001: Grounding in Reality
  G-002: Continuity Across Sessions
  ...

Bricks by Layer:
  Layer 0: B-decorators, B-config, B-validation
  Layer 1: B-cli, B-verification-graph

Specs: 113 total (98 implemented, 85 verified)

Traversal keys: S-001..S-113, O-001..O-030, G-001..G-005, B-cli, ...
```

### JSON (-j)

```json
{
  "charter": {"name": "JIG", "file": "jig/Charter_JIG.md"},
  "goals": [{"id": "G-001", "title": "Grounding in Reality"}, ...],
  "architecture": [{"id": "A-001", "title": "...", "file": "..."}, ...],
  "outcomes": [{"id": "O-001", "title": "...", "goals": ["G-001"]}, ...],
  "specs": {"total": 113, "implemented": 98, "verified": 85},
  "bricks_by_layer": {"0": ["B-decorators", ...], "1": ["B-cli", ...]},
  "towers": null,
  "traversal_keys": ["S-001", "S-002", ..., "B-cli", ...]
}
```

### Markdown (-m)

LLM-optimized format with structured headers and bullet lists.

## Acceptance Criteria

1. Overview includes all eight content sections
2. Charter section extracts name from H1 heading
3. Goals section lists all G-### with titles from Charter
4. Specs section shows total/implemented/verified counts
5. Bricks section groups by layer number
6. Traversal keys include all valid identifiers for context queries
7. Output respects -j/-m/-v flags per S-093
8. Missing sections (e.g., no towers) are omitted, not shown empty

## Rationale

Agents need one command to orient themselves in a project. The overview answers "what exists and how do I explore it?" in one call. The traversal keys section enables immediate follow-up queries.
