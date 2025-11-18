# Working Documents and Intent Lifecycle

**Date:** 2025-11-15
**Status:** Proposal
**Context:** JIG v5.0 introduces Intent Graph (OSTC) as canonical truth. This proposal explores the relationship between timeless Intent artifacts and temporal working documents.

---

## Executive Summary

**The Core Insight:**
Intent (OSTC) is **positional** - it describes where we are now.
Working docs are **vectorial** - they describe how we got here and where we're going.

Intent captures **state**. Working docs capture **change**.

This proposal:
1. Names working documents as **Deltas** (Δ-docs)
2. Identifies their unique value as **change narratives** and **decision context**
3. Proposes **git-branch lifecycle binding** as their natural retention policy
4. Introduces **Delta harvesting** - extracting insights into Intent before disposal

---

## 1. Nomenclature: What Are These Documents?

### 1.1 Proposed Name: **Deltas** (Δ-docs)

**Delta** captures their essential nature:
- Δ (delta) = change, difference, transformation
- Time-bounded: exist from work start → completion
- Branch-scoped: tied to specific development efforts
- Directional: capture the journey from A→B

**Categories of Deltas observed in ASE:**

| Type | Purpose | Lifespan | Examples |
|------|---------|----------|----------|
| **Δ-Plan** | Execution roadmap with work units | Branch duration | `PLAN_Operations_Future_State_Implementation.md` |
| **Δ-Scope** | Boundary definition for work | Pre-work → start | `SCOPE_BikeEchoform_Relay.md` |
| **Δ-Proposal** | Design options and decisions | Pre-work → ADR | `PROPOSAL_Operations_Future_State.md` |
| **Δ-Analysis** | Problem investigation | Incident → resolution | `ANALYSIS_CRDT_Relay_Issues_Nexus.md` |
| **Δ-Audit** | Code assessment before refactor | Pre-refactor | `AUDIT_Layer_4_Operations.md` |
| **Δ-Issue** | Bug report and fix tracking | Bug → fix | `ISSUE_WU6_STATE_QUERY_Regression.md` |
| **Δ-WU-Complete** | Work unit completion report | Work unit end | `WU21_1_COMPLETION_SUMMARY.md` |
| **Δ-Retrospective** | Branch/feature reflection | Branch merge | `RETROSPECTIVE_multiprocess_websocket_branch.md` |
| **Δ-Evaluation** | Assessment and measurement | Analysis phase | `EVALUATION_test_suite_performance_analysis.md` |
| **Δ-Migration** | Migration guides and records | Migration period | `MIGRATION_GUIDE.md` |

### 1.2 Why Not Call Them "Working Docs"?

"Working" implies they're drafts or temporary. But Deltas are **intentionally ephemeral** - they *should* disappear. Their value is in:
1. **Guiding change** during development
2. **Providing context** during review
3. **Seeding Intent** when insights emerge
4. **Creating history** for future archaeology

---

## 2. Unique Value of Deltas vs. Intent

### 2.1 What Deltas Contain That Intent Doesn't

| Aspect | Intent (OSTC) | Deltas (Δ-docs) |
|--------|---------------|-----------------|
| **Time orientation** | Present state | Past→Future trajectory |
| **Scope** | What/Why/How/That | The journey of change |
| **Uncertainty** | Resolved truth | Options, experiments, dead ends |
| **Context** | Timeless design | Temporal constraints, urgency |
| **Decisions** | Final choices | Decision process, alternatives considered |
| **Learning** | What we know | How we learned it |
| **Failures** | Success state | What didn't work, why |
| **Emotions** | Neutral | Frustration, breakthroughs, surprises |

**Example from ASE:**

**Intent (Outcome O-MP-001):**
```yaml
id: O-MP-001
title: ASE scales to 30+ devices with <30ms GUI response
status: achieved
```

**Delta (PLAN_multiprocess_websocket_architecture.md):**
```markdown
## What We Tried
1. Threading (failed - GIL bottleneck)
2. Async within single process (failed - still serialized)
3. Multi-process with shared memory (failed - GUI threading violations)
4. Multi-process with WebSocket (SUCCESS - this document)

## Why It Matters NOW
- Demo to execs in 5 days
- 14 devices = spinning beachball = embarrassment
- iOS app integration blocked on same architecture

## Risks We're Taking
- Never done WebSocket in production
- Process management complexity
- Graceful shutdown is hard
```

**The Delta tells the story Intent cannot.**

### 2.2 The Three Types of Delta Value

#### Type 1: **Execution Scaffolding**
- Checklists, work units, dependencies
- "What's done? What's next?"
- **Lifespan:** Active work period only
- **Disposition:** Discard after merge

#### Type 2: **Decision Context**
- Why we chose A over B
- What constraints existed at the time
- What we didn't know then
- **Lifespan:** Useful during reviews, retrospectives
- **Disposition:** Harvest key decisions → Intent, then discard

#### Type 3: **Discovery Artifacts**
- Emergent requirements (VIB)
- Implicit constraints surfaced (OSTC)
- Lessons learned
- **Lifespan:** Indefinite value
- **Disposition:** **MUST HARVEST** into Intent before disposal

---

## 3. The Lifecycle: Deltas and Git Branches

### 3.1 Observation: Deltas Are Branch-Scoped

From ASE git history analysis:

```
Branch: bike-echoform-relay
├─ Created: 2025-11-09
├─ Deltas in docs/wip/bike-state-crdt/*
│  ├─ PLAN_BikeEchoform_Relay.md
│  ├─ SCOPE_BikeEchoform_Relay.md
│  ├─ PROPOSAL_netspace_echoform_relay_sync.md
│  └─ CONCEPT_gateway_relay.md
├─ Branch lifecycle: 37 commits over 5 days
├─ Deltas updated: 47 commits to these docs
├─ Branch merged: 2025-11-14
└─ Deltas moved: docs/wip/* → docs/done/bike-echoform-relay/*
```

**Pattern:** Deltas are *born* when work starts, *active* during development, *archived* when branch closes.

**This is not coincidence - this is the natural lifecycle.**

### 3.2 Proposed: Delta Lifecycle = Git Workflow

```
┌─────────────────────────────────────────────────────────┐
│                   DELTA LIFECYCLE                        │
└─────────────────────────────────────────────────────────┘

Phase 1: CONCEPTION (pre-branch)
├─ Location: docs/wip/
├─ Documents: Δ-Proposal, Δ-Scope, Δ-Analysis
├─ Status: Exploring, deciding
└─ Git: main branch, no feature branch yet

Phase 2: EXECUTION (active branch)
├─ Branch created: feature/bike-echoform-relay
├─ Location: docs/wip/bike-echoform-relay/*
├─ Documents: Δ-Plan, Δ-Audit, Δ-Issue, Δ-WU-Complete
├─ Status: Active development
├─ Pattern: Frequent commits to both code and Deltas
└─ Git: Feature branch, many commits

Phase 3: COMPLETION (merge preparation)
├─ Location: Still docs/wip/bike-echoform-relay/*
├─ Documents: Δ-Retrospective created
├─ Action: **DELTA HARVEST** (see §4)
│  ├─ Extract discoveries → VIB_DISCOVERIES.md
│  ├─ Extract requirements → OSTC_DISCOVERIES.md
│  ├─ Promote decisions → docs/architecture/ADR-*.md
│  └─ Update Intent Graph (OSTC)
└─ Git: Branch ready to merge

Phase 4: ARCHIVE (post-merge)
├─ Branch merged to main
├─ Action: Move docs/wip/X/* → docs/done/X/*
├─ Documents: Frozen, read-only
├─ Git tags: (optional) tag the merge commit
└─ Retention: See §5

Phase 5: DECAY (long-term)
├─ Location: docs/done/X/* (unchanged)
├─ Access pattern: Rare reference, git archaeology
├─ Value diminishes as context fades
└─ Eventually: Compress, archive, or delete
```

### 3.3 Why This Binding Works

**Deltas answer questions about a *specific change effort*:**
- Why did we refactor the protocol stack?
- What problems existed before multiprocess architecture?
- Why did we choose WebSocket over gRPC?
- What broke during the migration?
- How long did it take?

**Git branches represent *the same change effort*:**
- Scope: Branch = one logical feature/fix
- Duration: Branch = finite work period
- Merge = work completion
- History = execution record

**Deltas are the *narrative* of what git commits *record*.**

---

## 4. Delta Harvesting: Extracting Insight to Intent

### 4.1 The Problem: Deltas Contain Latent Intent

During development, we discover:
- **Implicit requirements** (VIB: "user input must win over periodic updates")
- **Hidden constraints** (OSTC: "ELC ownership must be clear")
- **Design decisions** (ADR: "only hubs broadcast operations")
- **Test gaps** (OSTC: "no integration test for gateway initialization")

**These are Intent artifacts stuck in Delta documents.**

If we discard Deltas without extraction, **we lose this knowledge.**

### 4.2 Proposed: Systematic Delta Harvest

**Before archiving a Delta set (moving wip→done), run harvest process:**

#### Step 1: Scan for Discoveries
```bash
# Look for discovery markers in Deltas
grep -r "#VIB:" docs/wip/current-branch/
grep -r "#OSTC:" docs/wip/current-branch/
grep -r "Discovery:" docs/wip/current-branch/
grep -r "Learning:" docs/wip/current-branch/
```

#### Step 2: Extract to Continuous Logs
```bash
# Add to running discovery logs
cat discoveries_from_deltas >> docs/VIB_DISCOVERIES.md
cat ostc_insights >> docs/OSTC_DISCOVERIES.md
```

#### Step 3: Promote Architectural Decisions
```bash
# Significant decisions → ADRs
mv decision_rationale docs/architecture/ADR-027-hub-only-broadcast.md
```

#### Step 4: Update Intent Graph
```bash
# Add new Outcomes, Specs, Tests discovered
jigy extract --source docs/wip/current-branch/
jigy align --check
```

#### Step 5: Verify Harvest Complete
```bash
# Checklist before archiving
- [ ] All VIB/OSTC discoveries extracted?
- [ ] Architectural decisions captured in ADRs?
- [ ] New requirements added to Intent Graph?
- [ ] Retrospective written?
- [ ] Code fully annotated with @jig tags?
```

### 4.3 Harvest Automation

**Future tooling (jigy harvest):**

```bash
# Automated Delta harvest
jigy harvest --branch bike-echoform-relay --output .jig/harvest-report.md

# What it does:
# 1. Scans all Deltas in docs/wip/bike-echoform-relay/
# 2. Identifies VIB/OSTC markers
# 3. Extracts decision rationales
# 4. Generates harvest report for human review
# 5. Suggests Intent Graph updates
# 6. Creates archive checklist
```

---

## 5. Retention Policy: When to Delete Deltas

### 5.1 Retention Tiers

| Tier | Retention | Criteria | Location |
|------|-----------|----------|----------|
| **Ephemeral** | Delete on merge | Pure scaffolding, no insights | None (deleted) |
| **Short-term** | 6 months post-merge | Reference during stabilization | `docs/done/recent/` |
| **Long-term** | 2 years post-merge | Major features, complex changes | `docs/done/archive/` |
| **Permanent** | Forever | System-defining work | `docs/done/historical/` |

### 5.2 Classification Heuristics

**Ephemeral (delete immediately):**
- Δ-WU-Complete (work unit completion notes) - *value captured in git*
- Δ-Scope (if scope fully realized) - *value captured in code*
- Δ-Issue (if bug fixed and tests added) - *value captured in tests*

**Short-term (6 months):**
- Δ-Plan (normal feature work)
- Δ-Analysis (routine debugging)
- Δ-Audit (refactoring assessments)

**Long-term (2 years):**
- Δ-Retrospective (major branches)
- Δ-Migration (architecture changes)
- Δ-Proposal (significant design decisions)

**Permanent (forever):**
- First implementation of core systems
- System-defining pivots (e.g., multiprocess-websocket)
- Failure post-mortems with critical learnings
- Compliance/legal documentation

### 5.3 Compression Strategy

**After harvest, before deletion:**

```bash
# Compress Delta set into single archive file
jigy compress --branch bike-echoform-relay \
  --input docs/done/bike-echoform-relay/ \
  --output docs/done/archive/bike-echoform-relay-2025-11.tar.gz

# What's retained:
# - Full text of all Deltas
# - Git commit SHAs referencing them
# - Branch metadata
# - Harvest report
# - File size: ~100KB compressed vs 2MB raw
```

---

## 6. The Git History Connection

### 6.1 Deltas as Git's Missing Narrative

**Git captures:**
- What changed (diffs)
- When (timestamps)
- Who (authors)
- Where (file paths)

**Git doesn't capture:**
- **Why** this approach vs alternatives
- **What** we tried that failed
- **How** we decided
- **What** we learned

**Deltas fill this gap.**

### 6.2 Proposed: Git-Delta Linking

#### Link 1: Branch → Delta Directory
```bash
# Branch naming convention
git checkout -b bike-echoform-relay

# Creates corresponding Delta directory
mkdir docs/wip/bike-echoform-relay/
```

#### Link 2: Commits Reference Deltas
```bash
# Commit messages link to Deltas
git commit -m "WU7.3: Fix device operation tests

See: docs/wip/PLAN_Operations_Future_State_Implementation.md#WU7.3
Implements: S-PS-004 (Message structure)
Tests: test_device_operations.py::test_button_press
"
```

#### Link 3: Delta Front Matter References Git
```yaml
---
branch: bike-echoform-relay
base_commit: 6abdec3
merge_commit: a37d344
commits: 37
files_changed: 23
---
```

#### Link 4: Merge Commits Summarize Deltas
```bash
# Merge commit message = Retrospective summary
git merge bike-echoform-relay -m "$(cat docs/done/bike-echoform-relay/RETROSPECTIVE.md | head -50)"
```

### 6.3 Git Archaeology + Delta Archives

**Future developer (6 months later):**

```bash
# Question: Why did we switch to WebSocket architecture?

# Git archaeology
git log --grep="multiprocess" --oneline
# → 155 commits, not very helpful

# Better: Find the Delta
ls docs/done/multiprocess-websocket/
# → RETROSPECTIVE_multiprocess_websocket_branch.md

# Read the story
cat docs/done/multiprocess-websocket/RETROSPECTIVE_multiprocess_websocket_branch.md
# → Full context: problem, attempts, decision, results
```

**Delta archives are *indexed git history*.**

---

## 7. Integration with JIG System

### 7.1 Deltas → Intent Flow

```
┌─────────────┐
│   Deltas    │  Temporal, narrative, exploratory
│  (Δ-docs)   │  "How we changed the system"
└──────┬──────┘
       │ Delta Harvest
       ↓
┌─────────────┐
│ Discoveries │  Insights extracted from work
│  VIB/OSTC   │  "What we learned"
└──────┬──────┘
       │ Intent Graph Update
       ↓
┌─────────────┐
│   Intent    │  Timeless, canonical, current
│   (OSTC)    │  "What the system is/should be"
└─────────────┘
```

### 7.2 JIG Tool Support for Deltas

#### Command: `jigy delta new`
```bash
# Start new work
jigy delta new --type plan --branch bike-echoform-relay

# Creates:
# - docs/wip/bike-echoform-relay/PLAN_BikeEchoform_Relay.md (from template)
# - Front matter with git metadata
# - Work unit checklist
```

#### Command: `jigy delta harvest`
```bash
# Before archiving branch
jigy delta harvest --branch bike-echoform-relay

# Runs:
# 1. Extract VIB/OSTC discoveries
# 2. Check for unharvested decisions
# 3. Verify Intent Graph updated
# 4. Generate harvest report
```

#### Command: `jigy delta archive`
```bash
# After merge
jigy delta archive --branch bike-echoform-relay --retention long-term

# Moves:
# - docs/wip/bike-echoform-relay/* → docs/done/bike-echoform-relay/*
# - Updates .jig/delta-index.yaml
# - Schedules cleanup based on retention tier
```

#### Command: `jigy delta search`
```bash
# Find past work
jigy delta search "why did we choose WebSocket"

# Searches:
# - docs/done/**/RETROSPECTIVE*.md
# - docs/done/**/PROPOSAL*.md
# - Ranked by relevance, with git context
```

---

## 8. Practical Recommendations for ASE

### 8.1 Immediate Actions (Now)

1. **Rename docs/wip/ → docs/deltas/active/**
   - Signals different purpose from Intent
   - Emphasizes temporal nature

2. **Create docs/deltas/archive/**
   - Move current docs/done/* → docs/deltas/archive/*
   - Organize by branch/theme

3. **Template Deltas**
   - Create templates for Δ-Plan, Δ-Retrospective, etc.
   - Include harvest checklist

4. **Document Current Practice**
   - Write Delta authoring guidelines
   - Define harvest process
   - Set retention defaults

### 8.2 Short-term Actions (Next 2 weeks)

1. **Harvest Current WIP**
   - Review docs/wip/ for unharvested insights
   - Extract to VIB/OSTC discoveries
   - Archive completed work

2. **Git Branch Alignment**
   - Review active branches
   - Ensure each has Delta directory
   - Link via commit messages

3. **Retention Triage**
   - Review docs/done/*
   - Classify by retention tier
   - Compress/delete ephemeral Deltas

### 8.3 Long-term Vision (Next 6 months)

1. **Delta Tooling**
   - Implement `jigy delta` commands
   - Automate harvest process
   - Build Delta search

2. **Integration with JIG Graph**
   - Deltas reference OSTC nodes
   - OSTC nodes link back to originating Deltas
   - Traceability: Intent ↔ Change narrative

3. **Metrics**
   - Track harvest completion rate
   - Measure Delta→Intent conversion
   - Identify high-value Delta types

---

## 9. Open Questions

### 9.1 Questions for Jim

1. **Delta Naming:** Do you like "Deltas" or prefer another term?
   - Alternatives: Changelogs, Traces, Journals, Narratives

2. **Retention Defaults:** What feels right for ASE?
   - Keep everything forever (pack rat)?
   - Aggressive pruning after 6 months?
   - Somewhere in between?

3. **Harvest Frequency:** When should harvest happen?
   - Every work unit?
   - End of each branch?
   - Manual/on-demand only?

4. **Current docs/done/:** What to do with 200+ existing documents?
   - Triage now (high effort)?
   - Leave as-is, apply policy to new work only?
   - Batch compress everything older than 6 months?

### 9.2 Research Questions

1. **Version Control for Deltas?**
   - Deltas are in git, but should they be?
   - Alternative: External system (Notion, Linear, etc.)?
   - Hybrid: Keep in git until archive, then export?

2. **Delta Visualization?**
   - Timeline view of all Deltas?
   - Branch/Delta relationship graph?
   - Heatmap of harvest density?

3. **LLM-Assisted Harvest?**
   - Can Claude scan Deltas and suggest OSTC extractions?
   - Train model on VIB/OSTC patterns?
   - Automated discovery extraction?

---

## 10. Conclusion: The Value Proposition

### 10.1 What We Gain

**From recognizing Deltas as distinct from Intent:**
- Clarity of purpose (change vs state)
- Appropriate retention (branch-scoped vs permanent)
- Harvest discipline (don't lose insights)
- Archaeological value (understand past decisions)

**From git-branch lifecycle binding:**
- Natural organization (branch = work = Deltas)
- Automatic scope (branch boundaries = Delta boundaries)
- Merge triggers harvest (process checkpoint)
- History alignment (narrative + diffs = complete story)

**From systematic harvest:**
- Insights captured before disposal
- Intent Graph stays current
- Decision context preserved
- Lessons learned not lost

### 10.2 The Philosophy

**Intent is timeless. Deltas are temporal.**

Intent describes the world as it is (or should be).
Deltas describe how we changed that world.

Both are essential:
- Intent enables **alignment** (are we building the right thing?)
- Deltas enable **learning** (how did we get here? what worked?)

JIG maintains Intent.
Deltas maintain **wisdom**.

### 10.3 The Proposal in One Sentence

**Bind Delta documents to git branch lifecycles, harvest insights to Intent before archiving, and retain based on narrative value rather than execution scaffolding.**

---

**Next Steps:**
1. Jim reviews and provides feedback on nomenclature and approach
2. Refine based on ASE-specific needs
3. Create Delta templates and harvest checklist
4. Implement `jigy delta` tooling
5. Migrate current docs/wip → docs/deltas structure

---

**Document Status:** Proposal (awaiting review)
**Estimated Reading Time:** 18 minutes
**Key Insight:** Deltas are vectorial (change), Intent is positional (state)
