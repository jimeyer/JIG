---
id: S-099
title: Init Bricks Scaffold
type: specification
outcomes: [O-028]
---
# Init Bricks Scaffold

The `jigy init` command generates an empty bricks.yaml scaffold.

## Acceptance Criteria

1. Scaffold is created at `jig/bricks.yaml`

2. Generated content is:
   ```yaml
   bricks: []
   ```

3. File is valid YAML

4. Empty scaffold passes `jigy validate bricks` (no bricks = valid, just no partition)
