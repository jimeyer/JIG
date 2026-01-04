---
id: S-091
title: Jigy Matrix Command
type: specification
outcome: O-026
---

# Jigy Matrix Command

## Constraints

1. **CLI MUST provide layer×tower matrix visualization**
   - Command: `jigy matrix`
   - Rows: layers (0, 1, 2, ...)
   - Columns: towers
   - Cells: brick counts or brick names

2. **Matrix format**
   - ASCII table format
   - Header row with tower names
   - One row per layer
   - Cell shows brick count or "—" if empty

3. **Single-tower project message**
   - When no towers declared: "single-tower project"
   - Shows layer list without matrix (same as `jigy layers`)

## Output Format (Multi-Tower)

```
Layer × Tower Matrix:
          | backend | frontend | shared |
----------+---------+----------+--------+
Layer 0   |    2    |    1     |   3    |
Layer 1   |    1    |    2     |   —    |
Layer 2   |    1    |    —     |   —    |
```

## Output Format (Single-Tower)

```
Single-tower project (no matrix)
Use 'jigy layers' to view layer structure.
```

## Rationale

The matrix view provides at-a-glance understanding of project structure. It answers "how is complexity distributed across layers and towers?" and helps identify architectural imbalances.

