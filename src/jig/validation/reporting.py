"""
Validation reporting: human-readable and JSON output formats.
"""

import json

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
