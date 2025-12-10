# Jigy Test Directory Discovery Issue

## Problem

`jigy rebuild verify` finds 0 nodes because the test directory discovery is hardcoded to look for `tests/` (plural), but this project uses `test/` (singular).

**Location:** `jig-stable/src/jig/verification_graph/discovery.py:69-73`

```python
if test_dir is None:
    test_dir = project_root / "tests"

if not test_dir.exists():
    return []
```

## Impact

- Verification graph is empty
- `jigy align` reports 0 verified specs
- T→S traceability is broken

## Suggested Fix

Add a `jig.yaml` config file at project root with customizable paths:

```yaml
# jig.yaml
paths:
  test_dir: test        # default: tests
  source_dir: src       # default: src
  specs_dir: jig/specifications
  outcomes_dir: jig/outcomes
```

The discovery code would then:
1. Check for `jig.yaml` in project root
2. Use configured `test_dir` if present
3. Fall back to `tests/` default

## Workaround

Until jigy supports config, options are:
1. Symlink: `ln -s test tests`
2. Rename directory: `mv test tests` (requires updating imports)
3. Patch jigy locally
