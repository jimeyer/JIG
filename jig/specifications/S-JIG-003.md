---
id: S-JIG-003
type: specification
title: "Commands output valid YAML"
subsystem: core
created: 2025-11-18
---

# Specification: Structured Output for Composability

All JIG commands support `--output yaml` (and optionally `--output json`) to enable Unix-style composition.

## Requirements

### Output Modes

Commands support multiple output modes via `--output` flag:
- `text` (default): Human-friendly, colored output
- `yaml`: Machine-readable YAML
- `json`: Machine-readable JSON (optional, YAML preferred)

### Structured Output Format

Each command outputs a consistent schema:

```yaml
# jig validate --output yaml
status: success|error
errors: []
warnings: []
data:
  nodes_checked: 47
  nodes_valid: 45
  nodes_invalid: 2
```

```yaml
# jig extract --output yaml
status: success
markers:
  - type: DISCOVERY
    text: "Multi-process required for parallelism"
    file: jig/deltas/active/feature-x/PLAN.md
    line: 23
    relates: [O-PERF-001]
```

### Exit Codes

Consistent exit codes across all commands:
- `0`: Success
- `1`: Validation/logical errors (e.g., invalid nodes found)
- `2`: Usage errors (e.g., invalid arguments)
- `3`: System errors (e.g., file not found)

### Stream Separation

- STDOUT: Data output (YAML/JSON/text)
- STDERR: Diagnostics, warnings, progress

This enables: `jig extract 2>/dev/null | jq '.markers'`

### Quiet Mode

All commands support `--quiet` flag:
- Suppresses human-friendly output
- Only outputs structured data
- Errors still go to STDERR

## Examples

```bash
# Get error count from validation
jig validate --output yaml | yq '.data.nodes_invalid'

# Extract and filter markers
jig extract --output yaml | yq '.markers[] | select(.type == "DISCOVERY")'

# Chain with jq
jig graph --output json | jq '.subsystems[] | select(.coupling_ratio < 10)'

# Check status in CI
if jig validate --quiet; then
  echo "Valid"
fi
```

## Rationale

Composability is a core Unix principle. Structured output enables:
- Integration with existing tools (jq, yq, grep)
- Custom workflows without modifying JIG
- CI/CD automation
- Programmatic use

## Acceptance Criteria

- All commands support `--output yaml`
- YAML output is valid (parseable by standard tools)
- Exit codes match specification
- STDOUT/STDERR separation enforced
- `--quiet` suppresses non-essential output

## Related

- implements: O-JIG-003 (composability)
- subsystem: core

## History

- 2025-11-18: Created during WU0 bootstrap (known constraint from SCOPE)
