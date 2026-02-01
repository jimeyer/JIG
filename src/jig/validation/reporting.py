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
    import re

    lines = []

    # Overall status
    all_passed = all(result.passed for result in results.values())
    status = "Passed" if all_passed else "FAILED"

    # Header with status
    lines.append(f"# JIG Validation: {status}")
    lines.append("")

    # Extract key counts
    spec_result = results.get("specifications")
    spec_count = spec_result.items_checked if spec_result else 0

    outcome_result = results.get("outcomes")
    outcome_count = outcome_result.items_checked if outcome_result else 0

    brick_result = results.get("brick_definitions")
    brick_count = brick_result.items_checked if brick_result else 0

    # Extract decorator counts from detail string
    func_count = 0
    test_count = 0
    decorator_result = results.get("decorators")
    if decorator_result and decorator_result.detail:
        match = re.search(r"(\d+) functions, (\d+) tests", decorator_result.detail)
        if match:
            func_count = int(match.group(1))
            test_count = int(match.group(2))

    # Summary line
    lines.append(f"- **Specs:** {spec_count} | **Outcomes:** {outcome_count} | **Bricks:** {brick_count}")
    lines.append(f"- **Coverage:** {func_count} functions, {test_count} tests decorated")

    # Verbose: add more detail
    if verbose:
        lines.append("")
        lines.append("## Details")

        # Extract goal count
        goal_count = 0
        charter_result = results.get("charter")
        if charter_result and charter_result.detail:
            match = re.search(r"(\d+) goals", charter_result.detail)
            if match:
                goal_count = int(match.group(1))

        arch_result = results.get("architecture")
        arch_count = arch_result.items_checked if arch_result else 0

        lines.append(f"- Goals: {goal_count}")
        lines.append(f"- Architecture docs: {arch_count}")

        partition_result = results.get("brick_partition")
        partition_count = partition_result.items_checked if partition_result else 0
        lines.append(f"- Files partitioned: {partition_count}")

    # Collect all errors
    all_errors = []
    for result in results.values():
        for error in result.errors:
            all_errors.append(error)

    # Errors section (only if there are errors)
    if all_errors:
        lines.append("")
        lines.append("## Errors")
        lines.append("")
        for error in all_errors:
            file_display = Path(error.file).name if not verbose else error.file
            location = f"{file_display}:{error.line}" if error.line else file_display
            code_display = f"`{error.code}`" if error.code else ""

            if code_display:
                lines.append(f"- **{location}** {code_display}: {error.message}")
            else:
                lines.append(f"- **{location}**: {error.message}")

    return "\n".join(lines)
