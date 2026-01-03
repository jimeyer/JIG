"""Rebuild CLI commands for JIG graphs."""

from pathlib import Path

import click

import jig
from jig.cli.discovery import find_project_root
from jig.config import JigConfig
from jig.staleness import collect_git_metadata


@jig.implements("S-058", "S-065", "S-068")
def rebuild_impl_command(config: JigConfig) -> int:
    """Rebuild implementation graph.

    Args:
        config: JIG configuration with resolved paths.

    Returns:
        Exit code (0 for success).
    """
    from jig.cli.validate import auto_validate_decorators
    from jig.impl_graph.builder import build_graph

    click.echo(f"Rebuilding implementation graph...")

    # Auto-validate decorators first
    if not auto_validate_decorators(config):
        return 1

    output_path = config.paths.generated / "implementation-graph.ndjson"

    # Collect git metadata for staleness detection (S-068)
    git_metadata = collect_git_metadata(config, [config.paths.source])

    graph = build_graph(
        project_root=config.project_root,
        source_dir=config.paths.source,
        output_path=output_path,
        exclude_patterns=None,
        verbose=False,
        strict=True,
        include_timestamp=True,
        git_metadata=git_metadata,
    )

    click.echo(f"  impl: {graph.node_count()} nodes, {graph.edge_count()} edges")
    return 0


@jig.implements("S-058", "S-065", "S-068")
def rebuild_intent_command(config: JigConfig) -> int:
    """Rebuild intent graph.

    Args:
        config: JIG configuration with resolved paths.

    Returns:
        Exit code (0 for success).
    """
    from jig.intent_graph.generator import generate_intent_graph

    click.echo(f"Rebuilding intent graph...")

    output_path = config.paths.generated / "intent-graph.ndjson"

    # Collect git metadata for staleness detection (S-068)
    # Intent graph inputs: specifications, outcomes, bricks
    git_metadata = collect_git_metadata(config, [
        config.paths.specifications,
        config.paths.outcomes,
        config.paths.bricks.parent,  # jig_root for bricks.yaml
    ])

    output_path, node_count, edge_count = generate_intent_graph(
        project_root=config.project_root,
        output_path=output_path,
        include_timestamp=True,
        git_metadata=git_metadata,
    )

    click.echo(f"  intent: {node_count} nodes, {edge_count} edges")
    return 0


@jig.implements("S-058", "S-065", "S-068")
def rebuild_verify_command(config: JigConfig) -> int:
    """Rebuild verification graph.

    Args:
        config: JIG configuration with resolved paths.

    Returns:
        Exit code (0 for success).
    """
    from jig.verification_graph.builder import build_verification_graph

    click.echo(f"Rebuilding verification graph...")

    output_path = config.paths.generated / "verification-graph.ndjson"

    # Collect git metadata for staleness detection (S-068)
    git_metadata = collect_git_metadata(config, [config.paths.tests])

    graph = build_verification_graph(
        project_root=config.project_root,
        test_dir=config.paths.tests,
        output_path=output_path,
        include_timestamp=True,
        git_metadata=git_metadata,
    )

    click.echo(f"  verify: {graph.node_count()} nodes, {graph.edge_count()} edges")
    return 0


@jig.implements("S-058", "S-065")
def rebuild_all_command(config: JigConfig) -> int:
    """Rebuild all three graphs in order: impl -> verify -> intent.

    Args:
        config: JIG configuration with resolved paths.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    exit_code = rebuild_impl_command(config)
    if exit_code != 0:
        return exit_code

    exit_code = rebuild_verify_command(config)
    if exit_code != 0:
        return exit_code

    exit_code = rebuild_intent_command(config)
    if exit_code != 0:
        return exit_code

    return 0


@jig.implements("S-059", "S-065", "S-068")
def align_command(config: JigConfig) -> int:
    """Run full alignment workflow: rebuild all graphs, validate, display summary.

    Args:
        config: JIG configuration with resolved paths.

    Returns:
        Exit code (0 if aligned, non-zero on failure).
    """
    from jig.cli.validate import auto_validate_decorators
    from jig.impl_graph.builder import build_graph
    from jig.intent_graph.generator import generate_intent_graph
    from jig.validation.bricks import validate_brick_definitions, validate_brick_partition
    from jig.validation.intent import (
        validate_outcome_files,
        validate_specification_files,
    )
    from jig.verification_graph.builder import build_verification_graph

    click.echo("Rebuilding graphs...")

    # Step 1: Auto-validate decorators
    if not auto_validate_decorators(config):
        return 1

    # Step 2: Rebuild impl graph
    impl_output = config.paths.generated / "implementation-graph.ndjson"
    try:
        impl_git_metadata = collect_git_metadata(config, [config.paths.source])
        impl_graph = build_graph(
            project_root=config.project_root,
            source_dir=config.paths.source,
            output_path=impl_output,
            exclude_patterns=None,
            verbose=False,
            strict=True,
            include_timestamp=True,
            git_metadata=impl_git_metadata,
        )
        click.echo(f"  impl: {impl_graph.node_count()} functions")
    except Exception as e:
        click.echo(f"  impl: FAILED - {e}", err=True)
        return 1

    # Step 3: Rebuild verify graph
    verify_output = config.paths.generated / "verification-graph.ndjson"
    try:
        verify_git_metadata = collect_git_metadata(config, [config.paths.tests])
        verify_graph = build_verification_graph(
            project_root=config.project_root,
            test_dir=config.paths.tests,
            output_path=verify_output,
            include_timestamp=True,
            git_metadata=verify_git_metadata,
        )
        click.echo(f"  verify: {verify_graph.node_count()} tests")
    except Exception as e:
        click.echo(f"  verify: FAILED - {e}", err=True)
        return 1

    # Step 4: Rebuild intent graph
    try:
        intent_output = config.paths.generated / "intent-graph.ndjson"
        intent_git_metadata = collect_git_metadata(config, [
            config.paths.specifications,
            config.paths.outcomes,
            config.paths.bricks.parent,
        ])
        intent_output, intent_nodes, intent_edges = generate_intent_graph(
            project_root=config.project_root,
            output_path=intent_output,
            include_timestamp=True,
            git_metadata=intent_git_metadata,
        )
        # Count specs and outcomes from the graph
        spec_dir = config.paths.specifications
        outcome_dir = config.paths.outcomes
        spec_count = len(list(spec_dir.glob("*.md"))) if spec_dir.exists() else 0
        outcome_count = len(list(outcome_dir.glob("*.md"))) if outcome_dir.exists() else 0
        click.echo(f"  intent: {spec_count} specs, {outcome_count} outcomes")
    except Exception as e:
        click.echo(f"  intent: FAILED - {e}", err=True)
        return 1

    # Step 5: Validate
    click.echo("\nValidating...")

    # Validate intent
    spec_dir = config.paths.specifications
    outcome_dir = config.paths.outcomes

    intent_ok = True
    if spec_dir.exists():
        spec_result = validate_specification_files(spec_dir)
        if not spec_result.passed:
            intent_ok = False
    if outcome_dir.exists():
        outcome_result = validate_outcome_files(outcome_dir)
        if not outcome_result.passed:
            intent_ok = False

    if intent_ok:
        click.echo("  intent: OK")
    else:
        click.echo("  intent: FAILED")
        return 1

    # Validate bricks
    bricks_file = config.paths.bricks
    if bricks_file.exists():
        def_result = validate_brick_definitions(bricks_file, impl_output)
        part_result = validate_brick_partition(bricks_file, impl_output)

        if def_result.passed and part_result.passed:
            # Count bricks and layers
            import yaml
            with open(bricks_file) as f:
                bricks_data = yaml.safe_load(f)
            brick_count = len(bricks_data.get("bricks", []))
            layers = set(b.get("layer", 0) for b in bricks_data.get("bricks", []))
            layer_count = len(layers)
            click.echo(f"  bricks: OK ({brick_count} bricks, {layer_count} layers)")
        else:
            click.echo("  bricks: FAILED")
            return 1
    else:
        click.echo("  bricks: OK (no bricks.yaml)")

    # Step 6: Summary
    click.echo("\nSummary:")

    # Count implemented and verified specs
    implemented_count = _count_implemented_specs(impl_output, spec_dir)
    verified_count = _count_verified_specs(verify_output, spec_dir)

    click.echo(f"  Specs: {spec_count} total ({implemented_count} implemented, {verified_count} verified)")
    click.echo("  Status: ALIGNED")

    return 0


def _count_implemented_specs(impl_graph_path: Path, spec_dir: Path) -> int:
    """Count how many specs have at least one implementing function."""
    import json

    if not impl_graph_path.exists() or not spec_dir.exists():
        return 0

    # Get all spec IDs
    spec_ids = set()
    for spec_file in spec_dir.glob("*.md"):
        spec_ids.add(spec_file.stem)

    # Read impl graph and find implemented specs
    # Nodes have "implements": ["S-001", "S-002"] arrays
    implemented = set()
    with open(impl_graph_path) as f:
        for line in f:
            node = json.loads(line)
            impl_list = node.get("implements", [])
            for spec_id in impl_list:
                if spec_id in spec_ids:
                    implemented.add(spec_id)

    return len(implemented)


def _count_verified_specs(verify_graph_path: Path, spec_dir: Path) -> int:
    """Count how many specs have at least one verifying test."""
    import json

    if not verify_graph_path.exists() or not spec_dir.exists():
        return 0

    # Get all spec IDs
    spec_ids = set()
    for spec_file in spec_dir.glob("*.md"):
        spec_ids.add(spec_file.stem)

    # Read verify graph and find verified specs
    # Nodes have "verifies": ["S-001", "S-002"] arrays
    verified = set()
    with open(verify_graph_path) as f:
        for line in f:
            node = json.loads(line)
            verify_list = node.get("verifies", [])
            for spec_id in verify_list:
                if spec_id in spec_ids:
                    verified.add(spec_id)

    return len(verified)

