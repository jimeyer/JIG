"""Verify CLI commands for JIG verification graph."""

from pathlib import Path

import click

import jig
from jig.verification_graph.builder import build_verification_graph
from jig.verification_graph.discovery import discover_test_files


@jig.implements("S-056")
def verify_rebuild_command(
    project_root: Path,
    test_dir: Path | None,
    no_timestamp: bool,
) -> int:
    """Execute verification graph rebuild.

    Args:
        project_root: Root directory of the project.
        test_dir: Test directory to scan (defaults to project_root/tests).
        no_timestamp: Whether to exclude timestamp from metadata.

    Returns:
        Exit code (0 for success).
    """
    click.echo(f"Generating verification graph for {project_root}")

    # Step 1: Discover test files (for progress reporting)
    click.echo("\n[1] Discovering test files...")
    test_files = discover_test_files(project_root, test_dir)
    click.echo(f"    Found {len(test_files)} test files")

    # Step 2: Build verification graph
    click.echo("[2] Analyzing test functions...")
    output_path = project_root / "jig" / "generated" / "verification-graph.ndjson"

    graph = build_verification_graph(
        project_root=project_root,
        test_dir=test_dir,
        output_path=output_path,
        include_timestamp=not no_timestamp,
    )

    # Count verifies edges
    verifies_edges = sum(1 for e in graph.get_edges() if e.get("type") == "verifies")
    click.echo(f"    Found {graph.node_count()} tests")
    click.echo(f"    Found {verifies_edges} @jig.verifies edges")

    # Step 3: Report output
    click.echo("[3] Writing verification-graph.ndjson...")
    click.echo(f"    Wrote {graph.node_count()} nodes, {graph.edge_count()} edges")

    click.echo(f"\n✓ Verification graph generated successfully:")
    click.echo(f"  - Nodes: {graph.node_count()}")
    click.echo(f"  - Edges: {graph.edge_count()}")
    click.echo(f"  - Output: {output_path}")

    return 0
