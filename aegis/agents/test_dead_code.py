from aegis.mcp_servers.repo_reader.reader import RepoReader
from aegis.mcp_servers.dependency_graph.graph import DependencyGraph
from aegis.agents.dead_code import DeadCodeAgent


def test_dead_code_agent():
    """Test Dead Code Agent"""
    print("🧪 Testing Dead Code Agent.. .\n")

    repo_path = "."
    reader = RepoReader(repo_path)
    graph = DependencyGraph(reader)

    agent = DeadCodeAgent(graph)

    # Test 1: Default threshold
    print("=" * 60)
    print("Test 1: Dead Code Detection (threshold: 0.6)")
    print("=" * 60)
    output = agent.run(context={"threshold": 0.6, "top_n": 10})

    print(f"\n📊 Analysis:\n{output.analysis}\n")
    print(f"🎯 Confidence: {output.confidence}")
    print(f"📁 Evidence count: {len(output.evidence)}")
    print("\n✅ Test 1 passed")

    # Test 2: Higher threshold
    print("\n" + "=" * 60)
    print("Test 2: High Confidence Only (threshold: 0.8)")
    print("=" * 60)
    output2 = agent.run(context={"threshold": 0.8, "top_n": 5})

    print(f"\n📊 Analysis:\n{output2.analysis}\n")
    print(f"🎯 Confidence: {output2.confidence}")
    print("\n✅ Test 2 passed")

    print("\n" + "=" * 60)
    print("🎉 All Dead Code Agent tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_dead_code_agent()
