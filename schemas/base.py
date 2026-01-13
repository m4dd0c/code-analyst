from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Evidence(BaseModel):
    """Evidence linking analysis to actual code"""

    file_path: str
    line_numbers: Optional[List[int]] = None
    reason: str
    snippet: Optional[str] = None  # Actual code snippet


class AgentOutput(BaseModel):
    """Standard output format for all agents"""

    analysis: str
    evidence: List[Evidence]
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")
    metadata: Optional[Dict[str, Any]] = None


class FileData(BaseModel):
    """Metadata for a single file"""

    path: str
    content: str
    lines: List[str]
    line_count: int
    size: int
    extension: str


class DependencyData(BaseModel):
    """Dependency information for a file"""

    file_path: str
    imports: List[str]
    imported_by: List[str]
    fan_in: int  # Number of files that import this
    fan_out: int  # Number of files this imports


# Test at bottom of file
if __name__ == "__main__":
    evidence = Evidence(
        file_path="src/auth.py",
        line_numbers=[10, 15],
        reason="This function is called by 5 other modules",
    )
    output = AgentOutput(
        analysis="High risk file", evidence=[evidence], confidence=0.85
    )
    print(output.model_dump_json(indent=2))
