

we will do a Option D:
  We have Outcomes-Specs-Tests - but are missing the code.
  we are repairing the test suite now, not changing code.
  so make sure O-S-T are linked and correct.
  then make a document that lists the CODE that is missing. the list of missing CODE will become SCOPE for a new work plan to be completed later.
  for the tests that need CODE, make sure they all have the correct `@jig` decorators, then mark them Skip with a reference to the document that lists the SCOPE of CODE that must
  be created.





Fix test concept:

prompt:

  here is the recovery plan:

  1. we will use the JIG tooling:  @docs/jig/JIG-Concept-v6.1.md

  2. for each failing test, determine what SPEC the test is verifying:
  a. an existing SPEC? then do the '@jig' decoration and link
  b. a missing SPEC that we should have?  then do the '@jig' decoration and generate the SPEC we need
  c. a missing SPEC that is no longer relavant?  then delete the test

  3. link the new SPEC's to Outcomes.  Generate the missing outcomes if needed

  4. now we should have failing tests linked to good SPECs and OUTCOMES

  5. group the tests by root cause groups.

  6. for each of the root cause groups:
  a. fix the tests if the change required to address the root cause is clearn and the result will be test that are 'as good as new'.  no shims, adapaters or reverse compatiblity is
  allowed
  b. otherwise, delete the old test and write a new test according to the SPEC.
  note:  the SPECs and '@jig' decorators are there for a reason.   we can delete the tests and recreate them easily if we know the SPEC.   you are an AI Agent, so writing code is
  easy if the instructions are clear


  take these instructions and build a RECOVERY plan.   save in docs/wip/
  think hard.


Agent summary:


Key Strategy

  Core insight: SPECs are source of truth. Tests are reproducible. Old tests aren't sacred.

  5 Phases (9-12 hours total)

  Phase 0: Stop Bleeding (30min)
  - Fix replicator import (unblock 77 tests)
  - Get clean failure counts

  Phase 1: SPEC Audit (2-3hr)
  For each failing test, classify into:
  - Bucket A: Existing SPEC → add @jig annotation
  - Bucket B: Missing SPEC (needed) → create SPEC + @jig
  - Bucket C: Obsolete SPEC → mark for deletion

  Phase 2: Root Cause Groups (1hr)
  Group by strategy:
  - FIX: Mechanical (add param, fix import)
  - REWRITE: Architecture change (delete old, write new per SPEC)
  - DELETE: Obsolete (no replacement)

  Phase 3: Execute (4-6hr)
  - FIX: ~43 tests (constructor + imports)
  - DELETE: ~40 tests (flat-map obsolete)
  - REWRITE: ~35 tests (OR-Map semantics changed)

  Phase 4: JIG Integration (1hr)
  - Add @jig annotations to all tests
  - Rebuild graph index
  - Validate alignment

  Phase 5: Validation (1hr)
  - Full suite passes
  - Coverage check (>1450 tests)
  - Reflection + update PLAN.md WU8

  Decision Matrix

  NEVER: shims, adapters, backwards compatibility
  FIX: if change is mechanical and result is "as good as new"
  REWRITE: if architecture changed (OR-Map vs flat map)
  DELETE: if SPEC obsolete