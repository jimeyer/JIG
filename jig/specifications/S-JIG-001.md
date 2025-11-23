---
id: S-JIG-001
type: specification
title: "Marker extraction processes 1000 files in <1s"
subsystem: core
implements:
  - O-JIG-001
created: 2025-11-18
---

# Specification: High-Performance Marker Extraction

The `jig extract` command must process 1000 files with markers in under 1 second.

## Requirements

### Performance
- Process 1000 files in <1 second (wall-clock time)
- Linear scaling: 10,000 files in <10 seconds
- Memory usage <100MB for typical projects (<10k files)

### Implementation Approach
- Use regex matching, not full parsers
- Stream file processing (don't load all into memory)
- Parallelize if beneficial (measure first)
- Skip binary files automatically

### Marker Format
Simple inline markers for fast regex extraction:
```
#DISCOVERY "one-line summary"
#LEARNED "one-line summary"
#DECISION "one-line summary"
#RELATES node-id
```

### Output
YAML report with:
- marker type
- text content
- file path
- line number
- related node IDs (if any)

## Rationale

Git-like speed is essential for developer adoption. If extraction is slow, developers won't run it frequently. Fast extraction enables:
- Pre-commit hooks
- Frequent validation
- CI integration without slowdown

Target: grep-level performance (ripgrep as reference).

## Acceptance Criteria

- Benchmark test: 1000 markdown files with 100 markers total
- Must complete in <1 second on modern laptop
- Must handle malformed markers gracefully (skip, don't crash)
- Must report file count and marker count

## Related

- implements: O-JIG-001 (performance outcome)
- subsystem: core

## History

- 2025-11-18: Created during WU0 bootstrap (known constraint from SCOPE)
