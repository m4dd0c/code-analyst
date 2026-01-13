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

    def walk_repo(self, max_file_size: int = 1_000_000) -> List[FileData]:
        """
        Walk repository and return all code files

        Args:
            max_file_size: Maximum file size in bytes (default 1MB)
        """
        files = []
        for root, dirs, filenames in os.walk(self.repo_path):
            # filter out ignored directories IN_PLACE
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]

            for filename in filenames:
                # skip ignored files
                if filename in self.IGNORE_FILES:
                    continue

                # only process code files
                file_path = Path(root) / filename
                if file_path.suffix not in self.CODE_EXTENSIONS:
                    continue

                # Skip large files
                if file_path.stat().st_size > max_file_size:
                    print(
                        f"⚠️  Skipping large file: {file_path} ({file_path.stat().st_size} bytes)"
                    )
                    continue

                rel_path = file_path.relative_to(self.repo_path)
                try:
                    file_data = self.read_files(str(rel_path))
                    files.append(file_data)
                except Exception as e:
                    print(f"⚠️  Error reading {rel_path}: {e}")
                    continue
        return files
