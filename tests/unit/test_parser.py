# @jig T-CORE-003 verifies:S-JIG-002 subsystem:core
"""Unit tests for OSTC node parsing."""

from datetime import date
from pathlib import Path

import pytest

from jig.core.parser import OSTCNode, parse_ostc_node


def test_parse_outcome_node(tmp_path: Path) -> None:
    """Verify parsing of Outcome node with all fields."""
    node_file = tmp_path / "O-TEST-001.md"
    content = """---
id: O-TEST-001
type: outcome
title: "Test outcome title"
subsystem: core
status: active
created: 2025-11-18
updated: 2025-11-19
---

# Outcome: Test

This is the markdown body content.

## Value

Some value description.
"""
    node_file.write_text(content)

    node = parse_ostc_node(node_file)

    assert node.id == "O-TEST-001"
    assert node.type == "outcome"
    assert node.title == "Test outcome title"
    assert node.subsystem == "core"
    assert node.status == "active"
    assert node.created == date(2025, 11, 18)
    assert node.updated == date(2025, 11, 19)
    assert "# Outcome: Test" in node.body
    assert "Some value description" in node.body


def test_parse_specification_node(tmp_path: Path) -> None:
    """Verify parsing of Specification node."""
    node_file = tmp_path / "S-TEST-001.md"
    content = """---
id: S-TEST-001
type: specification
title: "Test spec title"
subsystem: cli
---

# Specification

Requirements here.
"""
    node_file.write_text(content)

    node = parse_ostc_node(node_file)

    assert node.id == "S-TEST-001"
    assert node.type == "specification"
    assert node.title == "Test spec title"
    assert node.subsystem == "cli"
    assert node.status is None
    assert node.created is None
    assert node.updated is None
    assert "Requirements here" in node.body


# @jig T-CORE-004 verifies:S-JIG-002 subsystem:core
def test_parse_node_missing_required_field(tmp_path: Path) -> None:
    """Verify error on missing required field (id, type, title)."""
    # Missing 'title'
    node_file = tmp_path / "O-TEST-002.md"
    content = """---
id: O-TEST-002
type: outcome
---

Body content.
"""
    node_file.write_text(content)

    with pytest.raises(ValueError, match="Missing required field 'title'"):
        parse_ostc_node(node_file)


def test_parse_node_missing_id(tmp_path: Path) -> None:
    """Verify error on missing 'id' field."""
    node_file = tmp_path / "test.md"
    content = """---
type: outcome
title: "Test"
---

Body.
"""
    node_file.write_text(content)

    with pytest.raises(ValueError, match="Missing required field 'id'"):
        parse_ostc_node(node_file)


def test_parse_node_missing_type(tmp_path: Path) -> None:
    """Verify error on missing 'type' field."""
    node_file = tmp_path / "test.md"
    content = """---
id: O-TEST-003
title: "Test"
---

Body.
"""
    node_file.write_text(content)

    with pytest.raises(ValueError, match="Missing required field 'type'"):
        parse_ostc_node(node_file)


def test_parse_node_file_not_found(tmp_path: Path) -> None:
    """Verify error when file doesn't exist."""
    node_file = tmp_path / "nonexistent.md"

    with pytest.raises(FileNotFoundError, match="OSTC node file not found"):
        parse_ostc_node(node_file)


def test_parse_node_invalid_yaml(tmp_path: Path) -> None:
    """Verify helpful error on malformed YAML."""
    node_file = tmp_path / "test.md"
    content = """---
id: O-TEST-004
type: outcome
title: [invalid yaml syntax
---

Body.
"""
    node_file.write_text(content)

    with pytest.raises(ValueError, match="Failed to parse frontmatter"):
        parse_ostc_node(node_file)


def test_parse_node_minimal(tmp_path: Path) -> None:
    """Verify parsing works with only required fields."""
    node_file = tmp_path / "C-TEST-001.md"
    content = """---
id: C-TEST-001
type: constraint
title: "Minimal constraint"
---
"""
    node_file.write_text(content)

    node = parse_ostc_node(node_file)

    assert node.id == "C-TEST-001"
    assert node.type == "constraint"
    assert node.title == "Minimal constraint"
    assert node.subsystem is None
    assert node.body == ""


def test_parse_node_date_formats(tmp_path: Path) -> None:
    """Verify date parsing handles ISO format."""
    node_file = tmp_path / "O-TEST-001.md"
    content = """---
id: O-TEST-001
type: outcome
title: "Outcome with dates"
created: 2025-01-15
updated: 2025-02-20
---

Outcome body.
"""
    node_file.write_text(content)

    node = parse_ostc_node(node_file)

    assert node.created == date(2025, 1, 15)
    assert node.updated == date(2025, 2, 20)


def test_parse_node_invalid_date_format(tmp_path: Path) -> None:
    """Verify invalid date formats return None instead of crashing."""
    node_file = tmp_path / "test.md"
    content = """---
id: O-TEST-005
type: outcome
title: "Test"
created: "invalid-date-format"
---

Body.
"""
    node_file.write_text(content)

    node = parse_ostc_node(node_file)

    # Invalid date should be treated as None rather than crashing
    assert node.created is None


def test_parse_node_metadata_preserved(tmp_path: Path) -> None:
    """Verify raw metadata dictionary is preserved."""
    node_file = tmp_path / "test.md"
    content = """---
id: O-TEST-006
type: outcome
title: "Test"
custom_field: "custom value"
tags:
  - tag1
  - tag2
---

Body.
"""
    node_file.write_text(content)

    node = parse_ostc_node(node_file)

    assert node.metadata is not None
    assert node.metadata["custom_field"] == "custom value"
    assert node.metadata["tags"] == ["tag1", "tag2"]


def test_ostc_node_dataclass() -> None:
    """Verify OSTCNode dataclass can be instantiated correctly."""
    node = OSTCNode(
        id="O-TEST-007",
        type="outcome",
        title="Test title",
        subsystem="core",
        status="active",
        created=date(2025, 11, 18),
        updated=date(2025, 11, 19),
        body="Test body",
        metadata={"key": "value"},
    )

    assert node.id == "O-TEST-007"
    assert node.type == "outcome"
    assert node.title == "Test title"
    assert isinstance(node.created, date)
