---
id: S-117
type: specification
title: MCP Server for LLM Agent Access
outcomes: [O-031]
status: active
---

# MCP Server for LLM Agent Access

## Behavior

JIG exposes an MCP server via `jigy mcp` that provides LLM agents with structured access to JIG's graph, documents, and validation state.

## Acceptance Criteria

- `jigy mcp` starts an MCP server using stdio transport
- Server exposes four tools: lookup_node, search_docs, get_overview, validate_project
- lookup_node accepts an identifier string and returns node content, frontmatter, and graph neighbors
- lookup_node supports full identifier vocabulary: S-###, O-###, G-###, A-###, B-*, F-*, T-*, Charter, file paths
- lookup_node with unknown identifier returns empty result (graceful degradation)
- search_docs accepts query string and optional limit, returns matching documents with context snippets
- get_overview returns project summary: charter, goals, outcomes, spec counts, bricks, traversal keys
- validate_project accepts scope ("intent", "bricks", "full") and returns validation results
- All tools are read-only — no mutation of JIG artifacts
- Missing graph files do not cause errors — tools degrade gracefully
- All path resolution through JigConfig — works with non-default jig.toml configuration
- Server loads config once at startup

## Rationale

LLM agents need structured access to JIG's traceability data to ground their reasoning in verifiable truth (G-001), maintain context across sessions (G-002), read intent before modifying code (G-004), and traverse the full Charter-Goal-Outcome-Spec-Function-Test chain (G-005).
