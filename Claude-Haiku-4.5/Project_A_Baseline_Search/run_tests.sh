#!/bin/bash

# Project A - Baseline Search Test Runner
# Executes all tests for the baseline (pre-feature) search implementation

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
LOGS_DIR="$PROJECT_DIR/logs"
RESULTS_DIR="$PROJECT_DIR/results"

echo "============================================================"
echo "PROJECT A - BASELINE SEARCH TEST RUNNER"
echo "============================================================"
echo ""

# Create directories
mkdir -p "$LOGS_DIR" "$RESULTS_DIR"

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "[Setup] Virtual environment not found. Creating..."
    cd "$PROJECT_DIR"
    bash setup.sh
fi

# Activate venv
echo "[Setup] Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source "$VENV_DIR/Scripts/activate"
else
    source "$VENV_DIR/bin/activate"
fi

echo "[Setup] Python version: $(python --version)"
echo "[Setup] Pip packages: $(pip list | wc -l)"
echo ""

# Run tests
echo "[Test] Running baseline search tests..."
echo ""

python "$PROJECT_DIR/tests/test_pre_feature.py"

TEST_EXIT_CODE=$?

echo ""
echo "[Results] Test execution completed with exit code: $TEST_EXIT_CODE"
echo "[Results] Results saved to: $RESULTS_DIR/results_pre.json"
echo "[Results] Logs saved to: $LOGS_DIR/"
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✓ All tests passed!"
else
    echo "✗ Some tests failed. Check logs for details."
fi

echo ""
echo "============================================================"

exit $TEST_EXIT_CODE
