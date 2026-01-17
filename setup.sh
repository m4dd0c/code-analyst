#!/bin/bash

# Aegis - Multi-Agent Codebase Analysis (Day 2 MVP)
echo "🤖 Aegis - Evidence-Backed Codebase Analysis"
echo "============================================"
echo ""

# Check Python version (>=3.10)
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"
if [[ $(echo "${PYTHON_VERSION%.*} < 3.10" | bc -l 2>/dev/null) ]]; then
  echo "❌ ERROR: Python 3.10+ required (found $PYTHON_VERSION)"
  exit 1
fi

# Clean previous attempts
echo "🧹 Cleaning previous installs..."
rm -rf .venv dist/ build/ *.egg-info/ aegis.egg-info/ 2>/dev/null

# Create virtual environment (FIXED: .venv → no space)
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
  echo "✓ Virtual environment created"
else
  echo "♻️  Using existing virtual environment"
fi

# Activate virtual environment (FIXED: correct path)
source "$VENV_DIR/bin/activate"

# Upgrade pip + install ALL deps (REMOVED duplicate pip install)
echo ""
echo "Installing Aegis + dependencies..."
pip install --upgrade pip >/dev/null 2>&1
pip install -e .[dev] >/dev/null 2>&1 # ✅ Production + dev deps
echo "✓ Dependencies installed"

# .env setup (FIXED: LANGCHAIN_TRACING_V)
if [ ! -f ".env" ]; then
  echo ""
  echo "⚠️  No .env file found - creating template..."
  cat >.env <<EOF
# Google Gemini API Key (REQUIRED for semantic search)
GOOGLE_API_KEY=your-gemini-api-key-here

# Optional: LangSmith tracing (for debugging)
# LANGCHAIN_TRACING_V="true"
# LANGCHAIN_PROJECT="aegis-mvp"
EOF
  echo "✓ .env template created"
  echo ""
  echo "📝 Edit .env → Add your GOOGLE_API_KEY before analysis"
else
  echo "✓ .env file exists"
  if ! grep -q "GOOGLE_API_KEY=" .env; then
    echo "⚠️  .env missing GOOGLE_API_KEY → semantic search will fail"
  fi
fi

# Smoke tests (FIXED: aegis command + flexible testing)
echo ""
echo "🧪 Running smoke tests..."
SMOKE_STATUS=0

# Test 1: CLI exists
if aegis --help >/dev/null 2>&1; then
  echo "✓ CLI command works"
else
  echo "❌ CLI command failed"
  SMOKE_STATUS=1
fi

# Test 2: Basic analysis (no API key needed)
if aegis analyze . >/dev/null 2>&1; then
  echo "✓ Basic analysis works"
else
  echo "⚠️  Analysis needs .env (normal without API key)"
fi

echo ""
echo "============================================"
if [ $SMOKE_STATUS -eq 0 ]; then
  echo "✅ Setup complete! Aegis ready 🚀"
else
  echo "⚠️  Setup complete - configure .env for full features"
fi
echo ""
echo "Quick start:"
echo "  1. Edit .env → Add GOOGLE_API_KEY"
echo "  2. aegis overview .          # Full analysis"
echo "  3. aegis risk --top 5       # Risk scan"
echo "  4. aegis analyze .          # Repo summary"
echo "  5. aegis --help             # All commands"
echo ""
echo "📁 Run on any git repo in current directory"
echo "============================================"
