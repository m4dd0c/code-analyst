"""
Quick smoke tests - run these first to catch major issues.

Run with:  python -m tests.test_smoke
"""

import sys


def test_imports():
    """Test that all core modules can be imported"""
    print("🧪 Testing imports...")

    try:
        # MCP Servers
        from aegis.mcp_servers.repo_reader.reader import RepoReader
        from aegis.mcp_servers.dependency_graph.graph import DependencyGraph
        from aegis.mcp_servers.code_index.index import CodeIndex

        # Agents
        from aegis.agents.base import BaseAgent
        from aegis.agents.risk import RiskAgent
        from aegis.agents.architecture import ArchitectureAgent
        from aegis.agents.dependency import DependencyAgent
        from aegis.agents.dead_code import DeadCodeAgent
        from aegis.agents.verifier import VerifierAgent

        # Orchestration
        from aegis.graph.orchestrator import Orchestrator
        from aegis.graph.states import OrchestratorInput, OrchestratorState

        # Synthesis
        from aegis.synthesis.report_builder import ReportBuilder
        from aegis.synthesis.mermaid_generator import MermaidGenerator

        # Schemas
        from aegis.schemas.base import AgentOutput, Evidence

        print("✅ All imports successful")
        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_mcp_servers():
    """Test MCP servers can initialize"""
    print("\n🧪 Testing MCP server initialization...")

    try:
        from aegis.mcp_servers.repo_reader.reader import RepoReader
        from aegis.mcp_servers.dependency_graph.graph import DependencyGraph

        reader = RepoReader(".")
        graph = DependencyGraph(reader)

        print("✅ MCP servers initialized")
        return True

    except Exception as e:
        print(f"❌ MCP initialization failed: {e}")
        return False


def test_agents():
    """Test agents can be instantiated"""
    print("\n🧪 Testing agent instantiation...")

    try:
        from aegis.mcp_servers.repo_reader.reader import RepoReader
        from aegis.mcp_servers.dependency_graph.graph import DependencyGraph
        from aegis.agents.risk import RiskAgent
        from aegis.agents.architecture import ArchitectureAgent
        from aegis.agents.dependency import DependencyAgent
        from aegis.agents.dead_code import DeadCodeAgent
        from aegis.agents.verifier import VerifierAgent

        reader = RepoReader(".")
        graph = DependencyGraph(reader)

        risk_agent = RiskAgent(graph)
        arch_agent = ArchitectureAgent(reader, graph)
        dep_agent = DependencyAgent(graph)
        dead_agent = DeadCodeAgent(graph)
        verify_agent = VerifierAgent(reader)

        print("✅ All agents instantiated")
        return True

    except Exception as e:
        print(f"❌ Agent instantiation failed: {e}")
        return False


def test_orchestrator():
    """Test orchestrator can initialize"""
    print("\n🧪 Testing orchestrator...")

    try:
        from aegis.graph.orchestrator import Orchestrator

        orchestrator = Orchestrator(repo_path=".")

        print("✅ Orchestrator initialized")
        return True

    except Exception as e:
        print(f"❌ Orchestrator initialization failed: {e}")
        return False


def test_synthesis():
    """Test synthesis layer"""
    print("\n🧪 Testing synthesis layer...")

    try:
        from aegis.synthesis.report_builder import ReportBuilder
        from aegis.synthesis.mermaid_generator import MermaidGenerator

        builder = ReportBuilder()
        generator = MermaidGenerator()

        print("✅ Synthesis layer initialized")
        return True

    except Exception as e:
        print(f"❌ Synthesis initialization failed: {e}")
        return False


def main():
    """Run smoke tests"""
    print("=" * 60)
    print(" CODE ANALYST MVP - SMOKE TESTS")
    print("=" * 60)

    tests = [
        test_imports,
        test_mcp_servers,
        test_agents,
        test_orchestrator,
        test_synthesis,
    ]

    results = [test() for test in tests]

    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL SMOKE TESTS PASSED")
        print("=" * 60)
        return 0
    else:
        print("❌ SOME SMOKE TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
