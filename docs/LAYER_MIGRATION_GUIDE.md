# Layer Validation Migration Guide

This guide helps you migrate existing JIG projects to use the new layer validation features introduced in WU1-WU6.

## What Changed

The layer validation system introduces:

1. **Brick ID Format Validation (S-035)**: Brick IDs must use kebab-case (e.g., `B-core-utils`) instead of numeric format (e.g., `B-001`)
2. **Required Layer Field (S-036, S-037)**: All bricks must have a `layer` field with a non-negative integer value
3. **Layer Constraint Validation (S-038)**: Bricks must follow dependency hierarchy (higher layers depend on lower layers)
4. **Circular Dependency Detection (S-039)**: Circular dependencies between bricks are not allowed
5. **New CLI Commands**: `jigy layers` (visualization) and `jigy layers suggest` (automatic layer assignment)

## Migration Workflow

### Step 1: Check Current Status

Run validation to see what needs to be fixed:

```bash
jigy validate bricks
```

You'll likely see errors like:
- `Invalid ID format. Must match pattern B-[a-z0-9-]+` (for old numeric IDs)
- `Missing required field 'layer'` (for bricks without layer field)

### Step 2: Update Brick IDs to Kebab-Case

**Before** (jig/bricks.yaml):
```yaml
bricks:
  - id: B-001
    name: Core Utilities
    units:
      - F-core.utils.helper

  - id: B-002
    name: API Handler
    units:
      - F-api.handler.process
```

**After**:
```yaml
bricks:
  - id: B-core-utils
    name: Core Utilities
    units:
      - F-core.utils.helper

  - id: B-api-handler
    name: API Handler
    units:
      - F-api.handler.process
```

**Guidelines for ID Conversion**:
- Use lowercase letters, numbers, and hyphens
- Start with `B-` prefix
- Use descriptive names based on the brick's purpose
- Examples: `B-core`, `B-api`, `B-cli`, `B-validation`, `B-impl-graph`

### Step 3: Add Layer Fields Using Suggest Command

The easiest way to add layers is to use the automatic suggestion:

```bash
# See suggested layer assignments
jigy layers suggest

# Apply suggestions to bricks.yaml
jigy layers suggest --apply
```

The suggest command:
- Analyzes brick dependencies from the implementation graph
- Assigns layer 0 to bricks with no dependencies (foundation)
- Assigns higher layers based on dependency depth
- Shows current vs. suggested layers with visual indicators (✓/⚠)

**Manual Layer Assignment** (if you prefer):

```yaml
bricks:
  - id: B-core-utils
    name: Core Utilities
    layer: 0  # Foundation - no dependencies
    units:
      - F-core.utils.helper

  - id: B-api-handler
    name: API Handler
    layer: 1  # Depends on B-core-utils
    units:
      - F-api.handler.process
```

### Step 4: Validate Again

After making changes, validate to ensure everything is correct:

```bash
jigy validate bricks
```

You should see:
```
✓ Validating brick definitions
✓ Validating brick partition
✓ Validating brick layer constraints
✓ Validating brick cycles

Brick validation passed.
```

### Step 5: Visualize Layer Structure

View your brick layer structure:

```bash
# Full visualization
jigy layers

# Summary (counts only)
jigy layers --summary
```

Example output:
```
Brick Layer Structure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Layer 0: Foundation (2 bricks)
────────────────────────────────────────────────────────────
  B-core-utils: Core Utilities (5 functions)
  B-data-models: Data Models (3 functions)

Layer 1: Core Logic (2 bricks)
────────────────────────────────────────────────────────────
  B-validation: Validation (12 functions)
    ↓ depends on: B-core-utils

  B-impl-graph: Implementation Graph (8 functions)
    ↓ depends on: B-core-utils, B-data-models

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 4 bricks, 2 layers, 28 functions
Dependency graph: DAG ✓ (no cycles)
```

## Common Issues & Solutions

### Issue 1: Layer Constraint Violations

**Error**:
```
✗ B-api (layer: 0) depends on B-cli (layer: 1)
  Violation: F-api.handler → F-cli.main
  Layer 0 brick cannot depend on layer 1 brick
```

**Solution**: Use `jigy layers suggest` to get correct layer assignments, or manually adjust layers so dependencies flow downward (higher layers depend on lower layers).

### Issue 2: Circular Dependencies

**Error**:
```
✗ Circular dependency detected: B-a → B-b → B-a
  Cycle includes:
    F-a.func1 → F-b.func2
    F-b.func3 → F-a.func4
```

**Solution**: Refactor code to break the circular dependency. Common approaches:
- Extract shared functionality into a new lower-layer brick
- Invert the dependency relationship
- Use dependency injection or events instead of direct calls

### Issue 3: Old Numeric IDs Still in Use

**Error**:
```
✗ Brick 'B-001': Invalid ID format. Must match pattern B-[a-z0-9-]+
```

**Solution**: Rename all brick IDs to kebab-case following the pattern `B-descriptive-name`.

## Layer Assignment Best Practices

### Layer 0 (Foundation)
- Utility functions
- Data models
- Core types
- No dependencies on other project bricks

### Layer 1 (Core Logic)
- Business logic
- Domain services
- Data processing
- Depends only on Layer 0

### Layer 2 (Interface)
- CLI commands
- API endpoints
- External interfaces
- Depends on Layer 0 and/or Layer 1

### Higher Layers
- Use sparingly (often 0-2 layers is sufficient)
- Each layer should have a clear architectural purpose

## Continuous Validation

Add validation to your development workflow:

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

jigy validate bricks
if [ $? -ne 0 ]; then
    echo "❌ Brick validation failed. Fix errors before committing."
    exit 1
fi
```

### CI/CD Pipeline
```yaml
# .github/workflows/validate.yml
- name: Validate JIG Artifacts
  run: |
    jigy validate bricks
    jigy validate intent
```

## FAQ

**Q: Can bricks at the same layer depend on each other?**
A: Only at layer 0. Bricks at layer 1 and higher cannot depend on other bricks at the same layer.

**Q: What if I need to reorganize my layers?**
A: Run `jigy layers suggest` to see recommendations based on current dependencies. Use `--apply` to update bricks.yaml automatically.

**Q: Do I need to rebuild the implementation graph after changing layers?**
A: No, changing layer values doesn't require rebuilding. However, if you change code that affects dependencies, run `jigy impl rebuild` first.

**Q: Can I skip layer validation?**
A: Layer validation is optional if you don't have an implementation graph. Once you have `jig/generated/implementation-graph.ndjson`, validation will check layers. You can run `jigy validate intent` to skip brick validation.

## Support

- Report issues: [GitHub Issues](https://github.com/anthropics/claude-code/issues)
- See full documentation: `jigy --help`, `jigy layers --help`
- Validation reference: A001 Section 4 (Brick Definitions)
