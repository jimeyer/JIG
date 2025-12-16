"""Audit CLI commands for JIG.

Provides commands for running coverage audits to determine T→F relationships.
"""

import click

import jig
from jig.config import JigConfig


@jig.implements("S-066")
def coverage_command(config: JigConfig) -> int:
    """Run coverage audit to collect T→F edges.

    Executes pytest with coverage instrumentation to determine which
    tests execute which functions.

    Args:
        config: JIG configuration with project paths.

    Returns:
        Exit code (0 for success, non-zero on test failures).
    """
    from jig.audit.coverage import ensure_audits_directory, run_coverage_collection

    click.echo("Running coverage audit...")

    # Ensure directory structure exists
    audits_dir = ensure_audits_directory(config)
    click.echo(f"  Records directory: {audits_dir}")

    # Run pytest with coverage
    click.echo("  Running tests with coverage...")
    exit_code, coverage_file = run_coverage_collection(config)

    if exit_code == 0:
        click.echo(f"  Coverage data written to: {coverage_file}")
        click.echo("Coverage collection complete.")
    else:
        click.echo(f"  Some tests failed (exit code {exit_code})")
        click.echo(f"  Coverage data still written to: {coverage_file}")

    return exit_code
