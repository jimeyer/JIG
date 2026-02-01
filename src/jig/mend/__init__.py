# ABOUTME: Mend module for applying fixes to JIG artifacts.
# ABOUTME: Provides YAML editor, action functions, and mend engine for file modifications.
"""
Mend module for JIG fix application.

This module provides:
- FrontmatterFile: Dataclass for manipulating frontmatter
- parse_frontmatter_file: Parse markdown file with YAML frontmatter
- write_frontmatter_file: Write modified frontmatter back to file
- Action functions: apply_set_field, apply_add_field_value, etc.
- Engine functions: mend_auto, mend_apply, mend_combined
"""

from jig.mend.actions import (
    apply_add_field_value,
    apply_delete_field,
    apply_remove_field_value,
    apply_rename_file,
    apply_set_field,
    apply_set_h1,
    apply_sync_title,
)
from jig.mend.engine import (
    MAX_ITERATIONS,
    mend_apply,
    mend_auto,
    mend_combined,
)
from jig.mend.yaml_editor import (
    FrontmatterFile,
    parse_frontmatter_file,
    write_frontmatter_file,
)

__all__ = [
    "FrontmatterFile",
    "parse_frontmatter_file",
    "write_frontmatter_file",
    "apply_set_field",
    "apply_add_field_value",
    "apply_remove_field_value",
    "apply_delete_field",
    "apply_rename_file",
    "apply_sync_title",
    "apply_set_h1",
    "mend_auto",
    "mend_apply",
    "mend_combined",
    "MAX_ITERATIONS",
]
