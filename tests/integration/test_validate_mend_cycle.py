# ABOUTME: Integration tests for validate -> mend -> validate cycle.
# ABOUTME: Verifies SCOPE claim: same rule produces both error and fix.
"""
Integration tests for the validate-mend cycle.

Verifies the SCOPE claim: "A rule knows how to detect violations, describe
repairs, and execute fixes. This eliminates divergence between validate and
mend by construction."

Tests:
- validate -> mend --auto -> validate cycle converges
- validate -> mend --apply -> validate cycle converges
- Same rule produces both error and fix
- Mend actually resolves the error
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import jig
from jig.mend.engine import mend_apply, mend_auto
from jig.rules.registry import RULES
from jig.validation.engine import validate


def _create_minimal_jig_project(tmpdir: Path) -> None:
    """Create a minimal valid JIG project structure."""
    jig_dir = tmpdir / "jig"
    jig_dir.mkdir(parents=True)

    # Create Charter
    charter = jig_dir / "Charter.md"
    charter.write_text(
        """---
id: Charter
title: Test Charter
type: charter
goals: [G-001]
---

# Test Charter

A test charter for integration tests.
"""
    )

    # Create specifications directory
    spec_dir = jig_dir / "specifications"
    spec_dir.mkdir()

    # Create outcomes directory
    outcome_dir = jig_dir / "outcomes"
    outcome_dir.mkdir()

    # Create bricks.yaml (minimal)
    bricks_file = jig_dir / "bricks.yaml"
    bricks_file.write_text(
        """bricks: []
"""
    )


class TestValidateMendAutoCycle:
    """Test the validate -> mend --auto -> validate cycle."""

    @jig.verifies("S-104", "S-105", "S-107")
    def test_auto_cycle_converges_for_type_field(self) -> None:
        """Auto-fix cycle converges when fixing missing type field.

        Scenario:
        1. Create spec without type field (auto-fixable)
        2. Validate -> error with auto:true fix
        3. Mend --auto -> fixes applied
        4. Validate -> no more errors for type field
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _create_minimal_jig_project(project_root)

            # Create spec with missing type field (auto-fixable)
            spec_file = project_root / "jig" / "specifications" / "S-001_Test_Spec.md"
            spec_file.write_text(
                """---
id: S-001
title: Test Spec
outcomes: [O-001]
---

# Test Spec

Test specification.
"""
            )

            # Create an outcome that references the spec
            outcome_file = project_root / "jig" / "outcomes" / "O-001_Test_Outcome.md"
            outcome_file.write_text(
                """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001]
goals: [G-001]
---

# Test Outcome

Test outcome.
"""
            )

            # Step 1: Validate - should have error for missing type
            result1 = validate(project_root)
            errors1 = result1["errors"]

            # Find the missing type error
            type_errors = [e for e in errors1 if "type" in e["message"].lower()]
            assert len(type_errors) >= 1, "Should have error for missing type field"

            # Verify the fix is auto-fixable
            type_error = type_errors[0]
            assert type_error["fix"]["auto"], "Type field fix should be auto-fixable"
            assert type_error["fix"]["action"] == "set_field"
            assert type_error["spec"], "Error should have spec traceability (S-109)"
            assert type_error["id"], "Error should have stable ID (S-108)"

            # Step 2: Mend --auto
            mend_result = mend_auto(project_root)
            assert mend_result["applied"] >= 1, "Should have applied at least 1 fix"

            # Step 3: Validate again - type error should be resolved
            result2 = validate(project_root)
            type_errors_after = [
                e for e in result2["errors"] if "type" in e["message"].lower()
            ]
            assert (
                len(type_errors_after) == 0
            ), "Type field error should be resolved after mend"

    @jig.verifies("S-104", "S-105", "S-107")
    def test_auto_cycle_with_header_sync(self) -> None:
        """Auto-fix cycle fixes mismatched H1 header.

        Scenario:
        1. Create spec with H1 that doesn't match title
        2. Validate -> error with auto:true fix for sync_title
        3. Mend --auto -> fixes applied
        4. Validate -> H1 now matches title
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _create_minimal_jig_project(project_root)

            # Create spec with mismatched H1
            spec_file = project_root / "jig" / "specifications" / "S-001_Test_Spec.md"
            spec_file.write_text(
                """---
id: S-001
title: Test Spec
type: specification
outcomes: [O-001]
---

# Wrong Header Title

Test specification.
"""
            )

            # Create outcome
            outcome_file = project_root / "jig" / "outcomes" / "O-001_Test_Outcome.md"
            outcome_file.write_text(
                """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001]
goals: [G-001]
---

# Test Outcome

Test outcome.
"""
            )

            # Step 1: Validate - should have error for H1 mismatch
            result1 = validate(project_root)
            errors1 = result1["errors"]

            header_errors = [e for e in errors1 if "h1" in e["message"].lower()]
            assert len(header_errors) >= 1, "Should have error for H1 mismatch"

            # Verify fix is auto-fixable
            header_error = header_errors[0]
            assert header_error["fix"]["auto"], "Header sync fix should be auto-fixable"
            assert header_error["fix"]["action"] == "sync_title"

            # Step 2: Mend --auto
            mend_result = mend_auto(project_root)
            assert mend_result["applied"] >= 1, "Should have applied header fix"

            # Step 3: Validate again - header error should be resolved
            result2 = validate(project_root)
            header_errors_after = [
                e for e in result2["errors"] if "h1" in e["message"].lower()
            ]
            assert len(header_errors_after) == 0, "Header error should be resolved"

            # Verify the H1 now matches
            content = spec_file.read_text()
            assert "# Test Spec" in content, "H1 should now match title"

    @jig.verifies("S-107")
    def test_fixed_point_iteration_reports_convergence(self) -> None:
        """Mend reports convergence when fixed point is reached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _create_minimal_jig_project(project_root)

            # Create a valid spec with one auto-fixable issue
            spec_file = project_root / "jig" / "specifications" / "S-001_Test_Spec.md"
            spec_file.write_text(
                """---
id: S-001
title: Test Spec
outcomes: [O-001]
---

# Test Spec

Test specification.
"""
            )

            # Create outcome
            outcome_file = project_root / "jig" / "outcomes" / "O-001_Test_Outcome.md"
            outcome_file.write_text(
                """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001]
goals: [G-001]
---

# Test Outcome

Test outcome.
"""
            )

            # Mend with iteration
            result = mend_auto(project_root, iterate=True)

            # Should converge (no conflicting rules creating infinite loops)
            assert result["converged"], "Should reach fixed point"
            assert result["iterations"] <= 3, "Should not exceed max iterations"


class TestValidateMendApplyCycle:
    """Test the validate -> mend --apply -> validate cycle."""

    @jig.verifies("S-104", "S-106")
    def test_apply_cycle_from_validate_output(self) -> None:
        """Apply cycle works with JSON from validate output.

        Scenario:
        1. Create spec with issues
        2. Validate -j -> get JSON with fixes
        3. Save fixes to file
        4. Mend --apply fixes.json -> fixes applied
        5. Validate -> errors resolved
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _create_minimal_jig_project(project_root)

            # Create spec missing type field
            spec_file = project_root / "jig" / "specifications" / "S-001_Test_Spec.md"
            spec_file.write_text(
                """---
id: S-001
title: Test Spec
outcomes: [O-001]
---

# Test Spec

Test specification.
"""
            )

            # Create outcome
            outcome_file = project_root / "jig" / "outcomes" / "O-001_Test_Outcome.md"
            outcome_file.write_text(
                """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001]
goals: [G-001]
---

# Test Outcome

Test outcome.
"""
            )

            # Step 1: Validate to get JSON
            result1 = validate(project_root)
            assert result1["summary"]["total"] >= 1, "Should have at least 1 error"

            # Step 2: Save to file (simulate `jigy validate -j > fixes.json`)
            fixes_file = project_root / "fixes.json"
            fixes_file.write_text(json.dumps(result1, indent=2))

            # Step 3: Apply from file
            apply_result = mend_apply(project_root, fixes_file)
            assert apply_result["applied"] >= 1, "Should have applied fixes"
            assert apply_result.get("success", True), "Apply should succeed"

            # Step 4: Validate again - errors should be reduced
            result2 = validate(project_root)
            # May still have manual-only errors, but auto-fixable should be gone
            auto_fixable_after = result2["summary"]["auto_fixable"]
            # The originally auto-fixable errors should be resolved
            assert auto_fixable_after < result1["summary"]["auto_fixable"] or (
                result1["summary"]["auto_fixable"] == 0
            ), "Auto-fixable errors should be reduced"

    @jig.verifies("S-106")
    def test_apply_manual_fix_with_user_decision(self) -> None:
        """Apply mode allows applying non-auto fixes with explicit approval.

        Per S-106: "Each fix is applied regardless of auto value (explicit
        user approval)."
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _create_minimal_jig_project(project_root)

            # Create spec missing outcomes field (not auto-fixable, needs human
            # decision on which outcomes)
            spec_file = project_root / "jig" / "specifications" / "S-001_Test_Spec.md"
            spec_file.write_text(
                """---
id: S-001
title: Test Spec
type: specification
---

# Test Spec

Test specification.
"""
            )

            # Validate to get the error
            result1 = validate(project_root)
            outcome_errors = [e for e in result1["errors"] if "outcomes" in e["message"]]
            assert len(outcome_errors) >= 1, "Should have error for missing outcomes"

            # The outcomes fix is NOT auto (needs human to pick outcomes)
            outcome_error = outcome_errors[0]
            assert not outcome_error["fix"]["auto"], "Outcomes fix should require human"

            # Create a manual fix file with human-decided value
            manual_fix = {
                "errors": [
                    {
                        "id": outcome_error["id"],
                        "file": outcome_error["file"],
                        "fix": {
                            "action": "set_field",
                            "target": outcome_error["file"],
                            "params": {"field": "outcomes", "value": ["O-001"]},
                            "auto": False,  # Doesn't matter for --apply
                        },
                    }
                ]
            }
            fixes_file = project_root / "fixes.json"
            fixes_file.write_text(json.dumps(manual_fix, indent=2))

            # Apply - should work even though auto=False
            apply_result = mend_apply(project_root, fixes_file)
            assert apply_result["applied"] >= 1, "Should apply manual fix"

            # Verify outcomes field was added
            content = spec_file.read_text()
            assert "outcomes:" in content, "Outcomes field should be added"


class TestSameRuleProducesErrorAndFix:
    """Test that the same rule produces both error and fix."""

    @jig.verifies("S-104", "S-109")
    def test_rule_unity_required_field(self) -> None:
        """RequiredFieldRule produces error and matching fix.

        This is the core SCOPE claim: "A rule knows how to detect violations,
        describe repairs, and execute fixes."
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _create_minimal_jig_project(project_root)

            # Create spec missing type field
            spec_file = project_root / "jig" / "specifications" / "S-001_Test_Spec.md"
            spec_file.write_text(
                """---
id: S-001
title: Test Spec
outcomes: [O-001]
---

# Test Spec

Test specification.
"""
            )

            # Create outcome
            outcome_file = project_root / "jig" / "outcomes" / "O-001_Test_Outcome.md"
            outcome_file.write_text(
                """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001]
goals: [G-001]
---

# Test Outcome

Test outcome.
"""
            )

            # Get validation errors
            result = validate(project_root)
            errors = result["errors"]

            # Find type error
            type_errors = [e for e in errors if "type" in e["message"]]
            assert len(type_errors) >= 1

            error = type_errors[0]

            # Verify error has required structure per S-104
            assert "id" in error, "Error must have id (S-108)"
            assert "message" in error, "Error must have message"
            assert "file" in error, "Error must have file"
            assert "spec" in error, "Error must have spec (S-109)"
            assert "fix" in error, "Error must have fix (S-104)"

            fix = error["fix"]
            assert "action" in fix, "Fix must have action"
            assert "target" in fix, "Fix must have target"
            assert "params" in fix, "Fix must have params"
            assert "auto" in fix, "Fix must have auto flag"

            # The fix action should match the violation type
            assert fix["action"] == "set_field"
            assert fix["params"]["field"] == "type"
            assert fix["params"]["value"] == "specification"

            # Apply the fix
            mend_auto(project_root)

            # Verify the error is resolved
            result2 = validate(project_root)
            type_errors_after = [e for e in result2["errors"] if "type" in e["message"]]
            assert len(type_errors_after) == 0, "Rule's fix should resolve its violation"

    @jig.verifies("S-104", "S-109")
    def test_rule_unity_header_sync(self) -> None:
        """HeaderSyncRule produces error and matching fix."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _create_minimal_jig_project(project_root)

            # Create spec with wrong H1
            spec_file = project_root / "jig" / "specifications" / "S-001_Test_Spec.md"
            spec_file.write_text(
                """---
id: S-001
title: Test Spec
type: specification
outcomes: [O-001]
---

# Wrong H1

Test specification.
"""
            )

            # Create outcome
            outcome_file = project_root / "jig" / "outcomes" / "O-001_Test_Outcome.md"
            outcome_file.write_text(
                """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001]
goals: [G-001]
---

# Test Outcome

Test outcome.
"""
            )

            # Get validation errors
            result = validate(project_root)
            errors = result["errors"]

            # Find H1 error
            h1_errors = [e for e in errors if "h1" in e["message"].lower()]
            assert len(h1_errors) >= 1

            error = h1_errors[0]

            # Verify structure
            assert error["fix"]["action"] == "sync_title"
            assert error["spec"], "Should have spec traceability"

            # Apply
            mend_auto(project_root)

            # Verify resolved
            result2 = validate(project_root)
            h1_errors_after = [e for e in result2["errors"] if "h1" in e["message"].lower()]
            assert len(h1_errors_after) == 0


class TestErrorIdStability:
    """Test that error IDs are stable across runs."""

    @jig.verifies("S-108")
    def test_same_error_same_id(self) -> None:
        """Same error produces same ID across validation runs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _create_minimal_jig_project(project_root)

            # Create spec with error
            spec_file = project_root / "jig" / "specifications" / "S-001_Test_Spec.md"
            spec_file.write_text(
                """---
id: S-001
title: Test Spec
outcomes: [O-001]
---

# Test Spec

Test specification.
"""
            )

            # Create outcome
            outcome_file = project_root / "jig" / "outcomes" / "O-001_Test_Outcome.md"
            outcome_file.write_text(
                """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001]
goals: [G-001]
---

# Test Outcome

Test outcome.
"""
            )

            # Validate twice
            result1 = validate(project_root)
            result2 = validate(project_root)

            # Find same error in both
            errors1 = {e["id"]: e for e in result1["errors"]}
            errors2 = {e["id"]: e for e in result2["errors"]}

            # IDs should match
            assert set(errors1.keys()) == set(errors2.keys()), "Same errors should have same IDs"

    @jig.verifies("S-108")
    def test_different_errors_different_ids(self) -> None:
        """Different errors produce different IDs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _create_minimal_jig_project(project_root)

            # Create two specs with same error type but different context
            spec1 = project_root / "jig" / "specifications" / "S-001_Test_One.md"
            spec1.write_text(
                """---
id: S-001
title: Test One
outcomes: [O-001]
---

# Test One

Test specification one.
"""
            )

            spec2 = project_root / "jig" / "specifications" / "S-002_Test_Two.md"
            spec2.write_text(
                """---
id: S-002
title: Test Two
outcomes: [O-001]
---

# Test Two

Test specification two.
"""
            )

            # Create outcome
            outcome_file = project_root / "jig" / "outcomes" / "O-001_Test_Outcome.md"
            outcome_file.write_text(
                """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001, S-002]
goals: [G-001]
---

# Test Outcome

Test outcome.
"""
            )

            # Validate
            result = validate(project_root)
            errors = result["errors"]

            # Find type errors for each spec
            type_errors = [e for e in errors if "type" in e["message"]]
            assert len(type_errors) >= 2, "Should have 2 type errors"

            # IDs should be different
            ids = [e["id"] for e in type_errors]
            assert len(set(ids)) == len(ids), "Different errors should have unique IDs"


class TestSpecTraceability:
    """Test that errors reference the specs they enforce."""

    @jig.verifies("S-109")
    def test_errors_have_spec_references(self) -> None:
        """All validation errors include spec references."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _create_minimal_jig_project(project_root)

            # Create spec with multiple issues
            spec_file = project_root / "jig" / "specifications" / "S-001_Test_Spec.md"
            spec_file.write_text(
                """---
id: S-001
title: Test Spec
outcomes: [O-001]
---

# Wrong H1

Test specification.
"""
            )

            # Create outcome
            outcome_file = project_root / "jig" / "outcomes" / "O-001_Test_Outcome.md"
            outcome_file.write_text(
                """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001]
goals: [G-001]
---

# Test Outcome

Test outcome.
"""
            )

            # Validate
            result = validate(project_root)
            errors = result["errors"]

            # All errors should have spec field
            for error in errors:
                assert "spec" in error, f"Error missing spec: {error['message']}"
                assert error["spec"].startswith("S-"), f"Spec should be S-###: {error['spec']}"

    @jig.verifies("S-109")
    def test_rules_in_registry_have_specs(self) -> None:
        """All rules in the registry have spec references."""
        for rule in RULES:
            assert hasattr(rule, "spec"), f"Rule {rule.code} missing spec property"
            assert rule.spec, f"Rule {rule.code} has empty spec"
            assert rule.spec.startswith("S-"), f"Rule {rule.code} spec not S-###: {rule.spec}"


class TestEndToEndCycle:
    """Test complete validate-mend-validate cycles."""

    @jig.verifies("S-104", "S-105", "S-106", "S-107", "S-108", "S-109")
    def test_complete_auto_cycle(self) -> None:
        """Complete cycle: validate with errors -> mend --auto -> validate clean.

        This is the primary integration test for the SCOPE goal.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _create_minimal_jig_project(project_root)

            # Create spec with multiple auto-fixable issues
            spec_file = project_root / "jig" / "specifications" / "S-001_Test_Spec.md"
            spec_file.write_text(
                """---
id: S-001
title: Test Spec
outcomes: [O-001]
---

# Wrong Title

Test specification.
"""
            )

            # Create outcome
            outcome_file = project_root / "jig" / "outcomes" / "O-001_Test_Outcome.md"
            outcome_file.write_text(
                """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001]
goals: [G-001]
---

# Test Outcome

Test outcome.
"""
            )

            # Step 1: Validate - should have errors
            result1 = validate(project_root)
            initial_errors = result1["summary"]["total"]
            initial_auto = result1["summary"]["auto_fixable"]
            assert initial_errors >= 2, f"Should have multiple errors, got {initial_errors}"
            assert initial_auto >= 2, f"Should have auto-fixable errors, got {initial_auto}"

            # Verify all errors have required fields (S-104, S-108, S-109)
            for error in result1["errors"]:
                assert "id" in error, "S-108: Error must have id"
                assert len(error["id"]) == 12, "S-108: ID must be 12 hex chars"
                assert "spec" in error, "S-109: Error must have spec"
                assert "fix" in error, "S-104: Error must have fix"

            # Step 2: Mend --auto
            mend_result = mend_auto(project_root)
            assert mend_result["applied"] >= 2, "Should apply multiple fixes"
            assert mend_result["converged"], "Should converge (S-107)"

            # Step 3: Validate again - auto-fixable errors should be gone
            result2 = validate(project_root)
            final_auto = result2["summary"]["auto_fixable"]
            assert (
                final_auto == 0
            ), f"All auto-fixable errors should be resolved, got {final_auto}"

            # Verify the file was actually modified
            content = spec_file.read_text()
            assert "type: specification" in content, "Type field should be added"
            assert "# Test Spec" in content, "H1 should match title"

    @jig.verifies("S-104", "S-106")
    def test_apply_cycle_with_modified_fixes(self) -> None:
        """User can modify fix values before applying.

        Workflow per S-106:
        1. jigy validate -j > fixes.json
        2. Human edits fixes.json
        3. jigy mend --apply fixes.json
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _create_minimal_jig_project(project_root)

            # Create spec missing type
            spec_file = project_root / "jig" / "specifications" / "S-001_Test_Spec.md"
            spec_file.write_text(
                """---
id: S-001
title: Test Spec
outcomes: [O-001]
---

# Test Spec

Test specification.
"""
            )

            # Create outcome
            outcome_file = project_root / "jig" / "outcomes" / "O-001_Test_Outcome.md"
            outcome_file.write_text(
                """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001]
goals: [G-001]
---

# Test Outcome

Test outcome.
"""
            )

            # Step 1: Get validation output
            result1 = validate(project_root)

            # Step 2: Simulate human editing the fixes
            # (In real workflow, human would edit fixes.json)
            modified_fixes = {"errors": []}
            for error in result1["errors"]:
                if error["fix"]["action"] == "set_field":
                    modified_fixes["errors"].append(error)

            fixes_file = project_root / "fixes.json"
            fixes_file.write_text(json.dumps(modified_fixes, indent=2))

            # Step 3: Apply
            apply_result = mend_apply(project_root, fixes_file)
            assert apply_result.get("success", apply_result.get("applied", 0) > 0)

            # Verify changes applied
            content = spec_file.read_text()
            assert "type:" in content, "Type field should be added"
