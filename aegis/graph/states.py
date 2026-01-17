from typing import TypedDict, List, Optional, Literal
from aegis.schemas.base import AgentOutput


class AgentRequest(TypedDict):
    """Input state for agent execution"""

    agent_name: Literal["risk", "architecture", "dependency", "dead_code", "verifier"]
    file_path: Optional[str]
    query_type: Optional[str]
    top_n: Optional[int]
    threshold: Optional[float]  # For dead code
    focus: Optional[str]
    max_depth: Optional[int]
    include_violations: Optional[bool]
    include_metrics: Optional[bool]


class OrchestratorInput(TypedDict):
    """Initial input to the orchestrator"""

    command: Literal[
        "overview",
        "risk",
        "deps",
        "impact",
        "analyze",
        "deadcode",
        "propose-architecture",
        "diagram",
        "ask",
    ]
    repo_path: str
    file_path: Optional[str]
    top_n: Optional[int]
    threshold: Optional[float]  # For dead code
    max_depth: Optional[int]
    goal: Optional[str]  # For propose-architecture
    diagram_type: Optional[str]  # For diagram

    # Metadata
    user_query: Optional[str]  # For 'ask' command


class OrchestratorState(TypedDict):
    """Main state that flows through LangGraph"""

    # Input
    command: str
    repo_path: str
    file_path: Optional[str]
    user_query: Optional[str]

    # Agent requests (queue of agents to execute)
    agent_requests: List[AgentRequest]

    # Agent outputs (collected results)
    agent_outputs: List[AgentOutput]

    # Final output
    final_analysis: Optional[str]
    final_evidence: List[dict]
    final_confidence: float

    # Execution metadata
    agents_executed: List[str]
    errors: List[str]
    status: Literal["pending", "executing", "completed", "failed"]


class SynthesisInput(TypedDict):
    """Input for synthesis/report generation"""

    agent_outputs: List[AgentOutput]
    format: Literal["cli", "markdown", "mermaid"]
    focus: Optional[str]
    title: Optional[str]
    goal: Optional[str]


class SynthesisOutput(TypedDict):
    """Output from synthesis"""

    content: str
    format: str
    metadata: dict
