"""JIG project initialization.

This module provides the core logic for initializing JIG projects,
creating the directory structure, configuration files, and managing
idempotent behavior.
"""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import jig
from jig.templates import (
    BRICKS_YAML_TEMPLATE,
    CHARTER_MD_TEMPLATE,
    CONTEXT_JIG_MD_TEMPLATE,
    JIG_TOML_TEMPLATE,
    SKILL_MD_TEMPLATE,
)


@dataclass
class InitResult:
    """Result of a project initialization operation.

    Attributes:
        success: Whether the initialization succeeded.
        paths_created: List of paths that were created during initialization.
        error: Error message if initialization failed, None otherwise.
    """

    success: bool
    paths_created: list[Path] = field(default_factory=list)
    error: str | None = None


def _detect_dig(project_root: Path) -> bool:
    """Detect if DIG is present in the project.

    Args:
        project_root: Path to the project root directory.

    Returns:
        True if dig/ directory or dig.toml exists, False otherwise.
    """
    return (project_root / "dig").is_dir() or (project_root / "dig.toml").exists()


def _update_gitignore(project_root: Path, entry: str = "jig/generated/") -> bool:
    """Update .gitignore to include the specified entry.

    Args:
        project_root: Path to the project root directory.
        entry: The entry to add to .gitignore.

    Returns:
        True if .gitignore was modified/created, False if entry already present.
    """
    gitignore_path = project_root / ".gitignore"

    if gitignore_path.exists():
        content = gitignore_path.read_text()
        # Check if entry is already present (exact line match)
        lines = content.splitlines()
        if entry.rstrip("/") in [line.rstrip("/") for line in lines]:
            return False
        if entry in lines:
            return False

        # Append entry with proper newline handling
        if content and not content.endswith("\n"):
            content += "\n"
        content += entry + "\n"
        gitignore_path.write_text(content)
    else:
        # Create new .gitignore
        gitignore_path.write_text(entry + "\n")

    return True


def _read_project_name_from_toml(project_root: Path) -> str | None:
    """Read project name from existing jig.toml if present.

    Args:
        project_root: Path to the project root directory.

    Returns:
        The project name if found in jig.toml, None otherwise.
    """
    jig_toml_path = project_root / "jig.toml"
    if not jig_toml_path.exists():
        return None

    try:
        with open(jig_toml_path, "rb") as f:
            config = tomllib.load(f)
        return config.get("name")
    except Exception:
        return None


def _find_existing_charter(jig_dir: Path) -> Path | None:
    """Find an existing Charter file in the jig directory.

    Supports both legacy Charter.md and new Charter_<name>.md naming.

    Args:
        jig_dir: Path to the jig/ directory.

    Returns:
        Path to existing charter file if found, None otherwise.
    """
    if not jig_dir.exists():
        return None

    charters = list(jig_dir.glob("Charter*.md"))
    return charters[0] if charters else None


@jig.implements("S-096", "S-100", "S-102")
def init_project(
    project_root: Path,
    project_name: str | None = None,
    force: bool = False,
) -> InitResult:
    """Initialize a JIG project with the required directory structure.

    Creates the following structure:
        project_root/
        ├── jig.toml                    # Configuration file
        ├── jig/
        │   ├── Charter_<project>.md    # Project charter
        │   ├── architecture/           # Empty directory
        │   ├── outcomes/               # Empty directory
        │   ├── specifications/         # Empty directory
        │   ├── bricks.yaml             # Brick definitions scaffold
        │   └── generated/              # Machine-written files (gitignored)
        └── .gitignore                  # Updated to ignore jig/generated/

    The function is idempotent:
    - Directories are created only if they don't exist
    - Files are created only if they don't exist (unless force=True for jig.toml)
    - Charter and bricks.yaml are NEVER overwritten (even with force)
    - jig/generated/ is always ensured to exist

    Args:
        project_root: Path to the project root directory.
        project_name: Optional project name. If not provided, uses the
            project_root directory name.
        force: If True, allows overwriting jig.toml. Does NOT affect
            Charter or bricks.yaml (they are never overwritten).

    Returns:
        InitResult with success status, paths created, and any error message.
    """
    paths_created: list[Path] = []

    try:
        # Derive project name: CLI flag > jig.toml > directory name
        if project_name is None:
            project_name = _read_project_name_from_toml(project_root)
        if project_name is None:
            project_name = project_root.name

        # Detect DIG presence for include_dig setting
        include_dig = _detect_dig(project_root)

        # Create jig.toml
        jig_toml_path = project_root / "jig.toml"
        if not jig_toml_path.exists() or force:
            # Generate content with project name and correct include_dig value
            content = JIG_TOML_TEMPLATE.format(name=project_name)
            if not include_dig:
                content = content.replace("include_dig = true", "include_dig = false")
            jig_toml_path.write_text(content)
            paths_created.append(jig_toml_path)

        # Create jig/ directory
        jig_dir = project_root / "jig"
        if not jig_dir.exists():
            jig_dir.mkdir(parents=True)
            paths_created.append(jig_dir)

        # Create subdirectories
        subdirs = ["architecture", "outcomes", "specifications", "generated"]
        for subdir in subdirs:
            subdir_path = jig_dir / subdir
            if not subdir_path.exists():
                subdir_path.mkdir(parents=True)
                paths_created.append(subdir_path)

        # Create Charter_<project>.md (NEVER overwrite, skip if any Charter exists)
        existing_charter = _find_existing_charter(jig_dir)
        if existing_charter is None:
            charter_filename = f"Charter_{project_name}.md"
            charter_path = jig_dir / charter_filename
            charter_path.write_text(CHARTER_MD_TEMPLATE)
            paths_created.append(charter_path)

        # Create bricks.yaml (NEVER overwrite)
        bricks_path = jig_dir / "bricks.yaml"
        if not bricks_path.exists():
            bricks_path.write_text(BRICKS_YAML_TEMPLATE)
            paths_created.append(bricks_path)

        # Update .gitignore
        if _update_gitignore(project_root):
            gitignore_path = project_root / ".gitignore"
            paths_created.append(gitignore_path)

        return InitResult(success=True, paths_created=paths_created)

    except Exception as e:
        return InitResult(success=False, paths_created=paths_created, error=str(e))


@jig.implements("S-101")
def install_skills(project_root: Path, global_install: bool = False) -> list[Path]:
    """Install JIG skill files for AI agents.

    Creates skill files that help AI agents understand and work with JIG:
        - SKILL.md - Skill definition for /jig command
        - contextJIG.md - Universal JIG mental model

    Args:
        project_root: Path to the project root directory (used for local install).
        global_install: If True, installs to ~/.agent/skills/jig/ instead of
            project-local .agent/skills/jig/.

    Returns:
        List of paths created/overwritten.

    Notes:
        - Skills are always overwritten (they are templates, not user content)
        - Works independently of jig/ structure existence
    """
    paths_created: list[Path] = []

    # Determine installation directory
    if global_install:
        install_dir = Path.home() / ".agent" / "skills" / "jig"
    else:
        install_dir = project_root / ".agent" / "skills" / "jig"

    # Create directory structure
    install_dir.mkdir(parents=True, exist_ok=True)

    # Install SKILL.md (always overwrite)
    skill_path = install_dir / "SKILL.md"
    skill_path.write_text(SKILL_MD_TEMPLATE)
    paths_created.append(skill_path)

    # Install contextJIG.md (always overwrite)
    context_path = install_dir / "contextJIG.md"
    context_path.write_text(CONTEXT_JIG_MD_TEMPLATE)
    paths_created.append(context_path)

    return paths_created
