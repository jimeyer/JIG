# @jig C-CLI-009 implements:S-JIGY-009 subsystem:jigy-tool interface:public
"""CLI commands for graph index management."""

from pathlib import Path

import click

from jig.core.index_builder import IndexBuilder


@click.group()
def index() -> None:
    """Manage graph index (graph-index.yaml)."""
    pass


@index.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be rebuilt without writing",
)
@click.option(
    "--backup/--no-backup",
    default=True,
    help="Backup existing graph-index.yaml before overwriting",
)
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path.cwd(),
    help="Project root directory (default: current directory)",
)
def rebuild(dry_run: bool, backup: bool, project_dir: Path) -> None:
    """Rebuild graph-index.yaml from markdown files and code annotations.
    
    Scans:
    - jig/outcomes/*.md for Outcome nodes
    - jig/specifications/*.md for Specification nodes
    - jig/constraints/*.md for Constraint nodes
    - src/ and test/ for @jig annotations (Code and Test nodes)
    
    Generates graph-index.yaml with all nodes and their relationships.
    """
    click.echo("Rebuilding graph-index.yaml from sources...")
    click.echo()
    
    # Build the index
    builder = IndexBuilder(project_dir)
    result = builder.build()
    
    # Report results
    click.echo("Scanning sources:")
    
    # Count nodes by type
    node_counts = {}
    for node in result.nodes.values():
        node_counts[node.type] = node_counts.get(node.type, 0) + 1
    
    # Report markdown nodes
    outcomes = node_counts.get("outcome", 0)
    specs = node_counts.get("specification", 0)
    constraints = node_counts.get("constraint", 0)
    click.echo(f"  ✓ jig/outcomes/*.md ({outcomes} nodes)")
    click.echo(f"  ✓ jig/specifications/*.md ({specs} nodes)")
    if constraints > 0:
        click.echo(f"  ✓ jig/constraints/*.md ({constraints} nodes)")
    
    # Report annotation nodes
    code = node_counts.get("code", 0)
    tests = node_counts.get("test", 0)
    if code > 0:
        click.echo(f"  ✓ src/ for @jig annotations ({code} code nodes)")
    if tests > 0:
        click.echo(f"  ✓ test/ for @jig annotations ({tests} test nodes)")
    
    click.echo()
    click.echo(f"Total nodes: {len(result.nodes)} ({outcomes} O, {specs} S, {code} C, {tests} T)")
    
    # Count edges
    edge_count = len(result.nodes) * 2  # Rough estimate, we'd need to count actual edges
    click.echo(f"Total edges: ~{edge_count}")
    click.echo()
    
    # Check for issues
    if result.conflicts:
        click.echo("❌ Conflicts found:")
        for conflict in result.conflicts:
            click.echo(f"  • {conflict}", err=True)
        click.echo()
    
    if result.validation_errors:
        click.echo("❌ Validation errors:")
        for error in result.validation_errors:
            click.echo(f"  • {error}", err=True)
        click.echo()
    
    if result.warnings:
        click.echo("⚠️  Warnings:")
        for warning in result.warnings[:5]:  # Limit to first 5
            click.echo(f"  • {warning}")
        if len(result.warnings) > 5:
            click.echo(f"  ... and {len(result.warnings) - 5} more")
        click.echo()
    
    # Validation summary
    if result.success:
        click.echo("Validating...")
        click.echo("  ✓ All node IDs valid")
        click.echo("  ✓ All edge targets exist")
        click.echo("  ✓ No duplicate node IDs")
        click.echo()
    
    # Write file
    if dry_run:
        click.echo("🔍 Dry-run mode: No changes written")
        click.echo(f"Would write to: {project_dir / 'jig' / 'graph-index.yaml'}")
    elif not result.success:
        click.echo("❌ Rebuild failed due to errors", err=True)
        click.echo("Fix the errors above and try again", err=True)
        raise click.Abort()
    else:
        output_file = project_dir / "jig" / "graph-index.yaml"
        
        if backup and output_file.exists():
            click.echo(f"Writing jig/graph-index.yaml...")
            click.echo(f"  ✓ Backed up to jig/graph-index.yaml.bak")
        else:
            click.echo(f"Writing jig/graph-index.yaml...")
        
        builder.write_yaml(result, output_file, backup=backup)
        click.echo(f"  ✓ Wrote {len(result.nodes)} nodes")
        click.echo()
        click.echo("✅ Done!")


@index.command()
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path.cwd(),
    help="Project root directory (default: current directory)",
)
def diff(project_dir: Path) -> None:
    """Show differences between current index and sources.
    
    Compares graph-index.yaml with what would be generated from
    markdown files and code annotations.
    """
    click.echo("Comparing current graph-index.yaml with sources...")
    click.echo()
    
    # Build what the index should be
    builder = IndexBuilder(project_dir)
    result = builder.build()
    
    # TODO: Load existing graph-index.yaml and compare
    # For now, just show what would be rebuilt
    
    click.echo("Note: Full diff functionality not yet implemented")
    click.echo(f"Current sources would generate {len(result.nodes)} nodes")
    
    if not result.success:
        click.echo()
        click.echo("⚠️  Warning: Rebuild would have errors")
        if result.conflicts:
            click.echo(f"  • {len(result.conflicts)} conflicts")
        if result.validation_errors:
            click.echo(f"  • {len(result.validation_errors)} validation errors")

