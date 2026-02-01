"""
Integration tests for JIG V2 Schema Migration.

Tests verify that the V2 schema is correctly implemented across the codebase:
1. Generated intent graph uses V2 field names
2. No V1 field names in frontmatter
3. Bidirectional consistency between specs and outcomes/architecture

Related SCOPE: dig/wip/E001_SCOPE_JIG_V2_Schema.md
"""

import json
from pathlib import Path

import jig

# Project root - tests run from project directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


class TestV2SchemaFieldNames:
    """Tests that verify V2 field naming conventions in generated graphs."""

    @jig.verifies("S-095")
    def test_intent_graph_uses_v2_field_names(self):
        """
        Verify the generated intent graph uses V2 field names.

        V2 field names:
        - Charter: 'goals' (not 'defines_goals')
        - Architecture: 'goals' (not 'supports_goals'), 'specifications' (not 'constrains')
        - Outcome: 'goals' (not 'supports_goals'), 'specifications' (not 'specifies')
        """
        intent_graph_path = PROJECT_ROOT / "jig" / "generated" / "intent-graph.ndjson"
        assert intent_graph_path.exists(), f"Intent graph not found at {intent_graph_path}"

        v1_fields = {"defines_goals", "supports_goals", "specifies", "constrains"}
        v2_fields = {"goals", "specifications"}

        v1_found = set()
        v2_found = set()

        with open(intent_graph_path) as f:
            for line in f:
                if not line.strip():
                    continue
                node = json.loads(line)
                for field in v1_fields:
                    if field in node:
                        v1_found.add(field)
                for field in v2_fields:
                    if field in node:
                        v2_found.add(field)

        assert not v1_found, f"V1 field names found in intent graph: {v1_found}"
        assert v2_found, "No V2 field names found in intent graph"

    @jig.verifies("S-095")
    def test_charter_uses_goals_field(self):
        """Verify Charter frontmatter uses 'goals' not 'defines_goals'."""
        # Find charter file (supports both Charter.md and Charter_<name>.md)
        jig_dir = PROJECT_ROOT / "jig"
        charter_files = list(jig_dir.glob("Charter*.md"))
        assert charter_files, "No Charter file found in jig/"
        charter_path = charter_files[0]
        content = charter_path.read_text()

        # Check frontmatter (between first two ---)
        lines = content.split("\n")
        in_frontmatter = False
        frontmatter_lines = []

        for line in lines:
            if line.strip() == "---":
                if in_frontmatter:
                    break
                in_frontmatter = True
                continue
            if in_frontmatter:
                frontmatter_lines.append(line)

        frontmatter = "\n".join(frontmatter_lines)
        assert "goals:" in frontmatter, "Charter should have 'goals' field"
        assert "defines_goals:" not in frontmatter, "Charter should not have V1 'defines_goals' field"

    @jig.verifies("S-095")
    def test_architecture_files_use_v2_fields(self):
        """Verify Architecture files use V2 field names."""
        arch_dir = PROJECT_ROOT / "jig" / "architecture"

        for arch_file in arch_dir.glob("A-*.md"):
            content = arch_file.read_text()
            lines = content.split("\n")
            in_frontmatter = False
            frontmatter_lines = []

            for line in lines:
                if line.strip() == "---":
                    if in_frontmatter:
                        break
                    in_frontmatter = True
                    continue
                if in_frontmatter:
                    frontmatter_lines.append(line)

            frontmatter = "\n".join(frontmatter_lines)

            # V2 field names
            assert "goals:" in frontmatter, f"{arch_file.name}: should have 'goals' field"
            assert "specifications:" in frontmatter, f"{arch_file.name}: should have 'specifications' field"

            # V1 field names should not be present
            assert "supports_goals:" not in frontmatter, f"{arch_file.name}: should not have V1 'supports_goals' field"
            assert "constrains:" not in frontmatter, f"{arch_file.name}: should not have V1 'constrains' field"
            assert "status:" not in frontmatter, f"{arch_file.name}: should not have 'status' field (removed in V2)"

    @jig.verifies("S-095")
    def test_outcome_files_use_v2_fields(self):
        """Verify Outcome files use V2 field names."""
        outcome_dir = PROJECT_ROOT / "jig" / "outcomes"

        for outcome_file in outcome_dir.glob("O-*.md"):
            content = outcome_file.read_text()
            lines = content.split("\n")
            in_frontmatter = False
            frontmatter_lines = []

            for line in lines:
                if line.strip() == "---":
                    if in_frontmatter:
                        break
                    in_frontmatter = True
                    continue
                if in_frontmatter:
                    frontmatter_lines.append(line)

            frontmatter = "\n".join(frontmatter_lines)

            # V2 field names
            assert "goals:" in frontmatter, f"{outcome_file.name}: should have 'goals' field"
            assert "specifications:" in frontmatter, f"{outcome_file.name}: should have 'specifications' field"

            # V1 field names should not be present
            assert "supports_goals:" not in frontmatter, f"{outcome_file.name}: should not have V1 'supports_goals' field"
            assert "specifies:" not in frontmatter, f"{outcome_file.name}: should not have V1 'specifies' field"

    @jig.verifies("S-095")
    def test_specification_files_have_backrefs(self):
        """Verify Specification files have required back-references (V2 requirement)."""
        spec_dir = PROJECT_ROOT / "jig" / "specifications"

        for spec_file in spec_dir.glob("S-*.md"):
            content = spec_file.read_text()
            lines = content.split("\n")
            in_frontmatter = False
            frontmatter_lines = []

            for line in lines:
                if line.strip() == "---":
                    if in_frontmatter:
                        break
                    in_frontmatter = True
                    continue
                if in_frontmatter:
                    frontmatter_lines.append(line)

            frontmatter = "\n".join(frontmatter_lines)

            # V2 requires outcomes back-reference
            assert "outcomes:" in frontmatter, f"{spec_file.name}: should have 'outcomes' back-reference (V2 requirement)"


class TestV2BidirectionalConsistency:
    """Tests for bidirectional reference consistency (S-095)."""

    @jig.verifies("S-095")
    def test_outcome_spec_bidirectional_consistency(self):
        """
        Verify bidirectional consistency between outcomes and specs.

        If O-001.specifications contains S-042, then S-042.outcomes must contain O-001.
        """
        import yaml

        outcome_dir = PROJECT_ROOT / "jig" / "outcomes"
        spec_dir = PROJECT_ROOT / "jig" / "specifications"

        # Build outcome -> specs mapping
        outcome_specs = {}
        for outcome_file in outcome_dir.glob("O-*.md"):
            content = outcome_file.read_text()
            if "---" not in content:
                continue
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue
            try:
                fm = yaml.safe_load(parts[1])
                if fm and "id" in fm and "specifications" in fm:
                    outcome_specs[fm["id"]] = set(fm.get("specifications", []))
            except yaml.YAMLError:
                continue

        # Build spec -> outcomes mapping
        spec_outcomes = {}
        for spec_file in spec_dir.glob("S-*.md"):
            content = spec_file.read_text()
            if "---" not in content:
                continue
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue
            try:
                fm = yaml.safe_load(parts[1])
                if fm and "id" in fm:
                    spec_outcomes[fm["id"]] = set(fm.get("outcomes", []))
            except yaml.YAMLError:
                continue

        # Check bidirectional consistency
        inconsistencies = []

        # Check forward refs (outcome -> spec)
        for outcome_id, specs in outcome_specs.items():
            for spec_id in specs:
                if spec_id in spec_outcomes:
                    if outcome_id not in spec_outcomes[spec_id]:
                        inconsistencies.append(
                            f"{outcome_id} references {spec_id}, but {spec_id} doesn't reference {outcome_id}"
                        )

        # Check back refs (spec -> outcome)
        for spec_id, outcomes in spec_outcomes.items():
            for outcome_id in outcomes:
                if outcome_id in outcome_specs:
                    if spec_id not in outcome_specs[outcome_id]:
                        inconsistencies.append(
                            f"{spec_id} references {outcome_id}, but {outcome_id} doesn't reference {spec_id}"
                        )

        assert not inconsistencies, f"Bidirectional inconsistencies found:\n" + "\n".join(inconsistencies)

    @jig.verifies("S-095")
    def test_architecture_spec_bidirectional_consistency(self):
        """
        Verify bidirectional consistency between architecture and specs.

        If A-001.specifications contains S-072, then S-072.architecture must contain A-001.
        """
        import yaml

        arch_dir = PROJECT_ROOT / "jig" / "architecture"
        spec_dir = PROJECT_ROOT / "jig" / "specifications"

        # Build architecture -> specs mapping
        arch_specs = {}
        for arch_file in arch_dir.glob("A-*.md"):
            content = arch_file.read_text()
            if "---" not in content:
                continue
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue
            try:
                fm = yaml.safe_load(parts[1])
                if fm and "id" in fm and "specifications" in fm:
                    arch_specs[fm["id"]] = set(fm.get("specifications", []))
            except yaml.YAMLError:
                continue

        # Build spec -> architecture mapping
        spec_arch = {}
        for spec_file in spec_dir.glob("S-*.md"):
            content = spec_file.read_text()
            if "---" not in content:
                continue
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue
            try:
                fm = yaml.safe_load(parts[1])
                if fm and "id" in fm:
                    spec_arch[fm["id"]] = set(fm.get("architecture", []))
            except yaml.YAMLError:
                continue

        # Check bidirectional consistency
        inconsistencies = []

        # Check forward refs (architecture -> spec)
        for arch_id, specs in arch_specs.items():
            for spec_id in specs:
                if spec_id in spec_arch:
                    if arch_id not in spec_arch[spec_id]:
                        inconsistencies.append(
                            f"{arch_id} references {spec_id}, but {spec_id} doesn't reference {arch_id}"
                        )

        # Check back refs (spec -> architecture)
        for spec_id, archs in spec_arch.items():
            for arch_id in archs:
                if arch_id in arch_specs:
                    if spec_id not in arch_specs[arch_id]:
                        inconsistencies.append(
                            f"{spec_id} references {arch_id}, but {arch_id} doesn't reference {spec_id}"
                        )

        assert not inconsistencies, f"Bidirectional inconsistencies found:\n" + "\n".join(inconsistencies)


class TestV2GraphGeneration:
    """Tests that verify V2 schema in generated graph content."""

    @jig.verifies("S-028")
    def test_charter_node_has_goals_field(self):
        """Verify Charter node in intent graph has 'goals' field."""
        intent_graph_path = PROJECT_ROOT / "jig" / "generated" / "intent-graph.ndjson"

        charter_node = None
        with open(intent_graph_path) as f:
            for line in f:
                if not line.strip():
                    continue
                node = json.loads(line)
                if node.get("type") == "charter":
                    charter_node = node
                    break

        assert charter_node is not None, "Charter node not found in intent graph"
        assert "goals" in charter_node, "Charter node should have 'goals' field"
        assert "defines_goals" not in charter_node, "Charter node should not have V1 'defines_goals' field"
        assert isinstance(charter_node["goals"], list), "Charter 'goals' should be a list"
        assert len(charter_node["goals"]) > 0, "Charter should define at least one goal"

    @jig.verifies("S-028")
    def test_outcome_nodes_have_specifications_field(self):
        """Verify Outcome nodes in intent graph have 'specifications' field."""
        intent_graph_path = PROJECT_ROOT / "jig" / "generated" / "intent-graph.ndjson"

        outcome_nodes = []
        with open(intent_graph_path) as f:
            for line in f:
                if not line.strip():
                    continue
                node = json.loads(line)
                if node.get("type") == "outcome":
                    outcome_nodes.append(node)

        assert len(outcome_nodes) > 0, "No outcome nodes found in intent graph"

        for node in outcome_nodes:
            assert "specifications" in node, f"Outcome {node.get('id')} should have 'specifications' field"
            assert "specifies" not in node, f"Outcome {node.get('id')} should not have V1 'specifies' field"
            assert isinstance(node["specifications"], list), f"Outcome {node.get('id')} 'specifications' should be a list"

    @jig.verifies("S-028")
    def test_architecture_nodes_have_v2_fields(self):
        """Verify Architecture nodes in intent graph have V2 field names."""
        intent_graph_path = PROJECT_ROOT / "jig" / "generated" / "intent-graph.ndjson"

        arch_nodes = []
        with open(intent_graph_path) as f:
            for line in f:
                if not line.strip():
                    continue
                node = json.loads(line)
                if node.get("type") == "architecture":
                    arch_nodes.append(node)

        assert len(arch_nodes) > 0, "No architecture nodes found in intent graph"

        for node in arch_nodes:
            # V2 field names
            assert "goals" in node, f"Architecture {node.get('id')} should have 'goals' field"
            assert "specifications" in node, f"Architecture {node.get('id')} should have 'specifications' field"

            # V1 field names should not be present
            assert "supports_goals" not in node, f"Architecture {node.get('id')} should not have V1 'supports_goals' field"
            assert "constrains" not in node, f"Architecture {node.get('id')} should not have V1 'constrains' field"
            assert "status" not in node, f"Architecture {node.get('id')} should not have 'status' field (removed in V2)"

    @jig.verifies("S-028")
    def test_graph_meta_has_version(self):
        """Verify the intent graph metadata includes version 2.0."""
        intent_graph_path = PROJECT_ROOT / "jig" / "generated" / "intent-graph.ndjson"

        meta_node = None
        with open(intent_graph_path) as f:
            for line in f:
                if not line.strip():
                    continue
                node = json.loads(line)
                if "_meta" in node:
                    meta_node = node["_meta"]
                    break

        assert meta_node is not None, "Meta node not found in intent graph"
        assert "version" in meta_node, "Meta node should have 'version' field"
        assert meta_node["version"] == "2.0", f"Meta node version should be '2.0', got '{meta_node['version']}'"
