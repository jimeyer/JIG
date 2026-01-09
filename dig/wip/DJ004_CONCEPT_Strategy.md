---
title: JIG/DIG Product Strategy
type: exploration
status: active
created: 1736200000
created_human: 2026-01-06 10:00 CST
parent: "[[DJ003_CONCEPT_Context_Integration]]"
children: []
---
# JIG/DIG Product Strategy

## One Tool or Two?

**Decision: Two separate tools.**

The mental models are genuinely different:

| JIG | DIG |
|-----|-----|
| "What should be true" | "Why we decided" |
| Evergreen, prescriptive | Archival, descriptive |
| Validates against reality | Captures reasoning |
| Day-to-day development | Archaeology/onboarding |
| Can fail (drift detected) | Can't fail (it's history) |

They're **complements**, not subsets:
- You might use JIG without DIG (small project, obvious decisions)
- You might use DIG without JIG (documenting legacy decisions)
- Together they're more powerful, but neither subsumes the other

---

## Twin Tools Precedent

Existing pairs in the wild:

| Pair | Relationship |
|------|--------------|
| `rg` + `fd` | Content search + file search (often installed together) |
| `bat` + `delta` | View files + view diffs (same rendering philosophy) |
| `kubectl` + `helm` | Resource management + package management |
| `terraform` + `terragrunt` | IaC + IaC orchestration |
| `curl` + `jq` | Fetch + transform (universally paired) |
| `git` + `gh` | Local VCS + remote platform |

JIG/DIG is unique because they're **designed as twins from birth**. Most pairs evolved separately and converged. Building them in parallel with aligned CLIs is rare and valuable.

The closest conceptual parallel: **ADRs + C4 diagrams** (decisions + structure) but those aren't tooled as a pair.

---

## Combined Context Command

**Decision: Config-based peer integration (no third tool).**

Options considered collapsed into one insight: whether via flags, third tool, or shared subcommand, the mechanism is the same—each tool detects and includes the other. The only variable is the default and visibility.

### The Mechanism

Each tool checks if the peer is installed and has content:

```bash
jigy context   # Checks: is `digy` in PATH? Does ./dig/ exist?
               # If yes to both, includes DIG context automatically
```

### Why Config Over Implicit Detection

**Explicit config that happens to be set > Implicit magic**

Using `init` to create visible config:
1. **No hidden behavior** — It's right there in the file
2. **Progressive discovery** — User sees it, learns the option exists
3. **Easy to change** — Delete the line or flip the bool
4. **Self-documenting** — Config file explains the system

### What `init` Creates

Both config files live in the **project root** for discoverability:

```
project/
├── jig.toml          # Created by jigy init
├── dig.toml          # Created by digy init
├── jig/
└── dig/
```

`jigy init` creates `jig.toml`:
```toml
[integration]
include_dig = true   # Include DIG context when available
```

`digy init` creates `dig.toml`:
```toml
[integration]
include_jig = true   # Include JIG context when available
```

> **Note:** DIG currently uses `dig/digconfig.yaml`. Migration to `dig.toml` in root is required.

### Behavior

```bash
jigy context   # Reads jig.toml, sees include_dig = true
               # Checks if digy exists and ./dig/ present
               # If yes: combined output
               # If no: JIG only (graceful degradation)
```

User never wonders "why am I seeing DIG stuff?"—they can grep their config and find the answer.

### Init Interaction (Optional Enhancement)

Could make it interactive when peer detected:

```bash
$ jigy init
Creating jig.toml...

Detected: digy is installed
? Include DIG context in `jigy context` output? [Y/n]

Created jig.toml with integration enabled.
```

Or non-interactive with a discoverable comment:

```toml
[integration]
# DIG detected - combined context enabled
include_dig = true
```

### Implementation

Simple subprocess call when peer integration enabled:

```go
func getContext() string {
    jigContext := buildJigContext()

    if config.IncludeDig && digInstalled() && digDirExists() {
        digContext, err := exec.Command("digy", "context", "-m").Output()
        if err == nil {
            return jigContext + "\n---\n" + digContext
        }
    }
    return jigContext
}
```

**Result**: No third tool, no new install, graceful degradation, discoverable config.

---

## The `y` Naming

### The Problem
`jig` and `dig` collide with existing tools, requiring `jigy` and `digy`.

### The Reframe
**The Y is for "Why"**:
- `digy` = "dig why" — excavate the reasoning
- `jigy` = "jig why" — understand the fixture's purpose

DIG is literally about capturing "why." The `y` suffix becomes thematic rather than collision avoidance.

### Alternative Strategies
1. Homebrew tap priority: `brew install jig` from your tap first
2. Claim `jig`/`dig` as aliases in docs, let users override if no collision
3. Long game: If adoption grows, become THE jig/dig

**Verdict**: Memorable short names that work > fighting for collisions. `jigy` and `digy` are sticky.

---

## Adoption Strategy

### Wedge Use Cases (Get First Win)

1. **"Document your architecture in 10 minutes"** — One JIG file, immediate value
2. **"Never re-explain a decision again"** — One DIG entry after painful PR review
3. **"Onboard a new dev in an hour"** — JIG/DIG context dump to Claude

Key insight: **Single-file value.** Don't require full adoption. One JIG should help.

### AI-Native Positioning (Primary Moat)

Position JIG/DIG as **the standard format for giving AI context about codebases**:

4. **Official Claude Code integration** — `jigy context -m` as recommended pattern
5. **"AI-readable architecture"** — Marketing angle that resonates now
6. **Prompt template library** — "Copy this JIG into your prompt"
7. **Benchmark**: "Claude answers X% more accurately with JIG context"

Every AI coding tool needs context. JIG/DIG is structured context. Make it the **interchange format**.

### Developer Workflow Hooks

8. **GitHub Action**: PR comment with "This change affects JIG: X"
9. **VS Code extension**: Hover over code, see related DIG decisions
10. **Git hook**: `jigy validate` on commit (like lint/format)
11. **PR template**: Auto-inject relevant JIG/DIG context

### Content & Community

12. **"JIG this repo"** — Tweet thread series documenting famous OSS architectures
13. **"Decision archaeology"** — Blog series: "Reconstructing the decisions behind X"
14. **Template gallery** — "JIG for Next.js", "JIG for CLI tools", etc.
15. **Case studies** — "How we cut onboarding from 2 weeks to 2 days"

### Enterprise Angle

16. **Compliance mapping** — JIGs for SOC2/HIPAA requirements
17. **Architecture review replacement** — "Better than ADRs"
18. **Decision debt metric** — "You have 47 undocumented decisions"

### Viral Mechanics

19. **Import from README** — Parse existing docs into JIG format
20. **AI generation** — "Analyze this codebase, generate initial JIG"
21. **"JIG coverage" badge** — Like test coverage, for docs
22. **One-click from Stack Overflow** — "JIG this question" browser extension

### Strategic Partnerships

23. **Anthropic dogfooding** — Get Claude Code to use JIG/DIG internally
24. **ThoughtWorks endorsement** — They popularized ADRs, position as evolution
25. **DevRel at key companies** — Stripe, Linear, Vercel adopt publicly

---

## Top 3 Strategic Recommendations

1. **Lead with AI context** — Unique timing. "The format AI understands" is positioning no one else has. Build the Claude Code integration deep.

2. **Single-file on-ramp** — Make `jigy init` create one file that's immediately useful. Don't require commitment. Let it grow organically.

3. **Document famous projects** — Create JIGs for React, Go, Kubernetes. Show the format's power. Becomes content marketing + template gallery + credibility.

---

## Open Questions

- How deep should the AI integration go in v1?
- Which famous project to JIG first for maximum visibility?
- Should `init` be interactive when peer detected, or just set defaults with comments?
