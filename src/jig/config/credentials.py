# @jig C-CRED-001 implements:S-JIG-007,S-JIG-009,S-JIG-010 subsystem:jig-config interface:public
"""Secure credential management with multi-source resolution.

This module provides secure loading, storage, and validation of API credentials
with support for multiple sources: explicit parameters, environment variables,
config files, and system keyring.
"""

import os
import stat
from pathlib import Path
from typing import Literal, Optional

import yaml


class CredentialError(Exception):
    """Raised when credential loading fails."""

    pass


def load_credential(service: str, explicit_key: Optional[str] = None) -> str:
    """Load API credential from multiple sources with priority order.

    Resolution order (first match wins):
    1. Explicit parameter (highest priority)
    2. Environment variable ({SERVICE}_API_KEY)
    3. Config file (~/.config/jig/credentials.yaml)
    4. System keyring (if available)

    Args:
        service: Service name (e.g., "anthropic")
        explicit_key: Optional explicit key (overrides other sources)

    Returns:
        API key string

    Raises:
        CredentialError: If no credential found via any source

    Examples:
        >>> key = load_credential("anthropic")  # Uses env var or config
        >>> key = load_credential("anthropic", explicit_key="sk-ant-...")  # Uses explicit
    """
    # 1. Explicit parameter (highest priority)
    if explicit_key:
        return explicit_key

    # 2. Environment variable
    env_var = f"{service.upper()}_API_KEY"
    if env_var in os.environ:
        return os.environ[env_var]

    # 3. Config file
    config_path = _get_config_path()
    if config_path.exists():
        # Check permissions before reading
        _check_permissions(config_path)

        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)

            if config and service in config:
                api_key = config[service].get("api_key")
                if api_key:
                    return api_key
        except Exception as e:
            # Don't fail on config read errors, try next source
            pass

    # 4. System keyring (optional, lowest priority)
    try:
        import keyring

        key = keyring.get_password("jig", f"{service}_api_key")
        if key:
            return key
    except ImportError:
        # Keyring not installed, skip
        pass
    except Exception:
        # Keyring error, skip
        pass

    # No credential found
    raise CredentialError(
        f"No API key found for '{service}'\n\n"
        f"💡 To set up credentials, run:\n"
        f"   jigy config set-credential {service}\n\n"
        f"Alternatively, set environment variable:\n"
        f"   export {env_var}=sk-..."
    )


def save_credential(
    service: str, api_key: str, storage: Literal["config", "keyring"] = "config"
) -> None:
    """Save credential to specified storage.

    Args:
        service: Service name (e.g., "anthropic")
        api_key: API key to save
        storage: Where to save ("config" or "keyring")

    Raises:
        CredentialError: If unable to save credential
    """
    if storage == "config":
        _save_to_config_file(service, api_key)
    elif storage == "keyring":
        _save_to_keyring(service, api_key)
    else:
        raise ValueError(f"Invalid storage type: {storage}")


def validate_credential(service: str) -> dict[str, str]:
    """Validate that credential can be loaded and determine its source.

    Args:
        service: Service name (e.g., "anthropic")

    Returns:
        Dictionary with:
        - "status": "found" or "missing"
        - "source": "explicit" | "env" | "config" | "keyring" | "none"
        - "key_preview": Redacted key (if found)
        - "config_permissions": Permission status (if config file exists)

    Examples:
        >>> result = validate_credential("anthropic")
        >>> print(result["status"])  # "found" or "missing"
        >>> print(result["source"])  # "config"
    """
    result = {
        "status": "missing",
        "source": "none",
        "key_preview": "",
        "config_permissions": "",
    }

    # Check environment variable
    env_var = f"{service.upper()}_API_KEY"
    if env_var in os.environ:
        key = os.environ[env_var]
        result["status"] = "found"
        result["source"] = "env"
        result["key_preview"] = redact_api_key(key)
        return result

    # Check config file
    config_path = _get_config_path()
    if config_path.exists():
        perms, is_secure = _get_permissions(config_path)
        result["config_permissions"] = (
            "secure (0600)" if is_secure else f"insecure ({oct(perms)})"
        )

        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)

            if config and service in config:
                api_key = config[service].get("api_key")
                if api_key:
                    result["status"] = "found"
                    result["source"] = "config"
                    result["key_preview"] = redact_api_key(api_key)
                    return result
        except Exception:
            pass

    # Check keyring
    try:
        import keyring

        key = keyring.get_password("jig", f"{service}_api_key")
        if key:
            result["status"] = "found"
            result["source"] = "keyring"
            result["key_preview"] = redact_api_key(key)
            return result
    except (ImportError, Exception):
        pass

    return result


def redact_api_key(api_key: str) -> str:
    """Redact API key for safe display.

    Shows first 7 characters (prefix) and last 6 characters (suffix),
    hiding the middle with ellipsis.

    Args:
        api_key: Full API key

    Returns:
        Redacted key (e.g., "sk-ant-...xyz123")

    Examples:
        >>> redact_api_key("sk-ant-api03-1234567890abcdefghijklmnopqrstuvwxyz123")
        "sk-ant-...xyz123"
    """
    if len(api_key) <= 13:
        # Too short, hide completely
        return "*" * len(api_key)

    prefix = api_key[:7]  # "sk-ant-"
    suffix = api_key[-6:]  # Last 6 chars
    return f"{prefix}...{suffix}"


# Private helper functions


def _get_config_path() -> Path:
    """Get path to credentials config file."""
    return Path.home() / ".config" / "jig" / "credentials.yaml"


def _check_permissions(config_path: Path) -> None:
    """Check and warn about insecure file permissions."""
    perms, is_secure = _get_permissions(config_path)

    if not is_secure:
        print(
            f"\n⚠ WARNING: Config file has insecure permissions ({oct(perms)})\n"
            f"   Expected: 0600 (user-only read/write)\n"
            f"   File: {config_path}\n\n"
            f"   This allows other users on the system to read your API keys.\n\n"
            f"Fix with: chmod 600 {config_path}\n"
        )


def _get_permissions(path: Path) -> tuple[int, bool]:
    """Get file permissions and check if secure.

    Returns:
        Tuple of (permissions_octal, is_secure)
        e.g., (0o600, True) or (0o644, False)
    """
    st = path.stat()
    perms = stat.S_IMODE(st.st_mode)
    is_secure = perms == 0o600
    return perms, is_secure


def _save_to_config_file(service: str, api_key: str) -> None:
    """Save credential to config file with secure permissions."""
    config_path = _get_config_path()

    # Create directory with secure permissions
    config_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

    # Load existing config or create new
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {}

    # Add/update service credential
    config[service] = {"api_key": api_key}

    # Write with secure permissions
    # Note: We write to a temp file first, then rename atomically
    temp_path = config_path.with_suffix(".tmp")
    with open(temp_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    # Set secure permissions
    temp_path.chmod(0o600)

    # Atomic rename
    temp_path.rename(config_path)

    print(f"✓ Credential saved to {config_path}")
    print(
        f"\n⚠ WARNING: Keep this file secure. Do not commit to version control.\n"
    )


def _save_to_keyring(service: str, api_key: str) -> None:
    """Save credential to system keyring."""
    try:
        import keyring

        keyring.set_password("jig", f"{service}_api_key", api_key)
        print(f"✓ Credential saved to system keyring")
    except ImportError:
        raise CredentialError(
            "Keyring library not installed. Install with: pip install keyring"
        )
    except Exception as e:
        raise CredentialError(f"Failed to save to keyring: {e}")
