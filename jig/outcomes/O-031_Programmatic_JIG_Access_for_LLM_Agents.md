---
id: O-031
type: outcome
title: Programmatic JIG Access for LLM Agents
supports_goals: [G-001, G-002, G-004, G-005]
specifications: [S-116, S-117]
status: active
---

# Programmatic JIG Access for LLM Agents

LLM agents can query JIG's complete graph structure — nodes, relationships, validation state, and document content — through structured MCP tools without parsing CLI text output.

## Value

Agents working on JIG-enabled codebases get first-class access to the intent hierarchy. Instead of running CLI commands and parsing human-formatted output, agents call typed MCP tools that return structured data. This eliminates an entire class of context-building errors where agents hallucinate code structure or miss architectural constraints.

## AI Agent Benefit

Without programmatic access, agents must:
1. Run `jigy context S-042` and parse text output
2. Guess file locations for specifications and outcomes
3. Manually construct relationships between nodes
4. Re-derive information that JIG already computes

With MCP tools, agents call `lookup_node("S-042")` and receive structured JSON with content, frontmatter, and graph neighbors — the same data, instantly usable.
