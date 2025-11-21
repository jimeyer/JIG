---
id: S-JIG-010
type: Specification
title: Zero Credential Exposure
subsystem: jig-config
implements:
  - O-JIG-009
created: 2025-11-21
status: active
---

# Specification: Zero Credential Exposure

## Purpose

Ensure API credentials are never logged, displayed, or included in error messages in full form, preventing accidental exposure.

## Requirements

### Redaction Rules

**API keys must be redacted in:**
- Log messages (all levels: DEBUG, INFO, WARNING, ERROR)
- CLI output (stdout, stderr)
- Error messages and exception text
- Stack traces
- Debug output
- Help text examples

**Redaction format:**
```
Full key:    sk-ant-api03-1234567890abcdefghijklmnopqrstuvwxyz...xyz123
Redacted:    sk-ant-...xyz123
```

**Algorithm:**
- Show first 7 characters (prefix identifier: `sk-ant-`)
- Show "..."
- Show last 6 characters (for debugging key source)
- Total visible: 13 characters + ellipsis

### Redaction Function

```python
def redact_api_key(api_key: str) -> str:
    """
    Redact API key for safe display.

    Args:
        api_key: Full API key (e.g., "sk-ant-api03-...")

    Returns:
        Redacted key showing prefix and suffix only

    Examples:
        >>> redact_api_key("sk-ant-api03-1234567890abcdef...xyz123")
        "sk-ant-...xyz123"
    """
    if len(api_key) <= 13:
        return "*" * len(api_key)  # Too short, hide completely

    prefix = api_key[:7]   # "sk-ant-"
    suffix = api_key[-6:]  # Last 6 chars
    return f"{prefix}...{suffix}"
```

### Application Points

1. **Credential Loading**
   ```python
   # ✗ BAD
   logger.info(f"Loaded API key: {api_key}")

   # ✓ GOOD
   logger.info(f"Loaded API key: {redact_api_key(api_key)}")
   ```

2. **Error Messages**
   ```python
   # ✗ BAD
   raise ValueError(f"Invalid API key: {api_key}")

   # ✓ GOOD
   raise ValueError(f"Invalid API key: {redact_api_key(api_key)}")
   ```

3. **CLI Output**
   ```python
   # ✗ BAD
   click.echo(f"Using API key: {api_key}")

   # ✓ GOOD
   click.echo(f"Using API key: {redact_api_key(api_key)}")
   ```

4. **Validation Command**
   ```bash
   jigy config validate-credentials
   # Output: ✓ API key found: sk-ant-...xyz123 (source: config file)
   ```

5. **Exception Handling**
   ```python
   # ✗ BAD
   except AuthenticationError as e:
       raise RuntimeError(f"Auth failed with key {api_key}: {e}")

   # ✓ GOOD
   except AuthenticationError as e:
       raise RuntimeError(f"Auth failed with key {redact_api_key(api_key)}: {e}")
   ```

### Logging Configuration

**Global redaction filter:**
```python
import logging
import re

class CredentialRedactionFilter(logging.Filter):
    """Redact API keys from all log messages."""

    API_KEY_PATTERN = re.compile(r'sk-ant-[a-zA-Z0-9_-]{20,}')

    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = self.API_KEY_PATTERN.sub(
                lambda m: redact_api_key(m.group(0)),
                record.msg
            )
        return True

# Apply to all loggers
logging.getLogger().addFilter(CredentialRedactionFilter())
```

### Never Store Credentials In

- ✗ Git commits (enforced via `.gitignore`)
- ✗ Log files
- ✗ Database tables
- ✗ Cache files
- ✗ Temporary files without secure permissions
- ✗ Environment variables (display in `env` or `printenv`)
- ✗ Stack traces
- ✗ HTTP request logs

## Testing

### Unit Tests

```python
def test_redact_api_key():
    key = "sk-ant-api03-1234567890abcdefghijklmnopqrstuvwxyz123"
    redacted = redact_api_key(key)
    assert redacted == "sk-ant-...xyz123"
    assert key not in redacted  # Full key never appears

def test_no_keys_in_logs(caplog):
    """Verify API keys are redacted in logs."""
    api_key = "sk-ant-api03-test123456789"

    with caplog.at_level(logging.INFO):
        logger.info(f"Using key: {api_key}")

    # Full key should NOT appear in logs
    assert api_key not in caplog.text
    # Redacted key SHOULD appear
    assert "sk-ant-...test123" in caplog.text

def test_no_keys_in_exceptions():
    """Verify API keys are redacted in exception messages."""
    api_key = "sk-ant-api03-test123456789"

    try:
        raise ValueError(f"Invalid key: {redact_api_key(api_key)}")
    except ValueError as e:
        assert api_key not in str(e)
        assert "sk-ant-...test123" in str(e)
```

### Security Audit Tests

```python
def test_grep_codebase_for_hardcoded_keys():
    """Ensure no hardcoded API keys in source."""
    # Pattern that matches Anthropic API keys
    pattern = r'sk-ant-[a-zA-Z0-9_-]{20,}'

    for file in Path("jig").rglob("*.py"):
        content = file.read_text()
        matches = re.findall(pattern, content)

        # Exclude test files with dummy keys
        if "test_" in file.name:
            continue

        assert not matches, f"Found potential API key in {file}: {matches}"

def test_credentials_in_gitignore():
    """Verify credential files are in .gitignore."""
    gitignore = Path(".gitignore").read_text()
    assert "credentials.yaml" in gitignore
    assert "**/credentials.yaml" in gitignore
```

## CLI Help Examples

**Show redacted keys in examples:**
```bash
jigy ai-repair-orphaned-nodes --help

Options:
  --api-key TEXT  Anthropic API key (overrides config)
                  Example: --api-key sk-ant-...xyz123
```

## Validation Command

```bash
jigy config validate-credentials

# Output (showing redacted key):
✓ Anthropic API key found: sk-ant-...xyz123 (source: config file)
✓ Config file permissions: 0600 (secure)
✓ Successfully authenticated with Claude API
```

## Incident Response

**If a key is accidentally exposed:**
1. Immediately revoke the exposed key in Anthropic Console
2. Generate new API key
3. Update credentials: `jigy config set-credential anthropic`
4. Audit logs/commits to identify scope of exposure
5. If committed to git:
   - Revoke key immediately
   - Consider repo history rewrite (git-filter-repo)
   - Inform team

## Rationale

**Why redact:**
- Accidental exposure in logs, screenshots, bug reports
- Credentials may be logged by third-party libraries
- Debug output often shared publicly (GitHub issues, Stack Overflow)

**Why show prefix/suffix:**
- Prefix identifies key type (Anthropic vs. other services)
- Suffix helps debug which key is being used (config vs. env vs. keyring)
- Maintains debuggability without exposing full key

**Why global log filter:**
- Defense in depth: catches keys even if redaction forgotten
- Protects against third-party library logging
- One-time setup, automatic protection

## Compliance

This specification aligns with:
- OWASP A07:2021 - Identification and Authentication Failures
- NIST SP 800-53 IA-5 (Authenticator Management)
- PCI DSS Requirement 3.4 (Render PAN unreadable)

## References

- SCOPE: `docs/wip/S014_SCOPE_ai_repair_orphaned_nodes.md` (WU3, WU6)
- Related: S-JIG-009 (secure storage), S-JIG-007 (credential resolution)
