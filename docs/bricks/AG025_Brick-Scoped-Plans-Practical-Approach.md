# AG025: Brick-Scoped Plans - Practical Approach

**How to Constrain Agent Work to Brick Boundaries Using Current Tools**

**Date:** 2025-11-26
**Status:** Proposal
**Depends On:** AG006 (Brick Context Enforcement), J016 (JIG v8), taskPlan.md v2.0
**Audience:** Human developers using Claude Code with JIG

---

## Problem Statement

When an AI agent (Claude Code) executes a PLAN, it has unrestricted access to the entire codebase. This creates risks:

1. **Accidental coupling**: Agent may import from modules outside the intended scope
2. **Context overload**: Agent reads irrelevant code, degrading response quality
3. **Unclear boundaries**: Hard to predict what the agent might touch
4. **Review overhead**: Changes could be scattered across architectural boundaries
5. **Architecture decay**: No enforcement of brick boundaries over time

**Goal**: Constrain agent work to explicit Brick boundaries using only current Claude Code capabilities (no custom tooling, no wishful features).

---

## Core Insight: Social Contracts Work

From AG006, we know the practical approach today is:

```
┌─────────────────────────────────────┐
│  1. Declare Boundaries Explicitly   │  ← PLAN document
│     (what files can be touched)     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  2. Instruct Agent Clearly          │  ← Prompt engineering
│     (boundary rules in context)     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  3. Validate Compliance             │  ← Manual git diff check
│     (human verifies boundaries)     │
└─────────────────────────────────────┘
```

This is **good enough** if done consistently. We don't need runtime enforcement to get value.

---

## Proposed Changes to PLAN Structure

### Current PLAN Template (from taskPlan.md v2.0)

```markdown
# PLAN: <Feature Name>

- **SCOPE**: <link>
- **Start**: <YYYY-MM-DD>
- **Status**: Draft | In-Progress | Complete
- **Branch**: <git-branch-name>

## Known Intent (Created Before Coding)
...

## Work Unit Checklist
...

## Work Units
...
```

### Proposed: Add Brick Scope Section

```markdown
# PLAN: <Feature Name>

- **SCOPE**: <link>
- **Start**: <YYYY-MM-DD>
- **Status**: Draft | In-Progress | Complete
- **Branch**: <git-branch-name>

## Brick Scope (IMPORTANT - READ FIRST)

**Primary Brick**: B-001 (Graph Core)

**Allowed Files** (you MAY read/edit these):

src/jig/core/graph.py
src/jig/core/relationships.py
tests/unit/test_graph.py
tests/unit/test_graph_queries.py
tests/unit/test_relationships.py
jig/outcomes/O-001.md
jig/outcomes/O-002.md
jig/specifications/S-001.md
jig/specifications/S-002.md
jig/specifications/S-003.md


**Forbidden Files** (you MUST NOT touch):

src/jig/cli/*          # CLI brick
src/jig/decompose/*    # Analysis brick
src/jig/core/parser.py # Parser brick
tests/integration/*    # Integration tests


**Dependency Interfaces** (you may CALL, but not READ implementation):

From BRICK-UTILS:
  - read_file(path: Path) -> str
  - write_file(path: Path, content: str) -> None
  - load_yaml(path: Path) -> dict

From BRICK-PARSER:
  - parse_ostc_node(path: Path) -> OSTCNode
  - OSTCNode (dataclass - see type stub below)


**Boundary Rules**:
1. ✅ You MAY read/edit any file in "Allowed Files"
2. ✅ You MAY call functions from "Dependency Interfaces"
3. ❌ You MUST NOT read implementation files of other bricks
4. ❌ You MUST NOT use Glob/Grep across entire codebase
5. ❌ You MUST NOT import from modules not in dependency list
6. ⚠️ If you need something outside this brick, STOP and ask the human

**Validation**: Before marking PLAN complete, human will run:
```bash
git diff --name-only <branch> | grep -v -E "^(src/jig/core/|tests/unit/test_graph|jig/outcomes/|jig/specifications/)"
# Should return empty (no files outside brick scope)
```

---

## Known Intent (Created Before Coding)
...


---

## Key Design Elements

### 1. Explicit File Allowlist

**Why**: Claude Code respects clear boundaries when explicitly stated.

**Format**: Plain text file paths (easy to parse visually)

**Coverage**:
- Source files in this brick
- Test files for this brick
- Intent nodes (O/S) this brick implements
- Dependency type signatures (interface only)

**Maintenance**: Human maintains this list when creating PLAN.

### 2. Dependency Interfaces (Type Stubs)

Instead of agent reading dependency implementation, provide type signatures:

```markdown
**Dependency Interfaces**:

### BRICK-UTILS (Foundation utilities)

```python
# Type signatures only - DO NOT read implementation

def read_file(path: Path) -> str:
    """Read file contents as string.

    Args:
        path: Absolute path to file

    Returns:
        File contents as string

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file not readable
    """
    ...

def load_yaml(path: Path) -> dict[str, Any]:
    """Load YAML file as dictionary.

    Args:
        path: Path to YAML file

    Returns:
        Parsed YAML as dict

    Raises:
        yaml.YAMLError: If invalid YAML
    """
    ...
```

### BRICK-PARSER (Intent parsing)

```python
@dataclass
class OSTCNode:
    """Parsed intent node (Outcome, Specification, or Constraint)."""
    id: str
    type: Literal["outcome", "specification", "constraint"]
    title: str
    body: str
    metadata: dict[str, Any]

def parse_ostc_node(path: Path) -> OSTCNode:
    """Parse OSTC markdown file with YAML frontmatter.

    Args:
        path: Path to .md file in jig/outcomes/ or jig/specifications/

    Returns:
        Parsed node

    Raises:
        ValueError: If invalid format
    """
    ...
```
```

**Benefit**: Agent knows what's available without reading implementation, reducing context size and preventing coupling.

### 3. Boundary Validation (Manual, Scripted)

**Simple validation script** (doesn't require JIG tooling):

```bash
#!/bin/bash
# validate-brick-boundaries.sh

BRANCH=${1:-HEAD}
BRICK_FILES_PATTERN=${2:-"^(src/jig/core/graph|tests/unit/test_graph|jig/outcomes/|jig/specifications/)"}

echo "Validating brick boundaries for branch: $BRANCH"
echo "Allowed pattern: $BRICK_FILES_PATTERN"
echo ""

# Get all modified files
MODIFIED=$(git diff --name-only main.."$BRANCH")

# Filter out allowed files
VIOLATIONS=$(echo "$MODIFIED" | grep -v -E "$BRICK_FILES_PATTERN" || true)

if [ -z "$VIOLATIONS" ]; then
  echo "✅ All changes within brick boundaries"
  echo ""
  echo "Modified files:"
  echo "$MODIFIED" | sed 's/^/  ✓ /'
  exit 0
else
  echo "❌ Files modified outside brick boundaries:"
  echo "$VIOLATIONS" | sed 's/^/  ✗ /'
  echo ""
  echo "Allowed files:"
  echo "$MODIFIED" | grep -E "$BRICK_FILES_PATTERN" | sed 's/^/  ✓ /' || echo "  (none)"
  exit 1
fi
```

**Usage**:
```bash
# In PLAN completion checklist
./scripts/validate-brick-boundaries.sh <branch> "<pattern>"
```

**No JIG tooling required** - just git and grep.

---

## Updated Work Unit Template

Each Work Unit should reinforce brick boundaries:

```markdown
### Work Unit N: <Title>

**Goal**: <Single, testable goal>

**Brick Scope**: B-001 (Graph Core)

**Files to Modify** (must be in allowed list):
- `src/jig/core/graph.py` - Add caching layer
- `tests/unit/test_graph.py` - Add cache tests

**Dependencies Used**:
- `BRICK-UTILS.read_file()` - Load cached data
- `BRICK-PARSER.OSTCNode` - Type hint for graph nodes

**Acceptance Criteria**:
- [ ] Specification S-003 is implemented
- [ ] Tests verify caching behavior
- [ ] All changes within `src/jig/core/graph.py` and `tests/unit/test_graph.py`
- [ ] No new imports from outside declared dependencies
- [ ] `jigy status` shows alignment for S-003

**Boundary Check** (run before committing):
```bash
git diff --name-only | grep -v -E "^(src/jig/core/graph|tests/unit/test_graph)"
# Should return empty
```
```

---

## Workflow Integration

### Before Starting PLAN

**Step 1: Human creates PLAN with Brick Scope**

```bash
# Determine which brick(s) this work affects
# For JIG v8: Look at jig/bricks.yaml to find brick containing the code

# Create PLAN with Brick Scope section
vim docs/plans/PLAN-graph-caching.md

# Fill in:
# - Primary Brick: B-001
# - Allowed Files: (list from brick definition)
# - Dependency Interfaces: (type stubs from dependencies)
# - Boundary Rules: (standard rules)
```

**Step 2: Agent reads PLAN**

```
You: @docs/plans/PLAN-graph-caching.md

You: Please read the PLAN carefully, especially the "Brick Scope" section.
You are constrained to work ONLY within the files listed in "Allowed Files".
Do NOT read or edit any files outside that list.
Do NOT use Glob or Grep across the entire codebase.

Start with Work Unit 0 (Create Intent).

Agent: I've read the PLAN. I understand I'm working within B-001 (Graph Core)
boundaries. I can only modify files in src/jig/core/ and tests/unit/test_graph*.
I'll start by creating the intent nodes...
```

### During Work

**Agent behavior**:
- ✅ Reads `src/jig/core/graph.py` (in allowed list)
- ✅ Reads `tests/unit/test_graph.py` (in allowed list)
- ✅ Uses `read_file()` from BRICK-UTILS (dependency interface)
- ❌ Tries to read `src/jig/cli/main.py` → **Human stops**: "That file is outside the brick boundary. Use only files in the allowed list."
- ❌ Tries `Glob("src/**/*.py")` → **Human stops**: "No global searches. Stay within brick scope."

**Human monitoring**:
- Watch for Read/Edit tool calls outside allowed files
- Remind agent of boundaries if violated
- If agent repeatedly violates, restart session with clearer instructions

### After Work Unit

**Validation checklist** (in Work Unit Reflect section):

```markdown
**Boundary Compliance**:
- [ ] Ran: `git diff --name-only | grep -v -E "^(src/jig/core/graph|tests/unit/test_graph)"`
- [ ] Result: Empty (no violations)
- [ ] All imports from declared dependencies only
- [ ] No new cross-brick coupling introduced
```

### After PLAN Complete

**Final validation**:

```bash
# Check all changes in branch respect brick boundaries
./scripts/validate-brick-boundaries.sh minimal-jig "^(src/jig/core/graph|tests/unit/test_graph|jig/outcomes/|jig/specifications/)"

# Check imports
grep -r "^from jig\." src/jig/core/graph.py | grep -v "jig.utils" | grep -v "jig.core.parser"
# Should be empty (only allowed dependencies)

# Mark in PLAN Completion Summary
echo "✅ Brick boundary validation passed"
```

---

## Handling Common Scenarios

### Scenario 1: Agent Needs Something From Another Brick

**Agent**: "I need to parse OSTC nodes. Should I read `src/jig/core/parser.py`?"

**Human**: "No, that's in BRICK-PARSER. Use the interface: `parse_ostc_node(path)` which is in your dependency list. You don't need to read the implementation."

**Agent**: "Got it. I'll call `parse_ostc_node()` using the type signature from the dependency interfaces."

### Scenario 2: Agent Wants to Create New File

**Agent**: "I want to create `src/jig/core/graph_cache.py` for the caching logic."

**Human**: "Is that file in the allowed list?"

**Agent**: "No, it's not listed."

**Human**: "Let me check if it belongs in this brick... Yes, B-001 includes all of `src/jig/core/` except parser. I'll add it to the allowed list. Proceed."

**Action**: Update PLAN "Allowed Files" section, commit PLAN change, continue.

### Scenario 3: Work Spans Multiple Bricks

**Human decision point**: "This feature requires changes to both BRICK-GRAPH and BRICK-CLI."

**Option A: Sequential PLANs** (Recommended)
```
PLAN-graph-caching-1.md
  Brick Scope: B-001 (Graph Core)
  Work Units: Add caching to graph.py

PLAN-graph-caching-2.md
  Brick Scope: B-003 (CLI)
  Work Units: Add --cache flag to CLI
  Dependencies: Uses new caching from B-001
```

**Option B: Multi-Brick PLAN** (Use sparingly)
```markdown
## Brick Scope

**Primary Bricks**: B-001 (Graph Core), B-003 (CLI)

**Allowed Files B-001**:
- src/jig/core/graph.py
- tests/unit/test_graph.py

**Allowed Files B-003**:
- src/jig/cli/main.py
- tests/cli/test_main.py

**Cross-Brick Rules**:
- Changes to B-001 must complete and pass tests before touching B-003
- B-003 can import from B-001's public interface only
- Validate each brick separately
```

**Recommendation**: Prefer sequential PLANs (clearer boundaries, easier validation).

### Scenario 4: Agent Violates Boundary Repeatedly

**Pattern**: Agent keeps trying to read files outside scope despite reminders.

**Action**:
1. Stop the session
2. Restart with clearer, more explicit instructions
3. Copy-paste the "Boundary Rules" section into the initial prompt
4. Add a reminder: "I will check every Read/Edit operation against the allowed list. If you access a forbidden file, I will stop the session."

**Prevention**: More explicit allowed/forbidden lists, shorter work units, more frequent validation.

---

## Design Questions for Decision

### Q1: Single-Brick vs Multi-Brick PLANs?

**Option A: Enforce single brick per PLAN**
- ✅ Simpler validation
- ✅ Clearer boundaries
- ✅ Easier to reason about
- ❌ Requires multiple PLANs for cross-brick features

**Option B: Allow multi-brick PLANs with explicit scoping**
- ✅ Can handle cross-brick work in one PLAN
- ✅ More flexible
- ❌ More complex validation
- ❌ Higher risk of boundary violations

**Recommendation Needed**: Which approach should be default?

**Suggested Answer**: Start with single-brick as default, allow multi-brick with justification.

---

### Q2: How to Handle Dependency Interfaces?

**Option A: Manual type stubs in PLAN**
- Human writes type signatures in PLAN document
- ✅ Self-contained (PLAN has all context)
- ❌ Maintenance burden (update when interfaces change)
- ❌ Risk of drift

**Option B: Reference separate interface files**
- Create `interfaces/BRICK-UTILS.interface.py` with stubs
- PLAN references these files
- ✅ Single source of truth
- ✅ Can be validated against actual implementation
- ❌ Requires additional files

**Option C: Just list function names**
- PLAN lists available functions, agent uses IDE/docs for signatures
- ✅ Minimal maintenance
- ❌ Agent might read implementation to find signatures

**Recommendation Needed**: Which approach balances maintainability and clarity?

**Suggested Answer**: Start with Option A (manual stubs in PLAN), migrate to Option B if maintenance becomes burden.

---

### Q3: Validation - When and How?

**When to validate?**
- After each Work Unit? (frequent, catches early)
- After entire PLAN? (infrequent, might catch violations late)
- On git commit (via pre-commit hook)?

**How to validate?**
- Manual git diff inspection? (simple, no tooling)
- Scripted validation? (automated, requires script maintenance)
- JIG tooling? (requires building `jigy brick validate`)

**Recommendation Needed**: What's the minimum viable validation?

**Suggested Answer**:
- After each Work Unit: Manual git diff check (list in Work Unit template)
- After PLAN complete: Scripted validation (simple bash script)
- Future: JIG tooling when available

---

### Q4: New Files - Which Brick Do They Belong To?

**Scenario**: Agent creates `src/jig/core/graph_cache.py`. Which brick?

**Option A: Path-based rules**
- File path determines brick (`src/jig/core/` → B-001)
- ✅ Clear, automatic
- ❌ Assumes directory structure matches bricks

**Option B: Explicit declaration**
- Human must approve new files and declare brick membership
- ✅ Intentional, prevents accidental misplacement
- ❌ Friction in workflow

**Option C: Agent declares, human validates**
- Agent proposes: "Creating graph_cache.py in B-001"
- Human approves or corrects
- ✅ Collaborative
- ⚠️ Requires human in loop

**Recommendation Needed**: How should new files be assigned to bricks?

**Suggested Answer**: Option C (agent declares, human validates). Add to PLAN template:

```markdown
**New Files Created** (declare brick membership):
- src/jig/core/graph_cache.py → B-001 (Graph Core)
  Rationale: Caching logic for graph operations
```

---

### Q5: Escape Hatches - When to Allow Boundary Violations?

**Legitimate reasons to violate**:
1. Architectural refactoring (moving functions between bricks)
2. Emergency bug fixes (need to touch multiple bricks)
3. Brick boundary redesign (redefining what belongs where)
4. Test infrastructure (integration tests across bricks)

**Options**:
- **Strict**: Never allow, always use multi-brick PLAN
- **Pragmatic**: Allow with explicit justification in PLAN
- **Permissive**: Boundaries are suggestions, not rules

**Recommendation Needed**: How strict should enforcement be?

**Suggested Answer**: Pragmatic. Add to PLAN template:

```markdown
## Boundary Exceptions (if any)

**Exception**: Need to modify `src/jig/cli/main.py` (BRICK-CLI) to fix import

**Justification**: Bug in current code imports wrong module, quick fix required

**Validation**: Will run separate validation for each affected brick

**Files Outside Primary Brick**:
- src/jig/cli/main.py (lines 42-44 only)
```

---

### Q6: How to Communicate Brick Boundaries to Agent?

**Current approach**: Markdown section in PLAN document

**Alternatives**:
- Separate file referenced by PLAN
- Code comments at top of each file
- Git commit message conventions
- Pre-commit hook output

**Recommendation Needed**: Is PLAN document sufficient, or additional mechanisms?

**Suggested Answer**: PLAN document is sufficient for v1. Reinforce with:
- Header comment in each source file: `# Brick: B-001 (Graph Core)`
- Reminder in agent's first message: "Read the Brick Scope section carefully"

---

## Minimal Viable Implementation

### What We Need to Start Using This Today

**1. PLAN Template Update**

File: `agents/taskPlan.md`

Add Brick Scope section to template (done in earlier task).

**2. Example PLAN with Brick Scope**

File: `docs/plans/PLAN-example-brick-scoped.md`

Create a concrete example showing all elements.

**3. Validation Script**

File: `scripts/validate-brick-boundaries.sh`

Simple bash script (shown above).

**4. Brick Definition File**

File: `jig/bricks.yaml` (already exists per JIG v8)

Ensure it lists files for each brick:

```yaml
bricks:
  - id: B-001
    name: Graph Core
    units:
      - M-jig.core.graph
      - M-jig.core.relationships
    files:  # NEW - explicit file list
      source:
        - src/jig/core/graph.py
        - src/jig/core/relationships.py
      test:
        - tests/unit/test_graph.py
        - tests/unit/test_relationships.py
```

**5. Dependency Interface Stubs**

File: `docs/bricks/interfaces/BRICK-UTILS.interface.md`

Document public interfaces for reference:

```markdown
# BRICK-UTILS Public Interface

## Functions

### read_file
```python
def read_file(path: Path) -> str:
    """Read file contents as string."""
    ...
```

### write_file
```python
def write_file(path: Path, content: str) -> None:
    """Write string content to file."""
    ...
```
```

---

## Success Metrics

How do we know this is working?

**Qualitative**:
- Agent stays within boundaries without repeated reminders
- Fewer cross-brick imports accidentally added
- Code reviews focus on logic, not "why did you touch that file?"
- Clearer PRs (all changes in one brick)

**Quantitative**:
- % of PLANs that pass brick validation on first try
- Number of boundary violations caught in review
- Lines of code per PLAN (should decrease - smaller scope)
- Time to complete PLAN (should decrease - less context)

**Target (3 months)**:
- 90% of PLANs pass validation
- <5% boundary violations in review
- Average PLAN size: 200-300 LOC (down from 500+)

---

## Rollout Plan

### Phase 1: Pilot (1 PLAN)

**Goal**: Validate approach with one brick-scoped PLAN

**Actions**:
1. Choose simple, isolated brick (BRICK-UTILS?)
2. Create PLAN with full Brick Scope section
3. Execute with Claude Code, monitor boundary compliance
4. Document: What worked? What didn't? Where did agent struggle?

**Success**: Complete PLAN with zero boundary violations

---

### Phase 2: Standardize (All New PLANs)

**Goal**: Make brick-scoped PLANs the default

**Actions**:
1. Update `agents/taskPlan.md` template
2. Create 3-5 examples for different scenarios
3. Add validation script to repo
4. Train team on approach

**Success**: All new PLANs use Brick Scope section, 80% pass validation

---

### Phase 3: Retrospective (After 10 PLANs)

**Goal**: Refine approach based on real usage

**Actions**:
1. Review all PLANs for boundary violations
2. Identify patterns (which boundaries violated most?)
3. Update template based on learnings
4. Decide on tooling investment (build `jigy brick validate`?)

**Success**: Process feels natural, violations rare, ready to scale

---

## Open Questions Summary

1. **Single vs Multi-Brick PLANs**: Should we enforce one brick per PLAN, or allow multiple with explicit scoping?

2. **Dependency Interfaces**: Manual stubs in PLAN, separate interface files, or just function names?

3. **Validation Frequency**: After each Work Unit, after PLAN, or on commit?

4. **New File Assignment**: Path-based, explicit declaration, or agent-proposes/human-validates?

5. **Escape Hatches**: How strict? Never allow violations, pragmatic exceptions, or suggestions-only?

6. **Communication**: Is PLAN document sufficient, or additional mechanisms needed?

7. **Brick Granularity**: Should bricks be as small as possible (one module), or larger (related modules)?

8. **Test Files**: Should test files be in same brick as implementation, or separate TEST bricks?

9. **Interface Stability**: How to version brick interfaces? When can we change them?

10. **Tooling Investment**: When should we build `jigy brick load` and `jigy brick validate`?

---

## Recommendations

### Immediate (This Week)

1. ✅ Answer design questions (Q1-Q6)
2. ✅ Update `agents/taskPlan.md` with Brick Scope section
3. ✅ Create example PLAN with brick scope
4. ✅ Write validation script (`scripts/validate-brick-boundaries.sh`)
5. ✅ Try with one PLAN (pilot)

### Short-term (This Month)

1. Standardize on approach after pilot
2. Create interface stubs for top 3 most-used bricks
3. Update `jig/bricks.yaml` to include file lists
4. Document lessons learned
5. Use for all new PLANs

### Long-term (Next Quarter)

1. Build `jigy brick load` (generates context file)
2. Build `jigy brick validate` (automated validation)
3. Add brick metrics to `jigy status`
4. Consider requesting native brick support from Claude Code team
5. Publish pattern for other teams

---

## Conclusion

**We can enforce brick boundaries today** using:
- Explicit allowed/forbidden file lists in PLAN documents
- Clear boundary rules and dependency interfaces
- Agent instruction via prompt (social contract)
- Simple validation scripts (git diff)
- Human monitoring during work

**This doesn't require**:
- Custom Claude Code features
- Complex JIG tooling
- Runtime enforcement
- Sophisticated analysis

**The key**: Make boundaries **explicit, visible, and validated**. Trust the agent to follow clear instructions, validate compliance, and refine based on learnings.

**Next step**: Answer the design questions and run the pilot.

---

## Appendix A: Example Brick-Scoped PLAN Snippet

```markdown
# PLAN: Add Graph Traversal Caching

- **SCOPE**: Improve graph query performance by adding caching layer
- **Start**: 2025-11-26
- **Status**: Draft
- **Branch**: graph-caching

## Brick Scope (IMPORTANT - READ FIRST)

**Primary Brick**: B-001 (Graph Core)

**Allowed Files** (you MAY read/edit):
```
src/jig/core/graph.py
src/jig/core/relationships.py
tests/unit/test_graph.py
tests/unit/test_graph_traversal.py
jig/specifications/S-003.md  (new - will create)
```

**Forbidden Files** (you MUST NOT touch):
```
src/jig/cli/*
src/jig/decompose/*
src/jig/core/parser.py
src/jig/utils/*
tests/integration/*
```

**Dependency Interfaces** (you may CALL, not READ):

From BRICK-UTILS (src/jig/utils/):
```python
def read_file(path: Path) -> str: ...
def write_file(path: Path, content: str) -> None: ...
```

**Boundary Rules**:
1. ✅ Read/edit only files in allowed list
2. ✅ Call dependency functions (use type signatures above)
3. ❌ Do NOT read implementation of BRICK-UTILS or BRICK-PARSER
4. ❌ Do NOT use `Glob("**/*.py")` or `Grep` across entire repo
5. ⚠️ If you need something outside this list, STOP and ask

**Validation**:
```bash
# Run before marking any Work Unit complete
git diff --name-only | grep -v -E "^(src/jig/core/|tests/unit/test_graph|jig/specifications/)"
# Expected: empty output (no files outside scope)
```

---

## Known Intent
...
```

---

## Appendix B: Validation Script

```bash
#!/bin/bash
# scripts/validate-brick-boundaries.sh
#
# Usage: ./validate-brick-boundaries.sh <branch> "<allowed-pattern>"
# Example: ./validate-brick-boundaries.sh feature-123 "^(src/jig/core/|tests/unit/test_graph)"

set -euo pipefail

BRANCH="${1:-HEAD}"
ALLOWED_PATTERN="${2:-}"

if [ -z "$ALLOWED_PATTERN" ]; then
  echo "Usage: $0 <branch> \"<allowed-pattern>\""
  echo "Example: $0 my-branch \"^(src/jig/core/|tests/unit/)\""
  exit 1
fi

echo "========================================"
echo "Brick Boundary Validation"
echo "========================================"
echo "Branch: $BRANCH"
echo "Allowed pattern: $ALLOWED_PATTERN"
echo ""

# Get modified files compared to main
MODIFIED=$(git diff --name-only main.."$BRANCH" 2>/dev/null || git diff --name-only "$BRANCH" 2>/dev/null || true)

if [ -z "$MODIFIED" ]; then
  echo "⚠️  No modified files found"
  exit 0
fi

# Filter to find violations
VIOLATIONS=$(echo "$MODIFIED" | grep -v -E "$ALLOWED_PATTERN" || true)

if [ -z "$VIOLATIONS" ]; then
  echo "✅ All changes within brick boundaries"
  echo ""
  echo "Modified files ($( echo "$MODIFIED" | wc -l | xargs )):"
  echo "$MODIFIED" | sed 's/^/  ✓ /'
  echo ""
  exit 0
else
  echo "❌ Boundary violations detected!"
  echo ""
  echo "Files outside allowed pattern:"
  echo "$VIOLATIONS" | sed 's/^/  ✗ /'
  echo ""

  ALLOWED=$(echo "$MODIFIED" | grep -E "$ALLOWED_PATTERN" || true)
  if [ -n "$ALLOWED" ]; then
    echo "Files within boundaries:"
    echo "$ALLOWED" | sed 's/^/  ✓ /'
    echo ""
  fi

  echo "Allowed pattern: $ALLOWED_PATTERN"
  echo ""
  echo "To fix: Only modify files matching the pattern, or update brick scope."
  exit 1
fi
```

**Make executable**:
```bash
chmod +x scripts/validate-brick-boundaries.sh
```

---

**Status**: Ready for review and decision on design questions
**Next**: Answer Q1-Q10, update taskPlan.md, run pilot PLAN
