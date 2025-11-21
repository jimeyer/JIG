---
id: S-JIG-007
type: Specification
title: Multi-Source Credential Resolution
subsystem: jig-config
implements:
  - O-JIG-009
created: 2025-11-21
status: active
---

# Specification: Multi-Source Credential Resolution

## Purpose

Securely load API credentials from multiple sources with clear priority order, supporting both development and CI/CD workflows.

## Requirements

### Resolution Priority

Credentials are loaded in this order (first match wins):

1. **Explicit parameter** (highest priority)
   - Passed directly to function/command
   - Example: `--api-key sk-ant-...`
   - Use case: One-off overrides, testing

2. **Environment variable**
   - Format: `{SERVICE}_API_KEY` (e.g., `ANTHROPIC_API_KEY`)
   - Use case: CI/CD pipelines, containerized environments

3. **Config file**
   - Location: `~/.config/jig/credentials.yaml`
   - Format:
     ```yaml
     anthropic:
       api_key: sk-ant-...
     ```
   - Use case: Local development, persistent credentials

4. **System keyring** (optional, lowest priority)
   - Uses `keyring` library if installed
   - Service: `jig`, Key: `{service}_api_key`
   - Use case: macOS Keychain, Windows Credential Manager integration

### Validation

- **Config file permissions**: Must be 0600 (user-only read/write)
- **Warning if too broad**: Display warning if permissions >0600
- **Test authentication**: `jigy config validate-credentials` makes test API call

### Setup Command

```bash
jigy config set-credential <service>
```

Interactive prompts:
1. Enter API key (hidden input)
2. Choose storage: [1] Config file, [2] Keyring
3. Confirm: "✓ Credential saved to ~/.config/jig/credentials.yaml"
4. Warning: "⚠ Keep this file secure. Do not commit to version control."

## Interface

```python
def load_credential(
    service: str,
    explicit_key: Optional[str] = None
) -> str:
    """
    Load API credential from multiple sources.

    Args:
        service: Service name (e.g., "anthropic")
        explicit_key: Optional explicit key (highest priority)

    Returns:
        API key string

    Raises:
        CredentialError: If no credential found via any source
    """

def check_permissions(config_path: Path) -> None:
    """
    Verify config file has secure permissions.

    Args:
        config_path: Path to credentials.yaml

    Raises:
        PermissionWarning: If permissions are too broad (>0600)
    """

def save_credential(
    service: str,
    api_key: str,
    storage: Literal["config", "keyring"]
) -> None:
    """
    Save credential to specified storage.

    Args:
        service: Service name
        api_key: API key to save
        storage: Where to save ("config" or "keyring")

    Raises:
        StorageError: If unable to save credential
    """
```

## Error Handling

**No credential found:**
```
❌ Credential error: No API key found for 'anthropic'

💡 To set up credentials, run:
   jigy config set-credential anthropic

Alternatively, set environment variable:
   export ANTHROPIC_API_KEY=sk-ant-...
```

**Broad permissions:**
```
⚠ WARNING: Config file has insecure permissions (0644)
   Expected: 0600 (user-only read/write)
   File: /Users/name/.config/jig/credentials.yaml

Fix with: chmod 600 /Users/name/.config/jig/credentials.yaml
```

## CI/CD Integration

**GitHub Actions:**
```yaml
- name: Run AI repair
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: jigy ai-repair-orphaned-nodes --no-interactive
```

**GitLab CI:**
```yaml
script:
  - export ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
  - jigy ai-repair-orphaned-nodes --no-interactive
```

## Security Requirements

- Config directory must be created with 0700 permissions
- Config file must be created with 0600 permissions
- Never log or display full API keys (see S-JIG-010)
- Add credential paths to `.gitignore`

## Rationale

**Multiple sources:**
- Explicit: Developer control, testing flexibility
- Env var: Industry standard for 12-factor apps, CI/CD friendly
- Config file: Convenient for local dev, persistent across sessions
- Keyring: OS-level security (optional, not all systems support)

**Priority order:**
- Most specific (explicit) to least specific (keyring)
- Allows environment-specific overrides

## Dependencies

- PyYAML for config file parsing
- `keyring` library (optional, soft dependency)
- `getpass` for hidden input in interactive setup

## Testing

- Unit tests for each resolution source (mocked)
- Permission check tests (create test files with various perms)
- Integration test: Full setup → load → validate cycle
- CI/CD simulation: Test with env vars only

## References

- SCOPE: `docs/wip/S014_SCOPE_ai_repair_orphaned_nodes.md` (WU3)
- 12-factor app config: https://12factor.net/config
