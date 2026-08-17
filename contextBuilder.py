import os

# Configuration
OUTPUT_FILE = "codebase_context.md"

# Directories to skip
EXCLUDE_DIRS = {
    "__pycache__", 
    ".git",
    ".vscode",
    ".claude",
    "node_modules",
    ".pytest_cache",
    "venv",
    ".venv",
    "llama.cpp",
    "gradio-app",
    "notebooks",
    "docs"
    
}

# Files or extensions to skip
EXCLUDE_FILES = {
    ".env",
    "codebase_context.md",
    "logs.txt",
    ".DS_Store",
    ".gitignore",
    "results_raw.json"
}

EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
    ".zip",
    ".tar",
    ".gz",
    ".sqlite3",
    ".db",
    ".md"
}


def is_text_file(filename):
    """Check if file has a binary extension."""
    _, ext = os.path.splitext(filename)
    return ext.lower() not in EXCLUDE_EXTENSIONS


def generate_markdown_context(root_dir="."):
    count = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_file:
        out_file.write("# Codebase Context\n\n")

        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Modify dirnames in-place to skip excluded directories
            dirnames[:] = [
                d
                for d in dirnames
                if d not in EXCLUDE_DIRS and not d.startswith(".")
            ]

            for filename in filenames:
                if filename in EXCLUDE_FILES or not is_text_file(filename):
                    continue

                full_path = os.path.join(dirpath, filename)
                relative_path = os.path.relpath(full_path, root_dir)

                # Infer code block language from file extension
                ext = os.path.splitext(filename)[1].lstrip(".")
                lang_map = {
                    "py": "python",
                    "js": "javascript",
                    "ts": "typescript",
                    "json": "json",
                    "md": "markdown",
                    "html": "html",
                    "css": "css",
                    "sh": "bash",
                    "yml": "yaml",
                    "yaml": "yaml",
                    "txt": "text",
                }
                lang = lang_map.get(ext, "")

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    out_file.write(f"## File: `{relative_path}`\n\n")
                    out_file.write(f"```{lang}\n")
                    out_file.write(content)
                    out_file.write("\n```\n\n")
                    out_file.write("---\n\n")

                    count += 1
                    print(f"Added: {relative_path}")
                except Exception as e:
                    print(f"Skipped {relative_path} (Error reading file: {e})")

    print(
        f"\nDone! Processed {count} files and saved to `{OUTPUT_FILE}`."
    )


if __name__ == "__main__":
    generate_markdown_context()