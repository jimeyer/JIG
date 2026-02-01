#!/usr/bin/env python3
"""
Migrate JIG intent documents from V1 to V2 schema.

This script transforms all Charter, Architecture, Outcome, and Specification files
from V1 field names to V2 field names, following the JIGPLAN for V2 Schema Migration.

V2 Schema Changes:
| Artifact      | V1 Field        | V2 Field        |
|---------------|-----------------|-----------------|
| Charter       | defines_goals   | goals           |
| Architecture  | supports_goals  | goals           |
| Architecture  | constrains      | specifications  |
| Architecture  | status          | (removed)       |
| Outcome       | supports_goals  | goals           |
| Outcome       | specifies       | specifications  |

New V2 Fields on Specifications (back-refs computed from forward-refs):
- outcomes: Array of O-### IDs that reference this spec
- architecture: Array of A-### IDs that reference this spec

Usage:
    python scripts/migrate_v2_schema.py --dry-run  # Preview changes
    python scripts/migrate_v2_schema.py            # Apply changes

The script is idempotent - safe to run multiple times.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class MigrationChange:
    """Represents a single change to be made or that was made."""
    file_path: Path
    change_type: str  # "rename", "remove", "add"
    field_name: str
    old_value: Any = None
    new_value: Any = None

    def describe(self) -> str:
        if self.change_type == "rename":
            return f"  Rename: {self.field_name} -> {self.new_value}"
        elif self.change_type == "remove":
            return f"  Remove: {self.field_name} (was: {self.old_value})"
        elif self.change_type == "add":
            return f"  Add: {self.field_name} = {self.new_value}"
        else:
            return f"  {self.change_type}: {self.field_name}"


@dataclass
class MigrationResult:
    """Result of migrating a single file."""
    file_path: Path
    success: bool
    changes: list[MigrationChange] = field(default_factory=list)
    error: str | None = None
    skipped: bool = False
    skip_reason: str | None = None


@dataclass
class ForwardRefIndex:
    """Index of spec references from Outcomes and Architectures."""
    # spec_id -> list of O-### IDs that reference it
    outcomes_by_spec: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    # spec_id -> list of A-### IDs that reference it
    architecture_by_spec: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))


# =============================================================================
# YAML Handling (preserves content outside frontmatter)
# =============================================================================


def parse_markdown_with_frontmatter(file_path: Path) -> tuple[dict | None, str, str]:
    """
    Parse a markdown file with YAML frontmatter.

    Returns:
        (frontmatter_dict, frontmatter_raw, body)
        - frontmatter_dict: parsed YAML as dict, or None if no frontmatter
        - frontmatter_raw: the raw YAML string (for error reporting)
        - body: everything after the frontmatter
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        raise ValueError(f"Cannot read file: {e}")

    if not content.startswith("---"):
        return None, "", content

    # Find the closing ---
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, "", content

    frontmatter_raw = parts[1].strip()
    body = parts[2]

    try:
        frontmatter_dict = yaml.safe_load(frontmatter_raw)
        if frontmatter_dict is None:
            frontmatter_dict = {}
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML frontmatter: {e}")

    return frontmatter_dict, frontmatter_raw, body


def write_markdown_with_frontmatter(file_path: Path, frontmatter: dict, body: str) -> None:
    """
    Write a markdown file with YAML frontmatter.

    Preserves the body content exactly as provided.
    """
    # Use yaml.dump with specific settings for clean output
    yaml_str = yaml.dump(
        frontmatter,
        default_flow_style=None,  # Use block style for lists
        allow_unicode=True,
        sort_keys=False,  # Preserve key order
        width=1000,  # Prevent line wrapping
    )

    content = f"---\n{yaml_str}---{body}"
    file_path.write_text(content, encoding="utf-8")


# =============================================================================
# First Pass: Build Forward Reference Index
# =============================================================================


def build_forward_ref_index(
    outcome_dir: Path,
    architecture_dir: Path,
    dry_run: bool,
) -> tuple[ForwardRefIndex, list[str]]:
    """
    First pass: Read all O/A files and build index of spec references.

    Returns:
        (index, errors) - the forward ref index and any errors encountered
    """
    index = ForwardRefIndex()
    errors = []

    # Index Outcomes
    if outcome_dir.exists():
        for outcome_file in sorted(outcome_dir.glob("O-*.md")):
            try:
                frontmatter, _, _ = parse_markdown_with_frontmatter(outcome_file)
                if frontmatter is None:
                    errors.append(f"{outcome_file}: No frontmatter found")
                    continue

                outcome_id = frontmatter.get("id")
                if not outcome_id:
                    errors.append(f"{outcome_file}: Missing 'id' in frontmatter")
                    continue

                # V1 uses "specifies", V2 uses "specifications"
                # Handle both for idempotency
                specs = frontmatter.get("specifies") or frontmatter.get("specifications") or []
                if isinstance(specs, str):
                    specs = [specs]

                for spec_id in specs:
                    index.outcomes_by_spec[spec_id].append(outcome_id)

            except Exception as e:
                errors.append(f"{outcome_file}: {e}")

    # Index Architecture documents
    if architecture_dir.exists():
        for arch_file in sorted(architecture_dir.glob("A-*.md")):
            try:
                frontmatter, _, _ = parse_markdown_with_frontmatter(arch_file)
                if frontmatter is None:
                    errors.append(f"{arch_file}: No frontmatter found")
                    continue

                arch_id = frontmatter.get("id")
                if not arch_id:
                    errors.append(f"{arch_file}: Missing 'id' in frontmatter")
                    continue

                # V1 uses "constrains", V2 uses "specifications"
                # Handle both for idempotency
                specs = frontmatter.get("constrains") or frontmatter.get("specifications") or []
                if isinstance(specs, str):
                    specs = [specs]

                for spec_id in specs:
                    index.architecture_by_spec[spec_id].append(arch_id)

            except Exception as e:
                errors.append(f"{arch_file}: {e}")

    return index, errors


# =============================================================================
# Migration Functions for Each Artifact Type
# =============================================================================


def migrate_charter(file_path: Path, dry_run: bool) -> MigrationResult:
    """
    Migrate Charter from V1 to V2 schema.

    V1: defines_goals -> V2: goals
    """
    result = MigrationResult(file_path=file_path, success=True)

    try:
        frontmatter, _, body = parse_markdown_with_frontmatter(file_path)
        if frontmatter is None:
            result.success = False
            result.error = "No frontmatter found"
            return result

        modified = False

        # Rename defines_goals -> goals
        if "defines_goals" in frontmatter:
            old_value = frontmatter.pop("defines_goals")
            frontmatter["goals"] = old_value
            result.changes.append(MigrationChange(
                file_path=file_path,
                change_type="rename",
                field_name="defines_goals",
                old_value=old_value,
                new_value="goals",
            ))
            modified = True
        elif "goals" in frontmatter:
            # Already migrated
            result.skipped = True
            result.skip_reason = "Already has 'goals' field (V2 schema)"
        else:
            # Neither field exists - edge case
            result.skipped = True
            result.skip_reason = "No 'defines_goals' or 'goals' field found"

        if modified and not dry_run:
            write_markdown_with_frontmatter(file_path, frontmatter, body)

    except Exception as e:
        result.success = False
        result.error = str(e)

    return result


def migrate_architecture(file_path: Path, dry_run: bool) -> MigrationResult:
    """
    Migrate Architecture from V1 to V2 schema.

    V1: supports_goals -> V2: goals
    V1: constrains -> V2: specifications
    V1: status -> (removed in V2)
    """
    result = MigrationResult(file_path=file_path, success=True)

    try:
        frontmatter, _, body = parse_markdown_with_frontmatter(file_path)
        if frontmatter is None:
            result.success = False
            result.error = "No frontmatter found"
            return result

        modified = False

        # Rename supports_goals -> goals
        if "supports_goals" in frontmatter:
            old_value = frontmatter.pop("supports_goals")
            frontmatter["goals"] = old_value
            result.changes.append(MigrationChange(
                file_path=file_path,
                change_type="rename",
                field_name="supports_goals",
                old_value=old_value,
                new_value="goals",
            ))
            modified = True

        # Rename constrains -> specifications
        if "constrains" in frontmatter:
            old_value = frontmatter.pop("constrains")
            frontmatter["specifications"] = old_value
            result.changes.append(MigrationChange(
                file_path=file_path,
                change_type="rename",
                field_name="constrains",
                old_value=old_value,
                new_value="specifications",
            ))
            modified = True

        # Remove status field
        if "status" in frontmatter:
            old_value = frontmatter.pop("status")
            result.changes.append(MigrationChange(
                file_path=file_path,
                change_type="remove",
                field_name="status",
                old_value=old_value,
            ))
            modified = True

        if not modified:
            # Check if already V2
            if "goals" in frontmatter and "specifications" in frontmatter:
                result.skipped = True
                result.skip_reason = "Already V2 schema"
            elif "goals" in frontmatter or "specifications" in frontmatter:
                # Partially migrated - still report as already handled
                result.skipped = True
                result.skip_reason = "Already partially/fully migrated"

        if modified and not dry_run:
            write_markdown_with_frontmatter(file_path, frontmatter, body)

    except Exception as e:
        result.success = False
        result.error = str(e)

    return result


def migrate_outcome(file_path: Path, dry_run: bool) -> MigrationResult:
    """
    Migrate Outcome from V1 to V2 schema.

    V1: supports_goals -> V2: goals
    V1: specifies -> V2: specifications
    """
    result = MigrationResult(file_path=file_path, success=True)

    try:
        frontmatter, _, body = parse_markdown_with_frontmatter(file_path)
        if frontmatter is None:
            result.success = False
            result.error = "No frontmatter found"
            return result

        modified = False

        # Rename supports_goals -> goals
        if "supports_goals" in frontmatter:
            old_value = frontmatter.pop("supports_goals")
            frontmatter["goals"] = old_value
            result.changes.append(MigrationChange(
                file_path=file_path,
                change_type="rename",
                field_name="supports_goals",
                old_value=old_value,
                new_value="goals",
            ))
            modified = True

        # Rename specifies -> specifications
        if "specifies" in frontmatter:
            old_value = frontmatter.pop("specifies")
            frontmatter["specifications"] = old_value
            result.changes.append(MigrationChange(
                file_path=file_path,
                change_type="rename",
                field_name="specifies",
                old_value=old_value,
                new_value="specifications",
            ))
            modified = True

        if not modified:
            # Check if already V2
            if "goals" in frontmatter and "specifications" in frontmatter:
                result.skipped = True
                result.skip_reason = "Already V2 schema"
            elif "goals" in frontmatter or "specifications" in frontmatter:
                result.skipped = True
                result.skip_reason = "Already partially/fully migrated"

        if modified and not dry_run:
            write_markdown_with_frontmatter(file_path, frontmatter, body)

    except Exception as e:
        result.success = False
        result.error = str(e)

    return result


def migrate_specification(
    file_path: Path,
    forward_ref_index: ForwardRefIndex,
    dry_run: bool,
) -> MigrationResult:
    """
    Migrate Specification from V1 to V2 schema.

    New V2 fields (computed from forward-refs):
    - outcomes: Array of O-### IDs that reference this spec
    - architecture: Array of A-### IDs that reference this spec
    """
    result = MigrationResult(file_path=file_path, success=True)

    try:
        frontmatter, _, body = parse_markdown_with_frontmatter(file_path)
        if frontmatter is None:
            result.success = False
            result.error = "No frontmatter found"
            return result

        spec_id = frontmatter.get("id")
        if not spec_id:
            result.success = False
            result.error = "Missing 'id' in frontmatter"
            return result

        modified = False

        # Compute back-refs from forward-ref index
        outcomes = sorted(forward_ref_index.outcomes_by_spec.get(spec_id, []))
        architectures = sorted(forward_ref_index.architecture_by_spec.get(spec_id, []))

        # Add/update outcomes field
        existing_outcomes = frontmatter.get("outcomes", [])
        if existing_outcomes != outcomes:
            if outcomes:  # Only add if non-empty
                frontmatter["outcomes"] = outcomes
                result.changes.append(MigrationChange(
                    file_path=file_path,
                    change_type="add" if "outcomes" not in frontmatter or not existing_outcomes else "update",
                    field_name="outcomes",
                    old_value=existing_outcomes if existing_outcomes else None,
                    new_value=outcomes,
                ))
                modified = True
            elif "outcomes" in frontmatter:
                # Remove empty outcomes field if it exists
                del frontmatter["outcomes"]
                modified = True

        # Add/update architecture field
        existing_arch = frontmatter.get("architecture", [])
        if existing_arch != architectures:
            if architectures:  # Only add if non-empty
                frontmatter["architecture"] = architectures
                result.changes.append(MigrationChange(
                    file_path=file_path,
                    change_type="add" if "architecture" not in frontmatter or not existing_arch else "update",
                    field_name="architecture",
                    old_value=existing_arch if existing_arch else None,
                    new_value=architectures,
                ))
                modified = True
            elif "architecture" in frontmatter:
                # Remove empty architecture field if it exists
                del frontmatter["architecture"]
                modified = True

        if not modified:
            result.skipped = True
            result.skip_reason = "No changes needed (back-refs already match)"

        if modified and not dry_run:
            write_markdown_with_frontmatter(file_path, frontmatter, body)

    except Exception as e:
        result.success = False
        result.error = str(e)

    return result


# =============================================================================
# Main Migration Logic
# =============================================================================


def run_migration(
    jig_dir: Path,
    dry_run: bool,
    verbose: bool = False,
) -> tuple[list[MigrationResult], list[str]]:
    """
    Run the full V1 to V2 schema migration.

    Returns:
        (results, errors) - list of migration results and any errors
    """
    results: list[MigrationResult] = []
    errors: list[str] = []

    charter_path = jig_dir / "Charter.md"
    architecture_dir = jig_dir / "architecture"
    outcome_dir = jig_dir / "outcomes"
    spec_dir = jig_dir / "specifications"

    # =========================================================================
    # First Pass: Build forward-ref index
    # =========================================================================
    print("\n=== Phase 1: Building forward-reference index ===")
    forward_ref_index, index_errors = build_forward_ref_index(
        outcome_dir=outcome_dir,
        architecture_dir=architecture_dir,
        dry_run=dry_run,
    )
    errors.extend(index_errors)

    if index_errors:
        print(f"  Warnings during indexing: {len(index_errors)}")
        for err in index_errors:
            print(f"    - {err}")

    total_specs_with_outcomes = sum(1 for v in forward_ref_index.outcomes_by_spec.values() if v)
    total_specs_with_arch = sum(1 for v in forward_ref_index.architecture_by_spec.values() if v)
    print(f"  Specs referenced by outcomes: {total_specs_with_outcomes}")
    print(f"  Specs referenced by architecture: {total_specs_with_arch}")

    # =========================================================================
    # Second Pass: Migrate all files
    # =========================================================================
    print("\n=== Phase 2: Migrating files ===")

    # Migrate Charter
    print("\n--- Charter ---")
    if charter_path.exists():
        result = migrate_charter(charter_path, dry_run)
        results.append(result)
        if result.success:
            if result.skipped:
                print(f"  {charter_path.name}: Skipped ({result.skip_reason})")
            else:
                print(f"  {charter_path.name}: {'Would migrate' if dry_run else 'Migrated'}")
                for change in result.changes:
                    print(change.describe())
        else:
            print(f"  {charter_path.name}: ERROR - {result.error}")
            errors.append(f"{charter_path}: {result.error}")
    else:
        print(f"  Charter not found at {charter_path}")

    # Migrate Architecture documents
    print("\n--- Architecture ---")
    if architecture_dir.exists():
        arch_files = sorted(architecture_dir.glob("A-*.md"))
        for arch_file in arch_files:
            result = migrate_architecture(arch_file, dry_run)
            results.append(result)
            if result.success:
                if result.skipped:
                    if verbose:
                        print(f"  {arch_file.name}: Skipped ({result.skip_reason})")
                else:
                    print(f"  {arch_file.name}: {'Would migrate' if dry_run else 'Migrated'}")
                    for change in result.changes:
                        print(change.describe())
            else:
                print(f"  {arch_file.name}: ERROR - {result.error}")
                errors.append(f"{arch_file}: {result.error}")
        print(f"  Architecture files processed: {len(arch_files)}")
    else:
        print(f"  Architecture directory not found: {architecture_dir}")

    # Migrate Outcome documents
    print("\n--- Outcomes ---")
    if outcome_dir.exists():
        outcome_files = sorted(outcome_dir.glob("O-*.md"))
        for outcome_file in outcome_files:
            result = migrate_outcome(outcome_file, dry_run)
            results.append(result)
            if result.success:
                if result.skipped:
                    if verbose:
                        print(f"  {outcome_file.name}: Skipped ({result.skip_reason})")
                else:
                    print(f"  {outcome_file.name}: {'Would migrate' if dry_run else 'Migrated'}")
                    for change in result.changes:
                        print(change.describe())
            else:
                print(f"  {outcome_file.name}: ERROR - {result.error}")
                errors.append(f"{outcome_file}: {result.error}")
        print(f"  Outcome files processed: {len(outcome_files)}")
    else:
        print(f"  Outcomes directory not found: {outcome_dir}")

    # Migrate Specification documents
    print("\n--- Specifications ---")
    if spec_dir.exists():
        spec_files = sorted(spec_dir.glob("S-*.md"))
        specs_modified = 0
        for spec_file in spec_files:
            result = migrate_specification(spec_file, forward_ref_index, dry_run)
            results.append(result)
            if result.success:
                if result.skipped:
                    if verbose:
                        print(f"  {spec_file.name}: Skipped ({result.skip_reason})")
                else:
                    specs_modified += 1
                    print(f"  {spec_file.name}: {'Would migrate' if dry_run else 'Migrated'}")
                    for change in result.changes:
                        print(change.describe())
            else:
                print(f"  {spec_file.name}: ERROR - {result.error}")
                errors.append(f"{spec_file}: {result.error}")
        print(f"  Specification files processed: {len(spec_files)}")
        print(f"  Specifications with back-refs added: {specs_modified}")
    else:
        print(f"  Specifications directory not found: {spec_dir}")

    return results, errors


def print_summary(results: list[MigrationResult], errors: list[str], dry_run: bool) -> None:
    """Print migration summary."""
    total = len(results)
    successful = sum(1 for r in results if r.success and not r.skipped)
    skipped = sum(1 for r in results if r.skipped)
    failed = sum(1 for r in results if not r.success)

    total_changes = sum(len(r.changes) for r in results)

    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"  Total files processed: {total}")
    print(f"  Files {'would be ' if dry_run else ''}modified: {successful}")
    print(f"  Files skipped (already V2): {skipped}")
    print(f"  Files with errors: {failed}")
    print(f"  Total changes: {total_changes}")

    if errors:
        print("\nERRORS:")
        for err in errors:
            print(f"  - {err}")

    if dry_run:
        print("\n=== DRY RUN COMPLETE (no files were modified) ===")
        print("Run without --dry-run to apply changes.")
    else:
        print("\n=== MIGRATION COMPLETE ===")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate JIG intent documents from V1 to V2 schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
V2 Schema Changes:
  Charter:       defines_goals -> goals
  Architecture:  supports_goals -> goals, constrains -> specifications, status -> (removed)
  Outcome:       supports_goals -> goals, specifies -> specifications
  Specification: (new fields) outcomes, architecture (back-refs from O/A)

Examples:
  python scripts/migrate_v2_schema.py --dry-run     # Preview changes
  python scripts/migrate_v2_schema.py               # Apply migration
  python scripts/migrate_v2_schema.py --verbose     # Show all files including skipped
        """,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )
    parser.add_argument(
        "--jig-dir",
        type=Path,
        default=Path("jig"),
        help="Path to jig directory (default: jig)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show all files including skipped ones",
    )

    args = parser.parse_args()

    if not args.jig_dir.exists():
        print(f"ERROR: JIG directory not found: {args.jig_dir}")
        return 1

    if args.dry_run:
        print("=" * 60)
        print("DRY RUN MODE - No files will be modified")
        print("=" * 60)

    results, errors = run_migration(
        jig_dir=args.jig_dir,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )

    print_summary(results, errors, args.dry_run)

    # Exit with error code if any failures
    if errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
