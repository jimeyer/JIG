# JIG: Jig Intent Graph v5.0
**Jig Intent Graph with Nearly Decomposable Systems**
**An Alignment-Based Development System Guided by Architectural Boundaries**
**Date:** 2025-11-13
**Status:** Architecture Proposal

> **v5 Key Innovation:** JIG now embodies Herbert Simon's "Nearly Decomposable Systems" principle as a core design constraint. Well-designed software naturally exhibits sparse inter-module connections with dense intra-module connections. JIG makes this structure visible, measurable, and maintainable.

---

## Executive Summary

JIG (Jig Intent Graph) represents a fundamental reimagining of software development as a **constraint-satisfaction and alignment problem** rather than a linear construction process.

The name "JIG" embodies the system's philosophy:
- **Jig** (noun): A template or guide that ensures components align correctly during construction
- **Intent Graph**: The explicit network of relationships between why we build (Outcomes), what we build (Specifications), how we verify (Tests), and how we implement (Code)

**New in v5:** The Intent Graph should be **nearly decomposable** - exhibiting natural subsystem boundaries with high internal cohesion and low external coupling. This structure is not imposed but **discovered and maintained** through JIG's analysis.

Instead of "writing code," development becomes:
1. **Expressing intent** in structured documentation (Outcomes and Specifications)
2. **Annotating reality** with lightweight decorators in tests and code
3. **Detecting misalignment** when changes create inconsistencies across the graph
4. **Monitoring decomposability** to ensure architectural health
5. **Restoring equilibrium** through AI-assisted repair operations
6. **Maintaining coherence** between business purpose and running systems

> "JIG doesn't build software forward or reverse—it maintains alignment across all representations of system meaning while preserving natural architectural boundaries."

---

## 1. Core Philosophy: Alignment and Decomposability

### 1.1 The Traditional Problem

Traditional development follows directional flows:
- **Forward**: Requirements → Design → Code → Tests
- **Reverse**: Code → Tests → Documentation → Intent

Problems:
- Assumes unidirectional causality
- Creates drift between artifacts
- Lacks unified model of "correctness"
- Manual synchronization burden
- Documentation becomes redundant and stale
- **Architectural erosion** through undisciplined connections

### 1.2 The JIG Solution: Nearly Decomposable Graphs

JIG treats software as a **constraint network** seeking equilibrium, guided by Herbert Simon's insight:

> "The behavior of a nearly decomposable system is approximately the sum of the behaviors of its subsystems, considered in isolation, plus the interactions among subsystems."
> — Herbert Simon, "The Architecture of Complexity" (1962)

**Key Properties of Nearly Decomposable Systems:**
1. **Hierarchical Structure**: Systems naturally form levels of abstraction
2. **Sparse Inter-module Coupling**: Subsystems interact through narrow interfaces
3. **Dense Intra-module Coupling**: Components within subsystems are tightly integrated
4. **Independent Evolution**: Subsystems can change without cascading effects
5. **Emergent Boundaries**: Natural seams arise from functional cohesion

```
┌─────────────────────────────────────────────────────┐
│         Jig Intent Graph (JIG) v5                   │
│                                                      │
│  ┌─────────────────┐     ┌─────────────────┐       │
│  │   Subsystem A   │     │   Subsystem B   │       │
│  │  ┌───┐ ┌───┐   │     │  ┌───┐ ┌───┐   │       │
│  │  │ O │→│ S │   │     │  │ O │→│ S │   │       │
│  │  └───┘ └───┘   │     │  └───┘ └───┘   │       │
│  │    ↓     ↓     │ ←─→ │    ↓     ↓     │       │
│  │  ┌───┐ ┌───┐   │     │  ┌───┐ ┌───┐   │       │
│  │  │ T │→│ C │   │     │  │ T │→│ C │   │       │
│  │  └───┘ └───┘   │     │  └───┘ └───┘   │       │
│  └─────────────────┘     └─────────────────┘       │
│   Dense Internal          Sparse External           │
│   Connections             Interface                 │
│                                                      │
│  ┌──────────────────────────────────────────┐      │
│  │        Decomposability Analyzer          │      │
│  │  • Modularity Score: 0.87                │      │
│  │  • Coupling Ratio: 12:1 (intra:inter)    │      │
│  │  • Interface Stability: 0.92             │      │
│  └──────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────┘
```

### 1.3 The Pragmatic Insight: Deep Modules

Building on John Ousterhout's concept of **deep modules**:

> "The best modules are those whose interfaces are much simpler than their implementations."

JIG measures and maintains module depth:
- **Interface Simplicity**: Few exported functions/classes
- **Implementation Richness**: High internal complexity
- **Information Hiding**: Implementation details opaque
- **Stable Boundaries**: Interfaces change rarely

**Depth Metric** = Lines of Code / Number of Exports

Good modules have depth > 100:1

---

## 2. The OSTC Model with Decomposability

### 2.1 Four Types of Truth in Subsystems

| Element | Type of Truth | Decomposability Role | Subsystem Scope |
|---------|--------------|---------------------|-----------------|
| **Outcome (O)** | Narrative truth | Defines subsystem purpose | Usually subsystem-specific |
| **Specification (S)** | Logical truth | Defines subsystem interface | Mix of internal and interface |
| **Test (T)** | Empirical truth | Validates subsystem contract | Both unit and integration |
| **Code (C)** | Operational truth | Implements subsystem logic | Mostly internal, some exports |

### 2.2 Subsystem Detection and Boundaries

**JIG automatically detects subsystem boundaries through:**

1. **Clustering Analysis**: Groups of highly connected OSTC nodes
2. **Dependency Analysis**: Identifies natural architectural layers
3. **Interface Detection**: Finds narrow connection points between clusters
4. **Stability Analysis**: Measures change frequency across boundaries

**New Annotation Pattern for Subsystems:**
```python
# @jig C-AUTH-001 implements:S-AUTH-001,S-AUTH-002 subsystem:auth
class AuthenticationService:
    """Core authentication logic for the system"""
    
# @jig C-USER-001 implements:S-USER-001 subsystem:user depends:auth
class UserManager:
    """User management that depends on authentication"""
```

### 2.3 Cross-Subsystem Relationships

**Types of Valid Cross-Subsystem Edges:**
1. **Uses**: Subsystem A calls subsystem B's interface
2. **Depends**: Subsystem A requires subsystem B to function
3. **Notifies**: Subsystem A sends events to subsystem B
4. **Shares**: Subsystems A and B share a common data structure

**Constraint**: Cross-subsystem edges should be **10x less frequent** than intra-subsystem edges.

---

## 3. Enhanced Data Model for Decomposability

### 3.1 Node Attributes (Extended)

```yaml
# Outcome node with subsystem assignment
---
id: O-AUTH-001
type: outcome
subsystem: auth
title: Secure user authentication
cluster_coefficient: 0.85  # How tightly connected to neighbors
centrality: 0.12           # Importance in overall graph
layer: business            # Architectural layer
---
```

### 3.2 Edge Attributes (Extended)

```yaml
# Edge with decomposability metadata
{
  "source": "S-AUTH-001",
  "target": "T-AUTH-001",
  "type": "validates",
  "subsystem": "auth",        # Internal to auth subsystem
  "crossing": false,           # Not crossing subsystem boundary
  "weight": 0.9,              # Strength of relationship
  "stability": 0.95           # How rarely this edge changes
}
```

### 3.3 Subsystem Metadata

```yaml
# New subsystem definition file
---
id: auth
name: Authentication Subsystem
type: subsystem
metrics:
  internal_edges: 47
  external_edges: 4
  coupling_ratio: 11.75      # internal/external
  cohesion: 0.89             # Average internal edge weight
  depth: 234                 # LOC per export
  modularity: 0.91           # Newman modularity score
interfaces:
  exports:
    - authenticate()
    - validate_token()
    - refresh_token()
  imports:
    - config.get_setting()
    - crypto.hash_password()
dependencies:
  - config                   # Configuration subsystem
  - crypto                   # Cryptography utilities
---
```

---

## 4. Deterministic Analysis Tools

### 4.1 Decomposability Scanner

```bash
# New decomposability analysis commands
jigy decompose --detect           # Auto-detect subsystems
jigy decompose --validate         # Check decomposability health
jigy decompose --metrics          # Calculate coupling/cohesion
jigy decompose --visualize        # Generate subsystem diagram
```

**Detection Algorithm:**
1. Build full OSTC graph from annotations
2. Apply community detection (Louvain method)
3. Calculate modularity score (Newman-Girvan)
4. Identify interface nodes (high betweenness centrality)
5. Validate against coupling ratio threshold (10:1)

### 4.2 Decomposability Metrics

**Core Metrics:**

```python
# Coupling Ratio (should be > 10:1)
coupling_ratio = internal_edges / external_edges

# Modularity Score (Newman, should be > 0.3)
modularity = sum(e_ii - a_i^2 for all communities)

# Interface Stability (should be > 0.8)
interface_stability = 1 - (interface_changes / total_changes)

# Depth Score (LOC per export, should be > 100)
depth_score = lines_of_code / number_of_exports

# Clustering Coefficient (should be > 0.5)
clustering = (3 * triangles) / (2 * triads)
```

### 4.3 Visualization Modes

```bash
# Generate different views of decomposability
jigy graph --mode subsystem      # Subsystem boundaries highlighted
jigy graph --mode layers         # Architectural layers
jigy graph --mode coupling       # Edge thickness = coupling strength
jigy graph --mode stability      # Color = change frequency
jigy graph --mode depth          # Node size = module depth
```

**Visual Indicators:**
- **Subsystem Boundaries**: Dotted boxes around clusters
- **Interface Nodes**: Diamond shapes at boundaries
- **Coupling Strength**: Edge thickness (thin = good)
- **Stability**: Green = stable, Red = volatile
- **Depth**: Larger nodes = deeper modules

---

## 5. Agent Prompts for Decomposability

### 5.1 Extraction Prompts (Updated)

```markdown
When extracting OSTC nodes from code, also identify:

1. **Subsystem Assignment**: Which logical subsystem does this belong to?
   - Look for package/module structure
   - Identify functional boundaries
   - Note import patterns

2. **Interface Detection**: Is this an exported/public interface?
   - Public methods/functions
   - Exported classes
   - API endpoints

3. **Dependency Tracking**: What does this depend on?
   - Import statements
   - Function calls across modules
   - Data structure sharing

Example annotation:
@jig C-001 implements:S-001 subsystem:auth interface:public depends:config,crypto
```

### 5.2 Alignment Repair Prompts (Updated)

```markdown
When proposing alignment repairs, ensure:

1. **Preserve Subsystem Boundaries**
   - Don't create new cross-subsystem dependencies
   - Keep coupling ratio above 10:1
   - Maintain interface stability

2. **Respect Module Depth**
   - Don't expose internal implementation details
   - Keep interfaces narrow and stable
   - Hide complexity behind clean abstractions

3. **Check Decomposability Impact**
   - Will this change increase coupling?
   - Does it violate subsystem boundaries?
   - Could it be done within a single subsystem?

Rejection criteria:
- Changes that reduce modularity score below 0.3
- New dependencies that create circular references
- Interface changes affecting multiple subsystems
```

### 5.3 Architecture Analysis Prompts

```markdown
Analyze this JIG graph for decomposability:

1. **Identify Natural Subsystems**
   - Communities with high internal connectivity
   - Clear functional boundaries
   - Minimal external dependencies

2. **Find Architectural Smells**
   - God modules (too many connections)
   - Circular dependencies between subsystems
   - Unstable interfaces (frequent changes)
   - Shallow modules (low depth score)

3. **Suggest Refactoring**
   - How to increase modularity score?
   - Which dependencies to remove?
   - Where to introduce interfaces?

Report format:
- Overall modularity score: X.XX
- Number of subsystems detected: N
- Average coupling ratio: XX:1
- Problem areas: [list]
- Recommended actions: [prioritized list]
```

---

## 6. User Documentation Updates

### 6.1 Why Decomposability Matters

**For Developers:**
- **Cognitive Load**: Work on one subsystem without understanding all others
- **Parallel Development**: Teams can work independently on different subsystems
- **Testing Isolation**: Test subsystems independently
- **Refactoring Safety**: Changes don't cascade across boundaries

**For Architects:**
- **Visible Structure**: Graph reveals actual vs intended architecture
- **Measurable Quality**: Quantify architectural health
- **Evolution Tracking**: Monitor architectural drift over time
- **Design Validation**: Ensure new features don't violate boundaries

**For Business:**
- **Team Scalability**: Add teams to different subsystems
- **Risk Mitigation**: Failures isolated to subsystems
- **Maintenance Cost**: Lower coupling = lower maintenance
- **Feature Velocity**: Independent subsystems = parallel features

### 6.2 Best Practices for Nearly Decomposable Systems

**Do:**
- Keep subsystems under 10,000 lines of code
- Maintain coupling ratio above 10:1
- Define clear interface contracts (Specifications)
- Test interfaces thoroughly
- Document subsystem boundaries in Outcomes

**Don't:**
- Share mutable state between subsystems
- Create circular dependencies
- Bypass interfaces for "performance"
- Expose implementation details
- Let subsystems grow unbounded

### 6.3 Reading the Decomposability Dashboard

```
┌────────────────────────────────────────┐
│     JIG Decomposability Dashboard      │
├────────────────────────────────────────┤
│ Overall Health: ■■■■■■■□□□ (72%)      │
│                                        │
│ Subsystems Detected: 7                 │
│ ├─ auth      [■■■■■■■■■□] 92% healthy │
│ ├─ user      [■■■■■■■□□□] 71% healthy │
│ ├─ billing   [■■■■■■■■□□] 83% healthy │
│ ├─ catalog   [■■■■■□□□□□] 56% concern │
│ ├─ shipping  [■■■■■■■■■□] 94% healthy │
│ ├─ inventory [■■■■■■□□□□] 67% warning │
│ └─ reports   [■■■■■■■■■■] 98% healthy │
│                                        │
│ Key Metrics:                           │
│ • Modularity Score: 0.71 ✓            │
│ • Avg Coupling Ratio: 8.3:1 ⚠         │
│ • Interface Stability: 0.89 ✓         │
│ • Avg Module Depth: 156:1 ✓           │
│                                        │
│ Top Issues:                            │
│ 1. catalog→inventory circular dep ⚠    │
│ 2. user subsystem growing large ⚠      │
│ 3. billing has 12 dependencies ⚠       │
└────────────────────────────────────────┘
```

---

## 7. Implementation Roadmap for Decomposability

### 7.1 Phase 1: Analysis Tools (Weeks 1-2)
- Implement community detection algorithm
- Add modularity score calculation
- Create subsystem detection scanner
- Generate decomposability report

### 7.2 Phase 2: Visualization (Weeks 3-4)
- Add subsystem boundary rendering
- Implement coupling strength visualization
- Create interactive subsystem explorer
- Add drill-down from subsystem to OSTC nodes

### 7.3 Phase 3: Monitoring (Weeks 5-6)
- Track decomposability metrics over time
- Alert on boundary violations
- Generate architecture drift reports
- Create CI/CD gates for modularity

### 7.4 Phase 4: AI Assistance (Weeks 7-8)
- Train models on well-decomposed systems
- Generate refactoring suggestions
- Predict decomposability impact of changes
- Auto-propose subsystem boundaries

---

## 8. Metrics and Success Criteria

### 8.1 Decomposability Health Metrics

| Metric | Excellent | Good | Warning | Critical |
|--------|-----------|------|---------|----------|
| **Modularity Score** | >0.7 | >0.5 | >0.3 | <0.3 |
| **Coupling Ratio** | >15:1 | >10:1 | >5:1 | <5:1 |
| **Interface Stability** | >0.9 | >0.8 | >0.6 | <0.6 |
| **Module Depth** | >200:1 | >100:1 | >50:1 | <50:1 |
| **Clustering Coefficient** | >0.7 | >0.5 | >0.3 | <0.3 |
| **Largest Subsystem** | <15% | <25% | <40% | >40% |

### 8.2 Architectural Drift Indicators

**Green Flags:**
- Subsystem count stable or slowly growing
- Coupling ratio improving over time
- Interface changes < 5% per release
- New features fit within existing subsystems

**Red Flags:**
- Sudden drop in modularity score
- New circular dependencies appear
- Interface explosion (>20% growth)
- "Util" or "Common" subsystem grows rapidly

---

## 9. Tool Support for Decomposability

### 9.1 CLI Commands (Extended)

```bash
# Initialize with subsystem detection
jigy init --auto-detect-subsystems

# Scan with decomposability analysis
jigy scan --analyze-structure

# Validate architectural boundaries
jigy validate --check-boundaries --min-modularity 0.5

# Generate subsystem documentation
jigy docs --subsystems --format markdown

# Refactor suggestions
jigy refactor --suggest --target-modularity 0.8

# Compare architectures
jigy compare --before v1.0 --after v2.0 --focus decomposability
```

### 9.2 Configuration for Decomposability

```toml
# .jig.toml
[decomposability]
min_modularity = 0.5
min_coupling_ratio = 10
max_subsystem_size = 10000
enforce_boundaries = true
alert_on_violations = true

[subsystems.auth]
max_size = 5000
allowed_dependencies = ["config", "crypto"]
exported_interfaces = ["authenticate", "validate_token"]

[subsystems.user]
max_size = 8000
allowed_dependencies = ["auth", "database"]
stability_requirement = 0.9
```

### 9.3 IDE Integration for Boundaries

**Visual Indicators:**
- Subsystem boundaries shown in file tree
- Cross-subsystem imports highlighted
- Coupling ratio displayed in status bar
- Quick actions for boundary violations

**Refactoring Support:**
- "Move to subsystem" refactoring
- "Extract interface" for boundary crossing
- "Reduce coupling" assistant
- "Split subsystem" when too large

---

## 10. Case Studies in Decomposability

### 10.1 Example: E-Commerce Platform

**Before JIG Decomposability Analysis:**
- Monolithic structure
- 200+ dependencies between modules
- 6-month feature delivery time
- 40% of changes cause bugs elsewhere

**After Applying Nearly Decomposable Principles:**
```
Subsystems Identified: 8
- auth (2.1k LOC, 3 exports)
- catalog (4.5k LOC, 8 exports)  
- cart (3.2k LOC, 5 exports)
- payment (2.8k LOC, 4 exports)
- shipping (3.9k LOC, 6 exports)
- inventory (4.1k LOC, 7 exports)
- notifications (1.8k LOC, 3 exports)
- reporting (5.2k LOC, 12 exports)

Results:
- Modularity score: 0.73 (from 0.21)
- Coupling ratio: 12:1 (from 1.5:1)
- Feature delivery: 6 weeks (75% reduction)
- Change-induced bugs: 8% (80% reduction)
```

### 10.2 Example: DevOps Tool

**Initial Bootstrap Reveals:**
```yaml
Problems Detected:
- "utils" subsystem with 47 dependencies (god module)
- Circular dependency: config ↔ validation ↔ config
- Average module depth: 23:1 (too shallow)
- 31% of code not in any clear subsystem

JIG Recommendations:
1. Split utils into focused subsystems
2. Extract validation interface
3. Combine related shallow modules
4. Create clear subsystem for orphaned code
```

**After Refactoring:**
- 6 clear subsystems
- No circular dependencies
- Module depth average: 187:1
- 100% code in defined subsystems

---

## 11. FAQ: Decomposability in JIG

### Q: How is this different from microservices?

**A**: Nearly decomposable systems are about logical boundaries, not deployment boundaries. You can have a nearly decomposable monolith or poorly decomposed microservices. JIG measures logical coupling regardless of deployment strategy.

### Q: What if my system is inherently highly connected?

**A**: Some domains require high connectivity (e.g., compilers, game engines). JIG can still help by:
- Identifying the most stable interfaces
- Finding hidden subsystem boundaries
- Measuring relative decomposability
- Tracking architectural drift

### Q: How do I start decomposing a legacy system?

**A**: 
1. Run `jigy decompose --detect` on existing code
2. Review auto-detected boundaries
3. Start with the most isolated subsystem
4. Add annotations incrementally
5. Use metrics to guide refactoring

### Q: Can I have nested subsystems?

**A**: Yes! JIG supports hierarchical decomposition:
```
system
├─ frontend
│  ├─ components
│  ├─ state
│  └─ api
└─ backend
   ├─ auth
   ├─ data
   └─ services
```

### Q: What's a good first subsystem to extract?

**A**: Look for:
- Utility modules (logging, config)
- Authentication/authorization
- External integrations
- Report generation
These typically have clear boundaries.

---

## 12. Conclusion: The Nearly Decomposable Advantage

JIG v5 transforms Simon's theoretical insight into practical tooling:

**What Simon Taught:**
- Complex systems are hierarchically decomposable
- Subsystems evolve quasi-independently
- Interfaces are the key to managing complexity

**What JIG Delivers:**
- Automatic subsystem detection
- Quantified decomposability metrics
- Visual architecture representation
- Enforcement of boundaries
- Guided refactoring toward better structure

**The Result:**
> "Software that knows its own shape, maintains its boundaries, and evolves within architectural constraints."

**The Promise:**
- **10x reduction** in cross-module coupling
- **5x improvement** in parallel development capacity
- **3x reduction** in change-induced bugs
- **2x improvement** in onboarding time

**The Philosophy:**
We don't impose structure on software; we discover the structure that wants to exist, document it in the Intent Graph, and maintain it through alignment. The best architectures are not designed—they are cultivated through careful attention to natural boundaries.

---

## 13. Migration Guide from v4 to v5

### For Existing JIG Users:

**No Breaking Changes**: v5 is fully backward compatible with v4.

**New Capabilities to Adopt:**
1. Add `subsystem:` tags to annotations
2. Run `jigy decompose --detect` to find boundaries
3. Set decomposability thresholds in `.jig.toml`
4. Monitor modularity metrics in CI/CD

**Recommended Migration Path:**
1. Week 1: Run decomposability analysis on existing JIG
2. Week 2: Add subsystem annotations to one module
3. Week 3: Set up boundary monitoring
4. Week 4: Enable decomposability gates in CI

### For New JIG Users:

**Start with Decomposability First:**
1. Run `jigy init --auto-detect-subsystems`
2. Review and adjust detected boundaries
3. Begin with the most isolated subsystem
4. Expand outward following dependencies

---

## 14. References & Acknowledgments

### 14.1 Theoretical Foundations (Updated)

1. **Herbert Simon**
   - "The Architecture of Complexity" (1962)
   - "The Sciences of the Artificial" (1969)
   - Nearly Decomposable Systems theory

2. **John Ousterhout**
   - "A Philosophy of Software Design" (2018)
   - Deep modules and information hiding

3. **Christopher Alexander**
   - "Notes on the Synthesis of Form" (1964)
   - Design as constraint satisfaction

4. **Network Science**
   - Newman, "Modularity and community structure" (2006)
   - Blondel et al., "Louvain method" (2008)

### 14.2 Related Tools & Practices (Updated)

5. **Architecture Analysis Tools**
   - Structure101: Architectural complexity
   - Lattix: Dependency structure matrix
   - ArchUnit: Architecture testing

6. **Graph Analysis**
   - NetworkX: Graph algorithms
   - Gephi: Graph visualization
   - Neo4j: Graph database

---

**Document Version**: 5.0.0
**Last Updated**: 2025-11-13
**Key Innovation**: Nearly Decomposable Systems as First Principle
**Authors**: JIG Team
**Status**: Architecture Proposal

---

*"JIG: The alignment template for nearly decomposable software."*
*"Intent documented. Reality annotated. Boundaries preserved. Alignment maintained."*

## Appendix A: Mathematical Foundations

### Newman Modularity Score

The modularity Q for a partition of a graph:

```
Q = Σ(e_ii - a_i²)
```

Where:
- e_ii = fraction of edges within community i
- a_i = fraction of edges with at least one end in community i

Target: Q > 0.3 (significant community structure)

### Coupling Ratio

```
CR = |E_internal| / |E_external|
```

Where:
- E_internal = edges within subsystem
- E_external = edges crossing subsystem boundary

Target: CR > 10:1

### Module Depth

```
D = LOC / |Exports|
```

Where:
- LOC = lines of code in module
- |Exports| = number of exported functions/classes

Target: D > 100:1

### Clustering Coefficient

```
C = 3 × (number of triangles) / (number of connected triples)
```

Measures how tightly connected a node's neighbors are.
Target: C > 0.5 for subsystem cores

---

*End of JIG Concept v5.0 - Nearly Decomposable Systems Edition*
