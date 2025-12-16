"""Record writer for coverage audit results.

Writes T→F edges to NDJSON record files with proper format for
grep-ability, diff-ability, and staleness detection.
"""

import json
from datetime import date
from pathlib import Path
from typing import Optional

import jig

from jig.audit.coverage import TFEdge


@jig.implements("S-067")
def write_coverage_record(
    edges: list[TFEdge],
    output_dir: Path,
    impl_graph_path: Path,
    verify_graph_path: Path,
    record_date: Optional[date] = None,
) -> Path:
    """Write T→F edges to NDJSON record file.

    Creates a dated record file containing all T→F edges with jig_hash
    values for staleness detection.

    Args:
        edges: List of TFEdge objects to write.
        output_dir: Directory for record files (jig/audits/records/).
        impl_graph_path: Path to implementation graph for function hashes.
        verify_graph_path: Path to verification graph for test hashes.
        record_date: Date for filename. Defaults to today.

    Returns:
        Path to the written record file.
    """
    if record_date is None:
        record_date = date.today()

    # Load hash lookups
    function_hashes = _load_function_hashes(impl_graph_path)
    test_hashes = _load_test_hashes(verify_graph_path)

    # Build records with hashes
    records = []
    for edge in edges:
        record = _build_edge_record(edge, function_hashes, test_hashes)
        records.append(record)

    # Sort by (from.id, to.id)
    records.sort(key=lambda r: (r["from"]["id"], r["to"]["id"]))

    # Write to file
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"coverage-{record_date.isoformat()}.ndjson"

    with open(output_path, "w") as f:
        for record in records:
            f.write(json.dumps(record, separators=(",", ":")) + "\n")

    return output_path


@jig.implements("S-067")
def _load_function_hashes(impl_graph_path: Path) -> dict[str, str]:
    """Load function ID to jig_hash mapping from implementation graph.

    Args:
        impl_graph_path: Path to implementation-graph.ndjson.

    Returns:
        Dict mapping function ID to jig_hash.
    """
    hashes: dict[str, str] = {}

    with open(impl_graph_path) as f:
        for line in f:
            node = json.loads(line)
            if node.get("type") == "function":
                node_id = node.get("id", "")
                jig_hash = node.get("jig_hash", "")
                if node_id and jig_hash:
                    hashes[node_id] = jig_hash

    return hashes


@jig.implements("S-067")
def _load_test_hashes(verify_graph_path: Path) -> dict[str, str]:
    """Load test ID to jig_hash mapping from verification graph.

    Args:
        verify_graph_path: Path to verification-graph.ndjson.

    Returns:
        Dict mapping test ID to jig_hash.
    """
    hashes: dict[str, str] = {}

    with open(verify_graph_path) as f:
        for line in f:
            node = json.loads(line)
            if node.get("type") == "test":
                node_id = node.get("id", "")
                jig_hash = node.get("jig_hash", "")
                if node_id and jig_hash:
                    hashes[node_id] = jig_hash

    return hashes


@jig.implements("S-067")
def _build_edge_record(
    edge: TFEdge,
    function_hashes: dict[str, str],
    test_hashes: dict[str, str],
) -> dict:
    """Build a single edge record with jig_hash values.

    Args:
        edge: TFEdge object.
        function_hashes: Function ID to jig_hash mapping.
        test_hashes: Test ID to jig_hash mapping.

    Returns:
        Dict ready for JSON serialization.
    """
    return {
        "edge": "T->F",
        "from": {
            "id": edge.test_id,
            "jig_hash": test_hashes.get(edge.test_id, ""),
        },
        "to": {
            "id": edge.function_id,
            "jig_hash": function_hashes.get(edge.function_id, ""),
        },
        "result": edge.result,
    }


@jig.implements("S-067")
def cleanup_coverage_file(coverage_file: Path) -> bool:
    """Delete .coverage file after successful processing.

    Args:
        coverage_file: Path to .coverage file.

    Returns:
        True if file was deleted, False if it didn't exist.
    """
    if coverage_file.exists():
        coverage_file.unlink()
        return True
    return False
