from typing import Optional, Dict, Any, Set
from aegis.agents.base import BaseAgent
from aegis.schemas.base import AgentOutput, Evidence
from aegis.mcp_servers.dependency_graph.graph import DependencyGraph


class DependencyAgent(BaseAgent):
    """
    Dependency Agent:  Analyzes and explains dependency relationships.

    Capabilities:
    - What does file X depend on?
    - What depends on file X?
    - Find circular dependencies
    - Trace dependency chains
    - Calculate coupling metrics

    Confidence scoring:
    - 1. 0 for direct queries (deterministic graph data)
    - Lower for inferred chains or complex paths
    """

    def __init__(self, dependency_graph: DependencyGraph):
        super().__init__(name="DependencyAgent")
        self.graph = dependency_graph

    def analyze(self, context: Optional[Dict[str, Any]] = None) -> AgentOutput:
        """
        Analyze dependencies for a file or the entire codebase.

        Context keys:
        - file_path: File to analyze (required for specific queries)
        - query_type: 'dependencies' | 'dependents' | 'both' | 'impact' (default: 'both')
        - max_depth: Maximum depth for transitive dependencies (default: 2)
        - include_metrics: Include coupling metrics (default: True)

        Returns:
            AgentOutput with dependency analysis and evidence
        """
        if not context or "file_path" not in context:
            raise ValueError("DependencyAgent requires 'file_path' in context")

        # Build graph if not already built
        if not self.graph._built:
            self.graph.build()

        file_path = context["file_path"]
        query_type = context.get("query_type", "both")
        max_depth = context.get("max_depth", 2)
        include_metrics = context.get("include_metrics", True)

        # Validate file exists in graph
        if file_path not in self.graph.graph:
            return AgentOutput(
                analysis=f"❌ File not found in dependency graph: `{file_path}`\n\n"
                f"This file either doesn't exist, is not a code file, or has no dependencies.",
                evidence=[
                    Evidence(
                        file_path=file_path,
                        reason="File not found in analyzed codebase",
                    )
                ],
                confidence=1.0,
            )

        # Route to appropriate analysis
        if query_type == "dependencies":
            return self._analyze_dependencies(file_path, max_depth, include_metrics)
        elif query_type == "dependents":
            return self._analyze_dependents(file_path, max_depth, include_metrics)
        elif query_type == "impact":
            return self._analyze_impact(file_path, max_depth)
        else:  # 'both'
            return self._analyze_both(file_path, max_depth, include_metrics)

    def _analyze_dependencies(
        self, file_path: str, max_depth: int, include_metrics: bool
    ) -> AgentOutput:
        """Analyze what this file depends on"""
        dependencies = self.graph.get_dependencies(file_path)
        data = self.graph.graph[file_path]

        analysis_parts = [
            f"**Dependencies of `{file_path}`**\n",
            f"This file imports **{len(dependencies)} file(s)**:\n",
        ]

        if dependencies:
            for dep in dependencies:
                analysis_parts.append(f"- `{dep}`")

            # Transitive dependencies
            if max_depth > 1:
                transitive = self._get_transitive_dependencies(file_path, max_depth)
                if len(transitive) > len(dependencies):
                    analysis_parts.append(
                        f"\n**Transitive dependencies** (depth {max_depth}): {len(transitive)} total files"
                    )
        else:
            analysis_parts.append("- *(No dependencies - this is a leaf module)*")

        # Metrics
        if include_metrics:
            analysis_parts.append("\n**Coupling Metrics**:")
            analysis_parts.append(f"- Fan-out (outgoing): {data.fan_out}")
            analysis_parts.append(f"- Fan-in (incoming): {data.fan_in}")

            coupling_score = self._calculate_coupling(data.fan_in, data.fan_out)
            analysis_parts.append(f"- Coupling score: {coupling_score:.2f}/1.0")
            analysis_parts.append(f"\n{self._interpret_coupling(coupling_score)}")

        # Build evidence
        evidence = [
            Evidence(
                file_path=file_path,
                reason=f"Has {len(dependencies)} direct dependencies (fan-out: {data.fan_out})",
            )
        ]

        for dep in dependencies:
            evidence.append(
                Evidence(
                    file_path=dep,
                    reason=f"Imported by {file_path}",
                )
            )

        return AgentOutput(
            analysis="\n".join(analysis_parts),
            evidence=evidence,
            confidence=1.0,  # Direct graph query - deterministic
            metadata={
                "file": file_path,
                "dependency_count": len(dependencies),
                "fan_out": data.fan_out,
                "fan_in": data.fan_in,
            },
        )

    def _analyze_dependents(
        self, file_path: str, max_depth: int, include_metrics: bool
    ) -> AgentOutput:
        """Analyze what depends on this file"""
        dependents = self.graph.get_dependents(file_path)
        data = self.graph.graph[file_path]

        analysis_parts = [
            f"**Dependents of `{file_path}`**\n",
            f"**{len(dependents)} file(s)** depend on this:\n",
        ]

        if dependents:
            for dep in dependents[:20]:  # Limit display
                analysis_parts.append(f"- `{dep}`")

            if len(dependents) > 20:
                analysis_parts.append(f"- ... and {len(dependents) - 20} more")

            # Transitive dependents
            if max_depth > 1:
                transitive = self._get_transitive_dependents(file_path, max_depth)
                if len(transitive) > len(dependents):
                    analysis_parts.append(
                        f"\n**Transitive dependents** (depth {max_depth}): {len(transitive)} total files"
                    )
                    analysis_parts.append(
                        f"⚠️  **Blast radius**:  Changing this file could affect {len(transitive)} files"
                    )
        else:
            analysis_parts.append(
                "- *(No dependents - this file is not imported by anyone)*"
            )
            analysis_parts.append("\n💡 This might be dead code or an entry point.")

        # Metrics
        if include_metrics:
            analysis_parts.append("\n**Coupling Metrics**:")
            analysis_parts.append(f"- Fan-in (incoming): {data.fan_in}")
            analysis_parts.append(f"- Fan-out (outgoing): {data.fan_out}")

        # Build evidence
        evidence = [
            Evidence(
                file_path=file_path,
                reason=f"Imported by {len(dependents)} files (fan-in: {data.fan_in})",
            )
        ]

        for dep in dependents:
            evidence.append(
                Evidence(
                    file_path=dep,
                    reason=f"Imports {file_path}",
                )
            )

        return AgentOutput(
            analysis="\n".join(analysis_parts),
            evidence=evidence,
            confidence=1.0,
            metadata={
                "file": file_path,
                "dependent_count": len(dependents),
                "fan_in": data.fan_in,
                "fan_out": data.fan_out,
            },
        )

    def _analyze_both(
        self, file_path: str, max_depth: int, include_metrics: bool
    ) -> AgentOutput:
        """Analyze both dependencies and dependents"""
        dependencies = self.graph.get_dependencies(file_path)
        dependents = self.graph.get_dependents(file_path)
        data = self.graph.graph[file_path]

        analysis_parts = [
            f"**Dependency Analysis for `{file_path}`**\n",
            f"**Dependencies** (what this imports): {len(dependencies)}",
            f"**Dependents** (what imports this): {len(dependents)}\n",
        ]

        # Dependencies
        if dependencies:
            analysis_parts.append("**Imports:**")
            for dep in dependencies[:10]:
                analysis_parts.append(f"  - `{dep}`")
            if len(dependencies) > 10:
                analysis_parts.append(f"  - ... and {len(dependencies) - 10} more")
        else:
            analysis_parts.append("**Imports:** *(none - leaf module)*")

        analysis_parts.append("")

        # Dependents
        if dependents:
            analysis_parts.append("**Imported by:**")
            for dep in dependents[:10]:
                analysis_parts.append(f"  - `{dep}`")
            if len(dependents) > 10:
                analysis_parts.append(f"  - ... and {len(dependents) - 10} more")
        else:
            analysis_parts.append("**Imported by:** *(none - possible dead code)*")

        # Metrics
        if include_metrics:
            coupling_score = self._calculate_coupling(data.fan_in, data.fan_out)
            analysis_parts.append("\n**Metrics:**")
            analysis_parts.append(f"  - Fan-in: {data.fan_in}, Fan-out: {data.fan_out}")
            analysis_parts.append(f"  - Coupling:  {coupling_score:.2f}/1.0")
            analysis_parts.append(f"\n{self._interpret_coupling(coupling_score)}")

        # Build evidence
        evidence = [
            Evidence(
                file_path=file_path,
                reason=f"Fan-in: {data.fan_in}, Fan-out: {data.fan_out}",
            )
        ]

        for dep in dependencies:
            evidence.append(Evidence(file_path=dep, reason=f"Imported by {file_path}"))

        for dep in dependents:
            evidence.append(Evidence(file_path=dep, reason=f"Imports {file_path}"))

        return AgentOutput(
            analysis="\n".join(analysis_parts),
            evidence=evidence,
            confidence=1.0,
            metadata={
                "file": file_path,
                "dependencies": len(dependencies),
                "dependents": len(dependents),
            },
        )

    def _analyze_impact(self, file_path: str, max_depth: int) -> AgentOutput:
        """Analyze blast radius if this file changes"""
        dependents = self.graph.get_dependents(file_path)
        transitive = self._get_transitive_dependents(file_path, max_depth)

        # data = self.graph.graph[file_path]

        analysis_parts = [
            f"**Change Impact Analysis for `{file_path}`**\n",
            f"**Direct impact**:  {len(dependents)} files",
            f"**Total blast radius** (depth {max_depth}): {len(transitive)} files\n",
        ]

        if len(transitive) > 0:
            severity = (
                "🔴 HIGH"
                if len(transitive) > 10
                else "🟡 MEDIUM"
                if len(transitive) > 3
                else "🟢 LOW"
            )
            analysis_parts.append(f"**Severity**: {severity}\n")

            analysis_parts.append("**Files potentially affected:**")
            for dep in list(transitive)[:15]:
                analysis_parts.append(f"  - `{dep}`")

            if len(transitive) > 15:
                analysis_parts.append(f"  - ...  and {len(transitive) - 15} more")

            analysis_parts.append(
                f"\n⚠️  **Recommendation**: Changes to this file require testing {len(transitive)} dependent files."
            )
        else:
            analysis_parts.append(
                "✅ **Low risk**: No files depend on this.  Changes are isolated."
            )

        # Build evidence
        evidence = [
            Evidence(
                file_path=file_path,
                reason=f"Blast radius:  {len(transitive)} files affected at depth {max_depth}",
            )
        ]

        for dep in transitive:
            evidence.append(
                Evidence(file_path=dep, reason=f"Transitively depends on {file_path}")
            )

        return AgentOutput(
            analysis="\n".join(analysis_parts),
            evidence=evidence,
            confidence=0.95,  # Slightly lower - transitive analysis has some uncertainty
            metadata={
                "file": file_path,
                "direct_impact": len(dependents),
                "total_impact": len(transitive),
                "max_depth": max_depth,
            },
        )

    def _get_transitive_dependencies(self, file_path: str, max_depth: int) -> Set[str]:
        """Get all transitive dependencies up to max_depth"""
        visited = set()
        queue = [(file_path, 0)]

        while queue:
            current, depth = queue.pop(0)
            if depth >= max_depth or current in visited:
                continue

            visited.add(current)
            deps = self.graph.get_dependencies(current)

            for dep in deps:
                if dep not in visited:
                    queue.append((dep, depth + 1))

        visited.discard(file_path)  # Remove self
        return visited

    def _get_transitive_dependents(self, file_path: str, max_depth: int) -> Set[str]:
        """Get all transitive dependents up to max_depth"""
        visited = set()
        queue = [(file_path, 0)]

        while queue:
            current, depth = queue.pop(0)
            if depth >= max_depth or current in visited:
                continue

            visited.add(current)
            deps = self.graph.get_dependents(current)

            for dep in deps:
                if dep not in visited:
                    queue.append((dep, depth + 1))

        visited.discard(file_path)  # Remove self
        return visited

    def _calculate_coupling(self, fan_in: int, fan_out: int) -> float:
        """Calculate coupling score (0-1)"""
        # High coupling = high fan-in OR high fan-out
        normalized_in = min(fan_in / 15.0, 1.0)
        normalized_out = min(fan_out / 15.0, 1.0)
        return max(normalized_in, normalized_out)

    def _interpret_coupling(self, coupling_score: float) -> str:
        """Interpret coupling score"""
        if coupling_score >= 0.7:
            return "🔴 **High coupling**:  This file is tightly integrated.  Changes are risky."
        elif coupling_score >= 0.4:
            return "🟡 **Moderate coupling**: Be careful with changes."
        else:
            return "🟢 **Low coupling**: This file is relatively isolated."
