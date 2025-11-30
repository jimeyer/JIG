"""
Tests for intent validation (specifications, outcomes, decorators).
"""

import tempfile
from pathlib import Path

import jig
from jig.validation.intent import (
    validate_decorator_files,
    validate_outcome_files,
    validate_specification_files,
)
from jig.validation.models import ValidationResult


@jig.verifies("S-018")
def test_validate_specification_valid():
    """Valid specification file passes validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()

        spec_file = spec_dir / "S-001.md"
        spec_file.write_text(
            """---
id: S-001
type: specification
implements: [O-001]
---

# Test Specification

This is a test specification.
"""
        )

        result = validate_specification_files(spec_dir)
        assert result.passed
        assert len(result.errors) == 0
        assert result.items_checked == 1


@jig.verifies("S-018")
def test_validate_specification_missing_required_field():
    """Missing required field 'id' detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()

        spec_file = spec_dir / "S-001.md"
        spec_file.write_text(
            """---
type: specification
---

# Test Specification
"""
        )

        result = validate_specification_files(spec_dir)
        assert not result.passed
        assert len(result.errors) == 1
        assert "id" in result.errors[0].message.lower()
        assert result.errors[0].file == str(spec_file)


@jig.verifies("S-018")
def test_validate_specification_invalid_id_format():
    """Invalid ID format rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()

        spec_file = spec_dir / "S-001.md"
        spec_file.write_text(
            """---
id: INVALID-001
type: specification
---

# Test Specification
"""
        )

        result = validate_specification_files(spec_dir)
        assert not result.passed
        assert len(result.errors) >= 1
        # Check that at least one error is about ID format
        assert any("format" in err.message.lower() or "pattern" in err.message.lower() for err in result.errors)


@jig.verifies("S-018")
def test_validate_specification_id_filename_mismatch():
    """ID must match filename."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()

        spec_file = spec_dir / "S-001.md"
        spec_file.write_text(
            """---
id: S-002
type: specification
---

# Test Specification
"""
        )

        result = validate_specification_files(spec_dir)
        assert not result.passed
        assert len(result.errors) == 1
        assert "filename" in result.errors[0].message.lower() or "match" in result.errors[0].message.lower()


@jig.verifies("S-018")
def test_validate_specification_duplicate_ids():
    """Duplicate spec IDs detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()

        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
type: specification
---

# First
"""
        )

        (spec_dir / "S-002.md").write_text(
            """---
id: S-001
type: specification
---

# Second (duplicate ID!)
"""
        )

        result = validate_specification_files(spec_dir)
        assert not result.passed
        assert any("duplicate" in err.message.lower() or "unique" in err.message.lower() for err in result.errors)


@jig.verifies("S-018")
def test_validate_specification_excluded_fields():
    """Excluded fields detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()

        spec_file = spec_dir / "S-001.md"
        spec_file.write_text(
            """---
id: S-001
type: specification
brick: B-001
depends_on: [S-002]
content: some content
---

# Test Specification
"""
        )

        result = validate_specification_files(spec_dir)
        assert not result.passed
        # Should detect all three excluded fields
        error_messages = " ".join(err.message for err in result.errors)
        assert "brick" in error_messages.lower()
        assert "depends_on" in error_messages.lower()
        assert "content" in error_messages.lower()


@jig.verifies("S-019")
def test_validate_outcome_valid():
    """Valid outcome file passes validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        outcome_file = outcome_dir / "O-001.md"
        outcome_file.write_text(
            """---
id: O-001
type: outcome
---

# Test Outcome

This is a test outcome.
"""
        )

        result = validate_outcome_files(outcome_dir)
        assert result.passed
        assert len(result.errors) == 0
        assert result.items_checked == 1


@jig.verifies("S-019")
def test_validate_outcome_no_files():
    """Validation succeeds when no outcome files present (outcomes are optional)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        result = validate_outcome_files(outcome_dir)
        assert result.passed
        assert len(result.errors) == 0
        assert result.items_checked == 0


@jig.verifies("S-019")
def test_validate_outcome_missing_required_field():
    """Missing required field 'id' detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        outcome_file = outcome_dir / "O-001.md"
        outcome_file.write_text(
            """---
type: outcome
---

# Test Outcome
"""
        )

        result = validate_outcome_files(outcome_dir)
        assert not result.passed
        assert len(result.errors) == 1
        assert "id" in result.errors[0].message.lower()


@jig.verifies("S-019")
def test_validate_outcome_invalid_id_format():
    """Invalid ID format rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        outcome_file = outcome_dir / "O-001.md"
        outcome_file.write_text(
            """---
id: INVALID-001
type: outcome
---

# Test Outcome
"""
        )

        result = validate_outcome_files(outcome_dir)
        assert not result.passed
        assert any("format" in err.message.lower() or "pattern" in err.message.lower() for err in result.errors)


@jig.verifies("S-019")
def test_validate_outcome_excluded_field():
    """Excluded field 'brick' detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        outcome_file = outcome_dir / "O-001.md"
        outcome_file.write_text(
            """---
id: O-001
type: outcome
brick: B-001
---

# Test Outcome
"""
        )

        result = validate_outcome_files(outcome_dir)
        assert not result.passed
        assert any("brick" in err.message.lower() for err in result.errors)


@jig.verifies("S-020")
def test_validate_decorator_valid_implements():
    """Valid @jig.implements decorator passes validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = Path(tmpdir) / "src"
        src_dir.mkdir()
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()

        # Create spec
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
type: specification
---

# Test
"""
        )

        # Create code with decorator
        (src_dir / "module.py").write_text(
            '''import jig

@jig.implements("S-001")
def my_function():
    pass
'''
        )

        result = validate_decorator_files(src_dir, spec_dir)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-020")
def test_validate_decorator_invalid_spec_reference():
    """Invalid spec reference detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = Path(tmpdir) / "src"
        src_dir.mkdir()
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()

        # Create code with decorator referencing non-existent spec
        (src_dir / "module.py").write_text(
            '''import jig

@jig.implements("S-999")
def my_function():
    pass
'''
        )

        result = validate_decorator_files(src_dir, spec_dir)
        assert not result.passed
        assert len(result.errors) == 1
        assert "S-999" in result.errors[0].message
        assert "exist" in result.errors[0].message.lower() or "not found" in result.errors[0].message.lower()
        assert result.errors[0].line is not None


@jig.verifies("S-020")
def test_validate_decorator_multiple_specs():
    """Multiple specs in single decorator validated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = Path(tmpdir) / "src"
        src_dir.mkdir()
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()

        # Create specs
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
type: specification
---

# Test
"""
        )
        (spec_dir / "S-002.md").write_text(
            """---
id: S-002
type: specification
---

# Test
"""
        )

        # Create code with multiple specs
        (src_dir / "module.py").write_text(
            '''import jig

@jig.implements("S-001", "S-002")
def my_function():
    pass
'''
        )

        result = validate_decorator_files(src_dir, spec_dir)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-020")
def test_validate_decorator_verifies_spec():
    """@jig.verifies referencing spec validated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "tests"
        test_dir.mkdir()
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()

        # Create spec
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
type: specification
---

# Test
"""
        )

        # Create test with verifies decorator
        (test_dir / "test_module.py").write_text(
            '''import jig

@jig.verifies("S-001")
def test_my_function():
    pass
'''
        )

        result = validate_decorator_files(test_dir, spec_dir)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-020")
def test_validate_decorator_verifies_outcome():
    """@jig.verifies referencing outcome validated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "tests"
        test_dir.mkdir()
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        # Create outcome
        (outcome_dir / "O-001.md").write_text(
            """---
id: O-001
type: outcome
---

# Test
"""
        )

        # Create test with verifies decorator
        (test_dir / "test_module.py").write_text(
            '''import jig

@jig.verifies("O-001")
def test_my_function():
    pass
'''
        )

        result = validate_decorator_files(test_dir, spec_dir, outcome_dir)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-020")
def test_validate_decorator_invalid_syntax():
    """Decorator with non-string argument detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = Path(tmpdir) / "src"
        src_dir.mkdir()
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()

        # Create code with invalid decorator syntax
        (src_dir / "module.py").write_text(
            '''import jig

spec_id = "S-001"

@jig.implements(spec_id)  # Variable, not string literal
def my_function():
    pass
'''
        )

        result = validate_decorator_files(src_dir, spec_dir)
        assert not result.passed
        assert any("string" in err.message.lower() or "literal" in err.message.lower() for err in result.errors)
