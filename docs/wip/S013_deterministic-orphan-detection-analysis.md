# Analysis: Deterministic vs Judgment-Based Operations in Orphaned Node Detection

**Date**: 2025-11-21
**Context**: Analysis of `agents/taskRepairOrphanedNodes.md` to identify automation opportunities

## Executive Summary

The orphaned node detection task is approximately **80% deterministic** and suitable for scripting. The remaining 20% involves contextual judgment that benefits from AI reasoning. We should implement the deterministic portions as helper scripts/tools that agents can invoke, reducing token usage and increasing reliability.

## Operation Breakdown

### Fully Deterministic Operations (Scriptable)

#### 1. Load and Parse Graph Data ✓
**Deterministic**: 100%

```python
# Pseudocode
def load_graph_data():
    graph = yaml.safe_load(open('jig/graph-index.yaml'))
    subsystems = yaml.safe_load(open('jig/subsystems.yaml'))
    node_registry = {node['id']: node for node in graph}
    return graph, subsystems, node_registry
```

**Why scriptable**: Pure file I/O and YAML parsing. No ambiguity.

---

#### 2. Identify Orphans - Type 1: Dangling References ✓
**Deterministic**: 100%

```python
# Pseudocode
def find_dangling_references(graph, node_registry):
    dangling = []
    relationship_fields = ['implements', 'specifies', 'contributes_to', 'depends_on']

    for node in graph:
        for field in relationship_fields:
            if field in node:
                refs = node[field] if isinstance(node[field], list) else [node[field]]
                for ref in refs:
                    if ref not in node_registry:
                        dangling.append({
                            'node_id': node['id'],
                            'field': field,
                            'missing_ref': ref
                        })
    return dangling
```

**Why scriptable**: Simple set membership check. Binary yes/no answer.

---

#### 3. Identify Orphans - Type 2: Unreferenced Nodes ✓
**Deterministic**: 100%

```python
# Pseudocode
def find_unreferenced_nodes(graph, node_registry):
    referenced_ids = set()
    relationship_fields = ['implements', 'specifies', 'contributes_to', 'depends_on']

    for node in graph:
        for field in relationship_fields:
            if field in node:
                refs = node[field] if isinstance(node[field], list) else [node[field]]
                referenced_ids.update(refs)

    all_ids = set(node_registry.keys())
    unreferenced = all_ids - referenced_ids

    return [{'node_id': nid, 'node': node_registry[nid]} for nid in unreferenced]
```

**Why scriptable**: Set operations. Mechanically defined.

---

#### 5. Generate Repair Report (Structure) ✓
**Deterministic**: 90%

```python
# Pseudocode
def generate_report_structure(dangling, unreferenced, malformed):
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'total_nodes': len(node_registry),
        'summary': {
            'broken_references': len(dangling),
            'isolated_nodes': len(unreferenced),
            'malformed': len(malformed)
        },
        'findings': {
            'dangling': dangling,
            'unreferenced': unreferenced,
            'malformed': malformed
        }
    }
    return report
```

**Why scriptable**: Template-based generation. Structure is fixed.

**Non-deterministic part**: Suggested fix text (requires context/judgment).

---

### Judgment-Based Operations (AI-Suitable)

#### 4. Categorize Findings and Suggest Repairs ⚖️
**Deterministic**: 20%
**Judgment Required**: 80%

**Questions requiring context:**
- Is this unreferenced node intentionally a root node?
- Is this a legacy/deprecated node that should be removed?
- What is the appropriate parent concept for an isolated node?
- Should this broken reference be fixed by creating the missing node or removing the reference?
- Does the node's description/context suggest it's still relevant?

**Example requiring judgment:**

```yaml
- id: T-JIG-042
  type: Technical Component
  description: "Legacy validation module for deprecated API v1"
```

**Deterministic detection**: ✓ Unreferenced
**Judgment call**: Should we:
- A) Remove it (deprecated)?
- B) Link it to a historical design document?
- C) Keep it isolated as archival reference?

The AI should read the description, understand "deprecated API v1" context, and make an informed recommendation.

---

## Proposed Architecture

### Helper Script: `jig/tools/graph_integrity.py`

```python
#!/usr/bin/env python3
"""
Deterministic graph integrity checks.
Outputs structured JSON for AI consumption.
"""

import yaml
import json
from datetime import datetime
from pathlib import Path

def check_graph_integrity(graph_path, subsystems_path):
    """
    Returns dict with:
    - dangling_references: [{node_id, field, missing_ref}]
    - unreferenced_nodes: [{node_id, node_data}]
    - malformed_structures: [{node_id, issue}]
    - stats: {total_nodes, total_relationships}
    """
    pass

if __name__ == '__main__':
    result = check_graph_integrity(
        'jig/graph-index.yaml',
        'jig/subsystems.yaml'
    )
    print(json.dumps(result, indent=2))
```

### Usage in Agent Task

**Old workflow:**
```
Agent reads YAML → Agent parses → Agent builds indices →
Agent finds issues → Agent categorizes → Agent writes report
```
**Token cost**: ~5000 tokens for processing

**New workflow:**
```
Agent runs: python jig/tools/graph_integrity.py →
Agent reads JSON output (structured findings) →
Agent adds contextual judgment and suggested fixes →
Agent writes enhanced report
```
**Token cost**: ~1500 tokens (70% reduction)

---

## Benefits of Hybrid Approach

### 1. **Reliability**
- Deterministic code has unit tests
- No risk of AI "forgetting" to check a relationship field
- Consistent results across runs

### 2. **Performance**
- Script runs in <100ms vs AI reasoning through each node
- Token efficiency: AI focuses on judgment, not mechanics

### 3. **Transparency**
- Script output is structured JSON—easy to inspect
- Clear separation: "here are the facts" vs "here's what they mean"

### 4. **Maintainability**
- If relationship fields change, update script once
- AI task doc references the tool: "Run graph_integrity.py first"

### 5. **Composability**
- Script can be used standalone for CI/CD validation
- Agent can invoke it as needed
- Human operators can run it for quick checks

---

## Implementation Recommendations

### Phase 1: Core Detection Script
Build `jig/tools/graph_integrity.py` with:
- [x] YAML parsing with error handling
- [x] Dangling reference detection
- [x] Unreferenced node detection
- [x] Malformed structure detection (null checks, type validation)
- [x] JSON output format
- [x] CLI interface with --format flag (json|summary)

### Phase 2: Enhanced Agent Task
Update `agents/taskRepairOrphanedNodes.md`:
- Add **Prerequisites** section: "Run `python jig/tools/graph_integrity.py` first"
- Update **Inputs** section: Include JSON output from script
- Refocus **Process** section on interpretation and repair suggestion logic
- Add example of script output → AI judgment flow

### Phase 3: Integration Patterns
Establish pattern for other deterministic operations:
- `jig/tools/validate_node_format.py` - Schema validation
- `jig/tools/graph_stats.py` - Metrics and coverage
- `jig/tools/extract_markers.py` - Deterministic marker extraction (WU0-level)

---

## Alternative: jigy Subcommand

Instead of standalone scripts, integrate into the `jigy` CLI:

```bash
# Deterministic check
jigy graph check-integrity --format json > findings.json

# AI-enhanced analysis
claude-agent agents/taskRepairOrphanedNodes.md --input findings.json
```

This follows the Unix philosophy: small tools that do one thing well, composed via pipes.

---

## Edge Case: When NOT to Script

Some operations seem deterministic but require judgment:

**Example**: "Find nodes with no description field"
- **Deterministic detection**: ✓ Easy
- **Problem**: Are missing descriptions always wrong?
  - Maybe Work Units don't need descriptions if title is clear
  - Maybe Technical Components require them
  - **Judgment needed**: Context-dependent rules

**Rule of thumb**: If the rule requires phrases like "usually," "typically," or "it depends," keep it AI-driven.

---

## Recommendation Summary

| Operation | Implementation | Rationale |
|-----------|---------------|-----------|
| Load/Parse | Script | Pure I/O |
| Dangling refs | Script | Set membership |
| Unreferenced nodes | Script | Set difference |
| Malformed check | Script | Schema validation |
| Categorization | AI | Requires context |
| Repair suggestions | AI | Domain knowledge |
| Report writing | AI | Natural language synthesis |

**Action Items**:
1. Implement `jig/tools/graph_integrity.py` with JSON output
2. Add unit tests for edge cases (circular refs, self-refs, null values)
3. Update agent task to reference the tool
4. Document the pattern in `CONTRIBUTING.md` as the standard for deterministic/AI hybrid workflows

---

## Appendix: JSON Output Schema

```json
{
  "timestamp": "2025-11-21T10:30:00Z",
  "graph_file": "jig/graph-index.yaml",
  "total_nodes": 42,
  "findings": {
    "dangling_references": [
      {
        "node_id": "S-JIG-001",
        "node_type": "Specification",
        "field": "specifies",
        "missing_reference": "O-JIG-999",
        "node_context": {
          "description": "Performance requirements for marker extraction"
        }
      }
    ],
    "unreferenced_nodes": [
      {
        "node_id": "T-JIG-042",
        "node_type": "Technical Component",
        "node_data": {
          "description": "Legacy validation module",
          "status": "deprecated"
        },
        "potential_reason": "isolated"
      }
    ],
    "malformed_structures": [
      {
        "node_id": "W-JIG-005",
        "issue": "relationship_field_empty",
        "field": "implements",
        "value": null
      }
    ]
  },
  "statistics": {
    "total_relationships": 87,
    "relationship_density": 2.07,
    "node_type_distribution": {
      "Outcome": 5,
      "Specification": 12,
      "WorkUnit": 18,
      "TechnicalComponent": 7
    }
  }
}
```

The AI receives this structured data and focuses on:
1. Interpreting `node_context` to determine if issues are problems or intentional
2. Generating human-readable explanations
3. Suggesting specific repair actions based on domain knowledge
4. Prioritizing fixes based on impact

---

**Next Steps**: Decide whether to implement as standalone script or `jigy` subcommand, then proceed with Phase 1 development.
