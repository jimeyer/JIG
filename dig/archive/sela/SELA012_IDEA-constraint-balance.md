---
title: "IDEA: Constraint Balance"
type: exploration
status: parked
created: 1763493911
created_human: "2025-11-18 13:25 CST"
parent: "[[SELA001_SELA-Concept-Document]]"
children: []
---
# IDEA: Constraint Balance

JIM:

We discussed SELA doing “Forward Development” and “reverse engineering”.  

What if we removed the directional nature and thought about a fully different mental model. 

What if what SELA seeks is consistency across the graph of value, intent, behavior, test, code.   

Then the development process is to introduce imbalance or inconsistency in the system By changing something on the VIBTC graph, adding a requirement, failing a test, removing a desired behavior.    

Then the SELA system will go do work to bring the system in balance again.  

Are there existing workflows or algorithms that do that?  

How would that change the design of SELA?

In an extreme case, the SELA framework could get dropped into and existing project with working code, and it would build the rest of the empty VIBT  graph to make everything balance.     Any missing information or context could be prompted for the user to input or give clues to fill in the missing parts.  


CHATGPT:

Love this reframing. Think of SELA not as “forward vs reverse,” but as a constraint-maintaining system over a V-I-B-T-C graph. Any edit introduces an imbalance (a violated constraint). The system’s job is to detect, localize, and repair until the graph is consistent again.

Here are the best mental models and what they imply for SELA’s design.

Proven patterns we can borrow
	1.	Bidirectional transformations (BX) / Lenses

	•	From PL & databases: keep multiple related artifacts consistent (e.g., model↔code, view↔source).
	•	Notions: Get (project), Putback (repair minimal changes), symmetric lenses, delta lenses.
	•	Fit: V, I, B, T, C are projections/views of one system meaning; a change in any view should propagate with principled putback.

	2.	Model synchronization / Triple Graph Grammars (TGG)

	•	From MDE: keep heterogeneous models in sync (UML↔code↔schemas).
	•	Notions: correspondence links, consistency rules, incremental synchronization, repair strategies.
	•	Fit: Treat V, I, B, T, C as five models with a correspondence graph and executable sync rules.

	3.	Truth-Maintenance Systems (TMS/ATMS)

	•	From AI: maintain a set of beliefs + justifications; when facts change, retract/derive to restore consistency.
	•	Fit: VIBTC nodes are beliefs; edges carry justifications (“Test T verifies Behavior B that satisfies Intent I”); the engine propagates consequences when something flips.

	4.	Constraint solving / SMT / MaxSAT (graph repair)

	•	Encode invariants as constraints; on violation, compute minimal repairs (edit sets) that restore satisfiability, optionally optimizing a cost function (preserve code, prefer test updates, etc.).
	•	Fit: “Make everything balance” = solve for a consistent assignment of artifacts & links.

	5.	Reactive/dataflow systems (spreadsheets, build graphs)

	•	Changes propagate along dependency edges; incremental recompute and dirty-bit invalidation.
	•	Fit: Mark impacted subgraph (e.g., Intent edited → invalidate linked Behaviors/Tests/Code) and regenerate just those.

	6.	Eventual consistency / CRDT mindsets

	•	Multiple editors/agents concurrently edit; converge via merge rules.
	•	Fit: if several agents propose repairs, use mergeable structures + policies to converge on one consistent state.

What this means for SELA’s architecture

Core abstractions
	•	Canonical semantic graph (VIBTC): nodes with typed edges and correspondence links (e.g., Code—implements→Behavior; Test—verifies→Behavior).
	•	Constraint set: declarative rules like “Every Behavior MUST map to ≥1 Test and ≥1 Code unit,” “Every Intent MUST be realized by ≥1 Behavior,” coverage thresholds, performance predicates, etc.
	•	Repair operators: primitives the system can apply: generate/modify Tests, Code, Behaviors, Intents, Value links, or Explanations/Prompts.
	•	Cost model / policy: prioritize repairs (e.g., “prefer generating tests from Intent; only modify Value with human confirmation,” or “never auto-edit production code”).
	•	Provenance & confidence: every edge/node has origin (human/agent), confidence, last-verified timestamp.

New SELA components
	•	Balancer (Consistency Manager): watches the graph, detects violations, proposes/apply repairs using BX/TGG + constraint solving.
	•	Impact Analyzer: computes the minimal affected subgraph for any change.
	•	Planner: sequences repair operators to reach a consistent state with minimal cost (A*/IDA*, or MaxSAT with soft constraints).
	•	Dialogue Prompter: asks humans only for missing facts the solver can’t infer (keep LLM use focused).
	•	Policy Engine: org-tunable: strict/lenient, auto-apply vs propose-diffs, safety rails.

Agent prompts shift from “directional” to “repair-oriented”

Add/reshape prompts into consistency passes:
	•	detect_inconsistencies_prompt: summarize violated constraints + impacted nodes.
	•	propose_repairs_prompt: enumerate candidate repair sets with rationale & cost.
	•	synthesize_tests_prompt: from Intent/Behavior deltas, produce (or update) failing tests.
	•	synthesize_code_prompt: minimal edits to satisfy the updated tests/behaviors.
	•	align_behavior_prompt: infer/update Behavior specs to match Intent & empirical code/test signals.
	•	explain_tradeoffs_prompt: human-ready summary of why a given repair set is preferred.

(Your prior validate/compile/testgen/diff prompts stay, but are now invoked by the Balancer as tactics inside a repair plan.)

The “balance-seeking” workflow
	1.	Perturbation (human or CI): edit a Value/Intent, delete a Test, refactor Code, or flip a requirement.
	2.	Detect: constraints fire; impacted subgraph marked dirty.
	3.	Generate candidates: BX/TGG rules + prompts create repair options (e.g., add two tests; or relax an invariant; or modify one Behavior).
	4.	Score: cost model ranks options (keep business Value stable; prefer test/code changes; minimize churn).
	5.	Propose: present diffs; humans approve or adjust policy.
	6.	Apply: synthesize artifacts (tests first, then code), update links, record provenance.
	7.	Verify: run tests, re-check constraints, update confidence.
	8.	Learn: feedback updates heuristics (which fixes the team tends to prefer).

Extreme case you described: drop SELA into a working repo

Bootstrap mode:
	•	Parse code → build initial C nodes + structure.
	•	Mine behaviors from code paths & docstrings; infer B candidates (property mining, dynamic traces).
	•	Generate a baseline test suite from observed behaviors (property + example extraction) → T.
	•	Surface likely intents (cluster behaviors by purpose, names, commit messages) → I candidates; prompt humans to curate.
	•	Map to existing business docs to seed V; where absent, prompt minimally.
	•	Run Balancer: highlight gaps (unverified behaviors, intents with no tests, dead code) and propose the next repairs.

Practical guardrails
	•	Determinism first: use schemas, lenses, graph rules; use LLMs only for text↔structure or name inference.
	•	Minimal repair principle: prefer the smallest edit set that restores constraints.
	•	Policy tiers:
	•	Advisory: propose repairs only.
	•	Assisted: auto-create tests, require approval to touch code/intent.
	•	Autonomous (sandboxed): auto-repair in a branch + PR with rationale.

What you’ll need to add to SELA
	•	Constraint language: declarative rules over the VIBTC graph (YAML/JSON + simple predicates, or CUE).
	•	Correspondence model: explicit links with stable IDs (like TGG correspondences).
	•	Repair DSL: enumerate allowed actions + pre/post conditions.
	•	Cost model config: weights for changing Value/Intent vs Behavior/Test/Code.
	•	Consistency API: detect(), propose(), apply(), verify(), explain().

Why this is powerful
	•	Unifies forward + reverse into one equilibrium-seeking loop.
	•	Scales to legacy: you can start from any node set, and SELA will grow the rest to meet constraints.
	•	Reduces LLM reliance to curated touch points, while most of the heavy lifting is structural, incremental, and test-driven.