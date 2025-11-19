# @jig C-CLI-001 implements:S-JIG-002 subsystem:core interface:public
"""Main CLI entry point for JIG."""

import click


@click.group()
@click.version_option(version="0.1.0", prog_name="jigy")
def cli() -> None:
    """JIG (Jig Intent Graph) - constraint-driven development tool.

    JIG helps you capture and track design decisions, constraints, and
    requirements as an Intent Graph using simple text files.
    """
    pass


# Import and register subcommands
from jig.cli.init import init  # noqa: E402
from jig.cli.node import node  # noqa: E402

cli.add_command(init)
cli.add_command(node)


if __name__ == "__main__":
    cli()
