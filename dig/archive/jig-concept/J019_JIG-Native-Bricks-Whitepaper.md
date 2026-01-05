---
title: "JIG: Native Bricks"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1764980842
created_human: "2025-12-05 18:27 CST"
parent: "[[J017_JIG-Concept-v9]]"
children: []
---
# JIG: Native Bricks
## Automatic Subsystem Discovery Through Language-Native Structures

**Version:** 1.0  
**Date:** December 2025  
**Authors:** Jim & Claude  
**Status:** Architecture Proposal  
**Builds On:** JIG: When in Rome (v1.0)

---

## Executive Summary

This whitepaper extends the "When in Rome" principle to address a fundamental question: **How do we automatically discover and propose brick boundaries in any programming language?**

The answer lies in recognizing two distinct concepts:

1. **Bricks** are logical containers—organizational units that group related functionality
2. **Brick Members** are the native language constructs that live inside bricks—functions, classes, types, and interfaces

Every mature programming ecosystem already has mechanisms for grouping code: build targets, packages, modules, or framework conventions. Rather than inventing new analysis algorithms, JIG reads these native structures to propose brick boundaries automatically.

Three fundamental strategies cover all mainstream languages:

| Strategy | Brick Source | Layer Source | Languages |
|----------|-------------|--------------|-----------|
| **Build Target** | Build system targets | Target dependencies | C, C++, Swift, Kotlin, Java, C#, Rust |
| **Package** | Language packages/modules | Import graph | Go, Python, TypeScript, Java, Rust |
| **Convention** | Directory patterns | Prescribed rules | Ruby/Rails, Django |

This document provides a complete reference for implementing automatic brick discovery across 12 programming languages.

---

## Table of Contents

1. [Bricks and Brick Members](#1-bricks-and-brick-members)
2. [Brick Members by Language](#2-brick-members-by-language)
3. [Native Structures for Boundary Discovery](#3-native-structures-for-boundary-discovery)
4. [The Three Strategies](#4-the-three-strategies)
5. [The Universal Algorithm](#5-the-universal-algorithm)
6. [Language Reference Guide](#6-language-reference-guide)
7. [Practical Implications](#7-practical-implications)
8. [Conclusion](#8-conclusion)

---

## 1. Bricks and Brick Members

### 1.1 The Fundamental Distinction

A common source of confusion in architectural discussions is conflating containers with their contents. JIG makes a clear distinction:

**Bricks** are logical containers defined by JIG. They represent cohesive units of functionality—what Herbert Simon called "nearly decomposable" subsystems. Bricks:

- Group related functionality together
- Have clear boundaries (public interface vs internal implementation)
- Participate in layer relationships (what can depend on what)
- Serve as context fences for AI agents

**Brick Members** are the native language constructs that live inside bricks. They are what developers actually write—functions, classes, interfaces, types. Brick members:

- Are written in the native language syntax
- Can be annotated with JIG markers (`@implements`, `@verifies`)
- Have language-native visibility (public, internal, private)
- Form the S-F-T (Specification-Function-Test) triangle

### 1.2 The Hierarchy

```
Brick (logical, defined by JIG)
│
├── Contains: Brick Members (native language objects)
│   ├── Functions
│   ├── Classes
│   ├── Interfaces / Protocols / Traits
│   ├── Types / Structs / Enums
│   └── Methods
│
└── Often aligns with: Grouping Constructs (native organization)
    ├── Build Targets (CMake, Cargo, SPM, Gradle)
    ├── Packages (Go, Python, Java)
    ├── Modules (Rust, TypeScript)
    └── Conventions (Rails directories)
```

### 1.3 Why This Distinction Matters

Understanding this distinction enables automatic discovery:

1. **Grouping constructs** tell us where brick boundaries are
2. **Brick members** tell us what participates in the S-F-T triangle
3. **Dependencies between grouping constructs** tell us layer ordering

JIG doesn't need complex graph analysis algorithms—it reads native structures that developers already create and maintain.

---

## 2. Brick Members by Language

### 2.1 Summary Table

| Language | Primary Brick Members | Secondary Members | Spec-as-Interface |
|----------|----------------------|-------------------|-------------------|
| **Python** | Functions, Classes | Methods, Modules | ✗ (duck typing) |
| **Java** | Classes, Interfaces | Methods, Enums | ✓ |
| **Kotlin** | Classes, Interfaces, Top-level Functions | Methods, Objects | ✓✓✓ |
| **Swift** | Classes, Structs, Protocols, Functions | Methods, Enums | ✓✓✓ |
| **Go** | Functions, Types (struct, interface) | Methods | ✓ |
| **Rust** | Functions, Structs, Traits, Enums | Methods, Impls | ✓ |
| **TypeScript** | Functions, Classes, Interfaces | Methods, Types | ✓ |
| **JavaScript** | Functions, Classes | Methods | ✓ (weak) |
| **Ruby** | Classes, Modules | Methods | ✗ |
| **C** | Functions, Structs | Typedefs | ✗ |
| **C++** | Classes, Functions, Structs | Methods, Templates | ✓ (concepts) |
| **C#** | Classes, Interfaces, Structs | Methods, Enums | ✓ |

### 2.2 Detailed Breakdown by Language

#### Python

| Member Type | Annotatable | Visibility | S-F-T Role |
|-------------|-------------|------------|------------|
| **Function** | `@implements` | Convention (`_prefix`) | F (implementation) |
| **Class** | `@implements` | Convention | F (implementation) |
| **Method** | `@implements` | Convention | F (implementation) |

```python
@implements("S-AUTH-001")
class Authenticator:                  # ← Brick member (class)
    
    @implements("S-AUTH-002")
    def validate(self, token):        # ← Brick member (method)
        pass

@verifies("S-AUTH-001")
def test_authenticator():             # ← Brick member (test function)
    pass
```

#### Java

| Member Type | Annotatable | Visibility | S-F-T Role |
|-------------|-------------|------------|------------|
| **Interface** | `@Spec` | public/package | S (specification) |
| **Class** | `@Implements` | All levels | F (implementation) |
| **Method** | `@Implements` | All levels | F (implementation) |

```java
@Spec("S-AUTH-001")
public interface Authenticator {      // ← Brick member (interface as spec)
    Token validate(String token);
}

@Implements("S-AUTH-001")
public class JWTAuthenticator         // ← Brick member (class)
        implements Authenticator {
    
    @Override
    public Token validate(String token) {
        // ...
    }
}
```

#### Kotlin

| Member Type | Annotatable | Visibility | S-F-T Role |
|-------------|-------------|------------|------------|
| **Interface** | `@Spec` | All levels | S (specification) |
| **Class** | `@Implements` | All levels | F (implementation) |
| **Top-level Function** | `@Implements` | All levels | F (implementation) |
| **Object** | `@Implements` | All levels | F (implementation) |

```kotlin
@Spec("S-AUTH-001")
interface Authenticator {             // ← Brick member (interface as spec)
    suspend fun validate(token: String): Token
}

@Implements("S-AUTH-001")
class JWTAuthenticator : Authenticator {  // ← Brick member (class)
    override suspend fun validate(token: String): Token {
        // ...
    }
}

@Implements("S-HASH-001")
fun hashPassword(pw: String): ByteArray {  // ← Brick member (top-level function)
    // ...
}
```

#### Swift

| Member Type | Annotatable | Visibility | S-F-T Role |
|-------------|-------------|------------|------------|
| **Protocol** | `@Spec` | All levels | S (specification) |
| **Class/Struct** | `@Implements` | All levels | F (implementation) |
| **Function** | `@Implements` | All levels | F (implementation) |

```swift
@Spec("S-AUTH-001")
protocol Authenticator {              // ← Brick member (protocol as spec)
    func validate(token: String) throws -> Token
}

@Implements("S-AUTH-001")
struct JWTAuthenticator: Authenticator {  // ← Brick member (struct)
    func validate(token: String) throws -> Token {
        // ...
    }
}

@Implements("S-HASH-001")
func hashPassword(_ password: String) -> Data {  // ← Brick member (function)
    // ...
}
```

#### Go

| Member Type | Annotatable | Visibility | S-F-T Role |
|-------------|-------------|------------|------------|
| **Interface** | `//jig:spec` | Exported/unexported | S (specification) |
| **Struct** | `//jig:implements` | Exported/unexported | F (implementation) |
| **Function** | `//jig:implements` | Exported/unexported | F (implementation) |

```go
//jig:spec S-AUTH-001
type Authenticator interface {        // ← Brick member (interface as spec)
    Validate(token string) (*Token, error)
}

//jig:implements S-AUTH-001
type JWTAuthenticator struct {        // ← Brick member (struct)
    // ...
}

//jig:implements S-AUTH-001
func (a *JWTAuthenticator) Validate(token string) (*Token, error) {
    // ...
}
```

#### Rust

| Member Type | Annotatable | Visibility | S-F-T Role |
|-------------|-------------|------------|------------|
| **Trait** | `#[spec]` | `pub`/`pub(crate)` | S (specification) |
| **Struct** | `#[implements]` | All levels | F (implementation) |
| **Function** | `#[implements]` | All levels | F (implementation) |
| **Impl block** | `#[implements]` | — | F (implementation) |

```rust
#[spec("S-AUTH-001")]
pub trait Authenticator {             // ← Brick member (trait as spec)
    fn validate(&self, token: &str) -> Result<Token, AuthError>;
}

#[implements("S-AUTH-001")]
pub struct JWTAuthenticator {         // ← Brick member (struct)
    // ...
}

#[implements("S-AUTH-001")]
impl Authenticator for JWTAuthenticator {
    fn validate(&self, token: &str) -> Result<Token, AuthError> {
        // ...
    }
}
```

#### TypeScript

| Member Type | Annotatable | Visibility | S-F-T Role |
|-------------|-------------|------------|------------|
| **Interface** | JSDoc `@jig spec` | `export` | S (specification) |
| **Class** | JSDoc/Decorator | `export` | F (implementation) |
| **Function** | JSDoc/Decorator | `export` | F (implementation) |

```typescript
/**
 * @jig spec S-AUTH-001
 */
export interface Authenticator {      // ← Brick member (interface as spec)
    validate(token: string): Token;
}

/**
 * @jig implements S-AUTH-001
 */
export class JWTAuthenticator implements Authenticator {
    validate(token: string): Token {
        // ...
    }
}
```

#### C

| Member Type | Annotatable | Visibility | S-F-T Role |
|-------------|-------------|------------|------------|
| **Function** | Doxygen/pragma | Header exposure | F (implementation) |
| **Struct** | Doxygen/pragma | Header exposure | F (implementation) |

```c
/**
 * @jig implements S-AUTH-001
 */
Token* authenticator_validate(        // ← Brick member (function)
    Authenticator* auth,
    const char* token
);

// Internal (static = brick-private)
static int parse_jwt(const char* token) {
    // ...
}
```

#### C++

| Member Type | Annotatable | Visibility | S-F-T Role |
|-------------|-------------|------------|------------|
| **Concept** (C++20) | `[[jig::spec]]` | — | S (specification) |
| **Class** | `[[jig::implements]]` | public/private | F (implementation) |
| **Function** | `[[jig::implements]]` | Header exposure | F (implementation) |

```cpp
// C++20 concept as spec
template<typename T>
[[jig::spec("S-AUTH-001")]]
concept Authenticator = requires(T t, std::string token) {
    { t.validate(token) } -> std::same_as<Token>;
};

[[jig::implements("S-AUTH-001")]]
class JWTAuthenticator {              // ← Brick member (class)
public:
    Token validate(const std::string& token);
};
```

#### C#

| Member Type | Annotatable | Visibility | S-F-T Role |
|-------------|-------------|------------|------------|
| **Interface** | `[Spec]` | public/internal | S (specification) |
| **Class** | `[Implements]` | All levels | F (implementation) |
| **Struct** | `[Implements]` | All levels | F (implementation) |

```csharp
[Spec("S-AUTH-001")]
public interface IAuthenticator       // ← Brick member (interface as spec)
{
    Token Validate(string token);
}

[Implements("S-AUTH-001")]
public class JWTAuthenticator : IAuthenticator
{
    public Token Validate(string token)
    {
        // ...
    }
}
```

#### Ruby

| Member Type | Annotatable | Visibility | S-F-T Role |
|-------------|-------------|------------|------------|
| **Class** | DSL | — | F (implementation) |
| **Module** | DSL | — | F (mixin) |
| **Method** | DSL | public/protected/private | F (implementation) |

```ruby
class Authenticator                   # ← Brick member (class)
  extend Jig::Annotations
  
  implements "S-AUTH-001"
  def validate(token)                 # ← Brick member (method)
    # ...
  end
end
```

---

## 3. Native Structures for Boundary Discovery

### 3.1 The Key Insight

The original JIG concept proposed using graph analysis algorithms (Newman-Girvan community detection, coupling ratios, modularity scores) to discover subsystem boundaries. 

**This approach was solving a problem that mature ecosystems have already solved.**

Every mainstream programming language has native mechanisms for organizing code into logical groups. These mechanisms exist because developers need them—and they've been refined over decades. JIG should read these structures, not reinvent them.

### 3.2 Native Grouping Mechanisms by Language

| Language | Primary Grouping | Secondary Grouping | Visibility System |
|----------|-----------------|-------------------|-------------------|
| **Go** | Packages (directories) | Modules (`go.mod`) | Capitalization |
| **Rust** | Crates (`Cargo.toml`) | Modules (`mod.rs`) | `pub`/`pub(crate)` |
| **Swift** | SPM Targets | Files | `public`/`internal` |
| **Kotlin** | Gradle Modules | Packages | `public`/`internal` |
| **Java** | Maven/Gradle Modules | Packages | Package-private |
| **C#** | Projects (`.csproj`) | Namespaces | `public`/`internal` |
| **TypeScript** | npm Workspaces | Files (barrels) | `export` |
| **Python** | Packages (`__init__.py`) | Modules (files) | Convention (`_`) |
| **C/C++** | Build Targets | Headers/Namespaces | Header exposure |
| **Ruby** | Gems | Modules/Classes | Convention |

### 3.3 Dependency Information Sources

| Language | Dependency Declaration | Extracted From |
|----------|----------------------|----------------|
| **Go** | `import "path"` | `go list -json` |
| **Rust** | `[dependencies]` | `cargo metadata` |
| **Swift** | `dependencies: [.target()]` | `swift package describe` |
| **Kotlin** | `implementation(project())` | Gradle API |
| **Java** | `<dependency>` / `implementation` | Maven/Gradle |
| **C#** | `<ProjectReference>` | MSBuild |
| **TypeScript** | `"dependencies"` / `import` | `package.json` + AST |
| **Python** | `import` | AST analysis |
| **C/C++** | `target_link_libraries()` | CMake/Bazel |
| **Ruby** | `gem` / `require` | Bundler + AST |

### 3.4 Compiler-Enforced Boundaries

Some languages have visibility systems that the **compiler enforces**. This is powerful—JIG doesn't need to validate boundaries; the compiler already does.

| Language | Boundary Keyword | Scope | Compiler Enforced? |
|----------|-----------------|-------|-------------------|
| **Go** | Capitalization | Package | ✓ (strictly) |
| **Rust** | `pub(crate)` | Crate | ✓ |
| **Swift** | `internal` | Module/Target | ✓ |
| **Kotlin** | `internal` | Gradle Module | ✓ |
| **C#** | `internal` | Assembly/Project | ✓ |
| **Java** | Package-private | Package | ✓ (weakly) |
| **TypeScript** | `export` | Module | ✗ (convention) |
| **Python** | `_prefix` | — | ✗ (convention) |
| **C/C++** | Header exposure | — | ✗ (convention) |
| **Ruby** | `private` | Class | ✗ (bypassable) |

---

## 4. The Three Strategies

### 4.1 Strategy Overview

Analysis of all 12 languages reveals that three fundamental strategies cover all cases:

```
┌─────────────────────────────────────────────────────────────────┐
│                    STRATEGY SELECTION                            │
│                                                                  │
│  Does project have explicit build modules?                       │
│  (Gradle, Maven, SPM, CMake, Cargo workspace, npm workspace)     │
│      │                                                           │
│      ├── YES → BUILD TARGET STRATEGY                             │
│      │                                                           │
│      └── NO → Does language have package/module system?          │
│               (Go packages, Python packages, Rust modules)       │
│                   │                                              │
│                   ├── YES → PACKAGE STRATEGY                     │
│                   │                                              │
│                   └── NO → Is it a framework project?            │
│                            (Rails, Django, Angular)              │
│                                │                                 │
│                                ├── YES → CONVENTION STRATEGY     │
│                                │                                 │
│                                └── NO → FALLBACK (directories)   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Strategy 1: Build Target Strategy

**Core Principle:** The build system defines targets. Each target is a brick. Members belong to whichever target compiles them.

```
Build Target = Brick
Source files in target = Brick members  
Target dependencies = Layer relationships
```

#### Applicable Languages

| Language | Build System | Target Declaration | Dependency Declaration |
|----------|--------------|-------------------|----------------------|
| **C** | CMake | `add_library()` | `target_link_libraries()` |
| **C++** | CMake/Bazel | `add_library()` | `target_link_libraries()` |
| **Swift** | SPM | `.target(name:)` | `dependencies: []` |
| **Kotlin** | Gradle | `include(":module")` | `implementation(project())` |
| **Java** | Maven/Gradle | `<module>` | `<dependency>` |
| **C#** | MSBuild | `.csproj` file | `<ProjectReference>` |
| **Rust** | Cargo | `[package]` (workspace) | `[dependencies]` |

#### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                       BUILD SYSTEM                               │
│  CMakeLists.txt / Package.swift / build.gradle.kts              │
└─────────────────────────────────────────────────────────────────┘
                              │
                    Parse build config
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         TARGETS                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  libauth    │  │ libnetwork  │  │   libcore   │             │
│  │             │  │             │  │             │             │
│  │ src/auth/*  │  │  src/net/*  │  │ src/core/*  │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                          BRICKS                                  │
│     Brick: auth      Brick: network     Brick: core             │
└─────────────────────────────────────────────────────────────────┘
                              │
                    Extract dependencies
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER DERIVATION                             │
│                                                                  │
│  From: target_link_libraries(libauth PRIVATE libcore)           │
│  From: target_link_libraries(libnetwork PRIVATE libcore)        │
│                                                                  │
│  Derived layers:                                                 │
│    Layer 0: core (no deps)                                       │
│    Layer 1: auth, network (depend on core)                       │
└─────────────────────────────────────────────────────────────────┘
```

#### Example: Swift Package Manager

```swift
// Package.swift
let package = Package(
    name: "MyApp",
    targets: [
        .target(name: "Core"),                            // Brick: Core
        .target(name: "Auth", dependencies: ["Core"]),    // Brick: Auth
        .target(name: "Network", dependencies: ["Core"]), // Brick: Network
        .target(name: "App", dependencies: ["Auth", "Network"]),
    ]
)
```

**JIG extracts:**
```yaml
bricks:
  - id: Core
    source: { adapter: spm, target: "Core" }
  - id: Auth
    source: { adapter: spm, target: "Auth" }
  - id: Network
    source: { adapter: spm, target: "Network" }
  - id: App
    source: { adapter: spm, target: "App" }

layers:
  - id: foundation
    bricks: [Core]
  - id: platform
    bricks: [Auth, Network]
    uses: [foundation]
  - id: application
    bricks: [App]
    uses: [platform, foundation]
```

#### Member Assignment

**Rule:** A source file belongs to whichever target includes it. All members in that file belong to that brick.

```cmake
add_library(libauth
    src/auth/authenticator.cpp    # All members → Brick: auth
    src/auth/token.cpp            # All members → Brick: auth
    src/auth/session.cpp          # All members → Brick: auth
)
```

### 4.3 Strategy 2: Package Strategy

**Core Principle:** The language's native package/module system defines groupings. Each package is a brick. Members belong to whichever package declares them.

```
Package = Brick
Symbols in package = Brick members
Import graph = Layer relationships
```

#### Applicable Languages

| Language | Package Mechanism | Package Declaration | Dependency via |
|----------|------------------|--------------------| --------------|
| **Go** | Directories | `package foo` | `import` |
| **Python** | Directories | `__init__.py` | `import` |
| **Rust** | Modules | `mod foo;` | `use` |
| **Java** | Packages | `package com.foo;` | `import` |
| **TypeScript** | Files/Barrels | `export` | `import` |

#### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                       FILE SYSTEM                                │
│  myapp/                                                          │
│  ├── auth/                                                       │
│  │   ├── __init__.py          ← Package marker                  │
│  │   ├── authenticator.py                                        │
│  │   └── token.py                                                │
│  ├── network/                                                    │
│  │   ├── __init__.py          ← Package marker                  │
│  │   └── client.py                                               │
│  └── core/                                                       │
│      ├── __init__.py          ← Package marker                  │
│      └── config.py                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                    Scan for packages
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         PACKAGES                                 │
│     myapp.auth         myapp.network        myapp.core          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          BRICKS                                  │
│     Brick: auth        Brick: network       Brick: core         │
└─────────────────────────────────────────────────────────────────┘
                              │
                    Analyze import graph
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER DERIVATION                             │
│                                                                  │
│  From: auth/authenticator.py imports myapp.core.config          │
│  From: network/client.py imports myapp.core.config              │
│                                                                  │
│  Derived layers:                                                 │
│    Layer 0: core (no internal deps)                              │
│    Layer 1: auth, network (depend on core)                       │
└─────────────────────────────────────────────────────────────────┘
```

#### Example: Go

```
myapp/
├── go.mod                    # module github.com/company/myapp
├── auth/
│   ├── authenticator.go      # package auth
│   └── token.go              # package auth
├── network/
│   └── client.go             # package network
└── core/
    └── config.go             # package core
```

```go
// auth/authenticator.go
package auth

import "github.com/company/myapp/core"  // ← Dependency

type Authenticator struct { ... }        // ← Brick member
```

**JIG extracts via `go list -json ./...`:**
```yaml
bricks:
  - id: auth
    source: { adapter: go, package: "github.com/company/myapp/auth" }
  - id: network
    source: { adapter: go, package: "github.com/company/myapp/network" }
  - id: core
    source: { adapter: go, package: "github.com/company/myapp/core" }

layers:
  - id: foundation
    bricks: [core]
  - id: platform
    bricks: [auth, network]
    uses: [foundation]
```

#### Member Assignment

**Rule:** A symbol belongs to whichever package declares it.

```go
package auth  // ← All members in this file belong to "auth" brick

type Authenticator struct {}  // → Brick: auth
func Validate() {}            // → Brick: auth
func newToken() {}            // → Brick: auth (internal)
```

### 4.4 Strategy 3: Convention Strategy

**Core Principle:** Framework conventions prescribe where code lives and how it flows. Directory patterns define bricks. Prescribed rules define layers.

```
Directory pattern = Brick
Files matching pattern = Brick members
Framework rules = Layer relationships (prescribed, not derived!)
```

#### Applicable Languages/Frameworks

| Language | Framework | Convention Source |
|----------|-----------|------------------|
| **Ruby** | Rails | `app/models/`, `app/controllers/`, etc. |
| **Python** | Django | `models.py`, `views.py`, etc. |
| **TypeScript** | Angular | `*.component.ts`, `*.service.ts`, etc. |

#### Key Difference: Prescribed vs Derived

| Aspect | Build/Package Strategy | Convention Strategy |
|--------|----------------------|---------------------|
| **Layers** | Derived from actual dependencies | Prescribed by framework rules |
| **Validation** | "Does A depend on B?" | "Is A *allowed* to depend on B?" |
| **Violations** | Circular dependencies | Layer skipping, wrong direction |

#### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAILS CONVENTIONS                             │
│  app/                                                            │
│  ├── models/              ← Pattern: app/models/**/*.rb         │
│  │   ├── user.rb                                                 │
│  │   └── post.rb                                                 │
│  ├── services/            ← Pattern: app/services/**/*.rb       │
│  │   ├── auth_service.rb                                         │
│  │   └── post_service.rb                                         │
│  └── controllers/         ← Pattern: app/controllers/**/*.rb    │
│      ├── users_controller.rb                                     │
│      └── posts_controller.rb                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                    Match patterns
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          BRICKS                                  │
│   Brick: models       Brick: services      Brick: controllers   │
│   (persistence)       (domain)             (presentation)       │
└─────────────────────────────────────────────────────────────────┘
                              │
                    Apply prescribed rules
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER RULES (PRESCRIBED)                     │
│                                                                  │
│  Rails convention says:                                          │
│    controllers → services → models                               │
│                                                                  │
│  Layer rules:                                                    │
│    - controllers MAY use: services, models                       │
│    - services MAY use: models                                    │
│    - models MAY use: (nothing internal)                          │
│                                                                  │
│  Violation example:                                              │
│    controller directly queries model (skips service layer)       │
└─────────────────────────────────────────────────────────────────┘
```

#### Example: Rails Configuration

```yaml
# jig/architecture.yaml
adapter: rails

brick_patterns:
  models:
    patterns: ["app/models/**/*.rb"]
    layer: persistence
    
  services:
    patterns: ["app/services/**/*.rb", "app/policies/**/*.rb"]
    layer: domain
    
  controllers:
    patterns: ["app/controllers/**/*.rb"]
    layer: presentation

layer_rules:
  presentation:
    may_use: [domain, persistence]
  domain:
    may_use: [persistence]
  persistence:
    may_use: []
```

#### Member Assignment

**Rule:** A file matches whichever pattern applies. All members in that file belong to that brick.

```ruby
# app/services/auth_service.rb  →  matches app/services/**/*.rb
#                               →  Brick: services

class AuthService           # → Brick: services
  def authenticate(user)    # → Brick: services  
    # ...
  end
end
```

### 4.5 Hybrid Strategies

Some languages/projects require combining strategies:

#### TypeScript: Workspace + Package Hybrid

```
┌─────────────────────────────────────────────────────────────────┐
│  MONOREPO (npm workspaces) → Build Target Strategy              │
│                                                                  │
│  packages/                                                       │
│  ├── @company/core/       ← Brick from workspace                │
│  ├── @company/auth/       ← Brick from workspace                │
│  └── @company/api/        ← Brick from workspace                │
│                                                                  │
│  Layers from package.json dependencies                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  SINGLE PACKAGE → Package Strategy (barrel files)               │
│                                                                  │
│  src/                                                            │
│  ├── auth/                                                       │
│  │   └── index.ts         ← Barrel defines brick boundary       │
│  ├── network/                                                    │
│  │   └── index.ts         ← Barrel defines brick boundary       │
│  └── core/                                                       │
│      └── index.ts         ← Barrel defines brick boundary       │
│                                                                  │
│  Layers from import graph                                        │
└─────────────────────────────────────────────────────────────────┘
```

#### Java: Module + Package Hybrid

```
┌─────────────────────────────────────────────────────────────────┐
│  MULTI-MODULE PROJECT → Build Target Strategy                   │
│                                                                  │
│  auth-module/             ← Brick from Maven/Gradle module      │
│  ├── pom.xml                                                     │
│  └── src/com/company/auth/                                       │
│                                                                  │
│  Layers from module dependencies                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  SINGLE MODULE PROJECT → Package Strategy                       │
│                                                                  │
│  src/com/company/                                                │
│  ├── auth/                ← Brick from package                  │
│  ├── network/             ← Brick from package                  │
│  └── core/                ← Brick from package                  │
│                                                                  │
│  Layers from import graph                                        │
└─────────────────────────────────────────────────────────────────┘
```

#### Rust: Workspace + Module Hybrid

```
┌─────────────────────────────────────────────────────────────────┐
│  CARGO WORKSPACE → Build Target Strategy                        │
│                                                                  │
│  auth/                    ← Brick from crate                    │
│  ├── Cargo.toml                                                  │
│  └── src/lib.rs                                                  │
│                                                                  │
│  Layers from Cargo.toml dependencies                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  SINGLE CRATE → Package Strategy (modules)                      │
│                                                                  │
│  src/                                                            │
│  ├── lib.rs                                                      │
│  ├── auth/                ← Brick from module                   │
│  │   └── mod.rs                                                  │
│  └── network/             ← Brick from module                   │
│      └── mod.rs                                                  │
│                                                                  │
│  Layers from use statements                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. The Universal Algorithm

Despite different strategies, the algorithm follows the same pattern:

```
┌─────────────────────────────────────────────────────────────────┐
│                 UNIVERSAL BRICK DISCOVERY ALGORITHM              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ STEP 1: DETECT                                            │   │
│  │                                                           │   │
│  │ Examine project root for markers:                         │   │
│  │   CMakeLists.txt → Build Target (C/C++)                  │   │
│  │   Package.swift  → Build Target (Swift)                  │   │
│  │   Cargo.toml     → Build Target or Package (Rust)        │   │
│  │   build.gradle   → Build Target (Kotlin/Java)            │   │
│  │   go.mod         → Package (Go)                          │   │
│  │   pyproject.toml → Package (Python)                      │   │
│  │   package.json   → Build Target or Package (TS/JS)       │   │
│  │   Gemfile + Rails markers → Convention (Ruby)            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ STEP 2: IDENTIFY BRICK BOUNDARIES                         │   │
│  │                                                           │   │
│  │ Build Target: Parse build config for targets              │   │
│  │ Package:      Scan for package markers (dirs, files)      │   │
│  │ Convention:   Match directory patterns                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ STEP 3: ASSIGN MEMBERS TO BRICKS                          │   │
│  │                                                           │   │
│  │ Build Target: Files in target → brick                    │   │
│  │ Package:      Symbols in package → brick                 │   │
│  │ Convention:   Files matching pattern → brick             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ STEP 4: DERIVE OR APPLY LAYER ORDERING                    │   │
│  │                                                           │   │
│  │ Build Target: Topological sort of target deps             │   │
│  │ Package:      Topological sort of import graph            │   │
│  │ Convention:   Apply prescribed layer rules                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ STEP 5: PROPOSE STRUCTURE                                 │   │
│  │                                                           │   │
│  │ Generate jig/architecture.yaml with:                      │   │
│  │   - Discovered bricks                                     │   │
│  │   - Derived/prescribed layers                             │   │
│  │   - Detected boundaries                                   │   │
│  │   - Suggested refinements                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ STEP 6: HUMAN REVIEW AND EDIT                             │   │
│  │                                                           │   │
│  │ Developer may:                                            │   │
│  │   - Accept proposed structure                             │   │
│  │   - Merge fine-grained bricks                             │   │
│  │   - Rename bricks for clarity                             │   │
│  │   - Adjust layer assignments                              │   │
│  │   - Add cross-brick rules                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ STEP 7: ONGOING VALIDATION                                │   │
│  │                                                           │   │
│  │ On each change, verify:                                   │   │
│  │   - Reality matches declared structure                    │   │
│  │   - Layer rules are respected                             │   │
│  │   - Boundaries are maintained                             │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 5.1 Example: `jig init` Output

```bash
$ jig init

Analyzing project...
Detected: Gradle (Kotlin), 8 modules

Proposed brick structure:

BRICKS (6):
  :core:common      (foundation)
  :core:auth        (platform)     → depends on :core:common
  :core:network     (platform)     → depends on :core:common
  :feature:login    (features)     → depends on :core:auth
  :feature:sync     (features)     → depends on :core:network
  :data:local       (platform)     → depends on :core:common

ENTRY POINTS (2):
  :app              → depends on all features
  :app:wear         → depends on :feature:sync

DERIVED LAYERS:
  foundation: [:core:common]
  platform:   [:core:auth, :core:network, :data:local]
  features:   [:feature:login, :feature:sync]
  app:        [:app, :app:wear]

Layer validation rules:
  ✓ features may depend on platform, foundation
  ✓ platform may depend on foundation  
  ✓ foundation has no internal dependencies

Accept this structure? [Y/n/edit]
```

---

## 6. Language Reference Guide

### 6.1 Complete Strategy Matrix

| Language | Primary Strategy | Brick Source | Member Assignment | Layer Source |
|----------|-----------------|--------------|-------------------|--------------|
| **Go** | Package | Directory = package | `package` declaration | Import graph |
| **Rust** (workspace) | Build Target | Cargo crate | Files in crate | `Cargo.toml` deps |
| **Rust** (single) | Package | `mod` declaration | `mod.rs` scope | `use` statements |
| **Swift** | Build Target | SPM target | Files in target | Target deps |
| **Kotlin** | Build Target | Gradle module | Files in module | Module deps |
| **Java** (multi) | Build Target | Maven/Gradle module | Files in module | Module deps |
| **Java** (single) | Package | Package declaration | `package` statement | Import graph |
| **C#** | Build Target | `.csproj` | Files in project | `ProjectReference` |
| **TypeScript** (mono) | Build Target | Workspace package | Files in workspace | `package.json` deps |
| **TypeScript** (single) | Package | Barrel file | Exports from barrel | Import graph |
| **Python** | Package | `__init__.py` directory | Files in package | Import graph |
| **C/C++** | Build Target | CMake/Bazel target | Files in target | Link deps |
| **Ruby/Rails** | Convention | Directory pattern | Files matching pattern | Prescribed rules |

### 6.2 Detection Markers

| Language | Detection Files | Strategy Selected |
|----------|----------------|-------------------|
| **Go** | `go.mod` | Package |
| **Rust** | `Cargo.toml` | Build Target (workspace) or Package (single) |
| **Swift** | `Package.swift` | Build Target |
| **Kotlin** | `build.gradle.kts`, `settings.gradle.kts` | Build Target |
| **Java** | `pom.xml`, `build.gradle` | Build Target or Package |
| **C#** | `*.sln`, `*.csproj` | Build Target |
| **TypeScript** | `package.json` (check for workspaces) | Build Target or Package |
| **Python** | `pyproject.toml`, `setup.py` | Package |
| **C/C++** | `CMakeLists.txt`, `BUILD`, `meson.build` | Build Target |
| **Ruby** | `Gemfile` + `config/application.rb` | Convention (Rails) |

### 6.3 Extraction Commands/APIs

| Language | Extraction Method |
|----------|------------------|
| **Go** | `go list -json ./...` |
| **Rust** | `cargo metadata --format-version=1` |
| **Swift** | `swift package describe --type json` |
| **Kotlin/Java** | Gradle Tooling API, `gradle dependencies` |
| **C#** | MSBuild API, parse `.csproj` |
| **TypeScript** | Parse `package.json`, TS Compiler API |
| **Python** | AST module, `pydeps` |
| **C/C++** | CMake File API, `cmake --graphviz` |
| **Ruby** | Bundler API, Rails conventions |

---

## 7. Practical Implications

### 7.1 Simplified JIG Architecture

The native bricks approach dramatically simplifies JIG:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORIGINAL JIG CONCEPT                          │
│                                                                  │
│  Source Code ──parse──▶ Dependency Graph ──analyze──▶ Bricks    │
│                              │                                   │
│                              ▼                                   │
│                    Community Detection                           │
│                    Coupling Ratios                               │
│                    Modularity Scores                             │
│                              │                                   │
│                              ▼                                   │
│                    Enforcement Gates                             │
│                                                                  │
│  Complexity: HIGH    Maintenance: DIFFICULT                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    NATIVE BRICKS APPROACH                        │
│                                                                  │
│  Build/Package Config ──read──▶ Bricks (already defined!)       │
│                                     │                            │
│                                     ▼                            │
│                           Developer declares layers              │
│                                     │                            │
│                                     ▼                            │
│                           JIG validates layers match reality     │
│                           Compiler enforces boundaries           │
│                                                                  │
│  Complexity: LOW     Maintenance: TRIVIAL                        │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 What's Required vs Optional

**Required (Core JIG):**

| Component | Purpose |
|-----------|---------|
| Strategy detection | Determine which approach to use |
| Brick extraction | Read native structures |
| Member assignment | Map code to bricks |
| Layer derivation | Topological sort or rules |
| Layer validation | Check reality vs declaration |

**Optional (Nice to Have):**

| Component | Purpose |
|-----------|---------|
| Coupling metrics | Descriptive health dashboard |
| Dependency visualization | Understanding, not enforcement |
| Community detection | Only if native structures are absent |

### 7.3 AI Agent Context Fencing

Native bricks enable precise context fencing for AI agents:

```typescript
async function getAgentContext(brickId: string): Promise<AgentContext> {
  const arch = loadArchitecture();
  const brick = arch.getBrick(brickId);
  
  return {
    // Agent can modify these files
    workingSet: brick.files,
    
    // Agent can read these (public interfaces of dependencies)
    readOnly: brick.dependencies.flatMap(d => 
      arch.getBrick(d).exports
    ),
    
    // Agent cannot see these (other bricks' internals)
    invisible: arch.getOtherBricks(brickId).flatMap(b => b.internals),
    
    // Specifications that apply
    specs: getSpecsForBrick(brickId),
    
    // Tests that verify this brick
    tests: getTestsForBrick(brickId),
  };
}
```

### 7.4 Work Ordering

Layers enable automatic work ordering for multi-brick changes:

```bash
$ jig plan --affecting "core:auth,feature:login,core:network"

Work order (respecting layer dependencies):

Phase 1: [:core:auth, :core:network]  (platform layer, parallel)
Phase 2: [:feature:login]              (features layer, after phase 1)

Rationale:
  - feature:login depends on core:auth
  - core:auth and core:network are independent (same layer)
  - Complete platform changes before feature changes
```

---

## 8. Conclusion

### 8.1 The Native Bricks Philosophy

The original JIG concept proposed sophisticated graph analysis to discover subsystem boundaries. The native bricks approach recognizes a simpler truth:

**Mature ecosystems have already solved the boundary problem.**

Every mainstream language has:
- Grouping mechanisms (packages, modules, targets)
- Visibility systems (public, internal, private)
- Dependency declarations (imports, links, references)

JIG's role is not to reinvent these solutions but to:

1. **Read** native structures
2. **Unify** into a common schema
3. **Extend** with layer declarations
4. **Validate** that code respects declarations
5. **Enable** AI agents to work within boundaries

### 8.2 The Three Strategies

Three fundamental strategies cover all mainstream languages:

| Strategy | Essence | Languages |
|----------|---------|-----------|
| **Build Target** | Build system defines structure | C, C++, Swift, Kotlin, Java, C#, Rust |
| **Package** | Language packages define structure | Go, Python, TypeScript, Java, Rust |
| **Convention** | Framework rules define structure | Ruby/Rails, Django |

The universal algorithm (detect → extract → assign → derive → propose → validate) works identically regardless of which strategy applies.

### 8.3 The Promise

Native bricks deliver:

- **Automatic discovery** — Bricks proposed from existing structures
- **Zero friction** — No new organizational systems to learn
- **Compiler enforcement** — Many languages enforce boundaries natively
- **Unified model** — Common schema across all languages
- **AI-ready** — Precise context fencing for agents

**The build system is the truth. JIG reads it, extends it, and validates it.**

---

## Appendix A: Adapter Interface Specifications

### A.1 Build Target Adapter

```typescript
interface BuildTargetAdapter {
  name: string;
  
  // Detection
  detect(root: string): Promise<boolean>;
  
  // Extraction
  parseTargets(root: string): Promise<Target[]>;
  getTargetFiles(target: Target): Promise<string[]>;
  getTargetDependencies(target: Target): Promise<string[]>;
  getTargetBoundary(target: Target): Promise<Boundary>;
}

interface Target {
  id: string;
  type: 'library' | 'executable' | 'test';
  sourceDir: string;
}

interface Boundary {
  exports: string[];      // Public interface files
  internals: string[];    // Private implementation files
}
```

### A.2 Package Adapter

```typescript
interface PackageAdapter {
  name: string;
  
  // Detection
  detect(root: string): Promise<boolean>;
  
  // Extraction
  findPackages(root: string): Promise<Package[]>;
  getPackageFiles(pkg: Package): Promise<string[]>;
  parseImports(file: string): Promise<Import[]>;
  getExports(pkg: Package): Promise<string[]>;
}

interface Package {
  id: string;
  path: string;
  marker: string;  // e.g., __init__.py, mod.rs, package declaration
}

interface Import {
  source: string;      // Importing file
  target: string;      // Imported package/module
  symbols: string[];   // Specific symbols (if applicable)
}
```

### A.3 Convention Adapter

```typescript
interface ConventionAdapter {
  name: string;
  
  // Detection
  detect(root: string): Promise<Framework | null>;
  
  // Configuration
  getBrickPatterns(framework: Framework): BrickPattern[];
  getLayerRules(framework: Framework): LayerRule[];
}

interface BrickPattern {
  id: string;
  patterns: string[];   // Glob patterns
  layer: string;
}

interface LayerRule {
  layer: string;
  mayUse: string[];     // Layers this layer may depend on
}
```

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Brick** | A logical container grouping related functionality; the unit of architectural organization in JIG |
| **Brick Member** | A native language construct (function, class, type) that lives inside a brick |
| **Layer** | An ordering relationship defining what bricks can depend on what |
| **Boundary** | The distinction between a brick's public interface (exports) and private implementation (internals) |
| **Build Target** | A compilation unit defined by a build system (CMake target, Gradle module, SPM target) |
| **Package** | A language-native grouping mechanism (Go package, Python package, Rust module) |
| **Convention** | Framework-prescribed organization patterns (Rails MVC directories) |
| **S-F-T Triangle** | The Specification-Function-Test relationship linking intent to implementation |

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**License:** Proprietary

*"The build system is the truth. JIG reads it, extends it, and validates it."*
