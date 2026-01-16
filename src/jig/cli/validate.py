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
    validate_bidirectional_consistency,
    validate_charter_file,
    validate_decorator_files,
    validate_goal_references,
    validate_outcome_completeness,
    validate_outcome_files,
    validate_specification_coverage,
    validate_specification_files,
)
from jig.validation.reporting import format_as_json, format_as_markdown


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


@jig.implements("S-023", "S-026", "S-065", "S-070", "S-093", "S-094")
def validate_intent_command(
    config: JigConfig,
    output_format: str = "human",
    skip_rebuild: bool = False,
    verbose: bool = False,
) -> int:
    """
    Validate intent artifacts (specifications, outcomes, decorators).

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

    # Validate bidirectional consistency (S-095)
    if spec_dir.exists() and outcome_dir.exists():
        arch_dir = config.paths.architecture
        results["bidirectional_consistency"] = validate_bidirectional_consistency(
            spec_dir,
            outcome_dir,
            arch_dir,
        )
    else:
        from jig.validation.models import ValidationResult
        results["bidirectional_consistency"] = ValidationResult(passed=True, phase_name="bidirectional consistency", items_checked=0)

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
        # Single-line JSON per S-026
        import json
        click.echo(json.dumps(_format_json_output(combined), separators=(",", ":")))
    elif output_format == "markdown":
        # Markdown output per S-094
        click.echo(format_as_markdown(results, verbose=verbose))
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


def _format_json_output(results: dict) -> dict:
    """Format ValidationResult objects as JSON-serializable dictionary.

    Args:
        results: Dictionary mapping phase name to ValidationResult.

    Returns:
        JSON-serializable dictionary with status, phases, and summary.
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

    return output


def _has_towers(bricks_file: Path) -> bool:
    """Check if any brick declares a tower field."""
    import yaml
    if not bricks_file.exists():
        return False
    bricks_data = yaml.safe_load(bricks_file.read_text())
    # Require production format: {"bricks": [...]}
    if not isinstance(bricks_data, dict) or "bricks" not in bricks_data:
        return False
    bricks_list = bricks_data["bricks"]
    if not isinstance(bricks_list, list):
        return False
    return any("tower" in brick for brick in bricks_list)


@jig.implements("S-024", "S-026", "S-065", "S-070", "S-093", "S-094")
def validate_bricks_command(
    config: JigConfig,
    output_format: str = "human",
    skip_rebuild: bool = False,
    verbose: bool = False,
) -> int:
    """
    Validate brick definitions and partition against implementation graph.

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
    bricks_file = config.paths.bricks
    impl_graph = config.paths.generated / "implementation-graph.ndjson"

    results = {}

    # Validate brick definitions
    definitions_result = validate_brick_definitions(bricks_file, impl_graph)
    results["definitions"] = definitions_result

    # If graph not found, return error code 2
    if any(err.code == "GRAPH_NOT_FOUND" for err in definitions_result.errors):
        if output_format == "json":
            import json
            click.echo(json.dumps(_format_json_output({"bricks": _combine_results(results)}), separators=(",", ":")))
        elif output_format == "markdown":
            click.echo(format_as_markdown(results, verbose=verbose))
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
        # Single-line JSON per S-026
        import json
        click.echo(json.dumps(_format_json_output(combined), separators=(",", ":")))
    elif output_format == "markdown":
        # Markdown output per S-094
        click.echo(format_as_markdown(results, verbose=verbose))
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


def _run_intent_validation(config: JigConfig) -> dict:
    """Run intent validation and return results dictionary.

    Args:
        config: JIG configuration.

    Returns:
        Dictionary mapping phase names to ValidationResult objects.
    """
    from jig.validation.models import ValidationResult

    spec_dir = config.paths.specifications
    outcome_dir = config.paths.outcomes
    src_dir = config.paths.source

    results = {}

    # Validate charter
    charter_path = config.paths.charter
    if charter_path.exists():
        results["charter"] = validate_charter_file(charter_path)
        charter_goals = _get_charter_goals(charter_path)
    else:
        results["charter"] = ValidationResult(passed=True, phase_name="charter", items_checked=0)
        charter_goals = set()

    # Validate specifications
    if spec_dir.exists():
        results["specifications"] = validate_specification_files(spec_dir)
    else:
        results["specifications"] = ValidationResult(passed=True, phase_name="specifications", items_checked=0)

    # Validate outcomes
    if outcome_dir.exists():
        results["outcomes"] = validate_outcome_files(outcome_dir)
        results["outcome_completeness"] = validate_outcome_completeness(outcome_dir)
    else:
        results["outcomes"] = ValidationResult(passed=True, phase_name="outcomes", items_checked=0)
        results["outcome_completeness"] = ValidationResult(passed=True, phase_name="outcome completeness", items_checked=0)

    # Validate architecture files
    arch_dir = config.paths.architecture
    if arch_dir.exists() and charter_goals:
        spec_ids = _get_all_spec_ids(spec_dir) if spec_dir.exists() else set()
        results["architecture"] = validate_architecture_files(arch_dir, charter_goals, spec_ids)
    else:
        results["architecture"] = ValidationResult(passed=True, phase_name="architecture", items_checked=0)

    # Validate goal references
    if charter_path.exists() and outcome_dir.exists():
        results["goal_references"] = validate_goal_references(
            charter_path,
            outcome_dir,
            arch_dir if arch_dir.exists() else None,
        )
    else:
        results["goal_references"] = ValidationResult(passed=True, phase_name="goal references", items_checked=0)

    # Validate specification coverage
    if spec_dir.exists() and outcome_dir.exists():
        results["specification_coverage"] = validate_specification_coverage(spec_dir, outcome_dir)
    else:
        results["specification_coverage"] = ValidationResult(passed=True, phase_name="specification coverage", items_checked=0)

    # Validate bidirectional consistency (S-095)
    if spec_dir.exists() and outcome_dir.exists():
        arch_dir = config.paths.architecture
        results["bidirectional_consistency"] = validate_bidirectional_consistency(
            spec_dir,
            outcome_dir,
            arch_dir,
        )
    else:
        results["bidirectional_consistency"] = ValidationResult(passed=True, phase_name="bidirectional consistency", items_checked=0)

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
        results["decorators"] = ValidationResult(passed=True, phase_name="decorators", items_checked=0)

    return results


def _run_bricks_validation(config: JigConfig) -> dict:
    """Run bricks validation and return results dictionary.

    Args:
        config: JIG configuration.

    Returns:
        Dictionary mapping phase names to ValidationResult objects.
    """
    bricks_file = config.paths.bricks
    impl_graph = config.paths.generated / "implementation-graph.ndjson"

    results = {}

    # Validate brick definitions
    definitions_result = validate_brick_definitions(bricks_file, impl_graph)
    results["brick_definitions"] = definitions_result

    # If graph not found, return early
    if any(err.code == "GRAPH_NOT_FOUND" for err in definitions_result.errors):
        return results

    # Validate tower format
    results["tower_format"] = validate_tower_format(bricks_file)

    # Validate brick partition
    results["brick_partition"] = validate_brick_partition(bricks_file, impl_graph)

    # Validate brick layer constraints
    if definitions_result.passed:
        results["layer_constraints"] = validate_brick_layer_constraints(bricks_file, impl_graph)

    # Validate brick cycles
    results["brick_cycles"] = validate_brick_cycles(bricks_file, impl_graph)

    # Validate tower isolation
    if _has_towers(bricks_file):
        results["tower_isolation"] = validate_tower_isolation(bricks_file, impl_graph)

    return results


@jig.implements("S-025", "S-026", "S-065", "S-070", "S-093", "S-094")
def validate_full_command(
    config: JigConfig,
    output_format: str = "human",
    skip_rebuild: bool = False,
    verbose: bool = False,
) -> int:
    """
    Run full validation (intent + bricks if graph exists).

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
    ensure_graphs_current(["impl", "verify", "intent"], config, skip_rebuild=skip_rebuild)

    # For human output, run sub-commands directly
    if output_format == "human":
        click.echo("=== Validating Intent ===\n")
        intent_exit_code = validate_intent_command(config, output_format, skip_rebuild=True, verbose=verbose)

        # Conditionally run brick validation if implementation graph exists
        impl_graph = config.paths.generated / "implementation-graph.ndjson"
        if impl_graph.exists():
            click.echo("\n=== Validating Bricks ===\n")
            brick_exit_code = validate_bricks_command(config, output_format, skip_rebuild=True, verbose=verbose)
        else:
            click.echo("\n=== Skipping Brick Validation ===")
            click.echo("(Implementation graph not found)")
            brick_exit_code = 0

        # Overall result
        if intent_exit_code == 0 and brick_exit_code == 0:
            click.echo("\n✓ All validations passed.")
        else:
            click.echo("\n✗ Validation failed.")

        return 0 if (intent_exit_code == 0 and brick_exit_code == 0) else 1

    # For JSON/markdown output, collect all results and output once
    all_results = {}

    # Run intent validation (collect results without output)
    intent_results = _run_intent_validation(config)
    all_results.update(intent_results)

    # Run brick validation if graph exists
    impl_graph = config.paths.generated / "implementation-graph.ndjson"
    if impl_graph.exists():
        brick_results = _run_bricks_validation(config)
        all_results.update(brick_results)

    # Format output
    if output_format == "json":
        import json
        click.echo(json.dumps(_format_json_output(all_results), separators=(",", ":")))
    elif output_format == "markdown":
        click.echo(format_as_markdown(all_results, verbose=verbose))

    # Return exit code
    all_passed = all(r.passed for r in all_results.values())
    return 0 if all_passed else 1


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
