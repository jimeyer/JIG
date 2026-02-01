---
title: "B026: Intent Document Title Audit"
type: journal
status: implemented
decision: "Superseded by newer deliberation"
created: 1766525018
created_human: "2025-12-23 14:23 MST"
parent: null
children: []
---
---
title: Intent Document Title Audit
date: 2025-12-22
status: draft
purpose: Audit outcome and specification titles against A001 title requirements
---

# B026: Intent Document Title Audit

This audit evaluates all outcome and specification titles against the updated
A001 Core Artifacts Contract requirements:

- **Outcomes**: Noun phrase describing delivered value
- **Specifications**: Noun phrase describing observable behavior or capability

---

## Summary

| Category | Conforming | Non-Conforming | Total |
|----------|------------|----------------|-------|
| Outcomes | 10 | 8 | 18 |
| Specifications | 46 | 8 | 54 |
| **Total** | **56** | **16** | **72** |

---

## Part I: Outcome Title Audit

### Conforming Titles (10)

These titles are proper noun phrases describing delivered value:

| ID | Title | Notes |
|----|-------|-------|
| O-004 | Early Error Detection in Artifact Validation | ✓ |
| O-005 | Clear Actionable Error Messages | ✓ |
| O-006 | Fast Project Validation | ✓ |
| O-015 | Completeness validation for intent graph | ✓ (lowercase but noun phrase) |
| O-016 | CI and Tooling Integration | ✓ |
| O-017 | Artifact Change Detection | ✓ |
| O-018 | Test-to-Specification Traceability | ✓ |
| O-019 | Intuitive CLI Experience | ✓ |
| O-020 | Configurable Project Structure | ✓ |
| O-021 | Verifiable Test-to-Implementation Coverage | ✓ |

### Non-Conforming Titles (8)

These titles use sentence structure instead of noun phrases:

| ID | Current Title | Issue | Recommended Title |
|----|---------------|-------|-------------------|
| O-001 | Implementation structure is discoverable from source code | Sentence (subject + predicate) | Discoverable Implementation Structure |
| O-002 | Code-to-specification traceability is automated | Sentence (subject + predicate) | Automated Code-to-Specification Traceability |
| O-003 | Implementation graphs support multi-language codebases | Sentence (subject + predicate) | Multi-Language Implementation Graph Support |
| O-009 | Generate Intent Graph from Specifications and Bricks | Imperative verb | Intent Graph Generation |
| O-012 | Brick definitions comply with A001 format requirements | Sentence (subject + predicate) | A001-Compliant Brick Definitions |
| O-013 | Layer architecture is enforced and validated | Sentence (subject + predicate) | Layer Architecture Enforcement |
| O-014 | Layer structure is visible and manageable | Sentence (subject + predicate) | Layer Structure Visibility |
| O-022 | Commands Operate on Current Data | Sentence (subject + predicate) | Current Data Guarantee for Commands |

---

## Part II: Specification Title Audit

### Conforming Titles (46)

These titles are proper noun phrases describing observable behavior or capability:

| ID | Title |
|----|-------|
| S-018 | Specification File Validation |
| S-019 | Outcome File Validation |
| S-020 | Decorator Reference Validation |
| S-021 | Brick Definition Validation |
| S-022 | Brick Partition Validation |
| S-023 | Intent Validation CLI Command |
| S-024 | Brick Validation CLI Command |
| S-025 | Full Validation CLI Command |
| S-026 | JSON Output Format for CI Integration |
| S-027 | Auto-Validation in Rebuild Commands |
| S-028 | CLI Command to Generate Intent Graph |
| S-035 | Brick ID Format Validation |
| S-036 | Layer Field Presence Validation |
| S-037 | Layer Value Validation |
| S-038 | Layer Constraint Validation |
| S-039 | Circular Dependency Detection |
| S-040 | CLI Command: jigy layers |
| S-041 | CLI Command: jigy layers suggest |
| S-044 | Content Hash Format |
| S-045 | Intent Artifact Hashing |
| S-046 | Function Hashing via AST |
| S-047 | Test Hashing via AST |
| S-048 | Brick Definition Hashing |
| S-049 | Git Blob Optimization |
| S-050 | Graph Schema Hash Fields |
| S-051 | Test File Discovery |
| S-052 | Test Node Schema |
| S-053 | Verifies Decorator Extraction |
| S-054 | Test Function Hashing |
| S-055 | Verification Graph Generation |
| S-056 | CLI Verify Rebuild Command |
| S-057 | Project Root Auto-Discovery |
| S-058 | Verb-First Rebuild Commands |
| S-059 | Align Command |
| S-060 | Show Command Structure |
| S-061 | Minimal Global Options |
| S-062 | Configuration File Discovery |
| S-063 | TOML Configuration Parsing |
| S-064 | Path Configuration with Defaults |
| S-065 | CLI Integration with Configuration |
| S-066 | T→F Edge Collection via Coverage |
| S-067 | Coverage Record Format |
| S-068 | Graph Metadata for Staleness Detection |
| S-069 | Staleness Detection Module |
| S-070 | Auto-Rebuild Before Commands |
| S-071 | Skip Auto-Rebuild Flag |

### Non-Conforming Titles (8)

These titles use sentence or passive construction instead of noun phrases:

| ID | Current Title | Issue | Recommended Title |
|----|---------------|-------|-------------------|
| S-001 | Python code structure extracted via AST analysis | Passive sentence | Python Code Structure Extraction |
| S-002 | @jig.implements() decorators extracted and linked | Passive sentence | Implements Decorator Extraction |
| S-003 | NDJSON output is deterministic and git-friendly | Sentence (subject + predicate) | Deterministic NDJSON Output |
| S-004 | Language analyzers follow plugin architecture | Sentence (subject + predicate) | Language Analyzer Plugin Architecture |
| S-005 | External dependencies tracked at package level | Passive sentence | External Dependency Tracking |
| S-006 | Parse errors fail fast with clear file:line reporting | Sentence (subject + predicate) | Fail-Fast Parse Error Reporting |
| S-042 | Validate outcomes specify at least one specification | Imperative verb | Outcome Specification Requirement |
| S-043 | Validate specifications are specified by at least one outcome | Imperative verb | Specification-Outcome Linkage Requirement |

---

## Part III: Pattern Analysis

### Common Issues

1. **Sentence Structure** (11 instances)
   - Using "X is Y" or "X does Y" instead of noun phrases
   - Examples: "Implementation structure is discoverable", "NDJSON output is deterministic"

2. **Passive Construction** (4 instances)
   - Using "X extracted" or "X tracked" as title
   - Examples: "decorators extracted and linked", "dependencies tracked"

3. **Imperative Verbs** (3 instances)
   - Starting with action verbs like "Generate" or "Validate"
   - Examples: "Generate Intent Graph", "Validate outcomes specify"

### Conforming Pattern Examples

The majority of specifications follow good patterns:

- **Behavior + Context**: "Brick ID Format Validation", "Layer Constraint Validation"
- **Noun + Noun**: "Content Hash Format", "Test Node Schema"
- **Capability Description**: "Project Root Auto-Discovery", "Circular Dependency Detection"
- **CLI Command Pattern**: "CLI Command: jigy layers" (acceptable for command specs)

---

## Part IV: Recommendations

### Priority 1: Outcome Titles (8 changes)

Outcomes are high-visibility documents. Fix these first:

| ID | Change |
|----|--------|
| O-001 | "Implementation structure is discoverable..." → **Discoverable Implementation Structure** |
| O-002 | "Code-to-specification traceability is automated" → **Automated Code-to-Specification Traceability** |
| O-003 | "Implementation graphs support multi-language..." → **Multi-Language Implementation Graph Support** |
| O-009 | "Generate Intent Graph from..." → **Intent Graph Generation** |
| O-012 | "Brick definitions comply with..." → **A001-Compliant Brick Definitions** |
| O-013 | "Layer architecture is enforced..." → **Layer Architecture Enforcement** |
| O-014 | "Layer structure is visible..." → **Layer Structure Visibility** |
| O-022 | "Commands Operate on Current Data" → **Current Data Guarantee for Commands** |

### Priority 2: Core Specification Titles (6 changes)

S-001 through S-006 are foundational specs frequently referenced:

| ID | Change |
|----|--------|
| S-001 | "Python code structure extracted..." → **Python Code Structure Extraction** |
| S-002 | "@jig.implements() decorators extracted..." → **Implements Decorator Extraction** |
| S-003 | "NDJSON output is deterministic..." → **Deterministic NDJSON Output** |
| S-004 | "Language analyzers follow..." → **Language Analyzer Plugin Architecture** |
| S-005 | "External dependencies tracked..." → **External Dependency Tracking** |
| S-006 | "Parse errors fail fast..." → **Fail-Fast Parse Error Reporting** |

### Priority 3: Validation Specification Titles (2 changes)

| ID | Change |
|----|--------|
| S-042 | "Validate outcomes specify..." → **Outcome Specification Requirement** |
| S-043 | "Validate specifications are specified..." → **Specification-Outcome Linkage Requirement** |

---

## Part V: Implementation Notes

### When Updating Titles

1. Update the H1 heading in the markdown body
2. Add `title:` field to frontmatter (not yet required, but recommended)
3. Ensure H1 matches frontmatter title exactly (per B025)
4. Update any cross-references in other documents

### Validation Checklist

For each title change, verify:
- [ ] Title is a noun phrase (no verbs as main element)
- [ ] Title describes value (outcomes) or behavior/capability (specs)
- [ ] Title is concise (aim for 3-6 words)
- [ ] Title avoids starting with articles (a, an, the)

---

## References

- [A001: Core Artifacts Contract](../architecture/A001_Core-Artifacts-Contract.md) — Title field requirements
- [B025: Intent Document Format Specification](./B025_Intent-Document-Format.md) — Full format guidance
