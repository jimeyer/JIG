"""Tests for auto-rebuild integration.

Verifies that commands automatically rebuild stale graphs before execution.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import jig
from jig.cli.auto_rebuild import ensure_graphs_current
from jig.config import JigConfig, PathsConfig


def make_config(tmp_path: Path) -> JigConfig:
    """Create a test JigConfig with paths in tmp_path."""
    paths = PathsConfig(
        source=tmp_path / "src",
        tests=tmp_path / "tests",
        jig_root=tmp_path / "jig",
        specifications=tmp_path / "jig" / "specifications",
        outcomes=tmp_path / "jig" / "outcomes",
        bricks=tmp_path / "jig" / "bricks.yaml",
        generated=tmp_path / "jig" / "generated",
    )
    return JigConfig(
        paths=paths,
        project_root=tmp_path,
        config_file_path=None,
        has_config_file=False,
    )


class TestEnsureGraphsCurrent:
    """Tests for ensure_graphs_current function."""

    @jig.verifies("S-070")
    def test_does_nothing_when_skip_rebuild_true(self, tmp_path: Path):
        """No staleness check when skip_rebuild=True."""
        config = make_config(tmp_path)

        # Should not raise or call any rebuild functions
        with patch("jig.cli.auto_rebuild.is_stale") as mock_is_stale:
            ensure_graphs_current(["impl"], config, skip_rebuild=True)
            mock_is_stale.assert_not_called()

    @jig.verifies("S-070")
    def test_does_nothing_when_graphs_current(self, tmp_path: Path):
        """No rebuild when graphs are current."""
        config = make_config(tmp_path)

        with patch("jig.cli.auto_rebuild.is_stale", return_value=False) as mock_is_stale:
            ensure_graphs_current(["impl", "verify", "intent"], config)
            assert mock_is_stale.call_count == 3

    @jig.verifies("S-070")
    def test_rebuilds_stale_impl_graph(self, tmp_path: Path):
        """Rebuilds impl graph when stale."""
        config = make_config(tmp_path)

        # Create minimal source structure
        config.paths.source.mkdir(parents=True)
        config.paths.generated.mkdir(parents=True)
        (config.paths.source / "module.py").write_text("def foo(): pass")

        # Mock staleness - only impl is stale
        def mock_is_stale(graph_type, cfg):
            return graph_type == "impl"

        with patch("jig.cli.auto_rebuild.is_stale", side_effect=mock_is_stale):
            with patch("jig.cli.auto_rebuild._rebuild_impl_quietly") as mock_rebuild:
                ensure_graphs_current(["impl", "verify"], config)
                mock_rebuild.assert_called_once_with(config)

    @jig.verifies("S-070")
    def test_rebuilds_only_stale_graphs(self, tmp_path: Path):
        """Only rebuilds graphs that are stale."""
        config = make_config(tmp_path)

        # Mock staleness - verify and intent stale, impl current
        def mock_is_stale(graph_type, cfg):
            return graph_type in ["verify", "intent"]

        with patch("jig.cli.auto_rebuild.is_stale", side_effect=mock_is_stale):
            with patch("jig.cli.auto_rebuild._rebuild_impl_quietly") as mock_impl:
                with patch("jig.cli.auto_rebuild._rebuild_verify_quietly") as mock_verify:
                    with patch("jig.cli.auto_rebuild._rebuild_intent_quietly") as mock_intent:
                        ensure_graphs_current(["impl", "verify", "intent"], config)
                        mock_impl.assert_not_called()
                        mock_verify.assert_called_once()
                        mock_intent.assert_called_once()


class TestValidateAutoRebuild:
    """Tests for validate command auto-rebuild integration."""

    @jig.verifies("S-070")
    def test_validate_full_rebuilds_all_graphs(self, tmp_path: Path):
        """jigy validate rebuilds all stale graphs."""
        config = make_config(tmp_path)

        # Setup minimal structure
        config.paths.source.mkdir(parents=True)
        config.paths.tests.mkdir(parents=True)
        config.paths.specifications.mkdir(parents=True)
        config.paths.outcomes.mkdir(parents=True)
        config.paths.generated.mkdir(parents=True)
        (config.paths.bricks).write_text("bricks: []")
        (config.paths.source / "module.py").write_text("def foo(): pass")
        (config.paths.tests / "test_module.py").write_text("def test_foo(): pass")
        (config.paths.specifications / "S-001.md").write_text(
            "---\nid: S-001\ntype: specification\n---\n# Test"
        )

        with patch("jig.cli.auto_rebuild.is_stale", return_value=True):
            with patch("jig.cli.auto_rebuild._rebuild_impl_quietly") as mock_impl:
                with patch("jig.cli.auto_rebuild._rebuild_verify_quietly") as mock_verify:
                    with patch("jig.cli.auto_rebuild._rebuild_intent_quietly") as mock_intent:
                        from jig.cli.validate import validate_full_command
                        # This will fail validation but we're testing rebuild calls
                        try:
                            validate_full_command(config, "human")
                        except Exception:
                            pass

                        # All three should be called
                        mock_impl.assert_called_once()
                        mock_verify.assert_called_once()
                        mock_intent.assert_called_once()

    @jig.verifies("S-070")
    def test_validate_intent_rebuilds_intent_only(self, tmp_path: Path):
        """jigy validate intent rebuilds only intent graph."""
        config = make_config(tmp_path)

        config.paths.source.mkdir(parents=True)
        config.paths.specifications.mkdir(parents=True)
        config.paths.outcomes.mkdir(parents=True)
        config.paths.generated.mkdir(parents=True)
        (config.paths.bricks).write_text("bricks: []")
        (config.paths.source / "module.py").write_text("def foo(): pass")
        (config.paths.specifications / "S-001.md").write_text(
            "---\nid: S-001\ntype: specification\n---\n# Test"
        )

        with patch("jig.cli.auto_rebuild.is_stale", return_value=True):
            with patch("jig.cli.auto_rebuild._rebuild_impl_quietly") as mock_impl:
                with patch("jig.cli.auto_rebuild._rebuild_intent_quietly") as mock_intent:
                    from jig.cli.validate import validate_intent_command
                    try:
                        validate_intent_command(config, "human")
                    except Exception:
                        pass

                    # Only intent should be called
                    mock_impl.assert_not_called()
                    mock_intent.assert_called_once()

    @jig.verifies("S-070")
    def test_validate_bricks_rebuilds_impl_and_intent(self, tmp_path: Path):
        """jigy validate bricks rebuilds impl + intent graphs."""
        config = make_config(tmp_path)

        config.paths.source.mkdir(parents=True)
        config.paths.specifications.mkdir(parents=True)
        config.paths.generated.mkdir(parents=True)
        (config.paths.bricks).write_text("bricks: []")

        with patch("jig.cli.auto_rebuild.is_stale", return_value=True):
            with patch("jig.cli.auto_rebuild._rebuild_impl_quietly") as mock_impl:
                with patch("jig.cli.auto_rebuild._rebuild_verify_quietly") as mock_verify:
                    with patch("jig.cli.auto_rebuild._rebuild_intent_quietly") as mock_intent:
                        from jig.cli.validate import validate_bricks_command
                        try:
                            validate_bricks_command(config, "human")
                        except Exception:
                            pass

                        # impl and intent, not verify
                        mock_impl.assert_called_once()
                        mock_verify.assert_not_called()
                        mock_intent.assert_called_once()


class TestShowAutoRebuild:
    """Tests for show command auto-rebuild integration."""

    @jig.verifies("S-070")
    def test_show_overview_rebuilds_all(self, tmp_path: Path):
        """jigy show rebuilds all stale graphs."""
        config = make_config(tmp_path)
        (config.paths.bricks).parent.mkdir(parents=True, exist_ok=True)

        with patch("jig.cli.auto_rebuild.is_stale", return_value=True):
            with patch("jig.cli.auto_rebuild._rebuild_impl_quietly") as mock_impl:
                with patch("jig.cli.auto_rebuild._rebuild_verify_quietly") as mock_verify:
                    with patch("jig.cli.auto_rebuild._rebuild_intent_quietly") as mock_intent:
                        from jig.cli.show import show_overview_command
                        show_overview_command(config)

                        mock_impl.assert_called_once()
                        mock_verify.assert_called_once()
                        mock_intent.assert_called_once()

    @jig.verifies("S-070")
    def test_show_layers_rebuilds_impl_intent(self, tmp_path: Path):
        """jigy show layers rebuilds impl + intent graphs."""
        config = make_config(tmp_path)
        (config.paths.bricks).parent.mkdir(parents=True, exist_ok=True)

        with patch("jig.cli.auto_rebuild.is_stale", return_value=True):
            with patch("jig.cli.auto_rebuild._rebuild_impl_quietly") as mock_impl:
                with patch("jig.cli.auto_rebuild._rebuild_verify_quietly") as mock_verify:
                    with patch("jig.cli.auto_rebuild._rebuild_intent_quietly") as mock_intent:
                        from jig.cli.show import show_layers_command
                        show_layers_command(config)

                        mock_impl.assert_called_once()
                        mock_verify.assert_not_called()
                        mock_intent.assert_called_once()


class TestAuditAutoRebuild:
    """Tests for audit command auto-rebuild integration."""

    @jig.verifies("S-070")
    def test_audit_coverage_rebuilds_impl_verify(self, tmp_path: Path):
        """jigy audit coverage rebuilds impl + verify graphs."""
        config = make_config(tmp_path)
        config.paths.generated.mkdir(parents=True)

        with patch("jig.cli.auto_rebuild.is_stale", return_value=True):
            with patch("jig.cli.auto_rebuild._rebuild_impl_quietly") as mock_impl:
                with patch("jig.cli.auto_rebuild._rebuild_verify_quietly") as mock_verify:
                    with patch("jig.cli.auto_rebuild._rebuild_intent_quietly") as mock_intent:
                        from jig.cli.audit import coverage_command
                        # Will fail because graphs don't exist, but we test rebuild calls
                        try:
                            coverage_command(config)
                        except Exception:
                            pass

                        mock_impl.assert_called_once()
                        mock_verify.assert_called_once()
                        mock_intent.assert_not_called()


class TestAutoRebuildSkipFlag:
    """Tests for skip_rebuild parameter."""

    @jig.verifies("S-070")
    def test_skip_rebuild_prevents_staleness_check(self, tmp_path: Path):
        """skip_rebuild=True prevents any staleness checking."""
        config = make_config(tmp_path)

        with patch("jig.cli.auto_rebuild.is_stale") as mock_is_stale:
            ensure_graphs_current(["impl", "verify", "intent"], config, skip_rebuild=True)
            mock_is_stale.assert_not_called()
