---
id: S-116
type: specification
title: Text Search Across JIG Corpus
outcomes: [O-031]
status: active
---

# Text Search Across JIG Corpus

## Behavior

Given a query string, JIG searches all managed markdown files for case-insensitive substring matches and returns structured results.

## Acceptance Criteria

- Case-insensitive substring matching across file content
- Searches specifications, outcomes, architecture documents, and charter
- Each result includes: document ID, title, relative file path, and first matching line as context snippet
- Empty query returns empty list
- No matches returns empty list
- Results capped at configurable limit (default 20)
- All file paths resolved through JigConfig.paths — never hardcoded directory layout
- Works with non-default jig.toml path configuration

## Rationale

JIG has structural graph queries (identifier resolution, traversal) but no text search. Agents and humans need to discover relevant documents by content, not just by ID.
