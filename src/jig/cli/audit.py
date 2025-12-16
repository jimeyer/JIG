"""Audit CLI commands for JIG.

Provides commands for running coverage audits to determine T→F relationships.
"""

import click

import jig
from jig.config import JigConfig


@jig.implements("S-066", "S-067")
def coverage_command(config: JigConfig) -> int:
    """Run full coverage audit pipeline.

    Executes the complete coverage audit workflow:
    1. Verify required graphs exist
    2. Run pytest with coverage instrumentation
    3. Extract T→F edges from coverage data
    4. Write edges to NDJSON record file
    5. Clean up .coverage file

    Args:
        config: JIG configuration with project paths.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    from jig.audit.coverage import (
        ensure_audits_directory,
        extract_tf_edges,
        run_coverage_collection,
    )
    from jig.audit.record_writer import cleanup_coverage_file, write_coverage_record

    click.echo("Running coverage audit...")

    # Step 1: Verify required graphs exist
    impl_graph_path = config.paths.generated / "implementation-graph.ndjson"
    verify_graph_path = config.paths.generated / "verification-graph.ndjson"

    if not impl_graph_path.exists():
        click.echo(
            "Error: Implementation graph not found.", err=True
        )
        click.echo(
            "Run 'jigy rebuild impl' first to generate it.", err=True
        )
        return 1

    if not verify_graph_path.exists():
        click.echo(
            "Error: Verification graph not found.", err=True
        )
        click.echo(
            "Run 'jigy rebuild verify' first to generate it.", err=True
        )
        return 1

    # Step 2: Ensure directory structure exists
    audits_dir = ensure_audits_directory(config)

    # Step 3: Run pytest with coverage
    click.echo("  Running tests with coverage...")
    exit_code, coverage_file = run_coverage_collection(config)

    if not coverage_file.exists():
        click.echo("Error: Coverage data not generated.", err=True)
        return 1

    # Note: Continue even if tests fail (exit_code != 0)
    # We still want to record what coverage was collected
    if exit_code != 0:
        click.echo(f"  Some tests failed (exit code {exit_code})")
        click.echo("  Continuing with coverage extraction...")

    # Step 4: Extract T→F edges
    click.echo("  Extracting T→F edges...")
    edges = extract_tf_edges(coverage_file, impl_graph_path, config.project_root)
    click.echo(f"  Found {len(edges)} T→F edges")

    # Step 5: Write record file
    click.echo("  Writing record file...")
    record_path = write_coverage_record(
        edges=edges,
        output_dir=audits_dir,
        impl_graph_path=impl_graph_path,
        verify_graph_path=verify_graph_path,
    )

    # Step 6: Clean up .coverage file
    cleanup_coverage_file(coverage_file)

    # Summary
    click.echo()
    click.echo(f"Wrote {len(edges)} edges to {record_path}")

    return 0
