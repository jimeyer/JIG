"""Verification graph builder.

Orchestrates test discovery, analysis, and NDJSON generation.
This is the main entry point for building the verification graph.
"""

from pathlib import Path
from typing import List, Optional

import jig
from jig.impl_graph.graph import Graph
from jig.impl_graph.ndjson_writer import write_ndjson
from jig.verification_graph.analyzer import TestAnalyzer
from jig.verification_graph.discovery import discover_test_files


@jig.implements("S-055")
def build_verification_graph(
    project_root: Path,
    test_dir: Optional[Path] = None,
    output_path: Optional[Path] = None,
    exclude_patterns: Optional[List[str]] = None,
    include_timestamp: bool = True,
) -> Graph:
    """Build verification graph from test files.

    Orchestrates discovery → analysis → serialization:
    1. Discovers test files using pytest conventions
    2. Analyzes each file for @jig.verifies decorators
    3. Builds Graph with T nodes and T→S edges
    4. Writes to NDJSON format

    Args:
        project_root: Root directory of the project.
        test_dir: Directory to search for tests (defaults to project_root/tests).
        output_path: Path for NDJSON output (defaults to jig/generated/verification-graph.ndjson).
        exclude_patterns: Additional patterns to exclude from discovery.
        include_timestamp: Whether to include timestamp in metadata.

    Returns:
        The populated Graph instance.
    """
    graph = Graph()

    # 1. Discover test files
    test_files = discover_test_files(project_root, test_dir, exclude_patterns)

    # 2. Analyze each file
    analyzer = TestAnalyzer(project_root)
    for file_path in test_files:
        result = analyzer.analyze_file(file_path)
        for node in result["nodes"]:
            graph.add_node(node)
            # Add T→S edges for each verified spec
            for spec_id in node.get("verifies", []):
                graph.add_edge({
                    "source": node["id"],
                    "target": spec_id,
                    "type": "verifies",
                })

    # 3. Write to NDJSON
    if output_path is None:
        output_path = project_root / "jig" / "generated" / "verification-graph.ndjson"
    write_ndjson(graph, output_path, include_timestamp=include_timestamp)

    return graph
