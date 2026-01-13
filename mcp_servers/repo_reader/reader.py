import os
from pathlib import Path
from typing import List, Set
from schemas.base import FileData


class RepoReader:
    """MCP Server: Read Repository Files"""

    # Directories to ignore
    IGNORE_DIRS = {
        ".git",
        "node_modules",
        "__pycache__",
        "venv",
        ".venv",
        "dist",
        "build",
        ".next",
        ".cache",
        "coverage",
        ".pytest_cache",
        ".mypy_cache",
        "target",
    }

    # File extensions to include (code only)
    CODE_EXTENSIONS = {
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".java",
        ".go",
        ".rs",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".cs",
        ".rb",
        ".php",
        ".swift",
        ".kt",
        ".scala",
        ".sh",
        ".md",
    }

    # Files to ignore
    IGNORE_FILES = {
        ".DS_Store",
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "Pipfile.lock",
        "poetry.lock",
        ".gitignore",
    }

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists() or not self.repo_path.is_dir():
            raise ValueError(f"Repository path does not exist: {repo_path}")

        self._files_cache: dict[str, FileData] = {}

    def read_files(self, file_path: str) -> FileData:
        """Read a single file with metadata"""
        if file_path in self._files_cache:
            return self._files_cache[file_path]

        full_path = self.repo_path / file_path
        if not full_path.exists() or not full_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                content = "".join(lines)

                file_data = FileData(
                    path=str(file_path),
                    content=content,
                    lines=lines,
                    line_count=len(lines),
                    size=full_path.stat().st_size,
                    extension=full_path.suffix,
                )

                self._files_cache[file_path] = file_data
                return file_data
        except Exception as e:
            raise IOError(f"Error reading file {file_path}: {e}")
