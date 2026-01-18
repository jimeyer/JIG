# ABOUTME: YAML frontmatter editor for markdown files.
# ABOUTME: Parses and writes frontmatter while preserving body content.
"""
YAML frontmatter editor for JIG artifacts.

Provides parsing and writing of markdown files with YAML frontmatter,
preserving body content during modifications.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

import jig


@dataclass
class FrontmatterFile:
    """Represents a markdown file with YAML frontmatter.

    Attributes:
        frontmatter: The parsed YAML frontmatter as a dict.
        body: The markdown body content (everything after the frontmatter).
    """

    frontmatter: dict[str, Any] = field(default_factory=dict)
    body: str = ""

    def set_field(self, field_name: str, value: Any) -> None:
        """Set a frontmatter field to a value.

        Args:
            field_name: Name of the field to set.
            value: Value to set.
        """
        self.frontmatter[field_name] = value

    def add_field_value(self, field_name: str, value: Any) -> None:
        """Append a value to an array field.

        Creates the array if the field doesn't exist.

        Args:
            field_name: Name of the array field.
            value: Value to append.
        """
        if field_name not in self.frontmatter:
            self.frontmatter[field_name] = []
        if isinstance(self.frontmatter[field_name], list):
            self.frontmatter[field_name].append(value)

    def remove_field_value(self, field_name: str, value: Any) -> None:
        """Remove a value from an array field.

        No-op if the field doesn't exist or value is not in the array.

        Args:
            field_name: Name of the array field.
            value: Value to remove.
        """
        if field_name in self.frontmatter and isinstance(
            self.frontmatter[field_name], list
        ):
            self.frontmatter[field_name] = [
                v for v in self.frontmatter[field_name] if v != value
            ]

    def delete_field(self, field_name: str) -> None:
        """Delete a field from frontmatter.

        No-op if the field doesn't exist.

        Args:
            field_name: Name of the field to delete.
        """
        if field_name in self.frontmatter:
            del self.frontmatter[field_name]


@jig.implements("S-105", "S-106")
def parse_frontmatter_file(file_path: Path) -> FrontmatterFile | None:
    """Parse a markdown file with YAML frontmatter.

    Args:
        file_path: Path to the markdown file.

    Returns:
        FrontmatterFile with parsed frontmatter and body, or None if
        parsing fails (no frontmatter, malformed YAML, etc.).
    """
    try:
        content = file_path.read_text()
    except Exception:
        return None

    if not content.startswith("---"):
        return None

    # Split on --- delimiter
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None

    yaml_content = parts[1]
    body = parts[2]

    try:
        frontmatter = yaml.safe_load(yaml_content)
        if frontmatter is None:
            frontmatter = {}
    except yaml.YAMLError:
        return None

    return FrontmatterFile(frontmatter=frontmatter, body=body)


@jig.implements("S-105", "S-106")
def write_frontmatter_file(file_path: Path, fm_file: FrontmatterFile) -> None:
    """Write a FrontmatterFile back to disk.

    Args:
        file_path: Path to write to.
        fm_file: The FrontmatterFile to write.
    """
    yaml_content = yaml.dump(fm_file.frontmatter, default_flow_style=False)
    content = f"---\n{yaml_content}---{fm_file.body}"
    file_path.write_text(content)


def get_h1_heading(body: str) -> str | None:
    """Extract the H1 heading from markdown body.

    Args:
        body: Markdown body content.

    Returns:
        The H1 heading text, or None if not found.
    """
    # Match # at start of line followed by text (not ##)
    match = re.search(r"^# (.+)$", body, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def set_h1_heading(body: str, new_heading: str) -> str:
    """Set or replace the H1 heading in markdown body.

    If no H1 exists, adds one at the start of the body.

    Args:
        body: Markdown body content.
        new_heading: New H1 heading text.

    Returns:
        Body with updated H1 heading.
    """
    # Try to replace existing H1
    new_body, count = re.subn(r"^# .+$", f"# {new_heading}", body, count=1, flags=re.MULTILINE)
    if count > 0:
        return new_body

    # No H1 found, add one at the start
    # Preserve any leading whitespace/newlines
    return f"\n# {new_heading}{body}"
