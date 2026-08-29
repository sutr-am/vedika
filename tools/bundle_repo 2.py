from pathlib import Path

# Directories and extensions to ignore
IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "egg-info",
    ".build",
    "dist",
    "docs",
    "tests",
    "tmp",
    "trash",
    ".vscode",
    ".github",
    ".git",
    ".pycharm",
}

IGNORE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".pyc",
    ".pyo",
    ".pyd",
    ".lock",
    ".DS_Store",
}

# Mapping extensions to markdown syntax highlighting
SYNTAX_MAP = {
    ".py": "python",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".json": "json",
    ".md": "markdown",
    ".puml": "plantuml",
    ".sh": "bash",
}


def bundle_repository(
    repo_root: Path = Path("."),
    output_file: Path = Path("repo_bundle.md"),
    target_dirs: list[str] = ["src", "configs", "docker"],
) -> None:
    output_lines: list[str] = [f"# Codebase Snapshot: {repo_root.resolve().name}\n\n"]

    file_paths: list[Path] = []

    # Collect files from targeted subdirectories, or fallback to root if not found
    for target in target_dirs:
        target_path = repo_root / target
        if target_path.exists():
            file_paths.extend(target_path.rglob("*"))
        else:
            print(f"Warning: directory '{target}' not found. Skipping.")

    # Sort files alphabetically for consistent ordering
    file_paths = sorted([f for f in file_paths if f.is_file()])

    processed_count = 0
    for file_path in file_paths:
        # Check ignored directories in the path
        if any(part in IGNORE_DIRS or part.endswith(".egg-info") for part in file_path.parts):
            continue

        # Check ignored file extensions
        if file_path.suffix in IGNORE_EXTENSIONS:
            continue

        rel_path = file_path.relative_to(repo_root)
        lang = SYNTAX_MAP.get(file_path.suffix, "")

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Skip binary or unreadable files
            continue

        # Append markdown block with header and separator
        output_lines.append(f"## `{rel_path}`\n\n")
        output_lines.append(f"```{lang}\n")
        output_lines.append(content.rstrip() + "\n")
        output_lines.append("```\n\n")
        output_lines.append("---\n\n")

        processed_count += 1

    output_file.write_text("".join(output_lines), encoding="utf-8")
    print(f"Bundled {processed_count} files into {output_file.resolve()}")


if __name__ == "__main__":
    bundle_repository()
