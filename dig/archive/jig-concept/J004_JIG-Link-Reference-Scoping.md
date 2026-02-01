---
title: "JIG Link Reference Scoping Strategy"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1763493911
created_human: "2025-11-18 13:25 CST"
parent: "[[J001_JIG-Concept-v4]]"
children: []
---
# JIG Link Reference Scoping Strategy
**Defining Content Boundaries with Link Reference Syntax**
**Date:** 2025-11-12

---

## The Challenge

Using link references for annotations:
```markdown
[jig:O-001]: # "outcome priority:high"
## Enable Accurate Expense Tracking

Content here...

But where does this content end?
```

**Question**: How do we know what content belongs to O-001?

---

## Option 1: No End Tag - Section Scope (Recommended)

**Strategy**: Content scope determined by markdown structure

```markdown
[jig:O-001]: # "outcome priority:high"
## Enable Accurate Expense Tracking

We want users to track expenses effortlessly,
reducing bookkeeping time from 2 hours/week to 10 minutes/week.

**Success Criteria**:
- 95% of users actively tracking after 30 days
- Average time per entry < 30 seconds

[jig:S-001]: # "spec satisfies:O-001"
### Automatic Expense Detection

Monitor linked bank accounts for new transactions.
Present detected expenses for user confirmation.
```

**Scoping Rules**:
1. If link ref precedes a heading: content = that heading + all content until next same-or-higher-level heading
2. If link ref is standalone: content = all paragraphs until next heading or link ref

**Example parsing**:

```
[jig:O-001] → marks next heading as outcome
## Enable Accurate... → START of O-001 content
  (all content here belongs to O-001)
### Automatic... → STILL part of O-001 (lower level heading)
  (this content also part of O-001)
[jig:S-001] → marks next heading as spec, ENDS O-001 content implicitly
### Automatic... → START of S-001 content
```

**Pros**:
- ✅ No end tag needed - clean and minimal
- ✅ Follows natural document structure
- ✅ Intuitive: "this section is an outcome"
- ✅ Matches how people think about document structure

**Cons**:
- ⚠️ Can't have mixed content (outcome + non-outcome in same section)
- ⚠️ Parser must understand markdown heading hierarchy

**Implementation**:
```python
def parse_link_ref_scoped(markdown_text):
    sections = split_by_headings(markdown_text)

    for section in sections:
        # Check if section has preceding link ref
        link_ref = find_preceding_link_ref(section)
        if link_ref:
            node_id = link_ref.id
            metadata = link_ref.metadata
            content = section.content  # Until next same/higher heading

            yield Node(id=node_id, metadata=metadata, content=content)
```

**Verdict**: 🥇 **RECOMMENDED** - Clean, intuitive, follows document structure

---

## Option 2: Explicit End Tag (New Line)

**Strategy**: Add explicit end marker

```markdown
[jig:O-001]: # "outcome priority:high"
## Enable Accurate Expense Tracking

We want users to track expenses effortlessly,
reducing bookkeeping time from 2 hours/week to 10 minutes/week.

[jig:O-001:end]: #
```

**Variation A**: Empty link ref
```markdown
[jig:end]: #
```

**Variation B**: Use distinctive marker
```markdown
[/jig:O-001]: #
```

**Pros**:
- ✅ Explicit boundaries
- ✅ Can have mixed content (outcome section + non-outcome paragraphs)
- ✅ No need to parse heading structure

**Cons**:
- ❌ More verbose (2 lines per annotation)
- ❌ Still visible clutter in raw markdown
- ❌ Easy to forget end tag

**Verdict**: 👎 Defeats the purpose of choosing link refs for cleanliness

---

## Option 3: Inline End Marker (HTML Comment)

**Strategy**: Use invisible inline marker for end

```markdown
[jig:O-001]: # "outcome priority:high"
## Enable Accurate Expense Tracking

We want users to track expenses effortlessly,
reducing bookkeeping time from 2 hours/week to 10 minutes/week.
<!-- /jig:O-001 -->

Some text that's NOT part of O-001.
```

**Pros**:
- ✅ Explicit boundaries
- ✅ Inline (doesn't take extra line)
- ✅ Invisible when rendered

**Cons**:
- ❌ Still requires HTML comments (we're trying to avoid these!)
- ⚠️ Mixing syntaxes feels inconsistent

**Verdict**: 👎 If we need HTML comments anyway, why use link refs?

---

## Option 4: Double Link Reference (Start and End)

**Strategy**: Use link refs for both boundaries

```markdown
[jig:O-001:start]: # "outcome priority:high"
## Enable Accurate Expense Tracking

We want users to track expenses effortlessly,
reducing bookkeeping time from 2 hours/week to 10 minutes/week.
[jig:O-001:end]: #

Some text that's NOT part of O-001.
```

**Simpler syntax**:
```markdown
[jig:O-001]: # "outcome priority:high"
## Enable Accurate Expense Tracking

We want users to track expenses effortlessly,
reducing bookkeeping time from 2 hours/week to 10 minutes/week.
[jig:]: #

Some text that's NOT part of O-001.
```

**Pros**:
- ✅ Consistent syntax (all link refs)
- ✅ Explicit boundaries
- ✅ Invisible when rendered

**Cons**:
- ⚠️ Takes up extra line
- ⚠️ Empty link ref `[jig:]: #` feels weird

**Verdict**: 👍 Acceptable if explicit boundaries are needed

---

## Option 5: Implied Scope by Next Annotation

**Strategy**: Content ends when next annotation starts

```markdown
[jig:O-001]: # "outcome priority:high"
## Enable Accurate Expense Tracking

We want users to track expenses effortlessly...

Some more text about outcomes...

[jig:S-001]: # "spec satisfies:O-001"
### Automatic Expense Detection

Monitor linked bank accounts...
```

**Scoping Rule**: Content from one annotation extends until the next annotation (any type)

**Pros**:
- ✅ No end tag
- ✅ Simple parser logic
- ✅ Works for documents that are fully annotated

**Cons**:
- ❌ Can't have non-annotated content between sections
- ❌ Last section has no boundary (until end of file)

**Verdict**: 👍 Works well if entire document is annotated

---

## Option 6: Paragraph-Level Scope (No Heading Required)

**Strategy**: If no heading follows, capture paragraphs until blank line or next annotation

```markdown
[jig:O-001]: # "outcome priority:high"

We want users to track expenses effortlessly,
reducing bookkeeping time from 2 hours/week to 10 minutes/week.

This is still part of O-001 because no boundary yet.

[jig:S-001]: # "spec satisfies:O-001"

Monitor linked bank accounts for new transactions.
```

**Scoping Rules**:
1. If heading follows link ref: use heading-based scoping
2. If no heading: capture paragraphs until next annotation or double-blank-line

**Pros**:
- ✅ Flexible (works with or without headings)
- ✅ Good for inline annotations
- ✅ No end tag

**Cons**:
- ⚠️ Complex parser logic
- ⚠️ Ambiguous boundaries with complex content

**Verdict**: 👍 Good for flexibility, but parser complexity increases

---

## Recommended Approach: Heading-Based Scoping

**Primary strategy**: Section scope determined by markdown headings

```markdown
# Product Requirements Document

## Background
Some context that's NOT annotated...

[jig:O-001]: # "outcome priority:high"
## Goal: Enable Accurate Expense Tracking

We want users to track expenses effortlessly,
reducing bookkeeping time from 2 hours/week to 10 minutes/week.

**Success Criteria**:
- 95% of users actively tracking after 30 days
- Average time per entry < 30 seconds

### User Research
(This subsection is PART of O-001)

Our research shows users struggle with manual entry...

[jig:S-001]: # "spec satisfies:O-001"
### Technical Requirements: Automatic Detection

Monitor linked bank accounts for new transactions.
Present detected expenses for user confirmation.

**Requirements**:
- Real-time monitoring via Plaid API
- Confidence score for categorization
- One-tap confirmation UI

[jig:S-002]: # "spec satisfies:O-001"
### Technical Requirements: Manual Entry

For transactions not detected, provide simple entry form.
```

**Parsing Algorithm**:

```python
def extract_annotated_sections(markdown_text):
    """
    Extract JIG-annotated sections from markdown.

    Strategy:
    1. Parse markdown into heading hierarchy
    2. Find link references with [jig:ID] pattern
    3. Associate link ref with next heading
    4. Content = heading + all subsections until next same/higher-level heading
    """

    # Parse markdown structure
    ast = parse_markdown_to_ast(markdown_text)

    nodes = []
    pending_annotation = None

    for element in ast:
        if element.type == 'link_reference' and element.label.startswith('jig:'):
            # Found annotation marker
            pending_annotation = parse_jig_annotation(element)

        elif element.type == 'heading' and pending_annotation:
            # This heading is annotated
            node_id = pending_annotation.id
            metadata = pending_annotation.metadata
            heading_level = element.level

            # Extract content: this heading + subsections
            content = extract_section_content(
                ast,
                start=element,
                until_heading_level=heading_level
            )

            nodes.append(Node(
                id=node_id,
                title=element.text,
                content=content,
                metadata=metadata,
                location={
                    'line': element.line,
                    'level': heading_level
                }
            ))

            pending_annotation = None  # Consumed

    return nodes

def extract_section_content(ast, start, until_heading_level):
    """
    Extract all content from start until next same-or-higher-level heading.
    """
    content = []
    started = False

    for element in ast:
        if element == start:
            started = True
            content.append(element)
            continue

        if started:
            # Stop at same or higher level heading
            if element.type == 'heading' and element.level <= until_heading_level:
                break

            content.append(element)

    return ast_to_markdown(content)
```

---

## Visual Examples

### Example 1: Simple Outcome + Spec

```markdown
[jig:O-001]: # "outcome priority:high"
## Enable Accurate Expense Tracking

We want users to track expenses effortlessly.

**Success Criteria**:
- 95% retention

[jig:S-001]: # "spec satisfies:O-001"
### Automatic Expense Detection

Monitor bank accounts for transactions.
```

**Parsed as**:
- **O-001**:
  - Title: "Enable Accurate Expense Tracking"
  - Content: "We want users... Success Criteria: 95% retention"
  - Scope: Lines 2-7 (until next annotation)

- **S-001**:
  - Title: "Automatic Expense Detection"
  - Content: "Monitor bank accounts..."
  - Scope: Lines 8-10 (until EOF or next annotation)

---

### Example 2: Nested Subsections

```markdown
[jig:O-001]: # "outcome priority:high"
## Goal: Improve User Retention

Increase 30-day retention from 60% to 75%.

### Strategy
(This is PART of O-001)

We'll focus on onboarding improvements...

### Success Metrics
(This is also PART of O-001)

- 75% retention
- NPS > 50

[jig:O-002]: # "outcome priority:medium"
## Goal: Expand Payment Options

Support international payments.
```

**Parsed as**:
- **O-001**:
  - Content: Everything from "## Goal: Improve..." to just before "## Goal: Expand..."
  - Includes subsections "### Strategy" and "### Success Metrics"

- **O-002**:
  - Content: Everything from "## Goal: Expand..." to EOF
  - No subsections (yet)

---

### Example 3: Mixed Annotated and Non-Annotated Content

```markdown
# Product Requirements Document

## Background
(NOT annotated - just context)

Our research shows users need better expense tracking...

## Vision
(NOT annotated - just vision statement)

We want to be the leading expense tracking app...

[jig:O-001]: # "outcome priority:high"
## Goal: Enable Accurate Expense Tracking
(This IS annotated)

We want users to track expenses effortlessly...

## Implementation Timeline
(NOT annotated - just project management)

Q1: Build core features
Q2: Launch beta
```

**Parsed as**:
- Only O-001 is extracted
- Background, Vision, Timeline sections are ignored (not annotated)

---

## End Tag: Do We Need One?

**Short answer: No, if we use heading-based scoping.**

### When you DON'T need end tag:
✅ Entire section belongs to one node (outcome or spec)
✅ Using markdown heading hierarchy to define boundaries
✅ Willing to annotate at section level

### When you MIGHT need end tag:
⚠️ Want to annotate partial section (e.g., only first 2 paragraphs)
⚠️ Want mixed content in one section (annotated + non-annotated)
⚠️ Complex documents with unusual structure

### Recommendation:
**Start without end tags.** Use heading-based scoping:

```markdown
[jig:O-001]: # "outcome priority:high"
## Goal: Enable Accurate Expense Tracking
(Everything until next same-level heading is O-001)

[jig:S-001]: # "spec satisfies:O-001"
### Technical Requirements
(Everything until next heading is S-001)
```

**If users need fine-grained control, add optional end tag:**

```markdown
[jig:O-001]: # "outcome priority:high"
## Enable Accurate Expense Tracking

First two paragraphs are part of O-001...

More content...

[jig:end]: #

This paragraph is NOT part of O-001.

[jig:S-001]: # "spec satisfies:O-001"
### Technical Requirements
...
```

---

## Configuration Option

Allow users to choose scoping strategy:

```toml
# .jig.toml
[docs.scoping]
strategy = "heading-based"  # heading-based | explicit-end-tag | next-annotation

# If "heading-based": content = heading + subsections until next same/higher heading
# If "explicit-end-tag": require [jig:end]: # to mark boundaries
# If "next-annotation": content until next [jig:...] annotation
```

---

## Inline End Tag?

**Question**: Can end tag be inline?

```markdown
[jig:O-001]: # "outcome priority:high"
## Enable Accurate Expense Tracking

Content here... [jig:end]: #

More content NOT part of O-001.
```

**Answer**: Yes, link references can appear anywhere, including inline. But:

❌ **Feels weird** - link refs usually on their own line
❌ **Less visible** - might miss it while editing
✅ **Technically works** - markdown parser will accept it

**Recommendation**: If you use end tags, put them on their own line for visibility.

---

## Final Recommendation

### ✅ Use heading-based scoping (no end tag)

```markdown
[jig:O-001]: # "outcome priority:high"
## Enable Accurate Expense Tracking

Content until next heading...

[jig:S-001]: # "spec satisfies:O-001"
### Technical Requirements

Content until next heading...
```

**Why**:
1. ✅ Clean and minimal
2. ✅ Matches natural document structure
3. ✅ Intuitive for authors
4. ✅ No risk of forgetting end tags
5. ✅ Works for 95% of use cases

### ⚠️ Provide escape hatch for edge cases

Add **optional** end tag support:

```markdown
[jig:end]: #
```

For the rare case where you need partial section annotation.

### Parser Complexity

Heading-based scoping requires:
- Markdown AST parsing (heading hierarchy)
- State machine to track current scope

But this is **one-time implementation cost** vs. ongoing **author burden** of end tags.

**Trade-off is worth it.**

---

**Status**: Recommendation Complete
**Recommended**: No end tag, heading-based scoping
**Escape hatch**: Optional `[jig:end]: #` for edge cases
