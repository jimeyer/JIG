#!/usr/bin/env python3
"""Analyze semantic cohesion of modules to identify potential Bricks."""

import ast
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

def extract_module_info(filepath: Path) -> Dict:
    """Extract classes, functions, and their docstrings."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            tree = ast.parse(content, filepath.name)

        info = {
            'classes': [],
            'functions': [],
            'imports_from_jig': set(),
            'external_imports': set()
        }

        # Get module docstring
        docstring = ast.get_docstring(tree)
        if docstring:
            info['module_doc'] = docstring.split('\n')[0]

        # Extract classes and their methods
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                info['classes'].append({
                    'name': node.name,
                    'methods': methods,
                    'doc': ast.get_docstring(node)
                })
            elif isinstance(node, ast.FunctionDef):
                # Only top-level functions
                if isinstance(getattr(node, 'parent', None), ast.Module) or not hasattr(node, 'parent'):
                    info['functions'].append({
                        'name': node.name,
                        'doc': ast.get_docstring(node)
                    })

        # Parse imports
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('from jig.'):
                parts = line.split()
                if len(parts) >= 2:
                    module = parts[1].split('.')[1] if '.' in parts[1] else None
                    if module:
                        info['imports_from_jig'].add(module)
            elif line.startswith('import ') and not line.startswith('import jig'):
                parts = line.split()
                if len(parts) >= 2:
                    info['external_imports'].add(parts[1].split('.')[0])

        return info
    except Exception as e:
        return {'error': str(e)}

def analyze_semantic_groups(src_dir: Path):
    """Group files by semantic responsibility."""

    module_info = {}

    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file) or "__init__" in py_file.name:
            continue

        rel_path = py_file.relative_to(src_dir)
        parts = rel_path.parts

        if parts[0] == "jig" and len(parts) >= 2:
            module = parts[1]
            filename = py_file.stem

            info = extract_module_info(py_file)
            module_info[f"{module}.{filename}"] = info

    return module_info

def print_module_summary(name: str, info: Dict):
    """Print a summary of a module's responsibilities."""
    print(f"\n{'=' * 80}")
    print(f"{name}")
    print('=' * 80)

    if 'module_doc' in info:
        print(f"Purpose: {info['module_doc']}")

    if info.get('classes'):
        print(f"\nClasses ({len(info['classes'])}):")
        for cls in info['classes'][:5]:
            doc = cls['doc'].split('\n')[0] if cls['doc'] else 'No docstring'
            print(f"  • {cls['name']}: {doc}")
            if cls['methods']:
                print(f"    Methods: {', '.join(cls['methods'][:5])}")
                if len(cls['methods']) > 5:
                    print(f"    ... and {len(cls['methods']) - 5} more")

    if info.get('functions'):
        print(f"\nFunctions ({len(info['functions'])}):")
        for func in info['functions'][:8]:
            if not func['name'].startswith('_'):
                doc = func['doc'].split('\n')[0] if func['doc'] else ''
                print(f"  • {func['name']}: {doc}")

    if info.get('imports_from_jig'):
        print(f"\nInternal deps: {', '.join(sorted(info['imports_from_jig']))}")

    if info.get('external_imports'):
        ext = sorted(info['external_imports'])[:10]
        print(f"External deps: {', '.join(ext)}")

if __name__ == "__main__":
    src_dir = Path("src")

    print("=" * 80)
    print("JIG MODULE SEMANTIC ANALYSIS")
    print("Identifying cohesive architectural units (potential Bricks)")
    print("=" * 80)

    module_info = analyze_semantic_groups(src_dir)

    # Group by top-level module
    by_module = defaultdict(dict)
    for name, info in module_info.items():
        module, file = name.split('.', 1)
        by_module[module][file] = info

    # Print organized summary
    for module in ['core', 'cli', 'decompose', 'utils']:
        print(f"\n\n{'#' * 80}")
        print(f"# MODULE: {module.upper()}")
        print(f"{'#' * 80}")

        if module in by_module:
            for filename in sorted(by_module[module].keys()):
                info = by_module[module][filename]
                if 'error' not in info:
                    print_module_summary(f"{module}.{filename}", info)
