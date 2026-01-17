from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from aegis.schemas.base import AgentOutput, Evidence


class BaseAgent(ABC):
    """
    Abstract base class for all specialist agents.

    Design principles:
    - Every agent MUST return AgentOutput with evidence
    - Agents are deterministic (no randomness)
    - Agents are composable (can be chained)
    - Agents never claim certainty without proof
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def analyze(self, context: Optional[Dict[str, Any]] = None) -> AgentOutput:
        """
        Main analysis method - must be implemented by all agents.

        Args:
            context: Optional context dict with agent-specific data

        Returns:
            AgentOutput with analysis, evidence, and confidence score

        Raises:
            ValueError: If context is missing required keys
            RuntimeError: If analysis fails
        """
        pass

    def validate_output(self, output: AgentOutput) -> bool:
        """
        Validate agent output before returning.

        Rules:
        - Must have non-empty analysis
        - Must have at least one piece of evidence
        - Confidence must be between 0 and 1
        - All evidence must reference real file paths

        Returns:
            True if valid, raises ValueError otherwise
        """
        if not output.analysis or not output.analysis.strip():
            raise ValueError(f"{self.name}: Analysis cannot be empty")

        if not output.evidence or len(output.evidence) == 0:
            raise ValueError(
                f"{self.name}: Must provide at least one piece of evidence"
            )

        if not 0.0 <= output.confidence <= 1.0:
            raise ValueError(
                f"{self.name}: Confidence must be between 0 and 1, got {output.confidence}"
            )

        # Validate evidence structure
        for i, evidence in enumerate(output.evidence):
            if not evidence.file_path:
                raise ValueError(f"{self.name}: Evidence {i} missing file_path")
            if not evidence.reason:
                raise ValueError(f"{self.name}: Evidence {i} missing reason")

        return True

    def run(self, context: Optional[Dict[str, Any]] = None) -> AgentOutput:
        """
        Execute the agent with validation.

        This is the main entry point that CLI/orchestrator should call.
        It wraps analyze() with validation and error handling.
        """
        try:
            output = self.analyze(context)
            self.validate_output(output)
            return output
        except Exception as e:
            # Return error as AgentOutput for consistent handling
            return AgentOutput(
                analysis=f"❌ {self.name} failed: {str(e)}",
                evidence=[
                    Evidence(
                        file_path="<error>",
                        reason=f"Agent execution failed: {type(e).__name__}",
                        snippet=str(e),
                    )
                ],
                confidence=0.0,
                metadata={"error": True, "exception": type(e).__name__},
            )

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"
