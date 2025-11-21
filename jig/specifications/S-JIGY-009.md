---
id: S-JIGY-009
type: specification
title: Index rebuild regenerates graph-index.yaml from sources
subsystem: jigy-tool
status: active
created: 2025-11-21
implements:
  - O-JIGY-003
---

# Specification: Index Rebuild

## Purpose

Regenerate `jig/graph-index.yaml` from source files (markdown frontmatter + code annotations), establishing a clear source of truth and enabling automatic synchronization between code and Intent.

## Requirements

### 1. Rebuild Command

**Command:** `jigy index --rebuild [--dry-run] [--backup]`

```bash
$ jigy index --rebuild

Rebuilding graph-index.yaml from sources...

Scanning sources:
  ✓ jig/outcomes/*.md (18 nodes)
  ✓ jig/specifications/*.md (47 nodes)
  ✓ src/ for @jig annotations (24 code nodes)
  ✓ test/ for @jig annotations (37 test nodes)

Total nodes: 126 (18 O, 47 S, 24 C, 37 T)
Total edges: 113

Validating...
  ✓ All node IDs valid
  ✓ All edge targets exist
  ✓ No duplicate node IDs

Writing jig/graph-index.yaml...
  ✓ Backed up to jig/graph-index.yaml.bak
  ✓ Wrote 126 nodes, 113 edges

Done in 1.2s
```

**Dry-run mode:**
```bash
$ jigy index --rebuild --dry-run

Would rebuild graph-index.yaml:
  Sources:
    - jig/outcomes/*.md (18 nodes)
    - jig/specifications/*.md (47 nodes)
    - src/ annotations (24 code nodes)
    - test/ annotations (37 test nodes)
  
  Changes from current graph-index.yaml:
    + 2 new nodes (C-AUTH-003, T-AUTH-042)
    - 1 removed node (C-OLD-001)
    ~ 3 nodes updated (relationships changed)
  
  No write performed (use without --dry-run to apply)
```

### 2. Source Priority

**Source of truth:**
1. **O/S nodes:** Markdown frontmatter in `jig/{outcomes,specifications}/`
2. **C/T nodes:** `@jig` annotations in source/test files
3. **Relationships:** Union of frontmatter + annotations

**If conflict (same node ID in multiple sources):**
- ERROR if same ID in different files with different types
- WARN if same ID in multiple locations with same type (pick first, report)
- ERROR if O/S in annotation (should be markdown) or C/T in markdown (should be annotation)

### 3. Output Format

Generate node-centric YAML format:

```yaml
version: '1.0'
generated: '2025-11-21T10:30:00Z'
generator: 'jigy v0.5.0'

nodes:
  - id: O-AUTH-001
    type: outcome
    title: Users authenticate securely across devices
    subsystem: auth
    status: active
    file: jig/outcomes/O-AUTH-001.md
  
  - id: S-AUTH-001
    type: specification
    title: JWT tokens with 24-hour expiration
    subsystem: auth
    status: active
    file: jig/specifications/S-AUTH-001.md
    implements:
      - O-AUTH-001
  
  - id: C-AUTH-001
    type: code
    title: JWTAuthenticator
    subsystem: auth
    status: active
    file: src/auth/jwt.py
    line: 42
    implements:
      - S-AUTH-001
  
  - id: T-AUTH-001
    type: test
    title: test_jwt_token_validation
    subsystem: auth
    status: active
    file: test/auth/test_jwt.py
    line: 18
    verifies:
      - S-AUTH-001
```

**Node-centric (relationships on nodes)** is preferred for hand-editing.

### 4. Rebuild Process

```python
# @jig C-JIGY-009 implements:S-JIGY-009 subsystem:jigy-tool interface:public
def rebuild_graph_index():
    """Rebuild graph-index.yaml from all sources"""
    
    # 1. Discover all nodes
    nodes = []
    
    # O/S from markdown
    for file in discover_markdown_files():
        node = parse_markdown_node(file)
        nodes.append(node)
    
    # C/T from annotations
    annotations = scan_annotations(['src', 'test'])
    for annotation in annotations:
        node = annotation_to_node(annotation)
        nodes.append(node)
    
    # 2. Validate
    validate_result = validate_nodes(nodes)
    if not validate_result.valid:
        print_errors(validate_result.errors)
        return False
    
    # 3. Build registry (deduplicates, merges relationships)
    registry = build_registry_from_nodes(nodes)
    
    # 4. Backup existing file
    if Path('jig/graph-index.yaml').exists():
        shutil.copy('jig/graph-index.yaml', 'jig/graph-index.yaml.bak')
    
    # 5. Write new file
    write_graph_index_yaml(registry, 'jig/graph-index.yaml')
    
    return True
```

### 5. Validation Before Write

Validate complete graph before writing:

- ✓ All node IDs match pattern: `[OSTC]-[A-Z]+-\d+`
- ✓ All node types valid: outcome, specification, code, test
- ✓ All files exist (warn if not, don't fail)
- ✓ No duplicate node IDs
- ✓ All edge targets exist (from relationships)
- ✓ Edge types valid for node types (S→O ok, O→S not ok)

If validation fails: Don't write file, report errors

### 6. Idempotence

Running rebuild twice with no changes should produce identical output:

```bash
$ jigy index --rebuild
# Creates graph-index.yaml

$ jigy index --rebuild
# No changes detected, file unchanged (or byte-identical)
```

**Implementation:** Deterministic YAML generation (sorted keys, consistent formatting)

### 7. Diff Mode

Show what changed without rebuilding:

```bash
$ jigy index --diff

Comparing current graph-index.yaml with sources:

Changes:
  + C-AUTH-003: JWTRefreshHandler (new annotation in src/auth/refresh.py:22)
  - C-OLD-001: DeprecatedAuth (annotation removed)
  ~ S-AUTH-001: Relationships changed
      + implements: O-AUTH-002 (added in frontmatter)

2 additions, 1 removal, 1 modification
```

## Implementation Notes

**Location:** `jigy/commands/index_rebuild.py`

**Dependencies:**
- AnnotationScanner (S-JIGY-008)
- Markdown parser (S-JIGY-001)
- Graph validator (S-JIGY-004)
- YAML generator

**Performance Target:** <3 seconds for 1000-node graph

**Backup Strategy:**
- Always backup before overwrite: `graph-index.yaml.bak`
- Keep last N backups (configurable, default=5)
- Timestamped backups: `graph-index.yaml.2025-11-21T10-30-00.bak`

## Test Cases

```python
# @jig T-JIGY-024 verifies:S-JIGY-009 subsystem:jigy-tool
def test_rebuild_from_sources():
    """Test complete rebuild from markdown + annotations"""
    # Setup test project with O/S markdown and C/T annotations
    project = create_test_project()
    
    result = rebuild_graph_index(project.path)
    
    assert result.success
    assert project.path / 'jig/graph-index.yaml' exists
    
    # Load and verify
    graph = load_yaml(project.path / 'jig/graph-index.yaml')
    assert len(graph['nodes']) == 126

# @jig T-JIGY-025 verifies:S-JIGY-009 subsystem:jigy-tool
def test_rebuild_idempotence():
    """Test rebuild is idempotent"""
    project = create_test_project()
    
    # Rebuild twice
    rebuild_graph_index(project.path)
    content1 = read_file('jig/graph-index.yaml')
    
    rebuild_graph_index(project.path)
    content2 = read_file('jig/graph-index.yaml')
    
    assert content1 == content2  # Byte-identical

# @jig T-JIGY-026 verifies:S-JIGY-009 subsystem:jigy-tool
def test_rebuild_detects_conflicts():
    """Test rebuild detects duplicate node IDs"""
    project = create_test_project()
    
    # Create conflict: same ID in two files
    write_file('src/a.py', '# @jig C-TEST-001 ...')
    write_file('src/b.py', '# @jig C-TEST-001 ...')  # Duplicate!
    
    result = rebuild_graph_index(project.path)
    
    assert not result.success
    assert "Duplicate" in result.errors[0]
```

## References

- O-JIGY-003: Code and Intent stay synchronized
- S-JIGY-001: Parse frontmatter relationships (O/S source)
- S-JIGY-008: Fast annotation scanner (C/T source)
- S-JIGY-004: Edge validation (validate before write)
- S017 Analysis: Part 3.4.2 (Index rebuild)
- JIG v6.1 Spec: §8.2 (Graph index format)

