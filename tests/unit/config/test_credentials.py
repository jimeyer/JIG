# @jig T-CRED-001 verifies:S-JIG-007,S-JIG-009,S-JIG-010 subsystem:jig-config
"""Tests for credential management module."""

import os
import stat
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml

from jig.config.credentials import (
    CredentialError,
    load_credential,
    redact_api_key,
    save_credential,
    validate_credential,
)


# Fixtures
@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary config directory."""
    config_dir = tmp_path / ".config" / "jig"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def temp_config_file(temp_config_dir):
    """Create temporary credentials file."""
    config_file = temp_config_dir / "credentials.yaml"
    return config_file


@pytest.fixture
def mock_config_path(temp_config_file, monkeypatch):
    """Mock the config path to use temp directory."""
    monkeypatch.setattr(
        "jig.config.credentials._get_config_path", lambda: temp_config_file
    )
    return temp_config_file


@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment variables."""
    # Remove any API key env vars
    for key in list(os.environ.keys()):
        if "API_KEY" in key:
            monkeypatch.delenv(key, raising=False)


# Tests for credential resolution priority


def test_explicit_key_highest_priority(mock_config_path, monkeypatch, clean_env):
    """Explicit key parameter has highest priority."""
    # Set up lower-priority sources
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-key-123")
    mock_config_path.write_text(
        yaml.dump({"anthropic": {"api_key": "config-key-123"}})
    )
    mock_config_path.chmod(0o600)

    # Explicit key should win
    explicit_key = "explicit-key-123"
    result = load_credential("anthropic", explicit_key=explicit_key)

    assert result == explicit_key
    assert result != "env-key-123"
    assert result != "config-key-123"


def test_env_var_second_priority(mock_config_path, monkeypatch, clean_env):
    """Environment variable has second priority."""
    # Set up env var
    env_key = "env-key-456"
    monkeypatch.setenv("ANTHROPIC_API_KEY", env_key)

    # Set up config file (lower priority)
    mock_config_path.write_text(
        yaml.dump({"anthropic": {"api_key": "config-key-456"}})
    )
    mock_config_path.chmod(0o600)

    result = load_credential("anthropic")

    assert result == env_key
    assert result != "config-key-456"


def test_config_file_third_priority(mock_config_path, clean_env):
    """Config file has third priority."""
    config_key = "config-key-789"
    mock_config_path.write_text(
        yaml.dump({"anthropic": {"api_key": config_key}})
    )
    mock_config_path.chmod(0o600)

    result = load_credential("anthropic")

    assert result == config_key


def test_keyring_fourth_priority(mock_config_path, clean_env, monkeypatch):
    """Keyring has lowest priority (fourth)."""
    keyring_key = "keyring-key-101"

    # Mock keyring module
    mock_keyring = MagicMock()
    mock_keyring.get_password.return_value = keyring_key
    monkeypatch.setitem(__import__("sys").modules, "keyring", mock_keyring)

    # No config file, no env var, so should use keyring
    result = load_credential("anthropic")

    assert result == keyring_key
    mock_keyring.get_password.assert_called_once_with(
        "jig", "anthropic_api_key"
    )


def test_no_credential_raises(mock_config_path, clean_env):
    """Raises CredentialError if no credential found."""
    with pytest.raises(CredentialError, match="No API key found for 'anthropic'"):
        load_credential("anthropic")


def test_error_message_includes_setup_instructions(mock_config_path, clean_env):
    """Error message includes helpful setup instructions."""
    try:
        load_credential("anthropic")
        pytest.fail("Should have raised CredentialError")
    except CredentialError as e:
        error_msg = str(e)
        assert "jigy config set-credential anthropic" in error_msg
        assert "export ANTHROPIC_API_KEY" in error_msg


# Tests for permission checking


def test_permission_warning_on_insecure_file(mock_config_path, clean_env, capsys):
    """Warns if config file has insecure permissions."""
    # Create config with broad permissions
    mock_config_path.write_text(
        yaml.dump({"anthropic": {"api_key": "test-key"}})
    )
    mock_config_path.chmod(0o644)  # Insecure

    load_credential("anthropic")

    captured = capsys.readouterr()
    assert "WARNING" in captured.out
    assert "insecure permissions" in captured.out
    assert "0o644" in captured.out
    assert "chmod 600" in captured.out


def test_no_warning_on_secure_file(mock_config_path, clean_env, capsys):
    """No warning if config file has secure permissions."""
    mock_config_path.write_text(
        yaml.dump({"anthropic": {"api_key": "test-key"}})
    )
    mock_config_path.chmod(0o600)  # Secure

    load_credential("anthropic")

    captured = capsys.readouterr()
    assert "WARNING" not in captured.out


# Tests for redaction


def test_redact_key_shows_prefix_and_suffix():
    """Redaction shows first 7 and last 6 characters."""
    key = "sk-ant-api03-1234567890abcdefghijklmnopqrstuvwxyz123"
    redacted = redact_api_key(key)

    assert redacted == "sk-ant-...xyz123"
    assert "1234567890" not in redacted  # Middle should be hidden


def test_redact_short_key_hides_completely():
    """Short keys are completely hidden."""
    short_key = "abc123"
    redacted = redact_api_key(short_key)

    assert redacted == "******"
    assert "abc" not in redacted
    assert "123" not in redacted


def test_redact_key_preserves_length_info():
    """Redacted key gives length information."""
    key = "sk-ant-" + "x" * 50
    redacted = redact_api_key(key)

    # Should show prefix and suffix
    assert redacted.startswith("sk-ant-")
    assert redacted.endswith("x" * 6)
    assert "..." in redacted


# Tests for saving credentials


def test_save_to_config_creates_directory(mock_config_path):
    """Saving creates config directory if missing."""
    # Remove directory
    if mock_config_path.parent.exists():
        mock_config_path.unlink(missing_ok=True)
        mock_config_path.parent.rmdir()

    save_credential("anthropic", "test-key-123", storage="config")

    assert mock_config_path.exists()
    assert mock_config_path.parent.exists()


def test_save_to_config_sets_secure_permissions(mock_config_path, capsys):
    """Saved config file has 0600 permissions."""
    save_credential("anthropic", "test-key-123", storage="config")

    perms = stat.S_IMODE(mock_config_path.stat().st_mode)
    assert perms == 0o600


def test_save_to_config_preserves_existing_services(mock_config_path):
    """Saving preserves other services in config."""
    # Create config with existing service
    mock_config_path.write_text(
        yaml.dump({"openai": {"api_key": "existing-key"}})
    )
    mock_config_path.chmod(0o600)

    # Save new service
    save_credential("anthropic", "new-key", storage="config")

    # Both should exist
    with open(mock_config_path) as f:
        config = yaml.safe_load(f)

    assert "openai" in config
    assert config["openai"]["api_key"] == "existing-key"
    assert "anthropic" in config
    assert config["anthropic"]["api_key"] == "new-key"


def test_save_to_config_updates_existing_service(mock_config_path):
    """Saving updates existing service key."""
    # Create config
    mock_config_path.write_text(
        yaml.dump({"anthropic": {"api_key": "old-key"}})
    )
    mock_config_path.chmod(0o600)

    # Update key
    save_credential("anthropic", "new-key", storage="config")

    with open(mock_config_path) as f:
        config = yaml.safe_load(f)

    assert config["anthropic"]["api_key"] == "new-key"


def test_save_to_keyring(monkeypatch):
    """Saving to keyring calls keyring.set_password."""
    # Mock keyring module
    mock_keyring = MagicMock()
    monkeypatch.setitem(__import__("sys").modules, "keyring", mock_keyring)

    save_credential("anthropic", "test-key", storage="keyring")

    mock_keyring.set_password.assert_called_once_with(
        "jig", "anthropic_api_key", "test-key"
    )


def test_save_to_keyring_without_library(monkeypatch):
    """Saving to keyring without library raises clear error."""
    # Remove keyring from sys.modules to simulate not installed
    import sys

    if "keyring" in sys.modules:
        monkeypatch.delitem(sys.modules, "keyring")

    with pytest.raises(CredentialError, match="Keyring library not installed"):
        save_credential("anthropic", "test-key", storage="keyring")


# Tests for validation


def test_validate_finds_env_var(monkeypatch, clean_env):
    """Validation detects environment variable."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")

    result = validate_credential("anthropic")

    assert result["status"] == "found"
    assert result["source"] == "env"
    assert result["key_preview"] == redact_api_key("test-key-123")


def test_validate_finds_config_file(mock_config_path, clean_env):
    """Validation detects config file."""
    mock_config_path.write_text(
        yaml.dump({"anthropic": {"api_key": "test-key-456"}})
    )
    mock_config_path.chmod(0o600)

    result = validate_credential("anthropic")

    assert result["status"] == "found"
    assert result["source"] == "config"
    assert result["key_preview"] == redact_api_key("test-key-456")
    assert result["config_permissions"] == "secure (0600)"


def test_validate_detects_insecure_permissions(mock_config_path, clean_env):
    """Validation reports insecure permissions."""
    mock_config_path.write_text(
        yaml.dump({"anthropic": {"api_key": "test-key"}})
    )
    mock_config_path.chmod(0o644)

    result = validate_credential("anthropic")

    assert "insecure" in result["config_permissions"]
    assert "0o644" in result["config_permissions"]


def test_validate_finds_keyring(clean_env, monkeypatch):
    """Validation detects keyring."""
    # Mock keyring module
    mock_keyring = MagicMock()
    mock_keyring.get_password.return_value = "keyring-key"
    monkeypatch.setitem(__import__("sys").modules, "keyring", mock_keyring)

    result = validate_credential("anthropic")

    assert result["status"] == "found"
    assert result["source"] == "keyring"
    assert result["key_preview"] == redact_api_key("keyring-key")


def test_validate_missing_credential(mock_config_path, clean_env):
    """Validation reports missing credential."""
    result = validate_credential("anthropic")

    assert result["status"] == "missing"
    assert result["source"] == "none"
    assert result["key_preview"] == ""


# Tests for error handling


def test_handles_corrupted_config_file(mock_config_path, clean_env):
    """Handles corrupted YAML gracefully."""
    # Write invalid YAML
    mock_config_path.write_text("{{invalid yaml: [}")
    mock_config_path.chmod(0o600)

    # Should not crash, should try next source (which is none, so raises)
    with pytest.raises(CredentialError):
        load_credential("anthropic")


def test_handles_missing_config_directory(tmp_path, monkeypatch, clean_env):
    """Handles missing config directory gracefully."""
    nonexistent = tmp_path / "nonexistent" / "jig" / "credentials.yaml"
    monkeypatch.setattr(
        "jig.config.credentials._get_config_path", lambda: nonexistent
    )

    # Should not crash, should raise CredentialError
    with pytest.raises(CredentialError):
        load_credential("anthropic")


# Integration-style tests


def test_full_workflow_save_and_load(mock_config_path):
    """Full workflow: save then load."""
    # Save credential
    save_credential("anthropic", "workflow-key-123", storage="config")

    # Load it back
    key = load_credential("anthropic")

    assert key == "workflow-key-123"


def test_multiple_services_independent(mock_config_path):
    """Multiple services can be managed independently."""
    # Save two services
    save_credential("anthropic", "anthropic-key", storage="config")
    save_credential("openai", "openai-key", storage="config")

    # Load each
    anthropic_key = load_credential("anthropic")
    openai_key = load_credential("openai")

    assert anthropic_key == "anthropic-key"
    assert openai_key == "openai-key"


def test_validation_after_save(mock_config_path):
    """Validation works after saving."""
    save_credential("anthropic", "validated-key", storage="config")

    result = validate_credential("anthropic")

    assert result["status"] == "found"
    assert result["source"] == "config"
    assert result["config_permissions"] == "secure (0600)"
