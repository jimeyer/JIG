# ABOUTME: Validation query layer — filtering and scoped validation dispatch.
# ABOUTME: Extracts filter logic and spec sets from cli/validate.py for reuse.

"""Query layer for validation filtering (S-023, S-024, S-025).

Provides:
- filter_errors_by_specs(): Filter validation results to specific spec IDs
- query_validate(): Run validation with scope filtering (full/intent/bricks)
- INTENT_SPECS / BRICK_SPECS: Canonical spec ID sets for each scope
"""

from typing import Any

from jig.validation.engine import validate

# Canonical spec ID sets for validation scopes
INTENT_SPECS = {"S-018", "S-019", "S-020", "S-042", "S-043", "S-072", "S-079", "S-095"}
BRICK_SPECS = {"S-021", "S-022", "S-035", "S-036", "S-037", "S-038", "S-039", "S-086", "S-087", "S-088", "S-089"}


def filter_errors_by_specs(result: dict[str, Any], spec_ids: set[str]) -> dict[str, Any]:
    """Filter validation result to only include errors for specific specs.

    Args:
        result: Engine result with 'errors' and 'summary'.
        spec_ids: Set of spec IDs to include.

    Returns:
        Filtered result with only matching errors and recalculated summary.
    """
    filtered_errors = [e for e in result.get("errors", []) if e.get("spec", "") in spec_ids]

    return {
        "errors": filtered_errors,
        "summary": {
            "total": len(filtered_errors),
            "auto_fixable": sum(1 for e in filtered_errors if e.get("fix", {}).get("auto", False)),
            "manual": sum(1 for e in filtered_errors if not e.get("fix", {}).get("auto", False)),
        },
    }


def query_validate(config: Any, scope: str = "full") -> dict[str, Any]:
    """Run validation with optional scope filtering.

    Args:
        config: JIG configuration (duck-typed, needs .project_root).
        scope: "full" (no filtering), "intent" (INTENT_SPECS), or "bricks" (BRICK_SPECS).

    Returns:
        Validation result dict, possibly filtered by scope.
    """
    result = validate(config.project_root)

    if scope == "intent":
        return filter_errors_by_specs(result, INTENT_SPECS)
    elif scope == "bricks":
        return filter_errors_by_specs(result, BRICK_SPECS)
    else:
        return result
