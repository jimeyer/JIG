# CLAUDE.md - Agent Context for JIG

This file provides guidance for AI agents working on the JIG codebase.

## Project Overview

JIG (Just-In-Graph) is a traceability and alignment tool that connects specifications to implementations to tests. It enables AI agents to understand and navigate complex codebases by providing machine-readable intent graphs.

## Key Commands

```bash
jigy rebuild        # Rebuild all graphs (implementation, verification, intent)
jigy validate       # Validate all artifacts against JIG rules
jigy layers         # Show brick layer structure
jigy align          # Check alignment between intent, implementation, and tests
```

## Creating JIG Intent Documents

When creating specifications, outcomes, or architecture documents:

### Filename Format

All intent documents must use the format: `{S/O/A}-{NNN}_{Title_In_Snake_Case}.md`

Examples:
- `S-001_Python_Code_Structure_Extraction.md`
- `O-015_Completeness_Validation_for_Intent_Graph.md`
- `A-001_JIG_Core_Architecture.md`

### Title Selection

**DO:**
- Describe BEHAVIOR or CAPABILITY, not implementation
- Use noun phrases that complete "This spec defines..."
- Be specific enough to distinguish from other specs
- Choose stable titles that won't change as implementation evolves

**DON'T:**
- Include version numbers (`User_Auth_v2`)
- Use temporal words (`New_Cache`, `Old_Parser`)
- Describe implementations (`Redis_Cache_Layer`)
- Describe tasks (`Fix_Auth_Bug`)
- Use vague comparatives (`Better_Error_Handling`)

### Examples

| Bad | Problem | Good |
|-----|---------|------|
| `New_Redis_Cache` | Temporal + implementation | `Response_Caching` |
| `Fix_Auth_Bug` | Task description | `Session_Persistence` |
| `User_Model_v2` | Version in title | `User_Profile_Schema` |
| `Better_Logging` | Vague comparative | `Structured_Log_Output` |
| `The_Main_Config` | Leading article | `Configuration_Loading` |

### Title Stability

Titles are semi-permanent. Changing a title causes:
- File rename → appears as delete + add in git history
- Broken external references (bookmarks, documentation links)
- Potential merge conflicts

Only rename when scope genuinely changed, not for stylistic preferences.

### H1 Header

The first H1 in the document body MUST match the frontmatter `title` exactly:

```markdown
---
id: S-001
title: Python Code Structure Extraction
type: specification
---

# Python Code Structure Extraction

...content...
```

## JIG Decorators

Use decorators to link code to specifications:

```python
import jig

@jig.implements("S-001")
def extract_functions(source: str) -> list:
    """Extract function definitions from Python source."""
    ...

@jig.verifies("S-001")
def test_extract_functions():
    """Verify function extraction works correctly."""
    ...
```

## Project Structure

```
jig/                    # Intent artifacts
  Charter.md            # Project goals (G-001 through G-005)
  architecture/         # A-NNN documents
  outcomes/             # O-NNN documents
  specifications/       # S-NNN documents
  bricks.yaml           # Brick definitions
  generated/            # Machine-generated graphs (never edit)

src/jig/                # Implementation code
tests/                  # Test code
```

## Validation

Before committing, always run:

```bash
jigy rebuild && jigy validate
```

If validation fails, fix the errors before proceeding.

