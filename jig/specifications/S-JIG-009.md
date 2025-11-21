---
id: S-JIG-009
type: Specification
title: Secure Credential Storage
subsystem: jig-config
implements:
  - O-JIG-009
created: 2025-11-21
status: active
---

# Specification: Secure Credential Storage

## Purpose

Ensure API credentials are stored with appropriate file system permissions and protected from unauthorized access.

## Requirements

### Config File Location

- **Path**: `~/.config/jig/credentials.yaml`
- **Cross-platform**: Use `Path.home()` for portability

### Directory Permissions

- **Config directory** (`~/.config/jig/`): 0700 (drwx------)
- Owner: Current user
- Group/Other: No permissions

### File Permissions

- **Credentials file** (`credentials.yaml`): 0600 (-rw-------)
- Owner: Current user (read/write)
- Group/Other: No permissions

### Validation

**On file creation:**
1. Create directory with `mkdir -p` equivalent
2. Set directory permissions to 0700
3. Create file with 0600 permissions atomically

**On file read:**
1. Check current permissions with `os.stat()`
2. If permissions >0600 (e.g., 0644, 0755):
   - Display warning (see below)
   - Continue operation (don't block, but warn)

**Warning message:**
```
⚠ WARNING: Config file has insecure permissions (0644)
   Expected: 0600 (user-only read/write)
   File: /Users/name/.config/jig/credentials.yaml

   This allows other users on the system to read your API keys.

Fix with: chmod 600 /Users/name/.config/jig/credentials.yaml
```

### Setup Command Behavior

When running `jigy config set-credential`:
1. Create `~/.config/jig/` if it doesn't exist (with 0700)
2. Write `credentials.yaml` with 0600 permissions
3. Verify permissions after write
4. Display confirmation with security notice

### Validation Command

```bash
jigy config validate-credentials
```

**Output:**
```
✓ Anthropic API key found (source: config file)
✓ Config file permissions: 0600 (secure)
✓ Successfully authenticated with Claude API

All credential checks passed.
```

**If issues found:**
```
✓ Anthropic API key found (source: config file)
⚠ Config file permissions: 0644 (INSECURE - should be 0600)
✗ Authentication failed: Invalid API key

Fix permissions: chmod 600 ~/.config/jig/credentials.yaml
Then verify API key: jigy config set-credential anthropic
```

## Implementation

### Permission Check Function

```python
def check_permissions(config_path: Path) -> Tuple[int, bool]:
    """
    Check file permissions for security.

    Args:
        config_path: Path to credentials file

    Returns:
        (permissions_octal, is_secure)
        e.g., (0o600, True) or (0o644, False)
    """
    import stat
    st = config_path.stat()
    perms = stat.S_IMODE(st.st_mode)
    is_secure = perms == 0o600
    return perms, is_secure
```

### File Creation

```python
def create_credentials_file(config_path: Path, content: str) -> None:
    """
    Create credentials file with secure permissions.

    Args:
        config_path: Path to credentials file
        content: YAML content to write
    """
    # Create directory with secure perms
    config_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

    # Write file
    config_path.write_text(content)

    # Set secure permissions (in case umask interfered)
    config_path.chmod(0o600)
```

## Platform Considerations

### Unix/Linux/macOS
- Standard POSIX permissions work as specified
- `chmod 600` enforced reliably

### Windows
- File permissions behave differently (ACLs)
- Permission checks may need platform-specific logic
- Consider using `os.name == 'nt'` to skip permission warnings on Windows
- Or implement Windows ACL checks for parity

## Security Rationale

**Why 0600 for credentials file:**
- Prevents other users on shared systems from reading API keys
- Industry standard for sensitive config files (SSH keys, AWS credentials)
- Matches behavior of `~/.ssh/id_rsa`, `~/.aws/credentials`

**Why 0700 for config directory:**
- Prevents other users from listing directory contents
- Defense in depth: even if file permissions misconfigured, directory blocks access

**Why warn instead of block:**
- Don't break workflows on misconfiguration
- User may have legitimate reasons (testing, debugging)
- Warning educates without obstructing

## Testing

- Test file creation sets correct permissions
- Test permission check correctly identifies 0600, 0644, 0755
- Test warning message displays on broad permissions
- Test cross-platform behavior (Unix, macOS, Windows)

## Compliance

This specification aligns with:
- OWASP secure storage guidelines
- CIS Benchmark recommendations for configuration files
- Industry standards (AWS CLI, gcloud, kubectl credential storage)

## References

- SCOPE: `docs/wip/S014_SCOPE_ai_repair_orphaned_nodes.md` (WU3)
- Related: S-JIG-007 (credential resolution), S-JIG-010 (exposure prevention)
