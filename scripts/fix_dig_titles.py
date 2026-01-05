#!/usr/bin/env python3
"""Fix title field to match first H1 heading in DIG documents."""

import re
from pathlib import Path


def extract_h1_title(content: str) -> str | None:
    """Extract the first H1 heading from markdown content."""
    # Skip frontmatter
    if content.startswith('---'):
        lines = content.split('\n')
        end_idx = None
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == '---':
                end_idx = i
                break
        if end_idx:
            content = '\n'.join(lines[end_idx + 1:])

    # Find first H1 heading
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def fix_title(filepath: Path) -> tuple[bool, str]:
    """Fix title field to match H1 heading.

    Returns:
        (changed, message) tuple
    """
    content = filepath.read_text()

    # Get H1 title
    h1_title = extract_h1_title(content)
    if not h1_title:
        return False, "No H1 heading found"

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
    body_lines = lines[end_idx:]  # Include closing ---

    # Find and update title line
    new_fm_lines = []
    changed = False

    for line in fm_lines:
        if line.startswith('title:'):
            # Extract current title
            current = line.split(':', 1)[1].strip().strip('"')
            if current != h1_title:
                # Escape quotes in title
                escaped_title = h1_title.replace('"', '\\"')
                new_fm_lines.append(f'title: "{escaped_title}"')
                changed = True
            else:
                new_fm_lines.append(line)
        else:
            new_fm_lines.append(line)

    if not changed:
        return False, "Title already matches"

    # Reconstruct file
    new_content = '---\n' + '\n'.join(new_fm_lines) + '\n' + '\n'.join(body_lines)

    filepath.write_text(new_content)

    return True, f'Updated to "{h1_title}"'


def main():
    dig_root = Path('/Users/jamesmeyer/Code/jig-dev/dig')

    fixed = 0
    skipped = 0
    errors = []

    for md_file in sorted(dig_root.rglob('*.md')):
        try:
            changed, msg = fix_title(md_file)
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
