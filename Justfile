# Automatically load variables from .env
set dotenv-load

# Variables
compose_file := "docker/docker-compose.yaml"
env_file := ".env"
dc := "docker compose --env-file " + env_file + " -f " + compose_file


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

[group('git')]
grebase +message:
    @{{panel}} "[bold green] INITIATING GIT WORKFLOW[/]"
    @just _run git status
    @just _run git add .
    @just _run "git commit -m '{{message}}'"
    @just _run git fetch origin
    @just _run git rebase origin/main
    @just _run git push origin 03_data_engineering --force-with-lease
    @just _run git pull

# Render architecture diagram to SVG
[group('docs')]
svg2png:
    @just _run rsvg-convert -d 600 -p 600 docs/vedika_architecture.svg -o docs/vedika_architecture.png
    @just _run rsvg-convert -d 600 -p 600 docs/vedika_runtime.svg -o docs/vedika_runtime.png

# Render architecture diagram to SVG
[group('docs')]
render-diagrams:
    @just _run plantuml -tsvg docs/*.puml
    just svg2png

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
    @just _run uv run ruff check --select I --fix --show-fixes .
    @just _run uv run ruff format

# Format codebase using ruff
[group('code-quality')]
format:
    # @just _run uv run ruff check --select I --fix --show-fixes .
    @just _run uv run ruff format

# [group('code-quality')]
# format_v2:
#     uv run ruff check --select I --fix --show-fixes .
#     @echo "\nFormatting files:"
#     -@uv run ruff format --check . | grep "Would reformat" || true
#     uv run ruff format .


# Shows the tree structure of the CWD without any excluded files
[group('code-quality')]
tree path=".":
    tree -I '__pycache__|*.pyc|__init__.py|*.egg-info' {{path}}

# ==============================================================================
# 🗄️ Database Lifecycle Recipes
# ==============================================================================
# Target a specific database by passing its service name ('mongodb' or 'qdrant').
# If no name is provided, the command applies to ALL databases simultaneously.

# Build and spin up container(s)
[group('database')]
db-up service="":
    @just _run "{{dc}} up -d --build {{service}}"

# Stop and remove container(s) safely (leaves the network running for other DBs)
[group('database')]
db-down service="":
    @just _run "{{dc}} rm -s -f {{service}}"

# Stream real-time logs
[group('database')]
db-logs service="":
    {{dc}} logs -f {{service}}

# Soft restart container(s) without losing data
[group('database')]
db-restart service="":
    just db-down {{service}}
    just db-up {{service}}

# Hard reset EVERYTHING (Global kill switch - deletes all database volumes!)
[group('database')]
db-reset-all:
    @just _run "{{dc}} down -v"
    just db-up

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
restart-all: db-down zenml-down clean sync format db-up zenml-up
    @just _run echo "All services successfully restarted and fresh!"


# Stop everything, clean artifacts, and sync dependencies
[group('maintenance')]
stop-all: db-down zenml-down
    @just _run echo "All services successfully shut down"

# ==============================================================================
# ==============================================================================
# 🧪 Testing & Execution Recipes
# ==============================================================================

# Run fast unit tests only (no DB required)
[group('testing')]
test-unit *args:
    @just _run uv run pytest -vv tests/unit {{args}}

# Run integration/DB tests (automatically spins up all DB)
[group('testing')]
test-integration *args: db-up
    @just _run "uv run pytest -vv tests/integration {{args}}"


# Run ETL-related tests (spins up all DB for pipeline-backed tests)
[group('testing')]
test-run-etl *args: db-up
    @just _run uv run pytest -vv tests -k "run_etl or etl" {{args}}

# Run ALL tests (spins up all DB)
[group('testing')]
test-all *args: db-up
    @just _run uv run pytest -vv {{args}}

# Run all tests or pass a specific path (e.g., just test tests/infrastructure/)
[group('testing')]
test path="tests/":
    @just _run uv run pytest {{path}} -v


# ==============================================================================
# ⚙️ Execution Recipes
# ==============================================================================

# Run the ETL service end-to-end
[group('core-services')]
etl:
    @just _run_logged "$ETL_LOGS_FILE" ZENML_LOGGING_VERBOSITY=WARN PYTHONPATH=src uv run python tools/run_etl.py
    @{{log}} "[green]✅ Pipeline execution finished![/]"


# Run the Feature Engineering service end-to-end
[group('core-services')]
feature-engineering:
    @just _run_logged "$ETL_LOGS_FILE" ZENML_LOGGING_VERBOSITY=WARN PYTHONPATH=src uv run python tools/run_feature_engineering.py
    @{{log}} "[green]✅ Pipeline execution finished![/]"

