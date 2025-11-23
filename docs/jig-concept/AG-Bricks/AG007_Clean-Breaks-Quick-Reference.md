# Clean Breaks - Quick Reference

**One-page guide for making breaking changes across Brick boundaries**

---

## The Philosophy

**Development Mode (pre-1.0):**
- ✅ Break things
- ✅ Fail everywhere immediately
- ✅ Fix all at once
- ❌ No compatibility layers
- ❌ No feature flags
- ❌ No "just in case" code

**Bricks help because they show EXACTLY what breaks.**

---

## Quick Workflow

### 1. Decide
```markdown
# In Delta file
#DECISION "Burn ships: change Graph.load_from_dir signature"
Rationale: Need access to full config
Affected Bricks: GRAPH, CLI, INDEX
```

### 2. Break
```python
# Delete old signature completely
def load_from_dir(config: JigConfig) -> Graph:  # ← New signature
    if not isinstance(config, JigConfig):
        raise TypeError(  # ← Fail loudly
            "load_from_dir requires JigConfig. "
            "Old Path signature removed."
        )
```

### 3. Validate (shows what broke)
```bash
$ jigy brick validate BRICK-GRAPH --check-dependents

❌ BRICK-CLI (3 call sites broken)
   - cli/status.py:42
   - cli/index.py:67
   - cli/validate.py:28

❌ BRICK-INDEX (1 call site broken)
   - core/index_builder.py:234
```

### 4. Fix All
```python
# Update every call site shown by validation
graph = Graph.load_from_dir(config)  # ← Updated
```

### 5. Validate Clean
```bash
$ jigy brick validate --all
✓ All Bricks valid
✓ System health: Excellent
```

### 6. Commit
```bash
$ git commit -m "refactor(graph)!: clean break to config-based loading

BREAKING CHANGE: Graph.load_from_dir now requires JigConfig

All consumers updated simultaneously.
Validation: jigy brick validate --all ✓"
```

---

## Commands

```bash
# See what depends on a Brick
jigy brick validate BRICK-X --check-dependents

# Validate entire system
jigy brick validate --all

# Show Brick consumers
jigy brick show BRICK-X --dependents

# Cross-Brick refactoring mode
jigy brick refactor start --bricks BRICK-A,BRICK-B
jigy brick refactor validate
jigy brick refactor complete
```

---

## Do's and Don'ts

### ✅ DO

```python
# Delete old signature completely
def new_function(new_param: NewType) -> Result:
    if not isinstance(new_param, NewType):
        raise TypeError("Old signature removed. Use NewType.")
    return implementation()
```

### ❌ DON'T

```python
# Don't create compatibility shims
def function(old_or_new: OldType | NewType) -> Result:
    if isinstance(old_or_new, OldType):
        warnings.warn("Old type deprecated")  # ← NO!
        new = convert(old_or_new)
    else:
        new = old_or_new
    return implementation(new)
```

---

## Integration with taskCleanBreak

Bricks **enhance** clean breaks:

| taskCleanBreak Says | Bricks Add |
|---------------------|------------|
| Delete old code completely | ✅ Know what to delete (Brick boundaries) |
| Fail loudly with errors | ✅ Validation shows ALL failures |
| Fix everything at once | ✅ Validation lists every call site |
| No "just in case" code | ✅ Detected by validation |
| Document decision | ✅ Delta + commit message |

---

## Example: Change Interface

**Before:**
```python
# BRICK-GRAPH interface
def load_from_dir(intent_dir: Path) -> Graph: ...
```

**After:**
```python
# BRICK-GRAPH interface (v2.0.0)
def load_from_dir(config: JigConfig) -> Graph:
    if not isinstance(config, JigConfig):
        raise TypeError(
            "load_from_dir requires JigConfig. "
            "Old signature (Path) removed in v2.0.0."
        )
    return _load(config)
```

**Consumers update:**
```python
# All call sites (shown by validation)
config = load_config()
graph = Graph.load_from_dir(config)  # ← Updated
```

**No intermediate step. No dual implementation. Clean.**

---

## When to Use

**Use Clean Breaks when:**
- ✅ Pre-1.0 (active development)
- ✅ Single developer or tight team
- ✅ Can change entire codebase
- ✅ Want to iterate fast

**Use Compatibility when:**
- ✅ Post-1.0 (stable release)
- ✅ External users
- ✅ Multiple teams
- ✅ Can't coordinate changes

**JIG is currently in Development Mode → Use Clean Breaks.**

---

## Validation Output Example

```bash
$ jigy brick validate --all

Validating All Bricks (Development Mode)
=========================================

✓ BRICK-UTILS: No changes
✓ BRICK-CONFIG: No changes
✓ BRICK-PARSER: No changes
✓ BRICK-VALIDATOR: No changes
✓ BRICK-GRAPH: Interface changed (v2.0.0)
    Breaking change: load_from_dir signature
✓ BRICK-SCANNER: No changes
✓ BRICK-ANNOT-VALIDATOR: No changes
✓ BRICK-INDEX: Updated for BRICK-GRAPH v2.0.0
✓ BRICK-DECOMPOSE: No changes
✓ BRICK-CLI: Updated for BRICK-GRAPH v2.0.0

Cross-Brick Dependencies:
-------------------------
✓ All call sites updated
✓ No breaking changes pending
✓ All Brick interfaces consistent

System Health: Excellent (100/100)
```

---

## Commit Format

Use conventional commits with breaking change marker:

```
refactor(scope)!: brief description

BREAKING CHANGE: Detailed description

Before: old signature/behavior
After: new signature/behavior

Rationale: why this change

Affected Bricks:
  - BRICK-X v2.0.0 (interface change)
  - BRICK-Y (updated consumer)
  - BRICK-Z (updated consumer)

Migration: how consumers updated
Validation: jigy brick validate --all ✓
```

---

## Key Insight

**Bricks make clean breaks SAFER because:**
1. Boundaries are explicit (know what to change)
2. Dependencies are tracked (know what depends)
3. Validation shows impact (know what broke)
4. Fixes are complete (know when done)

**You can break confidently.**

---

**Full guide:** `AG007_Clean-Breaks-And-Cross-Brick-Refactoring.md`
