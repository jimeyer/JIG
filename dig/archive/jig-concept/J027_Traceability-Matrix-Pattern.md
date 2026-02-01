---
title: "J027: Traceability Matrix Pattern"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1765341219
created_human: "2025-12-09 22:33 CST"
parent: "[[J017_JIG-Concept-v9]]"
children: []
---
# J027: Traceability Matrix Pattern

**Date:** 2025-12-09
**Status:** Pattern (Informational)
**Related:** J017 (JIG Concept v9), A001 (Core Artifacts Contract)

---

## Summary

A traceability matrix is a lightweight review artifact that maps architecture documents to JIG specifications. It lives outside the JIG system but supports verification that specs correctly derive from architecture.

**This is NOT a formal JIG artifact.** It's a helpful pattern for teams that want to verify coverage between architecture documents and specifications.

---

## The Problem

Architecture documents (like A002 CLI Command Architecture) define contracts and design decisions. JIG specifications (S-*) define testable behaviors. These are related but serve different purposes:

| Document | Purpose | Audience | Granularity |
|----------|---------|----------|-------------|
| Architecture (A-*) | Design philosophy, contracts | Humans designing systems | Broad |
| Specifications (S-*) | Testable requirements | Code, tests, auditors | Narrow |

**The question:** How do we verify that specifications correctly and completely derive from architecture documents?

**The constraint:** JIG specs must remain self-contained. The S-F-T audit chain (T → S → F) must be atomic—no external references that create indirection.

---

## The Solution: Traceability Matrix

A traceability matrix is a simple markdown table that maps architecture sections to specifications:

```markdown
| Architecture Section | Spec | Description |
|---------------------|------|-------------|
| A002 §2.2 | S-057 | Project root discovery |
| A002 §3.1 | S-058 | Rebuild commands |
| A002 §4.1 | — | Future work (not in scope) |
```

**Key properties:**

1. **Lives outside JIG** — in `docs/`, not `jig/`
2. **Not validated by JIG** — human-maintained review artifact
3. **Bi-directional** — shows both "what specs cover this section" and "what sections have no spec"
4. **Explicit gaps** — intentionally missing specs are documented with rationale

---

## Why Not Put References in Specs?

We considered several alternatives:

### Alternative 1: Frontmatter Reference
```yaml
---
id: S-057
type: specification
derived_from: "A002:§2.2"  # <-- Adding this
---
```

**Rejected because:**
- Creates coupling between specs and architecture docs
- Opens question: should JIG validate this field?
- If validated, architecture docs become JIG artifacts
- Violates "specs are self-contained" principle

### Alternative 2: Comment in Spec
```markdown
<!-- Derived from: A002 §2.2 -->
```

**Rejected because:**
- Comments are invisible to tooling
- No structured way to query coverage
- Drifts silently

### Alternative 3: Architecture Doc References Specs
```markdown
#### `jigy rebuild`
**Specification:** S-058
```

**Acceptable but insufficient:**
- Only shows one direction (arch → spec)
- Doesn't show gaps (sections without specs)
- Couples architecture doc to spec IDs

### Chosen: External Traceability Matrix

**Accepted because:**
- Specs remain self-contained
- JIG artifacts unchanged
- Easy to review coverage
- Explicit about intentional gaps
- Simple to maintain

---

## Template

Create `docs/architecture/{ID}-traceability.md`:

```markdown
# {Architecture Doc} Traceability Matrix

**Architecture Document:** {path to document}
**Last Reviewed:** {date}
**Reviewer:** {name or role}

## Purpose

This matrix verifies that specifications correctly and completely derive from the architecture document. It is a review artifact, not a JIG artifact.

## Traceability

| Section | Spec | Description | Notes |
|---------|------|-------------|-------|
| §1.1 ... | S-001 | ... | |
| §1.2 ... | S-002, S-003 | ... | Multiple specs for complex section |
| §2.1 ... | — | ... | Intentionally no spec: {reason} |
| §2.2 ... | — | ... | Future work: {ticket/plan reference} |

## Coverage Summary

- Sections with specifications: X
- Sections intentionally without specifications: Y
- Gaps requiring attention: Z

## Review Checklist

- [ ] All architecture sections accounted for
- [ ] Each spec is self-contained (no references to this doc)
- [ ] Intentional gaps have documented rationale
- [ ] No orphan specs (specs not traced to any section)
```

---

## Example: A002 CLI Architecture

```markdown
# A002 CLI Architecture Traceability Matrix

**Architecture Document:** docs/architecture/A002_CLI-Command-Architecture.md
**Last Reviewed:** 2025-12-09
**Reviewer:** Development team

## Purpose

This matrix verifies that CLI specifications correctly derive from A002. It is a review artifact, not a JIG artifact.

## Traceability

| A002 Section | Spec | Description | Notes |
|--------------|------|-------------|-------|
| §2.2 Sensible Discovery | S-057 | Project root auto-discovery | |
| §3.1 `jigy rebuild` | S-058 | Verb-first rebuild commands | |
| §3.2 `jigy align` | S-059 | Full workflow command | |
| §3.3 `jigy show` | S-060 | Show command structure | |
| §1.1 Radical Simplicity | S-061 | Minimal global options | |
| §3.4 `jigy validate` | — | Validate commands | No new spec: behavior unchanged |
| §3.5 `jigy audit` | — | Audit commands | Future work: B013 excludes |
| §4 Common Workflows | — | Usage examples | Documentation only, not testable |
| §5 Exit Codes | — | Exit code conventions | Covered implicitly by S-057-061 |

## Coverage Summary

- Sections with specifications: 5
- Sections intentionally without specifications: 4
- Gaps requiring attention: 0

## Review Checklist

- [x] All architecture sections accounted for
- [x] Each spec is self-contained
- [x] Intentional gaps have documented rationale
- [x] No orphan specs
```

---

## When to Use This Pattern

**Use when:**
- You have architecture documents that define contracts
- You want to verify spec coverage of those contracts
- You need to explain why some sections don't have specs
- Multiple people work on deriving specs from architecture

**Don't use when:**
- Architecture is informal or evolving rapidly
- Specs are the only source of truth (no architecture docs)
- Team is small and coverage is obvious

---

## Relationship to JIG

```
┌─────────────────────────────────────────────────────────┐
│                    Outside JIG                          │
│  ┌─────────────────┐      ┌──────────────────────────┐ │
│  │ Architecture    │      │ Traceability Matrix      │ │
│  │ Documents (A-*) │─────→│ (review artifact)        │ │
│  └─────────────────┘      └──────────────────────────┘ │
│           │                          │                  │
│           │ humans derive            │ humans verify    │
│           ▼                          ▼                  │
├─────────────────────────────────────────────────────────┤
│                    Inside JIG                           │
│  ┌─────────────────┐                                   │
│  │ Specifications  │◄──── @jig.verifies ──── Tests    │
│  │ (S-*)           │                                   │
│  │                 │◄──── @jig.implements ── Functions│
│  └─────────────────┘                                   │
│                                                         │
│  The S-F-T triangle remains self-contained             │
└─────────────────────────────────────────────────────────┘
```

**The traceability matrix bridges the gap between architecture and JIG without polluting JIG's core model.**

---

## Maintenance

### When to Update

- After creating new specs derived from architecture
- After architecture document changes
- Before major releases (coverage review)
- During architecture reviews

### Who Maintains

- The person deriving specs updates the matrix
- Architecture owner reviews for completeness
- No automated validation (intentionally human-reviewed)

### Version Control

- Commit matrix updates with related spec changes
- Matrix is documentation, not code—review standards apply

---

## Anti-Patterns

### Anti-Pattern 1: Matrix as Source of Truth

```markdown
| Section | Spec | Requirement |
|---------|------|-------------|
| §2.2 | S-057 | CLI discovers project root | <-- Don't duplicate spec content
```

**Problem:** Now you have two places defining the requirement.
**Fix:** Matrix only contains IDs and brief descriptions, not full requirements.

### Anti-Pattern 2: Validating Matrix in CI

```yaml
# Don't do this
- name: Validate traceability
  run: jig validate-traceability A002
```

**Problem:** Makes matrix a formal artifact, increases maintenance burden.
**Fix:** Matrix is human-reviewed, not machine-validated.

### Anti-Pattern 3: Spec References Matrix

```markdown
---
id: S-057
type: specification
traced_in: "A002-traceability.md"  # <-- Don't do this
---
```

**Problem:** Creates circular dependency, pollutes spec frontmatter.
**Fix:** Traceability is one-way: matrix → specs, not specs → matrix.

---

## Summary

The traceability matrix is a **lightweight, human-maintained review artifact** that helps teams verify specs derive correctly from architecture documents. It lives outside JIG, doesn't affect the S-F-T audit chain, and makes coverage gaps explicit.

**Use it when you need to answer:** "Did we correctly and completely extract specs from this architecture document?"

**Don't use it to:** Replace specs, automate validation, or create formal dependencies between architecture and JIG.

---

_A helpful pattern, not a requirement._
