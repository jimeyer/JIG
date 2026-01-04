# DIG Frontmatter Schema Reference

## Required Fields

| Field | Type | Example |
|-------|------|---------|
| type | string | "exploration" |
| status | string | "active" |
| created | integer | 1735761600 |
| created_human | string | "2026-01-01 12:00 PST" |
| parent | null or wiki-link | "[[D001_SCOPE]]" |
| children | array of wiki-links | ["[[D002]]", "[[D003]]"] |

## Optional Fields

| Field | Type | Example |
|-------|------|---------|
| prompt | multiline string | "exploring auth options..." |
| superseded_by | wiki-link | "[[D010_SCOPE_v2]]" |

## Valid Types

exploration, scope, jigplan, plan, journal, wu, retrospective

## Valid Statuses

active, parked, implemented, abandoned, superseded
