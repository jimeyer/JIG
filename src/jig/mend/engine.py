# ABOUTME: Mend engine for applying validation fixes to JIG artifacts.
# ABOUTME: Implements S-105 (auto), S-106 (apply), S-107 (fixed point iteration).
"""
Mend engine for applying validation fixes.

Provides:
- mend_auto: Apply all auto-fixable errors
- mend_apply: Apply explicit fixes from JSON file
- mend_combined: Combine --auto and --apply modes
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jig
from jig.mend.actions import (
    apply_add_field_value,
    apply_delete_field,
    apply_remove_field_value,
    apply_rename_file,
    apply_set_field,
    apply_set_h1,
    apply_sync_title,
)
from jig.validation.engine import validate

# Maximum iterations to prevent infinite loops (per S-107)
MAX_ITERATIONS = 3


def _apply_fix(project_root: Path, fix: dict[str, Any]) -> bool:
    """Apply a single fix action.

    Args:
        project_root: Project root directory.
        fix: Fix dictionary with action, target, params.

    Returns:
        True if fix was applied successfully, False otherwise.
    """
    action = fix.get("action")
    target = fix.get("target", "")
    params = fix.get("params", {})

    # Resolve target path
    target_path = Path(target)
    if not target_path.is_absolute():
        target_path = project_root / target

    try:
        if action == "set_field":
            apply_set_field(target_path, params.get("field", ""), params.get("value"))
            return True
        elif action == "add_field_value":
            apply_add_field_value(
                target_path, params.get("field", ""), params.get("value")
            )
            return True
        elif action == "remove_field_value":
            apply_remove_field_value(
                target_path, params.get("field", ""), params.get("value")
            )
            return True
        elif action == "delete_field":
            apply_delete_field(target_path, params.get("field", ""))
            return True
        elif action == "rename_file":
            new_path = Path(params.get("new_path", ""))
            if not new_path.is_absolute():
                new_path = project_root / new_path
            apply_rename_file(target_path, new_path)
            return True
        elif action == "sync_title":
            apply_sync_title(target_path, params.get("direction", "to_h1"))
            return True
        elif action == "set_h1":
            apply_set_h1(target_path, params.get("heading", ""))
            return True
        elif action == "manual_review":
            # Manual review cannot be applied automatically
            return False
        else:
            # Unknown action
            return False
    except Exception:
        return False


@jig.implements("S-105", "S-107")
def mend_auto(
    project_root: Path, *, dry_run: bool = False, iterate: bool = True
) -> dict[str, Any]:
    """Apply all auto-fixable validation errors.

    Runs validation, collects errors with auto: true fixes, and applies them.
    Iterates until no new auto-fixable errors appear (fixed point), up to
    MAX_ITERATIONS.

    Args:
        project_root: Path to project root.
        dry_run: If True, show changes without modifying files.
        iterate: If True (default), iterate until fixed point. If False, single pass.

    Returns:
        Dictionary with:
        - applied: Count of applied fixes
        - skipped: Count of skipped (manual) fixes
        - iterations: Number of iterations performed
        - converged: Whether fixed point was reached
        - details: List of applied fix details
    """
    max_iters = MAX_ITERATIONS if iterate else 1
    total_applied = 0
    total_skipped = 0
    all_details: list[dict[str, Any]] = []
    converged = False

    for iteration in range(1, max_iters + 1):
        # Run validation
        result = validate(project_root)
        errors = result.get("errors", [])

        # Separate auto and manual fixes
        auto_fixes = [e for e in errors if e.get("fix", {}).get("auto", False)]
        manual_fixes = [e for e in errors if not e.get("fix", {}).get("auto", False)]

        if iteration == 1:
            total_skipped = len(manual_fixes)

        if not auto_fixes:
            # No more auto-fixable errors - we've reached fixed point
            converged = True
            break

        applied_this_iter = 0
        for error in auto_fixes:
            fix = error.get("fix", {})
            detail = {
                "error_id": error.get("id"),
                "file": error.get("file"),
                "action": fix.get("action"),
                "iteration": iteration,
            }

            if dry_run:
                detail["status"] = "would_apply"
                all_details.append(detail)
            else:
                if _apply_fix(project_root, fix):
                    detail["status"] = "applied"
                    applied_this_iter += 1
                else:
                    detail["status"] = "failed"
                all_details.append(detail)

        total_applied += applied_this_iter

        if dry_run:
            # In dry-run, don't iterate since nothing changes
            break

    return {
        "applied": total_applied,
        "skipped": total_skipped,
        "iterations": iteration if "iteration" in dir() else 1,
        "converged": converged,
        "details": all_details,
    }


@jig.implements("S-106")
def mend_apply(
    project_root: Path, fixes_path: Path, *, dry_run: bool = False
) -> dict[str, Any]:
    """Apply explicit fixes from a JSON file.

    Fixes are applied regardless of their auto field value since they
    have explicit user approval.

    Args:
        project_root: Path to project root.
        fixes_path: Path to JSON file with fixes.
        dry_run: If True, show changes without modifying files.

    Returns:
        Dictionary with:
        - applied: Count of applied fixes
        - failed: Count of failed fixes
        - success: True if all fixes applied
        - error: Error message if JSON parsing failed
        - details: List of fix details
    """
    # Load and validate JSON
    try:
        content = fixes_path.read_text()
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return {
            "applied": 0,
            "failed": 0,
            "success": False,
            "error": f"Invalid JSON: {e}",
            "details": [],
        }
    except FileNotFoundError:
        return {
            "applied": 0,
            "failed": 0,
            "success": False,
            "error": f"File not found: {fixes_path}",
            "details": [],
        }

    # Validate structure
    if not isinstance(data, dict) or "errors" not in data:
        return {
            "applied": 0,
            "failed": 0,
            "success": False,
            "error": "JSON must have 'errors' array",
            "details": [],
        }

    errors = data.get("errors", [])
    if not isinstance(errors, list):
        return {
            "applied": 0,
            "failed": 0,
            "success": False,
            "error": "'errors' must be an array",
            "details": [],
        }

    applied = 0
    failed = 0
    details: list[dict[str, Any]] = []

    for error in errors:
        fix = error.get("fix", {})
        if not fix:
            # No fix in this error entry
            detail = {
                "error_id": error.get("id"),
                "status": "skipped",
                "reason": "No fix provided",
            }
            details.append(detail)
            continue

        detail = {
            "error_id": error.get("id"),
            "file": error.get("file"),
            "action": fix.get("action"),
        }

        if dry_run:
            detail["status"] = "would_apply"
            details.append(detail)
        else:
            if _apply_fix(project_root, fix):
                detail["status"] = "applied"
                applied += 1
            else:
                detail["status"] = "failed"
                failed += 1
            details.append(detail)

    return {
        "applied": applied,
        "failed": failed,
        "success": failed == 0,
        "details": details,
    }


@jig.implements("S-105", "S-106", "S-107")
def mend_combined(
    project_root: Path,
    *,
    apply_path: Path | None = None,
    dry_run: bool = False,
    iterate: bool = True,
) -> dict[str, Any]:
    """Combine --auto and --apply modes.

    First applies explicit fixes from apply_path, then runs auto-mend
    with iteration.

    Args:
        project_root: Path to project root.
        apply_path: Optional path to JSON file with explicit fixes.
        dry_run: If True, show changes without modifying files.
        iterate: If True (default), iterate until fixed point.

    Returns:
        Combined result dictionary.
    """
    result: dict[str, Any] = {
        "applied": 0,
        "skipped": 0,
        "iterations": 0,
        "converged": False,
        "details": [],
    }

    # Apply explicit fixes first
    if apply_path is not None:
        apply_result = mend_apply(project_root, apply_path, dry_run=dry_run)
        result["applied"] += apply_result.get("applied", 0)
        result["details"].extend(apply_result.get("details", []))

        if apply_result.get("error"):
            result["error"] = apply_result["error"]
            return result

    # Then run auto-mend with iteration
    auto_result = mend_auto(project_root, dry_run=dry_run, iterate=iterate)
    result["applied"] += auto_result.get("applied", 0)
    result["skipped"] = auto_result.get("skipped", 0)
    result["iterations"] = auto_result.get("iterations", 1)
    result["converged"] = auto_result.get("converged", False)
    result["details"].extend(auto_result.get("details", []))

    return result
