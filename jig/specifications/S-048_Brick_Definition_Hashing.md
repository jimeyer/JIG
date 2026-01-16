---
id: S-048
title: Brick Definition Hashing
type: specification
outcomes: [O-017]
---

# Brick Definition Hashing

Each brick definition is hashed independently using canonical JSON.

**Acceptance Criteria:**
- Each brick's dict (id, name, layer, units) hashed separately
- Changing one brick does not affect other bricks' hashes
- JSON canonicalized with sorted keys and minimal separators
- Adding/removing units changes the brick's hash
- Layer changes affect the brick's hash

**Rationale:** Fine-grained change tracking for architectural partitions. Moving a module between bricks shows exactly which two bricks changed.
