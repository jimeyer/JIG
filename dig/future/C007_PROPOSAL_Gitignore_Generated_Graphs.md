---
title: "Gitignore Generated Graphs"
type: exploration
status: active
created: 1767479764
created_human: "2026-01-03 16:36 CST"
parent: null
children: []
---
# Gitignore Generated Graphs

**Version:** 1.0
**Status:** Draft
**Date:** 2026-01-03

---

## Problem

JIG graphs in `jig/generated/` are currently version controlled, but this causes:

- **Git noise** — every `jigy rebuild` touches these files, polluting diffs and commit history
- **Merge conflicts** — spurious conflicts in generated files are annoying and meaningless
- **Unnecessary churn** — graphs are 100% derived from specs, decorators, bricks.yaml

## Proposal

1. Recommend `jig/generated/*.ndjson` be added to `.gitignore`
2. Keep `jig/generated/` visible (not hidden) with a tracked README
3. Bake this pattern into JIG tooling so all projects get it right

---

## Tradeoffs Considered

### Arguments FOR gitignoring

| Argument | Weight |
|----------|--------|
| **Git noise** | Strong — every `jigy rebuild` touches these files |
| **Derived data** | Strong — 100% regenerable from source artifacts |
| **Merge conflicts** | Moderate — spurious conflicts are meaningless |
| **Standard practice** | Strong — build artifacts belong in `.gitignore` |

### Arguments AGAINST gitignoring

| Argument | Weight |
|----------|--------|
| **Visibility without tools** | Moderate — can browse architecture without installing jigy |
| **Drift detection** | Weak — CI can enforce `jigy rebuild && git diff --exit-code` |
| **Audit trail** | Weak — source artifacts already provide history |

### On hidden directory (`.generated/`)

Considered but rejected:

| Approach | Pros | Cons |
|----------|------|------|
| `jig/.generated/` | Signals "don't touch" | Some tools skip hidden dirs, non-standard |
| `jig/generated/` + `.gitignore` | Explicit, visible, standard | Slightly more visible |

**Decision:** Keep `generated/` visible with gitignored contents.

---

## Target State

```
jig/generated/
├── README.md                    # tracked, explains regeneration
├── intent-graph.ndjson          # gitignored
├── implementation-graph.ndjson  # gitignored
└── verification-graph.ndjson    # gitignored
```

**.gitignore entry:**
```gitignore
# JIG generated graphs (regenerate with: jigy rebuild)
jig/generated/*.ndjson
```

---

## Changes to JIG Tooling

### 1. Add `jigy init` Command

New command to initialize JIG in a project:

```bash
$ jigy init

Created:
  jig/
  jig/specifications/
  jig/outcomes/
  jig/bricks.yaml
  jig/generated/
  jig/generated/README.md

Recommended: Add to .gitignore:
  jig/generated/*.ndjson

Add now? [Y/n]
```

**Behavior:**
- Creates directory structure
- Creates `jig/generated/README.md` (tracked, explains regeneration)
- Optionally appends to `.gitignore`

### 2. Auto-create README on `jigy rebuild`

When `jigy rebuild` runs and `jig/generated/` doesn't exist or lacks README:

```python
# In rebuild logic
generated_dir = config.project_root / "jig" / "generated"
readme_path = generated_dir / "README.md"

if not readme_path.exists():
    generated_dir.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(GENERATED_README_CONTENT)
```

### 3. Ship Template Files

Add to JIG package:

**`src/jig/templates/generated_README.md`:**
```markdown
# Generated JIG Graphs

These files are machine-generated. Do not edit.

**Regenerate with:**
```bash
jigy rebuild
```

**Files:**
- `intent-graph.ndjson` — specs, outcomes, bricks
- `implementation-graph.ndjson` — functions, calls, decorators
- `verification-graph.ndjson` — tests, coverage

These files should be gitignored. See project `.gitignore`.
```

**`src/jig/templates/gitignore_snippet.txt`:**
```gitignore
# JIG generated graphs (regenerate with: jigy rebuild)
jig/generated/*.ndjson
```

### 4. Update Documentation

- `agents/contextJIG.md` file structure section should show `generated/` as gitignored
- Add note: "Generated graphs are derived data — gitignore them"

### 5. Validation Warning (Optional)

`jigy validate` could warn if generated files are tracked:

```bash
$ jigy validate
Warning: jig/generated/*.ndjson files appear to be tracked in git.
  Recommend adding to .gitignore to reduce commit noise.
```

---

## CI Consideration

With gitignored graphs, CI pipelines need:

```bash
jigy rebuild && jigy validate
```

This is actually better — it proves the graphs are correctly regenerable and catches desync issues.

---

## Summary of Changes

| Change | File/Location | Priority |
|--------|---------------|----------|
| Add `jigy init` command | `src/jig/cli/init.py` | High |
| Auto-create README on rebuild | `src/jig/cli/rebuild.py` | High |
| Ship template files | `src/jig/templates/` | High |
| Update contextJIG.md | `agents/contextJIG.md` | Medium |
| Gitignore validation warning | `src/jig/cli/validate.py` | Low |

---

## Next Steps

1. Review and approve this proposal
2. Create JIGPLAN for implementation
3. Implement `jigy init` command
4. Update rebuild to auto-create README
5. Update documentation
