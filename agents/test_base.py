from agents.base import BaseAgent
from schemas.base import AgentOutput, Evidence


class DummyAgent(BaseAgent):
    """Test agent for validation"""

    def analyze(self, context=None):
        return AgentOutput(
            analysis="This is a test analysis",
            evidence=[
                Evidence(
                    file_path="test/file.py",
                    line_numbers=[1, 2, 3],
                    reason="Test evidence",
                    snippet="def test(): pass",
                )
            ],
            confidence=0.85,
        )


def test_valid_output():
    """Test that valid output passes validation"""
    agent = DummyAgent(name="TestAgent")
    output = agent.run()
    assert output.confidence == 0.85
    assert len(output.evidence) == 1
    assert "test analysis" in output.analysis.lower()
    print("✅ Valid output test passed")


def test_missing_evidence():
    """Test that missing evidence is caught"""

    class BadAgent(BaseAgent):
        def analyze(self, context=None):
            return AgentOutput(
                analysis="Analysis without evidence", evidence=[], confidence=0.5
            )

    agent = BadAgent(name="BadAgent")
    output = agent.run()

    # Should return error output
    assert output.confidence == 0.0
    assert "failed" in output.analysis.lower()
    if output.metadata is not None:
        assert output.metadata.get("error") is True
    else:
        print("No metadata found in output")
    print("✅ Missing evidence test passed")


def test_invalid_confidence():
    """Test that invalid confidence is caught"""

    class BadConfidenceAgent(BaseAgent):
        def analyze(self, context=None):
            return AgentOutput(
                analysis="Test",
                evidence=[Evidence(file_path="test.py", reason="test")],
                confidence=1.5,  # Invalid!
            )

    agent = BadConfidenceAgent(name="BadConfidence")
    output = agent.run()

    # Should return error output
    assert output.confidence == 0.0
    assert "failed" in output.analysis.lower()
    print("✅ Invalid confidence test passed")


def test_empty_analysis():
    """Test that empty analysis is caught"""

    class EmptyAnalysisAgent(BaseAgent):
        def analyze(self, context=None):
            return AgentOutput(
                analysis="",  # Empty!
                evidence=[Evidence(file_path="test.py", reason="test")],
                confidence=0.5,
            )

    agent = EmptyAnalysisAgent(name="EmptyAnalysis")
    output = agent.run()

    assert output.confidence == 0.0
    assert "failed" in output.analysis.lower()
    print("✅ Empty analysis test passed")


if __name__ == "__main__":
    test_valid_output()
    test_missing_evidence()
    test_invalid_confidence()
    test_empty_analysis()
    print("\n🎉 All base agent tests passed!")
