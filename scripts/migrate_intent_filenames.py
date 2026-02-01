#!/usr/bin/env python3
"""
Migrate intent document filenames to include title.

This script renames specification and outcome files from:
    {TYPE}-{NNN}.md
to:
    {TYPE}-{NNN}_{Title_Snake_Case}.md

It also updates architecture file H1 headers to remove ID prefix.

Usage:
    python scripts/migrate_intent_filenames.py --dry-run  # Preview changes
    python scripts/migrate_intent_filenames.py            # Apply changes
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml


def to_snake_case(title: str) -> str:
    """
    Convert title to snake_case for filename matching.

    Rules:
    - Replace spaces with underscores
    - Remove punctuation (except hyphens in compound words)
    - Preserve capitalization (Title_Case)
    - Preserve acronyms
    """
    result = []
    for char in title:
        if char.isalnum() or char == ' ':
            result.append(char)
        elif char == '-':
            result.append(char)
    cleaned = ''.join(result)
    return cleaned.replace(' ', '_')


def parse_frontmatter(file_path: Path) -> dict | None:
    """Parse YAML frontmatter from markdown file."""
    try:
        content = file_path.read_text()
        if not content.startswith("---"):
            return None

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        return yaml.safe_load(parts[1])
    except Exception:
        return None


def get_expected_filename(doc_id: str, title: str) -> str:
    """Generate expected filename from ID and title."""
    snake_title = to_snake_case(title)
    return f"{doc_id}_{snake_title}.md"


def rename_file(old_path: Path, new_path: Path, dry_run: bool) -> bool:
    """Rename file using git mv to preserve history."""
    if old_path == new_path:
        return True  # No rename needed

    if dry_run:
        print(f"  Would rename: {old_path.name} -> {new_path.name}")
        return True

    try:
        # Use git mv to preserve history
        result = subprocess.run(
            ["git", "mv", str(old_path), str(new_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"  Renamed: {old_path.name} -> {new_path.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ERROR renaming {old_path.name}: {e.stderr}")
        return False


def update_architecture_h1(file_path: Path, title: str, dry_run: bool) -> bool:
    """Update architecture file H1 to remove ID prefix."""
    try:
        content = file_path.read_text()

        # Pattern for H1 with ID prefix: # A-NNN: Title
        h1_pattern = re.compile(r"^(#\s+)[AOS]-\d{3}:\s*(.+)$", re.MULTILINE)

        match = h1_pattern.search(content)
        if not match:
            return True  # No ID prefix found, nothing to update

        old_h1 = match.group(0)
        new_h1 = f"# {title}"

        if old_h1 == new_h1:
            return True  # Already correct

        if dry_run:
            print(f"  Would update H1: '{old_h1}' -> '{new_h1}'")
            return True

        new_content = h1_pattern.sub(f"# {title}", content, count=1)
        file_path.write_text(new_content)
        print(f"  Updated H1: '{old_h1}' -> '{new_h1}'")
        return True

    except Exception as e:
        print(f"  ERROR updating H1 in {file_path}: {e}")
        return False


def migrate_files(directory: Path, type_prefix: str, dry_run: bool) -> tuple[int, int, list[str]]:
    """
    Migrate files in directory to include title in filename.

    Returns: (success_count, error_count, error_messages)
    """
    pattern = f"{type_prefix}-*.md"
    files = sorted(directory.glob(pattern))

    success = 0
    errors = 0
    error_msgs = []

    for file_path in files:
        frontmatter = parse_frontmatter(file_path)
        if frontmatter is None:
            error_msgs.append(f"{file_path}: Missing or invalid frontmatter")
            errors += 1
            continue

        doc_id = frontmatter.get("id")
        title = frontmatter.get("title")

        if not doc_id:
            error_msgs.append(f"{file_path}: Missing 'id' in frontmatter")
            errors += 1
            continue

        if not title:
            error_msgs.append(f"{file_path}: Missing 'title' in frontmatter")
            errors += 1
            continue

        expected_filename = get_expected_filename(doc_id, title)
        new_path = file_path.parent / expected_filename

        if rename_file(file_path, new_path, dry_run):
            success += 1
        else:
            errors += 1
            error_msgs.append(f"{file_path}: Rename failed")

    return success, errors, error_msgs


def update_architecture_h1s(directory: Path, dry_run: bool) -> tuple[int, int, list[str]]:
    """
    Update architecture file H1 headers to remove ID prefix.

    Returns: (success_count, error_count, error_messages)
    """
    if not directory.exists():
        return 0, 0, []

    files = sorted(directory.glob("A-*.md"))

    success = 0
    errors = 0
    error_msgs = []

    for file_path in files:
        frontmatter = parse_frontmatter(file_path)
        if frontmatter is None:
            error_msgs.append(f"{file_path}: Missing or invalid frontmatter")
            errors += 1
            continue

        title = frontmatter.get("title")
        if not title:
            error_msgs.append(f"{file_path}: Missing 'title' in frontmatter")
            errors += 1
            continue

        if update_architecture_h1(file_path, title, dry_run):
            success += 1
        else:
            errors += 1
            error_msgs.append(f"{file_path}: H1 update failed")

    return success, errors, error_msgs


def main():
    parser = argparse.ArgumentParser(
        description="Migrate intent document filenames to include title"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--jig-dir",
        type=Path,
        default=Path("jig"),
        help="Path to jig directory (default: jig)",
    )

    args = parser.parse_args()

    if args.dry_run:
        print("=== DRY RUN MODE (no changes will be made) ===\n")

    spec_dir = args.jig_dir / "specifications"
    outcome_dir = args.jig_dir / "outcomes"
    arch_dir = args.jig_dir / "architecture"

    total_success = 0
    total_errors = 0
    all_errors = []

    # Migrate specifications
    print("Migrating specifications...")
    s_success, s_errors, s_msgs = migrate_files(spec_dir, "S", args.dry_run)
    total_success += s_success
    total_errors += s_errors
    all_errors.extend(s_msgs)
    print(f"  Specifications: {s_success} success, {s_errors} errors\n")

    # Migrate outcomes
    print("Migrating outcomes...")
    o_success, o_errors, o_msgs = migrate_files(outcome_dir, "O", args.dry_run)
    total_success += o_success
    total_errors += o_errors
    all_errors.extend(o_msgs)
    print(f"  Outcomes: {o_success} success, {o_errors} errors\n")

    # Update architecture H1s
    print("Updating architecture H1 headers...")
    a_success, a_errors, a_msgs = update_architecture_h1s(arch_dir, args.dry_run)
    total_success += a_success
    total_errors += a_errors
    all_errors.extend(a_msgs)
    print(f"  Architectures: {a_success} success, {a_errors} errors\n")

    # Summary
    print("=" * 50)
    print(f"SUMMARY: {total_success} succeeded, {total_errors} errors")

    if all_errors:
        print("\nErrors:")
        for err in all_errors:
            print(f"  - {err}")

    if args.dry_run:
        print("\n=== DRY RUN COMPLETE (no changes made) ===")
        print("Run without --dry-run to apply changes.")

    sys.exit(0 if total_errors == 0 else 1)


if __name__ == "__main__":
    main()

