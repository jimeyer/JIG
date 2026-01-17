---
id: S-094
title: Markdown Output Format
type: specification
outcome: O-016
outcomes: [O-016]
---

# Markdown Output Format

CLI commands produce LLM-optimized markdown output when `-m/--markdown` flag is used.

## Acceptance Criteria

1. **Readable structure**: Headers, bullets, emphasis convey meaning
2. **Semantic organization**: Information grouped logically with clear hierarchy
3. **Dense content**: Information-rich without verbosity
4. **Self-contained**: Output stands alone as complete context
5. **Valid markdown**: Parseable by standard markdown processors

## Output Structure

### Validation Commands

```markdown
# JIG Validation: Passed

- **Specs:** 78 | **Outcomes:** 23 | **Bricks:** 11
- **Coverage:** 115 functions, 604 tests decorated
```

On failure:
```markdown
# JIG Validation: Failed

- **Specs:** 78 | **Outcomes:** 23 | **Bricks:** 11

## Errors

- **S-042.md:7** - Reference O-999 does not exist
- **S-043.md:12** - Required field 'outcome' missing
```

### Display Commands

```markdown
# Brick Structure

## Layer 0 (Foundation)
- **B-decorators**: JIG Core Decorators (1 unit)
- **B-validation**: Artifact Validation (4 units)

## Layer 1 (Services)
- **B-cli**: CLI Interface (10 units)
```

### Rebuild Commands

```markdown
# Rebuild Complete

**Graphs rebuilt:** implementation, verification, intent
**Duration:** 1.2s
```

## Verbose Mode (-m -v)

Verbose markdown adds:
- Detailed error context and suggestions
- Full file paths instead of basenames
- Additional metadata sections
- Expanded item descriptions

## Rationale

LLMs process markdown more effectively than terminal escape codes or dense JSON. Markdown provides structure (headers, lists) that aids comprehension while remaining human-readable. The format optimizes for AI agent context windows.
