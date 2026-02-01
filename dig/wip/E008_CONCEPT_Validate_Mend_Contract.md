---
title: "Validate Mend Contract"
type: concept
status: active
created: 1737162000
created_human: "2026-01-17 19:00 CST"
parent: "[[E006_SCOPE_JIG_Init_And_Skills]]"
children: []
---
# Validate Mend Contract

## Core Insight

`validate` and `mend` work as a pair. Validate diagnoses problems and emits structured errors with **fix templates** — like a return envelope included with each error. The agent (or human) fills in the template and sends it back to `mend` for execution.

```
validate -j → errors with fix templates
     ↓
  [agent fills in ???, decides apply: true/false]
     ↓
mend --apply fixes.json
     ↓
validate -j → fewer/no errors
```

This separates **diagnosis** from **repair**, and **decision** from **execution**.

---

## The Return Envelope Pattern

Every error includes its own fix template:

```json
{
  "id": "err_001",
  "code": "ORPHAN_LINK",
  "message": "O-001 references S-034, but S-034 doesn't reference O-001",
  "context": {
    "O-001.specifications": ["S-034", "S-035"],
    "S-034.outcomes": []
  },
  "fix": {
    "action": "add_field_value",
    "target": "S-034",
    "field": "outcomes",
    "value": "???"
  },
  "auto": false
}
```

The `fix` object is the return envelope. Agent fills in `"value": "O-001"` and returns it.

---

## Similar Patterns in Software

| System | Diagnose | Repair | Notes |
|--------|----------|--------|-------|
| Terraform | `plan -out=plan.tf` | `apply plan.tf` | Plan file is reviewable/editable |
| Git rebase | `-i` shows todo list | Execute edited todo | User edits pick/squash/drop |
| JSON Patch (RFC 6902) | Describe operations | Apply operations | Standard for JSON mutations |
| Database migrations | Generate migration | Run migration | Migration file is reviewable |
| Kubernetes | Desired state YAML | `kubectl apply` | Reconciles actual → desired |
| ESLint | Report errors | `--fix` | Auto-fix only, no template |

JIG's pattern is closest to **Terraform plan/apply**: structured output that can be reviewed, edited, and applied.

---

## Error Template Structure

### Full Schema

```json
{
  "errors": [
    {
      "id": "err_001",
      "code": "ERROR_CODE",
      "message": "Human-readable description",
      "location": {
        "file": "path/to/file.md",
        "line": 5
      },
      "context": {
        "relevant": "data",
        "for": "understanding"
      },
      "fix": {
        "action": "action_name",
        "target": "what to modify",
        "field": "which field",
        "value": "???"
      },
      "auto": false,
      "suggestions": ["hint1", "hint2"]
    }
  ],
  "summary": {
    "total": 5,
    "auto_fixable": 3,
    "manual": 2
  }
}
```

### Field Semantics

| Field | Purpose |
|-------|---------|
| `id` | Unique error identifier for correlation |
| `code` | Machine-readable error type |
| `message` | Human-readable description |
| `location` | Where the error occurs (file, line) |
| `context` | Relevant data for understanding the error |
| `fix` | The return envelope — template for the fix |
| `auto` | Can this be fixed without human decision? |
| `suggestions` | Hints for filling in `???` values |

### The `???` Convention

- `"value": "???"` — Agent must provide a value
- `"value": "O-001"` — Pre-filled, auto-fixable
- `"action": "???"` — Multiple valid actions, agent picks one

---

## Fix Actions

### Frontmatter Actions

| Action | Target | Fields | Description |
|--------|--------|--------|-------------|
| `set_field` | artifact ID | field, value | Set frontmatter field to value |
| `add_field_value` | artifact ID | field, value | Add value to array field |
| `remove_field_value` | artifact ID | field, value | Remove value from array field |
| `rename_field` | artifact ID | old_field, new_field | Rename a field |
| `delete_field` | artifact ID | field | Remove field entirely |

### File Actions

| Action | Target | Fields | Description |
|--------|--------|--------|-------------|
| `rename_file` | file path | new_path | Rename/move file |
| `sync_title` | artifact ID | source (h1\|frontmatter) | Sync title between H1 and frontmatter |
| `set_h1` | artifact ID | value | Set the H1 heading |

### Decorator Actions

| Action | Target | Fields | Description |
|--------|--------|--------|-------------|
| `change_decorator` | file:line | old_ref, new_ref | Change decorator reference |
| `remove_decorator` | file:line | — | Remove the decorator |
| `add_decorator` | file:line | decorator_type, ref | Add a decorator |

### Structural Actions

| Action | Target | Fields | Description |
|--------|--------|--------|-------------|
| `create_artifact` | — | type, id, title, fields | Create new spec/outcome/etc |
| `delete_artifact` | artifact ID | — | Delete artifact (dangerous) |

---

## Error Types and Their Templates

### ORPHAN_LINK (bidirectional linking broken)

```json
{
  "code": "ORPHAN_LINK",
  "message": "O-001 references S-034, but S-034 doesn't reference O-001",
  "context": {
    "forward": {"from": "O-001", "field": "specifications", "to": "S-034"},
    "reverse": {"from": "S-034", "field": "outcomes", "to": null}
  },
  "fix": {
    "action": "add_field_value",
    "target": "S-034",
    "field": "outcomes",
    "value": "???"
  },
  "auto": false,
  "suggestions": ["O-001"]
}
```

**Why not auto?** The agent must decide: add the reverse link, or remove the forward link? Both are valid depending on intent.

### TITLE_MISMATCH (frontmatter vs H1)

```json
{
  "code": "TITLE_MISMATCH",
  "message": "S-042 frontmatter title doesn't match H1",
  "context": {
    "frontmatter_title": "Old Title",
    "h1_title": "New Title"
  },
  "fix": {
    "action": "sync_title",
    "target": "S-042",
    "source": "h1",
    "value": "New Title"
  },
  "auto": true
}
```

**Why auto?** H1 is source of truth (human edits body, frontmatter should follow).

### MISSING_REQUIRED_FIELD

```json
{
  "code": "MISSING_REQUIRED_FIELD",
  "message": "S-042 missing required field 'outcomes'",
  "context": {
    "artifact": "S-042",
    "type": "specification",
    "required_fields": ["id", "type", "title", "outcomes"]
  },
  "fix": {
    "action": "set_field",
    "target": "S-042",
    "field": "outcomes",
    "value": "???"
  },
  "auto": false
}
```

**Why not auto?** We don't know which outcome(s) this spec belongs to.

### INVALID_ID_FORMAT

```json
{
  "code": "INVALID_ID_FORMAT",
  "message": "Spec ID 'S-42' should be 'S-042' (zero-padded)",
  "context": {
    "current": "S-42",
    "expected_pattern": "S-NNN"
  },
  "fix": {
    "action": "set_field",
    "target": "S-42",
    "field": "id",
    "value": "S-042"
  },
  "auto": true
}
```

### FILENAME_ID_MISMATCH

```json
{
  "code": "FILENAME_ID_MISMATCH",
  "message": "File 'S-043_Foo.md' contains artifact with id 'S-042'",
  "context": {
    "filename": "specifications/S-043_Foo.md",
    "frontmatter_id": "S-042"
  },
  "fix": {
    "action": "rename_file",
    "target": "specifications/S-043_Foo.md",
    "new_path": "specifications/S-042_Foo.md"
  },
  "auto": true
}
```

### ORPHAN_DECORATOR

```json
{
  "code": "ORPHAN_DECORATOR",
  "message": "@jig.implements('S-999') references non-existent spec",
  "location": {
    "file": "src/foo.py",
    "line": 42
  },
  "context": {
    "decorator": "@jig.implements('S-999')",
    "spec_exists": false
  },
  "fix": {
    "action": "???",
    "options": ["change_decorator", "remove_decorator", "create_artifact"]
  },
  "auto": false,
  "suggestions": ["S-099", "S-909"]
}
```

**Why `action: ???`?** Multiple valid fixes: typo correction, removal, or create the missing spec.

### MISSING_TYPE_FIELD

```json
{
  "code": "MISSING_TYPE_FIELD",
  "message": "S-042 missing 'type' field",
  "context": {
    "artifact": "S-042",
    "inferred_type": "specification",
    "inference_source": "directory: specifications/"
  },
  "fix": {
    "action": "set_field",
    "target": "S-042",
    "field": "type",
    "value": "specification"
  },
  "auto": true
}
```

**Why auto?** Type is inferrable from directory.

---

## Fix Response Structure

Agent returns fixes.json:

```json
{
  "fixes": [
    {
      "id": "err_001",
      "apply": true,
      "fix": {
        "action": "add_field_value",
        "target": "S-034",
        "field": "outcomes",
        "value": "O-001"
      }
    },
    {
      "id": "err_002",
      "apply": true
    },
    {
      "id": "err_003",
      "apply": false,
      "reason": "Will fix manually"
    }
  ]
}
```

### Response Semantics

| Field | Purpose |
|-------|---------|
| `id` | Correlates to error id from validate |
| `apply` | Whether to apply this fix |
| `fix` | The fix to apply (can override/fill template) |
| `reason` | Optional: why not applying |

For auto-fixable errors, agent can just set `apply: true` without providing `fix` — mend uses the pre-filled template.

---

## CLI Interface

### Validate

```bash
# Human output (default)
jigy validate

# JSON with fix templates
jigy validate -j > errors.json

# Just the counts
jigy validate --summary
```

### Mend

```bash
# Apply all auto-fixable errors
jigy mend --auto

# Apply explicit fixes from file
jigy mend --apply fixes.json

# Both: auto-fix + explicit
jigy mend --auto --apply fixes.json

# Dry run: show what would change
jigy mend --auto --dry-run
jigy mend --apply fixes.json --dry-run

# Interactive: prompt for each ???
jigy mend --interactive
```

### Workflow

```bash
# 1. Diagnose
jigy validate -j > errors.json

# 2. Agent processes errors.json, outputs fixes.json

# 3. Apply
jigy mend --apply fixes.json

# 4. Verify
jigy validate
```

---

## Mend Output

Mend reports what it did:

```bash
$ jigy mend --apply fixes.json
Applied 3 fixes:
  ✓ err_001: Added O-001 to S-034.outcomes
  ✓ err_002: Synced S-042 title from H1
  ✓ err_005: Renamed S-043_Foo.md → S-042_Foo.md
Skipped 1 fix:
  ⊘ err_003: apply=false (Will fix manually)
```

JSON output:
```json
{
  "applied": [
    {"id": "err_001", "action": "add_field_value", "target": "S-034"},
    {"id": "err_002", "action": "sync_title", "target": "S-042"},
    {"id": "err_005", "action": "rename_file", "target": "S-043_Foo.md"}
  ],
  "skipped": [
    {"id": "err_003", "reason": "apply=false"}
  ],
  "failed": []
}
```

---

## Auto-Fix Safety

**Principle:** Auto-fixes are non-destructive and reversible.

**Safe for auto:**
- Adding missing fields with inferrable values
- Syncing titles (H1 is source of truth)
- Zero-padding IDs
- Renaming files to match ID
- Adding reverse links (additive)

**Not safe for auto:**
- Removing links (destructive)
- Deleting artifacts
- Changing decorator references (might be wrong guess)
- Setting relationship fields (outcomes, specs, etc.)

**The --auto flag:** Only applies fixes where `auto: true`.

---

## Agent Integration

### Skill: /jig-mend

```markdown
---
name: jig-mend
description: Fix JIG graph issues. Run after validate reports errors.
---

# jig-mend

Repair JIG graph issues using the validate/mend contract.

## Procedure

1. Run `jigy validate -j` to get errors with fix templates
2. For each error:
   - If `auto: true`, mark `apply: true`
   - If `auto: false`, fill in `???` values using context
   - Set `apply: false` if unsure (ask human)
3. Run `jigy mend --apply fixes.json`
4. Run `jigy validate` to confirm fixes worked
```

### Example Agent Flow

```
Agent: Running jigy validate -j...
Agent: Found 5 errors. 3 auto-fixable, 2 need decisions.

Error err_001: ORPHAN_LINK
  O-001.specifications has S-034, but S-034.outcomes is empty.
  → I'll add O-001 to S-034.outcomes (symmetric linking)

Error err_003: ORPHAN_DECORATOR
  @jig.implements('S-999') at src/foo.py:42
  Suggestions: S-099, S-909
  → Looking at the function... it's about validation.
  → S-099 is "Input Validation" - that matches.
  → I'll change the decorator to S-099.

Agent: Applying fixes...
Agent: Done. Running validate again...
Agent: 0 errors. Graph is healthy.
```

---

## Implementation Notes

### Validate Changes

Current validate reports errors as prose. Need to:
1. Add error codes to all validation rules
2. Generate fix templates for each error type
3. Include `auto` flag based on fix determinism
4. Output structured JSON with `-j` flag

### Mend Implementation

New command:
1. Parse fixes.json
2. For each fix with `apply: true`:
   - Load target artifact
   - Apply action (set_field, add_field_value, etc.)
   - Write back to file
3. Report results

### File Operations

Mend needs helpers for:
- YAML frontmatter read/write (preserve formatting, comments)
- File renaming with git awareness
- Decorator parsing/modification (AST-level for Python)

---

## Open Questions

1. **Should mend create a backup before applying?** Or rely on git?

2. **Undo support?** Mend could output an inverse fixes.json for rollback.

3. **Conflict detection?** If file changed since validate, abort or warn?

4. **Batch vs atomic?** Apply all fixes or stop on first failure?

---

## References

- [[E006_SCOPE_JIG_Init_And_Skills]] — Parent scope
- [[E007_CONCEPT_Context_Command_Design]] — Context command (related)
- [[DJ001_CONCEPT_CLI_Design_Manifesto]] — Output format principles
- Terraform Plan/Apply — https://developer.hashicorp.com/terraform/cli/commands/plan
- JSON Patch RFC 6902 — https://datatracker.ietf.org/doc/html/rfc6902
