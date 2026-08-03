# Automatically load variables from .env
set dotenv-load

# Variables
compose_file := "docker/docker-compose.mongo.yaml"
env_file := ".env"

# Global Logging Utilities
log := "uv run rich --print"
panel := "uv run rich --print --panel double"


# Default recipe
default:
    @just --list

# ==============================================================================
# 🌿 Git Workflow Recipes
# ==============================================================================

[group('git')]
gpush +message:
    @{{panel}} "[bold green]🌿 INITIATING GIT WORKFLOW[/]"
    @{{log}} "[yellow]📦 Staging all changes...[/]"
    git add .
    @{{log}} "[yellow]📝 Committing with message: {{message}}[/]"
    git commit -m "{{message}}" || true
    @{{log}} "[yellow]🚀 Pushing to remote...[/]"
    git push
    @{{panel}} "[bold blue]✅ ALL DONE! Your branch is up to date.[/]"
    git pull

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
    find . -type d -name ".git" -prune -o -type d -name "__pycache__" -exec rm -rf {} +

# Stop everything, clean artifacts, sync dependencies, and start all services fresh
[group('maintenance')]
restart-all: mongo-down zenml-down clean sync mongo-up zenml-up
    echo "All services successfully restarted and fresh!"

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

# Run ETL-related tests (spins up MongoDB for pipeline-backed tests)
[group('testing')]
test-run-etl *args: mongo-up
    uv run pytest -vv tests -k "run_etl or etl" {{args}}

# Run ALL tests (spins up MongoDB)
[group('testing')]
test-all *args: mongo-up
    uv run pytest -vv {{args}}

# ==============================================================================
# 🚀 ZenML Lifecycle Recipes
# ==============================================================================

# Spin up ZenML locally and connect (saving output to logs)
[group('zenml')]
zenml-up:
    @{{log}} "[yellow]Starting and connecting to ZenML local server...[/]"
    uv run zenml login --local 2>&1 | uv run python tools/logger_filter.py "$ZENML_LOGS_FILE"
    @{{log}} "[yellow]Waiting 5 seconds for ZenML server daemon to initialize...[/]"
    sleep 5
    @{{panel}} "[bold blue]ZenML local server is ready and active![/]"

# Stop the ZenML local server
[group('zenml')]
zenml-down:
    uv run zenml logout --local

# ==============================================================================
# ⚙️ Execution Recipes
# ==============================================================================

# Run the ETL service end-to-end
[group('core-services')]
etl:
    uv run python tools/run_etl.py 2>&1 | uv run python tools/logger_filter.py "$ETL_LOGS_FILE"
