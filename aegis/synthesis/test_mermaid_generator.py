from aegis.synthesis.mermaid_generator import MermaidGenerator


def test_mermaid_generator():
    """Test Mermaid Generator"""
    print("🧪 Testing Mermaid Generator.. .\n")

    generator = MermaidGenerator()

    # Test 1: Architecture diagram
    print("=" * 60)
    print("Test 1: Architecture Diagram")
    print("=" * 60)

    arch_data = {
        "layers": {
            "Interface Layer (CLI)": ["cli/main.py", "cli/commands.py"],
            "Agent Layer": [
                "agents/risk. py",
                "agents/architecture.py",
                "agents/dependency.py",
            ],
            "MCP Server Layer": [
                "mcp_servers/repo_reader/reader.py",
                "mcp_servers/dependency_graph/graph.py",
            ],
            "Schema Layer": ["schemas/base.py"],
        },
        "violations": [
            {
                "source": "mcp_servers/repo_reader/reader.py",
                "target": "agents/risk.py",
                "type": "layering_violation",
            }
        ],
    }

    diagram = generator.generate("architecture", arch_data)
    print("\n📊 Generated Mermaid:\n")
    print(diagram)
    print("\n✅ Test 1 passed")

    # Test 2: Dependency diagram
    print("\n" + "=" * 60)
    print("Test 2: Dependency Diagram")
    print("=" * 60)

    dep_data = {
        "graph": {
            "agents/risk.py": {
                "imports": ["agents/base.py", "mcp_servers/dependency_graph/graph.py"],
                "imported_by": ["cli/main.py"],
                "fan_in": 1,
                "fan_out": 2,
            },
            "agents/base.py": {
                "imports": ["schemas/base.py"],
                "imported_by": ["agents/risk.py", "agents/architecture.py"],
                "fan_in": 2,
                "fan_out": 1,
            },
            "schemas/base.py": {
                "imports": [],
                "imported_by": ["agents/base.py"],
                "fan_in": 1,
                "fan_out": 0,
            },
        }
    }

    diagram = generator.generate("dependency", dep_data)
    print("\n📊 Generated Mermaid:\n")
    print(diagram)
    print("\n✅ Test 2 passed")

    # Test 3: Risk diagram
    print("\n" + "=" * 60)
    print("Test 3: Risk Diagram")
    print("=" * 60)

    risk_data = {
        "risk_files": [
            {"file": "mcp_servers/repo_reader/reader.py", "score": 0.85, "fan_in": 7},
            {"file": "schemas/base.py", "score": 0.72, "fan_in": 5},
            {"file": "agents/risk.py", "score": 0.55, "fan_in": 2},
        ]
    }

    diagram = generator.generate("risk", risk_data)
    print("\n📊 Generated Mermaid:\n")
    print(diagram)
    print("\n✅ Test 3 passed")

    # Test 4: Save to file
    print("\n" + "=" * 60)
    print("Test 4: Save Diagrams to Files")
    print("=" * 60)

    with open("architecture_diagram.mmd", "w") as f:
        f.write(generator.generate("architecture", arch_data))
    print("✅ Saved:  architecture_diagram.mmd")

    with open("dependency_diagram. mmd", "w") as f:
        f.write(generator.generate("dependency", dep_data))
    print("✅ Saved: dependency_diagram.mmd")

    with open("risk_diagram.mmd", "w") as f:
        f.write(generator.generate("risk", risk_data))
    print("✅ Saved: risk_diagram.mmd")

    print("\n💡 Open these files at https://mermaid.live to visualize")

    print("\n" + "=" * 60)
    print("🎉 All Mermaid Generator tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_mermaid_generator()
