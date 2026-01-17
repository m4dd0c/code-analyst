# Code Analyst CLI - Complete Reference

## Installation

```bash
# Install in development mode
pip install -e .

# Or install from source
pip install .
```

## Quick Start

```bash
# Analyze current directory
repo-analyst overview

# Find high-risk files
repo-analyst risk --top 10

# Check dead code
repo-analyst deadcode --threshold 0.7
```

---

## Commands

### 📊 `analyze`

**Full repository analysis (Architecture + Risk)**

```bash
repo-analyst analyze [PATH]
```

**Options:**

- `PATH`: Repository path (default: current directory)

**Output:**

- Architecture layers
- High-risk files
- Consolidated evidence
- Multi-agent insights

**Example:**

```bash
repo-analyst analyze ~/projects/my-app
```

---

### 🏗️ `overview`

**Architecture overview and layer detection**

```bash
repo-analyst overview [OPTIONS]
```

**Options:**

- `--path PATH`: Repository path (default: `.`)

**Output:**

- Detected layers
- Architecture pattern
- Boundary violations
- File counts per layer

**Example:**

```bash
repo-analyst overview --path .
```

---

### ⚠️ `risk`

**Identify high-risk files based on dependencies**

```bash
repo-analyst risk [OPTIONS]
```

**Options:**

- `--path PATH`: Repository path (default: `.`)
- `--top N`: Number of files to show (default: 10)

**Output:**

- Risk scores (0-1)
- Fan-in/fan-out metrics
- Blast radius estimates

**Example:**

```bash
repo-analyst risk --top 5
```

---

### 🔗 `deps`

**Show dependencies for a specific file**

```bash
repo-analyst deps FILE_PATH [OPTIONS]
```

**Arguments:**

- `FILE_PATH`: File to analyze (required)

**Options:**

- `--path PATH`: Repository path (default: `.`)

**Output:**

- Files this imports
- Files that import this
- Coupling metrics
- Fan-in/fan-out

**Example:**

```bash
repo-analyst deps agents/risk.py
```

---

### 💥 `impact`

**Analyze blast radius if file changes**

```bash
repo-analyst impact FILE_PATH [OPTIONS]
```

**Arguments:**

- `FILE_PATH`: File to analyze (required)

**Options:**

- `--path PATH`: Repository path (default: `.`)
- `--depth N`: Analysis depth (default: 3)

**Output:**

- Direct impact (immediate dependents)
- Transitive impact (depth-N)
- Severity level
- Affected files list

**Example:**

```bash
repo-analyst impact agents/base.py --depth 3
```

---

### 💀 `deadcode`

**Detect probable dead/unused code**

```bash
repo-analyst deadcode [OPTIONS]
```

**Options:**

- `--path PATH`: Repository path (default: `.`)
- `--threshold FLOAT`: Confidence threshold 0.0-1.0 (default: 0.7)
- `--top N`: Maximum files to report (default: 20)

**Output:**

- High/medium confidence candidates
- Dead code scores
- Fan-in/fan-out metrics
- Verification recommendations

**Example:**

```bash
repo-analyst deadcode --threshold 0.8 --top 10
```

**⚠️ Important:** Always verify before deleting. This is probabilistic analysis.

---

### 🏗️ `propose-architecture`

**Generate architecture improvement proposal (Multi-Agent)**

```bash
repo-analyst propose-architecture [OPTIONS]
```

**Options:**

- `--path PATH`: Repository path (default: `.`)
- `--goal TEXT`: Analysis goal (default: "Improve architecture quality")
- `--output FILE`: Save report to file (. md)

**Output:**

- Executive summary
- Architecture analysis
- Risk assessment
- Evidence tables
- Recommendations
- Confidence scores

**Example:**

```bash
repo-analyst propose-architecture \
  --goal "Improve scalability for 10x traffic" \
  --output proposal.md
```

**Agents used:**

- Architecture Agent
- Risk Agent
- Verifier Agent

---

### 🎨 `diagram`

**Generate Mermaid diagram**

```bash
repo-analyst diagram [OPTIONS]
```

**Options:**

- `--path PATH`: Repository path (default: `.`)
- `--type TYPE`: Diagram type: `architecture`, `dependency`, `risk` (default: `architecture`)
- `--focus TEXT`: Filter to specific layer/module
- `--output FILE`: Save to file (.mmd)

**Output:**

- Valid Mermaid syntax
- No prose or wrappers
- Grounded in actual files

**Examples:**

```bash
# Architecture diagram
repo-analyst diagram --type architecture --output arch.mmd

# Dependency graph focused on agents
repo-analyst diagram --type dependency --focus agents

# Risk matrix
repo-analyst diagram --type risk
```

**View diagrams:** Copy output to https://mermaid.live

---

### ❓ `ask`

**Ask a question in natural language**

```bash
repo-analyst ask "QUESTION" [OPTIONS]
```

**Arguments:**

- `QUESTION`: Your question (required)

**Options:**

- `--path PATH`: Repository path (default: `.`)

**Routing:**

- Architecture questions → Architecture Agent
- Risk/impact questions → Risk/Dependency Agent
- Dead code questions → Dead Code Agent
- Default → Full analysis

**Examples:**

```bash
repo-analyst ask "What are the high-risk files?"
repo-analyst ask "If I change auth.py, what breaks?"
repo-analyst ask "Show me the architecture layers"
repo-analyst ask "What code is probably unused?"
```

---

### 🔍 `search`

**Semantic code search**

```bash
repo-analyst search "QUERY" [OPTIONS]
```

**Arguments:**

- `QUERY`: Search query (required)

**Options:**

- `--path PATH`: Repository path (default: `.`)
- `--top N`: Number of results (default: 3)

**Output:**

- Relevant code chunks
- File paths and line numbers
- Function/class names
- Code previews

**Example:**

```bash
repo-analyst search "authentication logic" --top 5
```

---

### 🌳 `tree`

**Show repository file tree**

```bash
repo-analyst tree [PATH]
```

**Arguments:**

- `PATH`: Repository path (default: `.`)

**Output:**

- Hierarchical file tree
- Respects ignore rules
- Shows directory structure

**Example:**

```bash
repo-analyst tree ~/projects/my-app
```

---

## Example Workflows

### Workflow 1: New Codebase Exploration

```bash
# Step 1: Overview
repo-analyst overview

# Step 2: Find risky areas
repo-analyst risk --top 10

# Step 3: Investigate specific file
repo-analyst deps mcp_servers/repo_reader/reader.py

# Step 4: Check blast radius
repo-analyst impact mcp_servers/repo_reader/reader.py
```

### Workflow 2: Pre-Refactoring Analysis

```bash
# Step 1: Identify dead code
repo-analyst deadcode --threshold 0.7

# Step 2: Get architecture proposal
repo-analyst propose-architecture \
  --goal "Reduce coupling" \
  --output refactor-plan.md

# Step 3: Generate diagram
repo-analyst diagram --type architecture --output before. mmd
```

### Workflow 3: Impact Assessment

```bash
# Check what breaks if you change a file
repo-analyst impact src/core/auth.py --depth 3

# Get dependency details
repo-analyst deps src/core/auth.py

# Ask natural language
repo-analyst ask "What depends on the auth module?"
```

---

## Output Guarantees

Every command provides:

- **Analysis**: Human-readable insights
- **Evidence**: File-level proof with line numbers
- **Confidence**: Score from 0.0 (low) to 1.0 (high)
- **Metadata**: Agent info, metrics, traceability

**Philosophy:** "If the system can't explain why it said something, it shouldn't say it."

---

## Configuration

### Environment Variables

Create a `.env` file:

```bash
# Required for semantic search
GOOGLE_API_KEY=your-gemini-api-key

# Optional:  LangSmith tracing
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=code-analyst
```

### Ignore Patterns

Edit `mcp_servers/repo_reader/reader.py` to customize:

```python
IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__",
    "venv", ". venv", "dist", "build"
}

CODE_EXTENSIONS = {
    ".py", ". js", ".ts", ".jsx", ".tsx",
    ".java", ".go", ".rs", ".cpp"
}
```

---

## Troubleshooting

### Command not found

```bash
# Reinstall
pip install -e .

# Or run directly
python -m cli. main --help
```

### Module import errors

```bash
# Install dependencies
pip install -r requirements.txt
```

### API key errors

```bash
# Set environment variable
export GOOGLE_API_KEY=your-key

# Or add to .env file
echo "GOOGLE_API_KEY=your-key" >> .env
```

---

## Advanced Usage

### Chaining Commands

```bash
# Analyze and save multiple outputs
repo-analyst overview > overview.txt
repo-analyst risk --top 10 > risks.txt
repo-analyst propose-architecture --output proposal.md
repo-analyst diagram --type architecture --output arch.mmd
```

### Filtering

```bash
# Focus on specific modules
repo-analyst diagram --type dependency --focus agents

# Adjust thresholds
repo-analyst deadcode --threshold 0.9  # Very conservative
repo-analyst deadcode --threshold 0.5  # More aggressive
```

---

## Getting Help

```bash
# General help
repo-analyst --help

# Command-specific help
repo-analyst risk --help
repo-analyst propose-architecture --help
```

---

## Version

```bash
repo-analyst --version
```

---

_Built with LangChain, LangGraph, MCP, and RAG_
