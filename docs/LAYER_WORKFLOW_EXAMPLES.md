# Layer Validation Workflow Examples

This document provides practical examples of using JIG's layer validation and visualization commands.

## Quick Start

```bash
# 1. Validate your artifacts
jigy validate bricks

# 2. Visualize layer structure
jigy layers

# 3. Get layer suggestions
jigy layers suggest

# 4. Apply suggestions (with confirmation)
jigy layers suggest --apply
```

## Complete Workflows

### Workflow 1: Setting Up Layers for a New Project

Starting with a flat architecture (all bricks at layer 0 or no layers):

```bash
# Step 1: Generate implementation graph
jigy impl rebuild

# Step 2: Run validation to see current state
jigy validate bricks
# Output: May show missing layer fields or validation errors

# Step 3: Let JIG suggest layers based on dependencies
jigy layers suggest
# Output shows suggested layer assignments

# Step 4: Apply suggestions
jigy layers suggest --apply
# Confirm with 'y' when prompted

# Step 5: Validate again to confirm
jigy validate bricks
# Output: All validations should pass

# Step 6: Visualize the layer structure
jigy layers
# See your layered architecture
```

### Workflow 2: Detecting and Fixing Layer Violations

When validation finds layer constraint violations:

```bash
# Run validation
jigy validate bricks

# Example error output:
# ✗ Validating brick layer constraints
#   B-api (layer: 1) depends on B-cli (layer: 2)
#   Violation: F-api.handler → F-cli.main
#   Layer 1 brick cannot depend on layer 2 brick

# Step 1: Visualize current structure to understand the issue
jigy layers

# Step 2: Get suggestions for correct layer assignment
jigy layers suggest

# Example output:
# B-api: API Handler
#   Current layer: 1
#   Suggested: 2 (depends on: B-cli) ⚠ MISMATCH

# Step 3: Apply suggestions to fix
jigy layers suggest --apply

# Step 4: Verify the fix
jigy validate bricks
# Output: ✓ All validations passed
```

### Workflow 3: Refactoring to Break Circular Dependencies

When circular dependencies are detected:

```bash
# Run validation
jigy validate bricks

# Example error output:
# ✗ Validating brick cycles
#   Circular dependency detected: B-parser → B-validator → B-parser
#   Cycle includes:
#     F-parser.parse → F-validator.validate
#     F-validator.check → F-parser.helper

# Note: jigy layers suggest will fail with cycles
jigy layers suggest
# Output: ✗ Cannot suggest layers: circular dependencies exist

# Solution: Refactor code to break the cycle
# Option A: Extract shared functionality
#   1. Create new brick B-shared-utils at layer 0
#   2. Move F-parser.helper to B-shared-utils
#   3. Update both B-parser and B-validator to depend on B-shared-utils

# Option B: Invert dependency
#   1. Move functionality from B-validator to B-parser
#   2. Remove dependency from B-validator to B-parser

# After refactoring:
jigy impl rebuild  # Rebuild graph with new code structure
jigy validate bricks  # Should pass now
jigy layers suggest --apply  # Assign appropriate layers
```

### Workflow 4: Continuous Validation During Development

Integrate validation into your development workflow:

```bash
# After making code changes
git add .

# Rebuild graph with new code
jigy impl rebuild

# Run full validation before committing
jigy validate

# If validation fails, see details
jigy validate bricks

# Fix any issues, then commit
git commit -m "Your commit message"
```

### Workflow 5: Understanding Layer Structure

Exploring your architecture:

```bash
# Quick summary of layers
jigy layers --summary

# Example output:
# Layer Summary
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Layer 0: 3 bricks, 15 functions
# Layer 1: 4 bricks, 32 functions
# Layer 2: 2 bricks, 8 functions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Total: 9 bricks, 3 layers, 55 functions

# Full details with dependencies
jigy layers

# Example output:
# Layer 0: Foundation (3 bricks)
# ────────────────────────────────────────────────────
#   B-core-utils: Core Utilities (5 functions)
#   B-data-models: Data Models (4 functions)
#   B-config: Configuration (6 functions)
#
# Layer 1: Core Logic (4 bricks)
# ────────────────────────────────────────────────────
#   B-validation: Validation (12 functions)
#     ↓ depends on: B-core-utils, B-data-models
#
#   B-impl-graph: Implementation Graph (10 functions)
#     ↓ depends on: B-core-utils
```

### Workflow 6: Validating Specific Aspects

Run specific validations:

```bash
# Validate only intent artifacts (specs, outcomes, decorators)
jigy validate intent

# Validate only brick definitions
jigy validate bricks

# Validate everything
jigy validate

# Get JSON output for programmatic use
jigy validate bricks --format json

# Example JSON output:
# {
#   "status": "passed",
#   "summary": {
#     "total_errors": 0,
#     "items_checked": 9
#   },
#   "bricks": {
#     "passed": true,
#     "errors": []
#   }
# }
```

## Command Reference

### `jigy validate bricks`

Validates brick definitions against the implementation graph.

**Checks performed**:
- Brick ID format (kebab-case)
- Required fields (id, name, layer, units)
- Layer field presence and value
- Brick partition (no gaps, no overlaps)
- Layer constraints (dependency hierarchy)
- Circular dependencies

**Exit codes**:
- `0`: All validations passed
- `1`: Validation failures
- `2`: Missing implementation graph

### `jigy layers`

Visualizes brick layer structure.

**Options**:
- `--summary`: Show only counts per layer
- `--verbose`: Show detailed function lists (future)
- `--project-root PATH`: Specify project root (default: current directory)

**Output includes**:
- Bricks grouped by layer
- Function counts per brick
- Dependencies between bricks
- Total summary (bricks, layers, functions)
- DAG status (cycles detected or not)

### `jigy layers suggest`

Suggests layer assignments based on dependency analysis.

**Algorithm**:
1. Analyze brick dependencies from implementation graph
2. Check for circular dependencies (error if found)
3. Assign layer 0 to bricks with no dependencies
4. Assign layer = max(dependency_layers) + 1 for other bricks
5. Compare with current layer assignments

**Options**:
- `--apply`: Update bricks.yaml with suggestions (requires confirmation)
- `--project-root PATH`: Specify project root

**Output includes**:
- Current layer (if set)
- Suggested layer with reason
- Match/mismatch indicators (✓/⚠)
- Summary of matches, mismatches, unset

## Tips & Best Practices

### 1. Run Validation Early and Often
```bash
# Add to your pre-commit workflow
jigy validate
```

### 2. Use Suggest for Initial Layer Assignment
```bash
# Let JIG figure out the layers based on dependencies
jigy layers suggest --apply
```

### 3. Visualize Before Major Refactoring
```bash
# See current architecture
jigy layers

# Make changes...

# See new architecture
jigy impl rebuild
jigy layers
```

### 4. Check for Cycles Before Adding Dependencies
```bash
# After adding new dependencies in code
jigy impl rebuild
jigy validate bricks

# If cycles are detected, refactor immediately
```

### 5. Use JSON Format for CI/CD
```bash
# Get machine-readable output
jigy validate bricks --format json | jq '.status'
```

### 6. Keep Layers Minimal
```bash
# Aim for 0-3 layers
# Layer 0: Foundation
# Layer 1: Core Logic
# Layer 2: Interface

# More layers = more complexity
```

### 7. Review Suggestions Before Applying
```bash
# Always review first
jigy layers suggest

# Only apply if suggestions make sense
jigy layers suggest --apply
```

## Troubleshooting

### "Circular dependencies exist"

**Problem**: Cannot suggest layers due to circular dependencies.

**Solution**: Run `jigy validate bricks` to see the specific cycles, then refactor code to break them.

### "Layer constraint violation"

**Problem**: Brick at lower layer depends on brick at higher layer.

**Solution**: Run `jigy layers suggest` to see correct layer assignments, then apply them.

### "Invalid ID format"

**Problem**: Using old numeric IDs (B-001) instead of kebab-case (B-core).

**Solution**: Rename brick IDs to kebab-case. See [LAYER_MIGRATION_GUIDE.md](./LAYER_MIGRATION_GUIDE.md).

### Suggestions don't match expected architecture

**Problem**: `jigy layers suggest` assigns different layers than expected.

**Solution**:
1. Check that brick dependencies match your architectural intent
2. Layer assignments are derived from actual code dependencies
3. If code doesn't match intent, refactor code or update bricks.yaml manually

## Advanced Examples

### Scripting with JIG

```bash
#!/bin/bash
# check-architecture.sh

# Rebuild graph
jigy impl rebuild || exit 1

# Run validation
jigy validate bricks --format json > validation.json

# Check status
STATUS=$(jq -r '.status' validation.json)

if [ "$STATUS" != "passed" ]; then
    echo "❌ Architecture validation failed"
    jq -r '.bricks.errors[] | "  - \(.message)"' validation.json
    exit 1
fi

echo "✅ Architecture validation passed"

# Show layer summary
jigy layers --summary
```

### Comparing Layer Assignments

```bash
# Save current layers
jigy layers > layers-before.txt

# Make code changes...
git add .
jigy impl rebuild

# Compare
jigy layers > layers-after.txt
diff layers-before.txt layers-after.txt
```

### Finding Specific Violations

```bash
# Get all validation errors as JSON
jigy validate bricks --format json | jq '.bricks.errors[] | select(.code == "LAYER_VIOLATION")'
```
