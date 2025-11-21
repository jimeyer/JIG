# @jig C-JIGY-009 implements:S-JIGY-009 subsystem:jigy-tool interface:public
"""Graph index builder - regenerate graph-index.yaml from sources.

Scans markdown files (O/S nodes) and code annotations (C/T nodes) to rebuild
the complete graph-index.yaml file. This establishes markdown and annotations
as the source of truth for the Intent Graph.

Performance target: <3 seconds for 1000-node graph.
"""

import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jig.core.parser import OSTCNode, parse_ostc_node
from jig.core.relationships import extract_edges_from_node
from jig.core.scanner import AnnotationScanner
from jig.utils.yaml_utils import dump_yaml


@dataclass
class RebuildResult:
    """Result of graph index rebuild operation.

    Attributes:
        success: True if rebuild completed without errors
        nodes: Dictionary mapping node ID to OSTCNode
        conflicts: List of conflict messages (duplicate IDs)
        warnings: List of warning messages (non-fatal issues)
        validation_errors: List of validation error messages
    """

    success: bool
    nodes: dict[str, OSTCNode]
    conflicts: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    validation_errors: list[str] = field(default_factory=list)


class IndexBuilder:
    """Builds graph-index.yaml from markdown and annotation sources.

    Example:
        >>> builder = IndexBuilder(Path("/path/to/project"))
        >>> result = builder.build()
        >>> if result.success:
        ...     builder.write_yaml(result, Path("jig/graph-index.yaml"))
    """

    def __init__(self, project_root: Path) -> None:
        """Initialize index builder.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.intent_dir = project_root / "jig"
        self.src_dirs = [project_root / "src", project_root / "test", project_root / "tests"]
        self.parse_errors: list[str] = []  # Track parse errors

    def discover_markdown_nodes(self) -> list[OSTCNode]:
        """Discover O/S/C nodes from markdown files in jig/ directory.

        Scans jig/outcomes/, jig/specifications/, and jig/constraints/ for
        markdown files with YAML frontmatter.

        Returns:
            List of parsed OSTCNode objects from markdown files
        """
        nodes: list[OSTCNode] = []

        if not self.intent_dir.exists():
            return nodes

        # Scan markdown directories
        node_dirs = ["outcomes", "specifications", "constraints"]
        for node_dir in node_dirs:
            dir_path = self.intent_dir / node_dir
            if not dir_path.exists():
                continue

            for md_file in dir_path.glob("*.md"):
                try:
                    node = parse_ostc_node(md_file)
                    nodes.append(node)
                except Exception as e:
                    # Track parse error but continue (non-fatal)
                    self.parse_errors.append(f"Failed to parse {md_file}: {str(e)}")
                    pass

        return nodes

    def discover_annotation_nodes(self) -> list[OSTCNode]:
        """Discover C/T nodes from @jig annotations in source files.

        Scans src/, test/, and tests/ directories for @jig annotations.

        Returns:
            List of OSTCNode objects created from annotations
        """
        nodes: list[OSTCNode] = []

        # Scan for annotations
        scanner = AnnotationScanner()
        existing_dirs = [d for d in self.src_dirs if d.exists()]

        if not existing_dirs:
            return nodes

        annotations = scanner.scan(existing_dirs)

        # Convert annotations to OSTCNode objects
        for annotation in annotations:
            # Create OSTCNode from annotation
            node = OSTCNode(
                id=annotation.id,
                type=annotation.type,
                title=annotation.id,  # Use ID as title for code nodes (no title in annotation)
                subsystem=annotation.metadata.get("subsystem"),
                status=annotation.metadata.get("status", "active"),
                body="",  # Code nodes don't have markdown body
                metadata={
                    "file": annotation.file,
                    "line": annotation.line,
                    **annotation.metadata,
                    **annotation.relationships,  # Include relationships in metadata
                },
            )
            nodes.append(node)

        return nodes

    def build(self) -> RebuildResult:
        """Build complete graph index from all sources.

        This is the main method that:
        1. Discovers all nodes (markdown + annotations)
        2. Detects conflicts (duplicate IDs)
        3. Validates nodes and relationships
        4. Returns result with merged nodes

        Returns:
            RebuildResult with success status, nodes, and any errors/warnings
        """
        # 1. Discover all nodes
        markdown_nodes = self.discover_markdown_nodes()
        annotation_nodes = self.discover_annotation_nodes()

        all_nodes = markdown_nodes + annotation_nodes

        # 2. Detect conflicts (duplicate IDs)
        conflicts = detect_conflicts(all_nodes)

        # 3. Merge nodes (handle duplicates)
        merged_nodes, merge_conflicts = merge_nodes(all_nodes)
        conflicts.extend(merge_conflicts)

        # 4. Validate
        validation_errors = self._validate_nodes(merged_nodes)
        warnings = self._generate_warnings(merged_nodes)
        
        # Add parse errors to warnings
        warnings.extend(self.parse_errors)

        # Determine success (no conflicts and no critical validation errors)
        success = len(conflicts) == 0 and len(validation_errors) == 0

        return RebuildResult(
            success=success,
            nodes=merged_nodes,
            conflicts=conflicts,
            warnings=warnings,
            validation_errors=validation_errors,
        )

    def _validate_nodes(self, nodes: dict[str, OSTCNode]) -> list[str]:
        """Validate nodes and their relationships.

        Args:
            nodes: Dictionary of nodes to validate

        Returns:
            List of validation error messages
        """
        errors: list[str] = []

        for node_id, node in nodes.items():
            # Validate node ID format
            import re
            if not re.match(r'^[OSTC]-[A-Z]+-\d+$', node.id):
                errors.append(f"Invalid node ID format: {node.id}")

            # Validate node type
            valid_types = {"outcome", "specification", "constraint", "code", "test"}
            if node.type not in valid_types:
                errors.append(f"Invalid node type '{node.type}' for {node.id}")

            # Validate relationships (targets exist)
            if node.metadata:
                for rel_type in ["implements", "verifies", "satisfies", "depends_on", "depends"]:
                    if rel_type in node.metadata:
                        targets = node.metadata[rel_type]
                        if isinstance(targets, str):
                            targets = [targets]
                        for target in targets:
                            if target not in nodes:
                                errors.append(f"{node.id}: Relationship {rel_type} references non-existent node {target}")

        return errors

    def _generate_warnings(self, nodes: dict[str, OSTCNode]) -> list[str]:
        """Generate warnings for potential issues.

        Args:
            nodes: Dictionary of nodes to check

        Returns:
            List of warning messages
        """
        warnings: list[str] = []

        # Check for nodes without subsystem
        for node_id, node in nodes.items():
            if not node.subsystem:
                warnings.append(f"{node_id}: Node missing subsystem assignment")

        return warnings

    def write_yaml(self, result: RebuildResult, output_file: Path, backup: bool = True) -> None:
        """Write graph index to YAML file.

        Args:
            result: RebuildResult with nodes to write
            output_file: Path to output file (typically jig/graph-index.yaml)
            backup: If True and file exists, create .bak backup before overwriting
        """
        # Backup existing file if requested
        if backup and output_file.exists():
            backup_file = output_file.parent / f"{output_file.name}.bak"
            shutil.copy(output_file, backup_file)

        # Build YAML structure
        yaml_data: dict[str, Any] = {
            "version": "1.0",
            "generated": datetime.now(timezone.utc).isoformat(),
            "nodes": [],
        }

        # Convert nodes to YAML format (node-centric with relationships on nodes)
        for node_id in sorted(result.nodes.keys()):  # Sort for deterministic output
            node = result.nodes[node_id]
            
            node_dict: dict[str, Any] = {
                "id": node.id,
                "type": node.type,
                "title": node.title,
            }

            # Add optional fields
            if node.subsystem:
                node_dict["subsystem"] = node.subsystem
            if node.status:
                node_dict["status"] = node.status

            # Add file location
            if node.metadata and "file" in node.metadata:
                node_dict["file"] = node.metadata["file"]
            else:
                # For markdown nodes, construct file path
                if node.type == "outcome":
                    node_dict["file"] = f"jig/outcomes/{node.id}.md"
                elif node.type == "specification":
                    node_dict["file"] = f"jig/specifications/{node.id}.md"
                elif node.type == "constraint":
                    node_dict["file"] = f"jig/constraints/{node.id}.md"

            # Add line number for code/test nodes
            if node.metadata and "line" in node.metadata:
                node_dict["line"] = node.metadata["line"]

            # Add relationships from metadata or by extracting from node
            if node.metadata:
                for rel_type in ["implements", "verifies", "satisfies", "depends_on", "depends"]:
                    if rel_type in node.metadata:
                        value = node.metadata[rel_type]
                        # Normalize to list
                        if isinstance(value, str):
                            value = [value]
                        if value:  # Only add if not empty
                            node_dict[rel_type] = sorted(value)  # Sort for deterministic output

            yaml_data["nodes"].append(node_dict)

        # Write YAML file
        dump_yaml(yaml_data, output_file)


def build_graph_index(project_root: Path) -> RebuildResult:
    """Convenience function to build graph index.

    Args:
        project_root: Root directory of the project

    Returns:
        RebuildResult with build status and nodes

    Example:
        >>> result = build_graph_index(Path("/path/to/project"))
        >>> if result.success:
        ...     print(f"Built index with {len(result.nodes)} nodes")
    """
    builder = IndexBuilder(project_root)
    return builder.build()


def detect_conflicts(nodes: list[OSTCNode]) -> list[str]:
    """Detect duplicate node IDs in list of nodes.

    Args:
        nodes: List of OSTCNode objects to check

    Returns:
        List of conflict messages for duplicate IDs

    Example:
        >>> conflicts = detect_conflicts(nodes)
        >>> if conflicts:
        ...     print(f"Found {len(conflicts)} conflicts")
    """
    conflicts: list[str] = []
    seen: dict[str, list[str]] = {}  # node_id -> list of file paths

    for node in nodes:
        node_id = node.id
        
        # Get file path for error message
        if node.metadata and "file" in node.metadata:
            file_path = node.metadata["file"]
        else:
            file_path = f"(markdown: {node.type})"

        if node_id not in seen:
            seen[node_id] = []
        seen[node_id].append(file_path)

    # Report duplicates
    for node_id, file_paths in seen.items():
        if len(file_paths) > 1:
            conflicts.append(
                f"Duplicate node ID '{node_id}' found in: {', '.join(file_paths)}"
            )

    return conflicts


def merge_nodes(nodes: list[OSTCNode]) -> tuple[dict[str, OSTCNode], list[str]]:
    """Merge list of nodes into dictionary, handling duplicates.

    When duplicate IDs are found, keeps the first occurrence and reports conflict.

    Args:
        nodes: List of OSTCNode objects

    Returns:
        Tuple of (merged node dict, list of conflict messages)

    Example:
        >>> merged, conflicts = merge_nodes(nodes)
        >>> print(f"Merged {len(merged)} unique nodes, {len(conflicts)} conflicts")
    """
    merged: dict[str, OSTCNode] = {}
    conflicts: list[str] = []

    for node in nodes:
        if node.id in merged:
            # Duplicate found - keep first, report conflict
            existing = merged[node.id]
            
            existing_file = existing.metadata.get("file", "unknown") if existing.metadata else "unknown"
            new_file = node.metadata.get("file", "unknown") if node.metadata else "unknown"
            
            conflicts.append(
                f"Duplicate node ID '{node.id}': keeping {existing_file}, ignoring {new_file}"
            )
        else:
            merged[node.id] = node

    return merged, conflicts

