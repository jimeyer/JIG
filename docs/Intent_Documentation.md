# Intent Documentation

Intent is the record of *what the system must do* and *why*. It is the third artifact alongside code and tests, and the only one that survives a rewrite.

| Layer      | Question                       | Survives rewrite? |
|------------|--------------------------------|-------------------|
| **Intent** | What must be true, and why?    | Yes               |
| **Tests**  | Is it true right now?          | Sometimes         |
| **Code**   | How is it made true?           | No                |

 Intent answers *why* and *what*. Tests answer *whether*. Code answers *how*.

---

## What Intent Contains That Code and Tests Don't

**Business justification.** Code implements exponential backoff. Tests verify the delays double. Neither records: "Upstream service X has transient failures during deploys; dropping these requests costs $Y/minute." Without intent, the next engineer removes the retry as unnecessary complexity.

**Behavioral boundaries.** Code shows what happens. Tests check specific cases. Intent declares what *must always be true* and what is *explicitly excluded*. "We authenticate tokens but do NOT authorize --- that's the gateway's responsibility" prevents well-meaning scope creep.

**Decision context.** Why this approach over alternatives. Code can't explain the road not taken. "We chose eventual consistency because strong consistency requires cross-region coordination, and the business accepts a 5-second staleness window."

**Stable requirements across rewrites.** Implementations get replaced. Test suites get rewritten with them. "Users can recover their account with only an email address" remains true whether the mechanism is magic links, OTP, or reset tokens.

**Acceptance criteria for done.** Code is never self-evidently complete. Tests tell you what passes, not what's missing. Intent defines the finish line.

---

## Properties of Good Intent

### Describes behavior, not implementation

Bad: "Use Redis for caching."
Good: "Repeated queries for the same resource return within 50ms."

The first constrains how you build. The second constrains what users experience. When the implementation changes, good intent stays true.

### Is falsifiable

Every statement should have a clear pass/fail condition. If you can't write a test that fails when the intent is violated, the intent is too vague.

Bad: "The system should be fast."
Good: "P95 response time under 200ms for authenticated reads."

### Connects upward to value

Good intent explains which user problem the behavior solves. This lets engineers make judgment calls when requirements conflict.

### Stays true after the work is done

If a statement becomes false when the current task completes, it's a task description, not intent. Intent describes enduring system properties.

Bad: "Migrate users from v1 to v2 schema."
Good: "User records conform to a single canonical schema."

### Declares what is out of scope

What the system explicitly does *not* do is as important as what it does. Boundaries prevent feature creep and distinguish "not yet built" from "deliberately excluded."

### Is concise

A few precise invariants get read. Long rationale documents don't. Target the minimum text needed for an engineer --- or an AI agent --- to understand the required behavior, why it matters, and how to verify it.

---

## The Three Levels of Intent

### Outcomes: Why it matters

An outcome describes the value delivered. It answers: *what do users get?*

- One sentence stating the value
- Measurable acceptance criteria
- Links to the specifications that deliver it

Example:
> **Account Recovery.** Users regain access to their account using only their email address. Recovery completes within 2 minutes. No customer support interaction required.

### Specifications: What must be true

A specification describes a single testable behavioral requirement. It is the atomic unit --- what code implements and tests verify.

- Statement of required behavior (1--3 sentences)
- Invariants: conditions that must always hold, each falsifiable
- Verification criteria: what a test would assert

Example:
> **Recovery Token Expiry.** Recovery tokens are single-use and expire after 15 minutes. Expired or reused tokens return an unambiguous error. Token validity is checked server-side; client-side expiry is cosmetic only.

### Architectural contracts: What constraints apply

An architectural contract defines structural rules that multiple components must honor. It constrains *how* specifications may be implemented.

- Interface definitions and invariants
- Dependency rules (what may depend on what)
- Parties to the contract (who must conform)

Example:
> **Auth Boundary.** All authentication flows go through the `auth` module. No other module reads or writes session state directly. The auth module exposes tokens; consumers treat them as opaque.

---

## Writing Specifications: A Checklist

1. **Start from the outcome.** What user value does this serve? If you can't answer, stop.
2. **State the behavior.** What must be true? Not how --- what.
3. **List invariants.** What conditions hold in all cases? Each must be falsifiable.
4. **Define verification.** What would a passing test assert?
5. **Set boundaries.** What is explicitly out of scope?
6. **Test the test:** Can a developer write a test from this spec alone, without reading the code? If no, add detail. Can they implement it without being told which library to use? If no, remove detail.

### Spec body template

```
# {Title}

{1-3 sentence statement of required behavior.}

## Invariants
- {condition that must always hold}
- {another condition}

## Verification
- [ ] {what a test would assert}
- [ ] {another assertion}

## Boundaries
- {what is explicitly out of scope}
```

Target ~50 lines. If it's longer, the spec probably covers more than one behavior.

---

## Antipatterns

**Implementation masquerading as intent.** "Store sessions in Redis with a 30-minute TTL." This is a design decision, not a behavioral requirement. Rewrite: "Sessions expire after 30 minutes of inactivity."

**Untethered specs.** A specification that doesn't connect upward to any outcome or value statement. If no one can say why a behavior matters, question whether it belongs.

**Vague acceptance criteria.** "Handle errors appropriately." Appropriately how? Rewrite with specific behaviors: "Invalid input returns 400 with a machine-readable error code."

**Specs that track tasks.** "Migrate the database to PostgreSQL" is work to do, not a system property. Rewrite: "All persistent data is stored in a transactional relational database."

**Over-specification.** Constraining implementation where only behavior matters. Every unnecessary constraint is a future obstacle to refactoring.

---

## For AI Coding Agents

When creating or modifying intent documents, follow these rules:

1. **Read existing intent before writing code.** Understand what the system promises before changing how it delivers.
2. **Describe behavior, never implementation.** If your spec names a library, framework, file path, or data structure, rewrite it.
3. **Every invariant must be falsifiable.** If you can't describe a test that would fail when the invariant is violated, the invariant is too vague. Remove or rewrite it.
4. **Connect to value.** Every spec must trace to an outcome. Every outcome must trace to a goal. If the chain breaks, ask why before proceeding.
5. **Declare boundaries.** State what is out of scope. This prevents you and future agents from adding unrequested behavior.
6. **Keep specs atomic.** One testable behavior per specification. If you need the word "and" to describe what it covers, consider splitting.
7. **Choose stable titles.** Titles should describe capabilities, not implementations. "Response Caching" survives a rewrite; "Redis Layer" does not.
8. **Don't duplicate what code already says.** Intent captures what code *cannot*: the why, the constraints, the boundaries. If deleting the spec would lose no information, the spec is redundant.
