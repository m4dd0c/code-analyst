from typing import Optional
from pathlib import Path

from aegis.graph.states import OrchestratorInput
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
    Enhanced Orchestrator:   Routes CLI commands to agents and synthesis layer.

    Day 2:  Simple routing
    Day 3: Multi-agent workflows, verification, synthesis
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()

        # Initialize MCP servers
        print(f"🔧 Initializing MCP servers for:  {self.repo_path}")
        self.reader = RepoReader(str(self.repo_path))
        self.graph = DependencyGraph(self.reader)
        self.index = None  # Lazy load (expensive)

        # Initialize agents
        self.risk_agent = RiskAgent(self.graph)
        self.architecture_agent = ArchitectureAgent(self.reader, self.graph)
        self.dependency_agent = DependencyAgent(self.graph)
        self.dead_code_agent = DeadCodeAgent(self.graph)
        self.verifier_agent = VerifierAgent(self.reader)

        # Initialize synthesis
        self.report_builder = ReportBuilder()
        self.mermaid_generator = MermaidGenerator()

        print("✅ Orchestrator ready")

    def execute(self, input_data: OrchestratorInput) -> AgentOutput:
        """
        Execute a command by routing to appropriate agent(s).

        Args:
            input_data: OrchestratorInput with command and parameters

        Returns:
            AgentOutput from the executed agent(s)
        """
        command = input_data["command"]

        print(f"\n🎯 Executing command: {command}")

        # Route to appropriate handler
        if command == "risk":
            return self._handle_risk(input_data)
        elif command == "overview":
            return self._handle_overview(input_data)
        elif command == "deps":
            return self._handle_deps(input_data)
        elif command == "impact":
            return self._handle_impact(input_data)
        elif command == "analyze":
            return self._handle_analyze(input_data)
        elif command == "deadcode":
            return self._handle_deadcode(input_data)
        elif command == "propose-architecture":
            return self._handle_propose_architecture(input_data)
        elif command == "ask":
            return self._handle_ask(input_data)
        else:
            raise ValueError(f"Unknown command: {command}")

    def _handle_risk(self, input_data: OrchestratorInput) -> AgentOutput:
        """Handle 'risk' command - identify high-risk files"""
        top_n = input_data.get("top_n", 10)
        file_path = input_data.get("file_path")

        context = {}
        if file_path:
            context["focus_file"] = file_path
        else:
            context["top_n"] = top_n
            context["min_fan_in"] = 1

        print(f"🔍 Running Risk Agent (top_n={top_n})")
        return self.risk_agent.run(context=context)

    def _handle_overview(self, input_data: OrchestratorInput) -> AgentOutput:
        """Handle 'overview' command - architecture overview"""
        print("🏗️ Running Architecture Agent")
        return self.architecture_agent.run()

    def _handle_deps(self, input_data: OrchestratorInput) -> AgentOutput:
        """Handle 'deps' command - dependency analysis for a file"""
        file_path = input_data.get("file_path")

        if not file_path:
            raise ValueError("'deps' command requires file_path")

        print(f"🔗 Running Dependency Agent for: {file_path}")
        return self.dependency_agent.run(
            context={
                "file_path": file_path,
                "query_type": "both",
                "max_depth": 2,
            }
        )

    def _handle_impact(self, input_data: OrchestratorInput) -> AgentOutput:
        """Handle 'impact' command - change impact analysis"""
        file_path = input_data.get("file_path")
        max_depth = input_data.get("max_depth", 3)

        if not file_path:
            raise ValueError("'impact' command requires file_path")

        print(f"💥 Running Impact Analysis for: {file_path}")
        return self.dependency_agent.run(
            context={
                "file_path": file_path,
                "query_type": "impact",
                "max_depth": max_depth,
            }
        )

    def _handle_analyze(self, input_data: OrchestratorInput) -> AgentOutput:
        """Handle 'analyze' command - full repository analysis"""
        print("📊 Running Full Analysis (Architecture + Risk)")

        # Run architecture agent
        arch_output = self.architecture_agent.run()

        # Run risk agent
        risk_output = self.risk_agent.run(context={"top_n": 5, "min_fan_in": 2})

        # Combine outputs (simple concatenation for now)
        combined_analysis = f"{arch_output.analysis}\n\n---\n\n{risk_output.analysis}"
        combined_evidence = arch_output.evidence + risk_output.evidence
        avg_confidence = (arch_output.confidence + risk_output.confidence) / 2

        return AgentOutput(
            analysis=combined_analysis,
            evidence=combined_evidence,
            confidence=avg_confidence,
            metadata={
                "agents_run": ["architecture", "risk"],
                "architecture_metadata": arch_output.metadata,
                "risk_metadata": risk_output.metadata,
            },
        )

    def _handle_deadcode(self, input_data: OrchestratorInput) -> AgentOutput:
        """Handle 'deadcode' command - detect probable dead code"""
        threshold = input_data.get("threshold", 0.7)
        top_n = input_data.get("top_n", 20)

        print(f"💀 Running Dead Code Agent (threshold={threshold})")
        return self.dead_code_agent.run(
            context={
                "threshold": threshold,
                "top_n": top_n,
            }
        )

    def _handle_propose_architecture(
        self, input_data: OrchestratorInput
    ) -> AgentOutput:
        """
        Handle 'propose-architecture' command - multi-agent synthesis.

        Workflow:
        1. Run Architecture Agent
        2. Run Risk Agent
        3. Run Verifier Agent
        4. Synthesize report
        """
        goal = input_data.get("goal", "Improve architecture quality")

        print("🏗️ Multi-Agent Architecture Proposal")
        print(f"Goal: {goal}\n")

        # Step 1: Architecture analysis
        print("Step 1/3: Analyzing architecture...")
        arch_output = self.architecture_agent.run()

        # Step 2: Risk analysis
        print("Step 2/3: Analyzing risks...")
        risk_output = self.risk_agent.run(context={"top_n": 10, "min_fan_in": 2})

        # Step 3: Verification
        print("Step 3/3: Verifying outputs...")
        verification_output = self.verifier_agent.run(
            context={"agent_outputs": [arch_output, risk_output]}
        )

        # Check verification
        if verification_output.confidence < 0.5:
            print("⚠️ Verification failed, returning verification report")
            return verification_output

        # Step 4: Synthesize
        print("Synthesizing report...")

        agent_outputs = [arch_output, risk_output]

        # Build report
        report = self.report_builder.build_report(
            agent_outputs=agent_outputs,
            title="Architecture Improvement Proposal",
            goal=goal,
            repo_path=str(self.repo_path),
        )

        # Combine evidence
        all_evidence = []
        for output in agent_outputs:
            all_evidence.extend(output.evidence)

        # Calculate overall confidence
        overall_confidence = sum(o.confidence for o in agent_outputs) / len(
            agent_outputs
        )

        return AgentOutput(
            analysis=report,
            evidence=all_evidence,
            confidence=overall_confidence,
            metadata={
                "agents_run": ["architecture", "risk", "verifier"],
                "goal": goal,
                "verification_passed": True,
                "format": "markdown_report",
            },
        )

    def _handle_ask(self, input_data: OrchestratorInput) -> AgentOutput:
        """
        Handle 'ask' command - natural language question routing.

        Simple keyword-based routing (no LLM for MVP).
        """
        query = input_data.get("user_query", "")

        if not query:
            raise ValueError("'ask' command requires user_query")

        print(f"❓ Processing question: {query}")

        query_lower = query.lower()

        # Route based on keywords
        if any(
            word in query_lower
            for word in ["architecture", "structure", "layer", "organize"]
        ):
            print("→ Routing to Architecture Agent")
            return self.architecture_agent.run()

        elif any(
            word in query_lower
            for word in ["risk", "dangerous", "blast", "impact", "break"]
        ):
            # Check if specific file mentioned
            file_path = self._extract_file_from_query(query)
            if file_path:
                print(f"→ Routing to Impact Analysis for {file_path}")
                return self.dependency_agent.run(
                    context={
                        "file_path": file_path,
                        "query_type": "impact",
                        "max_depth": 3,
                    }
                )
            else:
                print("→ Routing to Risk Agent")
                return self.risk_agent.run(context={"top_n": 10})

        elif any(word in query_lower for word in ["depend", "import", "use", "call"]):
            file_path = self._extract_file_from_query(query)
            if file_path:
                print(f"→ Routing to Dependency Agent for {file_path}")
                return self.dependency_agent.run(
                    context={"file_path": file_path, "query_type": "both"}
                )
            else:
                return AgentOutput(
                    analysis="Please specify a file for dependency analysis.\n\nExample: 'What depends on agents/risk.py? '",
                    evidence=[],
                    confidence=0.5,
                )

        elif any(word in query_lower for word in ["dead", "unused", "remove"]):
            print("→ Routing to Dead Code Agent")
            return self.dead_code_agent.run(context={"threshold": 0.6})

        else:
            # Default: full analysis
            print("→ Routing to Full Analysis")
            return self._handle_analyze(input_data)

    def _extract_file_from_query(self, query: str) -> Optional[str]:
        """Extract file path from natural language query (simple version)"""
        # Look for common file patterns
        words = query.split()
        for word in words:
            # Check if word looks like a file path
            if "/" in word or word.endswith(".py") or word.endswith(".js"):
                # Clean up punctuation
                cleaned = word.strip(".,? !\"'")
                return cleaned

        return None

    def generate_diagram(self, diagram_type: str, focus: Optional[str] = None) -> str:
        """
        Generate Mermaid diagram.

        Args:
            diagram_type: 'architecture' | 'dependency' | 'risk'
            focus: Optional filter

        Returns:
            Valid Mermaid diagram syntax
        """
        print(f"🎨 Generating {diagram_type} diagram...")

        # Build graph if needed
        if not self.graph._built:
            self.graph.build()

        # Prepare data based on diagram type
        if diagram_type == "architecture":
            # Run architecture agent to get layers
            arch_output = self.architecture_agent.run()

            # Extract layers from metadata
            layers = {}
            violations = []

            # Parse evidence to build layer map
            for evidence in arch_output.evidence:
                reason = evidence.reason.lower()
                if "part of" in reason:
                    layer_name = evidence.reason.split("Part of ")[-1].strip()
                    if layer_name not in layers:
                        layers[layer_name] = []
                    layers[layer_name].append(evidence.file_path)
                elif "violation" in reason:
                    violations.append(
                        {
                            "source": evidence.file_path,
                            "target": "",
                            "type": evidence.reason,
                        }
                    )

            data = {"layers": layers, "violations": violations}

        elif diagram_type == "dependency":
            data = {"graph": self.graph.graph}

        elif diagram_type == "risk":
            # Run risk agent
            risk_output = self.risk_agent.run(context={"top_n": 15})

            risk_files = []
            for evidence in risk_output.evidence:
                # Parse risk data from reason
                if "risk" in evidence.reason.lower():
                    risk_files.append(
                        {
                            "file": evidence.file_path,
                            "score": 0.5,  # Default
                            "fan_in": 0,
                        }
                    )

            data = {"risk_files": risk_files}

        else:
            raise ValueError(f"Unknown diagram type: {diagram_type}")

        return self.mermaid_generator.generate(diagram_type, data, focus=focus)

    def get_code_index(self) -> CodeIndex:
        """Lazy-load code index (expensive operation)"""
        if self.index is None:
            print("🔨 Building code index (first time - may take a while)...")
            self.index = CodeIndex(self.reader)
            self.index.build_index()
        return self.index
