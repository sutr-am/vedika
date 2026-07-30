# Variables
compose_file := "docker/docker-compose.mongo.yaml"
env_file := ".env"

# Default recipe
default:
    @just --list
# ==============================================================================
# 🗄️ Database Lifecycle Recipes
# ==============================================================================

# Build and spin up MongoDB container in the background (preserves data)
[group('database')]
mongo-up:
    docker compose --env-file {{env_file}} -f {{compose_file}} up -d --build

# Stop and remove MongoDB container (data volume remains safe)
[group('database')]
mongo-down:
    docker compose --env-file {{env_file}} -f {{compose_file}} down

# Stream real-time MongoDB container logs
[group('database')]
mongo-logs:
    docker compose --env-file {{env_file}} -f {{compose_file}} logs -f

# Soft restart MongoDB container (reboots service without losing data)
[group('database')]
mongo-restart: mongo-down mongo-up

# Hard reset MongoDB (deletes database volume and starts fresh from scratch)
[group('database')]
mongo-reset:
    docker compose --env-file {{env_file}} -f {{compose_file}} down -v
    just mongo-up

# ==============================================================================
# 📦 Environment & Dependency Recipes
# ==============================================================================

# Sync virtual environment and install all dependencies
[group('environment')]
sync:
    uv sync

# ==============================================================================
# 🧹 Code Quality & Formatting Recipes
# ==============================================================================

# Run linter and format checks
[group('code-quality')]
lint:
    uv run ruff check .
    uv run ruff format --check .

# Automatically fix lint issues and format code
[group('code-quality')]
check-fix-format:
    uv run ruff check --select I --fix .
    uv run ruff format

# Format codebase using ruff
[group('code-quality')]
format:
    uv run ruff check --select I --fix .
    uv run ruff format

# ==============================================================================
# 🧹 Maintenance Recipes
# ==============================================================================

# Clean build artifacts, cache, and compiled bytecode
[group('maintenance')]
clean:
    rm -rf .venv .pytest_cache .ruff_cache build dist src/*.egg-info
    find . -type d -name "__pycache__" -exec rm -rf {} +

# ==============================================================================
# ==============================================================================
# 🧪 Testing & Execution Recipes
# ==============================================================================

# Run fast unit tests only (no MongoDB required)
[group('testing')]
test-unit *args:
    uv run pytest -vv tests/unit {{args}}

# Run integration/DB tests (automatically spins up MongoDB)
[group('testing')]
test-integration *args: mongo-up
    uv run pytest -vv tests/integration {{args}}

# Run ALL tests (spins up MongoDB)
[group('testing')]
test-all *args: mongo-up
    uv run pytest -vv {{args}}