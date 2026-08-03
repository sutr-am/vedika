# Automatically load variables from .env
set dotenv-load

# Variables
compose_file := "docker/docker-compose.mongo.yaml"
env_file := ".env"

# Global Logging Utilities
log := "uv run rich --print"
panel := "uv run rich --print --panel double"

# Default recipe....must be the first recipe in the file
default:
    @just --list

# ==============================================================================
# 🛠️ Master Execution Macros (Unquoted & Clean)
# ==============================================================================

# Run command with a Rich box and log filtering
_run_logged log_file +cmd:
    @python3 -c 'from rich import print; from rich.panel import Panel; import sys; print(Panel(f"[bold cyan]{sys.argv[1]}[/bold cyan]", title="Executing Command", border_style="blue"))' "{{cmd}}"
    @{{cmd}} 2>&1 | uv run python tools/logger_filter.py "{{log_file}}"

# Run command with a Rich box only (and fail fast on non-zero exit codes)
_run +cmd:
    @python3 -c 'from rich import print; from rich.panel import Panel; import sys; print(Panel(f"[bold cyan]{sys.argv[1]}[/bold cyan]", title="Executing Command", border_style="blue"))' "{{cmd}}"
    @sh -c '{{cmd}}'

# ==============================================================================
# 🌿 Git Workflow Recipes
# ==============================================================================

[group('git')]
gpush +message:
    @{{panel}} "[bold green] INITIATING GIT WORKFLOW[/]"
    @just _run git status
    @just _run git add .
    @just _run "git commit -m '{{message}}'"
    @just _run git push
    @just _run git pull


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
    @just _run uv run ruff check .
    @just _run uv run ruff format --check .

# Automatically fix lint issues and format code
[group('code-quality')]
check-fix-format:
    @just _run uv run ruff check --select I --fix .
    @just _run uv run ruff format

# Format codebase using ruff
[group('code-quality')]
format:
    # @just _run uv run ruff check --select I --fix .
    @just _run uv run ruff format

# Shows the tree structure of the CWD without any excluded files
[group('code-quality')]
tree:
    tree -I '__pycache__|*.pyc|__init__.py|*.egg-info'

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
# 🚀 ZenML Lifecycle Recipes
# ==============================================================================

# Spin up ZenML locally and connect (saving output to logs)
[group('zenml')]
zenml-up:
    @{{log}} "[yellow]Starting and connecting to ZenML local server...[/]"
    @just _run_logged "$ZENML_LOGS_FILE" uv run zenml login --local
    @{{log}} "[yellow]Waiting 5 seconds for ZenML server daemon to initialize...[/]"
    @just _run sleep 5
    @{{panel}} "[bold blue]ZenML local server is ready and active![/]"

# Stop the ZenML local server
[group('zenml')]
zenml-down:
    @just _run uv run zenml logout --local

# ==============================================================================
# 🧹 Maintenance Recipes
# ==============================================================================

# Clean build artifacts, cache, and compiled bytecode
[group('maintenance')]
clean:
    @just _run find . -type d -name ".git" -prune -o -type d -name "__pycache__" -exec rm -rf {} +
    @just _run rm -rf .venv .pytest_cache .ruff_cache build dist src/*.egg-info

# Stop everything, clean artifacts, sync dependencies, and start all services fresh
[group('maintenance')]
restart-all: mongo-down zenml-down clean sync format mongo-up zenml-up
    @just _run echo "All services successfully restarted and fresh!"

# ==============================================================================
# ==============================================================================
# 🧪 Testing & Execution Recipes
# ==============================================================================

# Run fast unit tests only (no MongoDB required)
[group('testing')]
test-unit *args:
    @just _run uv run pytest -vv tests/unit {{args}}

# Run integration/DB tests (automatically spins up MongoDB)
[group('testing')]
test-integration *args: mongo-up
    @just _run uv run pytest -vv tests/integration {{args}}

# Run ETL-related tests (spins up MongoDB for pipeline-backed tests)
[group('testing')]
test-run-etl *args: mongo-up
    @just _run uv run pytest -vv tests -k "run_etl or etl" {{args}}

# Run ALL tests (spins up MongoDB)
[group('testing')]
test-all *args: mongo-up
    @just _run uv run pytest -vv {{args}}

# ==============================================================================
# ⚙️ Execution Recipes
# ==============================================================================

# Run the ETL service end-to-end
[group('core-services')]
etl:
    @just _run_logged "$ETL_LOGS_FILE" uv run python tools/run_etl.py
    @{{log}} "[green]✅ Pipeline execution finished![/]"

