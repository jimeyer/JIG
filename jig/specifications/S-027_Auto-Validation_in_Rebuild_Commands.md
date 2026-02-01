---
id: S-027
title: Auto-Validation in Rebuild Commands
type: specification
outcomes: [O-004]
architecture: [A-002]
---

# Auto-Validation in Rebuild Commands

Graph rebuild commands auto-validate intent artifacts before building, with option to skip for power users.

**Acceptance Criteria**:
- `jigy impl rebuild` validates decorators (S-020) before building implementation graph
- `jigy intent rebuild` validates specs and outcomes (S-018, S-019) before building intent graph
- `jigy verify rebuild` validates test decorators (S-020) before building verification graph
- Validation failures prevent graph generation (fail fast with clear errors)
- Flag `--skip-validation` bypasses auto-validation on all rebuild commands
- Auto-validation uses same validators as `jigy validate intent`
- Error messages indicate validation failed before graph generation
- Exit code 1 on validation failure (consistent with validate commands)

**Rationale**: Prevents generating invalid graphs from malformed artifacts. Fail fast with clear error messages before expensive graph generation. Skip flag for power users who know artifacts are valid.

**References**: AG026 §2.2 (Phase 2: Build Graphs with Auto-Validation)
