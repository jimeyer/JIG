# SCOPE: Extended Intent Hierarchy and Slices

**ID:** C003
**Status:** Draft
**Date:** 2025-12-29
**Implements:** C001_PROPOSAL_JIG-Core-Artifacts-Contract.md, C002_PROPOSAL_Bricks-with-Slices.md

---

## Executive Summary

This scope document defines the work required to evolve JIG from a **4-level hierarchy** (Outcome → Specification → Code/Tests) to a **7-level hierarchy** (Charter → Goals → Architecture/Outcomes → Specifications → Code/Tests) while adding **vertical partitioning** (Slices) to the existing horizontal partitioning (Layers).

**Two complementary changes:**

1. **C001**: Extend intent hierarchy with Charter, Goals, and Architecture
2. **C002**: Add Slices to Bricks for complete isolation partitioning

---

## Current State Summary

| Artifact Type | Current | After C001+C002 |
|---------------|---------|-----------------|
| Root Document | Constitution.md (informal) | Charter.md (formal, defines goals) |
| Goal Definitions | Implicit in Constitution | Explicit G-# nodes in intent graph |
| Architecture | None | A-### documents with supports_goals, constrains |
| Outcomes | O-### with specifies only | O-### with supports_goals + specifies |
| Specifications | S-### | S-### (no change) |
| Bricks | layer only | layer + slice |
| Code/Tests | C-, T- annotations | C-, T- annotations (no change) |

---

## PART A: Functional Changes to JIG

### A.1 Intent Graph Generator

**File:** `src/jig/intent_graph/generator.py`

#### A.1.1 New Node Type: Charter

```json
{"id":"Charter","type":"charter","defines_goals":["G-1","G-2","G-3","G-4","G-5"],"file":"jig/Charter.md"}
```

**Implementation:**
- Add `_load_charter_node()` method
- Parse `jig/Charter.md` YAML frontmatter
- Extract `defines_goals` array
- Single node, always present

#### A.1.2 New Node Type: Goal

```json
{"id":"G-1","type":"goal","title":"Discover Correct Design Intent","file":"jig/Charter.md"}
```

**Implementation:**
- Add `_load_goal_nodes()` method
- Parse Charter markdown body for `### G-{number}:` headers
- Extract goal titles from headers
- Create one node per goal defined in Charter

#### A.1.3 New Node Type: Architecture

```json
{"id":"A-001","type":"architecture","title":"Device Logic Contract","status":"active","supports_goals":["G-1","G-5"],"constrains":["S-116","S-117"],"file":"jig/architecture/A-001.md"}
```

**Implementation:**
- Add `_load_architecture_nodes()` method
- Scan `jig/architecture/A-*.md` files
- Parse YAML frontmatter (id, type, title, status, supports_goals, constrains)
- Create one node per architecture document

#### A.1.4 Extended Outcome Nodes

**Current:**
```json
{"id":"O-001","type":"outcome","specifies":["S-001"],"file":"jig/outcomes/O-001.md"}
```

**After:**
```json
{"id":"O-001","type":"outcome","supports_goals":["G-2","G-4"],"specifies":["S-001"],"file":"jig/outcomes/O-001.md"}
```

**Implementation:**
- Update `_load_outcome_nodes()` to include `supports_goals` field
- Outcomes MUST have `supports_goals` (required field per C001)

#### A.1.5 Extended Brick Nodes (C002)

**Current:**
```json
{"id":"B-crdt","type":"brick","name":"CRDT Primitives","layer":0,"units":["M-ase.crdt"],"file":"jig/bricks.yaml"}
```

**After:**
```json
{"id":"B-crdt","type":"brick","name":"CRDT Primitives","layer":0,"slice":"device-logic","units":["M-ase.crdt"],"file":"jig/bricks.yaml"}
```

**Implementation:**
- Update `_load_brick_nodes()` to include `slice` field
- Bricks MUST have `slice` (required field per C002)

#### A.1.6 New Edge Types

| Edge Type | From | To | Direction |
|-----------|------|-----|-----------|
| `defines_goal` | Charter | Goal | Charter points to Goals |
| `supports_goal` | Architecture | Goal | Architecture points to Goal |
| `supports_goal` | Outcome | Goal | Outcome points to Goal |
| `constrains` | Architecture | Specification | Architecture points to Spec |

**Implementation:**
- Add `_create_charter_goal_edges()`
- Add `_create_architecture_edges()`
- Update `_create_outcome_edges()` to include supports_goal edges
- Edges are derived from frontmatter arrays

#### A.1.7 Updated Metadata

**Current:**
```json
{"_meta":{"version":"1.0","spec_count":54,"outcome_count":18,"brick_count":11,...}}
```

**After:**
```json
{"_meta":{"version":"2.0","charter":"Charter","goal_count":5,"architecture_count":2,"outcome_count":18,"spec_count":54,"brick_count":11,"slice_count":3,...}}
```

---

### A.2 Validation System

**Files:** `src/jig/validation/intent.py`, `src/jig/validation/bricks.py`

#### A.2.1 Charter Validation (NEW)

**Function:** `validate_charter_file(jig_config)`

**Rules:**
1. Exactly one file: `jig/Charter.md`
2. Required fields: `id`, `type`, `defines_goals`
3. `id` MUST be exactly `"Charter"`
4. `type` MUST be exactly `"charter"`
5. `defines_goals` MUST be non-empty array of `G-{number}` strings
6. Each goal in `defines_goals` MUST have matching `### G-{number}:` header in body
7. Excluded fields: `status`, `supports_goals`, `version`

**Error examples:**
```
ERROR: Charter validation failed
  File: jig/Charter.md
  Issue: defines_goals contains G-6 but no "### G-6:" header found in body
```

#### A.2.2 Goal Validation (NEW)

**Function:** `validate_goal_references(jig_config, charter_goals)`

**Rules:**
1. All goal references in Architecture `supports_goals` MUST exist in Charter
2. All goal references in Outcome `supports_goals` MUST exist in Charter
3. Goal IDs MUST match pattern `G-{number}` (not zero-padded)

**Error examples:**
```
ERROR: Invalid goal reference
  File: jig/outcomes/O-015.md
  Field: supports_goals
  Referenced: G-99
  Available: G-1, G-2, G-3, G-4, G-5
```

#### A.2.3 Architecture Validation (NEW)

**Function:** `validate_architecture_files(jig_config, charter_goals, spec_ids)`

**Rules:**
1. Files in `jig/architecture/A-*.md`
2. ID format: `A-{number}` (zero-padded to 3 digits)
3. Required fields: `id`, `type`, `title`, `status`, `supports_goals`
4. `type` MUST be exactly `"architecture"`
5. `status` MUST be one of: `draft`, `proposed`, `active`, `deprecated`
6. `supports_goals` MUST be non-empty array
7. Optional field: `constrains` (array of spec IDs)
8. If `constrains` present, all spec IDs MUST exist
9. Excluded fields: `specifies`, `depends_on`, `brick`

**Error examples:**
```
ERROR: Architecture validation failed
  File: jig/architecture/A-001.md
  Issue: supports_goals is empty - architecture must support at least one goal
```

#### A.2.4 Extended Outcome Validation

**Update:** `validate_outcome_files(jig_config)`

**New rules:**
1. Required field: `supports_goals` (non-empty array)
2. All goal references in `supports_goals` MUST exist in Charter

**Current rules (unchanged):**
- Required: id, type, title, specifies
- specifies MUST be non-empty (S-042)
- All specs in specifies MUST exist (reference integrity)

#### A.2.5 Slice Validation (C002) (NEW)

**Update:** `validate_brick_definitions(jig_config)` in `bricks.py`

**New rules:**
1. Required field: `slice`
2. `slice` MUST be one of: `server`, `harness`, `device-logic`
3. Cross-slice dependencies FORBIDDEN

**Error examples:**
```
ERROR: Missing required field 'slice'
  Brick: B-crdt-core
  File: jig/bricks.yaml

ERROR: Invalid slice value
  Brick: B-crdt-core
  Value: "core"
  Valid: server, harness, device-logic

ERROR: Cross-slice dependency forbidden
  Brick: B-crdt-core (slice=device-logic)
  Imports from: B-planes-core (slice=server)
  Rule: Slices are completely independent. No cross-slice imports.
  Fix: Use INTENT specifications instead of direct code imports.
```

#### A.2.6 Slice Isolation Enforcement

**Function:** `validate_slice_isolation(bricks, impl_graph)`

**Algorithm:**
```
1. Build brick → slice mapping from bricks.yaml
2. Build unit → brick mapping from brick.units
3. For each edge in implementation graph where type="imports":
   a. Get source_brick = unit_to_brick[source]
   b. Get target_brick = unit_to_brick[target]
   c. If source_brick.slice != target_brick.slice:
      - VIOLATION: cross-slice import detected
4. Return all violations with file locations
```

---

### A.3 Configuration Schema

**File:** `src/jig/config/schema.py`

#### A.3.1 New Path Configuration

**Current PathsConfig fields:**
- `jig_root`
- `specifications`
- `outcomes`
- `bricks`
- `generated`

**New fields:**
- `charter` — Path to Charter.md (default: `Charter.md` relative to jig_root)
- `architecture` — Path to architecture directory (default: `architecture`)

**Implementation:**
```python
@dataclass
class PathsConfig:
    jig_root: Path
    charter: Path           # NEW
    architecture: Path      # NEW
    specifications: Path
    outcomes: Path
    bricks: Path
    generated: Path
```

#### A.3.2 Slice Enum

**New constant:**
```python
VALID_SLICES = frozenset({"server", "harness", "device-logic"})
```

---

### A.4 CLI Commands

**File:** `src/jig/cli/main.py`

#### A.4.1 Show Command Extensions

**Current `jigy show` subcommands:**
- `jigy show specs`
- `jigy show outcomes`
- `jigy show bricks`
- `jigy show layers`

**New subcommands:**
- `jigy show charter` — Display Charter and defined goals
- `jigy show goals` — List all goals with supporting artifacts
- `jigy show architecture` — List architecture documents
- `jigy show architecture <A-###>` — Show specific architecture

**Example output: `jigy show goals`**
```
Goals defined in Charter:

G-1: Discover Correct Design Intent
  Supported by: A-001, A-002
  Outcomes: O-001, O-005, O-012

G-2: Model System Behavior
  Supported by: A-001
  Outcomes: O-002, O-003, O-007

G-3: Verify Implementation Completeness
  ...
```

#### A.4.2 Slices Commands (C002)

**New commands:**

**`jigy slices`** — List all slices with brick counts
```
Slices (3):

server (5 bricks)
  Layer 0: B-server-transport
  Layer 1: B-planes-core, B-enforcer
  Layer 2: B-simops

harness (4 bricks)
  Layer 0: B-harness-transport
  Layer 1: B-effect-executor, B-timers
  Layer 2: B-gui

device-logic (6 bricks)
  Layer 0: B-protocol-codecs, B-elc
  Layer 1: B-crdt-core, B-operations
  Layer 2: B-igp, B-replicator
```

**`jigy slices <slice_id>`** — Show all bricks in a specific slice

**`jigy matrix`** — Show 2D Layer × Slice grid
```
              │  server  │  harness  │  device-logic  │
──────────────┼──────────┼───────────┼────────────────┤
Layer 2       │  B-sim   │  B-gui    │  B-igp,B-rep   │
Layer 1       │  B-pln   │  B-eff    │  B-crdt,B-ops  │
Layer 0       │  B-trn   │  B-trn    │  B-codec,B-elc │
```

#### A.4.3 Validate Command Extensions

**Current `jigy validate`:**
- Validates specifications
- Validates outcomes
- Validates bricks
- Validates decorators

**Extensions:**
- Validate charter (new)
- Validate goals (new)
- Validate architecture (new)
- Validate slice isolation (new)

**New flags:**
- `--charter` — Validate charter only
- `--architecture` — Validate architecture only
- `--slices` — Validate slice isolation only

---

### A.5 Graph File Updates

**File:** `jig/generated/intent-graph.ndjson`

#### A.5.1 Version Bump

Schema version: `1.0` → `2.0`

#### A.5.2 New Node Types in Output

Order in NDJSON file:
1. `_meta` (updated with new counts)
2. Charter node (single)
3. Goal nodes (G-1, G-2, ...)
4. Architecture nodes (A-001, A-002, ...)
5. Outcome nodes (with supports_goals)
6. Specification nodes (unchanged)
7. Brick nodes (with slice)
8. Edge records (expanded)

#### A.5.3 Edge Record Format

```json
{"source":"Charter","target":"G-1","type":"defines_goal"}
{"source":"A-001","target":"G-1","type":"supports_goal"}
{"source":"A-001","target":"S-116","type":"constrains"}
{"source":"O-001","target":"G-2","type":"supports_goal"}
{"source":"O-001","target":"S-001","type":"specifies"}
```

---

## PART B: Meta Changes (INTENT Documents)

These are changes to the JIG intent documents themselves — the specifications, outcomes, and configuration that guide JIG's implementation.

### B.1 Charter Creation

**Action:** Create `jig/Charter.md`

**Source:** Consolidate from current `jig/Constitution.md` and `jig/Constitution_v2.md`

**Required content:**
```yaml
---
id: Charter
type: charter
defines_goals: [G-1, G-2, G-3, G-4, G-5]
---

# JIG Charter

## Charter Goals

### G-1: Discover Correct Design Intent
[Description]

### G-2: Model System Behavior
[Description]

### G-3: Verify Implementation Completeness
[Description]

### G-4: Enable Traceability
[Description]

### G-5: Support Evolution
[Description]
```

**Migration:** Constitution.md → Charter.md is a rename + frontmatter addition

---

### B.2 Architecture Documents

**Action:** Create `jig/architecture/` directory with initial documents

#### B.2.1 A-001: Four-Component Separation

Already exists at `jig/architecture/A-002.md` — needs renumbering and frontmatter update.

```yaml
---
id: A-001
type: architecture
title: Four-Component Separation
status: active
supports_goals: [G-1, G-2]
constrains: [S-001, S-002, S-003]
---
```

#### B.2.2 A-002: Intent Hierarchy

New document defining the G-A-O-S-C-T pyramid.

```yaml
---
id: A-002
type: architecture
title: Intent Hierarchy (G-A-O-S-C-T Pyramid)
status: active
supports_goals: [G-1, G-3, G-4]
constrains: []
---
```

---

### B.3 Outcome Updates

**Action:** Add `supports_goals` to all existing outcomes

**Current format:**
```yaml
---
id: O-001
type: outcome
title: ...
specifies: [S-001, S-002]
---
```

**Updated format:**
```yaml
---
id: O-001
type: outcome
title: ...
supports_goals: [G-2, G-4]
specifies: [S-001, S-002]
---
```

**Affected files:** All 18 files in `jig/outcomes/O-*.md`

**Goal assignment:** Each outcome must be mapped to at least one goal based on semantic analysis.

---

### B.4 Brick Updates (C002)

**Action:** Add `slice` field to all bricks in `jig/bricks.yaml`

**Current format:**
```yaml
bricks:
  - id: B-decorators
    name: JIG Core Decorators
    layer: 0
    units:
      - M-jig.__init__
```

**Updated format:**
```yaml
bricks:
  - id: B-decorators
    name: JIG Core Decorators
    layer: 0
    slice: device-logic    # NEW
    units:
      - M-jig.__init__
```

**Affected:** All 11 bricks in `jig/bricks.yaml`

**Note for JIG itself:** JIG tooling is NOT part of ASE's server/harness/device-logic slices. Options:
1. JIG uses a fourth slice: `tooling` (extends enum)
2. JIG is exempt from slice assignment (tooling lives outside the pyramid)
3. JIG uses `device-logic` as a catch-all for single-component projects

**Recommendation:** Option 2 — JIG tooling is exempt. The three slices are ASE architectural constants, not JIG constants. JIG validates slices but doesn't require them for its own codebase.

---

### B.5 New Specifications

New specifications needed to cover the extended functionality:

#### B.5.1 Charter Specifications

| ID | Title | Description |
|----|-------|-------------|
| S-072 | Charter file structure | Charter MUST be single file at jig/Charter.md |
| S-073 | Charter defines_goals field | Charter MUST have defines_goals array |
| S-074 | Goal header format | Goals MUST have `### G-{number}:` headers in Charter body |
| S-075 | Goal ID format | Goal IDs MUST match `G-{number}` pattern |

#### B.5.2 Architecture Specifications

| ID | Title | Description |
|----|-------|-------------|
| S-076 | Architecture file location | Architecture files MUST be in jig/architecture/A-*.md |
| S-077 | Architecture ID format | Architecture IDs MUST match `A-{NNN}` (zero-padded) |
| S-078 | Architecture supports_goals required | Architecture MUST have non-empty supports_goals |
| S-079 | Architecture constrains references | constrains field MUST reference existing specs |

#### B.5.3 Intent Graph Specifications

| ID | Title | Description |
|----|-------|-------------|
| S-080 | Charter node in intent graph | Intent graph MUST include Charter node |
| S-081 | Goal nodes in intent graph | Intent graph MUST include Goal nodes |
| S-082 | Architecture nodes in intent graph | Intent graph MUST include Architecture nodes |
| S-083 | defines_goal edges | Intent graph MUST include Charter→Goal edges |
| S-084 | supports_goal edges | Intent graph MUST include A/O→Goal edges |
| S-085 | constrains edges | Intent graph MUST include A→S edges |

#### B.5.4 Slice Specifications (C002)

| ID | Title | Description |
|----|-------|-------------|
| S-086 | Brick slice field required | Bricks MUST have slice field |
| S-087 | Slice enum values | slice MUST be one of: server, harness, device-logic |
| S-088 | Cross-slice isolation | Cross-slice dependencies are forbidden |
| S-089 | Slice validation in jigy validate | jigy validate MUST check slice isolation |
| S-090 | jigy slices command | CLI MUST provide slices listing command |
| S-091 | jigy matrix command | CLI MUST provide layer×slice matrix command |

---

### B.6 New Outcomes

New outcomes to group the new specifications:

| ID | Title | supports_goals | specifies |
|----|-------|----------------|-----------|
| O-023 | Charter establishes project goals | [G-1] | [S-072, S-073, S-074, S-075] |
| O-024 | Architecture constrains specifications | [G-1, G-4] | [S-076, S-077, S-078, S-079] |
| O-025 | Intent graph captures full hierarchy | [G-3, G-4] | [S-080, S-081, S-082, S-083, S-084, S-085] |
| O-026 | Slices enforce component isolation | [G-2] | [S-086, S-087, S-088, S-089, S-090, S-091] |

---

## PART C: Work Units

Atomic work packages for implementation:

### WU-C001: Create Charter Infrastructure

**Scope:**
- Create `jig/Charter.md` from Constitution.md
- Add YAML frontmatter with defines_goals
- Add goal headers in markdown body
- Archive Constitution.md → jig/old/

**Specs:** S-072, S-073, S-074, S-075
**Outcome:** O-023

---

### WU-C002: Create Architecture Infrastructure

**Scope:**
- Create `jig/architecture/` directory
- Create A-001.md (Four-Component Separation)
- Create A-002.md (Intent Hierarchy)
- Add YAML frontmatter to each

**Specs:** S-076, S-077, S-078, S-079
**Outcome:** O-024

---

### WU-C003: Update Outcome Documents

**Scope:**
- Add `supports_goals` to all 18 existing outcomes
- Map each outcome to appropriate goals
- Validate goal references

**Specs:** (existing S-018, S-042)
**Outcome:** (existing O-005)

---

### WU-C004: Charter Validation

**Scope:**
- Add `validate_charter_file()` to `src/jig/validation/intent.py`
- Add `_load_charter_data()` helper
- Add `_extract_goal_headers()` helper
- Integrate into validation pipeline

**Specs:** S-072, S-073, S-074
**Outcome:** O-023

---

### WU-C005: Architecture Validation

**Scope:**
- Add `validate_architecture_files()` to `src/jig/validation/intent.py`
- Validate ID format, required fields, goal references
- Validate constrains references if present
- Integrate into validation pipeline

**Specs:** S-076, S-077, S-078, S-079
**Outcome:** O-024

---

### WU-C006: Goal Reference Validation

**Scope:**
- Add `validate_goal_references()` to `src/jig/validation/intent.py`
- Check Architecture supports_goals against Charter
- Check Outcome supports_goals against Charter
- Report invalid goal references

**Specs:** S-075
**Outcome:** O-023

---

### WU-C007: Intent Graph - Charter and Goals

**Scope:**
- Add `_load_charter_node()` to generator.py
- Add `_load_goal_nodes()` to generator.py
- Add `_create_charter_goal_edges()`
- Update metadata with charter and goal_count

**Specs:** S-080, S-081, S-083
**Outcome:** O-025

---

### WU-C008: Intent Graph - Architecture

**Scope:**
- Add `_load_architecture_nodes()` to generator.py
- Add `_create_architecture_edges()` for supports_goal and constrains
- Update metadata with architecture_count

**Specs:** S-082, S-084, S-085
**Outcome:** O-025

---

### WU-C009: Intent Graph - Extended Outcomes

**Scope:**
- Update `_load_outcome_nodes()` to include supports_goals
- Update `_create_outcome_edges()` to add supports_goal edges
- Maintain backward compatibility with specifies edges

**Specs:** S-084
**Outcome:** O-025

---

### WU-C010: Configuration Schema Updates

**Scope:**
- Add `charter` path to PathsConfig
- Add `architecture` path to PathsConfig
- Update path resolution logic
- Update defaults in schema.py

**Specs:** (infrastructure, no new spec)
**Outcome:** O-025

---

### WU-C011: CLI - Show Charter/Goals/Architecture

**Scope:**
- Add `jigy show charter` subcommand
- Add `jigy show goals` subcommand
- Add `jigy show architecture` subcommand
- Add `jigy show architecture <A-###>` variant

**Specs:** (infrastructure, covered by existing S-060)
**Outcome:** O-025

---

### WU-C012: Brick Schema - Add Slice Field

**Scope:**
- Update brick validation to require `slice` field
- Add VALID_SLICES constant
- Validate slice is in enum
- Update bricks.yaml with slice for all bricks

**Specs:** S-086, S-087
**Outcome:** O-026

---

### WU-C013: Slice Isolation Validation

**Scope:**
- Add `validate_slice_isolation()` to bricks.py
- Build brick→slice and unit→brick mappings
- Scan implementation graph for cross-slice imports
- Report violations with fix suggestions

**Specs:** S-088, S-089
**Outcome:** O-026

---

### WU-C014: Intent Graph - Slices in Bricks

**Scope:**
- Update `_load_brick_nodes()` to include slice field
- Update metadata with slice_count
- Bump schema version to 2.0

**Specs:** S-086
**Outcome:** O-026

---

### WU-C015: CLI - Slice Commands

**Scope:**
- Add `jigy slices` command
- Add `jigy slices <slice_id>` variant
- Add `jigy matrix` command
- Format output for terminal display

**Specs:** S-090, S-091
**Outcome:** O-026

---

### WU-C016: Create New Specifications

**Scope:**
- Create S-072 through S-091 (20 new specs)
- Place in jig/specifications/
- Add to outcomes O-023 through O-026

**Specs:** (meta - creates specs)
**Outcome:** O-023, O-024, O-025, O-026

---

### WU-C017: Create New Outcomes

**Scope:**
- Create O-023, O-024, O-025, O-026
- Place in jig/outcomes/
- Include supports_goals for each

**Specs:** (meta - creates outcomes)
**Outcome:** (self-referential)

---

## PART D: Dependency Graph

```
                            WU-C016 (specs)
                                 │
                                 ▼
                            WU-C017 (outcomes)
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
     WU-C001                 WU-C002                 WU-C003
   (Charter.md)          (Architecture/)         (Outcome updates)
         │                       │                       │
         └───────────┬───────────┘                       │
                     │                                   │
                     ▼                                   │
                 WU-C010                                 │
             (Config schema)                             │
                     │                                   │
    ┌────────────────┼────────────────┐                 │
    │                │                │                 │
    ▼                ▼                ▼                 │
WU-C004          WU-C005          WU-C006 ◄─────────────┘
(Charter         (Architecture    (Goal ref
 validation)      validation)      validation)
    │                │                │
    └────────────────┴────────────────┘
                     │
                     ▼
              WU-C007, WU-C008, WU-C009
             (Intent graph generation)
                     │
                     ▼
                 WU-C011
            (CLI show commands)


                 WU-C012
            (Brick slice field)
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
     WU-C013                 WU-C014
(Slice isolation)      (Graph slice field)
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
                 WU-C015
            (CLI slice commands)
```

---

## PART E: Risks and Mitigations

### E.1 Breaking Change: Outcome supports_goals

**Risk:** All 18 existing outcomes need supports_goals field. Validation will fail until migration complete.

**Mitigation:**
- Make supports_goals validation opt-in with `--strict` flag initially
- Provide migration script to add placeholder `supports_goals: []`
- Complete migration before making it required

### E.2 Brick Slice Assignment

**Risk:** Current bricks may not cleanly map to server/harness/device-logic.

**Mitigation:**
- JIG tooling is exempt from slice requirements (it's a tool, not an ASE component)
- For ASE, analyze imports to determine correct slice
- Allow `slice: null` during migration period

### E.3 Cross-Slice Violations

**Risk:** Existing code may have cross-slice imports that are now forbidden.

**Mitigation:**
- Run validation in audit mode first (report but don't fail)
- Identify violations and plan refactoring
- Extract shared code to INTENT specifications
- Enable strict mode after cleanup

### E.4 Constitution → Charter Migration

**Risk:** Constitution.md has different structure than required Charter.md.

**Mitigation:**
- Manual curation required (not automated)
- Draft Charter.md alongside Constitution.md
- Validate Charter.md before removing Constitution.md

---

## PART F: Success Criteria

### F.1 Functional Criteria

1. `jigy validate` passes with Charter, Architecture, and slice validation
2. `jigy rebuild intent` generates graph with Charter, Goal, Architecture nodes
3. `jigy show charter` displays charter and goals
4. `jigy show architecture` lists all architecture documents
5. `jigy slices` displays slice breakdown
6. `jigy matrix` displays layer × slice grid
7. Cross-slice imports are detected and reported

### F.2 Document Criteria

1. Charter.md exists with valid frontmatter
2. At least 2 Architecture documents exist
3. All Outcomes have supports_goals
4. All Bricks have slice (or explicit exemption)
5. Specifications S-072 through S-091 exist
6. Outcomes O-023 through O-026 exist

### F.3 Graph Criteria

1. Intent graph version is 2.0
2. Charter node present with defines_goals
3. Goal nodes present (G-1 through G-N)
4. Architecture nodes present with supports_goals and constrains
5. Outcome nodes include supports_goals
6. Brick nodes include slice
7. All new edge types present: defines_goal, supports_goal, constrains

---

## References

- C001_PROPOSAL_JIG-Core-Artifacts-Contract.md
- C002_PROPOSAL_Bricks-with-Slices.md
- Current implementation: src/jig/
- Current intent documents: jig/
