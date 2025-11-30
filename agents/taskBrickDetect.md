# Task: Brick Partition Analysis and Validation

**Version:** 1.0
**Date:** 2025-11-30
**References:** AG028 (Brick Detection Workflow), J016 (JIG Concept v8), A001 (Core Artifacts Contract)

---

## Objective

Analyze the current brick partition in `jig/bricks.yaml` against the implementation graph to validate architectural coherence, identify quality issues, and recommend improvements that respect existing human decisions while detecting drift and misalignment.

---

## Context

### What is JIG?
JIG is an alignment measurement system that tracks the relationship between intent (specifications), implementation (functions), and verification (tests). The system partitions functions into "bricks" - architectural units that represent clear boundaries and responsibilities.

### What are Bricks?
From J016: "A Brick is a partition of the function space F." Bricks divide all functions in a codebase into named sets where:
- Every function belongs to exactly one brick (no overlaps, no gaps)
- Bricks represent coherent architectural units
- Bricks have clear responsibilities and boundaries

### Why This Task Matters
Brick partitions can drift as code evolves:
- New functions added (may not fit existing bricks)
- Functions moved or deleted (leaving orphaned bricks)
- Natural clusters emerge that suggest better boundaries
- Human adjustments may have been made for good reasons

This analysis validates the current partition and identifies opportunities for improvement WITHOUT automatically changing anything (humans must approve architectural decisions).

### Key Principle
**Respect existing brick definitions.** If a human has manually adjusted bricks, we bias towards preserving their decisions unless there's strong evidence of misalignment.

---

## Inputs

### 1. Implementation Graph
**Location:** `/Users/jamesmeyer/Code/jig/jig/generated/implementation-graph.ndjson`

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
  - `id`: Function identifier (format: `F-module.path.function_name`)
  - `type`: Node type (`"function"`, `"class"`, or `"module"`)
  - `file`: Relative path to source file
  - `implements`: Array of specification IDs (may be empty `[]`)
  - `calls`: Array of function IDs this function calls (may be empty `[]`)

- **Class nodes:**
  ```json
  {"id":"C-jig.impl_graph.graph.Graph","type":"class","file":"src/jig/impl_graph/graph.py","implements":["S-003"]}
  ```

- **Module nodes:**
  ```json
  {"id":"M-jig.cli.main","type":"module","file":"src/jig/cli/main.py"}
  ```

- **Edges:** Represent relationships (contains, implements, imports)
  ```json
  {"source":"C-jig.impl_graph.graph.Graph","target":"F-jig.impl_graph.graph.Graph.__init__","type":"contains"}
  {"source":"F-jig.cli.main.rebuild","target":"S-001","type":"implements"}
  ```

**What to extract:**
- All function nodes (type === "function")
- All module nodes (type === "module")
- All class nodes (type === "class")
- Call relationships (nodes with non-empty `calls` arrays)
- Implementation relationships (nodes with non-empty `implements` arrays)

### 2. Brick Definitions
**Location:** `/Users/jamesmeyer/Code/jig/jig/bricks.yaml`

**Format:** YAML

**Structure:**
```yaml
bricks:
  - id: B-001
    name: JIG Core Decorators
    units:
      - M-jig.__init__

  - id: B-002
    name: CLI Interface
    units:
      - M-jig.cli.main
```

**Schema:**
- `id`: Brick identifier (format: `B-NNN` where NNN is a number)
- `name`: Human-readable brick name
- `units`: Array of node references (M-, C-, or F- prefixes)
  - `M-module.path` expands to all functions in that module
  - `C-class.path` expands to all methods of that class
  - `F-function.path` references exactly one function

**What to extract:**
- List of all bricks (id, name, units)
- Mapping of functions to bricks (by expanding units)

---

## Process

### Step 1: Load and Parse Data

1. **Load implementation graph**
   - Read `jig/generated/implementation-graph.ndjson`
   - Skip line 1 (metadata)
   - Parse each line as JSON
   - Collect all nodes by type:
     - `functions = [all nodes where type === "function"]`
     - `classes = [all nodes where type === "class"]`
     - `modules = [all nodes where type === "module"]`
   - Build call graph: `{function_id: [list of function_ids it calls]}`
   - Count total functions

2. **Load brick definitions**
   - Read `jig/bricks.yaml`
   - Parse YAML structure
   - For each brick, extract: id, name, units
   - Count total bricks

3. **Expand brick units to function assignments**
   For each brick, expand units to actual function IDs:
   - If unit is `M-module.path`:
     - Find all function nodes where `id` starts with `F-module.path.`
     - Add these functions to brick's function list
   - If unit is `C-class.path`:
     - Find all function nodes where `id` starts with `F-class.path.`
     - Add these functions to brick's function list
   - If unit is `F-function.path`:
     - Add exactly this function ID to brick's function list

   Result: `brick_assignments = {function_id: brick_id}` mapping

---

### Step 2: Validate Partition Constraints (from A001)

Check the following constraints from the Core Artifacts Contract:

1. **Coverage: All functions assigned?**
   - For each function in implementation graph:
     - Is it assigned to at least one brick?
   - Report: `unassigned_functions = [functions with no brick assignment]`

2. **Uniqueness: No function in multiple bricks?**
   - For each function in implementation graph:
     - Is it assigned to exactly one brick?
   - Report: `duplicate_assignments = {function_id: [list of bricks it appears in]}`

3. **No class splitting: All methods of a class in same brick?**
   - For each class in implementation graph:
     - Find all methods (functions where `id` starts with `F-class.path.`)
     - Check if all methods belong to same brick
   - Report: `split_classes = {class_id: {method: brick_id}}`

4. **Valid references: All units exist in implementation graph?**
   - For each unit in bricks.yaml:
     - Does the referenced node exist in implementation graph?
   - Report: `invalid_units = {brick_id: [units that don't exist]}`

**Success criteria for this step:**
- ✓ All functions assigned (unassigned_functions is empty)
- ✓ No duplicates (duplicate_assignments is empty)
- ✓ No split classes (split_classes is empty)
- ✓ All units valid (invalid_units is empty)

---

### Step 3: Analyze Brick Coherence

For each brick, analyze whether its functions form a coherent architectural unit:

1. **Extract brick information**
   - Brick ID and name
   - List of all functions in brick (from expansion)
   - Count of functions
   - Module paths represented (extract module prefix from function IDs)
   - Specifications implemented (collect all unique spec IDs from `implements` arrays)

2. **Analyze structural coherence**

   **Internal cohesion:**
   - Count internal calls: calls between functions within the same brick
   - Count external calls: calls from this brick's functions to other bricks
   - Calculate: `cohesion = internal_calls / (internal_calls + external_calls)`
   - Interpretation:
     - cohesion > 0.7: Strong cohesion (functions work together)
     - cohesion 0.4-0.7: Moderate cohesion (acceptable)
     - cohesion < 0.4: Weak cohesion (may need refinement)

   **Module concentration:**
   - How many distinct modules are represented?
   - What percentage of functions come from the top module?
   - Interpretation:
     - 1-2 modules: Highly concentrated (good)
     - 3-5 modules: Moderate spread (acceptable)
     - >5 modules: Fragmented (may indicate poor boundary)

3. **Analyze semantic coherence**

   For each brick, examine the function names, module paths, and docstrings to answer:

   **Question 1: Do these functions share a clear responsibility?**
   - Look at function names: Do they suggest a common purpose?
   - Look at module paths: Are they from related modules?
   - Look at implemented specs: Are they related to a common outcome?

   **Question 2: What is the unifying theme?**
   - Suggest a concise description (2-5 words) of what this brick does
   - Compare to the brick's current name
   - Does the current name accurately reflect the contents?

   **Question 3: Are there outliers?**
   - Do any functions seem unrelated to the main theme?
   - List functions that might belong elsewhere

   **Coherence assessment:**
   - **COHERENT** (score 0.7-1.0): Functions clearly share a responsibility
   - **MODERATE** (score 0.4-0.7): Functions somewhat related, could be refined
   - **INCOHERENT** (score 0.0-0.4): Functions don't share clear responsibility, consider splitting

4. **Analyze brick size**
   - Too small: <3 functions (may be over-partitioned)
   - Appropriate: 3-50 functions (good granularity)
   - Too large: >50 functions (may need splitting)

---

### Step 4: Identify Quality Issues

Based on the analysis, identify specific issues:

1. **Orphaned bricks**
   - Brick has 0 functions (all functions deleted or moved)
   - **Recommendation:** DELETE brick

2. **Fragmented bricks**
   - Brick has low cohesion (<0.4)
   - Brick spans >5 modules
   - Functions don't share clear responsibility
   - **Recommendation:** SPLIT brick into multiple bricks

3. **Missing bricks**
   - Functions exist but aren't assigned to any brick
   - **Recommendation:** CREATE new brick for unassigned functions

4. **Merge candidates**
   - Two bricks with heavy coupling (many calls between them)
   - Two bricks with similar themes
   - Two bricks that are very small (<3 functions each)
   - **Recommendation:** MERGE bricks

5. **Naming mismatches**
   - Brick name doesn't match actual contents
   - **Recommendation:** RENAME brick

6. **Class splitting violations**
   - Methods of a class spread across multiple bricks
   - **Recommendation:** Move all methods to one brick

7. **Invalid references**
   - Brick units reference nodes that don't exist
   - **Recommendation:** Remove invalid units

---

### Step 5: Analyze Brick Dependencies

For each pair of bricks (B₁, B₂), calculate:

1. **Call count:** How many times do functions in B₁ call functions in B₂?
2. **Dependency strength:**
   - Light: 1-5 calls
   - Moderate: 6-20 calls
   - Heavy: >20 calls

3. **Detect dependency issues:**
   - **Circular dependencies:** B₁ → B₂ and B₂ → B₁
   - **Unexpected dependencies:** Dependencies that seem architecturally wrong

4. **Build dependency graph:**
   ```
   B-001 (3 functions)
     └→ B-003 (5 calls)
     └→ B-004 (2 calls)

   B-002 (12 functions)
     └→ B-003 (15 calls)

   B-003 (19 functions)
     └→ B-004 (8 calls)

   B-004 (51 functions)
     [no dependencies]
   ```

---

## Outputs

### Output Format: Markdown Report

**Location:** `docs/wip/B003_ANALYSIS-Brick-Validation-Report.md`

**Required Sections:**

```markdown
# Brick Partition Validation Report

**Date:** [ISO date]
**Implementation Graph:** jig/generated/implementation-graph.ndjson
**Brick Definitions:** jig/bricks.yaml

---

## Executive Summary

- **Total Functions:** [count]
- **Total Bricks:** [count]
- **Partition Quality:** [VALID | INVALID]
- **Issues Found:** [count]
- **Recommendations:** [count]

**Overall Assessment:** [1-2 sentences summarizing health of brick partition]

---

## Partition Validation (A001 Contract)

### Coverage
- ✓ All functions assigned: [YES/NO]
- Functions assigned: [X / Y] ([percentage]%)
- Unassigned functions: [count]

[If unassigned functions exist, list them]

### Uniqueness
- ✓ No duplicate assignments: [YES/NO]
- Duplicate assignments: [count]

[If duplicates exist, list them]

### No Class Splitting
- ✓ All classes intact: [YES/NO]
- Split classes: [count]

[If split classes exist, list them]

### Valid References
- ✓ All units reference valid nodes: [YES/NO]
- Invalid units: [count]

[If invalid units exist, list them]

---

## Brick Analysis

[For each brick, include:]

### B-XXX: [Brick Name]

**Size:** [count] functions
**Modules:** [count] distinct modules
**Specifications:** [list of spec IDs]

**Structural Metrics:**
- Internal cohesion: [score] ([STRONG/MODERATE/WEAK])
- Internal calls: [count]
- External calls: [count]
- Module concentration: [percentage]% from primary module

**Semantic Analysis:**
- Coherence: [COHERENT/MODERATE/INCOHERENT] (score: [0.0-1.0])
- Unifying theme: [description]
- Name accuracy: [ACCURATE/NEEDS UPDATE]

**Functions:** ([count] total)
[List first 10 functions, then "... and X more"]

**Outliers:** [List functions that seem misplaced, if any]

**Dependencies:**
- Depends on: [list of brick IDs with call counts]

**Issues:** [List any quality issues detected]

**Recommendations:** [List specific recommendations]

---

## Quality Issues Summary

[For each issue type found:]

### [Issue Type]

**Count:** [number of occurrences]

**Details:**
1. [Specific instance with context]
2. [Specific instance with context]
...

**Recommendation:** [What to do about these issues]

---

## Brick Dependency Graph

[Text representation of dependency relationships]

```
B-001: [Brick Name]
  ├→ B-003 ([count] calls)
  └→ B-004 ([count] calls)

B-002: [Brick Name]
  └→ B-003 ([count] calls)

...
```

**Circular Dependencies:** [List any cycles, or "None detected"]

**Architectural Concerns:** [List any unexpected dependencies]

---

## Recommendations

[Prioritized list of recommended actions]

### High Priority
1. [Specific actionable recommendation with justification]
2. [Specific actionable recommendation with justification]

### Medium Priority
1. [Specific actionable recommendation with justification]
2. [Specific actionable recommendation with justification]

### Low Priority / Optional
1. [Specific actionable recommendation with justification]
2. [Specific actionable recommendation with justification]

---

## Proposed Changes

[For each recommended change, provide specific YAML updates]

### Example: Create new brick for unassigned functions

**Current state:**
- 3 functions unassigned

**Proposed `bricks.yaml` addition:**
```yaml
  - id: B-005
    name: [Suggested Name]
    units:
      - F-module.path.function1
      - F-module.path.function2
      - F-module.path.function3
```

**Rationale:** [Why this change makes sense]

---

## Appendix: Raw Data

### Function to Brick Mapping
[Complete mapping, formatted for readability]

### Brick Expansion
[Show how each unit expands to function lists]

### Call Graph Statistics
- Total call edges: [count]
- Internal calls (within bricks): [count] ([percentage]%)
- External calls (between bricks): [count] ([percentage]%)
```

---

## Success Criteria

Your analysis is complete and successful when:

- [ ] Implementation graph loaded successfully (all function nodes extracted)
- [ ] Brick definitions loaded successfully (all units parsed)
- [ ] All partition constraints validated (coverage, uniqueness, no class splitting, valid references)
- [ ] All bricks analyzed (cohesion, coherence, size, dependencies)
- [ ] All quality issues identified and categorized
- [ ] Dependency graph constructed (showing brick relationships)
- [ ] Markdown report generated with all required sections
- [ ] At least one specific, actionable recommendation provided for each issue found
- [ ] Report saved to `docs/wip/B003_ANALYSIS-Brick-Validation-Report.md`

---

## Constraints

### DO NOT:
- **Do NOT modify any files** (this is read-only analysis)
- **Do NOT automatically apply recommendations** (humans must approve architectural changes)
- **Do NOT suggest changes without clear justification** (explain WHY each recommendation makes sense)
- **Do NOT assume current bricks are wrong** (bias towards preserving existing human decisions)
- **Do NOT create generic recommendations** (be specific: "Move F-utils.json.parse from B-003 to B-001")

### MUST:
- **MUST respect the A001 contract** (use exact validation rules from that document)
- **MUST expand units correctly** (M- → all functions in module, C- → all methods, F- → one function)
- **MUST calculate metrics accurately** (cohesion, coupling, coverage)
- **MUST provide evidence for claims** (if you say "fragmented," show the metrics)
- **MUST be specific in recommendations** (exact brick IDs, exact function IDs, exact YAML changes)

### PREFER:
- **PREFER preserving existing bricks** (threshold for "needs change" should be high)
- **PREFER incremental changes** (small adjustments over complete restructuring)
- **PREFER concrete examples** (show before/after YAML snippets)
- **PREFER quantitative metrics** (numbers over subjective judgments)

---

## Examples

### Example: Coherent Brick

**B-001: JIG Core Decorators**
- Functions: 3
- Modules: 1 (jig.__init__)
- Cohesion: 0.0 (no internal calls, but that's expected for a pure API)
- Module concentration: 100%
- Semantic coherence: COHERENT (score: 0.95)
  - All functions are decorator implementations
  - Clear theme: "Public API for JIG annotations"
  - Name is accurate
- Assessment: ✓ Well-defined brick, no changes needed

### Example: Fragmented Brick

**B-004: Language Analyzers**
- Functions: 51
- Modules: 4 (base, registry, python, python_visitor)
- Cohesion: 0.45 (moderate)
- Module concentration: 60% from python module
- Semantic coherence: MODERATE (score: 0.65)
  - Theme: "Language analysis and AST parsing"
  - Outliers: None detected
  - Size concern: 51 functions is large
- Assessment: ~ Consider splitting into:
  - B-004a: Analyzer Framework (base, registry)
  - B-004b: Python Analyzer (python, python_visitor)

### Example: Unassigned Functions

**Issue:** 3 functions not assigned to any brick

```
F-utils.json.parse
F-utils.json.dump
F-utils.json.validate
```

**Analysis:**
- All in utils.json module
- Semantically coherent (JSON utilities)
- No existing brick covers JSON utilities

**Recommendation:** CREATE new brick

```yaml
  - id: B-005
    name: JSON Utilities
    units:
      - M-utils.json
```

---

## Edge Cases and Error Handling

### If implementation graph is missing:
```
ERROR: Cannot find jig/generated/implementation-graph.ndjson
Please run: jigy impl rebuild
```

### If bricks.yaml is missing:
```
WARNING: No brick definitions found (jig/bricks.yaml missing)
This appears to be a cold start. Analysis will show all functions as unassigned.
Recommendations will focus on creating initial brick partition.
```

### If implementation graph is empty (0 functions):
```
ERROR: Implementation graph contains no functions
Cannot perform brick analysis on empty codebase.
```

### If a brick unit references a module that doesn't exist:
```
ISSUE: Invalid unit reference
Brick: B-003
Unit: M-utils.deprecated
Problem: No module 'utils.deprecated' found in implementation graph
Recommendation: Remove this unit from B-003
```

### If a function is assigned to multiple bricks:
```
VIOLATION: Function assigned to multiple bricks
Function: F-utils.io.read_file
Bricks: B-003, B-005
Problem: Violates partition constraint (each function exactly one brick)
Recommendation: Remove from one of these bricks
```

---

## Testing Your Analysis

Before submitting the report, verify:

1. **Can the report be read independently?**
   - Does it include all necessary context?
   - Can someone unfamiliar with JIG understand the findings?

2. **Are all metrics calculated correctly?**
   - Spot-check cohesion calculations
   - Verify function counts match implementation graph
   - Confirm coverage percentages add up

3. **Are recommendations actionable?**
   - Can someone copy-paste the proposed YAML?
   - Is the rationale clear enough to make a decision?

4. **Is the assessment fair?**
   - Are you respecting existing human decisions?
   - Are you providing evidence for claims?
   - Are you suggesting improvements, not demanding them?

---

## Notes

- This is an **analysis task**, not an implementation task. You are producing a report, not changing code.
- The report should be **informative and educational**, helping humans understand their brick structure.
- If you find the current partition is excellent, say so! Not every analysis must find problems.
- Your goal is to provide **decision support**, not to make decisions. Humans will review and approve any changes.

---

**The Golden Rule:** Every recommendation must be specific, justified, and actionable. "Consider refactoring B-003" is not enough. "Split B-003 into two bricks: (1) Core Graph (graph.py, builder.py) and (2) I/O (ndjson_writer.py) because cohesion is low (0.38) and these represent distinct concerns" is what we need.
