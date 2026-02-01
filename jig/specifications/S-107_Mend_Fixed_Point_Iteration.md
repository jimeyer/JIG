---
id: S-107
title: Mend Fixed Point Iteration
type: specification
outcomes: [O-029]
architecture: [A-004]
---

# Mend Fixed Point Iteration

The mend command iterates applying fixes until no new auto-fixable errors appear, with a maximum of 3 iterations.

**Acceptance Criteria**:
- After applying fixes, mend re-runs validation to detect any new errors
- If new auto-fixable errors appear, mend applies them (next iteration)
- Iteration continues until validation produces no new auto-fixable errors (fixed point)
- Maximum 3 iterations to prevent infinite loops from conflicting rules
- Reports "Converged after N iterations" on successful fixed point
- Reports "Did not converge after 3 iterations" if maximum reached
- Exit code 0 on convergence, 1 on non-convergence (remaining errors), 2 on error
- The `--no-iterate` flag disables iteration (single pass only)

**Rationale**: Some fixes create new validation errors (e.g., adding a reference field that needs its own validation). Iteration resolves cascading repairs automatically. The 3-iteration limit bounds worst-case behavior when rules conflict.

**Example**:
```
$ jigy mend --auto
Iteration 1: Applied 5 fixes
Iteration 2: Applied 2 fixes (newly detected)
Iteration 3: Applied 0 fixes
Converged after 3 iterations.
```
