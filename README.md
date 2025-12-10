# JIG — Keep specs, code, and tests aligned

JIG is a tool for maintaining traceability between specifications, implementation, and tests. It helps you ensure that every specification is implemented and tested.

## Installation

```bash
pip install jig
```

## Quick Start

```bash
# Initialize JIG in your project
mkdir -p jig/specifications jig/outcomes

# Validate your artifacts
jigy validate

# Rebuild all graphs
jigy rebuild

# Run full alignment check
jigy align
```

## Configuration

JIG works out of the box with standard Python project layouts:

```
my-project/
├── src/           # Source code
├── test/          # Tests
└── jig/           # JIG artifacts
    ├── specifications/
    ├── outcomes/
    └── bricks.yaml
```

For custom layouts, create a `jig.toml` in your project root:

```toml
[jig.paths]
source = "lib"      # Custom source directory
tests = "tests"     # Custom test directory
```

See [Configuration Guide](docs/configuration.md) for full details.

## Commands

| Command | Description |
|---------|-------------|
| `jigy validate` | Validate all JIG artifacts |
| `jigy validate intent` | Validate specifications and outcomes |
| `jigy validate bricks` | Validate brick definitions |
| `jigy rebuild` | Rebuild all graphs |
| `jigy rebuild impl` | Rebuild implementation graph |
| `jigy rebuild verify` | Rebuild verification graph |
| `jigy rebuild intent` | Rebuild intent graph |
| `jigy align` | Full alignment: rebuild + validate + summary |
| `jigy show` | Display project structure overview |
| `jigy show layers` | Display layer hierarchy |
| `jigy show bricks` | Display brick details |

## Decorators

Mark your code with JIG decorators:

```python
import jig

@jig.implements("S-001")
def my_function():
    """Implementation of specification S-001."""
    pass

@jig.verifies("S-001")
def test_my_function():
    """Test for specification S-001."""
    pass
```

## Documentation

- [Configuration Guide](docs/configuration.md)
- [Contributing](CONTRIBUTING.md)

## License

MIT
