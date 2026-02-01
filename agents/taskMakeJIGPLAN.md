# Task: Create JIGPLAN Document (taskMakeJIGPLAN)

**Version:** 2.0.0
**Date:** 2026-01-08
**Audience:** AI coding agents
**Status:** Active
**Related:** JigPlanOrchWorkflow.md, taskMakePLAN.md, taskDoPLAN.md, taskDoWU.md, contextBricks.md

## Objective

Create a JIGPLAN document that defines the complete architectural plan for a feature before any implementation begins. The JIGPLAN specifies what O/S nodes, bricks, and @jig decorators will be created, updated, or deleted.

**JIGPLAN is the architectural gate between SCOPE and implementation.**

---

## Inputs

Before creating a JIGPLAN, you need:

1. **SCOPE Document**: Problem description (human-authored)
   - Located in `docs/wip/SCOPE-<feature>.md`
   - May request backwards compatibility (if so, plan for it)

2. **Existing JIG Artifacts**: Review before planning
   - `jig/specifications/*.md` - existing specs (prefer REUSE over CREATE)
   - `jig/outcomes/*.md` - existing outcomes
   - `jig/bricks.yaml` - current brick structure

3. **Codebase Analysis**: Understand what exists
   - Relevant source code
   - Existing @jig decorators
   - Current layer structure

4. **Charter Decision Philosophy**: Read before making architectural choices
   - `jig/Charter.md` - Section "Decision Philosophy"
   - Decision heuristics for resolving tradeoffs
   - Anti-goals to avoid optimizing for

---

## Key Concepts

### The S-F-T Triangle

JIG measures alignment between **intent** (specifications), **implementation** (functions), and **verification** (tests):

```
         S (Specification)
        / \
       /   \
implements  verifies
     /       \
    F ————————→ T
       covers
```

Three relationships:
- **F → S** (implements): Function implements specification via `@jig.implements("S-001")`
- **T → S** (verifies): Test verifies specification via `@jig.verifies("S-001")`
- **T → F** (covers): Test executes function (automatic via coverage)

### JIG Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Specifications | `jig/specifications/S-{number}.md` | What we intend to build |
| Outcomes | `jig/outcomes/O-{number}.md` | Why we build it (optional) |
| Bricks | `jig/bricks.yaml` | Architectural partitions |
| Decorators | Source code | Links code/tests to specs |
| Generated graphs | `jig/generated/*.ndjson` | Machine-generated, NEVER edit |

### ID Formats

| Type | Format | Example |
|------|--------|---------|
| Specification | `S-{number}` | S-001, S-042 |
| Outcome | `O-{number}` | O-001 |
| Brick | `B-{kebab-case}` | B-auth-session |
| Function | `F-{path}` | F-auth.session.authenticate |
| Module | `M-{path}` | M-auth.session |
| Class | `C-{path}` | C-auth.tokens.TokenValidator |
| Test | `T-{path}` | T-test_auth.test_token_expiration |

### Bricks and Layers

**Bricks** partition functions into architectural units.
**Layers** stratify bricks vertically (layer N depends only on layers < N).

**See:** `docs/jig/contextBricks.md` for full brick/layer reference.

#### The Partition Property

Every function belongs to exactly ONE brick:
- **No gaps** - every function is assigned
- **No overlaps** - no function in multiple bricks
- **Class integrity** - all methods of a class must be in same brick

#### Brick Definition

```yaml
bricks:
  - id: B-core-utils
    name: Core Utilities
    layer: 0              # Foundation
    units:
      - M-utils.io           # All functions in module
      - C-utils.Parser       # All methods of class
      - F-utils.helpers.foo  # Single function
```

**Unit prefixes:**
- `M-{path}` — module (all functions)
- `C-{path}` — class (all methods)
- `F-{path}` — single function

**Brick ID format:** `B-{kebab-case-name}` — semantic naming (NOT numeric IDs)

#### Derived Properties (Not Stored)

Brick properties are computed, not declared:

| Property | Derived From |
|----------|--------------|
| Specs assigned | Functions' `@jig.implements` decorators |
| Dependencies | Call graph (F in brick A calls F in brick B) |
| Public API | Functions called from outside the brick |

**Single source of truth:** `bricks.yaml` defines membership only. Everything else is computed.

#### Layer Constraint

**A brick at layer N may depend ONLY on layers 0..(N-1).**

Dependencies flow DOWN, never up. Violations are errors, not warnings.

**Layer 0 special rules:**
- MAY depend on external libraries and other layer 0 bricks
- MUST NOT depend on any brick at layer 1+
- Cycles rejected even within layer 0

#### When to Create vs Extend Bricks

**Create new brick when:**
- Functions form cohesive unit with distinct responsibility
- Clear boundary exists (different concern, different rate of change)
- Dependency isolation is valuable (testing, deployment)

**Extend existing brick when:**
- Functions naturally belong to existing boundary
- No clear separation of concerns
- Would create artificial split

#### Layer Assignment

Layer = max(dependency layers) + 1

**Decision process:**
1. List brick's dependencies (what does it call?)
2. Find max layer among dependencies
3. Assign layer = max + 1
4. If no dependencies, layer = 0

Or: Use `jigy layers suggest` to compute from actual dependencies.

#### FORBIDDEN Bricks (Per-JIGPLAN)

FORBIDDEN is a per-work-scope constraint, NOT a permanent brick property.

Each JIGPLAN defines which bricks are off-limits for that specific work:
- **Scope discipline** - Prevents "while I'm here, let me also fix..."
- **Sub-agent guardrails** - Clear boundaries for automated execution
- **Change isolation** - Limits blast radius of modifications

Any brick can be FORBIDDEN regardless of layer. The constraint is "don't touch during THIS work."

---

## Clean Break as Default

**AI agents tend to add compatibility shims by default. This workflow counters that bias.**

### Clean Break Means

- Old code paths are DELETED, not feature-flagged
- Old tests are DELETED and new tests written from scratch
- No backwards compatibility shims or adapters
- Unimplemented features raise `NotImplementedError` (fail loudly)
- Deprecated O/S nodes are deleted after validation

### When Backwards Compatibility is Needed

Backwards compat must be **explicitly requested in SCOPE**. Valid reasons:
- Public API with external consumers
- Critical path code requiring rollback capability
- Multi-team coordination constraints
- Regulatory/compliance requirements

**If SCOPE does not request backwards compat, clean break is assumed.**

### Anti-Patterns to Avoid

```python
# BAD: Feature flag hell
if USE_NEW_PARSER:
    return new_parser.parse(content)
else:
    return old_parser.parse(content)  # "just in case"

# GOOD: Clean break with clear errors
def parse(content: str) -> ParseResult:
    result = new_parser.parse(content)
    if has_legacy_markers(content):
        raise NotImplementedError(
            "Legacy markers no longer supported. Use new format."
        )
    return result
```

---

## Process

### Step 1: Analyze SCOPE

Read the SCOPE document carefully. Extract:

1. **Behavioral requirements** → Map to specifications
2. **Business value statements** → Map to outcomes
3. **Architectural scope** → Which bricks affected
4. **Backwards compat requests** → Plan if present (rare)

**If SCOPE is unclear**, ask clarifying questions rather than guess.

### Step 2: Audit Existing O/S Nodes

Before creating new nodes, search existing specs and outcomes:

```bash
# Find specs that might already cover this behavior
grep -r "token" jig/specifications/
grep -r "authentication" jig/specifications/

# Check outcomes for related business value
grep -r "security" jig/outcomes/
```

**Strong preference for REUSE and UPDATE over CREATE.**

Questions to ask:
- Does an existing spec already cover this behavior?
- Can I update an existing spec instead of creating new?
- Is there an existing outcome this work supports?
- Are any existing specs now obsolete (DELETE)?

### Step 3: Audit Existing Bricks

Analyze brick structure:

```bash
# View current layer structure
jigy layers

# Check which bricks contain related code
grep -r "related_module" jig/bricks.yaml
```

Questions to ask:
- Which bricks will this work touch?
- Do we need a new brick, or extend existing?
- What layer should new code be at?
- Are there FORBIDDEN bricks (foundation that shouldn't change)?

### Step 4: Plan @jig Decorator Changes

For each spec being implemented:
- What functions will implement it? (`@jig.implements`)
- What tests will verify it? (`@jig.verifies`)
- What existing decorators become orphaned (spec deleted)?

### Step 5: Write O/S Node Files

**CREATE nodes:** Write actual spec/outcome files to disk.

```bash
# For each CREATE spec, write to jig/specifications/
jig/specifications/S-147.md
jig/specifications/S-148.md

# For each CREATE outcome, write to jig/outcomes/
jig/outcomes/O-024.md
```

**UPDATE nodes:** Edit existing files in place.

**DELETE nodes:** Do NOT delete yet - deletion happens after implementation validates.

### Step 6: Update bricks.yaml (If Needed)

If creating new bricks or modifying existing:

```yaml
# Add new brick
- id: B-crdt-observe
  name: CRDT Observation
  layer: 1
  units:
    - M-ase.crdt.observe

# Or add units to existing brick
- id: B-existing
  units:
    - M-existing.module
    - M-new.module  # Added
```

### Step 7: Validate

Run JIG validation to ensure no broken references:

```bash
jigy rebuild && jigy validate
jigy layers  # Verify layer structure
```

**All validation must pass before proceeding.**

### Step 8: Write JIGPLAN Document

Create `docs/wip/JIGPLAN-<feature>.md` using the template below.

The JIGPLAN references the O/S nodes you created - it does NOT embed their full content.

### Step 9: Fresh Agent Review (Required)

**Purpose:** Verify the JIGPLAN is complete and internally consistent before human approval.

**Why a fresh agent:** The creating agent has JIGPLAN context in working memory. A fresh agent tests whether the document is self-contained - it catches assumptions baked into the creator's mental model that would confuse implementers.

**Lens:** Architectural completeness (specs, bricks, layers, decorator coverage).

#### 9.1: Scope Check

For JIGPLANs affecting ≤2 specs with no brick changes, review categories 1 and 2 may be abbreviated (search existing specs, verify new specs are behavioral). Full review required otherwise.

#### 9.2: Spawn Review Agent

**Review agent has full codebase access** via Glob, Grep, Read tools.

Use this prompt to spawn a fresh agent for review:

```
You are reviewing a JIGPLAN document before human approval.

Read: <path to JIGPLAN file>

Your task: Identify issues that would cause problems during implementation.

## Review Categories

### 1. Spec Audit Completeness
- Search for existing specs related to the feature's domain
- Are there specs that should be REUSE/UPDATE but are missing?
- Are there specs that conflict with what's being proposed?

### 2. Anti-Pattern Detection
Check if new specs follow evergreen guidelines:
- Do they describe BEHAVIOR or implementation details?
- Could you write @jig.implements and @jig.verifies for them?

Read the actual spec files created and verify.

### 3. Brick/Layer Validation
- Do layer assignments make sense given dependencies?
- Are there circular dependency risks?
- Verify FORBIDDEN bricks exist in bricks.yaml

### 4. Decorator Completeness
- Are all functions/classes that implement specs listed?
- Are all tests that verify specs listed?
- Any obvious gaps in coverage?

### 5. Internal Consistency
- Do specs reference each other correctly?
- Are brick units consistent with decorator locations?
- Any contradictions between specs?

## Output Format

For each issue:
- **Category**: [1-5]
- **Type**: MECHANICAL | JUDGMENT
- **Severity**: BLOCKER | WARNING | NOTE
- **Issue**: [description]
- **Evidence**: [what you found]
- **Recommendation**: [what to do]

MECHANICAL = Can be fixed by applying clear rules
JUDGMENT = Requires architectural decision

If no issues in a category, state "No issues found."
```

#### 9.3: Resolve Issues

For each issue from the review:

**MECHANICAL issues** — Fix autonomously:
- Missing decorators → Add them
- Incomplete spec coverage → Expand
- Naming inconsistencies → Normalize
- Missing brick units → Add them
- Audit gaps → Run additional searches

**JUDGMENT issues** — Apply Charter philosophy:
1. Read `jig/Charter.md` section "Decision Philosophy"
2. Enumerate the options
3. Score each option against the decision heuristics
4. Choose the option that wins on highest-priority heuristic
5. Document which heuristic drove the decision

**Escalate to human only if:**
- Heuristics conflict (two point to different options with no clear winner)
- Novel situation: no existing heuristic directly applies AND analogical reasoning from existing heuristics yields conflicting answers
- Ambiguity in original SCOPE intent that affects architectural direction

#### 9.4: Re-Review If Needed

If changes affected ≥3 specs or any brick definitions, run another review pass. Maximum 2 re-review iterations - if still finding BLOCKERs after 2 passes, escalate to human.

**Exit criteria:**
- Review agent reports no BLOCKER issues, OR
- Review agent reports no issues at all → proceed directly to human approval
- All MECHANICAL issues resolved
- All JUDGMENT issues resolved via Charter philosophy OR escalated with documented rationale

---

## JIGPLAN Template

```markdown
# JIGPLAN: <Feature Name>

**SCOPE:** docs/wip/SCOPE-<feature>.md
**Date:** <YYYY-MM-DD>
**Status:** Draft | Approved
**Author:** <agent/human>

---

## Summary

<2-3 sentences describing what this JIGPLAN covers: which bricks affected,
how many specs created/updated/deleted, key architectural decisions.>

---

## O/S Node Reconciliation

### Outcomes

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | O-001 | <title> | <why reusing> |
| UPDATE | O-002 | <title> | <what changes> |
| DELETE | O-003 | <title> | <why obsolete> |
| CREATE | O-004 | <title> | <why new> |

### Specifications

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | S-001 | <title> | <why reusing> |
| UPDATE | S-002 | <title> | <what changes> |
| DELETE | S-003 | <title> | <what supersedes> |
| CREATE | S-004 | <title> | <why new> |

---

## O/S Node Details

### Nodes to UPDATE

#### S-002 Update Details

**Current acceptance criteria:**
- <existing criterion 1>
- <existing criterion 2>

**Changes:**
- ADD: <new criterion>
- MODIFY: <changed criterion>
- REMOVE: <obsolete criterion>

---

### Nodes to DELETE

#### S-003 Deletion Rationale

**Reason:** <why this spec is obsolete>
**Superseded by:** <what replaces it, or "N/A - behavior removed">
**Clean break:** All code with @jig.implements("S-003") will be deleted.

---

### Nodes to CREATE

List specs/outcomes created in Step 5. Reference the files - do NOT duplicate content here.

#### S-004: <Title> (NEW)

**File:** `jig/specifications/S-004.md` (created in Step 5)
**Implements:** O-001
**Summary:** <1-2 sentence summary of what this spec defines>

#### O-004: <Title> (NEW)

**File:** `jig/outcomes/O-004.md` (created in Step 5)
**Summary:** <1-2 sentence summary of business value>

---

## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| CREATE | B-new-brick | 1 | <why new brick needed> |
| MODIFY | B-existing | 2 | <what changes> |
| FORBIDDEN | B-foundation | 0 | <why must not touch> |
| UNAFFECTED | B-other | 2 | <no changes needed> |

---

### Brick Details

#### B-new-brick (NEW)

- **Layer:** 1
- **Purpose:** <what this brick does>
- **Units:**
  - M-module.path
  - C-module.ClassName
- **Dependencies:** B-core-utils (layer 0)

#### B-existing Modifications

- **Current units:** M-existing.module
- **Add units:** M-new.module (or none)
- **Layer change:** (none - stays at layer N)
- **New dependencies:** B-new-brick (layer 1)
- **Changes:** <describe what changes in this brick>

#### FORBIDDEN Bricks

These bricks MUST NOT be modified by any work unit:

- **B-foundation** (layer 0): <why it's off limits>

**Sub-agent constraint:** Any modification to FORBIDDEN bricks is an
immediate escalation trigger.

---

## Layer/Dependency Analysis

### Layer Structure (Affected Bricks)

```
Layer 0: FORBIDDEN
  B-core-utils ← no changes
  B-data-models ← no changes

Layer 1: AFFECTED
  B-new-brick (NEW)
    └─► depends on: B-core-utils ✓

Layer 2: AFFECTED
  B-existing (MODIFY)
    └─► depends on: B-core-utils, B-new-brick ✓
```

### Dependency Constraints

- B-new-brick (layer 1) MUST NOT depend on B-existing (layer 2)
- No circular dependencies between affected bricks
- B-existing MAY depend on B-new-brick (layer 2 → layer 1 is valid)

### Validation Commands

After implementation, verify with:
```bash
jigy rebuild && jigy validate
jigy layers  # Confirm layer structure
```

---

## @jig Decorator Changes

### Decorators to ADD

| Type | Location | Spec |
|------|----------|------|
| implements | F-module.function_name | S-004 |
| verifies | T-test_module.test_function | S-004 |

### Decorators to REMOVE

| Type | Location | Spec | Reason |
|------|----------|------|--------|
| implements | F-old.deprecated_func | S-003 | Spec deleted |
| verifies | T-test_old.test_deprecated | S-003 | Spec deleted |

### Decorators to MODIFY

| Type | Location | Old Spec | New Spec | Reason |
|------|----------|----------|----------|--------|
| implements | F-module.func | S-002 | S-002 | Spec updated (same ID) |

---

## Clean Break Actions

This work follows clean break protocol:

- [ ] Old code paths will be DELETED, not feature-flagged
- [ ] Old tests will be DELETED and new tests written from scratch
- [ ] No backwards compatibility shims
- [ ] Unimplemented features will raise NotImplementedError
- [ ] Deleted O/S nodes removed after final validation

### Code to Delete

- `src/path/to/old_module.py` (entire module)
- `test/path/to/test_old.py` (entire module)
- Any imports of old_module

### O/S Nodes to Delete (After Validation)

- `jig/specifications/S-003.md`

---

## Backwards Compatibility Plan (If Requested in SCOPE)

**Skip this section if clean break (default).**

If SCOPE requested backwards compatibility:

**Parallel implementation duration:** <N sprints>
**Old code to preserve:** <paths>
**Deprecation signals:**
- <warning on import>
- <log warning on use>
**Migration documentation:** <path>
**Deletion timeline:** <when old code gets deleted>
**Compat consumer list:**
- <who needs the old behavior>

---

## Fresh Agent Review Summary

(Populated during Step 9)

### Review Findings

| Category | Type | Severity | Issue | Resolution |
|----------|------|----------|-------|------------|
| <1-5> | MECHANICAL/JUDGMENT | BLOCKER/WARNING/NOTE | <issue> | <how resolved> |

### Judgment Decisions

For each JUDGMENT issue resolved using Charter philosophy:

**Issue:** <description>
**Options considered:**
1. <option A>
2. <option B>

**Heuristic analysis:**
| Heuristic | Option A | Option B |
|-----------|----------|----------|
| Conceptual clarity | ✅/❌ | ✅/❌ |
| Documentation value | ✅/❌ | ✅/❌ |
| Clean breaks | ✅/❌ | ✅/❌ |
| Single responsibility | ✅/❌ | ✅/❌ |

**Decision:** Option X, driven by <heuristic name>

---

## Approval Checklist

Before human approval:

- [ ] All existing specs reviewed for REUSE opportunities
- [ ] New specs follow evergreen guidelines (behavior, not implementation)
- [ ] Brick layer constraints validated
- [ ] FORBIDDEN bricks identified
- [ ] @jig decorator plan complete
- [ ] Clean break actions specified (unless compat requested)
- [ ] **Fresh Agent Review completed (Step 9)**
- [ ] All MECHANICAL issues resolved
- [ ] All JUDGMENT issues resolved via Charter philosophy OR escalated

---

**Awaiting human approval before proceeding to PLAN.**
```

---

## Writing Evergreen O/S Nodes

**CRITICAL:** O and S nodes are EVERGREEN documentation of system behavior and value. They are NOT project management artifacts.

Write O/S nodes that will be true FOREVER, not just until the PR merges.

### Outcomes (O-*)

**What Outcomes ARE:**
- Business value that persists after code is written
- WHY the system behaves a certain way
- User-facing or operational benefits
- Decompose into multiple specifications

**What Outcomes are NOT:**
- Project goals ("achieve 90% test coverage")
- Work unit objectives ("add missing tests")
- Refactoring tasks ("reorganize code")
- Process improvements ("improve code organization")

**Checklist:**
- [ ] Describes business value, not project state
- [ ] Remains true after project completes
- [ ] Explains WHY system behaves this way
- [ ] Would make sense to new developer in 2 years

**Test:** Remove all references to the work that created this outcome. Does it still make sense? If no, rewrite.

#### Outcome Anti-Patterns

**Anti-Pattern: Project Goals as Outcomes**

❌ **BAD:**
```markdown
# Test Coverage
Critical paths have comprehensive tests.
```
This describes a project state, not system value.

✓ **GOOD:**
```markdown
# System Reliability Through Verification
Critical system behaviors are verified to prevent regressions in production.

**Value:** Reduces customer-facing bugs and deployment risk.
```

**Anti-Pattern: Process Improvements as Outcomes**

❌ **BAD:**
```markdown
# Code Organization
Related code co-located in correct bricks.
```
This describes code structure, not value.

✓ **GOOD:**
```markdown
# Clear Architectural Boundaries
Authentication logic is isolated from business logic, enabling independent modification.

**Value:** Reduces time to implement auth changes without breaking other systems.
```

---

### Specifications (S-*)

**What Specifications ARE:**
- Observable system behavior
- Technical requirements that can be implemented and verified
- Contracts that code must satisfy
- Acceptance criteria that tests verify

**What Specifications are NOT:**
- Refactoring tasks ("move file X to location Y")
- Implementation instructions ("use Redis for caching")
- Work units ("add decorators to functions")
- Code quality goals ("add missing specs")

**Checklist:**
- [ ] Describes HOW system behaves, not HOW TO BUILD
- [ ] Has observable acceptance criteria
- [ ] Can be implemented by code (`@jig.implements`)
- [ ] Can be verified by tests (`@jig.verifies`)
- [ ] Avoids file paths, implementation details, refactoring tasks

**Test:** Can you write `@jig.implements("S-001")` on code? Can you write `@jig.verifies("S-001")` on tests? If no, rewrite.

#### Specification Anti-Patterns

**Anti-Pattern: Refactoring Tasks as Specs**

❌ **BAD:**
```markdown
# Relocate era_persistence
era_persistence.py moved from utils to protocol-core where EraLamportClock is defined.
```
This describes a file move, not behavior.

✓ **GOOD:**
```markdown
# EraLamportClock Persistence
EraLamportClock state persists across process restarts without clock regression.

**Acceptance Criteria:**
- get_era() returns last saved era + 1 on process start
- save_era() writes era to persistent storage
- Clock never returns same timestamp after restart

**Rationale:** Ensures causal consistency in distributed system.
```

**Anti-Pattern: Implementation Details as Specs**

❌ **BAD:**
```markdown
# Airspace-crdt Functions Have Decorators
add_device(), remove_device(), and update_device_element() have @jig.implements decorators.
```
This describes tooling, not requirements.

✓ **GOOD:**
```markdown
# Airspace Device Lifecycle
Devices can be added, removed, and updated in shared airspace CRDT.

**Acceptance Criteria:**
- add_device(id, metadata) creates device entry with vector clock
- remove_device(id) tombstones device, preserves history
- update_device_element(id, key, value) merges updates LWW
- Operations are commutative and idempotent

**Rationale:** Enables conflict-free replication across multiple clients.
```

**Anti-Pattern: Meta-Specifications**

❌ **BAD:**
```markdown
# Specification Completeness
All public APIs have specifications.
```
This describes documentation goals, not system behavior.

✓ **GOOD:**
```markdown
# Catalog Query Interface Contracts
DataDictionaryCatalog provides deterministic query results for device metadata.

**Acceptance Criteria:**
- get_data_element(id) returns element or None, never throws
- get_gui_metadata(id) returns display info or default values
- get_data_elements_for_device(device_id) returns sorted list
- Query results consistent across repeated calls with same DB state

**Rationale:** GUI and device layers depend on stable query interface.
```

---

### Converting Work Units to O/S Nodes

When analyzing SCOPE, you may encounter work unit language. Convert to evergreen O/S nodes.

**Example 1: Work Unit → Existing Spec**

Work Unit: "WU3: Add ELC Persistence Tests"

❌ **BAD Spec:**
```markdown
S-078: EraLamportClock persistence tested per S-036
```

✓ **GOOD:** Reference existing spec
```markdown
S-036: EraLamportClock Persistence [already exists - REUSE]
```

**Action:** Reference existing spec in work unit. If no spec exists, CREATE the spec that describes the behavior, then write tests for it.

**Example 2: Work Unit → Evergreen O/S**

Work Unit: "WU8: Consolidate GUI Location"

❌ **BAD Outcome:**
```markdown
O-024: Code Organization - Related code co-located in correct bricks
```

✓ **GOOD Outcome:**
```markdown
O-024: Modular GUI Components
GUI components are independently testable and reusable across different device types.

**Value:** Reduces time to add new device UI from days to hours.
```

✓ **GOOD Spec:**
```markdown
S-083: GUI Component Package Structure
All GUI components reside in ase.gui.* package with clear public API.

**Acceptance Criteria:**
- ase.gui.widgets exports all widget factories
- ase.gui.themes provides theme system
- ase.gui.layouts provides layout managers
- No GUI code exists outside ase.gui.*

**Rationale:** Enables GUI testing without device process dependencies.
```

---

### Summary

| Type | What It Is | What It's NOT |
|------|------------|---------------|
| **Outcomes** | Evergreen business value | Project goals, work objectives |
| **Specifications** | Evergreen behavioral requirements | Refactoring tasks, implementation details |
| **Work Units** | Temporary project tasks | O/S nodes |

---

## Validation

Before submitting JIGPLAN for approval:

```bash
# Verify current JIG state
jigy rebuild && jigy validate

# Check layer structure
jigy layers

# Verify no broken references
jigy validate
```

---

## Outputs

### Files Created/Modified

1. **O/S Node Files** (actual JIG artifacts):
   - `jig/specifications/S-*.md` - new or updated specs
   - `jig/outcomes/O-*.md` - new or updated outcomes
   - `jig/bricks.yaml` - if brick changes needed

2. **JIGPLAN Document** (`docs/wip/JIGPLAN-<feature>.md`):
   - O/S Node Reconciliation tables (REUSE/UPDATE/DELETE/CREATE)
   - References to created spec files (not embedded content)
   - Brick Scope (CREATE/MODIFY/FORBIDDEN/UNAFFECTED)
   - Layer/Dependency Analysis
   - @jig Decorator Changes (ADD/REMOVE/MODIFY)
   - Clean Break Actions
   - Fresh Agent Review Summary

### Validation State

After JIGPLAN creation, `jigy rebuild && jigy validate` must pass.

---

## Constraints

### DO NOT

- **Create new specs when existing ones suffice** - REUSE first
- **Skip brick analysis** - Layer violations cause cascading issues
- **Omit FORBIDDEN bricks** - Sub-agents need clear boundaries
- **Write implementation details as specs** - Specs are evergreen behavior
- **Add compatibility shims by default** - Clean break unless SCOPE requests
- **Skip Fresh Agent Review** - Catches issues before human review

### MUST

- **Read Charter Decision Philosophy** - Before making architectural choices
- **Write O/S node files to disk** - Specs must exist for implementation
- **Run jigy validate before submitting** - No broken references
- **Audit existing O/S nodes first** - Prevent specification sprawl
- **Identify FORBIDDEN bricks** - Protect foundation layers
- **Validate layer constraints** - No upward dependencies
- **Plan @jig decorator changes** - Enables JIG summary at end
- **Complete Fresh Agent Review** - Resolve issues before human sees it
- **Apply Charter heuristics to JUDGMENT issues** - Don't escalate prematurely

### PREFER

- **REUSE over UPDATE** - Fewer changes, less drift
- **UPDATE over CREATE** - Extend existing specs
- **DELETE obsolete specs** - Don't let dead specs accumulate
- **Conservative FORBIDDEN list** - Protect more than less
- **Autonomous resolution** - Use philosophy to decide, escalate only when stuck

---

## Version History

- **2.0.0** (2026-01-08): Added Fresh Agent Review (Step 9). Agents must resolve MECHANICAL issues autonomously and apply Charter Decision Philosophy to JUDGMENT issues before escalating to human. Added Fresh Agent Review Summary section to template. Added scope check for abbreviated review on small JIGPLANs. Clarified "novel situation" definition. Added max iteration limit (2) on re-review loops.
- **1.1.0** (2025-12-18): O/S nodes now written to disk during JIGPLAN (not just documented). Added Steps 5-7 for file creation, bricks.yaml update, and validation.
- **1.0.2** (2025-12-18): Expanded Bricks and Layers with derived properties, when to create vs extend, layer assignment, FORBIDDEN per-scope
- **1.0.1** (2025-12-18): Expanded evergreen O/S node guidance with full anti-patterns
- **1.0.0** (2025-12-18): Initial version

---

**Next:** After JIGPLAN is approved, create PLAN document using taskMakePLAN.md.
