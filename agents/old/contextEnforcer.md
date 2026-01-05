# Agent Context: Fixing Enforcer Violations

## The Rule

**The Enforcer is correct. The sender is wrong.**

The Protocol Enforcer validates messages against `docs/architecture/MESSAGE_LAYER_TAXONOMY_V2.md`. It is an isolated, incorruptible module that cannot be modified to "fix" violations. If the enforcer reports a violation, the **sender must change its output** to conform to the specification.

Never modify `src/ase_enforcer/` to suppress or work around violations.

---

## Finding Violations

### Log File
```
logs/enforcer.jsonl
```

Each line is a JSON object:
```json
{"ts": 1734892800.123, "plane": "airspace", "source": "rear_derailleur", "status": "violation", "violations": [...]}
```

### CLI Monitor (Real-time)
```bash
ase monitor --enforcer
```

Output format:
- `[HH:MM:SS] ✓ plane | source | N rules` — message passed
- `[HH:MM:SS] 🚨 ERROR plane | source | rule_id rule_name` — violation

### Filter by device or violations only
```bash
ase monitor --enforcer --filter rear_derailleur
ase monitor --enforcer --filter violation
```

---

## Understanding Violations

Each violation has:
- **rule_id**: e.g., `L3_001`, `ENV_002`
- **rule_name**: Human-readable name
- **severity**: `ERROR`, `WARNING`, `INFO`
- **message**: What's wrong
- **context**: Debug info (missing fields, expected values)

### Common Violations

| Rule ID | Name | Cause | Fix |
|---------|------|-------|-----|
| `ENV_001` | envelope_required_fields | Missing `env_data_plane` or `env_pdu` | Add required envelope fields |
| `ENV_002` | envelope_plane_match | `env_data_plane` doesn't match receiving plane | Set correct plane value |
| `L3_001` | pdu_requires_elc | L3_PDU missing `L3_elc` field | Add ELC with era, lamport, actor_id |
| `L3_003` | elc_structure | L3_elc missing required fields | Include `L3_era`, `L3_lamport`, `L3_actor_id` |
| `L4_001` | message_requires_operation | Missing `L4_operation` | Add operation field to L4_Message |

---

## Conforming Message Structure

Reference: `docs/architecture/MESSAGE_LAYER_TAXONOMY_V2.md`

### Required L3_PDU Structure (airspace/netspace)
```json
{
  "L3_source": "device_id",
  "L3_elc": {
    "L3_era": 1,
    "L3_lamport": 42,
    "L3_actor_id": "actor1"
  },
  "L3_body": {
    "L4_operation": "device_telemetry_broadcast",
    "L4_payload": { ... }
  }
}
```

### Server_Envelope Wrapping (server-side)
```json
{
  "env_data_plane": "airspace",
  "env_pdu": { ... L3_PDU ... }
}
```

---

## Fixing Violations: Workflow

1. **Read the violation** — note rule_id and context
2. **Find the sender** — trace `source` field to sending code
3. **Check the spec** — `docs/architecture/MESSAGE_LAYER_TAXONOMY_V2.md`
4. **Modify the sender** — add missing fields or fix structure
5. **Verify fix** — run `ase monitor --enforcer` and confirm `✓`

---

## Key Principle

The enforcer exists to catch "bilateral shortcuts" — when AI-written sender and receiver code agree with each other but neither conforms to spec. The enforcer only knows the spec. If it says the message is wrong, the message is wrong.

Fix the sender. Never modify the enforcer.
