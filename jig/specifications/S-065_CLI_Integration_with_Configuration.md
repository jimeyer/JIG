---
id: S-065
title: CLI Integration with Configuration
type: specification
outcomes: [O-020]
architecture: [A-003]
---

# CLI Integration with Configuration

All JIG CLI commands respect the loaded configuration for path resolution.

**Acceptance Criteria:**
- `jigy validate` discovers artifacts using configured `jig_root`, `specifications`, `outcomes`, `bricks` paths
- `jigy rebuild impl` scans source files using configured `source` path
- `jigy rebuild verify` scans test files using configured `tests` path
- `jigy show layers` loads bricks from configured `bricks` path
- Commands work identically with or without configuration file (defaults apply)
- Configuration is loaded once at CLI entry point and passed to subcommands

**Rationale:** Configuration affects all path-dependent operations consistently.

**References:** A002 (CLI Command Architecture), A003 (Configuration Architecture)
