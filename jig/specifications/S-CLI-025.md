---
id: S-CLI-025
type: specification
title: "Validation distinguishes structural vs semantic errors"
subsystem: cli
implements:
  - O-CLI-006
created: 2025-11-22
---

# S-CLI-025: Validation distinguishes structural vs semantic errors

## Specification

JIG commands SHALL clearly separate structural validation (performed during index rebuild) from semantic validation (performed by status command).

## Structural Validation (Index Rebuild)

**Performed by**: `jigy index rebuild`
**When**: While parsing node files and building index
**Purpose**: Ensure files are readable and structurally sound

**Checks**:
1. **Parseability**: Valid YAML/JSON syntax
2. **ID format**: Matches expected pattern (e.g., `O-CLI-001`)
3. **Required fields**: Presence of id, type, title, subsystem
4. **Node type validity**: Type is one of: outcome, specification, test, code
5. **Reference existence**: Edge targets exist as files

**Behavior on error**:
- Report which file failed and why
- Skip invalid files (log warning)
- Continue building index with valid files
- Exit 0 (rebuild is best-effort)

**Output example**:
```
Building graph index...
✓ Scanned 215 files
⚠ Skipped 2 files:
  - jig/outcomes/O-CLI-999.md: Invalid ID format
  - jig/tests/T-BROKEN.md: Missing required field 'subsystem'
✓ Indexed 213 nodes, 183 edges
```

## Semantic Validation (Status)

**Performed by**: `jigy status`
**When**: After index is loaded
**Purpose**: Ensure graph relationships make semantic sense

**Checks**:
1. **Edge type rules**: Valid edge types (O→S, S→S, S→T, T→T, not O→O)
2. **Subsystem hierarchy**: No cycles in subsystem parent/child relationships
3. **Self-loops**: No nodes with edges to themselves
4. **Quality metrics**: Orphans, unassigned nodes, isolated subgraphs

**Behavior on error**:
- Report all semantic violations
- Exit 1 if errors present
- Exit 0 if only warnings

**Output example**:
```
Validation Results:

✓ Schema Checks
  ✓ All node IDs valid (213 nodes)

✗ Graph Consistency
  ✗ Invalid edge types (2):
    - O-CLI-005 → O-CLI-006 (Outcome→Outcome not allowed)
    - S-AUTH-001 → S-AUTH-001 (self-loop)

✗ Graph is INVALID
```

## Separation Rationale

**Why separate structural and semantic validation:**

1. **Different failure modes**:
   - Structural errors: File corruption, typos, missing fields
   - Semantic errors: Logic violations, relationship rules, quality issues

2. **Different fix strategies**:
   - Structural: Fix file syntax, add missing fields
   - Semantic: Redesign relationships, fix edge types

3. **Different timing**:
   - Structural: During index build (must be valid to parse)
   - Semantic: After index built (requires complete graph)

4. **Better error messages**:
   - Structural: "File X line Y: syntax error"
   - Semantic: "Node A → Node B: invalid edge type"

5. **Clear mental model**:
   - `rebuild`: Make index readable
   - `status`: Check if readable index is correct

## Implementation Requirements

- **Index rebuild** uses file parsing and schema validation
- **Status** uses `validate_graph_comprehensive()` from `jig.core.validation`
- Clear error messages indicate which validation stage failed
- Documentation explains the separation

## Edge Cases

**What if rebuild fails?**
- Status cannot run (no index to validate)
- User must fix structural errors first
- Clear message: "No index found. Run `jigy index rebuild`"

**What if rebuild succeeds but status fails?**
- Index is readable but semantically incorrect
- User fixes semantic issues (edge types, cycles)
- Re-run `jigy status` to verify (no rebuild needed)

**What if both have errors?**
- Fix structural errors first (rebuild)
- Then fix semantic errors (status)
- Sequential workflow is clear

## Documentation

Users should understand:
1. **Rebuild validates structure**: "Can I parse this?"
2. **Status validates semantics**: "Does this make sense?"
3. **Workflow**: rebuild (structure) → status (semantics) → commit

## References

- Rebuild implementation: `src/jig/core/graph.py` (load_from_dir)
- Status validation: `src/jig/core/validation.py` (to be created)
- Plan: WU1 (validation extraction)

## Related Nodes

- Implements: O-CLI-006
- Related: S-CLI-022 (status validation), S-CLI-024 (validate removal)
