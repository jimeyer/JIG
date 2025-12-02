"""
Brick validation: definitions and partition constraints.

Validates brick definitions against implementation graph.
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Optional

import yaml

import jig
from jig.validation.models import ValidationError, ValidationResult


@jig.implements("S-021")
@jig.implements("S-035")
@jig.implements("S-036")
@jig.implements("S-037")
def validate_brick_definitions(
    bricks_file: Path,
    impl_graph_file: Path,
) -> ValidationResult:
    """
    Validate brick definitions against A001 contract and implementation graph.

    Checks:
    - Implementation graph exists
    - Required fields: id, name, units, layer
    - ID format: B-[a-z0-9-]+ (kebab-case)
    - ID uniqueness
    - Layer field presence (S-036)
    - Layer value: non-negative integer (S-037)
    - Unit prefix: must start with M-, C-, or F-
    - Unit references exist in implementation graph
    - No excluded fields: depends_on, public_api, specs
    """
    result = ValidationResult(passed=True, phase_name="brick definitions")

    # Check implementation graph exists
    if not impl_graph_file.exists():
        result.add_error(
            ValidationError(
                file=str(impl_graph_file),
                message=f"Implementation graph not found: {impl_graph_file}. Run 'jigy impl rebuild' first.",
                code="GRAPH_NOT_FOUND",
            )
        )
        return result

    # Load implementation graph nodes
    graph_node_ids = _load_graph_node_ids(impl_graph_file)

    # Check bricks.yaml exists
    if not bricks_file.exists():
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message=f"Bricks file not found: {bricks_file}",
                code="FILE_NOT_FOUND",
            )
        )
        return result

    # Parse bricks.yaml
    try:
        bricks_data = yaml.safe_load(bricks_file.read_text())
    except Exception as e:
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message=f"Failed to parse bricks.yaml: {e}",
                code="INVALID_YAML",
            )
        )
        return result

    # Handle both formats: {"bricks": [...]} or direct [...]
    if isinstance(bricks_data, dict) and "bricks" in bricks_data:
        bricks_data = bricks_data["bricks"]

    if not isinstance(bricks_data, list):
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message="bricks.yaml must contain a list of bricks (either as top-level list or under 'bricks:' key)",
                code="INVALID_STRUCTURE",
            )
        )
        return result

    result.items_checked = len(bricks_data)

    seen_ids = {}
    # S-035: Require kebab-case with at least one letter (semantic naming)
    brick_pattern = re.compile(r"^B-[a-z0-9-]*[a-z][a-z0-9-]*$")
    unit_prefix_pattern = re.compile(r"^(M-|C-|F-)")

    for i, brick in enumerate(bricks_data):
        brick_id = brick.get("id", f"brick at index {i}")

        # Check required fields
        if "id" not in brick:
            result.add_error(
                ValidationError(
                    file=str(bricks_file),
                    message=f"Brick at index {i}: Missing required field 'id'",
                    code="MISSING_REQUIRED_FIELD",
                    field="id",
                )
            )
            continue

        if "name" not in brick:
            result.add_error(
                ValidationError(
                    file=str(bricks_file),
                    message=f"Brick '{brick_id}': Missing required field 'name'",
                    code="MISSING_REQUIRED_FIELD",
                    field="name",
                )
            )

        if "units" not in brick:
            result.add_error(
                ValidationError(
                    file=str(bricks_file),
                    message=f"Brick '{brick_id}': Missing required field 'units'",
                    code="MISSING_REQUIRED_FIELD",
                    field="units",
                )
            )

        # Check layer field presence (S-036)
        if "layer" not in brick or brick.get("layer") is None:
            result.add_error(
                ValidationError(
                    file=str(bricks_file),
                    message=f"Brick '{brick_id}': Missing required field 'layer'. All bricks must have a layer field per A001 Section 4.",
                    code="MISSING_REQUIRED_FIELD",
                    field="layer",
                )
            )
        else:
            # Check layer value type and range (S-037)
            layer_value = brick.get("layer")
            if not isinstance(layer_value, int):
                result.add_error(
                    ValidationError(
                        file=str(bricks_file),
                        message=f"Brick '{brick_id}': Invalid layer type '{type(layer_value).__name__}'. Layer must be a non-negative integer (e.g., 0, 1, 2).",
                        code="INVALID_LAYER_TYPE",
                        field="layer",
                    )
                )
            elif layer_value < 0:
                result.add_error(
                    ValidationError(
                        file=str(bricks_file),
                        message=f"Brick '{brick_id}': Invalid layer value {layer_value}. Layer must be non-negative (>= 0).",
                        code="INVALID_LAYER_VALUE",
                        field="layer",
                    )
                )

        # Check ID format (S-035: kebab-case)
        if not brick_pattern.match(brick_id):
            result.add_error(
                ValidationError(
                    file=str(bricks_file),
                    message=f"Brick '{brick_id}': Invalid ID format. Must match pattern B-[a-z0-9-]+ (kebab-case). Example: B-auth, B-core-utils",
                    code="INVALID_ID_FORMAT",
                    field="id",
                )
            )

        # Check ID uniqueness
        if brick_id in seen_ids:
            result.add_error(
                ValidationError(
                    file=str(bricks_file),
                    message=f"Duplicate brick ID '{brick_id}'",
                    code="DUPLICATE_ID",
                    field="id",
                )
            )
        else:
            seen_ids[brick_id] = True

        # Check excluded fields
        excluded_fields = ["depends_on", "public_api", "specs"]
        for field in excluded_fields:
            if field in brick:
                result.add_error(
                    ValidationError(
                        file=str(bricks_file),
                        message=f"Brick '{brick_id}': Excluded field '{field}' must not be present",
                        code="EXCLUDED_FIELD_PRESENT",
                        field=field,
                    )
                )

        # Validate units
        units = brick.get("units", [])
        for unit in units:
            # Check unit prefix
            if not unit_prefix_pattern.match(unit):
                result.add_error(
                    ValidationError(
                        file=str(bricks_file),
                        message=f"Brick '{brick_id}': Unit '{unit}' has invalid prefix (must start with M-, C-, or F-)",
                        code="INVALID_UNIT_PREFIX",
                    )
                )

            # Check unit exists in graph
            if unit not in graph_node_ids:
                result.add_error(
                    ValidationError(
                        file=str(bricks_file),
                        message=f"Brick '{brick_id}': Unit '{unit}' not found in implementation graph",
                        code="UNIT_NOT_FOUND",
                    )
                )

    return result


@jig.implements("S-022")
def validate_brick_partition(
    bricks_file: Path,
    impl_graph_file: Path,
) -> ValidationResult:
    """
    Validate brick partition constraint.

    Every function must belong to exactly one brick.
    No class methods may be split across bricks.

    Checks:
    - Expand module units (M-) to all contained functions
    - Expand class units (C-) to all method functions
    - Build function-to-brick mapping
    - Detect gaps (functions in 0 bricks)
    - Detect overlaps (functions in 2+ bricks)
    - Detect class splitting
    """
    result = ValidationResult(passed=True, phase_name="brick partition")

    # Load implementation graph
    graph_nodes = _load_graph_nodes(impl_graph_file)
    functions = [node for node in graph_nodes if node.get("type") == "function"]

    # Check bricks.yaml exists
    if not bricks_file.exists():
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message=f"Bricks file not found: {bricks_file}",
                code="FILE_NOT_FOUND",
            )
        )
        return result

    # Parse bricks.yaml
    try:
        bricks_data = yaml.safe_load(bricks_file.read_text())
    except Exception as e:
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message=f"Failed to parse bricks.yaml: {e}",
                code="INVALID_YAML",
            )
        )
        return result

    # Handle both formats: {"bricks": [...]} or direct [...]
    if isinstance(bricks_data, dict) and "bricks" in bricks_data:
        bricks_data = bricks_data["bricks"]

    if not isinstance(bricks_data, list):
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message="bricks.yaml must contain a list of bricks (either as top-level list or under 'bricks:' key)",
                code="INVALID_STRUCTURE",
            )
        )
        return result

    # Build function-to-bricks mapping
    function_to_bricks = defaultdict(list)

    for brick in bricks_data:
        brick_id = brick.get("id", "unknown")
        units = brick.get("units", [])

        # Expand units to functions
        expanded_functions = _expand_units_to_functions(units, graph_nodes)

        for func_id in expanded_functions:
            function_to_bricks[func_id].append(brick_id)

    # Check partition constraints
    gaps = []
    overlaps = []

    for func in functions:
        func_id = func["id"]
        brick_count = len(function_to_bricks[func_id])

        if brick_count == 0:
            gaps.append(func_id)
        elif brick_count > 1:
            overlaps.append((func_id, function_to_bricks[func_id]))

    # Report gaps
    for func_id in gaps:
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message=f"Partition gap: Function '{func_id}' belongs to 0 bricks",
                code="PARTITION_GAP",
            )
        )

    # Report overlaps
    for func_id, brick_ids in overlaps:
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message=f"Partition overlap: Function '{func_id}' belongs to multiple bricks: {', '.join(brick_ids)}",
                code="PARTITION_OVERLAP",
            )
        )

    # Check class splitting
    class_splits = _detect_class_splitting(functions, function_to_bricks)
    for class_id, brick_ids in class_splits:
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message=f"Class splitting: Class '{class_id}' methods split across bricks: {', '.join(brick_ids)}",
                code="CLASS_SPLIT",
            )
        )

    result.items_checked = len(functions)

    return result


def _load_graph_node_ids(graph_file: Path) -> set[str]:
    """Load all node IDs from implementation graph."""
    node_ids = set()
    try:
        with graph_file.open() as f:
            for line in f:
                node = json.loads(line)
                if "id" in node:
                    node_ids.add(node["id"])
    except Exception:
        pass
    return node_ids


def _load_graph_nodes(graph_file: Path) -> list[dict]:
    """Load all nodes from implementation graph."""
    nodes = []
    try:
        with graph_file.open() as f:
            for line in f:
                node = json.loads(line)
                if "id" in node and "type" in node:
                    nodes.append(node)
    except Exception:
        pass
    return nodes


def _expand_units_to_functions(units: list[str], graph_nodes: list[dict]) -> set[str]:
    """
    Expand module and class units to function IDs.

    M-auth.session → all F-auth.session.*
    C-auth.Token → all F-auth.Token.*
    F-auth.login → F-auth.login
    """
    expanded = set()

    for unit in units:
        if unit.startswith("M-"):
            # Module: expand to all functions in that module
            module_path = unit[2:]  # Remove "M-" prefix
            for node in graph_nodes:
                if node.get("type") == "function":
                    func_id = node["id"]
                    # Check if function ID matches module path
                    # F-auth.session.login matches M-auth.session
                    if func_id.startswith(f"F-{module_path}."):
                        expanded.add(func_id)
        elif unit.startswith("C-"):
            # Class: expand to all methods
            class_path = unit[2:]  # Remove "C-" prefix
            for node in graph_nodes:
                if node.get("type") == "function":
                    func_id = node["id"]
                    # Check if function ID is a method of this class
                    # F-auth.Token.__init__ matches C-auth.Token
                    if func_id.startswith(f"F-{class_path}."):
                        expanded.add(func_id)
        elif unit.startswith("F-"):
            # Function: already a function ID
            expanded.add(unit)

    return expanded


def _detect_class_splitting(
    functions: list[dict],
    function_to_bricks: dict[str, list[str]],
) -> list[tuple[str, set[str]]]:
    """
    Detect classes whose methods are split across different bricks.

    Returns list of (class_id, set of brick_ids).
    """
    class_to_bricks = defaultdict(set)

    for func in functions:
        func_id = func["id"]
        # Extract class from function ID if it's a method
        # F-auth.Token.__init__ → C-auth.Token
        if "." in func_id:
            parts = func_id[2:].split(".")  # Remove "F-" prefix
            if len(parts) >= 2:
                # Could be a method: module.Class.method
                potential_class = ".".join(parts[:-1])
                # Check if this looks like a class (has uppercase first letter)
                if parts[-2][0].isupper():
                    class_id = f"C-{potential_class}"
                    bricks = function_to_bricks[func_id]
                    for brick in bricks:
                        class_to_bricks[class_id].add(brick)

    # Find classes split across multiple bricks
    splits = []
    for class_id, brick_ids in class_to_bricks.items():
        if len(brick_ids) > 1:
            splits.append((class_id, brick_ids))

    return splits
