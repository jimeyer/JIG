---
id: S-093
title: Universal Output Format Flags
type: specification
outcome: O-016
---

# Universal Output Format Flags

All CLI commands support consistent output format flags for machine and agent consumption.

## Flags

| Flag | Short | Purpose |
|------|-------|---------|
| `--json` | `-j` | Machine-parseable JSON output |
| `--markdown` | `-m` | LLM-optimized markdown output |
| `--verbose` | `-v` | Additional detail in any format |

## Acceptance Criteria

1. **Universal availability**: Every command accepts `-j`, `-m`, and `-v` flags
2. **Mutual exclusivity**: `-j` and `-m` cannot be combined; CLI errors with clear message
3. **Default output**: Without flags, output is human-readable terminal format
4. **Verbose modifier**: `-v` adds detail to any format (`-v`, `-j -v`, `-m -v` all valid)
5. **Consistent behavior**: Same flags produce predictable output across all commands

## Flag Combinations

| Combination | Behavior |
|-------------|----------|
| (none) | Human-readable terminal output |
| `-v` | Verbose human output |
| `-j` | Compact JSON (single-line) |
| `-j -v` | Verbose JSON (more fields) |
| `-m` | Compact markdown |
| `-m -v` | Verbose markdown (more sections) |
| `-j -m` | Error: mutually exclusive |

## Implementation

Commands use shared output infrastructure:
- `OutputFormat` enum: `HUMAN`, `JSON`, `MARKDOWN`
- `@add_output_options` decorator adds flags to commands
- `resolve_format()` validates flags and returns format

## Rationale

AI agents and CI systems need machine-parseable output. Universal flags eliminate per-command discovery. The `-j`/`-m` short flags optimize for frequent agent use. Mutual exclusivity prevents ambiguous output.
