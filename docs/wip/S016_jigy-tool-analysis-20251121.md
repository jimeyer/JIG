# Jigy Tool Analysis Report

**Date**: 2025-11-21
**Context**: Investigation during graph-index.yaml construction task

## Executive Summary

jigy v0.1.0 is significantly behind the JIG v5.0 project spec. The tool reads only O/S nodes from markdown files and doesn't recognize relationships, subsystems, or C/T nodes. Graph artifacts have been successfully built following markdown frontmatter conventions, but jigy cannot interpret them.

## Version Mismatch

**Installed**: jigy v0.1.0
**Project Spec**: JIG v5.0 (Nearly Decomposable Systems)
**Gap**: ~5 major versions

```bash
$ jigy --version
jigy, version 0.1.0
```

## Current Tool Capabilities

### What jigy v0.1.0 Does

1. **Node Discovery**: Reads markdown files from:
   - `jig/outcomes/*.md` (O-* nodes)
   - `jig/specifications/*.md` (S-* nodes)

2. **Commands**:
   - `jigy status`: Shows node counts, subsystems (empty), warnings
   - `jigy validate`: Checks required fields (id, type, title), ID format, duplicates
   - `jigy node`: Manage nodes (create, update, delete)
   - `jigy graph`: Query and navigate (non-functional without edges)
   - `jigy decompose`: Analyze subsystem boundaries (non-functional)
   - `jigy init`: Initialize JIG structure

3. **Current Output**:
```
JIG Graph Status
✓ 65 nodes, 0 edges, 0 subsystems

Node summary:
  • Outcomes: 18
  • Specifications: 47

Warnings:
  ⚠ Orphaned nodes (65): [all nodes listed]
```

### What jigy v0.1.0 Doesn't Do

1. **Relationships**: Doesn't parse `implements:`, `satisfies:`, `verifies:`, `depends_on:` from frontmatter
2. **Subsystems**: Doesn't read subsystems.yaml or aggregate subsystem fields from nodes
3. **C/T Nodes**: Doesn't discover or track Code/Test nodes
4. **Graph Index**: Doesn't read or write graph-index.yaml
5. **Edge Counting**: Reports 0 edges despite frontmatter relationships

## JIG v5.0 Specification

Based on jig/README.md and artifacts:

### Node Types (OSTC Framework)

- **O-***: Outcomes (narrative truth - WHY)
- **S-***: Specifications (logical truth - WHAT)
- **T-***: Tests (empirical truth - HOW we verify)
- **C-***: Code (operational truth - HOW we implement)

### Artifact Structure

```
jig/
├── outcomes/           # O-*.md files with frontmatter
├── specifications/     # S-*.md files with frontmatter
├── generated/          # Auto-generated indices
│   ├── code_index.json
│   ├── test_index.json
│   └── graph.json      # Complete OSTC graph (99 nodes, 113 edges)
├── code_nodes.md       # C-* catalog (documentation)
├── test_nodes.md       # T-* catalog (documentation)
├── graph-index.yaml    # Node registry (SHOULD BE SOURCE OF TRUTH)
└── subsystems.yaml     # Subsystem definitions
```

### Relationship Model

**Frontmatter Format** (in O/S markdown files):
```yaml
---
id: S-AIR-001
type: specification
title: BikeState messages use operation_type field directly
subsystem: airspace
status: active
implements:
  - O-AIR-001
  - O-AIR-002
---
```

**graph.json Format** (generated):
```json
{
  "edges": [
    {"source": "S-PS-001", "target": "O-PS-001", "type": "satisfies"},
    {"source": "C-PS-001", "target": "S-PS-001", "type": "implements"},
    {"source": "T-PS-007", "target": "S-PS-007", "type": "validates"}
  ]
}
```

**Relationship Types**:
- `satisfies`: S→O (specification satisfies outcome)
- `implements`: S→O or C→S (code implements spec)
- `verifies`: T→S (test verifies spec)
- `depends_on`: Generic dependency (cross-references)

### Code Annotations

C/T nodes tracked via inline annotations:
```python
# @jig C-PS-001 implements:S-PS-001 subsystem:protocol interface:public
class EraLamportClock:
    """Distributed timestamp with total ordering"""
```

## Artifacts Created

### 1. graph-index.yaml

**Location**: `jig/graph-index.yaml`
**Status**: ✓ Created
**Contents**: 126 nodes with top-level relationship fields

**Structure**:
```yaml
version: '1.0'
nodes:
- id: C-MPS-001
  type: code
  title: ASEServer
  subsystem: multi_plane_server
  status: active
  implements:
  - S-MPS-001
- id: S-AIR-001
  type: specification
  title: BikeState messages use operation_type
  subsystem: airspace
  status: active
  implements:
  - O-AIR-001
  - O-AIR-002
```

**Node Counts**:
- Outcomes: 18
- Specifications: 47
- Code: 24
- Tests: 37
- **Total**: 126 nodes

**Sources**:
- O/S: Parsed from markdown files
- C/T: Extracted from jig/generated/graph.json
- Relationships: Converted from graph.json edges + markdown frontmatter

### 2. subsystems.yaml

**Location**: `jig/subsystems.yaml`
**Status**: ✓ Created
**Contents**: 7 subsystems extracted from node metadata

```yaml
subsystems:
- name: airspace
  description: Airspace subsystem
- name: airspace/crdt
  description: Airspace / Crdt subsystem
- name: gateway
  description: Gateway subsystem
- name: mps
  description: Mps subsystem
- name: multi_plane_server
  description: Multi_Plane_Server subsystem
- name: protocol
  description: Protocol subsystem
- name: protocol-stack
  description: Protocol Stack subsystem
```

**Issue**: Naming inconsistency between markdown files (protocol-stack, mps) and graph.json (protocol, multi_plane_server)

## Reference: jig/generated/graph.json

**Location**: `jig/generated/graph.json`
**Status**: Exists (older/partial)
**Generated**: 2025-11-18
**Scope**: Protocol Stack + Multi-Plane Server only (Phases 1-2)

**Statistics**:
- Total nodes: 99
- Outcomes: 8 (O-PS-*, O-MPS-*)
- Specifications: 24 (S-PS-*, S-MPS-*)
- Code: 24 (C-PS-*, C-MPS-*)
- Tests: 35 (T-PS-*, T-MPS-*)
- Edges: 113
  - satisfies: 24
  - implements: 39
  - validates: 50

**Gap**: Missing CRDT, Airspace, Gateway nodes (Phases 3+)

## Discrepancies Found

### 1. Node Count Mismatch

| Source | O | S | C | T | Total |
|--------|---|---|---|---|-------|
| jigy status | 18 | 47 | 0 | 0 | **65** |
| graph-index.yaml | 18 | 47 | 24 | 37 | **126** |
| graph.json | 8 | 24 | 24 | 35 | **99** |
| Markdown files | 18 | 47 | - | - | **65** |

**Analysis**:
- jigy only sees markdown files (65 O/S nodes)
- graph.json covers Phases 1-2 only (PS + MPS subsystems)
- graph-index.yaml includes all discovered nodes but has 2 extra tests vs graph.json

### 2. Subsystem Naming

**In Markdown Files**:
- `protocol-stack` (4 outcomes)
- `mps` (4 outcomes)
- `airspace` (10 outcomes)
- `gateway` (2 outcomes)
- `airspace/crdt` (3 outcomes)

**In graph.json**:
- `protocol` (not protocol-stack)
- `multi_plane_server` (not mps)

**Issue**: Inconsistent naming between phases/documents

### 3. Relationship Recognition

**Expected Behavior**: jigy should count edges from:
- Markdown frontmatter (`implements: [O-AIR-001]`)
- graph-index.yaml (top-level fields on nodes)

**Actual Behavior**: Reports 0 edges

**Root Cause**: jigy v0.1.0 doesn't parse relationship fields

## Validation Results

```bash
$ jigy validate
Validating JIG graph...
✓ All 65 nodes valid

Node summary:
  • Outcomes: 18
  • Specifications: 47
```

**What Validates**: Node structure (id, type, title fields)
**What Doesn't Validate**: Relationships, edge targets, subsystem references

## Recommendations

### Immediate Actions

1. **Update jigy Tool**: Upgrade to support JIG v5.0 features
   - Parse relationship fields from frontmatter
   - Read graph-index.yaml for C/T nodes
   - Load subsystems.yaml
   - Count and validate edges

2. **Standardize Subsystem Names**: Choose one convention
   - Either: `protocol-stack`, `mps` (markdown style)
   - Or: `protocol`, `multi_plane_server` (graph.json style)
   - Update all artifacts consistently

3. **Regenerate graph.json**: Include all phases (CRDT, Airspace, Gateway)
   - Current coverage: Phases 1-2 only
   - Missing: ~27 O/S nodes from Phases 3+

### Tool Enhancement Checklist

For jigy to support JIG v5.0, implement:

- [ ] Parse frontmatter relationship fields (implements, satisfies, verifies, depends_on)
- [ ] Read graph-index.yaml as primary node registry
- [ ] Load subsystems.yaml
- [ ] Count edges from node relationships
- [ ] Validate edge targets exist
- [ ] Track C/T nodes from graph-index or annotations
- [ ] Graph navigation (follows edges)
- [ ] Decomposition analysis (subsystem coupling)
- [ ] Alignment metrics (coverage across OSTC layers)

### Design Question

**What is the source of truth?**

**Option A**: Markdown frontmatter (current assumption)
- O/S nodes are markdown files with relationships in frontmatter
- graph-index.yaml is generated from markdown + annotations
- jigy parses markdown directly

**Option B**: graph-index.yaml (recommended)
- graph-index.yaml is hand-maintained or tool-maintained
- Markdown files are documentation/narrative
- jigy reads graph-index.yaml for structure

**Current State**: Hybrid/unclear
- Markdown has relationships but jigy doesn't parse them
- graph-index.yaml exists but jigy ignores it
- graph.json is generated but incomplete

## Files Generated During Investigation

1. `jig/graph-index.yaml` (126 nodes with relationships)
2. `jig/subsystems.yaml` (7 subsystems)
3. `docs/reports/orphaned-nodes-20251121.md` (initial empty graph report)
4. `build_jig_graph.py` (script to build graph from markdown + graph.json)

## Next Steps

**If updating jigy**:
1. Determine source of truth (frontmatter vs graph-index.yaml)
2. Implement relationship parsing
3. Add subsystem loading
4. Add C/T node discovery
5. Implement edge validation

**If working with current jigy**:
1. Accept that only O/S nodes are tracked
2. Use graph.json for full graph analysis
3. Manually maintain graph-index.yaml for reference
4. Use external tools for graph queries

**If regenerating graph.json**:
1. Scan all markdown files (not just PS/MPS)
2. Discover all @jig annotations in code/tests
3. Build complete 126-node graph
4. Update alignment metrics

---

**Tool Location**: `/Users/jmeyer/Code/jig/.venv/bin/jigy`
**Project Root**: `/Users/jmeyer/Code/ASE-A`
**Report Generated**: 2025-11-21
