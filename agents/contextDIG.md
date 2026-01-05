# DIG Context for AI Agents

DIG (Deliberation Insight Graph) captures the **reasoning** behind code decisions. It answers "why is the system this way?" — not "what" (that's code/JIG) or "when" (that's git).

```
JIG  = Intent      (what should be true)   → evergreen
DIG  = Reasoning   (why it's true)         → archival
GIT  = History     (when it changed)       → immutable
```

---

## Location

All DIG documents reside in `dig/`. Subfolder structure is user's choice.

```
dig/
├── wip/              # Active deliberation
├── archive/          # Completed deliberation
└── digconfig.yaml    # Configuration (optional)
```

---

## Frontmatter Schema (7 Required Fields)

Every DIG document MUST have this YAML frontmatter:

```yaml
---
type: exploration           # From digconfig types
title: "Document Title"     # Must match first H1 heading exactly
status: active              # From digconfig statuses
created: 1735847400         # Unix epoch seconds
created_human: "2026-01-02 14:30 PST"  # Local datetime
parent: "[[Parent_Doc]]"    # Wiki link or null for roots
children: []                # Array of wiki links
---
```

### Conditional Required Fields

```yaml
decision: completed         # REQUIRED when status is implemented/superseded/parked/abandoned
```

Valid `decision` values: `completed`, `replaced`, `deferred`, `rejected`

### Optional Fields

```yaml
prompt: |                   # The triggering prompt (preserve provenance)
  Full prompt text here...
superseded_by: "[[New_Doc]]"  # When status is superseded
```

---

## Types (Default)

| Type | Mode | Purpose |
|------|------|---------|
| `exploration` | divergent | Open-ended thinking, what-ifs |
| `scope` | convergent | Problem/opportunity definition |
| `jigplan` | convergent | Alignment to JIG specs |
| `plan` | convergent | Implementation breakdown (WUs) |
| `journal` | mixed | Running notes during execution |
| `wu` | convergent | Work unit completion record |
| `retrospective` | convergent | Post-hoc lessons learned |

---

## Statuses (Default)

```
active → parked (can resume)
       → implemented (terminal)
       → abandoned (terminal)
       → superseded (terminal)
```

| Status | Meaning |
|--------|---------|
| `active` | Currently being worked on |
| `parked` | Set aside, may resume |
| `implemented` | Led to canonical state changes |
| `abandoned` | Decided not to pursue |
| `superseded` | Replaced by newer document |

---

## CLI Commands

```bash
digy new <type> <title>     # Create new DIG doc with frontmatter
digy validate [path]        # Validate frontmatter against schema
```

### `digy new` Auto-populates

- `type`: from argument
- `title`: from argument (used for H1 heading too)
- `status`: active
- `created`: epoch seconds (now)
- `created_human`: local datetime string
- `parent`: null (user fills in)
- `children`: []

Note: No `decision` field for active status (only required for terminal statuses).

---

## "dig this" Trigger

When user says **"dig this"** (or "dig that", "dig it"):

1. Parse for optional: `as <type>` and `: "<title>"`
2. Infer missing values from conversation context
3. Create doc in `dig/` with proper frontmatter
4. Include `prompt:` field with triggering conversation
5. Run `digy validate` to confirm structure
6. Report success with file path

### Examples

```
"Dig this."                              # Agent infers everything
"Dig this as a scope."                   # Type specified
"Dig this: 'CRDT Design Options'"        # Title specified
"Dig this as exploration: 'Auth Flow'"   # Both specified
```

---

## Wiki Links

Use `[[Document_Name]]` format for graph edges:

```yaml
# Frontmatter (required for structure)
parent: "[[D001_SCOPE]]"
children: ["[[D003_DESIGN]]", "[[D004_PLAN]]"]
```

```markdown
<!-- Body (for references) -->
This builds on [[D001_SCOPE]] and implements [[S-174]].
```

---

## Relationship to JIG

DIG and JIG are **independent peer systems**.

| Aspect | JIG | DIG |
|--------|-----|-----|
| Purpose | Specify intent | Capture reasoning |
| Question | What should be true? | Why is it true? |
| Location | `jig/` | `dig/` |
| Lifecycle | Evergreen | Archival |
| Tool | `jigy` | `digy` |

- Reference JIG specs in DIG body text: `[[S-174]]`
- `jigplan` type aligns deliberation to specs
- DIG validates independently of JIG

---

## Validation Rules

`digy validate` checks:

- All 7 required fields present (type, title, status, created, created_human, parent, children)
- `type` exists in digconfig types list
- `status` exists in digconfig statuses list
- `created` is integer (epoch seconds)
- `parent` is null or wiki link `[[...]]`
- `children` is array of wiki links
- `decision` field present when status is terminal (implemented/superseded/parked/abandoned)
- First H1 heading (`# Title`) matches frontmatter `title` exactly
- Document IDs in filenames don't conflict with JIG IDs (prefix with `dg_` if using S###, D###, etc.)

Does NOT check: link target existence, folder structure.

---

## Anti-patterns

**Missing parent/children:**
```yaml
# BAD: No graph edges
parent:
children:

# GOOD: Explicit edges (null for roots, [] for leaves)
parent: null
children: []
```

**H1 heading doesn't match title:**
```yaml
# BAD: Validator will fail
---
title: "CRDT Design"
---
# CRDT Design Options   <-- doesn't match!

# GOOD: Exact match
---
title: "CRDT Design Options"
---
# CRDT Design Options
```

**Missing decision for terminal status:**
```yaml
# BAD: Implemented without decision
---
status: implemented
---

# GOOD: Decision explains outcome
---
status: implemented
decision: completed
---
```

**JIG ID collision in filename:**
```
# BAD: S001_SCOPE_*.md conflicts with jig/specifications/S-001.md
# BAD: D035_PLAN_*.md conflicts with potential D-### IDs

# GOOD: Prefix with dg_ to disambiguate
dg_S001_SCOPE_BikeState.md
dg_D035_PLAN_Implementation.md
```

**Specs in frontmatter:**
```yaml
# BAD: DIG doesn't track specs in frontmatter
specs: [S-174, S-175]

# GOOD: Reference specs in body text
```markdown
This implements [[S-174]] and [[S-175]].
```

**Using DIG for canonical truth:**
```markdown
# BAD: Requirements belong in JIG
# S-174: Token Expiration
Tokens MUST expire after 15 minutes.

# GOOD: Deliberation about why
# Token Expiration Analysis
We considered 15, 30, and 60 minute timeouts...
```

**Losing prompts:**
```yaml
# BAD: No provenance
---
type: exploration
...
---

# GOOD: Preserve what triggered this thinking
---
type: exploration
prompt: |
  "What authentication approach should we use?"
...
---
```

---

## Quick Reference

| Task | Action |
|------|--------|
| Create new deliberation | `digy new <type> "<title>"` |
| Validate documents | `digy validate dig/` |
| Mark as complete | Change `status: implemented`, add `decision: completed` |
| Park for later | Change `status: parked`, add `decision: deferred` |
| Abandon | Change `status: abandoned`, add `decision: rejected` |
| Replace with new thinking | Change `status: superseded`, add `decision: replaced`, add `superseded_by` |
| Link to parent | Set `parent: "[[Parent_Doc]]"` |
| Add children | Append to `children: ["[[Child]]"]` |
| Reference JIG spec | Add `[[S-###]]` in body text |
| Avoid JIG ID conflict | Prefix filename with `dg_` (e.g., `dg_S001_SCOPE_*.md`) |

---

## Document Lifecycle

```
exploration  →  scope  →  jigplan  →  plan  →  implementation
     ↓            ↓          ↓          ↓           ↓
 (divergent)  (converge)  (align)   (break     (execute)
                                    down WUs)
```

Each stage can spawn children or be parked/abandoned. Dead ends are valuable — they prevent future repetition.
