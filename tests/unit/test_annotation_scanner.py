# @jig T-JIGY-021 verifies:S-JIGY-008 subsystem:jigy-tool
"""Unit tests for @jig annotation scanner."""

import time
from pathlib import Path
from textwrap import dedent

import pytest

from jig.core.scanner import (
    Annotation,
    AnnotationScanner,
    parse_annotation_line,
)


class TestAnnotationParsing:
    """Test annotation line parsing."""

    def test_parse_simple_annotation(self) -> None:
        """Parse basic annotation with single relationship."""
        line = "# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:auth"
        result = parse_annotation_line(line)

        assert result is not None
        assert result.id == "C-AUTH-001"
        assert result.type == "code"
        assert result.relationships == {"implements": ["S-AUTH-001"]}
        assert result.metadata == {"subsystem": "auth"}

    def test_parse_annotation_with_multiple_relationships(self) -> None:
        """Parse annotation with comma-separated relationship targets."""
        line = "# @jig C-AUTH-002 implements:S-AUTH-001,S-AUTH-002 subsystem:auth"
        result = parse_annotation_line(line)

        assert result is not None
        assert result.id == "C-AUTH-002"
        assert result.relationships == {"implements": ["S-AUTH-001", "S-AUTH-002"]}

    def test_parse_annotation_with_multiple_metadata(self) -> None:
        """Parse annotation with multiple metadata fields."""
        line = "# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:auth interface:public status:active"
        result = parse_annotation_line(line)

        assert result is not None
        assert result.metadata == {
            "subsystem": "auth",
            "interface": "public",
            "status": "active",
        }

    def test_parse_test_annotation(self) -> None:
        """Parse test annotation (T- prefix)."""
        line = "# @jig T-AUTH-001 verifies:S-AUTH-001 subsystem:auth"
        result = parse_annotation_line(line)

        assert result is not None
        assert result.id == "T-AUTH-001"
        assert result.type == "test"
        assert result.relationships == {"verifies": ["S-AUTH-001"]}

    def test_parse_annotation_with_depends(self) -> None:
        """Parse annotation with depends relationship."""
        line = "# @jig C-AUTH-003 implements:S-AUTH-003 depends:C-AUTH-001 subsystem:auth"
        result = parse_annotation_line(line)

        assert result is not None
        assert result.relationships == {
            "implements": ["S-AUTH-003"],
            "depends": ["C-AUTH-001"],
        }

    def test_parse_annotation_extra_whitespace(self) -> None:
        """Parse annotation with extra whitespace."""
        line = "#  @jig   C-AUTH-001   implements:S-AUTH-001   subsystem:auth  "
        result = parse_annotation_line(line)

        assert result is not None
        assert result.id == "C-AUTH-001"

    def test_parse_annotation_invalid_format(self) -> None:
        """Return None for invalid annotation format."""
        line = "# @jig INVALID-FORMAT"
        result = parse_annotation_line(line)

        assert result is None

    def test_parse_annotation_missing_node_id(self) -> None:
        """Return None when node ID is missing."""
        line = "# @jig implements:S-001"
        result = parse_annotation_line(line)

        assert result is None

    def test_parse_non_annotation_line(self) -> None:
        """Return None for non-annotation lines."""
        line = "# This is just a comment"
        result = parse_annotation_line(line)

        assert result is None

    def test_annotation_dataclass_attributes(self) -> None:
        """Verify Annotation dataclass has correct attributes."""
        annotation = Annotation(
            id="C-AUTH-001",
            type="code",
            file="test.py",
            line=42,
            relationships={"implements": ["S-AUTH-001"]},
            metadata={"subsystem": "test"},
        )

        assert annotation.id == "C-AUTH-001"
        assert annotation.type == "code"
        assert annotation.file == "test.py"
        assert annotation.line == 42
        assert annotation.relationships["implements"] == ["S-AUTH-001"]
        assert annotation.metadata["subsystem"] == "test"


class TestFileScanning:
    """Test scanning files for annotations."""

    def test_scan_single_file_with_annotation(self, tmp_path: Path) -> None:
        """Scan file containing one annotation."""
        test_file = tmp_path / "test.py"
        test_file.write_text(dedent("""
            # @jig C-AUTH-001 implements:S-AUTH-001 subsystem:auth
            def some_function():
                pass
        """))

        scanner = AnnotationScanner()
        annotations = scanner.scan_file(test_file)

        assert len(annotations) == 1
        assert annotations[0].id == "C-AUTH-001"
        assert annotations[0].file == str(test_file)
        assert annotations[0].line == 2  # Second line (after newline)

    def test_scan_file_with_multiple_annotations(self, tmp_path: Path) -> None:
        """Scan file containing multiple annotations."""
        test_file = tmp_path / "test.py"
        test_file.write_text(dedent("""
            # @jig C-AUTH-001 implements:S-AUTH-001 subsystem:test
            class TestClass:
                pass
            
            # @jig C-AUTH-002 implements:S-AUTH-002 subsystem:test
            def test_function():
                pass
            
            # @jig T-AUTH-001 verifies:S-AUTH-001 subsystem:test
            def test_validation():
                pass
        """))

        scanner = AnnotationScanner()
        annotations = scanner.scan_file(test_file)

        assert len(annotations) == 3
        assert annotations[0].id == "C-AUTH-001"
        assert annotations[1].id == "C-AUTH-002"
        assert annotations[2].id == "T-AUTH-001"

    def test_scan_file_with_no_annotations(self, tmp_path: Path) -> None:
        """Scan file with no annotations."""
        test_file = tmp_path / "test.py"
        test_file.write_text(dedent("""
            # Regular comment
            def some_function():
                # Another comment
                pass
        """))

        scanner = AnnotationScanner()
        annotations = scanner.scan_file(test_file)

        assert len(annotations) == 0

    def test_scan_file_with_invalid_annotations(self, tmp_path: Path) -> None:
        """Scan file with invalid annotations (should skip them)."""
        test_file = tmp_path / "test.py"
        test_file.write_text(dedent("""
            # @jig INVALID-FORMAT
            # @jig C-AUTH-001 implements:S-AUTH-001 subsystem:test
            # @jig ANOTHER-INVALID
        """))

        scanner = AnnotationScanner()
        annotations = scanner.scan_file(test_file)

        assert len(annotations) == 1
        assert annotations[0].id == "C-AUTH-001"

    def test_scan_nonexistent_file(self, tmp_path: Path) -> None:
        """Scan non-existent file returns empty list."""
        scanner = AnnotationScanner()
        annotations = scanner.scan_file(tmp_path / "nonexistent.py")

        assert len(annotations) == 0


class TestDirectoryScanning:
    """Test scanning directories for annotations."""

    def test_scan_directory_with_python_files(self, tmp_path: Path) -> None:
        """Scan directory containing Python files."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        (src_dir / "file1.py").write_text("# @jig C-AUTH-001 implements:S-001 subsystem:test")
        (src_dir / "file2.py").write_text("# @jig C-AUTH-002 implements:S-002 subsystem:test")
        (src_dir / "file3.py").write_text("# No annotation")

        scanner = AnnotationScanner()
        annotations = scanner.scan_directory(src_dir)

        assert len(annotations) == 2
        ids = {a.id for a in annotations}
        assert ids == {"C-AUTH-001", "C-AUTH-002"}

    def test_scan_directory_recursively(self, tmp_path: Path) -> None:
        """Scan directory recursively for annotations."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        subdir = src_dir / "subdir"
        subdir.mkdir()

        (src_dir / "file1.py").write_text("# @jig C-AUTH-001 implements:S-001 subsystem:test")
        (subdir / "file2.py").write_text("# @jig C-AUTH-002 implements:S-002 subsystem:test")

        scanner = AnnotationScanner()
        annotations = scanner.scan_directory(src_dir)

        assert len(annotations) == 2

    def test_scan_directory_filters_by_extension(self, tmp_path: Path) -> None:
        """Scan directory only processes .py files."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        (src_dir / "file.py").write_text("# @jig C-AUTH-001 implements:S-001 subsystem:test")
        (src_dir / "file.txt").write_text("# @jig C-AUTH-002 implements:S-002 subsystem:test")
        (src_dir / "file.md").write_text("# @jig C-AUTH-003 implements:S-003 subsystem:test")

        scanner = AnnotationScanner()
        annotations = scanner.scan_directory(src_dir)

        assert len(annotations) == 1
        assert annotations[0].id == "C-AUTH-001"

    def test_scan_multiple_directories(self, tmp_path: Path) -> None:
        """Scan multiple directories."""
        src_dir = tmp_path / "src"
        test_dir = tmp_path / "test"
        src_dir.mkdir()
        test_dir.mkdir()

        (src_dir / "code.py").write_text("# @jig C-AUTH-001 implements:S-001 subsystem:test")
        (test_dir / "test.py").write_text("# @jig T-AUTH-001 verifies:S-001 subsystem:test")

        scanner = AnnotationScanner()
        annotations = scanner.scan([src_dir, test_dir])

        assert len(annotations) == 2
        ids = {a.id for a in annotations}
        assert ids == {"C-AUTH-001", "T-AUTH-001"}

    def test_scan_empty_directory(self, tmp_path: Path) -> None:
        """Scan empty directory returns no annotations."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        scanner = AnnotationScanner()
        annotations = scanner.scan_directory(empty_dir)

        assert len(annotations) == 0


class TestDuplicateDetection:
    """Test detection of duplicate annotation IDs."""

    def test_detect_duplicate_in_same_file(self, tmp_path: Path) -> None:
        """Detect duplicate annotation IDs in same file."""
        test_file = tmp_path / "test.py"
        test_file.write_text(dedent("""
            # @jig C-AUTH-001 implements:S-001 subsystem:test
            class A:
                pass
            
            # @jig C-AUTH-001 implements:S-002 subsystem:test
            class B:
                pass
        """))

        scanner = AnnotationScanner()
        annotations = scanner.scan_file(test_file)
        duplicates = scanner.find_duplicates(annotations)

        assert len(duplicates) > 0
        assert "C-AUTH-001" in duplicates

    def test_detect_duplicate_across_files(self, tmp_path: Path) -> None:
        """Detect duplicate annotation IDs across multiple files."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        (src_dir / "file1.py").write_text("# @jig C-AUTH-001 implements:S-001 subsystem:test")
        (src_dir / "file2.py").write_text("# @jig C-AUTH-001 implements:S-002 subsystem:test")

        scanner = AnnotationScanner()
        annotations = scanner.scan_directory(src_dir)
        duplicates = scanner.find_duplicates(annotations)

        assert len(duplicates) > 0
        assert "C-AUTH-001" in duplicates
        assert len(duplicates["C-AUTH-001"]) == 2

    def test_no_duplicates_when_unique(self, tmp_path: Path) -> None:
        """Return empty dict when all annotations are unique."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        (src_dir / "file1.py").write_text("# @jig C-AUTH-001 implements:S-001 subsystem:test")
        (src_dir / "file2.py").write_text("# @jig C-AUTH-002 implements:S-002 subsystem:test")

        scanner = AnnotationScanner()
        annotations = scanner.scan_directory(src_dir)
        duplicates = scanner.find_duplicates(annotations)

        assert len(duplicates) == 0


class TestPerformance:
    """Test scanner performance meets requirements."""

    def test_scan_performance_small_codebase(self, tmp_path: Path) -> None:
        """Verify scanner completes quickly on small codebase."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create 100 files with annotations
        for i in range(100):
            file_path = src_dir / f"file{i}.py"
            file_path.write_text(f"# @jig C-AUTH-{i:03d} implements:S-001 subsystem:test\npass\n")

        scanner = AnnotationScanner()
        start = time.time()
        annotations = scanner.scan_directory(src_dir)
        elapsed = time.time() - start

        assert len(annotations) == 100
        assert elapsed < 1.0  # Should complete in well under 1 second for 100 files

    @pytest.mark.slow
    def test_scan_performance_large_codebase(self, tmp_path: Path) -> None:
        """Verify scanner meets <2s requirement for 10k files.
        
        Note: This test is marked as slow and may be skipped in regular test runs.
        """
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create 10,000 files (mimicking large codebase)
        # Each file has 2-3 annotations
        for i in range(10000):
            subdir = src_dir / f"dir{i // 100}"
            subdir.mkdir(exist_ok=True)
            file_path = subdir / f"file{i}.py"
            
            content = f"""# @jig C-AUTH-{i:05d} implements:S-001 subsystem:test
def func_{i}():
    pass

# @jig T-AUTH-{i:05d} verifies:S-001 subsystem:test
def test_func_{i}():
    pass
"""
            file_path.write_text(content)

        scanner = AnnotationScanner()
        start = time.time()
        annotations = scanner.scan_directory(src_dir)
        elapsed = time.time() - start

        assert len(annotations) == 20000  # 2 annotations per file
        assert elapsed < 2.0, f"Scanner took {elapsed:.2f}s, expected <2s"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_scan_with_unicode_content(self, tmp_path: Path) -> None:
        """Handle files with unicode content."""
        test_file = tmp_path / "test.py"
        test_file.write_text(dedent("""
            # @jig C-AUTH-001 implements:S-001 subsystem:test
            def greet():
                return "Hello 世界 🌍"
        """), encoding="utf-8")

        scanner = AnnotationScanner()
        annotations = scanner.scan_file(test_file)

        assert len(annotations) == 1
        assert annotations[0].id == "C-AUTH-001"

    def test_scan_with_very_long_lines(self, tmp_path: Path) -> None:
        """Handle files with very long lines."""
        test_file = tmp_path / "test.py"
        long_comment = "# " + "x" * 10000 + "\n"
        content = "# @jig C-AUTH-001 implements:S-001 subsystem:test\n" + long_comment
        test_file.write_text(content)

        scanner = AnnotationScanner()
        annotations = scanner.scan_file(test_file)

        assert len(annotations) == 1

    def test_scan_binary_file_skip(self, tmp_path: Path) -> None:
        """Skip binary files gracefully."""
        binary_file = tmp_path / "test.pyc"
        binary_file.write_bytes(b"\x00\x01\x02\x03")

        scanner = AnnotationScanner()
        # Should not raise exception, just return empty list
        annotations = scanner.scan_file(binary_file)

        assert len(annotations) == 0

    def test_scan_file_permission_error(self, tmp_path: Path) -> None:
        """Handle files with permission errors gracefully."""
        # This test might not work on all platforms
        test_file = tmp_path / "test.py"
        test_file.write_text("# @jig C-AUTH-001 implements:S-001 subsystem:test")
        
        # Make file unreadable (may not work on Windows)
        import os
        try:
            os.chmod(test_file, 0o000)
            scanner = AnnotationScanner()
            annotations = scanner.scan_file(test_file)
            assert len(annotations) == 0  # Should skip unreadable file
        finally:
            # Restore permissions for cleanup
            os.chmod(test_file, 0o644)

    def test_annotation_with_special_characters_in_metadata(self, tmp_path: Path) -> None:
        """Parse annotations with special characters in metadata values."""
        # Note: This tests current behavior - may need adjustment based on spec
        test_file = tmp_path / "test.py"
        test_file.write_text("# @jig C-REAL-001 implements:S-001 subsystem:test-core")

        scanner = AnnotationScanner()
        annotations = scanner.scan_file(test_file)

        assert len(annotations) == 1
        assert annotations[0].metadata["subsystem"] == "test-core"


# @jig T-JIGY-031 verifies:S-JIGY-011 subsystem:jigy-tool
class TestFixturePatternDetection:
    """Test Tier 3: Fixture pattern detection to exclude test fixtures."""

    def test_excludes_c_test_pattern(self) -> None:
        """Test that C-TEST-* patterns are excluded."""
        from jig.core.scanner import _is_test_fixture

        assert _is_test_fixture("C-TEST-001")
        assert _is_test_fixture("C-TEST-999")
        assert not _is_test_fixture("C-REAL-001")

    def test_excludes_t_test_pattern(self) -> None:
        """Test that T-TEST-* patterns are excluded."""
        from jig.core.scanner import _is_test_fixture

        assert _is_test_fixture("T-TEST-001")
        assert _is_test_fixture("T-TEST-999")
        assert not _is_test_fixture("T-REAL-001")

    def test_excludes_c_mock_pattern(self) -> None:
        """Test that C-MOCK-* patterns are excluded."""
        from jig.core.scanner import _is_test_fixture

        assert _is_test_fixture("C-MOCK-001")
        assert _is_test_fixture("C-MOCK-999")
        assert not _is_test_fixture("C-REAL-001")

    def test_excludes_c_fixture_pattern(self) -> None:
        """Test that C-FIXTURE-* patterns are excluded."""
        from jig.core.scanner import _is_test_fixture

        assert _is_test_fixture("C-FIXTURE-001")
        assert _is_test_fixture("C-FIXTURE-999")
        assert not _is_test_fixture("C-REAL-001")

    def test_excludes_c_example_pattern(self) -> None:
        """Test that C-EXAMPLE-* patterns are excluded."""
        from jig.core.scanner import _is_test_fixture

        assert _is_test_fixture("C-EXAMPLE-001")
        assert _is_test_fixture("C-EXAMPLE-999")
        assert not _is_test_fixture("C-REAL-001")

    def test_parse_annotation_line_skips_fixtures(self) -> None:
        """Test that parse_annotation_line returns None for fixture patterns."""
        # Test fixture annotations should return None
        assert parse_annotation_line("# @jig C-TEST-001 implements:S-001") is None
        assert parse_annotation_line("# @jig T-TEST-001 verifies:S-001") is None
        assert parse_annotation_line("# @jig C-MOCK-001 implements:S-001") is None
        assert parse_annotation_line("# @jig C-FIXTURE-001 implements:S-001") is None
        assert parse_annotation_line("# @jig C-EXAMPLE-001 implements:S-001") is None

        # Real annotations should parse normally
        result = parse_annotation_line("# @jig C-REAL-001 implements:S-001")
        assert result is not None
        assert result.id == "C-REAL-001"

    def test_scanner_excludes_fixture_annotations(self, tmp_path: Path) -> None:
        """Test that scanner excludes fixture annotations from files."""
        test_file = tmp_path / "test.py"
        test_file.write_text(dedent("""
            # This file contains both real and fixture annotations
            # @jig C-REAL-001 implements:S-REAL-001 subsystem:core
            # @jig C-TEST-001 implements:S-TEST-001 subsystem:test
            # @jig T-TEST-001 verifies:S-TEST-001 subsystem:test
            # @jig C-MOCK-001 implements:S-MOCK-001 subsystem:mock
            # @jig C-REAL-002 implements:S-REAL-002 subsystem:core
        """))

        scanner = AnnotationScanner()
        annotations = scanner.scan_file(test_file)

        # Should only find C-REAL-001 and C-REAL-002 (real annotations)
        assert len(annotations) == 2
        node_ids = {ann.id for ann in annotations}
        assert node_ids == {"C-REAL-001", "C-REAL-002"}

    def test_scanner_no_false_positives(self, tmp_path: Path) -> None:
        """Test that scanner doesn't exclude valid node IDs that look similar."""
        test_file = tmp_path / "test.py"
        test_file.write_text(dedent("""
            # Real nodes that might look similar to fixtures
            # @jig C-TESTING-001 implements:S-REAL-001 subsystem:testing
            # @jig C-MOCKING-001 implements:S-REAL-001 subsystem:mocking
            # @jig T-TESTABLE-001 verifies:S-REAL-001 subsystem:test
        """))

        scanner = AnnotationScanner()
        annotations = scanner.scan_file(test_file)

        # All should be included (they don't match the exact fixture patterns)
        assert len(annotations) == 3
        node_ids = {ann.id for ann in annotations}
        assert node_ids == {"C-TESTING-001", "C-MOCKING-001", "T-TESTABLE-001"}

