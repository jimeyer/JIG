---
id: S-056
title: CLI Verify Rebuild Command
type: specification
outcomes: [O-018]
architecture: [A-002]
---

# CLI Verify Rebuild Command

The `jigy verify rebuild` command generates the verification graph.

**Usage:**
```bash
jigy verify rebuild [--test-dir PATH] [--no-timestamp]
```

**Behavior:**
- Discovers tests in specified directory (default: `tests/`)
- Parses `@jig.verifies` decorators from all test functions
- Generates `jig/generated/verification-graph.ndjson`
- Prints progress: files discovered, tests found, edges extracted
- Returns exit code 0 on success

**Options:**
- `--test-dir PATH`: Override default test directory
- `--no-timestamp`: Omit timestamp from metadata (for deterministic testing)

**Integration:**
- `jigy rebuild` includes verification graph generation as final step

**Rationale:** CLI parity with `jigy impl rebuild` and `jigy intent rebuild`. Single command regenerates verification graph from source.
