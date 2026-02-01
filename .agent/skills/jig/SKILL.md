---
name: jig
description: Work with JIG intent graphs. Invoke with /jig.
---

# jig

Manage alignment between specifications, code, and tests.

## Bootstrap

Read `contextJIG.md` (in this skill folder) for universal JIG knowledge:
- G-A-O-S-C-T hierarchy (goals -> outcomes -> specs -> code -> tests)
- Frontmatter schemas for each artifact type
- Decorator syntax (`@jig.implements`, `@jig.verifies`)
- Validation rules

Read project-specific files:
- `jig/bricks.yaml` - brick definitions, layer/tower structure
- `jig/specifications/*.md` - existing specs as examples
- `jig/outcomes/*.md` - existing outcomes

## CLI Commands

| Command | Purpose |
|---------|---------|
| `jigy context` | Project overview |
| `jigy context <id>` | Understand any artifact (S-###, O-###, file path) |
| `jigy validate -j` | Diagnose issues, get fix templates |
| `jigy mend --auto` | Auto-fix safe issues |
| `jigy mend --apply fixes.json` | Apply explicit fixes |

## Workflows

**Understand something:**
```bash
jigy context S-042        # spec and its neighborhood
jigy context src/foo.py   # file's specs and tests
```

**Fix graph issues (validate/mend contract):**
```bash
jigy validate -j > errors.json   # get errors with fix templates
# Fill in ??? values in the fix templates
jigy mend --apply fixes.json     # apply fixes
```

**Create artifacts:**
Read `contextJIG.md` for schemas. Use standard file operations.

**Add decorators:**
```python
@jig.implements("S-042")
def my_function(): ...

@jig.verifies("S-042")
def test_my_function(): ...
```
