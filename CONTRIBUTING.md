# Contributing to JIG

Thank you for your interest in contributing to JIG! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Make (for Linux/macOS) or manual setup (for Windows)

### Development Setup

**Quick Setup (Linux/macOS)**

```bash
# Clone the repository
git clone https://github.com/yourorg/jig.git
cd jig

# One-command setup
make dev-setup

# Activate virtual environment
source .venv/bin/activate
```

**Manual Setup (All Platforms)**

```bash
# Clone the repository
git clone https://github.com/yourorg/jig.git
cd jig

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"
```

## Development Workflow

### Running Tests

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test file
pytest tests/unit/test_config.py -v
```

### Code Quality

Before submitting a PR, ensure your code passes all checks:

```bash
# Run all checks (lint + typecheck + test)
make validate

# Or run individually:
make lint        # Check code style
make format      # Auto-format code
make typecheck   # Type checking with mypy
```

### Code Style

- We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting
- We use [mypy](https://mypy-lang.org/) for type checking
- Line length: 100 characters
- Follow PEP 8 conventions
- All code must have type hints

### Commit Messages

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test changes
- `refactor`: Code refactoring
- `chore`: Build/tooling changes

Example:
```
feat(cli): add graph visualization command

Implements the `jigy graph show` command to display
the intent graph in ASCII format.

Closes #42
```

## Project Structure

```
jig/
├── src/jig/           # Source code
│   ├── cli/           # CLI commands
│   ├── core/          # Core functionality
│   └── utils/         # Utility functions
├── tests/             # Test suite
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
├── docs/              # Documentation
├── templates/         # Node templates
└── jig/               # Example JIG directory
```

## Testing Guidelines

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Test file names must start with `test_`
- Test function names must start with `test_`
- Use descriptive test names that explain what is being tested

Example:
```python
def test_parser_extracts_frontmatter_from_markdown():
    """Test that parser correctly extracts YAML frontmatter."""
    # Arrange
    content = "---\nid: O-TEST-001\n---\n# Content"
    
    # Act
    result = parse_frontmatter(content)
    
    # Assert
    assert result["id"] == "O-TEST-001"
```

### Test Coverage

- Aim for >80% code coverage
- All new features must include tests
- Bug fixes should include regression tests

## Pull Request Process

1. **Fork and Branch**
   ```bash
   git checkout -b feat/my-new-feature
   ```

2. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Validate**
   ```bash
   make validate
   ```

4. **Commit**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feat/my-new-feature
   ```
   Then create a pull request on GitHub

6. **PR Requirements**
   - All tests must pass
   - Code coverage should not decrease
   - Code must pass linting and type checking
   - Include clear description of changes
   - Reference any related issues

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions and classes
- Update relevant docs in `docs/` directory
- Include examples for new features

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to JIG! 🎉

