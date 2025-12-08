# JIG Agent Extensions (agx) Architecture

## Overview

This document describes the architecture for authoring, building, and deploying AI agent instructions within the JIG project. The system produces platform-specific outputs (Claude Code Skills, Cursor Rules) from a single source of truth, enabling consistent agent behavior across multiple AI-assisted development environments.

## Problem Statement

JIG contains agent instructions that need to be:

1. **Authored once** — avoid maintaining parallel versions for different platforms
2. **Used across projects** — not just within jig itself, but in any project where jig is installed
3. **Compatible with multiple editors** — primarily Claude Code and Cursor, with extensibility for future platforms
4. **Distributed via pip** — install jig as a package, get agent instructions automatically
5. **Portable across machines** — work identically on different development environments without path dependencies

### Why This Is Hard

Neither Cursor nor Claude Code can natively `@` reference files inside pip-installed packages. Both expect files in specific filesystem locations:

| Platform | Location | Format |
|----------|----------|--------|
| Claude Code (personal) | `~/.claude/skills/<name>/SKILL.md` | Folder with SKILL.md + scripts |
| Claude Code (project) | `.claude/skills/<name>/SKILL.md` | Same, checked into git |
| Cursor | `.cursor/rules/<name>.mdc` | Single .mdc file with YAML frontmatter |

Symlinks fail because Cursor's indexer doesn't follow them reliably, and absolute paths break across machines with different usernames or directory structures.

## Solution: Compiled Agent Instructions

Treat agent instructions like compiled artifacts:

```
Intent (YAML) + Template (Jinja) → Platform-specific output
```

A single **intent file** describes what the agent instruction should do. **Templates** transform intents into platform-specific formats. A **build process** generates the outputs. A **CLI** deploys them to the appropriate locations.

## Directory Structure

```
jig/
├── src/                          # Python package code
│   └── jig/
│       ├── __init__.py
│       ├── cli.py                # Build and deployment commands
│       └── ...
│
└── agx/                          # Agent eXtensions
    ├── authoring/                # Development inputs (not distributed to users)
    │   ├── templates/
    │   │   ├── claude-skill.md.j2
    │   │   └── cursor-rule.mdc.j2
    │   ├── intents/
    │   │   ├── ostc-alignment.yaml
    │   │   ├── crdt-review.yaml
    │   │   └── ...
    │   └── schema.yaml           # Intent validation schema
    │
    ├── skills/                   # Generated Claude Code artifacts
    │   ├── ostc-alignment/
    │   │   ├── SKILL.md
    │   │   ├── measure.py
    │   │   └── criteria.md
    │   └── ...
    │
    ├── rules/                    # Generated Cursor artifacts
    │   ├── ostc-alignment.mdc
    │   └── ...
    │
    └── evals/                    # Evaluation test cases
        ├── ostc-alignment/
        │   ├── cases.yaml
        │   └── fixtures/
        └── ...
```

## The Intent File

The intent file is the single source of truth for each agent instruction. It captures **what** the instruction should accomplish without being tied to a specific platform's format.

### Schema

```yaml
# agx/authoring/intents/<name>.yaml

# === Required Fields ===

name: ostc-alignment                # Identifier, kebab-case
version: 0.2.0                      # Semver for tracking changes

purpose: |
  One paragraph describing what this agent instruction does and why it exists.
  This becomes the description in both platforms.

triggers:                           # When should this activate?
  - reviewing PRs for OSTC compliance
  - checking alignment scores
  - auditing traceability gaps

instructions: |                     # The actual guidance for the AI
  ## Process
  
  1. Gather the diff or files to evaluate
  2. For each change, check against criteria
  3. Calculate alignment score
  4. Report gaps with specific references
  
  ## Output Format
  
  Alignment Score: XX/100
  Gaps: [file:line] description

# === Optional Fields ===

scope:
  in:                               # What the instruction covers
    - Evaluating git commits and diffs
    - Measuring alignment against criteria
  out:                              # Explicit boundaries
    - Modifying code directly
    - Making business priority decisions

success_metrics:                    # How we know it's working
  - Identifies traceability gaps in 95% of cases
  - Provides actionable suggestions
  - Completes in under 30 seconds

examples:                           # Concrete trigger/response pairs
  - trigger: "Check if this PR maintains OSTC alignment"
    behavior: "Runs alignment check, reports score and gaps"

scripts:                            # Executable helpers (Claude Code only)
  - name: measure.py
    description: Calculates alignment score from diff
    usage: "./measure.py <base_ref> <head_ref>"

references:                         # Files to include as context
  - criteria.md
  - scoring-guide.md

# === Platform-Specific Overrides ===

claude:
  allowed_tools:                    # Tool restrictions
    - Bash
    - Read
    - Grep

cursor:
  globs: "**/*.py"                  # Auto-attach pattern
  always_apply: false
```

### Design Principles

1. **Platform-agnostic core** — The `purpose`, `triggers`, `instructions`, and `examples` work for any AI assistant
2. **Platform-specific extensions** — The `claude:` and `cursor:` sections handle format differences
3. **Explicit scope** — `scope.out` prevents scope creep and sets clear boundaries
4. **Testable** — `success_metrics` and `examples` feed directly into evals

## Templates

Templates transform intents into platform-specific formats using Jinja2.

### Claude Code Skill Template

```jinja
{# agx/authoring/templates/claude-skill.md.j2 #}
---
name: {{ name }}
description: >-
  {{ purpose | truncate(200) }}
  Use when {{ triggers | join(', ') }}.
{% if claude.allowed_tools is defined %}
allowed-tools: {{ claude.allowed_tools | join(', ') }}
{% endif %}
---

# {{ name | replace('-', ' ') | title }}

{{ instructions }}

{% if examples %}
## Examples

{% for ex in examples %}
**User:** "{{ ex.trigger }}"
**Action:** {{ ex.behavior }}

{% endfor %}
{% endif %}
{% if scripts %}
## Available Scripts

{% for script in scripts %}
- `./{{ script.name }}` — {{ script.description }}
  ```
  {{ script.usage }}
  ```
{% endfor %}
{% endif %}
{% if references %}
## Reference Files

{% for ref in references %}
Read @{{ ref }} for additional context.
{% endfor %}
{% endif %}
{% if scope.out %}
## Out of Scope

This skill does NOT:
{% for item in scope.out %}
- {{ item }}
{% endfor %}
{% endif %}
```

### Cursor Rule Template

```jinja
{# agx/authoring/templates/cursor-rule.mdc.j2 #}
---
description: >-
  {{ purpose | truncate(150) }}
  Triggers: {{ triggers | join(', ') }}.
{% if cursor.globs is defined %}
globs: {{ cursor.globs }}
{% endif %}
alwaysApply: {{ cursor.always_apply | default(false) }}
---

# {{ name | replace('-', ' ') | title }}

{{ instructions }}

{% if scope.in %}
## Scope

{% for item in scope.in %}
- {{ item }}
{% endfor %}
{% endif %}
{% if scope.out %}
## Boundaries

Do NOT:
{% for item in scope.out %}
- {{ item }}
{% endfor %}
{% endif %}
{% if examples %}
## Examples

{% for ex in examples %}
**When asked:** "{{ ex.trigger }}"
**Response:** {{ ex.behavior }}

{% endfor %}
{% endif %}
{% if references %}
## References

{% for ref in references %}
See @{{ ref }}
{% endfor %}
{% endif %}
```

## Build Process

The build process is a developer activity, not exposed via the jig CLI. Build scripts are invoked directly during development and CI.

```bash
# Build all agent instructions
python -m agx.build

# Build a specific instruction
python -m agx.build --intent ostc-alignment

# Validate without building
python -m agx.build --validate-only

# Clean generated files
python -m agx.build --clean
```

### Build Steps

1. **Validate** — Check intent against schema, ensure required fields present
2. **Render templates** — Generate SKILL.md and .mdc from intent
3. **Copy scripts** — Move any scripts referenced in intent to skills/[name]/
4. **Copy references** — Move any reference files to skills/[name]/
5. **Report** — Show what was built, flag any warnings

### Build Script Implementation

```python
# agx/build.py

"""
AGX Build Script - Developer tool for generating agent instructions.

This is NOT part of the jig CLI. It's a standalone script for developers
maintaining the agx authoring content.

Usage:
    python -m agx.build                      # Build all
    python -m agx.build --intent foo         # Build specific intent
    python -m agx.build --validate-only      # Validate without building
    python -m agx.build --clean              # Remove generated files
"""

import argparse
import shutil
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

AGX_ROOT = Path(__file__).parent


def get_intent_files(intent_name: str | None = None) -> list[Path]:
    """Get intent files to process."""
    intents_dir = AGX_ROOT / 'authoring' / 'intents'
    if intent_name:
        return [intents_dir / f'{intent_name}.yaml']
    return list(intents_dir.glob('*.yaml'))


def validate_intent(data: dict) -> list[str]:
    """Validate intent data against schema. Returns list of errors."""
    errors = []
    required = ['name', 'version', 'purpose', 'triggers', 'instructions']
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    return errors


def build_intent(intent_path: Path, env: Environment, dry_run: bool = False) -> bool:
    """Build a single intent. Returns True on success."""
    if not intent_path.exists():
        print(f"Intent not found: {intent_path}", file=sys.stderr)
        return False

    data = yaml.safe_load(intent_path.read_text())
    name = data['name']

    errors = validate_intent(data)
    if errors:
        print(f"Validation failed for {name}:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    if dry_run:
        print(f"Would build: {name}")
        return True

    skills_dir = AGX_ROOT / 'skills'
    rules_dir = AGX_ROOT / 'rules'
    intents_dir = AGX_ROOT / 'authoring' / 'intents'

    # === Claude Code Skill ===
    skill_dir = skills_dir / name
    skill_dir.mkdir(parents=True, exist_ok=True)

    claude_template = env.get_template('claude-skill.md.j2')
    (skill_dir / 'SKILL.md').write_text(claude_template.render(**data))

    # Copy scripts
    for script in data.get('scripts', []):
        src = intents_dir.parent / 'scripts' / name / script['name']
        if src.exists():
            shutil.copy(src, skill_dir / script['name'])

    # Copy references
    for ref in data.get('references', []):
        src = intents_dir.parent / 'references' / name / ref
        if src.exists():
            shutil.copy(src, skill_dir / ref)

    # === Cursor Rule ===
    rules_dir.mkdir(parents=True, exist_ok=True)
    cursor_template = env.get_template('cursor-rule.mdc.j2')
    (rules_dir / f'{name}.mdc').write_text(cursor_template.render(**data))

    print(f"Built: {name}")
    return True


def clean() -> None:
    """Remove all generated files."""
    skills_dir = AGX_ROOT / 'skills'
    rules_dir = AGX_ROOT / 'rules'

    if skills_dir.exists():
        shutil.rmtree(skills_dir)
        print(f"Removed: {skills_dir}")

    if rules_dir.exists():
        shutil.rmtree(rules_dir)
        print(f"Removed: {rules_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Build AGX agent instructions from intents.'
    )
    parser.add_argument(
        '--intent', '-i',
        help='Build specific intent only'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Validate intents without building'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be built'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Remove generated files'
    )

    args = parser.parse_args()

    if args.clean:
        clean()
        return 0

    env = Environment(
        loader=FileSystemLoader(AGX_ROOT / 'authoring' / 'templates'),
        trim_blocks=True,
        lstrip_blocks=True
    )

    intent_files = get_intent_files(args.intent)
    if not intent_files:
        print("No intent files found", file=sys.stderr)
        return 1

    success_count = 0
    for intent_path in intent_files:
        if args.validate_only:
            if intent_path.exists():
                data = yaml.safe_load(intent_path.read_text())
                errors = validate_intent(data)
                if errors:
                    print(f"Invalid: {intent_path.stem}", file=sys.stderr)
                    for err in errors:
                        print(f"  - {err}", file=sys.stderr)
                else:
                    print(f"Valid: {intent_path.stem}")
                    success_count += 1
        else:
            if build_intent(intent_path, env, dry_run=args.dry_run):
                success_count += 1

    print(f"\n{success_count}/{len(intent_files)} intents processed")
    return 0 if success_count == len(intent_files) else 1


if __name__ == '__main__':
    sys.exit(main())
```

## Deployment

Deployment of generated artifacts to editor config locations is also a developer/local activity, handled by a separate script.

### Deployment Script

```python
# agx/deploy.py

"""
AGX Deploy Script - Install generated artifacts to editor config locations.

This is NOT part of the jig CLI. It's a standalone script for developers
to install agent instructions locally for testing.

Usage:
    python -m agx.deploy claude              # Deploy to ~/.claude/skills/
    python -m agx.deploy cursor --project    # Deploy to .cursor/rules/
    python -m agx.deploy both --project      # Deploy to both (project-level)
"""

import argparse
import shutil
import sys
from pathlib import Path

AGX_ROOT = Path(__file__).parent


def deploy_claude(project: bool = False) -> bool:
    """Deploy Claude Code skills."""
    skills_src = AGX_ROOT / 'skills'

    if not skills_src.exists():
        print("No skills found. Run build first.", file=sys.stderr)
        return False

    if project:
        dest = Path.cwd() / '.claude' / 'skills' / 'jig'
    else:
        dest = Path.home() / '.claude' / 'skills' / 'jig'

    dest.mkdir(parents=True, exist_ok=True)

    for skill in skills_src.iterdir():
        if skill.is_dir():
            shutil.copytree(skill, dest / skill.name, dirs_exist_ok=True)

    print(f"Claude skills installed to {dest}")
    return True


def deploy_cursor(project: bool = False) -> bool:
    """Deploy Cursor rules."""
    rules_src = AGX_ROOT / 'rules'

    if not rules_src.exists():
        print("No rules found. Run build first.", file=sys.stderr)
        return False

    if not project:
        print("Cursor only supports project-level rules", file=sys.stderr)
        return False

    dest = Path.cwd() / '.cursor' / 'rules' / 'jig'
    dest.mkdir(parents=True, exist_ok=True)

    for rule in rules_src.glob('*.mdc'):
        shutil.copy(rule, dest / rule.name)

    print(f"Cursor rules installed to {dest}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Deploy AGX artifacts to editor config locations.'
    )
    parser.add_argument(
        'target',
        choices=['claude', 'cursor', 'both'],
        help='Target platform(s)'
    )
    parser.add_argument(
        '--project', '-p',
        action='store_true',
        help='Install to current project instead of user config'
    )

    args = parser.parse_args()
    success = True

    if args.target in ('claude', 'both'):
        success = deploy_claude(args.project) and success

    if args.target in ('cursor', 'both'):
        success = deploy_cursor(args.project) and success

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
```

### Developer Workflow

```bash
# Build the artifacts
python -m agx.build

# Deploy to current project (both editors)
cd ~/dev/my-project
python -m agx.deploy both --project

# Or deploy to user-level config (Claude Code only)
python -m agx.deploy claude

# Result:
# ~/.claude/skills/jig/ostc-alignment/SKILL.md
# ~/.claude/skills/jig/crdt-review/SKILL.md
# .cursor/rules/jig/ostc-alignment.mdc
# .cursor/rules/jig/crdt-review.mdc
```

### Package Distribution

The generated `agx/skills/` and `agx/rules/` directories are committed to the repository. End users who clone or install jig get pre-built artifacts—they don't need to run the build process.

```toml
# pyproject.toml

[tool.setuptools.packages.find]
where = ["src"]

# Note: agx/ is NOT distributed via pip to end users.
# The artifacts are for developers working on jig itself.
```

## Evaluations

The `evals/` directory contains test cases to verify agent instructions work correctly.

### Purpose

Evals answer:
- Does the instruction trigger when it should?
- Does it produce correct outputs for known inputs?
- Does it stay within scope boundaries?
- Does it meet the success metrics?

### Structure

```
agx/evals/
├── ostc-alignment/
│   ├── cases.yaml              # Test case definitions
│   └── fixtures/
│       ├── good-pr.diff        # Input fixture
│       ├── bad-pr.diff
│       └── expected/
│           ├── good-pr.md      # Expected output
│           └── bad-pr.md
└── ...
```

### Test Case Format

```yaml
# agx/evals/ostc-alignment/cases.yaml

name: ostc-alignment
description: Evaluation cases for OSTC alignment checking

cases:
  - id: well-aligned-pr
    description: A PR that follows all OSTC requirements
    trigger: "Check this PR for OSTC alignment"
    input:
      type: file
      path: fixtures/good-pr.diff
    expected:
      score_range: [90, 100]
      contains:
        - "Alignment Score"
        - "no gaps found" | "0 gaps"
      not_contains:
        - "Critical"
        - "must fix"
    tags: [happy-path]

  - id: missing-traceability
    description: A PR missing traceability links
    trigger: "Review this diff for OSTC compliance"
    input:
      type: file
      path: fixtures/bad-pr.diff
    expected:
      score_range: [30, 60]
      contains:
        - "Gap"
        - "traceability"
      pattern: "\\[.*:\\d+\\]"  # Should reference specific lines
    tags: [regression, gaps]

  - id: out-of-scope-request
    description: User asks instruction to do something outside its scope
    trigger: "Fix the OSTC compliance issues in this code"
    input:
      type: file
      path: fixtures/bad-pr.diff
    expected:
      not_contains:
        - "```python"           # Should not generate code fixes
        - "Here's the fixed"
      contains:
        - "suggest"             # Should suggest, not do
    tags: [boundaries]

  - id: trigger-recognition
    description: Verify instruction activates on expected triggers
    triggers:
      - "Check OSTC alignment"
      - "Review for compliance"
      - "What's the alignment score?"
    expected:
      activates: true
    tags: [activation]

  - id: non-trigger
    description: Verify instruction doesn't activate incorrectly  
    triggers:
      - "Write a Python function"
      - "Explain CRDT convergence"
    expected:
      activates: false
    tags: [activation, negative]
```

### Eval Dimensions

| Dimension | What It Tests | How |
|-----------|--------------|-----|
| **Activation** | Does it trigger on the right prompts? | Check if skill/rule activates |
| **Accuracy** | Is the output correct? | Compare to expected outputs |
| **Boundaries** | Does it stay in scope? | Check for out-of-scope behavior |
| **Format** | Is output structured correctly? | Regex/schema validation |
| **Performance** | Is it fast enough? | Measure response time |
| **Consistency** | Same input → similar output? | Run multiple times, compare |

### Running Evals

```bash
# Run all evals
python -m agx.eval

# Run evals for specific instruction
python -m agx.eval --intent ostc-alignment

# Run only activation tests
python -m agx.eval --tag activation

# Run with verbose output
python -m agx.eval --verbose

# Generate eval report
python -m agx.eval --report eval-results.json
```

### Eval Script Implementation

```python
# agx/eval.py

"""
AGX Eval Script - Run evaluation cases against agent instructions.

This is NOT part of the jig CLI. It's a standalone script for developers
to verify agent instructions work correctly.

Usage:
    python -m agx.eval                          # Run all evals
    python -m agx.eval --intent foo             # Run specific intent evals
    python -m agx.eval --tag activation         # Filter by tag
    python -m agx.eval --report results.json    # Output JSON report
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

AGX_ROOT = Path(__file__).parent


def run_eval_case(eval_dir: Path, case: dict) -> dict:
    """Run a single eval case. Returns result dict."""
    # TODO: Implement actual eval logic
    # This would involve invoking the AI with the trigger
    # and checking the response against expected criteria
    return {
        'id': case['id'],
        'passed': True,  # Placeholder
        'details': {}
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Run AGX evaluation cases.'
    )
    parser.add_argument(
        '--intent', '-i',
        help='Eval specific instruction only'
    )
    parser.add_argument(
        '--tag', '-t',
        action='append',
        default=[],
        help='Filter by tag (can specify multiple)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )
    parser.add_argument(
        '--report',
        type=Path,
        help='Output JSON report to file'
    )

    args = parser.parse_args()

    evals_dir = AGX_ROOT / 'evals'
    if not evals_dir.exists():
        print("No evals directory found", file=sys.stderr)
        return 1

    results = []

    for eval_dir in evals_dir.iterdir():
        if not eval_dir.is_dir():
            continue
        if args.intent and eval_dir.name != args.intent:
            continue

        cases_file = eval_dir / 'cases.yaml'
        if not cases_file.exists():
            continue

        cases = yaml.safe_load(cases_file.read_text())

        for case in cases['cases']:
            if args.tag and not any(t in case.get('tags', []) for t in args.tag):
                continue

            result = run_eval_case(eval_dir, case)
            results.append(result)

            status = "PASS" if result['passed'] else "FAIL"
            print(f"{status}: {cases['name']}/{case['id']}")

            if args.verbose and not result['passed']:
                print(f"  Details: {result.get('details', {})}")

    if args.report:
        args.report.write_text(json.dumps(results, indent=2))
        print(f"\nReport written to {args.report}")

    passed = sum(1 for r in results if r['passed'])
    print(f"\n{passed}/{len(results)} cases passed")

    return 0 if passed == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
```

### Integration with CI

```yaml
# .github/workflows/eval.yml

name: Agent Instruction Evals

on:
  push:
    paths:
      - 'agx/**'
  pull_request:
    paths:
      - 'agx/**'

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install pyyaml jinja2

      - name: Build agent instructions
        run: python -m agx.build

      - name: Run evals
        run: python -m agx.eval --report eval-results.json

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: eval-results
          path: eval-results.json
```

## Authoring Workflow

### Creating a New Agent Instruction

```bash
# 1. Create the intent file
touch agx/authoring/intents/new-instruction.yaml

# 2. Fill in the intent (use schema as guide)
vim agx/authoring/intents/new-instruction.yaml

# 3. Create any supporting scripts
mkdir -p agx/authoring/scripts/new-instruction
vim agx/authoring/scripts/new-instruction/helper.py

# 4. Create any reference files
mkdir -p agx/authoring/references/new-instruction
vim agx/authoring/references/new-instruction/guide.md

# 5. Validate
python -m agx.build --validate-only

# 6. Build
python -m agx.build --intent new-instruction

# 7. Test locally
cd ~/dev/test-project
python -m agx.deploy both --project
# Use in Cursor/Claude Code, iterate

# 8. Add eval cases
mkdir -p agx/evals/new-instruction/fixtures
vim agx/evals/new-instruction/cases.yaml

# 9. Run evals
python -m agx.eval --intent new-instruction

# 10. Commit
git add agx/
git commit -m "feat(agx): add new-instruction"
```

### Modifying an Existing Instruction

```bash
# 1. Edit the intent (source of truth)
vim agx/authoring/intents/existing-instruction.yaml

# 2. Bump version
# version: 0.2.0 → version: 0.3.0

# 3. Rebuild
python -m agx.build --intent existing-instruction

# 4. Test
python -m agx.deploy both --project

# 5. Update/add eval cases if behavior changed
vim agx/evals/existing-instruction/cases.yaml

# 6. Run evals
python -m agx.eval --intent existing-instruction

# 7. Commit
git add agx/
git commit -m "fix(agx): improve existing-instruction accuracy"
```

## Platform Comparison Reference

| Aspect | Claude Code Skills | Cursor Rules |
|--------|-------------------|--------------|
| Location | `.claude/skills/` or `~/.claude/skills/` | `.cursor/rules/` |
| Format | Folder with `SKILL.md` | Single `.mdc` file |
| Frontmatter | `name`, `description`, `allowed-tools` | `description`, `globs`, `alwaysApply` |
| Activation | Description match (AI decides) | Globs, description, or always |
| Scripts | Yes, executed via bash | No |
| References | Yes, read into context | Yes, via `@filename` |
| User-level | Yes (`~/.claude/skills/`) | No (project only) |
| Scoping | Per-folder in project | Globs or subdirectory rules |

## Future Considerations

### Additional Platforms

The intent format is designed to be extensible. Future platforms could be supported by:

1. Adding a new template: `agx/authoring/templates/windsurf-rule.j2`
2. Adding platform-specific overrides to schema: `windsurf:` section in intents
3. Updating build command to generate new format
4. Updating init command to deploy to new location

### Skill Marketplace

If Anthropic expands their skills marketplace, a separate publish script could handle submission:

```bash
python -m agx.publish --platform anthropic
```

### Shared Intent Libraries

Organizations could maintain shared intent libraries:

```yaml
# In another repo's intent file
extends: jig/ostc-alignment
version: 0.2.0

# Override specific fields
purpose: |
  Extended OSTC alignment for ACME Corp specific requirements...

# Add company-specific references
references:
  - acme-compliance-guide.md
```

## Summary

The agx system provides:

1. **Single source of truth** — Intent files capture what an instruction does, not how it's formatted
2. **Multi-platform output** — One intent produces both Claude Code Skills and Cursor Rules
3. **Clean separation** — Authoring inputs stay in development; only generated artifacts are committed
4. **Testability** — Evals verify instructions work correctly before deployment
5. **Developer-focused workflow** — Python scripts (`build.py`, `deploy.py`, `eval.py`) for developers, not end-user CLI commands

The `agx/` directory sits alongside `src/` as a first-class part of the jig project, treating agent instructions with the same rigor as code. The build/deploy/eval tooling is intentionally separate from the jig CLI since creating agent instructions is a developer activity, not an end-user feature.
