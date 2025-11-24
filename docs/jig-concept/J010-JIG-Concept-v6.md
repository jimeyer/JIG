# JIG: Jig Intent Graph v6.0

**Jig Intent Graph: Alignment-Based Development with Temporal Deltas**
**Date:** 2025-11-16
**Status:** Architecture Proposal

> **v6 Key Innovation:** JIG distinguishes between timeless Intent (OSTC) and temporal Deltas, with systematic harvest/distill pipelines that extract wisdom from work narratives. Designed with git's philosophy: simple, fast, composable, text-based.

---

## Executive Summary

JIG (Jig Intent Graph) represents software development as a **constraint-satisfaction and alignment problem** with two distinct but complementary knowledge systems:

**The name "JIG" embodies the system's philosophy:**
- **Jig** (noun): A template or guide that ensures components align correctly during construction
- **Intent Graph**: The explicit network of relationships between why we build (Outcomes), what we build (Specifications), how we verify (Tests), and how we implement (Code)

### The Two Knowledge Systems

**1. Intent (OSTC) - Positional Truth**
- Describes **where we are now**
- Timeless, canonical, maintained
- Lives in `jig/` as structured nodes
- Captures **state**: "What the system is/should be"

**2. Deltas - Vectorial Narratives**
- Describes **how we got here and where we're going**
- Temporal, branch-scoped, disposable
- Lives in `jig/deltas/` during work
- Captures **change**: "The journey from A→B"

### The Development Flow

Instead of "writing code," development becomes:

1. **Expressing intent** in structured documentation (Outcomes and Specifications)
2. **Narrating work** in branch-scoped Deltas (Plans, Analyses, Retrospectives)
3. **Annotating reality** with lightweight decorators in tests and code
4. **Detecting misalignment** when changes create inconsistencies
5. **Monitoring decomposability** to preserve architectural boundaries
6. **Harvesting insights** from Deltas into Intent before disposal
7. **Restoring equilibrium** through AI-assisted repair operations

> "JIG doesn't build software forward or reverse—it maintains alignment between timeless Intent and temporal work while preserving natural architectural boundaries."

### The Git Philosophy

JIG design follows Linus Torvalds' principles:
- **Simple text formats** - YAML frontmatter + Markdown, grep-able
- **Fast operations** - Deterministic tools run in <1 second
- **Composable commands** - `jigy extract | jigy synthesize | jigy integrate`
- **Local-first** - No servers, no network dependencies
- **Explicit over magic** - Developers control everything
- **Trust users** - Provide tools, not guardrails
- **Content-addressable** - Everything versioned in git

---

## 1. Core Philosophy: Two Types of Truth

### 1.1 Intent: Positional Truth (State)

**Intent is timeless canonical knowledge about the system.**

| Element | Type of Truth | Purpose | Location |
|---------|---------------|---------|----------|
| **Outcome (O)** | Narrative truth | Why we build | `jig/outcomes/` |
| **Specification (S)** | Logical truth | What we build | `jig/specifications/` |
| **Test (T)** | Empirical truth | How we verify | `jig/tests/` |
| **Code (C)** | Operational truth | How we implement | Source files (annotated) |

**Properties of Intent:**
- **Persistent** - Maintained for life of system
- **Canonical** - Single source of truth
- **Measurable** - Can validate alignment
- **Subsystem-scoped** - Respects decomposability boundaries
- **Git-tracked** - Full version history

**Example Intent Node:**
```yaml
---
id: S-CRDT-042
type: specification
title: "CRDT operations validate input types"
subsystem: crdt
---

All CRDT operation handlers MUST validate input types before processing.
OR-Set elements MUST be hashable (str, int, tuple).
Lists MUST be expanded to individual add operations.

## Rationale
Lists are unhashable and cause runtime crashes when added to sets.

## References
- Implements: O-CRDT-005 (Multi-actor CRDT consistency)
- Tested by: T-CRDT-089
- Code: `bike_echoform_replicator.py:342`
```

### 1.2 Deltas: Vectorial Truth (Change)

**Deltas are temporal narratives about specific change efforts.**

| Delta Type | Purpose | Lifespan | Example |
|------------|---------|----------|---------|
| **Delta-Plan** | Execution roadmap | Branch duration | `PLAN_Operations_Future_State.md` |
| **Delta-Scope** | Work boundaries | Pre-work → start | `SCOPE_BikeEchoform_Relay.md` |
| **Delta-Proposal** | Design options | Pre-work → decision | `PROPOSAL_Multiprocess_Architecture.md` |
| **Delta-Analysis** | Problem investigation | Incident → resolution | `ANALYSIS_CRDT_Relay_Issues.md` |
| **Delta-Retrospective** | Branch reflection | Branch merge | `RETROSPECTIVE_multiprocess_branch.md` |
| **Delta-Issue** | Bug tracking | Bug → fix | `ISSUE_Shutdown_Timeout.md` |

**Properties of Deltas:**
- **Ephemeral** - Deleted after harvest (or archived)
- **Branch-scoped** - Tied to specific git branch
- **Narrative** - Tell the story code can't
- **Messy** - Capture uncertainty, dead ends, emotions
- **Harvestable** - Contain latent Intent to extract

**Example Delta:**
```markdown
---
branch: bike-echoform-relay
base_commit: 6abdec3
merge_commit: a37d344
harvest_status: pending
---

# PLAN: Bike Echoform Relay Implementation

## What We Tried
1. Threading (failed - GIL bottleneck)
2. AsyncIO single process (failed - still serialized)
3. Multi-process + shared memory (failed - GUI thread safety)
4. Multi-process + WebSocket (SUCCESS)

#DECISION:001 "WebSocket vs gRPC for device communication"
**Choice:** WebSocket
**Rationale:** Simpler deployment, no protobuf compilation
**Tradeoffs:** Process management complexity vs simplicity

#DISCOVERY:042 "OR-Set crashes when receiving list values"
**Where:** bike_echoform_replicator.py:342
**Why:** Lists are unhashable, can't be set elements
**Fix:** Expand list to N add operations
#OSTC:Spec "CRDT operations must validate input types"

#LEARNED:007 "Shutdown timeout needs 2x cleanup time"
**Pattern:** timeout = N × max_cleanup_time + margin
```

### 1.3 What Deltas Contain That Intent Doesn't

| Aspect | Intent (OSTC) | Deltas |
|--------|---------------|--------|
| **Time orientation** | Present state | Past→Future trajectory |
| **Uncertainty** | Resolved truth | Options, experiments, dead ends |
| **Context** | Timeless design | Temporal constraints, urgency |
| **Decisions** | Final choices | Decision process, alternatives |
| **Failures** | Success state | What didn't work, why |
| **Emotions** | Neutral | Frustration, breakthroughs |

**Deltas tell the story Intent cannot.**

---

## 2. Nearly Decomposable Systems

From Herbert Simon's insight: well-designed software exhibits **sparse inter-module connections** with **dense intra-module connections**.

### 2.1 Subsystem Properties

JIG makes architectural boundaries visible and measurable:

```
┌─────────────────────────────────────────────────────┐
│         Jig Intent Graph (JIG) v6                   │
│                                                      │
│  ┌─────────────────┐     ┌─────────────────┐       │
│  │   Subsystem A   │     │   Subsystem B   │       │
│  │  ┌───┐ ┌───┐   │     │  ┌───┐ ┌───┐   │       │
│  │  │ O │→│ S │   │     │  │ O │→│ S │   │       │
│  │  └───┘ └───┘   │     │  └───┘ └───┘   │       │
│  │    ↓     ↓     │ ←─→ │    ↓     ↓     │       │
│  │  ┌───┐ ┌───┐   │     │  ┌───┐ ┌───┐   │       │
│  │  │ T │→│ C │   │     │  │ T │→│ C │   │       │
│  │  └───┘ └───┘   │     │  └───┘ └───┘   │       │
│  └─────────────────┘     └─────────────────┘       │
│   Dense Internal          Sparse External           │
│   Connections             Interface                 │
│                                                      │
│  Metrics: Modularity=0.87, Coupling=12:1           │
└─────────────────────────────────────────────────────┘
```

**Key Metrics:**

```python
# Coupling Ratio (should be > 10:1)
coupling_ratio = internal_edges / external_edges

# Modularity Score (Newman, should be > 0.3)
modularity = sum(e_ii - a_i^2 for all communities)

# Depth Score (LOC per export, should be > 100:1)
depth_score = lines_of_code / number_of_exports
```

**Subsystem Annotation:**
```python
# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:auth
class AuthenticationService:
    """Core authentication logic"""

# @jig C-USER-001 implements:S-USER-001 subsystem:user depends:auth
class UserManager:
    """User management depends on auth subsystem"""
```

---

## 3. Delta Lifecycle: Bound to Git Branches

### 3.1 The Natural Binding

**Observation:** Deltas are born when work starts, active during development, archived when branch closes.

This is not coincidence—**this is the natural lifecycle**.

```
┌─────────────────────────────────────────────────────────┐
│                   DELTA LIFECYCLE                        │
└─────────────────────────────────────────────────────────┘

Phase 1: CONCEPTION (pre-branch)
├─ Location: jig/deltas/active/
├─ Documents: Delta-Proposal, Delta-Scope, Delta-Analysis
├─ Status: Exploring, deciding
└─ Git: main branch, no feature branch yet

Phase 2: EXECUTION (active branch)
├─ Branch created: feature/bike-echoform-relay
├─ Location: jig/deltas/active/bike-echoform-relay/
├─ Documents: Delta-Plan, Delta-Analysis, Delta-Issue
├─ Status: Active development
├─ Pattern: Frequent commits to both code and Deltas
└─ Git: Feature branch, many commits

Phase 3: HARVEST (merge preparation)
├─ Location: Still jig/deltas/active/bike-echoform-relay/
├─ Documents: Delta-Retrospective created
├─ Action: **HARVEST & DISTILL**
│  ├─ Extract discoveries → HarvestReport
│  ├─ LLM synthesize → SynthesisProposal
│  ├─ Human review → approve/reject
│  └─ Integrate → Update Intent Graph
└─ Git: Branch ready to merge

Phase 4: ARCHIVE (post-merge)
├─ Branch merged to main
├─ Action: Move jig/deltas/active/X/ → jig/deltas/archive/X/
├─ Documents: Frozen, read-only
├─ Retention: See retention tiers
└─ Git: Merge commit tagged with harvest metadata

Phase 5: DECAY (long-term)
├─ Location: jig/deltas/archive/X/ (unchanged)
├─ Access: Rare reference, git archaeology
├─ Value: Diminishes as context fades
└─ Eventually: Compress or delete per retention tier
```

### 3.2 Git-Branch Binding Commands

```bash
# Start new work (creates Delta directory)
git checkout -b bike-echoform-relay
jigy delta new --type plan

# Commit with Delta reference
git commit -m "WU7.3: Fix device tests

See: jig/deltas/active/PLAN_Operations.md#WU7.3
Implements: S-PS-004
Tests: test_device_operations.py::test_button_press"

# Before merge: harvest
jig ai-distill --branch bike-echoform-relay

# After merge: archive
git merge bike-echoform-relay
jig delta archive --branch bike-echoform-relay --retention long-term
```

### 3.3 Retention Tiers

| Tier | Retention | Criteria | Action |
|------|-----------|----------|--------|
| **Ephemeral** | Delete on merge | Pure scaffolding | Delete |
| **Short-term** | 6 months | Reference during stabilization | Archive |
| **Long-term** | 2 years | Major features | Archive compressed |
| **Permanent** | Forever | System-defining work | Keep forever |

---

## 4. Harvest & Distill: Extract Intent from Deltas

### 4.1 The Three-Phase Pipeline

```
┌─────────────────────────────────────────────────────────┐
│              DELTA HARVEST & DISTILLATION               │
└─────────────────────────────────────────────────────────┘

Phase 1: EXTRACT (deterministic, fast, reliable)
┌──────────────────────────────────────────┐
│ Input: Deltas (markdown files)           │
│ Process: Pattern matching, parsing       │
│ Output: HarvestReport (YAML)             │
│ Duration: <1 second                      │
│ Tool: grep + regex + YAML parser         │
└──────────────────────────────────────────┘
              ↓
Phase 2: SYNTHESIZE (LLM-assisted, slow, creative)
┌──────────────────────────────────────────┐
│ Input: HarvestReport + Intent Graph      │
│ Process: Understand, categorize, propose │
│ Output: SynthesisProposal (YAML)         │
│ Duration: 30-60 seconds                  │
│ Tool: Claude Sonnet 4.5                  │
└──────────────────────────────────────────┘
              ↓
Phase 3: INTEGRATE (human-approved, deterministic)
┌──────────────────────────────────────────┐
│ Input: Approved SynthesisProposal        │
│ Process: Update OSTC files, add links    │
│ Output: Updated Intent Graph             │
│ Duration: <1 second                      │
│ Tool: File I/O + YAML updates            │
└──────────────────────────────────────────┘
```

### 4.2 Division of Labor

**Deterministic Code (Fast, Reliable):**
- Extract markers from Deltas (regex)
- Validate syntax
- Build reference graphs
- Update Intent Graph files
- Generate changelogs

**LLM (Smart, Creative):**
- Understand narrative context
- Categorize by semantic meaning
- Detect patterns
- Identify conflicts
- Elevate abstraction level
- Draft formal specifications

**Human (Wise, Scarce):**
- Decide what's Intent-worthy
- Set business priority
- Resolve conflicts
- Approve integrations
- Define subsystem boundaries

### 4.3 Marker Syntax (Git-Like: Simple, Grep-able)

**Design principle:** Make implicit knowledge explicit through structured markers.

**Inline Markers:**
```markdown
# In Delta documents

#VIB:Value "User input must win over periodic updates"
#VIB:Intent "GUI update loop must not override pending user edits"
#VIB:Behavior "Text box reverts to old value when Return pressed"
#VIB:Gap "No lock preventing cache updates during user interaction"

#OSTC:Outcome "GUI responds to user input within 30ms"
#OSTC:Spec "Text input widget locks cache updates while focused"
#OSTC:Test "test_user_input_priority_over_cache_update"
#OSTC:Code "gui_builder.py:234-267"

#DECISION:001 "Chose WebSocket over gRPC for simpler deployment"
#DISCOVERY:042 "OR-Set requires hashable elements, lists must expand"
#LEARNED:007 "Shutdown timeout = N × max_cleanup_time + margin"

#RELATES:O-MP-001
#IMPLEMENTS:S-PS-004
#TESTS:T-WS-012
```

**YAML Frontmatter:**
```yaml
---
delta_type: plan
branch: bike-echoform-relay
base_commit: 6abdec3
harvest_status: pending
ostc_nodes:
  contributes: [O-MP-001, O-NW-003]
  implements: [S-PS-004, S-WS-001]
---
```

**Why this design?**
- **Grep-able**: `grep -r "#DISCOVERY:" jig/deltas/`
- **Simple**: No special tools to read/write
- **Fast**: Regex extraction <1 second
- **Explicit**: No magic, just markers
- **Git-friendly**: Plain text, good diffs

---

## 5. Tool Design: Git Philosophy

### 5.1 Core Commands (Composable)

```bash
# Plumbing (low-level, deterministic, no LLM)
jig extract --branch bike-echoform-relay --output harvest.yaml
jig integrate --harvest harvest.yaml --approve all

# Porcelain (convenience, may use LLM)
jig ai-synthesize --harvest harvest.yaml --output synthesis.yaml
jig ai-integrate --synthesis synthesis.yaml   # Interactive integration with AI assistance
jig ai-distill --branch bike-echoform-relay   # Full pipeline: extract → synthesize → integrate
# (runs extract → ai-synthesize → ai-integrate with review)

# Status (like git status)
jig status
# Shows:
# - Alignment violations
# - Unharvested deltas
# - Decomposability health
# - Recent Intent changes

# Validate (like git fsck)
jig validate --check-all
# Checks:
# - OSTC references valid
# - No orphaned nodes
# - Subsystem boundaries respected
# - No circular dependencies
```

### 5.2 Fast Operations

**Design constraint:** Most operations <1 second.

```bash
# Fast deterministic operations
jig extract    # <1s for 1000 files
jig validate   # <1s for full graph
jig status     # <100ms

# Slow LLM operations (explicit, prefixed with 'ai-')
jig ai-synthesize # 30-60s (LLM call)
jig ai-distill    # 30-60s (includes synthesis)
```

### 5.3 Text-Based Formats

**Everything is grep-able, diff-able, merge-able.**

```yaml
# jig/graph-index.yaml (content-addressable)
nodes:
  S-CRDT-042:
    file: jig/specifications/S-CRDT-042.md
    type: specification
    subsystem: crdt
    edges:
      implements: [O-CRDT-005]
      tested_by: [T-CRDT-089]
    source_deltas:
      - file: jig/deltas/archive/bike-relay/ANALYSIS.md
        line: 67
        commit: a37d344

# jig/subsystems.yaml
subsystems:
  auth:
    internal_edges: 47
    external_edges: 4
    coupling_ratio: 11.75
    exports:
      - authenticate()
      - validate_token()
```

### 5.4 Local-First

**No servers, no network dependencies.**

- All analysis runs locally
- Intent Graph in `jig/` directory
- Deltas in `jig/deltas/`
- Everything in git
- LLM calls optional (can skip synthesis step)

---

## 6. Harvest Workflow

### 6.1 Workflow: Branch Completion Harvest

```bash
# 1. Developer finishes work
git checkout bike-echoform-relay
git status  # Clean working directory

# 2. Write retrospective
jig delta new --type retrospective
# Edit jig/deltas/active/bike-relay/RETROSPECTIVE.md

# 3. Run harvest pipeline
jig ai-distill --branch bike-echoform-relay

# What happens:
# - Extract: Scans all Delta files for markers (fast)
# - Synthesize: LLM proposes Intent updates (slow)
# - Review: Human approves/rejects in terminal UI
# - Integrate: Updates jig/ files (fast)

# 4. Review changes
git diff jig/
jig validate --check-all

# 5. Commit harvest
git add jig/
git commit -m "Harvest insights from bike-echoform-relay

Distilled 47 markers into 12 OSTC nodes:
- 2 new Outcomes
- 5 new Specifications
- 3 new Tests
- 2 architectural patterns

See: jig/harvest-reports/bike-relay-2025-11-16.yaml"

# 6. Merge branch
git checkout main
git merge bike-echoform-relay

# 7. Archive deltas
jig delta archive --branch bike-echoform-relay --retention long-term
# Moves: jig/deltas/active/bike-relay/ → jig/deltas/archive/bike-relay/
```

### 6.2 Workflow: Continuous Harvest

```bash
# During development, capture insights immediately
echo '#DISCOVERY:042 "Widget factory needs lazy init"' >> PLAN.md

# Stage for later
jig extract --incremental --delta PLAN.md --stage
# Adds to jig/staging/discoveries.yaml

# At branch completion
jig ai-distill --from-staging --review
```

### 6.3 Harvest Report Example

```yaml
# jig/harvest-reports/bike-relay-2025-11-16.yaml

metadata:
  timestamp: 2025-11-16T14:32:00Z
  branch: bike-echoform-relay
  base_commit: 6abdec3
  merge_commit: a37d344
  delta_count: 8
  marker_count: 47

markers:
  - file: jig/deltas/active/bike-relay/PLAN.md
    line: 234
    type: VIB
    subtype: Value
    text: "User input must win over periodic updates"

  - file: jig/deltas/active/bike-relay/ANALYSIS.md
    line: 67
    type: DISCOVERY
    id: "042"
    text: "OR-Set requires hashable elements"

decisions:
  - id: D-001
    file: jig/deltas/active/bike-relay/RETROSPECTIVE.md
    line: 145
    title: "WebSocket vs gRPC"
    choice: websocket
    rationale: "Simpler deployment, no protobuf"

statistics:
  vib_values: 12
  vib_intents: 8
  discoveries: 23
  decisions: 12
  learnings: 8
```

### 6.4 Synthesis Proposal Example

```yaml
# Generated by LLM synthesis

synthesis:
  new_nodes:
    - id: S-CRDT-042
      type: specification
      title: "CRDT operations validate input types"
      content: |
        All CRDT operation handlers MUST validate input types.
        OR-Set elements MUST be hashable (str, int, tuple).
        Lists MUST be expanded to individual add operations.
      source_deltas:
        - file: jig/deltas/active/bike-relay/ANALYSIS.md
          line: 67
          marker: DISCOVERY:042
      subsystem: crdt
      priority: high

  modified_nodes:
    - id: S-PS-004
      action: extend
      addition: |
        See ADR-027 for ELC ownership patterns in multi-actor systems.
      rationale: "Delta work discovered ELC ownership as critical"

  conflicts:
    - existing_node: S-CRDT-012
      proposed_node: S-CRDT-042
      conflict_type: semantic_contradiction
      resolution_needed: human_review

  patterns_discovered:
    - name: "ELC Ownership Pattern"
      description: |
        Actors (Store, Relay) own ELC instances.
        Data structures accept timestamps as parameters.
      recommendation: "Create pattern doc in docs/architecture/PATTERNS/"
```

---

## 7. Decomposability Analysis

### 7.1 Commands

```bash
# Detect subsystems automatically
jig decompose --detect

# Validate decomposability health
jig decompose --validate

# Calculate metrics
jig decompose --metrics
```

### 7.2 Metrics Dashboard

```
┌────────────────────────────────────────┐
│     JIG Decomposability Dashboard      │
├────────────────────────────────────────┤
│ Overall Health: ████████░░ (72%)      │
│                                        │
│ Subsystems Detected: 7                 │
│ ├─ auth      [█████████░] 92% healthy │
│ ├─ user      [███████░░░] 71% healthy │
│ ├─ billing   [████████░░] 83% healthy │
│ ├─ catalog   [█████░░░░░] 56% concern │
│ ├─ shipping  [█████████░] 94% healthy │
│ └─ inventory [███████░░░] 67% warning │
│                                        │
│ Key Metrics:                           │
│ • Modularity Score: 0.71 ✓            │
│ • Avg Coupling Ratio: 8.3:1 ⚠         │
│ • Interface Stability: 0.89 ✓         │
│ • Avg Module Depth: 156:1 ✓           │
│                                        │
│ Top Issues:                            │
│ 1. catalog→inventory circular dep ⚠    │
│ 2. user subsystem growing large ⚠      │
└────────────────────────────────────────┘
```

### 7.3 Health Thresholds

| Metric | Excellent | Good | Warning | Critical |
|--------|-----------|------|---------|----------|
| **Modularity Score** | >0.7 | >0.5 | >0.3 | <0.3 |
| **Coupling Ratio** | >15:1 | >10:1 | >5:1 | <5:1 |
| **Interface Stability** | >0.9 | >0.8 | >0.6 | <0.6 |
| **Module Depth** | >200:1 | >100:1 | >50:1 | <50:1 |

---

## 8. Configuration

### 8.1 .jig.toml (Git-like Config)

```toml
# .jig.toml

[core]
version = "6.0"
subsystems = true
deltas = true

[decomposability]
min_modularity = 0.5
min_coupling_ratio = 10
enforce_boundaries = true
alert_on_violations = true

[subsystems.auth]
max_size = 5000
allowed_dependencies = ["config", "crypto"]
exported_interfaces = ["authenticate", "validate_token"]

[deltas]
location = "docs/deltas"
retention_default = "long-term"
auto_archive = true

[harvest]
markers = ["VIB", "OSTC", "DISCOVERY", "DECISION", "LEARNED"]
validate_references = true
require_approval = true

[distill]
llm_model = "claude-sonnet-4.5"
llm_temperature = 0.1
abstraction_level = "medium"
auto_approve = ["new_code_refs"]  # Low-risk changes
```

### 8.2 Delta Templates

```bash
# Create template
jig delta template --type plan --output templates/PLAN_TEMPLATE.md

# Use template
jig delta new --type plan --branch feature/new-work
# Creates: jig/deltas/active/new-work/PLAN_new_work.md from template
```

---

## 9. Implementation Roadmap

### Phase 1: Core Tools (Weeks 1-2)
- [ ] Implement deterministic extractor (`jig extract`)
- [ ] YAML-based harvest report format
- [ ] Basic marker validation
- [ ] Simple integration tool (update OSTC files)

### Phase 2: LLM Synthesis (Weeks 3-4)
- [ ] LLM synthesis prompts (`jig ai-synthesize`)
- [ ] Synthesis proposal format
- [ ] Conflict detection
- [ ] Pattern recognition

### Phase 3: Review & Integration (Weeks 5-6)
- [ ] Terminal UI for review (`jig ai-integrate`)
- [ ] Human approval workflow
- [ ] Traceability linking (Delta ↔ Intent)
- [ ] Changelog generation

### Phase 4: Decomposability (Weeks 7-8)
- [ ] Community detection algorithm
- [ ] Modularity score calculation
- [ ] Boundary violation alerts

### Phase 5: Git Integration (Weeks 9-10)
- [ ] Git hooks for harvest reminders
- [ ] Automatic Delta archiving on merge
- [ ] Branch-Delta binding
- [ ] Commit message templates

---

## 10. Design Principles (What Would Linus Do?)

### 10.1 Simple Text Formats
**Git:** Uses simple text files (refs, objects, index)
**JIG:** Uses YAML frontmatter + Markdown, grep-able markers

### 10.2 Fast Operations
**Git:** Most operations <100ms (status, diff, log)
**JIG:** Deterministic operations <1s, only LLM synthesis is slow

### 10.3 Composable Commands
**Git:** `git diff | git apply`, pipes work
**JIG:** `jig extract | jig ai-synthesize | jig integrate`

### 10.4 Local-First
**Git:** Everything local, distributed by design
**JIG:** All analysis local, no server dependencies

### 10.5 Explicit Over Magic
**Git:** Users control everything, no hidden state
**JIG:** Developers write markers explicitly, approve all integrations

### 10.6 Trust Users
**Git:** Doesn't prevent you from doing dangerous things
**JIG:** Provides tools, not guardrails; trust developers to harvest

### 10.7 Content-Addressable
**Git:** Objects identified by SHA-1 hash
**JIG:** OSTC nodes have stable IDs, source-traceable

### 10.8 Plumbing vs Porcelain
**Git:** Low-level commands (plumbing) + convenience (porcelain)
**JIG:**
- Plumbing: `extract`, `integrate`, `validate`
- Porcelain: `ai-synthesize`, `ai-integrate`, `ai-distill`, `status`

---

## 11. FAQ

### Q: How is this different from documentation?

**A:** Traditional docs are **artifacts** (static, often stale).
JIG has **two dynamic systems:**
- **Intent (OSTC)** = canonical truth, maintained like code
- **Deltas** = temporal narratives, harvested then discarded

### Q: Why delete Deltas if they're valuable?

**A:** Deltas are valuable **during work** and **for harvest**.
After harvest, insights are in Intent Graph (preserved).
Keeping all Deltas forever creates noise and maintenance burden.

Like git commit messages: valuable context, but you don't keep all feature branches forever.

### Q: Isn't the LLM synthesis step slow?

**A:** Yes (30-60s), but it's **opt-in** and **batched**.
Fast path: `jig extract` (deterministic, <1s) → manual review → `jig integrate`
Slow path: `jig ai-distill` (includes LLM synthesis)

Most developers will batch harvest at branch completion, not per-commit.

### Q: What if I don't want to use markers?

**A:** JIG works without markers:
- Minimal: Just OSTC nodes in `jig/`, no Deltas
- Standard: OSTC + Deltas, manual harvest
- Full: OSTC + Deltas + markers, automated harvest

Git philosophy: provide powerful tools, don't force usage.

### Q: How does this scale to large teams?

**A:** Nearly decomposable subsystems enable parallel work:
- Each team owns subsystems
- Intent Graph partitioned by subsystem
- Deltas are branch-scoped (isolated)
- Harvest happens per-branch (no coordination needed)
- Merge conflicts in `jig/` are rare (append-only growth)

---

## 12. Success Metrics

### 12.1 Alignment Metrics
- **Coverage:** % of code with `@jig` annotations
- **Violations:** Misalignments detected per week
- **Resolution Time:** Hours to fix alignment violations

### 12.2 Decomposability Metrics
- **Modularity Score:** >0.5 (good), >0.7 (excellent)
- **Coupling Ratio:** >10:1 internal:external
- **Boundary Violations:** Alerts per month

### 12.3 Harvest Metrics
- **Capture Rate:** % of markers successfully harvested
- **Review Time:** Minutes to review synthesis proposal
- **Knowledge Retention:** Markers harvested before Delta deletion

### 12.4 Velocity Metrics
- **Onboarding Time:** Days for new developer to understand system
- **Change Impact:** % of changes crossing subsystem boundaries
- **Parallel Work:** Number of concurrent feature branches

---

## 13. References & Acknowledgments

### 13.1 Theoretical Foundations

1. **Herbert Simon**
   - "The Architecture of Complexity" (1962)
   - Nearly Decomposable Systems theory

2. **John Ousterhout**
   - "A Philosophy of Software Design" (2018)
   - Deep modules and information hiding

3. **Christopher Alexander**
   - "Notes on the Synthesis of Form" (1964)
   - Design as constraint satisfaction

4. **Linus Torvalds & Git**
   - Simple, fast, composable tools
   - Trust users, local-first, text-based

### 13.2 Related Tools

5. **Architecture Tools**
   - Structure101, Lattix, ArchUnit

6. **Graph Analysis**
   - NetworkX, Gephi, Neo4j

---

## 14. Conclusion: The JIG Promise

### 14.1 What JIG Delivers

**For Developers:**
- Work on subsystems in isolation
- Explicit Intent available at fingertips
- Delta narratives capture journey
- Automated harvest preserves insights

**For Architects:**
- Visible, measurable architecture
- Decomposability metrics
- Alignment validation
- Evolution tracking

**For Business:**
- Intent traceable to business outcomes
- Team scalability through subsystems
- Reduced maintenance costs
- Faster feature delivery

### 14.2 The Philosophy

**Intent is positional. Deltas are vectorial.**

Intent describes the world as it is (or should be).
Deltas describe how we changed that world.

Both are essential:
- Intent enables **alignment** (building the right thing)
- Deltas enable **learning** (understanding how we got here)

JIG maintains Intent.
Deltas maintain **wisdom**.

### 14.3 The Git Parallel

**Git doesn't build software—it tracks changes.**
**JIG doesn't build software—it maintains alignment.**

Both are version control systems:
- Git: version control for **code**
- JIG: version control for **intent**

Both follow the same philosophy:
- Simple tools
- Fast operations
- Composable commands
- Local-first
- Trust users

---

**Document Version:** 6.0.0
**Last Updated:** 2025-11-16
**Key Innovations:**
- Deltas as temporal counterpart to timeless Intent
- Harvest/distill pipeline for systematic knowledge extraction
- Git philosophy throughout (simple, fast, composable, local-first)

**Status:** Architecture Proposal

---

*"JIG: The alignment template for nearly decomposable software."*
*"Intent documented. Deltas narrated. Wisdom harvested. Alignment maintained."*
