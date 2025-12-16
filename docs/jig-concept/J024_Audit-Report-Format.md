# J024: Audit Report Format

**Status:** Proposal
**Date:** 2025-12-07 (revised 2025-12-16)
**Extends:** J017 (JIG Concept v9), J023 (Audit Records and Triggers)
**Related:** J025 (Audit Agents), J026 (Audit Architecture), J028 (Coverage Audit)

---

## Context

JIG uses a **two-level audit model** (defined in J023):

1. **Audit Log** (`audit-log.ndjson`) — Compact log of audit activities
2. **Detail Files** — Per-edge data in records (NDJSON) or reports (Markdown)

This document defines the **Markdown report format** for semantic audits. Reports contain prose reasoning explaining audit decisions.

### Scope: Semantic Audits Only

| Audit Type | Output Format | Defined In |
|------------|---------------|------------|
| Coverage (T→F) | NDJSON record | J028 |
| **Semantic (F→S, T→S, O→S)** | **Markdown report** | **J024 (this doc)** |

Coverage audits produce structured data (T→F edge lists) → NDJSON records.
Semantic audits require reasoning (why is impl aligned?) → Markdown reports.

### What J024 Defines

- Report file location and naming conventions
- YAML frontmatter schema (including jig_hash for trigger detection)
- Guidelines for report prose
- Examples of different report types

### What J024 Does NOT Define

- When to audit (that's J023 — triggers)
- How to perform audits (that's J025 — agents and methods)
- Coverage audit format (that's J028 — NDJSON records)
- Audit log schema (that's J023)

---

## Report Files

### Location

```
jig/audits/reports/
├── S-040-2025-12-16.md           # Spec-focused report
├── S-041-2025-12-16.md           # Another spec report
├── O-001-2025-12-16.md           # Outcome-focused report
└── ...
```

Reports live in `jig/audits/reports/`, separate from NDJSON records in `jig/audits/records/`.

### Naming Conventions

Report naming follows the pattern: `{target}-{date}.md`

| Pattern | Use Case |
|---------|----------|
| `S-{id}-{date}.md` | Spec-focused audit |
| `O-{id}-{date}.md` | Outcome-focused audit |

The `report` field in audit-log.ndjson points to the report file:
```json
{"id": "S-040-2025-12-16", "type": "spec", "report": "reports/S-040-2025-12-16.md", ...}
```

---

## Frontmatter Schema

Each report has YAML frontmatter with audit metadata and **per-edge results with jig_hash**.

### Required Fields

```yaml
---
id: S-040-2025-12-16
audited_at: 2025-12-16T14:32:00Z
git_commit: abc1234
method: tiered-v1
edges:
  - edge: F→S
    from: F-jig.cli.layers.layers_command
    to: S-040
    result: aligned
    jig_hash_from: d4e5f6
    jig_hash_to: a1b2c3
  - edge: T→S
    from: T-test_layers.test_layers_command
    to: S-040
    result: aligned
    jig_hash_from: e5f6a7
    jig_hash_to: a1b2c3
---
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (matches log entry) |
| `audited_at` | ISO 8601 | Yes | When the audit was performed |
| `git_commit` | string | Yes | Git commit at audit time |
| `method` | string | Yes | Audit method identifier (see J025) |
| `edges` | list | Yes | Edges audited with results and hashes |

### Edge Fields

Each edge in the `edges` list has:

| Field | Type | Description |
|-------|------|-------------|
| `edge` | enum | Edge type: `F→S`, `T→S`, `O→S` |
| `from` | string | Source node ID |
| `to` | string | Target node ID |
| `result` | enum | `aligned`, `diverged`, `inconclusive` |
| `jig_hash_from` | string | Source node content hash at audit time |
| `jig_hash_to` | string | Target node content hash at audit time |

**Why include jig_hash?**

The hashes enable trigger detection (J023). When a node's hash changes, JIG compares against the audited hash to determine if re-audit is needed.

### Result Values

| Result | Meaning |
|--------|---------|
| `aligned` | Edge passes audit (impl fulfills spec, test verifies spec, etc.) |
| `diverged` | Edge fails audit (mismatch detected) |
| `inconclusive` | Cannot determine (ambiguous spec, complex impl, etc.) |

---

## Report Prose

After the frontmatter, the report contains human-readable analysis.

### Guidelines

1. **Explain reasoning** — Why is each edge aligned or diverged?
2. **Reference specific code** — File paths, line numbers, function names
3. **Note issues** — Missing coverage, potential problems
4. **Suggest improvements** — What could be done to improve alignment?

### Structure

```markdown
# Audit Report: [Target]

## Summary
[Brief overview of findings]

## Edge Analysis

### F→S: [function] → [spec]
[Analysis of whether function fulfills spec]

### T→S: [test] → [spec]
[Analysis of whether test verifies spec]

## Issues
[Problems found, if any]

## Recommendations
[Suggested improvements, if any]
```

This structure is **recommended but not required**. A simple report might just be:

```markdown
# Audit Report: S-040

All edges aligned. Function implements spec correctly, test verifies all acceptance criteria.
```

---

## Examples

### Spec-Focused Audit (Aligned)

**File:** `reports/S-040-2025-12-16.md`

```yaml
---
id: S-040-2025-12-16
audited_at: 2025-12-16T14:32:00Z
git_commit: abc1234
method: tiered-v1
edges:
  - edge: F→S
    from: F-jig.cli.layers.layers_command
    to: S-040
    result: aligned
    jig_hash_from: d4e5f6
    jig_hash_to: a1b2c3
  - edge: T→S
    from: T-test_layers.test_layers_command
    to: S-040
    result: aligned
    jig_hash_from: e5f6a7
    jig_hash_to: a1b2c3
---

# Audit Report: S-040 (Layer Visualization)

## Summary

All edges aligned. The `layers_command` function correctly implements the layer visualization specified in S-040, and tests verify all acceptance criteria.

## Edge Analysis

### F→S: layers_command → S-040

**Result: Aligned**

The function implements all acceptance criteria from S-040:
- ✓ Displays bricks grouped by layer
- ✓ Shows layer numbers (0, 1, 2, ...)
- ✓ Lists dependencies for each brick
- ✓ Shows function counts per brick
- ✓ Validates no cycles in dependency graph

Implementation at `src/jig/cli/layers.py:17-89`.

### T→S: test_layers_command → S-040

**Result: Aligned**

Test at `tests/unit/test_layers.py:45` verifies:
- Layer grouping output format
- Dependency display
- Cycle detection error handling

## Issues

None.
```

### Spec-Focused Audit (Diverged)

**File:** `reports/S-015-2025-12-16.md`

```yaml
---
id: S-015-2025-12-16
audited_at: 2025-12-16T09:15:00Z
git_commit: def5678
method: tiered-v1
edges:
  - edge: F→S
    from: F-jig.validation.intent.validate_specs
    to: S-015
    result: diverged
    jig_hash_from: e5f6a7
    jig_hash_to: b2c3d4
  - edge: T→S
    from: T-test_validation.test_spec_validation
    to: S-015
    result: diverged
    jig_hash_from: f6a7b8
    jig_hash_to: b2c3d4
---

# Audit Report: S-015 (Spec Validation)

## Summary

**Diverged.** Implementation missing error case handling specified in S-015.

## Edge Analysis

### F→S: validate_specs → S-015

**Result: Diverged**

S-015 specifies:
> "When a spec file has invalid YAML frontmatter, validation SHALL return a clear error message indicating the file path and parse error."

Current implementation at `src/jig/validation/intent.py:45`:
```python
def validate_specs(specs: list[Spec]) -> list[ValidationError]:
    # ... only checks for missing required fields
    # Does NOT handle YAML parse errors
```

The function catches `KeyError` for missing fields but lets `yaml.YAMLError` propagate unhandled.

### T→S: test_spec_validation → S-015

**Result: Diverged**

Test at `tests/unit/test_validation.py:78` does not include a test case for malformed YAML.

## Recommendations

1. Add try/except for `yaml.YAMLError` in `validate_specs`
2. Return `ValidationError` with file path and parse error message
3. Add test case: `test_spec_validation_invalid_yaml`
```

### Outcome-Focused Audit

**File:** `reports/O-001-2025-12-16.md`

```yaml
---
id: O-001-2025-12-16
audited_at: 2025-12-16T16:00:00Z
git_commit: abc1234
method: tiered-v1
edges:
  - edge: O→S
    from: O-001
    to: S-001
    result: aligned
    jig_hash_from: a1b2c3
    jig_hash_to: d4e5f6
  - edge: O→S
    from: O-001
    to: S-002
    result: aligned
    jig_hash_from: a1b2c3
    jig_hash_to: e5f6a7
  - edge: O→S
    from: O-001
    to: S-003
    result: diverged
    jig_hash_from: a1b2c3
    jig_hash_to: f6a7b8
---

# Audit Report: O-001 (User Authentication)

## Summary

Two of three O→S edges aligned. S-003 no longer fits the outcome's current scope.

## Edge Analysis

### O→S: O-001 → S-001

**Result: Aligned**

S-001 (User Login) directly addresses the outcome's core intent of "users can authenticate."

### O→S: O-001 → S-002

**Result: Aligned**

S-002 (Session Management) is necessary for the authentication outcome to be complete.

### O→S: O-001 → S-003

**Result: Diverged**

S-003 (Password Reset) was originally part of this outcome but the outcome's scope has narrowed. Password reset should be moved to a separate outcome (O-005 "Account Recovery").

## Recommendations

1. Remove S-003 from O-001's `specifies` list
2. Create O-005 for account recovery functionality
3. Add S-003 to O-005's `specifies` list
```

### Human Review Audit

**File:** `reports/S-042-2025-12-16.md`

```yaml
---
id: S-042-2025-12-16
audited_at: 2025-12-16T16:00:00Z
git_commit: abc1234
method: human-review
edges:
  - edge: F→S
    from: F-jig.core.graph.build_graph
    to: S-042
    result: aligned
    jig_hash_from: g7h8i9
    jig_hash_to: j0k1l2
---

# Audit Report: S-042 (Graph Construction)

## Summary

Aligned after manual review. The implementation is complex but correctly handles all specified edge cases.

## Notes

Reviewed by @jamesmeyer. The graph construction algorithm in `build_graph` handles:
- Circular reference detection (lines 120-145)
- Incremental updates (lines 150-180)
- Error recovery (lines 185-210)

The code is harder to follow than I'd like, but it correctly implements S-042. Consider refactoring in a future iteration, but no functional issues found.
```

---

## Relationship to Other Artifacts

### Reports vs Records

| Aspect | Reports (Markdown) | Records (NDJSON) |
|--------|-------------------|------------------|
| **For** | Semantic audits (F→S, T→S, O→S) | Coverage audits (T→F) |
| **Contains** | Prose reasoning + frontmatter | Structured edge data |
| **Location** | `jig/audits/reports/` | `jig/audits/records/` |
| **Defined in** | J024 (this doc) | J028 |

### Reports and Audit Log

The audit log (J023) points to reports via the `report` field:

```json
{"id":"S-040-2025-12-16","type":"spec","report":"reports/S-040-2025-12-16.md",...}
```

The log is authoritative for "what audits happened."
The report explains "why" and contains per-edge results with hashes.

---

## Method Identifiers

The `method` field identifies the audit strategy used. Common methods:

| Method | Description |
|--------|-------------|
| `human-review` | Manual human audit |
| `tiered-v1` | Tiered LLM audit (J025) |
| `haiku-consensus-v2` | Multi-model consensus (J025) |

Method identifiers are documented in J025 (Audit Agents).

---

## Design Decisions

### Why Markdown for reports?

- Human-readable without tooling
- Git diffs show changes clearly
- Supports rich formatting (code blocks, lists, links)
- Easy to generate from LLMs or manually

### Why include jig_hash in frontmatter?

- Enables trigger detection without parsing prose
- Single source of truth for "what was audited"
- Matches J022's hash values for comparison

### Why separate reports/ from records/?

- Clear separation of concerns (prose vs data)
- Different query patterns (grep vs jq)
- Different retention policies may apply

---

## Validation

Reports can be validated for consistency:

```python
def validate_report(report_path: Path, audit_log: list[dict]) -> list[str]:
    """Check that report is consistent with log entry."""
    errors = []

    frontmatter = parse_frontmatter(report_path)
    report_id = frontmatter['id']

    # Find corresponding log entry
    log_entry = find_log_entry(report_id, audit_log)
    if log_entry is None:
        errors.append(f"Report {report_id} has no log entry")
        return errors

    # Check git_commit matches
    if frontmatter['git_commit'] != log_entry['git_commit']:
        errors.append(f"git_commit mismatch: {frontmatter['git_commit']} vs {log_entry['git_commit']}")

    # Check edge count matches summary
    if len(frontmatter['edges']) != log_entry['summary']['edges']:
        errors.append(f"Edge count mismatch")

    return errors
```

---

## References

- **J023:** Audit Records and Triggers (two-level model, log schema)
- **J025:** Audit Agents (methods and strategies)
- **J026:** Audit Architecture Simplification (design rationale)
- **J028:** Coverage Audit (NDJSON record format)
- **J017:** JIG Concept v9 (S-F-T triangle)

---

_Reports explain. Records enumerate. The log remembers both._
