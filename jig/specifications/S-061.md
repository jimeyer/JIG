---
id: S-061
title: Minimal Global Options
type: specification
---

# Minimal Global Options

The CLI accepts only `--help` and `--version` as global options.

**Global Options:**
```bash
jigy --help      # Show help and exit
jigy --version   # Show version and exit
```

**Removed Options:**
- `--project-root` — replaced by auto-discovery (S-057)
- `--format` — human-readable output only
- `--verbose` — removed, output is always informative
- `--strict/--lenient` — removed, behavior is fixed
- All other command-specific options

**Behavior:**
- `jigy` (bare) shows help and exits 0
- Unknown flags produce clear error messages
- No global state or configuration files

**Rationale:** Zero-config experience. Users should not need to remember flags or options for common operations. Auto-discovery and sensible defaults eliminate configuration burden.
