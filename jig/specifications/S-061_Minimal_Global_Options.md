---
id: S-061
title: Minimal Global Options
type: specification
outcome: O-019
---

# Minimal Global Options

The CLI accepts minimal global options to maintain zero-config experience while enabling machine output.

## Global Options

```bash
jigy --help      # Show help and exit
jigy --version   # Show version and exit
jigy --no-rebuild  # Skip auto-rebuild (S-071)
```

## Universal Output Flags

All commands accept output format flags (S-093):

```bash
-j, --json       # Machine-parseable JSON output
-m, --markdown   # LLM-optimized markdown output
-v, --verbose    # Additional detail in any format
```

## Removed Options

- `--project-root` — replaced by auto-discovery (S-057)
- `--strict/--lenient` — removed, behavior is fixed
- `--format <type>` — replaced by `-j` and `-m` short flags

## Behavior

- `jigy` (bare) shows help and exits 0
- Unknown flags produce clear error messages
- Output flags are command-level, not global (each command handles its own)
- Default output is human-readable (no flags required)

## Rationale

Zero-config experience for common operations. Output format flags enable CI and agent integration without complex flag syntax. Short flags (`-j`, `-m`, `-v`) optimize for frequent programmatic use.
