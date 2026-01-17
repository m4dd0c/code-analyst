from typing import List, Optional, Dict, Any
from datetime import datetime
from aegis.schemas.base import AgentOutput


class ReportBuilder:
    """
    Report Builder:   Synthesize multi-agent outputs into Markdown reports.

    Capabilities:
    - Executive summaries
    - Evidence tables
    - Risk matrices
    - Architecture recommendations
    - Confidence scoring
    """

    def __init__(self):
        self.report_sections = []

    def build_report(
        self,
        agent_outputs: List[AgentOutput],
        title: str = "Codebase Analysis Report",
        goal: Optional[str] = None,
        repo_path: str = ".",
    ) -> str:
        """
        Build a complete Markdown report from agent outputs.

        Args:
            agent_outputs: List of AgentOutput from various agents
            title: Report title
            goal: Optional analysis goal/objective
            repo_path: Path to analyzed repository

        Returns:
            Complete Markdown report as string
        """
        sections = []

        # Header
        sections.append(self._build_header(title, repo_path, goal))

        # Executive Summary
        sections.append(self._build_executive_summary(agent_outputs))

        # Individual Agent Sections
        for i, output in enumerate(agent_outputs, 1):
            agent_name = self._extract_agent_name(output)
            sections.append(self._build_agent_section(agent_name, output, i))

        # Evidence Summary
        sections.append(self._build_evidence_section(agent_outputs))

        # Recommendations
        sections.append(self._build_recommendations_section(agent_outputs))

        # Metadata
        sections.append(self._build_metadata_section(agent_outputs))

        return "\n\n".join(sections)

    def _build_header(self, title: str, repo_path: str, goal: Optional[str]) -> str:
        """Build report header"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        header = f"""# {title}

**Repository**:  `{repo_path}`  
**Generated**: {timestamp}  
**Tool**:  Autonomous Code Analyst  
"""

        if goal:
            header += f"**Analysis Goal**: {goal}\n"

        header += "\n---\n"
        return header

    def _build_executive_summary(self, agent_outputs: List[AgentOutput]) -> str:
        """Build executive summary section"""
        total_evidence = sum(len(output.evidence) for output in agent_outputs)
        avg_confidence = sum(output.confidence for output in agent_outputs) / len(
            agent_outputs
        )

        # Extract key findings
        key_findings = []
        for output in agent_outputs:
            agent_name = self._extract_agent_name(output)

            # Extract first sentence or key metric
            analysis_preview = output.analysis.split("\n")[0][:150]
            if len(output.analysis.split("\n")[0]) > 150:
                analysis_preview += "..."

            key_findings.append(f"- **{agent_name}**: {analysis_preview}")

        summary = f"""## 📊 Executive Summary

**Analysis Confidence**: {avg_confidence:.2%}  
**Total Evidence Items**: {total_evidence}  
**Agents Executed**: {len(agent_outputs)}

### Key Findings

{chr(10).join(key_findings)}

"""
        return summary

    def _build_agent_section(
        self, agent_name: str, output: AgentOutput, section_num: int
    ) -> str:
        """Build section for individual agent output"""

        # Determine icon based on agent type
        icon = self._get_agent_icon(agent_name)

        section = f"""## {section_num}. {icon} {agent_name}

**Confidence**:  {output.confidence:.2%}  
**Evidence Count**: {len(output.evidence)}

### Analysis

{output.analysis}

"""

        # Add metadata if present
        if output.metadata:
            section += "### Metrics\n\n"
            section += self._format_metadata_table(output.metadata)
            section += "\n"

        return section

    def _build_evidence_section(self, agent_outputs: List[AgentOutput]) -> str:
        """Build consolidated evidence section"""

        all_evidence = []
        for output in agent_outputs:
            agent_name = self._extract_agent_name(output)
            for evidence in output.evidence:
                all_evidence.append((agent_name, evidence))

        if not all_evidence:
            return "## 📁 Evidence\n\nNo evidence collected.\n"

        # Group evidence by file
        evidence_by_file = {}
        for agent_name, evidence in all_evidence:
            file_path = evidence.file_path
            if file_path not in evidence_by_file:
                evidence_by_file[file_path] = []
            evidence_by_file[file_path].append((agent_name, evidence))

        section = "## 📁 Evidence Summary\n\n"
        section += f"**Total Files Referenced**: {len(evidence_by_file)}\n\n"

        # Build evidence table
        section += "| File | Agent | Reason | Lines |\n"
        section += "|------|-------|--------|-------|\n"

        # Show top 20 most referenced files
        sorted_files = sorted(
            evidence_by_file.items(), key=lambda x: len(x[1]), reverse=True
        )[:20]

        for file_path, evidences in sorted_files:
            for agent_name, evidence in evidences[:2]:  # Max 2 per file
                lines = evidence.line_numbers if evidence.line_numbers else "-"
                if isinstance(lines, list):
                    lines = (
                        f"{lines[0]}-{lines[-1]}" if len(lines) > 1 else str(lines[0])
                    )

                reason_short = (
                    evidence.reason[:60] + "..."
                    if len(evidence.reason) > 60
                    else evidence.reason
                )
                section += (
                    f"| `{file_path}` | {agent_name} | {reason_short} | {lines} |\n"
                )

        if len(evidence_by_file) > 20:
            section += f"\n*... and {len(evidence_by_file) - 20} more files*\n"

        return section

    def _build_recommendations_section(self, agent_outputs: List[AgentOutput]) -> str:
        """Extract and consolidate recommendations"""

        recommendations = []

        for output in agent_outputs:
            agent_name = self._extract_agent_name(output)

            # Look for recommendation sections in analysis
            lines = output.analysis.split("\n")
            in_recommendations = False
            current_recs = []

            for line in lines:
                if "recommendation" in line.lower() and line.strip().startswith("#"):
                    in_recommendations = True
                    continue

                if in_recommendations:
                    if line.strip().startswith("-") or line.strip().startswith("1. "):
                        current_recs.append(line.strip())
                    elif line.strip().startswith("#"):
                        break

            if current_recs:
                recommendations.append((agent_name, current_recs))

        if not recommendations:
            return "## 💡 Recommendations\n\nNo specific recommendations generated.\n"

        section = "## 💡 Consolidated Recommendations\n\n"

        for agent_name, recs in recommendations:
            section += f"### From {agent_name}\n\n"
            for rec in recs:
                section += f"{rec}\n"
            section += "\n"

        return section

    def _build_metadata_section(self, agent_outputs: List[AgentOutput]) -> str:
        """Build metadata/appendix section"""

        section = "## 📋 Analysis Metadata\n\n"

        # Confidence breakdown
        section += "### Confidence Scores\n\n"
        section += "| Agent | Confidence | Evidence Count |\n"
        section += "|-------|------------|----------------|\n"

        for output in agent_outputs:
            agent_name = self._extract_agent_name(output)
            section += (
                f"| {agent_name} | {output.confidence:.2%} | {len(output.evidence)} |\n"
            )

        section += "\n"

        # Overall statistics
        total_evidence = sum(len(output.evidence) for output in agent_outputs)
        avg_confidence = sum(output.confidence for output in agent_outputs) / len(
            agent_outputs
        )

        section += "### Overall Statistics\n\n"
        section += f"- **Average Confidence**: {avg_confidence:. 2%}\n"
        section += f"- **Total Evidence Items**: {total_evidence}\n"
        section += f"- **Agents Executed**: {len(agent_outputs)}\n"

        # Quality indicators
        high_confidence = sum(1 for o in agent_outputs if o.confidence >= 0.8)
        low_evidence = sum(1 for o in agent_outputs if len(o.evidence) < 3)

        section += f"- **High Confidence Agents** (≥80%): {high_confidence}/{len(agent_outputs)}\n"
        if low_evidence > 0:
            section += f"- ⚠️ **Agents with Low Evidence** (<3 items): {low_evidence}\n"

        section += "\n---\n\n"
        section += "*This report was generated by Autonomous Code Analyst - an evidence-backed codebase analysis tool.*\n"

        return section

    def _extract_agent_name(self, output: AgentOutput) -> str:
        """Extract agent name from metadata or infer from content"""
        if output.metadata and "agent_name" in output.metadata:
            return output.metadata["agent_name"]

        # Infer from content
        analysis_lower = output.analysis.lower()
        if "architecture" in analysis_lower or "layer" in analysis_lower:
            return "Architecture Agent"
        elif "risk" in analysis_lower or "blast radius" in analysis_lower:
            return "Risk Agent"
        elif "dependency" in analysis_lower or "import" in analysis_lower:
            return "Dependency Agent"
        elif "dead code" in analysis_lower:
            return "Dead Code Agent"
        elif "verification" in analysis_lower or "verif" in analysis_lower:
            return "Verifier Agent"
        else:
            return "Analysis Agent"

    def _get_agent_icon(self, agent_name: str) -> str:
        """Get emoji icon for agent type"""
        agent_lower = agent_name.lower()

        if "architecture" in agent_lower:
            return "🏗️"
        elif "risk" in agent_lower:
            return "⚠️"
        elif "dependency" in agent_lower:
            return "🔗"
        elif "dead" in agent_lower:
            return "💀"
        elif "verifier" in agent_lower or "verification" in agent_lower:
            return "✅"
        else:
            return "🤖"

    def _format_metadata_table(self, metadata: Dict[str, Any]) -> str:
        """Format metadata as a Markdown table"""
        if not metadata:
            return ""

        table = "| Metric | Value |\n"
        table += "|--------|-------|\n"

        for key, value in metadata.items():
            # Format key (convert snake_case to Title Case)
            formatted_key = key.replace("_", " ").title()

            # Format value
            if isinstance(value, float):
                formatted_value = f"{value:.2f}"
            elif isinstance(value, list):
                formatted_value = f"{len(value)} items"
            else:
                formatted_value = str(value)

            table += f"| {formatted_key} | {formatted_value} |\n"

        return table

    def build_simple_summary(self, agent_outputs: List[AgentOutput]) -> str:
        """Build a simple text summary (for CLI display)"""

        lines = []
        lines.append("=" * 80)
        lines.append("📊 ANALYSIS SUMMARY")
        lines.append("=" * 80)

        for output in agent_outputs:
            agent_name = self._extract_agent_name(output)
            icon = self._get_agent_icon(agent_name)

            lines.append(f"\n{icon} {agent_name}")
            lines.append(f"   Confidence: {output.confidence:. 2%}")
            lines.append(f"   Evidence: {len(output.evidence)} items")

            # First line of analysis
            first_line = output.analysis.split("\n")[0]
            if len(first_line) > 70:
                first_line = first_line[:67] + "..."
            lines.append(f"   {first_line}")

        lines.append("\n" + "=" * 80)

        return "\n".join(lines)
