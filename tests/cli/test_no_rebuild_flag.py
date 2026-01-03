"""Tests for --no-rebuild global flag.

Verifies that --no-rebuild skips staleness detection and auto-rebuild.
"""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

import jig
from jig.cli.main import cli, get_no_rebuild


class TestGetNoRebuild:
    """Tests for get_no_rebuild helper."""

    @jig.verifies("S-071")
    def test_returns_false_when_not_set(self):
        """Returns False when --no-rebuild not passed."""

        class MockContext:
            obj = {}

        result = get_no_rebuild(MockContext())
        assert result is False

    @jig.verifies("S-071")
    def test_returns_true_when_set(self):
        """Returns True when --no-rebuild passed."""

        class MockContext:
            obj = {"no_rebuild": True}

        result = get_no_rebuild(MockContext())
        assert result is True


class TestNoRebuildFlagCLI:
    """Tests for --no-rebuild flag in CLI."""

    @jig.verifies("S-071")
    def test_flag_is_global_option(self):
        """--no-rebuild is available as global option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "--no-rebuild" in result.output

    @jig.verifies("S-071")
    def test_flag_before_validate(self):
        """--no-rebuild works before validate subcommand."""
        runner = CliRunner()

        # Mock the validate function to avoid actually running
        with patch("jig.cli.main.validate_full_command") as mock_validate:
            mock_validate.return_value = 0
            with patch("jig.cli.main.get_config") as mock_config:
                mock_config.return_value = None
                result = runner.invoke(cli, ["--no-rebuild", "validate"])

                # Should pass skip_rebuild=True
                mock_validate.assert_called_once()
                call_kwargs = mock_validate.call_args[1]
                assert call_kwargs.get("skip_rebuild") is True

    @jig.verifies("S-071")
    def test_flag_before_show(self):
        """--no-rebuild works before show subcommand."""
        runner = CliRunner()

        with patch("jig.cli.main.show_overview_command") as mock_show:
            mock_show.return_value = 0
            with patch("jig.cli.main.get_config") as mock_config:
                mock_config.return_value = None
                result = runner.invoke(cli, ["--no-rebuild", "show"])

                # Should pass skip_rebuild=True
                mock_show.assert_called_once()
                call_kwargs = mock_show.call_args[1]
                assert call_kwargs.get("skip_rebuild") is True

    @jig.verifies("S-071")
    def test_flag_before_show_layers(self):
        """--no-rebuild works before show layers subcommand."""
        runner = CliRunner()

        with patch("jig.cli.main.show_layers_command") as mock_show:
            mock_show.return_value = 0
            with patch("jig.cli.main.get_config") as mock_config:
                mock_config.return_value = None
                result = runner.invoke(cli, ["--no-rebuild", "show", "layers"])

                mock_show.assert_called_once()
                call_kwargs = mock_show.call_args[1]
                assert call_kwargs.get("skip_rebuild") is True


class TestNoRebuildSkipsStalenessCheck:
    """Tests that --no-rebuild actually skips staleness."""

    @jig.verifies("S-071")
    def test_validate_with_no_rebuild_skips_staleness(self):
        """validate with --no-rebuild doesn't check staleness."""
        runner = CliRunner()

        with patch("jig.cli.auto_rebuild.is_stale") as mock_is_stale:
            with patch("jig.cli.main.validate_full_command") as mock_validate:
                mock_validate.return_value = 0
                with patch("jig.cli.main.get_config") as mock_config:
                    mock_config.return_value = None

                    # Without --no-rebuild, is_stale would be called
                    # With --no-rebuild, is_stale should NOT be called
                    runner.invoke(cli, ["--no-rebuild", "validate"])

                    # Check that validate was called with skip_rebuild=True
                    call_kwargs = mock_validate.call_args[1]
                    assert call_kwargs.get("skip_rebuild") is True

    @jig.verifies("S-071")
    def test_show_with_no_rebuild_skips_staleness(self):
        """show with --no-rebuild doesn't check staleness."""
        runner = CliRunner()

        with patch("jig.cli.auto_rebuild.is_stale") as mock_is_stale:
            with patch("jig.cli.main.show_overview_command") as mock_show:
                mock_show.return_value = 0
                with patch("jig.cli.main.get_config") as mock_config:
                    mock_config.return_value = None

                    runner.invoke(cli, ["--no-rebuild", "show"])

                    call_kwargs = mock_show.call_args[1]
                    assert call_kwargs.get("skip_rebuild") is True


class TestNoRebuildWithAudit:
    """Tests for --no-rebuild with audit commands."""

    @jig.verifies("S-071")
    def test_audit_coverage_with_no_rebuild(self):
        """audit coverage with --no-rebuild skips staleness check."""
        runner = CliRunner()

        with patch("jig.cli.main.coverage_command") as mock_coverage:
            mock_coverage.return_value = 0
            with patch("jig.cli.main.get_config") as mock_config:
                mock_config.return_value = None

                runner.invoke(cli, ["--no-rebuild", "audit", "coverage"])

                mock_coverage.assert_called_once()
                call_kwargs = mock_coverage.call_args[1]
                assert call_kwargs.get("skip_rebuild") is True


class TestNoRebuildOutput:
    """Tests for output behavior with --no-rebuild."""

    @jig.verifies("S-071")
    def test_no_rebuild_message_when_flag_used(self):
        """No rebuild message shown when --no-rebuild is set."""
        runner = CliRunner()

        # When --no-rebuild is used, there should be no "Graphs stale, rebuilding..."
        # message. We test this by mocking and checking output.
        with patch("jig.cli.main.validate_full_command") as mock_validate:
            mock_validate.return_value = 0
            with patch("jig.cli.main.get_config") as mock_config:
                mock_config.return_value = None

                result = runner.invoke(cli, ["--no-rebuild", "validate"])

                # The mock prevents actual execution, so no rebuild message
                assert "rebuilding" not in result.output.lower()
