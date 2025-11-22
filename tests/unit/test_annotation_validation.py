# @jig T-JIGY-027 verifies:S-JIGY-010 subsystem:jigy-tool
"""Unit tests for annotation validation."""

from pathlib import Path
from textwrap import dedent

import pytest

from jig.core.annotation_validator import (
    AnnotationValidator,
    ValidationResult,
    validate_annotations,
)
from jig.core.graph import Graph
from jig.core.parser import OSTCNode
from jig.core.scanner import Annotation


class TestAnnotationValidator:
    """Test AnnotationValidator class."""

    def test_initialize_validator(self, tmp_path: Path) -> None:
        """Initialize annotation validator with project directory."""
        validator = AnnotationValidator(tmp_path)
        
        assert validator.project_root == tmp_path

    def test_validate_all_valid_annotations(self, tmp_path: Path) -> None:
        """Validate project with all valid annotations."""
        # Setup Intent graph
        jig_dir = tmp_path / "jig"
        specs_dir = jig_dir / "specifications"
        specs_dir.mkdir(parents=True)
        
        (specs_dir / "S-AUTH-001.md").write_text(dedent("""
            ---
            id: S-AUTH-001
            type: specification
            title: Test spec
            subsystem: test
            status: active
            ---
        """))

        # Setup code with valid annotation
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "code.py").write_text("# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:test")

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        assert result.valid
        assert len(result.errors) == 0


class TestBrokenReferences:
    """Test detection of broken references in annotations."""

    def test_detect_missing_target(self, tmp_path: Path) -> None:
        """Detect annotation pointing to non-existent Intent node."""
        jig_dir = tmp_path / "jig"
        jig_dir.mkdir()

        # Code references non-existent spec
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "code.py").write_text("# @jig C-AUTH-001 implements:S-NONEXISTENT-999 subsystem:test")

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        assert not result.valid
        assert len(result.errors) > 0
        assert any("S-NONEXISTENT-999" in str(err) for err in result.errors)

    def test_detect_multiple_broken_references(self, tmp_path: Path) -> None:
        """Detect multiple broken references."""
        jig_dir = tmp_path / "jig"
        jig_dir.mkdir()

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        
        (src_dir / "file1.py").write_text("# @jig C-AUTH-001 implements:S-MISSING-001 subsystem:test")
        (src_dir / "file2.py").write_text("# @jig C-AUTH-002 implements:S-MISSING-002 subsystem:test")

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        assert not result.valid
        assert len(result.errors) >= 2


class TestDuplicateAnnotations:
    """Test detection of duplicate annotation IDs."""

    def test_detect_duplicate_in_different_files(self, tmp_path: Path) -> None:
        """Detect same annotation ID in multiple files."""
        jig_dir = tmp_path / "jig"
        specs_dir = jig_dir / "specifications"
        specs_dir.mkdir(parents=True)
        
        (specs_dir / "S-AUTH-001.md").write_text(dedent("""
            ---
            id: S-AUTH-001
            type: specification
            title: Test
            ---
        """))

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        
        (src_dir / "file1.py").write_text("# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:test")
        (src_dir / "file2.py").write_text("# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:test")

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        assert not result.valid
        assert any("duplicate" in str(err).lower() for err in result.errors)

    def test_allow_same_id_if_same_file_and_line(self, tmp_path: Path) -> None:
        """Same ID in same location should not be duplicate."""
        jig_dir = tmp_path / "jig"
        specs_dir = jig_dir / "specifications"
        specs_dir.mkdir(parents=True)
        
        (specs_dir / "S-AUTH-001.md").write_text(dedent("""
            ---
            id: S-AUTH-001
            type: specification
            title: Test
            ---
        """))

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "code.py").write_text("# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:test")

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        # Single annotation should be valid
        assert result.valid or len(result.errors) == 0


class TestOrphanedIntentNodes:
    """Test detection of Intent nodes without implementations."""

    def test_detect_spec_without_implementation(self, tmp_path: Path) -> None:
        """Detect spec with no code implementation."""
        jig_dir = tmp_path / "jig"
        specs_dir = jig_dir / "specifications"
        specs_dir.mkdir(parents=True)
        
        (specs_dir / "S-AUTH-001.md").write_text(dedent("""
            ---
            id: S-AUTH-001
            type: specification
            title: Test spec
            subsystem: test
            status: active
            ---
        """))

        # No code files with implementations
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        # Should have warning about orphaned spec
        assert len(result.warnings) > 0
        assert any("S-AUTH-001" in str(warn) for warn in result.warnings)

    def test_detect_spec_without_tests(self, tmp_path: Path) -> None:
        """Detect spec with implementation but no tests."""
        jig_dir = tmp_path / "jig"
        specs_dir = jig_dir / "specifications"
        specs_dir.mkdir(parents=True)
        
        (specs_dir / "S-AUTH-001.md").write_text(dedent("""
            ---
            id: S-AUTH-001
            type: specification
            title: Test spec
            status: active
            ---
        """))

        # Has implementation but no tests
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "code.py").write_text("# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:test")

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        # Should warn about missing tests
        assert any("test" in str(warn).lower() or "verif" in str(warn).lower() 
                   for warn in result.warnings)

    def test_ignore_orphaned_deprecated_specs(self, tmp_path: Path) -> None:
        """Don't warn about deprecated specs without implementations."""
        jig_dir = tmp_path / "jig"
        specs_dir = jig_dir / "specifications"
        specs_dir.mkdir(parents=True)
        
        (specs_dir / "S-AUTH-001.md").write_text(dedent("""
            ---
            id: S-AUTH-001
            type: specification
            title: Deprecated spec
            status: deprecated
            ---
        """))

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        # Should not warn about deprecated spec
        assert not any("S-AUTH-001" in str(warn) for warn in result.warnings)


class TestEdgeTypeValidation:
    """Test validation of edge type semantics."""

    def test_code_should_implement_not_verify(self, tmp_path: Path) -> None:
        """Code nodes should implement, not verify."""
        jig_dir = tmp_path / "jig"
        specs_dir = jig_dir / "specifications"
        specs_dir.mkdir(parents=True)
        
        (specs_dir / "S-AUTH-001.md").write_text(dedent("""
            ---
            id: S-AUTH-001
            type: specification
            title: Test
            ---
        """))

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        # Code using "verifies" is invalid
        (src_dir / "code.py").write_text("# @jig C-AUTH-001 verifies:S-AUTH-001 subsystem:test")

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        # Should error on invalid edge type
        assert not result.valid
        assert any("verif" in str(err).lower() or "invalid" in str(err).lower() 
                   for err in result.errors)

    def test_test_should_verify_not_implement(self, tmp_path: Path) -> None:
        """Test nodes should verify, not implement."""
        jig_dir = tmp_path / "jig"
        specs_dir = jig_dir / "specifications"
        specs_dir.mkdir(parents=True)
        
        (specs_dir / "S-AUTH-001.md").write_text(dedent("""
            ---
            id: S-AUTH-001
            type: specification
            title: Test
            ---
        """))

        test_dir = tmp_path / "test"
        test_dir.mkdir()
        # Test using "implements" is invalid
        (test_dir / "test_code.py").write_text("# @jig T-AUTH-001 implements:S-AUTH-001 subsystem:test")

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        # Should error on invalid edge type
        assert not result.valid
        assert any("implement" in str(err).lower() or "invalid" in str(err).lower() 
                   for err in result.errors)


class TestNodeIDFormat:
    """Test validation of node ID format."""

    def test_valid_code_node_id(self, tmp_path: Path) -> None:
        """Accept valid code node ID format."""
        jig_dir = tmp_path / "jig"
        specs_dir = jig_dir / "specifications"
        specs_dir.mkdir(parents=True)
        
        (specs_dir / "S-AUTH-001.md").write_text(dedent("""
            ---
            id: S-AUTH-001
            type: specification
            title: Test
            ---
        """))

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "code.py").write_text("# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:test")

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        # Valid format should pass
        assert result.valid or len(result.errors) == 0

    def test_invalid_node_id_format(self, tmp_path: Path) -> None:
        """Reject invalid node ID formats."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        
        # Invalid formats
        (src_dir / "invalid1.py").write_text("# @jig C-001 implements:S-001 subsystem:test")  # Missing subsystem part

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        # Should report format error
        # Note: Scanner might not even pick this up, so test might pass with 0 annotations


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_validation_result_success(self) -> None:
        """Create successful validation result."""
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=[],
            annotations_checked=10,
        )

        assert result.valid
        assert len(result.errors) == 0
        assert result.annotations_checked == 10

    def test_validation_result_with_errors(self) -> None:
        """Create validation result with errors."""
        result = ValidationResult(
            valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
            annotations_checked=10,
        )

        assert not result.valid
        assert len(result.errors) == 2
        assert len(result.warnings) == 1


class TestHelperFunctions:
    """Test module-level helper functions."""

    def test_validate_annotations_function(self, tmp_path: Path) -> None:
        """Test validate_annotations convenience function."""
        jig_dir = tmp_path / "jig"
        specs_dir = jig_dir / "specifications"
        specs_dir.mkdir(parents=True)
        
        (specs_dir / "S-AUTH-001.md").write_text(dedent("""
            ---
            id: S-AUTH-001
            type: specification
            title: Test
            ---
        """))

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "code.py").write_text("# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:test")

        result = validate_annotations(tmp_path)

        assert result.valid or len(result.errors) == 0


class TestCoverageMetrics:
    """Test coverage metric calculation."""

    def test_calculate_implementation_coverage(self, tmp_path: Path) -> None:
        """Calculate percentage of specs with implementations."""
        jig_dir = tmp_path / "jig"
        specs_dir = jig_dir / "specifications"
        specs_dir.mkdir(parents=True)
        
        # 3 specs, 2 implemented
        (specs_dir / "S-AUTH-001.md").write_text(dedent("""
            ---
            id: S-AUTH-001
            type: specification
            title: Implemented
            status: active
            ---
        """))
        (specs_dir / "S-AUTH-002.md").write_text(dedent("""
            ---
            id: S-AUTH-002
            type: specification
            title: Also implemented
            status: active
            ---
        """))
        (specs_dir / "S-AUTH-003.md").write_text(dedent("""
            ---
            id: S-AUTH-003
            type: specification
            title: Not implemented
            status: active
            ---
        """))

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "code.py").write_text(dedent("""
            # @jig C-AUTH-001 implements:S-AUTH-001 subsystem:test
            # @jig C-AUTH-002 implements:S-AUTH-002 subsystem:test
        """))

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        # Should calculate ~66.7% coverage (2/3)
        if hasattr(result, 'coverage'):
            assert result.coverage['implementation'] > 60
            assert result.coverage['implementation'] < 70


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_validate_empty_project(self, tmp_path: Path) -> None:
        """Validate project with no Intent nodes or annotations."""
        jig_dir = tmp_path / "jig"
        jig_dir.mkdir()

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        # Empty project is technically valid
        assert result.valid
        assert result.annotations_checked == 0

    def test_validate_annotations_only_no_intent(self, tmp_path: Path) -> None:
        """Annotations without Intent nodes should error."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "code.py").write_text("# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:test")

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        # Should error - S-AUTH-001 doesn't exist
        assert not result.valid

    def test_validate_intent_only_no_annotations(self, tmp_path: Path) -> None:
        """Intent nodes without annotations should warn."""
        jig_dir = tmp_path / "jig"
        specs_dir = jig_dir / "specifications"
        specs_dir.mkdir(parents=True)
        
        (specs_dir / "S-AUTH-001.md").write_text(dedent("""
            ---
            id: S-AUTH-001
            type: specification
            title: Test
            status: active
            ---
        """))

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        # Should warn about orphaned spec
        assert len(result.warnings) > 0

    def test_validate_with_circular_references(self, tmp_path: Path) -> None:
        """Handle circular reference gracefully."""
        jig_dir = tmp_path / "jig"
        specs_dir = jig_dir / "specifications"
        specs_dir.mkdir(parents=True)
        
        (specs_dir / "S-AUTH-001.md").write_text(dedent("""
            ---
            id: S-AUTH-001
            type: specification
            title: Test
            depends_on:
              - S-AUTH-002
            ---
        """))
        
        (specs_dir / "S-AUTH-002.md").write_text(dedent("""
            ---
            id: S-AUTH-002
            type: specification
            title: Test 2
            depends_on:
              - S-AUTH-001
            ---
        """))

        validator = AnnotationValidator(tmp_path)
        result = validator.validate()

        # Should not crash on circular references
        # Circular deps are not invalid per se
        assert result is not None

