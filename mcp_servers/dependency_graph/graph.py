import ast
from pathlib import Path
from typing import Dict, List, Set
from schemas.base import DependencyData
from mcp_servers.repo_reader.reader import RepoReader


class DependencyGraph:
    """MCP Server: Build and query dependency graph"""

    def __init__(self, repo_reader: RepoReader):
        self.repo_reader = repo_reader
        self.graph: Dict[str, DependencyData] = {}
        self._built = False

    def build(self) -> Dict[str, DependencyData]:
        """Build the dependency graph from repository"""
        if self._built:
            return self.graph

        print("🔨 Building dependency graph...")
        files = self.reader.walk_repo()

        import_map = {}
        # extract imports from each file
        for file_data in files:
            if file_data.path.suffix == ".py":
                imports = self._extract_python_imports(
                    file_data.content, file_data.path
                )
                import_map[file_data.path] = imports

        # build graph for forward edges (imports)
        for file_path, imports in import_map.items():
            self.graph[file_path] = DependencyData(
                file_path=file_path,
                imports=imports,
                imported_by=[],
                fan_in=0,
                fan_out=len(imports),
            )

        # build graph for reverse edges (imported_by)
        for file_path, data in self.graph.items():
            for imported_path in data.imports:
                if imported_path in self.graph:
                    self.graph[imported_path].imported_by.append(file_path)

        # calc fan_in
        for file_path in self.graph:
            self.graph[file_path].fan_in = len(self.graph[file_path].imported_by)

        self._built = True
        print(f"✅ Graph built:  {len(self.graph)} files analyzed")
        return self.graph
