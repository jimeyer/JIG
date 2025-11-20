# @jig C-CORE-003 implements:S-JIG-002 subsystem:core interface:internal
"""Validation logic for OSTC nodes and graph consistency."""

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from jig.core.parser import OSTCNode, parse_ostc_node


@dataclass
class ValidationResult:
    """Result of validation with errors and warnings.

    Attributes:
        valid: True if no errors, False if errors found
        errors: List of error messages
        warnings: List of warning messages
    """

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# Valid node types for markdown nodes (O/S/X in OSTCX model)
# T/C nodes are discovered via @jig annotations, not markdown files
VALID_TYPES = {"outcome", "specification", "constraint"}

# Type prefix mapping
TYPE_PREFIX_MAP = {
    "outcome": "O",
    "specification": "S",
    "constraint": "C",
}

# ID format regex
ID_FORMAT_REGEX = r"^[OSTC]-[A-Z0-9]+-\d{3}$"


def validate_node(node: OSTCNode) -> ValidationResult:
    """Validate single OSTC node schema.

    Args:
        node: OSTCNode to validate

    Returns:
        ValidationResult with errors and warnings
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Check required fields
    if not node.id:
        errors.append("Missing required field: id")
    if not node.type:
        errors.append("Missing required field: type")
    if not node.title:
        errors.append("Missing required field: title")

    # If required fields missing, can't continue validation
    if errors:
        return ValidationResult(valid=False, errors=errors, warnings=warnings)

    # Validate ID format
    if not re.match(ID_FORMAT_REGEX, node.id):
        errors.append(
            f"Invalid ID format: '{node.id}'. Must match pattern [OSTC]-[A-Z0-9]+-[0-9]{{3}}"
        )

    # Validate type value
    if node.type not in VALID_TYPES:
        errors.append(
            f"Invalid type: '{node.type}'. Valid types for markdown nodes: "
            f"{', '.join(sorted(VALID_TYPES))}. "
            f"Test nodes (T) must use @jig annotations in test code. "
            f"See: docs/jig-concept/JIG-Concept-v7.md"
        )
    else:
        # Validate ID prefix matches type
        id_prefix = node.id.split("-")[0] if "-" in node.id else ""
        expected_prefix = TYPE_PREFIX_MAP.get(node.type, "")

        if id_prefix != expected_prefix:
            errors.append(
                f"ID prefix '{id_prefix}' doesn't match type '{node.type}'. "
                f"Expected prefix '{expected_prefix}'"
            )

    # Warnings for optional but recommended fields
    if not node.subsystem:
        warnings.append(f"Node {node.id}: subsystem not specified")

    if not node.created:
        warnings.append(f"Node {node.id}: created date not specified")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


def validate_graph(intent_dir: Path) -> ValidationResult:
    """Validate all OSTC nodes and graph consistency.

    Args:
        intent_dir: Path to directory containing OSTC nodes

    Returns:
        ValidationResult with all errors and warnings across the graph
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not intent_dir.exists():
        errors.append(f"Intent directory not found: {intent_dir}")
        return ValidationResult(valid=False, errors=errors, warnings=warnings)

    # Track all node IDs and their file paths
    node_ids: dict[str, Path] = {}
    all_nodes: list[OSTCNode] = []

    # Load and validate all nodes (O/S/X markdown nodes only)
    # T/C nodes discovered via @jig annotations (future feature)
    for node_type in ["outcomes", "specifications", "constraints"]:
        type_dir = intent_dir / node_type
        if not type_dir.exists():
            warnings.append(f"Directory not found: {type_dir}")
            continue

        for node_file in type_dir.glob("*.md"):
            try:
                node = parse_ostc_node(node_file)
                all_nodes.append(node)

                # Check for duplicate IDs
                if node.id in node_ids:
                    errors.append(
                        f"Duplicate node ID '{node.id}' found in:\n"
                        f"  - {node_ids[node.id]}\n"
                        f"  - {node_file}"
                    )
                else:
                    node_ids[node.id] = node_file

                # Validate individual node
                node_result = validate_node(node)
                if not node_result.valid:
                    for error in node_result.errors:
                        errors.append(f"{node_file}: {error}")
                warnings.extend(node_result.warnings)

            except Exception as e:
                errors.append(f"Failed to parse {node_file}: {e}")

    # Validate graph-index.yaml if it exists
    graph_index_file = intent_dir / "graph-index.yaml"
    if graph_index_file.exists():
        try:
            graph_data = yaml.safe_load(graph_index_file.read_text())
            if graph_data and "nodes" in graph_data:
                indexed_ids = {n["id"] for n in graph_data["nodes"] if "id" in n}

                # Check that all indexed nodes exist
                for indexed_id in indexed_ids:
                    if indexed_id not in node_ids:
                        errors.append(
                            f"Graph index references non-existent node: {indexed_id}"
                        )

                # Check for orphaned nodes (exist but not in index)
                orphaned_ids = set(node_ids.keys()) - indexed_ids
                if orphaned_ids:
                    warnings.append(
                        f"Nodes not referenced in graph index: {', '.join(sorted(orphaned_ids))}"
                    )
        except Exception as e:
            errors.append(f"Failed to load graph index: {e}")
    else:
        warnings.append(f"Graph index not found: {graph_index_file}")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


def validate_node_file(node_file: Path) -> ValidationResult:
    """Validate a single node file.

    Args:
        node_file: Path to OSTC node file

    Returns:
        ValidationResult with errors and warnings
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not node_file.exists():
        errors.append(f"Node file not found: {node_file}")
        return ValidationResult(valid=False, errors=errors, warnings=warnings)

    try:
        node = parse_ostc_node(node_file)
        result = validate_node(node)
        return result
    except Exception as e:
        errors.append(f"Failed to parse node file: {e}")
        return ValidationResult(valid=False, errors=errors, warnings=warnings)
