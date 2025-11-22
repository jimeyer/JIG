# @jig C-JIGY-030 implements:S-JIGY-011 subsystem:jigy-tool interface:internal
"""Ignore pattern filtering for JIG scanning.

Implements .jigignore file support (Tier 1 exclusion filtering).
"""

from pathlib import Path
import fnmatch


class IgnoreFilter:
    """Handles .jigignore file parsing and path filtering.

    Supports gitignore-style pattern matching:
    - **/*.pyc - matches any .pyc file in any directory
    - test_*.py - matches test files
    - .venv/ - matches .venv directory
    - # comments - lines starting with # are ignored
    """

    def __init__(self, project_root: Path):
        """Initialize ignore filter.

        Args:
            project_root: Root directory of the JIG project
        """
        self.project_root = project_root
        self.patterns = self._load_ignore_patterns()

    def _load_ignore_patterns(self) -> list[str]:
        """Load patterns from .jigignore file.

        Returns:
            List of ignore patterns. Uses defaults if .jigignore doesn't exist.
        """
        ignore_file = self.project_root / ".jigignore"
        if not ignore_file.exists():
            return self._default_patterns()

        patterns = []
        try:
            with open(ignore_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception as e:
            # Log warning but don't fail - use defaults
            print(f"Warning: Failed to load .jigignore: {e}")
            return self._default_patterns()

        return patterns

    def _default_patterns(self) -> list[str]:
        """Default patterns when .jigignore doesn't exist.

        Returns:
            List of default ignore patterns for common build artifacts
        """
        return [
            "**/__pycache__/",
            "**/*.pyc",
            ".venv/",
            ".pytest_cache/",
            "dist/",
            "build/",
        ]

    def should_exclude(self, path: Path) -> bool:
        """Check if path matches any ignore pattern.

        Args:
            path: Path to check (can be absolute or relative to project root)

        Returns:
            True if path should be excluded, False otherwise
        """
        try:
            # Convert to relative path for pattern matching
            relative = path.relative_to(self.project_root)
        except ValueError:
            # Path is outside project root - don't exclude
            return False

        path_str = str(relative)

        for pattern in self.patterns:
            # Remove trailing slash from pattern for matching
            clean_pattern = pattern.rstrip('/')

            # Try direct match
            if fnmatch.fnmatch(path_str, clean_pattern):
                return True

            # Handle ** patterns - they can match at any depth including root
            if clean_pattern.startswith("**/"):
                # Extract the pattern after **/
                sub_pattern = clean_pattern[3:]  # Remove **/ prefix
                # Match if the sub-pattern matches the path or any suffix
                if fnmatch.fnmatch(path_str, sub_pattern):
                    return True
                # Also try matching any path component
                parts = path_str.split('/')
                for i in range(len(parts)):
                    suffix = '/'.join(parts[i:])
                    if fnmatch.fnmatch(suffix, sub_pattern):
                        return True

            # Try with ** prefix for patterns without it
            if not clean_pattern.startswith("**/"):
                if fnmatch.fnmatch(path_str, f"**/{clean_pattern}"):
                    return True

            # For directory patterns (ending with /), match against directory names
            if pattern.endswith('/'):
                # Match if any path component matches the pattern
                parts = path_str.split('/')
                for part in parts:
                    if fnmatch.fnmatch(part, clean_pattern):
                        return True

        return False

    def add_pattern(self, pattern: str) -> None:
        """Add a pattern to the ignore list at runtime.

        Args:
            pattern: Glob pattern to add
        """
        if pattern not in self.patterns:
            self.patterns.append(pattern)
