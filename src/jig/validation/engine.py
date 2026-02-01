# ABOUTME: Validation engine that runs all rules and produces JSON output with fix templates.
# ABOUTME: Implements S-104 (fix templates), S-108 (error IDs), S-109 (spec traceability).
"""
Validation engine using the rules-based architecture.

Provides:
- validate(): Run all rules and return structured results with fix templates
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import jig
from jig.rules.base import compute_error_id
from jig.rules.context import ValidationContext
from jig.rules.registry import RULES


@jig.implements("S-104")
def validate(project_root: Path) -> dict[str, Any]:
    """Run all validation rules and return structured results.

    Args:
        project_root: Path to the project root directory.

    Returns:
        Dictionary with 'errors' list and 'summary' object per S-104.
        Each error has: id, message, file, line, spec, fix
        Summary has: total, auto_fixable, manual
    """
    ctx = ValidationContext(project_root=project_root)
    errors: list[dict[str, Any]] = []

    for rule in RULES:
        violations = rule.violations(ctx)
        for v in violations:
            # Compute stable error ID per S-108
            error_id = compute_error_id(v.rule_code, v.artifact_id, v.context)

            # Get fix template per S-104
            fix = rule.fix_for(v)
            fix_dict: dict[str, Any]
            if fix:
                fix_dict = fix.to_dict()
            else:
                # No fix available - create a manual placeholder
                fix_dict = {
                    "action": "manual_review",
                    "target": v.file,
                    "params": {},
                    "auto": False,
                    "suggestions": ["Manual review required"],
                }

            error = {
                "id": error_id,
                "message": v.message,
                "file": v.file,
                "line": v.line,
                "spec": rule.spec,
                "fix": fix_dict,
            }
            errors.append(error)

    # Build summary
    auto_count = sum(1 for e in errors if e["fix"]["auto"])
    manual_count = sum(1 for e in errors if not e["fix"]["auto"])
    summary = {
        "total": len(errors),
        "auto_fixable": auto_count,
        "manual": manual_count,
    }

    # Build counts for artifact types
    counts = {
        "specs": len(ctx.specifications),
        "outcomes": len(ctx.outcomes),
        "architectures": len(ctx.architectures),
        "bricks": len(ctx.bricks),
    }

    return {
        "errors": errors,
        "summary": summary,
        "counts": counts,
    }
