---
id: O-JIG-002
type: outcome
title: "JIG uses simple text formats (YAML + Markdown)"
subsystem: core
created: 2025-11-18
---

# Outcome: Simple Text Formats

All JIG artifacts are human-readable text files using standard formats: YAML frontmatter and Markdown content.

## Value

Text files work with standard Unix tools (grep, diff, sed). They're version-controllable, merge-able, and future-proof. No special viewers or databases required.

Developer can:
- Read Intent with `cat` or any text editor
- Search with `grep -r "pattern" jig/`
- See meaningful diffs in pull requests
- Merge Intent changes like code
- Work offline without databases

## Success Metrics

- Zero binary file dependencies for core functionality
- All OSTC nodes readable without special tools
- Git diffs show semantic changes clearly
- Merge conflicts are human-resolvable

## Acceptance Criteria

- OSTC nodes: Markdown with YAML frontmatter
- Config files: TOML (like git config)
- Graph index: YAML
- Harvest reports: YAML
- No database required for core operations

## Related

- specs: S-JIG-002, S-JIG-003
- subsystem: core

## History

- 2025-11-18: Created during WU0 bootstrap (known constraint from SCOPE)
