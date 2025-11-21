# Migration Guide: Flat to Nested Subsystems

**Version:** 1.0
**Status:** Active
**Last Updated:** 2025-11-21

This guide provides step-by-step instructions for migrating from flat subsystem structure to nested subsystems.

---

## Table of Contents

1. [When to Migrate](#when-to-migrate)
2. [Pre-Migration Checklist](#pre-migration-checklist)
3. [Migration Steps](#migration-steps)
4. [Example Migration](#example-migration)
5. [Validation](#validation)
6. [Rollback Plan](#rollback-plan)
7. [Troubleshooting](#troubleshooting)

---

## When to Migrate

Consider migrating to nested subsystems when:

- ✅ You have **10+ subsystems** and flat structure feels cluttered
- ✅ **Natural groupings** exist (e.g., `auth`, `user` → `identity.auth`, `identity.user`)
- ✅ You're **splitting a large subsystem** into smaller pieces
- ✅ You want **multi-level analysis** (both parent and leaf metrics)

**Don't migrate if:**
- ❌ You have <10 subsystems
- ❌ No clear hierarchical relationship exists
- ❌ Team isn't familiar with nested structure yet (consider training first)

---

## Pre-Migration Checklist

Before starting migration:

- [ ] **Backup**: Commit all changes and tag current state
  ```bash
  git add -A
  git commit -m "Pre-nested-subsystems snapshot"
  git tag pre-nested-subsystems
  ```

- [ ] **Document current state**: Run status and metrics
  ```bash
  jigy status > docs/metrics/pre-migration-status.txt
  jigy decompose metrics > docs/metrics/pre-migration-metrics.txt
  ```

- [ ] **Validate graph**: Ensure current graph is valid
  ```bash
  jigy validate
  ```

- [ ] **Run tests**: Ensure all tests pass
  ```bash
  pytest
  ```

- [ ] **Plan hierarchy**: Sketch out new subsystem structure on paper
  ```
  Current:           Planned:
  - auth             identity/
  - user               ├── auth
  - billing            └── user
  - notifications    services/
  - analytics          ├── billing
  - logging            └── notifications
  - metrics          observability/
                       ├── analytics
                       ├── logging
                       └── metrics
  ```

- [ ] **Communicate**: Inform team about upcoming migration

---

## Migration Steps

### Step 1: Update graph-index.yaml

**Before:**
```yaml
version: 1.0.0
created: 2025-11-21

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
      - S-USER-002
```

**After:**
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
          - S-USER-002
```

**Changes:**
1. Add parent subsystem (`identity`)
2. Nest child subsystems under `subsystems` key
3. Keep node lists in leaf subsystems
4. Ensure parent has **no direct nodes**, only `subsystems`

**Validation after this step:**
```bash
# This will fail (nodes still reference old paths)
jigy validate

# Expected error:
# ❌ Node O-AUTH-001 frontmatter has subsystem 'auth', but graph-index has 'identity.auth'
```

This is expected - we'll fix it in Step 2.

---

### Step 2: Update Node Frontmatter

Update `subsystem` field in all node markdown files.

**Search pattern (all files in jig/):**
```bash
# Find all nodes that need updating
grep -r "subsystem: auth$" jig/
grep -r "subsystem: user$" jig/
```

**Before (`jig/outcomes/O-AUTH-001.md`):**
```yaml
---
id: O-AUTH-001
type: outcome
title: "Users authenticate securely"
subsystem: auth
created: 2025-11-21
---
```

**After:**
```yaml
---
id: O-AUTH-001
type: outcome
title: "Users authenticate securely"
subsystem: identity.auth
created: 2025-11-21
---
```

**Batch update with sed (macOS/Linux):**

```bash
# Backup first!
cp -r jig jig.backup

# Update auth → identity.auth
find jig -name "*.md" -type f -exec sed -i '' 's/^subsystem: auth$/subsystem: identity.auth/' {} +

# Update user → identity.user
find jig -name "*.md" -type f -exec sed -i '' 's/^subsystem: user$/subsystem: identity.user/' {} +

# Verify changes
git diff jig/
```

**Manual alternative:**

For each affected file in `jig/outcomes/`, `jig/specifications/`, `jig/constraints/`:
1. Open file
2. Change `subsystem: auth` → `subsystem: identity.auth`
3. Save

**Validation after this step:**
```bash
# Should show progress (graph-index.yaml and node frontmatter now match)
jigy validate

# May still show errors if code annotations not updated yet
```

---

### Step 3: Update Code Annotations

Update `subsystem:` in all `@jig` annotations in source code.

**Search pattern (all source files):**
```bash
# Find all annotations that need updating
grep -r "@jig.*subsystem:auth" src/ tests/
grep -r "@jig.*subsystem:user" src/ tests/
```

**Before (`src/auth/authenticator.py`):**
```python
# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:auth interface:public
class JWTAuthenticator:
    """Handles JWT-based authentication"""
    # ...
```

**After:**
```python
# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:identity.auth interface:public
class JWTAuthenticator:
    """Handles JWT-based authentication"""
    # ...
```

**Batch update with sed:**

```bash
# Backup first!
cp -r src src.backup
cp -r tests tests.backup

# Update auth → identity.auth in annotations
find src tests -name "*.py" -type f -exec sed -i '' 's/@jig \(.*\)subsystem:auth/@jig \1subsystem:identity.auth/' {} +

# Update user → identity.user in annotations
find src tests -name "*.py" -type f -exec sed -i '' 's/@jig \(.*\)subsystem:user/@jig \1subsystem:identity.user/' {} +

# Verify changes
git diff src/ tests/
```

**Validation after this step:**
```bash
# Should pass all validation
jigy validate

# ✓ All nodes validated
# ✓ Graph structure valid
# ✓ No orphaned nodes
# ✓ Nested subsystem structure valid
```

---

### Step 4: Update Documentation

Update any documentation that references subsystem names:

**Files to check:**
- `README.md` - Update examples
- `docs/` - Architecture docs
- `CONTRIBUTING.md` - Development guides
- Code comments - Remove outdated references

**Example updates:**

```bash
# Search for references
grep -r "subsystem auth" docs/ README.md
grep -r "auth subsystem" docs/ README.md
```

Update phrases like:
- "the auth subsystem" → "the identity.auth subsystem"
- "in subsystem auth" → "in subsystem identity.auth"
- Example paths in documentation

---

### Step 5: Verify Functionality

Test that all CLI commands work correctly with new structure:

```bash
# 1. Status shows hierarchical tree
jigy status

# Expected:
# Subsystems (hierarchical):
# identity (N nodes)
#   ├── auth (X nodes)
#   └── user (Y nodes)

# 2. Flat view still works
jigy status --flat

# Expected:
# - identity.auth: X nodes
# - identity.user: Y nodes

# 3. Graph queries work with nested paths
jigy graph list --subsystem identity
jigy graph list --subsystem identity --recursive
jigy graph list --subsystem identity.auth

# 4. Decompose metrics show hierarchy
jigy decompose metrics

# Expected:
# identity (N nodes, ...)
#   auth (X nodes, ...)
#   user (Y nodes, ...)

# 5. Decompose metrics work on subtrees
jigy decompose metrics --subsystem identity
jigy decompose metrics --subsystem identity.auth

# 6. Validation passes
jigy validate

# ✓ All checks pass
```

---

### Step 6: Verify Tests Still Pass

Ensure your test suite still passes:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test suites if needed
pytest tests/unit/
pytest tests/integration/
```

If tests fail, check:
- Hardcoded subsystem names in test fixtures
- Test data files with old subsystem references
- Assertion messages mentioning subsystem names

---

### Step 7: Document Migration & Commit

Create a commit documenting the migration:

```bash
# Stage all changes
git add jig/ src/ tests/ docs/ README.md

# Commit with clear message
git commit -m "Migrate to nested subsystems

Restructure flat subsystems into hierarchical organization:
- auth, user → identity.auth, identity.user
- billing, notifications → services.billing, services.notifications
- analytics, logging, metrics → observability.*

Changes:
- Updated graph-index.yaml with nested subsystem structure
- Updated all node frontmatter (subsystem: paths)
- Updated all @jig annotations in source code
- Updated documentation references

Benefits:
- Better organization for growing codebase (15+ subsystems)
- Improved coupling ratios (sibling edges now internal to parent)
- Multi-level analysis capability (parent + leaf metrics)

All validation checks pass. All tests pass.

Migration completed: $(date)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Tag the migration
git tag nested-subsystems-migration
```

---

## Example Migration

### Scenario: Auth System Refactoring

**Current structure (flat):**
```
Subsystems:
- auth (12 nodes)
- user (8 nodes)
- session (6 nodes)
```

**Goal:** Group related identity services

**Step-by-step:**

#### 1. Update graph-index.yaml

```yaml
# Add parent subsystem
subsystems:
  identity:
    description: "User identity services"
    subsystems:
      auth:
        description: "Authentication and authorization"
        nodes: [O-AUTH-001, S-AUTH-001, ...]

      user:
        description: "User profile management"
        nodes: [O-USER-001, S-USER-001, ...]

      session:
        description: "Session management"
        nodes: [O-SESSION-001, S-SESSION-001, ...]
```

#### 2. Update node frontmatter (12 + 8 + 6 = 26 files)

```bash
# Batch update
find jig -name "*.md" -type f -exec sed -i '' 's/^subsystem: auth$/subsystem: identity.auth/' {} +
find jig -name "*.md" -type f -exec sed -i '' 's/^subsystem: user$/subsystem: identity.user/' {} +
find jig -name "*.md" -type f -exec sed -i '' 's/^subsystem: session$/subsystem: identity.session/' {} +
```

#### 3. Update code annotations

```bash
# Update src/ and tests/
find src tests -name "*.py" -type f -exec sed -i '' 's/subsystem:auth/subsystem:identity.auth/g' {} +
find src tests -name "*.py" -type f -exec sed -i '' 's/subsystem:user/subsystem:identity.user/g' {} +
find src tests -name "*.py" -type f -exec sed -i '' 's/subsystem:session/subsystem:identity.session/g' {} +
```

#### 4. Validate

```bash
jigy validate
# ✓ All validation checks pass

jigy status
# Subsystems (hierarchical):
# identity (26 nodes)
#   ├── auth (12 nodes)
#   ├── user (8 nodes)
#   └── session (6 nodes)

jigy decompose metrics --subsystem identity
# identity (26 nodes, 85 internal, 12 external, ratio: 7.08)
#   auth (12 nodes, 35 internal, 5 external, ratio: 7.00)
#   user (8 nodes, 28 internal, 4 external, ratio: 7.00)
#   session (6 nodes, 20 internal, 3 external, ratio: 6.67)
```

#### 5. Notice improved coupling

**Before (flat):**
- Edge `auth → user`: External edge (hurts coupling)
- Edge `auth → session`: External edge (hurts coupling)

**After (nested):**
- Edge `identity.auth → identity.user`: **Internal to `identity`** (helps coupling)
- Edge `identity.auth → identity.session`: **Internal to `identity`** (helps coupling)

Result: Parent subsystem `identity` has better coupling ratio than individual children.

---

## Validation

After migration, validate thoroughly:

### 1. Structure Validation

```bash
jigy validate

# Should check:
# ✓ No cycles in subsystem hierarchy
# ✓ Parent subsystems have no direct nodes
# ✓ All node subsystem paths valid
# ✓ All nodes referenced in graph-index exist
# ✓ Frontmatter matches graph-index
```

### 2. Query Validation

Test all query patterns:

```bash
# Hierarchical status
jigy status

# Flat status (backward compatibility)
jigy status --flat

# List all subsystem paths
jigy graph list --subsystem identity
jigy graph list --subsystem identity --recursive
jigy graph list --subsystem identity.auth

# Show specific nodes
jigy graph show O-AUTH-001

# Dependency traversal
jigy graph deps O-AUTH-001
jigy graph impact S-AUTH-001
```

### 3. Metrics Validation

Compare metrics before and after:

```bash
# Compare with pre-migration baseline
diff docs/metrics/pre-migration-metrics.txt <(jigy decompose metrics)

# Should see:
# - Overall modularity similar or improved
# - Parent subsystems show aggregated metrics
# - Leaf subsystems show same granular metrics
# - Coupling ratios improved (sibling edges now internal)
```

### 4. Test Validation

```bash
# All tests should pass
pytest -v

# If tests fail, check:
# - Hardcoded subsystem names in fixtures
# - Test data files
# - Assertion error messages
```

---

## Rollback Plan

If migration fails or causes issues:

### Option 1: Git Revert

```bash
# Revert to pre-migration state
git reset --hard pre-nested-subsystems

# Verify
jigy validate
pytest
```

### Option 2: Restore from Backup

```bash
# If you made backups
rm -rf jig src tests
cp -r jig.backup jig
cp -r src.backup src
cp -r tests.backup tests

# Verify
jigy validate
pytest
```

### Option 3: Manual Rollback

Reverse each migration step:

1. Restore `graph-index.yaml` from git history
2. Revert node frontmatter changes
3. Revert code annotation changes
4. Validate and test

```bash
# Restore specific files
git checkout HEAD~1 -- jig/graph-index.yaml

# Revert subsystem changes in frontmatter
find jig -name "*.md" -type f -exec sed -i '' 's/^subsystem: identity\.auth$/subsystem: auth/' {} +

# Revert annotations
find src tests -name "*.py" -type f -exec sed -i '' 's/subsystem:identity\.auth/subsystem:auth/g' {} +

# Validate
jigy validate
pytest
```

---

## Troubleshooting

### Issue: "Node references invalid subsystem path"

**Error:**
```
❌ Node O-AUTH-001 references invalid subsystem path 'identity.auth'
```

**Cause:** Node frontmatter updated but graph-index.yaml not yet updated (or vice versa).

**Fix:** Ensure both are synchronized:
1. Check `jig/graph-index.yaml` has subsystem defined
2. Check node frontmatter uses exact path from graph-index

---

### Issue: "Parent subsystem has both children and direct nodes"

**Error:**
```
❌ Parent subsystem 'identity' has both children and direct nodes
```

**Cause:** Parent subsystem has `nodes` field AND `subsystems` field.

**Fix:** Move nodes to leaf subsystems:

```yaml
# Bad
identity:
  description: "..."
  nodes: [O-AUTH-001]  # ❌ Parent can't have direct nodes
  subsystems:
    auth: ...

# Good
identity:
  description: "..."
  subsystems:
    auth:
      nodes: [O-AUTH-001]  # ✓ Nodes in leaf subsystem
```

---

### Issue: Coupling ratio decreased after migration

**Symptom:** Leaf subsystem coupling ratio lower than before.

**Expected:** This can happen if edges between siblings (e.g., `auth → user`) were previously external but now appear as external to each leaf.

**Solution:** Analyze at **parent level**:

```bash
# Leaf metrics may be lower
jigy decompose metrics --subsystem identity.auth
# auth (10 internal, 5 external, ratio: 2.0)

# But parent metrics should be better
jigy decompose metrics --subsystem identity
# identity (35 internal, 8 external, ratio: 4.38)
```

The parent includes sibling edges as internal, giving a truer picture of the overall module's cohesion.

---

### Issue: Tests fail after migration

**Symptom:** Tests that passed before now fail.

**Common causes:**

1. **Hardcoded subsystem names in test fixtures:**
   ```python
   # Fix this:
   assert node.subsystem == "auth"  # ❌ Old name

   # To this:
   assert node.subsystem == "identity.auth"  # ✓ New name
   ```

2. **Test data files with old subsystem references:**
   ```yaml
   # tests/fixtures/sample-graph.yaml
   subsystem: auth  # ❌ Update to identity.auth
   ```

3. **Assertion error messages mentioning subsystem names:**
   ```python
   # Fix this:
   pytest.raises(ValueError, match="auth subsystem")  # ❌

   # To this:
   pytest.raises(ValueError, match="identity.auth subsystem")  # ✓
   ```

**Debugging:**
```bash
# Run tests with verbose output
pytest -vv

# Run specific failing test
pytest tests/unit/test_auth.py::test_subsystem_name -vv

# Check test fixtures
grep -r "subsystem.*auth" tests/fixtures/
```

---

### Issue: CLI commands slow after migration

**Symptom:** `jigy status` or `jigy decompose metrics` much slower.

**Unlikely but check:**

1. **Too deep nesting** (>5 levels):
   ```bash
   # Check maximum depth
   jigy status | grep "│" | wc -l
   ```
   If >4-5 levels, consider flattening.

2. **Very large number of subsystems** (>200):
   ```bash
   # Count leaf subsystems
   jigy status --flat | wc -l
   ```
   If >200, performance may degrade (file an issue).

**Expected performance:**
- Status: <100ms for 100 subsystems
- Queries: <200ms for 100 subsystems
- Metrics: <5s for 100 subsystems

If slower, file a bug report with `jigy --version` and subsystem count.

---

## Post-Migration Checklist

After successful migration:

- [ ] All validation checks pass (`jigy validate`)
- [ ] All tests pass (`pytest`)
- [ ] Status displays hierarchy correctly (`jigy status`)
- [ ] Flat view still works (`jigy status --flat`)
- [ ] Queries work on nested paths (`jigy graph list --subsystem parent.child`)
- [ ] Metrics show hierarchical breakdown (`jigy decompose metrics`)
- [ ] Documentation updated with new subsystem names
- [ ] Migration committed and tagged
- [ ] Team notified of new subsystem structure
- [ ] Training provided (if needed) on dot notation and hierarchical queries

---

## References

- [Nested Subsystems User Guide](NESTED_SUBSYSTEMS.md) - Concepts and usage
- [Tutorial](../tutorials/NESTED_SUBSYSTEMS_TUTORIAL.md) - Hands-on example
- [Architecture](../architecture/GRAPH_SUBSYSTEM.md) - Implementation details
- [Data Formats](../architecture/DATA_FORMATS.md) - File format specifications

---

**Document Version:** 1.0
**Last Updated:** 2025-11-21
**Maintained By:** JIG Core Team
