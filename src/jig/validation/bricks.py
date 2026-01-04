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


@jig.implements("S-038")
def validate_brick_layer_constraints(
    bricks_file: Path,
    impl_graph_file: Path,
) -> ValidationResult:
    """
    Validate brick layer constraints based on implementation graph.

    Checks that brick dependencies respect layer hierarchy:
    - Layer N can depend on layer < N
    - Layer 0 can depend on layer 0
    - Layer N (N > 0) cannot depend on same layer N

    Dependencies are derived from function call edges in implementation graph.
    """
    result = ValidationResult(passed=True, phase_name="brick layer constraints")

    # Load implementation graph
    if not impl_graph_file.exists():
        result.add_error(
            ValidationError(
                file=str(impl_graph_file),
                message=f"Implementation graph not found: {impl_graph_file}. Run 'jigy impl rebuild' first.",
                code="GRAPH_NOT_FOUND",
            )
        )
        return result

    graph_nodes = _load_graph_nodes(impl_graph_file)
    functions = [node for node in graph_nodes if node.get("type") == "function"]

    # Load function call edges
    call_edges = []
    try:
        with impl_graph_file.open() as f:
            for line in f:
                item = json.loads(line)
                if item.get("type") == "calls":
                    call_edges.append(item)
    except Exception as e:
        result.add_error(
            ValidationError(
                file=str(impl_graph_file),
                message=f"Failed to load implementation graph: {e}",
                code="INVALID_GRAPH",
            )
        )
        return result

    # Load bricks
    if not bricks_file.exists():
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message=f"Bricks file not found: {bricks_file}",
                code="FILE_NOT_FOUND",
            )
        )
        return result

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

    # Handle both formats
    if isinstance(bricks_data, dict) and "bricks" in bricks_data:
        bricks_data = bricks_data["bricks"]

    if not isinstance(bricks_data, list):
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message="bricks.yaml must contain a list of bricks",
                code="INVALID_STRUCTURE",
            )
        )
        return result

    # Build function-to-brick mapping
    function_to_brick = {}
    brick_layers = {}

    for brick in bricks_data:
        brick_id = brick.get("id", "unknown")
        layer = brick.get("layer")
        units = brick.get("units", [])

        if layer is not None:
            brick_layers[brick_id] = layer

        # Expand units to functions
        expanded_functions = _expand_units_to_functions(units, graph_nodes)
        for func_id in expanded_functions:
            function_to_brick[func_id] = brick_id

    # Derive brick-to-brick dependencies from function calls
    brick_dependencies = defaultdict(set)  # brick_id -> set of (dependency_brick_id, source_func, target_func)

    for edge in call_edges:
        source_func = edge.get("source")
        target_func = edge.get("target")

        if not source_func or not target_func:
            continue

        source_brick = function_to_brick.get(source_func)
        target_brick = function_to_brick.get(target_func)

        # Both functions must be in bricks
        if not source_brick or not target_brick:
            continue

        # Skip self-dependencies (same brick)
        if source_brick == target_brick:
            continue

        # Record dependency
        brick_dependencies[source_brick].add((target_brick, source_func, target_func))

    # Check layer constraints
    for source_brick, dependencies in brick_dependencies.items():
        source_layer = brick_layers.get(source_brick)

        # Skip if source brick has no layer (will be caught by field validation)
        if source_layer is None:
            continue

        for target_brick, source_func, target_func in dependencies:
            target_layer = brick_layers.get(target_brick)

            # Skip if target brick has no layer
            if target_layer is None:
                continue

            # Check layer constraint
            violation = False
            reason = ""

            if source_layer == 0:
                # Layer 0 can only depend on layer 0
                if target_layer != 0:
                    violation = True
                    reason = f"Layer 0 bricks can only depend on other layer 0 bricks, not layer {target_layer}"
            else:
                # Layer N (N > 0) can only depend on layer < N
                if target_layer >= source_layer:
                    violation = True
                    if target_layer == source_layer:
                        reason = f"Same-layer dependencies are only allowed at layer 0, not layer {source_layer}"
                    else:
                        reason = f"Layer {source_layer} cannot depend on layer {target_layer} (upward dependency)"

            if violation:
                # Find brick names for better error messages
                source_brick_name = next(
                    (b.get("name", source_brick) for b in bricks_data if b.get("id") == source_brick),
                    source_brick,
                )
                target_brick_name = next(
                    (b.get("name", target_brick) for b in bricks_data if b.get("id") == target_brick),
                    target_brick,
                )

                result.add_error(
                    ValidationError(
                        file=str(bricks_file),
                        message=f"Layer constraint violation: {source_brick} (layer {source_layer}) depends on {target_brick} (layer {target_layer})\n"
                        f"  → {source_func} calls {target_func}\n"
                        f"  → {reason}",
                        code="LAYER_CONSTRAINT_VIOLATION",
                    )
                )

    result.items_checked = len(brick_dependencies)

    return result


@jig.implements("S-039")
def validate_brick_cycles(
    bricks_file: Path,
    impl_graph_file: Path,
) -> ValidationResult:
    """
    Detect circular dependencies in brick dependency graph.

    All brick dependencies must form a directed acyclic graph (DAG).
    Cycles are detected at all layers including layer 0.
    """
    result = ValidationResult(passed=True, phase_name="brick cycles")

    # Load implementation graph
    if not impl_graph_file.exists():
        result.add_error(
            ValidationError(
                file=str(impl_graph_file),
                message=f"Implementation graph not found: {impl_graph_file}. Run 'jigy impl rebuild' first.",
                code="GRAPH_NOT_FOUND",
            )
        )
        return result

    graph_nodes = _load_graph_nodes(impl_graph_file)

    # Load function call edges
    call_edges = []
    try:
        with impl_graph_file.open() as f:
            for line in f:
                item = json.loads(line)
                if item.get("type") == "calls":
                    call_edges.append(item)
    except Exception as e:
        result.add_error(
            ValidationError(
                file=str(impl_graph_file),
                message=f"Failed to load implementation graph: {e}",
                code="INVALID_GRAPH",
            )
        )
        return result

    # Load bricks
    if not bricks_file.exists():
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message=f"Bricks file not found: {bricks_file}",
                code="FILE_NOT_FOUND",
            )
        )
        return result

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

    # Handle both formats
    if isinstance(bricks_data, dict) and "bricks" in bricks_data:
        bricks_data = bricks_data["bricks"]

    if not isinstance(bricks_data, list):
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message="bricks.yaml must contain a list of bricks",
                code="INVALID_STRUCTURE",
            )
        )
        return result

    # Build function-to-brick mapping
    function_to_brick = {}

    for brick in bricks_data:
        brick_id = brick.get("id", "unknown")
        units = brick.get("units", [])

        # Expand units to functions
        expanded_functions = _expand_units_to_functions(units, graph_nodes)
        for func_id in expanded_functions:
            function_to_brick[func_id] = brick_id

    # Build brick dependency graph (adjacency list)
    brick_graph = defaultdict(set)  # brick_id -> set of brick_ids it depends on
    brick_edges_map = defaultdict(list)  # (source_brick, target_brick) -> list of (source_func, target_func)

    for edge in call_edges:
        source_func = edge.get("source")
        target_func = edge.get("target")

        if not source_func or not target_func:
            continue

        source_brick = function_to_brick.get(source_func)
        target_brick = function_to_brick.get(target_func)

        # Both functions must be in bricks
        if not source_brick or not target_brick:
            continue

        # Skip self-dependencies (same brick)
        if source_brick == target_brick:
            continue

        # Add edge to graph
        brick_graph[source_brick].add(target_brick)
        brick_edges_map[(source_brick, target_brick)].append((source_func, target_func))

    # Detect cycles using DFS
    cycles = _detect_cycles_dfs(brick_graph)

    # Report cycles
    for cycle in cycles:
        # Format cycle path
        cycle_path = " → ".join(cycle)

        # Collect function calls for this cycle
        function_calls = []
        for i in range(len(cycle)):
            current_brick = cycle[i]
            next_brick = cycle[(i + 1) % len(cycle)]

            # Get function calls for this edge
            edge_key = (current_brick, next_brick)
            if edge_key in brick_edges_map:
                for source_func, target_func in brick_edges_map[edge_key]:
                    function_calls.append(f"    {source_func} → {target_func}")

        function_calls_str = "\n".join(function_calls) if function_calls else "    (no function details available)"

        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message=f"Circular dependency detected\n"
                f"\n"
                f"Cycle: {cycle_path}\n"
                f"  Functions involved:\n"
                f"{function_calls_str}\n"
                f"\n"
                f"Fix: Refactor to break the cycle by extracting shared functionality\n"
                f"to a separate brick or removing one of the dependencies.",
                code="CIRCULAR_DEPENDENCY",
            )
        )

    result.items_checked = len(brick_graph)

    return result


def _detect_cycles_dfs(graph: dict[str, set[str]]) -> list[list[str]]:
    """
    Detect all cycles in directed graph using DFS.

    Returns list of cycles, where each cycle is a list of node IDs.
    """
    visited = set()
    rec_stack = set()
    rec_stack_list = []  # To track path for cycle extraction
    cycles = []
    cycles_set = set()  # To avoid duplicate cycles

    def dfs(node: str) -> None:
        visited.add(node)
        rec_stack.add(node)
        rec_stack_list.append(node)

        # Visit all neighbors
        for neighbor in graph.get(node, set()):
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in rec_stack:
                # Found a cycle! Extract the cycle path
                cycle_start_idx = rec_stack_list.index(neighbor)
                cycle = rec_stack_list[cycle_start_idx:] + [neighbor]

                # Normalize cycle to avoid duplicates (start from smallest ID)
                normalized = _normalize_cycle(cycle[:-1])  # Remove duplicate last element
                cycle_key = tuple(normalized)

                if cycle_key not in cycles_set:
                    cycles_set.add(cycle_key)
                    cycles.append(normalized)

        rec_stack_list.pop()
        rec_stack.remove(node)

    # Run DFS from all nodes
    all_nodes = set(graph.keys())
    for neighbor_set in graph.values():
        all_nodes.update(neighbor_set)

    for node in all_nodes:
        if node not in visited:
            dfs(node)

    return cycles


def _normalize_cycle(cycle: list[str]) -> list[str]:
    """
    Normalize cycle to start from the lexicographically smallest node.

    This ensures that cycles are detected uniquely regardless of starting point.
    Example: [B-b, B-c, B-a] and [B-a, B-b, B-c] both normalize to [B-a, B-b, B-c]
    """
    if not cycle:
        return cycle

    min_idx = cycle.index(min(cycle))
    return cycle[min_idx:] + cycle[:min_idx]


# ============================================================================
# Tower Validation (S-086, S-087, S-088, S-089)
# ============================================================================


@jig.implements("S-086", "S-087")
def validate_tower_format(bricks_file: Path) -> ValidationResult:
    """
    Validate brick tower field format.

    Checks:
    - Tower field is optional (S-086)
    - When present, tower must be kebab-case (S-087)
    - Single-brick towers generate typo warning
    """
    from jig.config.schema import TOWER_PATTERN

    result = ValidationResult(passed=True, phase_name="tower format")

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

    # Handle both formats
    if isinstance(bricks_data, dict) and "bricks" in bricks_data:
        bricks_data = bricks_data["bricks"]

    if not isinstance(bricks_data, list):
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message="bricks.yaml must contain a list of bricks",
                code="INVALID_STRUCTURE",
            )
        )
        return result

    result.items_checked = len(bricks_data)

    # Compile tower pattern
    tower_pattern = re.compile(TOWER_PATTERN)

    # Count bricks per tower
    tower_bricks: dict[str, list[str]] = {}
    bricks_with_tower = 0

    for brick in bricks_data:
        brick_id = brick.get("id", "unknown")
        tower = brick.get("tower")

        if tower is not None:
            bricks_with_tower += 1

            # Validate tower format (S-087)
            if not isinstance(tower, str):
                result.add_error(
                    ValidationError(
                        file=str(bricks_file),
                        message=f"Brick '{brick_id}': tower must be a string, not {type(tower).__name__}",
                        code="INVALID_TOWER_TYPE",
                        field="tower",
                    )
                )
            elif not tower_pattern.match(tower):
                result.add_error(
                    ValidationError(
                        file=str(bricks_file),
                        message=f"Brick '{brick_id}': Invalid tower format '{tower}' (must be kebab-case, e.g., 'backend', 'device-logic')",
                        code="INVALID_TOWER_FORMAT",
                        field="tower",
                    )
                )
            else:
                # Track bricks per tower
                if tower not in tower_bricks:
                    tower_bricks[tower] = []
                tower_bricks[tower].append(brick_id)

    # Warn about single-brick towers (possible typo)
    for tower_name, bricks in tower_bricks.items():
        if len(bricks) == 1:
            # Find other towers to suggest
            other_towers = [t for t in tower_bricks.keys() if t != tower_name]
            hint = ""
            if other_towers:
                # Find similar tower name
                for other in other_towers:
                    if _is_similar(tower_name, other):
                        hint = f" Did you mean '{other}'?"
                        break

            result.add_warning(
                ValidationError(
                    file=str(bricks_file),
                    message=f"Tower '{tower_name}' has only 1 brick ({bricks[0]}).{hint}",
                    code="SINGLE_BRICK_TOWER",
                    severity="warning",
                )
            )

    # Set result detail
    if bricks_with_tower == 0:
        result.detail = "single-tower project (no tower fields)"
    else:
        result.detail = f"{len(tower_bricks)} towers, {bricks_with_tower} bricks with tower field"

    return result


def _is_similar(s1: str, s2: str) -> bool:
    """Check if two strings are similar (simple Levenshtein distance check)."""
    # Simple check: one character difference or substring
    if abs(len(s1) - len(s2)) > 2:
        return False
    if s1 in s2 or s2 in s1:
        return True
    # Check character difference
    differences = sum(1 for a, b in zip(s1, s2) if a != b)
    return differences <= 2


@jig.implements("S-088", "S-089")
def validate_tower_isolation(
    bricks_file: Path,
    impl_graph_file: Path,
) -> ValidationResult:
    """
    Validate tower isolation - cross-tower dependencies are forbidden.

    Checks:
    - If any brick has tower field, tower validation is active
    - Cross-tower function calls are detected and reported (S-088)
    - Skipped for single-tower projects (S-089)
    """
    result = ValidationResult(passed=True, phase_name="tower isolation")

    # Load implementation graph
    if not impl_graph_file.exists():
        result.add_error(
            ValidationError(
                file=str(impl_graph_file),
                message=f"Implementation graph not found: {impl_graph_file}. Run 'jigy impl rebuild' first.",
                code="GRAPH_NOT_FOUND",
            )
        )
        return result

    graph_nodes = _load_graph_nodes(impl_graph_file)

    # Load function call edges
    call_edges = []
    try:
        with impl_graph_file.open() as f:
            for line in f:
                item = json.loads(line)
                if item.get("type") == "calls":
                    call_edges.append(item)
    except Exception as e:
        result.add_error(
            ValidationError(
                file=str(impl_graph_file),
                message=f"Failed to load implementation graph: {e}",
                code="INVALID_GRAPH",
            )
        )
        return result

    # Load bricks
    if not bricks_file.exists():
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message=f"Bricks file not found: {bricks_file}",
                code="FILE_NOT_FOUND",
            )
        )
        return result

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

    # Handle both formats
    if isinstance(bricks_data, dict) and "bricks" in bricks_data:
        bricks_data = bricks_data["bricks"]

    if not isinstance(bricks_data, list):
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message="bricks.yaml must contain a list of bricks",
                code="INVALID_STRUCTURE",
            )
        )
        return result

    # Build brick-to-tower mapping
    brick_towers: dict[str, Optional[str]] = {}
    has_any_tower = False

    for brick in bricks_data:
        brick_id = brick.get("id", "unknown")
        tower = brick.get("tower")
        brick_towers[brick_id] = tower
        if tower is not None:
            has_any_tower = True

    # If no bricks have tower field, skip validation (single-tower project)
    if not has_any_tower:
        result.detail = "single-tower project, isolation check skipped"
        return result

    # Build function-to-brick mapping
    function_to_brick: dict[str, str] = {}

    for brick in bricks_data:
        brick_id = brick.get("id", "unknown")
        units = brick.get("units", [])

        # Expand units to functions
        expanded_functions = _expand_units_to_functions(units, graph_nodes)
        for func_id in expanded_functions:
            function_to_brick[func_id] = brick_id

    # Check for cross-tower dependencies
    violations: list[tuple[str, str, str, str, str, str]] = []  # (source_brick, source_tower, target_brick, target_tower, source_func, target_func)

    for edge in call_edges:
        source_func = edge.get("source")
        target_func = edge.get("target")

        if not source_func or not target_func:
            continue

        source_brick = function_to_brick.get(source_func)
        target_brick = function_to_brick.get(target_func)

        # Both functions must be in bricks
        if not source_brick or not target_brick:
            continue

        # Skip same-brick dependencies
        if source_brick == target_brick:
            continue

        # Get towers
        source_tower = brick_towers.get(source_brick)
        target_tower = brick_towers.get(target_brick)

        # If either has no tower, treat as "default" tower
        source_tower = source_tower or "default"
        target_tower = target_tower or "default"

        # Check for cross-tower dependency
        if source_tower != target_tower:
            violations.append((source_brick, source_tower, target_brick, target_tower, source_func, target_func))

    # Report violations
    for source_brick, source_tower, target_brick, target_tower, source_func, target_func in violations:
        result.add_error(
            ValidationError(
                file=str(bricks_file),
                message=f"Cross-tower dependency forbidden:\n"
                f"  {source_brick} (tower: {source_tower}) → {target_brick} (tower: {target_tower})\n"
                f"  {source_func} calls {target_func}\n"
                f"  Fix: Use INTENT specifications instead of direct code imports.",
                code="CROSS_TOWER_DEPENDENCY",
            )
        )

    result.items_checked = len(call_edges)
    result.detail = f"{len(violations)} cross-tower violations"
    return result
