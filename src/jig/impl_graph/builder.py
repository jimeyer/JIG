"""Graph builder orchestrator for implementation graph generation.

This module coordinates the analysis of source files and construction of
the implementation graph.
"""

import logging
from pathlib import Path
from typing import List, Optional

import jig

from .analyzers import AnalyzerRegistry, get_global_registry
from .analyzers.python import ParseError, PythonAnalyzer
from .graph import Graph
from .ndjson_writer import write_ndjson

logger = logging.getLogger(__name__)


@jig.implements("S-001", "S-006")
class GraphBuilder:
    """Orchestrates implementation graph generation from source files.

    Scans source directories, routes files to appropriate analyzers,
    collects results into a graph, and writes NDJSON output.
    """

    def __init__(
        self,
        project_root: Path,
        source_dir: Optional[Path] = None,
        registry: Optional[AnalyzerRegistry] = None,
    ) -> None:
        """Initialize the graph builder.

        Args:
            project_root: Root directory of the project.
            source_dir: Source directory to scan (defaults to project_root/src).
            registry: Analyzer registry (defaults to global registry).
        """
        self.project_root = project_root
        self.source_dir = source_dir or project_root / "src"
        self.registry = registry or get_global_registry()
        self.graph = Graph()

        # Always register Python analyzer with correct project_root
        # This overrides any existing analyzer to ensure correct path resolution
        self.registry.register(PythonAnalyzer(project_root=project_root))

    @jig.implements("S-001", "S-006")
    def build(
        self,
        exclude_patterns: Optional[List[str]] = None,
        verbose: bool = False,
        strict: bool = True,
    ) -> Graph:
        """Build the implementation graph from source files.

        Args:
            exclude_patterns: List of glob patterns to exclude (e.g., ["**/test_*.py"]).
            verbose: Enable verbose output.
            strict: Fail on parse errors (default True).

        Returns:
            The constructed graph.

        Raises:
            ParseError: If strict=True and a file cannot be parsed.
        """
        exclude_patterns = exclude_patterns or []

        # Discover source files
        files = self._discover_files(exclude_patterns)

        if verbose:
            logger.info(f"Found {len(files)} files to analyze")

        # Analyze each file
        for i, file_path in enumerate(files, 1):
            if verbose:
                logger.info(f"[{i}/{len(files)}] Analyzing {file_path.relative_to(self.project_root)}")

            try:
                self._analyze_file(file_path)
            except ParseError as e:
                if strict:
                    logger.error(str(e))
                    raise
                else:
                    logger.warning(f"Skipping {file_path}: {e}")
                    continue

        if verbose:
            logger.info(
                f"Analysis complete: {self.graph.node_count()} nodes, "
                f"{self.graph.edge_count()} edges"
            )

        return self.graph

    def write(
        self,
        output_path: Path,
        include_timestamp: bool = True,
        verbose: bool = False,
        git_metadata: Optional[dict] = None,
    ) -> None:
        """Write the graph to an NDJSON file.

        Args:
            output_path: Path to write the NDJSON file.
            include_timestamp: Include timestamp in metadata.
            verbose: Enable verbose output.
            git_metadata: Optional git state metadata for staleness detection.
        """
        write_ndjson(
            self.graph,
            output_path,
            include_timestamp=include_timestamp,
            git_metadata=git_metadata,
        )

        if verbose:
            logger.info(f"Graph written to {output_path}")

    def _discover_files(self, exclude_patterns: List[str]) -> List[Path]:
        """Discover source files to analyze.

        Args:
            exclude_patterns: List of glob patterns to exclude.

        Returns:
            List of file paths to analyze.
        """
        files: List[Path] = []

        # Get supported extensions from registry
        supported_extensions = self.registry.supported_extensions()

        # Find all files with supported extensions
        for ext in supported_extensions:
            pattern = f"**/*{ext}"
            for file_path in self.source_dir.rglob(pattern):
                if file_path.is_file() and not self._should_exclude(file_path, exclude_patterns):
                    files.append(file_path)

        # Sort for deterministic ordering
        files.sort()

        return files

    def _should_exclude(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if a file should be excluded.

        Args:
            file_path: Path to check.
            exclude_patterns: List of glob patterns to exclude.

        Returns:
            True if the file should be excluded.
        """
        for pattern in exclude_patterns:
            if file_path.match(pattern):
                return True
        return False

    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single file and add results to graph.

        Args:
            file_path: Path to the file to analyze.

        Raises:
            ParseError: If the file cannot be parsed.
        """
        # Get analyzer for this file
        analyzer = self.registry.get_analyzer(file_path)

        if not analyzer:
            logger.debug(f"No analyzer for {file_path.suffix}, skipping {file_path}")
            return

        # Analyze the file
        result = analyzer.analyze_file(file_path)

        # Add nodes and edges to graph
        self.graph.add_nodes(result["nodes"])
        self.graph.add_edges(result["edges"])


@jig.implements("S-001", "S-003", "S-006", "S-068")
def build_graph(
    project_root: Path,
    source_dir: Optional[Path] = None,
    output_path: Optional[Path] = None,
    exclude_patterns: Optional[List[str]] = None,
    verbose: bool = False,
    strict: bool = True,
    include_timestamp: bool = True,
    git_metadata: Optional[dict] = None,
) -> Graph:
    """Build an implementation graph from source files.

    Convenience function for building and optionally writing a graph.

    Args:
        project_root: Root directory of the project.
        source_dir: Source directory to scan (defaults to project_root/src).
        output_path: Path to write NDJSON output (optional).
        exclude_patterns: List of glob patterns to exclude.
        verbose: Enable verbose output.
        strict: Fail on parse errors.
        include_timestamp: Include timestamp in metadata.
        git_metadata: Optional git state metadata for staleness detection.

    Returns:
        The constructed graph.

    Raises:
        ParseError: If strict=True and a file cannot be parsed.
    """
    builder = GraphBuilder(project_root, source_dir)
    graph = builder.build(exclude_patterns=exclude_patterns, verbose=verbose, strict=strict)

    if output_path:
        builder.write(
            output_path,
            include_timestamp=include_timestamp,
            verbose=verbose,
            git_metadata=git_metadata,
        )

    return graph
