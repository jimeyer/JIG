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
{
  "status": "passed|failed",
  "phases": {
    "phase_name": {
      "passed": true,
      "errors": [
        {
          "file": "path/to/file.md",
          "line": 7,
          "code": "INVALID_REFERENCE",
          "message": "Reference O-999 does not exist",
          "severity": "error"
        }
      ]
    }
  },
  "summary": {
    "total_errors": 0,
    "total_warnings": 0,
    "specs_checked": 91,
    "bricks_checked": 11
  }
}
```

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

Verbose JSON adds additional fields:
- `metadata`: timestamps, versions
- `context`: related information
- `suggestions`: actionable next steps for errors

## Rationale

CI systems, editor integrations, and AI agents need machine-parseable output. Structured error codes enable automated handling. Single-line format minimizes token usage for agents.
