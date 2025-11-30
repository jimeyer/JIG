"""
Validation CLI commands.
"""

import sys
from pathlib import Path

import click

import jig
from jig.validation.bricks import validate_brick_definitions, validate_brick_partition
from jig.validation.intent import (
    validate_decorator_files,
    validate_outcome_files,
    validate_specification_files,
)


@jig.implements("S-023")
def validate_intent_command(project_root: Path) -> int:
    """
    Validate intent artifacts (specifications, outcomes, decorators).

    Returns exit code: 0 (success), 1 (validation failures).
    """
    spec_dir = project_root / "jig" / "specifications"
    outcome_dir = project_root / "jig" / "outcomes"
    src_dir = project_root / "src"

    all_passed = True
    total_errors = 0

    # Validate specifications
    if spec_dir.exists():
        result = validate_specification_files(spec_dir)
        click.echo(str(result))
        if not result.passed:
            all_passed = False
            total_errors += len(result.errors)
            for error in result.errors:
                click.echo(str(error))
    else:
        click.echo("✓ Validating specifications (0 files)")

    # Validate outcomes
    if outcome_dir.exists():
        result = validate_outcome_files(outcome_dir)
        click.echo(str(result))
        if not result.passed:
            all_passed = False
            total_errors += len(result.errors)
            for error in result.errors:
                click.echo(str(error))
    else:
        click.echo("✓ Validating outcomes (0 files)")

    # Validate decorators
    if src_dir.exists() and spec_dir.exists():
        result = validate_decorator_files(src_dir, spec_dir, outcome_dir if outcome_dir.exists() else None)
        click.echo(str(result))
        if not result.passed:
            all_passed = False
            total_errors += len(result.errors)
            for error in result.errors:
                click.echo(str(error))
    else:
        click.echo("✓ Validating decorators (0 files)")

    # Summary
    if all_passed:
        click.echo("\nIntent validation passed.")
        return 0
    else:
        click.echo(f"\nIntent validation failed: {total_errors} errors total.")
        return 1


@jig.implements("S-024")
def validate_bricks_command(project_root: Path) -> int:
    """
    Validate brick definitions and partition against implementation graph.

    Returns exit code: 0 (success), 1 (validation failures), 2 (errors).
    """
    bricks_file = project_root / "jig" / "bricks.yaml"
    impl_graph = project_root / "jig" / "generated" / "implementation-graph.ndjson"

    all_passed = True
    total_errors = 0

    # Validate brick definitions
    result = validate_brick_definitions(bricks_file, impl_graph)
    click.echo(str(result))
    if not result.passed:
        all_passed = False
        total_errors += len(result.errors)
        for error in result.errors:
            click.echo(str(error))

        # If graph not found, return error code 2
        if any(err.code == "GRAPH_NOT_FOUND" for err in result.errors):
            return 2

    # Validate brick partition
    if all_passed or impl_graph.exists():
        result = validate_brick_partition(bricks_file, impl_graph)
        click.echo(str(result))
        if not result.passed:
            all_passed = False
            total_errors += len(result.errors)
            for error in result.errors:
                click.echo(str(error))

    # Summary
    if all_passed:
        click.echo("\nBrick validation passed.")
        return 0
    else:
        click.echo(f"\nBrick validation failed: {total_errors} errors total.")
        return 1


@jig.implements("S-025")
def validate_full_command(project_root: Path) -> int:
    """
    Run full validation (intent + bricks if graph exists).

    Returns exit code: 0 (success), 1 (validation failures).
    """
    # Always run intent validation
    click.echo("=== Validating Intent ===\n")
    intent_exit_code = validate_intent_command(project_root)

    # Conditionally run brick validation if implementation graph exists
    impl_graph = project_root / "jig" / "generated" / "implementation-graph.ndjson"
    if impl_graph.exists():
        click.echo("\n=== Validating Bricks ===\n")
        brick_exit_code = validate_bricks_command(project_root)
    else:
        click.echo("\n=== Skipping Brick Validation ===")
        click.echo("(Implementation graph not found)")
        brick_exit_code = 0

    # Overall result
    if intent_exit_code == 0 and brick_exit_code == 0:
        click.echo("\n✓ All validations passed.")
        return 0
    else:
        click.echo("\n✗ Validation failed.")
        return 1


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
