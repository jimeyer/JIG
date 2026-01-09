#!/usr/bin/env python3
# ABOUTME: Analyzes jig-dev codebase structural health for Stage 1 CODE audit.
# ABOUTME: Computes layer violations, tower isolation, brick cycles, fan-out/in, cohesion, complexity, and LOC Gini.

"""
Stage 1 CODE Analysis Script

Analyzes the jig-dev codebase to compute metrics for the Five Stage Alignment Audit.
"""

import ast
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def parse_bricks_yaml(bricks_path: Path) -> dict:
    """Parse bricks.yaml and return brick definitions with layer info."""
    import yaml

    content = bricks_path.read_text()
    data = yaml.safe_load(content)

    if isinstance(data, dict) and "bricks" in data:
        bricks = data["bricks"]
    else:
        bricks = data if isinstance(data, list) else []

    return {
        "bricks": bricks,
        "brick_by_id": {b["id"]: b for b in bricks},
        "unit_to_brick": {},
        "brick_layers": {b["id"]: b.get("layer", 0) for b in bricks}
    }


def build_unit_to_brick_map(bricks_data: dict) -> dict[str, str]:
    """Build mapping from unit IDs (M-, C-, F-) to brick IDs."""
    mapping = {}
    for brick in bricks_data["bricks"]:
        brick_id = brick["id"]
        for unit in brick.get("units", []):
            mapping[unit] = brick_id
    return mapping


def extract_imports_from_file(file_path: Path, project_root: Path) -> dict:
    """Extract import information from a Python file."""
    try:
        content = file_path.read_text()
        tree = ast.parse(content, filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError):
        return {"imports": [], "functions": [], "classes": [], "module_name": ""}

    # Derive module name
    rel_path = file_path.relative_to(project_root / "src")
    module_parts = list(rel_path.with_suffix("").parts)
    module_name = ".".join(module_parts)

    imports = []
    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({
                    "type": "import",
                    "module": alias.name,
                    "line": node.lineno
                })
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append({
                    "type": "from_import",
                    "module": node.module,
                    "level": node.level,
                    "line": node.lineno
                })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Only count top-level and class methods
            functions.append({
                "name": node.name,
                "line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "complexity": compute_cyclomatic_complexity(node)
            })
        elif isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "line": node.lineno
            })

    return {
        "file": str(file_path),
        "module_name": module_name,
        "imports": imports,
        "functions": functions,
        "classes": classes
    }


def compute_cyclomatic_complexity(node: ast.AST) -> int:
    """Compute cyclomatic complexity for a function node."""
    complexity = 1  # Base complexity

    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                              ast.With, ast.Assert, ast.comprehension)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            # Each 'and' or 'or' adds a branch
            complexity += len(child.values) - 1
        elif isinstance(child, ast.Try):
            complexity += 1  # For the try block itself

    return complexity


def module_to_brick(module_name: str, unit_to_brick: dict) -> str | None:
    """Map a module name to its brick ID."""
    # Normalize: remove leading jig. if present
    if module_name.startswith("jig."):
        normalized = module_name
    else:
        normalized = f"jig.{module_name}"

    # Try exact match first
    unit_id = f"M-{normalized}"
    if unit_id in unit_to_brick:
        return unit_to_brick[unit_id]

    # Try parent modules
    parts = normalized.split(".")
    for i in range(len(parts), 0, -1):
        partial = ".".join(parts[:i])
        unit_id = f"M-{partial}"
        if unit_id in unit_to_brick:
            return unit_to_brick[unit_id]

    return None


def is_jig_internal_import(module_name: str) -> bool:
    """Check if import is from jig package."""
    return module_name.startswith("jig.") or module_name == "jig"


def analyze_layer_violations(
    file_analyses: list[dict],
    unit_to_brick: dict,
    brick_layers: dict
) -> list[dict]:
    """Find imports from higher layer to lower layer (violations)."""
    violations = []

    for analysis in file_analyses:
        source_module = analysis["module_name"]
        source_brick = module_to_brick(source_module, unit_to_brick)

        if not source_brick:
            continue

        source_layer = brick_layers.get(source_brick, 0)

        for imp in analysis["imports"]:
            imported_module = imp["module"]

            # Only check jig internal imports
            if not is_jig_internal_import(imported_module):
                continue

            # module_to_brick handles normalization
            target_brick = module_to_brick(imported_module, unit_to_brick)

            if not target_brick:
                continue

            target_layer = brick_layers.get(target_brick, 0)

            # Layer violation: higher layer importing from lower layer
            # In a layered architecture, lower layers should not depend on higher
            # Layer 0 = foundation, Layer 1 = application
            # Violation: Layer 0 importing from Layer 1
            if source_layer < target_layer:
                violations.append({
                    "file": analysis["file"],
                    "line": imp["line"],
                    "source_brick": source_brick,
                    "source_layer": source_layer,
                    "target_brick": target_brick,
                    "target_layer": target_layer,
                    "import": imp["module"]
                })

    return violations


def analyze_tower_isolation(
    file_analyses: list[dict],
    unit_to_brick: dict,
    bricks_data: dict
) -> list[dict]:
    """Find cross-tower imports (violations of tower isolation)."""
    # Build brick to tower mapping
    brick_towers = {}
    for brick in bricks_data["bricks"]:
        brick_id = brick["id"]
        tower = brick.get("tower")
        brick_towers[brick_id] = tower

    violations = []

    for analysis in file_analyses:
        source_module = analysis["module_name"]
        source_brick = module_to_brick(source_module, unit_to_brick)

        if not source_brick:
            continue

        source_tower = brick_towers.get(source_brick)

        for imp in analysis["imports"]:
            imported_module = imp["module"]

            if not is_jig_internal_import(imported_module):
                continue

            # module_to_brick handles normalization
            target_brick = module_to_brick(imported_module, unit_to_brick)

            if not target_brick:
                continue

            target_tower = brick_towers.get(target_brick)

            # Cross-tower violation (only if both have towers defined)
            if source_tower and target_tower and source_tower != target_tower:
                violations.append({
                    "file": analysis["file"],
                    "line": imp["line"],
                    "source_brick": source_brick,
                    "source_tower": source_tower,
                    "target_brick": target_brick,
                    "target_tower": target_tower
                })

    return violations


def find_brick_cycles(
    file_analyses: list[dict],
    unit_to_brick: dict
) -> list[list[str]]:
    """Find cycles in brick dependency graph using DFS."""
    # Build brick dependency graph
    graph = defaultdict(set)

    for analysis in file_analyses:
        source_module = analysis["module_name"]
        source_brick = module_to_brick(source_module, unit_to_brick)

        if not source_brick:
            continue

        for imp in analysis["imports"]:
            imported_module = imp["module"]

            if not is_jig_internal_import(imported_module):
                continue

            # module_to_brick handles normalization
            target_brick = module_to_brick(imported_module, unit_to_brick)

            if target_brick and target_brick != source_brick:
                graph[source_brick].add(target_brick)

    # Find SCCs using Tarjan's algorithm
    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    on_stack = {}
    sccs = []

    def strongconnect(v):
        index[v] = index_counter[0]
        lowlinks[v] = index_counter[0]
        index_counter[0] += 1
        on_stack[v] = True
        stack.append(v)

        for w in graph.get(v, []):
            if w not in index:
                strongconnect(w)
                lowlinks[v] = min(lowlinks[v], lowlinks[w])
            elif on_stack.get(w, False):
                lowlinks[v] = min(lowlinks[v], index[w])

        if lowlinks[v] == index[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.append(w)
                if w == v:
                    break
            if len(scc) > 1:  # Only report cycles (SCC size > 1)
                sccs.append(scc)

    all_nodes = set(graph.keys())
    for targets in graph.values():
        all_nodes.update(targets)

    for v in all_nodes:
        if v not in index:
            strongconnect(v)

    return sccs


def compute_fan_metrics(file_analyses: list[dict]) -> dict:
    """Compute fan-out and fan-in metrics."""
    # Fan-out: number of distinct modules imported per file
    fan_out_per_file = {}

    # Fan-in: number of files importing each module
    module_importers = defaultdict(set)

    for analysis in file_analyses:
        file_path = analysis["file"]
        imported_modules = set()

        for imp in analysis["imports"]:
            imported_modules.add(imp["module"])
            module_importers[imp["module"]].add(file_path)

        fan_out_per_file[file_path] = len(imported_modules)

    fan_in_per_module = {m: len(files) for m, files in module_importers.items()}

    max_fan_out = max(fan_out_per_file.values()) if fan_out_per_file else 0
    max_fan_in = max(fan_in_per_module.values()) if fan_in_per_module else 0

    high_fan_out_files = [
        {"file": f, "fan_out": v}
        for f, v in fan_out_per_file.items()
        if v > 10
    ]

    return {
        "max_fan_out": max_fan_out,
        "max_fan_in": max_fan_in,
        "fan_out_per_file": fan_out_per_file,
        "fan_in_per_module": fan_in_per_module,
        "high_fan_out_files": high_fan_out_files
    }


def compute_cohesion(file_analyses: list[dict], unit_to_brick: dict) -> float:
    """Compute mean module cohesion (intra-brick imports / total imports)."""
    cohesion_values = []

    for analysis in file_analyses:
        source_module = analysis["module_name"]
        source_brick = module_to_brick(source_module, unit_to_brick)

        if not source_brick:
            continue

        total_jig_imports = 0
        intra_brick_imports = 0

        for imp in analysis["imports"]:
            imported_module = imp["module"]

            if not is_jig_internal_import(imported_module):
                continue

            total_jig_imports += 1

            # module_to_brick handles normalization
            target_brick = module_to_brick(imported_module, unit_to_brick)

            if target_brick == source_brick:
                intra_brick_imports += 1

        if total_jig_imports > 0:
            cohesion = intra_brick_imports / total_jig_imports
            cohesion_values.append(cohesion)

    return sum(cohesion_values) / len(cohesion_values) if cohesion_values else 1.0


def find_complexity_outliers(file_analyses: list[dict], threshold: int = 10) -> list[dict]:
    """Find functions with cyclomatic complexity > threshold."""
    outliers = []

    for analysis in file_analyses:
        for func in analysis["functions"]:
            if func["complexity"] > threshold:
                outliers.append({
                    "file": analysis["file"],
                    "function": func["name"],
                    "line": func["line"],
                    "complexity": func["complexity"]
                })

    return outliers


def compute_gini_coefficient(values: list[float]) -> float:
    """Compute Gini coefficient for LOC distribution."""
    if not values or len(values) < 2:
        return 0.0

    sorted_values = sorted(values)
    n = len(sorted_values)

    # Mean value
    mean_val = sum(sorted_values) / n
    if mean_val == 0:
        return 0.0

    # Gini formula
    cumsum = 0
    for i, val in enumerate(sorted_values, 1):
        cumsum += (2 * i - n - 1) * val

    gini = cumsum / (n * n * mean_val)
    return max(0.0, min(1.0, gini))


def compute_loc_gini(file_analyses: list[dict]) -> float:
    """Compute Gini coefficient of function sizes."""
    function_sizes = []

    for analysis in file_analyses:
        for func in analysis["functions"]:
            size = func["end_line"] - func["line"] + 1
            function_sizes.append(size)

    return compute_gini_coefficient(function_sizes)


def compute_health_score(
    layer_violations: int,
    tower_violations: int,
    brick_cycles: int,
    max_fan_out: int,
    complexity_outliers: int,
    mean_cohesion: float
) -> int:
    """Compute overall health score 0-100."""
    score = 100

    # Deduct for layer violations (max -30)
    score -= min(30, layer_violations * 5)

    # Deduct for tower violations (max -15)
    score -= min(15, tower_violations * 3)

    # Deduct for brick cycles (max -20)
    score -= min(20, brick_cycles * 10)

    # Deduct for high fan-out (max -10)
    if max_fan_out > 15:
        score -= min(10, (max_fan_out - 15) * 2)

    # Deduct for complexity outliers (max -15)
    score -= min(15, complexity_outliers * 3)

    # Deduct for low cohesion (max -10)
    if mean_cohesion < 0.5:
        score -= int((0.5 - mean_cohesion) * 20)

    return max(0, score)


def build_brick_graph(file_analyses: list[dict], unit_to_brick: dict) -> dict:
    """Build brick dependency graph for output."""
    edges = defaultdict(set)
    all_bricks = set()

    for analysis in file_analyses:
        source_module = analysis["module_name"]
        source_brick = module_to_brick(source_module, unit_to_brick)

        if source_brick:
            all_bricks.add(source_brick)

        if not source_brick:
            continue

        for imp in analysis["imports"]:
            imported_module = imp["module"]

            if not is_jig_internal_import(imported_module):
                continue

            # module_to_brick handles normalization
            target_brick = module_to_brick(imported_module, unit_to_brick)

            if target_brick:
                all_bricks.add(target_brick)
                if target_brick != source_brick:
                    edges[source_brick].add(target_brick)

    return {
        "nodes": sorted(all_bricks),
        "edges": [
            {"source": src, "target": tgt}
            for src, targets in sorted(edges.items())
            for tgt in sorted(targets)
        ]
    }


def main():
    project_root = Path("/Users/jmeyer/Code/jig-dev")
    bricks_path = project_root / "jig" / "bricks.yaml"
    source_dir = project_root / "src" / "jig"
    output_path = project_root / "dig" / "generated" / "audit" / "stage1_code.json"

    # Parse bricks.yaml
    bricks_data = parse_bricks_yaml(bricks_path)
    unit_to_brick = build_unit_to_brick_map(bricks_data)
    brick_layers = bricks_data["brick_layers"]

    # Find all Python files
    python_files = sorted(source_dir.rglob("*.py"))

    # Analyze each file
    file_analyses = []
    for py_file in python_files:
        analysis = extract_imports_from_file(py_file, project_root)
        file_analyses.append(analysis)

    # Compute metrics
    layer_violations = analyze_layer_violations(file_analyses, unit_to_brick, brick_layers)
    tower_violations = analyze_tower_isolation(file_analyses, unit_to_brick, bricks_data)
    brick_cycles = find_brick_cycles(file_analyses, unit_to_brick)
    fan_metrics = compute_fan_metrics(file_analyses)
    mean_cohesion = compute_cohesion(file_analyses, unit_to_brick)
    complexity_outliers = find_complexity_outliers(file_analyses)
    loc_gini = compute_loc_gini(file_analyses)
    brick_graph = build_brick_graph(file_analyses, unit_to_brick)

    # Calculate health score
    health_score = compute_health_score(
        layer_violations=len(layer_violations),
        tower_violations=len(tower_violations),
        brick_cycles=len(brick_cycles),
        max_fan_out=fan_metrics["max_fan_out"],
        complexity_outliers=len(complexity_outliers),
        mean_cohesion=mean_cohesion
    )

    # Build output
    result = {
        "stage": 1,
        "name": "CODE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "C1.1_layer_violations": len(layer_violations),
            "C1.2_tower_isolation": len(tower_violations),
            "C1.3_brick_cycles": len(brick_cycles),
            "C1.4_max_fan_out": fan_metrics["max_fan_out"],
            "C1.5_max_fan_in": fan_metrics["max_fan_in"],
            "C1.6_mean_cohesion": round(mean_cohesion, 2),
            "C1.7_complexity_outliers": len(complexity_outliers),
            "C1.8_loc_gini": round(loc_gini, 2)
        },
        "health_score": health_score,
        "violations": layer_violations[:20],  # Limit to first 20
        "tower_violations": tower_violations[:10],
        "cycles": [{"cycle": c} for c in brick_cycles],
        "outliers": complexity_outliers[:20],
        "high_fan_out": fan_metrics["high_fan_out_files"][:10],
        "brick_graph": brick_graph,
        "files_analyzed": len(python_files),
        "total_functions": sum(len(a["functions"]) for a in file_analyses)
    }

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Stage 1 CODE analysis complete.")
    print(f"  Health Score: {health_score}/100")
    print(f"  Layer Violations: {len(layer_violations)}")
    print(f"  Tower Isolation Violations: {len(tower_violations)}")
    print(f"  Brick Cycles: {len(brick_cycles)}")
    print(f"  Max Fan-Out: {fan_metrics['max_fan_out']}")
    print(f"  Max Fan-In: {fan_metrics['max_fan_in']}")
    print(f"  Mean Cohesion: {mean_cohesion:.2f}")
    print(f"  Complexity Outliers: {len(complexity_outliers)}")
    print(f"  LOC Gini: {loc_gini:.2f}")
    print(f"  Files Analyzed: {len(python_files)}")
    print(f"  Output: {output_path}")


if __name__ == "__main__":
    main()
