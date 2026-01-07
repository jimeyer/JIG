"""Audit CLI commands for JIG.

Provides commands for running coverage audits to determine T->F relationships.
"""

import json
import time

import click

import jig
from jig.cli.output import OutputFormat
from jig.config import JigConfig


def _format_coverage_json(
    status: str,
    edge_count: int,
    record_path: str,
    test_exit_code: int,
    duration_ms: int,
    verbose: bool = False,
    edges: list | None = None,
) -> str:
    """Format coverage audit results as JSON.

    Args:
        status: Status string (success, failed)
        edge_count: Number of T->F edges found
        record_path: Path to the output record file
        test_exit_code: Exit code from pytest
        duration_ms: Duration in milliseconds
        verbose: If True, include edge details
        edges: List of TFEdge objects (required if verbose)

    Returns:
        JSON string
    """
    output = {
        "status": status,
        "edges_found": edge_count,
        "record_path": str(record_path),
        "test_exit_code": test_exit_code,
        "duration_ms": duration_ms,
    }

    if verbose and edges:
        output["edges"] = [
            {"test_id": e.test_id, "function_id": e.function_id}
            for e in edges
        ]

    return json.dumps(output)


def _format_coverage_markdown(
    status: str,
    edge_count: int,
    record_path: str,
    test_exit_code: int,
    duration_ms: int,
    verbose: bool = False,
    edges: list | None = None,
) -> str:
    """Format coverage audit results as markdown.

    Args:
        status: Status string (success, failed)
        edge_count: Number of T->F edges found
        record_path: Path to the output record file
        test_exit_code: Exit code from pytest
        duration_ms: Duration in milliseconds
        verbose: If True, include edge details
        edges: List of TFEdge objects (required if verbose)

    Returns:
        Markdown string
    """
    lines = ["# Coverage Audit Result", ""]
    lines.append(f"**Status:** {status.title()}")
    lines.append(f"**Duration:** {duration_ms}ms")
    lines.append(f"**Test Exit Code:** {test_exit_code}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **T->F Edges Found:** {edge_count}")
    lines.append(f"- **Record Path:** `{record_path}`")

    if verbose and edges:
        lines.append("")
        lines.append("## Edge Details")
        lines.append("")
        for e in edges:
            lines.append(f"- `{e.test_id}` -> `{e.function_id}`")

    return "\n".join(lines)


def _format_coverage_error_json(error_message: str, duration_ms: int = 0) -> str:
    """Format coverage audit error as JSON.

    Args:
        error_message: Error description
        duration_ms: Duration in milliseconds

    Returns:
        JSON string
    """
    return json.dumps({
        "status": "failed",
        "error": error_message,
        "duration_ms": duration_ms,
    })


def _format_coverage_error_markdown(error_message: str, duration_ms: int = 0) -> str:
    """Format coverage audit error as markdown.

    Args:
        error_message: Error description
        duration_ms: Duration in milliseconds

    Returns:
        Markdown string
    """
    lines = ["# Coverage Audit Result", ""]
    lines.append("**Status:** Failed")
    lines.append(f"**Duration:** {duration_ms}ms")
    lines.append("")
    lines.append("## Error")
    lines.append("")
    lines.append(f"{error_message}")
    return "\n".join(lines)


@jig.implements("S-066", "S-067", "S-070", "S-093")
def coverage_command(
    config: JigConfig,
    skip_rebuild: bool = False,
    output_format: OutputFormat = OutputFormat.HUMAN,
    verbose: bool = False,
) -> int:
    """Run full coverage audit pipeline.

    Executes the complete coverage audit workflow:
    1. Auto-rebuild stale impl + verify graphs
    2. Verify required graphs exist
    3. Run pytest with coverage instrumentation
    4. Extract T->F edges from coverage data
    5. Write edges to NDJSON record file
    6. Clean up .coverage file

    Args:
        config: JIG configuration with project paths.
        skip_rebuild: If True, skip auto-rebuild.
        output_format: Output format (HUMAN, JSON, MARKDOWN).
        verbose: If True, include additional output details.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    start_time = time.time()

    # Auto-rebuild stale impl + verify graphs before auditing (S-070)
    from jig.cli.auto_rebuild import ensure_graphs_current
    ensure_graphs_current(["impl", "verify"], config, skip_rebuild=skip_rebuild)
    from jig.audit.coverage import (
        ensure_audits_directory,
        extract_tf_edges,
        run_coverage_collection,
    )
    from jig.audit.record_writer import cleanup_coverage_file, write_coverage_record

    if output_format == OutputFormat.HUMAN:
        click.echo("Running coverage audit...")

    # Step 1: Verify required graphs exist
    impl_graph_path = config.paths.generated / "implementation-graph.ndjson"
    verify_graph_path = config.paths.generated / "verification-graph.ndjson"

    if not impl_graph_path.exists():
        duration_ms = int((time.time() - start_time) * 1000)
        error_msg = "Implementation graph not found. Run 'jigy rebuild impl' first to generate it."
        if output_format == OutputFormat.JSON:
            click.echo(_format_coverage_error_json(error_msg, duration_ms))
        elif output_format == OutputFormat.MARKDOWN:
            click.echo(_format_coverage_error_markdown(error_msg, duration_ms))
        else:
            click.echo("Error: Implementation graph not found.", err=True)
            click.echo("Run 'jigy rebuild impl' first to generate it.", err=True)
        return 1

    if not verify_graph_path.exists():
        duration_ms = int((time.time() - start_time) * 1000)
        error_msg = "Verification graph not found. Run 'jigy rebuild verify' first to generate it."
        if output_format == OutputFormat.JSON:
            click.echo(_format_coverage_error_json(error_msg, duration_ms))
        elif output_format == OutputFormat.MARKDOWN:
            click.echo(_format_coverage_error_markdown(error_msg, duration_ms))
        else:
            click.echo("Error: Verification graph not found.", err=True)
            click.echo("Run 'jigy rebuild verify' first to generate it.", err=True)
        return 1

    # Step 2: Ensure directory structure exists
    audits_dir = ensure_audits_directory(config)

    # Step 3: Run pytest with coverage
    if output_format == OutputFormat.HUMAN:
        click.echo("  Running tests with coverage...")
    test_exit_code, coverage_file = run_coverage_collection(config)

    if not coverage_file.exists():
        duration_ms = int((time.time() - start_time) * 1000)
        error_msg = "Coverage data not generated."
        if output_format == OutputFormat.JSON:
            click.echo(_format_coverage_error_json(error_msg, duration_ms))
        elif output_format == OutputFormat.MARKDOWN:
            click.echo(_format_coverage_error_markdown(error_msg, duration_ms))
        else:
            click.echo("Error: Coverage data not generated.", err=True)
        return 1

    # Note: Continue even if tests fail (test_exit_code != 0)
    # We still want to record what coverage was collected
    if test_exit_code != 0 and output_format == OutputFormat.HUMAN:
        click.echo(f"  Some tests failed (exit code {test_exit_code})")
        click.echo("  Continuing with coverage extraction...")

    # Step 4: Extract T->F edges
    if output_format == OutputFormat.HUMAN:
        click.echo("  Extracting T->F edges...")
    edges = extract_tf_edges(coverage_file, impl_graph_path, config.project_root)
    if output_format == OutputFormat.HUMAN:
        click.echo(f"  Found {len(edges)} T->F edges")

    # Step 5: Write record file
    if output_format == OutputFormat.HUMAN:
        click.echo("  Writing record file...")
    record_path = write_coverage_record(
        edges=edges,
        output_dir=audits_dir,
        impl_graph_path=impl_graph_path,
        verify_graph_path=verify_graph_path,
    )

    # Step 6: Clean up .coverage file
    cleanup_coverage_file(coverage_file)

    # Calculate duration
    duration_ms = int((time.time() - start_time) * 1000)

    # Output results based on format
    status = "success" if test_exit_code == 0 else "partial"

    if output_format == OutputFormat.JSON:
        click.echo(_format_coverage_json(
            status=status,
            edge_count=len(edges),
            record_path=str(record_path),
            test_exit_code=test_exit_code,
            duration_ms=duration_ms,
            verbose=verbose,
            edges=edges if verbose else None,
        ))
    elif output_format == OutputFormat.MARKDOWN:
        click.echo(_format_coverage_markdown(
            status=status,
            edge_count=len(edges),
            record_path=str(record_path),
            test_exit_code=test_exit_code,
            duration_ms=duration_ms,
            verbose=verbose,
            edges=edges if verbose else None,
        ))
    else:
        # Human format
        click.echo()
        click.echo(f"Wrote {len(edges)} edges to {record_path}")
        if verbose:
            click.echo()
            click.echo("Edge details:")
            for edge in edges:
                click.echo(f"  {edge.test_id} -> {edge.function_id}")

    return 0
