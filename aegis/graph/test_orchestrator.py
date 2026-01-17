"""
Test LangGraph workflow integration
"""

from aegis.graph.orchestrator import Orchestrator
from aegis.graph.states import OrchestratorInput


def test_langgraph_single_agent():
    """Test single-agent workflow"""
    print("🧪 Testing LangGraph - Single Agent\n")

    orchestrator = Orchestrator(repo_path=".")

    input_data: OrchestratorInput = {
        "command": "risk",
        "repo_path": ".",
        "top_n": 5,
        "file_path": None,
        "threshold": None,
        "max_depth": None,
        "goal": None,
        "diagram_type": None,
        "user_query": None,
    }

    result = orchestrator.execute(input_data)

    print("\n✅ Single-agent workflow complete")
    print(f"   Confidence: {result.confidence}")
    print(f"   Evidence: {len(result.evidence)} items")
    print(f"   Metadata: {result.metadata}")

    assert result.confidence > 0
    assert len(result.evidence) > 0
    if result.metadata:
        assert result.metadata["workflow"] == "langgraph"


def test_langgraph_multi_agent():
    """Test multi-agent workflow with verification"""
    print("\n🧪 Testing LangGraph - Multi-Agent\n")

    orchestrator = Orchestrator(repo_path=".")

    input_data: OrchestratorInput = {
        "command": "analyze",
        "repo_path": ".",
        "file_path": None,
        "top_n": None,
        "threshold": None,
        "max_depth": None,
        "goal": None,
        "diagram_type": None,
        "user_query": None,
    }

    result = orchestrator.execute(input_data)

    print("\n✅ Multi-agent workflow complete")
    if result.metadata:
        print(f"   Agents executed: {result.metadata.get('agents_executed')}")
    print(f"   Confidence: {result.confidence}")
    print(f"   Evidence: {len(result.evidence)} items")

    assert result.confidence > 0
    assert len(result.evidence) > 0
    if result.metadata:
        assert "architecture" in result.metadata["agents_executed"]
        assert "risk" in result.metadata["agents_executed"]


def test_langgraph_with_verification():
    """Test workflow includes verification step"""
    print("\n🧪 Testing LangGraph - With Verification\n")

    orchestrator = Orchestrator(repo_path=".")

    input_data: OrchestratorInput = {
        "command": "propose-architecture",
        "repo_path": ".",
        "goal": "Test goal",
        "file_path": None,
        "top_n": None,
        "threshold": None,
        "max_depth": None,
        "diagram_type": None,
        "user_query": None,
    }

    result = orchestrator.execute(input_data)
    print("\n✅ Verification workflow complete")
    if result.metadata:
        print(f"   Agents executed: {result.metadata.get('agents_executed')}")
        # Verifier should have run
        assert "verifier" in result.metadata.get("agents_executed", [])


if __name__ == "__main__":
    test_langgraph_single_agent()
    test_langgraph_multi_agent()
    test_langgraph_with_verification()

    print("\n" + "=" * 60)
    print("🎉 All LangGraph tests passed!")
    print("=" * 60)
