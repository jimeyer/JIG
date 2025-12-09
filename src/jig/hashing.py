"""Content hashing for JIG artifacts.

Implements J022: Content Hashing specification.
All hashes are SHA-256 truncated to 12 hex characters.
"""

import ast
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Union

import yaml

import jig


@jig.implements("S-044")
def compute_hash(content: str) -> str:
    """Compute SHA-256 hash truncated to 12 hex chars.

    Args:
        content: UTF-8 string to hash

    Returns:
        12-character lowercase hex string
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]


@jig.implements("S-045")
def hash_intent_artifact(path: Path) -> str:
    """Hash a specification or outcome file.

    Computes canonical JSON of frontmatter + normalized body.
    Ignores trailing whitespace and line ending differences.

    Args:
        path: Path to .md file with YAML frontmatter

    Returns:
        12-character jig_hash
    """
    content = path.read_text(encoding="utf-8")
    # Normalize line endings
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    # Parse frontmatter and body
    parts = content.split("---", 2)
    if len(parts) >= 3:
        frontmatter = yaml.safe_load(parts[1]) or {}
        body = parts[2].strip()
    else:
        frontmatter = {}
        body = content.strip()

    # Canonical representation
    canonical = json.dumps(
        {"body": body, "frontmatter": frontmatter},
        sort_keys=True,
        separators=(",", ":"),
    )

    return compute_hash(canonical)


@jig.implements("S-046")
def hash_function(node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> str:
    """Hash function signature + body, excluding decorators.

    Decorators are tracked separately in 'implements' field.
    Uses ast.unparse() for canonical representation.

    Args:
        node: AST function node

    Returns:
        12-character jig_hash
    """
    # Clone node without decorators
    if isinstance(node, ast.AsyncFunctionDef):
        node_copy = ast.AsyncFunctionDef(
            name=node.name,
            args=node.args,
            body=node.body,
            decorator_list=[],
            returns=node.returns,
            type_comment=getattr(node, "type_comment", None),
        )
    else:
        node_copy = ast.FunctionDef(
            name=node.name,
            args=node.args,
            body=node.body,
            decorator_list=[],
            returns=node.returns,
            type_comment=getattr(node, "type_comment", None),
        )

    # Copy location info from original node (required for ast.unparse)
    ast.copy_location(node_copy, node)
    ast.fix_missing_locations(node_copy)

    # Canonical source via ast.unparse
    canonical = ast.unparse(node_copy)
    return compute_hash(canonical)


@jig.implements("S-047")
def hash_test(node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> str:
    """Hash test function, excluding decorators.

    Same algorithm as hash_function (S-046).

    Args:
        node: AST test function node

    Returns:
        12-character jig_hash
    """
    return hash_function(node)


@jig.implements("S-048")
def hash_brick(brick_dict: dict) -> str:
    """Hash a single brick's definition.

    Args:
        brick_dict: Brick definition dict (id, name, layer, units)

    Returns:
        12-character jig_hash
    """
    canonical = json.dumps(brick_dict, sort_keys=True, separators=(",", ":"))
    return compute_hash(canonical)


@jig.implements("S-049")
def git_blob_hash(file: Path) -> str | None:
    """Get git blob hash for file.

    Returns None if not in a git repo or file not tracked.

    Args:
        file: Path to file

    Returns:
        12-character git blob hash, or None
    """
    try:
        result = subprocess.run(
            ["git", "hash-object", str(file)],
            capture_output=True,
            text=True,
            cwd=file.parent,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()[:12]
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None
