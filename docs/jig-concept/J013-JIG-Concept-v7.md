# JIG: Jig Intent Graph v7.0

**An Alignment System for Nearly Decomposable Software**

**Date:** 2025-11-20
**Status:** Architecture Proposal
**Key Innovations:**
- Constraints as predicates over Intent Graph
- Nested subsystems for hierarchical organization

> **v7 Philosophy:** Nearly decomposable systems with cross-cutting constraints and hierarchical organization. OSTC models intent hierarchy; X models system-wide properties as queries, not nodes; subsystems can nest to arbitrary depth.

---

## Executive Summary

JIG treats software development as maintaining alignment across five representations:

- **Outcome (O)**: What business value we deliver
- **Specification (S)**: What technical requirements we satisfy
- **Test (T)**: How we verify correctness
- **Code (C)**: What actually runs
- **Constraint (X)**: What system-wide properties we enforce

**The Core Insight:**

Intent (OSTC) is **positional** - it describes where we are now.
Deltas are **vectorial** - they describe how we got here.
Constraints are **predicates** - they describe what must hold everywhere.

**The Fundamental Separation:**

OSTC forms a **hierarchical graph** (nearly decomposable):
- Dense connections within subsystems (high cohesion)
- Sparse connections between subsystems (low coupling)
- Measurable with coupling ratios (10:1 target)
- **Subsystems can nest** for hierarchical organization (e.g., `crdt.ser`, `crdt.sync`)

X forms a **query layer** over the OSTC graph:
- Cross-cutting by nature (spans subsystems)
- Defined by scope selectors, not edges
- Validated through predicate evaluation
- Does not corrupt decomposability metrics
- Can target subsystem hierarchies (e.g., all nodes under `crdt`)

**Why This Matters:**

Real systems have cross-cutting concerns (security, performance, compliance). Traditional approaches either:
1. Model them as graph nodes → destroys modularity metrics
2. Ignore them → loses critical system properties

JIG v7 solves this by recognizing constraints as a **different category** - not nodes in the intent flow, but **properties of the system** that must be validated across nodes.

**The Git-Native Approach:**

Like git objects, JIG artifacts are:
- Plain text (grep-able, diff-able, merge-able)
- Content-addressed (immutable truth)
- Distributed (no central database)
- Fast (scan entire project in <1 second)

**The Promise:**

Nearly decomposable systems naturally exhibit sparse inter-module coupling with dense intra-module cohesion. JIG makes this structure visible, measurable, and maintainable while:
- Harvesting insights from temporal work artifacts into timeless Intent
- Tracking cross-cutting constraints without destroying architectural boundaries
- Enabling hierarchical subsystem organization that scales from small projects to large systems
- Supporting both coarse-grained (parent subsystem) and fine-grained (leaf subsystem) analysis

---

## 1. The OSTCX Model

### 1.1 Five Representations of Truth

| Element           | Truth Type               | Graph Role     | Lifecycle | Storage                      |
| ----------------- | ------------------------ | -------------- | --------- | ---------------------------- |
| **Outcome**       | Narrative truth (why)    | Node           | Timeless  | `jig/outcomes/O-*.md`       |
| **Specification** | Logical truth (what)     | Node           | Timeless  | `jig/specifications/S-*.md` |
| **Test**          | Empirical truth (verify) | Node           | Timeless  | Annotated with `@jig`        |
| **Code**          | Operational truth (how)  | Node           | Timeless  | Annotated with `@jig`        |
| **Constraint**    | System property (must)   | **Predicate**  | Timeless  | `jig/constraints/X-*.md`    |

**Critical Distinction:**

- **OSTC**: Nodes in the Intent Graph (hierarchical, decomposable)
- **X**: Predicates over the Intent Graph (cross-cutting, query-based)

**Why Separate?**

Cross-cutting constraints, if modeled as graph nodes, create edges that:
- Destroy coupling ratio metrics (10:1 → 1:10)
- Obscure subsystem boundaries
- Collapse modularity scores
- Make graph visualizations unreadable

Constraints as predicates preserve architectural integrity while tracking system-wide properties.

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

### 1.3 Reality Annotations (T, C)

**Test annotation:**

```python
# test_auth.py

# @jig T-AUTH-001 verifies:S-AUTH-001 subsystem:auth satisfies:X-SEC-001
def test_jwt_token_validation():
    """Verify JWT tokens validate correctly with device ID"""
    token = create_token(device_id="device-123")
    claims = authenticator.validate_token(token)
    assert claims.device_id == "device-123"
    assert claims.expiration > now()
```

**Code annotation:**

```python
# auth.py

# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:identity.auth interface:public satisfies:X-SEC-001,X-PERF-001
class JWTAuthenticator:
    """Handles JWT-based multi-device authentication"""

    # @jig C-AUTH-002 implements:S-AUTH-001,S-AUTH-002 subsystem:identity.auth satisfies:X-SEC-001
    def validate_token(self, token: str) -> Claims:
        """Validates JWT and extracts claims"""
        # ... implementation ...

# crdt/serialization.py

# @jig C-CRDT-SER-001 implements:S-CRDT-SER-001 subsystem:crdt.ser interface:public
class CRDTSerializer:
    """Handles CRDT serialization to protobuf"""
    # ... implementation ...
```

**Annotation rules:**
- One line, inline comment
- Pattern: `@jig {id} {relations} {metadata}`
- Test relations: `verifies:S-001` `verifies:O-001`
- Code relations: `implements:S-001` `depends:C-002`
- Metadata: `subsystem:auth interface:public`
- **New in v7**: `satisfies:X-001` links to constraints

### 1.4 Constraint Documents (X)

**Constraint example:**

```yaml
---
id: X-HIPAA-001
type: constraint
title: "HIPAA: Encrypt all PHI at rest and in transit"
category: compliance
severity: critical
created: 2025-11-20
---

# Constraint: HIPAA PHI Encryption

All personally identifiable health information (PHI) must be encrypted:
- At rest: AES-256 or stronger
- In transit: TLS 1.3 or stronger
- Keys: Managed in secure keychain, rotated quarterly

## Scope

This constraint applies to all code and specifications that handle PHI.

```yaml
scope:
  subsystems: [auth, storage, api, sync]
  node_types: [S, C, T]
  query: "tag:handles-phi OR subsystem:storage OR interface:public"
```

## Verification Strategy

- All S nodes matching scope must specify encryption method
- All C nodes handling PHI must use approved encryption libraries
- All T nodes must verify encryption is active and correct

## Satisfied By

**Specifications:**
- S-AUTH-ENCRYPTION-001 (JWT encryption with AES-256)
- S-STORAGE-AES256-001 (Database encryption at rest)
- S-API-TLS-001 (API transport security)

**Code:**
- C-AUTH-001 (uses `cryptography` library)
- C-STORAGE-001 (uses SQLCipher)
- C-API-001 (enforces TLS 1.3)

## Verified By

**Tests:**
- T-AUTH-ENCRYPT-001 (validates JWT encryption)
- T-STORAGE-ENCRYPT-001 (validates database encryption)
- T-API-TLS-001 (validates TLS handshake)

## Compliance Status

Last validated: 2025-11-20
Status: 95% compliant (22/23 nodes)
Violations:
- S-API-SESSION-001 missing encryption specification

## References

- Regulation: 45 CFR § 164.312(a)(2)(iv)
- Internal policy: SEC-POL-001
```

**Key properties:**

- **scope**: Query selector defining which nodes this constraint applies to
- **satisfied_by**: OSTC nodes that implement this constraint
- **verified_by**: Test nodes that validate compliance
- **Not a graph node**: No edges to/from constraints in the OSTC graph
- **Query-based**: Constraint evaluator matches nodes dynamically

---

## 2. Constraints as Predicates: The Graph Theory

### 2.1 The Architectural Tension

**JIG's foundational principle** (Herbert Simon): Nearly decomposable systems have:
- **Dense** connections within subsystems (high cohesion)
- **Sparse** connections between subsystems (low coupling)
- Target: 10:1 coupling ratio (internal:external edges)

**Constraints are cross-cutting:**
- Apply across multiple subsystems
- Create connections between otherwise independent modules
- Cannot be decomposed

**The Problem:**

If constraints are graph nodes with edges:

```
X-HIPAA
├→ S-AUTH-001 (subsystem: auth)
├→ S-STORAGE-001 (subsystem: storage)  ← Creates external edge
├→ S-API-001 (subsystem: api)          ← Creates external edge
└→ C-ENCRYPT-001 (subsystem: crypto)   ← Creates external edge
```

**Impact:**
- Every constraint creates N cross-subsystem edges
- Coupling ratio becomes meaningless (10:1 → 1:10)
- Modularity score collapses
- Subsystem boundaries obscured
- Graph visualization becomes spaghetti

### 2.2 The Solution: Query-Based Constraints

**Constraints are predicates, not nodes.**

Like how:
- Git commits are nodes; "this branch is protected" is a rule about commits
- Filesystem has files/directories (nodes); "files >1GB not allowed" is a policy

```
OSTC Graph (hierarchical, decomposable):
┌────────────────┐    ┌────────────────┐
│ Subsystem:auth │    │Subsystem:storage│
│ S-AUTH-001     │    │ S-STORAGE-001  │
│   ↓            │    │   ↓            │
│ C-AUTH-001     │    │ C-STORAGE-001  │
└────────────────┘    └────────────────┘
Coupling: 12:1 ✓      Coupling: 15:1 ✓

Constraint Layer (query-based, non-invasive):
X-HIPAA-001.query("tag:handles-phi") → [S-AUTH-001, S-STORAGE-001, ...]
                                        ↑
                                   No edges added
```

**Graph structure remains clean. Constraints query it.**

### 2.3 Query Selectors

**Simple selector:**

```yaml
scope:
  subsystems: [identity.auth, storage]
  node_types: [S, C]
```

**Hierarchical selector (all nodes under parent):**

```yaml
scope:
  subsystems: [identity]  # Matches identity.auth, identity.user, etc.
  recursive: true
  node_types: [S, C]
```

**Complex selector:**

```yaml
scope:
  query: "type:S AND (subsystem:identity.auth OR tag:security) AND NOT tag:legacy"
```

**Tag-based selector:**

```yaml
scope:
  tags: [handles-phi, public-api]
  node_types: [S, C, T]
```

**Nested subsystem examples:**

```yaml
# Apply to specific leaf subsystem
scope:
  subsystems: [crdt.ser]

# Apply to all subsystems under parent
scope:
  subsystems: [crdt]
  recursive: true  # Includes crdt.ser, crdt.sync, etc.

# Mix parent and leaf subsystems
scope:
  subsystems: [identity, storage, crdt.sync]
  # identity is recursive (all children), crdt.sync is specific
```

**Query language:**
- Boolean operators: AND, OR, NOT
- Selectors: `type:`, `subsystem:`, `tag:`, `interface:`
- Subsystem matching: `subsystem:crdt` (exact) or `subsystem:crdt.*` (wildcard for children)
- Matches against node metadata in graph index

### 2.4 Benefits of Query-Based Constraints

**✅ Preserves Decomposability**
- No cross-subsystem edges from constraints
- Coupling ratio remains meaningful (10:1 target valid)
- Subsystem detection algorithms unaffected
- Modularity metrics accurate

**✅ Represents Cross-Cutting Nature Correctly**
- Constraints **query** the graph, don't **mutate** it
- Scope is explicit (subsystem selector)
- Matches conceptual model (constraints are "about" the system)

**✅ Scales Gracefully**
- Adding constraint doesn't add N edges
- Query evaluation is on-demand
- New nodes automatically picked up by existing constraints

**✅ Enables Flexible Constraint Management**
- Dynamic scope (query matches new nodes)
- Conditional constraints (based on tags)
- Layered constraints (security, performance, compliance)

**✅ Maintains Traceability**
- Forward: X → {nodes it constrains}
- Reverse: node → {constraints that apply}
- Validation: X → {satisfied_by, verified_by}

---

## 3. Nearly Decomposable Systems

### 3.1 The Architectural Constraint

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

**Note:** These metrics apply to the **OSTC graph only**. Constraints are excluded from coupling calculations, as they represent system properties, not architectural dependencies.

### 3.2 Subsystem Detection

```bash
# Auto-detect subsystem boundaries
jig decompose --detect

# Output: Clusters with coupling metrics
Subsystem: auth (2.3k LOC, 3 exports)
├─ Internal edges: 47
├─ External edges: 4
├─ Coupling ratio: 11.8:1 ✓
├─ Modularity: 0.89 ✓
└─ Constrained by: X-HIPAA-001, X-SEC-001

Subsystem: crdt (4.1k LOC, 7 exports)
├─ Internal edges: 89
├─ External edges: 12
├─ Coupling ratio: 7.4:1 ⚠
├─ Modularity: 0.73 ✓
└─ Constrained by: X-PERF-001
```

### 3.3 Subsystem Annotation

```python
# @jig C-001 implements:S-001 subsystem:identity.auth interface:public satisfies:X-SEC-001
def authenticate(user: str, password: str) -> Token:
    """Public authentication API"""

# @jig C-002 implements:S-002 subsystem:identity.auth depends:crypto satisfies:X-HIPAA-001
def _hash_password(password: str) -> bytes:
    """Internal helper, depends on crypto subsystem"""

# @jig C-003 implements:S-003 subsystem:crdt.ser interface:public
def serialize_crdt(crdt: CRDT) -> bytes:
    """Serialize CRDT to protobuf - public interface of crdt.ser subsystem"""
```

**Key:**
- `interface:public` = exported, part of subsystem boundary
- `depends:X` = cross-subsystem dependency (keep these minimal)
- `satisfies:X-001` = satisfies constraint (not counted in coupling)
- Subsystem names use **dot notation** for nesting (e.g., `identity.auth`, `crdt.ser`)
- Subsystem paths map to package/module structure

### 3.4 Nested Subsystems

**Why Nest?**

Large systems with 20+ subsystems become hard to navigate with flat structure. Nesting enables:
- **Logical grouping**: Group related subsystems (e.g., `crdt.ser`, `crdt.sync` under `crdt`)
- **Scalable organization**: Manage complexity as projects grow
- **Hierarchical analysis**: Analyze entire parent subsystem or individual children
- **Flexible granularity**: Both coarse-grained and fine-grained metrics

**Example Hierarchy:**

```
identity/               # Parent subsystem
├─ auth/                # Child: identity.auth
│  ├─ jwt.py           # subsystem:identity.auth
│  └─ oauth.py         # subsystem:identity.auth
└─ user/                # Child: identity.user
   ├─ profile.py        # subsystem:identity.user
   └─ permissions.py    # subsystem:identity.user

crdt/                   # Parent subsystem
├─ ser/                 # Child: crdt.ser
│  └─ protobuf.py      # subsystem:crdt.ser
└─ sync/                # Child: crdt.sync
   └─ protocol.py      # subsystem:crdt.sync
```

**Subsystem Definition:**

```yaml
# jig/subsystems.yaml
subsystems:
  identity:
    name: identity
    description: "Identity and access management"
    subsystems:
      auth:
        name: auth
        description: "Authentication (JWT, OAuth)"
        max_exports: 5
        allowed_dependencies: [crypto]
      user:
        name: user
        description: "User profiles and permissions"
        max_exports: 3
        allowed_dependencies: [identity.auth, storage]

  crdt:
    name: crdt
    description: "CRDT implementation"
    subsystems:
      ser:
        name: ser
        description: "CRDT serialization"
        max_exports: 2
      sync:
        name: sync
        description: "CRDT synchronization"
        max_exports: 3
        allowed_dependencies: [crdt.ser, network]
```

**Key Rules:**

1. **Nodes belong to leaf subsystems only**: Parent subsystems with children cannot have nodes directly
2. **Fully-qualified paths**: Nodes reference `subsystem: crdt.ser`, not just `ser`
3. **Local uniqueness**: Subsystem names unique within parent (can have both `identity.api` and `crdt.api`)
4. **Arbitrary depth**: Nesting depth unlimited (recommended max 3-4 levels)
5. **Backward compatible**: Flat subsystems (no children) continue to work unchanged

**Hierarchical Metrics:**

```bash
jig decompose --metrics

# Output:
Subsystem: identity (coupling: 12.5:1 ✓)
├─ identity.auth (coupling: 14.2:1 ✓)
├─ identity.user (coupling: 10.8:1 ✓)

Subsystem: crdt (coupling: 18.3:1 ✓)
├─ crdt.ser (coupling: 22.1:1 ✓)
├─ crdt.sync (coupling: 14.5:1 ✓)

# Parent metrics aggregate children
# Edges within parent subsystem counted as internal
# Edges between parents counted as external
```

**Querying Hierarchies:**

```bash
# List all nodes in crdt (recursive)
jig graph list --subsystem crdt

# List only crdt.ser nodes
jig graph list --subsystem crdt.ser

# Analyze crdt subsystem tree
jig decompose --metrics --subsystem crdt

# Validate entire hierarchy
jig validate --check-all
```

---

## 4. Deltas: Temporal Work Artifacts

### 4.1 What Are Deltas?

**Deltas** are working documents tied to git branches. They capture the narrative of change.

| Aspect | Intent (OSTC) | Deltas | Constraints (X) |
|--------|---------------|--------|-----------------|
| **Time** | Present state | Past→Future journey | Timeless properties |
| **Purpose** | What/Why/How | The story of change | System-wide rules |
| **Truth** | Resolved | Options, failures, decisions | Must hold |
| **Lifecycle** | Permanent | Branch-scoped | Permanent |
| **Location** | `jig/` | `jig/deltas/{branch}/` | `jig/constraints/` |

### 4.2 Delta Types

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

### 4.3 Delta Lifecycle = Git Workflow

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

## 5. Harvest & Distill: From Deltas to Intent

### 5.1 The Pipeline (Three Phases)

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   EXTRACT    │───>│  SYNTHESIZE  │───>│  INTEGRATE   │
│ deterministic│    │  LLM-assisted│    │human-approved│
│   <1 sec     │    │   30-60 sec  │    │   <1 sec     │
└──────────────┘    └──────────────┘    └──────────────┘
```

**Phase 1: EXTRACT** (deterministic, grep-speed)
- Scan deltas for markers: `#DISCOVERY`, `#LEARNED`, `#DECISION`, `#CONSTRAINT`
- Output: harvest report (YAML)
- Zero false negatives

**Phase 2: SYNTHESIZE** (LLM, optional)
- Understand context, elevate abstraction
- Categorize into OSTCX types (O/S/T/C/X)
- Detect patterns, conflicts
- Output: synthesis proposal (YAML)

**Phase 3: INTEGRATE** (human-approved)
- Review proposal
- Create/update jig/ files
- Add traceability links
- Run validation

### 5.2 Marker Syntax (Simple, Inline)

```markdown
# In jig/deltas/active/feature-x/PLAN.md

We tried threading first, but hit the GIL bottleneck.

#DISCOVERY "Multi-process required for true parallelism"
#RELATES O-PERF-001

Then tried shared memory for GUI updates.

#LEARNED "GUI widgets can't cross process boundaries"
#DECISION "Use WebSocket for inter-process communication"

#CONSTRAINT "All API responses must complete in <1 second"
#SUGGESTS X-PERF-001
```

**Marker pattern:**
```
#{TYPE} "one-line summary"
#RELATES node-id
#SUGGESTS X-id
```

**Types:**
- `#DISCOVERY` - found something new (requirement, constraint)
- `#LEARNED` - gained knowledge (pattern, anti-pattern)
- `#DECISION` - chose A over B (rationale required)
- `#CONSTRAINT` - discovered cross-cutting requirement (**new in v7**)
- `#RELATES` - links to OSTC node
- `#SUGGESTS` - suggests constraint node (**new in v7**)

### 5.3 Extraction (Plumbing)

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

  - type: CONSTRAINT
    text: "All API responses must complete in <1 second"
    file: jig/deltas/active/feature-x/PLAN.md
    line: 35
    suggests: [X-PERF-001]
```

### 5.4 Synthesis (Porcelain, Optional)

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

  - id: X-PERF-001
    type: constraint
    title: "API response time <1 second"
    category: performance
    scope:
      subsystems: [api, sync, storage]
      node_types: [S, C]
      query: "interface:public AND type:C"
    content: |
      All public API endpoints must respond in <1 second at p99.
```

### 5.5 Integration (Human Gate)

```bash
# Review and integrate
jig integrate --proposal synthesis-proposal.yaml --review

# Interactive TUI:
# [1/5] New node: S-IPC-001
# Title: Inter-process communication uses WebSocket
# [A]pprove [E]dit [S]kip [Q]uit
# > a

# [2/5] New constraint: X-PERF-001
# Title: API response time <1 second
# Scope: 23 nodes in [api, sync, storage]
# [A]pprove [E]dit [S]kip [Q]uit
# > a

# Approved: creates jig/specifications/S-IPC-001.md
# Approved: creates jig/constraints/X-PERF-001.md
# Updates graph index
# Updates constraint index
```

---

## 6. Constraint Validation & Traceability

### 6.1 Constraint Validation

```bash
# Validate all constraints
jig validate --constraints

# Output:
Validating X-HIPAA-001 (HIPAA PHI Encryption)...
  Scope: 23 nodes across [auth, storage, api, sync]
  ✓ S-AUTH-ENCRYPTION specifies AES-256
  ✓ C-AUTH-001 uses approved crypto library
  ✓ T-AUTH-ENCRYPT-001 validates encryption
  ✗ S-API-SESSION missing encryption specification

  Status: 95% compliant (22/23 nodes)

Validating X-PERF-001 (API response time <1s)...
  Scope: 18 nodes across [api, sync, storage]
  ✓ All C nodes have performance tests
  ✓ All T nodes validate <1s requirement

  Status: 100% compliant (18/18 nodes)

Overall: 2 constraints, 1 violation
```

**Validation algorithm:**

1. For each constraint:
   - Evaluate scope query → get matching nodes
   - Check satisfaction criteria (nodes in `satisfied_by`)
   - Check verification criteria (nodes in `verified_by`)
   - Report violations

2. Optionally use LLM for semantic validation:
   ```bash
   jig ai-validate --constraint X-HIPAA-001
   # Uses LLM to check if S/C/T nodes actually satisfy constraint
   ```

### 6.2 Traceability

**Forward tracing (constraint → nodes):**

```bash
jig trace X-HIPAA-001

Constraint: X-HIPAA-001 (HIPAA PHI Encryption)
├─ Scope: 23 nodes in [auth, storage, api, sync]
├─ Satisfied by:
│  ├─ S-AUTH-ENCRYPTION
│  ├─ S-STORAGE-AES256
│  └─ S-API-TLS
├─ Verified by:
│  ├─ T-AUTH-ENCRYPT-001
│  └─ T-STORAGE-ENCRYPT-001
└─ Compliance: 95% (22/23 nodes)
```

**Reverse tracing (node → constraints):**

```bash
jig trace S-AUTH-001 --constraints

Specification: S-AUTH-001
├─ Constrained by:
│  ├─ X-HIPAA-001 (HIPAA compliance)
│  ├─ X-PERF-001 (API response time)
│  └─ X-SEC-001 (JWT token requirements)
├─ Compliance status: 100%
└─ Related tests:
   ├─ T-AUTH-001 (verifies S-AUTH-001, satisfies X-SEC-001)
   └─ T-AUTH-PERF-001 (verifies X-PERF-001)
```

**Graph visualization with constraint overlay:**

```bash
jig graph --show-constraints X-HIPAA-001

# Renders OSTC graph
# Highlights nodes matching X-HIPAA-001 scope
# Shows satisfaction status (green = satisfied, red = violated)
```

### 6.3 Constraint Index

```yaml
# jig/constraint-index.yaml (auto-generated)

constraints:
  X-HIPAA-001:
    file: jig/constraints/X-HIPAA-001.md
    type: constraint
    category: compliance
    severity: critical
    scope_nodes: [S-AUTH-001, S-STORAGE-001, C-AUTH-001, ...] # 23 nodes
    satisfied_by: [S-AUTH-ENCRYPTION, S-STORAGE-AES256, S-API-TLS]
    verified_by: [T-AUTH-ENCRYPT-001, T-STORAGE-ENCRYPT-001]
    compliance: 0.95
    last_validated: 2025-11-20

  X-PERF-001:
    file: jig/constraints/X-PERF-001.md
    type: constraint
    category: performance
    severity: high
    scope_nodes: [C-API-001, C-SYNC-001, ...]  # 18 nodes
    satisfied_by: [S-API-PERF, S-SYNC-PERF]
    verified_by: [T-API-PERF-001, T-SYNC-PERF-001]
    compliance: 1.0
    last_validated: 2025-11-20

# Rebuilt with: jig index --rebuild
```

---

## 7. Tool Design Philosophy: Git as Lodestar

### 7.1 What Would Linus Do?

**Git principles applied to JIG:**

| Git Principle | JIG Application |
|--------------|--------------------|
| **Fast** | Scan 10k files in <1 sec (like git status) |
| **Text-based** | All files .md or .yaml (like git objects) |
| **Distributed** | No database, just files (like git repo) |
| **Content-addressed** | Nodes by ID, immutable (like git SHA) |
| **Plumbing vs porcelain** | Core tools + convenience wrappers |
| **Trust developer** | Sharp tools, require skill (like rebase) |
| **Explicit** | No magic, no hidden state |

### 7.2 Plumbing vs Porcelain

**Plumbing (core, deterministic, fast):**
```bash
jig extract           # Find markers (grep-speed)
jig validate          # Check graph consistency
jig validate --constraints  # Check constraint compliance
jig graph             # Generate graph data
jig decompose         # Calculate metrics
jig integrate         # Apply approved changes to jig/
jig constraint check  # Validate specific constraint
```

**Porcelain (convenience, may use LLM):**
```bash
jig ai-synthesize     # LLM-assisted OSTCX proposal
jig ai-validate       # LLM-assisted constraint validation
jig ai-integrate      # Interactive integration with AI assistance
jig ai-distill        # Full pipeline: extract → synthesize → integrate
```

**Naming convention:** Any command that calls an LLM has `ai-` prefix. This makes API usage explicit and cost-transparent.

**You can use JIG without AI.** Plumbing is self-contained.

### 7.3 Speed Targets

```
jig extract              <1 second  (10k files)
jig validate             <1 second  (1k nodes)
jig validate --constraints  <2 seconds (1k nodes, 50 constraints)
jig graph                <2 seconds (1k nodes, 5k edges)
jig decompose            <3 seconds (complex analysis)
jig constraint check     <1 second  (single constraint)
jig ai-synthesize        30-60 sec  (LLM call)
jig ai-validate          10-30 sec  (LLM call per constraint)
```

### 7.4 File Format Constraints

**All human-readable text:**
- OSTC nodes: Markdown with YAML frontmatter
- Constraint nodes: Markdown with YAML frontmatter
- Graph index: YAML
- Constraint index: YAML
- Harvest reports: YAML
- Deltas: Markdown
- Config: TOML (like git config)

**Why?**
- Standard tools work (grep, sed, diff, merge)
- No special viewers needed
- Merge conflicts visible
- Human-readable diffs in PR

---

## 8. Decomposability Analysis

### 8.1 Core Metrics

```bash
jig decompose --metrics

# Output
Overall Decomposability: 78% ✓

Subsystems: 5 (3 with nesting)
├─ identity  (88% healthy, 12.5:1 coupling) ✓
│  ├─ identity.auth (92% healthy, 14.2:1 coupling)
│  │  └─ Constrained by: X-HIPAA-001 (95%), X-SEC-001 (100%)
│  └─ identity.user (84% healthy, 10.8:1 coupling)
│     └─ Constrained by: X-HIPAA-001 (100%)
├─ crdt      (81% healthy, 18.3:1 coupling) ✓
│  ├─ crdt.ser (85% healthy, 22.1:1 coupling)
│  │  └─ Constrained by: X-PERF-001 (100%)
│  └─ crdt.sync (77% healthy, 14.5:1 coupling)
│     └─ Constrained by: X-PERF-001 (88%)
├─ gui       (81% healthy, 9.2:1 coupling)
│  └─ Constrained by: X-PERF-001 (88%)
├─ network   (67% healthy, 5.8:1 coupling) ⚠
│  └─ Constrained by: X-PERF-001 (100%), X-SEC-001 (100%)
└─ storage   (94% healthy, 15.2:1 coupling)
   └─ Constrained by: X-HIPAA-001 (100%), X-PERF-001 (100%)

Hierarchical Metrics:
- Parent subsystems aggregate child metrics
- Edges within parent counted as internal
- Edges between parents counted as external
- identity: 15 internal edges, 2 external → 7.5:1 (before nesting was 3:1)
- crdt: 32 internal edges, 3 external → 10.7:1 (before nesting was 4:1)

Issues:
1. network subsystem below 10:1 coupling target
2. X-HIPAA-001 compliance at 95% (identity.auth subsystem violation)
```

**Analyzing Subsystem Trees:**

```bash
# Analyze just the identity subsystem and its children
jig decompose --metrics --subsystem identity

# Output:
Subsystem: identity (88% healthy, 12.5:1 coupling)

Child Subsystems: 2
├─ identity.auth (23 nodes, 42 internal, 3 external, 14.2:1 coupling)
└─ identity.user (18 nodes, 28 internal, 2 external, 10.8:1 coupling)

Cross-Child Edges: 4 (auth → user dependencies)
External Edges: 2 (identity → crypto, identity → storage)

Parent Metrics:
- Total nodes: 41
- Internal edges (within identity): 74  # Includes cross-child edges
- External edges (to other subsystems): 2
- Coupling ratio: 37:1 ✓ (excellent)

Constraints:
- X-HIPAA-001: 95% compliant (1 violation in identity.auth)
- X-SEC-001: 100% compliant
```

**Note:**
- Coupling ratio excludes constraint relationships (constraints are system properties, not architectural dependencies)
- Hierarchical coupling: edges between children of same parent counted as internal to parent
- This enables refactoring subsystems into hierarchies without breaking decomposability metrics

### 8.2 Enforcement

```toml
# jig/config.toml

[decomposability]
min_coupling_ratio = 10.0
min_modularity = 0.5
max_subsystem_size = 10000
max_nesting_depth = 4  # Warn if subsystems nested deeper than 4 levels

# Flat subsystem configuration (backward compatible)
[subsystems.storage]
max_exports = 8
allowed_dependencies = ["core"]

# Nested subsystem configuration
[subsystems."identity.auth"]
max_exports = 5
allowed_dependencies = ["crypto", "core"]

[subsystems."identity.user"]
max_exports = 3
allowed_dependencies = ["identity.auth", "storage"]

[subsystems."crdt.ser"]
max_exports = 2
allowed_dependencies = ["core"]

[subsystems."crdt.sync"]
max_exports = 3
allowed_dependencies = ["crdt.ser", "network"]

[constraints]
enforce_in_ci = true
min_compliance = 0.95  # Fail CI if <95% compliant
critical_constraints = ["X-HIPAA-001", "X-SEC-001"]  # Must be 100%
```

```bash
# CI/CD gate
jig decompose --validate --strict

# Fails if:
# - Coupling ratio < 10:1
# - Modularity < 0.5
# - Subsystem exceeds size limit
# - Forbidden dependency added
# - Constraint compliance < 95%
# - Critical constraint < 100%
```

---

## 9. Practical Workflows

### 9.1 Starting New Work

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

### 9.2 Capturing Discoveries (During Work)

```bash
# While coding, add markers to PLAN.md
echo "" >> jig/deltas/active/feature-multiprocess/PLAN.md
echo "#DISCOVERY \"Process isolation solves GIL bottleneck\"" >> jig/deltas/active/feature-multiprocess/PLAN.md
echo "#RELATES O-PERF-001" >> jig/deltas/active/feature-multiprocess/PLAN.md
echo "" >> jig/deltas/active/feature-multiprocess/PLAN.md
echo "#CONSTRAINT \"All IPC messages must complete in <100ms\"" >> jig/deltas/active/feature-multiprocess/PLAN.md
echo "#SUGGESTS X-PERF-IPC" >> jig/deltas/active/feature-multiprocess/PLAN.md

# Commit alongside code changes
git add jig/deltas/ src/
git commit -m "WU1: Process launcher

See: jig/deltas/active/feature-multiprocess/PLAN.md:L23"
```

### 9.3 Harvest Before Merge

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

## Constraints Discovered
#CONSTRAINT "IPC latency must be <100ms for responsive UI"
#SUGGESTS X-PERF-IPC
EOF

# Extract markers
jig extract --branch feature-multiprocess --output harvest.yaml

# (Optional) LLM synthesis
jig ai-synthesize --harvest harvest.yaml --output synthesis.yaml

# Review and integrate (human approval)
jig integrate --proposal synthesis.yaml --review

# Approve creates:
# - jig/specifications/S-IPC-001.md
# - jig/constraints/X-PERF-IPC.md (new constraint)
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

### 9.4 Validate Alignment

```bash
# Check OSTC graph consistency
jig validate --check-all

# Checks:
# ✓ All @jig annotations reference valid nodes
# ✓ All OSTC relations exist
# ✓ No orphaned nodes
# ✗ S-IPC-001 missing test reference (warning)

# Check constraints
jig validate --constraints

# ✓ X-HIPAA-001: 95% compliant (1 violation)
# ✓ X-PERF-001: 100% compliant
# ✓ X-PERF-IPC: 100% compliant (newly added)

# Check decomposability
jig decompose --validate

# ✓ All subsystems meet coupling ratio target
# ✓ Modularity score: 0.72 (above 0.5)
# ⚠ network subsystem has 8.1:1 coupling (target: 10:1)
```

### 9.5 Managing Constraints

```bash
# List all constraints
jig constraint list

# Output:
# X-HIPAA-001 [compliance/critical] - HIPAA PHI Encryption (95%)
# X-PERF-001  [performance/high]    - API response time <1s (100%)
# X-PERF-IPC  [performance/medium]  - IPC latency <100ms (100%)
# X-SEC-001   [security/critical]   - JWT token requirements (100%)

# Check specific constraint
jig constraint check X-HIPAA-001

# Scope: 23 nodes
# Compliant: 22 nodes
# Violations:
#   - S-API-SESSION (missing encryption specification)

# Trace constraint impact
jig trace X-HIPAA-001

# Show nodes affected by constraint
jig graph --constraint X-HIPAA-001

# Fix violation: add encryption spec to S-API-SESSION
# Then re-validate
jig validate --constraints
# ✓ X-HIPAA-001: 100% compliant
```

---

## 10. Data Model

### 10.1 Directory Structure

```
jig/
├─ config.toml                 # Project configuration
├─ graph-index.yaml           # Node and edge registry
├─ constraint-index.yaml      # Constraint registry (new in v7)
├─ outcomes/
│  ├─ O-PERF-001.md           # Business outcomes
│  └─ O-AUTH-001.md
├─ specifications/
│  ├─ S-IPC-001.md            # Technical requirements
│  └─ S-AUTH-001.md
├─ constraints/               # System-wide properties (new in v7)
│  ├─ X-HIPAA-001.md          # Compliance constraints
│  ├─ X-PERF-001.md           # Performance constraints
│  └─ X-SEC-001.md            # Security constraints
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

### 10.2 Graph Index (Fast Lookups)

```yaml
# jig/graph-index.yaml

nodes:
  O-AUTH-001:
    file: jig/outcomes/O-AUTH-001.md
    type: outcome
    subsystem: identity.auth  # Nested subsystem path
    constraints: [X-HIPAA-001, X-SEC-001]

  S-AUTH-001:
    file: jig/specifications/S-AUTH-001.md
    type: specification
    subsystem: identity.auth
    constraints: [X-HIPAA-001, X-SEC-001]

  C-AUTH-001:
    file: src/identity/auth/jwt.py
    line: 23
    type: code
    subsystem: identity.auth
    interface: public
    constraints: [X-HIPAA-001, X-SEC-001, X-PERF-001]

  O-CRDT-SER-001:
    file: jig/outcomes/O-CRDT-SER-001.md
    type: outcome
    subsystem: crdt.ser  # Nested subsystem path
    constraints: [X-PERF-001]

  S-CRDT-SER-001:
    file: jig/specifications/S-CRDT-SER-001.md
    type: specification
    subsystem: crdt.ser
    constraints: [X-PERF-001]

  C-CRDT-SER-001:
    file: src/crdt/ser/protobuf.py
    line: 15
    type: code
    subsystem: crdt.ser
    interface: public
    constraints: [X-PERF-001]

edges:
  - from: S-AUTH-001
    to: O-AUTH-001
    type: implements

  - from: C-AUTH-001
    to: S-AUTH-001
    type: implements

  - from: S-CRDT-SER-001
    to: O-CRDT-SER-001
    type: implements

  - from: C-CRDT-SER-001
    to: S-CRDT-SER-001
    type: implements

subsystems:
  # Hierarchical subsystem structure
  identity:
    # Parent subsystem - no direct nodes
    subsystems:
      auth:
        nodes: [O-AUTH-001, S-AUTH-001, C-AUTH-001, T-AUTH-001, ...]
        internal_edges: 42
        external_edges: 3
        coupling_ratio: 14.0
        constraints: [X-HIPAA-001, X-SEC-001]
      user:
        nodes: [O-USER-001, S-USER-001, C-USER-001, ...]
        internal_edges: 28
        external_edges: 2
        coupling_ratio: 14.0
        constraints: [X-HIPAA-001]
    # Parent aggregated metrics
    total_nodes: 41
    internal_edges: 74  # Includes cross-child edges (auth → user)
    external_edges: 2   # Only edges to outside identity
    coupling_ratio: 37.0

  crdt:
    subsystems:
      ser:
        nodes: [O-CRDT-SER-001, S-CRDT-SER-001, C-CRDT-SER-001, ...]
        internal_edges: 35
        external_edges: 1
        coupling_ratio: 35.0
        constraints: [X-PERF-001]
      sync:
        nodes: [O-CRDT-SYNC-001, S-CRDT-SYNC-001, ...]
        internal_edges: 28
        external_edges: 3
        coupling_ratio: 9.3
        constraints: [X-PERF-001]
    total_nodes: 32
    internal_edges: 67  # Includes ser ↔ sync edges
    external_edges: 2
    coupling_ratio: 33.5

  # Flat subsystem (backward compatible)
  storage:
    nodes: [O-STORAGE-001, S-STORAGE-001, C-STORAGE-001, ...]
    internal_edges: 52
    external_edges: 4
    coupling_ratio: 13.0
    constraints: [X-HIPAA-001, X-PERF-001]

# Note: Constraint relationships NOT in edges (they're predicates, not graph edges)
# Note: Nested subsystems use dot notation (identity.auth, crdt.ser)
```

### 10.3 Constraint Index

```yaml
# jig/constraint-index.yaml (auto-generated)

constraints:
  X-HIPAA-001:
    file: jig/constraints/X-HIPAA-001.md
    type: constraint
    category: compliance
    severity: critical
    scope:
      subsystems: [identity, storage]  # identity is recursive (includes identity.auth, identity.user)
      recursive: true
      node_types: [S, C, T]
      query: "tag:handles-phi OR subsystem:storage OR subsystem:identity.*"
    matched_nodes: [S-AUTH-001, S-USER-001, S-STORAGE-001, C-AUTH-001, ...]  # 23 nodes
    satisfied_by: [S-AUTH-ENCRYPTION, S-STORAGE-AES256, S-API-TLS]
    verified_by: [T-AUTH-ENCRYPT-001, T-STORAGE-ENCRYPT-001]
    compliance: 0.95
    violations: [S-API-SESSION]  # in identity.auth
    last_validated: 2025-11-20

  X-PERF-001:
    file: jig/constraints/X-PERF-001.md
    type: constraint
    category: performance
    severity: high
    scope:
      subsystems: [api, sync, storage]
      node_types: [S, C]
      query: "interface:public AND type:C"
    matched_nodes: [C-API-001, C-SYNC-001, ...]  # 18 nodes
    satisfied_by: [S-API-PERF, S-SYNC-PERF]
    verified_by: [T-API-PERF-001, T-SYNC-PERF-001]
    compliance: 1.0
    violations: []
    last_validated: 2025-11-20

  X-PERF-IPC:
    file: jig/constraints/X-PERF-IPC.md
    type: constraint
    category: performance
    severity: medium
    scope:
      subsystems: [ipc]
      node_types: [S, C, T]
    matched_nodes: [S-IPC-001, C-IPC-001, T-IPC-001]
    satisfied_by: [S-IPC-001]
    verified_by: [T-IPC-PERF-001]
    compliance: 1.0
    violations: []
    last_validated: 2025-11-20

# Rebuilt with: jig index --rebuild
# Query evaluation happens during rebuild
```

### 10.4 Traceability Links

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

**Constraint references:**
```yaml
# In jig/constraints/X-PERF-IPC.md frontmatter
---
id: X-PERF-IPC
source_delta: jig/deltas/archive/feature-multiprocess/RETRO.md:67
discovered_in_commit: a7f3c2b
---
```

---

## 11. Implementation Roadmap

### 11.1 Phase 1: Core Plumbing (Weeks 1-2)

**Deliverables:**
- `jig extract` - marker extraction (grep-based)
- `jig validate` - graph consistency checks
- `jig index` - graph index builder
- File format specs finalized

**Success criteria:**
- Extract 1000 markers in <1 second
- Validate 1000 nodes in <1 second
- All output is valid YAML/markdown

### 11.2 Phase 2: Decomposability (Weeks 3-4)

**Deliverables:**
- `jig decompose --detect` - subsystem detection
- `jig decompose --metrics` - coupling/modularity calculation
- `jig decompose --validate` - boundary enforcement
- Graph visualization (Graphviz output)

**Success criteria:**
- Detect subsystems in codebase
- Calculate accurate coupling ratios
- Generate useful visualizations

### 11.3 Phase 3: Harvest Pipeline (Weeks 5-6)

**Deliverables:**
- `jig ai-synthesize` - LLM synthesis (optional)
- `jig integrate` - apply approved synthesis proposals
- `jig ai-integrate` - interactive TUI with AI assistance
- `jig ai-distill` - full pipeline orchestrator
- Marker linting

**Success criteria:**
- Harvest one branch end-to-end
- >80% marker capture rate
- <10 minutes human review time

### 11.4 Phase 4: Constraints (Weeks 7-8) **[New in v7]**

**Deliverables:**
- `jig constraint check` - validate specific constraint
- `jig validate --constraints` - validate all constraints
- `jig trace --constraints` - constraint traceability
- Constraint index builder
- Query evaluator

**Success criteria:**
- Define and validate 5+ constraints
- Query evaluation <1 second
- 100% constraint coverage on test subsystem

### 11.5 Phase 5: Nested Subsystems (Weeks 9-10) **[New in v7]**

**Deliverables:**
- Hierarchical subsystem data model
- Nested subsystem loading from YAML
- Dot notation path resolution (e.g., `crdt.ser`)
- Hierarchical metrics calculation
- Tree view for `jig status`
- Recursive subsystem queries

**Success criteria:**
- Support arbitrary nesting depth (recommended max 4)
- Hierarchical coupling metrics aggregate correctly
- `jig decompose --metrics --subsystem crdt` analyzes subtree
- Backward compatibility with flat subsystems maintained
- Performance: load 100 nested subsystems <100ms

### 11.6 Phase 6: Porcelain & Polish (Weeks 11-12)

**Deliverables:**
- `jig delta new` - delta templates
- `jig delta archive` - automated archival
- `jig graph --interactive` - interactive explorer
- `jig graph --constraint X-001` - constraint overlay visualization
- Documentation and examples

**Success criteria:**
- Complete user guide
- Example project with full OSTCX
- CI/CD integration guide

---

## 12. Metrics & Success Criteria

### 12.1 Tool Performance

| Metric | Target | Why |
|--------|--------|-----|
| Extract speed | <1 sec / 10k files | Git-like responsiveness |
| Validate speed | <1 sec / 1k nodes | No waiting for checks |
| Constraint validation | <2 sec / 50 constraints | Fast CI feedback |
| Graph generation | <2 sec / 1k nodes | Fast iteration |
| Marker capture rate | >85% | Minimize knowledge loss |

### 12.2 Decomposability Health

| Metric | Excellent | Good | Warning | Critical |
|--------|-----------|------|---------|----------|
| Coupling ratio | >15:1 | >10:1 | >5:1 | <5:1 |
| Modularity | >0.7 | >0.5 | >0.3 | <0.3 |
| Module depth | >200:1 | >100:1 | >50:1 | <50:1 |

### 12.3 Constraint Compliance

| Metric | Target | Why |
|--------|--------|-----|
| Overall compliance | >95% | Regulatory safety margin |
| Critical constraints | 100% | Zero tolerance for critical violations |
| Constraint coverage | >80% of code | Most code has relevant constraints |

### 12.4 Adoption Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| Delta completion | 100% branches have deltas | Week 4 |
| Harvest rate | 100% deltas harvested before archive | Week 6 |
| OSTC coverage | >80% code has @jig annotations | Week 8 |
| Constraint definition | >10 constraints defined | Week 8 |
| Subsystem clarity | All code assigned to subsystem | Week 10 |

---

## 13. Design Decisions

### 13.1 Why Plain Text?

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

### 13.2 Why Git-Native Deltas?

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

### 13.3 Why Optional LLM?

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

### 13.4 Why Simple Markers?

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

### 13.5 Why `ai-` Prefix for LLM Commands?

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

### 13.6 Why Visible `jig/` Not Hidden `.jig/`?

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

### 13.7 Why Colocate Deltas in `jig/deltas/`?

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

### 13.8 Why Constraints as Predicates, Not Nodes? **[New in v7]**

**Decision:** Constraints are query-based predicates over the OSTC graph, not nodes in it

**Rationale:**
- **Preserves decomposability**: Cross-cutting constraints would create N×M edges, destroying coupling metrics
- **Correct representation**: Constraints are system properties, not parts of the intent flow
- **Scales gracefully**: New nodes automatically match existing constraint queries
- **Maintains traceability**: Forward/reverse tracing still works via indexes
- **Follows git model**: Like how branches are labels over commits, not commits themselves

**Tradeoff:**
- Less visible in graph visualizations (need overlay mode)
- Two-tier system (OSTC first-class, X second-class)
- More complex validation (query evaluation required)

**Commit:** Constraints as predicates. Cross-cutting concerns belong in a separate layer.

**Why this is fundamental:**

Adding cross-cutting constraints as graph nodes would be like adding linter rules as files in your codebase. They're **about** the code, not **part of** the code. Similarly, constraints are **about** the intent graph, not **part of** the intent graph.

This separation preserves JIG's core value: measuring and maintaining nearly decomposable system architecture.

### 13.9 Why Nested Subsystems? **[New in v7]**

**Decision:** Subsystems can contain child subsystems to arbitrary depth (recommended max 3-4 levels)

**Rationale:**
- **Scalability**: Flat structure becomes unwieldy with 20+ subsystems
- **Natural grouping**: Related subsystems logically grouped (e.g., `identity.auth`, `identity.user`)
- **Hierarchical analysis**: Analyze entire parent or individual children
- **Flexible granularity**: Both coarse and fine-grained decomposability metrics
- **Refactoring enabler**: Can reorganize subsystems without breaking metrics

**Tradeoff:**
- More complex data model (recursive structure)
- Path notation required (`crdt.ser` not just `ser`)
- Potential for over-nesting (mitigated by depth warnings)

**Commit:** Nested subsystems. Hierarchical organization enables scalability.

**Key design choices:**

1. **Nodes only in leaf subsystems**: Parent subsystems with children cannot have nodes directly
   - **Why**: Simplifies metrics (no ambiguity about which level to analyze)
   - **Alternative rejected**: Allow mixed (nodes + children) - too complex

2. **Hierarchical coupling**: Edges between children of same parent counted as internal to parent
   - **Why**: Enables refactoring into hierarchies without degrading metrics
   - **Example**: `identity.auth → identity.user` edge is internal to `identity`, not external

3. **Dot notation for paths**: Use `crdt.ser` not `crdt/ser` or `crdt::ser`
   - **Why**: Common convention (Python modules, Java packages, DNS)
   - **Familiar**: Most developers understand dot notation

4. **Local name uniqueness**: Subsystem names unique within parent, not globally
   - **Why**: Allows natural naming (`identity.api`, `crdt.api` both OK)
   - **Alternative rejected**: Global uniqueness - too restrictive

---

## 14. Comparison to Alternatives

### 14.1 vs Traditional ADRs

| Aspect | Traditional ADRs | JIG |
|--------|-----------------|-----|
| **Scope** | Architectural decisions only | All Intent (O/S/T/C/X) |
| **Structure** | Unstructured markdown | Graph with relationships |
| **Traceability** | Manual links | Bidirectional, enforced |
| **Evolution** | Static documents | Living graph |
| **Tooling** | None (just files) | Analysis, validation, viz |
| **Cross-cutting concerns** | Not addressed | First-class (constraints) |

**When to use ADRs:** Standalone for architectural decisions
**When to use JIG:** Full system Intent with code linkage + constraint tracking

### 14.2 vs Knowledge Graphs

| Aspect | Knowledge Graphs | JIG |
|--------|-----------------|-----|
| **Storage** | Database (Neo4j, etc) | Text files (git-tracked) |
| **Schema** | Formal ontology | Simple OSTCX types |
| **Queries** | Cypher/SPARQL | Grep, YAML parsing, constraint queries |
| **Distribution** | Centralized | Distributed (git) |
| **Setup** | Complex (DB server) | Simple (just files) |

**When to use KG:** Complex ontology, heavy querying
**When to use JIG:** Lightweight, git-native, simple

### 14.3 vs Living Documentation

| Aspect | Living Docs | JIG |
|--------|------------|-----|
| **Source** | Code comments | Code + separate Intent files |
| **Generation** | Automated from code | Manual curation + harvest |
| **Abstraction** | Code-level | Business + technical |
| **Verification** | Tests | OSTC alignment validation + constraint compliance |

**When to use Living Docs:** API documentation
**When to use JIG:** Business intent + architecture + compliance

---

## 15. FAQ

### Q: How is this different from Literate Programming?

**A:** Literate programming embeds code in documentation. JIG separates Intent (timeless) from Code (implementation). Code changes frequently; Intent evolves slowly. Different lifecycles require separation.

### Q: Won't jig/ get out of sync with code?

**A:** Yes, without discipline. That's why:
1. `jig validate` checks alignment (run in CI)
2. Harvest process extracts Intent from deltas (captures discoveries)
3. `@jig` annotations in code link to Intent nodes
4. `jig validate --constraints` checks system-wide properties

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
2. Mark discoveries as you find them (`#DISCOVERY`, `#CONSTRAINT`)
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
4. Define constraints for that subsystem
5. Expand subsystem by subsystem
6. Let decomposability analysis guide prioritization

### Q: How does this scale to large teams?

**A:** Like git:
- Each developer works in branches (deltas are branch-scoped)
- Intent changes merge like code (resolve conflicts in jig/)
- Subsystem boundaries enable parallel work
- Graph index enables fast lookups
- Constraint validation catches cross-cutting violations

### Q: Why constraints as predicates instead of graph nodes? **[New in v7]**

**A:** Graph nodes represent **parts of the system** (what we're building). Constraints represent **properties of the system** (what must be true).

Adding constraints as nodes would:
- Destroy coupling metrics (10:1 → 1:10)
- Obscure subsystem boundaries
- Make visualizations unreadable

Query-based constraints preserve architectural integrity while tracking cross-cutting concerns.

Think of it like:
- Files are nodes in a filesystem
- "No files >1GB" is a policy, not a file

### Q: How do I know which constraints apply to my code?

**A:** Three ways:

1. **Forward trace:** `jig trace X-HIPAA-001` shows all nodes affected
2. **Reverse trace:** `jig trace C-AUTH-001 --constraints` shows constraints on that node
3. **Annotations:** `@jig C-AUTH-001 ... satisfies:X-HIPAA-001` explicitly declares it

### Q: Can constraints apply to other constraints?

**A:** Not directly (constraints are predicates, not nodes). But you can:
- Define meta-constraints that validate constraint coverage
- Use constraint categories (compliance, performance, security)
- Link related constraints in documentation

### Q: When should I use nested subsystems vs flat subsystems? **[New in v7]**

**A:** Use nesting when:
- You have 10+ subsystems and need logical grouping
- Related subsystems naturally cluster (e.g., `auth`, `user`, `permissions` → `identity`)
- You want both coarse-grained and fine-grained analysis
- Your codebase mirrors a hierarchical package structure

Stick with flat when:
- You have <10 subsystems
- Subsystems are mostly independent
- Simpler mental model preferred

**You can mix**: Some subsystems nested, others flat.

### Q: How deep should subsystem nesting go? **[New in v7]**

**A:** **Recommended max: 3-4 levels.**

Deeper nesting:
- Complicates metrics interpretation
- Makes paths unwieldy (`identity.auth.jwt.validation`)
- Suggests over-decomposition

If you find yourself needing >4 levels, consider:
- Are these truly separate subsystems or implementation details?
- Can you collapse intermediate levels?
- Is this a sign of excessive coupling?

JIG will warn (not error) at >4 levels.

### Q: Do nested subsystems break decomposability metrics? **[New in v7]**

**A:** No, they improve them!

**Example:**

Before nesting (flat):
```
auth: 42 internal, 15 external → 2.8:1 ❌
user: 28 internal, 12 external → 2.3:1 ❌
```

After nesting (hierarchical):
```
identity.auth: 42 internal, 3 external → 14:1 ✓
identity.user: 28 internal, 2 external → 14:1 ✓
identity (parent): 74 internal, 2 external → 37:1 ✓
```

**Why?** Edges between `auth` and `user` were counted as external. After grouping under `identity`, they're internal to the parent.

**Key insight:** Nesting reveals true subsystem boundaries.

### Q: Can I refactor from flat to nested without breaking things? **[New in v7]**

**A:** Yes, it's backward compatible:

**Migration steps:**
1. Update `subsystems.yaml` to add nesting
2. Update node frontmatter: `subsystem: auth` → `subsystem: identity.auth`
3. Update `graph-index.yaml` subsystem paths
4. Run `jig validate --check-all`
5. Run `jig index --rebuild`

No code changes needed (assuming `@jig` annotations use node IDs, not subsystem names).

**Tip:** Use search/replace to update frontmatter in bulk.

---

## 16. Theoretical Foundations

### 16.1 Herbert Simon - Nearly Decomposable Systems

> "The behavior of a nearly decomposable system is approximately the sum of the behaviors of its subsystems, considered in isolation, plus the interactions among subsystems."

**Applied:**
- JIG detects subsystem boundaries via clustering
- Coupling ratio quantifies "nearly" (10:1 target)
- Modularity score measures decomposability
- **Constraints tracked separately to avoid distorting metrics**

**Reference:** "The Architecture of Complexity" (1962)

### 16.2 John Ousterhout - Deep Modules

> "The best modules are those whose interfaces are much simpler than their implementations."

**Applied:**
- Module depth metric: LOC / exports
- Target: >100:1 (deep modules)
- `interface:public` annotation marks boundaries
- **Constraints can require specific interface properties**

**Reference:** "A Philosophy of Software Design" (2018)

### 16.3 Christopher Alexander - Design as Constraint Satisfaction

> "Good design emerges from constraints, not plans."

**Applied:**
- Intent defines constraints (Outcomes, Specs)
- **System-wide constraints (X) are explicit, queryable**
- Code satisfies constraints
- Validation checks alignment
- Deltas capture constraint discovery

**Reference:** "Notes on the Synthesis of Form" (1964)

### 16.4 Linus Torvalds - Git Philosophy

> "The first rule of kernel development: never break user space."

**Applied:**
- Simple, fast, text-based tools
- Trust the developer (sharp tools)
- No magic, explicit operations
- Speed matters
- **Constraints as labels over graph, like git branches over commits**

**Reference:** Git design philosophy

### 16.5 Graph Theory - Separation of Concerns **[New in v7]**

**Two graph types in JIG:**

1. **Intent Flow Graph (OSTC)**: Hierarchical, directed, nearly decomposable
   - Nodes: O, S, T, C
   - Edges: implements, verifies, depends
   - Metrics: coupling ratio, modularity

2. **Constraint Satisfaction Graph (X)**: Query-based, predicate layer
   - Not nodes: Selectors and validators
   - No edges: Matches via queries
   - Metrics: compliance percentage

**Why separate?**

Mixing these creates incompatible graph topologies. Intent flow is hierarchical (tree-like); constraint satisfaction is cross-cutting (fully connected).

Solution: Two layers. Intent graph + constraint query layer.

---

## 17. Conclusion

### 17.1 The Core Thesis

**Software development is maintaining alignment across representations:**
- Business intent (Outcomes)
- Technical requirements (Specifications)
- Verification (Tests)
- Implementation (Code)
- System-wide properties (Constraints)

**The alignment problem has three dimensions:**
1. **Synchronic:** Are O/S/T/C aligned right now?
2. **Diachronic:** How do we harvest insights from change into Intent?
3. **Cross-cutting:** Are system-wide constraints satisfied everywhere?

**JIG v7 solves all three:**
- OSTC graph for synchronic alignment
- Delta harvest for diachronic learning
- Constraint predicates for cross-cutting properties
- Decomposability for structural health

### 17.2 The Promise

**10x improvement in:**
- Knowledge retention (harvest vs forget)
- Parallel development (subsystem isolation)
- Onboarding time (Intent graph shows design)
- Architectural drift detection (metrics over time)
- Compliance tracking (constraint validation)

**By making visible:**
- What we intend (Outcomes)
- What we require (Specifications)
- What we verify (Tests)
- What we run (Code)
- What must hold everywhere (Constraints)
- How we got here (Deltas)
- How it's organized (Subsystems)

### 17.3 The Git-Native Advantage

Like git transformed version control by being:
- Fast (millisecond operations)
- Simple (text-based, grep-able)
- Distributed (no central server)
- Powerful (sharp tools for experts)

JIG transforms Intent management by being:
- Fast (grep-speed extraction)
- Simple (markdown + YAML)
- Distributed (git-tracked files)
- Powerful (decomposability analysis, harvest pipeline, constraint validation)

**The result:**
> "Software that knows its own purpose, maintains its boundaries, learns from its own evolution, and validates its own properties."

### 17.4 The v7 Innovations

**Two key architectural insights:**

**1. Constraints as predicates over the Intent Graph**

By separating:
- **What the system does** (OSTC graph)
- **What the system must satisfy** (X predicates)

We can:
- Measure decomposability accurately (no constraint edge pollution)
- Track cross-cutting concerns explicitly (queries over nodes)
- Validate compliance systematically (predicate evaluation)
- Maintain architectural integrity (boundaries preserved)

This is a fundamental recognition that **cross-cutting properties** and **hierarchical intent** are different categories requiring different representations.

**2. Nested subsystems for hierarchical organization**

By supporting subsystem nesting:
- **Scalability**: Manage 20+ subsystems without cognitive overload
- **Natural grouping**: Reflect real system architecture (`identity.auth`, `identity.user`)
- **Hierarchical metrics**: Both coarse and fine-grained decomposability analysis
- **Improved coupling ratios**: Edges between related subsystems become internal to parent

This enables refactoring subsystems into logical hierarchies without degrading decomposability metrics - revealing true architectural boundaries rather than arbitrary flat divisions.

---

## 18. Migration from v6

**v6 → v7 changes:**

| Feature | v6 | v7 | Rationale |
|---------|----|----|-----------|
| **Constraints** | No constraint support | Query-based constraints | Track cross-cutting concerns |
| **Model** | OSTC only | OSTCX model | Constraints as predicates |
| **Storage** | N/A | `jig/constraints/` directory | Constraint documents |
| **Index** | N/A | `constraint-index.yaml` | Fast constraint lookups |
| **Validation** | `jig validate` | `jig validate --constraints` | Constraint compliance |
| **Markers** | N/A | `#CONSTRAINT` in deltas | Delta constraint discovery |
| **Annotations** | N/A | `satisfies:X-001` | Code constraint linking |
| **Commands** | N/A | `jig constraint check` | Constraint validation |
| **Traceability** | N/A | `jig trace --constraints` | Constraint tracing |
| **Subsystems** | Flat only | Nested subsystems | Hierarchical organization |
| **Paths** | Simple names | Dot notation (`crdt.ser`) | Hierarchical paths |
| **Metrics** | Flat metrics | Hierarchical coupling | Parent aggregates children |
| **Status** | Flat list | Tree view (`--flat` for old) | Visual hierarchy |
| **Queries** | N/A | Recursive subsystem queries | Query parent or leaf |

**Migration path (Constraints):**

1. Existing OSTC nodes compatible (no changes required)
2. Add `jig/constraints/` directory
3. Define initial constraints (security, performance, compliance)
4. Add `satisfies:X-001` to existing `@jig` annotations
5. Run `jig index --rebuild` to populate constraint index
6. Validate constraints with `jig validate --constraints`
7. Add `#CONSTRAINT` markers to future deltas

**Migration path (Nested Subsystems - Optional):**

1. Identify subsystems that should be grouped (e.g., `auth`, `user` → `identity`)
2. Update `jig/subsystems.yaml` to add hierarchical structure
3. Update node frontmatter: `subsystem: auth` → `subsystem: identity.auth`
4. Update `graph-index.yaml` with new paths
5. Run `jig validate --check-all` to verify
6. Run `jig index --rebuild`

**Backward Compatibility:**

- **Constraints**: Additive only. v6 projects work in v7 without constraints.
- **Nested Subsystems**: Additive only. Flat subsystems continue to work.
- **No breaking changes to OSTC model** - all existing nodes, edges, deltas remain valid.

---

**Document Version:** 7.0.0
**Date:** 2025-11-20
**Authors:** Jim & Claude
**Status:** Architecture Proposal
**Next Steps:**
- Phase 4: Constraints implementation
- Phase 5: Nested subsystems implementation

---

*"JIG: Simple, fast, git-native Intent alignment with constraint validation and hierarchical subsystems."*
*"Intent documented. Deltas harvested. Boundaries preserved. Hierarchies respected. Constraints satisfied. Alignment maintained."*
