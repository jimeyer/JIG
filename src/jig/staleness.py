"""Staleness detection module for JIG graphs.

Determines whether graphs need rebuilding based on git state comparison.
Uses fast git subprocess calls to detect changes without re-analyzing source files.

Implements S-069: Staleness Detection Module
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Optional

import jig
from jig.config import JigConfig


def git_rev_parse(cwd: Path) -> Optional[str]:
    """Get current HEAD SHA.

    Args:
        cwd: Working directory for git command.

    Returns:
        HEAD SHA string, or None if not in a git repo.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def git_tree_hash(cwd: Path, directory: Path) -> Optional[str]:
    """Get tree hash for a directory.

    Uses `git ls-tree` to get the tree object hash for a directory,
    which changes when any file in that directory changes.

    Args:
        cwd: Working directory for git command.
        directory: Directory to get tree hash for.

    Returns:
        Tree hash string, or None if directory not tracked or not in git.
    """
    try:
        # Get relative path from cwd
        try:
            rel_path = directory.resolve().relative_to(cwd.resolve())
        except ValueError:
            # Directory is outside the git repo
            return None

        result = subprocess.run(
            ["git", "ls-tree", "HEAD", str(rel_path)],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Output format: "040000 tree <hash>\t<path>"
            parts = result.stdout.strip().split()
            if len(parts) >= 3:
                return parts[2]
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def git_status_porcelain(cwd: Path, directories: list[Path]) -> list[str]:
    """Get list of dirty (uncommitted) files in directories.

    Args:
        cwd: Working directory for git command.
        directories: Directories to check for dirty files.

    Returns:
        List of relative file paths that are modified/untracked.
    """
    try:
        # Build list of directory paths to check
        dir_args = []
        for directory in directories:
            try:
                rel_path = directory.resolve().relative_to(cwd.resolve())
                dir_args.append(str(rel_path))
            except ValueError:
                continue

        if not dir_args:
            return []

        result = subprocess.run(
            ["git", "status", "--porcelain", "--"] + dir_args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            dirty_files = []
            # Split by newline, don't strip leading spaces (they're part of format)
            for line in result.stdout.rstrip("\n").split("\n"):
                if line and len(line) > 3:
                    # Format: "XY filename" or "XY filename -> newname"
                    # XY is 2 characters (index + worktree status), then a space
                    file_part = line[3:].split(" -> ")[0].strip()
                    if file_part:
                        dirty_files.append(file_part)
            return sorted(dirty_files)
        return []
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []


def _get_input_directories(graph_type: str, config: JigConfig) -> list[Path]:
    """Get input directories for a graph type.

    Args:
        graph_type: One of "impl", "verify", "intent".
        config: JIG configuration.

    Returns:
        List of input directories for this graph type.
    """
    if graph_type == "impl":
        return [config.paths.source]
    elif graph_type == "verify":
        return [config.paths.tests]
    elif graph_type == "intent":
        return [
            config.paths.specifications,
            config.paths.outcomes,
            config.paths.bricks.parent,  # bricks.yaml is in jig_root
        ]
    else:
        return []


def _get_graph_path(graph_type: str, config: JigConfig) -> Path:
    """Get the path to a graph file.

    Args:
        graph_type: One of "impl", "verify", "intent".
        config: JIG configuration.

    Returns:
        Path to the graph NDJSON file.
    """
    graph_names = {
        "impl": "implementation-graph.ndjson",
        "verify": "verification-graph.ndjson",
        "intent": "intent-graph.ndjson",
    }
    return config.paths.generated / graph_names.get(graph_type, "")


def _read_graph_metadata(graph_path: Path) -> Optional[dict[str, Any]]:
    """Read metadata from a graph file.

    Args:
        graph_path: Path to the graph NDJSON file.

    Returns:
        Metadata dictionary from _meta block, or None if unreadable.
    """
    if not graph_path.exists():
        return None

    try:
        with graph_path.open() as f:
            first_line = f.readline()
            if first_line:
                data = json.loads(first_line)
                return data.get("_meta", {})
    except (json.JSONDecodeError, OSError):
        pass
    return None


@jig.implements("S-069")
def is_stale(graph_type: str, config: JigConfig) -> bool:
    """Check if a graph needs rebuilding.

    A graph is stale when:
    - Graph file does not exist
    - Graph metadata cannot be parsed
    - Git HEAD differs AND relevant tree hashes changed
    - Uncommitted files in input directories differ from recorded list

    A graph is current when git state matches recorded metadata exactly.
    Non-git projects always return True (cannot detect changes efficiently).

    Args:
        graph_type: One of "impl", "verify", "intent".
        config: JIG configuration.

    Returns:
        True if graph needs rebuild, False if current.
    """
    graph_path = _get_graph_path(graph_type, config)
    input_dirs = _get_input_directories(graph_type, config)

    # Check if graph exists
    if not graph_path.exists():
        return True

    # Read stored metadata
    metadata = _read_graph_metadata(graph_path)
    if metadata is None:
        return True

    # Check if we have git metadata
    stored_head = metadata.get("git_head")
    stored_tree_hashes = metadata.get("git_tree_hashes", {})
    stored_dirty = metadata.get("git_dirty_files", [])

    # If no git metadata, assume stale (old graph format or non-git project)
    if stored_head is None:
        return True

    # Get current git state
    current_head = git_rev_parse(config.project_root)

    # Non-git project: always stale
    if current_head is None:
        return True

    # Compare dirty files first (fast check)
    current_dirty = git_status_porcelain(config.project_root, input_dirs)
    if sorted(current_dirty) != sorted(stored_dirty):
        return True

    # If HEAD matches and no dirty files changed, likely current
    if current_head == stored_head:
        return False

    # HEAD changed - check tree hashes for relevant directories
    for directory in input_dirs:
        if not directory.exists():
            continue

        try:
            rel_path = str(directory.resolve().relative_to(config.project_root.resolve()))
        except ValueError:
            continue

        stored_hash = stored_tree_hashes.get(rel_path)
        current_hash = git_tree_hash(config.project_root, directory)

        if stored_hash != current_hash:
            return True

    return False


@jig.implements("S-069")
def get_staleness_status(config: JigConfig) -> dict[str, bool]:
    """Get staleness status for all graph types.

    Args:
        config: JIG configuration.

    Returns:
        Dictionary mapping graph type to staleness status.
        {"impl": True/False, "verify": True/False, "intent": True/False}
    """
    return {
        "impl": is_stale("impl", config),
        "verify": is_stale("verify", config),
        "intent": is_stale("intent", config),
    }


@jig.implements("S-068")
def collect_git_metadata(config: JigConfig, input_dirs: list[Path]) -> dict[str, Any]:
    """Collect git metadata for graph generation.

    Called by graph builders to record git state at build time.

    Args:
        config: JIG configuration.
        input_dirs: List of input directories for this graph.

    Returns:
        Dictionary with git_head, git_tree_hashes, git_dirty_files.
        Empty/null values for non-git projects.
    """
    git_head = git_rev_parse(config.project_root)

    if git_head is None:
        # Non-git project
        return {
            "git_head": None,
            "git_tree_hashes": {},
            "git_dirty_files": [],
        }

    # Collect tree hashes for input directories
    tree_hashes = {}
    for directory in input_dirs:
        if not directory.exists():
            continue

        try:
            rel_path = str(directory.resolve().relative_to(config.project_root.resolve()))
        except ValueError:
            continue

        tree_hash = git_tree_hash(config.project_root, directory)
        if tree_hash:
            tree_hashes[rel_path] = tree_hash

    # Collect dirty files
    dirty_files = git_status_porcelain(config.project_root, input_dirs)

    return {
        "git_head": git_head,
        "git_tree_hashes": tree_hashes,
        "git_dirty_files": dirty_files,
    }
