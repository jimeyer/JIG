"""CLI command for JIG project initialization."""

import json
from pathlib import Path

import click

import jig
from jig.cli.output import OutputFormat
from jig.init import InitResult, init_project, install_skills


def format_human_output(
    result: InitResult,
    skill_paths: list[Path],
    verbose: bool = False,
) -> str:
    """Format initialization result as human-readable output.

    Args:
        result: The InitResult from init_project (may be None if skills-only).
        skill_paths: List of skill paths created.
        verbose: Whether to include verbose details.

    Returns:
        Human-readable string output.
    """
    lines: list[str] = []

    all_paths = list(result.paths_created) + skill_paths if result else skill_paths

    if not all_paths:
        lines.append("JIG already initialized (nothing new created)")
    else:
        lines.append("JIG initialized successfully!")
        lines.append("")
        lines.append("Created:")
        for path in all_paths:
            # Show relative path for cleaner output
            lines.append(f"  {path}")

    return "\n".join(lines)


def format_json_output(
    result: InitResult | None,
    skill_paths: list[Path],
) -> str:
    """Format initialization result as JSON output.

    Args:
        result: The InitResult from init_project (may be None if skills-only).
        skill_paths: List of skill paths created.

    Returns:
        JSON string output.
    """
    all_paths = list(result.paths_created) + skill_paths if result else skill_paths
    success = (result.success if result else True) and True

    output = {
        "success": success,
        "paths_created": [str(p) for p in all_paths],
    }

    if result and result.error:
        output["error"] = result.error

    return json.dumps(output)


def format_markdown_output(
    result: InitResult | None,
    skill_paths: list[Path],
    verbose: bool = False,
) -> str:
    """Format initialization result as markdown output.

    Args:
        result: The InitResult from init_project (may be None if skills-only).
        skill_paths: List of skill paths created.
        verbose: Whether to include verbose details.

    Returns:
        Markdown string output.
    """
    lines: list[str] = []
    all_paths = list(result.paths_created) + skill_paths if result else skill_paths
    success = (result.success if result else True) and True

    lines.append("# JIG Initialization")
    lines.append("")
    lines.append(f"**Status:** {'Success' if success else 'Failed'}")
    lines.append("")

    if all_paths:
        lines.append("## Created Paths")
        lines.append("")
        for path in all_paths:
            lines.append(f"- `{path}`")
    else:
        lines.append("*Nothing new created (already initialized)*")

    if result and result.error:
        lines.append("")
        lines.append(f"**Error:** {result.error}")

    return "\n".join(lines)


@jig.implements("S-103")
def init_command(
    project_name: str | None,
    no_skills: bool,
    skills_only: bool,
    global_skills: bool,
    force: bool,
    output_format: OutputFormat,
    verbose: bool,
) -> int:
    """Execute the init command logic.

    Args:
        project_name: Project name for Charter filename.
        no_skills: If True, skip skill installation.
        skills_only: If True, only install skills.
        global_skills: If True, install skills to ~/.agent/skills/.
        force: If True, allow overwriting jig.toml.
        output_format: Output format (HUMAN, JSON, MARKDOWN).
        verbose: Whether to show verbose output.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    project_root = Path.cwd()
    result: InitResult | None = None
    skill_paths: list[Path] = []

    # Execute init based on flags
    if not skills_only:
        result = init_project(
            project_root=project_root,
            project_name=project_name,
            force=force,
        )
        if not result.success:
            if output_format == OutputFormat.JSON:
                click.echo(format_json_output(result, []))
            else:
                click.echo(f"Error: {result.error}", err=True)
            return 1

    if not no_skills:
        skill_paths = install_skills(
            project_root=project_root,
            global_install=global_skills,
        )

    # Format and display output
    if output_format == OutputFormat.JSON:
        click.echo(format_json_output(result, skill_paths))
    elif output_format == OutputFormat.MARKDOWN:
        click.echo(format_markdown_output(result, skill_paths, verbose))
    else:
        click.echo(format_human_output(result, skill_paths, verbose))

    return 0
