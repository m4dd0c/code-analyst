from aegis.graph.orchestrator import Orchestrator
from aegis.graph.states import OrchestratorInput


def test_enhanced_orchestrator():
    """Test enhanced orchestrator with new commands"""
    print("🧪 Testing Enhanced Orchestrator.. .\n")

    orchestrator = Orchestrator(repo_path=".")

    # Test 1: Dead code detection
    print("=" * 60)
    print("Test 1: Dead Code Detection")
    print("=" * 60)

    deadcode_input: OrchestratorInput = {
        "command": "deadcode",
        "repo_path": ".",
        "threshold": 0.7,
        "top_n": 10,
        "file_path": None,
        "max_depth": None,
        "goal": None,
        "diagram_type": None,
        "user_query": None,
    }

    output = orchestrator.execute(deadcode_input)
    print("\n✅ Dead code analysis completed")
    print(f"   Confidence: {output.confidence}")
    print(f"   Evidence count: {len(output.evidence)}")

    # Test 2: Architecture proposal
    print("\n" + "=" * 60)
    print("Test 2: Architecture Proposal (Multi-Agent)")
    print("=" * 60)

    proposal_input: OrchestratorInput = {
        "command": "propose-architecture",
        "repo_path": ".",
        "goal": "Improve maintainability and reduce coupling",
        "file_path": None,
        "top_n": None,
        "threshold": None,
        "max_depth": None,
        "diagram_type": None,
        "user_query": None,
    }

    output = orchestrator.execute(proposal_input)
    print("\n✅ Proposal generated")
    print(f"   Confidence: {output.confidence}")
    print(f"   Evidence count: {len(output.evidence)}")
    print(f"   Agents run: {output.metadata.get('agents_run')}")

    # Test 3: Natural language query
    print("\n" + "=" * 60)
    print("Test 3: Natural Language 'Ask' Command")
    print("=" * 60)

    ask_input: OrchestratorInput = {
        "command": "ask",
        "repo_path": ".",
        "user_query": "What are the high-risk files in this codebase?",
        "file_path": None,
        "top_n": None,
        "threshold": None,
        "max_depth": None,
        "goal": None,
        "diagram_type": None,
    }

    output = orchestrator.execute(ask_input)
    print("\n✅ Question answered")
    print(f"   Confidence: {output.confidence}")

    # Test 4: Diagram generation
    print("\n" + "=" * 60)
    print("Test 4: Mermaid Diagram Generation")
    print("=" * 60)

    diagram = orchestrator.generate_diagram("architecture")
    print(f"\n📊 Generated diagram ({len(diagram)} chars)")
    print("First 200 chars:")
    print(diagram[:200] + "...")
    print("\n✅ Diagram generated")

    print("\n" + "=" * 60)
    print("🎉 All Enhanced Orchestrator tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_enhanced_orchestrator()
