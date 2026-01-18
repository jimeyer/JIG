# ABOUTME: Validation CLI commands using the rules-based engine.
# ABOUTME: Implements S-023, S-024, S-025 for validate intent/bricks/full.
"""
Validation CLI commands.

Uses the rules-based validation engine for all validation.
"""

import sys
from pathlib import Path
from typing import Any

import click

import jig
from jig.config import JigConfig
from jig.validation.engine import validate
from jig.validation.reporting import format_as_markdown


def _format_engine_results_as_json(result: dict[str, Any]) -> dict[str, Any]:
    """Format engine results for JSON output per S-026.

    Args:
        result: Engine result with 'errors', 'summary', and 'counts'.

    Returns:
        JSON-serializable output with valid, summary, errors.
    """
    errors = result.get("errors", [])
    counts = result.get("counts", {})

    # Build summary with artifact counts per S-026
    summary_out = {
        "specs": counts.get("specs", 0),
        "outcomes": counts.get("outcomes", 0),
        "bricks": counts.get("bricks", 0),
    }

    return {
        "valid": len(errors) == 0,
        "summary": summary_out,
        "errors": [
            {
                "id": e.get("id", ""),
                "code": e.get("spec", ""),
                "file": e.get("file", ""),
                "line": e.get("line"),
                "message": e.get("message", ""),
                "fix": e.get("fix", {}),
            }
            for e in errors
        ],
    }


def _format_engine_results_as_markdown(result: dict[str, Any], verbose: bool = False) -> str:
    """Format engine results as markdown for LLM-optimized output per S-094.

    Args:
        result: Engine result with 'errors', 'summary', and 'counts'.
        verbose: If True, include additional detail.

    Returns:
        Markdown string matching S-094 format.
    """
    from pathlib import Path

    errors = result.get("errors", [])
    summary = result.get("summary", {})
    counts = result.get("counts", {})

    lines = []

    # Status header per S-094
    status = "Passed" if len(errors) == 0 else "FAILED"
    lines.append(f"# JIG Validation: {status}")
    lines.append("")

    # Summary line with actual counts from result["counts"]
    specs_count = counts.get("specs", 0)
    outcomes_count = counts.get("outcomes", 0)
    bricks_count = counts.get("bricks", 0)
    lines.append(f"- **Specs:** {specs_count} | **Outcomes:** {outcomes_count} | **Bricks:** {bricks_count}")
    # Coverage deferred - leave as 0 per SCOPE
    lines.append("- **Coverage:** 0 functions, 0 tests decorated")

    # Verbose adds details section
    if verbose:
        lines.append("")
        lines.append("## Details")
        lines.append("")
        lines.append(f"- Total errors: {summary.get('total', 0)}")
        lines.append(f"- Auto-fixable: {summary.get('auto_fixable', 0)}")
        lines.append(f"- Manual: {summary.get('manual', 0)}")

    # Errors section
    if errors:
        lines.append("")
        lines.append("## Errors")
        lines.append("")
        for error in errors:
            file_path = error.get("file", "unknown")
            file_display = Path(file_path).name if not verbose else file_path
            line = error.get("line")
            location = f"{file_display}:{line}" if line else file_display
            spec = error.get("spec", "")
            msg = error.get("message", "")

            if spec:
                lines.append(f"- **{location}** `{spec}`: {msg}")
            else:
                lines.append(f"- **{location}**: {msg}")

    return "\n".join(lines)


def _output_human_results(
    result: dict[str, Any],
    verbose: bool = False,
    rebuild_summary: str | None = None,
    counts: dict[str, int] | None = None,
) -> None:
    """Output validation results in human-readable format.

    Args:
        result: Engine result with 'errors' and 'summary'.
        verbose: Whether to show detailed output.
        rebuild_summary: Optional rebuild summary from ensure_graphs_current().
        counts: Optional artifact counts dict with specs, outcomes, bricks keys.
    """
    errors = result.get("errors", [])
    summary = result.get("summary", {})

    if not errors:
        # Build single-line success message per S-025
        parts = []
        if rebuild_summary:
            parts.append(rebuild_summary.rstrip("."))
        if counts:
            parts.append(
                f"Validated {counts.get('specs', 0)} specs, "
                f"{counts.get('outcomes', 0)} outcomes, "
                f"{counts.get('bricks', 0)} bricks"
            )
        else:
            parts.append("Validation passed")
        click.echo(". ".join(parts) + ".")
        return

    # Group errors by file
    errors_by_file: dict[str, list[dict]] = {}
    for error in errors:
        file_path = error.get("file", "unknown")
        if file_path not in errors_by_file:
            errors_by_file[file_path] = []
        errors_by_file[file_path].append(error)

    # Output errors
    for file_path, file_errors in sorted(errors_by_file.items()):
        for error in file_errors:
            line = error.get("line")
            spec = error.get("spec", "")
            msg = error.get("message", "")

            if line:
                click.echo(f"{file_path}:{line}: [{spec}] {msg}")
            else:
                click.echo(f"{file_path}: [{spec}] {msg}")

            if verbose:
                fix = error.get("fix", {})
                if fix.get("suggestions"):
                    for suggestion in fix["suggestions"]:
                        click.echo(f"  -> {suggestion}")

    # Summary
    total = summary.get("total", 0)
    auto_fixable = summary.get("auto_fixable", 0)
    manual = summary.get("manual", 0)

    click.echo(f"\nValidation failed: {total} errors ({auto_fixable} auto-fixable, {manual} manual)")


def _filter_errors_by_specs(result: dict[str, Any], spec_ids: set[str]) -> dict[str, Any]:
    """Filter validation result to only include errors for specific specs.

    Args:
        result: Engine result with 'errors' and 'summary'.
        spec_ids: Set of spec IDs to include.

    Returns:
        Filtered result with only matching errors.
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


@jig.implements("S-023", "S-026", "S-065", "S-070", "S-093", "S-094")
def validate_intent_command(
    config: JigConfig,
    output_format: str = "human",
    skip_rebuild: bool = False,
    verbose: bool = False,
) -> int:
    """
    Validate intent artifacts (specifications, outcomes).

    Uses the rules-based validation engine.

    Args:
        config: JIG configuration.
        output_format: Output format ("human", "json", or "markdown").
        skip_rebuild: Skip automatic graph rebuild.
        verbose: Include additional detail in output.

    Returns:
        Exit code: 0 (success), 1 (validation failures).
    """
    # Auto-rebuild stale intent graph before validating (S-070)
    from jig.cli.auto_rebuild import ensure_graphs_current
    ensure_graphs_current(["intent"], config, skip_rebuild=skip_rebuild)

    # Run unified validation
    result = validate(config.project_root)

    # Filter to intent-related errors
    intent_specs = {"S-018", "S-019", "S-020", "S-042", "S-043", "S-072", "S-079", "S-095"}
    filtered_result = _filter_errors_by_specs(result, intent_specs)

    # Format output
    if output_format == "json":
        import json
        output = _format_engine_results_as_json(filtered_result)
        click.echo(json.dumps(output, separators=(",", ":")))
    elif output_format == "markdown":
        click.echo(_format_engine_results_as_markdown(filtered_result, verbose=verbose))
    else:
        _output_human_results(filtered_result, verbose=verbose)

    return 0 if len(filtered_result["errors"]) == 0 else 1


@jig.implements("S-024", "S-026", "S-065", "S-070", "S-093", "S-094")
def validate_bricks_command(
    config: JigConfig,
    output_format: str = "human",
    skip_rebuild: bool = False,
    verbose: bool = False,
) -> int:
    """
    Validate brick definitions and partition against implementation graph.

    Uses the rules-based validation engine.

    Args:
        config: JIG configuration.
        output_format: Output format ("human", "json", or "markdown").
        skip_rebuild: Skip automatic graph rebuild.
        verbose: Include additional detail in output.

    Returns:
        Exit code: 0 (success), 1 (validation failures), 2 (errors).
    """
    # Auto-rebuild stale impl + intent graphs before validating (S-070)
    from jig.cli.auto_rebuild import ensure_graphs_current
    ensure_graphs_current(["impl", "intent"], config, skip_rebuild=skip_rebuild)

    # Check if implementation graph exists
    impl_graph = config.paths.generated / "implementation-graph.ndjson"
    if not impl_graph.exists():
        if output_format == "json":
            import json
            click.echo(json.dumps({
                "valid": False,
                "summary": {"total": 1, "auto_fixable": 0, "manual": 1},
                "errors": [{"code": "GRAPH_NOT_FOUND", "message": "Implementation graph not found", "file": str(impl_graph)}]
            }, separators=(",", ":")))
        else:
            click.echo(f"Error: Implementation graph not found at {impl_graph}")
            click.echo("Run 'jigy rebuild impl' first.")
        return 2

    # Run unified validation
    result = validate(config.project_root)

    # Filter to brick-related errors
    brick_specs = {"S-021", "S-022", "S-035", "S-036", "S-037", "S-038", "S-039", "S-086", "S-087", "S-088", "S-089"}
    filtered_result = _filter_errors_by_specs(result, brick_specs)

    # Format output
    if output_format == "json":
        import json
        output = _format_engine_results_as_json(filtered_result)
        click.echo(json.dumps(output, separators=(",", ":")))
    elif output_format == "markdown":
        click.echo(_format_engine_results_as_markdown(filtered_result, verbose=verbose))
    else:
        _output_human_results(filtered_result, verbose=verbose)

    return 0 if len(filtered_result["errors"]) == 0 else 1


@jig.implements("S-025", "S-026", "S-065", "S-070", "S-093", "S-094")
def validate_full_command(
    config: JigConfig,
    output_format: str = "human",
    skip_rebuild: bool = False,
    verbose: bool = False,
) -> int:
    """
    Run full validation (intent + bricks if graph exists).

    Uses the rules-based validation engine.

    Args:
        config: JIG configuration.
        output_format: Output format ("human", "json", or "markdown").
        skip_rebuild: Skip automatic graph rebuild.
        verbose: Include additional detail in output.

    Returns:
        Exit code: 0 (success), 1 (validation failures).
    """
    # Auto-rebuild all stale graphs before validating (S-070)
    from jig.cli.auto_rebuild import ensure_graphs_current
    rebuild_summary = ensure_graphs_current(
        ["impl", "verify", "intent"], config, skip_rebuild=skip_rebuild, verbose=verbose
    )

    # Run unified validation
    result = validate(config.project_root)

    # Format output
    if output_format == "json":
        import json
        output = _format_engine_results_as_json(result)
        click.echo(json.dumps(output, separators=(",", ":")))
    elif output_format == "markdown":
        click.echo(_format_engine_results_as_markdown(result, verbose=verbose))
    else:
        # Pass rebuild_summary and counts to _output_human_results per S-025
        _output_human_results(
            result,
            verbose=verbose,
            rebuild_summary=rebuild_summary,
            counts=result.get("counts"),
        )

    return 0 if len(result.get("errors", [])) == 0 else 1


@jig.implements("S-027", "S-065")
def auto_validate_decorators(config: JigConfig) -> bool:
    """
    Auto-validate decorators before graph rebuild.

    Uses the rules-based engine and checks for S-020 errors.

    Returns True if validation passed, False otherwise.
    """
    # Run validation
    result = validate(config.project_root)

    # Filter to decorator-related errors (S-020)
    decorator_errors = [e for e in result["errors"] if e.get("spec", "") == "S-020"]

    if decorator_errors:
        click.echo("\n✗ Validation failed before graph generation:")
        for error in decorator_errors:
            click.echo(f"  {error.get('file', 'unknown')}: {error.get('message', '')}")
        click.echo("\nFix validation errors or use --skip-validation to bypass.")
        return False

    return True
