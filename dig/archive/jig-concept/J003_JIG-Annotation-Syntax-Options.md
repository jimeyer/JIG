---
title: "JIG Annotation Syntax: Aesthetic Options"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1763493911
created_human: "2025-11-18 13:25 CST"
parent: "[[J001_JIG-Concept-v4]]"
children: []
---
# JIG Annotation Syntax: Aesthetic Options
**Finding Beautiful, Readable, Machine-Parseable Annotations**
**Date:** 2025-11-12

---

## The Problem

HTML comments work but are visually noisy:

```markdown
<!-- @jig outcome O-001 priority:high -->
## Enable Accurate Expense Tracking
We want users to track expenses effortlessly...
<!-- @jig end -->
```

**Issues**:
- `<!-- -->` syntax is ugly in raw markdown
- Takes up visual space
- Breaks reading flow
- Feels like "code" not "documentation"

**Goal**: Find syntax that is:
1. ✅ Beautiful in raw markdown
2. ✅ Renders nicely in HTML/GitHub
3. ✅ Easy to find with regex
4. ✅ Doesn't break existing tools

---

## Option 1: Emoji Tags 🏷️

**Concept**: Use emoji as visual markers

```markdown
## 🎯 Enable Accurate Expense Tracking
`outcome:O-001 priority:high`

We want users to track expenses effortlessly...

### ⚙️ Expense Validation Rules
`spec:S-001 satisfies:O-001`

Expenses must be validated before storage:
- Amount must be positive
- Category must be valid
```

**Rendering**:
The backticks render as inline code, emoji render as-is.

**Pros**:
- ✅ Visually distinctive and pretty
- ✅ Emoji provide semantic meaning at a glance
- ✅ Works in all markdown renderers
- ✅ Easy to scan visually

**Cons**:
- ❌ Emoji might be seen as unprofessional
- ❌ Inline code blocks may interfere with syntax highlighting
- ❌ Not invisible when rendered
- ❌ What if heading already has emoji?

**Verdict**: 👎 Too playful, metadata too visible

---

## Option 2: Link Reference Style

**Concept**: Use markdown's link reference syntax

```markdown
## Enable Accurate Expense Tracking
[jig]: # (outcome O-001 priority:high)

We want users to track expenses effortlessly...

### Expense Validation Rules
[jig]: # (spec S-001 satisfies:O-001)

Expenses must be validated before storage:
- Amount must be positive
- Category must be valid
```

**Rendering**:
`[jig]: # (...)` is a link reference definition that renders invisible in HTML.

**Pros**:
- ✅ Invisible when rendered
- ✅ Native markdown syntax
- ✅ Cleaner than HTML comments
- ✅ All tools support this

**Cons**:
- ⚠️ Slightly verbose
- ⚠️ Multiple `[jig]` references in same document might conflict
- ❌ Closing tag problem (how to mark end?)

**Verdict**: 👍 Strong candidate, but needs end-tag solution

---

## Option 3: Setext Heading Underlines (Hidden Metadata)

**Concept**: Use setext-style underlines with metadata

```markdown
## Enable Accurate Expense Tracking {#O-001 .outcome .priority-high}

We want users to track expenses effortlessly...

### Expense Validation Rules {#S-001 .spec .satisfies-O-001}

Expenses must be validated before storage:
- Amount must be positive
- Category must be valid
```

**Rendering**:
Many markdown processors support header attributes (Pandoc, kramdown, etc.).
Renders as: `<h2 id="O-001" class="outcome priority-high">Enable Accurate Expense Tracking</h2>`

**Pros**:
- ✅ Clean, minimal syntax
- ✅ Follows existing conventions (Pandoc-style attributes)
- ✅ Creates semantic HTML
- ✅ Readable

**Cons**:
- ❌ Not supported by GitHub-flavored Markdown (GFM)
- ❌ Only works for headings (what about mid-section annotations?)
- ❌ No end-tag (assumes heading scope)

**Verdict**: 👍 Excellent for heading-level annotations, but limited scope

---

## Option 4: YAML Frontmatter Blocks

**Concept**: Use fenced YAML blocks (but inline)

```markdown
## Enable Accurate Expense Tracking

```jig
type: outcome
id: O-001
priority: high
```

We want users to track expenses effortlessly...

### Expense Validation Rules

```jig
type: spec
id: S-001
satisfies: O-001


Expenses must be validated before storage:
- Amount must be positive
- Category must be valid
```

**Rendering**:
Renders as a code block labeled "jig" (usually syntax highlighted).

**Pros**:
- ✅ Very clean, structured data
- ✅ Easy to parse (YAML)
- ✅ Familiar to developers
- ✅ Readable

**Cons**:
- ❌ Renders as visible code block (not invisible)
- ❌ Takes up vertical space
- ❌ Breaks prose flow

**Verdict**: 👎 Too visible and bulky

---

## Option 5: Minimal Brackets (Custom Extension)

**Concept**: Minimal syntax that looks like attribution

```markdown
## Enable Accurate Expense Tracking
[outcome O-001 | priority:high]

We want users to track expenses effortlessly...

### Expense Validation Rules
[spec S-001 | satisfies:O-001]

Expenses must be validated before storage:
- Amount must be positive
- Category must be valid
```

**Rendering**:
Renders as text (visible) unless you add custom CSS/JS to hide `[outcome ...]` patterns.

**Pros**:
- ✅ Very clean
- ✅ Looks like a citation or attribution
- ✅ Easy to read
- ✅ Simple to parse

**Cons**:
- ❌ Visible when rendered (unless custom processing)
- ⚠️ Might be confused with markdown links

**Verdict**: 👍 Good if visibility is acceptable

---

## Option 6: HTML Comments with Better Formatting

**Concept**: Keep HTML comments but make them prettier

```markdown
## Enable Accurate Expense Tracking
<!--- outcome O-001 | priority:high --->

We want users to track expenses effortlessly...

### Expense Validation Rules
<!--- spec S-001 | satisfies:O-001 --->

Expenses must be validated before storage:
- Amount must be positive
- Category must be valid
```

**Changes from original**:
- Single line (not block-style)
- Symmetric `<!--- ... --->`
- Pipe separator instead of key:value for better visual balance

**Pros**:
- ✅ Invisible when rendered
- ✅ Slightly cleaner than `<!-- @jig ... -->`
- ✅ Works everywhere
- ✅ Easy to parse

**Cons**:
- ⚠️ Still HTML comments (somewhat ugly)

**Verdict**: 👍 Incremental improvement

---

## Option 7: Double Slash Comments (Pseudo-Code Style)

**Concept**: Use `//` like code comments

```markdown
// @jig outcome O-001 priority:high
## Enable Accurate Expense Tracking

We want users to track expenses effortlessly...

// @jig spec S-001 satisfies:O-001
### Expense Validation Rules

Expenses must be validated before storage:
- Amount must be positive
- Category must be valid
```

**Rendering**:
Renders as plain text (visible).

**Pros**:
- ✅ Familiar to developers
- ✅ Very concise
- ✅ Easy to type

**Cons**:
- ❌ Visible when rendered
- ❌ Looks out of place in markdown
- ❌ No end-tag

**Verdict**: 👎 Too code-like for documentation

---

## Option 8: Blockquote with Metadata (Beautiful Attribution)

**Concept**: Use blockquotes as "metadata boxes"

```markdown
> **outcome** O-001 · _priority: high_

## Enable Accurate Expense Tracking

We want users to track expenses effortlessly...

> **spec** S-001 · _satisfies: O-001_

### Expense Validation Rules

Expenses must be validated before storage:
- Amount must be positive
- Category must be valid
```

**Rendering**:
Renders as a beautiful blockquote with emphasis:
> **outcome** O-001 · _priority: high_

**Pros**:
- ✅ Beautiful rendering
- ✅ Readable in raw markdown
- ✅ Visually distinctive
- ✅ Semantically meaningful (attribution/metadata)

**Cons**:
- ❌ Visible when rendered (not invisible)
- ⚠️ Blockquotes have semantic meaning (might confuse readers)

**Verdict**: 👍 Beautiful, but might be too prominent

---

## Option 9: Reference-Style Links with Inline Attributes (Hybrid)

**Concept**: Combine link references with heading attributes

```markdown
## Enable Accurate Expense Tracking {.outcome}
[O-001]: # "priority:high"

We want users to track expenses effortlessly...

### Expense Validation Rules {.spec}
[S-001]: # "satisfies:O-001"

Expenses must be validated before storage:
- Amount must be positive
- Category must be valid
```

**Rendering**:
- Heading attributes: `{.outcome}` renders as class if supported, otherwise ignored
- Link refs: `[O-001]: #` invisible

**Pros**:
- ✅ Mostly invisible
- ✅ Clean heading line
- ✅ Semantic class names
- ✅ Metadata in link ref (invisible)

**Cons**:
- ⚠️ Split metadata (type in heading, details in link ref)
- ❌ Heading attributes not universally supported

**Verdict**: 👍 Clever, but complex

---

## Option 10: Invisible Unicode Characters (Hidden Metadata)

**Concept**: Embed metadata in zero-width characters

```markdown
## Enable Accurate Expense Tracking​‌‍‌‍​‌‍‌​

We want users to track expenses effortlessly...
```

(Zero-width characters encode: outcome O-001 priority:high)

**Pros**:
- ✅ Completely invisible
- ✅ No visual clutter

**Cons**:
- ❌ Impossible to see/edit without special tools
- ❌ Copy/paste might lose encoding
- ❌ Accessibility nightmare
- ❌ Debugging nightmare

**Verdict**: 👎 Too clever, unmaintainable

---

## Option 11: Markdown Tables (Structured Metadata)

**Concept**: Use compact tables

```markdown
## Enable Accurate Expense Tracking

| Type | ID | Priority | Satisfies |
|------|----|----|-----------|
| outcome | O-001 | high | — |

We want users to track expenses effortlessly...

### Expense Validation Rules

| Type | ID | Satisfies |
|------|----|----|
| spec | S-001 | O-001 |

Expenses must be validated before storage:
- Amount must be positive
- Category must be valid
```

**Pros**:
- ✅ Very clear structure
- ✅ Readable
- ✅ Renders beautifully

**Cons**:
- ❌ Takes up a lot of vertical space
- ❌ Too prominent
- ❌ Breaks prose flow

**Verdict**: 👎 Too bulky

---

## Option 12: Footnote-Style References (Minimal Visual Impact)

**Concept**: Use footnote syntax

```markdown
## Enable Accurate Expense Tracking[^O-001]

We want users to track expenses effortlessly...

[^O-001]: outcome | priority:high

### Expense Validation Rules[^S-001]

Expenses must be validated before storage:
- Amount must be positive
- Category must be valid

[^S-001]: spec | satisfies:O-001
```

**Rendering**:
Renders as superscript footnote markers. Footnote definitions at bottom of section.

**Pros**:
- ✅ Minimal visual impact (just superscript)
- ✅ Native markdown syntax
- ✅ Metadata in footnote (less intrusive)
- ✅ Beautiful rendering

**Cons**:
- ⚠️ Footnotes have semantic meaning (might confuse)
- ⚠️ Metadata far from content
- ❌ Footnote markers visible in heading

**Verdict**: 👍 Clever, but footnotes are meant for different purpose

---

## Recommendation Matrix

| Approach | Beauty | Invisibility | Simplicity | Tool Compat | Overall |
|----------|--------|--------------|------------|-------------|---------|
| HTML Comments (original) | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 👍 |
| Emoji Tags | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 👎 |
| Link Reference Style | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 👍 |
| Header Attributes | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | 👍 |
| YAML Blocks | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 👎 |
| Minimal Brackets | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 👍 |
| Better HTML Comments | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 👍 |
| Double Slash | ⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | 👎 |
| Blockquote | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 👍 |
| Hybrid Link+Attr | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | 👎 |
| Unicode Hidden | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | 👎 |
| Tables | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 👎 |
| Footnotes | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 👍 |

---

## Top 3 Recommendations

### 🥇 Option 3: Header Attributes (Pandoc-style)

**Best for: Heading-level annotations in Pandoc-compatible environments**

```markdown
## Enable Accurate Expense Tracking {#O-001 .outcome .priority-high}

We want users to track expenses effortlessly...

### Expense Validation Rules {#S-001 .spec .satisfies-O-001}

Expenses must be validated before storage:
- Amount must be positive
- Category must be valid
```

**Why it wins**:
- Beautiful and minimal
- Follows existing markdown extension conventions
- Semantic HTML output
- Easy to read

**Limitation**: Only works for section headings (but that might be enough!)

---

### 🥈 Option 2: Link Reference Style

**Best for: Universal compatibility with invisible metadata**

```markdown
## Enable Accurate Expense Tracking
[jig:O-001]: # "outcome priority:high"

We want users to track expenses effortlessly...

### Expense Validation Rules
[jig:S-001]: # "spec satisfies:O-001"

Expenses must be validated before storage:
- Amount must be positive
- Category must be valid
```

**Why it wins**:
- Works everywhere
- Invisible when rendered
- Native markdown syntax
- Clean and readable

**Enhancement**: Use unique prefix per annotation to avoid conflicts:
```markdown
[jig:O-001]: # "outcome priority:high"
[jig:S-001]: # "spec satisfies:O-001"
```

---

### 🥉 Option 8: Blockquote Attribution

**Best for: Visible but beautiful metadata**

```markdown
> **outcome** O-001 · _priority: high_

## Enable Accurate Expense Tracking

We want users to track expenses effortlessly...

> **spec** S-001 · _satisfies: O-001_

### Expense Validation Rules

Expenses must be validated before storage:
- Amount must be positive
- Category must be valid
```

**Why it wins**:
- Gorgeous rendering
- Human-readable metadata
- Semantically meaningful (like paper citations)
- Encourages treating O/S nodes as "first-class" content

**Trade-off**: Metadata is visible, but beautiful visibility might be a feature, not a bug.

---

## Hybrid Approach (Recommended)

**Support multiple syntaxes, detect automatically:**

```markdown
# Document 1: Heading attributes (for Pandoc users)
## Outcome {#O-001 .outcome .priority-high}

# Document 2: Link references (for GitHub users)
## Outcome
[jig:O-001]: # "outcome priority:high"

# Document 3: Blockquotes (for beautiful visibility)
> **outcome** O-001 · _priority: high_
## Outcome

# Document 4: HTML comments (for invisible fallback)
<!--- outcome O-001 priority:high --->
## Outcome
```

**Scanner detects and parses all syntaxes**.

**Configuration**:
```toml
# .jig.toml
[docs.annotation]
style = "auto"  # auto-detect
# or specify: header-attributes | link-references | blockquotes | html-comments
```

---

## Visual Comparison (Same Content)

### HTML Comments (Current)
```markdown
<!-- @jig outcome O-001 priority:high -->
## Enable Accurate Expense Tracking
<!-- @jig end -->

We want users to track expenses effortlessly,
reducing bookkeeping time from 2 hours/week to 10 minutes/week.

<!-- @jig spec S-001 satisfies:O-001 -->
### Automatic Expense Detection
<!-- @jig end -->

Monitor linked bank accounts for new transactions.
```

**Visual density**: ⭐⭐ (comments break reading flow)

---

### Header Attributes
```markdown
## Enable Accurate Expense Tracking {#O-001 .outcome .priority-high}

We want users to track expenses effortlessly,
reducing bookkeeping time from 2 hours/week to 10 minutes/week.

### Automatic Expense Detection {#S-001 .spec .satisfies-O-001}

Monitor linked bank accounts for new transactions.
```

**Visual density**: ⭐⭐⭐⭐⭐ (clean, minimal)

---

### Link References
```markdown
## Enable Accurate Expense Tracking
[jig:O-001]: # "outcome priority:high"

We want users to track expenses effortlessly,
reducing bookkeeping time from 2 hours/week to 10 minutes/week.

### Automatic Expense Detection
[jig:S-001]: # "spec satisfies:O-001"

Monitor linked bank accounts for new transactions.
```

**Visual density**: ⭐⭐⭐⭐ (clean, one extra line per section)

---

### Blockquotes
```markdown
> **outcome** O-001 · _priority: high_

## Enable Accurate Expense Tracking

We want users to track expenses effortlessly,
reducing bookkeeping time from 2 hours/week to 10 minutes/week.

> **spec** S-001 · _satisfies: O-001_

### Automatic Expense Detection

Monitor linked bank accounts for new transactions.
```

**Visual density**: ⭐⭐⭐⭐ (visible but beautiful)

---

## Implementation Recommendation

### Phase 1: Start with Header Attributes (Primary)
```markdown
## Enable Accurate Expense Tracking {#O-001 .outcome .priority-high}
### Automatic Expense Detection {#S-001 .spec .satisfies-O-001}
```

**Parser**:
```python
import re

# Parse heading attributes
heading_pattern = r'^(#{1,6})\s+(.+?)\s+\{([^}]+)\}'

# Extract: {#O-001 .outcome .priority-high}
# - ID: O-001
# - Classes: outcome, priority-high
# - Type: "outcome" (from class)
# - Priority: "high" (from class pattern)
```

### Phase 2: Add Link Reference Support (Fallback)
```markdown
## Enable Accurate Expense Tracking
[jig:O-001]: # "outcome priority:high"
```

**Parser**:
```python
# Parse link references
link_ref_pattern = r'^\[jig:([^\]]+)\]:\s*#\s*"([^"]+)"'
```

### Phase 3: Auto-Conversion Tool
```bash
jigy docs convert --from html-comments --to header-attributes
```

---

## Final Recommendation

**Default to Header Attributes** with fallback to Link References:

```markdown
## Enable Accurate Expense Tracking {#O-001 .outcome .priority-high}

We want users to track expenses effortlessly...

### Automatic Expense Detection {#S-001 .spec .satisfies-O-001}

Monitor linked bank accounts for new transactions.

### Manual Entry Form {.spec}
[jig:S-002]: # "satisfies:O-001 tags:ui,mobile"

For transactions not detected automatically, provide simple entry form.
```

**Why this wins**:
1. ✅ Beautiful in raw markdown
2. ✅ Minimal visual clutter
3. ✅ Semantic HTML output (ids, classes)
4. ✅ Follows markdown extension conventions
5. ✅ Link reference fallback for flexibility
6. ✅ Auto-detectable

**Trade-off**: Not GitHub-flavored Markdown (GFM) standard, but widely supported by:
- Pandoc ✅
- kramdown (Jekyll) ✅
- Python-Markdown with extensions ✅
- Obsidian ✅
- Many static site generators ✅

For pure GFM, fall back to link references.

---

**Status**: Ready for decision
**Recommended**: Header Attributes (primary) + Link References (fallback)
