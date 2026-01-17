# Contributing to Code Analyst

Thank you for your interest in contributing! This project was built as an MVP to demonstrate multi-agent systems, but contributions are welcome.

---

## 🚀 Quick Start

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/code-analyst.git
cd code-analyst

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
python -m tests.test_smoke
python -m tests.test_e2e
```

---

## 🧪 Running Tests

```bash
# Fast smoke tests
python -m tests.test_smoke

# Comprehensive E2E tests
python -m tests.test_e2e

# Individual agent tests
python -m agents.test_risk
python -m agents.test_architecture

# All tests
./run_tests.sh
```

**Tests must pass before submitting PR.**

---

## 📝 Code Style

- **Python 3.9+**
- **Type hints** for public methods
- **Docstrings** for classes and complex functions
- **Black** formatting (line length 100)
- **isort** for import sorting

```bash
# Format code
black .  --line-length 100
isort .
```

---

## 🔧 Adding a New Agent

1. Create `agents/your_agent.py`:

```python
from agents.base import BaseAgent
from schemas.base import AgentOutput, Evidence

class YourAgent(BaseAgent):
    def __init__(self, dependencies):
        super().__init__(name="YourAgent")
        self.deps = dependencies

    def analyze(self, context):
        # Your logic
        return AgentOutput(
            analysis=".. .",
            evidence=[Evidence(...)],
            confidence=0.85
        )
```

2. Add tests in `agents/test_your_agent.py`

3. Register in `graph/orchestrator.py`:

```python
self.your_agent = YourAgent(dependencies)

def _handle_your_command(self, input_data):
    return self.your_agent.run(context)
```

4. Add CLI command in `cli/main.py`

---

## 🐛 Reporting Bugs

**Before opening an issue:**

- Search existing issues
- Run on latest version
- Reproduce with minimal example

**Include:**

- Python version
- Operating system
- Command that failed
- Full error message
- Sample repository (if possible)

---

## 💡 Feature Requests

Open an issue with:

- **Problem**: What pain point does this solve?
- **Proposed Solution**: How should it work?
- **Alternatives**: What else did you consider?
- **Evidence Requirement**: How will outputs be validated?

---

## 📋 Pull Request Process

1. **Fork** the repository
2. **Create branch**: `git checkout -b feature/amazing-feature`
3. **Make changes**:
   - Follow code style
   - Add tests
   - Update docs
4. **Run tests**: `./run_tests.sh`
5. **Commit**: Use clear, descriptive messages
6. **Push**: `git push origin feature/amazing-feature`
7. **Open PR** with description of changes

### PR Template

```markdown
## Description

[What does this PR do?]

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Testing

- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Updated existing tests

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex logic
- [ ] Updated documentation
- [ ] No warnings introduced
```

---

## 🎯 Areas for Contribution

### High Priority

- [ ] Multi-language support (Java, TypeScript, Go)
- [ ] Git history analysis (churn metrics)
- [ ] Circular dependency detection
- [ ] Test coverage analysis

### Medium Priority

- [ ] Performance optimizations (parallel agents)
- [ ] FAISS persistence (disk caching)
- [ ] Custom ignore patterns (config file)
- [ ] HTML report generation

### Low Priority

- [ ] IDE plugin (VSCode)
- [ ] Web UI (React)
- [ ] LLM-based intent classification
- [ ] Team-level reports

---

## 📖 Documentation

When adding features, update:

- `README.md` - If user-facing
- `docs/CLI_REFERENCE.md` - For new commands
- `docs/EXAMPLES.md` - Add usage examples
- `docs/ARCHITECTURE.md` - For architectural changes

---

## 🙏 Recognition

Contributors will be:

- Listed in README
- Mentioned in release notes
- Credited in documentation

---

## 📄 License

By contributing, you agree your contributions will be licensed under MIT License.

---

## ❓ Questions?

Open a discussion or reach out to maintainers.

**Thank you for contributing!** 🚀

---

---

# Contributing to Code Analyst

Thank you for your interest in contributing! This project was built as an MVP to demonstrate multi-agent systems, but contributions are welcome.

---

## 🚀 Quick Start

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/code-analyst.git
cd code-analyst

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
python -m tests.test_smoke
python -m tests.test_e2e
```

---

## 🧪 Running Tests

```bash
# Fast smoke tests
python -m tests.test_smoke

# Comprehensive E2E tests
python -m tests.test_e2e

# Individual agent tests
python -m agents.test_risk
python -m agents.test_architecture

# All tests
./run_tests.sh
```

**Tests must pass before submitting PR.**

---

## 📝 Code Style

- **Python 3.9+**
- **Type hints** for public methods
- **Docstrings** for classes and complex functions
- **Black** formatting (line length 100)
- **isort** for import sorting

```bash
# Format code
black .  --line-length 100
isort .
```

---

## 🔧 Adding a New Agent

1. Create `agents/your_agent.py`:

```python
from agents.base import BaseAgent
from schemas.base import AgentOutput, Evidence

class YourAgent(BaseAgent):
    def __init__(self, dependencies):
        super().__init__(name="YourAgent")
        self.deps = dependencies

    def analyze(self, context):
        # Your logic
        return AgentOutput(
            analysis=".. .",
            evidence=[Evidence(...)],
            confidence=0.85
        )
```

2. Add tests in `agents/test_your_agent.py`

3. Register in `graph/orchestrator.py`:

```python
self.your_agent = YourAgent(dependencies)

def _handle_your_command(self, input_data):
    return self.your_agent.run(context)
```

4. Add CLI command in `cli/main.py`

---

## 🐛 Reporting Bugs

**Before opening an issue:**

- Search existing issues
- Run on latest version
- Reproduce with minimal example

**Include:**

- Python version
- Operating system
- Command that failed
- Full error message
- Sample repository (if possible)

---

## 💡 Feature Requests

Open an issue with:

- **Problem**: What pain point does this solve?
- **Proposed Solution**: How should it work?
- **Alternatives**: What else did you consider?
- **Evidence Requirement**: How will outputs be validated?

---

## 📋 Pull Request Process

1. **Fork** the repository
2. **Create branch**: `git checkout -b feature/amazing-feature`
3. **Make changes**:
   - Follow code style
   - Add tests
   - Update docs
4. **Run tests**: `./run_tests.sh`
5. **Commit**: Use clear, descriptive messages
6. **Push**: `git push origin feature/amazing-feature`
7. **Open PR** with description of changes

### PR Template

```markdown
## Description

[What does this PR do?]

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Testing

- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Updated existing tests

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex logic
- [ ] Updated documentation
- [ ] No warnings introduced
```

---

## 🎯 Areas for Contribution

### High Priority

- [ ] Multi-language support (Java, TypeScript, Go)
- [ ] Git history analysis (churn metrics)
- [ ] Circular dependency detection
- [ ] Test coverage analysis

### Medium Priority

- [ ] Performance optimizations (parallel agents)
- [ ] FAISS persistence (disk caching)
- [ ] Custom ignore patterns (config file)
- [ ] HTML report generation

### Low Priority

- [ ] IDE plugin (VSCode)
- [ ] Web UI (React)
- [ ] LLM-based intent classification
- [ ] Team-level reports

---

## 📖 Documentation

When adding features, update:

- `README.md` - If user-facing
- `docs/CLI_REFERENCE.md` - For new commands
- `docs/EXAMPLES.md` - Add usage examples
- `docs/ARCHITECTURE.md` - For architectural changes

---

## 🙏 Recognition

Contributors will be:

- Listed in README
- Mentioned in release notes
- Credited in documentation

---

## 📄 License

By contributing, you agree your contributions will be licensed under MIT License.

---

## ❓ Questions?

Open a discussion or reach out to maintainers.

**Thank you for contributing!** 🚀
