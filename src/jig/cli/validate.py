"""
Validation CLI commands.
"""

import sys
from pathlib import Path

import click

import jig
from jig.validation.bricks import (
    validate_brick_definitions,
    validate_brick_layer_constraints,
    validate_brick_partition,
)
from jig.validation.intent import (
    validate_decorator_files,
    validate_outcome_files,
    validate_specification_files,
)
from jig.validation.reporting import format_as_json


@jig.implements("S-023")
def validate_intent_command(project_root: Path, output_format: str = "human") -> int:
    """
    Validate intent artifacts (specifications, outcomes, decorators).

    Returns exit code: 0 (success), 1 (validation failures).
    """
    spec_dir = project_root / "jig" / "specifications"
    outcome_dir = project_root / "jig" / "outcomes"
    src_dir = project_root / "src"

    results = {}

    # Validate specifications
    if spec_dir.exists():
        results["specifications"] = validate_specification_files(spec_dir)
    else:
        from jig.validation.models import ValidationResult
        results["specifications"] = ValidationResult(passed=True, phase_name="specifications", items_checked=0)

    # Validate outcomes
    if outcome_dir.exists():
        results["outcomes"] = validate_outcome_files(outcome_dir)
    else:
        from jig.validation.models import ValidationResult
        results["outcomes"] = ValidationResult(passed=True, phase_name="outcomes", items_checked=0)

    # Validate decorators
    if src_dir.exists() and spec_dir.exists():
        results["decorators"] = validate_decorator_files(src_dir, spec_dir, outcome_dir if outcome_dir.exists() else None)
    else:
        from jig.validation.models import ValidationResult
        results["decorators"] = ValidationResult(passed=True, phase_name="decorators", items_checked=0)

    # Format output
    if output_format == "json":
        # Combine all into single "intent" result for JSON
        combined = {"intent": _combine_results(results)}
        click.echo(format_as_json(combined))
    else:
        # Human-readable output
        for result in results.values():
            click.echo(str(result))
            for error in result.errors:
                click.echo(str(error))

        all_passed = all(r.passed for r in results.values())
        if all_passed:
            click.echo("\nIntent validation passed.")
        else:
            total_errors = sum(len(r.errors) for r in results.values())
            click.echo(f"\nIntent validation failed: {total_errors} errors total.")

    # Return exit code
    all_passed = all(r.passed for r in results.values())
    return 0 if all_passed else 1


def _combine_results(results: dict) -> "ValidationResult":
    """Combine multiple ValidationResult objects into one."""
    from jig.validation.models import ValidationResult

    combined = ValidationResult(passed=True, phase_name="combined")
    combined.items_checked = sum(r.items_checked for r in results.values())

    for result in results.values():
        if not result.passed:
            combined.passed = False
        combined.errors.extend(result.errors)

    return combined


@jig.implements("S-024")
def validate_bricks_command(project_root: Path, output_format: str = "human") -> int:
    """
    Validate brick definitions and partition against implementation graph.

    Returns exit code: 0 (success), 1 (validation failures), 2 (errors).
    """
    bricks_file = project_root / "jig" / "bricks.yaml"
    impl_graph = project_root / "jig" / "generated" / "implementation-graph.ndjson"

    results = {}

    # Validate brick definitions
    definitions_result = validate_brick_definitions(bricks_file, impl_graph)
    results["definitions"] = definitions_result

    # If graph not found, return error code 2
    if any(err.code == "GRAPH_NOT_FOUND" for err in definitions_result.errors):
        if output_format == "json":
            click.echo(format_as_json({"bricks": _combine_results(results)}))
        else:
            click.echo(str(definitions_result))
            for error in definitions_result.errors:
                click.echo(str(error))
        return 2

    # Validate brick partition
    partition_result = validate_brick_partition(bricks_file, impl_graph)
    results["partition"] = partition_result

    # Validate brick layer constraints (S-038)
    # Only run if definitions passed (need layer field to be present)
    if definitions_result.passed:
        layer_constraints_result = validate_brick_layer_constraints(bricks_file, impl_graph)
        results["layer_constraints"] = layer_constraints_result

    # Format output
    if output_format == "json":
        combined = {"bricks": _combine_results(results)}
        click.echo(format_as_json(combined))
    else:
        for result in results.values():
            click.echo(str(result))
            for error in result.errors:
                click.echo(str(error))

        all_passed = all(r.passed for r in results.values())
        if all_passed:
            click.echo("\nBrick validation passed.")
        else:
            total_errors = sum(len(r.errors) for r in results.values())
            click.echo(f"\nBrick validation failed: {total_errors} errors total.")

    # Return exit code
    all_passed = all(r.passed for r in results.values())
    return 0 if all_passed else 1


@jig.implements("S-025")
def validate_full_command(project_root: Path, output_format: str = "human") -> int:
    """
    Run full validation (intent + bricks if graph exists).

    Returns exit code: 0 (success), 1 (validation failures).
    """
    # Always run intent validation
    if output_format != "json":
        click.echo("=== Validating Intent ===\n")

    intent_exit_code = validate_intent_command(project_root, output_format)

    # Conditionally run brick validation if implementation graph exists
    impl_graph = project_root / "jig" / "generated" / "implementation-graph.ndjson"
    if impl_graph.exists():
        if output_format != "json":
            click.echo("\n=== Validating Bricks ===\n")
        brick_exit_code = validate_bricks_command(project_root, output_format)
    else:
        if output_format != "json":
            click.echo("\n=== Skipping Brick Validation ===")
            click.echo("(Implementation graph not found)")
        brick_exit_code = 0

    # Overall result
    if output_format != "json":
        if intent_exit_code == 0 and brick_exit_code == 0:
            click.echo("\n✓ All validations passed.")
        else:
            click.echo("\n✗ Validation failed.")

    return 0 if (intent_exit_code == 0 and brick_exit_code == 0) else 1


@jig.implements("S-027")
def auto_validate_decorators(project_root: Path) -> bool:
    """
    Auto-validate decorators before graph rebuild.

    Returns True if validation passed, False otherwise.
    """
    spec_dir = project_root / "jig" / "specifications"
    outcome_dir = project_root / "jig" / "outcomes"
    src_dir = project_root / "src"

    if not src_dir.exists() or not spec_dir.exists():
        # No source or specs to validate
        return True

    result = validate_decorator_files(src_dir, spec_dir, outcome_dir if outcome_dir.exists() else None)

    if not result.passed:
        click.echo("\n✗ Validation failed before graph generation:")
        click.echo(str(result))
        for error in result.errors:
            click.echo(str(error))
        click.echo("\nFix validation errors or use --skip-validation to bypass.")
        return False

    return True
