# Nested Subsystems User Guide

**Version:** 1.0
**Status:** Active
**Last Updated:** 2025-11-21

This guide explains how to use nested subsystems in JIG to organize large projects with hierarchical architectural boundaries.

---

## Table of Contents

1. [Overview](#overview)
2. [When to Use Nested Subsystems](#when-to-use-nested-subsystems)
3. [Subsystem Path Notation](#subsystem-path-notation)
4. [YAML Structure](#yaml-structure)
5. [CLI Commands](#cli-commands)
6. [Best Practices](#best-practices)
7. [Examples](#examples)

---

## Overview

Nested subsystems allow you to organize your JIG Intent Graph hierarchically, reflecting the natural architecture of larger systems. Instead of a flat list of subsystems, you can nest subsystems to arbitrary depth:

```
identity
├── auth
└── user
crdt
├── ser (serialization)
└── sync (synchronization)
core
```

This provides:
- **Scalability**: Organize 20+ subsystems without overwhelming flat listings
- **Clarity**: Subsystem hierarchy reflects actual system architecture
- **Flexibility**: Analyze at both coarse-grained (parent) and fine-grained (leaf) levels
- **Better metrics**: Edges between sibling subsystems count as internal to their parent, improving coupling ratios

---

## When to Use Nested Subsystems

### Use Nested Subsystems When:

✅ **You have 10+ subsystems** and a flat structure becomes hard to navigate

✅ **Natural groupings exist** - some subsystems logically belong together (e.g., `identity.auth` and `identity.user`)

✅ **Different analysis levels are needed** - you want to analyze both the entire `crdt` subsystem and its specific `crdt.ser` component

✅ **Refactoring existing subsystems** - splitting a large subsystem into smaller ones without losing the high-level grouping

### Use Flat Subsystems When:

❌ **You have <10 subsystems** - nesting adds complexity without benefit

❌ **No clear hierarchy exists** - all subsystems are peers

❌ **Single level of abstraction** - you only need one level of grouping

---

## Subsystem Path Notation

JIG uses **dot notation** for subsystem paths, similar to Python modules or Java packages:

| Path | Description | Type |
|------|-------------|------|
| `core` | Root subsystem | Root |
| `identity` | Root subsystem | Root |
| `identity.auth` | Child of identity | Leaf |
| `identity.user` | Child of identity | Leaf |
| `crdt.ser` | Child of crdt | Leaf |
| `crdt.sync` | Child of crdt | Leaf |

**Rules:**
- Root subsystems have no dots (e.g., `core`)
- Child subsystems use dots (e.g., `identity.auth`)
- Maximum recommended depth: 3-4 levels
- Path components use lowercase with hyphens: `data-access.sql-store`

---

## YAML Structure

### graph-index.yaml

Nested subsystems are defined in `jig/graph-index.yaml`:

```yaml
version: 1.0.0
created: 2025-11-21

subsystems:
  identity:
    description: "User identity and authentication"
    subsystems:
      auth:
        description: "Authentication and authorization"
        nodes:
          - O-AUTH-001
          - S-AUTH-001
          - S-AUTH-002
      user:
        description: "User profile management"
        nodes:
          - O-USER-001
          - S-USER-001

  crdt:
    description: "CRDT implementation"
    subsystems:
      ser:
        description: "CRDT serialization"
        nodes:
          - S-CRDT-SER-001
          - S-CRDT-SER-002
      sync:
        description: "CRDT synchronization"
        nodes:
          - S-CRDT-SYNC-001

nodes:
  O-AUTH-001:
    file: jig/outcomes/O-AUTH-001.md
    type: outcome
    title: "Users authenticate securely"
    subsystem: identity.auth

  S-AUTH-001:
    file: jig/specifications/S-AUTH-001.md
    type: specification
    title: "JWT tokens with 24-hour expiration"
    subsystem: identity.auth
```

**Key Points:**
- Parent subsystems have `subsystems` field (dictionary of child subsystems)
- Leaf subsystems have `nodes` field (list of node IDs)
- **Parent subsystems cannot have direct nodes** - nodes must be in leaf subsystems
- Node `subsystem` field uses full path (e.g., `identity.auth`)

### Node Frontmatter

In your node files (`jig/outcomes/O-AUTH-001.md`), use the full path:

```yaml
---
id: O-AUTH-001
type: outcome
title: "Users authenticate securely"
subsystem: identity.auth  # Full path with dot notation
created: 2025-11-21
---

# Outcome: Secure Authentication

...
```

### Code Annotations

In your source code, use full paths in `@jig` annotations:

```python
# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:identity.auth interface:public
class JWTAuthenticator:
    """Handles JWT-based authentication"""
    # ...

# @jig C-CRDT-SER-001 implements:S-CRDT-SER-001 subsystem:crdt.ser interface:public
class CRDTSerializer:
    """Handles CRDT serialization"""
    # ...
```

---

## CLI Commands

### Status: View Hierarchical Tree

```bash
# Display hierarchical tree view (default)
jigy status

# Output:
# Intent Graph Status
# ==================
#
# Nodes: 47
# Edges: 63
#
# Subsystems (hierarchical):
# identity (15 nodes)
#   ├── auth (8 nodes)
#   └── user (7 nodes)
# crdt (20 nodes)
#   ├── ser (10 nodes)
#   └── sync (10 nodes)
# core (12 nodes)

# Display flat view (backward compatible)
jigy status --flat

# Output:
# Subsystems (flat):
# - identity.auth: 8 nodes
# - identity.user: 7 nodes
# - crdt.ser: 10 nodes
# - crdt.sync: 10 nodes
# - core: 12 nodes
```

### Graph List: Query by Subsystem

```bash
# List nodes in a parent subsystem (non-recursive, leaf nodes only)
jigy graph list --subsystem identity

# List all nodes in a subsystem tree (recursive)
jigy graph list --subsystem identity --recursive

# List nodes in a specific leaf subsystem
jigy graph list --subsystem identity.auth

# Filter by type and subsystem
jigy graph list --type specification --subsystem crdt --recursive
```

**Behavior:**
- Without `--recursive`: Lists nodes in **leaf subsystems only** (not parent nodes, since parents can't have direct nodes)
- With `--recursive`: Lists nodes from entire subtree (all children)
- Leaf subsystem paths (e.g., `identity.auth`) work with or without `--recursive`

### Decompose Metrics: Hierarchical Analysis

```bash
# Analyze entire graph
jigy decompose metrics

# Output includes hierarchical breakdown:
# Decomposability Metrics
# =======================
#
# Overall Modularity: 0.73 ✓ (target: >0.7)
#
# Subsystem Metrics:
# identity (15 nodes, 42 internal, 8 external, ratio: 5.25)
#   auth (8 nodes, 20 internal, 3 external, ratio: 6.67)
#   user (7 nodes, 18 internal, 2 external, ratio: 9.00)
#
# crdt (20 nodes, 95 internal, 5 external, ratio: 19.0) ✓
#   ser (10 nodes, 40 internal, 2 external, ratio: 20.0)
#   sync (10 nodes, 45 internal, 1 external, ratio: 45.0)

# Analyze specific subsystem subtree
jigy decompose metrics --subsystem crdt

# Analyze single leaf subsystem
jigy decompose metrics --subsystem crdt.ser
```

**Hierarchical Coupling Calculation:**
- **Internal edges**: Both endpoints within the subsystem tree (including cross-child edges)
- **External edges**: One endpoint outside the subsystem tree
- **Coupling ratio**: internal / external (higher is better)

Example: For parent subsystem `identity`:
- Edge from `identity.auth` → `identity.user`: **Internal** (both under `identity`)
- Edge from `identity.auth` → `core`: **External** (crosses out of `identity`)

This means refactoring into nested subsystems **improves metrics** by treating sibling communication as internal to the parent.

### Decompose Report: Documentation with Hierarchy

```bash
# Generate comprehensive report
jigy decompose report

# Generate report for specific subsystem
jigy decompose report --subsystem identity

# Output to file
jigy decompose report --output docs/metrics/decomposability-report.md

# YAML format
jigy decompose report --format yaml
```

---

## Best Practices

### 1. Depth Limits

**Recommended maximum depth: 3-4 levels**

✅ Good:
```
identity.auth
identity.user
```

⚠️ Acceptable but complex:
```
data.access.sql.connections.pool
```

❌ Too deep (5 levels):
```
app.features.user.profile.settings.privacy
```

**Why:** Deep nesting becomes hard to understand and type. If you need 5+ levels, reconsider your architecture.

### 2. Consistent Naming

Use consistent patterns across your subsystems:

✅ Good (verb-noun pattern):
```
crdt.serialize
crdt.synchronize
crdt.merge
```

❌ Inconsistent:
```
crdt.ser
crdt.sync-manager
crdt.merge_handler
```

### 3. Balanced Trees

Avoid unbalanced hierarchies where one parent has many children:

✅ Good (balanced):
```
identity
├── auth
└── user

data
├── sql
└── cache
```

⚠️ Avoid (unbalanced):
```
services
├── auth
├── user
├── billing
├── notifications
├── analytics
├── logging
├── metrics
└── search  # 8 children - consider grouping
```

**Fix:** Group related subsystems:
```
services
├── identity (auth, user)
├── billing
├── observability (logging, metrics, analytics)
└── features (notifications, search)
```

### 4. Migration Strategy

When refactoring from flat to nested:

1. **Start with graph-index.yaml** - restructure subsystem definitions
2. **Update node frontmatter** - change `subsystem: auth` → `subsystem: identity.auth`
3. **Update code annotations** - change `subsystem:auth` → `subsystem:identity.auth`
4. **Validate** - run `jigy validate` to catch any errors
5. **Test queries** - verify `jigy graph list --subsystem identity --recursive` works

See [MIGRATION_NESTED.md](MIGRATION_NESTED.md) for detailed migration guide.

### 5. Constraint Scoping

Constraints (X nodes) work naturally with nested subsystems:

```yaml
---
id: X-PERF-001
type: constraint
title: "API endpoints respond in <100ms"
scope:
  subsystems: [identity, crdt]  # Applies to all children of identity and crdt
---
```

This applies to `identity.auth`, `identity.user`, `crdt.ser`, and `crdt.sync` automatically.

---

## Examples

### Example 1: Microservices Architecture

```yaml
subsystems:
  api-gateway:
    description: "API gateway and routing"
    nodes: [...]

  services:
    description: "Backend microservices"
    subsystems:
      auth:
        description: "Authentication service"
        nodes: [...]
      billing:
        description: "Billing service"
        nodes: [...]
      notifications:
        description: "Notification service"
        nodes: [...]

  infrastructure:
    description: "Infrastructure and deployment"
    subsystems:
      kubernetes:
        description: "K8s manifests and configs"
        nodes: [...]
      monitoring:
        description: "Observability stack"
        nodes: [...]
```

### Example 2: Layered Architecture

```yaml
subsystems:
  presentation:
    description: "UI layer"
    subsystems:
      web:
        description: "Web frontend"
        nodes: [...]
      mobile:
        description: "Mobile app"
        nodes: [...]

  application:
    description: "Application layer"
    subsystems:
      api:
        description: "REST API"
        nodes: [...]
      business-logic:
        description: "Core business logic"
        nodes: [...]

  data:
    description: "Data layer"
    subsystems:
      repositories:
        description: "Data access layer"
        nodes: [...]
      migrations:
        description: "Database migrations"
        nodes: [...]
```

### Example 3: Feature-Based Organization

```yaml
subsystems:
  core:
    description: "Core framework"
    nodes: [...]

  features:
    description: "Application features"
    subsystems:
      user-management:
        description: "User CRUD and profiles"
        nodes: [...]
      content-publishing:
        description: "Content creation and publishing"
        nodes: [...]
      analytics:
        description: "Analytics and reporting"
        nodes: [...]

  shared:
    description: "Shared utilities"
    subsystems:
      validation:
        description: "Input validation"
        nodes: [...]
      logging:
        description: "Logging infrastructure"
        nodes: [...]
```

---

## Validation

JIG validates nested subsystem structure:

```bash
jigy validate

# Checks:
# ✓ No cycles in subsystem hierarchy
# ✓ Parent subsystems have no direct nodes (only children)
# ✓ Node subsystem paths are valid (exist in graph-index.yaml)
# ✓ All node IDs in subsystems exist
# ✓ Subsystem paths in frontmatter match graph-index.yaml
```

Common validation errors:

```
❌ Parent subsystem 'identity' has both children and direct nodes
   Fix: Move nodes to leaf subsystems (identity.auth or identity.user)

❌ Node O-AUTH-001 references invalid subsystem path 'identity.auth'
   Fix: Define 'identity.auth' in graph-index.yaml subsystems

❌ Cycle detected in subsystem hierarchy at 'identity'
   Fix: Remove circular references in subsystem nesting
```

---

## Performance

Nested subsystems are designed for performance:

- **Status display**: <100ms for 100 subsystems
- **Subsystem queries**: <200ms for 100 subsystems
- **Metrics calculation**: <5s for 100 subsystems
- **Path resolution**: O(depth) lookup, typically <10 microseconds

---

## Backward Compatibility

Flat subsystems continue to work without changes:

```yaml
# Old format (still works)
subsystems:
  auth:
    description: "Authentication"
    nodes: [O-AUTH-001, S-AUTH-001]

  core:
    description: "Core infrastructure"
    nodes: [O-CORE-001, S-CORE-001]
```

Use `jigy status --flat` to view nested subsystems in flat format.

---

## References

- [Migration Guide](MIGRATION_NESTED.md) - Step-by-step migration from flat to nested
- [Tutorial](../tutorials/NESTED_SUBSYSTEMS_TUTORIAL.md) - Hands-on example with sample project
- [Architecture](../architecture/GRAPH_SUBSYSTEM.md) - Implementation details
- [JIG Concept v7](../jig-concept/JIG-Concept-v7.md) - OSTCX model with nested subsystems
- [Data Formats](../architecture/DATA_FORMATS.md) - File format specifications

---

**Document Version:** 1.0
**Last Updated:** 2025-11-21
**Maintained By:** JIG Core Team
