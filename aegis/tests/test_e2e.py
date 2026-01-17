"""
End-to-end integration tests for Code Analyst MVP.

Tests the full stack:  CLI → Orchestrator → Agents → MCP Servers → Output

Run with:  python -m tests.test_e2e
"""

import subprocess
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_test(message, color=Colors.CYAN):
    """Print formatted test message"""
    print(f"\n{color}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{color}{Colors.BOLD}{message}{Colors.RESET}")
    print(f"{color}{Colors.BOLD}{'=' * 60}{Colors.RESET}")


def print_result(passed, message):
    """Print test result"""
    if passed:
        print(f"{Colors.GREEN}✅ PASS: {message}{Colors.RESET}")
    else:
        print(f"{Colors.RED}❌ FAIL: {message}{Colors.RESET}")
    return passed


def run_command(cmd, expect_success=True):
    """Run CLI command and return success status"""
    print(f"\n{Colors.BLUE}Running: {cmd}{Colors.RESET}")

    result = subprocess.run(
        cmd.split(),
        capture_output=True,
        text=True,
        timeout=300,  # 5 minute timeout
    )

    # Print output
    if result.stdout:
        print(f"{Colors.RESET}{result.stdout[:500]}{Colors.RESET}")
        if len(result.stdout) > 500:
            print(f"{Colors.YELLOW}... (truncated){Colors.RESET}")

    if result.stderr:
        print(f"{Colors.YELLOW}STDERR: {result.stderr[:200]}{Colors.RESET}")

    success = (result.returncode == 0) == expect_success

    return success, result.stdout, result.stderr


def test_cli_help():
    """Test 1: CLI help command"""
    print_test("TEST 1: CLI Help Command")

    success, stdout, _ = run_command("repo-analyst --help")

    checks = [
        print_result(success, "Command executed successfully"),
        print_result("analyze" in stdout, "Contains 'analyze' command"),
        print_result("overview" in stdout, "Contains 'overview' command"),
        print_result("risk" in stdout, "Contains 'risk' command"),
        print_result("deadcode" in stdout, "Contains 'deadcode' command"),
    ]

    return all(checks)


def test_overview():
    """Test 2: Architecture overview"""
    print_test("TEST 2: Architecture Overview")

    success, stdout, _ = run_command("repo-analyst overview --path .")

    checks = [
        print_result(success, "Command executed successfully"),
        print_result(
            "Architecture" in stdout or "architecture" in stdout,
            "Contains architecture analysis",
        ),
        print_result("Layer" in stdout or "layer" in stdout, "Detects layers"),
        print_result(
            "Confidence" in stdout or "confidence" in stdout,
            "Includes confidence score",
        ),
        print_result("Evidence" in stdout or "evidence" in stdout, "Includes evidence"),
    ]

    return all(checks)


def test_risk_analysis():
    """Test 3: Risk analysis"""
    print_test("TEST 3: Risk Analysis")

    success, stdout, _ = run_command("repo-analyst risk --path .  --top 5")

    checks = [
        print_result(success, "Command executed successfully"),
        print_result("Risk" in stdout or "risk" in stdout, "Contains risk analysis"),
        print_result("Confidence" in stdout, "Includes confidence score"),
        print_result("Evidence" in stdout, "Includes evidence"),
        print_result(". py" in stdout, "References actual files"),
    ]

    return all(checks)


def test_dependency_analysis():
    """Test 4: Dependency analysis"""
    print_test("TEST 4: Dependency Analysis")

    # Use a file we know exists
    test_file = "agents/risk.py"

    success, stdout, _ = run_command(f"repo-analyst deps {test_file} --path .")

    checks = [
        print_result(success, "Command executed successfully"),
        print_result(
            "Dependency" in stdout or "dependency" in stdout,
            "Contains dependency analysis",
        ),
        print_result(test_file in stdout, "References target file"),
        print_result(
            "import" in stdout.lower() or "depend" in stdout.lower(),
            "Shows dependencies",
        ),
        print_result("Confidence" in stdout, "Includes confidence score"),
    ]

    return all(checks)


def test_impact_analysis():
    """Test 5: Impact analysis"""
    print_test("TEST 5: Impact Analysis")

    test_file = "agents/base.py"

    success, stdout, _ = run_command(
        f"repo-analyst impact {test_file} --path .  --depth 2"
    )

    checks = [
        print_result(success, "Command executed successfully"),
        print_result(
            "Impact" in stdout or "impact" in stdout or "blast" in stdout.lower(),
            "Contains impact analysis",
        ),
        print_result(test_file in stdout, "References target file"),
        print_result("Confidence" in stdout, "Includes confidence score"),
    ]

    return all(checks)


def test_dead_code_detection():
    """Test 6: Dead code detection"""
    print_test("TEST 6: Dead Code Detection")

    success, stdout, _ = run_command(
        "repo-analyst deadcode --path .  --threshold 0.7 --top 10"
    )

    checks = [
        print_result(success, "Command executed successfully"),
        print_result(
            "dead" in stdout.lower() or "Dead" in stdout, "Contains dead code analysis"
        ),
        print_result("Confidence" in stdout, "Includes confidence score"),
        print_result(
            "threshold" in stdout.lower() or "score" in stdout.lower(),
            "Mentions scoring",
        ),
    ]

    return all(checks)


def test_full_analyze():
    """Test 7: Full analysis"""
    print_test("TEST 7: Full Repository Analysis")

    success, stdout, _ = run_command("repo-analyst analyze .")

    checks = [
        print_result(success, "Command executed successfully"),
        print_result(
            "Architecture" in stdout or "architecture" in stdout,
            "Includes architecture",
        ),
        print_result("Risk" in stdout or "risk" in stdout, "Includes risk analysis"),
        print_result("Confidence" in stdout, "Includes confidence score"),
        print_result("Evidence" in stdout, "Includes evidence"),
        print_result("Agent" in stdout or "agent" in stdout, "Mentions agents"),
    ]

    return all(checks)


def test_propose_architecture():
    """Test 8: Architecture proposal"""
    print_test("TEST 8: Architecture Proposal (Multi-Agent)")

    output_file = "test_proposal.md"

    success, stdout, _ = run_command(
        f"repo-analyst propose-architecture --path . --goal 'Test goal' --output {output_file}"
    )

    # Check file was created
    file_exists = Path(output_file).exists()
    file_size = Path(output_file).stat().st_size if file_exists else 0

    checks = [
        print_result(success, "Command executed successfully"),
        print_result("Proposal" in stdout or "proposal" in stdout, "Mentions proposal"),
        print_result(file_exists, f"Created output file: {output_file}"),
        print_result(file_size > 1000, f"Output file has content ({file_size} bytes)"),
    ]

    # Read and validate file content
    if file_exists:
        with open(output_file, "r") as f:
            content = f.read()
            checks.extend(
                [
                    print_result(
                        "Architecture" in content, "Report contains architecture"
                    ),
                    print_result("Evidence" in content, "Report contains evidence"),
                    print_result("Confidence" in content, "Report contains confidence"),
                ]
            )

    return all(checks)


def test_diagram_generation():
    """Test 9: Mermaid diagram generation"""
    print_test("TEST 9: Mermaid Diagram Generation")

    output_file = "test_diagram. mmd"

    success, stdout, _ = run_command(
        f"repo-analyst diagram --path . --type architecture --output {output_file}"
    )

    # Check file was created
    file_exists = Path(output_file).exists()

    checks = [
        print_result(success, "Command executed successfully"),
        print_result(file_exists, f"Created diagram file: {output_file}"),
    ]

    # Validate Mermaid syntax
    if file_exists:
        with open(output_file, "r") as f:
            content = f.read()
            checks.extend(
                [
                    print_result(
                        "flowchart" in content or "graph" in content,
                        "Valid Mermaid diagram type",
                    ),
                    print_result(
                        "-->" in content or "---" in content, "Contains Mermaid edges"
                    ),
                    print_result(content.count("\n") > 5, "Has multiple lines"),
                    print_result(
                        not content.startswith("#"),
                        "No markdown headers (pure Mermaid)",
                    ),
                ]
            )

    return all(checks)


def test_ask_natural_language():
    """Test 10: Natural language query"""
    print_test("TEST 10: Natural Language Query")

    success, stdout, _ = run_command(
        'repo-analyst ask "What are the high-risk files?" --path .'
    )

    checks = [
        print_result(success, "Command executed successfully"),
        print_result(len(stdout) > 100, "Provides substantial answer"),
        print_result("Confidence" in stdout, "Includes confidence score"),
        print_result(". py" in stdout, "References actual files"),
    ]

    return all(checks)


def test_file_tree():
    """Test 11: File tree display"""
    print_test("TEST 11: File Tree Display")

    success, stdout, _ = run_command("repo-analyst tree .")

    checks = [
        print_result(success, "Command executed successfully"),
        print_result("agents" in stdout, "Shows agents directory"),
        print_result("cli" in stdout, "Shows cli directory"),
        print_result(". py" in stdout, "Shows Python files"),
    ]

    return all(checks)


def test_evidence_quality():
    """Test 12: Evidence quality validation"""
    print_test("TEST 12: Evidence Quality Validation")

    from aegis.graph.orchestrator import Orchestrator
    from aegis.graph.states import OrchestratorInput

    try:
        orchestrator = Orchestrator(repo_path=".")

        # Run risk analysis
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

        output = orchestrator.execute(input_data)

        checks = [
            print_result(output.analysis != "", "Analysis is not empty"),
            print_result(
                len(output.evidence) > 0, f"Has evidence ({len(output.evidence)} items)"
            ),
            print_result(
                0 <= output.confidence <= 1,
                f"Valid confidence score ({output.confidence})",
            ),
            print_result(
                all(e.file_path for e in output.evidence), "All evidence has file paths"
            ),
            print_result(
                all(e.reason for e in output.evidence), "All evidence has reasons"
            ),
        ]

        # Verify file paths are real
        valid_files = 0
        for evidence in output.evidence[:5]:  # Check first 5
            if evidence.file_path not in ["<none>", "<error>", "<unknown>"]:
                file_path = Path(". ") / evidence.file_path
                if file_path.exists():
                    valid_files += 1

        checks.append(
            print_result(
                valid_files > 0, f"Evidence references real files ({valid_files}/5)"
            )
        )

        return all(checks)

    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False


def test_multi_agent_workflow():
    """Test 13: Multi-agent workflow"""
    print_test("TEST 13: Multi-Agent Workflow")

    from aegis.graph.orchestrator import Orchestrator
    from aegis.graph.states import OrchestratorInput

    try:
        orchestrator = Orchestrator(repo_path=".")

        # Run full analysis (uses multiple agents)
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

        output = orchestrator.execute(input_data)

        checks = [
            print_result(output.metadata is not None, "Has metadata"),
            print_result("agents_run" in output.metadata, "Tracks agents run"),
            print_result(
                len(output.metadata.get("agents_run", [])) >= 2,
                f"Multiple agents executed ({len(output.metadata.get('agents_run', []))})",
            ),
            print_result(
                len(output.evidence) > 5,
                f"Combined evidence ({len(output.evidence)} items)",
            ),
        ]

        return all(checks)

    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False


def cleanup_test_files():
    """Clean up test output files"""
    print(f"\n{Colors.YELLOW}Cleaning up test files...{Colors.RESET}")

    test_files = [
        "test_proposal.md",
        "test_diagram.mmd",
        "test_report.md",
        "architecture_diagram.mmd",
        "dependency_diagram.mmd",
        "risk_diagram.mmd",
    ]

    for file in test_files:
        path = Path(file)
        if path.exists():
            path.unlink()
            print(f"  Deleted: {file}")


def main():
    """Run all tests"""
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}")
    print("=" * 60)
    print(" CODE ANALYST MVP - END-TO-END TEST SUITE")
    print("=" * 60)
    print(Colors.RESET)

    tests = [
        ("CLI Help", test_cli_help),
        ("Architecture Overview", test_overview),
        ("Risk Analysis", test_risk_analysis),
        ("Dependency Analysis", test_dependency_analysis),
        ("Impact Analysis", test_impact_analysis),
        ("Dead Code Detection", test_dead_code_detection),
        ("Full Analysis", test_full_analyze),
        ("Architecture Proposal", test_propose_architecture),
        ("Diagram Generation", test_diagram_generation),
        ("Natural Language Query", test_ask_natural_language),
        ("File Tree", test_file_tree),
        ("Evidence Quality", test_evidence_quality),
        ("Multi-Agent Workflow", test_multi_agent_workflow),
    ]

    results = {}

    for name, test_func in tests:
        try:
            passed = test_func()
            results[name] = passed
        except Exception as e:
            print(f"\n{Colors.RED}❌ EXCEPTION in {name}: {str(e)}{Colors.RESET}")
            results[name] = False

    # Summary
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}")
    print("=" * 60)
    print(" TEST SUMMARY")
    print("=" * 60)
    print(Colors.RESET)

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    for test_name, passed in results.items():
        status = f"{Colors.GREEN}✅ PASS" if passed else f"{Colors.RED}❌ FAIL"
        print(f"{status}{Colors.RESET} - {test_name}")

    print(
        f"\n{Colors.BOLD}Results: {passed_count}/{total_count} tests passed{Colors.RESET}"
    )

    if passed_count == total_count:
        print(f"{Colors.GREEN}{Colors.BOLD}")
        print("\n🎉 ALL TESTS PASSED!  MVP IS COMPLETE!  🎉")
        print(Colors.RESET)
        cleanup_test_files()
        return 0
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}")
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        print(Colors.RESET)
        cleanup_test_files()
        return 1


if __name__ == "__main__":
    sys.exit(main())
