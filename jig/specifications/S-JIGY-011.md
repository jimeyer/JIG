---
id: S-JIGY-011
type: specification
title: Exclusion filtering prevents test fixture pollution
subsystem: jigy-tool
status: active
created: 2025-11-21
implements:
  - O-JIGY-004
---

# Specification: Exclusion Filtering

## Purpose

Prevent test fixtures, template files, and build artifacts from polluting the JIG node index during scanning and rebuild operations.

## Requirements

The jigy scanner and index builder SHALL exclude non-real nodes using a three-tier filtering approach.

### Tier 1: Path-Based Exclusions (.jigignore)

**File:** `.jigignore` in project root (gitignore syntax)

**Behavior:**
- Load patterns from `.jigignore` if exists, else use defaults
- Pattern matching uses fnmatch/glob syntax
- Patterns apply to both markdown discovery and annotation scanning
- Relative to project root directory

**Default patterns (when .jigignore doesn't exist):**
```
**/__pycache__/       # Python cache
**/*.pyc
.venv/
.pytest_cache/
dist/
build/
```

**Example .jigignore:**
```
# Test files (contain fixtures)
**/test_*.py
**/conftest.py

# Build artifacts
**/__pycache__/
**/*.pyc
.venv/
dist/
build/

# IDE files
.vscode/
.idea/
*.swp

# Project-specific exclusions
docs/examples/
```

**Implementation:** `IgnoreFilter` class checks paths before scanning

### Tier 2: Status-Based Filtering

**Markdown frontmatter field:** `status`

**Excluded statuses:**
- `template` - Template/example files
- `deprecated` - Old nodes kept for history
- `draft` - Work in progress

**Included statuses:**
- `active` - Real, current nodes (default)
- `planned` - Future work (valid Intent)
- Missing/null - Defaults to active

**Behavior:**
- Markdown discovery filters out excluded statuses
- Only active/planned nodes appear in index
- Self-documenting approach (files declare themselves as non-active)

**Implementation:** Filter in `IndexBuilder.discover_markdown_nodes()`

### Tier 3: Fixture Pattern Detection

**Annotation IDs to skip (reserved for test fixtures):**
- `C-TEST-*` - Code test fixtures
- `T-TEST-*` - Test test fixtures
- `C-MOCK-*` - Mock objects
- `C-FIXTURE-*` - Explicit fixtures
- `C-EXAMPLE-*` - Example code

**Behavior:**
- Scanner skips annotations matching fixture patterns
- Prevents test fixture pollution at parse time
- Safety net for test files not in .jigignore

**Implementation:** `_is_test_fixture()` in `parse_annotation_line()`

## Data Flow

```
File discovered
    ↓
[Tier 1] Check .jigignore patterns → Skip if matched
    ↓
Parse frontmatter/annotation
    ↓
[Tier 2] Check status field → Skip if template/deprecated/draft
    ↓
[Tier 3] Check node ID pattern → Skip if C-TEST-*, etc.
    ↓
Add to index (real node)
```

## Configuration

Optional `jig.toml` settings (future enhancement):
```toml
[jig.scanning]
exclude_statuses = ["template", "deprecated", "draft"]
fixture_patterns = ["*-TEST-*", "*-MOCK-*", "*-FIXTURE-*", "*-EXAMPLE-*"]
```

## Rationale

**Layered defense prevents pollution at multiple levels:**
1. **User control (.jigignore):** Project-specific exclusions, familiar syntax
2. **Metadata-driven (status):** Self-documenting intent, no external config needed
3. **Pattern-based (fixtures):** Safety net, prevents common mistakes

**Why three tiers?**
- .jigignore alone misses inline test fixtures (strings in code)
- Status filtering alone requires all templates to be marked
- Fixture patterns alone don't handle build artifacts

Together they provide comprehensive protection with minimal user effort.

## Performance Impact

- .jigignore checking: O(patterns × files) - negligible with typical pattern counts
- Status filtering: No overhead (already parsing frontmatter)
- Fixture pattern matching: O(annotations) - regex compile once, match many times
- Overall: <5% performance impact on large codebases

## Error Handling

- **Missing .jigignore:** Use default patterns (silent fallback)
- **Invalid .jigignore pattern:** Log warning, skip pattern, continue
- **Unknown status value:** Treat as active (permissive)
- **Malformed node ID:** Already handled by annotation parser

## Test Cases

```python
# @jig T-JIGY-030 verifies:S-JIGY-011 subsystem:jigy-tool
def test_jigignore_excludes_test_files():
    """Test .jigignore excludes test_*.py files"""

# @jig T-JIGY-031 verifies:S-JIGY-011 subsystem:jigy-tool
def test_status_template_excluded():
    """Test status: template nodes excluded from index"""

# @jig T-JIGY-032 verifies:S-JIGY-011 subsystem:jigy-tool
def test_fixture_pattern_detection():
    """Test C-TEST-*, T-TEST-* patterns excluded"""

# @jig T-JIGY-033 verifies:S-JIGY-011 subsystem:jigy-tool
def test_index_rebuild_excludes_fixtures():
    """Test full rebuild with all three tiers active"""
```

## References

- O-JIGY-004: JIG scanning excludes test fixtures and template files
- S-JIGY-008: Fast annotation scanner (extended by this spec)
- S-JIGY-009: Index rebuild (extended by this spec)
- Discovery: WU8-10 implementation, `jigy index rebuild` output revealed issue

## Migration Guide

**For existing projects:**

1. Create `.jigignore` if needed:
   ```bash
   jig init  # Generates default .jigignore
   ```

2. Mark template files:
   ```yaml
   # In jig/outcomes/O-EXAMPLE-001.md
   status: template  # ← Add this line
   ```

3. Rebuild index:
   ```bash
   jigy index rebuild
   # Should now be clean
   ```

**For new projects:**
- `jig init` creates `.jigignore` automatically
- Templates marked at creation time
- No migration needed
