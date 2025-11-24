# PROPOSAL: Subsystem-Based Test Execution

**Author:** Jim Meyer
**Date:** 2025-11-15
**Status:** Draft for Review
**Related:** JIG-Concept-v5.md, JIG_DECOMPOSITION_STRATEGY.md

## Problem Statement

Developers need to run tests for a specific subsystem (e.g., Protocol Stack) without manually tracking which test files belong to that subsystem. Currently:

**Current State:**
- ❌ No way to run `pytest --subsystem PS` or `jigy test PS`
- ❌ Protocol Stack tests scattered across `test/protocol/`, `test/transport/`, `test/lint/`
- ❌ Subsystem boundaries not encoded in test infrastructure
- ❌ Manual directory-based testing (`pytest test/protocol/`) misses cross-cutting tests

**Example:** Protocol Stack (subsystem `protocol`) has tests in:
- `test/protocol/test_codec_contracts.py` (T-PS-010, T-PS-011, T-PS-012)
- `test/lint/test_layer_isolation.py` (T-PS-006)
- `test/transport/test_mock_transport.py` (future T-PS-008)

Running `pytest test/protocol/` misses T-PS-006 (layer isolation).

**Requirements:**
1. **Deterministic**: Find all tests for subsystem `X` reliably
2. **Sustainable**: Minimal manual maintenance, single source of truth
3. **Fast**: No significant overhead at test collection time
4. **Developer-friendly**: Simple CLI (`pytest -m subsystem_protocol` or `jigy test PS`)
5. **Aligned with JIG**: Leverage existing `@jig` annotations (`subsystem:protocol`)

## Proposed Solution: Three-Tier Approach

### Tier 1: Immediate (Pytest Markers)

**Add explicit pytest markers to test nodes**, aligned with `@jig` annotations.

**Example:**
```python
import pytest

# @jig T-PS-006 validates:S-PS-006 subsystem:protocol
@pytest.mark.subsystem("protocol")
def test_protocol_layer_does_not_import_transport():
    """Layer 3 (Protocol) must not import Layer 1 (Transport) directly."""
    ...
```

**Usage:**
```bash
# Run all Protocol Stack tests
pytest -m 'subsystem("protocol")'

# Or with simpler marker (protocol_stack)
pytest -m protocol_stack

# Run multiple subsystems
pytest -m 'subsystem("protocol") or subsystem("netspace")'
```

**Implementation:**
1. Define marker in `pytest.ini`:
   ```ini
   [pytest]
   markers =
       subsystem(name): mark test as belonging to a subsystem (protocol, netspace, gateway, etc.)
       protocol_stack: shorthand for subsystem("protocol")
       netspace: shorthand for subsystem("netspace")
       gateway: shorthand for subsystem("gateway")
   ```

2. Annotate test nodes (classes/functions) with markers:
   ```python
   @pytest.mark.subsystem("protocol")
   # @jig T-PS-010 validates:S-PS-010 subsystem:protocol
   class TestCodecRoundtripInvariant:
       ...
   ```

**Pros:**
- ✅ Works immediately with vanilla pytest
- ✅ IDE support (PyCharm, VSCode show markers)
- ✅ Fast (no parsing overhead)
- ✅ Standard pytest practice

**Cons:**
- ⚠️ Duplication: `subsystem:protocol` in both `@jig` comment and `@pytest.mark.subsystem("protocol")`
- ⚠️ Manual maintenance required
- ⚠️ Can drift out of sync

**Mitigation:** Add validation (Tier 2).

---

### Tier 2: Validation (Automated Alignment Check)

**Validate that pytest markers match `@jig` annotations** to prevent drift.

**Implementation:** Create `test/conftest.py` hook:

```python
# test/conftest.py
import re
import pytest

def pytest_collection_modifyitems(config, items):
    """Validate @jig annotations match pytest.mark.subsystem markers."""

    mismatches = []

    for item in items:
        # Extract @jig annotation from test source
        jig_subsystem = extract_jig_subsystem(item)

        # Extract pytest marker
        marker_subsystems = [
            mark.args[0] for mark in item.iter_markers(name="subsystem")
        ]

        # Validate match
        if jig_subsystem and not marker_subsystems:
            mismatches.append(f"{item.nodeid}: has @jig subsystem:{jig_subsystem} but no @pytest.mark.subsystem")
        elif jig_subsystem and jig_subsystem not in marker_subsystems:
            mismatches.append(f"{item.nodeid}: @jig subsystem:{jig_subsystem} != @pytest.mark.subsystem({marker_subsystems})")

    if mismatches:
        raise ValueError(
            "Subsystem annotation mismatch:\n" + "\n".join(mismatches)
        )

def extract_jig_subsystem(item):
    """Extract subsystem from @jig comment in test function/class."""
    import inspect

    # Get test function/class source
    try:
        source = inspect.getsource(item.obj)
    except (TypeError, OSError):
        return None

    # Parse @jig annotation: # @jig T-PS-006 validates:S-PS-006 subsystem:protocol
    match = re.search(r'#\s*@jig\s+T-\w+-\d+.*subsystem:(\w+)', source)
    if match:
        return match.group(1)
    return None
```

**Usage:**
```bash
# Pytest automatically validates on every run
pytest -m 'subsystem("protocol")'

# If markers don't match @jig annotations, test collection fails with clear error
```

**Pros:**
- ✅ Enforces alignment between @jig and pytest markers
- ✅ Fails fast if developer forgets marker
- ✅ Single source of truth (@jig annotation is canonical)

**Cons:**
- ⚠️ Small collection overhead (parsing source for @jig comments)

---

### Tier 3: Enhanced CLI (jigy test command)

**Provide `jigy test` command** for subsystem-aware testing with additional features.

**Implementation:** Create `jigy` tool (Python CLI):

```python
#!/usr/bin/env python3
"""jigy - JIG Intent Graph CLI tool."""

import click
import subprocess
import json
from pathlib import Path

@click.group()
def cli():
    """JIG Intent Graph tools."""
    pass

@cli.command()
@click.argument('subsystem')
@click.option('--verbose', '-v', is_flag=True, help='Verbose test output')
@click.option('--coverage', is_flag=True, help='Show alignment coverage after tests')
def test(subsystem, verbose, coverage):
    """Run tests for a subsystem.

    Examples:
        jigy test PS          # Protocol Stack
        jigy test protocol    # Same (accepts full name or abbreviation)
        jigy test NS          # NetSpace
    """
    # Map abbreviations to full subsystem names
    subsystem_map = {
        'PS': 'protocol',
        'NS': 'netspace',
        'GW': 'gateway',
        'APP': 'application',
    }

    subsystem_name = subsystem_map.get(subsystem.upper(), subsystem.lower())

    # Load test_index.json to validate subsystem exists
    test_index_path = Path('.jig/generated/test_index.json')
    if test_index_path.exists():
        with open(test_index_path) as f:
            test_index = json.load(f)
            if test_index['metadata']['subsystem'] != subsystem_name:
                click.echo(f"Warning: test_index.json is for subsystem '{test_index['metadata']['subsystem']}'", err=True)

    # Run pytest with subsystem marker
    pytest_args = [
        'pytest',
        '-m', f'subsystem("{subsystem_name}")',
    ]

    if verbose:
        pytest_args.append('-v')

    click.echo(f"Running tests for subsystem: {subsystem_name}")
    result = subprocess.run(pytest_args)

    if coverage and result.returncode == 0:
        # Show alignment coverage from alignment_report.md
        click.echo("\n" + "="*60)
        click.echo(f"Subsystem '{subsystem_name}' Alignment Coverage:")
        click.echo("="*60)

        alignment_report_path = Path('.jig/generated/alignment_report.md')
        if alignment_report_path.exists():
            # Extract coverage section (simplified)
            with open(alignment_report_path) as f:
                lines = f.readlines()
                in_metrics = False
                for line in lines:
                    if '## Coverage Metrics' in line:
                        in_metrics = True
                    elif in_metrics and line.startswith('##'):
                        break
                    elif in_metrics:
                        click.echo(line.rstrip())

    return result.returncode

if __name__ == '__main__':
    cli()
```

**Installation:**
```bash
# Add to pyproject.toml
[tool.poetry.scripts]
jigy = "jig.cli:cli"

# Or standalone
chmod +x jigy
ln -s $(pwd)/jigy /usr/local/bin/jigy
```

**Usage:**
```bash
# Run Protocol Stack tests
jigy test PS
jigy test protocol  # Equivalent

# Verbose output
jigy test PS -v

# Show alignment coverage after tests pass
jigy test PS --coverage

# Future: Run only failing tests from last alignment report
jigy test PS --repair
```

**Pros:**
- ✅ Clean abstraction (developer thinks in subsystems, not pytest markers)
- ✅ Abbreviations (PS, NS, GW) for speed
- ✅ Can add alignment-aware features (coverage reports, repair mode)
- ✅ Extensible (future: `jigy graph PS`, `jigy align PS`, `jigy spec create`)

**Cons:**
- ⚠️ Requires separate tool installation
- ⚠️ Not pure pytest (but wraps pytest, so existing workflows still work)

---

## Migration Path

### Phase 1: Bootstrap Protocol Stack (Now)
1. Add `subsystem` marker definition to `pytest.ini`
2. Annotate existing Protocol Stack tests (T-PS-006, T-PS-010, T-PS-011, T-PS-012)
3. Verify: `pytest -m 'subsystem("protocol")' -v`

**Effort:** 30 minutes

### Phase 2: Add Validation (Week 1)
1. Create `test/conftest.py` with alignment validation hook
2. Run test suite to ensure markers match @jig annotations
3. Fix any mismatches

**Effort:** 60 minutes

### Phase 3: Build jigy CLI (Week 2-3)
1. Create `jigy` Python package with Click CLI
2. Implement `jigy test <subsystem>` command
3. Add subsystem abbreviation mapping (PS → protocol)
4. Document in README.md

**Effort:** 4 hours

### Phase 4: Expand Features (Future)
- `jigy test --repair`: Run tests for specs with missing coverage
- `jigy test --watch`: Re-run tests on file changes (subsystem-aware)
- `jigy align <subsystem>`: Generate alignment report for one subsystem
- `jigy graph <subsystem>`: Visualize OSTC graph

---

## Alternative Approaches Considered

### Alternative 1: Directory-based (pytest-testconfig)
**Approach:** Map `test/protocol/` → subsystem `protocol` via config file.

**Rejected because:**
- ❌ Doesn't handle cross-cutting tests (`test/lint/test_layer_isolation.py`)
- ❌ Forces subsystems to match directory structure (inflexible)

### Alternative 2: Auto-generate markers from @jig comments
**Approach:** Parse `@jig` comments at pytest collection time, add markers dynamically.

**Rejected because:**
- ❌ Parsing overhead on every test run
- ❌ Implicit behavior (developers can't see markers in code)
- ❌ Harder to debug when things go wrong

**Decision:** Explicit markers (Tier 1) are better developer experience.

### Alternative 3: Separate test_index.json-driven runner
**Approach:** `jigy` reads `test_index.json`, runs pytest with file paths.

**Rejected because:**
- ❌ Requires `test_index.json` to be up-to-date (manual regeneration)
- ❌ Doesn't leverage pytest's built-in marker system
- ❌ Breaks IDE test discovery

**Decision:** Markers + `jigy` wrapper (Tier 3) provides both pytest native and enhanced features.

---

## Implementation Checklist

**Phase 1 (Bootstrap):**
- [ ] Add `subsystem` marker definition to `pytest.ini`
- [ ] Annotate `test/protocol/test_codec_contracts.py` classes with `@pytest.mark.subsystem("protocol")`
- [ ] Annotate `test/lint/test_layer_isolation.py` functions with `@pytest.mark.subsystem("protocol")`
- [ ] Verify: `pytest -m 'subsystem("protocol")' --collect-only` shows all Protocol Stack tests
- [ ] Update `.jig/test_nodes.md` with marker usage instructions

**Phase 2 (Validation):**
- [ ] Create `test/conftest.py` with `pytest_collection_modifyitems` hook
- [ ] Implement `extract_jig_subsystem()` parser
- [ ] Add alignment validation logic
- [ ] Run full test suite to validate
- [ ] Document validation behavior in `test/README.md`

**Phase 3 (CLI):**
- [ ] Create `jig/cli.py` with Click
- [ ] Implement `jigy test <subsystem>` command
- [ ] Add subsystem abbreviation mapping
- [ ] Add `--coverage` flag (show alignment report)
- [ ] Create `pyproject.toml` script entry point
- [ ] Document in `docs/jig/README.md`

---

## Success Criteria

**Developer Experience:**
- ✅ Developer runs `pytest -m protocol_stack` → sees 31 tests
- ✅ Developer runs `jigy test PS` → sees same 31 tests + alignment coverage
- ✅ New test without `@pytest.mark.subsystem` fails validation with clear error message
- ✅ Subsystem test runs are deterministic (always same test set for same subsystem)

**Alignment:**
- ✅ `@jig` annotations remain single source of truth
- ✅ Pytest markers auto-validated against `@jig` comments
- ✅ test_index.json generation can extract markers for verification

**Scalability:**
- ✅ Adding new subsystem (e.g., NetSpace) requires only:
  1. Add marker definition to `pytest.ini`
  2. Annotate tests with `@pytest.mark.subsystem("netspace")`
- ✅ No central registry to update
- ✅ Works with 10+ subsystems without performance degradation

---

## Open Questions

1. **Marker naming convention?**
   - Option A: `@pytest.mark.subsystem("protocol")` (parametrized, flexible)
   - Option B: `@pytest.mark.protocol_stack` (simple, one marker per subsystem)
   - **Recommendation:** Option A for consistency, Option B as shortcuts

2. **Handle tests spanning multiple subsystems?**
   - Example: Integration test for Protocol + NetSpace interaction
   - **Proposal:** Allow multiple markers: `@pytest.mark.subsystem("protocol")` + `@pytest.mark.subsystem("netspace")`
   - Running `pytest -m 'subsystem("protocol")'` includes multi-subsystem tests

3. **What if @jig annotation and marker disagree?**
   - **Proposal:** Tier 2 validation makes this a hard failure (test collection error)
   - Developer must fix (change marker or @jig annotation)
   - `@jig` annotation is canonical source of truth

4. **Should jigy be Python package or shell script?**
   - **Recommendation:** Python package (easier to test, better error handling, extensible)
   - Shell script acceptable for MVP

---

## Next Steps

1. **Review this proposal** (Jim approval)
2. **Implement Phase 1** (30 min work unit)
3. **Test with Protocol Stack** (verify 31 tests run)
4. **Document in JIG README** (link to this proposal)
5. **Plan Phase 2/3** (schedule in next sprint)

---

## References

- **JIG-Concept-v5.md** § 4 (Analysis Tools)
- **JIG_DECOMPOSITION_STRATEGY.md** § Subsystems
- **.jig/test_nodes.md** (current test catalog)
- **.jig/generated/test_index.json** (test metadata)
- **Pytest docs:** https://docs.pytest.org/en/stable/how-to/mark.html
