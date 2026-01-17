---
id: S-026
title: JSON Output Format for CI Integration
type: specification
outcome: O-016
outcomes: [O-016]
---

# JSON Output Format for CI Integration

CLI commands produce structured JSON output when `-j/--json` flag is used.

## Acceptance Criteria

1. **Flag**: `-j` or `--json` available on all commands (per S-093)
2. **Single-line**: JSON output is compact, not pretty-printed (saves tokens)
3. **Complete**: All data needed for programmatic processing, no follow-up required
4. **Typed**: Numbers are numbers, booleans are booleans (not stringified)
5. **Valid**: Output is always parseable JSON with no syntax errors
6. **Consistent schema**: Same command produces same JSON structure

## Validation Output Schema

```json
{"valid":true,"summary":{"specs":78,"outcomes":23,"goals":5,"bricks":11,"functions":115,"tests":604},"errors":[]}
```

Expanded for readability:
```json
{
  "valid": true,
  "summary": {
    "specs": 78,
    "outcomes": 23,
    "goals": 5,
    "bricks": 11,
    "functions": 115,
    "tests": 604
  },
  "errors": []
}
```

On failure, `errors` contains structured error objects:
```json
{
  "valid": false,
  "summary": {...},
  "errors": [
    {
      "file": "path/to/file.md",
      "line": 7,
      "code": "INVALID_REFERENCE",
      "message": "Reference O-999 does not exist"
    }
  ]
}
```

Key design choices:
- `valid: true` boolean (not `status: "passed"`) for ergonomic agent code
- Flat `errors` array at top level (agents don't iterate phases to find failures)
- `summary` contains domain-specific counts, not generic totals

## Rebuild Output Schema

```json
{
  "status": "success",
  "graphs": ["implementation", "verification", "intent"],
  "duration_ms": 1234
}
```

## Show/Query Output Schema

```json
{
  "type": "layers|bricks|towers|matrix",
  "data": { ... }
}
```

## Verbose Mode (-j -v)

Verbose JSON may add additional fields within `summary` for detailed breakdowns. The core schema (`valid`, `summary`, `errors`) remains consistent.

## Rationale

CI systems, editor integrations, and AI agents need machine-parseable output. Structured error codes enable automated handling. Single-line format minimizes token usage for agents.
