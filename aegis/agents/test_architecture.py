from aegis.mcp_servers.repo_reader.reader import RepoReader
from aegis.mcp_servers.dependency_graph.graph import DependencyGraph
from aegis.agents.architecture import ArchitectureAgent


def test_architecture_agent():
    """Test Architecture Agent on current repository"""
    print("🧪 Testing Architecture Agent.. .\n")

    # Use current repo
    repo_path = "."
    reader = RepoReader(repo_path)
    graph = DependencyGraph(reader)

    # Initialize agent
    agent = ArchitectureAgent(reader, graph)

    # Test 1: Full architecture analysis
    print("=" * 60)
    print("Test 1: Full Architecture Analysis")
    print("=" * 60)
    output = agent.run()

    print(f"\n📊 Analysis:\n{output.analysis}\n")
    print(f"🎯 Confidence: {output.confidence}")
    print(f"📁 Evidence count: {len(output.evidence)}")

    if output.metadata:
        print("📈 Metadata:")
        print(f"  - Layers: {output.metadata.get('layer_count')}")
        print(f"  - Violations: {output.metadata.get('violation_count')}")
        print(f"  - Total files: {output.metadata.get('total_files')}")

    print(f"\n✅ Test 1 passed: {output.confidence > 0}")

    # Test 2: Focus on specific layer
    print("\n" + "=" * 60)
    print("Test 2: Focus on Agent Layer")
    print("=" * 60)
    output2 = agent.run(context={"focus": "agent"})

    print(f"\n📊 Analysis:\n{output2.analysis}\n")
    print(f"🎯 Confidence: {output2.confidence}")
    print(f"\n✅ Test 2 passed: {output2.confidence > 0}")

    # Test 3: Validation
    print("\n" + "=" * 60)
    print("Test 3: Output Validation")
    print("=" * 60)

    assert output.analysis, "Analysis is empty"
    assert output.evidence, "Evidence is empty"
    assert 0 <= output.confidence <= 1, "Invalid confidence score"
    assert all(e.file_path for e in output.evidence), "Evidence missing file paths"
    assert all(e.reason for e in output.evidence), "Evidence missing reasons"

    print("✅ All validation checks passed")

    print("\n" + "=" * 60)
    print("🎉 All Architecture Agent tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_architecture_agent()
