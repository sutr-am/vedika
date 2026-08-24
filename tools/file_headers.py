from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"


def update_headers():
    for py_file in SRC_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        rel_path = py_file.relative_to(ROOT_DIR)
        header = f"# {rel_path}\n"

        content = py_file.read_text(encoding="utf-8")
        lines = content.splitlines(keepends=True)

        # Replace existing relative path header or insert a new one
        if lines and lines[0].startswith("# src/"):
            if lines[0] != header:
                lines[0] = header
                py_file.write_text("".join(lines), encoding="utf-8")
        else:
            py_file.write_text(header + content, encoding="utf-8")


if __name__ == "__main__":
    update_headers()
