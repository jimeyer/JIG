---
id: S-069
title: Staleness Detection Module
type: specification
---

# Staleness Detection Module

A staleness detection module determines whether graphs need rebuilding based on git state.

**Acceptance Criteria:**
- Function `is_stale(graph_type: str, config: JigConfig) -> bool` returns True if graph needs rebuild
- Function `get_staleness_status(config: JigConfig) -> dict[str, bool]` returns status for all graphs
- Staleness is True when:
  - Graph file does not exist
  - Graph metadata cannot be parsed
  - Git HEAD differs AND relevant tree hashes changed
  - Uncommitted files in input directories differ from recorded list
- Staleness is False when git state matches recorded metadata exactly
- Non-git projects: always returns True (cannot detect changes efficiently)

**Performance:**
- Staleness check for all three graphs completes in <100ms
- Uses git subprocess calls: `git rev-parse HEAD`, `git ls-tree`, `git status --porcelain`

**Module Location:** `src/jig/staleness.py`

**Rationale:** Fast staleness detection enables auto-rebuild without adding perceptible
delay when nothing has changed.

