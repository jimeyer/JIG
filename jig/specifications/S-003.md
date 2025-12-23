---
id: S-003
title: Deterministic NDJSON Output
type: specification
---

# Deterministic NDJSON Output

## Constraints

1. **One JSON object per line, no pretty-printing**
   - Each line is a complete, valid JSON object
   - No indentation, no extra whitespace
   - Newline (`\n`) separates objects
   - Can be processed line-by-line without loading entire file

2. **Nodes sorted by ID (stable diffs)**
   - Nodes appear in lexicographic order by ID
   - Same graph always produces same node order
   - Git diffs show semantic changes, not reordering noise

3. **Same input → identical output (deterministic)**
   - Given identical source code, output is byte-for-byte identical
   - Use `sort_keys=True` in `json.dumps()` for stable field ordering
   - Exclude non-deterministic fields like timestamps (or make them optional)

4. **Metadata line first, then nodes, then edges**
   - Line 1: `{"_meta": {"version": "1.0", "node_count": N, "edge_count": M, ...}}`
   - Lines 2-N+1: Node objects sorted by ID
   - Lines N+2-M+1: Edge objects (order not guaranteed, but deterministic)

## File Format Example

```ndjson
{"_meta": {"version": "1.0", "generated": "2025-11-26T10:00:00Z", "node_count": 3, "edge_count": 2}}
{"id": "C-jig.core.graph.Graph", "type": "class", "language": "python", "line": 10, "methods": ["add_node", "add_edge"]}
{"id": "F-jig.core.graph.Graph.add_node", "type": "function", "language": "python", "line": 15, "signature": "add_node(self, node: Dict) -> None"}
{"id": "M-jig.core.graph", "type": "module", "language": "python", "file": "src/jig/core/graph.py"}
{"source": "M-jig.core.graph", "target": "C-jig.core.graph.Graph", "type": "contains"}
{"source": "C-jig.core.graph.Graph", "target": "F-jig.core.graph.Graph.add_node", "type": "contains"}
```

## Output Location

Per A001 Core Artifacts Contract:
- **File**: `jig/generated/implementation-graph.ndjson`
- **Directory**: Auto-create `jig/generated/` if it doesn't exist
- **Git**: Add `jig/generated/` to `.gitignore` (generated artifacts not committed by default)

## Validation

Output must be:
1. **Valid NDJSON**: Every line parses as JSON
2. **Schema-compliant**: All nodes have required fields (`id`, `type`, `language`)
3. **Reference-valid**: All edge source/target IDs reference existing nodes
4. **Deterministic**: Running twice on same input produces identical output

## Rationale

NDJSON (newline-delimited JSON) is ideal for generated artifacts because:
- **Git-friendly**: Line-based diffs show semantic changes clearly
- **Streamable**: Can process large graphs without loading entire file into memory
- **Tool-friendly**: Standard format with broad ecosystem support (jq, ripgrep, etc.)
- **Human-readable**: Can inspect with `head`, `tail`, `grep` without special tools

Determinism is critical for version control: non-deterministic output creates noisy diffs that make code review difficult and trigger unnecessary CI runs.

## Processing Examples

```bash
# Count nodes by type
grep '"type"' jig/generated/implementation-graph.ndjson | grep -o '"type": "[^"]*"' | sort | uniq -c

# Find all functions that implement S-001
grep '"implements"' jig/generated/implementation-graph.ndjson | grep 'S-001'

# Extract metadata
head -1 jig/generated/implementation-graph.ndjson | jq .

# Validate all lines are valid JSON
cat jig/generated/implementation-graph.ndjson | while read line; do echo "$line" | jq . > /dev/null || echo "Invalid JSON"; done
```
