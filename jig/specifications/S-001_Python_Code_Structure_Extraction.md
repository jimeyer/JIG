---
id: S-001
title: Python Code Structure Extraction
type: specification
outcomes: [O-001]
---

# Python Code Structure Extraction

## Constraints

1. **Discovers modules, classes, functions, imports, calls, inheritance, containment**
   - Modules: File path, dotted module name, imports, exports
   - Classes: Name, parent classes, methods, line numbers
   - Functions: Name, signature, parent (class or module), line numbers
   - Imports: Both `import x` and `from x import y` statements
   - Calls: Direct function calls only (no type inference for method calls)
   - Inheritance: Class extends relationships
   - Containment: Module contains classes, classes contain methods

2. **99%+ accuracy for module/class discovery, 95%+ for direct calls**
   - Module and class structure is deterministic from AST
   - Function calls may have ambiguity (dynamic calls, method calls on unknown types)
   - Measured against hand-validated test fixtures

3. **No type inference required (direct calls only)**
   - V1 captures calls where target is statically known: `func()`, `module.func()`
   - V1 skips method calls on instances: `obj.method()` (would require type inference)
   - This constraint keeps V1 simple and fast while covering 80%+ of real-world traceability needs

## Node ID Format

- Modules: `M-dotted.module.path` (e.g., `M-jig.core.graph`)
- Classes: `C-dotted.module.path.ClassName` (e.g., `C-jig.core.graph.Graph`)
- Functions: `F-dotted.module.path.func_name` (e.g., `F-jig.utils.io.read_file`)
- Methods: `F-dotted.module.path.ClassName.method_name`

## Implementation Approach

Use Python's built-in `ast` module:
1. `ast.parse()` to get AST from source file
2. Custom `ast.NodeVisitor` subclass to traverse the tree
3. Extract `ast.Module`, `ast.ClassDef`, `ast.FunctionDef`, `ast.AsyncFunctionDef` nodes
4. Build node dictionaries with metadata (line numbers, signatures, etc.)
5. Return language-agnostic format for graph construction

## Edge Cases

- Nested classes: Supported (ID includes parent class)
- Lambda functions: Skipped (not named, can't be referenced)
- Decorators: Extracted separately (see S-002)
- Private functions/classes (leading `_`): Included (developer may want full graph)
- Dynamic imports: Not tracked (requires runtime analysis)

## Rationale

AST analysis provides accurate, fast structural analysis without requiring code execution. Python's `ast` module is stable, well-documented, and handles all modern Python syntax including type hints, async/await, and decorators.

This specification focuses on V1 scope: structural relationships that are deterministic from static analysis. Method call tracking (requiring type inference) is deferred to V2 to keep the initial implementation tractable.
