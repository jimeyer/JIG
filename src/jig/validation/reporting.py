"""
Validation reporting: human-readable and JSON output formats.
"""

import json
from pathlib import Path

import jig
from jig.validation.models import ValidationResult


@jig.implements("S-026")
def format_as_json(results: dict[str, ValidationResult]) -> str:
    """
    Format validation results as JSON for CI/tooling integration.

    Args:
        results: Dictionary mapping phase name to ValidationResult

    Returns:
        JSON string with structured error codes and summary
    """
    output = {}

    # Add each phase
    for phase_name, result in results.items():
        phase_data = {
            "passed": result.passed,
            "errors": [],
        }

        for error in result.errors:
            error_data = {
                "file": error.file,
                "line": error.line,
                "code": error.code,
                "message": error.message,
                "severity": error.severity,
            }

            # Add optional field if present
            if error.field:
                error_data["field"] = error.field

            phase_data["errors"].append(error_data)

        output[phase_name] = phase_data

    # Overall status
    all_passed = all(result.passed for result in results.values())
    output["status"] = "passed" if all_passed else "failed"

    # Summary
    total_errors = sum(len(result.errors) for result in results.values())
    total_warnings = sum(
        len([e for e in result.errors if e.severity == "warning"]) for result in results.values()
    )

    output["summary"] = {
        "total_errors": total_errors,
        "total_warnings": total_warnings,
    }

    return json.dumps(output, indent=2)


def format_validation_results(results: list[ValidationResult]) -> str:
    """
    Format validation results as human-readable output.

    Args:
        results: List of ValidationResult objects

    Returns:
        Human-readable string with check marks and error details
    """
    lines = []

    for result in results:
        lines.append(str(result))

        # Add error details
        for error in result.errors:
            lines.append(str(error))

    return "\n".join(lines)


@jig.implements("S-094")
def format_as_markdown(results: dict[str, ValidationResult], verbose: bool = False) -> str:
    """
    Format validation results as markdown for LLM-optimized output.

    Args:
        results: Dictionary mapping phase name to ValidationResult
        verbose: If True, include full file paths and additional detail

    Returns:
        Markdown string with headers, bullets, and emphasis
    """
    lines = []

    # Header
    lines.append("# Validation Result")
    lines.append("")

    # Overall status
    all_passed = all(result.passed for result in results.values())
    status = "Passed" if all_passed else "Failed"
    lines.append(f"**Status:** {status}")

    # Checked counts - build a summary line
    checked_parts = []
    for phase_name, result in results.items():
        checked_parts.append(f"{result.items_checked} {phase_name}")
    lines.append(f"**Checked:** {', '.join(checked_parts)}")
    lines.append("")

    # Verbose mode: add phase details section
    if verbose:
        lines.append("## Phases")
        lines.append("")
        for phase_name, result in results.items():
            phase_status = "Passed" if result.passed else "Failed"
            lines.append(f"- **{phase_name}**: {phase_status} ({result.items_checked} checked)")
        lines.append("")

    # Collect all errors from all phases
    all_errors = []
    for phase_name, result in results.items():
        for error in result.errors:
            all_errors.append(error)

    # Errors section (only if there are errors)
    if all_errors:
        lines.append("## Errors")
        lines.append("")
        for error in all_errors:
            # Format file location
            if verbose:
                # Verbose mode: use full path
                file_display = error.file
            else:
                # Normal mode: use basename only
                file_display = Path(error.file).name

            # Add line number if present
            if error.line is not None:
                location = f"{file_display}:{error.line}"
            else:
                location = file_display

            # Format error code
            code_display = f"`{error.code}`" if error.code else ""

            # Build the error line
            if code_display:
                lines.append(f"- **{location}** - {code_display}: {error.message}")
            else:
                lines.append(f"- **{location}** - {error.message}")

    return "\n".join(lines)
