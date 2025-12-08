# J024: Audit Report Format

**Status:** Proposal
**Date:** 2025-12-07
**Extends:** J017 (JIG Concept v9), J023 (Audit Records and Triggers)
**Related:** J025 (Audit Agents), J026 (Audit Architecture)

---

## Context

JIG audits produce two outputs:
1. **Audit log** (J023) — machine-readable per-edge records for trigger detection
2. **Audit reports** (this document) — human-readable analysis for understanding

This document defines the format for audit report files. Reports explain the "why" behind audit decisions. The log (J023) records the "what" (verdicts and hashes).

### What J024 Defines

- Report file location and naming conventions
- YAML frontmatter schema
- Guidelines for report prose
- Examples of different report types

### What J024 Does NOT Define

- When to audit (that's J023 — triggers)
- How to perform audits (that's J025 — agents and methods)
- Machine-readable audit data (that's J023 — audit log)

---

## Report Files

### Location

```
jig/audits/
├── audit-log.ndjson              # Machine data (J023)
├── audit-S-040.md                # Spec-focused report
├── audit-S-041.md                # Another spec report
├── audit-coverage-2025-12-07.md  # Coverage run report
├── audit-B-cli-2025-12-07.md     # Brick-focused report
└── ...
```

### Naming Conventions

Report naming is flexible. Common patterns:

| Pattern | Use Case |
|---------|----------|
| `audit-S-{id}.md` | Spec-focused audit |
| `audit-coverage-{date}.md` | Batch coverage run |
| `audit-B-{brick}-{date}.md` | Brick-focused audit |
| `audit-{custom}.md` | Custom audit scope |

The `report.file` field in audit-log.ndjson points to the report file.

---

## Frontmatter Schema

Each report has YAML frontmatter with audit metadata.

### Required Fields

```yaml
---
audited_at: 2025-12-07T14:32:00Z
by: agent
method: tiered-v1
edges:
  - edge: F→S
    from: F-jig.cli.layers.layers_command
    to: S-040
  - edge: T→S
    from: T-test_layers.test_layers_command
    to: S-040
  - edge: T→F
    from: T-test_layers.test_layers_command
    to: F-jig.cli.layers.layers_command
---
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `audited_at` | ISO 8601 | Yes | When the audit was performed |
| `by` | string | Yes | Who performed the audit: `agent`, `human`, `ci` |
| `method` | string | Yes | Audit method identifier (see J025) |
| `edges` | list | Yes | Edges covered by this report |

### Edge List Format

Each edge in the `edges` list has:

| Field | Type | Description |
|-------|------|-------------|
| `edge` | enum | Edge type: `F→S`, `T→S`, `T→F` |
| `from` | string | Source node ID |
| `to` | string | Target node ID |

**Note:** Per-edge results (aligned, diverged, etc.) are NOT in the frontmatter. They live in the audit log (J023). The report frontmatter lists what edges were audited; the log records the verdicts.

---

## Report Prose

After the frontmatter, the report contains human-readable analysis.

### Guidelines

1. **Explain reasoning** — Why is each edge aligned or diverged?
2. **Reference specific code** — File paths, line numbers, function names
3. **Note issues** — Coverage gaps, missing tests, potential problems
4. **Suggest improvements** — What could be done to improve alignment?

### Flexible Structure

The prose structure is intentionally flexible. Methods may evolve; the report format should accommodate different analysis styles.

**Recommended sections:**

```markdown
# Audit: [Title]

## Summary
[Brief overview of findings]

## Edge Analysis

### F→S: [function] → [spec]
[Analysis of whether function fulfills spec]

### T→S: [test] → [spec]
[Analysis of whether test verifies spec]

### T→F: [test] → [function]
[Coverage analysis]

## Issues
[Problems found, if any]

## Recommendations
[Suggested improvements, if any]
```

But this structure is not required. A simple report might just be:

```markdown
# Audit: S-040

All edges aligned. Function implements spec correctly, test verifies all acceptance criteria, and test executes the implementation.
```

---

## Examples

### Spec-Focused Audit

**File:** `audit-S-040.md`

```yaml
---
audited_at: 2025-12-07T14:32:00Z
by: agent
method: tiered-v1
edges:
  - edge: F→S
    from: F-jig.cli.layers.layers_command
    to: S-040
  - edge: T→S
    from: T-test_layers.test_layers_command
    to: S-040
  - edge: T→F
    from: T-test_layers.test_layers_command
    to: F-jig.cli.layers.layers_command
---

# Audit: S-040 (Layer Visualization)

## Summary

All edges aligned. The `layers_command` function correctly implements the layer visualization specified in S-040, tests verify all acceptance criteria, and coverage confirms tests execute the implementation.

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

### T→F: test_layers_command → layers_command

**Result: Covered**

Coverage analysis confirms test executes lines 17-89 of `layers.py`.

## Issues

None.
```

### Coverage-Only Audit

**File:** `audit-coverage-2025-12-07.md`

```yaml
---
audited_at: 2025-12-07T14:32:00Z
by: ci
method: pytest-cov
edges:
  - edge: T→F
    from: T-test_auth.test_login
    to: F-auth.authenticate
  - edge: T→F
    from: T-test_auth.test_login
    to: F-auth.validate_token
  - edge: T→F
    from: T-test_auth.test_logout
    to: F-auth.destroy_session
  # ... (potentially hundreds of edges)
---

# Coverage Audit: 2025-12-07

## Summary

Full test suite coverage run. 312 T→F edges analyzed.

- **Covered:** 298 edges
- **Not covered:** 14 edges

## Coverage Gaps

The following T→F edges show tests that claim to verify specs implemented by functions, but don't actually execute those functions:

1. `T-test_validation.test_brick_errors` → `F-validation.check_layer_constraints`
   - Test verifies S-038 but doesn't exercise layer constraint checking
   - Recommendation: Add test case for layer violations

2. `T-test_cli.test_status_command` → `F-cli.format_alignment_table`
   - Test verifies S-025 but uses mock output
   - Recommendation: Add integration test with real formatting

[... additional gaps ...]

## Method

Coverage collected via `pytest --cov` with branch coverage enabled.
```

### Diverged Audit

**File:** `audit-S-015.md`

```yaml
---
audited_at: 2025-12-07T09:15:00Z
by: agent
method: tiered-v1
edges:
  - edge: F→S
    from: F-jig.validation.intent.validate_specs
    to: S-015
  - edge: T→S
    from: T-test_validation.test_spec_validation
    to: S-015
---

# Audit: S-015 (Spec Validation)

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

### Human Review Audit

**File:** `audit-S-042.md`

```yaml
---
audited_at: 2025-12-07T16:00:00Z
by: human
method: human-review
edges:
  - edge: F→S
    from: F-jig.core.graph.build_graph
    to: S-042
---

# Audit: S-042 (Graph Construction)

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

## Relationship to Audit Log

The audit log (J023) and audit reports (J024) work together:

| Aspect | Audit Log | Audit Report |
|--------|-----------|--------------|
| Format | NDJSON | Markdown |
| Purpose | Machine queries, triggers | Human understanding |
| Granularity | Per-edge | Per-audit activity |
| Contains | Verdicts, hashes, method | Analysis, reasoning |
| Updated | Append per edge | Write once per audit |

**The log is authoritative for "what was decided."**
**The report explains "why."**

A log row's `report.file` points to the corresponding report:
```json
{"edge":"F→S",...,"report":{"result":"aligned","confidence":0.9,"method":"tiered-v1","file":"audit-S-040.md"}}
```

---

## Method Identifiers

The `method` field identifies the audit strategy used. Common methods:

| Method | Description |
|--------|-------------|
| `human-review` | Manual human audit |
| `tiered-v1` | Tiered LLM audit (J025) |
| `pytest-cov` | Automated coverage analysis |
| `haiku-consensus-v2` | Multi-model consensus (J025) |

Method identifiers are documented in J025 (Audit Agents).

---

## Design Decisions

### Why markdown for reports?

- Human-readable without tooling
- Git diffs show changes clearly
- Supports rich formatting (code blocks, lists, links)
- Easy to generate from LLMs or manually

### Why frontmatter instead of separate metadata file?

- Single file per audit (simpler)
- Metadata travels with content
- Standard pattern (Jekyll, Hugo, Obsidian)

### Why list edges in frontmatter?

- Shows audit scope at a glance
- Enables validation (are all edges in log?)
- Supports partial audits (subset of edges)

### Why no per-edge results in frontmatter?

- Avoids duplication with log
- Log is authoritative for verdicts
- Report focuses on reasoning, not data

---

## Validation

Reports can be validated against the audit log:

```python
def validate_report(report_path: Path, audit_log: list[dict]) -> list[str]:
    """Check that report edges match log entries."""
    errors = []

    frontmatter = parse_frontmatter(report_path)
    report_file = report_path.name

    # Find log entries pointing to this report
    log_entries = [r for r in audit_log if r['report']['file'] == report_file]

    # Check each edge in frontmatter has a log entry
    for edge in frontmatter['edges']:
        key = (edge['edge'], edge['from'], edge['to'])
        if not any(
            (r['edge'], r['from']['id'], r['to']['id']) == key
            for r in log_entries
        ):
            errors.append(f"Edge {key} in frontmatter but not in log")

    return errors
```

---

## References

- **J023:** Audit Records and Triggers (audit log format)
- **J025:** Audit Agents (methods and strategies)
- **J026:** Audit Architecture Simplification (design rationale)
- **J017:** JIG Concept v9 (S-F-T triangle)

---

_Reports explain. Logs remember._
