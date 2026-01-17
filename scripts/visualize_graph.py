"""
Visualize the LangGraph workflow
"""

from aegis.graph.orchestrator import Orchestrator

# Initialize orchestrator
orchestrator = Orchestrator(repo_path=".")

# Get the compiled graph
workflow = orchestrator.workflow.graph

# Print Mermaid diagram
print("LangGraph Workflow Visualization:")
print(workflow.get_graph().draw_mermaid())
