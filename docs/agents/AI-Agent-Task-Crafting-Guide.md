# Meta-Guide: Crafting Effective AI Agent Task Documents

## Core Characteristics

**A good task document is:**

- **Self-contained**: Includes all context the agent needs without external dependencies
- **Unambiguous**: One clear interpretation of what success looks like
- **Actionable**: Agent can start immediately without asking clarifying questions
- **Scoped**: Boundaries are clear—what's in scope, what's out
- **Verifiable**: Success criteria are concrete and checkable

## Essential Components

### 1. **Clear Objective Statement**

Start with a one-sentence purpose: "Your task is to [specific action] so that [outcome]."

### 2. **Context Section**

- Why this task exists
- What problem it solves
- Relevant background the agent needs
- Dependencies or prerequisites

### 3. **Specific Requirements**

- Input specifications (format, location, constraints)
- Processing rules and logic
- Output specifications (format, structure, naming)
- Edge cases to handle

### 4. **Success Criteria**

- Concrete, testable conditions
- Examples of good/bad outputs
- Quality standards

### 5. **Constraints & Boundaries**

- What NOT to do
- Resource limits
- Scope boundaries
- Style/tone requirements

## Do's ✓

**Be Specific with Action Verbs**

- ✓ "Extract all function names and their parameter counts"
- ✗ "Analyze the code"

**Provide Concrete Examples**

- Show expected input → output transformations
- Include edge cases
- Use before/after samples

**Define Output Format Explicitly**

- Specify: JSON, markdown, file structure, naming conventions
- Include templates or schemas when relevant

**Use Structured Formatting**

- Headers for scanability
- Lists for requirements
- Code blocks for examples
- Clear visual hierarchy

**Anticipate Failure Modes**

- "If X is missing, do Y"
- "When you encounter Z, skip it and log"

**Make Success Observable**

- "Output must include..."
- "All files must pass..."
- "Verify that..."

## Don'ts ✗

**Don't Be Vague**

- ✗ "Make it better" / "Improve quality" / "Optimize"
- ✓ "Reduce function length to <50 lines" / "Add error handling for null inputs"

**Don't Assume Context**

- AI has no memory between sessions unless you provide it
- Include relevant context even if it seems obvious

**Don't Mix Multiple Tasks**

- One task document = one cohesive objective
- Complex workflows should be broken into stages

**Don't Use Ambiguous Pronouns**

- ✗ "Process it and output them"
- ✓ "Process the input files and output the validation reports"

**Don't Forget Error Handling**

- Specify what to do when things go wrong
- Define fallback behaviors

**Don't Bury the Lede**

- Put the core task at the top
- Supporting details come after

## Structural Pattern

Here's a reliable template:

```markdown
# Task: [Concise Name]

## Objective
[One sentence: what and why]

## Context
[Background needed to understand the task]

## Inputs
- **Location**: [where to find]
- **Format**: [structure/type]
- **Constraints**: [what's expected]

## Process
1. [Step-by-step if order matters]
2. [Use numbered lists for sequences]
3. [Use bullets for unordered requirements]

## Outputs
- **Format**: [exact structure]
- **Location**: [where to save]
- **Naming**: [convention to follow]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Constraints
- DO NOT: [things to avoid]
- MUST: [non-negotiables]
- PREFER: [nice-to-haves]

## Examples
[Concrete before/after samples]
```

## Advanced Tips

**For Iterative Tasks**: Include a "verification step" where the agent checks its own output against criteria.

**For Complex Logic**: Use decision trees or flowcharts in markdown:

```
IF condition A:
  → Action X
ELSE IF condition B:
  → Action Y
ELSE:
  → Action Z
```

**For File Operations**: Always specify absolute paths or clear relative path conventions.

**For Code Tasks**: Specify language, style guide, testing requirements, and what constitutes "done."

**For Analysis Tasks**: Define what dimensions to analyze, what metrics to calculate, and how to present findings.

**Version Your Tasks**: Include a version number and changelog if the task evolves.

## Common Pitfalls to Avoid

1. **The Implicit Assumption**: "The agent will obviously know to..." — No, make it explicit.
    
2. **The Shifting Scope**: Task documents that try to handle every possible variation become unreadable. Better to have focused tasks.
    
3. **The Missing Exit Condition**: Always define when the agent should stop or declare completion.
    
4. **The Format Mismatch**: Asking for "a report" but not specifying markdown vs PDF vs JSON.
    
5. **The Undefined "Quality"**: Replace subjective quality judgments with measurable criteria.
    

## Testing Your Task Document

Before finalizing, ask:

1. Could a new AI agent complete this task without asking questions?
2. Would two different agents produce similar results?
3. Can success be verified without human judgment?
4. Are all terms defined or obvious from context?
5. Is the expected time/effort reasonable?

---

**The Golden Rule**: If you can't verify success mechanically, your success criteria aren't specific enough.