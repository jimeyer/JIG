---
id: O-CLI-003
type: outcome
title: "Consistent CLI Output Formatting"
subsystem: cli
created: 2025-11-21
---

# Outcome: Consistent CLI Output Formatting

All JIG CLI commands use consistent terminology, formatting patterns, and visual conventions. Users learn the output format once and it applies everywhere.

## Value

Inconsistent output formatting across commands creates cognitive load and makes the tool harder to learn. When `status` uses "Orphaned nodes" but `validate` uses "Nodes not referenced in graph index", users must remember multiple terms for the same concept. When one command uses newline-separated lists and another uses comma-separated lists, output is harder to scan and compare.

Consistent formatting enables:
- **Faster learning**: New users understand one command, understand all commands
- **Better scanning**: Predictable structure helps find information quickly
- **Easier scripting**: Consistent patterns are easier to parse programmatically
- **Professional polish**: Consistency signals quality and attention to detail

## Success Metrics

- 100% of commands use shared formatting library
- 0 terminology inconsistencies across commands (validated by grep)
- <5% of output lines exceed 80 characters (excluding tables)
- User feedback: "Output is clear and consistent" in >90% of surveys

## Acceptance Criteria

- All commands use identical terminology:
  - Nodes without edges → "Orphaned nodes" (everywhere)
  - Nodes missing subsystem → "Unassigned nodes" (everywhere)
  - Node type breakdown → "Node summary" (everywhere)
- All commands use same formatting patterns:
  - Small lists (≤5 items) → comma-separated, single line
  - Large lists (>5 items) → comma-separated, wrapped at ~80 chars
  - Counts shown in parentheses → "Orphaned nodes (12):"
  - Status indicators consistent → ✓ ✗ ⚠ • → ←
- All commands use same visual structure:
  - Summary line first
  - Sections clearly labeled
  - Warnings separate from Suggestions
  - Indentation consistent (2-space for continuations)

## Related

- implements: S-CLI-006 (Standard Formatting Library)
- implements: S-CLI-007 (Status Command Output Format)
- implements: S-CLI-008 (Validate Command Output Format)
- implements: S-CLI-009 (Graph Command Output Format)
- subsystem: cli

## History

- 2025-11-21: Created during WU0 (known constraint from S011_SUMMARY_cli_output_alignment.md)
