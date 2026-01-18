# ABOUTME: Fix action implementations for mending JIG artifacts.
# ABOUTME: Each function applies a specific fix action to a file.
"""
Fix action implementations for the JIG mend system.

Each action function takes a file path and parameters, modifying the
file to apply the fix. These are the primitive operations used by
MendContext.commit().

Actions:
- apply_set_field: Set a frontmatter field
- apply_add_field_value: Append to array field
- apply_remove_field_value: Remove from array field
- apply_delete_field: Remove field entirely
- apply_rename_file: Rename file (with parent directory creation)
- apply_sync_title: Sync H1 and frontmatter title
- apply_set_h1: Set the H1 heading
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Literal

import jig
from jig.mend.yaml_editor import (
    get_h1_heading,
    parse_frontmatter_file,
    set_h1_heading,
    write_frontmatter_file,
)


@jig.implements("S-105", "S-106")
def apply_set_field(file_path: Path, field_name: str, value: Any) -> None:
    """Set a frontmatter field to a value.

    Args:
        file_path: Path to the markdown file.
        field_name: Name of the field to set.
        value: Value to set.
    """
    fm_file = parse_frontmatter_file(file_path)
    if fm_file is None:
        return

    fm_file.set_field(field_name, value)
    write_frontmatter_file(file_path, fm_file)


@jig.implements("S-105", "S-106")
def apply_add_field_value(file_path: Path, field_name: str, value: Any) -> None:
    """Append a value to an array field.

    Creates the array if the field doesn't exist.

    Args:
        file_path: Path to the markdown file.
        field_name: Name of the array field.
        value: Value to append.
    """
    fm_file = parse_frontmatter_file(file_path)
    if fm_file is None:
        return

    fm_file.add_field_value(field_name, value)
    write_frontmatter_file(file_path, fm_file)


@jig.implements("S-105", "S-106")
def apply_remove_field_value(file_path: Path, field_name: str, value: Any) -> None:
    """Remove a value from an array field.

    No-op if the field doesn't exist or value is not in the array.

    Args:
        file_path: Path to the markdown file.
        field_name: Name of the array field.
        value: Value to remove.
    """
    fm_file = parse_frontmatter_file(file_path)
    if fm_file is None:
        return

    fm_file.remove_field_value(field_name, value)
    write_frontmatter_file(file_path, fm_file)


@jig.implements("S-105", "S-106")
def apply_delete_field(file_path: Path, field_name: str) -> None:
    """Delete a field from frontmatter.

    No-op if the field doesn't exist.

    Args:
        file_path: Path to the markdown file.
        field_name: Name of the field to delete.
    """
    fm_file = parse_frontmatter_file(file_path)
    if fm_file is None:
        return

    fm_file.delete_field(field_name)
    write_frontmatter_file(file_path, fm_file)


@jig.implements("S-105", "S-106")
def apply_rename_file(old_path: Path, new_path: Path) -> None:
    """Rename a file to a new path.

    Creates parent directories if needed.

    Args:
        old_path: Current file path.
        new_path: New file path.
    """
    # Create parent directories if needed
    new_path.parent.mkdir(parents=True, exist_ok=True)

    # Use shutil.move for cross-filesystem moves
    shutil.move(str(old_path), str(new_path))


@jig.implements("S-105", "S-106")
def apply_sync_title(
    file_path: Path, direction: Literal["to_h1", "to_frontmatter"]
) -> None:
    """Sync H1 heading and frontmatter title field.

    Args:
        file_path: Path to the markdown file.
        direction: Direction of sync:
            - "to_h1": Copy frontmatter title to H1 heading
            - "to_frontmatter": Copy H1 heading to frontmatter title
    """
    fm_file = parse_frontmatter_file(file_path)
    if fm_file is None:
        return

    if direction == "to_h1":
        # Copy frontmatter title to H1
        title = fm_file.frontmatter.get("title")
        if title:
            fm_file.body = set_h1_heading(fm_file.body, title)
    else:
        # Copy H1 to frontmatter title
        h1 = get_h1_heading(fm_file.body)
        if h1:
            fm_file.frontmatter["title"] = h1

    write_frontmatter_file(file_path, fm_file)


@jig.implements("S-105", "S-106")
def apply_set_h1(file_path: Path, heading: str) -> None:
    """Set the H1 heading in the file.

    If no H1 exists, adds one at the start of the body.

    Args:
        file_path: Path to the markdown file.
        heading: New H1 heading text.
    """
    fm_file = parse_frontmatter_file(file_path)
    if fm_file is None:
        return

    fm_file.body = set_h1_heading(fm_file.body, heading)
    write_frontmatter_file(file_path, fm_file)
