# Task: Orchestrate JIG Audit

**Version:** 1.0.0
**Audience:** Orchestration agent (Opus)
**Purpose:** Coordinate parallel batch audits of JIG outcomes and specifications

---

## Overview

You orchestrate a compliance audit of JIG intent documents (outcomes and/or specifications). You launch sub-agents in parallel batches, collect results, maintain a progress journal, and produce a consolidated audit report.

**Philosophy:**
- Audits are read-only (no modifications)
- Parallel batches for efficiency
- Progress visibility through journal
- Single consolidated results file

---

## Input

You receive one of:
- `audit outcomes` - Audit all outcomes in `jig/outcomes/`
- `audit specs` - Audit all specifications in `jig/specifications/`
- `audit all` - Audit both outcomes and specifications
- `audit <file-path>` - Audit a specific file

---

## Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                         SETUP                                    │
│   1. Discover files to audit                                     │
│   2. Create JOURNAL file                                         │
│   3. Plan batches (10 files per batch)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BATCH EXECUTION                             │
│   For each batch:                                                │
│   1. Launch 10 sub-agents in parallel                           │
│   2. Wait for all to complete                                    │
│   3. Write journal entry (progress + observations)              │
│   4. Collect results                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       COMPLETION                                 │
│   1. Write final journal synthesis                               │
│   2. Generate consolidated AUDIT-RESULTS file                   │
│   3. Report summary to user                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Setup

### 1.1 Discover Files

```bash
# Outcomes
ls jig/outcomes/O-*.md

# Specifications
ls jig/specifications/S-*.md
```

Record the count and list of files.

### 1.2 Create Journal File

Create `docs/wip/JOURNAL-audit-<timestamp>.md`:

```markdown
# Audit Journal

**Started:** YYYY-MM-DD HH:MM
**Scope:** [outcomes | specs | all]
**Total Files:** N
**Batches Planned:** M

---

## Progress

(Entries added during execution)

---

## Synthesis

(Added at completion)
```

### 1.3 Plan Batches

- Batch size: 10 files
- Calculate: `ceil(total_files / 10)` batches
- Record batch plan in journal

---

## Phase 2: Batch Execution

### 2.1 Launch Sub-Agents

For each batch, launch **10 sub-agents in parallel** using the Task tool:

```markdown
For outcomes: Use taskAuditOutcome.md instructions
For specs: Use taskAuditSpec.md instructions
```

**Sub-agent prompt template:**

```
You are auditing a JIG [outcome|specification] for compliance.

Follow the instructions in agents/taskAuditOutcome.md (or taskAuditSpec.md).

File to audit: [file-path]

Return your structured audit report.
```

**Important:** Use `model: "haiku"` for sub-agents to minimize cost and latency.

### 2.2 Collect Results

Wait for all 10 sub-agents to complete. Collect:
- Verdict (PASS/WARN/FAIL) for each file
- Issues found
- Suggested fixes

### 2.3 Write Journal Entry

After each batch completes, write a journal entry:

```markdown
### Batch N/M Complete

**Time:** HH:MM
**Files:** [list of 10 files]
**Results:**
- PASS: X
- WARN: Y
- FAIL: Z

**Observations:**
- [Notable pattern or issue seen across this batch]
- [Any unexpected findings]

**Running Totals:**
- Processed: XX/YY files
- PASS: A, WARN: B, FAIL: C
```

---

## Phase 3: Completion

### 3.1 Journal Synthesis

Add synthesis section to journal:

```markdown
## Synthesis

**Completed:** YYYY-MM-DD HH:MM
**Duration:** X minutes

### Patterns Observed

- [Common issue pattern 1]
- [Common issue pattern 2]

### Quality Distribution

| Verdict | Count | Percentage |
|---------|-------|------------|
| PASS | X | Y% |
| WARN | X | Y% |
| FAIL | X | Y% |

### Recommendations

1. [Systemic fix suggestion]
2. [Process improvement]
```

### 3.2 Generate Audit Results File

Create `docs/wip/AUDIT-RESULTS-<timestamp>.md` using the template below.

---

## Audit Results Template

```markdown
# JIG Audit Results

**Date:** YYYY-MM-DD
**Scope:** [outcomes | specs | all]
**Total Audited:** N files
**Journal:** docs/wip/JOURNAL-audit-<timestamp>.md

---

## Summary

| Verdict | Count | Percentage |
|---------|-------|------------|
| PASS | X | Y% |
| WARN | X | Y% |
| FAIL | X | Y% |

---

## Outcomes

### Passing (X)

| ID | Title | Notes |
|----|-------|-------|
| O-001 | [title] | |
| O-002 | [title] | |

### Warnings (Y)

| ID | Title | Issues |
|----|-------|--------|
| O-005 | [title] | [brief issue summary] |

### Failing (Z)

| ID | Title | Issues |
|----|-------|--------|
| O-012 | [title] | [brief issue summary] |

---

## Specifications

### Passing (X)

| ID | Title | Notes |
|----|-------|-------|
| S-001 | [title] | |

### Warnings (Y)

| ID | Title | Issues |
|----|-------|--------|
| S-027 | [title] | [brief issue summary] |

### Failing (Z)

| ID | Title | Issues |
|----|-------|--------|
| S-089 | [title] | [brief issue summary] |

---

## Common Issues

### Most Frequent Issues

1. **[Issue Name]** (X occurrences)
   - Files: O-001, O-005, S-027, ...
   - Fix: [How to fix]

2. **[Issue Name]** (Y occurrences)
   - Files: ...
   - Fix: [How to fix]

---

## Detailed Reports

### Failing Items (Full Details)

(Include full audit reports for FAIL items only)

#### O-XXX

[Full audit report from sub-agent]

---

#### S-YYY

[Full audit report from sub-agent]

---

## Next Steps

1. [ ] Fix FAIL items (Z total)
2. [ ] Review WARN items (Y total)
3. [ ] Re-run audit after fixes
```

---

## Journal Entry Categories

Use these categories for journal observations:

| Category | Use For |
|----------|---------|
| `progress` | Batch completion, counts |
| `pattern` | Recurring issue across files |
| `surprise` | Unexpected finding |
| `quality` | Notable good or bad example |
| `suggestion` | Process improvement idea |

**Format:**

```markdown
- **[category]:** [observation]
```

---

## Constraints

### DO

- Launch sub-agents in parallel (10 at a time)
- Write journal entries after each batch
- Include running totals in journal
- Consolidate all results into single AUDIT-RESULTS file
- Report final summary to user

### DO NOT

- Modify any audited files
- Skip journal entries
- Launch more than 10 sub-agents simultaneously
- Continue if sub-agent errors occur (stop and report)

---

## Error Handling

**If sub-agent fails to return:**
1. Log in journal: `**error:** Sub-agent timeout for [file]`
2. Mark file as `ERROR` in results
3. Continue with next batch

**If file not found:**
1. Log in journal: `**error:** File not found: [path]`
2. Skip file
3. Continue

---

## Example Execution

### User Request
```
audit outcomes
```

### Orchestrator Actions

1. **Discover:** Found 22 outcomes in `jig/outcomes/`
2. **Create Journal:** `docs/wip/JOURNAL-audit-2025-12-24-1430.md`
3. **Plan:** 3 batches (10, 10, 2)
4. **Batch 1:** Launch 10 sub-agents → 8 PASS, 1 WARN, 1 FAIL → journal entry
5. **Batch 2:** Launch 10 sub-agents → 7 PASS, 2 WARN, 1 FAIL → journal entry
6. **Batch 3:** Launch 2 sub-agents → 2 PASS → journal entry
7. **Synthesis:** Write journal synthesis
8. **Results:** Create `docs/wip/AUDIT-RESULTS-2025-12-24-1430.md`
9. **Report:**
   ```
   Audit complete.

   Results: 17 PASS, 3 WARN, 2 FAIL

   Files:
   - Journal: docs/wip/JOURNAL-audit-2025-12-24-1430.md
   - Results: docs/wip/AUDIT-RESULTS-2025-12-24-1430.md

   2 outcomes need immediate fixes (FAIL).
   3 outcomes should be reviewed (WARN).
   ```

---

## Sub-Agent Instructions Reference

- **Outcomes:** `agents/taskAuditOutcome.md`
- **Specifications:** `agents/taskAuditSpec.md`

Both follow the same output format, making result aggregation straightforward.

---

## Version History

- **1.0.0** (2025-12-24): Initial version
