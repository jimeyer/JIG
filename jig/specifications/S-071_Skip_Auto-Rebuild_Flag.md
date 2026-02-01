---
id: S-071
title: Skip Auto-Rebuild Flag
type: specification
outcomes: [O-022]
architecture: [A-002]
---

# Skip Auto-Rebuild Flag

A global CLI flag allows skipping staleness detection and auto-rebuild.

**Acceptance Criteria:**
- Flag `--no-rebuild` available as global option on `jigy` command
- When set, commands use existing graphs without checking staleness
- Flag affects `validate`, `show`, and `audit` commands
- No staleness check performed (saves ~50-100ms)
- Flag useful for CI/scripts where rebuild is controlled explicitly

**Usage:**
```bash
jigy --no-rebuild validate      # Use existing graphs, skip staleness check
jigy --no-rebuild show layers   # Display from existing graphs
jigy --no-rebuild audit coverage # Audit without auto-rebuild
```

**Output:**
No rebuild message shown when `--no-rebuild` is set:
```
$ jigy --no-rebuild validate
Validating...
```

**Rationale:** Power users and CI pipelines may want explicit control over rebuild
timing, especially when graphs are known to be current.

