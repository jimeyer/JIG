---
id: S-060
title: Show Command Structure
type: specification
outcome: O-019
outcomes: [O-019]
architecture: [A-002]
---

# Show Command Structure

Structural information is displayed via `jigy show {target}` commands.

## Commands

```bash
jigy show              # Display bricks + layers overview
jigy show layers       # Display layer hierarchy
jigy show bricks       # Display brick details
jigy show towers       # Display tower structure
jigy show matrix       # Display layer × tower grid
jigy show charter      # Display Charter.md
jigy show goals        # Display all goals with supporting artifacts
jigy show architecture # List architecture documents
jigy show architecture <id>  # Display specific architecture doc
```

## Behavior

- `jigy show` (bare): Combined overview of bricks and layer structure
- `jigy show layers`: Layer hierarchy with dependency arrows
- `jigy show bricks`: Brick names, layers, and dependencies
- `jigy show towers`: Tower structure with brick counts per layer (S-090)
- `jigy show matrix`: Layer × tower grid visualization (S-091)
- `jigy show charter`: Display Charter.md content
- `jigy show goals`: Goals with supporting artifacts
- `jigy show architecture`: List or show architecture documents
- All commands use auto-discovered project root (S-057)
- All commands support `-j/-m/-v` output flags (S-093)

## Rationale

Groups structural queries under `show` verb. Provides consistent verb-first pattern for all display operations. Tower and matrix commands moved under `show` to consolidate structural visibility.
