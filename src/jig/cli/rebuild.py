"""Rebuild CLI commands for JIG graphs."""

import json
import time
from pathlib import Path
from typing import Optional

import click

import jig
from jig.cli.discovery import find_project_root
from jig.cli.output import OutputFormat
from jig.config import JigConfig
from jig.staleness import collect_git_metadata


def _format_rebuild_json(
    graphs: list[dict],
    duration_ms: int,
    status: str = "success",
    verbose: bool = False,
) -> str:
    """Format rebuild results as JSON.

    Args:
        graphs: List of graph result dicts with name, nodes, edges
        duration_ms: Total duration in milliseconds
        status: Overall status string
        verbose: If True, include additional fields

    Returns:
        JSON string
    """
    output = {
        "status": status,
        "graphs": graphs,
        "duration_ms": duration_ms,
    }
    if verbose:
        output["verbose"] = True
    return json.dumps(output, indent=2)


def _format_rebuild_markdown(
    graphs: list[dict],
    duration_ms: int,
    status: str = "success",
    verbose: bool = False,
) -> str:
    """Format rebuild results as markdown.

    Args:
        graphs: List of graph result dicts with name, nodes, edges
        duration_ms: Total duration in milliseconds
        status: Overall status string
        verbose: If True, include additional sections

    Returns:
        Markdown string
    """
    lines = ["# Rebuild Result", ""]
    lines.append(f"**Status:** {status.title()}")
    lines.append(f"**Duration:** {duration_ms}ms")
    lines.append("")

    lines.append("## Graphs")
    lines.append("")
    for g in graphs:
        lines.append(f"- **{g['name']}**: {g['nodes']} nodes, {g['edges']} edges")

    if verbose:
        lines.append("")
        lines.append("## Details")
        lines.append("")
        for g in graphs:
            lines.append(f"### {g['name']}")
            lines.append(f"- Nodes: {g['nodes']}")
            lines.append(f"- Edges: {g['edges']}")
            if "path" in g:
                lines.append(f"- Path: `{g['path']}`")

    return "\n".join(lines)


@jig.implements("S-058", "S-065", "S-068", "S-093")
def rebuild_impl_command(
    config: JigConfig,
    output_format: OutputFormat = OutputFormat.HUMAN,
    verbose: bool = False,
) -> int:
    """Rebuild implementation graph.

    Args:
        config: JIG configuration with resolved paths.
        output_format: Output format (HUMAN, JSON, MARKDOWN).
        verbose: If True, include additional output.

    Returns:
        Exit code (0 for success).
    """
    from jig.cli.validate import auto_validate_decorators
    from jig.impl_graph.builder import build_graph

    start_time = time.time()

    if output_format == OutputFormat.HUMAN:
        click.echo(f"Rebuilding implementation graph...")

    # Auto-validate decorators first
    if not auto_validate_decorators(config):
        return 1

    output_path = config.paths.generated / "implementation-graph.ndjson"

    # Collect git metadata for staleness detection (S-068)
    git_metadata = collect_git_metadata(config, [config.paths.source])

    graph = build_graph(
        project_root=config.project_root,
        source_dir=config.paths.source,
        output_path=output_path,
        exclude_patterns=None,
        verbose=False,
        strict=True,
        include_timestamp=True,
        git_metadata=git_metadata,
    )

    duration_ms = int((time.time() - start_time) * 1000)
    graphs = [{"name": "impl", "nodes": graph.node_count(), "edges": graph.edge_count()}]

    if output_format == OutputFormat.JSON:
        click.echo(_format_rebuild_json(graphs, duration_ms, verbose=verbose))
    elif output_format == OutputFormat.MARKDOWN:
        click.echo(_format_rebuild_markdown(graphs, duration_ms, verbose=verbose))
    else:
        click.echo(f"  impl: {graph.node_count()} nodes, {graph.edge_count()} edges")

    return 0


@jig.implements("S-058", "S-065", "S-068", "S-093")
def rebuild_intent_command(
    config: JigConfig,
    output_format: OutputFormat = OutputFormat.HUMAN,
    verbose: bool = False,
) -> int:
    """Rebuild intent graph.

    Args:
        config: JIG configuration with resolved paths.
        output_format: Output format (HUMAN, JSON, MARKDOWN).
        verbose: If True, include additional output.

    Returns:
        Exit code (0 for success).
    """
    from jig.intent_graph.generator import generate_intent_graph

    start_time = time.time()

    if output_format == OutputFormat.HUMAN:
        click.echo(f"Rebuilding intent graph...")

    output_path = config.paths.generated / "intent-graph.ndjson"

    # Collect git metadata for staleness detection (S-068)
    # Intent graph inputs: specifications, outcomes, bricks
    git_metadata = collect_git_metadata(config, [
        config.paths.specifications,
        config.paths.outcomes,
        config.paths.bricks.parent,  # jig_root for bricks.yaml
    ])

    output_path, node_count, edge_count = generate_intent_graph(
        project_root=config.project_root,
        output_path=output_path,
        include_timestamp=True,
        git_metadata=git_metadata,
    )

    duration_ms = int((time.time() - start_time) * 1000)
    graphs = [{"name": "intent", "nodes": node_count, "edges": edge_count}]

    if output_format == OutputFormat.JSON:
        click.echo(_format_rebuild_json(graphs, duration_ms, verbose=verbose))
    elif output_format == OutputFormat.MARKDOWN:
        click.echo(_format_rebuild_markdown(graphs, duration_ms, verbose=verbose))
    else:
        click.echo(f"  intent: {node_count} nodes, {edge_count} edges")

    return 0


@jig.implements("S-058", "S-065", "S-068", "S-093")
def rebuild_verify_command(
    config: JigConfig,
    output_format: OutputFormat = OutputFormat.HUMAN,
    verbose: bool = False,
) -> int:
    """Rebuild verification graph.

    Args:
        config: JIG configuration with resolved paths.
        output_format: Output format (HUMAN, JSON, MARKDOWN).
        verbose: If True, include additional output.

    Returns:
        Exit code (0 for success).
    """
    from jig.verification_graph.builder import build_verification_graph

    start_time = time.time()

    if output_format == OutputFormat.HUMAN:
        click.echo(f"Rebuilding verification graph...")

    output_path = config.paths.generated / "verification-graph.ndjson"

    # Collect git metadata for staleness detection (S-068)
    git_metadata = collect_git_metadata(config, [config.paths.tests])

    graph = build_verification_graph(
        project_root=config.project_root,
        test_dir=config.paths.tests,
        output_path=output_path,
        include_timestamp=True,
        git_metadata=git_metadata,
    )

    duration_ms = int((time.time() - start_time) * 1000)
    graphs = [{"name": "verify", "nodes": graph.node_count(), "edges": graph.edge_count()}]

    if output_format == OutputFormat.JSON:
        click.echo(_format_rebuild_json(graphs, duration_ms, verbose=verbose))
    elif output_format == OutputFormat.MARKDOWN:
        click.echo(_format_rebuild_markdown(graphs, duration_ms, verbose=verbose))
    else:
        click.echo(f"  verify: {graph.node_count()} nodes, {graph.edge_count()} edges")

    return 0


@jig.implements("S-058", "S-065", "S-093")
def rebuild_all_command(
    config: JigConfig,
    output_format: OutputFormat = OutputFormat.HUMAN,
    verbose: bool = False,
) -> int:
    """Rebuild all three graphs in order: impl -> verify -> intent.

    Args:
        config: JIG configuration with resolved paths.
        output_format: Output format (HUMAN, JSON, MARKDOWN).
        verbose: If True, include additional output.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    from jig.cli.validate import auto_validate_decorators
    from jig.impl_graph.builder import build_graph
    from jig.intent_graph.generator import generate_intent_graph
    from jig.verification_graph.builder import build_verification_graph

    start_time = time.time()
    graphs = []

    # For human output, delegate to individual commands
    if output_format == OutputFormat.HUMAN:
        exit_code = rebuild_impl_command(config, output_format, verbose)
        if exit_code != 0:
            return exit_code

        exit_code = rebuild_verify_command(config, output_format, verbose)
        if exit_code != 0:
            return exit_code

        exit_code = rebuild_intent_command(config, output_format, verbose)
        if exit_code != 0:
            return exit_code

        return 0

    # For JSON/Markdown output, collect all graph data first
    # Step 1: Auto-validate decorators
    if not auto_validate_decorators(config):
        return 1

    # Step 2: Rebuild impl graph
    impl_output = config.paths.generated / "implementation-graph.ndjson"
    impl_git_metadata = collect_git_metadata(config, [config.paths.source])
    impl_graph = build_graph(
        project_root=config.project_root,
        source_dir=config.paths.source,
        output_path=impl_output,
        exclude_patterns=None,
        verbose=False,
        strict=True,
        include_timestamp=True,
        git_metadata=impl_git_metadata,
    )
    graphs.append({"name": "impl", "nodes": impl_graph.node_count(), "edges": impl_graph.edge_count()})

    # Step 3: Rebuild verify graph
    verify_output = config.paths.generated / "verification-graph.ndjson"
    verify_git_metadata = collect_git_metadata(config, [config.paths.tests])
    verify_graph = build_verification_graph(
        project_root=config.project_root,
        test_dir=config.paths.tests,
        output_path=verify_output,
        include_timestamp=True,
        git_metadata=verify_git_metadata,
    )
    graphs.append({"name": "verify", "nodes": verify_graph.node_count(), "edges": verify_graph.edge_count()})

    # Step 4: Rebuild intent graph
    intent_output = config.paths.generated / "intent-graph.ndjson"
    intent_git_metadata = collect_git_metadata(config, [
        config.paths.specifications,
        config.paths.outcomes,
        config.paths.bricks.parent,
    ])
    intent_output, intent_nodes, intent_edges = generate_intent_graph(
        project_root=config.project_root,
        output_path=intent_output,
        include_timestamp=True,
        git_metadata=intent_git_metadata,
    )
    graphs.append({"name": "intent", "nodes": intent_nodes, "edges": intent_edges})

    duration_ms = int((time.time() - start_time) * 1000)

    if output_format == OutputFormat.JSON:
        click.echo(_format_rebuild_json(graphs, duration_ms, verbose=verbose))
    elif output_format == OutputFormat.MARKDOWN:
        click.echo(_format_rebuild_markdown(graphs, duration_ms, verbose=verbose))

    return 0


def _format_align_json(
    graphs: list[dict],
    validation: dict,
    summary: dict,
    duration_ms: int,
    verbose: bool = False,
) -> str:
    """Format align results as JSON.

    Args:
        graphs: List of graph result dicts
        validation: Validation status dict
        summary: Summary dict with stats
        duration_ms: Total duration in milliseconds
        verbose: If True, include additional fields

    Returns:
        JSON string
    """
    output = {
        "status": "aligned" if validation.get("passed", False) else "failed",
        "graphs": graphs,
        "validation": validation,
        "summary": summary,
        "duration_ms": duration_ms,
    }
    if verbose:
        output["verbose"] = True
    return json.dumps(output, indent=2)


def _format_align_markdown(
    graphs: list[dict],
    validation: dict,
    summary: dict,
    duration_ms: int,
    verbose: bool = False,
) -> str:
    """Format align results as markdown.

    Args:
        graphs: List of graph result dicts
        validation: Validation status dict
        summary: Summary dict with stats
        duration_ms: Total duration in milliseconds
        verbose: If True, include additional sections

    Returns:
        Markdown string
    """
    lines = ["# Align Result", ""]
    status = "Aligned" if validation.get("passed", False) else "Failed"
    lines.append(f"**Status:** {status}")
    lines.append(f"**Duration:** {duration_ms}ms")
    lines.append("")

    lines.append("## Graphs Rebuilt")
    lines.append("")
    for g in graphs:
        lines.append(f"- **{g['name']}**: {g['nodes']} nodes, {g['edges']} edges")
    lines.append("")

    lines.append("## Validation")
    lines.append("")
    for phase, result in validation.get("phases", {}).items():
        phase_status = "Passed" if result.get("passed", False) else "Failed"
        lines.append(f"- **{phase}**: {phase_status}")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    if "specs" in summary:
        lines.append(f"- **Specs:** {summary['specs']['total']} total ({summary['specs']['implemented']} implemented, {summary['specs']['verified']} verified)")

    if verbose:
        lines.append("")
        lines.append("## Details")
        lines.append("")
        for g in graphs:
            lines.append(f"### {g['name']}")
            lines.append(f"- Nodes: {g['nodes']}")
            lines.append(f"- Edges: {g['edges']}")

    return "\n".join(lines)


@jig.implements("S-059", "S-065", "S-068", "S-093")
def align_command(
    config: JigConfig,
    output_format: OutputFormat = OutputFormat.HUMAN,
    verbose: bool = False,
) -> int:
    """Run full alignment workflow: rebuild all graphs, validate, display summary.

    Args:
        config: JIG configuration with resolved paths.
        output_format: Output format (HUMAN, JSON, MARKDOWN).
        verbose: If True, include additional output.

    Returns:
        Exit code (0 if aligned, non-zero on failure).
    """
    from jig.cli.validate import auto_validate_decorators
    from jig.impl_graph.builder import build_graph
    from jig.intent_graph.generator import generate_intent_graph
    from jig.validation.bricks import validate_brick_definitions, validate_brick_partition
    from jig.validation.intent import (
        validate_outcome_files,
        validate_specification_files,
    )
    from jig.verification_graph.builder import build_verification_graph

    start_time = time.time()
    graphs = []
    validation_results = {"phases": {}, "passed": True}

    if output_format == OutputFormat.HUMAN:
        click.echo("Rebuilding graphs...")

    # Step 1: Auto-validate decorators
    if not auto_validate_decorators(config):
        return 1

    # Step 2: Rebuild impl graph
    impl_output = config.paths.generated / "implementation-graph.ndjson"
    try:
        impl_git_metadata = collect_git_metadata(config, [config.paths.source])
        impl_graph = build_graph(
            project_root=config.project_root,
            source_dir=config.paths.source,
            output_path=impl_output,
            exclude_patterns=None,
            verbose=False,
            strict=True,
            include_timestamp=True,
            git_metadata=impl_git_metadata,
        )
        graphs.append({"name": "impl", "nodes": impl_graph.node_count(), "edges": impl_graph.edge_count()})
        if output_format == OutputFormat.HUMAN:
            click.echo(f"  impl: {impl_graph.node_count()} functions")
    except Exception as e:
        if output_format == OutputFormat.HUMAN:
            click.echo(f"  impl: FAILED - {e}", err=True)
        return 1

    # Step 3: Rebuild verify graph
    verify_output = config.paths.generated / "verification-graph.ndjson"
    try:
        verify_git_metadata = collect_git_metadata(config, [config.paths.tests])
        verify_graph = build_verification_graph(
            project_root=config.project_root,
            test_dir=config.paths.tests,
            output_path=verify_output,
            include_timestamp=True,
            git_metadata=verify_git_metadata,
        )
        graphs.append({"name": "verify", "nodes": verify_graph.node_count(), "edges": verify_graph.edge_count()})
        if output_format == OutputFormat.HUMAN:
            click.echo(f"  verify: {verify_graph.node_count()} tests")
    except Exception as e:
        if output_format == OutputFormat.HUMAN:
            click.echo(f"  verify: FAILED - {e}", err=True)
        return 1

    # Step 4: Rebuild intent graph
    try:
        intent_output = config.paths.generated / "intent-graph.ndjson"
        intent_git_metadata = collect_git_metadata(config, [
            config.paths.specifications,
            config.paths.outcomes,
            config.paths.bricks.parent,
        ])
        intent_output, intent_nodes, intent_edges = generate_intent_graph(
            project_root=config.project_root,
            output_path=intent_output,
            include_timestamp=True,
            git_metadata=intent_git_metadata,
        )
        graphs.append({"name": "intent", "nodes": intent_nodes, "edges": intent_edges})
        # Count specs and outcomes from the graph
        spec_dir = config.paths.specifications
        outcome_dir = config.paths.outcomes
        spec_count = len(list(spec_dir.glob("*.md"))) if spec_dir.exists() else 0
        outcome_count = len(list(outcome_dir.glob("*.md"))) if outcome_dir.exists() else 0
        if output_format == OutputFormat.HUMAN:
            click.echo(f"  intent: {spec_count} specs, {outcome_count} outcomes")
    except Exception as e:
        if output_format == OutputFormat.HUMAN:
            click.echo(f"  intent: FAILED - {e}", err=True)
        return 1

    # Step 5: Validate
    if output_format == OutputFormat.HUMAN:
        click.echo("\nValidating...")

    # Validate intent
    spec_dir = config.paths.specifications
    outcome_dir = config.paths.outcomes

    intent_ok = True
    if spec_dir.exists():
        spec_result = validate_specification_files(spec_dir)
        if not spec_result.passed:
            intent_ok = False
    if outcome_dir.exists():
        outcome_result = validate_outcome_files(outcome_dir)
        if not outcome_result.passed:
            intent_ok = False

    validation_results["phases"]["intent"] = {"passed": intent_ok}
    if not intent_ok:
        validation_results["passed"] = False

    if output_format == OutputFormat.HUMAN:
        if intent_ok:
            click.echo("  intent: OK")
        else:
            click.echo("  intent: FAILED")
            return 1

    # Validate bricks
    bricks_file = config.paths.bricks
    bricks_ok = True
    brick_count = 0
    layer_count = 0
    if bricks_file.exists():
        def_result = validate_brick_definitions(bricks_file, impl_output)
        part_result = validate_brick_partition(bricks_file, impl_output)

        if def_result.passed and part_result.passed:
            # Count bricks and layers
            import yaml
            with open(bricks_file) as f:
                bricks_data = yaml.safe_load(f)
            brick_count = len(bricks_data.get("bricks", []))
            layers = set(b.get("layer", 0) for b in bricks_data.get("bricks", []))
            layer_count = len(layers)
            if output_format == OutputFormat.HUMAN:
                click.echo(f"  bricks: OK ({brick_count} bricks, {layer_count} layers)")
        else:
            bricks_ok = False
            if output_format == OutputFormat.HUMAN:
                click.echo("  bricks: FAILED")
                return 1
    else:
        if output_format == OutputFormat.HUMAN:
            click.echo("  bricks: OK (no bricks.yaml)")

    validation_results["phases"]["bricks"] = {"passed": bricks_ok, "count": brick_count, "layers": layer_count}
    if not bricks_ok:
        validation_results["passed"] = False

    # Step 6: Summary
    # Count implemented and verified specs
    implemented_count = _count_implemented_specs(impl_output, spec_dir)
    verified_count = _count_verified_specs(verify_output, spec_dir)

    summary = {
        "specs": {
            "total": spec_count,
            "implemented": implemented_count,
            "verified": verified_count,
        }
    }

    if output_format == OutputFormat.HUMAN:
        click.echo("\nSummary:")
        click.echo(f"  Specs: {spec_count} total ({implemented_count} implemented, {verified_count} verified)")
        click.echo("  Status: ALIGNED")
    elif output_format == OutputFormat.JSON:
        duration_ms = int((time.time() - start_time) * 1000)
        click.echo(_format_align_json(graphs, validation_results, summary, duration_ms, verbose=verbose))
    elif output_format == OutputFormat.MARKDOWN:
        duration_ms = int((time.time() - start_time) * 1000)
        click.echo(_format_align_markdown(graphs, validation_results, summary, duration_ms, verbose=verbose))

    return 0


def _count_implemented_specs(impl_graph_path: Path, spec_dir: Path) -> int:
    """Count how many specs have at least one implementing function."""
    import json

    if not impl_graph_path.exists() or not spec_dir.exists():
        return 0

    # Get all spec IDs
    spec_ids = set()
    for spec_file in spec_dir.glob("*.md"):
        spec_ids.add(spec_file.stem)

    # Read impl graph and find implemented specs
    # Nodes have "implements": ["S-001", "S-002"] arrays
    implemented = set()
    with open(impl_graph_path) as f:
        for line in f:
            node = json.loads(line)
            impl_list = node.get("implements", [])
            for spec_id in impl_list:
                if spec_id in spec_ids:
                    implemented.add(spec_id)

    return len(implemented)


def _count_verified_specs(verify_graph_path: Path, spec_dir: Path) -> int:
    """Count how many specs have at least one verifying test."""
    import json

    if not verify_graph_path.exists() or not spec_dir.exists():
        return 0

    # Get all spec IDs
    spec_ids = set()
    for spec_file in spec_dir.glob("*.md"):
        spec_ids.add(spec_file.stem)

    # Read verify graph and find verified specs
    # Nodes have "verifies": ["S-001", "S-002"] arrays
    verified = set()
    with open(verify_graph_path) as f:
        for line in f:
            node = json.loads(line)
            verify_list = node.get("verifies", [])
            for spec_id in verify_list:
                if spec_id in spec_ids:
                    verified.add(spec_id)

    return len(verified)

