---
id: S-002
title: Implements Decorator Extraction
type: specification
outcomes: [O-002]
---

# Implements Decorator Extraction

## Constraints

1. **Syntax: `@jig.implements("S-001")` or `@jig.implements("S-001", "S-002")`**
   - Single specification: `@jig.implements("S-001")`
   - Multiple specifications: `@jig.implements("S-001", "S-002", ...)`
   - Alternative import form: `from jig import implements` then `@implements("S-001")`

2. **Validates spec IDs match pattern `S-{number}` or `O-{number}`**
   - Regex: `^[SO]-\d+$`
   - Valid: `S-001`, `O-042`, `S-999`
   - Invalid: `SPEC-001`, `S-1A`, `specification-001`
   - Invalid IDs generate warnings but don't fail the build

3. **99%+ extraction accuracy**
   - All well-formed decorators are extracted
   - Measured against hand-annotated test fixtures

## Decorator Placement

Decorators can be applied to:
- Functions (module-level)
- Methods (class-level)
- Classes (decorates the entire class)

Example:
```python
from jig import implements

@implements("S-001")
class GraphBuilder:
    """Builds implementation graph from source files."""

    @implements("S-003")
    def write_ndjson(self, output_path: Path) -> None:
        """Write graph to NDJSON format."""
        pass
```

## Graph Representation

1. **Node metadata**: Add `"implements": ["S-001", "S-002"]` field to function/class nodes
2. **Implementation edges**: Create edges `{"source": "F-X", "target": "S-Y", "type": "implements"}`

This dual representation enables:
- Quick lookup: "What does this function implement?" (node metadata)
- Reverse lookup: "What implements this spec?" (traverse edges)

## Error Handling

- **Malformed decorator syntax**: Log warning, skip decorator, continue analysis
- **Invalid spec ID format**: Log warning, include in graph with validation flag
- **Duplicate decorators**: De-duplicate automatically (same spec applied multiple times)
- **Missing spec file**: Tracked separately (link validation happens later in workflow)

## Implementation Approach

1. During AST traversal, inspect `decorator_list` on `ast.FunctionDef` and `ast.ClassDef` nodes
2. Look for `ast.Call` nodes where:
   - Function is `ast.Attribute` with attr `"implements"`
   - OR function is `ast.Name` with id `"implements"` (if directly imported)
3. Extract string arguments as spec IDs
4. Validate format with regex
5. Attach to node metadata and create edges

## Rationale

Python decorators provide a natural, non-invasive way to annotate code with metadata. Developers can add `@jig.implements()` at the point of implementation without changing function signatures or runtime behavior.

This approach:
- Keeps annotation close to code (better than separate mapping files)
- Uses familiar Python syntax (no new DSL to learn)
- Works with IDEs (syntax highlighting, navigation)
- Version controls with the code (no out-of-band tracking)
