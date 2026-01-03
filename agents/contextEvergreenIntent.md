# Writing Outcomes and Specifications

**Purpose**: O and S nodes are EVERGREEN documentation of system behavior and value. They are NOT project management artifacts.

---

## Outcomes (O-*)

**What Outcomes Are:**
- Business value that persists after code is written
- WHY the system behaves a certain way
- User-facing or operational benefits
- Decompose into multiple specifications

**What Outcomes Are NOT:**
- Project goals ("achieve 90% test coverage")
- Work unit objectives ("add missing tests")
- Refactoring tasks ("reorganize code")
- Process improvements ("improve code organization")

### Pattern: Evergreen Value Statements

```markdown
---
id: O-001
type: outcome
specifies: [S-001, S-002, S-003]
---

# Secure Authentication Without Passwords

Users can authenticate securely without managing passwords or secrets.

**Value:** Reduces support burden (no password resets) and improves security.
```

**Test:** Remove all references to the work that created this outcome. Does it still make sense? If no, rewrite.

### Anti-Pattern: Project Goals as Outcomes

❌ **BAD:**
```markdown
# Test Coverage
Critical paths have comprehensive tests.
```
This describes a project state, not system value.

✓ **GOOD:**
```markdown
# System Reliability Through Verification
Critical system behaviors are verified to prevent regressions in production.

**Value:** Reduces customer-facing bugs and deployment risk.
```

### Anti-Pattern: Process Improvements as Outcomes

❌ **BAD:**
```markdown
# Code Organization
Related code co-located in correct bricks.
```
This describes code structure, not value.

✓ **GOOD:**
```markdown
# Clear Architectural Boundaries
Authentication logic is isolated from business logic, enabling independent modification.

**Value:** Reduces time to implement auth changes without breaking other systems.
```

---

## Specifications (S-*)

**What Specifications Are:**
- Observable system behavior
- Technical requirements that can be implemented and verified
- Contracts that code must satisfy
- Acceptance criteria that tests verify

**What Specifications Are NOT:**
- Refactoring tasks ("move file X to location Y")
- Implementation instructions ("use Redis for caching")
- Work units ("add decorators to functions")
- Code quality goals ("add missing specs")

### Pattern: Behavioral Requirements

```markdown
---
id: S-001
type: specification
---

# Token Expiration

Authentication tokens MUST expire after 15 minutes of inactivity.

**Acceptance Criteria:**
- Token created with expires_at = now() + 15 minutes
- Any operation updates last_activity timestamp
- Token rejected if now() > last_activity + 15 minutes

**Rationale:** Limits exposure window if token is compromised.
```

**Test:** Can you write `@jig.implements("S-001")` on code? Can you write `@jig.verifies("S-001")` on tests? If no, rewrite.

### Anti-Pattern: Refactoring Tasks as Specs

❌ **BAD:**
```markdown
# Relocate era_persistence
era_persistence.py moved from utils to protocol-core where EraLamportClock is defined.
```
This describes a file move, not behavior.

✓ **GOOD:**
```markdown
# EraLamportClock Persistence
EraLamportClock state persists across process restarts without clock regression.

**Acceptance Criteria:**
- get_era() returns last saved era + 1 on process start
- save_era() writes era to persistent storage
- Clock never returns same timestamp after restart

**Rationale:** Ensures causal consistency in distributed system.
```

### Anti-Pattern: Implementation Details as Specs

❌ **BAD:**
```markdown
# Airspace-crdt Functions Have Decorators
add_device(), remove_device(), and update_device_element() have @jig.implements decorators.
```
This describes tooling, not requirements.

✓ **GOOD:**
```markdown
# Airspace Device Lifecycle
Devices can be added, removed, and updated in shared airspace CRDT.

**Acceptance Criteria:**
- add_device(id, metadata) creates device entry with vector clock
- remove_device(id) tombstones device, preserves history
- update_device_element(id, key, value) merges updates LWW
- Operations are commutative and idempotent

**Rationale:** Enables conflict-free replication across multiple clients.
```

### Anti-Pattern: Meta-Specifications

❌ **BAD:**
```markdown
# Specification Completeness
All public APIs have specifications.
```
This describes documentation goals, not system behavior.

✓ **GOOD:**
```markdown
# Catalog Query Interface Contracts
DataDictionaryCatalog provides deterministic query results for device metadata.

**Acceptance Criteria:**
- get_data_element(id) returns element or None, never throws
- get_gui_metadata(id) returns display info or default values
- get_data_elements_for_device(device_id) returns sorted list
- Query results consistent across repeated calls with same DB state

**Rationale:** GUI and device layers depend on stable query interface.
```

---

## Quick Reference

### Outcomes Checklist
- [ ] Describes business value, not project state
- [ ] Remains true after project completes
- [ ] Explains WHY system behaves this way
- [ ] Would make sense to new developer in 2 years

### Specifications Checklist
- [ ] Describes HOW system behaves, not HOW TO BUILD
- [ ] Has observable acceptance criteria
- [ ] Can be implemented by code (`@jig.implements`)
- [ ] Can be verified by tests (`@jig.verifies`)
- [ ] Avoids file paths, implementation details, refactoring tasks

---

## Converting Work Units to O/S Nodes

**Work Unit:** "WU3: Add ELC Persistence Tests"

❌ **BAD Spec:**
```
S-078: EraLamportClock persistence tested per S-036
```

✓ **GOOD Spec (already exists):**
```
S-036: EraLamportClock Persistence [already defined]
```

**Action:** Reference existing spec in work unit. If no spec exists, CREATE the spec that describes the behavior, then write tests for it.

---

**Work Unit:** "WU8: Consolidate GUI Location"

❌ **BAD Outcome:**
```
O-024: Code Organization - Related code co-located in correct bricks
```

✓ **GOOD Outcome:**
```
O-024: Modular GUI Components
GUI components are independently testable and reusable across different device types.

**Value:** Reduces time to add new device UI from days to hours.
```

✓ **GOOD Spec:**
```
S-083: GUI Component Package Structure
All GUI components reside in ase.gui.* package with clear public API.

**Acceptance Criteria:**
- ase.gui.widgets exports all widget factories
- ase.gui.themes provides theme system
- ase.gui.layouts provides layout managers
- No GUI code exists outside ase.gui.*

**Rationale:** Enables GUI testing without device process dependencies.
```

---

## Summary

**Outcomes** = Evergreen business value
**Specifications** = Evergreen behavioral requirements
**Work Units** = Temporary project tasks (NOT O/S nodes)

Write O/S nodes that will be true FOREVER, not just until the PR merges.
