.PHONY: help install install-dev clean test lint format typecheck validate all dev-setup

# Default target
help:
	@echo "JIG Development Commands"
	@echo "========================"
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Create venv and install package"
	@echo "  make install-dev  - Create venv and install with dev dependencies"
	@echo "  make dev-setup    - Full development setup (install-dev + validate)"
	@echo ""
	@echo "Development:"
	@echo "  make test         - Run tests with pytest"
	@echo "  make lint         - Run ruff linter"
	@echo "  make format       - Format code with ruff"
	@echo "  make typecheck    - Run mypy type checker"
	@echo "  make validate     - Run all checks (lint + typecheck + test)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Remove venv, cache, and build artifacts"
	@echo ""
	@echo "Quick start: make dev-setup"

# Create virtual environment and install package
install:
	@echo "Creating virtual environment..."
	@test -d .venv || python3 -m venv .venv
	@echo "Installing jig..."
	@.venv/bin/pip install --upgrade pip
	@.venv/bin/pip install -e .
	@echo ""
	@echo "✓ Installation complete!"
	@echo "  Activate with: source .venv/bin/activate"
	@echo "  Then run: jigy --help"

# Create virtual environment and install with dev dependencies
install-dev:
	@echo "Creating virtual environment..."
	@test -d .venv || python3 -m venv .venv
	@echo "Installing jig with dev dependencies..."
	@.venv/bin/pip install --upgrade pip
	@.venv/bin/pip install -e ".[dev]"
	@echo ""
	@echo "✓ Development installation complete!"
	@echo "  Activate with: source .venv/bin/activate"
	@echo "  Then run: jigy --help"

# Full development setup
dev-setup: install-dev
	@echo ""
	@echo "Running initial validation..."
	@.venv/bin/pytest --version
	@.venv/bin/ruff --version
	@.venv/bin/mypy --version
	@echo ""
	@echo "✓ Development environment ready!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. source .venv/bin/activate"
	@echo "  2. jigy --help"
	@echo "  3. make test"

# Run tests
test:
	@echo "Running tests..."
	@.venv/bin/pytest -v

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	@.venv/bin/pytest --cov=src/jig --cov-report=term-missing --cov-report=html

# Run linter
lint:
	@echo "Running ruff linter..."
	@.venv/bin/ruff check src/ tests/

# Format code
format:
	@echo "Formatting code with ruff..."
	@.venv/bin/ruff format src/ tests/
	@.venv/bin/ruff check --fix src/ tests/

# Run type checker
typecheck:
	@echo "Running mypy type checker..."
	@.venv/bin/mypy src/

# Run all validation checks
validate: lint typecheck test
	@echo ""
	@echo "✓ All checks passed!"

# Alias for common workflow
all: validate

# Clean up build artifacts and virtual environment
clean:
	@echo "Cleaning up..."
	@rm -rf .venv
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info
	@rm -rf src/*.egg-info
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@rm -rf htmlcov/
	@rm -rf .coverage
	@echo "✓ Cleanup complete!"

