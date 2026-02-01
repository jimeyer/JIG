"""Auto-rebuild helper for JIG commands.

Provides functions to check staleness and rebuild graphs before command execution.
Implements S-070: Auto-Rebuild Before Commands.
"""

from typing import List, Optional

import click

import jig
from jig.config import JigConfig
from jig.staleness import is_stale


def get_rebuild_summary(rebuilt_count: int) -> str:
    """Generate a summary string for rebuild operations.

    Args:
        rebuilt_count: Number of graphs rebuilt.

    Returns:
        Summary string like "Rebuilt 3 graphs." or empty string if none rebuilt.
    """
    if rebuilt_count == 0:
        return ""
    elif rebuilt_count == 1:
        return "Rebuilt 1 graph."
    else:
        return f"Rebuilt {rebuilt_count} graphs."


@jig.implements("S-070")
def ensure_graphs_current(
    graph_types: List[str],
    config: JigConfig,
    skip_rebuild: bool = False,
    verbose: bool = False,
) -> str:
    """Ensure specified graphs are current, rebuilding if stale.

    Checks staleness for each specified graph type and rebuilds only
    those that are stale.

    Args:
        graph_types: List of graph types to check ("impl", "verify", "intent").
        config: JIG configuration.
        skip_rebuild: If True, skip staleness check entirely (--no-rebuild).
        verbose: If True, output detailed rebuild progress.

    Returns:
        Summary string (e.g., "Rebuilt 3 graphs.") or empty string if none rebuilt.
    """
    if skip_rebuild:
        return ""

    # Check which graphs are stale
    stale_graphs = [gt for gt in graph_types if is_stale(gt, config)]

    if not stale_graphs:
        return ""

    rebuilt_count = 0
    rebuild_details: List[str] = []

    # Rebuild each stale graph
    for graph_type in stale_graphs:
        try:
            detail = _rebuild_graph_quietly(graph_type, config, verbose=verbose)
            rebuilt_count += 1
            if detail:
                rebuild_details.append(detail)
        except Exception as e:
            # Log error but continue - don't fail the whole command
            click.echo(f"  {graph_type}: rebuild failed ({e})", err=True)

    # Build summary
    summary = get_rebuild_summary(rebuilt_count)

    # In verbose mode, show details
    if verbose and rebuild_details:
        click.echo("Rebuilding graphs...")
        for detail in rebuild_details:
            click.echo(f"  {detail}")
        # Show which graphs were up to date
        for graph_type in graph_types:
            if graph_type not in stale_graphs:
                click.echo(f"  {graph_type}: up to date")
        return summary

    return summary


def _rebuild_graph_quietly(graph_type: str, config: JigConfig, verbose: bool = False) -> str:
    """Rebuild a single graph with minimal output.

    Args:
        graph_type: One of "impl", "verify", "intent".
        config: JIG configuration.
        verbose: If True, return detailed info.

    Returns:
        Detail string for verbose output (e.g., "impl: 510 nodes, 1038 edges").
    """
    if graph_type == "impl":
        return _rebuild_impl_quietly(config, verbose)
    elif graph_type == "verify":
        return _rebuild_verify_quietly(config, verbose)
    elif graph_type == "intent":
        return _rebuild_intent_quietly(config, verbose)
    return ""


def _rebuild_impl_quietly(config: JigConfig, verbose: bool = False) -> str:
    """Rebuild implementation graph with minimal output.

    Returns:
        Detail string for verbose output.
    """
    from jig.cli.validate import auto_validate_decorators
    from jig.impl_graph.builder import build_graph
    from jig.staleness import collect_git_metadata

    # Auto-validate decorators first (silently - errors still shown)
    if not auto_validate_decorators(config):
        return "impl: validation failed"

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

    return f"impl: {graph.node_count()} nodes, {graph.edge_count()} edges"


def _rebuild_verify_quietly(config: JigConfig, verbose: bool = False) -> str:
    """Rebuild verification graph with minimal output.

    Returns:
        Detail string for verbose output.
    """
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

    return f"verify: {graph.node_count()} nodes, {graph.edge_count()} edges"


def _rebuild_intent_quietly(config: JigConfig, verbose: bool = False) -> str:
    """Rebuild intent graph with minimal output.

    Returns:
        Detail string for verbose output.
    """
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

    return f"intent: {node_count} nodes, {edge_count} edges"
