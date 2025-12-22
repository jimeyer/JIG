"""NDJSON writer for implementation graphs.

This module provides functionality to serialize implementation graphs to
NDJSON (newline-delimited JSON) format with deterministic output.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import jig

from .graph import Graph


@jig.implements("S-003", "S-068")
class NDJSONWriter:
    """Writer for implementation graphs in NDJSON format.

    Outputs graphs with:
    - Line 1: Metadata (_meta)
    - Lines 2-N: Nodes sorted by ID
    - Lines N+1-M: Edges
    - Deterministic output (same input → identical output)
    """

    def __init__(self, graph: Graph, git_metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the NDJSON writer.

        Args:
            graph: The graph to write.
            git_metadata: Optional git state metadata for staleness detection.
        """
        self.graph = graph
        self.git_metadata = git_metadata

    @jig.implements("S-003")
    def write(
        self, output_path: Path, include_timestamp: bool = True
    ) -> None:
        """Write the graph to an NDJSON file.

        Args:
            output_path: Path to write the NDJSON file.
            include_timestamp: Whether to include generated timestamp in metadata.
                Defaults to True. Set to False for deterministic testing.

        Raises:
            IOError: If the file cannot be written.
        """
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as f:
            # Write metadata line
            metadata = self._generate_metadata(include_timestamp)
            f.write(json.dumps(metadata, sort_keys=True))
            f.write("\n")

            # Write nodes sorted by ID
            sorted_nodes = self._sort_nodes(self.graph.get_nodes())
            for node in sorted_nodes:
                f.write(json.dumps(node, sort_keys=True))
                f.write("\n")

            # Write edges (deterministic order)
            sorted_edges = self._sort_edges(self.graph.get_edges())
            for edge in sorted_edges:
                f.write(json.dumps(edge, sort_keys=True))
                f.write("\n")

    @jig.implements("S-068")
    def _generate_metadata(self, include_timestamp: bool) -> Dict[str, Any]:
        """Generate metadata for the NDJSON file.

        Args:
            include_timestamp: Whether to include the generated timestamp.

        Returns:
            Metadata dictionary with _meta key.
        """
        metadata: Dict[str, Any] = {
            "_meta": {
                "version": "1.0",
                "node_count": self.graph.node_count(),
                "edge_count": self.graph.edge_count(),
            }
        }

        if include_timestamp:
            metadata["_meta"]["generated"] = datetime.now(timezone.utc).isoformat()

        # Add git metadata for staleness detection (S-068)
        if self.git_metadata:
            metadata["_meta"]["git_head"] = self.git_metadata.get("git_head")
            metadata["_meta"]["git_tree_hashes"] = self.git_metadata.get("git_tree_hashes", {})
            metadata["_meta"]["git_dirty_files"] = self.git_metadata.get("git_dirty_files", [])

        return metadata

    def _sort_nodes(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort nodes by ID for deterministic output.

        Args:
            nodes: List of node dictionaries.

        Returns:
            Nodes sorted by 'id' field lexicographically.
        """
        return sorted(nodes, key=lambda n: n.get("id", ""))

    def _sort_edges(self, edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort edges for deterministic output.

        Edges are sorted by (source, target, type) tuple.

        Args:
            edges: List of edge dictionaries.

        Returns:
            Edges sorted by (source, target, type).
        """
        return sorted(
            edges,
            key=lambda e: (
                e.get("source", ""),
                e.get("target", ""),
                e.get("type", ""),
            ),
        )


@jig.implements("S-003", "S-068")
def write_ndjson(
    graph: Graph,
    output_path: Path,
    include_timestamp: bool = True,
    git_metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Write a graph to NDJSON format.

    Convenience function for writing graphs to NDJSON.

    Args:
        graph: The graph to write.
        output_path: Path to write the NDJSON file.
        include_timestamp: Whether to include generated timestamp in metadata.
        git_metadata: Optional git state metadata for staleness detection.
    """
    writer = NDJSONWriter(graph, git_metadata=git_metadata)
    writer.write(output_path, include_timestamp=include_timestamp)
