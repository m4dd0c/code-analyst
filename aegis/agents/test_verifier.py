from aegis.mcp_servers.repo_reader.reader import RepoReader
from aegis.agents.verifier import VerifierAgent
from aegis.schemas.base import AgentOutput, Evidence


def test_verifier_agent():
    """Test Verifier Agent"""
    print("🧪 Testing Verifier Agent.. .\n")

    repo_path = "."
    reader = RepoReader(repo_path)
    agent = VerifierAgent(reader)

    # Test 1: Valid output
    print("=" * 60)
    print("Test 1: Verify Valid Output")
    print("=" * 60)

    valid_output = AgentOutput(
        analysis="This is a valid analysis with good evidence.",
        evidence=[
            Evidence(
                file_path="agents/base.py",
                reason="This file exists and has a valid reason",
            ),
            Evidence(
                file_path="agents/risk.py",
                reason="Another valid piece of evidence",
            ),
        ],
        confidence=0.85,
    )

    result = agent.run(context={"agent_outputs": [valid_output]})
    print(f"\n📊 Verification Result:\n{result.analysis}\n")
    print(f"🎯 Confidence: {result.confidence}")
    assert result.confidence > 0.8, "Valid output should pass"
    print("✅ Test 1 passed")

    # Test 2: Invalid file path
    print("\n" + "=" * 60)
    print("Test 2: Detect Hallucinated File")
    print("=" * 60)

    invalid_output = AgentOutput(
        analysis="Analysis with fake file",
        evidence=[
            Evidence(
                file_path="fake/nonexistent/file.py",
                reason="This file doesn't exist",
            )
        ],
        confidence=0.9,
    )

    result = agent.run(context={"agent_outputs": [invalid_output]})
    print(f"\n📊 Verification Result:\n{result.analysis}\n")
    print(f"🎯 Confidence: {result.confidence}")
    assert result.confidence < 0.5, "Invalid file should fail"
    print("✅ Test 2 passed")

    # Test 3: Missing evidence
    print("\n" + "=" * 60)
    print("Test 3: Detect Missing Evidence")
    print("=" * 60)

    no_evidence_output = AgentOutput(
        analysis="Analysis without evidence",
        evidence=[],
        confidence=0.95,
    )

    result = agent.run(context={"agent_outputs": [no_evidence_output]})
    print(f"\n📊 Verification Result:\n{result.analysis}\n")
    assert result.confidence < 0.5, "Missing evidence should fail"
    print("✅ Test 3 passed")

    # Test 4: Overengineering detection
    print("\n" + "=" * 60)
    print("Test 4: Detect Overengineering")
    print("=" * 60)

    recommendation = (
        "We should do a complete rewrite using microservices and blockchain"
    )
    challenge = agent.challenge_recommendation(recommendation, [])

    print(f"Judgment: {challenge['judgment']}")
    print(f"Overengineering score: {challenge['overengineering_score']}")
    print(f"Buzzwords: {challenge['buzzwords_found']}")
    assert "REJECTED" in challenge["judgment"] or "SKEPTICAL" in challenge["judgment"]
    print("✅ Test 4 passed")

    print("\n" + "=" * 60)
    print("🎉 All Verifier Agent tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_verifier_agent()
