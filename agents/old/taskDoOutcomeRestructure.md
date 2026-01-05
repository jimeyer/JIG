# Task: Orchestrate Outcome Restructuring

**Version:** 1.0.0
**Audience:** Orchestration agent (Opus)
**Purpose:** Coordinate parallel restructuring of JIG outcomes to B025 format

---

## Overview

You orchestrate the restructuring of JIG outcome documents from legacy format to B025 compliance. You launch sub-agents in batches, collect results, maintain a progress journal, and verify quality.

**Philosophy:**
- Preserve existing content/intent while restructuring
- Parallel batches for efficiency (but smaller batches than audit - restructuring is heavier)
- Quality verification after each batch
- Human review checkpoint after first batch

---

## Input

You receive:
- `restructure outcomes` - Restructure all outcomes in `jig/outcomes/`
- `restructure outcomes O-001 O-005 O-012` - Restructure specific outcomes

---

## Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                         SETUP                                    │
│   1. Read B025 format spec for reference                        │
│   2. Read an exemplary outcome (if any exist)                   │
│   3. List outcomes to restructure                               │
│   4. Create JOURNAL file                                        │
│   5. Plan batches (5 files per batch - restructuring is heavy)  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PILOT BATCH (Batch 1)                        │
│   1. Launch 5 sub-agents in parallel                            │
│   2. Wait for completion                                        │
│   3. Verify outputs (read restructured files)                   │
│   4. Write journal entry                                        │
│   5. STOP - Ask user to review pilot batch before continuing    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BATCH EXECUTION (2-N)                        │
│   For each remaining batch:                                     │
│   1. Launch 5 sub-agents in parallel                            │
│   2. Wait for completion                                        │
│   3. Spot-check 1-2 outputs                                     │
│   4. Write journal entry                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       COMPLETION                                 │
│   1. Write final journal synthesis                              │
│   2. Run jigy validate (if available)                           │
│   3. Report summary to user                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Setup

### 1.1 Reference Materials

Read these files to understand the target format:
- `docs/jig/B025_Outcome-Format-Specification.md` (if exists)
- `docs/jig/taskRestructureOutcome.md` (sub-agent instructions)

### 1.2 List Outcomes

```bash
ls jig/outcomes/O-*.md
```

### 1.3 Create Journal

Create `docs/audits/JOURNAL-restructure-<date>.md`:

```markdown
# Outcome Restructuring Journal

**Started:** YYYY-MM-DD
**Total Outcomes:** N
**Batches Planned:** M (5 per batch)

---

## Progress

(Entries added during execution)

---

## Quality Notes

(Observations about restructuring quality)
```

---

## Phase 2: Pilot Batch

### 2.1 Launch First Batch

Launch **5 sub-agents in parallel** using:

```markdown
You are restructuring a JIG outcome to B025 format.

Follow the instructions in docs/jig/taskRestructureOutcome.md.

File to restructure: jig/outcomes/O-XXX.md

Read the file, restructure it to B025 format, and write it back.
Return a summary of changes made.
```

**Important:** Use `model: "sonnet"` for sub-agents - restructuring requires stronger reasoning than audit.

### 2.2 Verify Pilot Batch

After sub-agents complete:
1. Read each restructured file
2. Verify B025 sections are present
3. Verify content was preserved (not lost)
4. Check for any obvious issues

### 2.3 Human Checkpoint

**STOP and ask user:**

```markdown
Pilot batch complete. I've restructured 5 outcomes:
- O-001: [summary]
- O-002: [summary]
- ...

Please review these files and let me know:
1. Are the restructured outcomes acceptable?
2. Should I adjust the approach?
3. Should I continue with remaining batches?
```

---

## Phase 3: Remaining Batches

After user approval, continue with batches of 5.

### Journal Entry Format

```markdown
### Batch N/M Complete

**Files:** O-XXX, O-YYY, O-ZZZ, O-AAA, O-BBB
**Status:** All restructured

**Spot Check:** O-XXX
- B025 sections: ✓ all present
- Content preserved: ✓
- Quality: Good

**Running Total:** XX/YY outcomes restructured
```

---

## Phase 4: Completion

### 4.1 Final Verification

```bash
# Check all outcomes have required sections
for f in jig/outcomes/O-*.md; do
  grep -q "## Why This Matters" "$f" || echo "Missing: $f"
done
```

### 4.2 Report

```markdown
Restructuring complete.

**Results:**
- Restructured: 43/43 outcomes
- All now have B025 sections

**Files:**
- Journal: docs/audits/JOURNAL-restructure-YYYY-MM-DD.md

**Recommended next steps:**
1. Review a sample of restructured outcomes
2. Run full audit to verify compliance
3. Commit changes
```

---

## Constraints

### DO
- Launch sub-agents with `model: "sonnet"` (stronger than haiku)
- Use smaller batches (5 files) than audit (restructuring is heavier)
- Stop after pilot batch for human review
- Spot-check outputs after each batch
- Preserve original content/intent

### DO NOT
- Use haiku for restructuring (too lightweight)
- Launch more than 5 sub-agents at once
- Continue past pilot batch without user approval
- Delete or lose existing content

---

## Error Handling

**If sub-agent reports it cannot restructure:**
1. Log in journal
2. Mark file as SKIP
3. Continue with batch
4. Report skipped files to user

**If file appears corrupted after restructure:**
1. STOP immediately
2. Report to user
3. User can `git checkout` to restore

---

## Sub-Agent Instructions

Sub-agents follow: `docs/jig/taskRestructureOutcome.md`
