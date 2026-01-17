# 🤖 Autonomous Code Analyst

**A CLI-first, multi-agent AI system for evidence-backed codebase analysis.**

[![Python 3.11+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> _"If the system can't explain why it said something, it shouldn't say it."_

---

## 🎯 What Is This?

An **engineering analysis tool** (not a chatbot) that:

- ✅ Explains **how your codebase is structured**
- ✅ Identifies **high-risk files** and **blast radius**
- ✅ Answers **change-impact questions**
- ✅ Detects **probable dead code**
- ✅ Proposes **architecture improvements**
- ✅ Generates **Markdown reports** and **Mermaid diagrams**

**All outputs are deterministic, evidence-backed, and confidence-scored.**

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/m4dd0c/code-analyst.git
cd code-analyst

# Install dependencies
pip install -r requirements.txt

# Install CLI tool
pip install -e .

# Set up API key (for semantic search)
echo "GOOGLE_API_KEY=your-key-here" > .env
```

### Basic Commands

```bash
# Architecture overview
repo-analyst overview

# Find high-risk files
repo-analyst risk --top 10

# Analyze dependencies
repo-analyst deps agents/risk.py

# Check blast radius
repo-analyst impact agents/base.py

# Detect dead code
repo-analyst deadcode --threshold 0.7

# Full analysis
repo-analyst analyze .
```

---

## 📊 Example Output

```bash
$ repo-analyst risk --top 5

⚠️ Risk Analysis (top 5)

🔧 Initializing MCP servers...
✅ Orchestrator ready

================================================================================
**Top 5 High-Risk Files**

Files with the highest blast radius if changed:

1. `mcp_servers/repo_reader/reader.py` — Risk:  0.26, Dependents: 7, Dependencies: 1
2. `mcp_servers/dependency_graph/graph.py` — Risk: 0.18, Dependents: 4, Dependencies: 2
3. `schemas/base.py` — Risk: 0.17, Dependents: 5, Dependencies: 0

**Risk Interpretation**:
✅ **Manageable risk**:  Dependencies are relatively well-distributed.

**Recommendations**:
1. Architecture boundaries are clean - Good layering discipline.
2. Add test coverage - No test layer detected in architecture.
================================================================================

🎯 Confidence:  0.90
📁 Evidence: 19 items
```

---

## 🧩 Core Features

### 🏗️ Architecture Analysis

```bash
repo-analyst overview
```

- Detects layers from directory structure
- Identifies boundary violations
- Infers architecture patterns
- **Output**: Layer map, violations, recommendations

### ⚠️ Risk Analysis

```bash
repo-analyst risk --top 10
```

- Calculates fan-in/fan-out metrics
- Scores blast radius (0-1)
- Identifies critical dependencies
- **Output**: Ranked risk list with evidence

### 🔗 Dependency Analysis

```bash
repo-analyst deps path/to/file.py
```

- Shows what file imports
- Shows what imports file
- Calculates coupling metrics
- **Output**: Bidirectional dependency map

### 💥 Impact Analysis

```bash
repo-analyst impact path/to/file.py --depth 3
```

- Traces transitive dependencies
- Estimates blast radius
- Severity classification
- **Output**: Affected files, recommendations

### 💀 Dead Code Detection

```bash
repo-analyst deadcode --threshold 0.7
```

- Identifies files with zero fan-in
- Probabilistic scoring (never claims certainty)
- Excludes entry points automatically
- **Output**: Confidence-scored candidates

### 📄 Architecture Proposals

```bash
repo-analyst propose-architecture \
  --goal "Improve scalability" \
  --output proposal.md
```

- Multi-agent analysis (Architecture + Risk + Verifier)
- Executive summary with evidence tables
- Actionable recommendations
- **Output**: Professional Markdown report

### 🎨 Mermaid Diagrams

```bash
repo-analyst diagram --type architecture --output arch.mmd
```

- Valid Mermaid syntax (no prose)
- Grounded in actual file paths
- Types: `architecture`, `dependency`, `risk`
- **Output**: Paste into [mermaid.live](https://mermaid.live)

### ❓ Natural Language Queries

```bash
repo-analyst ask "What breaks if I change auth. py?"
```

- Keyword-based routing (no LLM required)
- Routes to appropriate agent
- Evidence-backed answers
- **Output**: Contextual analysis

### 🔍 Semantic Code Search

```bash
repo-analyst search "authentication logic" --top 5
```

- RAG-powered search
- Function/class-level chunking
- Gemini embeddings
- **Output**: Relevant code with line numbers

---

## 🧠 Architecture

### System Design

```
┌─────────────────────────────────────────────────┐
│                 CLI (Click)                      │
│  Commands:  analyze, overview, risk, deps,       │
│            impact, deadcode, propose, diagram    │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│      LangGraph Orchestrator                      │
│  - Command routing                               │
│  - Multi-agent workflows                         │
│  - Verification                                  │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────┼─────────┬─────────┬───────┐
        ▼         ▼         ▼         ▼       ▼
   ┌────────┐ ┌──────┐ ┌────────┐ ┌─────┐ ┌─────────┐
   │  Arch  │ │ Risk │ │  Dep   │ │Dead │ │Verifier │
   │ Agent  │ │Agent │ │ Agent  │ │Code │ │ Agent   │
   └────┬───┘ └───┬──┘ └───┬────┘ └──┬──┘ └────┬────┘
        │         │        │         │         │
        └─────────┴────────┴─────────┴─────────┘
                  │
                  ▼
        ┌─────────────────────┐
        │   MCP Servers        │
        │ - RepoReader         │
        │ - DependencyGraph    │
        │ - CodeIndex (RAG)    │
        └──────────┬───────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │  Synthesis Layer     │
        │ - ReportBuilder      │
        │ - MermaidGenerator   │
        └─────────────────────┘
```

### Agents

| Agent            | Purpose                     | Input               | Output                |
| ---------------- | --------------------------- | ------------------- | --------------------- |
| **Architecture** | Layer detection, boundaries | Repo files, imports | Layer map, violations |
| **Risk**         | Blast radius calculation    | Dependency graph    | Risk scores (0-1)     |
| **Dependency**   | Import analysis             | Specific file       | Dependency map        |
| **Dead Code**    | Unused code detection       | Graph, churn        | Probability scores    |
| **Verifier**     | Output validation           | Agent outputs       | Pass/fail, issues     |

### MCP Servers

| Server              | Purpose                         | Technology                 |
| ------------------- | ------------------------------- | -------------------------- |
| **RepoReader**      | File traversal, content reading | Python pathlib             |
| **DependencyGraph** | AST-based import extraction     | Python ast module          |
| **CodeIndex**       | Semantic search                 | LangChain + FAISS + Gemini |

---

## 📁 Project Structure

```
code-analyst/
├── agents/
│   ├── base.py              # Abstract agent class
│   ├── architecture. py      # Layer detection
│   ├── risk.py              # Risk scoring
│   ├── dependency. py        # Import analysis
│   ├── dead_code.py         # Unused code detection
│   └── verifier.py          # Output validation
├── cli/
│   └── main. py              # CLI commands (Click)
├── graph/
│   ├── orchestrator.py      # Command routing
│   └── states.py            # State schemas (TypedDict)
├── mcp_servers/
│   ├── repo_reader/
│   │   └── reader.py        # File traversal
│   ├── dependency_graph/
│   │   └── graph.py         # Import graph builder
│   └── code_index/
│       └── index.py         # RAG implementation
├── schemas/
│   └── base.py              # Pydantic models
├── synthesis/
│   ├── report_builder.py    # Markdown report generation
│   └── mermaid_generator.py # Diagram generation
├── tests/
│   ├── test_e2e.py          # End-to-end tests
│   └── test_smoke.py        # Smoke tests
├── docs/
│   ├── CLI_REFERENCE.md     # Complete CLI guide
│   └── EXAMPLES.md          # Usage examples
├── . env                     # API keys (not in git)
├── . gitignore
├── requirements.txt
├── setup.py
└── README.md
```

---

## 🧪 Testing

### Run All Tests

```bash
# Smoke tests (fast)
python -m tests.test_smoke

# End-to-end tests (comprehensive)
python -m tests.test_e2e

# Full test suite
./run_tests.sh
```

### Test Coverage

- ✅ 13 E2E test scenarios
- ✅ All 5 agents tested
- ✅ CLI command validation
- ✅ Evidence quality checks
- ✅ Multi-agent workflows
- ✅ File artifact verification

---

## 📚 Documentation

- **[CLI Reference](docs/CLI_REFERENCE.md)** - Complete command documentation
- **[Examples](docs/EXAMPLES.md)** - Real-world usage examples
- **[Architecture](docs/ARCHITECTURE.md)** - System design deep-dive

---

## 🔧 Configuration

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

### Customization

Edit `mcp_servers/repo_reader/reader.py` to adjust:

```python
# Directories to ignore
IGNORE_DIRS = {". git", "node_modules", "__pycache__", "venv"}

# File extensions to analyze
CODE_EXTENSIONS = {".py", ".js", ".ts", ".java", ".go"}
```

---

## 🎯 Design Principles

1. **Evidence over eloquence** - Every claim backed by file paths
2. **Deterministic over clever** - Reproducible results
3. **Incremental over rewrite** - Practical recommendations
4. **Skeptical by default** - Verifier challenges outputs
5. **No silent failures** - Errors return structured outputs

---

## 🚧 Limitations

### Current Scope (MVP)

- ✅ Python repository analysis (primary)
- ✅ Static analysis only (no runtime data)
- ✅ Local repositories only
- ✅ CLI interface (no web UI)

### Known Limitations

- **Language support**: Best for Python, basic support for JS/TS
- **Dynamic imports**: Not detected by static analysis
- **Accuracy**: Dead code detection is probabilistic (~70-90% confidence)
- **Scale**: Tested on repos up to ~1000 files

---

## 🗺️ Roadmap

### Future Enhancements

- [ ] Multi-language support (Java, Go, Rust)
- [ ] Git history analysis (churn metrics)
- [ ] PR impact analysis
- [ ] CI/CD integration
- [ ] IDE plugin (VSCode)
- [ ] Team-level reports
- [ ] Historical trend analysis
- [ ] LLM-based intent classification

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`./run_tests.sh`)
4. Commit with clear messages
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:

- [LangChain](https://langchain.com) - Agent framework
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Orchestration
- [FAISS](https://github.com/facebookresearch/faiss) - Vector search
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Pydantic](https://docs.pydantic.dev/) - Data validation

---

## 📞 Contact

**Author**: m4dd0c  
**Project**: Code Analyst MVP  
**Built**: January 2026 (3-day sprint)

---

## ⚡ Quick Reference

```bash
# Setup
pip install -e .
echo "GOOGLE_API_KEY=your-key" > .env

# Analyze
repo-analyst overview                    # Architecture
repo-analyst risk --top 10               # High-risk files
repo-analyst deps path/to/file.py        # Dependencies
repo-analyst impact path/to/file.py      # Blast radius
repo-analyst deadcode --threshold 0.7    # Unused code

# Generate Artifacts
repo-analyst propose-architecture --output report.md
repo-analyst diagram --type architecture --output arch.mmd

# Query
repo-analyst ask "What are the risky files?"
repo-analyst search "authentication logic"

# Help
repo-analyst --help
repo-analyst <command> --help
```

---

**🎉 You now have a production-ready code analysis tool!**

Star ⭐ the repo if this helps your workflow!
