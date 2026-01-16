---
id: S-057
title: Project Root Auto-Discovery
type: specification
outcomes: [O-019]
architecture: [A-002]
---

# Project Root Auto-Discovery

The CLI automatically finds the project root by walking up directories from the current working directory.

**Behavior:**
- Starting from current directory, walk up parent chain
- Look for a `jig/` directory at each level
- Return the parent of the found `jig/` directory as project root
- Raise clear error if not found after reaching filesystem root

**Error Message:**
```
Not in a JIG project. No jig/ directory found.
```

**Function Signature:**
```python
def find_project_root(start_dir: Path | None = None) -> Path
```

**Rationale:** Eliminates `--project-root` flag from all commands. Users can run JIG commands from any subdirectory within a project.
