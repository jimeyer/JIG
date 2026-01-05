#!/usr/bin/env python3
"""Fix missing title and decision fields in DIG frontmatter."""

import re
from pathlib import Path


def extract_title_from_filename(filename: str) -> str:
    """Extract human-readable title from DIG filename.

    Examples:
        C005_INTENT_EXPLAINER_Intent-Artifacts-Guide.md -> Intent Artifacts Guide
        AG019_Irreducible-Core.md -> Irreducible Core
        B029_JOURNAL_outcome-updates.md -> Outcome Updates
        J001_Evergreen_Intent_Whitepaper.md -> Evergreen Intent Whitepaper
    """
    # Remove .md extension
    name = filename.replace('.md', '')

    # Remove prefix pattern (e.g., C005_, AG019_, B029_, J001_, SELA_)
    # Pattern: letter(s) + digits + underscore, or SELA_
    name = re.sub(r'^[A-Z]+\d*_', '', name)

    # Remove type suffix if present (e.g., INTENT_EXPLAINER_, JOURNAL_, SCOPE_, etc.)
    type_patterns = [
        'SCOPE_', 'JIGPLAN_', 'PLAN_', 'JOURNAL_', 'WU_',
        'PROPOSAL_', 'EXPLAINER_', 'INTENT_EXPLAINER_',
        'CONCEPT_', 'AUDIT_', 'MANIFEST_', 'RETROSPECTIVE_'
    ]
    for pattern in type_patterns:
        name = name.replace(pattern, '')

    # Replace hyphens and underscores with spaces
    name = name.replace('-', ' ').replace('_', ' ')

    # Title case
    name = name.title()

    # Clean up multiple spaces
    name = ' '.join(name.split())

    return name


def fix_frontmatter(filepath: Path) -> tuple[bool, str]:
    """Fix missing title and decision fields in a file's frontmatter.

    Returns:
        (changed, message) tuple
    """
    content = filepath.read_text()

    # Check if file has frontmatter
    if not content.startswith('---'):
        return False, "No frontmatter"

    # Find end of frontmatter
    lines = content.split('\n')
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        return False, "Unclosed frontmatter"

    # Parse frontmatter lines
    fm_lines = lines[1:end_idx]
    body_lines = lines[end_idx + 1:]

    # Check what's present
    has_title = any(line.startswith('title:') for line in fm_lines)
    has_decision = any(line.startswith('decision:') for line in fm_lines)
    status_line = next((line for line in fm_lines if line.startswith('status:')), None)

    status = None
    if status_line:
        status = status_line.split(':', 1)[1].strip()

    needs_title = not has_title
    needs_decision = not has_decision and status in ('implemented', 'abandoned')

    if not needs_title and not needs_decision:
        return False, "Already valid"

    # Build new frontmatter
    new_fm_lines = []
    title_added = False
    decision_added = False

    for line in fm_lines:
        # Add title after type line (or at start if no type)
        if line.startswith('type:') and needs_title and not title_added:
            title = extract_title_from_filename(filepath.name)
            new_fm_lines.append(f'title: "{title}"')
            title_added = True

        new_fm_lines.append(line)

        # Add decision after status line if needed
        if line.startswith('status:') and needs_decision and not decision_added:
            decision = "Superseded by newer deliberation" if status == 'implemented' else "Not pursued"
            new_fm_lines.append(f'decision: "{decision}"')
            decision_added = True

    # If title wasn't added (no type line), add at start
    if needs_title and not title_added:
        title = extract_title_from_filename(filepath.name)
        new_fm_lines.insert(0, f'title: "{title}"')

    # Reconstruct file
    new_content = '---\n' + '\n'.join(new_fm_lines) + '\n---\n' + '\n'.join(body_lines)

    filepath.write_text(new_content)

    changes = []
    if needs_title:
        changes.append("title")
    if needs_decision:
        changes.append("decision")

    return True, f"Added {', '.join(changes)}"


def main():
    dig_root = Path('/Users/jamesmeyer/Code/jig-dev/dig')

    fixed = 0
    skipped = 0
    errors = []

    for md_file in sorted(dig_root.rglob('*.md')):
        try:
            changed, msg = fix_frontmatter(md_file)
            rel_path = md_file.relative_to(dig_root)
            if changed:
                print(f"  ✓ {rel_path}: {msg}")
                fixed += 1
            else:
                skipped += 1
        except Exception as e:
            errors.append((md_file, str(e)))
            print(f"  ✗ {md_file.relative_to(dig_root)}: {e}")

    print(f"\nFixed: {fixed}")
    print(f"Skipped: {skipped}")
    if errors:
        print(f"Errors: {len(errors)}")


if __name__ == '__main__':
    main()
