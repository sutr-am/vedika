# default recipe to show available commands
default:
    @just --list

# Sync virtual environment and install all dependencies
sync:
    uv sync

# RUn unit tests
test:
    uv run pytest tests/unit

# Run linter and formatter checks
lint:
    uv run ruff check .
    uv run ruff format --check .

# Automatically fix lint issues and format code
check_fix_format:
    uv run ruff check --fix .
    uv run ruff format

format:
    uv run ruff format

# Clean build artifacts and bytecode cache
clean:
    rm -rf .venv .pytest_cache .ruff_cache build dist src/*.egg-info
    find . -type d -name "__pycache__" -exec rm -rf {} +

