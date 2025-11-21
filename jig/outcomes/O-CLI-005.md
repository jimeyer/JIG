---
id: O-CLI-005
type: outcome
title: "Progressive Disclosure of Information"
subsystem: cli
created: 2025-11-21
---

# Outcome: Progressive Disclosure of Information

Default output fits on screen. --verbose provides detailed information. Summary always shown first.

## Value

CLI output that dumps everything at once overwhelms users and obscures the most important information. When `status` shows 12 orphaned nodes as a newline-separated list, it takes 13 lines just for that one warning. When output is 100+ lines long, users miss critical information and scrollback becomes necessary.

Progressive disclosure respects the user's attention and terminal space:
- **Default output**: Concise summary with key metrics and warnings
- **Verbose output**: Full details including file paths, complete edge lists, per-file validation
- **Summary first**: Most important information at the top

Progressive disclosure enables:
- **Quick health checks**: Scan status in 1-2 seconds without scrolling
- **Drill-down when needed**: Add --verbose to see details
- **Better focus**: Most important info (warnings, suggestions) is visible
- **Terminal-friendly**: Output respects 24-line terminals

## Success Metrics

- Default output fits in 24 lines for typical projects (<100 nodes)
- Key information visible without scrolling in >90% of cases
- <5% of users report "too much output" in surveys
- Summary line always present: "✓ 20 nodes, 8 edges, 1 subsystem"

## Acceptance Criteria

- Default output shows:
  - Summary line with counts (nodes, edges, subsystems)
  - Node summary (type breakdown)
  - Subsystem list (with counts, not full node lists)
  - Warnings (aggregated, not per-item)
  - Suggestions (actionable, not verbose)
- Default output uses space-efficient formatting:
  - Comma-separated lists instead of newline-separated (saves 10-12 lines)
  - Counts in parentheses for quick scanning
  - Section headers without redundant content
- Verbose output adds:
  - Individual node titles under subsystems
  - Complete edge list with relationship types
  - Per-file validation results with paths
  - File paths for all nodes
- Summary always first:
  - Status line at top: "✓ 20 nodes, 8 edges, 1 subsystem"
  - Node summary before detailed sections
  - Warnings before suggestions

## Related

- implements: S-CLI-007 (Status Command Output Format - summary line)
- implements: S-CLI-009 (Graph Command Output Format - compact option)
- related: O-CLI-003 (Consistent CLI Output Formatting)
- subsystem: cli

## History

- 2025-11-21: Created during WU0 (known constraint from S011_SUMMARY_cli_output_alignment.md)
