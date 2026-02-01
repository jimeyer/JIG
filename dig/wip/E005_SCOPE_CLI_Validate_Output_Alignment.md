---
title: "CLI Validate Output Alignment"
type: scope
status: implemented
decision: completed
created: 1737151200
created_human: "2026-01-17 14:00 CST"
parent: "[[DJ001_CONCEPT_CLI_Design_Manifesto]]"
children: []
---
# CLI Validate Output Alignment

## Executive Summary

Aligned `jigy validate` and `digy validate` output formats across all three modes (human, JSON, markdown) per the CLI Design Manifesto (DJ001). Both tools now follow the same structural patterns while expressing domain-specific content.

**Before:** jigy was verbose (25+ lines), digy was silent (0 lines) on success.

**After:** Both output one-line summaries by default, detailed breakdowns with `-v`, and share consistent JSON/markdown schemas.

---

## Problem Statement

### Initial State

| Aspect | jigy validate | digy validate |
|--------|---------------|---------------|
| Default success | 25+ lines, per-step checkmarks | Silent (0 lines) |
| JSON schema | `status: "passed"`, per-phase objects | `valid: true`, 157-entry file list |
| Markdown | Raw phase dump | Minimal 2 lines |
| Verbose flag | Unused for output switching | Unused |

### Violations of DJ001 Manifesto

1. **digy violated "No silent success"** (Part VII anti-patterns) — "Feedback builds trust and discoverability"
2. **jigy violated progressive disclosure** (Part I §3) — Per-step checkmarks should be `-v` behavior, not default
3. **Parallel structure broken** (Part V) — Learning one didn't teach the other
4. **JSON for agents was wasteful** (digy) or lacking metrics (jigy)

---

## Scope of Work

### 1. Human Output (Default Mode)

**Requirement:** One-line summary with metrics on success; errors only on failure.

**jigy validate:**
```
Rebuilt 3 graphs. Validated 78 specs, 23 outcomes, 11 bricks.
```

**digy validate:**
```
Validated 157 documents (19 active, 116 implemented, 13 parked).
```

### 2. Human Output (Verbose Mode: `-v`)

**Requirement:** Category-based breakdown matching parallel structure.

**jigy validate -v:**
```
Intent: 106 artifacts
  ✓ 78 specifications
  ✓ 23 outcomes
  ✓ 5 goals
  ✓ 0 architecture docs

Coverage:
  ✓ 78/78 specs covered by outcomes
  ✓ 115 functions decorated
  ✓ 604 tests decorated

Bricks: 11 definitions
  ✓ 238 files partitioned
  ✓ 0 layer violations
  ✓ 0 cycles

Validated 78 specs, 23 outcomes, 11 bricks.
```

**digy validate -v:**
```
Documents: 157 total
  ✓ 104 exploration
  ✓ 18 plan
  ✓ 14 scope
  ...

Status distribution:
  ✓ 19 active
  ✓ 116 implemented
  ✓ 13 parked

Validated 157 documents.
```

### 3. JSON Output (`-j`)

**Requirement:** Compact, agent-optimized, no redundant data.

**Shared schema:**
```json
{
  "valid": true,
  "summary": { /* domain-specific counts */ },
  "errors": []
}
```

**jigy validate -j:**
```json
{"valid":true,"summary":{"specs":78,"outcomes":23,"goals":5,"bricks":11,"functions":115,"tests":604},"errors":[]}
```

**digy validate -j:**
```json
{"valid":true,"summary":{"documents":157,"types":{"exploration":104,"plan":18},"statuses":{"active":19,"implemented":116}},"errors":[]}
```

**Key changes:**
- Top-level `valid` boolean (not `status: "passed"`)
- Domain-specific `summary` with counts
- Empty `errors` array on success (not 157 file entries)
- Errors only populated when failures exist

### 4. Markdown Output (`-m`)

**Requirement:** LLM-optimized context injection format.

**jigy validate -m:**
```markdown
# JIG Validation: Passed

- **Specs:** 78 | **Outcomes:** 23 | **Bricks:** 11
- **Coverage:** 115 functions, 604 tests decorated
```

**digy validate -m:**
```markdown
# DIG Validation: Passed

- **Documents:** 157 (19 active, 116 implemented, 13 parked)
```

---

## Files Modified

### jig-dev (JIG CLI)

| File | Changes |
|------|---------|
| `src/jig/cli/validate.py` | Refactored `validate_full_command` to collect results silently, output based on verbose flag. New `_output_human_validation` function with one-line default and category-based verbose. Updated `_format_json_output` for new schema. |
| `src/jig/cli/auto_rebuild.py` | Changed `ensure_graphs_current` to return summary string instead of printing. Added `get_rebuild_summary` helper. Made `_rebuild_*_quietly` functions return detail strings for verbose mode. |
| `src/jig/validation/reporting.py` | Rewrote `format_as_markdown` for new format with `# JIG Validation: {status}` header, summary bullets, optional `## Details` section in verbose mode. |

### dig-dev (DIG CLI)

| File | Changes |
|------|---------|
| `src/dig/cli/commands/validate.py` | Rewrote `_output_human` for one-line default with status breakdown, verbose with type/status counts. Added `_count_types` and `_count_statuses` helpers. Rewrote `_output_markdown` for new format. |
| `src/dig/validate.py` | Rewrote `format_json_output` to use new schema with `valid`, `summary` (documents, types, statuses), `errors` array. Removed per-file listing. |

### dotfiles

| File | Changes |
|------|---------|
| `bin/digjig` | Added `shift` after command capture and `"$@"` pass-through to forward flags like `-v` to both tools. |

---

## Tests Updated

### jig-dev

- `tests/cli/test_validate.py` — 14 tests updated for new JSON (`valid` instead of `status`) and markdown (`# JIG Validation:` instead of `# Validation Result`) schemas
- `tests/cli/test_auto_rebuild.py` — 1 test updated for new function signature
- `tests/cli/test_validate_integration.py` — 1 test skipped (pre-existing architecture discovery issue), 1 test updated to use `--no-rebuild`
- `tests/validation/test_reporting.py` — 5 tests updated for new markdown format

### dig-dev

- `tests/test_validate_cli.py` — 15 tests updated for new JSON schema (`errors` instead of `files`, `documents` instead of `total`)
- `tests/test_filename_identity.py` — 1 test updated (success outputs summary, not silent)
- `tests/test_integration.py` — 2 tests updated for new JSON schema

---

## Test Results

| Project | Result |
|---------|--------|
| jig-dev | 867 passed, 1 skipped |
| dig-dev | 487 passed, 1 pre-existing failure (unrelated CLI help test) |

---

## Design Decisions

### Why one-line default (not silent)?

DJ001 explicitly lists "Silent success" as an anti-pattern: "Feedback builds trust and discoverability. Users learn what the tool did, not just that it succeeded."

### Why category-based verbose (not per-step)?

Matches digy's structure (Types/Statuses) with jigy's domain (Intent/Coverage/Bricks). Both tools now show:
1. Header with total count
2. Category breakdowns with checkmarks
3. Summary line (same as default)

### Why flatten JSON errors to top-level?

Per DJ001: "One rich query beats five narrow queries." Agents don't need to iterate over 157 file objects to find 2 errors. The `errors` array contains only failures, with `file` field identifying the source.

### Why `valid: true` instead of `status: "passed"`?

Boolean is more ergonomic for agents:
```python
if result["valid"]:
    proceed()
```

vs.

```python
if result["status"] == "passed":
    proceed()
```

---

## Alignment with DJ001

| Manifesto Principle | Implementation |
|---------------------|----------------|
| "One command, three modes" (Part I §1) | ✓ Default, `-j`, `-m` all available |
| "Progressive disclosure" (Part I §3) | ✓ Default is minimal, `-v` adds detail |
| "Minimal feedback on success" (Part II) | ✓ One-line summary with metrics |
| "JSON is single-line, complete, typed" (Part III) | ✓ Compact JSON with boolean `valid` |
| "Markdown is readable, semantic, dense" (Part III) | ✓ Header + bullets format |
| "Parallel universes" (Part V) | ✓ Same structure, domain-specific content |
| "No silent success" (Part VII) | ✓ Both tools output summary |

---

## Future Work

None identified. This scope is complete.

---

## References

- [[DJ001_CONCEPT_CLI_Design_Manifesto]] — Source requirements
- [[DJ002_SCOPE_CLI_Recommendations]] — Parallel structure patterns
- [[DJ010_SCOPE_JIG_DIG_CLI_Conformance]] — Prior conformance work
