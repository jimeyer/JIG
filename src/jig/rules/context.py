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
from typing import Any

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

    def rollback(self) -> None:
        """Discard all pending changes."""
        self.pending_changes.clear()

    def commit(self) -> None:
        """Apply all pending changes to files.

        Groups changes by file and applies them in order.
        """
        # Group changes by file
        changes_by_file: dict[str, list[_PendingChange]] = {}
        for change in self.pending_changes:
            if change.file not in changes_by_file:
                changes_by_file[change.file] = []
            changes_by_file[change.file].append(change)

        # Apply changes to each file
        for file_path_str, changes in changes_by_file.items():
            self._apply_changes_to_file(file_path_str, changes)

        # Clear pending changes
        self.pending_changes.clear()

    def _apply_changes_to_file(
        self, file_path_str: str, changes: list[_PendingChange]
    ) -> None:
        """Apply a list of changes to a single file.

        Args:
            file_path_str: Path to the file.
            changes: List of changes to apply.
        """
        file_path = Path(file_path_str)
        if not file_path.is_absolute():
            file_path = self.project_root / file_path

        if not file_path.exists():
            return

        # Read file content
        content = file_path.read_text()

        # Parse frontmatter and body
        if not content.startswith("---"):
            return

        parts = content.split("---", 2)
        if len(parts) < 3:
            return

        try:
            frontmatter = yaml.safe_load(parts[1]) or {}
        except Exception:
            return

        body = parts[2]

        # Apply each change to frontmatter
        for change in changes:
            if change.action == "set_field":
                frontmatter[change.params["field"]] = change.params["value"]
            elif change.action == "add_field_value":
                field_name = change.params["field"]
                if field_name not in frontmatter:
                    frontmatter[field_name] = []
                if isinstance(frontmatter[field_name], list):
                    frontmatter[field_name].append(change.params["value"])
            elif change.action == "remove_field_value":
                field_name = change.params["field"]
                if field_name in frontmatter and isinstance(
                    frontmatter[field_name], list
                ):
                    value = change.params["value"]
                    frontmatter[field_name] = [
                        v for v in frontmatter[field_name] if v != value
                    ]
            elif change.action == "delete_field":
                field_name = change.params["field"]
                if field_name in frontmatter:
                    del frontmatter[field_name]

        # Write back
        new_content = "---\n" + yaml.dump(frontmatter, default_flow_style=False) + "---" + body
        file_path.write_text(new_content)
