from typing import Optional, Dict, Any, List, Tuple
from aegis.agents.base import BaseAgent
from aegis.schemas.base import AgentOutput, Evidence
from aegis.mcp_servers.dependency_graph.graph import DependencyGraph
from aegis.mcp_servers.code_index.index import CodeIndex


class DeadCodeAgent(BaseAgent):
    """
    Dead Code Agent:  Identifies probable dead/unused code.

    Detection strategies:
    - Zero fan-in (nothing imports this)
    - Low semantic search matches (rarely referenced)
    - Non-entry-point files with no usage

    CRITICAL: Never claims certainty - always probabilistic
    """

    def __init__(
        self, dependency_graph: DependencyGraph, code_index: Optional[CodeIndex] = None
    ):
        super().__init__(name="DeadCodeAgent")
        self.graph = dependency_graph
        self.index = code_index

    def analyze(self, context: Optional[Dict[str, Any]] = None) -> AgentOutput:
        """
        Identify probable dead code.

        Context keys:
        - threshold: Minimum confidence to report (default: 0.6)
        - top_n: Maximum files to report (default: 20)
        - exclude_patterns:  List of patterns to exclude (e.g., ["__init__", "test_"])

        Returns:
            AgentOutput with dead code candidates
        """
        # Build graph if not already built
        if not self.graph._built:
            self.graph.build()

        # Parse context
        threshold = context.get("threshold", 0.6) if context else 0.6
        top_n = context.get("top_n", 20) if context else 20
        exclude_patterns = (
            context.get("exclude_patterns", ["__init__", "test_", "setup.py"])
            if context
            else ["__init__", "test_", "setup.py"]
        )

        # Find candidates
        candidates = self._find_dead_code_candidates(exclude_patterns)

        # Score each candidate
        scored_candidates = []
        for file_path, data in candidates:
            score = self._calculate_dead_code_score(file_path, data)
            if score >= threshold:
                scored_candidates.append((file_path, data, score))

        # Sort by score
        scored_candidates.sort(key=lambda x: x[2], reverse=True)
        scored_candidates = scored_candidates[:top_n]

        return self._build_analysis(scored_candidates, threshold)

    def _find_dead_code_candidates(
        self, exclude_patterns: List[str]
    ) -> List[Tuple[str, Any]]:
        """Find files with zero or low fan-in"""
        candidates = []

        for file_path, data in self.graph.graph.items():
            # Skip excluded patterns
            if any(pattern in file_path for pattern in exclude_patterns):
                continue

            # Zero fan-in = potential dead code
            if data.fan_in == 0:
                candidates.append((file_path, data))

        return candidates

    def _calculate_dead_code_score(self, file_path: str, data: Any) -> float:
        """
        Calculate probability this is dead code (0-1).

        Scoring factors:
        - Fan-in = 0: high score
        - Fan-out = 0: even higher (nothing uses it, uses nothing)
        - Entry point patterns (cli/, main.py): reduce score
        """
        score = 0.0

        # Base score for zero fan-in
        if data.fan_in == 0:
            score = 0.7
        elif data.fan_in == 1:
            score = 0.4
        else:
            score = 0.2

        # Boost if also has zero fan-out (isolated file)
        if data.fan_out == 0:
            score += 0.2

        # Reduce score for likely entry points
        if any(pattern in file_path for pattern in ["cli/", "main. py", "__main__"]):
            score *= 0.3

        # Reduce score for test files (they're not dead, just not imported)
        if "test" in file_path:
            score *= 0.1

        return min(score, 1.0)

    def _build_analysis(
        self, candidates: List[Tuple[str, Any, float]], threshold: float
    ) -> AgentOutput:
        """Build analysis output"""

        if not candidates:
            return AgentOutput(
                analysis=f"✅ **No dead code detected** (threshold: {threshold})\n\n"
                f"All files appear to be in use or are entry points.",
                evidence=[
                    Evidence(
                        file_path="<none>",
                        reason=f"No files with confidence >= {threshold} for dead code",
                    )
                ],
                confidence=0.8,
            )

        analysis_parts = [
            "**⚠️ Probable Dead Code Detection**\n",
            f"Found **{len(candidates)} file(s)** with low usage (threshold: {threshold})\n",
            "**IMPORTANT**: These are probabilistic findings. Always verify before deletion.\n",
        ]

        # Group by confidence
        high_confidence = [c for c in candidates if c[2] >= 0.8]
        medium_confidence = [c for c in candidates if 0.6 <= c[2] < 0.8]

        if high_confidence:
            analysis_parts.append(
                f"\n🔴 **High Confidence** ({len(high_confidence)} files):"
            )
            for file_path, data, score in high_confidence[:10]:
                analysis_parts.append(
                    f"  - `{file_path}` (score: {score:.2f}, fan-in: {data.fan_in}, fan-out: {data.fan_out})"
                )

        if medium_confidence:
            analysis_parts.append(
                f"\n🟡 **Medium Confidence** ({len(medium_confidence)} files):"
            )
            for file_path, data, score in medium_confidence[:10]:
                analysis_parts.append(
                    f"  - `{file_path}` (score: {score:.2f}, fan-in: {data.fan_in}, fan-out: {data.fan_out})"
                )

        # Recommendations
        analysis_parts.append("\n**Recommendations**:")
        analysis_parts.append("1. Verify each file manually before deletion")
        analysis_parts.append(
            "2. Check for runtime imports (not detected by static analysis)"
        )
        analysis_parts.append("3. Look for entry points (CLI commands, scripts)")
        analysis_parts.append("4. Consider if files are used by external tools")

        # Build evidence
        evidence = []
        for file_path, data, score in candidates:
            reason = f"Dead code score: {score:.2f} (fan-in: {data.fan_in}, fan-out:  {data.fan_out})"
            if score >= 0.8:
                reason += " - High confidence"
            elif score >= 0.6:
                reason += " - Medium confidence"

            evidence.append(
                Evidence(
                    file_path=file_path,
                    reason=reason,
                )
            )

        # Overall confidence is medium - this is always probabilistic
        overall_confidence = 0.7

        return AgentOutput(
            analysis="\n".join(analysis_parts),
            evidence=evidence,
            confidence=overall_confidence,
            metadata={
                "total_candidates": len(candidates),
                "high_confidence": len(high_confidence),
                "medium_confidence": len(medium_confidence),
                "threshold": threshold,
            },
        )
