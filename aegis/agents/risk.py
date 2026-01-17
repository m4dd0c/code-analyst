from typing import Optional, Dict, Any, List
from aegis.agents.base import BaseAgent
from aegis.schemas.base import AgentOutput, Evidence
from aegis.mcp_servers.dependency_graph.graph import DependencyGraph


class RiskAgent(BaseAgent):
    """
    Risk Agent:  Identifies high-risk files based on dependency analysis.

    Risk factors:
    - High fan-in (many files depend on this)
    - High fan-out (this depends on many files)
    - Critical path files (both high fan-in and fan-out)

    Confidence scoring:
    - Based purely on dependency metrics (deterministic)
    - High confidence when metrics are clear
    - Lower confidence for edge cases
    """

    def __init__(self, dependency_graph: DependencyGraph):
        super().__init__(name="RiskAgent")
        self.graph = dependency_graph

    def analyze(self, context: Optional[Dict[str, Any]] = None) -> AgentOutput:
        """
        Analyze repository for high-risk files.

        Context keys:
        - top_n: Number of high-risk files to return (default: 10)
        - min_fan_in: Minimum fan-in to consider (default: 2)
        - focus_file: Optional specific file to analyze

        Returns:
            AgentOutput with risk analysis and evidence
        """
        # Build graph if not already built
        if not self.graph._built:
            self.graph.build()

        # Parse context
        top_n = context.get("top_n", 10) if context else 10
        min_fan_in = context.get("min_fan_in", 2) if context else 2
        focus_file = context.get("focus_file") if context else None

        # If analyzing a specific file
        if focus_file:
            return self._analyze_single_file(focus_file)

        # Otherwise, get top risky files
        return self._analyze_top_risk_files(top_n, min_fan_in)

    def _analyze_single_file(self, file_path: str) -> AgentOutput:
        """Analyze risk for a single file"""
        if file_path not in self.graph.graph:
            return AgentOutput(
                analysis=f"File not found in dependency graph: {file_path}",
                evidence=[
                    Evidence(
                        file_path=file_path,
                        reason="File does not exist in analyzed codebase",
                    )
                ],
                confidence=1.0,
            )

        data = self.graph.graph[file_path]
        risk_score = self._calculate_risk_score(data.fan_in, data.fan_out)

        # Build analysis
        analysis_parts = [
            f"**Risk Analysis for {file_path}**\n",
            f"- **Fan-in (Dependents)**: {data.fan_in} files depend on this",
            f"- **Fan-out (Dependencies)**: {data.fan_out} files this depends on",
            f"- **Risk Score**: {risk_score:.2f}/1.0",
            f"\n**Interpretation**:  {self._interpret_risk(risk_score, data.fan_in, data.fan_out)}",
        ]

        # Build evidence
        evidence = [
            Evidence(
                file_path=file_path,
                reason=f"Fan-in: {data.fan_in}, Fan-out: {data.fan_out}, Risk score: {risk_score:.2f}",
            )
        ]

        # Add dependents as evidence
        if data.imported_by:
            for dependent in data.imported_by[:5]:  # Top 5
                evidence.append(
                    Evidence(
                        file_path=dependent,
                        reason=f"Imports {file_path} (creates dependency risk)",
                    )
                )

        return AgentOutput(
            analysis="\n".join(analysis_parts),
            evidence=evidence,
            confidence=0.95,  # High confidence - based on hard metrics
            metadata={
                "risk_score": risk_score,
                "fan_in": data.fan_in,
                "fan_out": data.fan_out,
            },
        )

    def _analyze_top_risk_files(self, top_n: int, min_fan_in: int) -> AgentOutput:
        """Analyze top N highest-risk files"""
        # Get high fan-in files
        high_risk_files = self.graph.get_high_fan_in_files(top_n=top_n * 2)

        # Filter by minimum fan-in
        filtered = [
            (path, fan_in) for path, fan_in in high_risk_files if fan_in >= min_fan_in
        ]

        if not filtered:
            return AgentOutput(
                analysis=f"No high-risk files found (minimum fan-in: {min_fan_in})",
                evidence=[
                    Evidence(
                        file_path="<none>",
                        reason=f"No files have fan-in >= {min_fan_in}",
                    )
                ],
                confidence=1.0,
            )

        # Calculate risk scores
        risk_data = []
        for file_path, fan_in in filtered[:top_n]:
            data = self.graph.graph[file_path]
            risk_score = self._calculate_risk_score(data.fan_in, data.fan_out)
            risk_data.append((file_path, data, risk_score))

        # Sort by risk score
        risk_data.sort(key=lambda x: x[2], reverse=True)

        # Build analysis
        analysis_parts = [
            f"**Top {len(risk_data)} High-Risk Files**\n",
            "Files with the highest blast radius if changed:\n",
        ]

        for i, (file_path, data, risk_score) in enumerate(risk_data, 1):
            analysis_parts.append(
                f"{i}. `{file_path}` — Risk:  {risk_score:.2f}, "
                f"Dependents: {data.fan_in}, Dependencies: {data.fan_out}"
            )

        analysis_parts.append(
            f"\n**Risk Interpretation**:\n{self._interpret_top_risks(risk_data)}"
        )

        # Build evidence
        evidence = []
        for file_path, data, risk_score in risk_data:
            evidence.append(
                Evidence(
                    file_path=file_path,
                    reason=f"High risk: {data.fan_in} dependents, {data.fan_out} dependencies, score {risk_score:.2f}",
                )
            )

            # Add top dependents as sub-evidence
            for dependent in data.imported_by[:3]:
                evidence.append(
                    Evidence(
                        file_path=dependent,
                        reason=f"Depends on {file_path}",
                    )
                )

        return AgentOutput(
            analysis="\n".join(analysis_parts),
            evidence=evidence,
            confidence=0.9,
            metadata={
                "top_n": top_n,
                "min_fan_in": min_fan_in,
                "files_found": len(risk_data),
            },
        )

    def _calculate_risk_score(self, fan_in: int, fan_out: int) -> float:
        """
        Calculate risk score (0-1) based on fan-in and fan-out.

        Formula:
        - Fan-in is weighted more (breaking this breaks many files)
        - Fan-out adds secondary risk (complex dependencies)
        - Normalized to 0-1 scale
        """
        # Weight fan-in more heavily (70%) than fan-out (30%)
        fan_in_weight = 0.7
        fan_out_weight = 0.3

        # Normalize using sigmoid-like function
        # Assumes fan-in of 20+ is very high risk, 50+ is extreme
        normalized_fan_in = min(fan_in / 20.0, 1.0)
        normalized_fan_out = min(fan_out / 15.0, 1.0)

        risk_score = (fan_in_weight * normalized_fan_in) + (
            fan_out_weight * normalized_fan_out
        )

        return min(risk_score, 1.0)

    def _interpret_risk(self, risk_score: float, fan_in: int, fan_out: int) -> str:
        """Generate human-readable risk interpretation"""
        if risk_score >= 0.7:
            level = "🔴 **CRITICAL RISK**"
            explanation = (
                f"This file is a critical dependency with {fan_in} dependents.  "
                "Changes here will have widespread impact.  "
                "Consider refactoring to reduce coupling."
            )
        elif risk_score >= 0.5:
            level = "🟡 **HIGH RISK**"
            explanation = (
                f"This file has {fan_in} dependents.  "
                "Changes require careful testing of dependent modules."
            )
        elif risk_score >= 0.3:
            level = "🟢 **MODERATE RISK**"
            explanation = "This file has some dependents but impact is manageable."
        else:
            level = "⚪ **LOW RISK**"
            explanation = "This file has few dependents.  Changes are relatively safe."

        if fan_out >= 10:
            explanation += f" Note: This file also depends on {fan_out} other files, adding complexity."

        return f"{level}\n{explanation}"

    def _interpret_top_risks(self, risk_data: List[tuple]) -> str:
        """Interpret overall risk profile of top files"""
        if not risk_data:
            return "No significant risks detected."

        avg_risk = sum(score for _, _, score in risk_data) / len(risk_data)
        max_fan_in = max(data.fan_in for _, data, _ in risk_data)

        interpretations = []

        if avg_risk >= 0.6:
            interpretations.append(
                "⚠️ **High overall risk**:  Multiple critical dependencies detected.  "
                "Prioritize decoupling and testing."
            )
        elif avg_risk >= 0.4:
            interpretations.append(
                "⚡ **Moderate risk profile**: Some files have significant impact. "
                "Plan changes carefully."
            )
        else:
            interpretations.append(
                "✅ **Manageable risk**: Dependencies are relatively well-distributed."
            )

        if max_fan_in >= 20:
            interpretations.append(
                f"🔥 **Critical hub detected**: One file has {max_fan_in} dependents. "
                "This is a major architectural bottleneck."
            )

        return "\n".join(interpretations)
