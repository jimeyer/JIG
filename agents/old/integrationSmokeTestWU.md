# Integration Smoke Test Work Unit

**Version:** 1.0.0
**Date:** 2025-12-18
**Status:** Proposal
**Related:** taskMakePLAN.md, taskDoWU.md, taskDoPLAN.md

## Problem Statement

When PLANs are decomposed into focused Work Units, sub-agents work effectively within their defined scope. Unit tests verify that individual components work correctly *when called*. However, this "boxed" approach can miss **wiring bugs** - cases where components are implemented correctly but never integrated into the system lifecycle.

### Pattern Observed

1. WU specifies creating a method/function
2. Sub-agent implements the method correctly
3. Sub-agent writes unit tests that call the method directly
4. Tests pass (method works when called)
5. But: method is never called in production code
6. Result: Feature appears complete but doesn't work

### Why This Happens

- **Focused scope is good**: Targeted WUs keep sub-agent context small and work predictable
- **Unit tests verify the box**: Tests prove components work in isolation
- **Integration points are implicit**: WU says "call X after Y" but doesn't verify the call exists
- **Mocking hides gaps**: Test mocks simulate the environment, bypassing real wiring

---

## Case Study: D037 SimOps Trace Routing

### What the PLAN Specified (WU1)

```markdown
**Goal**: Connect BikeStateCRDT and IGPHandler SimOps sinks to the SimOps
websocket so S-138 events reach the dump file.

**Implementation Notes**:
- Call `enable_simops(self._create_trace_sink())` after SimOps websocket connected
```

### What the Sub-Agent Delivered

1. Created `_create_trace_sink()` method - **correct**
2. Created `_wire_simops_sinks()` helper - **correct**
3. Wrote 8 unit tests - **all passed**

```python
# Test called the method directly
device._wire_simops_sinks()
assert device._bike_state._simops_sink is not None
```

### What Was Missing

Nobody added the lifecycle hook:

```python
async def connect_to_airspace(self) -> None:
    await super().connect_to_airspace()
    self._wire_simops_sinks()  # THIS LINE WAS MISSING
```

### How It Was Discovered

User ran the system manually:
```bash
ase bike dev
# Changed bike_name in GUI
ase monitor --simops
# Expected: trace messages
# Actual: only cli_marker messages, no trace
```

### Additional Bug Found

The sink also had a double-encoding bug:
```python
# Wrong: send_to_plane() does its own json.dumps()
self.plane_manager.send_to_plane('simops', json.dumps(envelope))

# Correct:
self.plane_manager.send_to_plane('simops', envelope)
```

This would have been caught by the same smoke test - trace messages would appear malformed or cause errors.

---

## Solution: Integration Smoke Test WU

Add a final Work Unit to every PLAN that tests the feature end-to-end using the actual system, not test harnesses.

### Template

```markdown
### Work Unit N: Integration Smoke Test

**Goal**: Verify end-to-end behavior matches user expectations using the
running system.

**Specs Addressed**: (all specs from this PLAN - integration verification)

**Acceptance Criteria**:
- [ ] System started using standard CLI commands
- [ ] User-level actions performed (not programmatic API calls)
- [ ] Expected outputs observed at system boundaries
- [ ] Any gaps found are fixed with regression tests added

**Success Gates** (all must pass):
- [ ] Manual verification produces expected observable output
- [ ] Any bugs found are fixed
- [ ] Regression tests added for bugs found
- [ ] jigy rebuild && jigy validate passes

**Escalation Triggers** (stop and ask human if):
- Expected output not observed after fix attempts
- Fix requires changes to FORBIDDEN bricks
- Unclear what "correct" output should look like

**Verification Steps**:
```bash
# 1. Start the system
<commands to start server/devices>

# 2. Perform user action
<description of what to do - GUI click, CLI command, etc>

# 3. Observe output
<command to check output - grep, cat, CLI query>

# 4. Expected result
<what should appear>
```

**Why This WU Exists**:
Unit tests verify components work in isolation with mocked dependencies.
This WU verifies components are actually wired together in the running
system and produce observable results at the boundaries users interact with.
```

### Example for D037

If D037 had included this WU:

```markdown
### Work Unit 7: Integration Smoke Test

**Goal**: Verify trace events flow from device to dump file.

**Verification Steps**:
```bash
# 1. Start system
ase server &
sleep 2
ase bike dev &
sleep 2

# 2. Perform user action
# In device GUI: change bike_name field

# 3. Observe output
ase monitor --simops | grep -c '"type": "trace"'
# OR
grep '"type": "trace"' logs/debug_simops.jsonl | head -3

# 4. Expected result
# Should see trace messages with:
# - type: "trace"
# - data.event: contains CRDT operation details
# - data.element: "bike_name"
```

**If No Trace Messages Appear**:
1. Check device logs for "SimOps trace sinks wired"
2. Verify _wire_simops_sinks() is called in device lifecycle
3. Check BikeStateCRDT._simops_sink is not None after connection
```

This would have immediately revealed:
1. No "SimOps trace sinks wired" log message
2. Investigation shows `_wire_simops_sinks()` never called
3. Fix: add lifecycle hook
4. Regression test: verify log message appears on device startup

---

## Characteristics of Good Smoke Test WUs

### DO

- **Use real CLI commands** - `ase server`, not `server.start()` in test
- **Perform user-level actions** - GUI interactions, CLI commands users would run
- **Check observable boundaries** - files on disk, CLI output, network traffic
- **Include "what to check if it fails"** - debugging guidance for sub-agent
- **Create regression tests for bugs found** - prevent recurrence

### DON'T

- **Don't use test harness** - pytest fixtures hide wiring issues
- **Don't mock dependencies** - mocks bypass the exact integration points we're testing
- **Don't check internal state** - check what users see, not implementation details
- **Don't skip if "unit tests pass"** - that's the whole point

---

## When to Include Integration Smoke Test WU

**Always include when:**
- Feature involves multiple components communicating
- Feature produces user-visible output (files, CLI, GUI)
- Feature involves lifecycle hooks or event wiring
- Feature spans multiple bricks

**May skip when:**
- Pure refactoring with no behavior change
- Documentation-only changes
- Single-function changes with comprehensive unit tests

---

## Integration with Orchestration Workflow

The orchestrator (taskDoPLAN.md) should:

1. Execute all implementation WUs first
2. Execute Integration Smoke Test WU last
3. If smoke test fails:
   - Sub-agent investigates and proposes fix
   - Fix is applied
   - Regression test added
   - Smoke test re-run
4. Only mark PLAN complete when smoke test passes

---

## Version History

- **1.0.0** (2025-12-18): Initial version based on D037 wiring bug analysis
