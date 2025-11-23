#!/usr/bin/env python3
"""Analyze import patterns in the jig codebase to understand dependencies."""

import ast
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set, List

def extract_imports(filepath: Path) -> Set[str]:
    """Extract all imports from a Python file."""
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read(), filepath.name)

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])

        return imports
    except Exception as e:
        print(f"Error parsing {filepath}: {e}", file=sys.stderr)
        return set()

def analyze_module_dependencies(src_dir: Path) -> Dict[str, Dict[str, List[str]]]:
    """Analyze dependencies between jig modules."""
    module_files = defaultdict(list)
    module_deps = defaultdict(lambda: defaultdict(list))

    # Group files by module
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        rel_path = py_file.relative_to(src_dir)
        parts = rel_path.parts

        if parts[0] == "jig":
            if len(parts) > 2:
                module = parts[1]  # cli, core, utils, decompose
                module_files[module].append(py_file)

    # Analyze each module's dependencies
    for module, files in module_files.items():
        for py_file in files:
            imports = extract_imports(py_file)

            # Filter to jig imports
            jig_imports = [imp for imp in imports if imp == "jig"]

            # Also parse from jig.X imports
            try:
                with open(py_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("from jig."):
                            parts = line.split()
                            if len(parts) >= 2:
                                mod_path = parts[1].split('.')
                                if len(mod_path) >= 2:
                                    imported_module = mod_path[1]
                                    if imported_module != module:
                                        filename = py_file.name
                                        if filename not in module_deps[module][imported_module]:
                                            module_deps[module][imported_module].append(filename)
            except:
                pass

    return module_deps

def analyze_function_responsibilities(src_dir: Path) -> Dict[str, List[str]]:
    """Analyze what each module does based on its functions."""
    module_functions = defaultdict(list)

    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file) or "__init__" in py_file.name:
            continue

        rel_path = py_file.relative_to(src_dir)
        parts = rel_path.parts

        if parts[0] == "jig" and len(parts) >= 2:
            module = parts[1]
            file_name = py_file.stem

            try:
                with open(py_file, 'r') as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if not node.name.startswith('_'):
                            module_functions[f"{module}.{file_name}"].append(node.name)
            except:
                pass

    return module_functions

if __name__ == "__main__":
    src_dir = Path("src")

    print("=" * 80)
    print("JIG MODULE DEPENDENCY ANALYSIS")
    print("=" * 80)
    print()

    # Analyze dependencies
    deps = analyze_module_dependencies(src_dir)

    print("MODULE DEPENDENCIES")
    print("-" * 80)
    for module in sorted(deps.keys()):
        print(f"\n{module.upper()}:")
        if deps[module]:
            for dep_module in sorted(deps[module].keys()):
                files = deps[module][dep_module]
                print(f"  → {dep_module}: {len(files)} files")
                for f in sorted(set(files))[:5]:
                    print(f"      - {f}")
                if len(files) > 5:
                    print(f"      ... and {len(files) - 5} more")
        else:
            print("  (no internal dependencies)")

    print("\n" + "=" * 80)
    print("MODULE RESPONSIBILITIES (Public Functions)")
    print("=" * 80)

    funcs = analyze_function_responsibilities(src_dir)
    for module_file in sorted(funcs.keys()):
        if funcs[module_file]:
            print(f"\n{module_file}:")
            for func in funcs[module_file][:10]:
                print(f"  • {func}")
            if len(funcs[module_file]) > 10:
                print(f"  ... and {len(funcs[module_file]) - 10} more")
