from aegis.mcp_servers.repo_reader.reader import RepoReader
from aegis.mcp_servers.dependency_graph.graph import DependencyGraph
from aegis.agents.risk import RiskAgent


def test_risk_agent():
    """Test Risk Agent on current repository"""
    print("🧪 Testing Risk Agent.. .\n")

    # Use current repo
    repo_path = "."
    reader = RepoReader(repo_path)
    graph = DependencyGraph(reader)

    # Initialize agent
    agent = RiskAgent(graph)

    # Test 1: Top risk files
    print("=" * 60)
    print("Test 1: Top 5 High-Risk Files")
    print("=" * 60)
    output = agent.run(context={"top_n": 5, "min_fan_in": 1})

    print(f"\n📊 Analysis:\n{output.analysis}\n")
    print(f"🎯 Confidence: {output.confidence}")
    print(f"📁 Evidence count: {len(output.evidence)}")
    print(f"\n✅ Test 1 passed: {output.confidence > 0}")

    # Test 2: Specific file
    print("\n" + "=" * 60)
    print("Test 2: Analyze Specific File")
    print("=" * 60)

    # Find a Python file to analyze
    test_file = None
    for file_path in graph.graph.keys():
        if file_path.endswith(". py"):
            test_file = file_path
            break

    if test_file:
        output2 = agent.run(context={"focus_file": test_file})
        print(f"\n📊 Analysis:\n{output2.analysis}\n")
        print(f"🎯 Confidence: {output2.confidence}")
        print(f"📁 Evidence count:  {len(output2.evidence)}")
        print(f"\n✅ Test 2 passed: {output2.confidence > 0}")
    else:
        print("⚠️ No Python files found to test")

    # Test 3: Validation
    print("\n" + "=" * 60)
    print("Test 3: Output Validation")
    print("=" * 60)

    # Check that output has required fields
    assert output.analysis, "Analysis is empty"
    assert output.evidence, "Evidence is empty"
    assert 0 <= output.confidence <= 1, "Invalid confidence score"
    assert all(e.file_path for e in output.evidence), "Evidence missing file paths"

    print("✅ All validation checks passed")

    print("\n" + "=" * 60)
    print("🎉 All Risk Agent tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_risk_agent()
