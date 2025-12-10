"""Rebuild CLI commands for JIG graphs."""

from pathlib import Path

import click

import jig
from jig.cli.discovery import find_project_root


@jig.implements("S-058")
def rebuild_impl_command(project_root: Path) -> int:
    """Rebuild implementation graph.

    Args:
        project_root: Root directory of the project.

    Returns:
        Exit code (0 for success).
    """
    from jig.cli.validate import auto_validate_decorators
    from jig.impl_graph.builder import build_graph

    click.echo(f"Rebuilding implementation graph...")

    # Auto-validate decorators first
    if not auto_validate_decorators(project_root):
        return 1

    output_path = project_root / "jig" / "generated" / "implementation-graph.ndjson"

    graph = build_graph(
        project_root=project_root,
        source_dir=None,
        output_path=output_path,
        exclude_patterns=None,
        verbose=False,
        strict=True,
        include_timestamp=True,
    )

    click.echo(f"  impl: {graph.node_count()} nodes, {graph.edge_count()} edges")
    return 0


@jig.implements("S-058")
def rebuild_intent_command(project_root: Path) -> int:
    """Rebuild intent graph.

    Args:
        project_root: Root directory of the project.

    Returns:
        Exit code (0 for success).
    """
    from jig.intent_graph.generator import generate_intent_graph

    click.echo(f"Rebuilding intent graph...")

    output_path, node_count, edge_count = generate_intent_graph(
        project_root=project_root,
        output_path=None,
        include_timestamp=True,
    )

    click.echo(f"  intent: {node_count} nodes, {edge_count} edges")
    return 0


@jig.implements("S-058")
def rebuild_verify_command(project_root: Path) -> int:
    """Rebuild verification graph.

    Args:
        project_root: Root directory of the project.

    Returns:
        Exit code (0 for success).
    """
    from jig.verification_graph.builder import build_verification_graph

    click.echo(f"Rebuilding verification graph...")

    output_path = project_root / "jig" / "generated" / "verification-graph.ndjson"

    graph = build_verification_graph(
        project_root=project_root,
        test_dir=None,
        output_path=output_path,
        include_timestamp=True,
    )

    click.echo(f"  verify: {graph.node_count()} nodes, {graph.edge_count()} edges")
    return 0


@jig.implements("S-058")
def rebuild_all_command(project_root: Path) -> int:
    """Rebuild all three graphs in order: impl -> verify -> intent.

    Args:
        project_root: Root directory of the project.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    exit_code = rebuild_impl_command(project_root)
    if exit_code != 0:
        return exit_code

    exit_code = rebuild_verify_command(project_root)
    if exit_code != 0:
        return exit_code

    exit_code = rebuild_intent_command(project_root)
    if exit_code != 0:
        return exit_code

    return 0
