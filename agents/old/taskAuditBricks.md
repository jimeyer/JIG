# Task: Layer-Ordered Brick Audit

**Version:** 1.0
**Date:** 2025-12-03
**References:** AG029 (Brick Layers), AG028 (Brick Detection Workflow), AG020 (Bricks as Partitions), A001 (Core Artifacts Contract)

---

## Objective

Systematically audit all bricks in the system layer by layer (starting from foundation layer 0 and proceeding upward) to validate architectural coherence, identify quality issues, and verify layer constraints are properly maintained.

---

## Context

### What is This Task For?

JIG organizes code into **bricks** (coherent functional units) arranged in **layers** (architectural strata). This task performs a comprehensive audit of all bricks in layer order to:

1. **Verify layer constraints** - Ensure bricks only depend on lower layers
2. **Validate brick quality** - Check cohesion, coherence, and appropriate sizing
3. **Identify architectural drift** - Detect when implementation diverges from declared structure
4. **Generate actionable reports** - Provide specific recommendations for each brick

### Why Layer Order Matters

Auditing proceeds bottom-up (layer 0 ’ layer 1 ’ layer 2 ’ ...) because:
- **Foundation first**: Layer 0 issues cascade upward, so catch them early
- **Dependency context**: Can't properly audit layer N until layer N-1 is validated
- **Work prioritization**: Issues in lower layers are higher priority (wider impact)
- **Incremental validation**: Can stop at any layer and have partial validation

### Key Principle

This is a **read-only analysis task**. You are producing audit reports, not modifying code or architecture. All recommendations require human approval before implementation.

---

## Inputs

### 1. Brick Definitions
**Location:** `jig/bricks.yaml`

**Format:** YAML

**Structure:**
```yaml
bricks:
  - id: B-core-utils
    name: Core Utilities
    layer: 0
    units:
      - M-jig.utils.io
      - M-jig.utils.yaml_utils

  - id: B-impl-graph
    name: Implementation Graph Core
    layer: 1
    units:
      - M-jig.impl_graph.graph
      - M-jig.impl_graph.builder
```

**Required fields:**
- `id` (string): Brick identifier in format `B-{kebab-case-name}`
- `name` (string): Human-readable brick name
- `layer` (integer): Architectural layer (0 = foundation, higher = more dependent)
- `units` (array): Node references (M-, C-, or F- prefixes)

**What to extract:**
- List of all bricks grouped by layer
- For each brick: id, name, layer, units
- Layer count (highest layer number + 1)

### 2. Implementation Graph
**Location:** `jig/generated/implementation-graph.ndjson`

**Format:** NDJSON (one JSON object per line)

**Structure:**
- **Line 1:** Metadata (skip this line)
  ```json
  {"_meta": {"node_count": 126, "edge_count": 158, ...}}
  ```

- **Function nodes:**
  ```json
  {"id":"F-jig.cli.main.rebuild","type":"function","file":"src/jig/cli/main.py","implements":["S-001"],"calls":["F-jig.impl_graph.builder.build_graph"]}
  ```

- **Class nodes:**
  ```json
  {"id":"C-jig.impl_graph.graph.Graph","type":"class","file":"src/jig/impl_graph/graph.py","implements":["S-003"]}
  ```

- **Module nodes:**
  ```json
  {"id":"M-jig.cli.main","type":"module","file":"src/jig/cli/main.py"}
  ```

**What to extract:**
- All nodes (functions, classes, modules)
- Call relationships (who calls whom)
- Implementation relationships (which functions implement which specs)

### 3. Intent Graph (Optional but Recommended)
**Location:** `jig/generated/intent-graph.ndjson`

**Purpose:** Provides specification and outcome information for context

**What to extract:**
- Specification nodes (S-XXX) with their descriptions
- Outcome nodes (O-XXX) with their goals
- Which specs are implemented by which functions

---

## Process

### Step 1: Load and Parse Data

**1.1 Load brick definitions**
```python
# Read jig/bricks.yaml
# Parse YAML structure
# Group bricks by layer: {0: [bricks...], 1: [bricks...], ...}
# Count total bricks and layers
```

**1.2 Load implementation graph**
```python
# Read jig/generated/implementation-graph.ndjson
# Skip line 1 (metadata)
# Parse each line as JSON
# Collect nodes by type: functions, classes, modules
# Build call graph: {function_id: [called_function_ids]}
```

**1.3 Expand brick units to function assignments**
```python
# For each brick:
#   For each unit in brick.units:
#     If unit is M-module.path:
#       Add all functions starting with F-module.path.
#     If unit is C-class.path:
#       Add all methods starting with F-class.path.
#     If unit is F-function.path:
#       Add exactly this function
# Result: {brick_id: [function_ids]}
```

---

### Step 2: Determine Audit Order

**2.1 Sort bricks by layer**
```python
# Group bricks by layer number
# Sort layers ascending (0, 1, 2, ...)
# Within each layer, sort bricks alphabetically by ID
```

**2.2 Generate audit sequence**
```python
audit_sequence = []
for layer in sorted(layers):
    layer_bricks = get_bricks_at_layer(layer)
    audit_sequence.append({
        "layer": layer,
        "brick_count": len(layer_bricks),
        "bricks": sorted(layer_bricks, key=lambda b: b.id)
    })
```

**Output:** Ordered list of layers, each containing ordered list of bricks to audit

---

### Step 3: Audit Each Layer Sequentially

**For each layer (starting from layer 0):**

#### 3.1 Layer-Level Analysis

**A. Layer Summary**
- Layer number and description
- Brick count in this layer
- Total functions in this layer
- Expected role (what should this layer contain?)
  - Layer 0: Foundation utilities, no internal dependencies
  - Layer 1: Core logic depending only on foundation
  - Layer 2+: Higher-level features building on lower layers

**B. Cross-Brick Dependencies Within Layer**
- For layer 0 ONLY: Identify which bricks depend on other layer 0 bricks
- Check for circular dependencies (ERROR if found)
- For layer 1+: Bricks at same layer should NOT depend on each other (ERROR if found)

**C. Layer Health Metrics**
- Average brick size (functions per brick)
- Cohesion distribution (how many bricks are coherent vs fragmented?)
- External dependency count (how many lower-layer bricks are used?)

---

#### 3.2 Individual Brick Audit

**For each brick in the current layer, perform comprehensive audit:**

**A. Basic Information**
```
Brick ID: B-core-utils
Name: Core Utilities
Layer: 0
Functions: 23
Modules: 2 (jig.utils.io, jig.utils.yaml_utils)
```

**B. Partition Validation** (A001 Contract)

Check the following constraints:

1. **Coverage: All functions assigned?**
   - Are all functions in the brick's units actually present in implementation graph?
   - Report missing functions (units reference non-existent functions)

2. **Uniqueness: No function in multiple bricks?**
   - Check if any functions belong to multiple bricks (VIOLATION)
   - Report duplicate assignments

3. **No class splitting: All methods of a class in same brick?**
   - For each class, verify all methods are in the same brick
   - Report split classes (VIOLATION)

4. **Valid references: All units exist?**
   - Check if units reference nodes that exist in implementation graph
   - Report invalid units (reference nodes that don't exist)

**C. Structural Coherence Analysis**

Calculate and analyze:

1. **Internal cohesion**
   ```
   internal_calls = count of calls between functions within this brick
   external_calls = count of calls from this brick to other bricks
   cohesion = internal_calls / (internal_calls + external_calls)

   Interpretation:
   - cohesion > 0.7: Strong (functions work together)
   - cohesion 0.4-0.7: Moderate (acceptable)
   - cohesion < 0.4: Weak (may need refinement)
   ```

2. **Module concentration**
   ```
   distinct_modules = count of unique module prefixes
   primary_module_percentage = % of functions from most common module

   Interpretation:
   - 1-2 modules: Highly concentrated (good)
   - 3-5 modules: Moderate spread (acceptable)
   - >5 modules: Fragmented (may indicate poor boundary)
   ```

3. **Dependency analysis**
   ```
   - Which bricks does this brick depend on?
   - Are all dependencies in lower layers? (REQUIRED)
   - Are dependencies minimal? (fewer is better)
   - Dependency weight: How many call edges to each dependency?
   ```

**D. Semantic Coherence Analysis**

Examine function names, module paths, and purposes to assess:

1. **Unifying theme**
   - Do functions share a clear responsibility?
   - Can you describe the brick's purpose in 2-5 words?
   - Does the current name match the actual contents?

2. **Outlier detection**
   - Are there functions that seem unrelated to the main theme?
   - List functions that might belong in a different brick

3. **Coherence score**
   - COHERENT (0.7-1.0): Functions clearly share responsibility
   - MODERATE (0.4-0.7): Functions somewhat related, could be refined
   - INCOHERENT (0.0-0.4): Functions don't share clear responsibility

**E. Size Assessment**
```
Function count:
- Too small: <3 functions (may be over-partitioned)
- Appropriate: 3-50 functions (good granularity)
- Too large: >50 functions (may need splitting)
```

**F. Layer Constraint Validation**

For the current brick at layer L:
```python
for dependency_brick in brick_dependencies:
    dep_layer = get_brick_layer(dependency_brick)

    # VALIDATION RULES:
    if L == 0:
        # Layer 0 can depend on other layer 0 bricks (no cycles)
        if dep_layer == 0:
            check_no_cycle(brick, dependency_brick)  # Must be acyclic
        elif dep_layer > 0:
            VIOLATION: Layer 0 cannot depend on higher layers

    else:  # L > 0
        if dep_layer >= L:
            VIOLATION: Layer L can only depend on layers < L
```

Report any violations with:
- Which bricks are involved
- What the actual call is (F ’ F)
- Why it's a violation
- Suggested fixes

---

### Step 4: Identify Quality Issues

Based on the analysis, categorize and document issues:

**1. CRITICAL ISSUES (Block further work)**

- **Layer constraint violations**
  - Brick depends on same-layer or higher-layer brick
  - Example: B-core-utils (L0) ’ B-cli (L2)
  - Impact: Breaks architectural contract
  - Fix: Refactor dependency or adjust layers

- **Circular dependencies**
  - Cycle detected between bricks (even at layer 0)
  - Example: B-utils ” B-models
  - Impact: Impossible to build in order
  - Fix: Break cycle by extracting shared code

- **Partition violations**
  - Function assigned to multiple bricks
  - Class methods split across bricks
  - Impact: Ambiguous ownership
  - Fix: Consolidate assignments

**2. HIGH PRIORITY ISSUES**

- **Incoherent bricks**
  - Coherence score < 0.4
  - Functions don't share clear responsibility
  - Impact: Confusing context boundaries
  - Fix: Split into focused bricks

- **Fragmented bricks**
  - Low cohesion (<0.4)
  - Spans >5 modules
  - Impact: Weak architectural unit
  - Fix: Consolidate or split

- **Missing specifications**
  - Brick functions implement no specs
  - Impact: No intent documentation
  - Fix: Write specs for brick's responsibilities

**3. MEDIUM PRIORITY ISSUES**

- **Size issues**
  - Too small (<3 functions): May be over-partitioned
  - Too large (>50 functions): May need splitting
  - Impact: Granularity mismatch
  - Fix: Merge small bricks or split large ones

- **Naming mismatches**
  - Brick name doesn't reflect actual contents
  - Impact: Misleading documentation
  - Fix: Rename brick

**4. LOW PRIORITY / SUGGESTIONS**

- **Merge candidates**
  - Two bricks with heavy coupling
  - Both are small and related
  - Impact: Unnecessary partition
  - Consider: Merge into single brick

- **Dependency optimization**
  - Brick depends on many bricks (>5)
  - Impact: High coupling
  - Consider: Refactor to reduce dependencies

---

### Step 5: Generate Layer-Ordered Audit Report

**Output Format:** Markdown report

**Location:** `jig/Layer-Ordered-Brick-Audit.md`

---

## Outputs

### Output Format: Markdown Report

**Location:** `jig/Layer-Ordered-Brick-Audit.md`

**Required Sections:**

```markdown
# Layer-Ordered Brick Audit Report

**Date:** [ISO date]
**Brick Definitions:** jig/bricks.yaml
**Implementation Graph:** jig/generated/implementation-graph.ndjson
**Audit Order:** Layer 0 ’ Layer N (bottom-up)

---

## Executive Summary

- **Total Bricks:** [count]
- **Total Layers:** [count] (Layer 0 to Layer N)
- **Total Functions:** [count]
- **Critical Issues:** [count] (layer violations, cycles, partition violations)
- **High Priority Issues:** [count] (incoherence, fragmentation)
- **Medium Priority Issues:** [count] (size, naming)
- **Low Priority Suggestions:** [count] (merges, optimizations)

**Overall Assessment:** [2-3 sentences on system health]

**Audit Completion:** [FULL | PARTIAL - stopped at layer X]

---

## Layer-by-Layer Audit

[For each layer, include full audit section]

---

### Layer 0: Foundation

**Layer Role:** Foundation bricks with no dependencies on higher layers

**Layer Stats:**
- Bricks: [count]
- Functions: [count]
- Average brick size: [count] functions
- Average cohesion: [score]

**Layer Health:** [HEALTHY | CONCERNS | ISSUES]

**Cross-Brick Dependencies (Layer 0 only):**
[Show which layer 0 bricks depend on other layer 0 bricks]
```
B-core-utils ’ [none]
B-data-models ’ B-core-utils
B-validation ’ B-data-models, B-core-utils
```

**Circular Dependencies:** [None | List any cycles - ERROR if present]

---

#### B-core-utils: Core Utilities

**Basic Information:**
- Name: Core Utilities
- Layer: 0 (Foundation)
- Functions: 23
- Modules: 2 (jig.utils.io, jig.utils.yaml_utils)
- Specifications: S-001, S-002, S-003

**Partition Validation:** [ PASS |  FAIL]
-  All functions assigned
-  No duplicate assignments
-  No class splitting
-  All units reference valid nodes

**Structural Metrics:**
- Internal cohesion: 0.82 (STRONG)
- Internal calls: 45
- External calls: 10
- Module concentration: 65% from jig.utils.io
- Dependencies: [none] (layer 0 foundation)

**Semantic Analysis:**
- Coherence: COHERENT (score: 0.85)
- Unifying theme: "File and data utilities"
- Name accuracy: ACCURATE
- Outliers: None detected

**Size Assessment:**  APPROPRIATE (23 functions)

**Layer Constraints:**  VALID (no dependencies)

**Issues:** None detected

**Recommendations:** None (brick is well-defined)

---

[Repeat for each brick in layer 0...]

---

### Layer 1: [Layer Name/Role]

[Same structure as Layer 0, including:]
- Layer stats
- Layer health
- No cross-brick dependencies (layer 1+ should not have same-layer deps)
- Individual brick audits

---

[Continue for all layers...]

---

## Critical Issues Summary

[For each critical issue type found:]

### Layer Constraint Violations

**Count:** [number]

**Details:**

1. **B-core-utils (layer 0) ’ B-cli (layer 2)**
   - Violation: Layer 0 brick depends on layer 2 brick
   - Function call: F-jig.utils.io.read_config ’ F-jig.cli.main.get_args
   - Impact: Foundation depends on interface layer (architectural inversion)
   - Fix: Remove dependency or refactor to pass config as parameter
   - Priority: CRITICAL

[Continue for all violations...]

---

### Circular Dependencies

**Count:** [number]

[If any found, list with details and fix recommendations]

---

### Partition Violations

**Count:** [number]

[If any found, list functions in multiple bricks or split classes]

---

## High Priority Issues Summary

[Similar structure for incoherent bricks, fragmented bricks, etc.]

---

## Medium Priority Issues Summary

[Similar structure for size issues, naming mismatches]

---

## Low Priority Suggestions

[Similar structure for merge candidates, dependency optimization]

---

## Layer Dependency Graph

```
Layer 0 (Foundation):
  B-core-utils [23 functions]
  B-data-models [15 functions] ’ B-core-utils
  B-validation [12 functions] ’ B-data-models, B-core-utils

Layer 1 (Core Logic):
  B-impl-graph [31 functions] ’ B-core-utils, B-data-models
  B-analyzers [18 functions] ’ B-core-utils, B-impl-graph

Layer 2 (Interface):
  B-cli [12 functions] ’ B-core-utils, B-impl-graph, B-validation
```

---

## Recommendations by Priority

### CRITICAL (Fix Immediately)

1. **Fix B-core-utils ’ B-cli dependency** (Layer 0 ’ Layer 2 violation)
   - Current: F-utils.io.read_config calls F-cli.main.get_args
   - Fix: Pass config as parameter instead of fetching from CLI
   - Rationale: Foundation layer cannot depend on interface layer

[Continue for all critical issues...]

### HIGH PRIORITY (Fix Soon)

[List specific, actionable recommendations]

### MEDIUM PRIORITY (Consider)

[List specific recommendations]

### LOW PRIORITY (Optional)

[List suggestions]

---

## Audit Metrics

**Bricks Audited:** [X / Y] ([percentage]%)
**Layers Completed:** [X / Y]
**Issues Found:** [count]
**Recommendations Generated:** [count]

**Audit Duration:** [if tracked]
**Next Audit Recommended:** [date, if relevant]

---

## Appendix A: Brick Function Mapping

[Complete mapping of bricks to functions, organized by layer]

### Layer 0

**B-core-utils:**
```
F-jig.utils.io.read_file
F-jig.utils.io.write_file
F-jig.utils.yaml_utils.load_yaml
[... continue for all functions]
```

[Continue for all bricks...]

---

## Appendix B: Raw Metrics

[Detailed metrics for reference]

**Cohesion by Brick:**
```
B-core-utils: 0.82
B-data-models: 0.75
B-validation: 0.68
[... continue for all bricks]
```

**Size Distribution:**
```
<3 functions: 0 bricks
3-10 functions: 2 bricks (B-validation, B-data-models)
11-30 functions: 3 bricks (B-core-utils, B-impl-graph, B-cli)
31-50 functions: 1 brick (B-analyzers)
>50 functions: 0 bricks
```

---

## Appendix C: Audit Methodology

This audit followed layer-ordered approach:
1. Loaded brick definitions and grouped by layer
2. Loaded implementation graph
3. Expanded brick units to function assignments
4. Audited each layer sequentially (0 ’ N)
5. For each brick: validated partition, analyzed structure, analyzed semantics
6. Identified and categorized quality issues
7. Generated layer-ordered report with recommendations

**Audit Principles:**
- Bottom-up: Foundation issues are highest priority
- Layer-aware: Layer constraints are architectural contracts
- Evidence-based: All claims backed by metrics
- Actionable: Recommendations are specific and implementable
- Read-only: No modifications made, only analysis and recommendations
```

---

## Success Criteria

Your audit is complete and successful when:

- [ ] All brick definitions loaded and grouped by layer
- [ ] Implementation graph loaded and parsed
- [ ] All brick units expanded to function assignments
- [ ] All layers audited in order (0 ’ highest)
- [ ] For each brick:
  - [ ] Partition constraints validated
  - [ ] Structural metrics calculated
  - [ ] Semantic coherence assessed
  - [ ] Layer constraints verified
  - [ ] Quality issues identified
- [ ] All issues categorized by severity (Critical, High, Medium, Low)
- [ ] Markdown report generated with all required sections
- [ ] At least one specific, actionable recommendation for each issue
- [ ] Report saved to `jig/Layer-Ordered-Brick-Audit.md`
- [ ] No modifications made to any files (read-only analysis)

---

## Constraints

### DO NOT:

- **DO NOT modify any files** (this is read-only analysis)
- **DO NOT automatically apply recommendations** (humans must approve all changes)
- **DO NOT suggest changes without evidence** (cite metrics, function calls, specific examples)
- **DO NOT assume current architecture is wrong** (bias towards preserving existing decisions)
- **DO NOT skip layers** (must audit in order: layer 0, then 1, then 2, etc.)
- **DO NOT create generic recommendations** (be specific: exact brick IDs, function IDs, YAML changes)
- **DO NOT continue to next layer if critical issues found** (unless explicitly requested)

### MUST:

- **MUST audit in layer order** (0 ’ 1 ’ 2 ’ ... ’ N)
- **MUST validate layer constraints** (layer L only depends on layers < L)
- **MUST respect A001 contract** (use exact validation rules)
- **MUST expand units correctly** (M- ’ all functions in module, C- ’ all methods, F- ’ one function)
- **MUST calculate metrics accurately** (cohesion, coupling, coherence)
- **MUST provide evidence** (if you say "fragmented," show the metrics)
- **MUST be specific** (exact brick IDs, exact function IDs, exact YAML snippets)
- **MUST categorize by severity** (Critical, High, Medium, Low)

### PREFER:

- **PREFER stopping at first critical issue layer** (fix foundation before auditing higher layers)
- **PREFER quantitative over subjective** (use numbers: "cohesion 0.35" not "seems fragmented")
- **PREFER preserving existing architecture** (high threshold for "needs change")
- **PREFER concrete examples** (show before/after YAML snippets)
- **PREFER incremental fixes** (small adjustments over restructuring)

---

## Examples

### Example 1: Layer 0 Brick (Healthy)

**B-core-utils: Core Utilities**

**Basic Information:**
- Layer: 0 (Foundation)
- Functions: 23
- Modules: 2

**Partition Validation:**  PASS

**Structural Metrics:**
- Cohesion: 0.82 (STRONG)
- Module concentration: 65%
- Dependencies: None

**Semantic Analysis:**
- Coherence: COHERENT (0.85)
- Theme: "File and data utilities"
- Name: ACCURATE

**Layer Constraints:**  VALID (no dependencies)

**Assessment:** Well-defined foundation brick, no changes needed.

---

### Example 2: Layer Constraint Violation (Critical)

**B-core-utils (layer 0) ’ B-cli (layer 2)**

**Issue Type:** CRITICAL - Layer constraint violation

**Details:**
- Current: F-jig.utils.io.read_config calls F-jig.cli.main.get_args
- Violation: Layer 0 (foundation) cannot depend on layer 2 (interface)
- Impact: Architectural inversion

**Fix:**
```python
# Current (BAD):
def read_config():
    args = cli.main.get_args()  # Layer 0 ’ Layer 2 
    return load_yaml(args.config)

# Fixed (GOOD):
def read_config(config_path: str):  # Pass as parameter
    return load_yaml(config_path)
```

**Rationale:** Foundation utilities must not depend on interface layer. Pass data down, not up.

---

### Example 3: Incoherent Brick (High Priority)

**B-misc-utils: Miscellaneous Utilities**

**Structural Metrics:**
- Cohesion: 0.25 (WEAK)
- Module concentration: 20% (FRAGMENTED)
- Functions: 15 across 8 modules

**Semantic Analysis:**
- Coherence: INCOHERENT (0.30)
- Theme: No unifying theme detected
- Outliers: 8 of 15 functions unrelated

**Functions:**
```
F-utils.string.capitalize
F-utils.json.parse
F-utils.network.fetch
F-utils.crypto.hash
F-utils.ui.render_table
[... no clear pattern]
```

**Recommendation:** SPLIT into focused bricks:
```yaml
# Proposed:
- id: B-string-utils
  name: String Utilities
  layer: 0
  units: [M-utils.string]

- id: B-json-utils
  name: JSON Utilities
  layer: 0
  units: [M-utils.json]

- id: B-network-utils
  name: Network Utilities
  layer: 0
  units: [M-utils.network]
```

---

## Edge Cases and Error Handling

### If bricks.yaml is missing:
```
ERROR: Cannot find jig/bricks.yaml
Cannot perform layer-ordered audit without brick definitions.
Please run: jigy brick propose --mode=discover
```

### If implementation graph is missing:
```
ERROR: Cannot find jig/generated/implementation-graph.ndjson
Cannot perform brick audit without implementation graph.
Please run: jigy impl rebuild
```

### If brick has no layer field:
```
ERROR: Brick B-core-utils missing required 'layer' field
All bricks must declare a layer (see AG029).
Please update jig/bricks.yaml to add layer field to all bricks.
```

### If critical issues found in layer 0:
```
WARNING: Critical issues found in Layer 0 (Foundation)
Found: 2 layer violations, 1 circular dependency

Recommendation: Fix Layer 0 issues before auditing higher layers.
Foundation issues cascade upward and make higher-layer analysis unreliable.

Continue to Layer 1 anyway? [y/N]
```

### If brick is empty (0 functions):
```
ISSUE: Orphaned brick
Brick: B-old-utils
Layer: 0
Problem: Brick has 0 functions (all deleted or moved)
Recommendation: DELETE brick from bricks.yaml
```

---

## Testing Your Audit

Before finalizing the report, verify:

1. **Can the report be read independently?**
   - Does it include all necessary context?
   - Can someone unfamiliar with JIG understand the findings?

2. **Are metrics calculated correctly?**
   - Spot-check cohesion calculations
   - Verify function counts match implementation graph
   - Confirm layer assignments are accurate

3. **Are recommendations actionable?**
   - Can someone implement the fix without guessing?
   - Is the rationale clear enough to make a decision?
   - Are YAML snippets provided where relevant?

4. **Is severity categorization appropriate?**
   - Critical: Architectural contract violations (layer violations, cycles)
   - High: Quality issues affecting maintainability (incoherence, fragmentation)
   - Medium: Naming and sizing issues
   - Low: Optimization opportunities

5. **Is the assessment fair?**
   - Are you respecting existing human decisions?
   - Are you providing evidence for all claims?
   - Are you suggesting improvements, not demanding them?

---

## Notes

- This is an **analysis task**, not an implementation task. You are producing a report, not changing code.
- The report should be **informative and educational**, helping humans understand their brick structure layer by layer.
- **Layer order is mandatory**. Audit layer 0 completely before moving to layer 1.
- If you find critical issues in a layer, **consider stopping** and recommending fixes before auditing higher layers.
- If the architecture is excellent, say so! Not every audit must find problems.
- Your goal is **decision support**, not decisions. Humans review and approve all changes.

---

**The Golden Rule:** Every recommendation must be specific, justified, and actionable. Layer order matters - fix the foundation before building higher.
