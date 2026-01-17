"""
LangGraph workflow for multi-agent orchestration.
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END

from aegis.schemas.base import AgentOutput


class AnalysisState(TypedDict):
    """State that flows through the LangGraph"""

    # Input
    command: str
    repo_path: str
    file_path: str | None
    user_query: str | None

    # Agent outputs
    architecture_output: AgentOutput | None
    risk_output: AgentOutput | None
    dependency_output: AgentOutput | None
    deadcode_output: AgentOutput | None
    verification_output: AgentOutput | None

    # Metadata
    agents_executed: list[str]
    errors: list[str]

    # Final output
    final_output: AgentOutput | None


class AnalysisWorkflow:
    """LangGraph-based multi-agent workflow"""

    def __init__(self, agents_dict: dict):
        """
        Args:
            agents_dict: Dict with keys:  'architecture', 'risk', 'dependency', 'deadcode', 'verifier'
        """
        self.agents = agents_dict
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph state machine"""

        # Create graph
        workflow = StateGraph(AnalysisState)

        # Add nodes (agent execution steps)
        workflow.add_node("route", self._route_command)
        workflow.add_node("architecture", self._run_architecture_agent)
        workflow.add_node("risk", self._run_risk_agent)
        workflow.add_node("dependency", self._run_dependency_agent)
        workflow.add_node("deadcode", self._run_deadcode_agent)
        workflow.add_node("verify", self._run_verifier)
        workflow.add_node("synthesize", self._synthesize_outputs)

        # Define edges (workflow transitions)
        workflow.set_entry_point("route")

        # Conditional routing based on command
        workflow.add_conditional_edges(
            "route",
            self._decide_next_step,
            {
                "architecture": "architecture",
                "risk": "risk",
                "dependency": "dependency",
                "deadcode": "deadcode",
                "multi_agent": "architecture",  # Start multi-agent flow
                "end": END,
            },
        )

        # Single-agent flows go to synthesis
        workflow.add_edge("architecture", "synthesize")
        workflow.add_edge("risk", "synthesize")
        workflow.add_edge("dependency", "synthesize")
        workflow.add_edge("deadcode", "synthesize")

        # Multi-agent flow:  architecture → risk → verify → synthesize
        workflow.add_conditional_edges(
            "architecture",
            lambda state: "risk"
            if state["command"] in ["analyze", "propose-architecture"]
            else "synthesize",
        )
        workflow.add_edge("risk", "verify")
        workflow.add_edge("verify", "synthesize")

        # End after synthesis
        workflow.add_edge("synthesize", END)

        return workflow.compile()

    def _route_command(self, state: AnalysisState) -> AnalysisState:
        """Initial routing node"""
        print(f"📍 Routing command: {state['command']}")
        state["agents_executed"] = []
        state["errors"] = []
        return state

    def _decide_next_step(self, state: AnalysisState) -> str:
        """Conditional edge:  decide which agent to run"""
        command = state["command"]

        if command == "overview":
            return "architecture"
        elif command == "risk":
            return "risk"
        elif command in ["deps", "impact"]:
            return "dependency"
        elif command == "deadcode":
            return "deadcode"
        elif command in ["analyze", "propose-architecture"]:
            return "multi_agent"
        else:
            return "end"

    def _run_architecture_agent(self, state: AnalysisState) -> AnalysisState:
        """Run architecture agent"""
        print("🏗️ Running Architecture Agent...")

        try:
            output = self.agents["architecture"].run()
            state["architecture_output"] = output
            state["agents_executed"].append("architecture")
        except Exception as e:
            state["errors"].append(f"Architecture agent failed: {str(e)}")

        return state

    def _run_risk_agent(self, state: AnalysisState) -> AnalysisState:
        """Run risk agent"""
        print("⚠️ Running Risk Agent...")

        try:
            context = {"top_n": 10, "min_fan_in": 1}
            output = self.agents["risk"].run(context=context)
            state["risk_output"] = output
            state["agents_executed"].append("risk")
        except Exception as e:
            state["errors"].append(f"Risk agent failed: {str(e)}")

        return state

    def _run_dependency_agent(self, state: AnalysisState) -> AnalysisState:
        """Run dependency agent"""
        print("🔗 Running Dependency Agent...")

        file_path = state.get("file_path")
        if not file_path:
            state["errors"].append("Dependency agent requires file_path")
            return state

        try:
            query_type = "impact" if state["command"] == "impact" else "both"
            context = {"file_path": file_path, "query_type": query_type}
            output = self.agents["dependency"].run(context=context)
            state["dependency_output"] = output
            state["agents_executed"].append("dependency")
        except Exception as e:
            state["errors"].append(f"Dependency agent failed: {str(e)}")

        return state

    def _run_deadcode_agent(self, state: AnalysisState) -> AnalysisState:
        """Run dead code agent"""
        print("💀 Running Dead Code Agent...")

        try:
            context = {"threshold": 0.7, "top_n": 20}
            output = self.agents["deadcode"].run(context=context)
            state["deadcode_output"] = output
            state["agents_executed"].append("deadcode")
        except Exception as e:
            state["errors"].append(f"Dead code agent failed:  {str(e)}")

        return state

    def _run_verifier(self, state: AnalysisState) -> AnalysisState:
        """Run verifier on collected outputs"""
        print("✅ Running Verifier Agent...")

        outputs = []
        if state.get("architecture_output"):
            outputs.append(state["architecture_output"])
        if state.get("risk_output"):
            outputs.append(state["risk_output"])

        if not outputs:
            state["errors"].append("No outputs to verify")
            return state

        try:
            context = {"agent_outputs": outputs}
            output = self.agents["verifier"].run(context=context)
            state["verification_output"] = output
            state["agents_executed"].append("verifier")
        except Exception as e:
            state["errors"].append(f"Verifier failed: {str(e)}")

        return state

    def _synthesize_outputs(self, state: AnalysisState) -> AnalysisState:
        """Synthesize final output from all agent outputs"""
        print("🔄 Synthesizing outputs...")

        # Collect all outputs
        outputs = []
        for key in [
            "architecture_output",
            "risk_output",
            "dependency_output",
            "deadcode_output",
        ]:
            if state.get(key):
                outputs.append(state[key])

        if not outputs:
            # Return error output
            from aegis.schemas.base import Evidence

            state["final_output"] = AgentOutput(
                analysis="❌ No agent outputs available",
                evidence=[Evidence(file_path="<error>", reason="Workflow failed")],
                confidence=0.0,
                metadata={"errors": state["errors"]},
            )
            return state

        # Single agent:  return as-is
        if len(outputs) == 1:
            state["final_output"] = outputs[0]
            return state

        # Multi-agent: combine outputs
        combined_analysis = "\n\n---\n\n".join(o.analysis for o in outputs)
        combined_evidence = []
        for o in outputs:
            combined_evidence.extend(o.evidence)

        avg_confidence = sum(o.confidence for o in outputs) / len(outputs)

        state["final_output"] = AgentOutput(
            analysis=combined_analysis,
            evidence=combined_evidence,
            confidence=avg_confidence,
            metadata={
                "agents_executed": state["agents_executed"],
                "workflow": "langgraph",
            },
        )

        return state

    def execute(self, initial_state: AnalysisState) -> AgentOutput:
        """Execute the workflow"""
        print("\n🚀 Starting LangGraph workflow...")

        # Run the graph
        final_state = self.graph.invoke(initial_state)

        print(
            f"✅ Workflow complete.  Agents executed: {final_state['agents_executed']}"
        )

        return final_state["final_output"]
