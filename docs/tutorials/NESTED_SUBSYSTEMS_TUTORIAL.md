# Nested Subsystems Tutorial

**Version:** 1.0
**Status:** Active
**Last Updated:** 2025-11-21

This hands-on tutorial walks through creating a sample project with nested subsystems, demonstrating hierarchical organization and improved metrics.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Part 1: Create Flat Structure](#part-1-create-flat-structure)
4. [Part 2: Analyze Flat Metrics](#part-2-analyze-flat-metrics)
5. [Part 3: Refactor to Nested Structure](#part-3-refactor-to-nested-structure)
6. [Part 4: Compare Metrics](#part-4-compare-metrics)
7. [Part 5: Advanced Queries](#part-5-advanced-queries)
8. [Summary](#summary)

---

## Overview

### What You'll Learn

- Creating a JIG project with multiple subsystems
- Understanding coupling ratios and modularity
- Refactoring flat subsystems into hierarchical structure
- How nested subsystems improve metrics
- Querying and analyzing subsystem hierarchies

### Sample Project: E-commerce Platform

We'll build an Intent Graph for a simplified e-commerce platform with subsystems for:
- User authentication
- User profiles
- Product catalog
- Shopping cart
- Order processing

By the end, we'll reorganize these into:
- `identity` (auth, profile)
- `commerce` (catalog, cart, orders)

**Time:** 30-45 minutes

---

## Prerequisites

1. **JIG installed:**
   ```bash
   pip install -e .
   jigy --version
   ```

2. **Create tutorial directory:**
   ```bash
   mkdir -p ~/jig-tutorial
   cd ~/jig-tutorial
   ```

3. **Initialize JIG:**
   ```bash
   jigy init
   ```

This creates:
```
jig/
├── outcomes/
├── specifications/
├── constraints/
└── graph-index.yaml
```

---

## Part 1: Create Flat Structure

### Step 1: Define Flat Subsystems

Edit `jig/graph-index.yaml`:

```yaml
version: 1.0.0
created: 2025-11-21

subsystems:
  auth:
    description: "User authentication"
    nodes: []

  profile:
    description: "User profile management"
    nodes: []

  catalog:
    description: "Product catalog"
    nodes: []

  cart:
    description: "Shopping cart"
    nodes: []

  orders:
    description: "Order processing"
    nodes: []

nodes: {}
edges: []
```

### Step 2: Create Intent Nodes

Create outcome nodes for each subsystem:

```bash
# Auth outcome
jigy node create --type outcome \
  --id O-AUTH-001 \
  --title "Users authenticate securely" \
  --subsystem auth

# Profile outcome
jigy node create --type outcome \
  --id O-PROFILE-001 \
  --title "Users manage their profiles" \
  --subsystem profile

# Catalog outcome
jigy node create --type outcome \
  --id O-CATALOG-001 \
  --title "Users browse product catalog" \
  --subsystem catalog

# Cart outcome
jigy node create --type outcome \
  --id O-CART-001 \
  --title "Users add products to cart" \
  --subsystem cart

# Orders outcome
jigy node create --type outcome \
  --id O-ORDERS-001 \
  --title "Users place and track orders" \
  --subsystem orders
```

Create specification nodes:

```bash
# Auth spec
jigy node create --type specification \
  --id S-AUTH-001 \
  --title "JWT-based authentication" \
  --subsystem auth

# Profile spec
jigy node create --type specification \
  --id S-PROFILE-001 \
  --title "User profile CRUD API" \
  --subsystem profile

# Catalog spec
jigy node create --type specification \
  --id S-CATALOG-001 \
  --title "Product search and filtering" \
  --subsystem catalog

# Cart spec
jigy node create --type specification \
  --id S-CART-001 \
  --title "Cart management with persistence" \
  --subsystem cart

# Orders spec
jigy node create --type specification \
  --id S-ORDERS-001 \
  --title "Order creation and status tracking" \
  --subsystem orders
```

### Step 3: Define Relationships

Edit `jig/graph-index.yaml` to add edges representing dependencies:

```yaml
edges:
  # Specifications implement outcomes
  - from: S-AUTH-001
    to: O-AUTH-001
    type: implements

  - from: S-PROFILE-001
    to: O-PROFILE-001
    type: implements

  - from: S-CATALOG-001
    to: O-CATALOG-001
    type: implements

  - from: S-CART-001
    to: O-CART-001
    type: implements

  - from: S-ORDERS-001
    to: O-ORDERS-001
    type: implements

  # Cross-subsystem dependencies
  - from: S-PROFILE-001
    to: S-AUTH-001
    type: depends

  - from: S-CART-001
    to: S-AUTH-001
    type: depends

  - from: S-CART-001
    to: S-CATALOG-001
    type: depends

  - from: S-ORDERS-001
    to: S-AUTH-001
    type: depends

  - from: S-ORDERS-001
    to: S-CART-001
    type: depends
```

### Step 4: Validate Structure

```bash
jigy validate

# ✓ All nodes validated
# ✓ Graph structure valid
# ✓ No orphaned nodes
```

### Step 5: View Status

```bash
jigy status

# Intent Graph Status
# ==================
#
# Nodes: 10 (5 outcomes, 5 specifications)
# Edges: 10
#
# Subsystems (flat):
# - auth: 2 nodes
# - profile: 2 nodes
# - catalog: 2 nodes
# - cart: 2 nodes
# - orders: 2 nodes
```

---

## Part 2: Analyze Flat Metrics

### Step 1: Calculate Decomposability Metrics

```bash
jigy decompose metrics

# Decomposability Metrics
# =======================
#
# Overall Modularity: 0.45 ⚠ (target: >0.7)
#
# Subsystem Metrics:
# auth (2 nodes, 1 internal, 4 external, ratio: 0.25) ⚠ Low coupling
# profile (2 nodes, 1 internal, 1 external, ratio: 1.00)
# catalog (2 nodes, 1 internal, 1 external, ratio: 1.00)
# cart (2 nodes, 1 internal, 2 external, ratio: 0.50)
# orders (2 nodes, 1 internal, 2 external, ratio: 0.50)
#
# Average coupling ratio: 0.65 ⚠ (target: >3.0)
```

### Step 2: Analyze the Problem

**Observations:**
- ❌ **Low modularity (0.45)**: Subsystems not well-separated
- ❌ **Low coupling ratios**: Many external dependencies
- ❌ **auth is a hub**: Many subsystems depend on it (4 external edges)

**Why?**
- `auth` and `profile` are related (identity management) but counted as separate subsystems
- `cart` and `orders` are related (commerce) but counted as separate subsystems
- Cross-dependency between related subsystems hurts metrics

**Solution:** Group related subsystems hierarchically!

---

## Part 3: Refactor to Nested Structure

### Step 1: Update graph-index.yaml Structure

Replace the flat `subsystems` section:

```yaml
subsystems:
  # Parent: Identity management
  identity:
    description: "User identity and authentication"
    subsystems:
      auth:
        description: "User authentication"
        nodes:
          - O-AUTH-001
          - S-AUTH-001

      profile:
        description: "User profile management"
        nodes:
          - O-PROFILE-001
          - S-PROFILE-001

  # Parent: Commerce
  commerce:
    description: "E-commerce features"
    subsystems:
      catalog:
        description: "Product catalog"
        nodes:
          - O-CATALOG-001
          - S-CATALOG-001

      cart:
        description: "Shopping cart"
        nodes:
          - O-CART-001
          - S-CART-001

      orders:
        description: "Order processing"
        nodes:
          - O-ORDERS-001
          - S-ORDERS-001
```

### Step 2: Update Node Frontmatter

Update subsystem paths in all node files (10 files):

**Auth nodes** (`jig/outcomes/O-AUTH-001.md`, `jig/specifications/S-AUTH-001.md`):
```yaml
subsystem: auth  # Old
↓
subsystem: identity.auth  # New
```

**Profile nodes**:
```yaml
subsystem: profile  # Old
↓
subsystem: identity.profile  # New
```

**Catalog nodes**:
```yaml
subsystem: catalog  # Old
↓
subsystem: commerce.catalog  # New
```

**Cart nodes**:
```yaml
subsystem: cart  # Old
↓
subsystem: commerce.cart  # New
```

**Orders nodes**:
```yaml
subsystem: orders  # Old
↓
subsystem: commerce.orders  # New
```

**Quick way (using sed):**
```bash
# Backup first
cp -r jig jig.backup

# Update subsystem paths
find jig -name "*.md" -type f -exec sed -i '' 's/^subsystem: auth$/subsystem: identity.auth/' {} +
find jig -name "*.md" -type f -exec sed -i '' 's/^subsystem: profile$/subsystem: identity.profile/' {} +
find jig -name "*.md" -type f -exec sed -i '' 's/^subsystem: catalog$/subsystem: commerce.catalog/' {} +
find jig -name "*.md" -type f -exec sed -i '' 's/^subsystem: cart$/subsystem: commerce.cart/' {} +
find jig -name "*.md" -type f -exec sed -i '' 's/^subsystem: orders$/subsystem: commerce.orders/' {} +

# Verify changes
git diff jig/
```

### Step 3: Validate New Structure

```bash
jigy validate

# ✓ All nodes validated
# ✓ Graph structure valid
# ✓ No orphaned nodes
# ✓ Nested subsystem structure valid
# ✓ Parent subsystems have no direct nodes
```

### Step 4: View Hierarchical Status

```bash
jigy status

# Intent Graph Status
# ==================
#
# Nodes: 10 (5 outcomes, 5 specifications)
# Edges: 10
#
# Subsystems (hierarchical):
# identity (4 nodes)
#   ├── auth (2 nodes)
#   └── profile (2 nodes)
# commerce (6 nodes)
#   ├── catalog (2 nodes)
#   ├── cart (2 nodes)
#   └── orders (2 nodes)
```

---

## Part 4: Compare Metrics

### Step 1: Calculate New Metrics

```bash
jigy decompose metrics

# Decomposability Metrics
# =======================
#
# Overall Modularity: 0.72 ✓ (target: >0.7)
#
# Subsystem Metrics:
# identity (4 nodes, 3 internal, 4 external, ratio: 0.75)
#   auth (2 nodes, 1 internal, 4 external, ratio: 0.25)
#   profile (2 nodes, 1 internal, 1 external, ratio: 1.00)
#
# commerce (6 nodes, 6 internal, 4 external, ratio: 1.50)
#   catalog (2 nodes, 1 internal, 1 external, ratio: 1.00)
#   cart (2 nodes, 1 internal, 2 external, ratio: 0.50)
#   orders (2 nodes, 1 internal, 2 external, ratio: 0.50)
#
# Average coupling ratio (parents): 1.13 (improved from 0.65!)
```

### Step 2: Compare Before/After

| Metric | Flat (Before) | Nested (After) | Improvement |
|--------|---------------|----------------|-------------|
| **Modularity** | 0.45 ⚠ | 0.72 ✓ | **+60%** |
| **Avg Coupling** | 0.65 ⚠ | 1.13 | **+74%** |
| **identity coupling** | N/A | 0.75 | New parent metric |
| **commerce coupling** | N/A | 1.50 | New parent metric |

### Step 3: Understand the Improvement

**Why did metrics improve?**

1. **Edge from auth → profile:**
   - **Flat:** External edge (hurts both subsystems)
   - **Nested:** Internal to `identity` parent (helps parent coupling)

2. **Edge from cart → orders:**
   - **Flat:** External edge (hurts both subsystems)
   - **Nested:** Internal to `commerce` parent (helps parent coupling)

3. **Modularity increased:**
   - Better-defined boundaries at parent level
   - Related subsystems grouped appropriately

**Key insight:** Nesting doesn't change the graph structure, but it **changes how we measure cohesion**. Sibling communication is appropriately counted as internal to the parent module.

---

## Part 5: Advanced Queries

### Step 1: Query by Parent Subsystem

List all nodes in identity subsystem:
```bash
jigy graph list --subsystem identity --recursive

# O-AUTH-001     outcome        identity.auth    Users authenticate securely
# S-AUTH-001     specification  identity.auth    JWT-based authentication
# O-PROFILE-001  outcome        identity.profile Users manage their profiles
# S-PROFILE-001  specification  identity.profile User profile CRUD API
```

List only direct children (leaf subsystems):
```bash
jigy graph list --subsystem identity

# (No results - parent has no direct nodes, only children)
```

### Step 2: Query by Leaf Subsystem

List nodes in specific leaf:
```bash
jigy graph list --subsystem identity.auth

# O-AUTH-001     outcome        identity.auth    Users authenticate securely
# S-AUTH-001     specification  identity.auth    JWT-based authentication
```

### Step 3: Analyze Specific Subtrees

Analyze just identity subsystem:
```bash
jigy decompose metrics --subsystem identity

# Subsystem: identity
# ==================
#
# Nodes: 4
# Internal edges: 3
# External edges: 4
# Coupling ratio: 0.75
#
# Children:
#   auth (2 nodes, 1 internal, 4 external, ratio: 0.25)
#   profile (2 nodes, 1 internal, 1 external, ratio: 1.00)
```

Analyze just commerce subsystem:
```bash
jigy decompose metrics --subsystem commerce

# Subsystem: commerce
# ==================
#
# Nodes: 6
# Internal edges: 6
# External edges: 4
# Coupling ratio: 1.50 ✓
#
# Children:
#   catalog (2 nodes, 1 internal, 1 external, ratio: 1.00)
#   cart (2 nodes, 1 internal, 2 external, ratio: 0.50)
#   orders (2 nodes, 1 internal, 2 external, ratio: 0.50)
```

### Step 4: View Flat (Backward Compatibility)

```bash
jigy status --flat

# Subsystems (flat):
# - identity.auth: 2 nodes
# - identity.profile: 2 nodes
# - commerce.catalog: 2 nodes
# - commerce.cart: 2 nodes
# - commerce.orders: 2 nodes
```

### Step 5: Generate Report

```bash
jigy decompose report --output tutorial-report.md

# Report written to: tutorial-report.md
```

Open `tutorial-report.md` to see full hierarchical breakdown with:
- Overall metrics
- Parent subsystem metrics
- Leaf subsystem metrics
- Boundary violations (if any)
- Recommendations

---

## Summary

### What We Learned

1. **Flat structure limitations:**
   - Low coupling ratios for related subsystems
   - Poor modularity scores
   - Cross-dependencies between related modules hurt metrics

2. **Nested structure benefits:**
   - **60% improvement in modularity** (0.45 → 0.72)
   - **74% improvement in coupling** (0.65 → 1.13)
   - Sibling communication appropriately counted as internal
   - Multi-level analysis (parent + leaf)

3. **Hierarchical organization:**
   - Parent subsystems group related functionality
   - Leaf subsystems contain actual nodes
   - Dot notation for clear, unambiguous paths
   - Backward compatible with flat view

### Key Takeaways

✅ **Use nested subsystems when:**
- You have 10+ subsystems with natural groupings
- Related subsystems communicate frequently
- You want multi-level analysis

✅ **Metrics improve because:**
- Sibling edges count as internal to parent
- Better reflection of actual system architecture
- Clearer boundaries at multiple levels

✅ **CLI commands work seamlessly:**
- `jigy status` shows hierarchy by default
- `jigy graph list --subsystem parent --recursive` works on subtrees
- `jigy decompose metrics --subsystem parent` analyzes parent + children

### Next Steps

1. **Apply to your project:**
   - Identify natural subsystem groupings
   - Follow [Migration Guide](../user-guide/MIGRATION_NESTED.md)
   - Compare metrics before/after

2. **Read architecture docs:**
   - [User Guide](../user-guide/NESTED_SUBSYSTEMS.md) - Complete reference
   - [Architecture](../architecture/GRAPH_SUBSYSTEM.md) - Implementation details

3. **Experiment:**
   - Try different hierarchical structures
   - Analyze at different levels (parent vs. leaf)
   - Find optimal organization for your project

---

## Cleanup

Remove tutorial directory:
```bash
cd ~
rm -rf jig-tutorial
```

---

## References

- [User Guide](../user-guide/NESTED_SUBSYSTEMS.md) - Complete nested subsystems guide
- [Migration Guide](../user-guide/MIGRATION_NESTED.md) - Flat to nested migration
- [Architecture](../architecture/GRAPH_SUBSYSTEM.md) - Implementation details
- [JIG Concept v7](../jig-concept/JIG-Concept-v7.md) - OSTCX model

---

**Document Version:** 1.0
**Last Updated:** 2025-11-21
**Maintained By:** JIG Core Team
