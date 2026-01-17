from aegis.synthesis.report_builder import ReportBuilder
from aegis.schemas.base import AgentOutput, Evidence


def test_report_builder():
    """Test Report Builder"""
    print("🧪 Testing Report Builder.. .\n")

    # Create sample agent outputs
    arch_output = AgentOutput(
        analysis="""**Architecture Analysis**

**Detected Layers**:  5

- **Interface Layer (CLI)**: 3 files
- **Agent Layer**: 6 files
- **MCP Server Layer (Data)**: 9 files

**Architecture Pattern**: Layered Architecture with Agent Pattern

**Recommendations**:
1. Architecture boundaries are clean
2. Continue monitoring boundary violations""",
        evidence=[
            Evidence(file_path="cli/main.py", reason="Part of Interface Layer"),
            Evidence(file_path="agents/risk. py", reason="Part of Agent Layer"),
            Evidence(
                file_path="mcp_servers/repo_reader/reader.py",
                reason="Part of MCP Server Layer",
            ),
        ],
        confidence=0.85,
        metadata={"layer_count": 5, "violation_count": 0},
    )

    risk_output = AgentOutput(
        analysis="""**Top 5 High-Risk Files**

1. `mcp_servers/repo_reader/reader.py` — Risk:  0.26, Dependents: 7
2. `schemas/base.py` — Risk: 0.17, Dependents: 5

**Risk Interpretation**: 
✅ Manageable risk:  Dependencies are relatively well-distributed. 

**Recommendations**:
1. Monitor high fan-in files for changes
2. Add comprehensive tests for critical dependencies""",
        evidence=[
            Evidence(
                file_path="mcp_servers/repo_reader/reader. py",
                line_numbers=[1, 50],
                reason="High risk:  7 dependents, risk score 0.26",
            ),
            Evidence(
                file_path="schemas/base.py",
                reason="High risk: 5 dependents, risk score 0.17",
            ),
        ],
        confidence=0.9,
        metadata={"top_n": 5, "files_found": 5},
    )

    # Build report
    print("=" * 60)
    print("Test 1: Build Full Markdown Report")
    print("=" * 60)

    builder = ReportBuilder()
    report = builder.build_report(
        agent_outputs=[arch_output, risk_output],
        title="Test Codebase Analysis",
        goal="Evaluate architecture and identify risks",
        repo_path="./test-repo",
    )

    print("\n📄 Generated Report:\n")
    print(report)
    print("\n✅ Test 1 passed")

    # Test simple summary
    print("\n" + "=" * 60)
    print("Test 2: Build Simple Summary")
    print("=" * 60)

    summary = builder.build_simple_summary([arch_output, risk_output])
    print("\n" + summary)
    print("\n✅ Test 2 passed")

    # Save to file
    print("\n" + "=" * 60)
    print("Test 3: Save Report to File")
    print("=" * 60)

    output_file = "test_report.md"
    with open(output_file, "w") as f:
        f.write(report)

    print(f"✅ Report saved to: {output_file}")
    print("✅ Test 3 passed")

    print("\n" + "=" * 60)
    print("🎉 All Report Builder tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_report_builder()
