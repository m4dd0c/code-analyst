from typing import Optional
from pathlib import Path

from aegis.graph.states import OrchestratorInput
from aegis.graph.flow import AnalysisWorkflow, AnalysisState
from aegis.schemas.base import AgentOutput

from aegis.mcp_servers.repo_reader.reader import RepoReader
from aegis.mcp_servers.dependency_graph.graph import DependencyGraph
from aegis.mcp_servers.code_index.index import CodeIndex

from aegis.agents.risk import RiskAgent
from aegis.agents.architecture import ArchitectureAgent
from aegis.agents.dependency import DependencyAgent
from aegis.agents.dead_code import DeadCodeAgent
from aegis.agents.verifier import VerifierAgent

from aegis.synthesis.report_builder import ReportBuilder
from aegis.synthesis.mermaid_generator import MermaidGenerator


class Orchestrator:
    """
    LangGraph-powered Orchestrator
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()

        # Initialize MCP servers
        print(f"🔧 Initializing MCP servers for:  {self.repo_path}")
        self.reader = RepoReader(str(self.repo_path))
        self.graph = DependencyGraph(self.reader)
        self.index = None

        # Initialize agents
        agents_dict = {
            "architecture": ArchitectureAgent(self.reader, self.graph),
            "risk": RiskAgent(self.graph),
            "dependency": DependencyAgent(self.graph),
            "deadcode": DeadCodeAgent(self.graph),
            "verifier": VerifierAgent(self.reader),
        }

        # Initialize LangGraph workflow
        self.workflow = AnalysisWorkflow(agents_dict)

        # Initialize synthesis
        self.report_builder = ReportBuilder()
        self.mermaid_generator = MermaidGenerator()

        print("✅ Orchestrator ready (powered by LangGraph)")

    def execute(self, input_data: OrchestratorInput) -> AgentOutput:
        """Execute command using LangGraph workflow"""

        # Convert to LangGraph state
        initial_state: AnalysisState = {
            "command": input_data["command"],
            "repo_path": input_data["repo_path"],
            "file_path": input_data.get("file_path"),
            "user_query": input_data.get("user_query"),
            "architecture_output": None,
            "risk_output": None,
            "dependency_output": None,
            "deadcode_output": None,
            "verification_output": None,
            "agents_executed": [],
            "errors": [],
            "final_output": None,
        }

        # Execute LangGraph workflow
        result = self.workflow.execute(initial_state)

        return result

    # Keep other methods (diagram generation, etc.) as-is
    def generate_diagram(self, diagram_type: str, focus: Optional[str] = None):
        """Generate Mermaid diagram"""
        print(f"🎨 Generating {diagram_type} diagram...")

        if not self.graph._built:
            self.graph.build()

        # ...  (same as before)

    def get_code_index(self) -> CodeIndex:
        """Lazy-load code index"""
        if self.index is None:
            print("🔨 Building code index...")
            self.index = CodeIndex(self.reader)
            self.index.build_index()
        return self.index
