# ABOUTME: Text search across JIG markdown documents (specs, outcomes, architecture, charter).
# ABOUTME: Returns matching docs with id, title, path, and first matching line.

"""Query layer for document search (S-116).

Provides:
- search_docs(): Case-insensitive substring search across JIG documents
"""

from pathlib import Path
from typing import Any

import yaml

import jig


def _load_yaml_frontmatter(file_path: Path) -> dict:
    """Load YAML frontmatter from a markdown file."""
    try:
        content = file_path.read_text()
        if content.startswith("---"):
            end_idx = content.find("---", 3)
            if end_idx != -1:
                frontmatter = content[3:end_idx].strip()
                return yaml.safe_load(frontmatter) or {}
    except Exception:
        pass
    return {}


def _search_file(file_path: Path, query_lower: str) -> dict | None:
    """Search a single markdown file for a query string.

    Returns a result dict if found, None otherwise.
    """
    try:
        content = file_path.read_text()
    except Exception:
        return None

    if query_lower not in content.lower():
        return None

    fm = _load_yaml_frontmatter(file_path)
    doc_id = fm.get("id", file_path.stem)
    title = fm.get("title", file_path.stem)

    # Find first matching line
    match_line = ""
    for line in content.splitlines():
        if query_lower in line.lower():
            match_line = line.strip()
            break

    return {
        "id": doc_id,
        "title": title,
        "path": str(file_path),
        "match": match_line,
    }


@jig.implements("S-116")
def search_docs(query: str, config: Any, limit: int = 20) -> list[dict[str, Any]]:
    """Search JIG markdown documents for a query string.

    Case-insensitive substring match across specifications, outcomes,
    architecture, and charter documents.

    Args:
        query: Search string. Empty string returns [].
        config: JIG configuration (duck-typed, needs .paths).
        limit: Maximum number of results to return.

    Returns:
        List of dicts with id, title, path, match fields.
    """
    if not query:
        return []

    query_lower = query.lower()
    results: list[dict[str, Any]] = []

    # Collect all markdown files to search
    search_paths: list[Path] = []

    # Directories: glob *.md
    for dir_path in [config.paths.specifications, config.paths.outcomes, config.paths.architecture]:
        if dir_path.exists() and dir_path.is_dir():
            search_paths.extend(sorted(dir_path.glob("*.md")))

    # Charter: single file
    charter = config.paths.charter
    if charter.exists() and charter.is_file():
        search_paths.append(charter)

    for file_path in search_paths:
        if len(results) >= limit:
            break
        hit = _search_file(file_path, query_lower)
        if hit is not None:
            results.append(hit)

    return results
