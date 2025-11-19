# JIG Data Formats Specification

**Version:** 1.0
**Status:** Active
**Last Updated:** 2025-11-19

This document specifies the data formats used by JIG for Intent nodes, configuration files, and templates.

---

## Table of Contents

1. [OSTC Node Format](#ostc-node-format)
2. [Graph Index Format](#graph-index-format)
3. [Subsystems Format](#subsystems-format)
4. [Configuration Format (jig.toml)](#configuration-format-jigtoml)
5. [Template Format](#template-format)

---

## OSTC Node Format

All Intent nodes (Outcome, Specification, Test, Constraint) use YAML frontmatter + Markdown body format.

### File Structure

```markdown
---
id: O-XXX-NNN
type: outcome|specification|test|constraint
title: "Human-readable title"
subsystem: subsystem-name
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft|active|deprecated
---

# Markdown Title

Markdown content here...

## Sections

More content...
```

### Required Fields (YAML Frontmatter)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Node identifier (format: `[OSTC]-[A-Z0-9]+-\d{3}`) |
| `type` | string | One of: `outcome`, `specification`, `test`, `constraint` |
| `title` | string | Human-readable title (quoted string) |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `subsystem` | string | Subsystem name (lowercase, hyphenated) |
| `created` | date | Creation date (YYYY-MM-DD) |
| `updated` | date | Last update date (YYYY-MM-DD) |
| `status` | string | One of: `draft`, `active`, `deprecated` |
| `source_delta` | string | Path to delta file that created this (for traceability) |
| `source_commit` | string | Git commit SHA |
| `source_branch` | string | Git branch name |

### ID Format Rules

Node IDs follow a strict pattern: `[PREFIX]-[PROJECT]-[NUMBER]`

| Node Type | Prefix | Example |
|-----------|--------|---------|
| Outcome | `O` | `O-JIG-001` |
| Specification | `S` | `S-JIG-001` |
| Test | `T` | `T-JIG-001` |
| Constraint | `C` | `C-JIG-001` |

Where:
- `{PREFIX}`: Single letter indicating node type
- `{PROJECT}`: Uppercase project abbreviation (e.g., JIG, AUTH)
- `{NUMBER}`: Zero-padded 3-digit number (001-999)

**Validation Rules:**
- ID must match regex: `^[OSTC]-[A-Z0-9]+-\d{3}$`
- Prefix must match type (O→outcome, S→specification, T→test, C→constraint)
- IDs must be unique across all nodes

### Markdown Body

The markdown body is free-form content following the YAML frontmatter.

**Recommended sections** (not enforced):
- **Value / Rationale**: Why this node exists
- **Acceptance Criteria / Requirements**: What must be satisfied
- **Related**: Links to other nodes
- **History**: Changelog of updates

### Example: Outcome Node

```markdown
---
id: O-AUTH-001
type: outcome
title: "Users authenticate securely"
subsystem: auth
created: 2025-11-19
status: active
---

# Outcome: Secure User Authentication

Users must be able to authenticate securely using industry-standard protocols.

## Value

Secure authentication is critical for protecting user data and maintaining trust.

## Success Metrics

- Zero authentication-related security incidents
- 99.9% authentication success rate for valid users
- <200ms authentication latency

## Related

- specs: S-AUTH-001, S-AUTH-002
- subsystem: auth

## History

- 2025-11-19: Created during auth system redesign
```

### Example: Specification Node

```markdown
---
id: S-AUTH-001
type: specification
title: "JWT tokens with 24-hour expiration"
subsystem: auth
created: 2025-11-19
status: active
---

# Specification: JWT Token Expiration

Authentication tokens use JWT format with 24-hour expiration.

## Requirements

- Use RS256 algorithm for signing
- Set `exp` claim to 24 hours from issuance
- Include `sub` (user ID) and `iat` (issued at) claims
- Refresh tokens valid for 30 days

## Rationale

24-hour expiration balances security (short-lived tokens) with usability
(users don't need to re-authenticate constantly).

## Acceptance Criteria

- Tokens expire exactly 24 hours after issuance
- Expired tokens rejected with 401 status
- Refresh token flow works seamlessly

## Related

- implements: O-AUTH-001
- tests: T-AUTH-001
- subsystem: auth

## History

- 2025-11-19: Created during auth system redesign
```

### Parsing (Python)

```python
import frontmatter
from pathlib import Path

def parse_ostc_node(path: Path) -> dict:
    """Parse OSTC node with YAML frontmatter + Markdown body."""
    with open(path, 'r') as f:
        post = frontmatter.load(f)
        return {
            'metadata': post.metadata,  # YAML as dict
            'content': post.content,    # Markdown as string
        }

# Example usage
node = parse_ostc_node(Path('jig/outcomes/O-AUTH-001.md'))
print(node['metadata']['id'])      # O-AUTH-001
print(node['metadata']['type'])    # outcome
print(node['content'])             # Markdown body
```

---

## Graph Index Format

The graph index (`jig/graph-index.yaml`) contains the registry of all nodes and their relationships.

### File Structure

```yaml
version: 1.0.0
created: YYYY-MM-DD

nodes:
  NODE-ID:
    file: path/to/node.md
    type: outcome|specification|test|constraint
    title: "Node title"
    subsystem: subsystem-name

edges:
  - from: NODE-ID
    to: NODE-ID
    type: implements|verifies|constrains|relates

subsystems:
  subsystem-name:
    nodes:
      - NODE-ID
      - NODE-ID
```

### Fields

**Top-level:**
- `version` (required): Graph index format version (currently `1.0.0`)
- `created` (required): Date the graph was initialized (YYYY-MM-DD)
- `nodes` (required): Map of node IDs to node metadata
- `edges` (optional): List of edges between nodes
- `subsystems` (optional): Map of subsystem names to node lists

**Node metadata:**
- `file` (required): Relative path from project root to node file
- `type` (required): Node type (outcome, specification, test, constraint)
- `title` (required): Human-readable title
- `subsystem` (optional): Subsystem name

**Edge metadata:**
- `from` (required): Source node ID
- `to` (required): Target node ID
- `type` (required): Relationship type
  - `implements`: Specification implements Outcome
  - `verifies`: Test verifies Specification or Code
  - `constrains`: Constraint constrains any node
  - `relates`: Generic relationship

### Example

```yaml
version: 1.0.0
created: 2025-11-18

nodes:
  O-JIG-001:
    file: jig/outcomes/O-JIG-001.md
    type: outcome
    title: "JIG tools run in <1 second for most operations"
    subsystem: core

  S-JIG-001:
    file: jig/specifications/S-JIG-001.md
    type: specification
    title: "Marker extraction processes 1000 files in <1s"
    subsystem: core

edges:
  - from: S-JIG-001
    to: O-JIG-001
    type: implements

subsystems:
  core:
    nodes:
      - O-JIG-001
      - S-JIG-001
```

### Validation Rules

- All node IDs in `edges` must exist in `nodes`
- All node IDs in `subsystems` must exist in `nodes`
- Node file paths must exist on disk
- Node type in index must match type in file's YAML frontmatter

---

## Subsystems Format

The subsystems file (`jig/subsystems.yaml`) defines the architectural boundaries of the system.

### File Structure

```yaml
subsystems:
  subsystem-name:
    description: "Human-readable description"
    exports:
      - interface-name
      - interface-name
    internal_nodes:
      - NODE-ID
      - NODE-ID
```

### Fields

- `subsystems` (required): Map of subsystem names to metadata
  - `description` (optional): Human-readable description
  - `exports` (optional): List of public interface names
  - `internal_nodes` (optional): List of node IDs belonging to this subsystem

### Example

```yaml
subsystems:
  core:
    description: "Core JIG infrastructure (parser, validator, config)"
    exports:
      - JigConfig
      - OSTCNode
      - ValidationResult
    internal_nodes:
      - C-CORE-001
      - C-CORE-002
      - C-CORE-003

  cli:
    description: "Command-line interface"
    exports:
      - cli
    internal_nodes:
      - C-CLI-001
      - C-CLI-002
      - C-CLI-003
```

### Validation Rules

- All node IDs in `internal_nodes` must exist in graph-index.yaml
- Export count per subsystem should be <5 (S-JIG-004 constraint)

---

## Configuration Format (jig.toml)

Project configuration is stored in `jig.toml` at the project root.

### File Structure

```toml
[project]
name = "project-name"

[paths]
intent_dir = "jig"
outcomes_dir = "jig/outcomes"
specifications_dir = "jig/specifications"
constraints_dir = "jig/constraints"
tests_dir = "jig/tests"
deltas_dir = "jig/deltas"
templates_dir = "templates"

[validation]
require_subsystem = false
check_orphaned_nodes = true

[performance]
marker_extraction_timeout_ms = 1000
validation_timeout_ms = 5000
```

### Sections

**`[project]`**
- `name` (required): Project name (used for node ID prefixes)

**`[paths]`**
- `intent_dir` (optional): Directory containing all JIG artifacts (default: `jig`)
- `outcomes_dir` (optional): Directory for Outcome nodes (default: `jig/outcomes`)
- `specifications_dir` (optional): Directory for Specification nodes (default: `jig/specifications`)
- `constraints_dir` (optional): Directory for Constraint nodes (default: `jig/constraints`)
- `tests_dir` (optional): Directory for Test nodes (default: `jig/tests`)
- `deltas_dir` (optional): Directory for Delta artifacts (default: `jig/deltas`)
- `templates_dir` (optional): Directory for node templates (default: `templates`)

**`[validation]`**
- `require_subsystem` (optional): Fail validation if node lacks subsystem (default: `false`)
- `check_orphaned_nodes` (optional): Warn about nodes not in graph index (default: `true`)

**`[performance]`**
- `marker_extraction_timeout_ms` (optional): Timeout for marker extraction (default: `1000`)
- `validation_timeout_ms` (optional): Timeout for validation (default: `5000`)

### Defaults

If `jig.toml` is missing, JIG uses these defaults:

```python
JigConfig(
    project_name="PROJECT",
    intent_dir=Path("jig"),
    outcomes_dir=Path("jig/outcomes"),
    specifications_dir=Path("jig/specifications"),
    constraints_dir=Path("jig/constraints"),
    tests_dir=Path("jig/tests"),
    deltas_dir=Path("jig/deltas"),
    templates_dir=Path("templates"),
    require_subsystem=False,
    check_orphaned_nodes=True,
    marker_extraction_timeout_ms=1000,
    validation_timeout_ms=5000,
)
```

---

## Template Format

Node templates are stored in the `templates/` directory and use placeholder substitution.

### File Structure

Templates are OSTC node files with placeholders in curly braces:

```markdown
---
id: {id}
type: {type}
title: "{title}"
subsystem: {subsystem}
created: {date}
---

<!-- Template comments guide users -->

# {type_title}: {title}

<!-- Sections vary by node type -->
```

### Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{id}` | Node ID | `O-JIG-001` |
| `{type}` | Node type | `outcome` |
| `{title}` | Node title | `Users authenticate securely` |
| `{subsystem}` | Subsystem name | `auth` |
| `{date}` | Current date | `2025-11-19` |
| `{type_title}` | Capitalized type | `Outcome` |

### Template Files

JIG includes four standard templates:

1. **`outcome_template.md`**: For Outcome nodes
2. **`specification_template.md`**: For Specification nodes
3. **`test_template.md`**: For Test nodes
4. **`constraint_template.md`**: For Constraint nodes

### Example: Outcome Template

```markdown
---
id: {id}
type: outcome
title: "{title}"
subsystem: {subsystem}
created: {date}
status: draft
---

<!-- This is an Outcome node: describes business value -->

# Outcome: {title}

<!-- Describe the business value this outcome delivers -->

## Value

<!-- Why does this outcome matter? What business need does it address? -->

## Success Metrics

<!-- How will we measure success? Include specific, measurable criteria -->

- Metric 1: [description]
- Metric 2: [description]

## Acceptance Criteria

<!-- What conditions must be met to consider this outcome achieved? -->

- [ ] Criterion 1
- [ ] Criterion 2

## Related

<!-- Link to related nodes -->

- specs: [List Specification IDs that implement this outcome]
- subsystem: {subsystem}

## History

- {date}: Created
```

### Substitution Logic

```python
from datetime import date

def substitute_template(template: str, **kwargs) -> str:
    """Simple string substitution for template placeholders."""
    return template.format(
        id=kwargs.get('id', ''),
        type=kwargs.get('type', ''),
        title=kwargs.get('title', ''),
        subsystem=kwargs.get('subsystem', 'null'),
        date=kwargs.get('date', date.today().isoformat()),
        type_title=kwargs.get('type', '').capitalize(),
    )
```

---

## Validation Rules Summary

### Node-level Validation
- ✓ Required fields present (id, type, title)
- ✓ ID format matches regex `^[OSTC]-[A-Z0-9]+-\d{3}$`
- ✓ ID prefix matches type (O→outcome, S→specification, T→test, C→constraint)
- ✓ Type is one of: outcome, specification, test, constraint
- ✓ Dates are valid ISO 8601 format (YYYY-MM-DD)
- ✓ YAML frontmatter parses correctly

### Graph-level Validation
- ✓ No duplicate node IDs
- ✓ All edge references exist in nodes map
- ✓ All subsystem node references exist in nodes map
- ✓ Node files exist on disk at specified paths
- ⚠ Warn if nodes not referenced in graph index (orphaned nodes)
- ⚠ Warn if subsystem field missing (when `require_subsystem=false`)

---

## Format Rationale

### Why YAML Frontmatter + Markdown?

1. **Human-readable**: Works with standard text tools (cat, less, grep)
2. **Well-supported**: Many parsers available (python-frontmatter, jekyll, hugo)
3. **Git-friendly**: Meaningful diffs, easy merges
4. **Standard**: Used by static site generators (Jekyll, Hugo, Gatsby)
5. **Simple**: No custom format, no database

### Why Not JSON/XML/Database?

- **JSON**: Not human-readable, poor for long-form content
- **XML**: Verbose, difficult to read/write manually
- **Database**: Requires external service (violates O-JIG-004)

### Design Constraints

These formats satisfy JIG's core constraints:

- **O-JIG-001**: Performance (<1s operations) ✓ Fast file parsing
- **O-JIG-002**: Simple text formats ✓ YAML + Markdown
- **O-JIG-003**: Composability ✓ Works with Unix pipes
- **O-JIG-004**: No external services ✓ Just files

---

## References

- [YAML Specification](https://yaml.org/spec/1.2/spec.html)
- [Markdown Specification (CommonMark)](https://commonmark.org/)
- [python-frontmatter](https://python-frontmatter.readthedocs.io/)
- [JIG Concept v6.1](../jig-concept/JIG-Concept-v6.1.md)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-19
**Maintained By:** JIG Core Team
