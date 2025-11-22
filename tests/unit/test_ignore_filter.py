# @jig T-JIGY-030 verifies:S-JIGY-011 subsystem:jigy-tool
"""Tests for .jigignore filtering (Tier 1 exclusion filtering)."""

import pytest
from pathlib import Path
from jig.core.ignore_filter import IgnoreFilter


class TestIgnoreFilterBasics:
    """Test basic IgnoreFilter functionality."""

    def test_default_patterns_exclude_pycache(self, tmp_path):
        """Test that default patterns exclude __pycache__."""
        ignore_filter = IgnoreFilter(tmp_path)

        pycache_path = tmp_path / "src" / "__pycache__"
        assert ignore_filter.should_exclude(pycache_path)

    def test_default_patterns_exclude_pyc_files(self, tmp_path):
        """Test that default patterns exclude .pyc files."""
        ignore_filter = IgnoreFilter(tmp_path)

        pyc_path = tmp_path / "src" / "module.pyc"
        assert ignore_filter.should_exclude(pyc_path)

    def test_default_patterns_exclude_venv(self, tmp_path):
        """Test that default patterns exclude .venv directory."""
        ignore_filter = IgnoreFilter(tmp_path)

        venv_path = tmp_path / ".venv"
        assert ignore_filter.should_exclude(venv_path)

    def test_default_patterns_allow_python_source(self, tmp_path):
        """Test that default patterns allow .py source files."""
        ignore_filter = IgnoreFilter(tmp_path)

        py_path = tmp_path / "src" / "module.py"
        assert not ignore_filter.should_exclude(py_path)

    def test_paths_outside_project_not_excluded(self, tmp_path):
        """Test that paths outside project root are not excluded."""
        ignore_filter = IgnoreFilter(tmp_path)

        outside_path = Path("/some/other/path/file.pyc")
        assert not ignore_filter.should_exclude(outside_path)


class TestCustomIgnorePatterns:
    """Test custom .jigignore patterns."""

    def test_loads_custom_jigignore_file(self, tmp_path):
        """Test loading patterns from custom .jigignore file."""
        jigignore_path = tmp_path / ".jigignore"
        jigignore_path.write_text("**/test_*.py\n**/conftest.py\n")

        ignore_filter = IgnoreFilter(tmp_path)

        assert "**/test_*.py" in ignore_filter.patterns
        assert "**/conftest.py" in ignore_filter.patterns

    def test_excludes_test_files_with_custom_pattern(self, tmp_path):
        """Test that custom patterns exclude test files."""
        jigignore_path = tmp_path / ".jigignore"
        jigignore_path.write_text("**/test_*.py\n")

        ignore_filter = IgnoreFilter(tmp_path)

        test_file = tmp_path / "tests" / "test_module.py"
        assert ignore_filter.should_exclude(test_file)

    def test_allows_non_test_files_with_custom_pattern(self, tmp_path):
        """Test that custom patterns allow non-test files."""
        jigignore_path = tmp_path / ".jigignore"
        jigignore_path.write_text("**/test_*.py\n")

        ignore_filter = IgnoreFilter(tmp_path)

        source_file = tmp_path / "src" / "module.py"
        assert not ignore_filter.should_exclude(source_file)

    def test_ignores_comments_in_jigignore(self, tmp_path):
        """Test that comments in .jigignore are ignored."""
        jigignore_path = tmp_path / ".jigignore"
        jigignore_path.write_text("# This is a comment\n**/test_*.py\n# Another comment\n")

        ignore_filter = IgnoreFilter(tmp_path)

        # Comments should not be in patterns
        for pattern in ignore_filter.patterns:
            assert not pattern.startswith('#')

    def test_ignores_empty_lines_in_jigignore(self, tmp_path):
        """Test that empty lines in .jigignore are ignored."""
        jigignore_path = tmp_path / ".jigignore"
        jigignore_path.write_text("**/test_*.py\n\n\n**/conftest.py\n")

        ignore_filter = IgnoreFilter(tmp_path)

        # Empty strings should not be in patterns
        assert "" not in ignore_filter.patterns

    def test_handles_missing_jigignore_gracefully(self, tmp_path):
        """Test that missing .jigignore falls back to defaults."""
        # Don't create .jigignore file
        ignore_filter = IgnoreFilter(tmp_path)

        # Should have default patterns
        assert "**/__pycache__/" in ignore_filter.patterns
        assert "**/*.pyc" in ignore_filter.patterns


class TestPatternMatching:
    """Test pattern matching logic."""

    def test_glob_pattern_with_double_star(self, tmp_path):
        """Test that ** matches nested directories."""
        jigignore_path = tmp_path / ".jigignore"
        jigignore_path.write_text("**/__pycache__\n")

        ignore_filter = IgnoreFilter(tmp_path)

        # Should match at any depth
        assert ignore_filter.should_exclude(tmp_path / "__pycache__")
        assert ignore_filter.should_exclude(tmp_path / "src" / "__pycache__")
        assert ignore_filter.should_exclude(tmp_path / "src" / "sub" / "__pycache__")

    def test_simple_pattern_without_double_star(self, tmp_path):
        """Test that simple patterns match anywhere (implicit **)."""
        jigignore_path = tmp_path / ".jigignore"
        jigignore_path.write_text("*.pyc\n")

        ignore_filter = IgnoreFilter(tmp_path)

        # Should match at any depth due to implicit ** prefix
        assert ignore_filter.should_exclude(tmp_path / "file.pyc")
        assert ignore_filter.should_exclude(tmp_path / "src" / "file.pyc")

    def test_pattern_with_directory_slash(self, tmp_path):
        """Test patterns ending with / match directories."""
        jigignore_path = tmp_path / ".jigignore"
        jigignore_path.write_text(".venv/\n")

        ignore_filter = IgnoreFilter(tmp_path)

        venv_dir = tmp_path / ".venv"
        assert ignore_filter.should_exclude(venv_dir)

    def test_can_add_pattern_at_runtime(self, tmp_path):
        """Test adding patterns at runtime."""
        ignore_filter = IgnoreFilter(tmp_path)

        # Add custom pattern
        ignore_filter.add_pattern("**/build/")

        build_dir = tmp_path / "src" / "build"
        assert ignore_filter.should_exclude(build_dir)


class TestIntegrationWithScanner:
    """Test integration with AnnotationScanner."""

    def test_scanner_respects_ignore_filter(self, tmp_path):
        """Test that AnnotationScanner uses ignore filter correctly."""
        from jig.core.scanner import AnnotationScanner

        # Create .jigignore
        jigignore_path = tmp_path / ".jigignore"
        jigignore_path.write_text("test_*.py\n")

        # Create test file with annotation (should be excluded)
        test_file = tmp_path / "test_module.py"
        test_file.write_text("# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:auth\n")

        # Create source file with annotation (should be included)
        src_file = tmp_path / "module.py"
        src_file.write_text("# @jig C-AUTH-002 implements:S-AUTH-001 subsystem:auth\n")

        # Scan with ignore filter
        ignore_filter = IgnoreFilter(tmp_path)
        scanner = AnnotationScanner(ignore_filter=ignore_filter)
        annotations = scanner.scan_directory(tmp_path)

        # Should find only the source file annotation
        assert len(annotations) == 1
        assert annotations[0].id == "C-AUTH-002"
