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

        spec_file = spec_dir / "S-001_Test_Specification.md"
        spec_file.write_text(
            """---
id: S-001
title: Test Specification
type: specification
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
title: Test Specification
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
def test_validate_specification_missing_title():
    """Missing required field 'title' detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()

        spec_file = spec_dir / "S-001.md"
        spec_file.write_text(
            """---
id: S-001
type: specification
---

# Test Specification
"""
        )

        result = validate_specification_files(spec_dir)
        assert not result.passed
        assert len(result.errors) == 1
        assert "title" in result.errors[0].message.lower()
        assert result.errors[0].code == "MISSING_REQUIRED_FIELD"


@jig.verifies("S-018")
def test_validate_specification_duplicate_ids():
    """Duplicate spec IDs detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()

        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
title: First Specification
type: specification
---

# First
"""
        )

        (spec_dir / "S-002.md").write_text(
            """---
id: S-001
title: Second Specification
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
title: Test Specification
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

        outcome_file = outcome_dir / "O-001_Test_Outcome.md"
        outcome_file.write_text(
            """---
id: O-001
title: Test Outcome
type: outcome
specifications: []
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
title: Test Outcome
type: outcome
specifications: []
brick: B-001
---

# Test Outcome
"""
        )

        result = validate_outcome_files(outcome_dir)
        assert not result.passed
        assert any("brick" in err.message.lower() for err in result.errors)


@jig.verifies("S-019")
def test_validate_outcome_missing_title():
    """Missing required field 'title' detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        outcome_file = outcome_dir / "O-001.md"
        outcome_file.write_text(
            """---
id: O-001
type: outcome
specifications: []
---

# Test Outcome
"""
        )

        result = validate_outcome_files(outcome_dir)
        assert not result.passed
        assert len(result.errors) == 1
        assert "title" in result.errors[0].message.lower()
        assert result.errors[0].code == "MISSING_REQUIRED_FIELD"


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
title: Test Specification
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
title: Test Specification 1
type: specification
---

# Test
"""
        )
        (spec_dir / "S-002.md").write_text(
            """---
id: S-002
title: Test Specification 2
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
title: Test Specification
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
title: Test Outcome
type: outcome
specifications: []
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


# --- S-042: Outcome Completeness Validation ---


@jig.verifies("S-042")
def test_validate_outcome_completeness_valid_single_spec():
    """Outcome with one specification passes completeness validation."""
    from jig.validation.intent import validate_outcome_completeness

    with tempfile.TemporaryDirectory() as tmpdir:
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        outcome_file = outcome_dir / "O-001.md"
        outcome_file.write_text(
            """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001]
---

# Test Outcome
"""
        )

        result = validate_outcome_completeness(outcome_dir)
        assert result.passed
        assert len(result.errors) == 0
        assert result.items_checked == 1


@jig.verifies("S-042")
def test_validate_outcome_completeness_valid_multiple_specs():
    """Outcome with multiple specifications passes completeness validation."""
    from jig.validation.intent import validate_outcome_completeness

    with tempfile.TemporaryDirectory() as tmpdir:
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        outcome_file = outcome_dir / "O-001.md"
        outcome_file.write_text(
            """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001, S-002, S-003]
---

# Test Outcome
"""
        )

        result = validate_outcome_completeness(outcome_dir)
        assert result.passed
        assert len(result.errors) == 0
        assert result.items_checked == 1


@jig.verifies("S-042")
def test_validate_outcome_completeness_empty_specifications():
    """Outcome with empty specifications array fails completeness validation."""
    from jig.validation.intent import validate_outcome_completeness

    with tempfile.TemporaryDirectory() as tmpdir:
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        outcome_file = outcome_dir / "O-001.md"
        outcome_file.write_text(
            """---
id: O-001
title: Test Outcome
type: outcome
specifications: []
---

# Test Outcome
"""
        )

        result = validate_outcome_completeness(outcome_dir)
        assert not result.passed
        assert len(result.errors) == 1
        assert "O-001" in result.errors[0].message
        assert "empty" in result.errors[0].message.lower() or "completeness" in result.errors[0].message.lower()
        assert str(outcome_file) in result.errors[0].file


@jig.verifies("S-042")
def test_validate_outcome_completeness_multiple_empty():
    """Multiple outcomes with empty specifications arrays all reported."""
    from jig.validation.intent import validate_outcome_completeness

    with tempfile.TemporaryDirectory() as tmpdir:
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        # Outcome with empty specifications
        (outcome_dir / "O-001.md").write_text(
            """---
id: O-001
title: Test Outcome 1
type: outcome
specifications: []
---

# Test Outcome 1
"""
        )

        # Valid outcome
        (outcome_dir / "O-002.md").write_text(
            """---
id: O-002
title: Test Outcome 2
type: outcome
specifications: [S-001]
---

# Test Outcome 2
"""
        )

        # Another outcome with empty specifications
        (outcome_dir / "O-003.md").write_text(
            """---
id: O-003
title: Test Outcome 3
type: outcome
specifications: []
---

# Test Outcome 3
"""
        )

        result = validate_outcome_completeness(outcome_dir)
        assert not result.passed
        assert len(result.errors) == 2
        assert result.items_checked == 3
        # Check that both O-001 and O-003 are reported
        error_messages = " ".join([err.message for err in result.errors])
        assert "O-001" in error_messages
        assert "O-003" in error_messages


@jig.verifies("S-042")
def test_validate_outcome_completeness_no_outcomes():
    """Validation passes when no outcome files present (outcomes are optional)."""
    from jig.validation.intent import validate_outcome_completeness

    with tempfile.TemporaryDirectory() as tmpdir:
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        result = validate_outcome_completeness(outcome_dir)
        assert result.passed
        assert len(result.errors) == 0
        assert result.items_checked == 0


# --- S-043: Specification Coverage Validation ---


@jig.verifies("S-043")
def test_validate_specification_coverage_valid_single_outcome():
    """Specification referenced by one outcome passes coverage validation."""
    from jig.validation.intent import validate_specification_coverage

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        # Create spec
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
title: Test Specification
type: specification
---

# Test Spec
"""
        )

        # Create outcome that references the spec
        (outcome_dir / "O-001.md").write_text(
            """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001]
---

# Test Outcome
"""
        )

        result = validate_specification_coverage(spec_dir, outcome_dir)
        assert result.passed
        assert len(result.errors) == 0
        assert result.items_checked == 1


@jig.verifies("S-043")
def test_validate_specification_coverage_valid_multiple_outcomes():
    """Specification referenced by multiple outcomes passes coverage validation."""
    from jig.validation.intent import validate_specification_coverage

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        # Create spec
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
title: Test Specification
type: specification
---

# Test Spec
"""
        )

        # Create multiple outcomes that reference the spec
        (outcome_dir / "O-001.md").write_text(
            """---
id: O-001
title: Test Outcome 1
type: outcome
specifications: [S-001]
---

# Test Outcome 1
"""
        )

        (outcome_dir / "O-002.md").write_text(
            """---
id: O-002
title: Test Outcome 2
type: outcome
specifications: [S-001, S-002]
---

# Test Outcome 2
"""
        )

        result = validate_specification_coverage(spec_dir, outcome_dir)
        assert result.passed
        assert len(result.errors) == 0
        assert result.items_checked == 1


@jig.verifies("S-043")
def test_validate_specification_coverage_orphaned_spec():
    """Specification not referenced by any outcome fails coverage validation."""
    from jig.validation.intent import validate_specification_coverage

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        # Create two specs
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
title: Test Specification 1
type: specification
---

# Test Spec 1
"""
        )

        (spec_dir / "S-002.md").write_text(
            """---
id: S-002
title: Test Specification 2
type: specification
---

# Test Spec 2 (orphaned)
"""
        )

        # Create outcome that only references S-001
        (outcome_dir / "O-001.md").write_text(
            """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001]
---

# Test Outcome
"""
        )

        result = validate_specification_coverage(spec_dir, outcome_dir)
        assert not result.passed
        assert len(result.errors) == 1
        assert "S-002" in result.errors[0].message
        assert "not specified" in result.errors[0].message.lower() or "orphaned" in result.errors[0].message.lower()
        assert result.items_checked == 2


@jig.verifies("S-043")
def test_validate_specification_coverage_multiple_orphaned():
    """Multiple orphaned specifications all reported."""
    from jig.validation.intent import validate_specification_coverage

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        # Create three specs
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
title: Test Specification 1
type: specification
---

# Test Spec 1
"""
        )

        (spec_dir / "S-002.md").write_text(
            """---
id: S-002
title: Test Specification 2
type: specification
---

# Test Spec 2 (orphaned)
"""
        )

        (spec_dir / "S-003.md").write_text(
            """---
id: S-003
title: Test Specification 3
type: specification
---

# Test Spec 3 (orphaned)
"""
        )

        # Create outcome that only references S-001
        (outcome_dir / "O-001.md").write_text(
            """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001]
---

# Test Outcome
"""
        )

        result = validate_specification_coverage(spec_dir, outcome_dir)
        assert not result.passed
        assert len(result.errors) == 2
        assert result.items_checked == 3
        # Check that both S-002 and S-003 are reported
        error_messages = " ".join([err.message for err in result.errors])
        assert "S-002" in error_messages
        assert "S-003" in error_messages


@jig.verifies("S-043")
def test_validate_specification_coverage_no_outcomes():
    """All specs are orphaned when no outcomes exist."""
    from jig.validation.intent import validate_specification_coverage

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        # Create specs but no outcomes
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
title: Test Specification 1
type: specification
---

# Test Spec 1
"""
        )

        (spec_dir / "S-002.md").write_text(
            """---
id: S-002
title: Test Specification 2
type: specification
---

# Test Spec 2
"""
        )

        result = validate_specification_coverage(spec_dir, outcome_dir)
        assert not result.passed
        assert len(result.errors) == 2
        assert result.items_checked == 2
        # Both specs should be reported as orphaned
        error_messages = " ".join([err.message for err in result.errors])
        assert "S-001" in error_messages
        assert "S-002" in error_messages


@jig.verifies("S-043")
def test_validate_specification_coverage_no_specs():
    """Validation passes when no specification files present."""
    from jig.validation.intent import validate_specification_coverage

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        # No specs, but outcomes exist
        (outcome_dir / "O-001.md").write_text(
            """---
id: O-001
title: Test Outcome
type: outcome
specifications: []
---

# Test Outcome
"""
        )

        result = validate_specification_coverage(spec_dir, outcome_dir)
        assert result.passed
        assert len(result.errors) == 0
        assert result.items_checked == 0


# --- V2 Schema: Charter uses 'goals' instead of 'defines_goals' (S-073) ---


@jig.verifies("S-073")
def test_validate_charter_valid_v2_schema():
    """Charter with 'goals' field (V2 schema) passes validation."""
    from jig.validation.intent import validate_charter_file

    with tempfile.TemporaryDirectory() as tmpdir:
        charter_path = Path(tmpdir) / "Charter.md"
        charter_path.write_text(
            """---
id: Charter
type: charter
goals: [G-001, G-002]
---

# Charter

## Goals

### G-001: First Goal

Description of first goal.

### G-002: Second Goal

Description of second goal.
"""
        )

        result = validate_charter_file(charter_path)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-073")
def test_validate_charter_missing_goals():
    """Charter missing 'goals' field fails validation."""
    from jig.validation.intent import validate_charter_file

    with tempfile.TemporaryDirectory() as tmpdir:
        charter_path = Path(tmpdir) / "Charter.md"
        charter_path.write_text(
            """---
id: Charter
type: charter
---

# Charter

## Goals

### G-001: First Goal

Description.
"""
        )

        result = validate_charter_file(charter_path)
        assert not result.passed
        assert len(result.errors) >= 1
        assert any("goals" in err.message.lower() for err in result.errors)


# --- V2 Schema: Architecture uses 'goals' and 'specifications' (S-078, S-079) ---


@jig.verifies("S-078", "S-079")
def test_validate_architecture_valid_v2_schema():
    """Architecture with V2 fields (goals, specifications) passes validation."""
    from jig.validation.intent import validate_architecture_files

    with tempfile.TemporaryDirectory() as tmpdir:
        arch_dir = Path(tmpdir) / "architecture"
        arch_dir.mkdir()

        arch_file = arch_dir / "A-001_Test_Architecture.md"
        arch_file.write_text(
            """---
id: A-001
type: architecture
title: Test Architecture
goals: [G-001]
specifications: [S-001, S-002]
---

# Test Architecture

Architecture content.
"""
        )

        # V2 schema does not require status field
        result = validate_architecture_files(arch_dir, {"G-001"}, {"S-001", "S-002"})
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-078")
def test_validate_architecture_missing_goals():
    """Architecture missing 'goals' field fails validation."""
    from jig.validation.intent import validate_architecture_files

    with tempfile.TemporaryDirectory() as tmpdir:
        arch_dir = Path(tmpdir) / "architecture"
        arch_dir.mkdir()

        arch_file = arch_dir / "A-001_Test_Architecture.md"
        arch_file.write_text(
            """---
id: A-001
type: architecture
title: Test Architecture
specifications: [S-001]
---

# Test Architecture

Architecture content.
"""
        )

        result = validate_architecture_files(arch_dir, {"G-001"}, {"S-001"})
        assert not result.passed
        assert any("goals" in err.message.lower() for err in result.errors)


@jig.verifies("S-079")
def test_validate_architecture_specifications_optional():
    """Architecture without 'specifications' field passes validation (optional)."""
    from jig.validation.intent import validate_architecture_files

    with tempfile.TemporaryDirectory() as tmpdir:
        arch_dir = Path(tmpdir) / "architecture"
        arch_dir.mkdir()

        arch_file = arch_dir / "A-001_Test_Architecture.md"
        arch_file.write_text(
            """---
id: A-001
type: architecture
title: Test Architecture
goals: [G-001]
---

# Test Architecture

Architecture content.
"""
        )

        result = validate_architecture_files(arch_dir, {"G-001"}, {"S-001"})
        assert result.passed


@jig.verifies("S-079")
def test_validate_architecture_invalid_spec_reference():
    """Architecture with invalid specification reference fails validation."""
    from jig.validation.intent import validate_architecture_files

    with tempfile.TemporaryDirectory() as tmpdir:
        arch_dir = Path(tmpdir) / "architecture"
        arch_dir.mkdir()

        arch_file = arch_dir / "A-001_Test_Architecture.md"
        arch_file.write_text(
            """---
id: A-001
type: architecture
title: Test Architecture
goals: [G-001]
specifications: [S-999]
---

# Test Architecture

Architecture content.
"""
        )

        result = validate_architecture_files(arch_dir, {"G-001"}, {"S-001"})
        assert not result.passed
        assert any("S-999" in err.message for err in result.errors)


# --- S-095: Bidirectional Reference Consistency Validation ---


@jig.verifies("S-095")
def test_validate_bidirectional_consistency_outcome_spec_valid():
    """Bidirectional consistency passes when outcome->spec and spec->outcome match."""
    from jig.validation.intent import validate_bidirectional_consistency

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()
        arch_dir = Path(tmpdir) / "architecture"
        arch_dir.mkdir()

        # Create spec that references outcome
        (spec_dir / "S-001_Test_Spec.md").write_text(
            """---
id: S-001
title: Test Spec
type: specification
outcomes: [O-001]
architecture: []
---

# Test Spec
"""
        )

        # Create outcome that references spec
        (outcome_dir / "O-001_Test_Outcome.md").write_text(
            """---
id: O-001
title: Test Outcome
type: outcome
goals: [G-001]
specifications: [S-001]
---

# Test Outcome
"""
        )

        result = validate_bidirectional_consistency(spec_dir, outcome_dir, arch_dir)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-095")
def test_validate_bidirectional_consistency_missing_back_ref_from_spec():
    """Missing back-reference from spec to outcome detected."""
    from jig.validation.intent import validate_bidirectional_consistency

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()
        arch_dir = Path(tmpdir) / "architecture"
        arch_dir.mkdir()

        # Create spec that does NOT reference outcome
        (spec_dir / "S-001_Test_Spec.md").write_text(
            """---
id: S-001
title: Test Spec
type: specification
outcomes: []
architecture: []
---

# Test Spec
"""
        )

        # Create outcome that references spec
        (outcome_dir / "O-001_Test_Outcome.md").write_text(
            """---
id: O-001
title: Test Outcome
type: outcome
goals: [G-001]
specifications: [S-001]
---

# Test Outcome
"""
        )

        result = validate_bidirectional_consistency(spec_dir, outcome_dir, arch_dir)
        assert not result.passed
        assert len(result.errors) == 1
        assert "O-001" in result.errors[0].message
        assert "S-001" in result.errors[0].message


@jig.verifies("S-095")
def test_validate_bidirectional_consistency_missing_forward_ref_from_outcome():
    """Missing forward-reference from outcome to spec detected."""
    from jig.validation.intent import validate_bidirectional_consistency

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()
        arch_dir = Path(tmpdir) / "architecture"
        arch_dir.mkdir()

        # Create spec that references outcome
        (spec_dir / "S-001_Test_Spec.md").write_text(
            """---
id: S-001
title: Test Spec
type: specification
outcomes: [O-001]
architecture: []
---

# Test Spec
"""
        )

        # Create outcome that does NOT reference spec
        (outcome_dir / "O-001_Test_Outcome.md").write_text(
            """---
id: O-001
title: Test Outcome
type: outcome
goals: [G-001]
specifications: []
---

# Test Outcome
"""
        )

        result = validate_bidirectional_consistency(spec_dir, outcome_dir, arch_dir)
        assert not result.passed
        assert len(result.errors) == 1
        assert "O-001" in result.errors[0].message
        assert "S-001" in result.errors[0].message


@jig.verifies("S-095")
def test_validate_bidirectional_consistency_arch_spec_valid():
    """Bidirectional consistency passes when architecture->spec and spec->architecture match."""
    from jig.validation.intent import validate_bidirectional_consistency

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()
        arch_dir = Path(tmpdir) / "architecture"
        arch_dir.mkdir()

        # Create spec that references architecture
        (spec_dir / "S-001_Test_Spec.md").write_text(
            """---
id: S-001
title: Test Spec
type: specification
outcomes: []
architecture: [A-001]
---

# Test Spec
"""
        )

        # Create architecture that references spec
        (arch_dir / "A-001_Test_Arch.md").write_text(
            """---
id: A-001
title: Test Arch
type: architecture
goals: [G-001]
specifications: [S-001]
---

# Test Arch
"""
        )

        result = validate_bidirectional_consistency(spec_dir, outcome_dir, arch_dir)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-095")
def test_validate_bidirectional_consistency_missing_back_ref_from_spec_to_arch():
    """Missing back-reference from spec to architecture detected."""
    from jig.validation.intent import validate_bidirectional_consistency

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()
        arch_dir = Path(tmpdir) / "architecture"
        arch_dir.mkdir()

        # Create spec that does NOT reference architecture
        (spec_dir / "S-001_Test_Spec.md").write_text(
            """---
id: S-001
title: Test Spec
type: specification
outcomes: []
architecture: []
---

# Test Spec
"""
        )

        # Create architecture that references spec
        (arch_dir / "A-001_Test_Arch.md").write_text(
            """---
id: A-001
title: Test Arch
type: architecture
goals: [G-001]
specifications: [S-001]
---

# Test Arch
"""
        )

        result = validate_bidirectional_consistency(spec_dir, outcome_dir, arch_dir)
        assert not result.passed
        assert len(result.errors) == 1
        assert "A-001" in result.errors[0].message
        assert "S-001" in result.errors[0].message


@jig.verifies("S-095")
def test_validate_bidirectional_consistency_missing_forward_ref_from_arch():
    """Missing forward-reference from architecture to spec detected."""
    from jig.validation.intent import validate_bidirectional_consistency

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()
        arch_dir = Path(tmpdir) / "architecture"
        arch_dir.mkdir()

        # Create spec that references architecture
        (spec_dir / "S-001_Test_Spec.md").write_text(
            """---
id: S-001
title: Test Spec
type: specification
outcomes: []
architecture: [A-001]
---

# Test Spec
"""
        )

        # Create architecture that does NOT reference spec
        (arch_dir / "A-001_Test_Arch.md").write_text(
            """---
id: A-001
title: Test Arch
type: architecture
goals: [G-001]
specifications: []
---

# Test Arch
"""
        )

        result = validate_bidirectional_consistency(spec_dir, outcome_dir, arch_dir)
        assert not result.passed
        assert len(result.errors) == 1
        assert "A-001" in result.errors[0].message
        assert "S-001" in result.errors[0].message


@jig.verifies("S-095")
def test_validate_bidirectional_consistency_multiple_inconsistencies():
    """Multiple bidirectional inconsistencies all detected and reported."""
    from jig.validation.intent import validate_bidirectional_consistency

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()
        arch_dir = Path(tmpdir) / "architecture"
        arch_dir.mkdir()

        # Create spec with missing refs
        (spec_dir / "S-001_Test_Spec.md").write_text(
            """---
id: S-001
title: Test Spec
type: specification
outcomes: []
architecture: []
---

# Test Spec
"""
        )

        # Create another spec with missing refs
        (spec_dir / "S-002_Test_Spec_2.md").write_text(
            """---
id: S-002
title: Test Spec 2
type: specification
outcomes: []
architecture: []
---

# Test Spec 2
"""
        )

        # Outcome references both specs
        (outcome_dir / "O-001_Test_Outcome.md").write_text(
            """---
id: O-001
title: Test Outcome
type: outcome
goals: [G-001]
specifications: [S-001, S-002]
---

# Test Outcome
"""
        )

        # Architecture references S-001
        (arch_dir / "A-001_Test_Arch.md").write_text(
            """---
id: A-001
title: Test Arch
type: architecture
goals: [G-001]
specifications: [S-001]
---

# Test Arch
"""
        )

        result = validate_bidirectional_consistency(spec_dir, outcome_dir, arch_dir)
        assert not result.passed
        # Should detect 3 inconsistencies:
        # - O-001 -> S-001 but S-001 doesn't reference O-001
        # - O-001 -> S-002 but S-002 doesn't reference O-001
        # - A-001 -> S-001 but S-001 doesn't reference A-001
        assert len(result.errors) == 3


@jig.verifies("S-095")
def test_validate_bidirectional_consistency_no_specs():
    """Validation passes when no specification files exist."""
    from jig.validation.intent import validate_bidirectional_consistency

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()
        arch_dir = Path(tmpdir) / "architecture"
        arch_dir.mkdir()

        result = validate_bidirectional_consistency(spec_dir, outcome_dir, arch_dir)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("S-095")
def test_validate_bidirectional_consistency_spec_missing_outcomes_field():
    """Specs without outcomes field treated as empty array for bidirectional check."""
    from jig.validation.intent import validate_bidirectional_consistency

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()
        arch_dir = Path(tmpdir) / "architecture"
        arch_dir.mkdir()

        # Create spec WITHOUT outcomes field (V1 style)
        (spec_dir / "S-001_Test_Spec.md").write_text(
            """---
id: S-001
title: Test Spec
type: specification
---

# Test Spec
"""
        )

        # Create outcome that references spec
        (outcome_dir / "O-001_Test_Outcome.md").write_text(
            """---
id: O-001
title: Test Outcome
type: outcome
goals: [G-001]
specifications: [S-001]
---

# Test Outcome
"""
        )

        result = validate_bidirectional_consistency(spec_dir, outcome_dir, arch_dir)
        assert not result.passed
        # Should detect that O-001 references S-001 but S-001 has no outcomes field
        assert len(result.errors) == 1
        assert "O-001" in result.errors[0].message
        assert "S-001" in result.errors[0].message
