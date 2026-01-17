from typing import Optional, Dict, Any, List
from collections import defaultdict
from aegis.agents.base import BaseAgent
from aegis.schemas.base import AgentOutput, Evidence
from aegis.mcp_servers.repo_reader.reader import RepoReader
from aegis.mcp_servers.dependency_graph.graph import DependencyGraph


class ArchitectureAgent(BaseAgent):
    """
    Architecture Agent:  Detects layers, boundaries, and architectural patterns.

    Detection strategies:
    - File path patterns (e.g., cli/, agents/, mcp_servers/)
    - Import direction analysis (layers should flow one way)
    - Boundary violations (e.g., MCP importing from agents)
    - Naming conventions

    Confidence scoring:
    - High confidence for clear path-based layers
    - Lower confidence for inferred patterns
    """

    def __init__(self, repo_reader: RepoReader, dependency_graph: DependencyGraph):
        super().__init__(name="ArchitectureAgent")
        self.reader = repo_reader
        self.graph = dependency_graph

    def analyze(self, context: Optional[Dict[str, Any]] = None) -> AgentOutput:
        """
        Analyze repository architecture.

        Context keys:
        - focus:  Optional layer/directory to focus on
        - include_violations: Whether to check for boundary violations (default: True)

        Returns:
            AgentOutput with architecture analysis and evidence
        """
        # Build graph if not already built
        if not self.graph._built:
            self.graph.build()

        # Parse context
        focus = context.get("focus") if context else None
        include_violations = (
            context.get("include_violations", True) if context else True
        )

        # Detect layers
        layers = self._detect_layers()

        # Detect boundary violations
        violations = []
        if include_violations:
            violations = self._detect_boundary_violations(layers)

        # Build analysis
        return self._build_analysis(layers, violations, focus)

    def _detect_layers(self) -> Dict[str, List[str]]:
        """
        Detect architectural layers based on directory structure.

        Returns:
            Dict mapping layer name to list of files in that layer
        """
        layers = defaultdict(list)

        files = self.reader.walk_repo()

        for file_data in files:
            path = file_data.path

            # Skip test files for architecture analysis
            if "test_" in path or "/tests/" in path:
                continue

            # Detect layer based on top-level directory
            parts = path.split("/")

            if len(parts) >= 2:
                top_dir = parts[0]

                # Map directories to architectural layers
                if top_dir == "cli":
                    layers["Interface Layer (CLI)"].append(path)
                elif top_dir == "agents":
                    layers["Agent Layer"].append(path)
                elif top_dir == "graph":
                    layers["Orchestration Layer"].append(path)
                elif top_dir == "mcp_servers":
                    layers["MCP Server Layer (Data)"].append(path)
                elif top_dir == "schemas":
                    layers["Schema Layer (Shared)"].append(path)
                elif top_dir == "synthesis":
                    layers["Synthesis Layer (Output)"].append(path)
                else:
                    layers["Other"].append(path)
            else:
                # Root-level files
                layers["Root"].append(path)

        return dict(layers)

    def _detect_boundary_violations(
        self, layers: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Detect architectural boundary violations.

        Rules:
        - MCP servers should not import from agents
        - Schemas should not import from anything (pure data)
        - CLI should not import from MCP directly (should go through agents/orchestration)

        Returns:
            List of violations with details
        """
        violations = []

        # Build reverse layer mapping (file -> layer)
        file_to_layer = {}
        for layer_name, files in layers.items():
            for file_path in files:
                file_to_layer[file_path] = layer_name

        # Check each file's imports
        for file_path, data in self.graph.graph.items():
            source_layer = file_to_layer.get(file_path, "Unknown")

            for imported_path in data.imports:
                target_layer = file_to_layer.get(imported_path, "Unknown")

                # Check for violations
                violation = self._check_violation(
                    file_path, source_layer, imported_path, target_layer
                )

                if violation:
                    violations.append(violation)

        return violations

    def _check_violation(
        self, source_file: str, source_layer: str, target_file: str, target_layer: str
    ) -> Optional[Dict[str, Any]]:
        """Check if an import violates architectural boundaries"""

        # Rule 1: MCP servers should not import from agents
        if "MCP Server Layer" in source_layer and "Agent Layer" in target_layer:
            return {
                "type": "layering_violation",
                "severity": "high",
                "source": source_file,
                "target": target_file,
                "reason": "MCP servers should not depend on agents (should be lower-level)",
            }

        # Rule 2: Schemas should not import from application code
        if "Schema Layer" in source_layer and target_layer not in [
            "Schema Layer",
            "Unknown",
        ]:
            return {
                "type": "schema_pollution",
                "severity": "high",
                "source": source_file,
                "target": target_file,
                "reason": "Schemas should be pure data structures with no business logic dependencies",
            }

        # Rule 3: CLI should go through orchestration, not directly to MCP
        if "Interface Layer" in source_layer and "MCP Server Layer" in target_layer:
            return {
                "type": "layer_skip",
                "severity": "medium",
                "source": source_file,
                "target": target_file,
                "reason": "CLI should interact with MCP through agents/orchestration, not directly",
            }

        # Rule 4: Orchestration importing from CLI is backwards
        if "Orchestration Layer" in source_layer and "Interface Layer" in target_layer:
            return {
                "type": "reverse_dependency",
                "severity": "medium",
                "source": source_file,
                "target": target_file,
                "reason": "Orchestration should not depend on CLI (should be inverted)",
            }

        return None

    def _build_analysis(
        self,
        layers: Dict[str, List[str]],
        violations: List[Dict[str, Any]],
        focus: Optional[str],
    ) -> AgentOutput:
        """Build final analysis output"""

        # Filter layers if focus is specified
        if focus:
            layers = {k: v for k, v in layers.items() if focus.lower() in k.lower()}

        # Build analysis text
        analysis_parts = ["**Architecture Analysis**\n"]

        # Layer summary
        analysis_parts.append(f"**Detected Layers**:  {len(layers)}\n")
        for layer_name, files in sorted(
            layers.items(), key=lambda x: len(x[1]), reverse=True
        ):
            analysis_parts.append(f"- **{layer_name}**: {len(files)} files")

        # Architecture pattern
        analysis_parts.append(
            f"\n**Architecture Pattern**: {self._infer_pattern(layers)}"
        )

        # Violations
        if violations:
            analysis_parts.append(
                f"\n**⚠️  Boundary Violations Detected**: {len(violations)}"
            )

            high_severity = [v for v in violations if v["severity"] == "high"]
            medium_severity = [v for v in violations if v["severity"] == "medium"]

            if high_severity:
                analysis_parts.append(f"\n🔴 **High Severity**: {len(high_severity)}")
                for v in high_severity[:3]:  # Top 3
                    analysis_parts.append(
                        f"  - `{v['source']}` → `{v['target']}`: {v['reason']}"
                    )

            if medium_severity:
                analysis_parts.append(
                    f"\n🟡 **Medium Severity**: {len(medium_severity)}"
                )
                for v in medium_severity[:3]:  # Top 3
                    analysis_parts.append(
                        f"  - `{v['source']}` → `{v['target']}`: {v['reason']}"
                    )
        else:
            analysis_parts.append("\n✅ **No boundary violations detected**")

        # Recommendations
        analysis_parts.append(
            f"\n**Recommendations**:\n{self._generate_recommendations(layers, violations)}"
        )

        # Build evidence
        evidence = []

        # Add layer evidence
        for layer_name, files in layers.items():
            for file_path in files[:5]:  # Top 5 per layer
                evidence.append(
                    Evidence(
                        file_path=file_path,
                        reason=f"Part of {layer_name}",
                    )
                )

        # Add violation evidence
        for violation in violations:
            evidence.append(
                Evidence(
                    file_path=violation["source"],
                    reason=f"{violation['type']}: {violation['reason']} (imports {violation['target']})",
                )
            )

        # Calculate confidence
        confidence = self._calculate_confidence(layers, violations)

        return AgentOutput(
            analysis="\n".join(analysis_parts),
            evidence=evidence,
            confidence=confidence,
            metadata={
                "layer_count": len(layers),
                "violation_count": len(violations),
                "total_files": sum(len(files) for files in layers.values()),
            },
        )

    def _infer_pattern(self, layers: Dict[str, List[str]]) -> str:
        """Infer architectural pattern from detected layers"""
        layer_names = set(layers.keys())

        has_cli = any("Interface" in name or "CLI" in name for name in layer_names)
        has_agents = any("Agent" in name for name in layer_names)
        has_orchestration = any("Orchestration" in name for name in layer_names)
        has_data = any("MCP" in name or "Data" in name for name in layer_names)

        if has_cli and has_agents and has_orchestration and has_data:
            return "**Layered Architecture with Agent Pattern** (CLI → Orchestration → Agents → Data)"
        elif has_cli and has_agents and has_data:
            return "**Multi-Agent System** (CLI → Agents → Data)"
        elif len(layers) >= 4:
            return "**Layered Architecture** (multiple tiers detected)"
        elif len(layers) >= 2:
            return "**Simple Layered Architecture**"
        else:
            return "**Monolithic / Flat Structure**"

    def _generate_recommendations(
        self, layers: Dict[str, List[str]], violations: List[Dict[str, Any]]
    ) -> str:
        """Generate architecture recommendations"""
        recommendations = []

        if violations:
            high_severity_count = sum(1 for v in violations if v["severity"] == "high")
            if high_severity_count > 0:
                recommendations.append(
                    f"1. **Fix {high_severity_count} high-severity boundary violations** - "
                    "These break architectural layering and should be refactored."
                )

            medium_severity_count = sum(
                1 for v in violations if v["severity"] == "medium"
            )
            if medium_severity_count > 0:
                recommendations.append(
                    f"2. **Review {medium_severity_count} medium-severity issues** - "
                    "Consider refactoring for cleaner separation."
                )
        else:
            recommendations.append(
                "1. **Architecture boundaries are clean** - Good layering discipline."
            )

        # Check for missing layers
        layer_names = set(layers.keys())
        if not any("Orchestration" in name for name in layer_names):
            recommendations.append(
                "2. **Consider adding an orchestration layer** - "
                "Separates business logic from agents."
            )

        if not any("Test" in name for name in layer_names):
            recommendations.append(
                f"{len(recommendations) + 1}. **Add test coverage** - "
                "No test layer detected in architecture."
            )

        if not recommendations:
            recommendations.append(
                "Architecture looks solid.  Continue monitoring boundary violations."
            )

        return "\n".join(recommendations)

    def _calculate_confidence(
        self, layers: Dict[str, List[str]], violations: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence in architecture analysis"""

        # Base confidence on clear layer detection
        if len(layers) >= 3:
            confidence = 0.85
        elif len(layers) >= 2:
            confidence = 0.75
        else:
            confidence = 0.6

        # Reduce confidence if many files are in "Other" or "Unknown"
        total_files = sum(len(files) for files in layers.values())
        unknown_files = len(layers.get("Other", [])) + len(layers.get("Unknown", []))

        if total_files > 0:
            unknown_ratio = unknown_files / total_files
            confidence -= unknown_ratio * 0.2

        return max(min(confidence, 1.0), 0.0)
