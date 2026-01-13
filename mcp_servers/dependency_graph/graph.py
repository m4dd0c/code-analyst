import ast
from pathlib import Path
from typing import Dict, List, Optional, Set
from schemas.base import DependencyData
from mcp_servers.repo_reader.reader import RepoReader


class DependencyGraph:
    """MCP Server: Build and query dependency graph"""

    def __init__(self, repo_reader: RepoReader):
        self.reader = repo_reader
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
            if file_data.extension == ".py":
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

    def _extract_python_imports(self, code: str, file_path: str) -> List[str]:
        """Extract import statements from Python code using AST"""
        imports = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return imports

        repo_root = self.reader.repo_path
        file_dir = (repo_root / file_path).parent

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_path = self._resolve_module_to_file(alias.name, file_dir)
                    if module_path:
                        imports.append(module_path)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_path = self._resolve_module_to_file(node.module, file_dir)
                    if module_path:
                        imports.append(module_path)

        return list(set(imports))

    def _resolve_module_to_file(
        self, module_name: str, current_dir: Path
    ) -> Optional[str]:
        """Convert module name to relative file path"""
        repo_root = self.reader.repo_path

        # Convert module path to file path
        # e.g., "agents.dependency" -> "agents/dependency.py"
        module_parts = module_name.split(".")

        # Try as relative import from current directory
        potential_file = current_dir / "/".join(module_parts)
        for suffix in [".py", "/__init__.py"]:
            test_path = Path(str(potential_file) + suffix)
            if test_path.exists():
                return str(test_path.relative_to(repo_root))

        # try as absolute import from repo root
        potential_file = repo_root / "/".join(module_parts)
        for suffix in [".py", "/__init__.py"]:
            test_path = Path(str(potential_file) + suffix)
            if test_path.exists():
                return str(test_path.relative_to(repo_root))

        return None
