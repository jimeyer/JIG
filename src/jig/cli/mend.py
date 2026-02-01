# ABOUTME: CLI command for mending JIG artifacts.
# ABOUTME: Implements `jigy mend` with --auto, --apply, --dry-run, and -j options.
"""
CLI command for mending JIG artifacts.

Provides the `jigy mend` command with:
- --auto: Apply all auto-fixable validation errors
- --apply FILE: Apply explicit fixes from JSON file
- --dry-run: Show changes without modifying files
- --no-iterate: Disable fixed point iteration
- -j: Output results as JSON
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import click

import jig
from jig.cli.discovery import find_project_root
from jig.mend.engine import mend_apply, mend_auto, mend_combined


def _format_text_output(result: dict[str, Any], dry_run: bool = False) -> str:
    """Format mend result as human-readable text.

    Args:
        result: Mend result dictionary.
        dry_run: Whether this was a dry run.

    Returns:
        Formatted text output.
    """
    lines = []

    if "error" in result:
        lines.append(f"Error: {result['error']}")
        return "\n".join(lines)

    iterations = result.get("iterations", 1)
    applied = result.get("applied", 0)
    skipped = result.get("skipped", 0)
    converged = result.get("converged", False)

    if dry_run:
        lines.append("Dry run - no files modified")
        lines.append("")

    # Report iterations
    if iterations > 1:
        for i in range(1, iterations + 1):
            iter_fixes = [
                d for d in result.get("details", []) if d.get("iteration") == i
            ]
            iter_applied = len(
                [d for d in iter_fixes if d.get("status") in ("applied", "would_apply")]
            )
            verb = "Would apply" if dry_run else "Applied"
            lines.append(f"Iteration {i}: {verb} {iter_applied} fixes")
    elif applied > 0 or (dry_run and result.get("details")):
        verb = "Would apply" if dry_run else "Applied"
        count = (
            len(result.get("details", []))
            if dry_run
            else applied
        )
        lines.append(f"{verb} {count} fixes")

    # Report convergence per S-107
    if converged:
        lines.append(f"Converged after {iterations} iteration(s).")
    elif iterations >= 3:
        lines.append(f"Did not converge after {iterations} iterations.")

    # Report skipped manual fixes
    if skipped > 0:
        lines.append(f"Skipped {skipped} manual fixes (require human decision)")

    # Summary
    if not result.get("details") and applied == 0 and skipped == 0:
        lines.append("No fixes to apply.")

    return "\n".join(lines)


def _format_json_output(result: dict[str, Any]) -> str:
    """Format mend result as JSON.

    Args:
        result: Mend result dictionary.

    Returns:
        JSON string.
    """
    return json.dumps(result, indent=2)


@click.command(name="mend")
@click.option(
    "--auto",
    "auto_mode",
    is_flag=True,
    default=False,
    help="Apply all auto-fixable validation errors",
)
@click.option(
    "--apply",
    "apply_path",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Apply explicit fixes from JSON file",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show changes without modifying files",
)
@click.option(
    "--no-iterate",
    is_flag=True,
    default=False,
    help="Disable fixed point iteration (single pass only)",
)
@click.option(
    "-j",
    "--json",
    "json_output",
    is_flag=True,
    default=False,
    help="Output results as JSON",
)
@jig.implements("S-105", "S-106")
def mend_command(
    auto_mode: bool,
    apply_path: Path | None,
    dry_run: bool,
    no_iterate: bool,
    json_output: bool,
) -> None:
    """Apply fixes to JIG artifacts.

    Mend command applies validation fixes to JIG artifacts. Use --auto to
    apply all auto-fixable errors, or --apply to apply specific fixes from
    a JSON file.

    Exit codes:
      0 - Success (all fixes applied, or no fixes needed)
      1 - Partial success (some fixes skipped, require manual decision)
      2 - Error (invalid input, file errors)

    Examples:
        jigy mend --auto                  # Fix all auto-fixable errors
        jigy mend --auto --dry-run        # Preview auto-fixes
        jigy mend --apply fixes.json      # Apply curated fixes
        jigy mend --auto --apply f.json   # Combine both modes
        jigy mend --auto --no-iterate     # Single pass, no iteration
        jigy mend --auto -j               # JSON output
    """
    # Require at least one mode
    if not auto_mode and apply_path is None:
        raise click.UsageError("Must specify --auto and/or --apply FILE")

    # Find project root
    try:
        project_root = find_project_root()
    except Exception as e:
        if json_output:
            click.echo(json.dumps({"error": str(e), "success": False}))
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(2)

    # Run mend
    result: dict[str, Any]

    if auto_mode and apply_path is not None:
        # Combined mode
        result = mend_combined(
            project_root,
            apply_path=apply_path,
            dry_run=dry_run,
            iterate=not no_iterate,
        )
    elif apply_path is not None:
        # Apply mode only
        result = mend_apply(project_root, apply_path, dry_run=dry_run)
    else:
        # Auto mode only
        result = mend_auto(project_root, dry_run=dry_run, iterate=not no_iterate)

    # Format output
    if json_output:
        click.echo(_format_json_output(result))
    else:
        click.echo(_format_text_output(result, dry_run=dry_run))

    # Determine exit code per S-105, S-106, S-107
    if "error" in result:
        sys.exit(2)
    elif result.get("skipped", 0) > 0:
        # Partial success - some fixes require manual decision
        sys.exit(1)
    elif result.get("failed", 0) > 0:
        # Some fixes failed to apply
        sys.exit(1)
    else:
        # Full success
        sys.exit(0)
