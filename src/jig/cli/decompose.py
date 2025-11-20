# @jig C-NESTED-007 implements:S-NESTED-004 subsystem:decompose interface:public
"""Decompose commands for subsystem boundary analysis."""

import sys

import click

from jig.core.config import load_config
from jig.core.graph import Graph
from jig.decompose.metrics import calculate_all_metrics


@click.group()
def decompose() -> None:
    """Analyze subsystem boundaries and decomposability."""
    pass


@decompose.command()
@click.option(
    "--subsystem",
    help="Analyze specific subsystem subtree (e.g., 'core' or 'crdt.ser')",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "yaml"]),
    default="table",
    help="Output format",
)
def metrics(subsystem: str | None, output_format: str) -> None:
    """Calculate decomposability health scores.

    Displays:
    - Modularity score (Newman algorithm)
    - Per-subsystem coupling ratios
    - Average coupling ratio
    - Hierarchical breakdown for nested subsystems

    Examples:
        jigy decompose metrics
        jigy decompose metrics --subsystem crdt
        jigy decompose metrics --format yaml
    """
    config = load_config()

    try:
        graph = Graph.load_from_dir(config.intent_dir)
    except FileNotFoundError:
        click.echo(click.style("Error: Intent directory not found", fg="red"))
        click.echo("Have you run 'jigy init' to initialize this project?")
        sys.exit(3)

    if subsystem:
        # Verify subsystem exists
        subsys = graph.get_subsystem_by_path(subsystem)
        if not subsys:
            click.echo(
                click.style(f"Error: Subsystem '{subsystem}' not found", fg="red")
            )
            sys.exit(1)

        click.echo(
            click.style(f"Analyzing subsystem '{subsystem}'...\n", bold=True)
        )

        # For subsystem analysis, we calculate metrics for just that subtree
        # We do this by temporarily filtering the graph
        # Note: This is a simplified approach for WU22
        # A more complete implementation would create a subgraph
        from jig.decompose.metrics import calculate_coupling_ratio

        try:
            subsys_metrics = calculate_coupling_ratio(subsystem, graph)
        except ValueError as e:
            click.echo(click.style(f"Error: {e}", fg="red"))
            sys.exit(1)

        if output_format == "yaml":
            import yaml

            data = {
                "subsystem": subsys_metrics.name,
                "node_count": subsys_metrics.node_count,
                "internal_edges": subsys_metrics.internal_edges,
                "external_edges": subsys_metrics.external_edges,
                "coupling_ratio": (
                    subsys_metrics.coupling_ratio
                    if subsys_metrics.coupling_ratio != float("inf")
                    else "infinity"
                ),
            }
            click.echo(yaml.dump(data, default_flow_style=False))
        else:
            # Table format
            click.echo(click.style(f"Subsystem: {subsys_metrics.name}", bold=True))
            click.echo(f"  Nodes: {subsys_metrics.node_count}")
            click.echo(f"  Internal edges: {subsys_metrics.internal_edges}")
            click.echo(f"  External edges: {subsys_metrics.external_edges}")

            if subsys_metrics.coupling_ratio == float("inf"):
                ratio_str = "∞ (perfect isolation)"
                color = "green"
            elif subsys_metrics.coupling_ratio >= 3.0:
                ratio_str = f"{subsys_metrics.coupling_ratio:.2f} (good)"
                color = "green"
            elif subsys_metrics.coupling_ratio >= 1.0:
                ratio_str = f"{subsys_metrics.coupling_ratio:.2f} (moderate)"
                color = "yellow"
            else:
                ratio_str = f"{subsys_metrics.coupling_ratio:.2f} (weak)"
                color = "red"

            click.echo(f"  Coupling ratio: " + click.style(ratio_str, fg=color))

    else:
        # Analyze entire graph
        if output_format != "yaml":
            click.echo(click.style("Calculating metrics...\n", bold=True))

        all_metrics = calculate_all_metrics(graph)

        if output_format == "yaml":
            import yaml

            data = {
                "modularity": all_metrics.modularity,
                "subsystem_count": all_metrics.subsystem_count,
                "avg_coupling_ratio": all_metrics.avg_coupling_ratio,
                "subsystems": {
                    name: {
                        "node_count": m.node_count,
                        "internal_edges": m.internal_edges,
                        "external_edges": m.external_edges,
                        "coupling_ratio": (
                            m.coupling_ratio if m.coupling_ratio != float("inf") else "infinity"
                        ),
                    }
                    for name, m in all_metrics.subsystems.items()
                },
            }
            click.echo(yaml.dump(data, default_flow_style=False, sort_keys=False))
        else:
            # Table format with hierarchical display
            _display_metrics_table(all_metrics, graph)


def _display_metrics_table(metrics, graph: Graph) -> None:
    """Display metrics in table format with hierarchical structure."""
    # Overall scores
    click.echo(click.style("Overall Metrics", bold=True))
    click.echo("")

    # Modularity score with interpretation
    mod_score = metrics.modularity
    if mod_score >= 0.3:
        mod_str = f"{mod_score:.3f} (good modular structure)"
        mod_color = "green"
    elif mod_score >= 0.2:
        mod_str = f"{mod_score:.3f} (moderate structure)"
        mod_color = "yellow"
    else:
        mod_str = f"{mod_score:.3f} (weak structure)"
        mod_color = "yellow"

    click.echo(f"  Modularity: " + click.style(mod_str, fg=mod_color))
    click.echo(f"  Subsystems: {metrics.subsystem_count}")
    click.echo(f"  Average coupling ratio: {metrics.avg_coupling_ratio:.2f}")

    # Per-subsystem breakdown (hierarchical)
    click.echo("")
    click.echo(click.style("Per-Subsystem Metrics", bold=True))
    click.echo("")

    # Display in hierarchical order
    def display_subsystem(subsystem, indent=""):
        """Recursively display subsystem metrics."""
        path = subsystem.full_path
        if path in metrics.subsystems:
            m = metrics.subsystems[path]

            # Format coupling ratio with color
            if m.coupling_ratio == float("inf"):
                ratio_str = "∞"
                color = "green"
            elif m.coupling_ratio >= 3.0:
                ratio_str = f"{m.coupling_ratio:.2f}"
                color = "green"
            elif m.coupling_ratio >= 1.0:
                ratio_str = f"{m.coupling_ratio:.2f}"
                color = "yellow"
            else:
                ratio_str = f"{m.coupling_ratio:.2f}"
                color = "red"

            click.echo(
                f"{indent}{subsystem.name}: "
                f"{m.node_count} nodes, "
                f"{m.internal_edges}↔{m.external_edges} edges, "
                f"ratio=" + click.style(ratio_str, fg=color)
            )

            # Recursively display children with increased indent
            for child in subsystem.subsystems.values():
                display_subsystem(child, indent + "  ")

    # Display root subsystems
    for root in sorted(graph.subsystems.values(), key=lambda s: s.name):
        display_subsystem(root)


@decompose.command()
@click.option(
    "--output",
    type=click.Path(),
    help="Output file path (default: stdout)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["markdown", "yaml"]),
    default="markdown",
    help="Output format",
)
def report(output: str | None, output_format: str) -> None:
    """Generate decomposability analysis report.

    Creates a comprehensive report including:
    - Overall modularity score
    - Per-subsystem coupling metrics
    - Hierarchical breakdown
    - Constraint compliance (v7)
    - Recommendations

    Examples:
        jigy decompose report
        jigy decompose report --output metrics.md
        jigy decompose report --format yaml
    """
    config = load_config()

    try:
        graph = Graph.load_from_dir(config.intent_dir)
    except FileNotFoundError:
        click.echo(click.style("Error: Intent directory not found", fg="red"))
        click.echo("Have you run 'jigy init' to initialize this project?")
        sys.exit(3)

    click.echo(click.style("Generating decomposability report...\n", bold=True))
    all_metrics = calculate_all_metrics(graph)

    if output_format == "markdown":
        report_content = _generate_markdown_report(all_metrics, graph)
    else:  # yaml
        report_content = _generate_yaml_report(all_metrics, graph)

    if output:
        # Write to file
        from pathlib import Path

        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_content)
        click.echo(click.style(f"Report written to {output}", fg="green"))
    else:
        # Print to stdout
        click.echo(report_content)


def _generate_markdown_report(metrics, graph: Graph) -> str:
    """Generate markdown format report."""
    lines = []

    lines.append("# Decomposability Analysis Report")
    lines.append("")
    lines.append(f"**Generated:** {_get_timestamp()}")
    lines.append("")

    # Overall metrics
    lines.append("## Overall Metrics")
    lines.append("")
    lines.append(f"- **Modularity:** {metrics.modularity:.3f}")
    lines.append(f"- **Subsystem Count:** {metrics.subsystem_count}")
    lines.append(f"- **Average Coupling Ratio:** {metrics.avg_coupling_ratio:.2f}")
    lines.append("")

    # Interpretation
    lines.append("### Interpretation")
    lines.append("")
    if metrics.modularity >= 0.3:
        lines.append("✅ **Good modular structure** - Subsystems are well-defined")
    elif metrics.modularity >= 0.2:
        lines.append("⚠️  **Moderate structure** - Some improvement possible")
    else:
        lines.append("❌ **Weak structure** - Consider refactoring subsystem boundaries")
    lines.append("")

    # Per-subsystem metrics
    lines.append("## Per-Subsystem Metrics")
    lines.append("")

    def format_subsystem_section(subsystem, level=3):
        """Recursively format subsystem metrics."""
        path = subsystem.full_path
        if path in metrics.subsystems:
            m = metrics.subsystems[path]

            lines.append(f"{'#' * level} {subsystem.name}")
            lines.append("")
            lines.append(f"- **Path:** `{path}`")
            lines.append(f"- **Nodes:** {m.node_count}")
            lines.append(f"- **Internal Edges:** {m.internal_edges}")
            lines.append(f"- **External Edges:** {m.external_edges}")

            if m.coupling_ratio == float("inf"):
                lines.append(f"- **Coupling Ratio:** ∞ (perfect isolation)")
            else:
                lines.append(f"- **Coupling Ratio:** {m.coupling_ratio:.2f}")
            lines.append("")

            # Show constraints if any
            constraints = graph.get_constraints_for_subsystem(path)
            if constraints:
                lines.append(f"- **Constraints:** {', '.join(constraints)}")
                lines.append("")

            # Recursively process children
            for child in subsystem.subsystems.values():
                format_subsystem_section(child, level + 1)

    for root in sorted(graph.subsystems.values(), key=lambda s: s.name):
        format_subsystem_section(root)

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")

    recommendations = []
    if metrics.modularity < 0.2:
        recommendations.append("- Consider restructuring subsystems to improve modularity")

    low_coupling = [
        name for name, m in metrics.subsystems.items() if m.coupling_ratio < 1.0
    ]
    if low_coupling:
        recommendations.append(
            f"- Review subsystems with low coupling ratios: {', '.join(low_coupling)}"
        )

    if not recommendations:
        recommendations.append("- ✅ Decomposition looks healthy!")

    lines.extend(recommendations)
    lines.append("")

    return "\n".join(lines)


def _generate_yaml_report(metrics, graph: Graph) -> str:
    """Generate YAML format report."""
    import yaml

    data = {
        "generated": _get_timestamp(),
        "overall_metrics": {
            "modularity": metrics.modularity,
            "subsystem_count": metrics.subsystem_count,
            "avg_coupling_ratio": metrics.avg_coupling_ratio,
        },
        "subsystems": {},
    }

    for name, m in metrics.subsystems.items():
        data["subsystems"][name] = {
            "node_count": m.node_count,
            "internal_edges": m.internal_edges,
            "external_edges": m.external_edges,
            "coupling_ratio": (
                m.coupling_ratio if m.coupling_ratio != float("inf") else "infinity"
            ),
            "constraints": graph.get_constraints_for_subsystem(name),
        }

    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def _get_timestamp() -> str:
    """Get current timestamp."""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
