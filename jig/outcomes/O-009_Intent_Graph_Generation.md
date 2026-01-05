---
id: O-009
title: Intent Graph Generation
type: outcome
theme: [Alignment Graph]
supports_goals: [G-004, G-002]
specifies: [S-028]
---

# Intent Graph Generation

**Value:** JIG generates a complete intent graph from specifications, outcomes, and brick definitions, making human-authored intent machine-queryable.

**Acceptance:** `jigy rebuild intent` generates a valid NDJSON intent graph from all JIG artifacts in <2 seconds.

## AI Agent Benefit

Agents query the intent graph to understand what the system should do before examining what it actually does. This prevents agents from inferring intent from implementation - a common source of hallucination. The intent graph is the single source of truth for "why" and "what," enabling agents to verify their work against explicit requirements.

## Rationale

Software projects accumulate implicit intent. Developers know what the code should do, but this knowledge lives in their heads, scattered comments, and outdated documentation. When an AI agent (or new developer) arrives, they must infer intent from implementation - a noisy, error-prone process.

The intent graph makes intent explicit and machine-readable. Specifications describe behaviors. Outcomes describe value. Bricks describe boundaries. Together, they form a queryable graph of project intent that agents can traverse and reason about.

This graph enables alignment analysis. By joining intent nodes with implementation nodes, JIG can answer: Which specs are implemented? Which are not? Which implementations have no corresponding intent (possible cruft)? These queries surface misalignment before it causes production issues.

The NDJSON format enables clean git diffs (one node per line), streaming processing (useful for large graphs), and easy tooling integration. Deterministic generation ensures reproducible builds - the same inputs always produce the same graph.

## Success Criteria

The intent graph generator must:
1. Parse all specification files from `jig/specifications/*.md`
2. Parse all outcome files from `jig/outcomes/*.md`
3. Parse brick definitions from `jig/bricks.yaml`
4. Generate graph conforming to A001 schema
5. Output NDJSON format with one node per line
6. Complete generation in <2 seconds for typical projects
7. Produce deterministic, reproducible output

## Specified By

This outcome is delivered through:
- **S-028**: Intent Graph Generation - parses artifacts and generates NDJSON graph

## Constitution Linkage

This outcome serves: **Part I: Alignment Graph** - Connecting Intent to Code
Enables: Machine-queryable intent, alignment analysis, agent grounding in explicit requirements
Without this: Intent is implicit and must be inferred from implementation; agents hallucinate requirements
