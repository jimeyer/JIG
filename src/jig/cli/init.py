# @jig C-CLI-002 implements:S-JIG-002 subsystem:core interface:public
"""Initialize JIG directory structure in a project."""

import sys
from pathlib import Path

import click
import toml
import yaml

from jig.utils.io import ensure_dir, write_file


@click.command()
@click.option("--path", default=".", help="Directory to initialize (default: current)")
def init(path: str) -> None:
    """Initialize JIG structure in a project.

    Creates the directory structure and configuration files needed to start
    using JIG for constraint-driven development.

    Example:
        jigy init              # Initialize in current directory
        jigy init --path ./myproject  # Initialize in specific directory
    """
    project_path = Path(path).resolve()
    jig_dir = project_path / "jig"
    config_file = project_path / "jig.toml"

    # Check if already initialized (idempotency)
    if jig_dir.exists():
        click.echo(f"Error: JIG already initialized in {project_path}", err=True)
        click.echo(f"Found existing directory: {jig_dir}", err=True)
        click.echo("\nTo reinitialize, remove the jig/ directory first.", err=True)
        sys.exit(1)

    try:
        # Create directory structure
        ensure_dir(jig_dir / "outcomes")
        ensure_dir(jig_dir / "specifications")
        ensure_dir(jig_dir / "tests")
        ensure_dir(jig_dir / "constraints")

        # Create graph-index.yaml
        graph_index = {"version": "1.0", "nodes": []}
        graph_index_path = jig_dir / "graph-index.yaml"
        write_file(graph_index_path, yaml.dump(graph_index, sort_keys=False))

        # Create subsystems.yaml
        subsystems = {"subsystems": [{"name": "core", "description": "Core subsystem"}]}
        subsystems_path = jig_dir / "subsystems.yaml"
        write_file(subsystems_path, yaml.dump(subsystems, sort_keys=False))

        # Create jig.toml
        config_data = {
            "project": {
                "name": project_path.name,
                "intent_dir": "jig",
                "delta_dir": "jig/deltas",
                "templates_dir": "templates",
                "graph_index_file": "jig/graph-index.yaml",
                "subsystems_file": "jig/subsystems.yaml",
            }
        }
        write_file(config_file, toml.dumps(config_data))

        # Success message
        click.echo(f"✓ Initialized JIG in {project_path}")
        click.echo("\nCreated:")
        click.echo(f"  - {jig_dir / 'outcomes/'}")
        click.echo(f"  - {jig_dir / 'specifications/'}")
        click.echo(f"  - {jig_dir / 'tests/'}")
        click.echo(f"  - {jig_dir / 'constraints/'}")
        click.echo(f"  - {graph_index_path}")
        click.echo(f"  - {subsystems_path}")
        click.echo(f"  - {config_file}")
        click.echo("\nNext steps:")
        click.echo("  1. Create your first node: jigy node create --type outcome --id O-PROJ-001 --title \"Your outcome\"")
        click.echo("  2. Validate your graph: jigy validate")

        sys.exit(0)

    except PermissionError as e:
        click.echo("Error: Permission denied while creating JIG structure", err=True)
        click.echo(f"Details: {e}", err=True)
        sys.exit(2)
    except Exception as e:
        click.echo("Error: Failed to initialize JIG", err=True)
        click.echo(f"Details: {e}", err=True)
        sys.exit(1)
