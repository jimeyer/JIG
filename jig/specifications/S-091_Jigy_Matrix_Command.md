---
id: S-091
title: Jigy Matrix Command
type: specification
outcome: O-026
outcomes: [O-026]
architecture: [A-002]
---

# Jigy Matrix Command

## Command

```bash
jigy show matrix  # Display layer × tower grid
```

## Constraints

1. **CLI provides layer×tower matrix visualization**
   - Command: `jigy show matrix` (under show group per S-060)
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
   - Shows layer list without matrix (same as `jigy show layers`)

4. **Output format flags**
   - Supports `-j/-m/-v` flags (S-093)

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
Use 'jigy show layers' to view layer structure.
```

## Rationale

The matrix view provides at-a-glance understanding of project structure. It answers "how is complexity distributed across layers and towers?" Grouped under `show` for consistent verb-first structure.
