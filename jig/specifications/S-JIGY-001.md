---
id: S-JIGY-001
type: specification
title: Parse frontmatter relationship fields from markdown
subsystem: jigy-tool
status: active
created: 2025-11-21
implements:
  - O-JIGY-001
---

# Specification: Frontmatter Relationship Parsing

## Purpose

Extract relationship fields (implements, satisfies, verifies, depends_on) from YAML frontmatter in Outcome and Specification markdown files, converting them into graph edges.

## Requirements

### 1. YAML Frontmatter Extraction

Parse YAML frontmatter from markdown files using standard YAML parser (PyYAML):

```yaml
---
id: S-AIR-001
type: specification
title: BikeState messages use operation_type field
subsystem: airspace
status: active
implements:
  - O-AIR-001
  - O-AIR-002
---
```

### 2. Relationship Field Support

Support four relationship types:

| Field | Meaning | Typical Usage |
|-------|---------|---------------|
| `implements:` | Implements/satisfies requirement | S→O, C→S |
| `satisfies:` | Satisfies outcome | S→O (synonym for implements) |
| `verifies:` | Verifies correctness | T→S, T→O |
| `depends_on:` | Depends on other node | Any→Any |

### 3. Value Format Handling

Accept both single values and lists:

```yaml
# Single value
implements: O-AIR-001

# List (preferred)
implements:
  - O-AIR-001
  - O-AIR-002

# Inline list (also valid YAML)
implements: [O-AIR-001, O-AIR-002]
```

### 4. Edge List Generation

Convert relationship fields to edge list:

```python
# From frontmatter:
{
  "id": "S-AIR-001",
  "implements": ["O-AIR-001", "O-AIR-002"]
}

# Generate edges:
[
  {"source": "S-AIR-001", "target": "O-AIR-001", "type": "implements"},
  {"source": "S-AIR-001", "target": "O-AIR-002", "type": "implements"}
]
```

### 5. Error Handling

- **Missing frontmatter:** Warn and skip file
- **Invalid YAML:** Report parse error with file path and line number
- **Unknown relationship fields:** Ignore (future compatibility)
- **Empty relationship list:** Valid (node with no relationships yet)

## Implementation Notes

**Location:** Likely in `jigy/parsers/markdown.py` or similar

**Dependencies:**
- PyYAML for frontmatter parsing
- Existing markdown file discovery code

**Data Flow:**
1. Discover markdown files (jig/outcomes/*.md, jig/specifications/*.md)
2. Read file contents
3. Extract YAML frontmatter (between `---` delimiters)
4. Parse YAML into dict
5. Extract relationship fields
6. Normalize to list (if single value)
7. Generate edge objects
8. Store in node registry

**Performance Target:** <500ms to parse 100 markdown files

## Validation Rules

- Source node ID must match file's frontmatter `id:` field
- Relationship field values must be valid node ID format: `[A-Z]-[A-Z]+-\d+`
- Target node existence validated separately (in S-JIGY-004)

## Test Cases

```python
# @jig T-JIGY-001 verifies:S-JIGY-001 subsystem:jigy-tool
def test_parse_frontmatter_single_implements():
    """Test parsing single implements value"""
    content = """---
id: S-TEST-001
implements: O-TEST-001
---
# Content
"""
    result = parse_frontmatter(content)
    assert result["implements"] == ["O-TEST-001"]
    
# @jig T-JIGY-002 verifies:S-JIGY-001 subsystem:jigy-tool
def test_parse_frontmatter_list_implements():
    """Test parsing list of implements values"""
    content = """---
id: S-TEST-001
implements:
  - O-TEST-001
  - O-TEST-002
---
"""
    result = parse_frontmatter(content)
    assert result["implements"] == ["O-TEST-001", "O-TEST-002"]

# @jig T-JIGY-003 verifies:S-JIGY-001 subsystem:jigy-tool  
def test_build_edges_from_relationships():
    """Test edge list generation from relationships"""
    node = {
        "id": "S-TEST-001",
        "implements": ["O-TEST-001", "O-TEST-002"]
    }
    edges = build_edges(node)
    assert len(edges) == 2
    assert edges[0] == {"source": "S-TEST-001", "target": "O-TEST-001", "type": "implements"}
```

## References

- O-JIGY-001: JIG graph accurately reflects all OSTC relationships
- S017 Analysis: Part 3.1.1 (Priority 1: Parse frontmatter relationships)
- JIG v6.1 Spec: §1.2 (Intent files with frontmatter)

