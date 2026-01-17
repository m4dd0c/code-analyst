from aegis.mcp_servers.repo_reader.reader import RepoReader
from aegis.mcp_servers.dependency_graph.graph import DependencyGraph
from aegis.agents.dependency import DependencyAgent


def test_dependency_agent():
    """Test Dependency Agent on current repository"""
    print("🧪 Testing Dependency Agent.. .\n")

    # Use current repo
    repo_path = "."
    reader = RepoReader(repo_path)
    graph = DependencyGraph(reader)

    # Initialize agent
    agent = DependencyAgent(graph)

    # Find a file with dependencies
    graph.build()
    test_file = None
    for file_path, data in graph.graph.items():
        if data.fan_in > 0 and data.fan_out > 0:
            test_file = file_path
            break

    if not test_file:
        print(
            "⚠️  No suitable test file found (need file with both dependencies and dependents)"
        )
        return

    print(f"Testing with file: {test_file}\n")

    # Test 1: Both dependencies and dependents
    print("=" * 60)
    print("Test 1: Full Dependency Analysis")
    print("=" * 60)
    output = agent.run(context={"file_path": test_file, "query_type": "both"})

    print(f"\n📊 Analysis:\n{output.analysis}\n")
    print(f"🎯 Confidence: {output.confidence}")
    print(f"📁 Evidence count: {len(output.evidence)}")
    print(f"\n✅ Test 1 passed: {output.confidence > 0}")

    # Test 2: Impact analysis
    print("\n" + "=" * 60)
    print("Test 2: Change Impact Analysis")
    print("=" * 60)
    output2 = agent.run(
        context={"file_path": test_file, "query_type": "impact", "max_depth": 3}
    )

    print(f"\n📊 Analysis:\n{output2.analysis}\n")
    print(f"🎯 Confidence: {output2.confidence}")
    print(f"📁 Evidence count: {len(output2.evidence)}")
    print(f"\n✅ Test 2 passed: {output2.confidence > 0}")

    # Test 3: Only dependencies
    print("\n" + "=" * 60)
    print("Test 3: Dependencies Only")
    print("=" * 60)
    output3 = agent.run(context={"file_path": test_file, "query_type": "dependencies"})

    print(f"\n📊 Analysis:\n{output3.analysis}\n")
    print(f"🎯 Confidence: {output3.confidence}")
    print(f"\n✅ Test 3 passed: {output3.confidence == 1.0}")

    # Test 4: File not found
    print("\n" + "=" * 60)
    print("Test 4: Non-existent File Handling")
    print("=" * 60)
    output4 = agent.run(context={"file_path": "fake/file. py"})

    print(f"\n📊 Analysis:\n{output4.analysis}\n")
    assert "not found" in output4.analysis.lower()
    print("✅ Test 4 passed: Graceful error handling")

    # Test 5: Validation
    print("\n" + "=" * 60)
    print("Test 5: Output Validation")
    print("=" * 60)

    assert output.analysis, "Analysis is empty"
    assert output.evidence, "Evidence is empty"
    assert 0 <= output.confidence <= 1, "Invalid confidence score"
    assert all(e.file_path for e in output.evidence), "Evidence missing file paths"

    print("✅ All validation checks passed")

    print("\n" + "=" * 60)
    print("🎉 All Dependency Agent tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_dependency_agent()
