"""Project root auto-discovery for JIG CLI."""

from pathlib import Path

import jig


class ProjectNotFoundError(Exception):
    """Raised when no JIG project root can be found."""

    pass


@jig.implements("S-057")
def find_project_root(start_dir: Path | None = None) -> Path:
    """Find the JIG project root by walking up directories.

    Searches for a `jig/` directory starting from start_dir (or current
    working directory) and walking up the parent chain.

    Args:
        start_dir: Directory to start searching from. Defaults to cwd.

    Returns:
        Path to the project root (parent of the jig/ directory).

    Raises:
        ProjectNotFoundError: If no jig/ directory is found.
    """
    if start_dir is None:
        start_dir = Path.cwd()

    current = start_dir.resolve()

    while True:
        jig_dir = current / "jig"
        if jig_dir.is_dir():
            return current

        parent = current.parent
        if parent == current:
            # Reached filesystem root
            raise ProjectNotFoundError(
                "Not in a JIG project. No jig/ directory found."
            )
        current = parent
