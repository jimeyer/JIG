# @jig C-CORE-004 implements:S-CLI-022,S-CLI-025 subsystem:core interface:internal
"""Semantic validation for JIG graphs.

This module provides comprehensive semantic validation for JIG graphs,
separating concerns from structural validation (performed during index rebuild).

Structural validation (in validator.py):
    - File parseability (valid YAML/JSON)
    - ID format and required fields
    - Node type validity
    - Reference existence

Semantic validation (this module):
    - Edge type rules (O→S, S→S, etc.)
    - Subsystem hierarchy (no cycles)
    - Self-loops
    - Quality metrics (orphans, unassigned nodes)

See S-CLI-025 for full separation of concerns.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

# Use existing ValidationResult from validator.py
from jig.core.validator import ValidationResult, validate_edges, validate_nested_subsystems

if TYPE_CHECKING:
    from jig.core.graph import Graph


@dataclass
class ComprehensiveValidationResult:
    """Enhanced validation result with check details.

    Extends ValidationResult with structured check results for better reporting.

    Attributes:
        valid: True if no errors, False if errors found
        errors: List of error messages
        warnings: List of warning messages
        node_count: Total number of nodes validated
        edge_count: Total number of edges validated
        checks_passed: Dictionary of check name -> bool (passed/failed)
    """
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0
    checks_passed: dict[str, bool] = field(default_factory=dict)


def validate_graph_comprehensive(graph: "Graph") -> ComprehensiveValidationResult:
    """Perform comprehensive semantic validation on graph.

    This function performs all semantic checks needed for graph health:
    - Edge type rules (O→S, S→S, etc.)
    - Subsystem hierarchy (no cycles)
    - Self-loops detection
    - Quality warnings (orphans, unassigned nodes)

    Structural validation (file parsing, ID format) is performed during
    index rebuild and is NOT checked here.

    Args:
        graph: Graph to validate

    Returns:
        ComprehensiveValidationResult with detailed check results

    Example:
        >>> graph = Graph.load_from_dir(Path("jig"))
        >>> result = validate_graph_comprehensive(graph)
        >>> if result.valid:
        ...     print("Graph is valid!")
        ... else:
        ...     for error in result.errors:
        ...         print(f"Error: {error}")
    """
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, bool] = {}

    # Count nodes and edges
    node_count = len(graph.nodes)
    edge_count = len(graph.edges)

    # Check 1: Validate edges (type rules, self-loops, targets exist)
    edge_result = validate_edges(graph, check_orphans=True)
    errors.extend(edge_result.errors)
    warnings.extend(edge_result.warnings)
    checks["edge_validation"] = edge_result.valid

    # Check 2: Validate subsystem hierarchy (no cycles)
    subsystem_errors = validate_nested_subsystems(graph)
    errors.extend(subsystem_errors)
    checks["subsystem_hierarchy"] = len(subsystem_errors) == 0

    # Check 3: Validate all node IDs are valid format
    # (This is already done during index build, so we assume it's valid here)
    # We just need to count duplicate IDs if any somehow slipped through
    node_ids = list(graph.nodes.keys())
    if len(node_ids) != len(set(node_ids)):
        duplicate_ids = [node_id for node_id in node_ids if node_ids.count(node_id) > 1]
        errors.append(f"Duplicate node IDs found: {', '.join(set(duplicate_ids))}")
        checks["no_duplicate_ids"] = False
    else:
        checks["no_duplicate_ids"] = True

    # Check 4: Quality warnings for unassigned nodes
    unassigned_nodes = [
        node_id for node_id, node in graph.nodes.items()
        if not node.subsystem
    ]
    if unassigned_nodes:
        warnings.append(
            f"Nodes missing subsystem assignment ({len(unassigned_nodes)}): "
            f"{', '.join(sorted(unassigned_nodes)[:10])}"
            + ("..." if len(unassigned_nodes) > 10 else "")
        )

    # Determine overall validity
    valid = len(errors) == 0

    return ComprehensiveValidationResult(
        valid=valid,
        errors=errors,
        warnings=warnings,
        node_count=node_count,
        edge_count=edge_count,
        checks_passed=checks,
    )