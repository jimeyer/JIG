---
id: O-029
title: Automated Validation Repair
type: outcome
theme: [Validation]
goals: [G-003, G-004]
specifications: [S-104, S-105, S-106, S-107, S-108, S-109]
---

# Automated Validation Repair

**Value:** Validation errors include machine-readable repair instructions, enabling automated or agent-assisted fixing of common issues.

**Acceptance:** Running `jigy validate -j` produces JSON output where each error includes a `fix` field with structured repair instructions. Running `jigy mend --auto` applies fixes marked as auto-fixable.

## AI Agent Benefit

Agents can fix validation errors programmatically without parsing human-readable error messages. The validate-mend cycle enables agents to iterate on artifacts until they pass validation, reducing context loss from repeated human intervention.

## Rationale

Validation errors often have mechanical fixes: missing required fields can be set to defaults, malformed IDs can be normalized, and mismatched filenames can be renamed. Today, these fixes require manual intervention - either human editing or agents parsing error messages and inferring repairs.

Machine-readable fix templates eliminate this ambiguity. Each validation error declares exactly what repair would resolve it. Some repairs are safe to apply automatically (e.g., normalizing ID case); others require human judgment (e.g., choosing between two conflicting values).

The mend command consumes these fix templates, applying safe fixes automatically and reporting which fixes require human decision. This creates a validate-then-mend workflow that converges to valid artifacts.

## Success Criteria

The validation repair system must:
1. Output JSON with `fix` field for each validation error
2. Provide `jigy mend --auto` to apply all auto-fixable errors
3. Provide `jigy mend --apply fixes.json` to apply explicit fixes
4. Iterate until no new auto-fixable errors appear (max 3 iterations)
5. Report which fixes require human judgment
6. Preserve YAML formatting where possible during repairs

## Specified By

This outcome is delivered through:
- **S-104**: Validation Fix Template Output - JSON output with fix templates
- **S-105**: Mend Command Auto Mode - automatic repair of safe fixes
- **S-106**: Mend Command Apply Mode - explicit fix application
- **S-107**: Mend Fixed Point Iteration - convergence to valid state
- **S-108**: Validation Error ID Stability - deterministic error identification
- **S-109**: Rule Spec Traceability - errors linked to specifications

## Constitution Linkage

This outcome serves: **Part III: Validation** - Actionable Errors
Enables: Automated repair, agent autonomy, reduced human intervention
Without this: Agents must parse error messages; fixes require human editing
