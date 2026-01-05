---
id: S-088
title: Cross Tower Isolation
type: specification
outcome: O-026
---

# Cross Tower Isolation

## Constraints

1. **Cross-tower dependencies are forbidden**
   - A brick in tower A MUST NOT depend on a brick in tower B
   - Dependencies are determined from implementation graph
   - Function calls across tower boundaries are violations

2. **Shared dependencies allowed**
   - Multiple towers MAY depend on the same external packages
   - Shared bricks (no tower field) MAY be used by any tower
   - Only cross-tower internal dependencies are forbidden

3. **Layer constraints apply within towers**
   - Tower isolation is orthogonal to layer constraints
   - A brick at layer 1 in tower A can depend on layer 0 in tower A
   - A brick at layer 1 in tower A CANNOT depend on any layer in tower B

## Examples

Valid dependencies (single tower):
```
B-cli (layer 1) → B-validation (layer 0)  ✓ same tower
B-cli (layer 1) → B-config (layer 0)      ✓ same tower
```

Invalid dependencies (multi-tower):
```
B-api (tower: backend) → B-ui (tower: frontend)  ✗ cross-tower
B-frontend (tower: frontend) → B-data (tower: backend)  ✗ cross-tower
```

## Rationale

Tower isolation enables independent development, testing, and deployment of components. Cross-tower dependencies create hidden coupling that defeats the purpose of partitioning.

