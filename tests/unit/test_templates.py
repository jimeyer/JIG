# @jig T-TPL-001 verifies:S-JIG-002 subsystem:core
"""Unit tests for OSTC node templates."""

from datetime import date
from pathlib import Path

from jig.core.parser import parse_ostc_node  # type: ignore[import-untyped]


def substitute_template(template_content: str, node_id: str, title: str) -> str:
    """Substitute placeholders in template with test values.

    Args:
        template_content: Raw template content with placeholders
        node_id: Node ID to use (e.g., O-TEST-001)
        title: Title to use

    Returns:
        Template with all placeholders substituted
    """
    subsystem = "core"
    today = date.today().isoformat()

    return (
        template_content.replace("{id}", node_id)
        .replace("{title}", title)
        .replace("{subsystem}", subsystem)
        .replace("{date}", today)
    )


def test_outcome_template_parses(tmp_path: Path) -> None:
    """Verify outcome template parses with valid YAML frontmatter."""
    template_file = Path("templates/outcome_template.md")
    assert template_file.exists(), "outcome_template.md not found in templates/"

    # Read template
    template_content = template_file.read_text()

    # Substitute placeholders
    node_content = substitute_template(template_content, "O-TEST-001", "Test Outcome")

    # Write to temp file
    test_file = tmp_path / "O-TEST-001.md"
    test_file.write_text(node_content)

    # Parse with OSTCNode parser - should not raise
    node = parse_ostc_node(test_file)

    # Verify required fields present
    assert node.id == "O-TEST-001"
    assert node.type == "outcome"
    assert node.title == "Test Outcome"
    assert node.subsystem == "core"
    assert node.created == date.today()
    assert len(node.body) > 0


def test_specification_template_parses(tmp_path: Path) -> None:
    """Verify specification template parses with valid YAML frontmatter."""
    template_file = Path("templates/specification_template.md")
    assert template_file.exists(), "specification_template.md not found in templates/"

    # Read template
    template_content = template_file.read_text()

    # Substitute placeholders
    node_content = substitute_template(template_content, "S-TEST-001", "Test Specification")

    # Write to temp file
    test_file = tmp_path / "S-TEST-001.md"
    test_file.write_text(node_content)

    # Parse with OSTCNode parser - should not raise
    node = parse_ostc_node(test_file)

    # Verify required fields present
    assert node.id == "S-TEST-001"
    assert node.type == "specification"
    assert node.title == "Test Specification"
    assert node.subsystem == "core"
    assert node.created == date.today()
    assert len(node.body) > 0


def test_constraint_template_parses(tmp_path: Path) -> None:
    """Verify constraint template parses with valid YAML frontmatter."""
    template_file = Path("templates/constraint_template.md")
    assert template_file.exists(), "constraint_template.md not found in templates/"

    # Read template
    template_content = template_file.read_text()

    # Substitute placeholders
    node_content = substitute_template(template_content, "C-TEST-001", "Test Constraint")

    # Write to temp file
    test_file = tmp_path / "C-TEST-001.md"
    test_file.write_text(node_content)

    # Parse with OSTCNode parser - should not raise
    node = parse_ostc_node(test_file)

    # Verify required fields present
    assert node.id == "C-TEST-001"
    assert node.type == "constraint"
    assert node.title == "Test Constraint"
    assert node.subsystem == "core"
    assert node.created == date.today()
    assert len(node.body) > 0


def test_all_templates_exist() -> None:
    """Verify all three template files exist (O/S/C only; T nodes use annotations)."""
    templates_dir = Path("templates")
    assert templates_dir.is_dir(), "templates/ directory not found"

    expected_templates = [
        "outcome_template.md",
        "specification_template.md",
        "constraint_template.md",
    ]

    for template_name in expected_templates:
        template_path = templates_dir / template_name
        assert template_path.exists(), f"Template {template_name} not found"
        assert template_path.is_file(), f"{template_name} is not a file"


def test_templates_have_required_sections() -> None:
    """Verify templates include required sections and placeholders."""
    templates = {
        "templates/outcome_template.md": ["{id}", "{title}", "{subsystem}", "{date}", "## Value", "## Success Metrics", "## Acceptance Criteria"],
        "templates/specification_template.md": ["{id}", "{title}", "{subsystem}", "{date}", "## Requirements", "## Rationale", "## Acceptance Criteria"],
        "templates/constraint_template.md": ["{id}", "{title}", "{subsystem}", "{date}", "## Constraint Type", "## Rules", "## Validation"],
    }

    for template_path, required_sections in templates.items():
        content = Path(template_path).read_text()
        for section in required_sections:
            assert section in content, f"{template_path} missing required section: {section}"


def test_templates_have_yaml_frontmatter() -> None:
    """Verify all templates have valid YAML frontmatter structure."""
    templates_dir = Path("templates")
    template_files = list(templates_dir.glob("*_template.md"))

    assert len(template_files) == 3, f"Expected 3 templates (O/S/C), found {len(template_files)}"

    for template_file in template_files:
        content = template_file.read_text()

        # Should start with ---
        assert content.startswith("---\n"), f"{template_file.name} doesn't start with YAML frontmatter"

        # Should have closing ---
        assert "\n---\n" in content, f"{template_file.name} doesn't have closing YAML frontmatter"

        # Should have required frontmatter fields
        assert "id:" in content
        assert "type:" in content
        assert "title:" in content


def test_templates_consistent_formatting() -> None:
    """Verify all templates follow consistent formatting conventions."""
    templates_dir = Path("templates")
    template_files = list(templates_dir.glob("*_template.md"))

    for template_file in template_files:
        content = template_file.read_text()

        # Should have History section at end
        assert "## History" in content, f"{template_file.name} missing History section"

        # Should have Related section
        assert "## Related" in content, f"{template_file.name} missing Related section"

        # History should reference {date} placeholder
        assert "{date}:" in content, f"{template_file.name} History section doesn't use {{date}} placeholder"
