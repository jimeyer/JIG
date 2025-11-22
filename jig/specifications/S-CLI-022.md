---
id: S-CLI-022
type: specification
title: "Status command validates graph semantics and shows health metrics"
subsystem: cli
implements:
  - O-CLI-006
  - O-CLI-007
created: 2025-11-22
---

# S-CLI-022: Status command validates graph semantics and shows health metrics

## Specification

The `jigy status` command SHALL perform comprehensive semantic validation in addition to displaying graph metrics, providing a single command for complete graph health assessment.

## Validation Scope

### Semantic Checks (Performed by Status)

1. **Edge type rules**: Validate allowed edge types (O→S, S→S, S→T, T→T, etc.)
2. **Subsystem hierarchy**: Detect cycles in subsystem relationships
3. **Self-loops**: Detect and report nodes with edges to themselves
4. **Quality warnings**: Report orphans, unassigned nodes, isolated subgraphs

### Structural Checks (NOT Performed by Status)

These are validated during `jigy index rebuild`:
- File parseability (valid YAML/JSON)
- ID format (matches pattern)
- Required fields presence
- Reference existence (edge targets exist)

This separation ensures `status` operates on an already-validated index.

## Output Format

```
JIG Graph Status

✓ 215 nodes, 183 edges, 7 subsystems

Node Summary:
  Outcomes: 42
  Specifications: 78
  Tests: 65
  Code: 30

Subsystems: api (45), auth (23), cli (67), core (42), db (18), ui (12), utils (8)

Validation Results:

✓ Schema Checks
  ✓ All node IDs valid (215 nodes)
  ✓ No duplicate IDs

✓ Graph Consistency
  ✓ All edge targets exist (183 edges)
  ✓ No self-loops
  ✓ Edge type rules valid (O→S, S→S, S→T, T→T)

✓ Subsystem Hierarchy
  ✓ No cycles detected

Warnings:
  ⚠ Orphaned nodes (3): O-TEST-002, S-AUTH-007, T-API-015

✅ Graph is valid
```

## Exit Code Behavior

- **Exit 0**: No errors (warnings are acceptable)
- **Exit 1**: Semantic errors detected
- Exit code determined AFTER validation completes
- Configurable via flags (see S-CLI-023)

## Performance Requirements

- Combined metrics + validation SHALL complete in <2s for graphs with <500 nodes
- Validation overhead SHALL be <100ms beyond existing status metrics
- Graph loaded only once (shared between metrics and validation)

## Implementation Requirements

- Use `validate_graph_comprehensive()` from `jig.core.validation`
- Run validation AFTER calculating status metrics
- Display validation results in separate section
- Use consistent formatting (✓/✗ symbols, color coding)
- Preserve existing status metrics display

## Error Handling

- If index missing: Report "No index found. Run `jigy index rebuild`"
- If validation fails: Show errors, exit 1
- If validation warnings only: Show warnings, exit 0
- Validation exceptions: Report clearly, exit 1

## Rationale

Combining metrics and validation into `status` provides:
1. Single command for complete graph health (O-CLI-006)
2. Consistent CI validation strategy (O-CLI-007)
3. Separation of structural (rebuild) vs semantic (status) validation
4. Clear developer workflow: rebuild → status → commit

## References

- Implementation: `src/jig/cli/status.py`
- Validation module: `src/jig/core/validation.py` (to be created in WU1)
- Related: S-CLI-025 (Structural vs semantic validation separation)

## Related Nodes

- Implements: O-CLI-006, O-CLI-007
- Related: S-CLI-023 (configurable exit codes), S-CLI-025 (validation separation)
