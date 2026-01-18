---
id: S-104
title: Validation Fix Template Output
type: specification
outcomes: [O-029, O-005]
architecture: [A-004]
---

# Validation Fix Template Output

The `jigy validate -j` command outputs validation errors as JSON, where each error includes a `fix` field containing structured repair instructions.

**Acceptance Criteria**:
- Command `jigy validate -j` outputs JSON to stdout
- Each error object includes `id`, `message`, `file`, `line`, `fix`, and `spec` fields
- The `fix` field is an object with `action`, `target`, `params`, `auto`, and `suggestions` fields
- The `action` field names the repair operation (e.g., `set_field`, `rename_file`)
- The `auto` field is boolean indicating if the fix is safe to apply automatically
- The `suggestions` field contains human-readable repair guidance when `auto` is false
- Output includes `summary` object with `total`, `auto_fixable`, and `manual` counts
- Exit code 0 when no errors, 1 when errors present

**Rationale**: Machine-readable fix templates enable automated repair via `jigy mend` and agent-assisted fixing. The JSON format is consumable by both CLI tools and AI agents.

**Example Output**:
```json
{
  "errors": [
    {
      "id": "abc123def456",
      "message": "Missing required field: outcomes",
      "file": "jig/specifications/S-099.md",
      "line": 1,
      "spec": "S-018",
      "fix": {
        "action": "set_field",
        "target": "outcomes",
        "params": {"value": []},
        "auto": false,
        "suggestions": ["Add outcomes field with list of O-### IDs"]
      }
    }
  ],
  "summary": {
    "total": 1,
    "auto_fixable": 0,
    "manual": 1
  }
}
```
