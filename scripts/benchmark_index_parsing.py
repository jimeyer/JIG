#!/usr/bin/env python3
"""Benchmark script for graph-index.json parsing performance.

Measures JSON parsing time to validate the 3-5x performance improvement
over YAML parsing (from S025 analysis: YAML ~15-20ms, JSON target <5ms).
"""

import json
import timeit
from pathlib import Path


def benchmark_json_parsing(jig_root: Path) -> None:
    """Measure JSON parsing performance.

    Args:
        jig_root: Path to project root containing jig/ directory
    """
    json_path = jig_root / "jig" / "graph-index.json"

    if not json_path.exists():
        print(f"ERROR: graph-index.json not found at {json_path}")
        print("Run: jigy index rebuild")
        return

    # Read file content once
    json_data = json_path.read_text(encoding='utf-8')

    # Benchmark JSON parsing (1000 iterations for accuracy)
    json_time = timeit.timeit(
        lambda: json.loads(json_data),
        number=1000
    ) / 1000

    # Parse once to get node count
    data = json.loads(json_data)
    node_count = len(data.get("nodes", []))

    # File stats
    file_size = json_path.stat().st_size

    # Display results
    print("=" * 60)
    print("Graph Index Parsing Benchmark")
    print("=" * 60)
    print(f"\nFile: {json_path.relative_to(jig_root)}")
    print(f"Format: JSON")
    print(f"Nodes: {node_count}")
    print(f"File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"\nJSON parse time: {json_time*1000:.2f} ms")

    # Compare to YAML baseline (from S025 analysis)
    yaml_baseline_ms = 15.0  # Conservative estimate from analysis
    speedup = yaml_baseline_ms / (json_time * 1000)

    print(f"\nPerformance:")
    if json_time * 1000 < 5.0:
        print(f"  ✓ Target met: <5ms parse time")
    else:
        print(f"  ⚠ Slower than target: {json_time*1000:.2f}ms")

    print(f"\nComparison to YAML (from S025 analysis):")
    print(f"  YAML baseline: ~{yaml_baseline_ms:.0f}ms")
    print(f"  JSON current:  {json_time*1000:.2f}ms")
    print(f"  Speedup:       ~{speedup:.1f}x faster")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    from pathlib import Path

    # Run from project root
    jig_root = Path.cwd()
    benchmark_json_parsing(jig_root)
