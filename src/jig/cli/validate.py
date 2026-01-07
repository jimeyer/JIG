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
    validate_tower_format,
    validate_tower_isolation,
)
from jig.validation.intent import (
    validate_architecture_files,
    validate_charter_file,
    validate_decorator_files,
    validate_goal_references,
    validate_outcome_completeness,
    validate_outcome_files,
    validate_specification_coverage,
    validate_specification_files,
)
from jig.validation.reporting import format_as_json


def _get_charter_goals(charter_path: Path) -> set[str]:
    """Extract goal IDs from Charter frontmatter."""
    import yaml
    content = charter_path.read_text()
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            return set(frontmatter.get("defines_goals", []))
    return set()


def _get_all_spec_ids(spec_dir: Path) -> set[str]:
    """Get all specification IDs from spec directory."""
    import yaml
    spec_ids = set()
    for spec_file in spec_dir.glob("S-*.md"):
        content = spec_file.read_text()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                if "id" in frontmatter:
                    spec_ids.add(frontmatter["id"])
    return spec_ids


@jig.implements("S-023", "S-065", "S-070")
def validate_intent_command(
    config: JigConfig,
    output_format: str = "human",
    skip_rebuild: bool = False,
) -> int:
    """
    Validate intent artifacts (specifications, outcomes, decorators).

    Returns exit code: 0 (success), 1 (validation failures).
    """
    # Auto-rebuild stale intent graph before validating (S-070)
    from jig.cli.auto_rebuild import ensure_graphs_current
    ensure_graphs_current(["intent"], config, skip_rebuild=skip_rebuild)
    spec_dir = config.paths.specifications
    outcome_dir = config.paths.outcomes
    src_dir = config.paths.source

    results = {}

    # Validate charter (per A-004 rules C-1 through C-4)
    charter_path = config.paths.charter
    if charter_path.exists():
        results["charter"] = validate_charter_file(charter_path)
        charter_goals = _get_charter_goals(charter_path)
    else:
        from jig.validation.models import ValidationResult
        results["charter"] = ValidationResult(passed=True, phase_name="charter", items_checked=0)
        charter_goals = set()

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

    # Validate architecture files (per A-004 rules A-1 through A-7)
    arch_dir = config.paths.architecture
    if arch_dir.exists() and charter_goals:
        spec_ids = _get_all_spec_ids(spec_dir) if spec_dir.exists() else set()
        results["architecture"] = validate_architecture_files(arch_dir, charter_goals, spec_ids)
    else:
        from jig.validation.models import ValidationResult
        results["architecture"] = ValidationResult(passed=True, phase_name="architecture", items_checked=0)

    # Validate goal references (per A-004 rules GR-1 and GR-2)
    if charter_path.exists() and outcome_dir.exists():
        results["goal_references"] = validate_goal_references(
            charter_path,
            outcome_dir,
            arch_dir if arch_dir.exists() else None,
        )
    else:
        from jig.validation.models import ValidationResult
        results["goal_references"] = ValidationResult(passed=True, phase_name="goal references", items_checked=0)

    # Validate specification coverage (S-043)
    if spec_dir.exists() and outcome_dir.exists():
        results["specification_coverage"] = validate_specification_coverage(spec_dir, outcome_dir)
    else:
        from jig.validation.models import ValidationResult
        results["specification_coverage"] = ValidationResult(passed=True, phase_name="specification coverage", items_checked=0)

    # Validate decorators
    test_dir = config.paths.tests
    if src_dir.exists() and spec_dir.exists():
        results["decorators"] = validate_decorator_files(
            src_dir,
            spec_dir,
            outcome_dir if outcome_dir.exists() else None,
            test_dir if test_dir.exists() else None,
        )
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


def _has_towers(bricks_file: Path) -> bool:
    """Check if any brick declares a tower field."""
    import yaml
    if not bricks_file.exists():
        return False
    content = yaml.safe_load(bricks_file.read_text())
    bricks = content.get("bricks", [])
    return any("tower" in brick for brick in bricks)


@jig.implements("S-024", "S-065", "S-070")
def validate_bricks_command(
    config: JigConfig,
    output_format: str = "human",
    skip_rebuild: bool = False,
) -> int:
    """
    Validate brick definitions and partition against implementation graph.

    Returns exit code: 0 (success), 1 (validation failures), 2 (errors).
    """
    # Auto-rebuild stale impl + intent graphs before validating (S-070)
    from jig.cli.auto_rebuild import ensure_graphs_current
    ensure_graphs_current(["impl", "intent"], config, skip_rebuild=skip_rebuild)
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

    # Validate tower format (per A-004 rule T-1)
    tower_format_result = validate_tower_format(bricks_file)
    results["tower_format"] = tower_format_result

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

    # Validate tower isolation (per A-004 rules T-2 and T-3)
    if _has_towers(bricks_file):
        results["tower_isolation"] = validate_tower_isolation(bricks_file, impl_graph)

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


@jig.implements("S-025", "S-065", "S-070")
def validate_full_command(
    config: JigConfig,
    output_format: str = "human",
    skip_rebuild: bool = False,
) -> int:
    """
    Run full validation (intent + bricks if graph exists).

    Returns exit code: 0 (success), 1 (validation failures).
    """
    # Auto-rebuild all stale graphs before validating (S-070)
    from jig.cli.auto_rebuild import ensure_graphs_current
    ensure_graphs_current(["impl", "verify", "intent"], config, skip_rebuild=skip_rebuild)

    # Always run intent validation
    if output_format != "json":
        click.echo("=== Validating Intent ===\n")

    # Pass skip_rebuild=True to sub-commands since we already rebuilt
    intent_exit_code = validate_intent_command(config, output_format, skip_rebuild=True)

    # Conditionally run brick validation if implementation graph exists
    impl_graph = config.paths.generated / "implementation-graph.ndjson"
    if impl_graph.exists():
        if output_format != "json":
            click.echo("\n=== Validating Bricks ===\n")
        brick_exit_code = validate_bricks_command(config, output_format, skip_rebuild=True)
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
    test_dir = config.paths.tests

    if not src_dir.exists() or not spec_dir.exists():
        # No source or specs to validate
        return True

    result = validate_decorator_files(
        src_dir,
        spec_dir,
        outcome_dir if outcome_dir.exists() else None,
        test_dir if test_dir.exists() else None,
    )

    if not result.passed:
        click.echo("\n✗ Validation failed before graph generation:")
        click.echo(str(result))
        for error in result.errors:
            click.echo(str(error))
        click.echo("\nFix validation errors or use --skip-validation to bypass.")
        return False

    return True
