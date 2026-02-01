---
title: "JIG Decomposition Strategy for ASE"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1763493911
created_human: "2025-11-18 13:25 CST"
parent: "[[J001_JIG-Concept-v4]]"
children: []
---
# JIG Decomposition Strategy for ASE

**Date:** 2025-11-13
**Purpose:** Define subsystem boundaries for incremental JIG adoption
**Based on:** Herbert Simon's "Nearly Decomposable Systems" principle
**Goal:** Create intent graph that mirrors architectural boundaries

---

## Executive Summary

ASE already exhibits **near-decomposable structure**. The codebase has:
- **5-layer protocol stack** (documented)
- **4 independent data planes** (MP_CONTRACT.md)
- **Zero circular dependencies** at module level
- **Clear architectural seams**

**Strategy:** Extract and document the existing structure via JIG, don't impose new boundaries.

**Approach:** Start with foundation (Protocol Stack), build outward in dependency order.

---

## 1. Core Principle: Deep Modules

> "The best modules are those whose interfaces are much simpler than their implementations."
> — John Ousterhout, *A Philosophy of Software Design*

**Deep Module Characteristics:**
- High internal complexity
- Minimal surface area (few exports)
- Clear interface contract
- Information hiding (implementation details opaque)

**ASE Deep Modules:**

| Module | LOC | Exports | Ratio | Quality |
|--------|-----|---------|-------|---------|
| device_process | 5109 | 2 | 2554:1 | Excellent |
| netspace | 1529 | 1 | 1529:1 | Excellent |
| config | 4412 | 7 | 630:1 | Good |
| catalog | 1765 | 6 | 294:1 | Good |
| protocol | 989 | 7 | 141:1 | Good |

**JIG Strategy:** Each deep module becomes a JIG subsystem with outcomes/specs focused on interface contracts, not implementation details.

---

## 2. Nearly Decomposable Systems (Herbert Simon)

### Simon's Criteria for Near-Decomposability:

1. **Intra-subsystem coupling >> Inter-subsystem coupling**
2. **Clear interface boundaries**
3. **Independent evolvability**
4. **Testable in isolation**

### ASE Assessment:

#### ✅ **Criterion 1: Coupling Ratios**

**Excellent:**
```
Protocol Stack:
  Internal: protocol ↔ transport ↔ codecs (tight coupling)
  External: 0 efferent dependencies
  Ratio: ∞ (pure foundation)

NetSpace Sync:
  Internal: netspace ↔ gateway ↔ airspace (shared CRDTs)
  External: protocol only (read-only)
  Ratio: ~10:1
```

**Metrics:**
- Max efferent coupling: 2 dependencies
- Max afferent coupling: 3 dependents (protocol)
- Circular dependencies: NONE

#### ✅ **Criterion 2: Interface Boundaries**

**Well-defined:**
- Transport: `@runtime_checkable` Protocol (4 methods)
- PDUCodec: Protocol (2 methods: encode/decode)
- Router: Pure function (deterministic routing)
- MP_CONTRACT.md: Documented plane semantics

#### ✅ **Criterion 3: Evolvability**

**Evidence:**
- Can add BLE transport without touching protocol layer
- Can add Protobuf codec without changing PDU structure
- NetSpace changes don't cascade to Airspace
- Gateway aggregation independent of CRDT primitives

#### ⚠️ **Criterion 4: Testable in Isolation**

**Status:**
- Protocol/Transport: ✅ Excellent (contract tests, mocks)
- Multi-plane Server: ✅ Good (8 contract tests)
- NetSpace Sync: ⚠️ Partial (unit tests exist, integration gaps)
- Device Simulation: ❌ Weak (scattered tests)
- Configuration: ❌ Weak (no centralized contract tests)

**JIG Focus:** Fill test gaps as we document contracts.

---

## 3. Proposed Subsystem Structure

**7 Subsystems (in dependency order):**
1. Protocol Stack - Foundation (0 dependencies)
2. Multi-Plane Server - Infrastructure (depends: Protocol)
3. NetSpace Sync - CRDT Replication (depends: Protocol, Multi-Plane)
4. Configuration - Cross-cutting (stable utilities)
5A. Device Simulation Infrastructure - Application platform (depends: all above)
5B. Device Behaviors - Domain logic (depends: 5A)
6. CLI/UI - User interface (optional)

**Key Insight:** Separating Device Infrastructure (5A) from Device Behaviors (5B) allows:
- Infrastructure to stabilize as framework
- Behaviors to evolve with product requirements
- Clear boundary between "how we simulate" vs "what devices do"

---

### Subsystem 1: **Protocol Stack** (Foundation)

**Modules:** `protocol/`, `transport/`, `protocol/codecs/`

**What it does:** Implements Layers 1-3 of message taxonomy
- Layer 1: Transport (WebSocket, Mock)
- Layer 2: Codec (JSON, Passthrough)
- Layer 3: Protocol (ELC, QoS, Flags, Message, PDU)

**Why it's a subsystem:**
- Zero efferent dependencies (pure foundation)
- High afferent coupling (3 modules depend on it)
- Clean separation of concerns (layers)
- Documented in MESSAGE_LAYER_TAXONOMY.md

**Interface (7 exports):**
```python
# protocol/__init__.py
- ELCTimestamp, EraLamportClock  # Distributed timestamps
- QoSClass, Flags                # Message metadata
- Message, ProtocolPDU           # Layer 3/4 abstractions
- MessageContext                 # Contextual info

# transport/__init__.py
- Transport                      # Protocol interface
- MockTransport, WebSocketTransport

# protocol/codecs/__init__.py
- PDUCodec                       # Codec protocol
- JSONPDUCodec, PassthroughPDUCodec
```

**Complexity:** 989 LOC, 13 classes
**Surface:** 11 exports
**Ratio:** 90 LOC per export (deep!)

**Current tests:**
- `test/protocol/`: 7 tests (ELC, QoS, PDU, Message)
- `test/transport/`: 3 tests (MockTransport, WebSocketTransport)
- `test/lint/test_layer_isolation.py`: 1 architectural test

**Test gaps:**
- Codec contract tests (roundtrip encode/decode)
- Cross-codec compatibility
- Layer boundary enforcement

**JIG scope (Outcomes → Specs → Tests → Code):**

**Outcomes:**
- O-PS-001: Deterministic message ordering across distributed devices
- O-PS-002: Type-safe message encoding without data loss
- O-PS-003: Pluggable transport layer for multi-protocol support
- O-PS-004: Layer isolation prevents abstraction leakage

**Specifications (examples):**
- S-PS-001: EraLamportClock provides total ordering of events
- S-PS-002: QoS classes (EPHEMERAL, NORMAL, PRIORITY) control delivery
- S-PS-003: ProtocolPDU wraps Message with routing metadata
- S-PS-004: Codecs satisfy roundtrip encode/decode invariant
- S-PS-005: Transport implements connect/disconnect/send/receive contract
- S-PS-006: Layer N only depends on Layer N-1 (no skipping)

**Why start here:**
1. **Zero external dependencies** → Easiest to document in isolation
2. **Foundation for all communication** → High leverage
3. **Well-designed** → Clean interfaces already exist
4. **Stable** → Low change frequency (0.00 stability metric)

---

### Subsystem 2: **Multi-Plane Server** (Infrastructure)

**Modules:** `ase_server/`, `process_manager/`

**What it does:** Orchestrates 4 independent WebSocket servers with routing
- AirspacePlane: RF broadcast simulation
- MeatSpacePlane: Physical action simulation
- NetSpacePlane: TCP/IP gateway sync
- SimOpsPlane: Diagnostic backchannel

**Why it's a subsystem:**
- Clear contract (MP_CONTRACT.md already exists!)
- Well-tested (8 contract tests)
- Independent plane semantics
- Process lifecycle management

**Interface (12 exports):**
```python
# ase_server/__init__.py
- ASEServer                      # Main orchestrator
- BasePlane                      # Abstract plane
- AirspacePlane, MeatSpacePlane, NetSpacePlane, SimOpsPlane
- RoutingEnvelope               # Layer 2.5 abstraction
- Router                        # Deterministic routing
- invariants                    # Runtime checks

# process_manager/__init__.py
- DeviceProcessManager          # Lifecycle manager
- DeviceProcessInfo             # Process metadata
```

**Complexity:** 1843 LOC, 13 classes
**Surface:** 12 exports
**Ratio:** 154 LOC per export

**Dependencies:**
- Efferent: `protocol` (for PDU/Message)
- Afferent: `device_process` (clients)

**Current tests:**
- `test/contract/`: 8 tests covering:
  - Server lifecycle
  - Routing correctness (all planes)
  - Backpressure handling
  - Connection management
  - Observability (debug dumps)

**Test gaps:**
- Process manager lifecycle tests
- Multi-process failure scenarios
- Resource cleanup verification

**JIG scope:**

**Outcomes:**
- O-MPS-001: Deterministic routing prevents message leakage between planes
- O-MPS-002: Backpressure protects server from slow clients
- O-MPS-003: Process isolation prevents cascade failures
- O-MPS-004: Diagnostic observability for all plane traffic

**Specifications (examples):**
- S-MPS-001: AirspacePlane broadcasts to all connected devices
- S-MPS-002: NetSpacePlane routes targeted messages (source + target only)
- S-MPS-003: SimOpsPlane routing is conditional (broadcast or targeted)
- S-MPS-004: Router is pure function (same input → same output)
- S-MPS-005: Backpressure drops messages when client queue full
- S-MPS-006: Debug dumps capture all envelopes (per plane, rotating logs)
- S-MPS-007: Process manager spawns devices in isolated process groups
- S-MPS-008: Graceful shutdown sends SimOps message before SIGKILL

**Why second:**
1. **MP_CONTRACT.md already documents intent** → Specs partially written
2. **Strong test coverage** → Good baseline
3. **Depends only on Protocol Stack** → Safe to document after foundation
4. **High architectural value** → Core abstraction

---

### Subsystem 3: **NetSpace Sync** (CRDT Replication)

**Modules:** `netspace/`, `airspace/`, `gateway/`

**What it does:** Conflict-free state replication between gateways
- Gateway: Aggregates device broadcasts into BikeEchoform
- Replicator: Syncs echoforms via CRDT operations
- Mode detection: Edge (has airspace) vs Hub (no airspace)
- Anti-entropy: Cold-start recovery

**Why it's a subsystem:**
- Clear data flow: AirSpace → Gateway → NetSpace
- Shared CRDT primitives (LWW, OR-Set, PN-Counter)
- Independent of device logic
- Well-documented CRDT semantics

**Interface (6 exports):**
```python
# netspace/replicator/__init__.py
- BikeEchoformReplicator         # Edge ↔ Hub sync

# gateway/__init__.py
- BikeEchoform                   # Temporal aggregation
- DeviceData                     # Device contribution
- BikeEchoformCache              # Multi-bike tracking

# airspace/crdt/__init__.py
- ELCTimestamp, EraLamportClock  # (re-export from protocol)
```

**Complexity:** 2216 LOC, 12 classes
**Surface:** 6 exports
**Ratio:** 369 LOC per export (very deep!)

**Dependencies:**
- Efferent: `protocol` (ELC), `netspace/crdt/` (primitives)
- Afferent: `device_process` (gateway devices)

**Current tests:**
- `test/netspace/`: 9 tests (CRDT ops, replicator modes)
- `test/airspace/`: 7 tests (bike state, boot sequence, late joiners)
- `test/gateway/`: 1 test (basic aggregation)

**Test gaps:**
- End-to-end pipeline: AirSpace broadcast → Gateway aggregation → NetSpace sync
- Merge conflict scenarios (concurrent updates)
- Anti-entropy verification (cold-start recovery)
- Throttled batching behavior (1000ms window)

**JIG scope:**

**Outcomes:**
- O-NS-001: Gateways converge to consistent bike state without coordination
- O-NS-002: BikeEchoform embraces incompleteness (temporal aggregation)
- O-NS-003: Anti-entropy recovers from cold starts and missed messages
- O-NS-004: Mode detection adapts to network topology (edge vs hub)

**Specifications (examples):**
- S-NS-001: LWW-Register resolves conflicts via timestamp (last-write-wins)
- S-NS-002: OR-Set adds/removes elements with unique tags
- S-NS-003: PN-Counter supports increment/decrement without coordination
- S-NS-004: BikeEchoform stores (value, received_at) per element
- S-NS-005: Gateway aggregates state_broadcast messages by bike_id
- S-NS-006: Edge mode: listen Airspace → send NetSpace (hub target)
- S-NS-007: Hub mode: receive NetSpace → broadcast to all peers
- S-NS-008: Throttled batching: 1000ms window, accumulate then flush
- S-NS-009: Anti-entropy: push full state on device_announce

**Why third:**
1. **Complex semantics** → Needs clear specification
2. **Integration gaps** → Tests will drive spec clarity
3. **Depends on Protocol + Multi-Plane** → Must wait for foundation
4. **High business value** → Gateway sync is critical feature

---

### Subsystem 4: **Configuration** (Cross-cutting)

**Modules:** `config/`, `utils/`

**What it does:** YAML-driven device definition and schema validation
- Device kind inheritance (device_kind → device)
- Type-specific merge strategies (Type A lists, Type B scalars)
- Schema validation
- Configuration monitoring

**Why it's a subsystem:**
- Cross-cutting concern (affects all subsystems)
- Complex inheritance semantics
- Pure utilities (no domain logic)
- High surface area but clear contracts

**Interface (9 exports):**
```python
# config/__init__.py
- ConfigurationMonitor           # Load-time monitoring
- monitor_configuration_loading  # Decorator
- monitor_validation             # Decorator
- get_configuration_health       # Health check
- log_configuration_summary      # Logging

# utils/__init__.py
- get_package_path               # Path resolution
- validate_file_path             # Path validation
```

**Complexity:** 5039 LOC, 23 classes
**Surface:** 9 exports
**Ratio:** 560 LOC per export

**Dependencies:**
- Efferent: None (pure utilities)
- Afferent: All application modules

**Current tests:**
- Scattered: `test_config_loader.py`, `test_unified_config_loader.py`, etc.
- No centralized contract tests

**Test gaps:**
- Inheritance edge cases (circular dependencies, conflicting overrides)
- Schema validation error messages
- Configuration monitoring hooks
- Hot reload behavior

**JIG scope:**

**Outcomes:**
- O-CFG-001: Zero-code device creation via YAML configuration
- O-CFG-002: DRY device definitions through inheritance
- O-CFG-003: Type-safe schema validation prevents runtime errors
- O-CFG-004: Configuration monitoring enables observability

**Specifications (examples):**
- S-CFG-001: Device inherits from device_kind with merge semantics
- S-CFG-002: Type A merge (lists): device extends kind's list
- S-CFG-003: Type B override (scalars): device wins over kind
- S-CFG-004: Deep merge (dicts): recursive key-by-key merge
- S-CFG-005: Schema validation enforces required fields
- S-CFG-006: Monitoring decorators log load/validation events
- S-CFG-007: Configuration health check exposes metrics

**Why fourth:**
1. **Cross-cutting** → Easier after subsystems are defined
2. **High test debt** → JIG will force consolidation
3. **Independent of runtime** → Can document separately
4. **High leverage** → Affects all subsystems

---

### Subsystem 5A: **Device Simulation Infrastructure** (Application Platform)

**Modules:** `device_process/` (infrastructure parts), `core/`, `catalog/`

**What it does:** Provides the mechanics to run any simulated device
- Device process lifecycle (spawn, connect, event loop, shutdown)
- Catalog-driven GUI rendering
- Data element management (state storage, validation)
- Plane connection management (WebSocket multiplexing)
- Message send/receive plumbing

**Why it's a subsystem:**
- Pure infrastructure (generic across all 14 device types)
- High internal complexity (5109 LOC!)
- Clear interface (2 exports: DeviceProcess, DeviceConfig)
- Zero device-specific logic (all 14 production devices use GenericDevice)

**Interface (11 exports):**
```python
# device_process/__init__.py
- DeviceProcess                  # Main process class (base)
- DeviceConfig                   # Configuration

# core/__init__.py
- Device, DeviceClass            # Device abstractions
- SimpleDeviceParser             # Config parser

# catalog/__init__.py
- DataDictionaryCatalog          # SRAM Data Dictionary
- get_catalog, reset_catalog     # Singleton access
- DataElementWidgetFactory       # GUI widgets
- DataElementRowManager          # GUI rows
```

**Complexity:** 9096 LOC, 42 classes
**Surface:** 11 exports
**Ratio:** 827 LOC per export (very deep!)

**Dependencies:**
- Efferent: `ase_server`, `utils`, `ui`, `protocol`
- Afferent: Device Behaviors (extension via subclass/config)

**Current tests:**
- `test/unit/`: 6 tests (catalog, widget factory)
- Scattered: device lifecycle, config integration

**Test gaps:**
- Device lifecycle state transitions
- Catalog-driven GUI rendering end-to-end
- Data element validation
- PlaneConnectionManager connection handling

**JIG scope:**

**Outcomes:**
- O-DSIM-001: Catalog-driven GUI eliminates hardcoded state
- O-DSIM-002: Device process isolation prevents cascade failures
- O-DSIM-003: Data element schema ensures type safety
- O-DSIM-004: Generic infrastructure supports any device type

**Specifications (examples):**
- S-DSIM-001: DeviceProcess lifecycle (init → connect → run → cleanup)
- S-DSIM-002: Catalog state manager provides O(1) type-safe access
- S-DSIM-003: GUI widgets auto-generated from data_refs in YAML
- S-DSIM-004: Data element changes emit events → GUI updates
- S-DSIM-005: PlaneConnectionManager handles multi-plane WebSocket connections
- S-DSIM-006: Message send/receive abstracts codec details (JSON/CBOR)
- S-DSIM-007: Configuration inheritance (device_kind → device)

**Why fifth:**
1. **Pure infrastructure** → Independent of device domain logic
2. **Stable** → Changes infrequently (foundation for behaviors)
3. **High leverage** → Supports all 14 device types
4. **Top of dependency graph** → Depends on all lower subsystems

---

### Subsystem 5B: **Device Behaviors** (Domain Logic)

**Modules:** `device_process/devices/` (behavior implementations), YAML config (`axs-devices.yaml`)

**What it does:** Defines what AXS components DO in response to events
- Power state transitions (RUN → STANDBY → SLEEP → OFF)
- Button press responses (wake device, shift gear, calibrate, etc.)
- Internal state updates (gear position, battery drain, etc.)
- Event generation (periodic broadcasts, state changes)
- Device-specific logic (shifter ≠ derailleur ≠ power meter)

**Why it's a separate subsystem:**
- **Domain logic, not infrastructure** → What real AXS devices do
- **Device-specific** → Shifter behavior ≠ derailleur behavior
- **Future growth area** → Minimal now, will expand significantly
- **Different change drivers** → Product requirements, not architecture

**Current State (Minimal):**
- Generic behaviors: Auto-transitions (YAML-driven), button wake, periodic broadcasts
- All 14 production devices use GenericDevice (no custom behaviors)
- Extension points exist but unused (override hooks)

**Future State (Rich):**
- Device-specific responses: Shifter button → change gear, derailleur → execute shift
- State machines: Calibration sequences, pairing flows
- Reactive behaviors: Respond to AirSpace messages (button presses from controllers)
- Battery simulation: Drain over time, charging states
- Error conditions: Out of range, mechanical failures

**Interface (Current):**
```python
# device_process/devices/__init__.py
- GenericDevice                  # Base implementation (all 14 devices use this)

# Extension Points (for future behaviors):
- _init_device_behavior()        # Set behavior flags
- handle_airspace_message()      # React to AirSpace events
- update_device_behavior()       # Periodic behavior updates
- _handle_button_press()         # Override button response
```

**Complexity (Current):** ~500 LOC (generic behaviors only)
**Complexity (Future):** Could grow to 2000+ LOC as behaviors expand

**Dependencies:**
- Efferent: Device Simulation Infrastructure (uses DeviceProcess, catalog)
- Afferent: None (top of graph)

**Current behaviors (YAML-driven):**
```yaml
# axs-devices.yaml
auto_transitions:              # Power state transitions
  - from: RUN, to: STANDBY, after: 300s
  - from: STANDBY, to: SLEEP, after: 10s

broadcast_config:              # Periodic state broadcasts
  enabled: true
  run_period: 5000ms
  standby_period: 30000ms

button_reactions:              # Button press responses
  # Currently: wake to RUN (generic)
  # Future: shift_up, shift_down, calibrate, etc.
```

**Current tests:**
- Generic behavior tests scattered
- **Major gap:** No device-specific behavior tests (because no behaviors exist yet)

**Test gaps (Future):**
- Power state transition sequences
- Button press → gear change (shifter)
- AirSpace message → shift execution (derailleur)
- Battery drain simulation
- Calibration sequences

**JIG scope:**

**Outcomes:**
- O-DBEH-001: Power state transitions simulate realistic RF behavior
- O-DBEH-002: Button press responses match real AXS component behavior
- O-DBEH-003: Device state machines model product specifications
- O-DBEH-004: AirSpace message handling enables component interaction

**Specifications (examples):**
- S-DBEH-001: Power states: RUN (radio active), SLEEP (radio off), OFF (no comms)
- S-DBEH-002: SLEEP/OFF disable Airspace/MeatSpace, SimOps always active
- S-DBEH-003: Auto-transitions: RUN → STANDBY (300s) → SLEEP (10s)
- S-DBEH-004: Button wake: any button press → RUN (if configured)
- S-DBEH-005: Shifter button press: shift_up → increment current_gear (clamped to max)
- S-DBEH-006: Derailleur hears shift command → execute gear change
- S-DBEH-007: Periodic broadcasts send state_broadcast at configured intervals
- S-DBEH-008: Battery simulation: drain over time based on power state

**Why fifth (separate from infrastructure):**
1. **Different concern** → What devices do (domain) vs how simulation works (infrastructure)
2. **Different change frequency** → Behaviors change with product requirements
3. **Device-specific** → Each device type has unique behavior specs
4. **Future growth** → Minimal now (generic only), will expand significantly

---

**Critical Distinction:**

| Aspect | Device Simulation Infrastructure | Device Behaviors |
|--------|----------------------------------|------------------|
| **Question** | How do we simulate a device? | What does this device do? |
| **Scope** | Generic (all devices) | Device-specific (shifter ≠ derailleur) |
| **Change Driver** | Architecture, framework | Product requirements, AXS specs |
| **Complexity** | High (5109 LOC) | Low now, high future |
| **Stability** | Stable (foundation) | Volatile (product evolution) |
| **Examples** | Process lifecycle, GUI, catalog, WebSocket | Button → shift, power transitions, broadcasts |
| **Test Focus** | Infrastructure works correctly | Behavior matches AXS component spec |

---

### Subsystem 6: **CLI/UI** (Interface)

**Modules:** `cli/`, `ui/`

**What it does:** Command-line interface and UI helpers
- CLI commands (list, show, create)
- UI fonts and helpers
- User interaction layer

**Interface (6 exports):**
```python
# cli/__init__.py
- list_devices, list_bikes       # Discovery
- show_config, create_config_file # Config management

# ui/__init__.py
- ui_fonts, ui_helpers           # UI utilities
```

**Complexity:** 2315 LOC
**Surface:** 6 exports
**Ratio:** 386 LOC per export

**Dependencies:**
- Efferent: `config`, `core`, `catalog`
- Afferent: None (top of graph)

**Current tests:**
- `test_cli.py`, `test_cli_debug.py`, `test_ui_framework.py`

**JIG scope:**
- CLI command contracts
- UI rendering patterns
- Error message clarity

**Why last (or skip):**
1. **Thin layer** → Low architectural value
2. **Frequently changing** → High maintenance
3. **User-facing** → Specs are obvious (commands do what they say)
4. **Low risk** → Errors are visible immediately

---

## 4. Dependency Order for JIG Adoption

```
┌─────────────────────┐
│ 1. Protocol Stack   │  (0 dependencies)
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ 2. Multi-Plane      │  (depends: Protocol)
│    Server           │
└──────────┬──────────┘
           │
    ┏━━━━━━▼━━━━━━┓
    ┃ 3. NetSpace ┃  (depends: Protocol, Multi-Plane)
    ┃    Sync     ┃
    ┗━━━━━━┬━━━━━━┛
           │
    ┌──────▼───────┐
    │ 4. Config    │  (cross-cutting, stable)
    └──────┬───────┘
           │
    ┌──────▼───────────────┐
    │ 5A. Device Sim       │  (depends: all above)
    │     Infrastructure   │  (process, GUI, catalog)
    └──────┬───────────────┘
           │
    ┌──────▼───────────────┐
    │ 5B. Device Behaviors │  (depends: 5A)
    │     (Domain Logic)   │  (power, buttons, state machines)
    └──────┬───────────────┘
           │
    ┌──────▼───────┐
    │ 6. CLI/UI    │  (user interface)
    └──────────────┘
```

**Rationale:** Start with foundation, build up dependency tree. Each subsystem is fully documented before dependents.

**Key Split:** Subsystems 5A and 5B separate infrastructure (how we simulate) from domain logic (what devices do). This allows:
- Infrastructure to stabilize independently
- Behavior specs to evolve with product requirements
- Clear distinction between framework and application

---

## 5. JIG Structure Per Subsystem

Each subsystem will have:

```
.jig/
├── outcomes/
│   ├── O-PS-001.md      # Protocol Stack outcomes
│   ├── O-MPS-001.md     # Multi-Plane Server outcomes
│   ├── O-NS-001.md      # NetSpace Sync outcomes
│   ├── O-CFG-001.md     # Configuration outcomes
│   └── O-DEV-001.md     # Device Simulation outcomes
├── specifications/
│   ├── S-PS-001.md      # Protocol Stack specs
│   ├── S-MPS-001.md     # Multi-Plane Server specs
│   ├── S-NS-001.md      # NetSpace Sync specs
│   ├── S-CFG-001.md     # Configuration specs
│   └── S-DEV-001.md     # Device Simulation specs
└── generated/
    ├── code_index.json  # Generated by jigy scan
    ├── test_index.json  # Generated by jigy scan
    └── graph.json       # Generated by jigy scan
```

**Naming Convention:**
- Outcomes: `O-<SUBSYSTEM>-NNN`
- Specifications: `S-<SUBSYSTEM>-NNN`
- Tests: `T-<SUBSYSTEM>-NNN`
- Code: `C-<SUBSYSTEM>-NNN`

**Subsystem Prefixes:**
- `PS`: Protocol Stack
- `MPS`: Multi-Plane Server
- `NS`: NetSpace Sync
- `CFG`: Configuration
- `DSIM`: Device Simulation Infrastructure
- `DBEH`: Device Behaviors
- `CLI`: CLI/UI

---

## 6. Adoption Phases

### Phase 1: Foundation (Weeks 1-2)
**Target:** Protocol Stack JIG

**Activities:**
1. Create outcomes (4-6 O-PS-* files)
2. Create specifications (10-15 S-PS-* files)
3. Add `@jig` annotations to protocol/, transport/, protocol/codecs/
4. Run `jigy scan` to generate indices
5. Fill test gaps (codec contracts, layer isolation)
6. Validate alignment (`jigy validate`)

**Deliverables:**
- `.jig/outcomes/O-PS-*.md` (4-6 files)
- `.jig/specifications/S-PS-*.md` (10-15 files)
- Annotated code (protocol/, transport/)
- Updated tests (test/protocol/, test/transport/)
- Generated graph (`.jig/generated/graph.json`)

**Success Criteria:**
- Alignment index ≥ 0.90
- All protocol exports linked to specs
- All specs have tests
- Layer isolation enforced

---

### Phase 2: Infrastructure (Weeks 3-4)
**Target:** Multi-Plane Server JIG

**Activities:**
1. Extract outcomes from MP_CONTRACT.md (already documented!)
2. Create specifications from contract (routing, backpressure, lifecycle)
3. Add `@jig` annotations to ase_server/, process_manager/
4. Run `jigy scan` to update indices
5. Fill test gaps (process manager lifecycle)
6. Validate alignment

**Deliverables:**
- `.jig/outcomes/O-MPS-*.md` (4-6 files)
- `.jig/specifications/S-MPS-*.md` (8-12 files)
- Annotated code (ase_server/)
- Updated tests (test/contract/)

**Success Criteria:**
- Alignment index ≥ 0.90
- MP_CONTRACT fully mapped to JIG
- All routing semantics tested
- Process lifecycle verified

---

### Phase 3: Replication (Weeks 5-6)
**Target:** NetSpace Sync JIG

**Activities:**
1. Document CRDT semantics as outcomes
2. Create specifications for replication modes
3. Add `@jig` annotations to netspace/, airspace/, gateway/
4. Run `jigy scan` to update indices
5. Fill test gaps (end-to-end pipeline, anti-entropy)
6. Validate alignment

**Deliverables:**
- `.jig/outcomes/O-NS-*.md` (4-6 files)
- `.jig/specifications/S-NS-*.md` (10-15 files)
- Annotated code (netspace/, gateway/)
- New integration tests (test/integration/)

**Success Criteria:**
- Alignment index ≥ 0.85 (complex semantics)
- CRDT merge rules tested
- End-to-end pipeline verified
- Anti-entropy recovery tested

---

### Phase 4: Configuration (Weeks 7-8)
**Target:** Configuration JIG

**Activities:**
1. Document configuration as business value (zero-code devices)
2. Create specifications for inheritance, validation
3. Add `@jig` annotations to config/
4. Consolidate scattered config tests
5. Run `jigy scan` to update indices
6. Validate alignment

**Deliverables:**
- `.jig/outcomes/O-CFG-*.md` (3-5 files)
- `.jig/specifications/S-CFG-*.md` (8-10 files)
- Annotated code (config/)
- Consolidated tests (test/config/)

**Success Criteria:**
- Alignment index ≥ 0.90
- Inheritance edge cases tested
- Schema validation verified
- Configuration monitoring functional

---

### Phase 5A: Device Simulation Infrastructure (Weeks 9-11)
**Target:** Device Infrastructure JIG

**Activities:**
1. Document infrastructure as outcomes (process, GUI, catalog)
2. Create specifications for lifecycle, rendering, connections
3. Add `@jig` annotations to device_process/ (infrastructure), core/, catalog/
4. Fill test gaps (lifecycle, GUI end-to-end)
5. Run `jigy scan` to update indices
6. Validate alignment

**Deliverables:**
- `.jig/outcomes/O-DSIM-*.md` (4-6 files)
- `.jig/specifications/S-DSIM-*.md` (10-15 files)
- Annotated code (device_process/, core/, catalog/)
- New tests (test/device_process/, test/catalog/)

**Success Criteria:**
- Alignment index ≥ 0.85 (infrastructure)
- Device lifecycle fully tested
- Catalog rendering verified
- PlaneConnectionManager validated

---

### Phase 5B: Device Behaviors (Weeks 12-14)
**Target:** Device Behavior JIG

**Activities:**
1. Document device behaviors as outcomes (power, buttons, state machines)
2. Create specifications for generic + device-specific behaviors
3. Add `@jig` annotations to device_process/devices/
4. Fill test gaps (power transitions, button responses)
5. Run `jigy scan` to update indices
6. Validate alignment

**Deliverables:**
- `.jig/outcomes/O-DBEH-*.md` (4-6 files)
- `.jig/specifications/S-DBEH-*.md` (8-12 files)
- Annotated code (device_process/devices/)
- New tests (test/behaviors/)

**Success Criteria:**
- Alignment index ≥ 0.80 (behaviors evolving)
- Power state transitions fully tested
- Generic behaviors (wake, broadcast) validated
- Extension points documented for future device-specific behaviors

---

### Phase 6: Interface (Weeks 15-16, Optional)
**Target:** CLI/UI JIG

**Activities:**
1. Document CLI commands as outcomes
2. Create specifications for command contracts
3. Add `@jig` annotations to cli/
4. Validate alignment

**Deliverables:**
- `.jig/outcomes/O-CLI-*.md` (2-4 files)
- `.jig/specifications/S-CLI-*.md` (5-8 files)
- Annotated code (cli/)

**Success Criteria:**
- Alignment index ≥ 0.85
- CLI commands tested
- Error messages verified

---

## 7. Nearly Decomposable Graph Validation

After each phase, validate near-decomposability:

### Metric 1: Coupling Ratio
```bash
jigy graph --layer O --format json | jq '.edges[] | select(.type == "satisfies")'
```

**Target:** Intra-subsystem edges >> Inter-subsystem edges
- Protocol Stack: 100% internal (0 dependencies)
- Multi-Plane Server: >90% internal (depends only on Protocol)
- NetSpace Sync: >80% internal (depends on Protocol + Multi-Plane)

### Metric 2: Interface Stability
```bash
jigy show C-PS-* --edges | grep "implements"
```

**Target:** All exports mapped to specifications
- Protocol Stack: 11 exports → 11 C nodes → 15 S nodes (specs)
- Multi-Plane Server: 12 exports → 12 C nodes → 20 S nodes

### Metric 3: Test Coverage
```bash
jigy coverage --type specs --threshold 90
```

**Target:** ≥90% spec coverage
- All specifications have tests
- All code nodes have tests

### Metric 4: Alignment Index
```bash
jigy validate --min-alignment 0.85
```

**Target:** ≥0.85 overall, ≥0.90 for foundation
- Protocol Stack: ≥0.90 (stable, well-defined)
- Multi-Plane Server: ≥0.90 (documented contract)
- NetSpace Sync: ≥0.85 (complex semantics)
- Configuration: ≥0.90 (stable utilities)
- Device Simulation: ≥0.80 (high complexity)

---

## 8. Benefits of This Decomposition

### For Development:
1. **Incremental adoption** → Low risk, high ROI
2. **Dependency-ordered** → Each subsystem builds on previous
3. **Test-driven** → Gaps identified and filled during JIG creation
4. **Architecture enforcement** → Layer isolation automated

### For Understanding:
1. **Clear boundaries** → New devs understand subsystem scope
2. **Explicit contracts** → Interface specifications documented
3. **Traceability** → Outcomes → Specs → Tests → Code
4. **Living documentation** → Graph auto-updates

### For Evolution:
1. **Independent subsystems** → Can evolve separately
2. **Regression prevention** → Tests linked to specs
3. **Refactoring confidence** → Know what depends on what
4. **Technical debt visibility** → Alignment metrics track health

---

## 9. Risk Mitigation

### Risk 1: JIG overhead too high
**Mitigation:**
- Start with foundation (Protocol Stack) where benefits are clear
- Use existing docs (MP_CONTRACT.md, MESSAGE_LAYER_TAXONOMY.md)
- Annotations are one-liners, not full documentation

### Risk 2: Subsystem boundaries wrong
**Mitigation:**
- Based on actual dependency analysis, not theory
- Validated by stability metrics (efferent/afferent coupling)
- Can adjust boundaries after Phase 1 learning

### Risk 3: Test gaps too large
**Mitigation:**
- JIG identifies gaps explicitly (alignment violations)
- Fill gaps incrementally during each phase
- Focus on contract tests, not exhaustive coverage

### Risk 4: Alignment index too low
**Mitigation:**
- Target 0.85, not 1.0 (perfection not required)
- Use `jigy align --propose` for repair suggestions
- Human judgment on when "good enough"

---

## 10. Success Metrics

### Technical:
- **Alignment Index:** ≥0.85 overall, ≥0.90 for foundation
- **Spec Coverage:** ≥90% (all specs have tests)
- **Code Coverage:** ≥90% (all code has tests)
- **Coupling Ratio:** Intra-subsystem >> Inter-subsystem (≥10:1)
- **Interface Stability:** All exports mapped to specs (100%)

### Human:
- **Developer Satisfaction:** ≥4/5 ("JIG helps, not hinders")
- **Onboarding Time:** -30% vs baseline (graph accelerates learning)
- **Time Spent on Manual Sync:** -50% vs baseline (auto-generated docs)

### Business:
- **Feature-to-Intent Traceability:** 100% (all code linked to outcomes)
- **Misalignment-Caused Bugs:** -40% (better semantic checks)
- **Documentation Staleness:** -60% (living graph)

---

## 11. Tooling Requirements

### jigy CLI:
```bash
# Initialize JIG
jigy init --path /Users/jmeyer/Code/ASE-A

# Scan codebase
jigy scan --source src/ase/ --tests test/ --validate

# Generate graph
jigy graph --format html --output .jig/graph.html --interactive

# Check alignment
jigy validate --min-alignment 0.85 --check-coverage

# Propose repairs
jigy align --propose

# Coverage report
jigy coverage --type all --format html --output .jig/coverage.html
```

### IDE Integration:
- Jump from spec to implementation
- Show JIG annotations in hover
- Visualize subsystem boundaries

### CI Integration:
```yaml
# .github/workflows/jig-validation.yml
- name: Validate JIG
  run: |
    jigy scan --validate
    jigy validate --strict --min-alignment 0.85
    jigy align --detect
```

---

## 12. Next Steps

### Immediate (This Week):
1. ✅ Complete architecture analysis (done)
2. ✅ Write decomposition strategy (this document)
3. ⏳ Create Phase 1 plan (Protocol Stack JIG)
4. ⏳ Set up `.jig/` directory structure
5. ⏳ Write first outcome (O-PS-001)

### Phase 1 Start (Next Week):
1. Create 4-6 Protocol Stack outcomes
2. Create 10-15 Protocol Stack specifications
3. Add `@jig` annotations to protocol/, transport/
4. Run `jigy scan` (when tool available)
5. Fill test gaps (codec contracts)

### Continuous:
- Monitor alignment metrics
- Adjust subsystem boundaries if needed
- Document learnings in `docs/introspection/JIG_LEARNINGS.md`

---

## 13. References

**Herbert Simon:**
- "The Architecture of Complexity" (1962)
- Nearly Decomposable Systems theory

**John Ousterhout:**
- *A Philosophy of Software Design* (2018)
- Deep modules, information hiding

**ASE Architecture Docs:**
- `docs/architecture/MP_CONTRACT.md`
- `docs/architecture/MESSAGE_LAYER_TAXONOMY.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/CRDT_DESIGN.md`

**JIG Concept:**
- `docs/introspection/JIG-Concept-v4.md`

**ASE Analysis:**
- `docs/introspection/ARCHITECTURE_ANALYSIS.md`

---

## Conclusion

ASE's natural subsystem structure makes it ideal for JIG adoption. The codebase already exhibits:
- Clear architectural layers
- Zero circular dependencies
- Well-defined interfaces
- Strong foundation modules

**Critical Split:** Separating Device Simulation Infrastructure (5A) from Device Behaviors (5B) creates clean boundary between:
- **Infrastructure:** How we simulate devices (stable framework)
- **Behaviors:** What devices do (evolving domain logic)

This split enables:
- Infrastructure JIG to stabilize independently
- Behavior specs to evolve with product requirements
- Future device-specific behaviors (shifter ≠ derailleur) to have separate specs
- Clear distinction between framework concerns and AXS component modeling

**Strategy:** Extract and document the existing boundaries, starting with the Protocol Stack foundation and building outward in dependency order.

**Timeline:** 16 weeks for full adoption (Phases 1-6), with incremental value after each phase.

**Risk:** Low. JIG documents what already exists, doesn't impose new architecture.

**ROI:** High. Traceability, test coverage, and living documentation with minimal overhead.

---

**Document Status:** Draft
**Author:** Claude + Jim Meyer
**Next Review:** After Phase 1 completion
**Version:** 1.0
