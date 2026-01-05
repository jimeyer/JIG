---
title: "This IS the brick definition"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1764767474
created_human: "2025-12-03 07:11 CST"
parent: null
children: []
---

**JIM PROMPT:

creating the dependency graph is a way to get to an implementation graph, which in tern gets to bricks and layers.    bricks are used to context fence an area for the AI agent to work on.    layers help to establish a high-level order of operations (do this before that at a macro level)

when in rome, do as romans. 

what if the 'dependancy graph'  question is wrong.    for the 'hard' languages, what is the mental model that a good developer uses?  is there another perspective that is more natural for the language to create the bricks and layers concept?  

think hard.   be creative.

**CLAUDE

This is a _much_ better question. Let me think about this from first principles.

## The Inversion

You're right - "dependency graph extraction" is a compiler-writer's mental model, not a practitioner's mental model. What do developers in these languages _actually_ think about?

---

## C: The Build System IS the Graph

C developers don't think about function dependencies. They think about:

**Bricks = Build Targets**

- "This is `libauth`, it produces `libauth.a`"
- "This is the `network` module, it compiles to `network.o`"
- Headers define the interface. Implementation is private.

**Layers = Link Order**

- "You can't link the app until you've built the core libraries"
- "Static libraries depend on other static libraries in a specific order"
- The linker will _fail_ if you get the order wrong

**The insight:** CMake/Bazel/Meson already _have_ the implementation graph:

```cmake
# This IS the brick definition
add_library(libauth STATIC
    src/auth/token.c
    src/auth/session.c
)

# This IS the layer relationship
target_link_libraries(app 
    PRIVATE libauth    # app depends on libauth
    PRIVATE libcrypto  # app depends on libcrypto
)
```

**JIG doesn't parse C. JIG parses CMakeLists.txt.** Or consumes `compile_commands.json`.

---

## C++: Same, Plus Namespaces as Logical Bricks

C++ adds namespaces as a grouping mechanism that doesn't map to files:

```cpp
namespace auth::internal {  // Logical brick
    class TokenValidator { ... };
}

namespace auth {  // Public surface of the brick
    Token validate(const std::string& token);
}
```

**Bricks = Libraries + Namespaces**

- Build target is the physical brick
- Namespace is the logical brick within it

**Layers = Link order (physical) + Namespace nesting (logical)**

The build system still has the physical graph. For logical structure, C++ devs think in namespace hierarchies.

---

## Ruby: Flow, Not Structure

Ruby developers don't think in static dependencies. They think about:

**How requests flow through the system:**

```
HTTP Request 
  → Middleware 
    → Router 
      → Controller 
        → Service 
          → Model 
            → Database
```

**Bricks = Gems + Rails Components**

- "The auth gem handles authentication"
- "User-related stuff is models/user.rb, services/user_service.rb, controllers/users_controller.rb"

**Layers = The Rails Request Lifecycle**

- Controllers don't call other controllers
- Models don't call controllers
- Services orchestrate models

**The insight:** Rails conventions _are_ the layer definitions. Bundler _is_ the gem graph.

```ruby
# Gemfile - the gem-level brick graph
gem 'devise'      # auth brick
gem 'sidekiq'     # async brick
gem 'pg'          # persistence brick

# config/routes.rb - the entry points
# app/controllers/ - presentation layer
# app/services/ - domain layer  
# app/models/ - persistence layer
```

**JIG doesn't analyze Ruby metaprogramming. JIG reads the Gemfile and respects Rails conventions.**

---

## The Pattern: Use What's Already There

|Language|Brick Source|Layer Source|
|---|---|---|
|Go|`go.mod` packages|import DAG (enforced!)|
|TypeScript|npm packages, barrel files|import graph|
|Python|packages, `__init__.py`|import graph|
|Rust|Cargo crates, `mod.rs`|`Cargo.toml` deps|
|Java|Maven/Gradle modules|POM/Gradle dependencies|
|**C/C++**|**CMake/Bazel targets**|**Link dependencies**|
|**Ruby**|**Gems + Rails dirs**|**Request flow convention**|

The implementation graph **already exists** in every ecosystem. It's just stored in different places.

---

## What This Means for JIG

Instead of:

```
jig analyze --language=cpp  # Try to parse C++ (nightmare)
```

Do this:

```
jig analyze --from=cmake     # Read CMakeLists.txt
jig analyze --from=bazel     # Read BUILD files
jig analyze --from=rails     # Read Gemfile + conventions
```

### Declaration + Validation Model

For hard languages, flip the script:

1. **Developer declares bricks and layers** using idioms they already know
2. **JIG validates** that reality matches declarations
3. **JIG computes metrics** on the declared structure

```yaml
# jig/architecture.yaml for C++ project

brick_source: cmake  # JIG reads CMakeLists.txt

# Override/annotate what CMake doesn't express
subsystems:
  auth:
    targets: [libauth, libauth_test]
    public_interface: src/auth/include/
    
  network:
    targets: [libnetwork, libnetwork_test]
    public_interface: src/network/include/

# Layers as they exist in developer's mind
layers:
  - name: platform
    subsystems: [logging, crypto, threading]
    
  - name: core
    subsystems: [auth, session]
    uses: [platform]  # Can depend on platform
    
  - name: services  
    subsystems: [network, storage]
    uses: [core, platform]
```

```yaml
# jig/architecture.yaml for Rails project

brick_source: rails  # JIG reads Gemfile + conventions

# The "layers" Rails devs already think in
layers:
  - name: persistence
    patterns: 
      - app/models/**/*.rb
      
  - name: domain
    patterns:
      - app/services/**/*.rb
      - app/policies/**/*.rb
    uses: [persistence]
    
  - name: presentation
    patterns:
      - app/controllers/**/*.rb
      - app/views/**/*.rb
    uses: [domain]

# What JIG validates:
# - Controllers don't directly call models (skip domain)
# - Models don't reference controllers
# - Services don't reference controllers
```

---

## The Creative Leap: Layer = Execution Order, Not Just Dependency

Your insight about "order of operations" is key. Layers aren't just "A depends on B". They're:

**"When doing work, operate in this order"**

For an AI agent:

1. First, understand the **platform layer** (shared utilities)
2. Then, understand the **core layer** (business logic)
3. Then, understand the **services layer** (orchestration)
4. Finally, understand the **presentation layer** (UI/API)

This maps beautifully to:

- **C/C++**: Build order (link deps)
- **Ruby/Rails**: Request flow (controller → service → model)
- **Go**: Import order (DAG)
- **Microservices**: Call graph (API deps)

---

## The Brick/Layer Declaration Language

What if JIG has a simple, universal way to express bricks and layers, and then _adapters_ for each ecosystem?

```yaml
# Universal structure
bricks:
  - id: auth
    type: subsystem
    source: cmake:libauth  # Adapter: cmake, target: libauth
    # or
    source: rails:pattern:app/models/user*.rb
    # or
    source: go:package:github.com/myco/auth
    
layers:
  - id: platform
    bricks: [logging, crypto]
    
  - id: core
    bricks: [auth, session]
    below: [platform]  # platform is below core (core can use platform)
```

Adapters:

- `cmake` adapter: reads CMakeLists.txt, extracts targets and deps
- `rails` adapter: reads Gemfile, scans conventional directories
- `go` adapter: reads go.mod, follows imports
- `npm` adapter: reads package.json, follows imports

---

## Summary

**Wrong question:** "How do we extract dependency graphs from hard languages?"

**Right question:** "What do developers in these languages already use to organize their code, and how do we read that?"

**Answer by language:**

|Language|Native Organization|JIG Reads|
|---|---|---|
|C/C++|Build system|CMake/Bazel/Meson|
|Ruby|Gems + conventions|Gemfile + directory structure|
|Java|Maven/Gradle|pom.xml / build.gradle|
|Go|Modules|go.mod + compiler|
|Rust|Cargo|Cargo.toml|

The implementation graph is never constructed from scratch. It's _adapted_ from what already exists.

**"When in Rome, do as the Romans."** ← Exactly right. The Romans already have roads. JIG should use them.

---

**JIM PROMPT:

boom.   What if JIG has a simple, universal way to express bricks and layers, and then _adapters_ for each ecosystem?

expand this thought.   think hard.  be awesome.

**CLAUDE:
## The Adapter Architecture for JIG

Let me build this out properly.

---

## 1. The Universal Schema: Bricks, Layers, Boundaries

First, the language-agnostic primitives that every ecosystem maps to:

```yaml
# jig/architecture.yaml - The Universal Schema

schema_version: "1.0"

# ============================================================
# BRICKS: Logical units of cohesive functionality
# ============================================================
bricks:
  - id: auth
    name: "Authentication Subsystem"
    description: "User identity, sessions, tokens"
    
    # WHERE does this brick live? (Adapter-specific)
    source:
      adapter: cmake
      target: libauth
      
    # WHAT is the public surface? (Context fence for agents)
    boundary:
      exports:
        - src/auth/include/auth.h
        - src/auth/include/session.h
      internals:
        - src/auth/impl/**
        
    # WHO owns this? (Human coordination)
    ownership:
      team: platform
      contacts: ["alice@co.com"]

  - id: network
    name: "Network Layer"
    source:
      adapter: cmake
      target: libnetwork
    boundary:
      exports:
        - src/network/include/*.h
      internals:
        - src/network/impl/**

# ============================================================
# LAYERS: Ordering relationships (what can use what)
# ============================================================
layers:
  - id: foundation
    description: "Core utilities, zero internal dependencies"
    bricks: [logging, errors, config]
    uses: []  # Foundation uses nothing
    
  - id: platform
    description: "Platform abstractions"
    bricks: [crypto, threading, storage]
    uses: [foundation]  # Can use foundation
    
  - id: domain
    description: "Business logic"
    bricks: [auth, billing, inventory]
    uses: [platform, foundation]  # Can use platform and foundation
    
  - id: services
    description: "Orchestration and external APIs"
    bricks: [api, webhooks, sync]
    uses: [domain, platform, foundation]  # Can use everything below

# ============================================================
# RULES: Constraints on the structure
# ============================================================
rules:
  # Layer rules
  - type: layer-order
    description: "Layers can only depend downward"
    mode: strict  # fail CI if violated
    
  # Brick rules  
  - type: brick-boundary
    description: "Internals are private"
    mode: warn  # warn but don't fail
    
  # Custom rules
  - type: no-circular
    scope: [auth, billing]
    description: "Auth and billing must not have circular deps"
    mode: strict
```

---

## 2. The Adapter Interface

Each adapter implements a simple contract:

```typescript
// The universal types
interface Brick {
  id: string;
  files: string[];           // All files in this brick
  exports: string[];         // Public interface files
  internals: string[];       // Private implementation files
  dependencies: string[];    // Other brick IDs this depends on
}

interface AdapterResult {
  bricks: Brick[];
  raw_dependencies: Edge[];  // Direct file-to-file deps (for validation)
  metadata: Record<string, unknown>;  // Adapter-specific info
}

// The adapter contract
interface Adapter {
  name: string;
  
  // Can this adapter handle this project?
  detect(projectRoot: string): Promise<boolean>;
  
  // Extract bricks and dependencies from native config
  extract(projectRoot: string, config: AdapterConfig): Promise<AdapterResult>;
  
  // Validate that declared structure matches reality
  validate(declared: Brick[], actual: AdapterResult): ValidationResult;
}
```

---

## 3. Adapter Implementations

### CMake Adapter (C/C++)

```typescript
// adapters/cmake.ts

class CMakeAdapter implements Adapter {
  name = "cmake";
  
  async detect(root: string): Promise<boolean> {
    return exists(`${root}/CMakeLists.txt`);
  }
  
  async extract(root: string, config: AdapterConfig): Promise<AdapterResult> {
    // Option 1: Parse CMakeLists.txt directly
    // Option 2: Run cmake --graphviz to get dependency graph
    // Option 3: Use cmake-file-api for structured output
    
    const targets = await parseCMakeTargets(root);
    
    return {
      bricks: targets.map(t => ({
        id: t.name,
        files: t.sources,
        exports: t.publicHeaders,
        internals: t.privateHeaders.concat(t.sources),
        dependencies: t.linkLibraries,
      })),
      raw_dependencies: await extractIncludeDeps(root),
      metadata: { cmake_version: targets.cmake_version }
    };
  }
}
```

**What CMake gives us:**

```cmake
add_library(libauth STATIC
    src/auth/token.cpp
    src/auth/session.cpp
)
target_include_directories(libauth
    PUBLIC  src/auth/include    # This is the boundary!
    PRIVATE src/auth/impl       # This is internal!
)
target_link_libraries(libauth
    PRIVATE libcrypto           # This is a dependency!
)
```

CMake already has bricks (targets), boundaries (PUBLIC/PRIVATE), and layers (link deps). We just read it.

---

### Rails Adapter (Ruby)

```typescript
// adapters/rails.ts

class RailsAdapter implements Adapter {
  name = "rails";
  
  async detect(root: string): Promise<boolean> {
    return exists(`${root}/config/application.rb`) && 
           exists(`${root}/Gemfile`);
  }
  
  async extract(root: string, config: AdapterConfig): Promise<AdapterResult> {
    // Rails has CONVENTIONAL layers
    const conventionalBricks = [
      {
        id: "models",
        files: glob("app/models/**/*.rb"),
        exports: glob("app/models/**/*.rb"),  // All public in Rails
        internals: [],
        dependencies: [],  // Models are the bottom
      },
      {
        id: "services",
        files: glob("app/services/**/*.rb"),
        exports: glob("app/services/**/*.rb"),
        internals: [],
        dependencies: ["models"],  // Services use models
      },
      {
        id: "controllers",
        files: glob("app/controllers/**/*.rb"),
        exports: glob("app/controllers/**/*.rb"),
        internals: [],
        dependencies: ["services", "models"],
      },
    ];
    
    // Also extract gems as external bricks
    const gems = parseGemfile(root);
    
    return {
      bricks: [...conventionalBricks, ...gemBricks(gems)],
      raw_dependencies: await extractRequireDeps(root),
      metadata: { rails_version: detectRailsVersion(root) }
    };
  }
}
```

**What Rails gives us:** The conventions ARE the architecture. We don't discover it - we enforce it:

- `app/models/` = persistence layer
- `app/services/` = domain layer
- `app/controllers/` = presentation layer
- `Gemfile` = external dependencies

---

### Go Adapter

```typescript
// adapters/go.ts

class GoAdapter implements Adapter {
  name = "go";
  
  async detect(root: string): Promise<boolean> {
    return exists(`${root}/go.mod`);
  }
  
  async extract(root: string, config: AdapterConfig): Promise<AdapterResult> {
    // Go is BEAUTIFUL for this
    // - Packages are bricks
    // - Imports are dependencies  
    // - Exported = Capitalized, internal = lowercase
    // - The compiler ENFORCES no circular deps
    
    const packages = await goListPackages(root);
    
    return {
      bricks: packages.map(pkg => ({
        id: pkg.importPath,
        files: pkg.goFiles,
        exports: pkg.exports,  // Capitalized symbols
        internals: pkg.internals,  // lowercase symbols
        dependencies: pkg.imports,
      })),
      raw_dependencies: packages.flatMap(p => 
        p.imports.map(i => ({ from: p.importPath, to: i }))
      ),
      metadata: { go_version: goModVersion(root) }
    };
  }
}
```

**What Go gives us:**

```
go list -json ./...
```

This literally gives us everything: packages, imports, exports. Go is the dream language for JIG.

---

### Cargo Adapter (Rust)

```typescript
// adapters/cargo.ts

class CargoAdapter implements Adapter {
  name = "cargo";
  
  async detect(root: string): Promise<boolean> {
    return exists(`${root}/Cargo.toml`);
  }
  
  async extract(root: string, config: AdapterConfig): Promise<AdapterResult> {
    // Cargo workspaces = bricks
    // Cargo.toml deps = dependencies
    // pub = exported, non-pub = internal
    
    const metadata = await exec("cargo metadata --format-version=1");
    
    return {
      bricks: metadata.packages.map(pkg => ({
        id: pkg.name,
        files: pkg.targets.flatMap(t => t.src_path),
        exports: await extractPubItems(pkg),
        internals: await extractPrivateItems(pkg),
        dependencies: pkg.dependencies.map(d => d.name),
      })),
      raw_dependencies: metadata.resolve.nodes.flatMap(n =>
        n.deps.map(d => ({ from: n.id, to: d.pkg }))
      ),
      metadata: { rust_edition: metadata.packages[0].edition }
    };
  }
}
```

---

### NPM/TypeScript Adapter

```typescript
// adapters/npm.ts

class NpmAdapter implements Adapter {
  name = "npm";
  
  async detect(root: string): Promise<boolean> {
    return exists(`${root}/package.json`);
  }
  
  async extract(root: string, config: AdapterConfig): Promise<AdapterResult> {
    // For monorepos: workspaces = bricks
    // For single packages: directories = bricks (convention)
    
    const pkg = readPackageJson(root);
    
    if (pkg.workspaces) {
      // Monorepo: each workspace is a brick
      return extractWorkspaces(root, pkg.workspaces);
    } else {
      // Single package: use barrel files as boundaries
      // src/auth/index.ts = auth brick exports
      // src/network/index.ts = network brick exports
      return extractFromBarrels(root, config);
    }
  }
}
```

**What NPM gives us:**

- `package.json` workspaces for monorepos
- Barrel files (`index.ts`) as boundaries
- `madge` or `dependency-cruiser` for import graph

---

## 4. The Detection + Fallback Chain

```typescript
// core/detect.ts

async function detectProject(root: string): Promise<Adapter[]> {
  const allAdapters = [
    new GoAdapter(),
    new CargoAdapter(),
    new CMakeAdapter(),
    new RailsAdapter(),
    new NpmAdapter(),
    new MavenAdapter(),
    new GradleAdapter(),
    new PoetryAdapter(),
    // ... more
  ];
  
  const detected = await Promise.all(
    allAdapters.map(async a => ({
      adapter: a,
      detected: await a.detect(root)
    }))
  );
  
  return detected.filter(d => d.detected).map(d => d.adapter);
}

// A project can have MULTIPLE adapters
// e.g., C++ with CMake + Python bindings with Poetry
```

---

## 5. The Composition Model

Real projects aren't monolithic. They're composed:

```yaml
# jig/architecture.yaml

# A complex project might have multiple ecosystems
adapters:
  - name: cmake
    root: ./core           # C++ core
    prefix: "core::"       # Brick IDs: core::auth, core::network
    
  - name: npm
    root: ./web            # TypeScript frontend
    prefix: "web::"        # Brick IDs: web::components, web::api
    
  - name: poetry
    root: ./ml             # Python ML pipeline
    prefix: "ml::"         # Brick IDs: ml::training, ml::inference

# Cross-ecosystem dependencies
bridges:
  - from: web::api
    to: core::network
    via: grpc              # How they communicate
    
  - from: ml::inference
    to: core::model
    via: ffi               # Python calls C++ via FFI

# Unified layers across ecosystems
layers:
  - id: platform
    bricks: 
      - core::logging
      - core::crypto
      
  - id: domain
    bricks:
      - core::auth
      - ml::inference
    uses: [platform]
    
  - id: services
    bricks:
      - core::api
      - web::api
    uses: [domain]
```

---

## 6. What This Enables for AI Agents

### Automatic Context Fencing

```typescript
// When AI agent is assigned to work on a brick

async function getBrickContext(brickId: string): Promise<AgentContext> {
  const architecture = loadArchitecture();
  const brick = architecture.getBrick(brickId);
  
  return {
    // The agent can see/modify these
    workingSet: brick.files,
    
    // The agent can read these (interfaces of dependencies)
    readOnly: brick.dependencies.flatMap(d => 
      architecture.getBrick(d).exports
    ),
    
    // The agent cannot see these (other bricks' internals)
    invisible: architecture.bricks
      .filter(b => b.id !== brickId && !brick.dependencies.includes(b.id))
      .flatMap(b => b.internals),
      
    // Specs that apply to this brick
    specifications: getSpecsForBrick(brickId),
    
    // Tests that verify this brick
    tests: getTestsForBrick(brickId),
  };
}
```

### Automatic Work Ordering

```typescript
// When planning a large change that spans bricks

function planWorkOrder(affectedBricks: string[]): WorkPlan {
  const architecture = loadArchitecture();
  
  // Topological sort based on layers
  const ordered = topologicalSort(
    affectedBricks,
    (a, b) => architecture.dependsOn(a, b)
  );
  
  return {
    phases: ordered.map((brickId, index) => ({
      phase: index + 1,
      brick: brickId,
      layer: architecture.getLayer(brickId),
      blockedBy: architecture.getDependencies(brickId)
        .filter(d => affectedBricks.includes(d)),
    })),
    
    // Which phases can run in parallel
    parallelGroups: groupByLayer(ordered, architecture),
  };
}
```

Example output:

```yaml
work_plan:
  phases:
    - phase: 1
      parallel_group: A
      bricks: [core::crypto, core::logging]
      layer: foundation
      blocked_by: []
      
    - phase: 2
      parallel_group: B
      bricks: [core::auth]
      layer: platform
      blocked_by: [core::crypto]
      
    - phase: 3
      parallel_group: C
      bricks: [web::api, core::api]
      layer: services
      blocked_by: [core::auth]
```

### Specification Scoping

```yaml
# Specs can now declare which brick they apply to

---
id: S-AUTH-001
type: specification
title: "JWT tokens with 24-hour expiration"
scope:
  brick: core::auth          # This spec applies to this brick
  layer: platform            # And this layer
  
# JIG validates:
# - Code implementing S-AUTH-001 is in core::auth brick
# - Tests for S-AUTH-001 can see core::auth's exports
# - Changes to S-AUTH-001 trigger validation of core::auth
---
```

---

## 7. The Validation Engine

The adapters extract reality. JIG validates that reality matches intent:

```typescript
// core/validate.ts

async function validateArchitecture(root: string): Promise<ValidationResult> {
  const architecture = loadArchitecture(root);
  const adapters = await detectProject(root);
  
  // Extract actual structure from each adapter
  const actual = await Promise.all(
    adapters.map(a => a.extract(root, architecture.getAdapterConfig(a.name)))
  );
  
  const violations: Violation[] = [];
  
  // 1. Layer violations
  for (const edge of actual.flatMap(a => a.raw_dependencies)) {
    const fromLayer = architecture.getLayer(edge.from);
    const toLayer = architecture.getLayer(edge.to);
    
    if (!architecture.canUse(fromLayer, toLayer)) {
      violations.push({
        type: "layer-violation",
        message: `${edge.from} (${fromLayer}) depends on ${edge.to} (${toLayer})`,
        severity: architecture.getRuleSeverity("layer-order"),
        file: edge.sourceFile,
        line: edge.sourceLine,
      });
    }
  }
  
  // 2. Boundary violations
  for (const edge of actual.flatMap(a => a.raw_dependencies)) {
    const targetBrick = architecture.getBrickForFile(edge.to);
    if (targetBrick && targetBrick.isInternal(edge.to)) {
      violations.push({
        type: "boundary-violation",
        message: `${edge.from} imports internal file ${edge.to}`,
        severity: architecture.getRuleSeverity("brick-boundary"),
        file: edge.sourceFile,
        line: edge.sourceLine,
      });
    }
  }
  
  // 3. Circular dependency detection
  const cycles = detectCycles(actual.flatMap(a => a.raw_dependencies));
  for (const cycle of cycles) {
    violations.push({
      type: "circular-dependency",
      message: `Cycle detected: ${cycle.join(" → ")}`,
      severity: "error",
    });
  }
  
  return { violations, metrics: computeMetrics(actual) };
}
```

---

## 8. The CLI Experience

```bash
# Auto-detect project type and extract architecture
$ jig init
Detected: cmake (./core), npm (./web), poetry (./ml)
Created: jig/architecture.yaml (review and customize)

# Validate current state
$ jig validate
✓ Layer ordering valid
✓ Brick boundaries respected
✗ Violation: web::api imports core::auth/internal/token.cpp
  → Boundary violation: internal file accessed from outside brick
  
# Show architecture overview
$ jig architecture
Layers (4):
  foundation → platform → domain → services

Bricks (12):
  foundation: core::logging, core::errors
  platform:   core::crypto, core::auth, core::storage  
  domain:     ml::inference, core::model
  services:   web::api, core::api, web::components

Adapters (3):
  cmake:  ./core (8 bricks)
  npm:    ./web (3 bricks)
  poetry: ./ml (1 brick)

# Plan work order for a change
$ jig plan --affecting "core::auth,web::api,ml::inference"
Phase 1 (parallel): core::auth
Phase 2 (parallel): ml::inference, web::api
  
# Get context for AI agent
$ jig context --brick core::auth
Working set: 12 files (src/auth/*)
Read-only:   4 files (crypto.h, logging.h, errors.h, config.h)
Specs:       S-AUTH-001, S-AUTH-002, S-AUTH-003
Tests:       T-AUTH-001, T-AUTH-002
Layer:       platform
Dependencies: core::crypto, core::logging
Dependents:  ml::inference, web::api, core::api
```

---

## 9. The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                     JIG Universal Schema                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │ Bricks  │  │ Layers  │  │ Rules   │  │ Bridges │            │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ maps to
                              │
┌─────────────────────────────────────────────────────────────────┐
│                        Adapter Layer                             │
│  ┌───────┐ ┌───────┐ ┌───────┐ ┌─────┐ ┌───────┐ ┌─────────┐  │
│  │ CMake │ │ Cargo │ │  Go   │ │ NPM │ │ Maven │ │  Rails  │  │
│  └───────┘ └───────┘ └───────┘ └─────┘ └───────┘ └─────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ reads
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     Native Ecosystem                             │
│  ┌─────────────┐ ┌──────────┐ ┌────────┐ ┌─────────────────┐   │
│  │CMakeLists.txt│ │Cargo.toml│ │ go.mod │ │ package.json    │   │
│  │ + link deps │ │ + crates │ │ + pkgs │ │ + workspaces    │   │
│  └─────────────┘ └──────────┘ └────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Why This Changes Everything

**Before (the wrong question):**

> "How do we parse C++ to extract dependencies?" Answer: Pain. Suffering. Incomplete results.

**After (the right question):**

> "What do C++ developers already use to express structure?" Answer: CMake. We just read it.

**The insight:** Every mature ecosystem has already solved the "how do we organize code" problem. They've built tools (CMake, Cargo, Go modules, npm workspaces) that encode architectural decisions.

JIG doesn't reinvent this. JIG:

1. **Reads** what's already there
2. **Unifies** into a common schema
3. **Validates** against declared intent
4. **Enables** AI agents to work within boundaries

**The power:**

- Works with ANY language that has a build system
- No complex parsing of code
- Leverages decades of ecosystem tooling
- Scales from simple (one Go module) to complex (C++ + Python + TypeScript monorepo)

---

**Next step:** Pick two adapters to build first (I'd suggest Go + NPM/TypeScript), validate the universal schema works for both, then expand.

Want me to draft the actual adapter implementations?