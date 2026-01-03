"""Auto-rebuild helper for JIG commands.

Provides functions to check staleness and rebuild graphs before command execution.
Implements S-070: Auto-Rebuild Before Commands.
"""

from typing import List

import click

import jig
from jig.config import JigConfig
from jig.staleness import is_stale


@jig.implements("S-070")
def ensure_graphs_current(
    graph_types: List[str],
    config: JigConfig,
    skip_rebuild: bool = False,
) -> None:
    """Ensure specified graphs are current, rebuilding if stale.

    Checks staleness for each specified graph type and rebuilds only
    those that are stale. Outputs status messages when rebuilding.

    Args:
        graph_types: List of graph types to check ("impl", "verify", "intent").
        config: JIG configuration.
        skip_rebuild: If True, skip staleness check entirely (--no-rebuild).
    """
    if skip_rebuild:
        return

    # Check which graphs are stale
    stale_graphs = [gt for gt in graph_types if is_stale(gt, config)]

    if not stale_graphs:
        return

    # Output header
    click.echo("Graphs stale, rebuilding...")

    # Import rebuild functions (avoid circular import)
    from jig.cli.rebuild import (
        rebuild_impl_command,
        rebuild_intent_command,
        rebuild_verify_command,
    )

    rebuild_funcs = {
        "impl": rebuild_impl_command,
        "verify": rebuild_verify_command,
        "intent": rebuild_intent_command,
    }

    # Rebuild each stale graph
    for graph_type in stale_graphs:
        if graph_type in rebuild_funcs:
            # Note: rebuild commands echo their own output ("Rebuilding X graph...")
            # We suppress that for auto-rebuild by not calling the full command
            try:
                _rebuild_graph_quietly(graph_type, config)
            except Exception as e:
                # Log error but continue - don't fail the whole command
                click.echo(f"  {graph_type}: rebuild failed ({e})", err=True)

    # Show which graphs were up to date
    for graph_type in graph_types:
        if graph_type not in stale_graphs:
            click.echo(f"  {graph_type}: up to date")


def _rebuild_graph_quietly(graph_type: str, config: JigConfig) -> None:
    """Rebuild a single graph with minimal output.

    Args:
        graph_type: One of "impl", "verify", "intent".
        config: JIG configuration.
    """
    if graph_type == "impl":
        _rebuild_impl_quietly(config)
    elif graph_type == "verify":
        _rebuild_verify_quietly(config)
    elif graph_type == "intent":
        _rebuild_intent_quietly(config)


def _rebuild_impl_quietly(config: JigConfig) -> None:
    """Rebuild implementation graph with minimal output."""
    from jig.cli.validate import auto_validate_decorators
    from jig.impl_graph.builder import build_graph
    from jig.staleness import collect_git_metadata

    # Auto-validate decorators first (silently - errors still shown)
    if not auto_validate_decorators(config):
        return

    output_path = config.paths.generated / "implementation-graph.ndjson"
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


def _rebuild_verify_quietly(config: JigConfig) -> None:
    """Rebuild verification graph with minimal output."""
    from jig.staleness import collect_git_metadata
    from jig.verification_graph.builder import build_verification_graph

    output_path = config.paths.generated / "verification-graph.ndjson"
    git_metadata = collect_git_metadata(config, [config.paths.tests])

    graph = build_verification_graph(
        project_root=config.project_root,
        test_dir=config.paths.tests,
        output_path=output_path,
        include_timestamp=True,
        git_metadata=git_metadata,
    )

    click.echo(f"  verify: {graph.node_count()} nodes, {graph.edge_count()} edges")


def _rebuild_intent_quietly(config: JigConfig) -> None:
    """Rebuild intent graph with minimal output."""
    from jig.intent_graph.generator import generate_intent_graph
    from jig.staleness import collect_git_metadata

    output_path = config.paths.generated / "intent-graph.ndjson"
    git_metadata = collect_git_metadata(config, [
        config.paths.specifications,
        config.paths.outcomes,
        config.paths.bricks.parent,
    ])

    output_path, node_count, edge_count = generate_intent_graph(
        project_root=config.project_root,
        output_path=output_path,
        include_timestamp=True,
        git_metadata=git_metadata,
    )

    click.echo(f"  intent: {node_count} nodes, {edge_count} edges")
