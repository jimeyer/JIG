"""
Validation CLI commands.
"""

import sys
from pathlib import Path
from typing import Union

import click

import jig
from jig.config import JigConfig
from jig.validation.bricks import (
    validate_brick_cycles,
    validate_brick_definitions,
    validate_brick_layer_constraints,
    validate_brick_partition,
)
from jig.validation.intent import (
    validate_decorator_files,
    validate_outcome_completeness,
    validate_outcome_files,
    validate_specification_coverage,
    validate_specification_files,
)
from jig.validation.reporting import format_as_json


@jig.implements("S-023", "S-065")
def validate_intent_command(config: JigConfig, output_format: str = "human") -> int:
    """
    Validate intent artifacts (specifications, outcomes, decorators).

    Returns exit code: 0 (success), 1 (validation failures).
    """
    spec_dir = config.paths.specifications
    outcome_dir = config.paths.outcomes
    src_dir = config.paths.source

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
        # Validate outcome completeness (S-042)
        results["outcome_completeness"] = validate_outcome_completeness(outcome_dir)
    else:
        from jig.validation.models import ValidationResult
        results["outcomes"] = ValidationResult(passed=True, phase_name="outcomes", items_checked=0)
        results["outcome_completeness"] = ValidationResult(passed=True, phase_name="outcome completeness", items_checked=0)

    # Validate specification coverage (S-043)
    if spec_dir.exists() and outcome_dir.exists():
        results["specification_coverage"] = validate_specification_coverage(spec_dir, outcome_dir)
    else:
        from jig.validation.models import ValidationResult
        results["specification_coverage"] = ValidationResult(passed=True, phase_name="specification coverage", items_checked=0)

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


@jig.implements("S-024", "S-065")
def validate_bricks_command(config: JigConfig, output_format: str = "human") -> int:
    """
    Validate brick definitions and partition against implementation graph.

    Returns exit code: 0 (success), 1 (validation failures), 2 (errors).
    """
    bricks_file = config.paths.bricks
    impl_graph = config.paths.generated / "implementation-graph.ndjson"

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

    # Validate brick cycles (S-039)
    # Always run - cycles are independent of layer values
    cycles_result = validate_brick_cycles(bricks_file, impl_graph)
    results["cycles"] = cycles_result

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


@jig.implements("S-025", "S-065")
def validate_full_command(config: JigConfig, output_format: str = "human") -> int:
    """
    Run full validation (intent + bricks if graph exists).

    Returns exit code: 0 (success), 1 (validation failures).
    """
    # Always run intent validation
    if output_format != "json":
        click.echo("=== Validating Intent ===\n")

    intent_exit_code = validate_intent_command(config, output_format)

    # Conditionally run brick validation if implementation graph exists
    impl_graph = config.paths.generated / "implementation-graph.ndjson"
    if impl_graph.exists():
        if output_format != "json":
            click.echo("\n=== Validating Bricks ===\n")
        brick_exit_code = validate_bricks_command(config, output_format)
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


@jig.implements("S-027", "S-065")
def auto_validate_decorators(config: JigConfig) -> bool:
    """
    Auto-validate decorators before graph rebuild.

    Returns True if validation passed, False otherwise.
    """
    spec_dir = config.paths.specifications
    outcome_dir = config.paths.outcomes
    src_dir = config.paths.source

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
