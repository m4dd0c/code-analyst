#!/bin/bash

# Code Analyst MVP - Test Runner
# Run all tests in sequence

echo "=================================="
echo " CODE ANALYST MVP - TEST SUITE"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
OVERALL_STATUS=0

# Run smoke tests first
echo "${YELLOW}Running smoke tests...${NC}"
python -m aegis.tests.test_smoke
SMOKE_STATUS=$?

if [ $SMOKE_STATUS -ne 0 ]; then
  echo "${RED}❌ Smoke tests failed!  Aborting. ${NC}"
  exit 1
fi

echo "${GREEN}✅ Smoke tests passed!${NC}"
echo ""

# Run unit tests
echo "${YELLOW}Running unit tests...${NC}"

echo "Testing Base Agent..."
python -m aegis.agents.test_base
if [ $? -ne 0 ]; then OVERALL_STATUS=1; fi

echo ""
echo "Testing Risk Agent..."
python -m aegis.agents.test_risk
if [ $? -ne 0 ]; then OVERALL_STATUS=1; fi

echo ""
echo "Testing Architecture Agent..."
python -m aegis.agents.test_architecture
if [ $? -ne 0 ]; then OVERALL_STATUS=1; fi

echo ""
echo "Testing Dependency Agent..."
python -m aegis.agents.test_dependency
if [ $? -ne 0 ]; then OVERALL_STATUS=1; fi

echo ""
echo "Testing Dead Code Agent..."
python -m aegis.agents.test_dead_code
if [ $? -ne 0 ]; then OVERALL_STATUS=1; fi

echo ""
echo "Testing Verifier Agent..."
python -m aegis.agents.test_verifier
if [ $? -ne 0 ]; then OVERALL_STATUS=1; fi

echo ""
echo "Testing Report Builder..."
python -m aegis.synthesis.test_report_builder
if [ $? -ne 0 ]; then OVERALL_STATUS=1; fi

echo ""
echo "Testing Mermaid Generator..."
python -m aegis.synthesis.test_mermaid_generator
if [ $? -ne 0 ]; then OVERALL_STATUS=1; fi

echo ""
echo "Testing Orchestrator..."
python -m aegis.graph.test_orchestrator_enhanced
if [ $? -ne 0 ]; then OVERALL_STATUS=1; fi

# Run E2E tests
echo ""
echo "${YELLOW}Running end-to-end tests...${NC}"
python -m aegis.tests.test_e2e
E2E_STATUS=$?

if [ $E2E_STATUS -ne 0 ]; then
  OVERALL_STATUS=1
fi

# Final summary
echo ""
echo "=================================="
if [ $OVERALL_STATUS -eq 0 ]; then
  echo "${GREEN}✅ ALL TESTS PASSED!${NC}"
  echo "=================================="
  exit 0
else
  echo "${RED}❌ SOME TESTS FAILED${NC}"
  echo "=================================="
  exit 1
fi
