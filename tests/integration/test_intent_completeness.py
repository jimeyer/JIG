"""
Integration tests for orphaned intent validation workflow.

Tests end-to-end validation scenarios for O-015 (intent completeness).
"""

import tempfile
from pathlib import Path

import jig
from jig.validation.intent import (
    validate_outcome_completeness,
    validate_specification_coverage,
)


@jig.verifies("O-015")
def test_orphaned_outcome_workflow():
    """
    End-to-end workflow: create orphaned outcome, detect error, fix, validate pass.

    Workflow:
    1. Create outcome with empty specifications array
    2. Run validation, see error
    3. Add specification to specifications array
    4. Run validation, pass
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        # Step 1: Create orphaned outcome
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

        # Step 2: Validate (should fail)
        result = validate_outcome_completeness(outcome_dir)
        assert not result.passed
        assert len(result.errors) == 1
        assert "O-001" in result.errors[0].message
        assert "empty" in result.errors[0].message.lower()

        # Step 3: Fix by adding spec
        outcome_file.write_text(
            """---
id: O-001
type: outcome
specifications: [S-001]
---

# Test Outcome
"""
        )

        # Step 4: Validate (should pass)
        result = validate_outcome_completeness(outcome_dir)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("O-015")
def test_orphaned_specification_workflow():
    """
    End-to-end workflow: create orphaned spec, detect error, fix, validate pass.

    Workflow:
    1. Create spec not referenced by any outcome
    2. Run validation, see error
    3. Create outcome that references the spec
    4. Run validation, pass
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        # Step 1: Create orphaned spec
        spec_file = spec_dir / "S-001.md"
        spec_file.write_text(
            """---
id: S-001
type: specification
---

# Test Specification
"""
        )

        # Step 2: Validate (should fail - no outcomes reference it)
        result = validate_specification_coverage(spec_dir, outcome_dir)
        assert not result.passed
        assert len(result.errors) == 1
        assert "S-001" in result.errors[0].message
        assert "not specified" in result.errors[0].message.lower() or "orphaned" in result.errors[0].message.lower()

        # Step 3: Fix by creating outcome that references the spec
        outcome_file = outcome_dir / "O-001.md"
        outcome_file.write_text(
            """---
id: O-001
type: outcome
specifications: [S-001]
---

# Test Outcome
"""
        )

        # Step 4: Validate (should pass)
        result = validate_specification_coverage(spec_dir, outcome_dir)
        assert result.passed
        assert len(result.errors) == 0


@jig.verifies("O-015")
def test_bidirectional_completeness():
    """
    Test that both validations work together to ensure bidirectional completeness.

    Scenario: Multiple outcomes and specs with various completeness issues.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        # Create specs
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
type: specification
---

# Spec 1 (referenced)
"""
        )

        (spec_dir / "S-002.md").write_text(
            """---
id: S-002
type: specification
---

# Spec 2 (orphaned)
"""
        )

        # Create outcomes
        (outcome_dir / "O-001.md").write_text(
            """---
id: O-001
type: outcome
specifications: [S-001]
---

# Outcome 1 (valid)
"""
        )

        (outcome_dir / "O-002.md").write_text(
            """---
id: O-002
type: outcome
specifications: []
---

# Outcome 2 (empty specifications)
"""
        )

        # Validate outcome completeness
        outcome_result = validate_outcome_completeness(outcome_dir)
        assert not outcome_result.passed
        assert len(outcome_result.errors) == 1
        assert "O-002" in outcome_result.errors[0].message

        # Validate specification coverage
        spec_result = validate_specification_coverage(spec_dir, outcome_dir)
        assert not spec_result.passed
        assert len(spec_result.errors) == 1
        assert "S-002" in spec_result.errors[0].message

        # Fix both issues
        (outcome_dir / "O-002.md").write_text(
            """---
id: O-002
type: outcome
specifications: [S-002]
---

# Outcome 2 (now references S-002)
"""
        )

        # Validate again - both should pass
        outcome_result = validate_outcome_completeness(outcome_dir)
        assert outcome_result.passed

        spec_result = validate_specification_coverage(spec_dir, outcome_dir)
        assert spec_result.passed


@jig.verifies("O-015")
def test_complete_valid_intent_graph():
    """
    Test that a complete, valid intent graph passes all validations.

    Scenario: Multiple outcomes and specs, all properly connected.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        # Create specs
        for i in range(1, 4):
            (spec_dir / f"S-00{i}.md").write_text(
                f"""---
id: S-00{i}
type: specification
---

# Specification {i}
"""
            )

        # Create outcomes that reference specs
        (outcome_dir / "O-001.md").write_text(
            """---
id: O-001
type: outcome
specifications: [S-001, S-002]
---

# Outcome 1
"""
        )

        (outcome_dir / "O-002.md").write_text(
            """---
id: O-002
type: outcome
specifications: [S-003]
---

# Outcome 2
"""
        )

        # Validate - all should pass
        outcome_result = validate_outcome_completeness(outcome_dir)
        assert outcome_result.passed
        assert len(outcome_result.errors) == 0

        spec_result = validate_specification_coverage(spec_dir, outcome_dir)
        assert spec_result.passed
        assert len(spec_result.errors) == 0


@jig.verifies("O-015")
def test_empty_intent_graph():
    """
    Test that empty directories pass validation (valid during project setup).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specifications"
        spec_dir.mkdir()
        outcome_dir = Path(tmpdir) / "outcomes"
        outcome_dir.mkdir()

        # No files created - both should pass
        outcome_result = validate_outcome_completeness(outcome_dir)
        assert outcome_result.passed
        assert outcome_result.items_checked == 0

        spec_result = validate_specification_coverage(spec_dir, outcome_dir)
        assert spec_result.passed
        assert spec_result.items_checked == 0
