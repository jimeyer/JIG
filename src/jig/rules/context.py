# ABOUTME: Context classes for validation and mending: ValidationContext and MendContext.
# ABOUTME: ValidationContext loads artifacts; MendContext batches and commits repairs.
"""
Context classes for the JIG rules engine.

Provides:
- ValidationContext: Loads all artifacts into a queryable structure for rule execution.
- MendContext: Batches modifications and commits them atomically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

import jig
from jig.rules.base import Artifact


def _parse_frontmatter(file_path: Path) -> dict[str, Any] | None:
    """Parse YAML frontmatter from a markdown file.

    Args:
        file_path: Path to the markdown file.

    Returns:
        Frontmatter dict, or None if parsing fails.
    """
    try:
        content = file_path.read_text()
        if not content.startswith("---"):
            return None

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        return yaml.safe_load(parts[1])
    except Exception:
        return None


def _load_artifacts_from_dir(
    directory: Path, pattern: str, project_root: Path
) -> dict[str, Artifact]:
    """Load artifacts from a directory matching a glob pattern.

    Args:
        directory: Directory to search.
        pattern: Glob pattern (e.g., "S-*.md").
        project_root: Project root for relative path computation.

    Returns:
        Dict mapping artifact ID to Artifact.
    """
    artifacts: dict[str, Artifact] = {}
    if not directory.exists():
        return artifacts

    for file_path in sorted(directory.glob(pattern)):
        frontmatter = _parse_frontmatter(file_path)
        if frontmatter is None:
            continue

        artifact_id = frontmatter.get("id")
        if not artifact_id:
            continue

        relative_path = str(file_path.relative_to(project_root))
        artifacts[artifact_id] = Artifact(
            id=artifact_id,
            file=relative_path,
            frontmatter=frontmatter,
        )

    return artifacts


@jig.implements("S-109")
@dataclass
class ValidationContext:
    """Context for rule validation, providing access to all JIG artifacts.

    Loads specifications, outcomes, architectures, goals, charter, and bricks
    from the JIG directory structure.

    Attributes:
        project_root: Root directory of the JIG project.
        specifications: Dict mapping spec ID to Artifact.
        outcomes: Dict mapping outcome ID to Artifact.
        architectures: Dict mapping architecture ID to Artifact.
        goals: Dict mapping goal ID to Artifact.
        charter: The Charter artifact, or None if not present.
        bricks: List of brick definitions from bricks.yaml.
    """

    project_root: Path
    specifications: dict[str, Artifact] = field(default_factory=dict)
    outcomes: dict[str, Artifact] = field(default_factory=dict)
    architectures: dict[str, Artifact] = field(default_factory=dict)
    goals: dict[str, Artifact] = field(default_factory=dict)
    charter: Artifact | None = None
    bricks: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Load all artifacts after initialization."""
        jig_dir = self.project_root / "jig"

        # Load specifications
        self.specifications = _load_artifacts_from_dir(
            jig_dir / "specifications", "S-*.md", self.project_root
        )

        # Load outcomes
        self.outcomes = _load_artifacts_from_dir(
            jig_dir / "outcomes", "O-*.md", self.project_root
        )

        # Load architectures
        self.architectures = _load_artifacts_from_dir(
            jig_dir / "architecture", "A-*.md", self.project_root
        )

        # Load goals
        self.goals = _load_artifacts_from_dir(
            jig_dir / "goals", "G-*.md", self.project_root
        )

        # Load charter
        charter_path = jig_dir / "Charter.md"
        if charter_path.exists():
            frontmatter = _parse_frontmatter(charter_path)
            if frontmatter is not None:
                self.charter = Artifact(
                    id="Charter",
                    file=str(charter_path.relative_to(self.project_root)),
                    frontmatter=frontmatter,
                )

        # Load bricks
        bricks_path = jig_dir / "bricks.yaml"
        if bricks_path.exists():
            try:
                bricks_data = yaml.safe_load(bricks_path.read_text())
                if bricks_data and "bricks" in bricks_data:
                    self.bricks = bricks_data["bricks"]
            except Exception:
                pass

    def get(self, artifact_id: str) -> Artifact | None:
        """Get an artifact by ID.

        Searches specifications, outcomes, architectures, goals, and charter.

        Args:
            artifact_id: The artifact ID (e.g., "S-001", "O-001").

        Returns:
            The Artifact if found, None otherwise.
        """
        if artifact_id in self.specifications:
            return self.specifications[artifact_id]
        if artifact_id in self.outcomes:
            return self.outcomes[artifact_id]
        if artifact_id in self.architectures:
            return self.architectures[artifact_id]
        if artifact_id in self.goals:
            return self.goals[artifact_id]
        if artifact_id == "Charter" and self.charter:
            return self.charter
        return None

    @property
    def all_artifacts(self) -> list[Artifact]:
        """Return all loaded artifacts as a list."""
        result = list(self.specifications.values())
        result.extend(self.outcomes.values())
        result.extend(self.architectures.values())
        result.extend(self.goals.values())
        if self.charter:
            result.append(self.charter)
        return result


@dataclass
class _PendingChange:
    """Represents a pending change to a file."""

    action: str
    file: str
    params: dict[str, Any]


@jig.implements("S-105", "S-106")
@dataclass
class MendContext:
    """Context for applying fixes, with batched modifications.

    Changes are batched until commit() is called, allowing rollback
    if something goes wrong.

    Attributes:
        project_root: Root directory of the JIG project.
        pending_changes: List of pending changes to apply on commit.
    """

    project_root: Path
    pending_changes: list[_PendingChange] = field(default_factory=list)

    def set_field(self, file: str, field_name: str, value: Any) -> None:
        """Set a frontmatter field to a value.

        Args:
            file: Path to the file (relative or absolute).
            field_name: Name of the field to set.
            value: Value to set.
        """
        self.pending_changes.append(
            _PendingChange(
                action="set_field",
                file=file,
                params={"field": field_name, "value": value},
            )
        )

    def add_field_value(self, file: str, field_name: str, value: Any) -> None:
        """Append a value to an array field.

        Args:
            file: Path to the file.
            field_name: Name of the array field.
            value: Value to append.
        """
        self.pending_changes.append(
            _PendingChange(
                action="add_field_value",
                file=file,
                params={"field": field_name, "value": value},
            )
        )

    def remove_field_value(self, file: str, field_name: str, value: Any) -> None:
        """Remove a value from an array field.

        Args:
            file: Path to the file.
            field_name: Name of the array field.
            value: Value to remove.
        """
        self.pending_changes.append(
            _PendingChange(
                action="remove_field_value",
                file=file,
                params={"field": field_name, "value": value},
            )
        )

    def delete_field(self, file: str, field_name: str) -> None:
        """Delete a field from frontmatter.

        Args:
            file: Path to the file.
            field_name: Name of the field to delete.
        """
        self.pending_changes.append(
            _PendingChange(
                action="delete_field",
                file=file,
                params={"field": field_name},
            )
        )

    def rename_file(self, old_path: str, new_path: str) -> None:
        """Rename a file to a new path.

        Args:
            old_path: Current file path.
            new_path: New file path.
        """
        self.pending_changes.append(
            _PendingChange(
                action="rename_file",
                file=old_path,
                params={"new_path": new_path},
            )
        )

    def sync_title(
        self, file: str, direction: Literal["to_h1", "to_frontmatter"]
    ) -> None:
        """Sync H1 heading and frontmatter title.

        Args:
            file: Path to the file.
            direction: Direction of sync:
                - "to_h1": Copy frontmatter title to H1 heading
                - "to_frontmatter": Copy H1 heading to frontmatter title
        """
        self.pending_changes.append(
            _PendingChange(
                action="sync_title",
                file=file,
                params={"direction": direction},
            )
        )

    def set_h1(self, file: str, heading: str) -> None:
        """Set the H1 heading.

        Args:
            file: Path to the file.
            heading: New H1 heading text.
        """
        self.pending_changes.append(
            _PendingChange(
                action="set_h1",
                file=file,
                params={"heading": heading},
            )
        )

    def rollback(self) -> None:
        """Discard all pending changes."""
        self.pending_changes.clear()

    def commit(self) -> None:
        """Apply all pending changes to files.

        Applies changes in order using the mend actions module.
        """
        for change in self.pending_changes:
            self._apply_change(change)

        # Clear pending changes
        self.pending_changes.clear()

    def _apply_change(self, change: _PendingChange) -> None:
        """Apply a single change using mend actions.

        Args:
            change: The change to apply.
        """
        # Import here to avoid circular imports
        from jig.mend.actions import (
            apply_add_field_value,
            apply_delete_field,
            apply_remove_field_value,
            apply_rename_file,
            apply_set_field,
            apply_set_h1,
            apply_sync_title,
        )

        file_path = Path(change.file)
        if not file_path.is_absolute():
            file_path = self.project_root / file_path

        if change.action == "set_field":
            apply_set_field(file_path, change.params["field"], change.params["value"])
        elif change.action == "add_field_value":
            apply_add_field_value(
                file_path, change.params["field"], change.params["value"]
            )
        elif change.action == "remove_field_value":
            apply_remove_field_value(
                file_path, change.params["field"], change.params["value"]
            )
        elif change.action == "delete_field":
            apply_delete_field(file_path, change.params["field"])
        elif change.action == "rename_file":
            new_path = Path(change.params["new_path"])
            if not new_path.is_absolute():
                new_path = self.project_root / new_path
            apply_rename_file(file_path, new_path)
        elif change.action == "sync_title":
            apply_sync_title(file_path, change.params["direction"])
        elif change.action == "set_h1":
            apply_set_h1(file_path, change.params["heading"])
