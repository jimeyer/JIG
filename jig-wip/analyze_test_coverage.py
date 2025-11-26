#!/usr/bin/env python3
"""Analyze test coverage patterns to understand architectural boundaries."""

from pathlib import Path
from collections import defaultdict
import re

def map_tests_to_sources():
    """Map test files to their source files."""
    test_mapping = defaultdict(list)

    # Unit tests
    for test_file in Path("tests/unit").rglob("*.py"):
        if test_file.name == "__init__.py":
            continue

        # Extract what's being tested from filename
        name = test_file.stem
        if name.startswith("test_"):
            tested = name[5:]  # Remove "test_" prefix

            # Try to find matching source file
            potential_sources = list(Path("src").rglob(f"{tested}.py"))

            test_mapping[tested] = {
                'test_file': str(test_file),
                'source_files': [str(s) for s in potential_sources],
                'type': 'unit'
            }

    # Integration tests
    for test_file in Path("tests/integration").rglob("*.py"):
        if test_file.name == "__init__.py":
            continue

        name = test_file.stem
        if name.startswith("test_"):
            tested = name[5:]

            test_mapping[tested] = {
                'test_file': str(test_file),
                'source_files': [],
                'type': 'integration'
            }

    return test_mapping

def analyze_test_imports():
    """Analyze which modules tests import from."""
    test_imports = defaultdict(set)

    for test_file in Path("tests").rglob("*.py"):
        if "__pycache__" in str(test_file):
            continue

        try:
            with open(test_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("from jig."):
                        parts = line.split()
                        if len(parts) >= 2:
                            module_path = parts[1]
                            # Extract top-level module
                            module_parts = module_path.split('.')
                            if len(module_parts) >= 2:
                                module = module_parts[1]  # cli, core, utils, etc.
                                test_imports[test_file.stem].add(module)
        except:
            pass

    return test_imports

def group_by_architectural_unit():
    """Group sources and tests by architectural responsibility."""

    units = {
        'Intent Management': {
            'source': ['core/parser.py', 'core/validator.py', 'core/validation.py'],
            'tests': ['test_parser', 'test_validator', 'test_validation_core'],
            'description': 'Parse and validate OSTC Intent nodes'
        },
        'Graph Operations': {
            'source': ['core/graph.py', 'core/relationships.py', 'core/index_builder.py'],
            'tests': ['test_graph', 'test_graph_queries', 'test_graph_traversal', 'test_index_rebuild', 'test_relationship_parsing'],
            'description': 'Build and query the Intent graph'
        },
        'Annotation System': {
            'source': ['core/scanner.py', 'core/annotation_validator.py'],
            'tests': ['test_annotation_scanner', 'test_annotation_validation'],
            'description': 'Scan and validate @jig annotations in code'
        },
        'Configuration': {
            'source': ['core/config.py', 'core/ignore_filter.py'],
            'tests': ['test_config', 'test_ignore_filter'],
            'description': 'Configuration and filtering'
        },
        'CLI Interface': {
            'source': ['cli/main.py', 'cli/formatting.py', 'cli/*.py'],
            'tests': ['test_*_command', 'test_graph_commands'],
            'description': 'Command-line interface'
        },
        'Decomposition Analysis': {
            'source': ['decompose/metrics.py'],
            'tests': ['test_decompose_metrics', 'test_decompose_commands'],
            'description': 'Analyze subsystem boundaries and coupling'
        },
        'Utilities': {
            'source': ['utils/io.py', 'utils/yaml_utils.py'],
            'tests': ['test_io', 'test_yaml_utils'],
            'description': 'File I/O and YAML operations'
        }
    }

    return units

if __name__ == "__main__":
    print("=" * 80)
    print("TEST-TO-SOURCE MAPPING ANALYSIS")
    print("=" * 80)
    print()

    test_mapping = map_tests_to_sources()

    print("Unit Tests with Source Mapping:")
    print("-" * 80)
    for tested, info in sorted(test_mapping.items()):
        if info['type'] == 'unit':
            sources = info['source_files'] if info['source_files'] else ['(no direct match)']
            print(f"\n{tested}:")
            print(f"  Test: {info['test_file']}")
            print(f"  Sources:")
            for s in sources:
                print(f"    - {s}")

    print("\n" * 2)
    print("=" * 80)
    print("ARCHITECTURAL UNITS (Potential Bricks)")
    print("=" * 80)

    units = group_by_architectural_unit()

    for unit_name, info in units.items():
        print(f"\n{unit_name}")
        print("-" * 80)
        print(f"Purpose: {info['description']}")
        print(f"\nSource files:")
        for s in info['source']:
            print(f"  • {s}")
        print(f"\nTests:")
        for t in info['tests']:
            print(f"  • {t}")

    print("\n" * 2)
    print("=" * 80)
    print("TEST IMPORT ANALYSIS")
    print("=" * 80)

    test_imports = analyze_test_imports()

    # Group by imported module
    by_module = defaultdict(list)
    for test, modules in test_imports.items():
        for module in modules:
            by_module[module].append(test)

    print("\nTests by imported module:")
    print("-" * 80)
    for module in sorted(by_module.keys()):
        tests = by_module[module]
        print(f"\n{module}: {len(tests)} test files")
        for t in sorted(tests)[:10]:
            print(f"  • {t}")
        if len(tests) > 10:
            print(f"  ... and {len(tests) - 10} more")
