# Syllabus: JIG Context for AI Agents

**Purpose**: Plan what an AI agent needs to know to work effectively on a JIG project. This informs the eventual `agents/contextJIG.md` document.

---

## Design Constraints

- **Token budget**: Must be concise enough to leave room for actual work
- **Self-contained**: Agent should not need to read other docs
- **Actionable**: Agent can immediately apply knowledge
- **Scannable**: Quick reference during work, not a tutorial

---

## Knowledge Tiers

### Tier 1: Mental Model (ESSENTIAL - ~200 words)

The agent MUST understand:

1. **What JIG measures**: Alignment between intent, implementation, and verification
2. **The S-F-T triangle**:
   - S (Specifications) = what we intend to build
   - F (Functions) = what we built
   - T (Tests) = what we verify
3. **Three relationships**:
   - F → S (implements): `@jig.implements("S-001")`
   - T → S (verifies): `@jig.verifies("S-001")`
   - T → F (covers): automatic via coverage
4. **Bricks**: Partition functions into named architectural units
5. **Layers**: Stratify bricks (layer N depends only on layers < N)

### Tier 2: Artifact Formats (ESSENTIAL - ~300 words)

The agent MUST know how to read/write:

1. **Specification files** (`jig/specifications/S-{number}.md`)
   - Minimal frontmatter: `id`, `type: specification`
   - Markdown body for humans/agents

2. **Outcome files** (`jig/outcomes/O-{number}.md`) - OPTIONAL
   - Frontmatter: `id`, `type: outcome`, `specifies: [S-001, ...]`
   - Decompose into specs

3. **Brick definitions** (`jig/bricks.yaml`)
   - `id: B-{kebab-case}`, `name`, `layer` (integer), `units` (M-/C-/F- prefixes)

4. **Decorators** (in source code)
   - `@jig.implements("S-001")` on functions
   - `@jig.verifies("S-001")` on tests

5. **Graph files** (`jig/generated/`) - machine-generated, never edit

### Tier 3: ID Conventions (ESSENTIAL - ~100 words)

| Type | Format | Example |
|------|--------|---------|
| Specification | `S-{number}` | S-001, S-042 |
| Outcome | `O-{number}` | O-001 |
| Brick | `B-{kebab-case}` | B-auth-session |
| Function | `F-{path}` | F-auth.session.authenticate |
| Module | `M-{path}` | M-auth.session |
| Class | `C-{path}` | C-auth.tokens.TokenValidator |
| Test | `T-{path}` | T-test_auth.test_token_expiration |

### Tier 4: Writing Guidelines (IMPORTANT - ~200 words)

**Outcomes** = Evergreen business value
- WHY the system behaves this way
- Persists after project completes
- NOT: project goals, refactoring tasks, process improvements

**Specifications** = Evergreen behavioral requirements
- Observable system behavior
- Testable acceptance criteria
- Can be implemented (`@jig.implements`) and verified (`@jig.verifies`)
- NOT: file moves, implementation details, tooling

**Test**: "Remove all project references. Does it still make sense?" If no, rewrite.

### Tier 5: CLI Workflow (USEFUL - ~100 words)

```bash
jigy index         # Generate intent graph from specs/outcomes/bricks
jigy impl rebuild  # Generate implementation graph from code
jigy validate      # Check references, partition, layers
jigy status        # Show alignment status
jigy layers        # Show layer structure
```

### Tier 6: Validation Rules (REFERENCE - ~150 words)

The agent should be aware validation enforces:
- ID uniqueness within type
- Brick ID format: `B-[a-z0-9-]+`
- Reference integrity (implements/verifies → existing specs)
- Brick partition (every function in exactly one brick)
- No class splitting (all methods same brick)
- Layer constraints (depends only on lower layers)
- No circular dependencies

### Tier 7: Common Mistakes (REFERENCE - ~100 words)

- Writing specs about refactoring/file moves (not behavior)
- Writing outcomes about project goals (not persistent value)
- Forgetting `specifies:` field on outcomes
- Using sequential brick IDs instead of kebab-case
- Missing layer field on bricks
- Editing generated graph files

---

## What to EXCLUDE from contextJIG.md

- Full J017 concept document (too long)
- Historical context (why decisions were made)
- Hypotheses and validation evidence
- Alternative approaches considered
- Migration guides
- Tool builder instructions

---

## Suggested Structure for contextJIG.md

```markdown
# JIG Context for AI Agents

## What JIG Measures
[Tier 1: 2-3 paragraphs]

## Core Artifacts
[Tier 2: File formats with minimal examples]

## ID Formats
[Tier 3: Table]

## Writing Outcomes & Specifications
[Tier 4: Checklists]

## CLI Commands
[Tier 5: Command list]

## Validation Rules
[Tier 6: Bullet list]

## Anti-patterns
[Tier 7: Quick list]
```

---

## Estimated Length

- Target: 800-1200 words
- Approximately 3-4 pages of markdown
- Should render to ~6KB

---

## Success Criteria

1. Agent can create valid S-*.md file without asking questions
2. Agent can create valid O-*.md file without asking questions
3. Agent knows when to use `@jig.implements` vs `@jig.verifies`
4. Agent understands brick/layer architecture
5. Agent avoids common anti-patterns (refactoring specs, project goal outcomes)
6. Agent knows which files are human-authored vs machine-generated
