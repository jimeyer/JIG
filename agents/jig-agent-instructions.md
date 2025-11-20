# JIG Agent Instructions

This project uses JIG (Jig Intent Graph) for alignment management.

## What JIG Is
Four linked layers representing the same truth:
- **Outcomes (O)**: Business value we deliver (`jig/outcomes/O-*.md`)
- **Specifications (S)**: Technical requirements (`jig/specifications/S-*.md`)  
- **Tests (T)**: Verification (code with `@jig T-*` annotations)
- **Code (C)**: Implementation (code with `@jig C-*` annotations)

**Your job: Keep these aligned when you make changes.**

## Before You Work
1. Run `jig validate` to check current alignment
2. Find related O/S/T/C nodes for your task area:
   ```bash
   grep -r "subsystem:auth" jig/
   # Look for @jig annotations in code
   ```

## During Work
Follow existing patterns:
- **Adding tests**: Add `@jig T-XXX verifies:S-YYY subsystem:name` annotation
- **Writing code**: Add `@jig C-XXX implements:S-YYY subsystem:name` annotation
- **Changing behavior**: Update related S/O files AND their linked T/C

## After Work
1. Verify all four layers reflect your changes
2. Run `jig validate` - fix any broken links
3. Ensure bidirectional consistency:
   - If code implements S-001, does S-001 reference the code?
   - If test verifies S-001, is test listed in S-001?

## Key Rules
- **Never orphan**: Every T/C must link to an S or O
- **Never break links**: Update both sides of relationships  
- **Use subsystems**: Match existing subsystem annotations
- **Stay aligned**: When business intent (O) changes, cascade to S→T→C

## Common Operations
**Bug fix**: Update C → verify T catches it → check S is accurate
**New feature**: Create/update O → derive S → write T → implement C
**Refactor**: Update C/T → verify S unchanged (or update if behavior changed)
**Debug**: Check if T→C alignment broke, or S no longer matches reality

## Anti-Patterns
- Changing code without checking related S nodes
- Writing tests that don't link to specifications
- Updating O without propagating to S/T/C
- Breaking validation without fixing it

**Remember**: OSTC is a constraint system. All four must stay aligned.
