---
title: "JIG Core Artifacts Contract"
type: exploration
status: implemented
decision: "Adopted as A-001 JIG Core Architecture"
created: 1767412904
created_human: "2026-01-02 22:01 CST"
parent: null
children: ['[[C003_SCOPE_Extended-Intent-Hierarchy-and-Towers]]']
---
# JIG Core Artifacts Contract

**Version:** 2.0
**Status:** Active
**Date:** 2025-12-29
**Supersedes:** docs/jig/old/contract_JIG-Core-Artifacts.md

---

## Context

The JIG system measures alignment between intent (specifications), implementation (code), and verification (tests). This contract defines the structure of all core artifacts that form the foundation for tooling, automation, and analysis.

Version 2.0 extends the original S-F-T triangle to include Charter, Goals, and Architecture documents, creating a complete intent hierarchy.

---

## Core Principle

**The G-A-O-S-C-T pyramid:**

```
                      CHARTER
                    (defines G-#)
                    /          \
                   /            \
          ARCHITECTURE         OUTCOMES
               A-###              O-###
           supports_goals     supports_goals
           constrains ──┐    ┌── specifies
                        │    │
                        ▼    ▼
                    SPECIFICATIONS
                         S-###
                       /      \
                      /        \
                 verifies   implements
                    /            \
                   /              \
               TESTS              CODE
                T-###              C-###
```

Six relationships define alignment:

| Relationship | Direction | Meaning |
|--------------|-----------|---------|
| Charter `defines_goals` | Parent → Child | Charter defines which goals exist |
| Architecture `supports_goals` | Child → Parent | Which goals this architecture supports |
| Architecture `constrains` | Parent → Child | Which specs this architecture constrains |
| Outcome `supports_goals` | Child → Parent | Which goals this outcome supports |
| Outcome `specifies` | Parent → Child | Which specs this outcome decomposes into |
| Code `implements` | Child → Parent | Which specs this code implements |
| Test `verifies` | Child → Parent | Which specs this test verifies |

---

## Core Artifacts

The system consists of exactly **seven** core artifact types:

| # | Artifact | Format | Count | Authored By |
|---|----------|--------|-------|-------------|
| 1 | Charter | `.md` with YAML frontmatter | Single | Human |
| 2 | Architecture | `.md` with YAML frontmatter | Multiple | Human |
| 3 | Outcome | `.md` with YAML frontmatter | Multiple | Human |
| 4 | Specification | `.md` with YAML frontmatter | Multiple | Human |
| 5 | Brick definitions | `bricks.yaml` | Single | Human |
| 6 | @jig annotations | In source code | Multiple | Human |
| 7 | Graph files | `.ndjson` | Multiple | Machine |

---

## 1. Charter

**Location:** `jig/Charter.md` (single file)

**Purpose:** Single source of truth for project goals and principles. The root of the intent hierarchy.

### Required YAML Frontmatter

```yaml
---
id: Charter
type: charter
defines_goals: [G-001, G-002, G-003, G-004, G-005]
---
```

### Field Contract

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | YES | Value SHALL be exactly `"Charter"` |
| `type` | string | YES | Value SHALL be exactly `"charter"` |
| `defines_goals` | array[string] | YES | Goal IDs defined by this Charter |

### Excluded Fields

- `status` — Charter is always active
- `supports_goals` — Charter defines goals, it doesn't support them
- `version` — Keep in markdown body, not frontmatter

### Markdown Body

Goals SHALL be defined in the markdown body using this header format:

```markdown
## Charter Goals

### G-001: Discover Correct Design Intent
[Description of goal]

### G-002: Model System Behavior
[Description of goal]
```

Goal IDs in `defines_goals` SHALL match `### G-{number}:` headers in the body.

---

## 2. Architecture Documents

**Location:** `jig/architecture/A-{number}_{Title_Snake_Case}.md`

**Purpose:** Define structural constraints that shape specifications. Architecture documents establish boundaries, interfaces, and invariants.

### Required YAML Frontmatter

```yaml
---
id: A-001
type: architecture
title: Device Logic Contract
status: active
supports_goals: [G-001, G-005]
constrains: [S-116, S-117, S-118]
---
```

### Field Contract

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | YES | Format: `A-{number}` (e.g., `A-001`, `A-007`) |
| `type` | string | YES | Value SHALL be exactly `"architecture"` |
| `title` | string | YES | Human-readable title |
| `status` | string | YES | One of: `draft`, `proposed`, `active`, `deprecated` |
| `supports_goals` | array[string] | YES | Goal IDs this architecture supports |
| `constrains` | array[string] | NO | Spec IDs this architecture constrains. MAY be empty `[]` or omitted. |

### Excluded Fields

- `specifies` — Architecture constrains, it does not specify (that's Outcomes)
- `depends_on` — Creates circular dependency risk
- `brick` — Not applicable to intent documents

### Naming Convention

- Files SHALL be named `A-{NNN}_{Title_Snake_Case}.md`
- Examples: `A-001_Device_Logic_Contract.md`, `A-002_Intent_Hierarchy.md`
- Numbers SHALL be zero-padded to 3 digits
- Title in filename SHALL match frontmatter `title` field (validation warns on drift)
- ID in frontmatter is canonical — references use `A-001`, not the filename

---

## 3. Outcome Files

**Location:** `jig/outcomes/O-{number}_{Title_Snake_Case}.md`

**Purpose:** Define business value and decompose into specifications. Outcomes answer "why does this matter?"

### Required YAML Frontmatter

```yaml
---
id: O-001
type: outcome
title: Airspace messages use single, semantic operation type
supports_goals: [G-002, G-004]
specifies: [S-001, S-002, S-003, S-004]
---
```

### Field Contract

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | YES | Format: `O-{number}` (e.g., `O-001`, `O-045`) |
| `type` | string | YES | Value SHALL be exactly `"outcome"` |
| `title` | string | YES | Human-readable title |
| `supports_goals` | array[string] | YES | Goal IDs this outcome supports |
| `specifies` | array[string] | YES | Spec IDs this outcome decomposes into. MAY be empty `[]`. |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | One of: `draft`, `proposed`, `active`, `deprecated` |

### Excluded Fields

- `constrains` — Outcomes specify, they don't constrain (that's Architecture)
- `brick` — Not applicable to intent documents

### Naming Convention

- Files SHALL be named `O-{NNN}_{Title_Snake_Case}.md`
- Examples: `O-001_Secure_Authentication.md`, `O-015_Real_Time_Sync.md`
- Numbers SHALL be zero-padded to 3 digits
- Title in filename SHALL match frontmatter `title` field (validation warns on drift)
- ID in frontmatter is canonical — references use `O-001`, not the filename

---

## 4. Specification Files

**Location:** `jig/specifications/S-{number}_{Title_Snake_Case}.md`

**Purpose:** Define technical requirements. Specifications are the target of both `constrains` (from Architecture) and `specifies` (from Outcomes).

### Required YAML Frontmatter

```yaml
---
id: S-001
type: specification
title: BikeState messages use operation_type field directly
status: active
---
```

### Field Contract

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | YES | Format: `S-{number}` (e.g., `S-001`, `S-169`) |
| `type` | string | YES | Value SHALL be exactly `"specification"` |
| `title` | string | YES | Human-readable title |
| `status` | string | YES | One of: `draft`, `proposed`, `active`, `deprecated` |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `subsystem` | string | Domain grouping (e.g., `airspace`, `crdt`, `protocol`) |
| `created` | string | ISO date (e.g., `2025-11-19`) |

### Excluded Fields

- `brick` — Creates circular dependency
- `depends_on` — Not part of core relationships
- `constrained_by` — Derived from Architecture `constrains` field
- `specified_by` — Derived from Outcome `specifies` field
- `supports_goals` — Specs don't directly support goals; they are constrained/specified by documents that do

### Naming Convention

- Files SHALL be named `S-{NNN}_{Title_Snake_Case}.md`
- Examples: `S-001_Token_Expiration.md`, `S-042_CRDT_Value_Observation.md`
- Numbers SHALL be zero-padded to 3 digits
- Title in filename SHALL match frontmatter `title` field (validation warns on drift)
- ID in frontmatter is canonical — references use `S-001`, not the filename

### Important Note

Specifications do NOT point upward. The relationships TO specs are:
- Architecture `constrains: [S-###]` — Architecture points to Spec
- Outcome `specifies: [S-###]` — Outcome points to Spec

These relationships are derived by querying Architecture and Outcome documents.

---

## 5. Brick Definitions

**Location:** `jig/bricks.yaml` (single file)

**Purpose:** Partition code into architectural units.

### Structure

```yaml
bricks:
  - id: B-crdt
    name: CRDT Primitives
    layer: 0
    units:
      - M-ase.crdt.lww_register
      - M-ase.crdt.or_set

  - id: B-protocol
    name: Protocol Layer
    layer: 1
    units:
      - M-ase.protocol.l3_pdu
      - M-ase.protocol.l4_message
```

### Field Contract

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | YES | Format: `B-{kebab-case}` (e.g., `B-crdt`, `B-auth`) |
| `name` | string | YES | Human-readable name |
| `layer` | integer | YES | Non-negative integer (0, 1, 2, ...) |
| `units` | array[string] | YES | Implementation graph node IDs (M-, C-, F- prefixes) |

### ID Format

- SHALL use lowercase letters, numbers, and hyphens only
- SHALL match pattern: `B-[a-z0-9-]+`
- SHALL be semantic and descriptive (e.g., `B-crdt`, not `B-001`)

### Layer Semantics

- `layer: 0` — Foundation bricks; MAY depend on other layer 0 bricks or external libraries
- `layer: N` — Bricks that depend only on bricks at layers < N

### Units Format

- `M-{module.path}` — All functions in module
- `C-{class.path}` — All methods of class
- `F-{function.path}` — Single function

### Excluded Fields

- `depends_on` — Derived from implementation graph
- `public_api` — Derived from call graph
- `specs` — Derived from C→S edges

### Constraint

Every function in the codebase SHALL belong to exactly one brick (partition constraint).

---

## 6. @jig Annotations

**Purpose:** Declare explicit relationships between code/tests and specifications.

### In Code (implements)

```python
# @jig C-ase.crdt.lww_register.LWWRegister.merge implements:S-007
def merge(self, other: 'LWWRegister[T]') -> 'LWWRegister[T]':
    ...
```

### In Tests (verifies)

```python
# @jig T-test_lww.test_merge_higher_wins verifies:S-007
def test_merge_higher_wins():
    ...
```

### Contract

- Code annotations SHALL use format `# @jig C-{path} implements:S-{number}`
- Test annotations SHALL use format `# @jig T-{path} verifies:S-{number}`
- MAY reference multiple specs: `implements:S-001,S-002`
- SHALL reference spec IDs that exist in specification files
- Code/tests without annotations have no explicit spec linkage

---

## 7. Graph Files

**Location:** `jig/generated/`

**Three graph files SHALL exist:**

```
jig/generated/intent-graph.ndjson
jig/generated/implementation-graph.ndjson
jig/generated/verification-graph.ndjson
```

**Format:** All graph files SHALL use NDJSON (Newline-Delimited JSON).

### 7.1 Intent Graph

**Generated from:**
- `jig/Charter.md` frontmatter and goal extraction
- `jig/architecture/A-*.md` frontmatter
- `jig/outcomes/O-*.md` frontmatter
- `jig/specifications/S-*.md` frontmatter
- `jig/bricks.yaml`

**Node Types:**

**Charter Node:**
```json
{"id":"Charter","type":"charter","defines_goals":["G-001","G-002","G-003","G-004","G-005"],"file":"jig/Charter.md"}
```

**Goal Node:**
```json
{"id":"G-001","type":"goal","title":"Discover Correct Design Intent","file":"jig/Charter.md"}
```

**Architecture Node:**
```json
{"id":"A-001","type":"architecture","title":"Device Logic Contract","status":"active","supports_goals":["G-001","G-005"],"constrains":["S-116","S-117"],"file":"jig/architecture/A-001_Device_Logic_Contract.md"}
```

**Outcome Node:**
```json
{"id":"O-001","type":"outcome","title":"...","supports_goals":["G-002"],"specifies":["S-001","S-002"],"file":"jig/outcomes/O-001_Secure_Authentication.md"}
```

**Specification Node:**
```json
{"id":"S-001","type":"specification","title":"...","status":"active","file":"jig/specifications/S-001.md"}
```

**Brick Node:**
```json
{"id":"B-crdt","type":"brick","name":"CRDT Primitives","layer":0,"file":"jig/bricks.yaml"}
```

### 7.2 Implementation Graph

**Generated from:**
- Python source files (AST parsing)
- `@jig ... implements:` annotations

**Node Schema:**

```json
{"id":"C-ase.crdt.lww.LWWRegister.merge","type":"code","file":"src/ase/crdt/lww.py","implements":["S-007"],"calls":["C-ase.crdt.elc.EraLamportClock.__lt__"]}
```

### 7.3 Verification Graph

**Generated from:**
- Test discovery
- Coverage analysis
- `@jig ... verifies:` annotations

**Node Schema:**

```json
{"id":"T-test_lww.test_merge","type":"test","file":"test/crdt/test_lww.py","verifies":["S-007"],"covers":["C-ase.crdt.lww.LWWRegister.merge"]}
```

---

## ID Format Contract

| Type | Format | Example | Notes |
|------|--------|---------|-------|
| Charter | `Charter` | `Charter` | Singleton |
| Goal | `G-{number}` | `G-001`, `G-005` | From Charter, zero-padded to 3 digits |
| Architecture | `A-{number}` | `A-001`, `A-007` | Zero-padded to 3 digits |
| Outcome | `O-{number}` | `O-001`, `O-045` | Zero-padded to 3 digits |
| Specification | `S-{number}` | `S-001`, `S-169` | Zero-padded to 3 digits |
| Brick | `B-{kebab-case}` | `B-crdt`, `B-protocol` | Semantic kebab-case |
| Code | `C-{path}` | `C-ase.crdt.lww.merge` | Fully-qualified path |
| Test | `T-{path}` | `T-test_lww.test_merge` | Test path |

---

## File Structure Contract

```
project-root/
├── jig/
│   ├── Charter.md                              # Root document (singleton)
│   ├── architecture/                           # Architecture documents
│   │   ├── A-001_Device_Logic_Contract.md
│   │   ├── A-002_Intent_Hierarchy.md
│   │   └── ...
│   ├── outcomes/                               # Outcome documents
│   │   ├── O-001_Secure_Authentication.md
│   │   ├── O-002_Real_Time_Sync.md
│   │   └── ...
│   ├── specifications/                         # Specification documents
│   │   ├── S-001_Token_Expiration.md
│   │   ├── S-002_Password_Hashing.md
│   │   └── ...
│   ├── bricks.yaml                             # Brick definitions
│   └── generated/                              # Machine-generated graphs
│       ├── intent-graph.ndjson
│       ├── implementation-graph.ndjson
│       └── verification-graph.ndjson
├── src/
│   └── [source code with @jig annotations]
└── test/
    └── [test code with @jig annotations]
```

### Filename Convention

All JIG artifact files (except Charter.md and bricks.yaml) include the title in the filename:

| Artifact | Format | Example |
|----------|--------|---------|
| Architecture | `A-{NNN}_{Title_Snake_Case}.md` | `A-001_Device_Logic_Contract.md` |
| Outcome | `O-{NNN}_{Title_Snake_Case}.md` | `O-001_Secure_Authentication.md` |
| Specification | `S-{NNN}_{Title_Snake_Case}.md` | `S-001_Token_Expiration.md` |

**Rules:**
- Title in filename SHALL match frontmatter `title` field
- ID in frontmatter is canonical — code references use `S-001`, not the filename
- Validation SHOULD warn when filename title drifts from frontmatter title
- Snake_Case preserves word boundaries and avoids case-sensitivity issues

**Rationale:**
- Discoverability: `ls jig/specifications/` shows what specs exist without reading files
- Navigation: Fuzzy finders can search by concept, not just ID
- Git diffs: PRs show meaningful names, not just `S-042.md`

---

## Validation Contract

Implementations SHALL validate:

### Charter Validation
1. Charter `id` SHALL be exactly `"Charter"`
2. Charter `defines_goals` SHALL be non-empty
3. All goal IDs in `defines_goals` SHALL match `G-{number}` format
4. All goal IDs SHALL have corresponding `### G-{number}:` headers in body

### Architecture Validation
5. Architecture `id` SHALL match pattern `A-[0-9]{3}`
6. Architecture `supports_goals` SHALL be non-empty
7. Architecture `supports_goals` SHALL reference goals defined in Charter
8. Architecture `constrains` (if present) SHALL reference existing spec IDs

### Outcome Validation
9. Outcome `id` SHALL match pattern `O-[0-9]{3}`
10. Outcome `supports_goals` SHALL be non-empty
11. Outcome `supports_goals` SHALL reference goals defined in Charter
12. Outcome `specifies` SHALL reference existing spec IDs

### Specification Validation
13. Specification `id` SHALL match pattern `S-[0-9]{3}`
14. Specification `status` SHALL be one of: `draft`, `proposed`, `active`, `deprecated`

### Brick Validation
15. Brick `id` SHALL match pattern `B-[a-z0-9-]+`
16. Brick `layer` SHALL be non-negative integer
17. Brick `units` SHALL reference nodes in implementation graph
18. Every function SHALL belong to exactly one brick (partition)
19. Brick dependencies SHALL respect layer hierarchy (DAG)

### Reference Integrity
20. All `@jig ... implements:S-###` SHALL reference existing specs
21. All `@jig ... verifies:S-###` SHALL reference existing specs

---

## Derivation Contract

The following data SHALL be computed on demand, NOT stored:

**Derived from intent-graph:**
- Which specs are constrained by which architectures (inverse of `constrains`)
- Which specs are specified by which outcomes (inverse of `specifies`)
- Goal coverage (which goals have supporting architectures/outcomes)

**Derived from implementation-graph:**
- Brick dependencies (from call graph)
- Public APIs (functions called from outside their brick)

**Derived from verification-graph:**
- Coverage percentages
- Spec verification status

**Rationale:** Stored derived data drifts from source of truth. Compute on demand ensures freshness.

---

## Relationship Summary

| From | Field | To | Cardinality |
|------|-------|----|----|
| Charter | `defines_goals` | Goal | 1:N |
| Architecture | `supports_goals` | Goal | N:M |
| Architecture | `constrains` | Specification | N:M |
| Outcome | `supports_goals` | Goal | N:M |
| Outcome | `specifies` | Specification | N:M |
| Code | `implements` | Specification | N:M |
| Test | `verifies` | Specification | N:M |
| Test | `covers` | Code | N:M |

**Direction convention:**
- Downward (decomposition): Parent lists children (`defines_goals`, `constrains`, `specifies`)
- Upward (support): Child lists parents (`supports_goals`)
- Implementation: Code/Tests list specs (`implements`, `verifies`)

---

## Migration from V1

1. **Add Charter frontmatter** — Add `defines_goals` field
2. **Update Architecture** — Add required `supports_goals` field
3. **Update Outcomes** — Add required `supports_goals` field
4. **Rename Goal references** — Change `[1, 5]` to `[G-001, G-005]`
5. **Regenerate intent-graph** — Include Charter and Goal nodes
6. **Validate** — Run validation for new rules

---

## Compliance

All future work SHALL comply with this contract. Deviations SHALL require explicit architectural decision superseding this document.

Tools, automation, and analysis SHALL treat this contract as normative.

---

## References

- **V1 Contract:** docs/jig/old/contract_JIG-Core-Artifacts.md
- **Charter:** jig/Charter.md
- **Architecture Documents:** jig/architecture/A-*.md
