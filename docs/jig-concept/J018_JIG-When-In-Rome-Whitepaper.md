
# JIG: When in Rome
## A Language-Native Approach to Software Architecture Alignment

**Version:** 1.0  
**Date:** December 2025  
**Authors:** Jim & Claude  
**Status:** Architecture Proposal

---

## Executive Summary

JIG (Jig Intent Graph) is an alignment system for nearly decomposable software. A critical challenge in implementing JIG across diverse programming ecosystems is extracting architectural structure—**bricks** (cohesive units of functionality) and **layers** (ordering relationships)—from codebases written in different languages.

The naive approach asks: *"How do we parse each language to extract dependency graphs?"*

This is the wrong question.

**The right question is:** *"What do developers in each language already use to organize their code, and how do we read that?"*

This whitepaper presents the **"When in Rome"** principle: rather than fighting against language ecosystems, JIG adapts to them. Every mature language has already solved the "how do we organize code" problem. JIG doesn't reinvent these solutions—it reads them, unifies them into a common schema, validates against declared intent, and enables AI agents to work within well-defined boundaries.

---

## Table of Contents

1. [The Core Insight](#1-the-core-insight)
2. [The Universal Schema](#2-the-universal-schema)
3. [The Adapter Architecture](#3-the-adapter-architecture)
4. [Language-Native Brick Definitions](#4-language-native-brick-definitions)
5. [Language-Native S-F-T Annotations](#5-language-native-s-f-t-annotations)
6. [Language Reference Guide](#6-language-reference-guide)
7. [The Tri-Layer Native Stack](#7-the-tri-layer-native-stack)
8. [Implementation Priorities](#8-implementation-priorities)
9. [Conclusion](#9-conclusion)

---

## 1. The Core Insight

### 1.1 The Wrong Question

Traditional static analysis approaches attempt to parse source code directly to extract dependency information. For languages like Python or Go, this works reasonably well. For languages like C++, Ruby, or JavaScript, it becomes a nightmare of preprocessor macros, metaprogramming, and dynamic imports.

The dependency graph extraction problem framed this way is essentially asking: *"How do we become a compiler for every language?"*

This is the wrong question because:

- It duplicates decades of tooling work
- It's incomplete (metaprogramming, dynamic behavior)
- It's fragile (language version changes break parsers)
- It ignores what developers actually think about

### 1.2 The Right Question

Developers don't think about function-level dependency graphs. They think about:

| Language | What Developers Think About |
|----------|---------------------------|
| **C/C++** | "This is `libauth`, it produces `libauth.a`" |
| **Ruby/Rails** | "Controllers call services, services call models" |
| **Go** | "This package exports these functions" |
| **Swift** | "This is the Auth target in my SPM package" |
| **Kotlin** | "This is the `:core:auth` Gradle module" |

Every mature ecosystem has tools that already encode architectural decisions:

- **CMake/Bazel** for C/C++
- **Cargo** for Rust
- **Go modules** for Go
- **npm/yarn workspaces** for JavaScript/TypeScript
- **Swift Package Manager** for Swift
- **Gradle/Maven** for Java/Kotlin
- **Bundler + Rails conventions** for Ruby

**The implementation graph already exists. It's just stored in different places.**

### 1.3 The "When in Rome" Principle

> *"When in Rome, do as the Romans do."*

JIG doesn't impose a foreign structure on codebases. Instead:

1. **Read** what's already there (build configs, conventions, module systems)
2. **Unify** into a common schema (bricks, layers, boundaries)
3. **Validate** against declared intent
4. **Enable** AI agents to work within boundaries

The Romans already have roads. JIG uses them.

---

## 2. The Universal Schema

JIG defines a language-agnostic schema that all ecosystem-specific structures map to.

### 2.1 Core Primitives

```yaml
# jig/architecture.yaml - The Universal Schema

schema_version: "1.0"

# BRICKS: Logical units of cohesive functionality
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
      contacts: ["alice@company.com"]

# LAYERS: Ordering relationships (what can use what)
layers:
  - id: foundation
    description: "Core utilities, zero internal dependencies"
    bricks: [logging, errors, config]
    uses: []  # Foundation uses nothing
    
  - id: platform
    description: "Platform abstractions"
    bricks: [crypto, threading, storage]
    uses: [foundation]
    
  - id: domain
    description: "Business logic"
    bricks: [auth, billing, inventory]
    uses: [platform, foundation]
    
  - id: services
    description: "Orchestration and external APIs"
    bricks: [api, webhooks, sync]
    uses: [domain, platform, foundation]

# RULES: Constraints on the structure
rules:
  - type: layer-order
    description: "Layers can only depend downward"
    mode: strict
    
  - type: brick-boundary
    description: "Internals are private"
    mode: warn
```

### 2.2 Key Concepts

**Bricks** are logical units of cohesive functionality:
- Have a clear boundary (exports vs internals)
- Map to native constructs (packages, modules, targets)
- Are the unit of context fencing for AI agents

**Layers** define ordering relationships:
- Establish what can depend on what
- Map to build order, request flow, or architectural tiers
- Enable parallel work on independent layers

**Boundaries** separate public interface from private implementation:
- Exports are what other bricks can use
- Internals are implementation details
- The compiler/runtime may enforce these (Go, Kotlin, Swift)

---

## 3. The Adapter Architecture

### 3.1 The Adapter Interface

Each adapter implements a simple contract:

```typescript
interface Adapter {
  name: string;
  
  // Can this adapter handle this project?
  detect(projectRoot: string): Promise<boolean>;
  
  // Extract bricks and dependencies from native config
  extract(projectRoot: string, config: AdapterConfig): Promise<AdapterResult>;
  
  // Validate that declared structure matches reality
  validate(declared: Brick[], actual: AdapterResult): ValidationResult;
}

interface AdapterResult {
  bricks: Brick[];
  raw_dependencies: Edge[];
  metadata: Record<string, unknown>;
}

interface Brick {
  id: string;
  files: string[];
  exports: string[];
  internals: string[];
  dependencies: string[];
}
```

### 3.2 Detection and Composition

Projects can have multiple adapters active simultaneously:

```yaml
# A complex project with multiple ecosystems
adapters:
  - name: cmake
    root: ./core
    prefix: "core::"
    
  - name: npm
    root: ./web
    prefix: "web::"
    
  - name: poetry
    root: ./ml
    prefix: "ml::"

# Cross-ecosystem bridges
bridges:
  - from: web::api
    to: core::network
    via: grpc
    
  - from: ml::inference
    to: core::model
    via: ffi
```

### 3.3 Validation Engine

The adapters extract reality. JIG validates that reality matches intent:

```bash
$ jig validate

✓ Layer ordering valid
✓ Brick boundaries respected  
✗ Violation: web::api imports core::auth/internal/token.cpp
  → Boundary violation: internal file accessed from outside brick
```

---

## 4. Language-Native Brick Definitions

### 4.1 Summary Table

| Language | Brick Source | Layer Source | Boundary Enforcement |
|----------|-------------|--------------|---------------------|
| **Go** | `go.mod` packages | Import DAG (enforced!) | Exported/unexported |
| **Rust** | Cargo crates, `mod.rs` | `Cargo.toml` deps | `pub`/`pub(crate)` |
| **Swift** | SPM targets | Target dependencies | `public`/`internal` |
| **Kotlin** | Gradle modules | Module dependencies | `public`/`internal` |
| **Java** | Maven/Gradle modules | POM/Gradle deps | Package-private (weak) |
| **TypeScript** | npm workspaces, barrels | Import graph | Convention only |
| **Python** | Packages, `__init__.py` | Import graph | Convention only |
| **C/C++** | CMake/Bazel targets | Link dependencies | Header visibility |
| **Ruby** | Gems + Rails dirs | Request flow convention | Convention only |
| **C#** | Projects/assemblies | Project references | `public`/`internal` |

### 4.2 Go

Go is arguably the easiest language for JIG. The ecosystem enforces good architecture.

**Native Brick Definition:**
```go
// go.mod defines the module (top-level brick)
module github.com/company/myapp

// Packages are sub-bricks
// github.com/company/myapp/auth
// github.com/company/myapp/network
```

**What Go Gives Us:**
- Packages = Bricks
- Imports = Dependencies (DAG enforced by compiler!)
- Capitalized = Exported, lowercase = Internal
- `go list -json ./...` provides everything

**Adapter Extraction:**
```bash
go list -json ./...
# Returns: packages, imports, exports - complete graph
```

### 4.3 Rust

Rust's Cargo system provides excellent structure.

**Native Brick Definition:**
```toml
# Cargo.toml
[package]
name = "auth"

[dependencies]
crypto = { path = "../crypto" }  # Dependency = layer relationship
```

**What Cargo Gives Us:**
- Crates = Bricks
- `[dependencies]` = Layer relationships
- `pub` = Exported, non-pub = Internal
- `pub(crate)` = Module-internal

**Adapter Extraction:**
```bash
cargo metadata --format-version=1
# Returns: packages, dependencies, features
```

### 4.4 Swift

Swift Package Manager defines bricks clearly.

**Native Brick Definition:**
```swift
// Package.swift
let package = Package(
    name: "MyApp",
    products: [
        .library(name: "Auth", targets: ["Auth"]),
    ],
    targets: [
        .target(
            name: "Auth",
            dependencies: ["Crypto"]  // Layer relationship
        ),
        .testTarget(
            name: "AuthTests",
            dependencies: ["Auth"]
        ),
    ]
)
```

**What SPM Gives Us:**
- Targets = Bricks
- Dependencies = Layer relationships
- Products = Public interfaces
- `public` vs `internal` = Boundary enforcement (compiler!)

**Adapter Extraction:**
```bash
swift package describe --type json
```

### 4.5 Kotlin

Gradle modules are natural bricks.

**Native Brick Definition:**
```kotlin
// settings.gradle.kts
include(":core:auth")
include(":core:crypto")
include(":core:network")

// core/auth/build.gradle.kts
dependencies {
    implementation(project(":core:crypto"))  // Layer relationship
}
```

**What Gradle Gives Us:**
- Modules = Bricks
- `implementation` vs `api` = Internal vs Public dependencies
- Kotlin `internal` visibility = Module-scoped (compiler enforced!)

**Adapter Extraction:**
```bash
gradle dependencies --configuration compileClasspath
```

### 4.6 Java

Similar to Kotlin, using Maven or Gradle.

**Native Brick Definition:**
```xml
<!-- pom.xml -->
<artifactId>auth</artifactId>
<dependencies>
    <dependency>
        <groupId>com.company</groupId>
        <artifactId>crypto</artifactId>
    </dependency>
</dependencies>
```

**What Maven/Gradle Gives Us:**
- Modules/artifacts = Bricks
- Dependencies = Layer relationships
- Package-private visibility (weaker than Kotlin's `internal`)

### 4.7 TypeScript/JavaScript

npm workspaces for monorepos, barrel files for single packages.

**Native Brick Definition:**
```json
// package.json (monorepo)
{
  "workspaces": [
    "packages/auth",
    "packages/network"
  ]
}

// Or: barrel files as boundaries
// src/auth/index.ts exports the public API
```

**What npm Gives Us:**
- Workspaces = Bricks
- Barrel files (`index.ts`) = Boundaries
- Package dependencies = Layer relationships

**Adapter Extraction:**
```bash
# madge or dependency-cruiser for import graph
npx madge --json src/
```

### 4.8 Python

Packages and `__init__.py` define structure.

**Native Brick Definition:**
```
myapp/
├── auth/
│   ├── __init__.py      # Exports
│   └── internal/        # Internals
├── network/
│   └── __init__.py
```

**What Python Gives Us:**
- Packages = Bricks
- `__init__.py` with `__all__` = Exports
- Import graph = Dependencies

**Adapter Extraction:**
```bash
# pydeps for dependency graph
pydeps myapp --show-deps
```

### 4.9 C/C++

Build system IS the architecture.

**Native Brick Definition:**
```cmake
# CMakeLists.txt
add_library(libauth STATIC
    src/auth/token.cpp
    src/auth/session.cpp
)
target_include_directories(libauth
    PUBLIC  src/auth/include    # Boundary: exports
    PRIVATE src/auth/impl       # Boundary: internals
)
target_link_libraries(libauth
    PRIVATE libcrypto           # Layer relationship
)
```

**What CMake Gives Us:**
- Targets = Bricks
- `PUBLIC`/`PRIVATE` include dirs = Boundaries
- `target_link_libraries` = Layer relationships

**Adapter Extraction:**
```bash
cmake --graphviz=deps.dot .
# Or: cmake-file-api for structured output
```

### 4.10 Ruby/Rails

Gems + conventions define structure.

**Native Brick Definition:**
```ruby
# Gemfile
gem 'devise'      # Auth brick (external)
gem 'sidekiq'     # Async brick (external)

# Rails conventions ARE the layers:
# app/models/      = Persistence layer
# app/services/    = Domain layer
# app/controllers/ = Presentation layer
```

**What Rails Gives Us:**
- Gems = External bricks
- Directory conventions = Internal layers
- Request flow = Layer ordering

### 4.11 "C#"

Projects and assemblies define structure.

**Native Brick Definition:**
```xml
<!-- Auth.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
    <ItemGroup>
        <ProjectReference Include="..\Crypto\Crypto.csproj" />
    </ItemGroup>
</Project>
```

**What .NET Gives Us:**
- Projects = Bricks
- Project references = Layer relationships
- `internal` keyword = Assembly-scoped visibility (compiler enforced!)

---

## 5. Language-Native S-F-T Annotations

The S-F-T (Specification-Function-Test) triangle links intent to implementation. Each language has an idiomatic way to express these annotations.

### 5.1 The Spectrum of Native-ness

```
Most Native                                              Least Native
     │                                                        │
     ▼                                                        ▼
┌─────────┐  ┌─────────┐  ┌─────────────┐  ┌────────┐  ┌─────────┐
│Language │  │Language │  │  Language   │  │  Doc   │  │ Plain   │
│Attributes│  │Decorators│  │  Directives │  │Comments│  │Comments │
│(compile) │  │(runtime) │  │ (tooling)   │  │(JSDoc) │  │ (grep)  │
└─────────┘  └─────────┘  └─────────────┘  └────────┘  └─────────┘
   Java         Python         Go             TS          C
   C#           Ruby           
   Rust         
   Swift
   Kotlin
```

### 5.2 Summary Table

| Language | Native Mechanism | Spec-as-Interface? | Compile-time Validation |
|----------|-----------------|-------------------|------------------------|
| **Python** | Decorators | ✗ (duck typing) | ✗ |
| **Java** | Annotations | ✓ | ✓ (APT) |
| **C#** | Attributes | ✓ | ✓ (Roslyn) |
| **Rust** | Proc macros | ✓ (traits) | ✓ |
| **Go** | Directive comments | ✓ (interfaces) | ✗ |
| **TypeScript** | JSDoc + Decorators | ✓ | ✓ (compiler) |
| **Ruby** | DSL or comments | ✗ | ✗ |
| **C++** | Attributes (C++11+) | ✓ (concepts C++20) | ✗ |
| **C** | Pragmas/Doxygen | ✗ | ✗ |
| **Swift** | Macros (5.9+) | ✓✓✓ (protocols) | ✓ |
| **Kotlin** | Annotations | ✓✓✓ (interfaces) | ✓ (KSP) |

### 5.3 Python: Decorators

Python decorators are first-class language features with excellent IDE support.

```python
from jig import implements, verifies, spec

@spec("S-AUTH-001", title="JWT Authentication", brick="auth")
class AuthSpec:
    """Marker class defining the auth specification."""
    pass

@implements("S-AUTH-001")
def authenticate(user: str, password: str) -> Token:
    """Authenticate user and return session token."""
    ...

@verifies("S-AUTH-001")
def test_authenticate_valid_user():
    """Test that valid credentials produce a token."""
    ...
```

**Extraction:** `inspect` module, AST parsing

### 5.4 Java: Annotations

Java developers live in annotations. This is their native language.

```java
import com.jig.Implements;
import com.jig.Verifies;
import com.jig.Spec;

@Spec(id = "S-AUTH-001", title = "JWT Authentication", brick = "auth")
public interface AuthSpec {
    Token authenticate(String user, String password);
}

@Implements("S-AUTH-001")
public class JWTAuthenticator implements AuthSpec {
    @Override
    public Token authenticate(String user, String password) {
        // ...
    }
}

@Verifies("S-AUTH-001")
@Test
public void testAuthenticateValidUser() {
    // ...
}
```

**Extraction:** Reflection, annotation processors (APT)

### 5.5 C#: Attributes

Same pattern as Java, with Roslyn analyzer support.

```csharp
using Jig;

[Spec("S-AUTH-001", Title = "JWT Authentication", Brick = "auth")]
public interface IAuthService 
{
    Token Authenticate(string user, string password);
}

[Implements("S-AUTH-001")]
public class JWTAuthenticator : IAuthService
{
    public Token Authenticate(string user, string password) 
    {
        // ...
    }
}

[Verifies("S-AUTH-001")]
[Test]
public void TestAuthenticateValidUser() 
{
    // ...
}
```

**Extraction:** Reflection, Roslyn analyzers

### 5.6 Rust: Attribute Macros

Rust's proc macros are powerful and idiomatic.

```rust
use jig::{implements, verifies, spec};

#[spec("S-AUTH-001", title = "JWT Authentication", brick = "auth")]
pub trait Authenticator {
    fn authenticate(&self, user: &str, password: &str) -> Result<Token, AuthError>;
}

#[implements("S-AUTH-001")]
impl Authenticator for JWTAuthenticator {
    fn authenticate(&self, user: &str, password: &str) -> Result<Token, AuthError> {
        // ...
    }
}

#[verifies("S-AUTH-001")]
#[test]
fn test_authenticate_valid_user() {
    // ...
}
```

**Extraction:** `syn` crate, custom cargo subcommand

### 5.7 Go: Directive Comments

Go uses magic comments (`//go:generate`, `//go:embed`). JIG follows this pattern.

```go
//jig:spec S-AUTH-001 title:"JWT Authentication" brick:auth
type Authenticator interface {
    Authenticate(user, password string) (*Token, error)
}

//jig:implements S-AUTH-001
func (a *JWTAuthenticator) Authenticate(user, password string) (*Token, error) {
    // ...
}

//jig:verifies S-AUTH-001
func TestAuthenticateValidUser(t *testing.T) {
    // ...
}
```

**Extraction:** `go/parser` and `go/ast` (standard library)

### 5.8 TypeScript: JSDoc + Decorators

TypeScript supports both JSDoc (universal) and decorators (for frameworks).

**JSDoc Style (works everywhere):**
```typescript
/**
 * @jig spec S-AUTH-001
 * @jig title JWT Authentication
 * @jig brick auth
 */
export interface Authenticator {
    authenticate(user: string, password: string): Token;
}

/**
 * @jig implements S-AUTH-001
 */
export function authenticate(user: string, password: string): Token {
    // ...
}

/**
 * @jig verifies S-AUTH-001
 */
test('authenticate valid user', () => {
    // ...
});
```

**Decorator Style (Angular, NestJS):**
```typescript
import { Implements, Verifies, Spec } from '@jig/decorators';

@Spec('S-AUTH-001', { title: 'JWT Authentication', brick: 'auth' })
export interface Authenticator {
    authenticate(user: string, password: string): Token;
}

@Implements('S-AUTH-001')
export class JWTAuthenticator implements Authenticator {
    authenticate(user: string, password: string): Token {
        // ...
    }
}
```

**Extraction:** TypeScript Compiler API, `ts-morph`

### 5.9 Ruby: DSL or Magic Comments

Ruby's flexibility allows multiple approaches.

**DSL Style (more Ruby-like):**
```ruby
class AuthService
  extend Jig::Annotations
  
  spec "S-AUTH-001", title: "JWT Authentication", brick: "auth"
  
  implements "S-AUTH-001"
  def authenticate(user, password)
    # ...
  end
end

# In RSpec
RSpec.describe AuthService do
  verifies "S-AUTH-001"
  it "authenticates valid user" do
    # ...
  end
end
```

**Magic Comment Style:**
```ruby
# jig:implements S-AUTH-001
def authenticate(user, password)
  # ...
end
```

**Extraction:** Parser gem, RuboCop AST tools

### 5.10 C++: Attributes or Pragmas

Modern C++ (C++11+) has attributes; older codebases use pragmas.

**C++11 Attributes:**
```cpp
[[jig::spec("S-AUTH-001", title="JWT Authentication", brick="auth")]]
class Authenticator {
public:
    virtual Token authenticate(const std::string& user, 
                               const std::string& password) = 0;
};

[[jig::implements("S-AUTH-001")]]
class JWTAuthenticator : public Authenticator {
public:
    Token authenticate(const std::string& user, 
                       const std::string& password) override {
        // ...
    }
};

[[jig::verifies("S-AUTH-001")]]
TEST(AuthTest, ValidUser) {
    // ...
}
```

**Pragma Style:**
```cpp
#pragma jig spec S-AUTH-001 title:"JWT Authentication" brick:auth

#pragma jig implements S-AUTH-001
Token authenticate(const std::string& user, const std::string& password) {
    // ...
}
```

**C++20 Concepts as Specs:**
```cpp
template<typename T>
concept AuthenticatorSpec = requires(T t, std::string user, std::string pw) {
    { t.authenticate(user, pw) } -> std::same_as<Token>;
};
// The language itself enforces the spec!
```

**Extraction:** libclang, clang-tidy

### 5.11 C: Pragmas or Doxygen

C lacks modern metaprogramming but has established patterns.

**Doxygen Style (familiar to C developers):**
```c
/**
 * @jig spec S-AUTH-001
 * @jig title JWT Authentication
 * @jig brick auth
 */

/**
 * @jig implements S-AUTH-001
 * @brief Authenticate user and return token
 */
Token* authenticate(const char* user, const char* password) {
    // ...
}
```

**Pragma Style:**
```c
#pragma jig implements S-AUTH-001
Token* authenticate(const char* user, const char* password) {
    // ...
}
```

**Extraction:** libclang, regex on Doxygen comments

### 5.12 Swift: Macros (Swift 5.9+)

Swift macros are the cleanest modern solution.

```swift
import Jig

@Spec("S-AUTH-001", title: "JWT Authentication", brick: "auth")
protocol Authenticator {
    func authenticate(user: String, password: String) throws -> Token
}

@Implements("S-AUTH-001")
class JWTAuthenticator: Authenticator {
    func authenticate(user: String, password: String) throws -> Token {
        // ...
    }
}

@Verifies("S-AUTH-001")
func testAuthenticateValidUser() {
    // ...
}
```

**The compiler enforces protocol conformance.** If `JWTAuthenticator` doesn't implement all `Authenticator` methods, compilation fails.

**Extraction:** SwiftSyntax, SourceKit-LSP

### 5.13 Kotlin: Annotations

Kotlin annotations with KSP provide compile-time validation.

```kotlin
import com.jig.Implements
import com.jig.Verifies
import com.jig.Spec

@Spec("S-AUTH-001", title = "JWT Authentication", brick = "auth")
interface Authenticator {
    suspend fun authenticate(user: String, password: String): Token
}

@Implements("S-AUTH-001")
class JWTAuthenticator : Authenticator {
    override suspend fun authenticate(user: String, password: String): Token {
        // ...
    }
}

@Verifies("S-AUTH-001")
@Test
fun `authenticate valid user`() {
    // ...
}
```

**Kotlin DSL for Spec Definitions:**
```kotlin
specs {
    spec("S-AUTH-001") {
        title = "JWT Authentication"
        brick = "auth"
        
        requires {
            function("authenticate") {
                params("user" to String::class, "password" to String::class)
                returns(Token::class)
            }
        }
    }
}
```

**Extraction:** KSP (Kotlin Symbol Processing), reflection

---

## 6. Language Reference Guide

### 6.1 Complete Reference Table

| Language | Brick Source | Annotation Style | Spec-as-Interface | Boundary Keyword | Extraction Tool |
|----------|-------------|------------------|-------------------|-----------------|-----------------|
| **Python** | Packages | `@decorator` | ✗ | Convention | `inspect`, AST |
| **Java** | Maven/Gradle | `@Annotation` | ✓ | `package` | Reflection, APT |
| **C#** | Projects | `[Attribute]` | ✓ | `internal` | Reflection, Roslyn |
| **Rust** | Cargo crates | `#[macro]` | ✓ (traits) | `pub(crate)` | `syn`, cargo |
| **Go** | Packages | `//jig:` | ✓ (interfaces) | unexported | `go/ast` |
| **TypeScript** | npm/workspaces | JSDoc/`@decorator` | ✓ | Convention | TS Compiler API |
| **JavaScript** | npm/workspaces | JSDoc | ✓ | Convention | TS Compiler API |
| **Ruby** | Gems + dirs | DSL/`# jig:` | ✗ | Convention | Parser gem |
| **C** | CMake targets | `#pragma`/Doxygen | ✗ | Header visibility | libclang |
| **C++** | CMake targets | `[[attr]]`/`#pragma` | ✓ (concepts) | Header visibility | libclang |
| **Swift** | SPM targets | `@Macro` | ✓✓✓ (protocols) | `internal` | SwiftSyntax |
| **Kotlin** | Gradle modules | `@Annotation` | ✓✓✓ (interfaces) | `internal` | KSP |

### 6.2 Recommended Patterns by Language

**For maximum native-ness, use:**

| Language | Recommended Pattern |
|----------|-------------------|
| **Python** | `@implements`, `@verifies` decorators |
| **Java** | `@Implements`, `@Verifies` annotations on classes/methods |
| **C#** | `[Implements]`, `[Verifies]` attributes |
| **Rust** | `#[implements]`, `#[verifies]` proc macros |
| **Go** | `//jig:implements`, `//jig:verifies` directive comments |
| **TypeScript** | JSDoc `@jig implements` or `@Implements` decorators |
| **Ruby** | `implements "S-001"` DSL in classes |
| **C/C++** | Doxygen `@jig implements` or `#pragma jig implements` |
| **Swift** | `@Implements`, `@Verifies` macros |
| **Kotlin** | `@Implements`, `@Verifies` annotations |

---

## 7. The Tri-Layer Native Stack

For languages with strong type systems (Swift, Kotlin, Rust, Go, C#), JIG benefits from three layers of native support:

```
┌─────────────────────────────────────────┐
│  Layer 1: Annotations/Macros            │
│  @Implements, @Verifies, @Spec          │
│  → S-F-T triangle relationships         │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  Layer 2: Visibility Modifiers          │
│  public / internal / private            │
│  → Brick boundaries (compiler-enforced) │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  Layer 3: Build System                  │
│  SPM targets / Gradle modules / Cargo   │
│  → Brick definitions + layer deps       │
└─────────────────────────────────────────┘
```

### 7.1 Languages with Full Tri-Layer Support

**Swift:**
- Layer 1: `@Implements` macros
- Layer 2: `public`/`internal` visibility (compiler enforced)
- Layer 3: SPM targets and dependencies

**Kotlin:**
- Layer 1: `@Implements` annotations
- Layer 2: `public`/`internal` visibility (compiler enforced)
- Layer 3: Gradle modules and dependencies

**Rust:**
- Layer 1: `#[implements]` proc macros
- Layer 2: `pub`/`pub(crate)` visibility (compiler enforced)
- Layer 3: Cargo crates and dependencies

**Go:**
- Layer 1: `//jig:implements` directives
- Layer 2: Exported/unexported (compiler enforced)
- Layer 3: Go modules and packages

**C#:**
- Layer 1: `[Implements]` attributes
- Layer 2: `public`/`internal` visibility (compiler enforced)
- Layer 3: Project references

### 7.2 The Compiler as Validator

In these languages, the compiler itself enforces architectural constraints:

```swift
// Swift: The compiler validates S-F relationship
@Spec("S-AUTH-001")
protocol Authenticator {
    func authenticate(user: String, password: String) -> Token
}

@Implements("S-AUTH-001")
class JWTAuthenticator: Authenticator {
    // If this method is missing, COMPILATION FAILS
    func authenticate(user: String, password: String) -> Token {
        // ...
    }
}
```

JIG doesn't need to validate the spec-implementation link—the compiler does it. JIG's role becomes:
1. Track which protocols/interfaces are specs
2. Track which implementations fulfill them
3. Track which tests verify them
4. Compute metrics on the graph

---

## 8. Implementation Priorities

### 8.1 Recommended Order

Based on ecosystem maturity, native support, and market value:

| Priority | Language | Rationale |
|----------|----------|-----------|
| **1** | **Python** | Reference implementation, mature tooling |
| **2** | **TypeScript** | Primary target, excellent compiler API |
| **3** | **Kotlin** | Clean annotations, Gradle modules, `internal` visibility |
| **4** | **Swift** | Same benefits, Apple ecosystem value |
| **5** | **Go** | Clean directives, excellent stdlib, enforced DAG |
| **6** | **Rust** | Proc macros, Cargo, growing systems programming market |
| **7** | **Java** | Enterprise market, mature tooling |
| **8** | **C#** | Similar to Kotlin/Swift with `internal` |
| **9** | **Ruby** | DSL works but static analysis is limited |
| **10** | **C/C++** | Structure from build system, pragmas for annotations |

### 8.2 Quick Wins vs Long-term Value

**Quick Wins (easiest to implement):**
- Go: `go/ast` standard library does everything
- Kotlin: Reflection + Gradle parsing
- Swift: SwiftSyntax + SPM parsing

**Highest Value (market size × native-ness):**
- TypeScript: Huge market, excellent tooling
- Kotlin: Android + backend, tri-layer support
- Swift: iOS market, tri-layer support
- Java: Enterprise market, mature tooling

**Hardest (but valuable):**
- C++: Build system parsing works, but ecosystem is fragmented
- Ruby: Metaprogramming limits static analysis

---

## 9. Conclusion

### 9.1 The "When in Rome" Principle

Every mature programming ecosystem has already solved the "how do we organize code" problem. They've built tools—CMake, Cargo, Go modules, npm workspaces, SPM, Gradle—that encode architectural decisions.

JIG doesn't reinvent these solutions. JIG:

1. **Reads** what's already there
2. **Unifies** into a common schema (bricks, layers, boundaries)
3. **Validates** against declared intent
4. **Enables** AI agents to work within well-defined boundaries

### 9.2 The Promise

By adopting language-native patterns:

- **Zero friction adoption:** Developers use patterns they already know
- **IDE support:** Autocomplete, go-to-definition, refactoring work
- **Compile-time validation:** Many languages can check at build time
- **No new syntax:** Just new semantics on familiar forms
- **Tooling integration:** Language-native tools can process JIG annotations

### 9.3 The JIG Commitment

> *"JIG speaks your language. Literally."*

Each adapter translates native constructs into the universal schema. The core JIG engine only sees the unified model. Language-specific complexity is encapsulated in adapters.

The result: architectural alignment that feels native to every ecosystem, enabling AI agents to work safely and effectively within well-defined boundaries, across any language.

---

## Appendix A: Adapter Implementation Checklist

For each new language adapter, implement:

1. **Detection:** Can this adapter handle this project?
2. **Brick Extraction:** Read native build config for structure
3. **Dependency Extraction:** Extract brick-to-brick dependencies
4. **Boundary Detection:** Identify exports vs internals
5. **Annotation Extraction:** Parse S-F-T annotations from source
6. **Validation:** Check declared structure matches reality

## Appendix B: Universal CLI

```bash
# Auto-detect and initialize
jig init
# Detected: gradle (./core), npm (./web)
# Created: jig/architecture.yaml

# Validate architecture
jig validate
# ✓ Layer ordering valid
# ✗ Boundary violation: web::api imports core::auth/internal

# Show architecture overview  
jig architecture
# Layers: foundation → platform → domain → services
# Bricks: 12 across 2 adapters

# Plan work order for AI agent
jig plan --affecting "core::auth,web::api"
# Phase 1: core::auth
# Phase 2: web::api (depends on Phase 1)

# Get context fence for AI agent
jig context --brick core::auth
# Working set: 12 files
# Read-only: 4 interface files
# Specs: S-AUTH-001, S-AUTH-002
```

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**License:** Proprietary - Anthropic

*"When in Rome, do as the Romans. The Romans already have roads. JIG uses them."*
