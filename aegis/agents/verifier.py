from typing import Optional, Dict, Any, List
from aegis.agents.base import BaseAgent
from aegis.schemas.base import AgentOutput, Evidence
from aegis.mcp_servers.repo_reader.reader import RepoReader


class VerifierAgent(BaseAgent):
    """
    Verifier Agent:  Validates and challenges other agents' outputs.

    Responsibilities:
    - Verify evidence exists and is valid
    - Check for hallucinated file paths
    - Flag overengineering or unjustified recommendations
    - Resolve conflicts between agents
    - Ensure feasibility of proposals

    This agent is SKEPTICAL by default.
    """

    def __init__(self, repo_reader: RepoReader):
        super().__init__(name="VerifierAgent")
        self.reader = repo_reader
        self._valid_files = None

    def analyze(self, context: Optional[Dict[str, Any]] = None) -> AgentOutput:
        """
        Verify one or more agent outputs.

        Context keys:
        - agent_outputs: List[AgentOutput] to verify (required)
        - strict_mode:  Fail on any issue vs. warn (default:  False)

        Returns:
            AgentOutput with verification results
        """
        if not context or "agent_outputs" not in context:
            raise ValueError("VerifierAgent requires 'agent_outputs' in context")

        agent_outputs = context["agent_outputs"]
        strict_mode = context.get("strict_mode", False)

        if not isinstance(agent_outputs, list):
            agent_outputs = [agent_outputs]

        # Lazy-load valid file list
        if self._valid_files is None:
            self._valid_files = self._get_valid_files()

        # Verify each output
        verification_results = []
        for output in agent_outputs:
            result = self._verify_output(output, strict_mode)
            verification_results.append(result)

        return self._build_analysis(verification_results, strict_mode)

    def _get_valid_files(self) -> set:
        """Get set of all valid file paths in the repository"""
        files = self.reader.walk_repo()
        return {f.path for f in files}

    def _verify_output(self, output: AgentOutput, strict_mode: bool) -> Dict[str, Any]:
        """Verify a single agent output"""
        issues = []
        warnings = []

        # Check 1: Evidence exists
        if not output.evidence or len(output.evidence) == 0:
            issues.append(
                {
                    "type": "missing_evidence",
                    "severity": "critical",
                    "message": "Output has no evidence",
                }
            )

        # Check 2: File paths are valid
        if self._valid_files is not None:
            for i, evidence in enumerate(output.evidence):
                if evidence.file_path in ["<none>", "<error>", "<unknown>"]:
                    # These are acceptable for certain cases
                    continue

                if evidence.file_path not in self._valid_files:
                    issues.append(
                        {
                            "type": "invalid_file",
                            "severity": "critical",
                            "message": f"Evidence {i} references non-existent file: {evidence.file_path}",
                            "file": evidence.file_path,
                        }
                    )

        # Check 3: Evidence has reasoning
        for i, evidence in enumerate(output.evidence):
            if not evidence.reason or not evidence.reason.strip():
                warnings.append(
                    {
                        "type": "weak_evidence",
                        "severity": "medium",
                        "message": f"Evidence {i} lacks explanation",
                        "file": evidence.file_path,
                    }
                )

        # Check 4: Confidence score is reasonable
        if output.confidence > 0.95 and len(output.evidence) < 3:
            warnings.append(
                {
                    "type": "overconfident",
                    "severity": "low",
                    "message": f"High confidence ({output.confidence}) with minimal evidence ({len(output.evidence)} items)",
                }
            )

        # Check 5: Analysis is not empty
        if not output.analysis or len(output.analysis.strip()) < 10:
            issues.append(
                {
                    "type": "empty_analysis",
                    "severity": "critical",
                    "message": "Analysis is too short or empty",
                }
            )

        # Check 6: Look for overengineering signals
        overengineering_keywords = [
            "microservices",
            "kubernetes",
            "blockchain",
            "AI-powered",
            "complete rewrite",
            "revolutionary",
            "paradigm shift",
        ]
        analysis_lower = output.analysis.lower()
        for keyword in overengineering_keywords:
            if keyword in analysis_lower:
                warnings.append(
                    {
                        "type": "potential_overengineering",
                        "severity": "medium",
                        "message": f"Detected buzzword '{keyword}' - verify recommendation is justified",
                    }
                )

        # Check 7: Metadata should exist for complex analyses
        if output.confidence > 0.8 and not output.metadata:
            warnings.append(
                {
                    "type": "missing_metadata",
                    "severity": "low",
                    "message": "High confidence output should include metadata for traceability",
                }
            )

        # Determine if output passes verification
        critical_issues = [i for i in issues if i["severity"] == "critical"]
        passed = len(critical_issues) == 0

        if strict_mode:
            passed = passed and len(issues) == 0 and len(warnings) == 0

        return {
            "output": output,
            "passed": passed,
            "issues": issues,
            "warnings": warnings,
            "critical_count": len(critical_issues),
            "total_issues": len(issues) + len(warnings),
        }

    def _build_analysis(
        self, results: List[Dict[str, Any]], strict_mode: bool
    ) -> AgentOutput:
        """Build verification analysis"""

        total_outputs = len(results)
        passed_count = sum(1 for r in results if r["passed"])
        failed_count = total_outputs - passed_count

        all_issues = []
        all_warnings = []
        for r in results:
            all_issues.extend(r["issues"])
            all_warnings.extend(r["warnings"])

        critical_issues = [i for i in all_issues if i["severity"] == "critical"]

        # Build analysis
        analysis_parts = [
            "**Verification Report**\n",
            f"Verified {total_outputs} agent output(s)\n",
        ]

        if failed_count == 0:
            analysis_parts.append("✅ **All outputs passed verification**\n")
        else:
            analysis_parts.append(
                f"❌ **{failed_count} output(s) failed verification**\n"
            )

        # Critical issues
        if critical_issues:
            analysis_parts.append(f"\n🔴 **Critical Issues** ({len(critical_issues)}):")
            for issue in critical_issues[:10]:
                msg = issue["message"]
                if "file" in issue:
                    msg += f" (file: {issue['file']})"
                analysis_parts.append(f"  - {msg}")

        # Warnings
        if all_warnings:
            analysis_parts.append(f"\n🟡 **Warnings** ({len(all_warnings)}):")
            for warning in all_warnings[:10]:
                msg = warning["message"]
                if "file" in warning:
                    msg += f" (file: {warning['file']})"
                analysis_parts.append(f"  - {msg}")

        # Recommendations
        analysis_parts.append("\n**Recommendations**:")
        if critical_issues:
            analysis_parts.append("1. ❌ **Do not use outputs with critical issues**")
            analysis_parts.append("2. Fix evidence validation before proceeding")
        elif all_warnings:
            analysis_parts.append(
                "1. ⚠️ Review warnings before acting on recommendations"
            )
            analysis_parts.append("2. Verify any overengineering claims")
        else:
            analysis_parts.append("1. ✅ Outputs are verified and safe to use")
            analysis_parts.append("2. Proceed with confidence")

        # Build evidence
        evidence = []

        # Add evidence for each verified output
        for r in results:
            status = "✅ PASSED" if r["passed"] else "❌ FAILED"

            evidence.append(
                Evidence(
                    file_path="<verification>",
                    reason=f"{status}:  {r['critical_count']} critical issues, {r['total_issues']} total issues",
                )
            )

            # Add evidence for critical issues
            for issue in r["issues"]:
                if issue["severity"] == "critical":
                    evidence.append(
                        Evidence(
                            file_path=issue.get("file", "<unknown>"),
                            reason=f"CRITICAL: {issue['message']}",
                        )
                    )

        # Calculate overall confidence
        if failed_count == 0 and len(critical_issues) == 0:
            confidence = 0.95
        elif failed_count == 0:
            confidence = 0.8  # Warnings only
        else:
            confidence = 0.3  # Failed verification

        return AgentOutput(
            analysis="\n".join(analysis_parts),
            evidence=evidence,
            confidence=confidence,
            metadata={
                "total_verified": total_outputs,
                "passed": passed_count,
                "failed": failed_count,
                "critical_issues": len(critical_issues),
                "warnings": len(all_warnings),
                "strict_mode": strict_mode,
            },
        )

    def verify_file_exists(self, file_path: str) -> bool:
        """Check if a file exists in the repository"""
        if self._valid_files is None:
            self._valid_files = self._get_valid_files()
        return file_path in self._valid_files

    def challenge_recommendation(
        self, recommendation: str, evidence: List[Evidence]
    ) -> Dict[str, Any]:
        """
        Challenge a specific recommendation.

        Returns skeptical analysis of whether the recommendation is justified.
        """
        # Check for overengineering signals
        overengineering_score = 0
        buzzwords_found = []

        overengineering_patterns = {
            "microservices": 3,
            "kubernetes": 3,
            "complete rewrite": 5,
            "revolutionary": 2,
            "paradigm shift": 2,
            "blockchain": 4,
            "serverless": 2,
            "reactive": 1,
            "event-driven": 1,
        }

        rec_lower = recommendation.lower()
        for pattern, weight in overengineering_patterns.items():
            if pattern in rec_lower:
                overengineering_score += weight
                buzzwords_found.append(pattern)

        # Check evidence quality
        evidence_score = len(evidence)
        if evidence_score == 0:
            evidence_quality = "none"
        elif evidence_score < 3:
            evidence_quality = "weak"
        elif evidence_score < 10:
            evidence_quality = "moderate"
        else:
            evidence_quality = "strong"

        # Make judgment
        if overengineering_score >= 5:
            judgment = "🚫 REJECTED - High overengineering risk"
        elif overengineering_score >= 3 and evidence_quality in ["none", "weak"]:
            judgment = "⚠️ SKEPTICAL - Insufficient evidence for complexity"
        elif evidence_quality == "none":
            judgment = "❌ REJECTED - No evidence"
        else:
            judgment = "✅ ACCEPTABLE - Reasonable recommendation"

        return {
            "judgment": judgment,
            "overengineering_score": overengineering_score,
            "buzzwords_found": buzzwords_found,
            "evidence_quality": evidence_quality,
            "evidence_count": evidence_score,
        }
