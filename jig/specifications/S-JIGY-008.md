---
id: S-JIGY-008
type: specification
title: Fast annotation scanner (<2s for 10k files)
subsystem: jigy-tool
status: active
created: 2025-11-21
implements:
  - O-JIGY-003
---

# Specification: Annotation Scanner

## Purpose

Scan source and test files to discover `@jig` annotations marking Code (C-*) and Test (T-*) nodes. Extract node metadata, relationships, and file locations. Achieve <2 second scan time for 10,000 files.

## Requirements

### 1. Annotation Format

Parse JIG v6.1 annotation syntax:

```python
# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:auth interface:public
class JWTAuthenticator:
    """Handles JWT-based multi-device authentication"""

# @jig C-AUTH-002 implements:S-AUTH-001,S-AUTH-002 subsystem:auth
def validate_token(self, token: str) -> Claims:
    """Validates JWT and extracts claims"""

# @jig T-AUTH-001 verifies:S-AUTH-001 subsystem:auth
def test_jwt_token_validation():
    """Verify JWT tokens validate correctly"""
```

**Annotation Pattern:**
```
# @jig <NODE-ID> <RELATIONS> <METADATA>
```

Where:
- `NODE-ID`: `[CT]-[A-Z]+-\d+` (e.g., C-AUTH-001, T-AUTH-001)
- `RELATIONS`: `key:value[,value]` pairs (e.g., `implements:S-001`, `verifies:S-001,S-002`)
- `METADATA`: `key:value` pairs (e.g., `subsystem:auth`, `interface:public`)

### 2. Scanning Strategy

**Option A: Use ripgrep (fastest)**
```bash
rg --line-number --no-heading '@jig [CT]-[A-Z]+-\d+' src/ test/
```

**Option B: Python implementation (portable)**
```python
def scan_annotations(directories):
    """Scan directories for @jig annotations"""
    pattern = re.compile(r'#\s*@jig\s+([CT]-[A-Z]+-\d+)\s+(.*)')
    
    for directory in directories:
        for file_path in Path(directory).rglob('*.py'):
            with open(file_path) as f:
                for line_num, line in enumerate(f, 1):
                    match = pattern.match(line)
                    if match:
                        yield parse_annotation(match, file_path, line_num)
```

**Performance Target:** <2 seconds for 10,000 files

**Choose:** ripgrep if available (10x faster), fallback to Python

### 3. Metadata Extraction

Extract from annotation line:

```python
# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:auth interface:public
```

Parsed result:
```python
{
    "id": "C-AUTH-001",
    "type": "code",  # Inferred from C- prefix
    "file": "src/auth/jwt.py",
    "line": 42,
    "relationships": {
        "implements": ["S-AUTH-001"]
    },
    "metadata": {
        "subsystem": "auth",
        "interface": "public"
    }
}
```

**Relationship Parsing:**
- Format: `key:value1,value2`
- Common keys: `implements`, `verifies`, `depends`
- Values: Comma-separated node IDs

**Metadata Parsing:**
- Format: `key:value`
- Common keys: `subsystem`, `interface`, `status`
- Values: Single tokens (no commas)

### 4. Supported File Types

**Primary:** Python (`.py`)

**Future extensions:**
- JavaScript/TypeScript: `// @jig ...`
- Go: `// @jig ...`
- Rust: `// @jig ...`
- Java: `// @jig ...`

**Configuration:** Specify file extensions in `jig/config.toml`

```toml
[scanner]
file_extensions = [".py", ".js", ".ts", ".go", ".rs"]
directories = ["src", "test", "tests"]
```

### 5. Scan Command

**Command:** `jigy scan [--directory DIR] [--dry-run]`

```bash
$ jigy scan

Scanning for @jig annotations...
  src/: 24 code nodes found
  test/: 37 test nodes found

Total: 61 annotations (24 code, 37 test)
Scanned 842 files in 1.2s

$ jigy scan --dry-run

Would scan:
  src/ (423 files)
  test/ (419 files)

$ jigy scan --directory src/auth

Scanning src/auth/...
  Found: C-AUTH-001, C-AUTH-002, C-AUTH-003
Total: 3 code nodes
```

### 6. Error Handling

**Invalid annotation format:**
```python
# @jig INVALID-FORMAT
# Warning: Invalid annotation format at src/auth/jwt.py:42
#          Expected: @jig [CT]-SUBSYSTEM-NNN relationships metadata
```

**Duplicate node IDs:**
```python
# @jig C-AUTH-001 ...  # src/auth/jwt.py:42
# @jig C-AUTH-001 ...  # src/auth/token.py:18
# Error: Duplicate annotation C-AUTH-001 found:
#        - src/auth/jwt.py:42
#        - src/auth/token.py:18
```

**Severity:**
- Invalid format: WARNING (skip annotation)
- Duplicate IDs: ERROR (validation failure)
- File read errors: WARNING (skip file)

## Implementation Notes

**Location:** `jigy/scanners/annotation_scanner.py`

**Dependencies:**
- `ripgrep` (optional, for speed)
- `pathlib` for file traversal
- `re` for pattern matching

**Scanner Implementation:**
```python
# @jig C-JIGY-008 implements:S-JIGY-008 subsystem:jigy-tool interface:public
class AnnotationScanner:
    """Fast scanner for @jig annotations in source files"""
    
    def scan(self, directories):
        """Scan directories for annotations"""
        # Try ripgrep first (faster)
        if shutil.which('rg'):
            return self._scan_with_ripgrep(directories)
        else:
            return self._scan_with_python(directories)
    
    def _scan_with_ripgrep(self, directories):
        """Use ripgrep for fast scanning"""
        pattern = '@jig [CT]-[A-Z]+-\\d+'
        result = subprocess.run(
            ['rg', '--line-number', '--no-heading', pattern] + directories,
            capture_output=True, text=True
        )
        return self._parse_ripgrep_output(result.stdout)
    
    def _scan_with_python(self, directories):
        """Fallback Python implementation"""
        pattern = re.compile(r'#\s*@jig\s+([CT]-[A-Z]+-\d+)\s+(.*)')
        annotations = []
        
        for directory in directories:
            for file_path in Path(directory).rglob('*.py'):
                annotations.extend(self._scan_file(file_path, pattern))
        
        return annotations
```

**Performance Optimization:**
- Parallel file scanning (ThreadPoolExecutor)
- Skip binary files, test fixtures, generated code
- Regex compilation (compile once, reuse)
- Stream processing (don't load entire files)

## Test Cases

```python
# @jig T-JIGY-021 verifies:S-JIGY-008 subsystem:jigy-tool
def test_parse_annotation():
    """Test annotation parsing"""
    line = "# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:auth interface:public"
    result = parse_annotation(line)
    
    assert result.id == "C-AUTH-001"
    assert result.type == "code"
    assert result.relationships["implements"] == ["S-AUTH-001"]
    assert result.metadata["subsystem"] == "auth"
    assert result.metadata["interface"] == "public"

# @jig T-JIGY-022 verifies:S-JIGY-008 subsystem:jigy-tool
def test_scan_performance():
    """Test scan completes in <2 seconds for 10k files"""
    # Create test directory with 10k Python files
    test_dir = create_test_files(count=10000)
    
    start = time.time()
    results = scan_annotations([test_dir])
    elapsed = time.time() - start
    
    assert elapsed < 2.0

# @jig T-JIGY-023 verifies:S-JIGY-008 subsystem:jigy-tool
def test_duplicate_detection():
    """Test detection of duplicate annotation IDs"""
    files = {
        "file1.py": "# @jig C-TEST-001 implements:S-001",
        "file2.py": "# @jig C-TEST-001 implements:S-002"  # Duplicate!
    }
    
    result = scan_annotations_from_dict(files)
    assert not result.valid
    assert "Duplicate" in result.errors[0]
```

## References

- O-JIGY-003: Code and Intent stay synchronized
- S017 Analysis: Part 3.4.1 (Code scanner)
- JIG v6.1 Spec: §1.3 (Reality annotations)

