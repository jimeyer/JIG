---
id: S-064
title: Path Configuration with Defaults
type: specification
outcomes: [O-020]
architecture: [A-003]
---

# Path Configuration with Defaults

JIG provides configurable paths with sensible defaults for standard project layouts.

**Acceptance Criteria:**
- Default paths when no configuration exists:
  - `source`: `"src"`
  - `tests`: `"test"`
  - `jig_root`: `"jig"`
  - `specifications`: `"specifications"` (relative to jig_root)
  - `outcomes`: `"outcomes"` (relative to jig_root)
  - `bricks`: `"bricks.yaml"` (relative to jig_root)
  - `generated`: `"generated"` (relative to jig_root)
- Partial configuration merges with defaults (unset paths use defaults)
- All paths resolve to absolute paths relative to project root
- Configured paths override defaults exactly as specified

**Rationale:** Convention over configuration - standard layouts need no config, custom layouts override only what differs.

**References:** A003 (Configuration Architecture)
