# Shared Artifacts and Brick Boundaries

**Question:** How do shared artifacts like `graph-index.json` fit into the Brick model when multiple Bricks need to touch them?

---

## The Challenge

`graph-index.json` is accessed by multiple Bricks:

| Brick | How It Touches graph-index.json |
|-------|--------------------------------|
| **Index Builder** | Creates, writes, updates |
| **Graph Core** | Reads, loads, deserializes into domain model |
| **CLI (index command)** | Triggers rebuild, shows diff |
| **Validator** | May read for validation |
| **Annotation Validator** | May consult for node existence |

**Problem:** If Bricks should be isolated context boundaries, how can they share a file?

---

## Solution: Shared Artifacts as Interface Contracts

`graph-index.json` is not a boundary violation—it's a **Brick Interface Contract**.

### Conceptual Model

Think of shared artifacts like `graph-index.json` as:

1. **API Response Format** (in microservices)
2. **Database Schema** (in layered architecture)
3. **Message Format** (in event-driven systems)
4. **Serialized Domain Model** (in DDD)

It's the **published interface** between Bricks, not internal implementation.

---

## Ownership Model

### Single Writer, Multiple Readers

```
┌─────────────────────────────────────────────┐
│        BRICK: Index Builder (OWNER)         │
│                                             │
│  Responsibility:                            │
│  - Define schema (versioned)                │
│  - Write graph-index.json                   │
│  - Guarantee schema compliance              │
│  - Handle migrations                        │
└─────────────┬───────────────────────────────┘
              │
              │ WRITES (owns schema)
              │
              ▼
    ┌─────────────────────┐
    │  graph-index.json   │  ◄─── Shared Artifact
    │  (Interface Contract)│       (Published Interface)
    └─────────────────────┘
              │
              │ READS (consumes interface)
              │
    ┌─────────┴────────┬───────────┬─────────────┐
    │                  │           │             │
┌───▼─────────┐  ┌────▼─────┐  ┌──▼────┐  ┌────▼──────┐
│ Graph Core  │  │   CLI    │  │Validator│ │  Annot.  │
│  (PRIMARY   │  │(triggers)│  │ (audit) │ │Validator │
│   READER)   │  │          │  │         │ │ (lookup) │
└─────────────┘  └──────────┘  └─────────┘ └──────────┘
```

---

## Interface Contract Principles

### 1. Schema as Interface Definition

The structure of `graph-index.json` is a **published API contract**:

```json
{
  "version": "1.0.0",  // ← Versioned interface
  "nodes": {
    "node-id": {
      "type": "outcome",
      "title": "...",
      "subsystem": "..."
      // ... schema defined by Index Builder
    }
  },
  "edges": [...],
  "subsystems": {...}
}
```

**Owner (Index Builder) guarantees:**
- Schema compliance
- Backward compatibility
- Version migration
- Data integrity

**Consumers agree to:**
- Read-only access
- Parse versioned schema
- Handle unknown fields gracefully
- Not bypass the contract

---

### 2. Single Source of Truth

- **Index Builder** is the **authoritative writer**
- All writes go through Index Builder Brick
- No other Brick modifies the file directly
- Index Builder enforces schema and validation

This prevents:
- Race conditions
- Schema drift
- Inconsistent state
- Boundary violations

---

### 3. Versioned Evolution

Schema changes must be versioned:

```yaml
# In Index Builder Brick interface definition
interface:
  artifacts:
    graph-index.json:
      version: "1.0.0"
      schema: "./schemas/graph-index-v1.schema.json"
      stability: stable
      breaking_changes:
        - version: "2.0.0"
          date: "2026-01-15"
          migration: "scripts/migrate-index-v1-to-v2.py"
```

**Rules:**
- Version bumps require migration path
- Consumers must handle version field
- Breaking changes require major version
- Deprecation warnings before removal

---

### 4. Brick Context Contract Enforcement

When an agent works inside a Brick, what can it see?

#### Working in Index Builder Brick:
✅ **Can see:**
- Index Builder source code
- Write logic for graph-index.json
- Schema definition
- Build/merge algorithms
- Tests for index building

❌ **Cannot see:**
- How Graph Core reads the file
- Internal graph query logic
- CLI rendering code
- How consumers use the data

#### Working in Graph Core Brick:
✅ **Can see:**
- Graph Core source code
- Deserialization logic for graph-index.json
- Graph domain model
- Query algorithms
- Schema version handling

❌ **Cannot see:**
- How Index Builder builds the file
- Internal indexing algorithms
- Other consumers' reading logic
- CLI formatting details

**The shared artifact (`graph-index.json`) appears as:**
- **In Index Builder:** Output artifact with write responsibility
- **In Graph Core:** Input artifact with read contract
- **In CLI:** External data source (via Graph Core API, not directly)

---

## Types of Shared Artifacts

JIG has several of these. Let's categorize:

### 1. Domain Model Serialization (Owned by One Brick)

| Artifact | Owner Brick | Consumers | Type |
|----------|-------------|-----------|------|
| `graph-index.json` | Index Builder | Graph Core, CLI | Single writer, multiple readers |
| `subsystems.yaml` | Configuration | Graph Core, Index Builder | Config file (shared read) |
| Intent nodes (`.md` files) | (Human-authored) | Parser, Index Builder | External source |

### 2. Configuration (Shared Read, External Write)

| Artifact | Owner | Consumers | Type |
|----------|-------|-----------|------|
| `jig.toml` | User/Human | Configuration Brick | Read-only config |
| `.jigignore` | User/Human | Ignore Filter Brick | Read-only patterns |

### 3. Annotations (Embedded in Source)

| Artifact | Owner | Consumers | Type |
|----------|-------|-----------|------|
| `@jig` annotations | Developers (in code) | Scanner, Annot. Validator | Distributed markers |

---

## How Bricks Handle Shared Artifacts

### Pattern 1: Repository Pattern

**Example:** `graph-index.json`

```python
# Index Builder Brick (WRITER)
class GraphIndexRepository:
    def save(self, graph: Graph) -> None:
        """Write graph to graph-index.json (owns format)."""
        data = self._serialize(graph)  # Internal serialization
        write_file("graph-index.json", data)

# Graph Core Brick (READER)
class GraphIndexLoader:
    def load(self) -> Graph:
        """Load graph from graph-index.json (consumes format)."""
        data = read_file("graph-index.json")
        return self._deserialize(data)  # Knows published schema
```

**Key:** Each Brick has its own adapter/repository for the artifact. They don't share implementation, just the schema contract.

---

### Pattern 2: Facade/Adapter

**Example:** CLI doesn't touch `graph-index.json` directly

```python
# ❌ BAD: CLI Brick reading file directly
def index_diff():
    old_index = json.loads(read_file("graph-index.json"))  # Violates boundary
    new_index = build_index()
    diff(old_index, new_index)

# ✅ GOOD: CLI uses Graph Core and Index Builder APIs
def index_diff():
    current_graph = Graph.load_from_dir("jig/")  # Via Graph Core API
    rebuilt = build_graph_index(".")  # Via Index Builder API
    diff(current_graph, rebuilt)  # Both are domain objects, not JSON
```

**Key:** CLI orchestrates Bricks via their public APIs, not by touching shared files.

---

### Pattern 3: Event Sourcing / Audit Log

**Future:** If we track changes to the graph:

```
graph-index.json  ← Current state (owned by Index Builder)
.jig/events/      ← Change log (owned by Event Store Brick)
  - 2025-11-22-rebuild.json
  - 2025-11-22-add-node.json
```

Multiple Bricks can **append** events, but only Event Store Brick **reads/replays** them.

---

## Brick Definition for Shared Artifacts

Add to Brick definition files:

```yaml
# bricks/index-builder.brick.yaml
brick:
  id: BRICK-INDEX
  name: "Index Builder"

interface:
  artifacts:
    produced:
      - name: graph-index.json
        path: jig/graph-index.json
        schema: schemas/graph-index.schema.json
        version: "1.0.0"
        access: write
        stability: stable
        description: "Serialized Intent graph with nodes, edges, subsystems"

  consumed_by:
    - BRICK-GRAPH (primary reader)
    - BRICK-CLI (via Graph Core API, for diff/status)
    - BRICK-VALIDATOR (optional audit)

---

# bricks/graph-core.brick.yaml
brick:
  id: BRICK-GRAPH
  name: "Graph Core"

interface:
  artifacts:
    consumed:
      - name: graph-index.json
        path: jig/graph-index.json
        schema: schemas/graph-index.schema.json
        version: ">=1.0.0"
        access: read
        source_brick: BRICK-INDEX
        description: "Load graph structure from index"
```

---

## In Architecture Mode (Agent Designing Bricks)

When an agent operates in **Architecture Mode**, it sees:

✅ **Visible:**
- Brick definitions
- Interface contracts (including artifact schemas)
- Published APIs
- Artifact flow diagrams

❌ **Not Visible:**
- Implementation details of how Index Builder writes
- Implementation details of how Graph Core reads
- File formats (only schema contracts)

**Agent can:**
- Propose new artifacts
- Modify artifact schemas (with versioning)
- Change ownership (which Brick owns an artifact)
- Design migration paths

---

## In Implementation Mode (Agent Coding in a Brick)

When an agent works in **Implementation Mode** inside Index Builder:

✅ **Visible:**
- Index Builder source code
- Schema definition for graph-index.json
- Write/serialization logic
- Tests for index building
- **Interface contract** for the artifact (what consumers expect)

❌ **Not Visible:**
- How Graph Core deserializes the file
- How CLI uses the data
- Internal query logic in other Bricks

**Agent can:**
- Modify write logic
- Change serialization format (with schema version bump)
- Add validation before writing
- Improve performance of indexing

**Agent cannot:**
- Modify how other Bricks read the file
- Change consumer behavior
- See implementation of other Bricks

---

## Guidelines for Shared Artifacts

### ✅ Acceptable Sharing

1. **Well-defined schema** (versioned, documented)
2. **Single owner** (one Brick writes)
3. **Published interface** (part of Brick's public API)
4. **Read-only for consumers** (no modification outside owner)
5. **Version handling** (consumers handle version field)

### ❌ Boundary Violations

1. **Multiple writers** (race conditions, inconsistency)
2. **Undocumented format** (implicit coupling)
3. **Direct file manipulation** (bypassing owner Brick)
4. **Shared mutable state** (not file-based persistence)
5. **Format knowledge leak** (consumers know internal details)

---

## Examples in Other Systems

### Microservices
- **API Gateway** owns HTTP response format
- Services consume it (read-only contract)
- Schema versioning via API versions

### Databases
- **ORM layer** owns schema
- Apps read via ORM interface
- Migrations managed centrally

### Build Systems
- **Compiler** owns object file format
- **Linker** consumes object files
- Format is versioned ABI

### Git
- **git commit** owns `.git/objects/` format
- **git log** reads objects
- Format is stable, versioned

---

## Recommendation for JIG

### 1. Formalize Artifact Ownership

Create `schemas/` directory:

```
schemas/
├── graph-index.schema.json       # JSON Schema for graph-index.json
├── subsystems.schema.yaml        # Schema for subsystems.yaml
└── ostc-node.schema.yaml         # Schema for Intent node frontmatter
```

### 2. Document in Brick Definitions

Add `artifacts` section to each Brick:

```yaml
interface:
  artifacts:
    produced: [...]   # What this Brick writes
    consumed: [...]   # What this Brick reads
```

### 3. Enforce Single Writer

Add validation:
```python
# In Index Builder
def save_graph_index(graph: Graph, path: Path) -> None:
    """Only Index Builder should call this."""
    assert_caller_is_index_builder()  # Runtime check
    _write_index(graph, path)
```

### 4. Version All Artifacts

Every serialized artifact includes:
```json
{
  "version": "1.0.0",
  "schema": "graph-index",
  ...
}
```

### 5. Add to Alignment Graph

Track artifacts as nodes:

```yaml
# In Alignment Graph
artifacts:
  - id: ARTIFACT-GRAPH-INDEX
    type: artifact
    format: json
    schema: schemas/graph-index.schema.json
    owner: BRICK-INDEX
    consumers:
      - BRICK-GRAPH (read)
      - BRICK-CLI (read via Graph Core API)
```

---

## Summary

**Shared artifacts like `graph-index.json` are not violations—they're Brick interfaces.**

### Key Principles

1. **Artifacts are Interface Contracts** - Like API schemas, not internal data
2. **Single Owner** - One Brick owns writing and schema
3. **Multiple Readers** - Other Bricks consume via documented interface
4. **Versioned Evolution** - Changes require version bumps and migrations
5. **Access Control** - Owner writes, consumers read (enforced by contract)
6. **Context Scoping** - Agents see artifact from their Brick's perspective

### For graph-index.json Specifically

- **Owner:** Index Builder Brick (writes, owns schema)
- **Primary Reader:** Graph Core Brick (deserializes to domain model)
- **Secondary Readers:** CLI (via Graph Core API), Validators (audit)
- **Type:** Domain model serialization / persistence format
- **Stability:** Stable, versioned interface

This pattern applies to all shared artifacts in JIG and makes Brick boundaries **more clear**, not less—by making interfaces explicit.

---

**Related:**
- `Brick-Analysis-JIG-System.md` - Brick definitions
- `Alignment-Graph-Bricks.md` - Brick concept
- Repository Pattern (DDD)
- API Contracts (Microservices)
