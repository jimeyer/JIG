# taskBurnShips: Clean Break Protocol

**Purpose:** Execute clean breaks from old implementations to new ones with zero technical debt.

**Philosophy:** This is a reference implementation. Pristine code > backwards compatibility.

---

## Core Principles

### 1. Complete Deletion
- Delete all old code paths completely—no feature flags, no fallbacks, no commented code
- Remove old tests entirely and write new ones from scratch for the new implementation
- No `# TODO: remove old implementation` comments—if you're burning ships, burn them now

### 2. Fail Loudly
- Fail loudly with clear errors for any unhandled cases—never fail silently or return defaults
- If something doesn't work yet, throw an error explaining what's missing
- Example: `raise NotImplementedError("X feature requires Y subsystem (not yet implemented)")`

### 3. Full Commitment
- Commit fully to the new approach—we're burning the ships
- No "just in case" preservation of old code
- If you need to reference old logic, check git history

---

## JIG-Specific Instructions

### When Refactoring JIG Components

**1. Update Intent Graph First**
- If changing subsystem boundaries, update `jig/specifications/` files first
- Document the architectural decision in a Delta (PLAN or NOTES)
- Use `#DECISION` marker to capture why you're burning the ships

**2. Maintain OSTC Alignment**
- When deleting code with `@jig` annotations, update graph-index.yaml
- Remove orphaned Test (T) and Code (C) node references
- Run `jig validate` after deletion to catch broken references

**3. Clean Subsystem Boundaries**
- If removing a subsystem export, ensure no external dependencies remain
- Update `allowed_dependencies` in jig.toml if dependency graph changes
- Maintain coupling ratio >10:1 (internal:external edges)

**4. Delta Documentation**
```markdown
# In your active Delta (e.g., PLAN_refactor_X.md)

#DECISION "Burn ships: removing old parser implementation"
**Choice:** Complete rewrite using ripgrep instead of Python regex
**Rationale:** 10x performance gain, simpler code
**Tradeoffs:** Breaking change, no backwards compatibility
**Migration:** Users re-run `jig extract` (fast operation)

#LEARNED "Clean breaks reduce cognitive load"
Maintaining dual implementations added 40% code complexity.
Deleting old path freed us to optimize new implementation.
```

**5. Test Migration Strategy**
```bash
# Don't just delete tests—replace them

# 1. Delete old test file
rm tests/unit/test_old_parser.py

# 2. Write new tests from scratch
# In tests/unit/test_new_extractor.py
# @jig T-JIG-042 verifies:S-JIG-015 subsystem:core
def test_ripgrep_extraction_speed():
    """New extractor must process 1000 files in <1s"""
    # Test the new way, not backwards compatibility
```

**6. Update Harvest Reports**
- When archiving a Delta that burned ships, note it in the Completion Summary
- Helps future you understand why the old approach doesn't exist
```markdown
### Harvest Preparation (JIG)
**Architectural Changes:**
- Burned ships: Removed old Python regex parser (committed to ripgrep)
- Breaking change: Marker syntax simplified (removed verbose YAML blocks)
- Migration: Zero-cost for users (deterministic re-extraction)
```

---

## Execution Checklist

When executing a burn-ships refactor:

- [ ] Document decision in active Delta with `#DECISION` marker
- [ ] Delete old code completely (no commented blocks)
- [ ] Delete old tests completely
- [ ] Write new tests from scratch
- [ ] Remove old `@jig` annotations from deleted code
- [ ] Update `jig/graph-index.yaml` if needed
- [ ] Run `jig validate --check-all` to catch broken references
- [ ] Update `jig/specifications/` if subsystem contract changed
- [ ] Add errors for unimplemented features (fail loudly)
- [ ] Commit with clear message: `refactor(subsystem): burn ships - <reason>`
- [ ] Update Delta reflection with `#LEARNED` about what you gained

---

## Anti-Patterns to Avoid

**❌ Don't:**
```python
# Feature flag hell
if USE_NEW_PARSER:
    return new_parser.parse(content)
else:
    return old_parser.parse(content)  # "just in case"
```

**✅ Do:**
```python
# Clean break with clear errors
def parse(content: str) -> ParseResult:
    """Parse using ripgrep-based extractor (v2).

    Raises:
        NotImplementedError: If legacy YAML markers detected
    """
    result = ripgrep_extract(content)

    if has_legacy_yaml_markers(content):
        raise NotImplementedError(
            "Legacy YAML markers no longer supported. "
            "Use inline markers: #DISCOVERY \"text\""
        )

    return result
```

---

## Rationale: Why Burn Ships?

**For JIG specifically:**
- JIG is a reference implementation demonstrating nearly decomposable architecture
- Technical debt obscures the architectural lessons
- Clean subsystem boundaries require clean code
- This is a tool for building better software—it should be an example

**General benefits:**
- Simpler mental model (one way to do things)
- Faster iteration (no compatibility constraints)
- Better testing (test what actually runs, not what might run)
- Clearer git history (commits show real direction, not hedging)

---

**TL;DR:** Delete old code. Write new code. Fail loudly. Document the decision. Move forward.