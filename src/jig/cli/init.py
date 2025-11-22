# @jig C-CLI-002 implements:S-CLI-003,S-CLI-004,S-CLI-005 subsystem:cli interface:public
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
    using JIG for constraint-driven development. Idempotent - can be run
    multiple times safely. Verifies existing structure and repairs any
    missing components.

    Example:
        jigy init              # Initialize in current directory
        jigy init --path ./myproject  # Initialize in specific directory
        jigy init              # Run again to verify/repair structure
    """
    project_path = Path(path).resolve()
    jig_dir = project_path / "jig"
    config_file = project_path / "jig.toml"

    # Check if already initialized
    already_initialized = jig_dir.exists()
    
    if already_initialized:
        click.echo(f"JIG already initialized in {project_path}")
        click.echo("Checking structure...")
    
    # Track what was created vs repaired
    created: list[str] = []
    repaired: list[str] = []

    try:
        # Create/verify directory structure (O/S/C only - T nodes use @jig annotations)
        for dir_name in ["outcomes", "specifications", "constraints"]:
            dir_path = jig_dir / dir_name
            if not dir_path.exists():
                ensure_dir(dir_path)
                target_list = repaired if already_initialized else created
                target_list.append(str(dir_path))

        # Create/verify graph-index.yaml
        graph_index_path = jig_dir / "graph-index.yaml"
        if not graph_index_path.exists():
            graph_index = {"version": "1.0", "nodes": []}
            write_file(graph_index_path, yaml.dump(graph_index, sort_keys=False))
            target_list = repaired if already_initialized else created
            target_list.append(str(graph_index_path))

        # Create/verify subsystems.yaml
        subsystems_path = jig_dir / "subsystems.yaml"
        if not subsystems_path.exists():
            subsystems = {"subsystems": [{"name": "core", "description": "Core subsystem"}]}
            write_file(subsystems_path, yaml.dump(subsystems, sort_keys=False))
            target_list = repaired if already_initialized else created
            target_list.append(str(subsystems_path))

        # Create/verify .jigignore (Tier 1 exclusion filtering)
        jigignore_path = project_path / ".jigignore"
        if not jigignore_path.exists():
            jigignore_content = """# .jigignore - JIG scanning exclusions
# Syntax: gitignore-style patterns (supports *, **, ?)

# Test files (contain fixtures that pollute node index)
**/test_*.py
**/conftest.py

# Build artifacts
**/__pycache__/
**/*.pyc
.venv/
.pytest_cache/
.tox/
*.egg-info/
dist/
build/

# IDE files
.vscode/
.idea/
*.swp

# Add project-specific exclusions below
"""
            write_file(jigignore_path, jigignore_content)
            target_list = repaired if already_initialized else created
            target_list.append(str(jigignore_path))

        # Create/verify jig.toml (never overwrite if exists)
        if not config_file.exists():
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
            target_list = repaired if already_initialized else created
            target_list.append(str(config_file))

        # Success message - three scenarios
        if not already_initialized:
            # Scenario 1: First-time initialization
            click.echo(f"✓ Initialized JIG in {project_path}")
            click.echo("\nCreated:")
            for item in created:
                click.echo(f"  - {item}")
            click.echo("\nNext steps:")
            click.echo("  1. Create your first node: jigy node create --type outcome --id O-PROJ-001 --title \"Your outcome\"")
            click.echo("  2. Validate your graph: jigy validate")
        elif repaired:
            # Scenario 3: Repair (some missing)
            click.echo("✓ Repaired JIG structure")
            click.echo("\nRepaired:")
            for item in repaired:
                click.echo(f"  - {item}")
        else:
            # Scenario 2: Verification (all present)
            click.echo("✓ JIG structure verified - all components present")

        sys.exit(0)

    except PermissionError as e:
        click.echo("Error: Permission denied while creating JIG structure", err=True)
        click.echo(f"Details: {e}", err=True)
        sys.exit(2)
    except Exception as e:
        click.echo("Error: Failed to initialize JIG", err=True)
        click.echo(f"Details: {e}", err=True)
        sys.exit(1)
