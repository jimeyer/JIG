# JIG: Jig Intent Graph v6.0

**An Alignment System for Nearly Decomposable Software**

**Date:** 2025-11-18
**Status:** Architecture Proposal
**Key Innovation:** Git-native deltas with deterministic harvest

> **v6 Philosophy:** Simple, fast, text-based. If git can scan the Linux kernel in milliseconds, JIG should be similarly lean. Deterministic core, AI as optional porcelain.

---

## Executive Summary

JIG treats software development as maintaining alignment across four representations of truth:

- **Outcome (O)**: What business value we deliver
- **Specification (S)**: What technical requirements we satisfy
- **Test (T)**: How we verify correctness
- **Code (C)**: What actually runs

**The Core Insight:**

Intent (OSTC) is **positional** - it describes where we are now.
Deltas are **vectorial** - they describe how we got here.

Intent captures **state**. Deltas capture **change**.

**The Git-Native Approach:**

Like git objects, JIG artifacts are:
- Plain text (grep-able, diff-able, merge-able)
- Content-addressed (immutable truth)
- Distributed (no central database)
- Fast (scan entire project in <1 second)

**The Promise:**

Nearly decomposable systems naturally exhibit sparse inter-module coupling with dense intra-module cohesion. JIG makes this structure visible, measurable, and maintainable while harvesting insights from temporal work artifacts into timeless Intent.

---

## 1. The OSTC Model

### 1.1 Four Types of Truth

| Element           | Truth Type               | Lifecycle | Storage                      |
| ----------------- | ------------------------ | --------- | ---------------------------- |
| **Outcome**       | Narrative truth (why)    | Timeless  | `jig/outcomes/O-*.md`       |
| **Specification** | Logical truth (what)     | Timeless  | `jig/specifications/S-*.md` |
| **Test**          | Empirical truth (verify) | Timeless  | Annotated with `@jig`        |
| **Code**          | Operational truth (how)  | Timeless  | Annotated with `@jig`        |

**Pattern:** Intent lives in separate files (O, S). Reality is marked inline (T, C).

**Acceptance criteria:** Non-code verification criteria live in Outcome or Specification files as prose, not separate test files.

### 1.2 Intent Files (O, S)

**Outcome example:**

```yaml
---
id: O-AUTH-001
type: outcome
title: "Users authenticate securely across multiple devices"
subsystem: auth
created: 2025-11-18
---

# Outcome: Multi-device authentication

Users can log in on phone, tablet, desktop with same credentials.
Session persists across devices. Logout on one device doesn't affect others.

## Value
Enables mobile-first workflow. Users start on phone, continue on desktop.

## Acceptance Criteria
- User logs in on device A, immediately usable on device B
- Session persists for 24 hours without re-auth
- Device-specific revocation supported

## Related
- specs: S-AUTH-001, S-AUTH-002
- tests: T-AUTH-001, T-AUTH-003
```

**Specification example:**

```yaml
---
id: S-AUTH-001
type: specification
title: "JWT tokens with 24-hour expiration"
subsystem: auth
created: 2025-11-18
source_delta: jig/deltas/auth-refactor/RETRO.md:67
---

# Specification: JWT-based authentication

JWT tokens with 24-hour expiration.
Refresh tokens stored in secure keychain.
Device ID embedded in token claims.

## Rationale
Enables offline operation while maintaining security.

## Related
- implements: O-AUTH-001
- tested_by: T-AUTH-001, T-AUTH-003
- code: C-AUTH-001
```

**Why plain markdown?**
- Grep-able: `grep -r "JWT" jig/`
- Diff-able: See what changed
- Merge-able: Conflicts are visible
- No parser needed for reading

### 1.3 Reality Annotations (T, C)

**Test annotation:**

```python
# test_auth.py

# @jig T-AUTH-001 verifies:S-AUTH-001 subsystem:auth
def test_jwt_token_validation():
    """Verify JWT tokens validate correctly with device ID"""
    token = create_token(device_id="device-123")
    claims = authenticator.validate_token(token)
    assert claims.device_id == "device-123"
    assert claims.expiration > now()

# @jig T-AUTH-003 verifies:S-AUTH-001,O-AUTH-001 subsystem:auth
def test_multi_device_session():
    """Verify same user can be logged in on multiple devices"""
    token_a = login(user="alice", device="phone")
    token_b = login(user="alice", device="desktop")
    assert both_valid(token_a, token_b)
```

**Code annotation:**

```python
# auth.py

# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:auth interface:public
class JWTAuthenticator:
    """Handles JWT-based multi-device authentication"""

    # @jig C-AUTH-002 implements:S-AUTH-001,S-AUTH-002 subsystem:auth
    def validate_token(self, token: str) -> Claims:
        """Validates JWT and extracts claims"""
        # ... implementation ...
```

**Annotation rules:**
- One line, inline comment
- Pattern: `@jig {id} {relations} {metadata}`
- Test relations: `verifies:S-001` `verifies:O-001`
- Code relations: `implements:S-001` `depends:C-002`
- Metadata: `subsystem:auth interface:public`

---

## 2. Nearly Decomposable Systems

### 2.1 The Architectural Constraint

From Herbert Simon: well-designed systems exhibit **sparse inter-module** connections with **dense intra-module** connections.

**Target Metrics:**

```python
# Coupling Ratio (internal edges / external edges)
coupling_ratio = internal_edges / external_edges
target = 10:1  # At least 10x more internal than external

# Modularity (Newman-Girvan score)
modularity = sum(e_ii - a_i^2 for all communities)
target = 0.5  # Significant community structure

# Module Depth (LOC per export)
depth = lines_of_code / number_of_exports
target = 100:1  # Deep modules (Ousterhout)
```

### 2.2 Subsystem Detection

```bash
# Auto-detect subsystem boundaries
jig decompose --detect

# Output: Clusters with coupling metrics
Subsystem: auth (2.3k LOC, 3 exports)
├─ Internal edges: 47
├─ External edges: 4
├─ Coupling ratio: 11.8:1 ✓
└─ Modularity: 0.89 ✓

Subsystem: crdt (4.1k LOC, 7 exports)
├─ Internal edges: 89
├─ External edges: 12
├─ Coupling ratio: 7.4:1 ⚠
└─ Modularity: 0.73 ✓
```

### 2.3 Subsystem Annotation

```python
# @jig C-001 implements:S-001 subsystem:auth interface:public
def authenticate(user: str, password: str) -> Token:
    """Public authentication API"""

# @jig C-002 implements:S-002 subsystem:auth depends:crypto
def _hash_password(password: str) -> bytes:
    """Internal helper, depends on crypto subsystem"""
```

**Key:**
- `interface:public` = exported, part of subsystem boundary
- `depends:X` = cross-subsystem dependency (keep these minimal)
- Subsystem names map to package/module structure

---

## 3. Deltas: Temporal Work Artifacts

### 3.1 What Are Deltas?

**Deltas** are working documents tied to git branches. They capture the narrative of change.

| Aspect | Intent (OSTC) | Deltas |
|--------|---------------|--------|
| **Time** | Present state | Past→Future journey |
| **Purpose** | What/Why/How | The story of change |
| **Truth** | Resolved | Options, failures, decisions |
| **Lifecycle** | Permanent | Branch-scoped |
| **Location** | `jig/` | `jig/deltas/{branch}/` |

### 3.2 Delta Types

```
jig/deltas/
├─ active/              # Current work (WIP branches)
│  └─ feature-x/
│     ├─ PLAN.md       # Execution roadmap
│     ├─ RETRO.md      # Retrospective (written at end)
│     └─ NOTES.md      # Scratchpad
└─ archive/            # Completed work (merged branches)
   └─ feature-x/       # Frozen after merge
```

### 3.3 Delta Lifecycle = Git Workflow

```
Branch created
└─> mkdir jig/deltas/active/{branch}/

During work
├─> Update PLAN.md with discoveries
├─> Mark insights with #DISCOVERY, #LEARNED, #DECISION
└─> Commit deltas alongside code

Before merge
├─> Write RETRO.md
├─> Run: jig harvest --branch {branch}
└─> Review synthesis, integrate to jig/

After merge
└─> mv jig/deltas/active/{branch}/ jig/deltas/archive/
```

**Git-native binding:**
- Branch name = delta directory name
- Commits reference deltas: `See: jig/deltas/active/feature-x/PLAN.md:L42`
- Delta frontmatter references commits: `base_commit: abc123`

---

## 4. Harvest & Distill: From Deltas to Intent

### 4.1 The Pipeline (Three Phases)

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   EXTRACT    │───>│  SYNTHESIZE  │───>│  INTEGRATE   │
│ deterministic│    │  LLM-assisted│    │human-approved│
│   <1 sec     │    │   30-60 sec  │    │   <1 sec     │
└──────────────┘    └──────────────┘    └──────────────┘
```

**Phase 1: EXTRACT** (deterministic, grep-speed)
- Scan deltas for markers: `#DISCOVERY`, `#LEARNED`, `#DECISION`
- Output: harvest report (YAML)
- Zero false negatives

**Phase 2: SYNTHESIZE** (LLM, optional)
- Understand context, elevate abstraction
- Categorize into OSTC types (O/S/T/C)
- Detect patterns, conflicts
- Output: synthesis proposal (YAML)

**Phase 3: INTEGRATE** (human-approved)
- Review proposal
- Create/update jig/ files
- Add traceability links
- Run validation

### 4.2 Marker Syntax (Simple, Inline)

```markdown
# In jig/deltas/active/feature-x/PLAN.md

We tried threading first, but hit the GIL bottleneck.

#DISCOVERY "Multi-process required for true parallelism"
#RELATES O-PERF-001

Then tried shared memory for GUI updates.

#LEARNED "GUI widgets can't cross process boundaries"
#DECISION "Use WebSocket for inter-process communication"
```

**Marker pattern:**
```
#{TYPE} "one-line summary"
#RELATES node-id
```

**Types:**
- `#DISCOVERY` - found something new (requirement, constraint)
- `#LEARNED` - gained knowledge (pattern, anti-pattern)
- `#DECISION` - chose A over B (rationale required)
- `#RELATES` - links to OSTC node

**Why simple?**
- Grep-able: `grep -r "#DISCOVERY" jig/deltas/`
- Fast extraction: regex match, no parsing
- Easy to write during flow
- No ceremony, no YAML

### 4.3 Extraction (Plumbing)

```bash
# Extract markers from branch deltas
jig extract --branch feature-x

# Output: harvest-report.yaml
markers:
  - type: DISCOVERY
    text: "Multi-process required for true parallelism"
    file: jig/deltas/active/feature-x/PLAN.md
    line: 23
    relates: [O-PERF-001]

  - type: LEARNED
    text: "GUI widgets can't cross process boundaries"
    file: jig/deltas/active/feature-x/PLAN.md
    line: 27

  - type: DECISION
    text: "Use WebSocket for inter-process communication"
    file: jig/deltas/active/feature-x/PLAN.md
    line: 29
```

**Speed requirement:** <1 second for 1000 files

### 4.4 Synthesis (Porcelain, Optional)

```bash
# LLM synthesis (optional, requires API key)
jig ai-synthesize --harvest harvest-report.yaml

# Output: synthesis-proposal.yaml
new_nodes:
  - id: S-IPC-001
    type: specification
    title: "Inter-process communication uses WebSocket"
    content: |
      GUI processes communicate via WebSocket over localhost.
      Avoids GIL bottleneck and process boundary issues.
    source_delta: jig/deltas/active/feature-x/PLAN.md:29
    subsystem: ipc

patterns_discovered:
  - name: "Process Isolation Pattern"
    description: |
      GUI widgets in separate processes.
      WebSocket for message passing.
      Avoids shared memory and thread safety issues.
```

**Can skip LLM:** Extract markers, manually write OSTC nodes. LLM is convenience, not requirement.

### 4.5 Integration (Human Gate)

```bash
# Review and integrate
jig integrate --proposal synthesis-proposal.yaml --review

# Interactive TUI:
# [1/5] New node: S-IPC-001
# Title: Inter-process communication uses WebSocket
# [A]pprove [E]dit [S]kip [Q]uit
# > a

# Approved: creates jig/specifications/S-IPC-001.md
# Adds traceability link to delta
# Updates graph index (T and C nodes point to test/src files with @jig)
```

**Note:** Integration creates O and S files only. T and C nodes exist as `@jig` annotations in code/tests - integration adds them to graph index by scanning for annotations.

---

## 5. Tool Design Philosophy: Git as Lodestar

### 5.1 What Would Linus Do?

**Git principles applied to JIG:**

| Git Principle | JIG Application |
|--------------|-----------------|
| **Fast** | Scan 10k files in <1 sec (like git status) |
| **Text-based** | All files .md or .yaml (like git objects) |
| **Distributed** | No database, just files (like git repo) |
| **Content-addressed** | Nodes by ID, immutable (like git SHA) |
| **Plumbing vs porcelain** | Core tools + convenience wrappers |
| **Trust developer** | Sharp tools, require skill (like rebase) |
| **Explicit** | No magic, no hidden state |

### 5.2 Plumbing vs Porcelain

**Plumbing (core, deterministic, fast):**
```bash
jig extract       # Find markers (grep-speed)
jig validate      # Check graph consistency
jig graph         # Generate graph data
jig decompose     # Calculate metrics
jig integrate     # Apply approved changes to jig/
```

**Porcelain (convenience, may use LLM):**
```bash
jig ai-synthesize # LLM-assisted OSTC proposal
jig ai-integrate  # Interactive integration with AI assistance
jig ai-distill    # Full pipeline: extract → synthesize → integrate
```

**Naming convention:** Any command that calls an LLM has `ai-` prefix. This makes API usage explicit and cost-transparent.

**You can use JIG without AI.** Plumbing is self-contained.

### 5.3 Speed Targets

```
jig extract       <1 second  (10k files)
jig validate      <1 second  (1k nodes)
jig graph         <2 seconds (1k nodes, 5k edges)
jig decompose     <3 seconds (complex analysis)
jig ai-synthesize 30-60 sec  (LLM call)
```

### 5.4 File Format Constraints

**All human-readable text:**
- OSTC nodes: Markdown with YAML frontmatter
- Graph index: YAML
- Harvest reports: YAML
- Deltas: Markdown
- Config: TOML (like git config)

**Why?**
- Standard tools work (grep, sed, diff, merge)
- No special viewers needed
- Merge conflicts visible
- Human-readable diffs in PR

---

## 6. Decomposability Analysis

### 6.1 Core Metrics

```bash
jig decompose --metrics

# Output
Overall Decomposability: 78% ✓

Subsystems: 7
├─ auth      (92% healthy, 11.8:1 coupling)
├─ crdt      (73% healthy, 7.4:1 coupling)
├─ gui       (81% healthy, 9.2:1 coupling)
├─ network   (67% healthy, 5.8:1 coupling) ⚠
├─ protocol  (89% healthy, 13.1:1 coupling)
├─ storage   (94% healthy, 15.2:1 coupling)
└─ testing   (98% healthy, 22.1:1 coupling)

Issues:
1. network subsystem below 10:1 coupling target
2. Circular dependency: storage ↔ protocol
```

**Note:** Graph visualization is plugin/add-on territory. UI needs are deep and diverse - no baseline behavior prescribed. `jig graph` outputs data (YAML/JSON/DOT), external tools render.

### 6.2 Enforcement

```toml
# jig/config.toml

[decomposability]
min_coupling_ratio = 10.0
min_modularity = 0.5
max_subsystem_size = 10000

[subsystems.auth]
max_exports = 5
allowed_dependencies = ["crypto", "config"]

[subsystems.network]
max_exports = 10
allowed_dependencies = ["protocol", "config"]
```

```bash
# CI/CD gate
jig decompose --validate --strict

# Fails if:
# - Coupling ratio < 10:1
# - Modularity < 0.5
# - Subsystem exceeds size limit
# - Forbidden dependency added
```

---

## 7. Practical Workflows

### 7.1 Starting New Work

```bash
# Create branch and delta directory
git checkout -b feature-multiprocess
mkdir -p jig/deltas/active/feature-multiprocess

# Start delta
cat > jig/deltas/active/feature-multiprocess/PLAN.md << 'EOF'
# Feature: Multiprocess Architecture

## Goal
Scale to 30+ devices without GUI lag.

## Approach
Try multi-process with WebSocket IPC.

## Work Units
- [ ] WU1: Process launcher
- [ ] WU2: WebSocket server
- [ ] WU3: Client integration
EOF

git add jig/deltas/
git commit -m "Start feature-multiprocess"
```

### 7.2 Capturing Discoveries (During Work)

```bash
# While coding, add markers to PLAN.md
echo "" >> jig/deltas/active/feature-multiprocess/PLAN.md
echo "#DISCOVERY \"Process isolation solves GIL bottleneck\"" >> jig/deltas/active/feature-multiprocess/PLAN.md
echo "#RELATES O-PERF-001" >> jig/deltas/active/feature-multiprocess/PLAN.md

# Commit alongside code changes
git add jig/deltas/ src/
git commit -m "WU1: Process launcher

See: jig/deltas/active/feature-multiprocess/PLAN.md:L23"
```

### 7.3 Harvest Before Merge

```bash
# Feature complete, write retrospective
cat > jig/deltas/active/feature-multiprocess/RETRO.md << 'EOF'
# Retrospective: Multiprocess Architecture

## What Worked
- WebSocket IPC clean and simple
- Process isolation eliminated race conditions

#LEARNED "Graceful shutdown needs timeout = N × 200ms + 1s"

## What Didn't
- Tried shared memory first (failed - GUI thread safety)

#DECISION "Use WebSocket over shared memory"

## Outcomes Achieved
#RELATES O-PERF-001
EOF

# Extract markers
jig extract --branch feature-multiprocess --output harvest.yaml

# (Optional) LLM synthesis
jig ai-synthesize --harvest harvest.yaml --output synthesis.yaml

# Review and integrate (human approval)
jig integrate --proposal synthesis.yaml --review

# Approve creates:
# - jig/specifications/S-IPC-001.md
# - jig/outcomes/O-PERF-001.md (updated)
# - Traceability links

# Commit Intent changes
git add jig/
git commit -m "Harvest: feature-multiprocess → Intent"

# Merge branch
git checkout main
git merge feature-multiprocess

# Archive delta
mv jig/deltas/active/feature-multiprocess/ jig/deltas/archive/
git add jig/deltas/
git commit -m "Archive: feature-multiprocess deltas"
```

### 7.4 Validate Alignment

```bash
# Check OSTC graph consistency
jig validate --check-all

# Checks:
# ✓ All @jig annotations reference valid nodes
# ✓ All OSTC relations exist
# ✓ No orphaned nodes
# ✗ S-IPC-001 missing test reference (warning)

# Check decomposability
jig decompose --validate

# ✓ All subsystems meet coupling ratio target
# ✓ Modularity score: 0.72 (above 0.5)
# ⚠ network subsystem has 8.1:1 coupling (target: 10:1)
```

---

## 8. Data Model

### 8.1 Directory Structure

```
jig/
├─ config.toml                 # Project configuration
├─ graph-index.yaml           # Node and edge registry
├─ outcomes/
│  ├─ O-PERF-001.md           # Business outcomes
│  └─ O-AUTH-001.md
├─ specifications/
│  ├─ S-IPC-001.md            # Technical requirements
│  └─ S-AUTH-001.md
└─ deltas/
   ├─ active/                 # Current work
   │  └─ {branch-name}/
   │     ├─ PLAN.md
   │     ├─ NOTES.md
   │     └─ RETRO.md
   └─ archive/                # Completed work
      └─ {branch-name}/
         └─ (frozen)

src/                          # Code with @jig annotations
test/                         # Tests with @jig annotations
```

### 8.2 Graph Index (Fast Lookups)

```yaml
# jig/graph-index.yaml

nodes:
  O-PERF-001:
    file: jig/outcomes/O-PERF-001.md
    type: outcome
    subsystem: performance

  S-IPC-001:
    file: jig/specifications/S-IPC-001.md
    type: specification
    subsystem: ipc

  T-IPC-001:
    file: test/test_ipc.py
    line: 42
    type: test
    subsystem: ipc

  C-IPC-001:
    file: src/ipc/websocket.py
    line: 23
    type: code
    subsystem: ipc

edges:
  - from: S-IPC-001
    to: O-PERF-001
    type: implements

  - from: T-IPC-001
    to: S-IPC-001
    type: verifies

  - from: C-IPC-001
    to: S-IPC-001
    type: implements

subsystems:
  ipc:
    nodes: [S-IPC-001, T-IPC-001, C-IPC-001]
    internal_edges: 12
    external_edges: 2
    coupling_ratio: 6.0
```

**Key differences:**
- O and S nodes: Point to `jig/` files
- T and C nodes: Point to source/test files + line number
- All tracked in same index

**Regenerate index:**
```bash
jig index --rebuild
# Scans jig/ files + extracts @jig annotations from code/tests
```

### 8.3 Traceability Links

**Forward (Intent → Delta):**
```yaml
# In jig/specifications/S-IPC-001.md frontmatter
---
id: S-IPC-001
source_delta: jig/deltas/archive/feature-multiprocess/PLAN.md:42
source_commit: a7f3c2b
source_branch: feature-multiprocess
---
```

**Reverse (Delta → Intent):**
```markdown
# In jig/deltas/archive/feature-multiprocess/PLAN.md

#DISCOVERY "Process isolation solves GIL bottleneck"
<!-- @jig-harvested: S-IPC-001, 2025-11-18 -->
```

---

## 9. Implementation Roadmap

### 9.1 Phase 1: Core Plumbing (Weeks 1-2)

**Deliverables:**
- `jig extract` - marker extraction (grep-based)
- `jig validate` - graph consistency checks
- `jig index` - graph index builder
- File format specs finalized

**Success criteria:**
- Extract 1000 markers in <1 second
- Validate 1000 nodes in <1 second
- All output is valid YAML/markdown

### 9.2 Phase 2: Decomposability (Weeks 3-4)

**Deliverables:**
- `jig decompose --detect` - subsystem detection
- `jig decompose --metrics` - coupling/modularity calculation
- `jig decompose --validate` - boundary enforcement
- Graph visualization (Graphviz output)

**Success criteria:**
- Detect subsystems in ASE codebase
- Calculate accurate coupling ratios
- Generate useful visualizations

### 9.3 Phase 3: Harvest Pipeline (Weeks 5-6)

**Deliverables:**
- `jig ai-synthesize` - LLM synthesis (optional)
- `jig integrate` - apply approved synthesis proposals
- `jig ai-integrate` - interactive TUI with AI assistance
- `jig ai-distill` - full pipeline orchestrator
- Marker linting

**Success criteria:**
- Harvest one ASE branch end-to-end
- >80% marker capture rate
- <10 minutes human review time

### 9.4 Phase 4: Porcelain & Polish (Weeks 7-8)

**Deliverables:**
- `jig delta new` - delta templates
- `jig delta archive` - automated archival
- `jig graph --interactive` - interactive explorer
- Documentation and examples

**Success criteria:**
- Complete user guide
- Example project with full OSTC
- CI/CD integration guide

---

## 10. Metrics & Success Criteria

### 10.1 Tool Performance

| Metric | Target | Why |
|--------|--------|-----|
| Extract speed | <1 sec / 10k files | Git-like responsiveness |
| Validate speed | <1 sec / 1k nodes | No waiting for checks |
| Graph generation | <2 sec / 1k nodes | Fast iteration |
| Marker capture rate | >85% | Minimize knowledge loss |

### 10.2 Decomposability Health

| Metric | Excellent | Good | Warning | Critical |
|--------|-----------|------|---------|----------|
| Coupling ratio | >15:1 | >10:1 | >5:1 | <5:1 |
| Modularity | >0.7 | >0.5 | >0.3 | <0.3 |
| Module depth | >200:1 | >100:1 | >50:1 | <50:1 |

### 10.3 Adoption Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| Delta completion | 100% branches have deltas | Week 4 |
| Harvest rate | 100% deltas harvested before archive | Week 6 |
| OSTC coverage | >80% code has @jig annotations | Week 8 |
| Subsystem clarity | All code assigned to subsystem | Week 8 |

---

## 11. Design Decisions

### 11.1 Why Plain Text?

**Decision:** All artifacts are human-readable text (.md, .yaml, .toml)

**Rationale:**
- Standard tools work (grep, diff, merge)
- No special viewers required
- Git-friendly (meaningful diffs)
- Future-proof (text outlives binary formats)
- Inspectable (cat/less work)

**Tradeoff:**
- Slightly larger file sizes
- Manual schema validation needed
- No relational queries

**Commit:** Text-based. Like git.

### 11.2 Why Git-Native Deltas?

**Decision:** Delta lifecycle bound to git branches

**Rationale:**
- Git already tracks branches, commits, merges
- No parallel tracking system needed
- Natural scope (branch = one logical change)
- Automatic history (git log)
- Merge = natural harvest checkpoint

**Tradeoff:**
- Deltas live in repo (larger repo size)
- Archived deltas could be pruned

**Commit:** Git-native. Branch = delta scope.

### 11.3 Why Optional LLM?

**Decision:** Core extraction is deterministic, LLM synthesis is optional porcelain

**Rationale:**
- Plumbing works without API keys
- Deterministic = testable, reproducible
- LLM is convenience, not dependency
- Human can do synthesis manually

**Tradeoff:**
- More human work if no LLM
- Need to maintain both paths

**Commit:** Optional LLM. Trust humans more than AI.

### 11.4 Why Simple Markers?

**Decision:** Inline markers only: `#DISCOVERY "text"`

**Rationale:**
- Grep-able (fast extraction)
- Low ceremony (easy to write during flow)
- No context switching (stay in markdown)
- Regex-parseable (no AST needed)

**Tradeoff:**
- Less structure than YAML blocks
- Context comes from surrounding text

**Commit:** Simple markers. Optimize for writing speed.

### 11.5 Why `ai-` Prefix for LLM Commands?

**Decision:** Commands that call LLMs have `ai-` prefix (`jig ai-synthesize`, not `jig synthesize`)

**Rationale:**
- **Cost transparency**: API calls cost money, prefix makes this explicit
- **Offline usage**: Clear which commands need network/API keys
- **Predictability**: Deterministic commands have no prefix
- **Discoverability**: `jig ai-<tab>` shows all AI features
- **Future-proof**: More AI features can follow same pattern

**Tradeoff:**
- Slightly longer command names
- Two-tier UX (plumbing vs AI porcelain)

**Commit:** `ai-` prefix. Make cost and dependencies explicit.

### 11.6 Why Visible `jig/` Not Hidden `.jig/`?

**Decision:** Use `jig/` folder not `.jig/` (no leading dot)

**Rationale:**
- **Browsing**: Developers need to read outcomes/specs frequently
- **Discovery**: New contributors can `ls` and find Intent easily
- **Tools**: No special flags needed (`ls -a`)
- **IDE**: Visible folders show in file trees by default

**Tradeoff:**
- Slightly more visible clutter in root
- Not "magic infrastructure" like `.git`

**Commit:** Visible `jig/`. Intent is for humans, not hidden plumbing.

### 11.7 Why Colocate Deltas in `jig/deltas/`?

**Decision:** Deltas live in `jig/deltas/` not `docs/deltas/`

**Rationale:**
- **Single tree**: All JIG artifacts under one roof
- **Conceptual clarity**: Deltas are JIG-specific, not general docs
- **Traceability**: Delta → Intent paths shorter (`jig/deltas` → `jig/outcomes`)
- **Consistency**: `jig/` is the namespace

**Tradeoff:**
- Mixing timeless (outcomes) with temporal (deltas)
- `jig/` folder gets larger

**Commit:** Colocate. `jig/` is the Intent universe (both static and dynamic).

---

## 12. Comparison to Alternatives

### 12.1 vs Traditional ADRs

| Aspect | Traditional ADRs | JIG |
|--------|-----------------|-----|
| **Scope** | Architectural decisions only | All Intent (O/S/T/C) |
| **Structure** | Unstructured markdown | Graph with relationships |
| **Traceability** | Manual links | Bidirectional, enforced |
| **Evolution** | Static documents | Living graph |
| **Tooling** | None (just files) | Analysis, validation, viz |

**When to use ADRs:** Standalone for architectural decisions
**When to use JIG:** Full system Intent with code linkage

### 12.2 vs Knowledge Graphs

| Aspect | Knowledge Graphs | JIG |
|--------|-----------------|-----|
| **Storage** | Database (Neo4j, etc) | Text files (git-tracked) |
| **Schema** | Formal ontology | Simple OSTC types |
| **Queries** | Cypher/SPARQL | Grep, YAML parsing |
| **Distribution** | Centralized | Distributed (git) |
| **Setup** | Complex (DB server) | Simple (just files) |

**When to use KG:** Complex ontology, heavy querying
**When to use JIG:** Lightweight, git-native, simple

### 12.3 vs Living Documentation

| Aspect | Living Docs | JIG |
|--------|------------|-----|
| **Source** | Code comments | Code + separate Intent files |
| **Generation** | Automated from code | Manual curation + harvest |
| **Abstraction** | Code-level | Business + technical |
| **Verification** | Tests | OSTC alignment validation |

**When to use Living Docs:** API documentation
**When to use JIG:** Business intent + architecture

---

## 13. FAQ

### Q: How is this different from Literate Programming?

**A:** Literate programming embeds code in documentation. JIG separates Intent (timeless) from Code (implementation). Code changes frequently; Intent evolves slowly. Different lifecycles require separation.

### Q: Won't jig/ get out of sync with code?

**A:** Yes, without discipline. That's why:
1. `jig validate` checks alignment (run in CI)
2. Harvest process extracts Intent from deltas (captures discoveries)
3. `@jig` annotations in code link to Intent nodes

It's like tests: they can get stale, but validation catches it.

### Q: Why not use a database for the graph?

**A:** Git is the database. Text files in git provide:
- Distribution (clone = full copy)
- History (git log shows evolution)
- Branching (experiment with Intent changes)
- Merging (resolve conflicts visibly)
- Tooling (grep, diff, merge work)

Database adds complexity without clear benefit.

### Q: Is this just more documentation burden?

**A:** Only if you don't harvest. The workflow is:
1. Work in deltas (informal, like notes)
2. Mark discoveries as you find them (`#DISCOVERY`)
3. Harvest extracts markers into Intent
4. Archive deltas when done

Most Intent comes from **harvesting**, not manual authoring.

### Q: What if my system is highly coupled?

**A:** JIG measures coupling, doesn't require low coupling. For highly connected systems:
- Use to visualize actual coupling
- Track coupling over time
- Identify opportunities to decouple
- Accept high coupling where necessary (but measure it)

### Q: Can I use JIG on existing codebases?

**A:** Yes:
1. Start with one subsystem
2. Create OSTC nodes for it
3. Add `@jig` annotations gradually
4. Expand subsystem by subsystem
5. Let decomposability analysis guide prioritization

### Q: How does this scale to large teams?

**A:** Like git:
- Each developer works in branches (deltas are branch-scoped)
- Intent changes merge like code (resolve conflicts in jig/)
- Subsystem boundaries enable parallel work
- Graph index enables fast lookups

---

## 14. Theoretical Foundations

### 14.1 Herbert Simon - Nearly Decomposable Systems

> "The behavior of a nearly decomposable system is approximately the sum of the behaviors of its subsystems, considered in isolation, plus the interactions among subsystems."

**Applied:**
- JIG detects subsystem boundaries via clustering
- Coupling ratio quantifies "nearly" (10:1 target)
- Modularity score measures decomposability

**Reference:** "The Architecture of Complexity" (1962)

### 14.2 John Ousterhout - Deep Modules

> "The best modules are those whose interfaces are much simpler than their implementations."

**Applied:**
- Module depth metric: LOC / exports
- Target: >100:1 (deep modules)
- `interface:public` annotation marks boundaries

**Reference:** "A Philosophy of Software Design" (2018)

### 14.3 Christopher Alexander - Design as Constraint Satisfaction

> "Good design emerges from constraints, not plans."

**Applied:**
- Intent defines constraints (Outcomes, Specs)
- Code satisfies constraints
- Validation checks alignment
- Deltas capture constraint discovery

**Reference:** "Notes on the Synthesis of Form" (1964)

### 14.4 Linus Torvalds - Git Philosophy

> "The first rule of kernel development: never break user space."

**Applied:**
- Simple, fast, text-based tools
- Trust the developer (sharp tools)
- No magic, explicit operations
- Speed matters

**Reference:** Git design philosophy

---

## 15. Conclusion

### 15.1 The Core Thesis

**Software development is maintaining alignment across representations:**
- Business intent (Outcomes)
- Technical requirements (Specifications)
- Verification (Tests)
- Implementation (Code)

**The alignment problem has two dimensions:**
1. **Synchronic:** Are O/S/T/C aligned right now?
2. **Diachronic:** How do we harvest insights from change into Intent?

**JIG solves both:**
- OSTC graph for synchronic alignment
- Delta harvest for diachronic learning
- Decomposability for structural health

### 15.2 The Promise

**10x improvement in:**
- Knowledge retention (harvest vs forget)
- Parallel development (subsystem isolation)
- Onboarding time (Intent graph shows design)
- Architectural drift detection (metrics over time)

**By making visible:**
- What we intend (Outcomes)
- What we require (Specifications)
- What we verify (Tests)
- What we run (Code)
- How we got here (Deltas)
- How it's organized (Subsystems)

### 15.3 The Git-Native Advantage

Like git transformed version control by being:
- Fast (millisecond operations)
- Simple (text-based, grep-able)
- Distributed (no central server)
- Powerful (sharp tools for experts)

JIG transforms Intent management by being:
- Fast (grep-speed extraction)
- Simple (markdown + YAML)
- Distributed (git-tracked files)
- Powerful (decomposability analysis, harvest pipeline)

**The result:**
> "Software that knows its own purpose, maintains its boundaries, and learns from its own evolution."

---

## 16. Migration from v5

**v5 → v6 changes:**

| v5 | v6 | Rationale |
|----|----|----|
| Complex YAML frontmatter | Simple frontmatter | Optimize for writing |
| Structured delta blocks | Inline markers | Grep-able, fast |
| "Working docs" | "Deltas" | Clearer terminology |
| Separate harvest tracking | Git-native binding | Simpler, no parallel tracking |
| LLM-required synthesis | Optional LLM | Works without API |
| Abstract tool design | Concrete implementation | Ship-able |
| Separate test files (jig/tests/) | @jig on test code | Tests are code, mark inline |
| `.jig/` hidden folder | `jig/` visible folder | Easy browsing of outcomes/specs |
| `docs/deltas/` separate | `jig/deltas/` colocated | Single jig/ tree |
| `jig synthesize` | `jig ai-synthesize` | Explicit LLM usage (cost) |

**Migration path:**
1. Rename `.jig/` → `jig/` (visible folder)
2. Move `docs/deltas/` → `jig/deltas/` (colocate)
3. Existing OSTC nodes compatible (no changes)
4. Deltas: add simple markers to existing docs
5. Harvest: manual first, then automate
6. Tools: build incrementally (plumbing first)

**No breaking changes to OSTC model.**

---

**Document Version:** 6.0.0
**Date:** 2025-11-18
**Authors:** Jim & Claude
**Status:** Architecture Proposal
**Next:** Phase 1 implementation (core plumbing)

---

*"JIG: Simple, fast, git-native Intent alignment."*
*"Intent documented. Deltas harvested. Boundaries preserved. Alignment maintained."*
